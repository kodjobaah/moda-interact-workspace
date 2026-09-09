# ARCH-009 implementation handoff

## Read order

1. `docs/architecture/ARCH-009-merchant-billing-lifecycle-cancellations-refunds.md`
2. `docs/architecture/ARCH-009-MATERIALIZATION-NOTE.md`
3. domain `_index.md`
4. exact task file

## Initial frontier

```text
ARCH-009-DATABASE-001
  Pending on ARCH-008-BACKGROUND-002
```

## Mirrored branch rule

For task `<TASK_ID>`:

```text
parent:         task/<TASK_ID>
implementation: task/<TASK_ID>
```

Changes Requested continue on the same branches/worktree.

## Global invariants

```text
Free lifetime balance survives plan changes.
Purchased credits survive plan/cycle changes.
Paid included capacity precedes purchased credits.
Paid -> Free uses hosted plan selection.
Full cancellation never creates implicit Free.
Admin never chooses merchant plan.
Financial actions require human approval.
Refund V1 is full-pack only.
Pending refund subtracts refundingQuantity.
Negative App Event REPORTED is not refund completion.
Cash refund is Partner Dashboard V1.
Generic pack correction must use refund workflow.
```

ARCH-009 system test is terminal/manual-gated.
