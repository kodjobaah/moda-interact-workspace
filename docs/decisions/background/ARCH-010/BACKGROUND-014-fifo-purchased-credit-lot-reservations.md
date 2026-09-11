---
id: ARCH-010-BACKGROUND-014
architecture_id: ARCH-010
title: Make purchased recovery reservations FIFO lot-aware
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 68
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-007
  - ARCH-010-BACKGROUND-011
enables:
  - ARCH-010-ADMIN-003
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-014: Make purchased recovery reservations FIFO lot-aware

## Objective

Replace aggregate-only purchased-credit reservation with deterministic purchase-lot reservation while preserving the existing aggregate counter as the fast shop-level balance.

This task does not process human refunds. It creates the runtime accounting prerequisite that makes partial unused-credit refunds provable.

## Files to inspect

Inspect actual integrated equivalents before editing, especially:

```text
moda-interact-background/src/services/purchased-recovery-reservation.service.ts
moda-interact-background/src/services/recovery-credit-purchase.service.ts
moda-interact-background/src/services/recovery-billing.service.ts
moda-interact-background/src/services/billing-reconciliation.service.ts
moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts
moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts
```

Do not assume filenames are unchanged if prior ARCH-010 tasks have refactored them.

## Canonical priority

This task changes only how the `purchased` step chooses a historical purchase lot. It MUST NOT itself insert/reorder other buckets.

`ARCH-010-BACKGROUND-019` owns the final cross-bucket order:

```text
Paid: included -> promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
Free: promotional -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
```

Within that final order, this task owns FIFO lot selection only when the `purchased` step is reached.

## FIFO purchased-lot selection

When a new purchased-credit reservation is required, within the existing Serializable transaction:

1. replay by `sourceKey` first;
2. read the aggregate PURCHASED counter;
3. require aggregate spendable >= requested quantity;
4. select the oldest provider-confirmed purchase lot with lot-refundable/spendable capacity using exact order:

```text
activatedAt ASC NULLS LAST
createdAt ASC
id ASC
```

5. ARCH-010 recovery reservations are quantity 1. Require one lot with >=1 spendable credit; do not split one recovery across lots;
6. atomically increment both aggregate `reservedQuantity` and selected lot `reservedQuantity` using version/CAS semantics;
7. create `UsageReservation` with both aggregate counter identity and exact purchase-lot identity.

Lot spendable is exactly:

```text
creditsGranted
- committedQuantity
- reservedQuantity
- refundingQuantity
- refundedQuantity
```

Never reserve held/refunded credits.

## Commit

For a RESERVED purchased reservation:

1. re-read reservation and exact lot;
2. require lot identity matches reservation;
3. atomically:

```text
aggregate.reserved -= 1
aggregate.committed += 1
lot.reserved -= 1
lot.committed += 1
```

4. preserve the existing NOT_APPLICABLE recovery UsageEvent semantics;
5. mark reservation COMMITTED exactly once.

## Release

For a RESERVED reservation, atomically decrement:

```text
aggregate.reserved
lot.reserved
```

then mark RELEASED.

Committed reservations remain non-releasable.

## Ambiguous

Preserve current safety semantics: AMBIGUOUS retains its reserved capacity.

Therefore do not decrement either aggregate or lot `reservedQuantity` when transitioning RESERVED -> AMBIGUOUS.

## Concurrency

Refund approval and recovery reservation compete on the same purchase-lot/aggregate capacity.

Use Serializable transactions plus optimistic version/CAS so these two operations cannot both consume/hold the same credit.

Do not rely only on a pre-read available number.

## Purchase activation

When provider reconciliation activates a new `RecoveryCreditPurchase`:

- `creditsGranted` is added once to aggregate granted quantity;
- lot committed/reserved/refunding/refunded quantities remain zero by schema default;
- no lifetime Free mutation.

## Provider reconciliation compatibility

Do not infer provider-confirmed purchase units from local spendable balance.

A Partner Dashboard refund/credit does not reduce the original App Pricing top-up meter quantity.

New ARCH-010 partial refunds keep the purchase provider status ACTIVE and lower local lot/aggregate granted balance through refunded quantities.

Legacy data may contain `RecoveryCreditPurchase.status=REFUNDED` and/or legacy negative refund correction events. Those rows are explained historical provider units and must never become new activation candidates.

If the integrated provider reconciliation still counts only ACTIVE purchase rows and would misinterpret legacy REFUNDED provider units as unmatched provider quantity, correct that logic narrowly with regression coverage. Do not change new ARCH-010 refunds to negative App Events.

## Required tests

At minimum prove:

1. oldest lot selected first;
2. exhausted/refunding/refunded older lot skipped;
3. second lot selected only when first has no spendable credit;
4. reserve updates aggregate + lot exactly once;
5. commit updates aggregate + lot exactly once;
6. release updates aggregate + lot exactly once;
7. ambiguous retains both reserved quantities;
8. replay keeps original lot identity;
9. concurrent reserve vs refund-hold CAS cannot overspend one lot;
10. aggregate and sum-of-lots remain equal after reserve/commit/release;
11. purchased exhaustion still falls through to lifetime Free through BACKGROUND-011/BACKGROUND-002;
12. new purchase activation initializes spendable lot without double grant;
13. manual completed partial refund does not cause provider reconciliation to re-grant the refunded credit;
14. legacy REFUNDED/correction history never becomes an activation candidate.

Run actual repository scripts from `package.json` plus task-required focused tests, build, Prisma validation if declared and `git diff --check`.

## Explicit non-goals

Do not implement Admin refund approval, Partner Dashboard settlement, merchant UI, refund system messages, negative/fractional App Events or a new queue.

## Stop

If existing runtime quantity semantics require one recovery reservation to span multiple purchase lots, STOP and return to `moda_architect`; do not invent a split-allocation model inside this task.

Return `review` and STOP after validation/completion report.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
