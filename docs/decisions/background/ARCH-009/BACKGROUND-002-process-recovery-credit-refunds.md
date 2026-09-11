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
status: complete
priority: 50
executor: null
claimed_at: null
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
  review/report content commit: `cb8fa8cbe98969411c66cbe965c33537794b3ad2`
  pre-final metadata handoff commit: `d13f1aa5ef9b7d14f12d9ee5196e3d19f70650a3`
  reviewed published parent branch tip: `c3f5f92be0775b4fe441e03e9755874f0f19f06d`
  remote branch: `origin/task/ARCH-009-BACKGROUND-002`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Accepted

### Review Notes

Attempt 3 closes the complete Changes Requested contract from Attempt 2.

The refund progression state machine now re-reads durable state inside `advance()` and permits Background progression only from:

```text
PROCESSING
PROVIDER_PENDING
```

A stale outer selection cannot overwrite Admin-owned or human-confirmed state. Durable `REJECTED`, `WITHDRAWN`, `PROVIDER_CONFIRMED`, `PROVIDER_ACTION_REQUIRED`, `COMPLETED`, `NEEDS_ATTENTION`, `REQUESTED`, and `APPROVED` rows are no-ops in the progression path.

The optimistic-concurrency corrections are also complete:

- lifecycle transitions CAS exact `id + version + expected status`;
- every transition checks `updated.count == 1`;
- correction linking CASes exact `id + version + status + correctionUsageEventId=null`;
- a losing correction/status CAS raises `RefundConcurrencyConflict`;
- the Serializable transaction is retried through the bounded conflict policy;
- a failed correction link rolls back correction creation rather than leaving an orphaned task-owned correction.

The prior Attempt-2 accounting and reconciliation corrections remain intact:

- full-pack holds use Shared 0.9.0 refund-aware availability;
- purchase remains ACTIVE while a refund is pending;
- finalization atomically decrements only `grantedQuantity` and `refundingQuantity`;
- `committedQuantity` and `reservedQuantity` are preserved;
- purchase becomes REFUNDED only after complete provider-confirmation evidence;
- refund becomes COMPLETED exactly once;
- post-write CAS failures roll back the complete finalization transaction;
- REJECTED/WITHDRAWN pre-provider holds are automatically and idempotently released only when safe;
- correction/provider ambiguity retains the hold;
- CURRENT_CYCLE_APP_EVENT_CORRECTION creates one deterministic `-1` App Event and fails closed for source/cycle/plan/meter/state mismatches;
- `REPORTED` correction means PROVIDER_ACTION_REQUIRED, not completion;
- PARTNER_DASHBOARD_REFUND creates no synthetic negative App Event;
- completed Partner-Dashboard refunds remain explained historical provider `+1` units for ARCH-008 reconciliation without restoring entitlement;
- correction-mode REFUNDED purchases are never reactivated;
- purchased-credit admission subtracts `refundingQuantity`;
- paid included allowance continues to precede purchased credits;
- the refund path does not consume the Free lifetime counter.

### Regression Review

The Attempt-3 focused surface now covers the authoritative 17-item task matrix and the additional architect-requested concurrency cases, including:

1. Serializable exact full-pack hold while purchase remains ACTIVE;
2. held credits lower purchased-credit availability;
3. insufficient purchased balance produces no hold;
4. shared-counter refund/reservation competition cannot overspend;
5. deterministic one logical `-1` correction with durable source identity;
6. wrong source report state/cycle/provider cycle/plan/meter/original meter fails closed;
7. REPORTED correction does not finalize or decrement entitlement;
8. Partner Dashboard mode creates no correction;
9. complete human provider confirmation finalizes exactly once;
10. only granted/refunding quantities are decremented;
11. purchase-CAS and final-refund-CAS failures roll back preceding accounting writes;
12. REJECTED and WITHDRAWN hold release is safe and idempotent;
13. provider-confirmed/correction-linked ambiguity does not auto-release;
14. correction-mode REFUNDED purchase is not reactivated;
15. completed dashboard-refunded historical `+1` prevents erroneous regrant;
16. fresh paid included allowance precedes purchased credits;
17. Free lifetime counter remains untouched.

Additional races prove that a row changed to REJECTED, WITHDRAWN, or PROVIDER_CONFIRMED after selection is not overwritten by stale Background progression, and a correction-link CAS loss rolls back the correction transaction.

### Validation Reviewed

Agent-reported Attempt 3:

```text
focused B002 suites:       65 passed
npm run test:unit:         470 passed
npm run build:             passed
npm run prisma:validate:   passed
git diff --check:          passed
```

The supplied review archive does not contain `node_modules`, so npm commands were not independently rerun by the architect. The architect inspected the changed implementation, focused tests, task contract, dependency state and published Git history directly.

### Published Git Verification

Implementation repository:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-002
Attempt 2: 3dec78ea19ca6ac738ea0fcb4d252dc2436f16e2
Attempt 3: d2b7977c28b878d2cfadd251ecf72ad71fd24863
Attempt 3 parent: 3dec78ea19ca6ac738ea0fcb4d252dc2436f16e2
```

Attempt 3 is exactly one correction commit after Attempt 2. The cumulative task branch remains isolated from the BACKGROUND-001 sibling task and is based on the accepted direct prerequisites.

Published parent workspace branch reviewed at:

```text
c3f5f92be0775b4fe441e03e9755874f0f19f06d
```

The final parent commit is metadata-only and follows the recorded Attempt-3 report/handoff commits.

### Architecture Conformance
Accepted.

### Follow-up

`ARCH-009-BACKGROUND-002` is Complete.

Do not start `ARCH-009-ADMIN-002` yet. Its authoritative dependencies are:

```text
ARCH-009-ADMIN-001
ARCH-009-BACKGROUND-001
ARCH-009-BACKGROUND-002
```

Only BACKGROUND-002 is completed by this acceptance. BACKGROUND-001 remains in its separate security-only correction cycle, and ADMIN-001 is not Complete in this reviewed workspace.

Once all three individual dependencies are Complete, moda_architect may promote ADMIN-002 to Ready.

`ARCH-009-SYSTEM-TEST-001` remains terminal/manual-gated and must not execute automatically.
