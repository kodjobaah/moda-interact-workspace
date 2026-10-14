---
id: ARCH-038
title: Administrator-managed CommerceAgent execution budget policies
status: in_progress
coordinator: moda_architect
created: 2026-10-13
updated: 2026-10-13
---

# ARCH-038: Administrator-managed CommerceAgent execution budget policies

## Status

In Progress. DATABASE-001 and ADMIN-001/002/003 have passed review and are complete. DATABASE-002 is superseded. BACKGROUND-001 remains Ready, so SYSTEM-TEST-001 is still pending on that dependency. Remaining implementation, Preview certification, and deployment work are outstanding.

## Problem

Commerce Studio Preview currently reads execution budgets from service configuration, while Background supplies a separate fixed remaining-time envelope to the Shared runner. Neither establishes centrally managed, durable execution limits with Price Plan and individual merchant precedence for live CommerceAgent turns. The merchant must **not** control these limits. Live and Preview policies have distinct purposes and must never overwrite one another.

## Goals

- One canonical `CommerceModelPolicy` persistence model, with independent `LIVE` (Background customer turns) and `PREVIEW` (Commerce Studio tests) contexts. Rows share schema but are distinguished by a mandatory context key; reads and writes may never cross contexts.
- A versioned JSONB `budget` object (`budgetSchemaVersion=1`) with `deadlineMs` and `outputTokens` initially, allowing approved future fields without adding policy columns.
- LIVE `deadlineMs` and `outputTokens` resolve **per field**: `MERCHANT` > `PRICE_PLAN` > `PLATFORM`.
- Persisted PREVIEW resolves per field: selected-shop **test override** > Studio **platform test default**; it never silently falls back to LIVE policy. Authorised Studio users may additionally select an explicit, read-only LIVE-policy simulation or a temporary custom test budget when starting a conversation; neither writes any LIVE policy or a custom policy row.
- All mutations require authorised Moda administrator, audit reason, optimistic concurrency and server-side validation. No merchant-facing edit surface in Shopify or WooCommerce.
- Resolve and snapshot the exact effective budget and its provenance for each admitted LIVE turn or Studio Preview conversation. Every run in that Studio conversation uses the frozen selection; changes to policy rows or form controls affect newly started conversations only.
- Shared enforces valid caller-provided budgets without adding a competing product-level ceiling; caller/runtime owners remain responsible for provider, queue and reservation compatibility.

## Non-Goals

- Giving Shopify or WooCommerce merchants permission to edit budgets.
- Configuring model selection, capacity credits, message pricing or billing hard limits through execution budgets.
- Changing `runCommerceTurn` schema or adding a second Shared runner for policies.
- Making Studio Preview settings affect Background live turns.
- Recreating the existing Price Plan-to-BillingPlan association with a new foreign key.
- Introducing a new cache/database, real-time push transport or Gateway service without a demonstrated requirement.

## Current Architecture

In ARCH-024, effective model selection resolves the current subscribed `MerchantPricingPlan` using `Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle`; only `ACTIVE`/`TRIALING` subscriptions and the **current** `planId` participate. `MerchantPricingPlan` already owns the plan's model association; no direct plan-to-`BillingPlan` FK is required. Commerce Preview calls Shared `runCommerceTurn`, with local configured budgets. Background `src/commerce/host.ts` currently provides only a deadline derived from `90_000 - elapsedMs`. `PlatformBillingPolicy` exists for billing controls and must not become the source of truth for Commerce execution budgets.

## Proposed Architecture

### LIVE hierarchy (administrator-owned)

For each `deadlineMs` and `outputTokens` independently:

```text
explicit Merchant override if the JSON key is present
  else matching current Price Plan override if the JSON key is present
  else mandatory Platform default
```

A merchant override belongs to trusted `Shop.id`. A Price Plan override belongs to canonical `MerchantPricingPlan.id`, looked up through the established current Subscription/BillingPlan handle matching. Pending plans do not participate. An explicit invalid/unavailable high-priority JSON value is a configuration failure, **not** permission to silently fall back. An absent key means inherit; JSON `null` and zero never mean inherit.

Use the existing `CommerceEnvironment` dimension (`LOCAL`, `TEST`, `DEVELOPMENT`, `STAGING`, `PRODUCTION`) to isolate policies. Each environment requires one LIVE/PLATFORM policy row. LIVE PRICE_PLAN and SHOP overrides may be absent, and each **JSON key** on those rows may be absent. All scopes are writable only by the authorised internal Admin surface. The live path includes Shopify and WooCommerce merchants where their Subscription resolves through the canonical plan handle; do not create separate provider implementations.

### PREVIEW hierarchy (Studio only)

```text
selected Shop test override if the JSON key is present
  else mandatory Studio Platform test default
```

This is the independent `context=PREVIEW` namespace in the **same** `CommerceModelPolicy` table, with per-environment Platform test defaults and optional per-Shop test overrides. `PREVIEW+PRICE_PLAN` is forbidden by a database constraint. A Preview policy does **not** consult LIVE Platform, Price Plan or Merchant rows, and Preview writes must filter `context=PREVIEW`; shared table storage is not permission to cross contexts. A Studio shop override has no effect on the merchant's actual customer turns. Test settings must be visible to an authorised Studio admin and auditable. Existing local environment variables `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` may be used only as documented transitional bootstrap defaults while migrating, **not** as an invisible competing precedence layer after policy is configured.

**Test Conversation policy-source selector (Studio-only):**

1. **Effective LIVE policy (read-only simulation):** explicitly resolve the selected Shop's current LIVE Merchant → Price Plan → Platform budget under the authorised Studio identity, copy only its effective numbers and per-field provenance into an isolated PREVIEW snapshot, and never edit LIVE rows, schedule live messaging, or fall back to LIVE implicitly. If the LIVE policy/current plan cannot be resolved, show an actionable error and prevent starting in this mode. This is a user-requested inspection mode, not an alternate PREVIEW inheritance layer.
2. **Saved Studio Preview policy:** resolve the selected Shop's persisted `PREVIEW/SHOP` keys over `PREVIEW/PLATFORM` per field, retaining effective sources and versions; this remains the default mode.
3. **Custom test budget:** allow the authorised Studio operator to enter `deadlineMs` and `outputTokens` directly and, under clearly labelled *advanced runner limits*, `modelSteps` and `remoteCalls`. The latter two are **temporary execution inputs**, not keys in `CommerceModelPolicy.budget` v1. Custom fields are positive safe integers and must be checked for provider, reservation and runner feasibility. Custom values are never written to `CommerceModelPolicy`, `CommerceAuditEvent` or LIVE configuration. They may be retained only in the isolated, bounded-lifetime Preview conversation/run snapshot for resume/retry.

The selected source and exact four effective runner limits are frozen at **Start Conversation**, before the first run is admitted. Subsequent turns and retries in that Test Conversation use the same snapshot; changing the policy UI requires starting a new conversation. The UI supports resetting custom controls to the current Studio defaults without persisting them. Polling frequency is a separate browser setting and never influences the execution budget.

### Units and authority

`deadlineMs` = total wall-clock deadline for one CommerceAgent turn, including model and tool operations; `outputTokens` = maximum output tokens passed to each model invocation, **not** a per-conversation cumulative token total. The caller resolves values before execution. Shared validates positive safe integers and honours these values; no arbitrary Shared upper bounds. Admin policy mutation and caller runtime must independently validate operational feasibility. A configured deadline must fit actual worker leases, cancellation and queue/reservation lifetimes; do not silently clamp it or claim it was used when it was not. If the limit is unsupported, reject configuration with a specific reason or return a typed runtime failure. Provider-specific constraints remain enforced at the adapter/provider boundary.

## Request / Event Flow

```text
LIVE incoming event -> Background verifies current Shop/Subscription
  -> snapshot environment + current plan + effective LIVE limits/sources
  -> admit and run ordered Commerce turn via published Shared runner
  -> record final outcome and immutable budget provenance

Studio Start Conversation -> authorise selected Shop and selected test policy source
  -> resolve saved PREVIEW, read-only effective LIVE, or validate temporary custom values
  -> freeze selected source + limits/provenance in bounded Preview conversation state
  -> atomically reserve each run with that frozen conversation budget
  -> execute Shared runner with those exact limits
  -> store terminal state; UI polling is presentation-only
```

### Administrator policy-editor interaction contract

Admin presents budget fields as a **reusable, schema-driven editor**, not as a raw JSON editor. The versioned, allowlisted field descriptors for `budgetSchemaVersion=1` describe `deadlineMs` (positive integer milliseconds, with a human-readable seconds equivalent) and `outputTokens` (positive integer per model invocation). Each descriptor supplies a clear label, unit, explanatory help and input validation; the same internal Admin component renders LIVE Platform, Price Plan and Shop scopes. A new key appearing in JSONB is **not** sufficient to display or accept it: future keys require an approved schema-version contract and explicit runtime/validation support. Unknown versions/keys fail closed.

- **Admin / System Controls / Platform Policy:** show a separate **CommerceAgent Execution Policy** section, not a billing-policy field. Choose the environment; both LIVE Platform budget fields are required. Show exact stored values, the friendly time equivalent, edit/schema versions, and a reasoned, version-checked Save action. Inherited mode is forbidden for required Platform defaults.
- **Admin / Merchant Pricing Plan builder:** add a **CommerceAgent Policy** section within the existing plan editor (not a replacement plan builder). A per-field **Override / Inherit** control starts unset by default; Inherit shows the current LIVE Platform value and its source without copying it into the plan's sparse `budget`. Show the effective plan values and independent provenance.
- **Admin / Tenant Directory / Merchant details:** add an internal-only **CommerceAgent Policy** section with the merchant's canonical current plan identity (or an explicit unresolved/no-current-plan state), a link to the existing plan editor where available, each field's **Override / Inherit** control, and a read-only effective-value/source comparison (**Merchant / Price Plan / Platform**). No merchant-facing Shopify/WooCommerce editor or mutation endpoint.
- **Commerce Studio / Agent Configuration or Test Conversations:** use the same *interaction pattern*, but Commerce owns its own reusable form code. Preserve authorised, audited PREVIEW Platform/Shop editing, separate from a Test Conversations **policy-source selector** (saved PREVIEW, read-only LIVE simulation, temporary custom). Display descriptions, effective-value provenance, 2 editable custom budget fields plus 2 clearly labelled advanced test-runner limits, reset/defaults, and existing separate browser-only polling settings. Only the explicit LIVE simulation reads LIVE values, under privileged read-only authorisation; no Studio editor/action may write LIVE rows or silently fall back across contexts.

For all editor scopes, explicit values must be validated before submission; clearing an override removes the JSON key (never persists `null` or a copied inherited value). Every modification requires a non-empty audit reason, server-side permission checks, transactional `CommerceAuditEvent`, CAS/edit-version check, and disable-while-saving single-flight submission. Surface field-level validation errors and a recoverable conflict/reload action, preserving unsaved user input where safe. Provide a **Policy History** section with timestamp, actor, audit reason and before/after changed keys from the existing `CommerceAuditEvent` (scope/environment/owner-filtered, paginated); show an empty state when no edits exist. Do not expose audit metadata for other merchants or contexts.

## Repository Responsibilities

| Repository | Ownership |
|---|---|
| moda-interact-database | LIVE and PREVIEW durable policy schema, constraints, migrations and audit persistence requirements |
| moda-interact-admin | LIVE Platform controls, Price Plan builder fields and Tenant Directory merchant overrides; exclusively privileged writes |
| moda-interact-background | Resolve and snapshot LIVE effective budgets, verify worker lifecycle compatibility, enforce through Shared |
| moda-interact-commerce | Manage and consume the independent PREVIEW policy in authorised Studio |
| moda-interact-system-test | Integrated precedence, isolation, tenancy, snapshot and runtime certification |
| moda-interact-shared | Existing generic runner and caller-budget enforcement; no new implementation task unless a specific contract gap is discovered |
| moda-interact / moda-interact-woocommerce | **No merchant-facing configuration or implementation tasks** |

## Data Model

Create **one new** Prisma model `CommerceModelPolicy` in PostgreSQL schema `commerce`; do not extend `CommerceModelAvailability`, `PlatformBillingPolicy`, `BillingPlan`, `CommerceAgentConfiguration` or create five near-identical scope tables. The table has:

| Field | Contract |
|---|---|
| `id` | Stable policy identifier (e.g. Prisma CUID) |
| `environment` | Existing `CommerceEnvironment`, required |
| `context` | New enum `CommerceModelPolicyContext`: `LIVE`, `PREVIEW` |
| `scope` | New enum `CommerceModelPolicyScope`: `PLATFORM`, `PRICE_PLAN`, `SHOP` |
| `merchantPricingPlanId` | Nullable FK to existing `MerchantPricingPlan.id`, only for `PRICE_PLAN` |
| `shopId` | Nullable FK to existing `Shop.id`, only for `SHOP` |
| `budget` | Required PostgreSQL `jsonb` object (`Json @db.JsonB`) |
| `budgetSchemaVersion` | Required positive integer, initially `1` |
| `editVersion` | Required optimistic-concurrency counter, initially `1` |
| `createdByAdminId`, `updatedByAdminId` | Nullable for migration-created Platform seeds; authorised Admin FK for later mutations |
| `createdAt`, `updatedAt` | Required timestamps |

Ownership checks (enforced by PostgreSQL `CHECK` constraints):

- `PLATFORM`: no shop or pricing plan ID; allowed in LIVE and PREVIEW.
- `PRICE_PLAN`: requires `merchantPricingPlanId`, no shop ID; **LIVE only**.
- `SHOP`: requires `shopId`, no pricing plan ID; allowed in LIVE and PREVIEW.
- A policy row has exactly the association required by its scope. Use FK `onDelete: Restrict` for Shop/Plan to avoid silent deletion of an override.

Uniqueness must be enforced despite nullable ownership columns, using **partial unique indexes** (or a demonstrably equivalent SQL approach): `(environment, context) WHERE scope=PLATFORM`, `(environment, context, merchantPricingPlanId) WHERE scope=PRICE_PLAN`, and `(environment, context, shopId) WHERE scope=SHOP`. Add indexes supporting the corresponding runtime reads. Prisma schema and the SQL migration must agree on exposed indexes/constraints where Prisma supports them.

### Versioned JSON budget contract

Initially support exactly two keys: `deadlineMs` and `outputTokens`, both positive safe integers when present. Platform rows have **both** required, e.g. `{"deadlineMs":60000,"outputTokens":800}`; plan and shop overrides are sparse objects, e.g. `{"deadlineMs":90000}` or `{"outputTokens":2000}`. **Missing keys inherit independently**; explicit JSON `null` values, arrays, non-object roots, unknown keys in schema version 1, floats, non-positive/unsafe integer values, and empty override objects are invalid. JSON object overlays resolve property-by-property Platform → Plan → Shop for LIVE and Platform → Shop for PREVIEW; never replace the whole effective budget when an override is partial. A future schema version may introduce additional approved keys, with validators and runtime compatibility reviewed explicitly; `budgetSchemaVersion` is not carte blanche for arbitrary JSON.

Use PostgreSQL constraints for scope/JSON shape and supported type/integer invariants that can be enforced safely, and matching version-aware server validation at every read/write boundary. **Do not invent an arbitrary database ceiling** for token/deadline values; Admin/Background/Commerce validate actual worker and reservation feasibility. Unsupported/unknown versions fail closed until consumers support them.

### Defaults, mutation and audit

Migrate/seed exactly one `PLATFORM` row per **context and environment** (initially 5 environments × 2 contexts = 10 rows), each with independent `{"deadlineMs":60000,"outputTokens":800}` values. Protect Platform rows from normal deletion; a missing Platform policy is an error, not a silent fallback. Empty-DB production migration creates the defaults; upgrade rehearsals preserve billing, Shop and subscription rows. Do not introduce a `MerchantPricingPlan` → `BillingPlan` FK or a separate model-specific association; budgets are model-independent.

Use existing `CommerceAuditEvent` plus **five context/scope-specific audit actions** (LIVE Platform/Plan/Shop and PREVIEW Platform/Shop), with actor, reason, old/new JSON, schema and edit version, environment/context/scope and owner ID. Audit and version-checked mutation must be atomic. Add necessary reverse Prisma relations to `Shop`, `MerchantPricingPlan`, `PlatformAdmin` as supported by the existing schema. Migration-created defaults may have null admin attribution; later updates require authorised actor and non-empty reason.

## Contracts

`CommerceModelPolicy` is the canonical database contract for both persisted contexts. Temporary custom test budgets require no additional database table or migration. Neither Preview nor Background imports the other's private service code. Both must select the correct `context` and reject unsupported `budgetSchemaVersion`. Effective result shape is internal to each owner: `{deadlineMs, outputTokens, deadlineSource, outputTokenSource, policyEditVersions, resolvedAt}` (including the involved scope/plan identity and environment). Existing `@modainteract/moda-interact-shared` runner budget input remains unchanged. If implementation discovers a genuinely new cross-repository serialized API/queue contract, stop and route it through a bounded `moda_shared` task before producer/consumer changes; do not duplicate validators.

## Consistency and Transactions

All writes use `editVersion` compare-and-swap and append `CommerceAuditEvent` within the same transaction; use sparse JSONB updates deliberately, not accidental patch-merges that lose or copy inherited keys. Runtime reads only the current Subscription plan and active scope matching the trusted Shop and environment; no cross-tenant override application. Snapshot LIVE values at turn admission and Studio policy-source selection at Test Conversation creation. Each Studio run consumes its conversation snapshot; replays of one run and later turns in that same conversation never silently reread updated policies or edited browser form values. Missing required Platform default must fail closed with an actionable operational diagnostic.

## Ordering

A plan change or Admin policy mutation affects newly admitted turns; already-running turns keep their effective budget. Preserve Background's existing per-conversation ordering and generation fencing. Preview duplicate submission/resume must retain the same conversation-selected budget and associated run snapshot, including temporary custom limits.

## Failure Handling

Malformed persisted policy inputs are rejected before persistence; invalid temporary test budgets are rejected before starting a Preview conversation and cannot write policy rows; conflicting policy versions return an actionable reload/retry conflict. Missing required policy, unknown subscription/plan states or corrupted explicit rows must not silently become permissive defaults. Model/provider timeouts and tool failures preserve existing typed runner outcomes. Budget exhaustion or configured deadline yields an observable failure and terminal run state. Never turn a provider/model failure into a successful answer solely because a budget was increased.

## Scalability

Budget resolution performs bounded indexed PostgreSQL lookups per admitted Commerce turn, not per raw Shopify webhook and not on every Preview polling request. No globally serialized policy lock. The selected budget determines per-turn concurrency/cost exposure; Admin edits should document potential capacity impact. Respect Redis/queue/worker connection and lease limits without new infrastructure until evidence requires it.

## Security

Only authorised Moda internal administrators edit policies or start custom-budget/LIVE-simulation Studio tests. The platform admin permission boundary must be server-side and auditable. Shop context is established by trusted authentication and durable IDs; user input cannot impersonate another shop. No merchant-facing Shopify/Woo configuration. Audit and telemetry must not log credentials, prompt bodies, or customer messages.

## Observability

Use `@modainteract/moda-interact-shared/logging` through the approved runtime. Emit effective `deadlineMs`/`outputTokens`, independent source labels (`PLATFORM`, `PRICE_PLAN`, `MERCHANT` for LIVE; `PREVIEW_PLATFORM`, `PREVIEW_SHOP`, `LIVE_SIMULATION`, or `CUSTOM_TEST` for Studio) plus model-step/tool-call budgets for Studio, environment, bounded identifiers/edit versions, terminal outcome and elapsed time. Reuse existing `commerce.turn.*`/`commerce.preview.*` events; do not duplicate standard HTTP metrics or log sensitive content. Ensure telemetry failure cannot block a turn.

## Rollout / Migration

Classification: **pre-production feature introduction**, subject to confirmation at execution that no existing production policy/queue data requires compatibility. Migrations are additive and non-destructive; protect existing billing/subscription data and do not infer permission to reset PostgreSQL. Order: one consolidated DATABASE-001 migration containing both contexts; independent Admin and Commerce integration and Background runtime implementation after DATABASE-001 is accepted and developer-completed; developer manual validation; terminal System Tests. Defer environment/worker deployment changes unless execution exposes a concrete requirement, at which point create a bounded Gateway task for that boundary. Rolling workers must not read missing columns or uninitialized defaults before schema deployment.
Classification: **pre-production feature introduction**, subject to confirmation at execution that no existing production policy/queue data requires compatibility. Migrations are additive and non-destructive; protect existing billing/subscription data and do not infer permission to reset PostgreSQL. Order: one consolidated DATABASE-001 migration containing both contexts; independent Admin and Commerce integration and Background runtime implementation after DATABASE-001 is accepted; developer manual validation; terminal System Tests. Defer environment/worker deployment changes unless execution exposes a concrete requirement, at which point create a bounded Gateway task for that boundary. Rolling workers must not read missing columns or uninitialized defaults before schema deployment.

## Decisions / Tasks

| Task | Owner | Current status | Depends On |
|---|---|---|---|
| ARCH-038-DATABASE-001 | moda_database | Complete — developer completion recorded | - |
| ARCH-038-DATABASE-002 | moda_database | Superseded | replaced by DATABASE-001 |
| ARCH-038-ADMIN-001 | moda_admin | Complete — developer completion recorded | DATABASE-001 |
| ARCH-038-ADMIN-002 | moda_admin | Complete — developer completion recorded | DATABASE-001, ADMIN-001 |
| ARCH-038-ADMIN-003 | moda_admin | Complete — developer completion recorded | DATABASE-001, ADMIN-001 |
| ARCH-038-BACKGROUND-001 | moda_background | Ready | DATABASE-001 |
| ARCH-038-COMMERCE-001 | moda_commerce | Ready | DATABASE-001 |
| ARCH-038-COMMERCE-002 | moda_commerce | Pending | DATABASE-001, COMMERCE-001 |
| ARCH-038-SYSTEM-TEST-001 | moda_system_test | Pending | DATABASE-001, ADMIN-001/002/003, BACKGROUND-001 |
| ARCH-038-SYSTEM-TEST-002 | moda_system_test | Pending | DATABASE-001, COMMERCE-001/002 |

DATABASE-002 is preserved as a **superseded** historical task definition: no implementation, no dependency and no implementation worktree should be started for it. All downstream Preview work now depends on DATABASE-001. Full task IDs in YAML frontmatter are authoritative. System-test work is terminal: no implementation task depends on system tests. `docs/decisions/**/_index.md` must not be created or modified until the developer confirms this architecture session is complete.

## Open Questions

- Confirm supported live worker-lease/deadline envelope and operational maximum from actual deployed queue/runtime configuration before finalising Admin input bounds. No invented universal cap.
- Confirm how any current WooCommerce subscription maps to `Subscription.plan` and `shopifyPlanHandle` in the actual target environment; do not invent alternative lookup semantics.
- Confirm whether a development-only environment variable transition period is required; once durable policy is active, it must have one documented source of truth.
- At implementation, verify the existing `CommerceAuditEvent` metadata/actions support policy edits without an unrelated audit-table change; any gap must be surfaced explicitly.

## Change History

- 2026-10-13: Adopted administrator-only three-level LIVE hierarchy and isolated two-level Studio PREVIEW hierarchy; authored granular implementation and terminal verification tasks.
- 2026-10-13: Agreed consolidated `CommerceModelPolicy` with `context`, `scope`, owner FKs and versioned JSONB `budget`; DATABASE-001 owns both contexts, DATABASE-002 superseded, downstream Preview dependencies redirected.
- 2026-10-13: Specified reusable Admin policy editor, per-field Override/Inherit controls, effective-source display, privileged audit history, explicit validation/conflict recovery and independent Studio Preview UI; ADMIN-002/003 reuse ADMIN-001 editor.
- 2026-10-13: Added a privileged Studio Test Conversation policy-source selector: saved PREVIEW, read-only effective LIVE simulation, or temporary custom budgets (including test-only advanced runner limits). Freeze selection per Test Conversation; preserve persisted PREVIEW editor and prohibit changes to LIVE policy or new persistence for temporary inputs.
