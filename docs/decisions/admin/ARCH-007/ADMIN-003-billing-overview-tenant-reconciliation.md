---
id: ARCH-007-ADMIN-003
architecture_id: ARCH-007
title: Build billing overview, tenant detail and Shopify reconciliation visibility
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 120
executor: copilot
claimed_at: 2026-09-08T22:12:49Z
attempt: 3
depends_on: 
  - ARCH-007-ADMIN-002
  - ARCH-007-BACKGROUND-007
  - ARCH-007-SHOPIFY-001
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-ADMIN-004
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007-ADMIN-003: Build billing overview, tenant detail and Shopify reconciliation visibility

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Add bounded operational billing views for plan distribution, merchant usage, App Event delivery and per-shop Shopify-vs-Moda reconciliation without turning Admin into the telemetry transport owner.

## Context

With paid usage billing, support needs to see why a merchant was billed/blocked and whether Moda reporting matches Shopify. Existing tenant view only shows limited plan/subscription state.

## Scope

Admin billing overview, paginated UsageEvent/report-state views and tenant Billing tab/read services/tests. Read-only operations in this task.

## Out of Scope

- Retrying events or creating corrections (ADMIN-004).
- Changing policy/plan mappings (ADMIN-001/002).
- Building custom telemetry duplicates.

## Requirements

- Overview uses bounded/paginated/index-supported database queries; never load all shops/events to aggregate in application memory.
- Show counts/distribution for mapped Free/paid/unmapped/sync-error shops, Free exhaustion, paid recovery usage, pending/retryable/needs-attention/reported events, and safety-cap outcomes where persisted.
- Tenant Billing detail shows current mapped/observed plan, pending plan/effective date, exact Shopify cycle, Free lifetime base/adjustments/committed/reserved/remaining, paid current-cycle Moda usage, provider reported usage/cost snapshot when available, message counts/cap and active/expired overrides.
- Show App Event ledger rows with occurredAt, quantity, report state/attempts/last error/reportedAt and safe provider response summary. Do not show bearer tokens/customer payload.
- Show reconciliation discrepancy between Moda net REPORTED recovery usage for current meter/cycle and Shopify TieredPrice usage quantity when BACKGROUND-008 records/provides it.
- Every named shop route remains tenant-parameter-safe and Admin-authenticated; cross-shop lookup cannot be influenced by merchant-controlled identifiers without authorization.
- Use Grafana/OTel only for generic operational telemetry already present; billing ledger/reconciliation is domain data and can be queried from DB.
- INTERNATIONALISATION — every new or changed Admin user-visible string in this task MUST use the existing ARCH-005 Admin ICU/i18n path. Reuse the current Admin locale resolver/runtime and `src/i18n/locales/*`; update `src/i18n/required-keys.ts` when that is the repository convention. Do not hard-code English labels, headings, filters, empty states, reconciliation/status copy or help text in TSX/server UI responses. Add each new key to every Admin locale catalogue currently declared by the repository and use the existing locale-aware formatting helpers for dates/numbers. Do not create a second i18n mechanism.

## Work Items

- [x] Add Billing overview navigation/page.
- [x] Add paginated report-state/event listing.
- [x] Extend tenant detail with Billing section.
- [x] Implement bounded queries and filters for plan/state/date/shop.
- [x] Add security/pagination/empty-state/reconciliation tests.
- [x] Add focused i18n coverage proving every new Admin-visible key resolves through the existing Admin ICU catalogue path and required-key validation remains complete.

## Interfaces / Contracts

Read-only domain sources:

```text
BillingPlan/Subscription/BillingPeriod
ShopEntitlementCounter/adjustments/overrides
UsageEvent report ledger
reconciliation state produced by Background
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-004

## Acceptance Criteria

- [x] Admin can identify unmapped plan and failed billing event without database shell access.
- [x] Tenant view explains Free remaining and paid current-cycle usage.
- [x] Reconciliation discrepancy is visible and bounded.
- [x] Pages are paginated/index-aligned and secure.
- [x] No secret/PII leakage.
- [x] All new Admin-visible copy uses the existing ARCH-005 ICU/i18n catalogues; no task-introduced user-visible English literal bypasses that path.
- [x] Tests/build/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-003` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-003` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for architect review (Attempt 3)

### Files Changed

- `moda-interact-admin/src/components/admin/billing-overview.tsx`
- `moda-interact-admin/src/components/admin/tenant-billing.tsx`
- `moda-interact-admin/src/i18n/index.ts`
- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/billing-presentation.mjs`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`

### Work Completed

- Synchronized the implementation branch with accepted Admin-002 via merge commit `23f62da`, preserving platform controls, tenant overrides, append-only allowance adjustments, and the absolute platform cap.
- Corrected the billing page merge integration while retaining both the overview/ledger and Admin-002 controls.
- Made Free exhaustion explicitly unavailable (`null`) instead of inferring it from a counter threshold.
- Added inclusive date-only filter boundaries, localized report-state labels, locale-formatted quantities, and all bounded ledger diagnostics in both platform and tenant views.
- Added current-period automated-message usage, active/expired override state, platform-bounded effective hard caps, pause-state visibility, and required i18n keys.
- Kept reconciliation explicitly unavailable because no accepted durable provider snapshot/discrepancy model exists.
- Added focused regression coverage for report-state fallback behavior, diagnostics, date boundaries, unavailable exhaustion, message aggregation, override expiry, and Admin-002 preservation.
- Attempt 3 completed the remaining tenant ledger diagnostic presentation, preserved expired override values as historical data while ignoring them for effective policy, failed closed when the platform absolute hard cap is unavailable, and routed overview/filter/report-state copy through the existing ICU runtime.
- Added production-owned behavioral helpers for hard-cap calculation, override state, inclusive date boundaries, localized report-state labels, and tenant ledger presentation; tests execute those same helpers.
- Admin implementation commit: `a1ef38d`; pushed to `origin/task/ARCH-007-ADMIN-003`.

### Validation Results

- `node --test tests/security/admin-billing-visibility.test.mjs`: passed, 9 tests.
- `npm test`: passed, 124 tests; existing Node module-type warnings remain.
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed with 2 pre-existing queue-monitor hook warnings and no errors.
- `npm run build`: passed; existing BullMQ dynamic dependency and optional `@valkey/valkey-glide` warnings remain.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Targeted Prettier check: passed for all Attempt 3 files.
- `npm run format:check`: reports 70 unrelated pre-existing formatting-drift files; all Attempt 3 files were formatted with the repository Prettier binary.
- Nested Admin `database` gitlink staged: no.

### Deviations

- The accepted Admin Prisma schema has no durable Shopify usage snapshot or discrepancy table. Reconciliation is therefore rendered as explicitly unavailable (`discrepancy: null`) rather than fabricated or obtained with raw SQL.
- Free exhaustion remains unavailable until a schema-supported aggregate or accepted persisted exhaustion outcome exists; the former counter-threshold proxy was removed.
- No new locale keys were required; all changed visible copy continues to use existing Admin ICU catalogue keys.

### Assumptions

- Paid current-cycle usage is represented by reported `UsageEvent` rows matching the subscription billing period and mapped Shopify usage-event handle.
- Automated-message usage is represented by all current-period `OUTBOUND_AUTOMATED_MESSAGE` events; it is `null` when no billing period exists.

### Unresolved Issues

- Shopify-vs-Moda numeric discrepancy remains unavailable until Background or Database provides a durable provider usage snapshot/comparison contract.

### Architectural Concerns

- The discrepancy requirement is a cross-repository contract gap, not an Admin presentation gap. `ADMIN-004` should not add a local duplicate or raw provider query; it should consume the accepted shared/database snapshot contract when available.

### Git / VCS

Task branch: `task/ARCH-007-ADMIN-003`

Implementation repository:
   repository: `moda-interact-admin`
   commit: `a1ef38d`
   remote branch: `origin/task/ARCH-007-ADMIN-003`
   pushed: yes

Parent workspace:
   task file: `docs/decisions/admin/ARCH-007/ADMIN-003-billing-overview-tenant-reconciliation.md`
   claim commit: `2d1988c`
   review report commit: `25957aa`
   remote branch: `origin/task/ARCH-007-ADMIN-003`
   pushed: claim yes; review report yes
   submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested

### Review Notes

#### Attempt 1 — Changes Requested

The implementation direction is accepted, including the decision to render Shopify-vs-Moda reconciliation as unavailable while the accepted schema has no durable provider usage snapshot. Do **not** add raw SQL, direct Shopify provider calls, a duplicate reconciliation table, or any ADMIN-004 retry/correction behavior in this task.

Attempt 2 is a narrow correction pass. Execute the following steps **in order**. Do not broaden scope or redesign billing.

##### Step 0 — Synchronize the implementation task branch with accepted ADMIN-002

The reviewed Admin implementation commit `66c5730` was created from a branch that diverges from the current Admin `main`; it does not contain the architect-accepted ADMIN-002 implementation even though ADMIN-003 depends on ADMIN-002. ADMIN-003 also edits files that ADMIN-002 changed, including the billing page, Admin types, locale catalogue and required-key manifest.

Before making Attempt 2 code changes, in `moda-interact-admin` while checked out on `task/ARCH-007-ADMIN-003`:

```bash
git fetch origin
git merge origin/main
```

Rules:

- Merge `origin/main` **into the existing task branch**. Do not rebase and do not force-push.
- Resolve conflicts by preserving **both** the accepted ADMIN-002 billing-control functionality and ADMIN-003 billing visibility additions.
- Do not merge `task/ARCH-007-ADMIN-003` into `main`.
- After conflict resolution, verify the accepted ADMIN-002 control-plane files/features still exist, including platform billing controls, tenant billing overrides and append-only Free allowance adjustments.
- If `origin/main` does not yet contain the architect-accepted ADMIN-002 implementation, STOP implementation work and record the dependency/integration problem in this task instead of reimplementing ADMIN-002 locally.

##### Step 1 — Correct App Event ledger diagnostics and report-state rendering

Current data loading already selects these fields in `src/lib/admin/billing.ts` and they MUST remain bounded/paginated:

```text
occurredAt
quantity
shopifyReportState
reportAttemptCount
lastReportAttemptAt
reportedAt
providerErrorCode
providerResponseSummary
```

Update **both** ledger presentations:

```text
src/components/admin/billing-overview.tsx
src/components/admin/tenant-billing.tsx
```

Each ledger row MUST visibly expose:

```text
occurredAt
metric
quantity
report state
reportAttemptCount
lastReportAttemptAt
reportedAt
providerErrorCode
providerResponseSummary
```

Use the existing Admin ICU/i18n path for column labels, empty values and visible report-state labels. Use existing locale-aware date/number formatters.

The following behavior is mandatory:

| UsageEvent state | providerErrorCode | UI result |
| --- | --- | --- |
| `PENDING` | `null` | show localized Pending state; MUST NOT show `Reported` |
| `IN_FLIGHT` | `null` | show localized In-flight state; MUST NOT show `Reported` |
| `RETRYABLE` | any/null | show localized Retryable state plus error fields when present |
| `NEEDS_ATTENTION` | any/null | show localized Needs-attention state plus error fields when present |
| `REPORTED` | `null` | show localized Reported state |

Delete/replace the current fallback equivalent to:

```ts
providerErrorCode ?? adminI18n.t("billing.reported")
```

because absence of an error code does not mean the event was reported.

Do not expose bearer tokens or customer payloads. `providerResponseSummary` is the only provider response detail permitted by this task.

##### Step 2 — Stop fabricating the cross-tenant Free-exhaustion KPI

The current overview counts `FREE_RECOVERY_LIFETIME` counters with `committedQuantity >= 5`. That is not the ARCH-007 exhaustion definition because it ignores reserved capacity, the plan's configured base allowance and signed ADMIN-002 allowance adjustments.

The correct tenant-level formula remains:

```text
effectiveAllowance = baseAllowance + signedAdjustments
remaining = max(effectiveAllowance - committed - reserved, 0)
exhausted = remaining == 0
```

The accepted schema does not currently provide an index-supported/materialized cross-tenant aggregate for that exact calculation, and this task MUST NOT load all shops/adjustments into application memory or add raw SQL.

Therefore Attempt 2 MUST use this contract:

```ts
BillingOverview.freeExhausted: number | null
```

and:

```text
getBillingOverview() -> freeExhausted = null
BillingOverviewCards -> localized "Unavailable" when freeExhausted is null
```

Do not use `committedQuantity >= 5` or any other constant threshold as a proxy. Keep the tenant-level exact allowance calculation unchanged.

##### Step 3 — Add the required tenant message-count/cap visibility

Extend the existing bounded `getTenantBilling()` read model; do not create a second billing read service.

Use accepted database fields only:

```text
UsageEvent.metric = OUTBOUND_AUTOMATED_MESSAGE
Subscription.billingPeriod.id
BillingPlan.defaultOutboundHardLimit
PlatformBillingPolicy.absoluteOutboundHardLimit
ShopBillingPolicyOverride.outboundHardLimit
ShopBillingPolicyOverride.pauseNewRecoveries
ShopBillingPolicyOverride.pauseAutomatedWhatsapp
ShopBillingPolicyOverride.reason
ShopBillingPolicyOverride.expiresAt
```

Required behavior:

1. `currentPeriodAutomatedMessageQuantity`
   - If a current `billingPeriod.id` exists, aggregate the tenant's `UsageEvent.quantity` for that `billingPeriodId` and `metric = OUTBOUND_AUTOMATED_MESSAGE`.
   - This is Moda's local current-period count. Do not require Shopify `REPORTED` state for this local count.
   - If no current billing period exists, represent the value as unavailable (`null`), not a fabricated zero.

2. Override state
   - `ACTIVE` when an override exists and `expiresAt` is `null` or strictly later than the evaluation time.
   - `EXPIRED` when an override exists and `expiresAt <= evaluation time`.
   - An expired override MUST remain visible historically, including reason and configured values.
   - An expired override MUST NOT affect the effective hard cap.

3. Effective outbound hard cap

```text
candidateHardCap =
    activeOverride.outboundHardLimit
    ?? BillingPlan.defaultOutboundHardLimit

effectiveOutboundHardCap =
    min(candidateHardCap, PlatformBillingPolicy.absoluteOutboundHardLimit)
```

   - If a required source value is genuinely unavailable, return/display unavailable rather than inventing a default.
   - Display the plan default hard cap, platform absolute hard cap, shop hard override (if recorded), effective hard cap, override state, override reason, `pauseNewRecoveries` and `pauseAutomatedWhatsapp`.
   - Clearly label the automated-message quantity as a tenant/current-billing-period aggregate. Do not imply that the aggregate quantity is itself a per-conversation cap.

Use the existing ADMIN-002 `PlatformBillingPolicy` and `ShopBillingPolicyOverride` records after Step 0. Do not duplicate those models or business rules.

##### Step 4 — Correct date-range boundary semantics

The Billing ledger `from`/`to` form is date-based. For a valid `YYYY-MM-DD` input:

```text
from -> YYYY-MM-DDT00:00:00.000Z
to   -> YYYY-MM-DDT23:59:59.999Z
```

A `to=2026-09-08` filter MUST include events occurring at any time on 8 September 2026. Do not parse the `to` value as midnight at the start of the day.

Keep the database query bounded/paginated and index-aligned. Do not switch to application-memory filtering.

##### Step 5 — Complete the ARCH-005 i18n invariant

All new or changed visible Admin copy in Attempt 2 MUST use the existing Admin ICU runtime/catalogue and required-key manifest.

Mandatory presentation rules:

- Format displayed billing quantities with the existing locale-aware number formatter instead of rendering raw decimal strings directly where they represent numeric quantities.
- Render visible Shopify report-state labels through i18n. Operational form/query values may remain `PENDING`, `IN_FLIGHT`, `RETRYABLE`, `REPORTED`, `NEEDS_ATTENTION`.
- Add every new key to every Admin locale catalogue currently declared by the repository and update `src/i18n/required-keys.ts` according to the existing convention.
- Do not create a second translation helper/runtime and do not hard-code new user-visible English in TSX.

##### Step 6 — Required behavioral regression coverage

Do not satisfy these checks with source-regex assertions alone. Add/extend deterministic behavioral tests that exercise the read/presentation logic or extracted pure helpers.

The focused Attempt 2 coverage MUST prove all of the following:

```text
A. PENDING + providerErrorCode=null
   -> rendered state is Pending
   -> "Reported" is not used as a fallback

B. REPORTED + providerErrorCode=null
   -> rendered state is Reported

C. Ledger presentation exposes:
   reportAttemptCount
   lastReportAttemptAt
   reportedAt
   providerErrorCode
   providerResponseSummary

D. Billing overview with exact cross-tenant Free exhaustion unavailable
   -> freeExhausted is null
   -> UI renders localized Unavailable
   -> no committed>=5 proxy query remains

E. Active shop hard override
   -> participates in effective hard-cap calculation
   -> effective hard cap is also bounded by platform absolute hard limit

F. Expired shop hard override
   -> remains visible as EXPIRED with reason/configured values
   -> is ignored when calculating effective hard cap

G. Current billing period exists
   -> OUTBOUND_AUTOMATED_MESSAGE quantity is aggregated for that shop + billingPeriodId

H. No current billing period
   -> current-period automated-message quantity is unavailable/null

I. Date filter
   from=2026-09-08 -> 2026-09-08T00:00:00.000Z
   to=2026-09-08   -> 2026-09-08T23:59:59.999Z

J. ADMIN-002 integration preservation after merging main
   -> platform billing-control route/service still exists
   -> tenant override path still exists
   -> Free allowance adjustment path still exists
```

Run the focused ADMIN-003 tests plus the repository-declared full Admin validation required by this task (`test`, TypeScript/typecheck if declared, Prisma generate/validate if declared, lint, build, and `git diff --check`). Do not invent missing scripts.

##### Explicit non-goals for Attempt 2

Do **not** do any of the following:

- Do not implement `ARCH-007-ADMIN-004` retry/correction actions.
- Do not implement `ARCH-007-BACKGROUND-008` reconciliation persistence.
- Do not query Shopify directly from Admin for provider usage.
- Do not add a reconciliation table/model/migration.
- Do not add raw SQL or load all shops/events/adjustments into memory for aggregation.
- Do not change billing policy semantics established by ADMIN-002.
- Do not remove or rewrite accepted ADMIN-002 functionality while resolving the branch merge.
- Do not merge the task branch into `main`.

##### Completion/stop condition

When all corrections and required tests pass:

1. Update this same task's Completion Report for **Attempt 2** with exact files changed, validation results, and implementation commit SHA.
2. Commit and push `moda-interact-admin` on `task/ARCH-007-ADMIN-003`.
3. Commit and push this task report on the mirrored parent `task/ARCH-007-ADMIN-003` branch.
4. Set this task to `review`.
5. **STOP.** Do not start ADMIN-004 and do not claim architect acceptance.

The existing reconciliation-unavailable decision is accepted for this task: keep `discrepancy: null` until an accepted durable Background/Database contract provides a Shopify usage snapshot/comparison.


#### Attempt 2 — Changes Requested

Attempt 2 materially corrected the Attempt 1 issues. Preserve the following accepted Attempt 2 behavior exactly unless a correction below explicitly requires touching it:

```text
ADMIN-002 is integrated into the ADMIN-003 branch
Free exhaustion overview is null/unavailable rather than committed>=5
from/to date-only parsing uses inclusive UTC day boundaries
platform ledger exposes the complete safe reporting diagnostics
report-state labels use the existing Admin i18n path
automated-message usage is scoped to the current billing period
expired hard overrides do not affect the effective hard cap
reconciliation remains discrepancy=null because no accepted durable provider snapshot exists
```

Attempt 3 is a **narrow correction pass**. Do not redesign ADMIN-003 or reopen already-corrected architecture. Execute the following steps in order.

##### Step 0 — Verify the task branch baseline before editing

Work only on `moda-interact-admin` branch `task/ARCH-007-ADMIN-003` and the mirrored parent-workspace branch of the same name.

Run:

```bash
git fetch origin
git branch --show-current
git merge-base --is-ancestor origin/main HEAD
```

Required result:

```text
branch == task/ARCH-007-ADMIN-003
origin/main is an ancestor of HEAD
```

If `git merge-base --is-ancestor origin/main HEAD` exits non-zero because `main` advanced after this review, merge `origin/main` into the existing task branch before continuing:

```bash
git merge origin/main
```

Do not rebase and do not force-push.

Before changing ADMIN-003, verify the accepted ADMIN-002 implementation still exists, including:

```text
src/app/(protected)/billing/controls/page.tsx
src/app/actions/billing-controls.ts
src/components/admin/billing-controls.tsx
src/lib/admin/billing-controls.ts
src/lib/admin/billing-control-validation.ts
```

If those accepted dependency files are absent, STOP and record the integration problem in this task. Do not reimplement ADMIN-002.

##### Step 1 — Complete the tenant ledger diagnostics

File to change:

```text
src/components/admin/tenant-billing.tsx
```

The platform ledger already displays the accepted safe diagnostic set. Make the tenant ledger display the same diagnostic data for each row.

The tenant ledger MUST visibly render all of these fields:

```text
metric
quantity
shopifyReportState
providerErrorCode
providerResponseSummary
reportAttemptCount
lastReportAttemptAt
reportedAt
shopifyEventHandle
```

Presentation rules:

```text
shopifyReportState       -> adminBillingReportStateLabel(...)
quantity                 -> adminI18n.formatNumber(...)
reportAttemptCount       -> adminI18n.formatNumber(...)
lastReportAttemptAt      -> adminI18n.formatDateTime(...) when present
reportedAt               -> adminI18n.formatDateTime(...) when present
null diagnostic value    -> existing localized empty/not-recorded label
```

Do not expose bearer tokens, provider secrets or customer payloads. `providerResponseSummary` is the maximum provider-response detail permitted by this task.

Do not remove the diagnostics already present in the platform ledger.

##### Step 2 — Preserve expired override values as history while ignoring them for effective policy

Files to inspect/change:

```text
src/lib/admin/billing.ts
src/components/admin/tenant-billing.tsx
src/lib/admin/types.ts   # only if the read-model shape needs a narrow correction
```

The current implementation correctly ignores an expired override when calculating the **effective** hard cap. Preserve that behavior.

The remaining bug is presentation/history: an expired override's configured pause values are currently converted to `null` before the UI renders them.

Use this exact distinction:

```text
RECORDED/HISTORICAL OVERRIDE VALUES
    come from the persisted ShopBillingPolicyOverride row
    remain visible for ACTIVE and EXPIRED overrides

EFFECTIVE RUNTIME POLICY
    may use override values only when overrideState == ACTIVE
    must ignore the override when overrideState == EXPIRED
```

For an existing override, the tenant Billing UI MUST display the persisted configured values regardless of expiry:

```text
override.outboundSoftLimit
override.outboundHardLimit
override.recoverySafetyCeiling
override.pauseNewRecoveries
override.pauseAutomatedWhatsapp
override.reason
override.expiresAt
```

Deterministic example:

```text
stored override:
  state after evaluation = EXPIRED
  pauseNewRecoveries = true
  pauseAutomatedWhatsapp = true
  outboundHardLimit = 40
  reason = "temporary support hold"

UI history MUST show:
  state = Expired
  pause new recoveries = Enabled
  pause automated WhatsApp = Enabled
  hard override = 40
  reason = temporary support hold

Effective hard-cap calculation MUST ignore the expired 40 value.
```

Do not render root-level derived `pauseNewRecoveries` / `pauseAutomatedWhatsapp` fields as the historical configured values if those fields intentionally represent only active/effective behavior. Render the persisted `billing.override.*` values for override history, or rename/remove ambiguous derived fields if necessary.

##### Step 3 — Fail closed when the platform absolute hard cap is unavailable

File to change:

```text
src/lib/admin/billing.ts
```

The effective outbound hard cap is valid only when both of these inputs exist:

```text
configuredHardLimit
PlatformBillingPolicy.absoluteOutboundHardLimit
```

Use this exact contract:

```text
configuredHardLimit == null
    -> effectiveOutboundHardCap = null

platform policy == null
    -> effectiveOutboundHardCap = null

both values exist
    -> effectiveOutboundHardCap = min(configuredHardLimit, platformAbsoluteOutboundHardLimit)
```

Do NOT return the plan/override configured hard limit as an "effective" value when the platform absolute hard cap is unavailable.

Required truth table:

| configured hard limit | platform absolute cap | effective hard cap |
| ---: | ---: | ---: |
| `50` | `100` | `50` |
| `150` | `100` | `100` |
| `50` | unavailable | unavailable / `null` |
| unavailable | `100` | unavailable / `null` |

The UI already knows how to render nullable values as localized unavailable; preserve that behavior.

##### Step 4 — Finish the remaining ARCH-005 Admin i18n/locale formatting

Files to inspect/change:

```text
src/components/admin/billing-overview.tsx
src/components/admin/tenant-billing.tsx
src/i18n/index.ts
src/i18n/locales/*
src/i18n/required-keys.ts
```

Correct these exact remaining presentation paths:

1. **Paid-recovery overview quantity**

Current semantic problem:

```text
overview.paidRecoveryUsage is displayed as a raw numeric string
```

Required:

```text
Number(overview.paidRecoveryUsage)
    -> existing adminI18n.formatNumber(...)
```

2. **Overview report-state cards**

The raw enum value MUST NOT be used as visible copy inside `billing.reportState`.

Required:

```text
state enum
    -> adminBillingReportStateLabel(state)
    -> pass localized label to billing.reportState
```

3. **Ledger filter options**

The `<option value>` MUST remain the operational enum because it is the query/filter contract:

```text
value="PENDING"
value="IN_FLIGHT"
value="RETRYABLE"
value="REPORTED"
value="NEEDS_ATTENTION"
```

But the visible option label MUST be `adminBillingReportStateLabel(value)`, not the raw enum text.

4. **Override numeric values**

When present, render these through `adminI18n.formatNumber(...)`:

```text
billing.override.outboundSoftLimit
billing.override.outboundHardLimit
billing.override.recoverySafetyCeiling
```

Continue using the existing Admin ICU runtime/catalogue. Do not create a second translation system. Add/update catalogue keys only if genuinely required, and keep `src/i18n/required-keys.ts` complete.

##### Step 5 — Replace source-presence-only assertions with real behavioral regression coverage

Current `tests/security/admin-billing-visibility.test.mjs` primarily uses `readFile(...)` plus `assert.match(...)`. Those source-contract checks may remain, but they are **not sufficient** for the Attempt 3 acceptance tests below.

The new tests MUST execute the production logic or a pure helper extracted from production. Do not copy/reimplement the production formula inside the test.

If direct execution is awkward because the logic is embedded in a Prisma read function or TSX component, extract the smallest pure production helper required for deterministic testing. Keep that helper in the normal Admin source tree and make production code call the same helper the test executes.

Attempt 3 MUST behaviorally prove these cases:

```text
A. Effective hard cap — active override below platform cap
   plan default = 80
   active override hard limit = 50
   platform cap = 100
   -> effective = 50

B. Effective hard cap — active override above platform cap
   active override hard limit = 150
   platform cap = 100
   -> effective = 100

C. Effective hard cap — expired override
   plan default = 80
   expired override hard limit = 50
   platform cap = 100
   -> effective = 80
   -> historical override hard limit remains 50

D. Effective hard cap — missing platform policy
   configured hard limit = 50
   platform policy = null
   -> effective = null

E. Expired override history
   expired override pauseNewRecoveries=true
   expired override pauseAutomatedWhatsapp=true
   -> historical presentation/read model preserves true/true
   -> override state is EXPIRED

F. Date boundaries execute the production date helper
   billingDateBoundary("2026-09-08", false)
       -> 2026-09-08T00:00:00.000Z
   billingDateBoundary("2026-09-08", true)
       -> 2026-09-08T23:59:59.999Z

G. Report-state presentation executes the production label helper
   PENDING  -> localized Pending label
   REPORTED -> localized Reported label

H. Tenant ledger diagnostic presentation
   a row containing providerResponseSummary, reportAttemptCount,
   lastReportAttemptAt, reportedAt and shopifyEventHandle
   -> all five values are represented by the tenant ledger presentation path
```

For case H, a rendered-component assertion is preferred. If the repository test runtime cannot render TSX directly, extract a minimal production presentation/view-model helper and test that helper; do not fall back to regex-only assertions for the values themselves.

Also retain the existing source/security guards that prove:

```text
bounded pagination remains present
provider secrets/customer payloads are not selected/displayed
ADMIN-002 control routes/services remain present
no merge-conflict markers remain
```

##### Step 6 — Validation, commits and stop condition

After implementing only the corrections above, run the repository-declared validation that exists:

```text
focused ADMIN-003 tests
full npm test
npx tsc --noEmit
npm run prisma:validate
npm run lint
npm run build
git diff --check
```

If `format:check` still reports repository-wide pre-existing drift, format every file changed by Attempt 3 and record the baseline separately; do not mass-format unrelated files.

Then:

1. Update this same task's Completion Report to **Attempt 3** and record exact files changed, behavioral tests added, validation results and implementation commit SHA.
2. Commit and push `moda-interact-admin` branch `task/ARCH-007-ADMIN-003`.
3. Commit and push the mirrored parent-workspace `task/ARCH-007-ADMIN-003` branch.
4. Set this task to `review`.
5. **STOP.** Do not start or modify ADMIN-004 and do not claim architect acceptance.

##### Explicit non-goals for Attempt 3

Do **not**:

- implement ADMIN-004 retry/correction actions;
- add or change database schema/migrations;
- add raw SQL;
- query Shopify directly from Admin;
- create a new reconciliation persistence mechanism;
- change the accepted `discrepancy: null` behavior;
- change ADMIN-002 billing-control semantics;
- remove already-correct platform-ledger diagnostics;
- replace bounded DB reads with load-all/application-memory aggregation;
- rebase or force-push;
- merge the task branch into `main`.

The accepted reconciliation decision remains:

```text
BACKGROUND-008 completion does not itself create a durable Admin-queryable
Shopify usage snapshot/discrepancy model. Keep reconciliation unavailable in
ADMIN-003 until an accepted durable contract exists.
```

### Reviewed Files

- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/components/admin/billing-overview.tsx`
- `moda-interact-admin/src/components/admin/tenant-billing.tsx`
- `moda-interact-admin/src/i18n/index.ts`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`
- accepted ADMIN-002 integration present in the supplied tree
- implementation commit `f096d68`
- parent task-report commit `39659d2`

### Validation Reviewed

- Agent-reported full Admin suite: 121 passed.
- Agent-reported TypeScript, Prisma validation, build, lint and `git diff --check`: passed.
- Focused `tests/security/admin-billing-visibility.test.mjs` was independently executed: 6/6 passed.
- Git ancestry reviewed: `f096d68` is ahead of current Admin `main` and no longer behind it; accepted ADMIN-002 is integrated.
- Existing focused ADMIN-003 tests are still primarily source-regex assertions and do not behaviorally prove the Attempt 3 cases above.
### Architecture Conformance

Changes required, but the remaining scope is narrow. Branch integration, bounded/read-only ownership, reconciliation-unavailable handling, nullable Free-exhaustion semantics, inclusive date boundaries, platform-ledger diagnostics, current-period message aggregation and expired-override exclusion from effective hard-cap calculations now conform. Tenant-ledger diagnostic completeness, expired override history presentation, fail-closed effective-cap semantics, remaining locale formatting and behavioral regression quality require Attempt 3 correction.

### Follow-up

No new task. Continue the same `ARCH-007-ADMIN-003` task as Attempt 3. `ARCH-007-ADMIN-004` remains blocked/pending until ADMIN-003 is architect-accepted `complete`.
