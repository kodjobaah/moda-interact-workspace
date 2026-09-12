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
status: review
priority: 68
executor: copilot
claimed_at: '2026-09-12T21:34:04Z'
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-BACKGROUND-011
enables:
- ARCH-010-ADMIN-003
- ARCH-010-BACKGROUND-019
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-12'
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
Paid: selected promotional -> included -> purchased -> lifetime Free -> BLOCK NEW RECOVERY ADMISSION
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

## Provider reconciliation and pre-production refund cleanup

Do not infer provider-confirmed purchase units from local spendable balance.

A Partner Dashboard refund/credit does not reduce the original App Pricing top-up meter quantity.

ARCH-010 partial refunds keep the purchase provider status `ACTIVE` and lower local lot/aggregate spendable balance through refunded quantities.

DATABASE-013 removes `RecoveryCreditPurchaseStatus.REFUNDED`, refund settlement-mode/correction-UsageEvent fields and the negative-App-Event refund model. Inspect `recovery-credit-purchase.service.ts`, provider reconciliation and any refund worker/helper code. Remove any remaining branch whose purpose is to:

```text
mark a purchase REFUNDED
submit a negative/fractional App Event as refund settlement
create/read a refund correction UsageEvent
retry automatic provider refund settlement
```

Do not replace that behaviour with another automatic provider refund processor. Human provider settlement is owned by ADMIN-002/003 and DATABASE-013's `REFUND | CREDIT` evidence model.

Provider reconciliation must treat the original provider-confirmed top-up unit as explained by the durable purchase even after local partial refunds; it must not re-grant refunded local capacity.

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
14. no REFUNDED/negative-App-Event correction branch remains, and provider reconciliation never re-grants locally refunded capacity.

Run actual repository scripts from `package.json` plus task-required focused tests, build, Prisma validation if declared and `git diff --check`.

## Explicit non-goals

Do not implement Admin refund approval, Partner Dashboard settlement, merchant UI, refund system messages, negative/fractional App Events or a new queue.

## Stop

If existing runtime quantity semantics require one recovery reservation to span multiple purchase lots, STOP and return to `moda_architect`; do not invent a split-allocation model inside this task.

Return `review` and STOP after validation/completion report.

## Completion Report

### Status
Ready for Review — Attempt 2 corrections implemented.

### Files Changed
- `moda-interact-background/src/entrypoints/billing.ts`
- `moda-interact-background/src/services/purchased-recovery-reservation.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- `moda-interact-background/src/services/recovery-credit-refund.service.ts` deleted
- `moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-purchase.service.test.ts`
- `moda-interact-background/tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`
- `moda-interact-background/tests/unit/services/recovery-credit-refund.service.test.ts` deleted

### Work Completed
- Implemented deterministic FIFO purchased-lot selection by `activatedAt ASC NULLS LAST`, `createdAt ASC`, and `id ASC`.
- Added aggregate and exact-lot CAS reservation, commit, release, ambiguous retention, replay, and released-row reactivation behavior.
- Preserved purchased exhaustion fallback behavior and NOT_APPLICABLE recovery usage events.
- Added activation idempotency and provider reconciliation coverage so local refunds do not re-grant capacity.
- Removed obsolete automatic provider refund settlement registration and deleted the retired refund service/tests; no Admin settlement was added.
- Added focused coverage for FIFO skipping, aggregate/lot parity, replay identity, activation, and cleanup requirements.
- Added the required real PostgreSQL reserve-vs-refund-hold race using two independent Prisma clients, Serializable isolation, bounded P2034/CAS retries, and aggregate/lot conservation assertions. No ADMIN-003 production refund logic was added.
- Strengthened released-reservation replay coverage to prove the original reservation row and purchase-lot identity are retained while a second lot remains untouched.
- Attempt 2 correction checklist: Correction 1 implemented in the new PostgreSQL integration test; Correction 2 implemented in the purchased reservation unit test; Correction 3 implemented in the explicit VCS/worktree evidence below.

### Validation Results
- `npx vitest run tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/recovery-credit-purchase.service.test.ts`: passed, 2 files, 24 tests.
- `MODA_DISPOSABLE_INTEGRATION=1 npx vitest run tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts`: passed, 1 file, 1 test, against local disposable `moda_interact_test` initialized with `20260912000000_arch010_first_production_baseline`.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- `npm test`: 48 files passed, 541 tests passed, 9 skipped; one unrelated existing observability assertion fails because it expects shared runtime `0.9.0` while package metadata is `0.11.0`.
- `git diff --check`: passed.
- Source search found no remaining `REFUNDED`, refund-settlement, correction-event, negative-App-Event, `settlementMode`, or obsolete refund-service branch.

### Git / VCS
Task branch: `task/ARCH-010-BACKGROUND-014`

Physical task isolation:
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-014`
  parent branch: `task/ARCH-010-BACKGROUND-014`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-014`
  implementation branch: `task/ARCH-010-BACKGROUND-014`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: yes
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-background`
  commit: `2104959` (`test: complete purchased reservation concurrency proof`)

Parent workspace:
  commit: `a335f9b` (Attempt-2 Completion Report)

The implementation `database` gitlink remains intentionally unstaged and was not changed or published by this task. No main branch was modified or merged.

### Architect Review

**Status:** Changes Requested — Attempt 1

The production implementation is architecturally conformant on inspection. Do **not** rewrite the FIFO purchased-reservation implementation merely because this task is being returned to `ready`. The required correction is limited to concurrency/replay validation and the mandatory VCS evidence unless the new PostgreSQL test exposes an actual production defect.

#### Correction 1 — add a real PostgreSQL reserve-vs-refund-hold concurrency proof

The existing unit test `allows at most one of a full refund hold and recovery reservation to consume shared capacity` uses an in-memory mocked transaction. It does not exercise PostgreSQL Serializable isolation, transaction rollback, independent connections, or real version/CAS conflicts. The task requires proof that concurrent purchased reservation and refund hold cannot consume the same purchase-lot capacity.

Create:

```text
moda-interact-background/tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts
```

Use the same disposable PostgreSQL gate and cleanup pattern already used by:

```text
tests/integration/free-recovery-reservation.concurrency.integration.test.ts
tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts
```

The test MUST use at least two independent `PrismaClient` connections and one real `PurchasedRecoveryReservationService` instance. Seed one shop with:

```text
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS):
  grantedQuantity = 1
  committedQuantity = 0
  reservedQuantity = 0
  refundingQuantity = 0

RecoveryCreditPurchase:
  status = ACTIVE
  creditsGranted = 1
  committedQuantity = 0
  reservedQuantity = 0
  refundingQuantity = 0
  refundedQuantity = 0
```

Create the required provider-confirmed purchase `UsageEvent`/relations using valid DATABASE-013 schema fields. Do not add test-only schema or production hooks.

Race these operations with `Promise.all`:

1. `PurchasedRecoveryReservationService.reserve({ shopId, sourceKey })`;
2. a test-local **refund-hold transaction** implementing the already-agreed ADMIN-003 hold invariant against the same aggregate counter and exact purchase lot. The helper must:
   - run at `Prisma.TransactionIsolationLevel.Serializable`;
   - re-read both aggregate counter and lot inside each attempt;
   - require one whole credit is currently refundable/spendable;
   - CAS/version-update `purchase.refundingQuantity += 1` and `aggregate.refundingQuantity += 1`;
   - treat a zero-row CAS as a retryable conflict;
   - retry bounded `P2034`/CAS conflicts using the repository-approved bounded pattern;
   - return `held` only when both updates commit in the same transaction; otherwise return `unavailable` after observing that the credit has been reserved/consumed.

After both operations settle, assert exactly one capacity owner won:

```text
(reservation outcome is reserved) XOR (refund hold outcome is held)
```

Then query PostgreSQL and assert all of the following:

```text
aggregate.reservedQuantity + aggregate.refundingQuantity == 1
lot.reservedQuantity + lot.refundingQuantity == 1
aggregate.committedQuantity == 0
lot.committedQuantity == 0
lot.refundedQuantity == 0
aggregate granted - committed - reserved - refunding >= 0
lot creditsGranted - committed - reserved - refunding - refunded >= 0
```

If the reservation wins, exactly one `UsageReservation` for the supplied `sourceKey` must point to that exact `RecoveryCreditPurchase.id`. If the refund hold wins, no reservation may have consumed that credit.

This is a concurrency test only. Do not implement ADMIN-003 production refund logic in `moda-interact-background`.

#### Correction 2 — make replay-lot identity explicit in the unit test

The task requires `replay keeps original lot identity`. Strengthen the existing released-reservation reactivation test in:

```text
moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts
```

Seed at least two ACTIVE spendable purchase lots. Reserve the source key once, capture the original `purchasedCreditPurchaseId`, release it, then reserve the **same source key** again. Assert:

```text
reservation row id is unchanged
purchasedCreditPurchaseId is unchanged
the second lot remains untouched
no second UsageReservation row is created
```

Do not switch a replayed/released source key to a newer purchase lot.

#### Correction 3 — Completion Report VCS/worktree evidence

The Completion Report names the two task worktrees but omits the mandatory start-of-attempt synchronization outcomes required by `docs/agent-worktree-isolation-policy.md` and `docs/agent-vcs-ownership-policy.md`. On Attempt 2, reclaim the same task through the canonical launcher path and record the evidence explicitly.

The final `### Git / VCS` section MUST contain, at minimum:

```text
Task branch: task/ARCH-010-BACKGROUND-014

Physical task isolation:
  parent worktree: <launcher-resolved canonical parent path>
  parent branch: task/ARCH-010-BACKGROUND-014
  implementation worktree: <launcher-resolved canonical implementation path>
  implementation branch: task/ARCH-010-BACKGROUND-014
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation repository:
  repository: moda-interact-background
  commit: <Attempt-2 implementation/test commit>

Parent workspace:
  commit: <Attempt-2 Completion Report commit>
```

Do not modify either `main` branch. Keep the database gitlink unstaged unless the task's canonical dependency materialization explicitly changes it.

#### Validation for Attempt 2

Run the repository-declared commands from the canonical implementation worktree. At minimum:

```text
npx vitest run tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/recovery-credit-purchase.service.test.ts

MODA_DISPOSABLE_INTEGRATION=1 TEST_DATABASE_URL=<disposable-postgresql-url> \
  npx vitest run tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts

npm run prisma:validate
npm run build
npm test
git diff --check
```

Document the exact pass/fail counts. Known unrelated baseline failures may be referenced by their durable baseline evidence, but any failure in the changed purchased-reservation/refund-hold slice is a blocker.

#### Scope and stop conditions

Do not change cross-bucket priority. The final architecture remains:

```text
Paid: promotional -> included -> purchased FIFO -> lifetime Free -> block
Free: promotional -> purchased FIFO -> lifetime Free -> block
```

`BACKGROUND-019` still owns promotion-first routing. `ADMIN-003` still owns the production refund hold/settlement action.

Expected Attempt-2 code changes are test/report changes only. Do not refactor production reservation/purchase code opportunistically. If the real PostgreSQL concurrency test demonstrates that the current production transaction can overspend or produce aggregate/lot divergence, stop and report that concrete failure to `moda_architect` rather than inventing a different concurrency model.

Return this SAME task to `review` after the required evidence passes, then STOP.
