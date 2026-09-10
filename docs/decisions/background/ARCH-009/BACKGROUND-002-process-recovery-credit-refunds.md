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
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-10T22:27:52Z
attempt: 3
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
- `moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-refund.service.test.ts`
### Work Completed
- Preserved the accepted hold, correction, reconciliation, release, and finalization behavior from Attempt 2.
- Restricted `advance()` to freshly re-read `PROCESSING` and `PROVIDER_PENDING` rows; stale Admin-owned terminal/provider-confirmed states now no-op without correction creation or lifecycle overwrite.
- Made status transitions require exact `id + version + expected status` and checked `count`; correction linking now also requires the current version/status and increments the refund version, with Serializable conflict retry.
- Added deterministic races for REJECTED, WITHDRAWN, and PROVIDER_CONFIRMED state changes after selection, plus correction-link CAS loss and all requested hold, correction, release, finalization, message, reconciliation, paid-cycle, and free-counter proofs.
- Added direct admission coverage proving `refundingQuantity` blocks reservation and cannot overspend in a concurrent refund-hold versus reservation race.
- Added the missing original UsageEvent meter snapshot guard so a held correction fails closed to `NEEDS_ATTENTION`.
### Validation Results
- `npx vitest run tests/unit/services/recovery-credit-refund.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/recovery-billing.service.test.ts tests/unit/services/billing-reconciliation.service.test.ts`: passed, 4 files and 65 tests.
- `npm run test:unit`: passed, 44 files and 470 tests.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
Attempt 3 remained within the requested narrow scope but included one justified production correction: the required source-identity regression exposed that an already-held correction path did not revalidate the original UsageEvent meter snapshot. No unrelated task, sibling implementation, schema, queue, or contract changes were made.
### Assumptions
Admin confirmation writes `PROVIDER_CONFIRMED` and the provider confirmation fields before Background finalization, as defined by ARCH-009. Existing accepted ARCH-009 database and Shared 0.9.0 prerequisites remain authoritative.
### Unresolved Issues
None.
### Architectural Concerns
None.

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
  commit: `d2b7977c28b878d2cfadd251ecf72ad71fd24863`
  remote branch: `origin/task/ARCH-009-BACKGROUND-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-002-process-recovery-credit-refunds.md`
  review/report content commit: pending
  final parent handoff / branch tip: pending
  remote branch: `origin/task/ARCH-009-BACKGROUND-002`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 2 successfully closes the major Attempt 1 defects:

- the BACKGROUND-002 implementation branch is isolated directly from `moda-interact-background/main` and no longer carries unaccepted BACKGROUND-001 code;
- finalization throws on post-write CAS failure so counter/purchase/refund accounting rolls back atomically;
- terminal hold release throws on a losing refund CAS and is retried only through the bounded conflict path;
- REJECTED/WITHDRAWN hold release is now state-driven from durable terminal state rather than invented by Background;
- ARCH-008 purchase reconciliation now counts exact-scope completed Partner-Dashboard refunds as explained historical `+1` units without restoring entitlement;
- correction report-state mapping is explicit and `NOT_APPLICABLE` fails closed;
- linked correction identity is validated against the refund snapshots and canonical Shopify idempotency key;
- purchased-credit admission now subtracts `refundingQuantity`.

Those corrections should be preserved.

Attempt 2 is not yet acceptable because one concurrency/authorization defect remains in the runtime state machine and the prior Architect Review explicitly required a larger deterministic regression matrix than the implementation currently provides.

#### 1. `advance()` must never overwrite an Admin-owned terminal or provider-confirmed state

`processDue()` selects PROCESSING / PROVIDER_PENDING rows and later calls `advance(refund.id, now)`.

Inside `advance()`, the refund is re-read, but the implementation currently checks only:

```ts
if (!refund || !refund.holdAppliedAt) return "attention";
```

It does **not** require that the freshly re-read durable row is still in a Background-actionable state.

This creates a real race:

```text
Worker selects PROCESSING
        |
        v
SUPER_ADMIN changes row -> REJECTED / WITHDRAWN / PROVIDER_CONFIRMED
        |
        v
Worker advance() re-reads the new state
        |
        v
current code can still create/inspect a correction
and transition the row to PROVIDER_PENDING /
PROVIDER_ACTION_REQUIRED / NEEDS_ATTENTION
```

For `PARTNER_DASHBOARD_REFUND`, a freshly re-read REJECTED row can be overwritten to `PROVIDER_ACTION_REQUIRED`.

For correction mode, a freshly re-read terminal/provider-confirmed row can have a correction created or can be overwritten by the correction-state mapping.

That violates the human approval boundary.

Attempt 3 must:

- treat only the intended Background progression states as actionable inside `advance()`:
  - `PROCESSING`;
  - `PROVIDER_PENDING`;
- after the in-transaction re-read, if the durable status is any of:
  - `REJECTED`;
  - `WITHDRAWN`;
  - `PROVIDER_CONFIRMED`;
  - `PROVIDER_ACTION_REQUIRED`;
  - `COMPLETED`;
  - `NEEDS_ATTENTION`;
  - `REQUESTED`;
  - `APPROVED`;
  then `advance()` must perform **no correction creation and no status overwrite**;
- a stale outer selection must never be sufficient authority to progress the row;
- REJECTED/WITHDRAWN should be left for the terminal-hold-release path;
- PROVIDER_CONFIRMED should be left for finalization;
- do not automatically reinterpret an Admin-owned terminal state.

A clean implementation may let `advance()` return a no-op/null outcome and have `processDue()` simply continue without incrementing a misleading lifecycle result.

Add deterministic races proving:

```text
selected PROCESSING
then durable REJECTED before advance
=> terminal status preserved
=> no correction
=> no provider-action transition
```

```text
selected PROVIDER_PENDING
then durable WITHDRAWN before advance
=> terminal status preserved
=> no correction/state overwrite
```

```text
selected PROCESSING/PROVIDER_PENDING
then durable PROVIDER_CONFIRMED before advance
=> confirmation preserved
=> advance performs no correction/state overwrite
=> a later pass may finalize normally
```

#### 2. Correction linking and lifecycle transitions must use checked optimistic CAS

The helper:

```ts
transition(transaction, refund, status, now)
```

currently updates by:

```text
id + version
```

but ignores `updated.count`.

`createCorrection()` also links `correctionUsageEventId` using only:

```text
id + correctionUsageEventId:null
```

and ignores the result.

Attempt 3 must make these transitions concurrency-safe:

- status transition predicate must include:
  - exact `id`;
  - exact `version`;
  - exact expected current `status`;
- if the transition CAS loses, throw `RefundConcurrencyConflict` so the Serializable transaction rolls back/retries rather than reporting an outcome that was not persisted;
- correction linkage must be tied to the same freshly re-read actionable refund identity/state;
- if another writer changed the refund before the link is persisted, fail/retry rather than linking a correction to a terminal or provider-confirmed refund;
- do not create a second correction; preserve the deterministic upsert/idempotency contract.

One acceptable correction-link predicate is equivalent to:

```text
id == refund.id
version == refund.version
status == refund.status
correctionUsageEventId == null
```

with a checked `count == 1`.

Do not weaken the existing linked-correction identity validation.

#### 3. Complete the still-missing mandatory regression proofs

The prior Architect Review explicitly required deterministic tests for all 17 task cases plus the additional correction/message cases. Attempt 2 adds useful coverage, but a number of those required proofs remain absent or only partial.

Attempt 3 must add the following missing tests.

##### Hold / admission

1. **Exact hold state**
   - prove the hold transaction is Serializable;
   - after the hold write, prove:
     - purchase remains ACTIVE;
     - `refundingQuantity += creditsSnapshot`;
     - refund had the PROCESSING/hold/version transition before provider progression.

2. **Hold lowers purchased-credit availability**
   - use `PurchasedRecoveryReservationService` with a non-zero `refundingQuantity`;
   - prove the held credits cannot be reserved.

3. **Concurrent refund hold vs recovery reservation**
   - use a stateful shared counter/CAS fixture or focused DB test;
   - insufficient capacity for both;
   - prove at most one wins and the counter never overspends.

##### Correction creation / validation

4. **Exact one `-1` correction**
   Assert all required fields, including the ones not currently asserted:

```text
shopId
metric = RECOVERY_CREDIT_PACK_PURCHASE
quantity = -1
billingPeriodId
correctionOfUsageEventId
sourceType = RECOVERY_CREDIT_REFUND
sourceId = refund.id
idempotencyKey = recovery-credit-refund:<refund.id>
shopifyEventHandle
shopifyIdempotencyKey = canonical Shared helper
```

Track the upsert/create count and prove replay does not create a second logical correction.

5. **Wrong source/current scope fails closed**
   Add separate cases for:
   - original UsageEvent not REPORTED;
   - wrong original billing cycle;
   - current Subscription billing cycle mismatch;
   - current provider plan mismatch;
   - current pack meter mismatch;
   - original UsageEvent meter/snapshot mismatch.

Each must:

```text
create no correction
-> NEEDS_ATTENTION
keep hold
```

6. **REPORTED correction is not completion**
   In addition to the current status assertion, prove:
   - purchase remains ACTIVE;
   - granted/refunding quantities are unchanged;
   - no `BILLING_REFUND_COMPLETED` message exists.

7. **Partner Dashboard mode creates no correction**
   Explicitly assert no UsageEvent correction/upsert is called before moving to `PROVIDER_ACTION_REQUIRED`.

##### Finalization / release

8. **Only granted/refunding are decremented**
   Start with non-zero `committedQuantity` and `reservedQuantity`;
   after finalization prove both are unchanged.

9. **Forced final refund CAS rollback**
   Attempt 2 proves purchase-CAS rollback, but the previous review required both purchase and refund CAS failures.
   Force the final:

```text
refund PROVIDER_CONFIRMED -> COMPLETED
```

CAS to lose after counter and purchase writes and prove the whole transaction rolls back:

```text
granted unchanged
refunding unchanged
purchase ACTIVE
refund PROVIDER_CONFIRMED
no completion message
```

10. **WITHDRAWN release and release exactly once**
    Repeat the safe terminal release regression for `WITHDRAWN`, and prove a second pass does not decrement `refundingQuantity` again.

11. **Provider-confirmed/ambiguous provider action never auto-releases**
    Explicitly prove:
    - terminal row with provider-confirmation evidence is not auto-released;
    - any linked correction in PENDING/IN_FLIGHT/RETRYABLE/REPORTED/NEEDS_ATTENTION prevents automatic hold release.

##### Billing invariants / messaging

12. **Free counter untouched**
    The refund hold/finalization path and purchased-credit admission must never read/update `FREE_RECOVERY_LIFETIME`.
    Add a direct tracked regression.

13. **Fresh paid-cycle precedence**
    Preserve/prove the paid billing invariant in the ARCH-009 task surface:
    fresh paid included allowance is consumed before purchased-credit reservation after cycle renewal.

14. **Completion message logical idempotency**
    Prove first finalization uses exactly:

```text
BILLING_REFUND_COMPLETED
```

with the canonical `createMerchantBillingSystemSourceKey(...)`, and replay/concurrent finalization cannot produce a second logical message.

#### 4. Preserve the corrected reconciliation behavior

The new reconciliation changes are correct and should not regress:

```text
ACTIVE exact-scope purchases
+
COMPLETED PARTNER_DASHBOARD_REFUND exact-scope REFUNDED purchases
=
alreadyMatchedUnits
```

The current tests correctly prove:

```text
providerUnits=1
dashboard-refunded historical +1 + pending purchase
=> pending purchase not activated
```

and:

```text
providerUnits=2
dashboard-refunded historical +1 + pending purchase
=> exactly one pending purchase activates
```

and the correction-mode REFUNDED purchase itself is not reactivated.

Do not redesign this part in Attempt 3.

#### 5. Completion Report metadata

The published parent branch tip is:

```text
43bc35bb0b8eb3a01e7253699ea8b60a7db282fb
```

The Attempt 2 Completion Report currently records the earlier report commit:

```text
3b875395c7e3a075e9195d434a965d5c5af61df9
```

Attempt 3 must distinguish:

```text
review/report content commit
final parent branch/handoff tip
```

and record the final pushed parent tip explicitly.

Preserve the existing physical worktree and synchronization evidence.

### Positive Findings To Preserve

- implementation branch is now a single BACKGROUND-002 commit directly on synchronized `moda-interact-background/main`;
- no unaccepted BACKGROUND-001 implementation is carried;
- exact accepted ARCH-009 DB gitlink and Shared 0.9.0 are adopted directly by this task;
- refund hold uses Shared `availablePurchasedRecoveryCredits`;
- purchase stays ACTIVE while held;
- original purchase/UsageEvent snapshot checks include original meter identity;
- negative App Event uses deterministic local and canonical Shopify idempotency;
- correction state mapping is explicit and `NOT_APPLICABLE` fails closed;
- linked correction identity is validated before reuse;
- Partner Dashboard refund creates no synthetic negative event in production;
- completed dashboard refunds are accounted for as explained historical provider units;
- correction-mode REFUNDED purchase is not an activation candidate;
- finalization requires durable provider confirmation evidence;
- finalization and terminal hold release use Serializable transactions and bounded conflict retry;
- counter/purchase/refund accounting now rolls back when later CAS operations fail;
- REJECTED/WITHDRAWN terminal release is Background-observed, not Background-invented;
- purchased-credit reservation availability subtracts `refundingQuantity`;
- billing-worker integration remains after the existing reconciliation pass.

### Validation Reviewed

Agent-reported Attempt 2:

```text
focused refund/purchase tests: 32 passed
npm run test:unit:              451 passed
npm run build:                  passed
npm run prisma:validate:        passed
git diff --check:               passed
```

The supplied archive does not contain `node_modules`, so npm validation was not independently rerun by the architect.

The architect inspected the task contract, architecture, modified source, focused test files, and published Git state directly.

### Published Git Verification

Implementation branch:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-002
tip: 3dec78ea19ca6ac738ea0fcb4d252dc2436f16e2
parent: eff586b2a23c1315018bbd27cefb96500d7681da
```

The tip is directly based on `main`, so the Attempt 1 sibling-task contamination is removed.

Parent workspace branch tip:

```text
43bc35bb0b8eb3a01e7253699ea8b60a7db282fb
```

Both published task branches match the supplied handoff.

### Architecture Conformance

Changes required.

### Follow-up

Attempt 3 remains on the SAME `ARCH-009-BACKGROUND-002` task and canonical mirrored task branches/worktrees.

Attempt 3 scope is narrow:

1. protect Admin-owned terminal/provider-confirmed states from stale Background `advance()` work;
2. make correction-link/status transition writes exact checked CAS operations;
3. complete only the missing tests enumerated above;
4. preserve the corrected atomic finalization, automatic release, reconciliation, correction-state mapping, Shared availability and branch isolation;
5. do not import BACKGROUND-001 or any other sibling task branch;
6. rerun:
   - focused refund/reconciliation/admission tests;
   - `npm run test:unit`;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
7. update the Completion Report with Attempt 3 files, test counts, worktree/sync evidence, implementation commit, report commit and final parent branch tip;
8. preserve this Architect Review until the next architect decision;
9. return the same task to `review`;
10. STOP.

`ARCH-009-ADMIN-002` remains Pending until BACKGROUND-001, BACKGROUND-002 and ADMIN-001 are all architect-accepted Complete.
