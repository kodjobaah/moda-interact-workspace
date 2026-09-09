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
status: complete
priority: 25
executor: null
claimed_at: null
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

Accepted

### Review Notes

#### Attempt 1 — Changes Requested

Attempt 1 was directionally correct but required five bounded corrections: local
durable-cycle admission before provider access, exact BillingPeriod identity
revalidation inside the write transaction, the explicit current-cycle rejection
matrix, stronger merchant eligibility/presentation regression coverage, and
mandatory worktree/synchronisation evidence.

#### Attempt 2 — Accepted

Attempt 2 closes the requested gaps without broadening the ARCH-008 producer
scope.

Accepted findings:

1. New-purchase local durable-cycle admission now occurs before Shopify access.
   `hasDurableBillingPeriod(...)` requires the non-null local BillingPeriod id,
   Subscription current-period boundaries, linked BillingPeriod identity and
   exact boundary equality. Invalid local state fails closed before
   `getActiveSubscription(...)`.
2. Provider verification still requires the accepted plan/meter mapping and now
   requires provider current-cycle boundaries to equal the verified local cycle.
3. The pre-provider `billingPeriodId` is captured and passed into the
   transactional freshness check. A replacement BillingPeriod with identical
   dates is therefore rejected, as is boundary drift.
4. Successful creation persists the exact non-null transactional BillingPeriod
   id while preserving quantity `+1`, the pack meter, `PENDING` report state and
   the existing Shared Shopify usage idempotency helper.
5. Existing same-shop durable purchase replay remains before provider/current-
   cycle admission, so replay remains provider-independent.
6. The request path still does not grant `PURCHASED_RECOVERY_CREDITS`; entitlement
   activation remains owned by the dependent Background reconciliation task.
7. Merchant presentation keeps purchased-credit balance independent from new-
   purchase eligibility, and the Buy form is guarded by the server-derived exact
   current-cycle eligibility boolean plus the existing pack/meter checks.
8. Focused regressions now cover local null/missing boundary, provider missing/
   mismatched cycle, transaction BillingPeriod identity/boundary drift, and
   balance visibility while purchase eligibility is false.
9. No schema, Background, Admin, Shared, pricing, pack-size or App Events publisher
   change was introduced.

GitHub review verified implementation commit `3960b75` as the tip of
`task/ARCH-008-SHOPIFY-001`, directly following Attempt 1 commit `37f4a93`. The
implementation branch is two commits ahead of `main`, zero behind, and its full
diff is limited to the four authorised Shopify files. The parent task branch tip
is Completion Report commit `2355395`.

The combined review archive intentionally excludes `.git`, so physical execution
inside the recorded macOS worktree paths cannot be reconstructed from the ZIP
alone. The Completion Report now supplies the mandatory canonical parent and
implementation worktree paths plus start-of-attempt synchronisation evidence,
and the review archive structure is consistent with the documented combined
worktree helper contract. No contradictory workflow evidence was found.

### Reviewed Files

- `app/services/billing/billing.service.ts`
- `app/routes/app.billing.tsx`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/billing-ui.test.ts`
- `docs/decisions/shopify/ARCH-008/SHOPIFY-001-require-current-cycle-for-pack-purchase.md`
- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- `docs/architecture/ARCH-008-recovery-credit-reconciliation-preflight-2026-09-09.md`
- `docs/agent-worktree-isolation-policy.md`
- `docs/development-baseline.md`

### Validation Reviewed

- Focused suite reported by the implementing agent: 40 tests passed.
- Build reported passed.
- `git diff --check` reported passed.
- Repository-wide typecheck remains non-zero in the documented
  `TYPECHECK-001` baseline; Completion Report states changed production files
  introduced no diagnostic.
- Independent source/test inspection completed from the combined review archive.
- GitHub commit inspection confirmed implementation commit `3960b75` and parent
  Completion Report commit `2355395` are published on the expected task branches.
- GitHub branch comparison confirmed the implementation branch modifies only the
  four task-authorised files.
- The archive excludes `node_modules`, so the focused suite/build/typecheck could
  not be independently rerun in the review container.

### Architecture Conformance

Conforms. ARCH-008-SHOPIFY-001 now provides the exact durable provider/local
current-cycle identity required by downstream provider aggregate reconciliation,
while preserving provider-independent replay, existing App Events economics and
the ownership boundary that defers purchased-credit activation to Background.

### Follow-up

`ARCH-008-SHOPIFY-001` is architect-accepted Complete.

All dependencies of `ARCH-008-BACKGROUND-002` are now Complete, so promote
`ARCH-008-BACKGROUND-002` from Pending to Ready for `moda_background`. Do not
start `ARCH-008-ADMIN-001` until BACKGROUND-002 is architect-accepted Complete.
