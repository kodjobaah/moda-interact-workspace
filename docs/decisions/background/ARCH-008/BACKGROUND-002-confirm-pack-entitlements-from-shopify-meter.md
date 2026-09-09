---
id: ARCH-008-BACKGROUND-002
architecture_id: ARCH-008
title: Confirm recovery-credit pack entitlements from Shopify meter usage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-008-BACKGROUND-001
  - ARCH-008-SHOPIFY-001
  - ARCH-007-BACKGROUND-008
  - ARCH-007-BACKGROUND-009
  - ARCH-007-SHOPIFY-001
enables:
  - ARCH-008-ADMIN-001
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-BACKGROUND-002: Confirm recovery-credit pack entitlements from Shopify meter usage

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Stop granting recovery-credit packs from App Events transport success and activate exactly the provider-confirmed aggregate number of current-cycle pack purchases using Partner `activeSubscription` pack-meter usage.

## Architectural invariant

```text
UsageEvent.REPORTED alone MUST NOT activate a RecoveryCreditPurchase.
```

Shopify provider `usage.quantity` is an aggregate confirmation signal. It does not identify a particular App Events idempotency key. Implementation must not claim otherwise.

## Architect reconciliation preflight — completed 2026-09-09

The architecture preflight is complete.

Decision:

```text
DATABASE TASK REQUIRED: NO
SHOPIFY PRODUCER HARDENING REQUIRED: YES
```

The existing schema is sufficient because exact reconciliation can use:

```text
provider current cycle start/end
-> exact BillingPeriod [shopId, periodStart, periodEnd]
-> UsageEvent.billingPeriodId
-> UsageEvent metric/quantity/report state/meter
-> RecoveryCreditPurchase plan/meter/credits snapshots
-> RecoveryCreditPurchase status
```

`ARCH-008-SHOPIFY-001` now guarantees that every **new** pack UsageEvent enters
this flow with a non-null exact current `billingPeriodId` and matching
provider/local cycle boundaries.

Do not create a database migration.

If a legacy/unexpected row with null or wrong cycle identity is encountered,
never infer cycle membership from timestamps. Exclude it from activation and
surface the existing attention/diagnostic outcome.

## Required preflight — do before editing

1. Work only in the launcher-resolved ARCH-008-BACKGROUND-002 task worktree after normal synchronisation.
2. Confirm `ARCH-008-BACKGROUND-001` is Complete and its 409/submission behavior is present.
3. Confirm `ARCH-008-SHOPIFY-001` is Complete and the integrated Shopify
   purchase path now requires exact non-null current-cycle identity.
4. Confirm accepted ARCH-007 capability is present:
   - `src/services/billing-reconciliation.service.ts`;
   - `src/providers/shopify-partner-billing.provider.ts`;
   - recurring billing worker from ARCH-007-BACKGROUND-008;
   - recovery-credit transaction/counter logic from ARCH-007-BACKGROUND-009.
5. Confirm the Partner projection still exposes:
   - current billing cycle start/end;
   - current plan handle;
   - provider usage snapshots with meter handle + quantity.
6. Confirm the Prisma schema still exposes:
   - `BillingPeriod` unique by `shopId + periodStart + periodEnd`;
   - `UsageEvent.billingPeriodId`;
   - `UsageEvent.shopifyEventHandle`;
   - `RecoveryCreditPurchase.shopifyPlanHandleSnapshot`;
   - `RecoveryCreditPurchase.shopifyEventHandleSnapshot`;
   - `RecoveryCreditPurchase.creditsGranted`.
7. If any of those **previously verified** capabilities has disappeared after
   synchronisation, STOP and report source drift to `moda_architect`.
   Do not invent a replacement schema or heuristic.

## Primary files

Expected implementation boundary:

- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- accepted ARCH-007 Partner reconciliation service/provider equivalents
- focused recovery-credit/reconciliation unit tests

Do not create a second Partner billing client if ARCH-007 already provides one.

## Required implementation

### Reconciliation orchestration — normative

Replace the current global transport-state purchase activation order:

```text
publishDue()
-> reconcilePending()   # must be removed as an activation source
-> fetch Partner subscriptions
```

with:

```text
publishDue()
-> select bounded rotating shop page
-> for each shop:
     fetch Partner activeSubscription
     apply/sync exact current subscription + BillingPeriod
     resolve exact configured pack meter
     reconcile provider-confirmed pack units for that shop/current cycle/meter
     compare normal recovery usage
```

`RecoveryCreditPurchaseService.reconcilePending()` must no longer activate
`REPORTED` pack purchases merely from local transport state. Remove it from the
billing-worker activation path or refactor it so it cannot grant without an
explicit provider-confirmed budget.

Introduce/reuse one bounded provider-confirmed reconciliation operation with an
input equivalent to:

```text
shopId
billingPeriodId
providerPlanHandle
packMeterHandle
providerUnits
```

The operation must perform ACTIVE matched-unit counting, candidate selection,
ambiguity evaluation and all new grants inside one Serializable transaction so
concurrent reconciliation retries the entire budget calculation.


### A. Remove pack activation from App Events HTTP-success path

In the durable App Events publisher:

- remove the success-path dependency/callback that activates a `RECOVERY_CREDIT_PACK_PURCHASE` solely after `markReported`;
- leave successful UsageEvent transition to `REPORTED` intact;
- leave normal usage publication and retry semantics intact.

After 202:

```text
UsageEvent = REPORTED
RecoveryCreditPurchase = PENDING_BILLING
purchased credit counter unchanged
```

### B. Make RecoveryCreditPurchase activation provider-confirmation-only

Any existing public method such as `activateFromUsageEvent` / `activateForUsageEvent` that activates solely because linked UsageEvent is `REPORTED` must no longer be used as a transport-success activator.

Refactor narrowly so activation occurs only through the provider reconciliation path with an explicit confirmed-unit budget.

Keep the existing exactly-once durable transaction semantics:

- purchase transitions to ACTIVE once;
- `activatedAt` is set once;
- `PURCHASED_RECOVERY_CREDITS.grantedQuantity` is incremented once by that purchase's `creditsGranted` snapshot;
- repeated reconciliation cannot increment again.

Do not revoke ACTIVE purchases automatically if a later provider quantity falls below previously matched units. Surface discrepancy/attention instead.

### C. Provider aggregate calculation

For one **shop + provider current billing cycle + exact pack meter**:

```text
providerUnits = Partner activeSubscription pack usage.quantity
```

Validate before using:

- finite number;
- integer;
- >= 0;
- belongs to exact configured pack meter for the effective plan/current cycle.

If provider quantity is missing/non-finite/negative/non-integer or the meter cannot be identified exactly, activate nothing and route through the existing reconciliation attention/diagnostic outcome.

### D. Local matched/eligible sets

Calculate within the same shop/cycle/meter scope:

```text
alreadyMatchedUnits = count of ACTIVE pack purchases already matched for this provider cycle/meter
```

Each pack purchase represents one provider App Event unit regardless of `creditsGranted`.

Eligible pending candidates must satisfy **all** of:

- `RecoveryCreditPurchase.status == PENDING_BILLING` (or an accepted retryable attention state only if ARCH-007 explicitly allows safe re-entry);
- linked UsageEvent exists;
- linked UsageEvent metric is `RECOVERY_CREDIT_PACK_PURCHASE`;
- linked UsageEvent quantity is exactly `+1`;
- linked UsageEvent `shopifyReportState == REPORTED`;
- candidate belongs to the provider current billing cycle;
- candidate corresponds to the exact pack meter/effective plan configuration being reconciled;
- `RecoveryCreditPurchase.shopifyPlanHandleSnapshot` equals the current provider plan handle;
- `RecoveryCreditPurchase.shopifyEventHandleSnapshot` equals the exact pack meter;
- candidate is not already ACTIVE/cancelled.

Do not count a merely-created local purchase whose App Event was never submitted.

### E. Confirmed unit budget

```text
confirmedDelta = providerUnits - alreadyMatchedUnits
```

Rules:

1. `confirmedDelta <= 0`
   - activate no new purchases;
   - if `< 0`, surface provider-under-local discrepancy/attention; do not revoke.
2. `confirmedDelta == eligibleCandidateCount`
   - all eligible candidates are provider-covered; activate all deterministically.
3. `confirmedDelta > eligibleCandidateCount`
   - activate all eligible candidates only;
   - surface provider-over-local discrepancy for unmatched provider units;
   - do not fabricate local purchases.
4. `0 < confirmedDelta < eligibleCandidateCount`
   - provider confirms only a subset; apply the ambiguity rule below.

### F. Ambiguous partial matching rule

Shopify does not expose which App Event produced an aggregate unit. Therefore when only a subset is confirmed:

- order equivalent candidates deterministically by `createdAt ASC`, then `id ASC`;
- **but** do not arbitrarily choose across candidates whose entitlement value/configuration differs.

Define an equivalent candidate group as candidates that share all provider-relevant/configuration snapshots required to make one unit interchangeable, including at minimum the same effective pack-meter identity and same `creditsGranted` snapshot.

For partial confirmation:

- if every eligible candidate is equivalent, activate the earliest `confirmedDelta` candidates by `createdAt`, then `id`;
- if the partial boundary crosses candidates with different `creditsGranted` or different pack/meter/plan snapshots, **activate none from the ambiguous subset**, surface `NEEDS_ATTENTION`/reconciliation discrepancy, and require operator resolution;
- never choose the most valuable/least valuable/newest candidate heuristically.

If current accepted state already records a stronger deterministic provider correlation, use it only if it comes from a supported Shopify API and is documented in Completion Report. Do not invent correlation from request timing.

### G. Reconciliation replay and concurrency

Reuse the accepted ARCH-007 transaction/isolation/locking approach. The implementation must remain correct when:

- two billing reconciliation runs overlap;
- reconciliation is retried after process failure;
- provider quantity has not changed;
- a purchase is activated by the other transaction first.

The final durable counter must equal the sum of ACTIVE purchase `creditsGranted` snapshots, never double-counting the same purchase.

### H. Normal recovery isolation

Do not gate ordinary checkout recovery completion, customer messaging or paid-recovery UsageEvent creation on Partner reconciliation. Only **advance pack entitlement grant** waits for provider aggregate confirmation.

## Required tests

Add/adjust focused tests proving:

1. 202/`REPORTED` leaves pack PENDING and counter unchanged.
2. Provider quantity increment of 1 activates exactly one equivalent eligible pending purchase.
3. Re-running same provider quantity grants nothing twice.
4. Provider increment 2 activates two equivalent candidates deterministically.
5. Provider quantity lower than ACTIVE matched units revokes nothing and surfaces discrepancy.
6. Provider quantity greater than local eligible + active units fabricates nothing and surfaces discrepancy.
7. Partial confirmation across candidates with different `creditsGranted` fails closed for the ambiguous subset.
8. Non-REPORTED candidate is never activated.
9. Wrong cycle/wrong meter candidate is never consumed by current reconciliation.
10. Concurrent/replayed reconciliation remains exactly once.
11. Normal recovery path remains independent of provider reconciliation availability.

## Out of Scope / MUST NOT

- No database migration unless architect creates a separate database task after a reported gap.
- No Shopify app UI/plan-selection changes.
- No App Events endpoint redesign.
- No Admin layout work.
- No automatic credit clawback.
- No synthetic “provider confirmed event id” field based on local assumptions.
- No date-window approximation when durable billing-cycle identity is missing.
- No cross-repository edits.

## Acceptance Criteria

- [x] Transport success no longer activates a recovery-credit purchase.
- [x] Provider current-cycle exact pack-meter quantity is required for activation.
- [x] Aggregate matching never claims per-event Shopify confirmation.
- [x] Exact provider-confirmed unit budget is respected.
- [x] Equivalent partial candidates use deterministic `createdAt`, then `id` ordering.
- [x] Non-equivalent ambiguous partial matching fails closed.
- [x] ACTIVE purchase credit is granted exactly once under replay/concurrency.
- [x] Provider under/over-count discrepancies are surfaced without destructive correction/fabrication.
- [x] Normal recovery remains independent of reconciliation latency/failure.
- [x] No schema/cross-repository change is introduced silently.

## Validation — run from `moda-interact-background`

Run exact focused unit tests for changed services first, for example:

```bash
npx vitest run \
  tests/unit/services/recovery-credit-purchase.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts \
  <any-new-focused-test>
```

Use actual current filenames if accepted ARCH-007 uses different names.

Then run:

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

Do not invent a lint command if none exists.

## Stop / return rule

If preflight reveals a missing durable cycle/meter identity, return `blocked`/architectural concern with exact evidence instead of implementing a heuristic.

Otherwise, after successful implementation/validation:

1. complete Completion Report;
2. set status `review`;
3. return to `moda_architect`;
4. STOP.

Do not begin ADMIN-001.

## Completion Report

### Status

Review — attempt 2 implementation complete; awaiting architect acceptance.

### Files Changed

- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- `moda-interact-background/src/services/billing-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts`
- `moda-interact-background/tests/unit/services/billing-reconciliation.service.test.ts`

### Work Completed

Attempt 2 closes the architect-requested gaps. Linked UsageEvents are now scoped to the exact shop, billing period, and pack meter for both active matching and candidate selection. Repaired `NEEDS_ATTENTION` purchases re-enter only when their linked event is `REPORTED`, guarded activation permits only the accepted source states, and the returned activation count reflects successful durable transitions. Present Partner subscriptions without exact current-cycle boundaries now surface `invalid-scope` without activation. The focused harness honors nested predicates and covers excluded scope dimensions, repaired attention, exact pack-meter quantity, and overlapping replay. No schema or cross-repository change was introduced.

### Validation Results

Preflight and implementation evidence:

- Parent claim published at `ec8d703`; implementation worktree is clean before publication on `task/ARCH-008-BACKGROUND-002`.
- Focused tests passed: 3 files, 37 tests.
- `npm run build` passed, including Prisma client generation and TypeScript compilation.
- `npm run prisma:validate` passed against `database/prisma/schema.prisma`.
- `git diff --check` passed.
- Full `npm run test:unit` ran 43 files / 432 tests; 430 passed and 2 unrelated `pending-recovery-candidate.service.test.ts` tests failed.

### Deviations

The implementation branch is ready for architect review. The full suite retains two failures in `pending-recovery-candidate.service.test.ts` concerning checkout-context refresh behavior; those tests and their owning service are outside this task's changed files. No migration, schema repair, heuristic, or cross-repository change was introduced.

### Assumptions

No task-specific unresolved implementation issues. Full-suite residual risk is limited to the two unrelated pending-recovery-candidate failures noted above.

### Unresolved Issues

None.

### Architectural Concerns

None. The apparent divergence was resolved by initializing the implementation worktree's existing tracked database submodule.

## Architect Review

### Review Status

Accepted

### Review Notes

#### Attempt 2 — Accepted

`ARCH-008-BACKGROUND-002` is architect-accepted Complete.

Attempt 2 closes every correction requested after Attempt 1:

1. ACTIVE matched-unit counting and candidate selection now scope the linked
   `UsageEvent` to the exact shop, exact pack meter, exact BillingPeriod, metric
   `RECOVERY_CREDIT_PACK_PURCHASE`, quantity `+1`, and `REPORTED` transport state.
2. Accepted ARCH-007 repaired-attention compatibility is preserved: a
   `NEEDS_ATTENTION` purchase can re-enter only through the same exact provider
   scope after its linked UsageEvent is `REPORTED`, and activation remains
   exactly once.
3. A present Partner subscription without exact current-period boundaries now
   produces an `invalid-scope` reconciliation discrepancy and grants nothing.
4. `activatedCount` now counts successful durable state transitions rather than
   the number of selected candidates. The counter increment remains inside the
   same Serializable transaction and occurs only after a successful guarded
   transition.
5. Focused tests now exercise nested Prisma scope exclusions for non-REPORTED,
   wrong cycle, wrong/null UsageEvent meter and wrong UsageEvent shop; repaired
   attention re-entry; exact provider pack-meter quantity; missing provider
   cycle diagnostics; replay/overlap; and the existing transport-success
   no-activation boundary.

The normal recovery/customer-message path remains architecturally independent:
provider reconciliation is invoked from the dedicated billing reconciliation
entrypoint/scheduler, and this task changes no checkout/recovery/messaging worker
production path.

The two remaining full-suite failures are the documented unrelated
`pending-recovery-candidate.service.test.ts` baseline and are outside the six
changed task files. No schema, Shared contract, Shopify app, Admin, gateway or
other cross-repository change was introduced.

#### Attempt 1 — Changes Requested

The implementation correctly removes transport-success pack activation, moves
new entitlement grants behind Partner aggregate reconciliation, scopes the
budget to the current provider plan/BillingPeriod/purchase meter snapshots, uses
a Serializable transaction with retry, preserves deterministic ordering for
equivalent packs, and surfaces under/over/ambiguous provider discrepancies.
The implementation branch is also cleanly scoped to the expected Background
services/tests.

Attempt 1 nevertheless has correctness and required-regression gaps that must be
closed before acceptance.

Required corrections for Attempt 2:

1. **Scope the linked UsageEvent to the exact reconciliation shop and pack
   meter.**

   `RecoveryCreditPurchaseService.reconcileProviderConfirmed()` currently
   filters the purchase snapshot by `shopifyEventHandleSnapshot`, but its nested
   `usageEvent` predicate checks only metric, quantity, report state and
   `billingPeriodId`. The linked UsageEvent itself must also satisfy the exact
   reconciliation identity:

   - `usageEvent.shopId == input.shopId`;
   - `usageEvent.shopifyEventHandle == input.packMeterHandle`;
   - existing exact `billingPeriodId`, metric `RECOVERY_CREDIT_PACK_PURCHASE`,
     quantity `+1` and `REPORTED` checks remain.

   Apply the same exact nested scope to both ACTIVE matched-unit counting and
   pending/attention candidate selection. A wrong/null UsageEvent meter must
   never be consumed merely because the RecoveryCreditPurchase snapshot has the
   expected meter.

2. **Preserve ARCH-007's accepted repaired-attention re-entry.**

   `ARCH-007-BACKGROUND-009` explicitly accepted that a
   `RecoveryCreditPurchase.NEEDS_ATTENTION` may later become ACTIVE exactly once
   when its linked UsageEvent is repaired/retried and becomes `REPORTED`.
   Attempt 1 now selects only `PENDING_BILLING`, which strands those previously
   valid rows across the ARCH-008 rollout.

   For provider-confirmed reconciliation, treat the accepted repaired-attention
   state as eligible only when the linked UsageEvent is now `REPORTED` and all
   exact shop/cycle/plan/meter predicates pass. The guarded activation update
   must allow that same accepted source state. Do not make a non-REPORTED
   attention row eligible and do not invent any new retryable state.

3. **Do not silently suppress a present provider subscription with a missing
   current-cycle boundary.**

   `BillingReconciliationService.reconcilePackPurchases()` currently returns
   `{ activatedCount: 0, discrepancy: null }` whenever
   `currentPeriodStart/currentPeriodEnd` is absent. `provider == null` may
   legitimately mean no current contract, but a *present* Partner subscription
   without an exact current cycle is invalid reconciliation scope and must be
   surfaced through the existing discrepancy/attention path. Activate nothing
   and return/log an `invalid-scope` diagnostic (or the existing equivalent)
   rather than silently skipping it.

4. **Report the actual number of durable activations and prove overlapping
   reconciliation.**

   The reconciliation loop returns `activatedCount: selected.length` even when
   a guarded `updateMany()` returns zero for a selected candidate. Count only
   successful `PENDING_BILLING`/accepted repaired-attention -> `ACTIVE`
   transitions for the returned `activatedCount`. Preserve the exactly-once
   counter increment inside the same transaction.

   Add a deterministic overlap/concurrency regression proving two reconciliation
   attempts for the same provider quantity cannot double-grant and cannot report
   two successful activations for one durable transition. A Prisma `P2034`
   retry simulation is acceptable if it deterministically proves the intended
   Serializable retry path; do not weaken transaction isolation.

5. **Complete the required ARCH-008 reconciliation regression matrix.**

   The current purchase-test harness ignores the Prisma `where` predicate, so it
   cannot prove the task's exact scope exclusions. Strengthen the tests/harness
   so the following are explicit and meaningful:

   - non-`REPORTED` linked UsageEvent is not eligible;
   - wrong `billingPeriodId` is not eligible;
   - wrong/null linked `UsageEvent.shopifyEventHandle` is not eligible;
   - wrong linked UsageEvent shop is not eligible;
   - repaired `NEEDS_ATTENTION` + `REPORTED` re-enters and activates exactly once;
   - present Partner subscription with missing current-cycle boundary surfaces
     invalid scope and activates nothing;
   - provider pack usage is passed as the exact pack-meter quantity (update the
     B008-R6 fixture to contain the pack meter and assert the concrete quantity,
     rather than `expect.any(Number)` which also accepts `NaN`-typed values);
   - overlapping/replayed reconciliation remains exactly once;
   - preserve a focused proof that normal recovery/customer messaging does not
     become dependent on Partner reconciliation. If the existing separate-worker
     boundary already proves this, a structural regression is sufficient and no
     recovery production-code change is requested.

   Keep the existing equivalent-pack deterministic ordering, under/over
   discrepancy, invalid-provider-units, transport `REPORTED` semantics, build,
   Prisma validation and full-suite baseline coverage.

No database migration, Shared contract change, Shopify app change, Admin change,
new provider client, timestamp heuristic or entitlement clawback is requested.
Keep all corrections on this same task and mirrored branch pair.

### Reviewed Files

- `src/services/shopify-usage-event-publisher.service.ts`
- `src/services/recovery-credit-purchase.service.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/providers/shopify-partner-billing.provider.ts` (read-only contract verification)
- `tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `tests/unit/services/recovery-credit-purchase.service.test.ts`
- `tests/unit/services/billing-reconciliation.service.test.ts`
- `database/prisma/schema.prisma` (read-only architecture verification)
- `docs/decisions/background/ARCH-007/BACKGROUND-009-activate-consume-recovery-credit-packs.md`
- `docs/decisions/background/ARCH-008/BACKGROUND-002-confirm-pack-entitlements-from-shopify-meter.md`
- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- `docs/architecture/ARCH-008-recovery-credit-reconciliation-preflight-2026-09-09.md`

### Validation Reviewed

- Published implementation commit `c90aa39` inspected.
- GitHub branch comparison: `task/ARCH-008-BACKGROUND-002` is one commit ahead
  of Background `main`, zero behind, with only the six authorised service/test
  files changed.
- Published parent report commit `29e0bd6` inspected; parent task branch is
  based on current workspace `main` and contains only task-report history.
- Completion Report: 3 focused files / 29 tests passed.
- Completion Report: `npm run build` passed.
- Completion Report: `npm run prisma:validate` passed against the initialized
  tracked database submodule at `ebe43c0`.
- Completion Report: `git diff --check` passed.
- Completion Report: full unit suite 422/424 passed; the two
  `pending-recovery-candidate.service.test.ts` failures match the pre-existing
  unrelated Background baseline and are outside this task's changed files.
- Review archive inspected directly. It contains no `node_modules`, so tests
  were not independently rerun in the review container.

### Architecture Conformance

Accepted.

Attempt 2 conforms to ARCH-008 provider-confirmed pack entitlement semantics:
App Events `REPORTED` remains transport submission only; provider aggregate
current-cycle pack-meter quantity is the entitlement confirmation input; local
matching is exact and deterministic; ambiguous/non-matching scope fails closed;
provider under/over discrepancies do not revoke or fabricate purchases; and
activation/counter grant is exactly-once under the existing Serializable retry
boundary.

Attempt 1 was Partial before the corrections recorded above.
 The core provider-confirmed budget architecture is implemented and
transport acknowledgement no longer grants credits. Conformance remains
incomplete because the linked UsageEvent is not scoped to the exact pack meter
(and shop), accepted ARCH-007 repaired-attention re-entry is lost, a present
provider subscription with no current cycle is silently skipped, and the
required exact-scope/concurrency/isolation regression matrix is incomplete.

### Follow-up

`ARCH-008-ADMIN-001` is now dependency-eligible and may remain/be promoted
`ready`. Do not begin ADMIN-002 until ADMIN-001 is architect-accepted Complete.
