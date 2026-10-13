---
id: ARCH-038
title: Administrator-managed CommerceAgent execution budget policies
status: agreed
coordinator: moda_architect
created: 2026-10-13
updated: 2026-10-13
---

# ARCH-038: Administrator-managed CommerceAgent execution budget policies

## Status

Agreed for task definition. Implementation and integrated certification are outstanding. These are portable definitions based on the 2026-10-13 11:33 uploaded workspace snapshot; subsequent local ARCH-037 patches must be reconciled at task execution.

## Problem

Commerce Studio Preview currently reads execution budgets from service configuration, while Background supplies a separate fixed remaining-time envelope to the Shared runner. Neither establishes centrally managed, durable execution limits with Price Plan and individual merchant precedence for live CommerceAgent turns. The merchant must **not** control these limits. Live and Preview policies have distinct purposes and must never overwrite one another.

## Goals

- Two explicitly independent policies: **LIVE** for production-path CommerceAgent turns, **PREVIEW** for Commerce Studio tests.
- LIVE `deadlineMs` and `outputTokens` resolve **per field**: `MERCHANT` > `PRICE_PLAN` > `PLATFORM`.
- PREVIEW resolves per field: selected-shop **test override** > Studio **platform test default**. A Preview policy cannot fall back to or mutate LIVE policy.
- All mutations require authorised Moda administrator, audit reason, optimistic concurrency and server-side validation. No merchant-facing edit surface in Shopify or WooCommerce.
- Resolve and snapshot the exact effective budget and its provenance for each admitted turn/run. Running work is not changed by later plan or policy mutations.
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
explicit Merchant override if non-null
  else matching current Price Plan override if non-null
  else mandatory Platform default
```

A merchant override belongs to trusted `Shop.id`. A Price Plan override belongs to canonical `MerchantPricingPlan.id`, looked up through the established current Subscription/BillingPlan handle matching. Pending plans do not participate. A non-null explicitly invalid/unavailable high-priority override is a configuration failure, **not** permission to silently fall back. A missing value (`NULL`) means inherit; zero never means inherit.

Use the existing `CommerceEnvironment` dimension to isolate DEVELOPMENT, TEST, STAGING and PRODUCTION policy values. Each live environment requires one Platform row. Price Plan and Merchant rows may be absent, and each column on those rows may be null. All three scopes are writable only by the authorised internal Admin surface. The live path includes Shopify and WooCommerce merchants where their Subscription resolves through the canonical plan handle; do not create separate provider implementations.

### PREVIEW hierarchy (Studio only)

```text
selected Shop test override if non-null
  else mandatory Studio Platform test default
```

This is a separate durable policy/namespace, with per-environment Platform test defaults and optional per-Shop test overrides. It does **not** consult live Platform, Price Plan or Merchant policy. A Studio shop override has no effect on the merchant's actual customer turns. Test settings must be visible to an authorised Studio admin and auditable. Existing local environment variables `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` may be used only as documented transitional bootstrap defaults while migrating, **not** as an invisible competing precedence layer after policy is configured.

### Units and authority

`deadlineMs` = total wall-clock deadline for one CommerceAgent turn, including model and tool operations; `outputTokens` = maximum output tokens passed to each model invocation, **not** a per-conversation cumulative token total. The caller resolves values before execution. Shared validates positive safe integers and honours these values; no arbitrary Shared upper bounds. Admin policy mutation and caller runtime must independently validate operational feasibility. A configured deadline must fit actual worker leases, cancellation and queue/reservation lifetimes; do not silently clamp it or claim it was used when it was not. If the limit is unsupported, reject configuration with a specific reason or return a typed runtime failure. Provider-specific constraints remain enforced at the adapter/provider boundary.

## Request / Event Flow

```text
LIVE incoming event -> Background verifies current Shop/Subscription
  -> snapshot environment + current plan + effective LIVE limits/sources
  -> admit and run ordered Commerce turn via published Shared runner
  -> record final outcome and immutable budget provenance

Studio test request -> Commerce resolves selected Shop + PREVIEW policy
  -> atomically reserve run + resolved limits/sources
  -> execute Shared runner with that exact budget
  -> store terminal state; UI polling is presentation-only
```

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

Database implementation may choose bounded, normalized tables or an equivalent schema satisfying these exact invariants:

- LIVE: one Platform row per `CommerceEnvironment`; at most one Price Plan override per `(environment, merchantPricingPlanId)` and Merchant override per `(environment, shopId)`; foreign keys to `MerchantPricingPlan` and `Shop`; nullable override fields; versioned CAS and attribution to Platform Admin.
- PREVIEW: independently keyed Platform test default per environment, at most one test override per `(environment, shopId)`, with nullable override fields and CAS. No database relationship allowing Preview updates to mutate LIVE policies.
- Both: audited old/new values and effective scope identity (or equivalent durable audit), required human reason, safe validation, appropriate delete/referential behaviour and indexes matching runtime reads. Seed required Platform defaults in an empty production database through migration, not merely a development seed script.
- Initial documented Platform defaults: `deadlineMs=60000`, `outputTokens=800` for both tracks, independently stored and subsequently editable. Explicit Preview deadline validation must respect the current 120-second run reservation lifecycle unless that lifecycle is separately changed and proven safe.
- Avoid copying budget overrides into existing `PlatformBillingPolicy`/`BillingPlan` or `CommerceAgentConfiguration.modelId` fields; those objects own different policies.

## Contracts

Existing Prisma models and migrations are the canonical database contract. Neither Preview nor Background imports the other's private service code. Effective result shape is internal to each owner: `{deadlineMs, outputTokens, deadlineSource, outputTokenSource, policyEditVersions, resolvedAt}` (including the involved scope/plan identity and environment). Existing `@modainteract/moda-interact-shared` runner budget input remains unchanged. If implementation discovers a genuinely new cross-repository serialized API/queue contract, stop and route it through a bounded `moda_shared` task before producer/consumer changes; do not duplicate validators.

## Consistency and Transactions

All writes CAS against policy version and append audit within the same transaction. Runtime reads only the current Subscription plan and active scope matching the trusted Shop and environment; no cross-tenant override application. Snapshot resolved values once at admission/start, with the precise admission boundary documented by each runtime owner. Replays of one run use the same snapshot, never silently reread newer policy. Missing required Platform default must fail closed with an actionable operational diagnostic.

## Ordering

A plan change or Admin policy mutation affects newly admitted turns; already-running turns keep their effective budget. Preserve Background's existing per-conversation ordering and generation fencing. Preview duplicate submission/resume must retain the same run-budget snapshot.

## Failure Handling

Malformed admin inputs are rejected before persistence; conflicting policy versions return an actionable reload/retry conflict. Missing required policy, unknown subscription/plan states or corrupted explicit rows must not silently become permissive defaults. Model/provider timeouts and tool failures preserve existing typed runner outcomes. Budget exhaustion or configured deadline yields an observable failure and terminal run state. Never turn a provider/model failure into a successful answer solely because a budget was increased.

## Scalability

Budget resolution performs bounded indexed PostgreSQL lookups per admitted Commerce turn, not per raw Shopify webhook and not on every Preview polling request. No globally serialized policy lock. The selected budget determines per-turn concurrency/cost exposure; Admin edits should document potential capacity impact. Respect Redis/queue/worker connection and lease limits without new infrastructure until evidence requires it.

## Security

Only authorised Moda internal administrators edit policies. The platform admin permission boundary must be server-side and auditable. Shop context is established by trusted authentication and durable IDs; user input cannot impersonate another shop. No merchant-facing Shopify/Woo configuration. Audit and telemetry must not log credentials, prompt bodies, or customer messages.

## Observability

Use `@modainteract/moda-interact-shared/logging` through the approved runtime. Emit effective `deadlineMs`/`outputTokens`, independent source labels (`PLATFORM`, `PRICE_PLAN`, `MERCHANT` for LIVE; `PREVIEW_PLATFORM`, `PREVIEW_SHOP` for Preview), environment, bounded identifiers/edit versions, terminal outcome and elapsed time. Reuse existing `commerce.turn.*`/`commerce.preview.*` events; do not duplicate standard HTTP metrics or log sensitive content. Ensure telemetry failure cannot block a turn.

## Rollout / Migration

Classification: **pre-production feature introduction**, subject to confirmation at execution that no existing production policy/queue data requires compatibility. Migrations are additive and non-destructive; protect existing billing/subscription data and do not infer permission to reset PostgreSQL. Order: Database live/Preview migrations; independent Admin and Commerce integration and Background runtime implementation after applicable schema task is accepted; developer manual validation; terminal System Tests. Defer environment/worker deployment changes unless execution exposes a concrete requirement, at which point create a bounded Gateway task for that boundary. Rolling workers must not read missing columns or uninitialized defaults before schema deployment.

## Decisions / Tasks

| Task | Owner | Initial status | Depends On |
|---|---|---|---|
| ARCH-038-DATABASE-001 | moda_database | Ready | - |
| ARCH-038-DATABASE-002 | moda_database | Ready | - |
| ARCH-038-ADMIN-001 | moda_admin | Pending | DATABASE-001 |
| ARCH-038-ADMIN-002 | moda_admin | Pending | DATABASE-001 |
| ARCH-038-ADMIN-003 | moda_admin | Pending | DATABASE-001 |
| ARCH-038-BACKGROUND-001 | moda_background | Pending | DATABASE-001 |
| ARCH-038-COMMERCE-001 | moda_commerce | Pending | DATABASE-002 |
| ARCH-038-COMMERCE-002 | moda_commerce | Pending | DATABASE-002, COMMERCE-001 |
| ARCH-038-SYSTEM-TEST-001 | moda_system_test | Pending | DATABASE-001, ADMIN-001/002/003, BACKGROUND-001 |
| ARCH-038-SYSTEM-TEST-002 | moda_system_test | Pending | DATABASE-002, COMMERCE-001/002 |

Full task IDs in YAML frontmatter are authoritative. System-test work is terminal: no implementation task depends on system tests. `docs/decisions/**/_index.md` must not be created or modified until the developer confirms this architecture session is complete.

## Open Questions

- Confirm supported live worker-lease/deadline envelope and operational maximum from actual deployed queue/runtime configuration before finalising Admin input bounds. No invented universal cap.
- Confirm how any current WooCommerce subscription maps to `Subscription.plan` and `shopifyPlanHandle` in the actual target environment; do not invent alternative lookup semantics.
- Confirm whether a development-only environment variable transition period is required; once durable policy is active, it must have one documented source of truth.

## Change History

- 2026-10-13: Adopted administrator-only three-level LIVE hierarchy and isolated two-level Studio PREVIEW hierarchy; authored granular implementation and terminal verification tasks.
