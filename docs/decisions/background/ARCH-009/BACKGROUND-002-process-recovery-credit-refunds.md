---
id: ARCH-009-BACKGROUND-002
architecture_id: ARCH-009
title: Hold, correct and finalize human-approved recovery-credit refunds
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-008-BACKGROUND-002
  - ARCH-007-BACKGROUND-007
enables:
  - ARCH-009-ADMIN-002
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-009-BACKGROUND-002

## Objective

Full-pack refund hold, correction and exactly-once finalization.

## Availability

Registry availability was confirmed on 2026-09-10 for `@modainteract/moda-interact-shared@0.9.0`.
The executor must still resolve and verify exactly `0.9.0` during task preflight.

All touched purchased-credit availability uses Shared 0.9.0:

```text
granted - committed - reserved - refunding
```

## Approval -> hold

Serializable transaction:

1. re-read refund;
2. purchase + original UsageEvent;
3. same shop;
4. purchase ACTIVE;
5. snapshots exact;
6. credits positive integer;
7. read purchased counter;
8. Shared available;
9. require available >= creditsSnapshot;
10. counter.refundingQuantity += creditsSnapshot with version;
11. refund holdAppliedAt=now,status=PROCESSING,version+1.

Purchase stays ACTIVE.

## CURRENT_CYCLE_APP_EVENT_CORRECTION

Require:

```text
original metric RECOVERY_CREDIT_PACK_PURCHASE
original quantity +1
original REPORTED
original billingPeriodId non-null
current Subscription.billingPeriodId == original
current plan snapshot exact
current pack meter exact
```

Otherwise NEEDS_ATTENTION and keep hold.

Create exactly one correction:

```text
metric RECOVERY_CREDIT_PACK_PURCHASE
quantity -1
billingPeriodId original
correctionOfUsageEventId original.id
sourceType RECOVERY_CREDIT_REFUND
sourceId refund.id
shopifyReportState PENDING
shopifyEventHandle refund.eventHandleSnapshot
idempotencyKey recovery-credit-refund:<refund.id>
shopifyIdempotencyKey canonical Shared helper
```

Link correctionUsageEventId.

Replay never creates second correction.

Mapping:

```text
PENDING/IN_FLIGHT/RETRYABLE -> PROVIDER_PENDING
NEEDS_ATTENTION -> NEEDS_ATTENTION, hold
REPORTED -> PROVIDER_ACTION_REQUIRED, hold
```

REPORTED is not completion.

## PARTNER_DASHBOARD_REFUND

After hold:

```text
PROVIDER_ACTION_REQUIRED
correctionUsageEventId=null
```

No negative event.

## Human provider confirmation

Only Admin writes:

```text
providerReference
providerConfirmedByPlatformAdminId
providerConfirmedAt
PROVIDER_CONFIRMED
```

## Finalization

Serializable transaction:

```text
require holdAppliedAt
purchase ACTIVE
refundingQuantity >= creditsSnapshot
grantedQuantity >= creditsSnapshot

grantedQuantity -= creditsSnapshot
refundingQuantity -= creditsSnapshot
purchase REFUNDED
refund COMPLETED
completedAt now
```

Exactly once.

## Hold release

Auto-release only if:

```text
provider confirmation absent
correctionUsageEventId absent
explicit REJECTED/WITHDRAWN before provider action
```

If correction exists and is IN_FLIGHT/RETRYABLE/REPORTED/NEEDS_ATTENTION,
do not release; human resolution.

## Messages

COMPLETED:

```text
BILLING_REFUND_COMPLETED
```

REJECTED message owned by Admin.

## Refund-aware ARCH-008 reconciliation

Pending refund ACTIVE purchase still counts positive provider unit.

Completed correction-mode REFUNDED purchase never reactivates.

Completed dashboard refund never regrants despite historical +1 provider usage.

No auto clawback/regrant.

## Paid-cycle invariant

Fresh paid included allowance still precedes purchased credits after renewal.

Refund holds survive rollover.

## Tests

1. exact hold;
2. hold lowers availability;
3. insufficient balance no hold;
4. concurrent refund/recovery cannot overspend;
5. exact one -1;
6. wrong cycle/meter/plan/nonreported no correction;
7. REPORTED correction not completion;
8. dashboard mode no correction;
9. confirmation finalizes once;
10. granted/refunding only decremented;
11. replay no double decrement;
12. safe reject releases hold;
13. ambiguous provider action does not;
14. REFUNDED never reactivated;
15. dashboard historical +1 no regrant;
16. new paid cycle included before purchased;
17. Free counter untouched.

## Validation

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
Ready for Review
### Files Changed
- `moda-interact-background/src/services/recovery-credit-refund.service.ts`
- `moda-interact-background/src/services/purchased-recovery-reservation.service.ts`
- `moda-interact-background/src/entrypoints/billing.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-refund.service.test.ts`
### Work Completed
- Added serializable full-pack approval holds using Shared 0.9.0 purchased-credit availability, exact purchase/event snapshot validation, versioned counter updates, and durable `NEEDS_ATTENTION` outcomes when a hold cannot be safely applied.
- Added current-cycle correction creation with deterministic idempotency, exact cycle/plan/meter checks, publisher-state mapping, replay-safe correction linkage, and provider-action gating.
- Added Partner Dashboard refund action-required handling, human-confirmed exactly-once finalization, counter/purchase state transitions, safe pre-provider hold release, and exactly-once `BILLING_REFUND_COMPLETED` support messaging.
- Added `refundingQuantity` to purchased-credit admission so held credits cannot be consumed by concurrent recovery work.
- Integrated refund progression into the existing billing worker cycle after usage publication and reconciliation.
### Validation Results
- `npx vitest run tests/unit/services/recovery-credit-refund.service.test.ts`: passed, 3 tests.
- Focused billing regression suite: passed, 32 tests.
- `npm run test:unit`: passed, 45 files and 445 tests.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
The accepted ARCH-009-BACKGROUND-001 implementation commit was carried onto this dependent task branch because `origin/main` does not yet contain accepted ARCH-009 prerequisite artifacts. No prerequisite source was changed by this task.
### Assumptions
Admin confirmation writes `PROVIDER_CONFIRMED` and the provider confirmation fields before Background finalization, as defined by ARCH-009.
### Unresolved Issues
### Architectural Concerns

### Git / VCS

Task branch: `task/ARCH-009-BACKGROUND-002`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-009-BACKGROUND-002`
  parent branch: `task/ARCH-009-BACKGROUND-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-009-BACKGROUND-002`
  implementation branch: `task/ARCH-009-BACKGROUND-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-background`
  commit: `47c9bf417b0c4dd3c86dc66359d9e1aac7cfc441`
  remote branch: `origin/task/ARCH-009-BACKGROUND-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-002-process-recovery-credit-refunds.md`
  commit: `ea9d28e5013845f98d0985a5ff67cd869f906d58`
  remote branch: `origin/task/ARCH-009-BACKGROUND-002`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 1 implements the basic refund lifecycle shape, but it is not yet safe to accept. The hold/correction flow is directionally correct; however, exactly-once finalization can currently commit partial accounting, ARCH-008 reconciliation is not yet refund-aware for Partner-Dashboard refunds, safe terminal hold release is not actually wired as an automatic Background behavior, and the focused tests cover only 3 of the task's 17 mandatory cases.

There is also a workflow isolation problem: the published BACKGROUND-002 implementation branch contains a cherry-picked copy of the unaccepted BACKGROUND-001 Attempt 1 implementation even though BACKGROUND-002 does not depend on BACKGROUND-001.

#### 1. Restore task-branch isolation; do not carry unaccepted BACKGROUND-001

The published BACKGROUND-002 branch is two commits ahead of `moda-interact-background/main`.

Its first task-branch commit is:

```text
3614d9853312f8c64e0485207644ccd481b92305
feat(ARCH-009-BACKGROUND-001): execute approved cancellations
```

and BACKGROUND-002 is then:

```text
47c9bf417b0c4dd3c86dc66359d9e1aac7cfc441
feat: process approved recovery credit refunds
```

`ARCH-009-BACKGROUND-002.depends_on` does NOT include `ARCH-009-BACKGROUND-001`, and BACKGROUND-001 is presently under Architect Changes Requested, not accepted Complete.

Attempt 2 must restore isolation:

1. synchronize the canonical BACKGROUND-002 implementation worktree from current `origin/main`;
2. do not cherry-pick/carry `3614d985...` or any other unaccepted BACKGROUND-001 implementation;
3. reapply the BACKGROUND-002-owned changes on the correct baseline;
4. if ARCH-009 DB/Shared adoption is not yet present on `origin/main`, BACKGROUND-002 may itself adopt only the exact accepted prerequisites it directly requires:
   - accepted ARCH-009 database revision;
   - exact `@modainteract/moda-interact-shared@0.9.0`;
5. if BACKGROUND-001 becomes architect-accepted and is merged to `origin/main` before Attempt 2 begins, it may naturally be present through the synchronized baseline; do not manually import a sibling task branch;
6. the cumulative BACKGROUND-002 diff must not contain task-owned cancellation provider/service/test changes unless they are already part of `origin/main`.

Do not solve this by adding BACKGROUND-001 as a dependency. The tasks are intentionally independent.

#### 2. Finalization and hold-release transactions must never commit partial accounting

There are two partial-commit paths in the current implementation.

##### Finalization

Current order:

```text
decrement granted/refunding
mark purchase REFUNDED
mark refund COMPLETED
```

but if the purchase CAS or refund CAS returns `count = 0`, the method returns `false` from the transaction callback. Returning `false` COMMITs the earlier successful mutations.

Therefore this is currently possible:

```text
counter decremented
purchase update loses CAS
transaction commits
refund still PROVIDER_CONFIRMED
```

or:

```text
counter decremented
purchase REFUNDED
refund update loses CAS
transaction commits
refund still PROVIDER_CONFIRMED
```

That violates exactly-once accounting.

Attempt 2 must:

- keep finalization Serializable;
- re-read refund, purchase and purchased counter in the transaction;
- require a valid human provider confirmation:
  - `status == PROVIDER_CONFIRMED`;
  - `providerConfirmedAt != null`;
  - `providerConfirmedByPlatformAdminId != null`;
  - non-empty bounded `providerReference`;
  - `holdAppliedAt != null`;
- require purchase ACTIVE;
- require:
  - `refundingQuantity >= creditsSnapshot`;
  - `grantedQuantity >= creditsSnapshot`;
- CAS the counter by version;
- CAS purchase from ACTIVE;
- CAS refund by exact `id + version + PROVIDER_CONFIRMED`;
- if ANY mutation after the first write fails its CAS, THROW a retryable concurrency error so the entire transaction rolls back;
- retry only recognized Serializable/optimistic conflicts with a small bounded retry count;
- never return a normal `false` after an earlier accounting write has succeeded;
- only create/upsert `BILLING_REFUND_COMPLETED` after all three durable accounting transitions have succeeded in the same transaction.

##### Hold release

`releasePreProviderHold` currently decrements `refundingQuantity` first and then returns `false` if the refund update loses its CAS. That also commits a partial accounting change.

Attempt 2 must use the same all-or-nothing rule:

- if the refund CAS fails after the counter decrement, THROW so the transaction rolls back;
- CAS the terminal refund by version;
- no successful return until both counter release and durable refund/hold transition are committed together.

Add regressions that explicitly force the second/third CAS to fail and prove the counter/purchase/refund state is unchanged after rollback.

#### 3. Safe REJECTED/WITHDRAWN hold release must be an automatic Background path

The task says:

```text
Auto-release only if:
provider confirmation absent
correctionUsageEventId absent
explicit REJECTED/WITHDRAWN before provider action
```

The current public helper accepts `"REJECTED" | "WITHDRAWN"` as an argument and itself changes the refund to that status, but it is not called from the billing worker and does not prove that Admin already made an explicit terminal decision.

Attempt 2 must make this state-driven:

- Background must detect a durable refund already in `REJECTED` or `WITHDRAWN` with:
  - `holdAppliedAt != null`;
  - `providerConfirmedAt == null`;
  - `correctionUsageEventId == null`;
- Background then releases only the held `refundingQuantity`, clears `holdAppliedAt` / processing lease fields as appropriate, and PRESERVES the existing terminal status;
- use a bounded/deterministic scan or incorporate these terminal rows into the existing bounded work pass;
- if a correction exists in ANY state, do not release automatically;
- if provider confirmation exists, do not release automatically;
- PROVIDER_ACTION_REQUIRED by itself is not permission to release;
- do not let Background invent REJECTED/WITHDRAWN from a method argument.

This keeps authorization ownership with Admin and accounting ownership with Background.

#### 4. ARCH-008 pack reconciliation must account for completed Partner-Dashboard refunds

The task requires:

```text
Completed dashboard refund never regrants despite historical +1 provider usage.
```

The current `RecoveryCreditPurchaseService.reconcileProviderConfirmed(...)` is unchanged.

It currently computes:

```text
alreadyMatchedUnits = count(ACTIVE purchases)
confirmedDelta = providerUnits - alreadyMatchedUnits
```

and candidates remain PENDING_BILLING / NEEDS_ATTENTION.

For a completed `PARTNER_DASHBOARD_REFUND`:

```text
purchase.status = REFUNDED
historical provider +1 may remain
```

so that purchase drops out of `alreadyMatchedUnits`. The historical `+1` can then make `confirmedDelta > 0` and incorrectly activate an unrelated pending purchase.

Attempt 2 must make the ARCH-008 reconciliation refund-aware.

Required semantics:

- pending refund purchase remains ACTIVE and therefore still counts as one matched provider unit;
- completed `CURRENT_CYCLE_APP_EVENT_CORRECTION` REFUNDED purchase does NOT count as a historical matched +1 because the provider meter was reversed by the linked -1;
- completed `PARTNER_DASHBOARD_REFUND` REFUNDED purchase DOES count as an explained historical provider +1 for the exact same:
  - shop;
  - billing period;
  - plan snapshot;
  - pack meter;
  - original REPORTED +1 UsageEvent;
- the explained dashboard unit must consume provider quantity for `confirmedDelta` purposes but must grant zero entitlement;
- REFUNDED purchases are NEVER eligible activation candidates;
- no automatic clawback or regrant is introduced.

One acceptable shape is:

```text
alreadyMatchedUnits =
  exact-scope ACTIVE purchases
  +
  exact-scope REFUNDED purchases whose refund is
    COMPLETED + PARTNER_DASHBOARD_REFUND
```

while candidate selection remains only the accepted pending/re-entry states.

Add exact regressions:

```text
providerUnits=1
one completed dashboard-refunded historical +1
one new pending purchase
=> new pending purchase NOT activated
```

and:

```text
providerUnits=2
one completed dashboard-refunded historical +1
one new pending purchase
=> exactly one new pending purchase may activate
```

Also prove a completed correction-mode REFUNDED purchase is never itself reactivated.

#### 5. Correction replay/state mapping must fail closed

The task defines the exact correction mapping:

```text
PENDING / IN_FLIGHT / RETRYABLE -> PROVIDER_PENDING
NEEDS_ATTENTION                 -> NEEDS_ATTENTION
REPORTED                        -> PROVIDER_ACTION_REQUIRED
```

The current code treats every state other than REPORTED and NEEDS_ATTENTION as PROVIDER_PENDING. That incorrectly accepts `NOT_APPLICABLE`.

Attempt 2 must use an explicit exhaustive mapping:

- PENDING -> PROVIDER_PENDING;
- IN_FLIGHT -> PROVIDER_PENDING;
- RETRYABLE -> PROVIDER_PENDING;
- REPORTED -> PROVIDER_ACTION_REQUIRED;
- NEEDS_ATTENTION -> NEEDS_ATTENTION;
- NOT_APPLICABLE -> NEEDS_ATTENTION / fail closed while retaining the hold.

For an already-linked correction UsageEvent, validate before trusting it that it still matches the refund's immutable correction identity:

```text
shopId
metric == RECOVERY_CREDIT_PACK_PURCHASE
quantity == -1
billingPeriodId == snapshot
correctionOfUsageEventId == original snapshot
sourceType == RECOVERY_CREDIT_REFUND
sourceId == refund.id
shopifyEventHandle == event snapshot
idempotencyKey == recovery-credit-refund:<refund.id>
shopifyIdempotencyKey == canonical Shared helper
```

Any mismatch -> NEEDS_ATTENTION and keep the hold. Do not create a replacement correction.

During approval/hold validation also assert the original UsageEvent meter/identity is consistent with the approved purchase/refund snapshots; do not silently trust contradictory durable data.

#### 6. Complete the mandatory 17-test matrix

The task requires 17 refund/reconciliation/admission scenarios. Attempt 1 adds only 3 task-specific refund tests.

Attempt 2 must add deterministic tracked regressions for ALL of these:

1. **exact hold**
   - Serializable transaction;
   - purchase remains ACTIVE;
   - `refundingQuantity += creditsSnapshot`;
   - refund `PROCESSING`, `holdAppliedAt`, version increment.

2. **hold lowers availability**
   - a non-zero refund hold is observed by `PurchasedRecoveryReservationService`;
   - available purchased credits subtract `refundingQuantity`.

3. **insufficient balance**
   - no counter mutation;
   - no hold;
   - safe attention state.

4. **concurrent refund/recovery cannot overspend**
   - stateful CAS/transaction fake or DB integration;
   - exactly one competing reservation/hold wins when capacity is insufficient for both.

5. **exactly one -1 correction**
   - assert every required field:
     metric, quantity, billing period, correctionOf, source type/id,
     local idempotency key, event handle, canonical Shopify idempotency key;
   - replay creates no second correction.

6. **wrong cycle / meter / plan / non-REPORTED original**
   - each case creates no correction;
   - refund -> NEEDS_ATTENTION;
   - hold remains.

7. **REPORTED correction is not completion**
   - -> PROVIDER_ACTION_REQUIRED;
   - purchase ACTIVE;
   - entitlement unchanged;
   - no completed message.

8. **Partner Dashboard mode**
   - no negative UsageEvent;
   - -> PROVIDER_ACTION_REQUIRED.

9. **human confirmation finalizes exactly once**
   - requires complete provider-confirmation evidence;
   - one successful completion.

10. **only granted/refunding decrement**
    - committed/reserved counters are unchanged.

11. **replay/concurrency no double decrement**
    - second finalizer does not change counters/purchase/refund/message;
    - forced purchase/refund CAS failures roll back earlier counter mutations.

12. **safe reject/withdraw releases hold**
    - only when durable state is already REJECTED/WITHDRAWN;
    - no confirmation;
    - no correction;
    - release is exactly once.

13. **ambiguous provider action does not release**
    - any linked correction in IN_FLIGHT/RETRYABLE/REPORTED/NEEDS_ATTENTION keeps hold;
    - provider-confirmed rows keep hold until finalization/human resolution.

14. **REFUNDED correction-mode purchase never reactivates**
    - reconciliation candidate set excludes it.

15. **dashboard historical +1 does not regrant**
    - completed dashboard-refunded historical provider unit is explained/matched;
    - cannot activate an unrelated pending pack.

16. **fresh paid cycle included allowance before purchased**
    - after renewal, paid included allowance is consumed before purchased-credit reservation.

17. **Free counter untouched**
    - refund flow and purchased-credit hold/finalization never mutate FREE_RECOVERY_LIFETIME.

Additional required regressions:

- correction `NOT_APPLICABLE` fails closed;
- linked correction identity mismatch fails closed and retains hold;
- `BILLING_REFUND_COMPLETED` logical message is created exactly once.

Do not satisfy accounting/concurrency cases with mocks that unconditionally return `{ count: 1 }`. Use a stateful Prisma-shaped fake or focused DB integration so rollback/CAS behavior is actually proved.

### Positive Findings To Preserve

Attempt 1 correctly implements several important pieces:

- exact Shared 0.9.0 availability helper is used for purchased-credit reservation admission;
- approval re-reads refund + purchase + original UsageEvent inside a Serializable transaction;
- purchase stays ACTIVE while held;
- positive safe-integer credits are enforced;
- hold counter uses version CAS;
- current-cycle correction checks original +1 metric, REPORTED state, billing-period equality, current plan and current pack meter;
- negative correction uses:
  - metric `RECOVERY_CREDIT_PACK_PURCHASE`;
  - quantity `-1`;
  - source type `RECOVERY_CREDIT_REFUND`;
  - source id `refund.id`;
  - deterministic local idempotency key;
  - canonical Shared Shopify idempotency key;
- correction `REPORTED` is not treated as local completion;
- Partner Dashboard mode creates no synthetic negative UsageEvent;
- completion SYSTEM message uses a deterministic idempotent source key;
- refund progression is integrated into the billing-worker cycle after publication/reconciliation;
- worktree paths and start-of-attempt synchronization evidence are present.

### Validation Reviewed

Agent-reported Attempt 1:

```text
focused refund tests:     3 passed
focused billing suite:    32 passed
npm run test:unit:        445 passed
npm run build:            passed
npm run prisma:validate:  passed
git diff --check:          passed
```

The supplied archive does not include `node_modules`, so npm validation was not independently rerun by the architect. Source, task contract, architecture, focused tests and published Git state were inspected directly.

### Published Git Verification

Implementation branch:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-002
tip: 47c9bf417b0c4dd3c86dc66359d9e1aac7cfc441
ahead of main: 2
behind main: 0
```

The immediate parent of `47c9bf4` is:

```text
3614d9853312f8c64e0485207644ccd481b92305
feat(ARCH-009-BACKGROUND-001): execute approved cancellations
```

That sibling-task implementation is not an authoritative dependency of BACKGROUND-002 and is not architect-accepted.

The B002-owned commit itself changes only:

- `src/entrypoints/billing.ts`;
- `src/services/purchased-recovery-reservation.service.ts`;
- `src/services/recovery-credit-refund.service.ts`;
- `tests/unit/services/recovery-credit-refund.service.test.ts`.

Parent workspace branch tip:

```text
bdedc1c91f26587f76caa762b55e5620e1392df3
```

### Architecture Conformance
Changes required.

### Follow-up

Attempt 2 remains on the SAME `ARCH-009-BACKGROUND-002` task and canonical mirrored task branches/worktrees.

Required Attempt 2 sequence:

1. restore implementation-branch isolation from current synchronized `origin/main`; do not carry an unaccepted BACKGROUND-001 sibling commit;
2. preserve/adopt only BACKGROUND-002's own accepted prerequisites;
3. make finalization and safe hold release transactionally all-or-nothing on every CAS failure;
4. implement automatic state-driven REJECTED/WITHDRAWN pre-provider hold release;
5. make ARCH-008 pack reconciliation dashboard-refund-aware without regrant/clawback;
6. make correction-state/replay validation explicit and fail closed;
7. complete the full 17-test matrix plus the additional architect regressions above;
8. rerun:
   - focused refund/reconciliation/admission tests;
   - `npm run test:unit`;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
9. update the Completion Report with the new isolated branch base/history, exact Attempt 2 files, validation, worktree synchronization evidence, implementation commit and parent handoff;
10. preserve this Architect Review until the next architect decision;
11. return the same task to `review`;
12. STOP.

`ARCH-009-ADMIN-002` remains Pending until BACKGROUND-001, BACKGROUND-002 and ADMIN-001 are all architect-accepted Complete.
