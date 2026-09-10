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
attempt: 0
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
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
