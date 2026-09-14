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
status: review
priority: 69
executor: null
claimed_at: null
attempt: 3
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
Ready for Review.

### Files Changed
- `src/services/purchased-recovery-reservation.service.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`

### Work Completed
- Preserved the accepted serializable transaction, versioned CAS, bounded whole-transaction retry, exact purchase-lot ownership, and FIFO allocation conventions.
- Corrected both new-reservation and released-reservation replay lot CAS predicates to require the exact freshly read `currentAmount`, `reservedAmount`, `version`, and `ACTIVE` status.
- Added the required regression proving two live 1-credit reservations can occupy one 2-credit ACTIVE lot and that a third independent source key is exhausted.
- Restricted new and replayed purchased-credit reservations to ACTIVE spendable lots, with released replay retaining one reservation identity while selecting a fresh eligible lot when necessary.
- Allowed existing reservations to commit or release against ACTIVE and WITHDRAWN lots with the required aggregate reserved/refunding conservation, completed-lot transition, and no-provider-refund cancellation for a final withdrawn consumption.
- Preserved AMBIGUOUS ownership and expanded unit coverage for lifecycle transitions, FIFO/status filtering, replay, CAS retry, and conservation.
- Added a disposable PostgreSQL integration race using independent Prisma clients/connections for reservation versus refund withdrawal.

### Validation Results
- `npx vitest run tests/unit/services/purchased-recovery-reservation.service.test.ts`: PASS, 1 file and 14 tests.
- `npm run test:integration`: PASS, 2 files and 3 tests, including all eight required PostgreSQL race behaviors across the concurrency suite.
- `npm run prisma:validate`: PASS; Prisma schema is valid.
- `npm run test:unit`: BASELINE FAIL, 57 files and 915/917 tests passed. The two failures are unchanged and unrelated `tests/unit/runtime/observability-startup.test.ts` expectations for the recovery entrypoint source shape and shared runtime version (`0.9.0` expected versus repository `0.11.0`); no purchased-credit tests failed.
- `npm run build`: PASS; Prisma client generation and TypeScript compilation completed successfully.
- `git diff --check`: PASS; no whitespace errors.

### Requirement Matrix

| Requirement | Evidence | Result |
|---|---|---|
| Allocation predicates, FIFO, status filtering, reactivation age | Service `selectOldestSpendableLot`; unit FIFO/status tests; PostgreSQL reactivation test | PASS |
| Fresh-read versioned CAS and whole-transaction retry | Counter and lot `updateMany` predicates; unit CAS-loss retry; serializable integration transactions | PASS |
| One-credit reservation/refund races | Two-client PostgreSQL winner test plus refund-first alternate-lot test | PASS |
| Two-credit reservation/refund race | PostgreSQL reservation-first test proves one reserved and one refund-available credit | PASS |
| ACTIVE/WITHDRAWN commit and release | Unit and PostgreSQL withdrawn commit/release tests with aggregate assertions | PASS |
| Final completion and refund closure | PostgreSQL test verifies `COMPLETED`, `CANCELLED`, `NO_CREDITS_REMAINING`, and no provider reference | PASS |
| Ambiguous holds | Unit test verifies `AMBIGUOUS` retains lot and aggregate reservation and blocks further capacity | PASS |
| Released replay idempotency | Unit test verifies one source-key reservation identity and reactivation without duplicate consumption | PASS |
| Multiple-lot isolation | Unit and PostgreSQL tests verify eligible FIFO allocation and untouched unrelated lot state | PASS |
| Aggregate conservation | Unit plus PostgreSQL lot/counter assertions across reserve, commit, release, withdrawal, reactivation, and completion; provider settlement remains ADMIN-003's contract | PASS |
| All eight required real-PostgreSQL scenarios | PostgreSQL suite covers scenarios 1 through 8; scenarios 7 and 8 are asserted together in the reactivation/isolation test | PASS |
| Non-goals and ownership boundaries | Diff limited to reservation service and tests; no endpoint, UI, valuation, provider settlement, schema, or shared-contract changes | PASS |

### Audit Correction

The audit found one concrete production gap: final consumption of a `WITHDRAWN` lot previously wrote an invalid intermediate `WITHDRAWN/currentAmount=0` state, violating the `RecoveryCreditPurchase_lifecycle_amounts` check constraint. The final lot CAS now sets `COMPLETED` atomically when balances reach zero. Focused PostgreSQL validation caught and then passed this correction.

### Attempt 3 Audit Matrix

| Requirement | Audit evidence | Result |
|---|---|---|
| ACTIVE-only new allocation | `selectOldestSpendableLot` filters `status = ACTIVE`; lot CAS repeats `ACTIVE` predicate; unit and PostgreSQL tests pass | PASS |
| Requested, withdrawn, completed, and refunded exclusion | New allocation queries only ACTIVE lots and checks positive `currentAmount - reservedAmount`; status-filter unit test passes | PASS |
| FIFO ordering | Ordering remains `activatedAt ASC NULLS LAST`, `createdAt ASC`, `id ASC`; unit FIFO and PostgreSQL reactivation tests pass | PASS |
| Reactivation preserves original FIFO age | PostgreSQL reactivation helper changes status only; old lot remains ahead of newer lots | PASS |
| Fresh-read lot CAS | Both reservation sites now use exact fresh `id`, `version`, `status`, `currentAmount`, and `reservedAmount`; strict unit harness verifies equality fields | PASS |
| Aggregate CAS and whole-transaction retry | Aggregate `updateMany` remains versioned; `ReservationConcurrencyConflict` retries the complete Serializable transaction; CAS-loss unit test passes | PASS |
| Serializable isolation | Reserve, commit, release, and ambiguous transitions use Prisma Serializable transactions; refund helpers use the same level | PASS |
| One-credit reservation wins race | Two independent reservation/refund PostgreSQL clients leave exactly one owner and no over-allocation | PASS |
| One-credit refund wins race | Refund-first PostgreSQL scenario withdraws the old lot and reservation selects the next ACTIVE FIFO lot | PASS |
| Two-credit reservation/refund race | Reservation leaves one available credit; PostgreSQL refund transition withdraws with `currentAmount=2`, `reservedAmount=1` | PASS |
| ACTIVE commit | Commit decrements lot reserved/current and aggregate reserved, increments committed, and emits one usage event | PASS |
| WITHDRAWN commit | Existing RESERVED ownership remains valid; PostgreSQL test commits a withdrawn lot and conserves aggregate quantities | PASS |
| ACTIVE release | Release decrements lot and aggregate reserved without changing aggregate refunding | PASS |
| WITHDRAWN release | Release decrements lot/aggregate reserved and increments aggregate refunding; unit and PostgreSQL tests pass | PASS |
| Final withdrawn completion and refund closure | Last commit atomically sets `COMPLETED` and cancels live refund as `NO_CREDITS_REMAINING` with no provider reference | PASS |
| Ambiguous hold | `markAmbiguous` changes only reservation status; lot and aggregate holds remain; subsequent capacity is exhausted in unit test | PASS |
| Released replay idempotency | Source key reuses the same reservation/counter identity, excludes ineligible original lots, and can select a fresh eligible lot; replay tests pass | PASS |
| Multiple live reservations per lot | New 14-test unit regression reserves two sequential source keys on one 2-credit lot, asserts same lot and `reservedAmount=2`, then third exhaustion | PASS |
| Multiple-lot isolation | Old/completed/withdrawn/refunded/requested lots are skipped; unrelated active lot remains unchanged in PostgreSQL test | PASS |
| Aggregate conservation | Reserve, commit, release, withdrawal, reactivation, completion, and provider-settlement ownership boundaries are asserted; ADMIN-003 owns provider movement | PASS |
| Eight real PostgreSQL races | Independent Prisma clients/connections exercise: reservation-first one-credit, refund-first alternate lot, two-credit withdrawal, withdrawn release, withdrawn commit, final completion/refund cancellation, reactivation FIFO, and unrelated-lot isolation | PASS |
| Validations | Focused unit PASS; integration PASS; Prisma PASS; build PASS; diff check PASS; full unit suite only has the unchanged observability baseline failures | PASS |
| Non-goals and ownership | Diff is limited to the reservation service, focused unit test, and task report; no endpoint, UI, valuation, provider settlement, schema, or shared-contract changes | PASS |

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-022`
- Implementation branch/commit: `task/ARCH-010-BACKGROUND-022` at `af2e2f134387e7da768ce8fe68f27c83654cbc6b` (`Fix purchased credit lot reservation CAS`), pushed to `origin/task/ARCH-010-BACKGROUND-022`; worktree clean after validation.
- Implementation base: `992638f0e7be8c40249adfece485fb4f65439c53`.
- Parent report branch: `task/ARCH-010-BACKGROUND-022`; report update pending as the next parent-only commit.

### Architect Review
Pending.

## Architect Review — Attempt 2

### Status

**Changes Requested — one functional CAS correction only**

This review intentionally prioritises production behaviour over exhaustive test
coverage.

The audit correction for final withdrawn-credit consumption is accepted:

```text
WITHDRAWN purchase
currentAmount = quantity
reservedAmount = quantity
existing RESERVED reservation commits
  -> decrement currentAmount/reservedAmount
  -> transition purchase to COMPLETED in the same transaction
  -> cancel live refund as NO_CREDITS_REMAINING
  -> no provider refund movement
```

The ACTIVE/WITHDRAWN commit/release semantics, refunding conservation, FIFO/status
filtering, Serializable transaction convention, whole-transaction retry, exact
purchase-lot ownership, and multiple-lot isolation are also accepted.

One production allocation defect remains.

---

### Finding — valid second reservation from the same ACTIVE lot fails its CAS

Both the new-reservation path and released-reservation replay path currently update
the selected purchase lot with a predicate equivalent to:

```ts
reservedAmount: {
  lte: lot.currentAmount - lot.reservedAmount - quantity
}
```

This does **not** express the required invariant:

```text
currentAmount - reservedAmount >= quantity
```

It effectively compares the durable `reservedAmount` against a value that has already
subtracted that same `reservedAmount`.

Concrete example:

```text
purchase:
  currentAmount  = 2
  reservedAmount = 1
  status         = ACTIVE

requested quantity = 1

spendable:
  2 - 1 = 1
```

The reservation is valid.

But the current CAS becomes:

```text
reservedAmount <= 2 - 1 - 1
1 <= 0
```

which is false.

Therefore:

```text
first conversation reserves credit 1
second conversation arrives before the first commits/releases
one purchased credit is still genuinely available
```

but the second reservation loses the lot CAS.

Because the lot has not actually changed, whole-transaction retry selects the same lot
and encounters the same invalid predicate again. It can exhaust the retry budget even
though spendable purchased capacity exists.

This violates the task's core rule that many reservations may safely consume a
purchase lot up to:

```text
currentAmount - reservedAmount
```

and unnecessarily serialises usage of a multi-credit lot behind completion/release of
earlier conversations.

This is a production functionality defect; it is not a request for broader test
coverage.

---

### Required production correction

Modify only:

```text
src/services/purchased-recovery-reservation.service.ts
```

Correct the purchase-lot reservation CAS in **both** locations:

```text
1. released-reservation replay reactivation;
2. new purchased reservation.
```

The transaction has already:

```text
freshly selected the lot
verified spendableLotQuantity(lot) >= quantity
captured lot.id
captured lot.version
captured lot.status = ACTIVE
captured lot.currentAmount
captured lot.reservedAmount
```

Use those exact freshly-read values as the CAS authority.

Required shape:

```ts
const updatedLot =
  await transaction.recoveryCreditPurchase.updateMany({
    where: {
      id: lot.id,
      version: lot.version,
      status: RecoveryCreditPurchaseStatus.ACTIVE,
      currentAmount: lot.currentAmount,
      reservedAmount: lot.reservedAmount,
    },
    data: {
      reservedAmount: { increment: quantity },
      version: { increment: 1 },
    },
  });
```

Then retain:

```ts
if (updatedLot.count !== 1) {
  throw new ReservationConcurrencyConflict();
}
```

Why this is the required shape:

```text
spendability is proven from the fresh snapshot before CAS;
exact version + exact currentAmount + exact reservedAmount + ACTIVE status prove that
the same snapshot still owns the mutation;
any competing reservation/refund/commit/release changes version and/or balances;
CAS loss restarts the whole Serializable transaction and selection from fresh state.
```

Do not replace this with:

```text
raw SELECT FOR UPDATE
Redis/process locks
shop-wide purchase locks
unversioned update
blind retry of the same lot
```

Do not alter FIFO ordering or the aggregate counter CAS.

---

### Functional regression evidence required

This does **not** require another broad concurrency matrix.

Add the smallest permanent regression proving the actual defect.

In:

```text
tests/unit/services/purchased-recovery-reservation.service.test.ts
```

add:

```text
allows multiple live reservations from one ACTIVE multi-credit purchase lot
```

Exact scenario:

```text
purchase:
  status         = ACTIVE
  currentAmount  = 2
  reservedAmount = 0

aggregate:
  two spendable purchased credits
```

Execute sequentially without committing/releasing the first reservation:

```text
reserve(sourceKey A, quantity 1)
reserve(sourceKey B, quantity 1)
```

Require:

```text
A -> reserved
B -> reserved

both reservations:
  status = RESERVED
  same purchasedCreditPurchaseId

purchase:
  currentAmount  = 2
  reservedAmount = 2

aggregate:
  reservedQuantity increased by 2
```

Then a third independent source-key reservation must return:

```text
credits-exhausted
```

This proves the lot supports concurrent/live ownership up to its actual balance.

Also ensure the existing released-reservation replay test still passes. If convenient,
strengthen that existing test so replay can reserve the final available credit while a
different reservation already holds another credit from the same multi-credit lot.
Do not add a separate large test matrix solely for this review.

---

### Accepted Attempt-2 work — do not churn

Do not redesign or reopen:

```text
ACTIVE-only new allocation
REQUESTED/WITHDRAWN/COMPLETED/REFUNDED exclusion
original FIFO age after reactivation
aggregate purchased-credit accounting
reservation/refund version race
ACTIVE/WITHDRAWN commit
ACTIVE/WITHDRAWN release
WITHDRAWN release -> aggregate refunding
AMBIGUOUS hold semantics
final WITHDRAWN commit -> COMPLETED
refund cancellation with NO_CREDITS_REMAINING
Serializable isolation
bounded whole-transaction retry
exact purchasedCreditPurchaseId ownership
provider-refund ownership boundaries
```

Do not modify Shopify/Admin endpoints, valuation, provider settlement, schema, Shared
contracts, or other repositories.

---

### Attempt-3 allowed scope

Production:

```text
src/services/purchased-recovery-reservation.service.ts
```

Tests:

```text
tests/unit/services/purchased-recovery-reservation.service.test.ts
```

plus this task/Completion Report.

The existing PostgreSQL race suite need only be rerun for regression confidence; no
new PostgreSQL scenario is required specifically for this deterministic CAS bug unless
the implementation agent discovers a real database-only discrepancy.

---

### Attempt-3 validation

Run:

```bash
npx vitest run \
  tests/unit/services/purchased-recovery-reservation.service.test.ts

npm run test:integration
npm run prisma:validate
npm run build
git diff --check
```

Run the full unit suite only for regression awareness:

```bash
npm run test:unit
```

The existing unrelated observability baseline remains non-blocking only if unchanged.

Do not spend Attempt 3 fixing unrelated baseline diagnostics.

---

### Workflow / Completion Report

Preserve immutable Attempt-2 evidence, including:

```text
Attempt-2 implementation:
2f08bd70

Attempt-2 parent report:
96b414ab
```

Record the full SHAs in the Completion Report if repository history provides them.

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
```

The next authorized claim must increment to **Attempt 3 exactly once**.

Attempt 3 may return to `review` when:

```text
1. both reservation lot CAS sites use the exact fresh lot snapshot;
2. a 2-credit ACTIVE lot accepts two live 1-credit reservations before either commits;
3. a third reservation is exhausted;
4. focused/integration/build/Prisma/diff validation has no new regression;
5. status = review, executor = null, claimed_at = null;
6. both worktrees are clean and pushed.
```

Then STOP and return to `moda_architect`.

`ARCH-010-SHOPIFY-025`, `ARCH-010-ADMIN-002`, `ARCH-010-ADMIN-003`,
`ARCH-010-SYSTEM-TEST-001`, and `ARCH-010-SYSTEM-TEST-003` remain gated until
`BACKGROUND-022` is architect-accepted Complete.

