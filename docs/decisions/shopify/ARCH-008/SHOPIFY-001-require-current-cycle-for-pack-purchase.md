---
id: ARCH-008-SHOPIFY-001
architecture_id: ARCH-008
title: Require an exact current billing cycle for recovery-credit pack purchases
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 25
executor: copilot
claimed_at: 2026-09-09T16:18:00Z
attempt: 2
depends_on:
  - ARCH-007-SHOPIFY-004
enables:
  - ARCH-008-BACKGROUND-002
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-SHOPIFY-001: Require an exact current billing cycle for recovery-credit pack purchases

## Architecture

Canonical:

- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- `docs/architecture/ARCH-008-recovery-credit-reconciliation-preflight-2026-09-09.md`

## Objective

Ensure every newly created recovery-credit-pack UsageEvent has an exact durable
Shopify current-billing-cycle identity before it can enter asynchronous App
Events/reconciliation.

This task hardens the accepted ARCH-007-SHOPIFY-004 producer. It does not change
pricing, pack size, App Events publication or purchased-credit activation.

## Architectural invariant

A **new** recovery-credit pack must never be created with:

```text
UsageEvent.billingPeriodId = null
```

and must never be attached to a stale/local billing period whose boundaries do
not equal Shopify Partner `activeSubscription.currentBillingCycle`.

Existing-purchase idempotent replay remains independent from current provider
availability.

## Why this task exists

The accepted SHOPIFY-004 implementation permits ACTIVE or TRIALING subscriptions
and currently copies:

```text
billingPeriodId: currentSubscription.billingPeriodId
```

without requiring that value to be non-null.

The provider also exposes `currentPeriodStart/currentPeriodEnd`, but the current
pack request checks plan/meter identity only.

ARCH-008 provider reconciliation requires exact current-cycle identity; it must
not recover cycle membership later from timestamps.

## Required preflight

1. Work only in the launcher-resolved `ARCH-008-SHOPIFY-001` task worktree.
2. Confirm accepted ARCH-007-SHOPIFY-004 behavior is present, including:
   - early existing-purchase replay;
   - provider plan/meter verification outside the Prisma write transaction;
   - transactional re-read of current subscription/plan;
   - Shared canonical Shopify usage idempotency helper;
   - independent purchased-credit balance presentation.
3. Confirm `ProviderSubscription` still exposes:
   - `currentPeriodStart`;
   - `currentPeriodEnd`.
4. Confirm Subscription still links to BillingPeriod through `billingPeriodId`.
5. If those accepted capabilities are absent after normal synchronisation, STOP
   with exact evidence. Do not recreate SHOPIFY-004.

## Primary files

Expected implementation boundary:

- `app/services/billing/billing.service.ts`
- `app/routes/app.billing.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`

Use actual equivalent filenames only if current accepted source has been renamed.

No database, Background, Admin or Shared repository edits are allowed.

## Required implementation

### A. Preserve existing replay ordering

Keep:

```text
validate intent + purchaseId
-> existing RecoveryCreditPurchase lookup
-> same-shop existing purchase returns immediately
```

This must remain before provider/current-cycle admission checks.

Do not make replay of an existing durable purchase depend on Shopify being
reachable.

### B. Require exact local current-cycle identity

Before provider verification for a **new** purchase require all of:

```text
subscription.status = ACTIVE or TRIALING
subscription.billingPeriodId != null
subscription.currentPeriodStart != null
subscription.currentPeriodEnd != null
subscription.billingPeriod exists
subscription.billingPeriod.id == subscription.billingPeriodId
subscription.billingPeriod.periodStart == subscription.currentPeriodStart
subscription.billingPeriod.periodEnd == subscription.currentPeriodEnd
```

If any condition fails:

```text
create no UsageEvent
create no RecoveryCreditPurchase
grant no entitlement
```

Fail closed with a bounded billing-domain error.

Do not infer a period from `new Date()`, `occurredAt`, trial end or plan cadence.

### C. Require provider/local current-cycle equality

The provider subscription used for the existing plan/meter verification must
also satisfy:

```text
provider.currentPeriodStart != null
provider.currentPeriodEnd != null
provider.currentPeriodStart == local currentPeriodStart
provider.currentPeriodEnd == local currentPeriodEnd
```

Continue to require the accepted plan-handle and meter-handle checks.

A provider subscription with no current billing cycle is not eligible for a
new pack purchase.

### D. Revalidate inside the write transaction

After provider verification and the existing transactional replay check,
re-read current Subscription + BillingPeriod + BillingPlan and require:

```text
same billingPeriodId
same periodStart
same periodEnd
same provider-verified current cycle
same plan handle
same pack meter
same creditsGranted
```

If any of those facts changed:

```text
rollback
create nothing
```

### E. Persist non-null exact cycle identity

Only after the transactional checks pass create:

```text
UsageEvent.metric = RECOVERY_CREDIT_PACK_PURCHASE
UsageEvent.quantity = +1
UsageEvent.billingPeriodId = exact current BillingPeriod.id
UsageEvent.shopifyEventHandle = exact pack meter
UsageEvent.shopifyReportState = PENDING
```

The linked RecoveryCreditPurchase snapshots remain unchanged.

Do not change Shopify App Events quantity/economics.

### F. Merchant purchase eligibility

Purchased-credit **balance** remains visible independently.

The **Buy recovery-credit pack** action must only be rendered when:

```text
existing safe plan/meter conditions
AND exact current local BillingPeriod exists
AND provider current cycle is present
AND provider/local current-cycle boundaries match
```

Do not hide existing purchased credit balance during a trial or sync gap.

If the repository already has an appropriate purchase-eligibility field, extend
it. Otherwise add one bounded server-derived boolean; do not expose provider
credentials or raw billing payloads to the browser.

## Required tests

Add/adjust focused tests proving:

1. existing same-shop purchase replay succeeds before provider/cycle checks;
2. ACTIVE subscription + matching local/provider cycle creates one pending pack
   UsageEvent with the exact non-null `billingPeriodId`;
3. local `billingPeriodId = null` creates no UsageEvent/purchase;
4. missing local current period boundary creates no UsageEvent/purchase;
5. provider current cycle missing creates no UsageEvent/purchase;
6. provider/local cycle boundary mismatch creates no UsageEvent/purchase;
7. transaction re-read observes changed billingPeriodId/boundary and rolls back;
8. plan/meter/pack-size freshness checks from SHOPIFY-004 remain intact;
9. purchased-credit balance remains visible when purchase eligibility is false;
10. Buy form is hidden when no exact current cycle is available;
11. no entitlement counter is updated by this request path.

## Out of Scope / MUST NOT

- No Prisma schema/migration.
- No Background reconciliation implementation.
- No App Events publisher change.
- No pricing or pack-size redesign.
- No manual Billing API / one-time purchase API.
- No date-window inference.
- No removal of existing purchased credits during trial.
- No cross-repository edits.

## Acceptance Criteria

- [x] Every newly created pack UsageEvent has a non-null exact billingPeriodId.
- [x] Provider and local current-cycle boundaries must match before creation.
- [x] Stale cycle changes are caught inside the write transaction.
- [x] Existing purchase replay remains provider-independent.
- [x] Trial/no-current-cycle state cannot create a new pack purchase.
- [x] Existing purchased balance remains visible.
- [x] No entitlement is granted by the request path.
- [x] No schema/cross-repository change is introduced.

## Validation

Run focused tests first:

```bash
npm test -- --run \
  tests/unit/services/billing.service.test.ts \
  tests/unit/billing-ui.test.ts
```

Then use the repository's existing validation commands:

```bash
npm run typecheck
npm run build
git diff --check
```

If repository-wide typecheck retains documented pre-existing unrelated
diagnostics, record them exactly and prove no new touched-file diagnostic was
introduced.

Do not invent a lint command if the current package does not define one.

## Stop / return rule

After implementation and validation:

1. complete Completion Report;
2. set status `review`;
3. return to `moda_architect`;
4. STOP.

Do not begin `ARCH-008-BACKGROUND-002`.

## Completion Report

### Status

Implemented and ready for architect review.

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/routes/app.billing.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`

### Work Completed

Attempt 2 correction checklist:

- [x] Perform local durable-cycle admission before calling Shopify.
- [x] Capture and compare the pre-provider BillingPeriod identity inside the transaction.
- [x] Add explicit local-null, missing-boundary, provider-null, provider-mismatch, and transaction-drift regressions.
- [x] Strengthen server-derived eligibility and UI balance/Buy-form regressions.
- [x] Record complete start-of-attempt synchronization and Git/worktree evidence.

Implemented correction details:

- Split local durable BillingPeriod validation from provider-cycle comparison.
- Captured the pre-provider BillingPeriod ID and required the transactional re-read to retain that identity and matching boundaries.
- Added explicit no-provider-call coverage for invalid local cycles and no-purchase/no-UsageEvent assertions for every rejection path.
- Added UI coverage proving server-derived ineligibility hides the Buy form while preserving purchased balance presentation.

### Validation Results

- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/billing-ui.test.ts`: passed, 40 tests.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: exits nonzero on existing legacy JSX and test-fixture diagnostics; no diagnostics were reported for changed production files.

### Deviations

- No schema, migration, Background, Admin, Shared, pricing, App Events, or entitlement changes.

### Assumptions

- The accepted Subscription projection continues to include `billingPeriod` whenever `billingPeriodId` is populated.

### Unresolved Issues

- Repository-wide typecheck remains blocked by existing diagnostics outside the changed production files.

### Architectural Concerns

- None identified.

### Git / VCS

Task branch: `task/ARCH-008-SHOPIFY-001`

Physical worktree isolation:

   canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
   parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-008-SHOPIFY-001`
   parent branch: `task/ARCH-008-SHOPIFY-001`
   implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-008-SHOPIFY-001`
   implementation branch: `task/ARCH-008-SHOPIFY-001`
   shared workspace checkout switched/mutated for task work: no
   shared implementation checkout switched/mutated for task work: no
   another task worktree reused: no

Start-of-attempt synchronization:

   parent remote task branch fast-forward: already up to date
   parent `origin/main` merge: already unnecessary
   implementation remote task branch fast-forward: already up to date
   implementation `origin/main` merge: already unnecessary
   unexpected divergence/conflict: none

Implementation repository:

   repository: `moda-interact`
   correction commit: `3960b75`
   remote branch: `origin/task/ARCH-008-SHOPIFY-001`
   pushed: yes

Parent workspace:

   task file: `docs/decisions/shopify/ARCH-008/SHOPIFY-001-require-current-cycle-for-pack-purchase.md`
   claim commit: `5482bf8`
   remote branch: `origin/task/ARCH-008-SHOPIFY-001`
   completion-report commit: pending
   submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested

### Review Notes

#### Attempt 1 — Changes Requested

The implementation is directionally correct and preserves the ARCH-007 pack
purchase model, early provider-independent replay, provider/local cycle matching,
non-null persisted `billingPeriodId`, and no request-path entitlement grant.
However, Attempt 1 does not yet satisfy the complete ARCH-008-SHOPIFY-001
contract.

Required corrections for Attempt 2:

1. **Perform local durable-cycle admission before the Shopify provider call.**
   For a new purchase, validate the local Subscription + BillingPeriod invariant
   before `getActiveSubscription()`:
   - `billingPeriodId != null`;
   - `currentPeriodStart != null`;
   - `currentPeriodEnd != null`;
   - linked BillingPeriod exists and its id equals `billingPeriodId`;
   - linked BillingPeriod boundaries equal the Subscription current-period
     boundaries.

   The current implementation combines local and provider validation in
   `hasMatchingBillingCycle()` only *after* the provider call. This violates the
   task's required ordering and causes a locally invalid request to contact
   Shopify unnecessarily. Add a regression proving the provider is not called
   when local durable-cycle admission fails.

2. **Revalidate the exact billing-period identity inside the write
   transaction.** Capture the provider-verified local `billingPeriodId` from the
   pre-provider admission state and require the transactional re-read to retain
   that same id. The current transaction only calls
   `hasMatchingBillingCycle(currentSubscription, providerSubscription)`. That
   proves the re-read relation/boundaries still match the provider cycle, but it
   does not explicitly prove `currentSubscription.billingPeriodId` is the same
   durable identity that was verified before the provider call, as required by
   section D of this task.

   Add regressions for a changed transactional `billingPeriodId` and for changed
   transactional cycle boundaries. Both must roll back with no UsageEvent or
   RecoveryCreditPurchase.

3. **Complete the required current-cycle rejection matrix.** Focused tests must
   explicitly prove, rather than infer from one all-null case:
   - local `billingPeriodId = null`;
   - a missing local current-period boundary;
   - provider current cycle missing;
   - provider/local current-cycle boundary mismatch;
   - transactional billing-period identity/boundary drift.

   Each case must prove no UsageEvent and no RecoveryCreditPurchase are created.

4. **Strengthen merchant eligibility/presentation regressions.** The existing
   `billing-ui.test.ts` source-order assertion predates this ARCH-008 boolean and
   does not prove the new contract. Add focused coverage proving:
   - `recoveryCreditPackPurchaseEligible` is false when the exact current cycle
     is unavailable or mismatched;
   - the Buy form is not rendered in that state;
   - the already-purchased credit balance remains presented independently when
     new-pack eligibility is false.

5. **Add the mandatory Git/worktree evidence to the Completion Report.** The
   supplied Completion Report omits the physical worktree isolation and
   start-of-attempt synchronization evidence required by
   `docs/agent-worktree-isolation-policy.md`, and it also omits the canonical
   Git/VCS evidence block. Missing evidence is workflow non-conformance.

   If Attempt 1 actually ran in the launcher-resolved dedicated parent and
   implementation worktrees, record those exact paths/branches and the
   synchronization results, then rerun the required validation from the
   canonical implementation worktree before returning to review. If it did not,
   restore/create the canonical task worktrees, check out the already-pushed
   `task/ARCH-008-SHOPIFY-001` branches there, rerun validation, and correct the
   Completion Report. Do not create code churn solely to manufacture another
   implementation commit.

No database, Background, Admin, Shared, pricing, pack-size, App Events publisher
or entitlement-lifecycle redesign is requested. Keep the correction on this
same task and same branch pair.

### Reviewed Files

- `app/services/billing/billing.service.ts`
- `app/routes/app.billing.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`
- `database/prisma/schema.prisma` (read-only architecture verification)
- `docs/decisions/shopify/ARCH-008/SHOPIFY-001-require-current-cycle-for-pack-purchase.md`
- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- `docs/agent-worktree-isolation-policy.md`

### Validation Reviewed

- Completion Report: focused suite reports 34 passing tests.
- Completion Report: build passed.
- Completion Report: `git diff --check` passed.
- Completion Report: repository-wide typecheck retains unrelated baseline
  diagnostics and reports no changed-production-file diagnostic.
- Review archive: source/test implementation inspected directly.
- Review archive has no usable implementation Git metadata and no `node_modules`,
  so commit ancestry, remote pushes, physical worktree state and an independent
  test rerun could not be verified from the archive itself.

### Architecture Conformance

Partial. The producer now fails closed for provider/local cycle mismatch and
persists a non-null cycle identity when creation succeeds, while replay remains
provider-independent and no entitlement counter is mutated. Conformance remains
incomplete because local durable-cycle admission occurs after provider access,
transactional freshness does not explicitly retain the same pre-provider
`billingPeriodId`, the ARCH-008 cycle/merchant-eligibility regression matrix is
incomplete, and mandatory worktree evidence is absent.

### Follow-up

Return `ARCH-008-SHOPIFY-001` to the same `moda_app` execution path for Attempt
2. `ARCH-008-BACKGROUND-002` remains Pending until this task is architect-
accepted Complete.
