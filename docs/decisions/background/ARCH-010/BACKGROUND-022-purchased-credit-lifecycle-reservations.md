---
id: ARCH-010-BACKGROUND-022
architecture_id: ARCH-010
title: Conform purchased-credit reservations to purchase lifecycle and refund concurrency
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 69
executor: copilot
claimed_at: 2026-09-14T16:24:19Z
attempt: 1
depends_on:
- ARCH-010-DATABASE-014
- ARCH-010-BACKGROUND-014
- ARCH-010-BACKGROUND-019
- ARCH-010-BACKGROUND-021
enables:
- ARCH-010-SHOPIFY-025
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-003
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: 2026-09-14
---

# ARCH-010-BACKGROUND-022: Conform purchased-credit reservations to purchase lifecycle and refund concurrency

## Forward-correction boundary

`ARCH-010-BACKGROUND-014` is accepted immutable history and already established:

- exact purchase-lot ownership on `UsageReservation`;
- FIFO allocation;
- aggregate + lot versioned CAS;
- Serializable bounded retries;
- real PostgreSQL concurrency testing.

Do not reopen that task. This task preserves those accepted properties while replacing its development-only partial-refund counters with the final `currentAmount/reservedAmount/status` purchase lifecycle.

`ARCH-010-BACKGROUND-019` is also accepted immutable history. Preserve its canonical cross-bucket routing exactly:

```text
PAID: selected promotional -> current-period included -> purchased FIFO -> lifetime Free -> block
FREE: selected promotional -> purchased FIFO -> lifetime Free -> block
```

This task may change the purchased-credit primitive and the minimum adapter code required by that primitive, but it must not reorder, bypass or duplicate BACKGROUND-019 promotional admission. Existing promotional reservation/replay/commit/release semantics remain untouched.

## Objective

Make every purchased-credit conversation reservation race safely against merchant purchase withdrawal/reactivation while allowing many purchase lots for the same shop to evolve independently.

## Canonical purchase allocation rule

A new purchased-credit reservation may use only a lot satisfying:

```text
shopId = target shop
status = ACTIVE
currentAmount - reservedAmount >= requested quantity
```

Canonical order remains the original purchase FIFO order:

```text
activatedAt ASC NULLS LAST
createdAt   ASC
id          ASC
```

Withdrawal/reactivation does not change FIFO age. A reactivated old purchase returns to its original position.

Skip all lots in:

```text
REQUESTED
WITHDRAWN
COMPLETED
REFUNDED
```

## New reservation CAS

Preserve the repository convention:

1. interactive Prisma transaction;
2. `Serializable` isolation;
3. fresh read inside transaction;
4. conditional `updateMany` CAS on `id + version + lifecycle predicates`;
5. require `count == 1`;
6. retry the **whole transaction** on CAS/P2034 conflict, bounded by existing retry policy.

Do not replace this with raw `SELECT FOR UPDATE`, process mutexes, Redis locks or unversioned read/update.

For quantity 1, winning reservation atomically performs equivalent mutations:

```text
purchase.reservedAmount += 1
purchase.version += 1

aggregate.reservedQuantity += 1
aggregate.version += 1

UsageReservation(purchasedCreditPurchaseId = exact purchase)
```

The lot update predicate must still require `status = ACTIVE` and fresh availability.

If another process changes the purchase first, restart selection from fresh DB state. Do not blindly retry the same lot; it may now be WITHDRAWN/COMPLETED while another ACTIVE lot is available.

## Reservation versus refund-request race

SHOPIFY-025 will transition one ACTIVE purchase to WITHDRAWN using the same versioned-CAS convention.

Required behaviour:

### One available credit

Starting state:

```text
currentAmount = 1
reservedAmount = 0
status = ACTIVE
version = N
```

If conversation reservation wins first:

```text
reservedAmount = 1
version = N+1
```

Refund CAS using N must fail/retry. Fresh `availableAmount = 0`; refund returns `REFUND_NOT_AVAILABLE` and purchase stays ACTIVE.

If refund wins first:

```text
status = WITHDRAWN
version = N+1
```

Reservation CAS must fail/retry, skip this lot and attempt the next eligible ACTIVE lot.

### Two available credits

If one reservation wins before refund:

```text
currentAmount = 2
reservedAmount = 1
availableAmount = 1
```

Refund may then win on the fresh version and withdraw the purchase with request-time available snapshot 1. The pre-existing reservation still owns the other credit and may later commit/release.

## Commit existing reservation

A reservation created while the purchase was ACTIVE remains valid if the merchant subsequently withdraws the purchase.

Commit is allowed when the exact reservation is RESERVED and its exact purchase is either:

```text
ACTIVE
WITHDRAWN
```

On successful WhatsApp confirmation, atomically:

```text
purchase.currentAmount  -= quantity
purchase.reservedAmount -= quantity
purchase.version += 1

aggregate.reservedQuantity  -= quantity
aggregate.committedQuantity += quantity
aggregate.version += 1
```

Do not change aggregate `refundingQuantity` for a committed pre-withdrawal reservation: that reserved credit was never part of the unreserved withdrawal hold.

If resulting purchase state is:

```text
currentAmount = 0
reservedAmount = 0
```

then transition purchase to `COMPLETED` in the same transaction.

If it was WITHDRAWN, also terminally close its live `RecoveryCreditRefund` without provider money movement using existing refund status `CANCELLED` and bounded reason equivalent to `NO_CREDITS_REMAINING`. No provider refund is possible because every credit was consumed.

## Release existing reservation

Release is allowed against an exact RESERVED reservation whose purchase is ACTIVE or WITHDRAWN.

Always atomically:

```text
purchase.reservedAmount -= quantity
aggregate.reservedQuantity -= quantity
```

If purchase is ACTIVE:

```text
aggregate.refundingQuantity unchanged
```

If purchase is WITHDRAWN:

```text
aggregate.refundingQuantity += quantity
```

because the released credit has returned to `currentAmount` but must remain non-spendable while the whole purchase is withdrawn for refund.

This is required to keep:

```text
aggregate.refundingQuantity
  = unreserved current credits held by all WITHDRAWN lots
```

## Ambiguous reservation

`markAmbiguous` retains reservation ownership/hold exactly as today. It does not decrement `reservedAmount` and therefore prevents provider refund finalisation until reconciliation resolves the reservation.

Do not force a withdrawn purchase through refund while an ambiguous reservation remains.

## Released reservation replay

Preserve accepted idempotency semantics, but a replay must never create a new reservation against a lot whose current status is WITHDRAWN/COMPLETED/REFUNDED/REQUESTED.

If the existing source-key semantics require selection of another lot after a released original lot becomes ineligible, refactor only as much as necessary to retain one canonical reservation identity without creating duplicate consumption. Document the exact accepted behaviour in tests.

## Multiple purchase lots

A shop may simultaneously have for example:

```text
A = COMPLETED
B = ACTIVE
C = WITHDRAWN
D = ACTIVE
E = REFUNDED
F = REQUESTED
```

New allocation considers only B/D in original FIFO order.

Withdrawing C must not freeze B/D. Reactivating C later returns C to its original FIFO position.

No shop-wide purchase lock/state is allowed.

## Aggregate conservation

Prove aggregate and per-lot state remain conserved across:

```text
reserve
commit
release
refund withdrawal request
refund reactivation
withdrawn reservation commit
withdrawn reservation release
purchase completion
provider refund finalisation (ADMIN-003, integration contract only)
```

BACKGROUND-022 owns reservation-side mutations only; SHOPIFY-025 and ADMIN-003 own their respective transaction paths.

## Real PostgreSQL concurrency tests

Use disposable PostgreSQL and **two independent Prisma clients/connections**. Do not satisfy these races using only mocked calls.

Required races at minimum:

1. one available credit: reservation wins -> refund retry sees 0 and cannot withdraw;
2. one available credit: refund transition wins -> reservation retry skips lot and can use another ACTIVE lot;
3. two available credits: one reservation wins -> refund can withdraw remaining available 1;
4. WITHDRAWN lot with one reserved credit: release transfers that quantity from aggregate reserved to aggregate refunding;
5. WITHDRAWN lot with one reserved credit: commit decrements lot current/reserved and aggregate reserved/increments committed;
6. last pre-withdrawal reservation commits -> purchase becomes COMPLETED and refund closes without provider settlement;
7. old withdrawn lot reactivated by the other service later remains original FIFO predecessor (model/query assertion);
8. unrelated purchase lots remain untouched.

The race helper may directly perform the exact documented SHOPIFY-025 CAS transaction shape in the integration test. Do not implement merchant HTTP/UI behaviour in Background production code.

## Required validation

Run focused unit/integration tests, disposable PostgreSQL race tests, Prisma validation, repository build/full suite and `git diff --check`. Document only unrelated baseline failures.

## Non-goals

Do not implement merchant request/reactivation endpoints, purchase valuation, Admin provider settlement, or UI.

## Stop conditions

STOP if DATABASE-014 final fields are unavailable, if implementing the refund race requires weakening the accepted CAS convention, or if another completed task would need modification.

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
