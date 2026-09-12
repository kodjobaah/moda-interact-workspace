---
id: ARCH-010-BACKGROUND-011
architecture_id: ARCH-010
title: Make the lifetime Free recovery entitlement plan-independent and consume it after purchased credits
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 41
executor: copilot
claimed_at: '2026-09-12T17:25:09Z'
attempt: 3
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-001
- ARCH-007-BACKGROUND-003
- ARCH-007-BACKGROUND-009
enables:
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-009
- ARCH-010-BACKGROUND-014
- ARCH-010-BACKGROUND-019
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-011: Make the lifetime Free recovery entitlement plan-independent and consume it after purchased credits

## Objective

Change recovery admission so `LIFETIME_FREE_RECOVERY_CREDITS` is a shop-lifetime fallback available under both Free and Paid subscriptions, while purchased lifetime top-ups are intentionally consumed before that lifetime Free grant.

This task implements the **purchased → shop-lifetime Free** fallback primitive. `ARCH-010-BACKGROUND-019` later inserts promotional credits ahead of purchased capacity, so the final ARCH-010 order is:

```text
FREE
  promotional credits
  -> purchased lifetime credits
  -> shop-lifetime Free credits
  -> BLOCK NEW RECOVERY ADMISSION

PAID
  promotional credits
  -> paid period included credits
  -> purchased lifetime credits
  -> shop-lifetime Free credits
  -> BLOCK NEW RECOVERY ADMISSION
```

This task owns only the plan-independent lifetime-Free primitive and the purchased→lifetime fallback. It must not implement promotional accounting itself; `ARCH-010-BACKGROUND-019` owns the promotional layer and composes it ahead of this helper.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/free-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/free-recovery-reservation.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/integration/free-recovery-reservation.concurrency.integration.test.ts
database/prisma/schema.prisma
package.json
```

Read the implemented ARCH-007 purchased-credit reservation path before editing. Do not duplicate its CAS/transaction logic.

## 1. Lifetime Free policy must be plan-independent

The current development implementation may still derive Free allowance from plan-owned or adjustment compatibility state. DATABASE-013 removes that schema. Delete those reads rather than adapting them.

For every active mapped subscription plan (Free or Paid), load exactly:

```text
ShopEntitlementCounter(counter = LIFETIME_FREE_RECOVERY_CREDITS)
```

The effective shop-lifetime state is derived only from that durable shop counter:

```text
grant = counter.grantedQuantity
remaining = max(grant - committedQuantity - reservedQuantity, 0)
```

There is no `BillingPlan.freeLifetimeConversationAllowance`, no `BillingAllowanceAdjustment` query and no signed compatibility arithmetic in first production.

For an active/onboarded shop, a missing lifetime counter after DATABASE-013 is a configuration/data-integrity error. Fail closed; do not silently create a fresh grant during ordinary recovery admission.

## 2. Keep the existing service/file names unless a rename is mechanically required

`free-recovery-reservation.service.ts` is an accepted ARCH-007 implementation. To keep this Luna task bounded, do not perform a broad rename solely for terminology.

Change its eligibility semantics:

- remove the rule that rejects Paid plans as `not-free`;
- require an active mapped subscription and active Shop through the effective policy;
- reserve/commit/release the shop-lifetime counter regardless of current plan kind;
- preserve the existing serializable/CAS concurrency guarantees;
- lifetime-Free commit remains `ShopifyReportState.NOT_APPLICABLE` and MUST NOT create a Shopify App Event.

If the current public outcome type contains `not-free`, remove it only if all repository references/tests can be updated within this task. Do not leave Paid lifetime fallback impossible merely to preserve that outcome.

## 3. Free-plan recovery order

Change Free recovery admission from the legacy order to exactly:

```text
try purchased reservation
  -> reserved: fund from PURCHASED_RECOVERY_CREDITS
  -> exhausted: try lifetime Free reservation
       -> reserved: fund from LIFETIME_FREE_RECOVERY_CREDITS
       -> exhausted: capacity-exhausted
```

Purchased credits MUST be attempted first even when lifetime Free credits remain.

Do not reserve both buckets for one recovery.

## 4. Commit/release ownership

The admission result must retain enough source information that the provider-send path commits/releases exactly the bucket that was reserved.

Required:

```text
purchased source
  -> existing purchased reservation commit/release

lifetime-free source
  -> existing lifetime Free counter reservation commit/release
```

Do not switch funding source after the provider call has begun.

## 5. Refund consequence is intentional

Purchased credits are refundable only while unused under the later refund lifecycle. Because purchased credits are consumed before lifetime Free credits, a recovery intentionally reduces purchased refundable quantity first.

Do not reverse the order to maximise refundability.

## Required regression coverage

At minimum prove:

1. Free + purchased available + lifetime Free available reserves purchased;
2. Free + purchased exhausted + lifetime Free available reserves lifetime Free;
3. Free + both exhausted returns capacity-exhausted;
4. Paid plan can reserve lifetime Free through the plan-independent lifetime service;
5. lifetime Free reservation remains concurrency-safe;
6. lifetime Free commit creates no Shopify-reportable App Event;
7. purchased commit remains unchanged;
8. replay does not reserve a second bucket;
9. failure/release returns quantity to the same reserved bucket;
10. no plan-owned lifetime allowance field is read;
11. platform-policy changes after grant do not alter an existing shop's counter grant;
12. no signed lifetime-Free adjustment query or compatibility arithmetic exists;
13. missing lifetime counter on active onboarded shop fails closed;
14. inactive/uninstalled shop remains blocked by existing shop-availability rules.

Run focused tests plus repository-declared build/typecheck/test validation required by the task. Preserve unrelated documented baseline failures.

## Non-goals

Do not:

- implement paid period included-credit reservation (BACKGROUND-002);
- implement top-up purchase billing;
- implement refunds;
- implement the promotional-credit bucket in this task (`ARCH-010-BACKGROUND-019` owns that layer);
- change Shopify plans;
- reset/regrant lifetime Free credits;
- modify another repository.

## Stop conditions

Stop and return to `moda_architect` if:

- DATABASE-013 schema/client is unavailable;
- purchased reservation semantics differ materially from the inspected ARCH-007 design;
- the required routing would need cross-repository contract changes;
- preserving the existing reservation idempotency/source-key rules is not possible.

## Completion Report

### Status
Ready for Review

### Files Changed
- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/free-recovery-reservation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `src/services/recovery-billing.service.ts`
- `tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `tests/unit/services/free-recovery-reservation.service.test.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `tests/unit/services/recovery-billing.service.test.ts`

### Work Completed
Implemented the DATABASE-013-backed, plan-independent lifetime Free fallback.
The effective policy now reads only the durable
`LIFETIME_FREE_RECOVERY_CREDITS` counter and fails closed when that counter is
missing. Legacy plan-owned lifetime allowance reads, signed adjustment queries,
and `FREE_RECOVERY_LIFETIME` compatibility identifiers were removed from the
touched path.

Free admission now attempts purchased credits before lifetime Free credits, and
Paid admission uses lifetime Free after included and purchased capacity are
exhausted. Admission source identity is preserved so commit, release, and
ambiguous provider outcomes operate on the exact reserved bucket. Lifetime Free
commit remains `NOT_APPLICABLE` and does not create a Shopify-reportable App
Event. Reconciliation now provisions the renamed lifetime counter for new Free
subscriptions without changing an existing grant.

Required regressions cover purchased-first ordering, lifetime fallback and
exhaustion, Paid fallback, concurrency, replay, same-bucket release/commit,
missing-counter fail-closed behavior, plan-independent grants, and inactive or
uninstalled shop blocking. Attempt 3 additionally uses one canonical recovery
source key across purchased and lifetime-Free admission, preserves the owning
counter on replay and provider failure, spends existing purchased capacity even
when pack purchase is disabled, removes the partial Paid included-capacity
composition from this bounded task, and adds activation/reconciliation grant
preservation regressions.

### Validation Results
Focused tests:
`npm test -- --run tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/recovery-billing.service.test.ts tests/unit/services/billing-subscription-reconciliation.service.test.ts tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 4 files, 71 tests; 1 integration test was skipped because its database
guard requires explicit disposable-test flags.

Guarded PostgreSQL concurrency test:
`TEST_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/moda_interact' MODA_DISPOSABLE_INTEGRATION=1 npm test -- --run tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 1 file, 1 test.

Prisma generation succeeded through `npm run build` with the hydrated
DATABASE-013 schema/client. The repository build remains non-zero under the
documented `TYPECHECK-001` baseline: no current-task files produce errors, but
the pre-existing purchased-reservation nullability errors and recovery-credit
purchase/refund schema-consumer errors remain.

Repository unit validation via `npm run test:unit` remains non-zero with 44
files passed and 3 files failed, 488 tests passed and 41 failed. The failures
are in the unrelated recovery-credit purchase/refund consumers and observability
startup baseline; no Attempt-3 changed file produced a test failure.

`git diff --check` passed. The database submodule remains an unstaged gitlink at
`014408e0402221f08a3961880b34e828a8bdc736` and was not modified or committed.

### Deviations
Repository-wide build and unit validation retain documented/unrelated baseline
failures described above. The focused task validation is green.

### Assumptions
The hydrated DATABASE-013 database submodule and generated Prisma client are
the accepted prerequisite baseline supplied for this attempt.

### Unresolved Issues
Repository-wide recovery-credit purchase/refund consumers still require the
DATABASE-013 follow-up work owned outside this task. Those errors do not affect
the changed lifetime Free path.

### Architectural Concerns
None. No cross-repository contract, schema, transaction, or idempotency
boundary was changed.

### Git / VCS
Task branch: `task/ARCH-010-BACKGROUND-011`

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-011
  parent branch: task/ARCH-010-BACKGROUND-011
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-011
  implementation branch: task/ARCH-010-BACKGROUND-011
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no
  start-of-attempt synchronization: implementation and parent task branches were
    already aligned with their origin/task/ARCH-010-BACKGROUND-011 refs; origin/main
    was an ancestor of the implementation branch and no merge was required

Implementation repository:
  repository: moda-interact-background
  implementation commit: db8cec1 (fix: complete BACKGROUND-011 attempt 3 corrections)
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  pushed: yes

Parent workspace:
  task file: docs/decisions/background/ARCH-010/BACKGROUND-011-shop-lifetime-free-fallback.md
  claim commit: e21293b (chore: claim BACKGROUND-011 attempt 3)
  report commit: pending (this report update)
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review

#### Review Status

Changes Requested — Attempt 2.

#### Review Summary

Attempt 2 has several accepted pieces:

```text
DATABASE-013 revision:
  014408e0402221f08a3961880b34e828a8bdc736

implementation commit:
  a6b7dd3

latest submitted parent report publication:
  1ce6e8f

focused unit tests:
  42 passed

guarded PostgreSQL concurrency regression:
  1 passed

database gitlink:
  intentionally unstaged
```

Architect inspection confirms the following implementation work is correct and should
be retained:

```text
FREE_RECOVERY_LIFETIME
  -> LIFETIME_FREE_RECOVERY_CREDITS

remove BillingPlan.freeLifetimeConversationAllowance reads

remove BillingAllowanceAdjustment reads/signed compatibility arithmetic

derive lifetime state from:
  ShopEntitlementCounter.grantedQuantity
  ShopEntitlementCounter.committedQuantity
  ShopEntitlementCounter.reservedQuantity

missing active-shop lifetime counter fails closed during ordinary admission

lifetime reservation remains SERIALIZABLE + version/CAS protected

Paid plans are no longer rejected by the lifetime reservation service merely because
the plan kind is PAID_METERED

lifetime commit remains ShopifyReportState.NOT_APPLICABLE

accepted BACKGROUND-001 initial activation producer now targets
LIFETIME_FREE_RECOVERY_CREDITS
```

The PostgreSQL concurrency regression is accepted evidence that the renamed lifetime
counter path retains the reservation concurrency property.

The task cannot yet be accepted because the current Free fallback composition can
reserve **two different funding buckets for the same recovery on replay**, and purchased
lifetime-credit spendability is incorrectly gated by whether the current plan allows
buying another recovery-credit pack.

There is also an out-of-scope partial Paid routing implementation that couples included
capacity exhaustion to `recoveryCreditPack.enabled`. BACKGROUND-002 owns the
concurrency-safe Paid included-credit routing boundary and must compose that final Paid
order after BACKGROUND-011 supplies the plan-independent lifetime primitive.

#### Changes Requested — Attempt 3

Implement exactly the corrections below. Preserve all accepted Attempt-2 work not
explicitly changed here.

##### 1. One recovery may own exactly one capacity reservation

Current code uses two reservation identities:

```text
purchased:
  purchased:${createRecoveryIdempotencyKey(shopId, recoveryId)}

lifetime Free:
  createRecoveryIdempotencyKey(shopId, recoveryId)
```

This violates Required Regression 8.

Concrete failure:

```text
call 1:
  purchased exhausted
  -> lifetime Free reserves recovery:shop:recovery

capacity later changes / replay occurs

call 2:
  purchased now available
  -> purchased service sees no purchased:... reservation
  -> reserves PURCHASED_RECOVERY_CREDITS as a second bucket
```

The same recovery must never own both reservations.

Use **one canonical UsageReservation source identity per recovery** across the
purchased/lifetime-Free fallback:

```text
canonicalSourceKey = createRecoveryIdempotencyKey(shopId, recoveryId)
```

Do not solve this with a preflight-only read of two different keys; that is race-prone.

Use the database uniqueness of:

```text
UsageReservation.sourceKey @unique
```

as the cross-bucket serialization boundary.

Because both reservation services may encounter an already-existing reservation owned
by the other shop entitlement counter, make replay ownership explicit.

Required behaviour:

```text
existing reservation linked to PURCHASED_RECOVERY_CREDITS
  -> recovery remains purchased-funded
  -> do not reserve lifetime Free

existing reservation linked to LIFETIME_FREE_RECOVERY_CREDITS
  -> recovery remains lifetime-Free-funded
  -> do not reserve purchased

existing reservation status RESERVED / COMMITTED / AMBIGUOUS / RELEASED
  -> replay must preserve the already-selected bucket
  -> never switch funding source because capacity later changed
```

A bounded implementation may extend the existing reservation outcomes so the caller can
distinguish the counter that owns an existing reservation. Do not create a new database
model or cross-repository contract.

Files expected to be involved:

```text
src/services/recovery-billing.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/free-recovery-reservation.service.ts
tests/unit/services/recovery-billing.service.test.ts
focused reservation-service tests where ownership classification is implemented
```

Stop if satisfying this requires a database schema change.

##### 2. Purchased lifetime credits are spendable independently of pack purchase eligibility

Current code contains:

```ts
const pack = policy.recoveryCreditPack;
if (!pack?.enabled) return null;
```

inside purchased-capacity admission.

That is incorrect.

`recoveryCreditPackEnabled` / `recoveryCreditPack` controls whether the merchant can
**buy a new pack**. It does not erase or disable already-purchased lifetime credits.

For Free recovery admission, always attempt the existing
`PURCHASED_RECOVERY_CREDITS` reservation before lifetime Free, regardless of whether the
current plan's recovery-credit-pack purchase configuration is enabled.

Required:

```text
Free plan
+ recoveryCreditPack disabled/null
+ existing purchased capacity
=> reserve PURCHASED_RECOVERY_CREDITS

Free plan
+ no purchased capacity
=> attempt LIFETIME_FREE_RECOVERY_CREDITS
```

Do not require a Shopify pack event handle merely to spend an already-active purchased
credit.

##### 3. Keep Paid included-credit composition out of BACKGROUND-011

Attempt 2 added a partial Paid routing rule:

```text
paidIncludedCapacityExhausted(policy)
```

whose result depends on:

```text
policy.recoveryCreditPack?.enabled
```

and usage aggregation embedded in the pack policy.

This produces different Paid admission semantics depending on whether top-up purchase is
enabled and partially implements work explicitly owned by `ARCH-010-BACKGROUND-002`.

For Attempt 3, keep BACKGROUND-011 bounded:

```text
BACKGROUND-011 owns:
  plan-independent lifetime counter policy
  plan-independent lifetime reservation primitive
  Free purchased -> lifetime-Free fallback
  canonical single-reservation replay ownership

BACKGROUND-002 owns:
  current BillingPeriod INCLUDED_RECOVERY_CREDITS reservation
  detection of included exhaustion
  final Paid included -> purchased -> lifetime-Free composition
```

Therefore:

- remove/revert the new `paidIncludedCapacityExhausted(...)` composition from
  `RecoveryBillingService.admit`;
- do not use `recoveryCreditPack.enabled` or pack usage aggregation to decide whether
  Paid included capacity is exhausted;
- preserve the pre-BACKGROUND-002 Paid route until BACKGROUND-002 replaces it with the
  durable period-counter reservation path;
- prove only that the lifetime reservation primitive itself accepts an active mapped
  `PAID_METERED` policy.

The final architecture remains:

```text
Paid:
  selected promotion
  -> current-period INCLUDED_RECOVERY_CREDITS
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> BLOCK
```

but BACKGROUND-002 is the task that composes the Paid included-capacity boundary.

##### 4. Add the missing accepted-BACKGROUND-001 conformance regressions

Attempt 2 changed:

```text
src/services/billing-subscription-reconciliation.service.ts
```

from the removed enum name to `LIFETIME_FREE_RECOVERY_CREDITS`, but the focused test
set contains no corresponding reconciliation-service regression.

Add focused tests in the existing reconciliation test surface proving:

```text
A. first verified activation with no lifetime counter
   -> creates/upserts exactly LIFETIME_FREE_RECOVERY_CREDITS
   -> grantedQuantity comes from PlatformBillingPolicy.lifetimeFreeRecoveryAllowance

B. existing lifetime counter replay
   -> preserves grantedQuantity
   -> preserves committedQuantity
   -> preserves reservedQuantity
   -> preserves refundingQuantity
   -> preserves version/history
   -> does not regrant/reset

C. accepted BACKGROUND-001 queue/retry/CAS/onboarding behaviour is unchanged
   -> no queue-name/payload/job-id/retry/schedule alteration in this task
```

Do not reopen any other BACKGROUND-001 semantics.

##### 5. Required Attempt-3 regression matrix

At minimum, focused tests must now prove all of the following:

```text
1. Free + purchased available + lifetime available -> purchased
2. Free + purchased exhausted + lifetime available -> lifetime Free
3. Free + both exhausted -> blocked
4. Free + pack purchase disabled/null + purchased available -> purchased
5. active mapped Paid policy can reserve lifetime Free through the lifetime service
6. lifetime reservation remains concurrency-safe
7. lifetime commit -> NOT_APPLICABLE; no Shopify-reportable App Event
8. purchased commit behaviour unchanged
9. lifetime-selected recovery replay after purchased capacity appears
   -> remains lifetime-funded
   -> no purchased reservation is created
10. purchased-selected recovery replay
    -> remains purchased-funded
    -> no lifetime reservation is created
11. concurrent/retry conflict cannot create two UsageReservation rows/buckets for the
    same canonical recovery source key
12. definitive failure/release returns quantity to the originally selected bucket
13. ambiguous failure remains attached to the originally selected bucket
14. no plan-owned lifetime allowance read
15. no signed lifetime adjustment query/arithmetic
16. missing lifetime counter on active mapped shop fails closed
17. inactive/uninstalled shop remains blocked
18. initial activation creates only LIFETIME_FREE_RECOVERY_CREDITS when absent
19. initial activation preserves an existing lifetime counter exactly
20. platform-policy changes after grant do not change an existing shop grant
```

The existing real PostgreSQL concurrency test should remain and continue to pass.

##### 6. Validation

Use database revision:

```text
014408e0402221f08a3961880b34e828a8bdc736
```

or a later architect-accepted DATABASE-013 `main` revision containing the same final
schema.

Run at minimum:

```text
focused effective-policy tests
focused lifetime reservation tests
focused purchased reservation tests if changed
focused RecoveryBillingService tests
focused billing-subscription-reconciliation tests added above
guarded PostgreSQL lifetime reservation concurrency regression
npm run build
npm run test:unit
git diff --check
```

Repository-wide build/unit baseline failures may remain only when they are unchanged,
documented and outside every file changed by Attempt 3.

Any diagnostic/failure in an Attempt-3 changed file is a blocker.

##### 7. Scope guard

Do not:

```text
implement BACKGROUND-002 included-period reservations
implement BACKGROUND-014 FIFO purchased lots
implement BACKGROUND-019 promotional reservations
change DATABASE-013 schema
stage the database gitlink
modify Shared/Shopify/Admin repositories
change accepted BACKGROUND-001 queue/retry/scheduling semantics
introduce compatibility aliases for removed DATABASE-013 names
```

##### 8. VCS / report evidence

Preserve the submitted Attempt-2 evidence:

```text
implementation:
  a6b7dd3

latest submitted parent report publication:
  1ce6e8f

database revision:
  014408e0402221f08a3961880b34e828a8bdc736
```

For Attempt 3 record:

```text
new implementation commit
new parent claim commit
new parent report/status commit
canonical parent worktree
canonical implementation worktree
all physical-isolation declarations
all start-of-attempt synchronization outcomes
database revision
database gitlink staged: no
main branches modified: no
```

#### Architect Decision

**Changes Requested — Attempt 2.**

The task returns to:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next valid claim is **Attempt 3**.
