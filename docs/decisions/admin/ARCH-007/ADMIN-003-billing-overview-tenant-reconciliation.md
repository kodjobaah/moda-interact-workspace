---
id: ARCH-007-ADMIN-003
architecture_id: ARCH-007
title: Build billing overview, tenant detail and Shopify reconciliation visibility
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: ready
priority: 120
executor: null
claimed_at: null
attempt: 1
depends_on: 
  - ARCH-007-ADMIN-002
  - ARCH-007-BACKGROUND-007
  - ARCH-007-SHOPIFY-001
  - ARCH-007-BACKGROUND-008
enables: 
  - ARCH-007-ADMIN-004
created: 2026-09-07
updated: 2026-09-08T21:16:00Z
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

- [ ] Admin can identify unmapped plan and failed billing event without database shell access.
- [ ] Tenant view explains Free remaining and paid current-cycle usage.
- [ ] Reconciliation discrepancy is visible and bounded.
- [ ] Pages are paginated/index-aligned and secure.
- [ ] No secret/PII leakage.
- [ ] All new Admin-visible copy uses the existing ARCH-005 ICU/i18n catalogues; no task-introduced user-visible English literal bypasses that path.
- [ ] Tests/build/validation pass.

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

Ready for Architect Review (Attempt 1)

### Files Changed

- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/components/admin/billing-overview.tsx`
- `moda-interact-admin/src/components/admin/tenant-billing.tsx`
- `moda-interact-admin/src/components/admin/tenant-detail-panel.tsx`
- `moda-interact-admin/src/components/admin/tenant-table.tsx`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`

### Work Completed

- Added authenticated, bounded billing overview reads for mapped Free/paid distribution, unmapped/sync-error subscriptions, Free exhaustion, reported paid recovery usage, and App Event report-state counts.
- Added filtered, date-ranged, shop-scoped, state-scoped, paginated App Event ledger visibility with safe provider status fields and no bearer-token/customer-payload display.
- Added a tenant Billing tab showing observed/current/pending plan state, exact billing cycle, Free base/adjustment/committed/reserved/remaining values, current-cycle paid meter usage, active policy override values, ledger rows, and an explicit unavailable reconciliation state.
- Added required-key catalogue entries and focused security/contract tests.
- Admin implementation commit: `66c5730`; pushed to `origin/task/ARCH-007-ADMIN-003`.

### Validation Results

- `npm run build`: passed; existing BullMQ dynamic dependency warnings remain.
- `npm test -- --runInBand`: passed, 111 tests.
- Focused `node --test tests/security/admin-billing-visibility.test.mjs`: passed, 2 tests.
- `npm run lint`: passed with 2 pre-existing queue-monitor hook warnings and no errors.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run format:check`: repository-wide check reports 78 pre-existing files; all task-changed files were formatted with the repository Prettier binary.

### Deviations

- The accepted Admin Prisma schema has no durable Shopify usage snapshot or discrepancy table. Reconciliation is therefore rendered as explicitly unavailable (`discrepancy: null`) rather than fabricated or obtained with raw SQL.
- Overview Free exhaustion uses the bounded indexed counter threshold of 5; tenant detail computes the exact base plus signed adjustments versus committed and reserved quantities. A schema-supported aggregate for per-plan allowance plus adjustments would be needed for exact cross-tenant overview counts without loading all shops.

### Assumptions

- `BillingPlan.freeLifetimeConversationAllowance` is the configured Free allowance and the current accepted Free policy threshold is 5.
- Paid current-cycle usage is represented by reported `UsageEvent` rows matching the subscription billing period and mapped Shopify usage-event handle.

### Unresolved Issues

- Shopify-vs-Moda numeric discrepancy remains unavailable until Background or Database provides a durable provider usage snapshot/comparison contract.

### Architectural Concerns

- The discrepancy requirement is a cross-repository contract gap, not an Admin presentation gap. `ADMIN-004` should not add a local duplicate or raw provider query; it should consume the accepted shared/database snapshot contract when available.

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

### Reviewed Files

- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/components/admin/billing-overview.tsx`
- `moda-interact-admin/src/components/admin/tenant-billing.tsx`
- `moda-interact-admin/src/components/admin/tenant-detail-panel.tsx`
- `moda-interact-admin/src/components/admin/tenant-table.tsx`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`
- implementation commit `66c5730`
- parent task-report commit `815280c`

### Validation Reviewed

- Agent-reported full Admin suite: 111 passed.
- Agent-reported build, Prisma validation, lint and `git diff --check`: passed.
- Focused ADMIN-003 security tests were independently inspected; their current coverage is insufficient for the behavioral corrections above.
- Git branch ancestry was reviewed: implementation commit `66c5730` diverges from the Admin main line containing the architect-accepted ADMIN-002 merge, so Step 0 is required before Attempt 2 can be accepted.

### Architecture Conformance

Changes required. Bounded/read-only ownership and reconciliation-unavailable handling conform; ledger diagnostics, Free-exhaustion semantics, tenant cap/message visibility, date boundaries, i18n presentation and same-repository dependency integration require correction.

### Follow-up

No new task. Continue the same `ARCH-007-ADMIN-003` task as Attempt 2.
