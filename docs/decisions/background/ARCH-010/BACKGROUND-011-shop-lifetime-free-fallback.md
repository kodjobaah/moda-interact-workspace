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
status: complete
priority: 41
executor: null
claimed_at: null
attempt: 4
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

remaining =
    counter.grantedQuantity
    - counter.committedQuantity
    - counter.reservedQuantity
```

Required lifetime-Free invariants:

```text
grantedQuantity >= 0
committedQuantity >= 0
reservedQuantity >= 0

committedQuantity + reservedQuantity <= grantedQuantity
```

If an invariant that participates in this lifetime-Free calculation fails, fail closed.
Do not hide an invalid counter by clamping a negative result to zero.

No other generic counter field participates in BG11's lifetime-Free capacity model.

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

## 5. Purchased-credit accounting remains opaque to BG11

`BACKGROUND-011` defines the ordering relationship:

```text
try PurchasedRecoveryReservationService
    -> if it reserves, use purchased capacity
    -> if it is exhausted, try lifetime Free
```

BG11 MUST NOT duplicate or redefine the internal accounting formula used by
`PurchasedRecoveryReservationService`.

For this task, purchased capacity is consumed only through that service's public
reservation outcomes and reservation ownership.

The lifetime-Free model remains exclusively:

```text
grantedQuantity
committedQuantity
reservedQuantity
```

No unrelated generic counter field participates in lifetime-Free availability.

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
- redesign purchased-credit accounting internals;
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
Complete — architect accepted Attempt 4

### Files Changed
- `package.json`
- `package-lock.json`
- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/checkout-recovery.service.ts`
- `src/services/effective-billing-policy.service.ts`
- `src/services/free-recovery-reservation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `src/services/recovery-billing.service.ts`
- `tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `tests/unit/services/effective-billing-policy.service.test.ts`
- `tests/unit/services/free-recovery-reservation.service.test.ts`
- `tests/unit/services/purchased-recovery-reservation.service.test.ts`
- `tests/unit/services/recovery-billing.service.test.ts`

### Work Completed
Implemented the DATABASE-013-backed, plan-independent lifetime Free fallback.
The effective policy reads only the durable `LIFETIME_FREE_RECOVERY_CREDITS`
counter, validates its lifetime invariants, and fails closed for missing or
invalid state. Free admission uses one canonical recovery source key and tries
purchased capacity before lifetime Free capacity, while preserving the selected
bucket through RESERVED, COMMITTED, AMBIGUOUS, and RELEASED replays. Released
rows reactivate on the same `UsageReservation` row and counter through CAS; an
ambiguous row blocks and never falls through to another bucket. Lifetime Free
commit remains `NOT_APPLICABLE` and creates no Shopify-reportable App Event.

Reconciliation provisions `LIFETIME_FREE_RECOVERY_CREDITS` from the platform
policy only when absent and preserves existing grant, committed, reserved, and
version state. BACKGROUND-011 supplies the plan-independent lifetime reservation
primitive. BACKGROUND-002 owns the Paid `included -> purchased -> lifetime-Free`
composition. Shared `0.11.0` is consumed and the removed Shared-007 symbols are
absent from Background source/tests.

### Validation Results
Focused tests:
`npm test -- --run tests/unit/services/effective-billing-policy.service.test.ts tests/unit/services/free-recovery-reservation.service.test.ts tests/unit/services/purchased-recovery-reservation.service.test.ts tests/unit/services/recovery-billing.service.test.ts tests/unit/services/billing-subscription-reconciliation.service.test.ts`
passed: 5 files, 97 tests.

Guarded PostgreSQL concurrency test:
`TEST_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/moda_interact' MODA_DISPOSABLE_INTEGRATION=1 npm test -- --run tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 1 file, 1 test.

`npm run build` regenerated Prisma successfully but remains non-zero under the
documented DATABASE-013 schema-consumer baseline: 29 TypeScript errors remain
in unchanged `src/services/recovery-credit-purchase.service.ts` and
`src/services/recovery-credit-refund.service.ts`; no changed task file is in the
error list.

Repository unit validation via `npm run test:unit` remains non-zero with 44
files passed and 3 files failed, 501 tests passed and 41 failed. The failures
are confined to unchanged recovery-credit purchase/refund consumers and their
existing schema/test baseline; no changed task file failed.

Guarded PostgreSQL validation:
`TEST_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/moda_interact' MODA_DISPOSABLE_INTEGRATION=1 npm test -- --run tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
passed: 1 file, 1 test. Shared version check reported `0.11.0`; the removed
symbol scan was clean; `git diff --check` passed. The database submodule remains
an unstaged gitlink at `014408e0402221f08a3961880b34e828a8bdc736`.

### Deviations
Repository-wide build and unit validation retain only the documented,
unchanged DATABASE-013 schema-consumer baseline described above. Focused task
validation, guarded concurrency validation, package verification, and diff
checks are green.

### Assumptions
The hydrated DATABASE-013 database submodule at
`014408e0402221f08a3961880b34e828a8bdc736` and generated Prisma client are the
accepted prerequisite baseline supplied for this attempt.

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
  implementation commit: e5d6f0b (fix: complete BACKGROUND-011 attempt 4 corrections)
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  pushed: yes

Parent workspace:
  task file: docs/decisions/background/ARCH-010/BACKGROUND-011-shop-lifetime-free-fallback.md
  claim commit: 7e42c4f (chore: claim BACKGROUND-011 attempt 4)
  report commit: 150a557 (docs: return BACKGROUND-011 attempt 4 for review)
  remote branch: origin/task/ARCH-010-BACKGROUND-011
  submodule gitlink staged: no

Database gitlink staged: no
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

#### Attempt 3 — Changes Requested

##### Review Status

Changes Requested — Attempt 3.

##### Accepted Attempt-3 work

Retain the following corrections:

```text
implementation:
  db8cec1

latest submitted parent report publication:
  ba384a3

database revision:
  014408e0402221f08a3961880b34e828a8bdc736

focused tests:
  71 passed

guarded PostgreSQL concurrency regression:
  passed
```

Architect comparison of Attempt 2 -> Attempt 3 confirms:

```text
1. purchased and lifetime-Free admission now use the same canonical:
     createRecoveryIdempotencyKey(shopId, recoveryId)

2. purchased reservation replay can identify an existing lifetime-Free owner;

3. lifetime reservation replay can identify an existing purchased owner;

4. Free admission spends existing purchased credits even when recovery-pack
   purchasing is disabled/null;

5. the partial paidIncludedCapacityExhausted(...) routing was removed;

6. PAID_METERED admission remains on the pre-BACKGROUND-002 paid path;

7. activation/reconciliation tests now prove:
     first lifetime counter uses LIFETIME_FREE_RECOVERY_CREDITS;
     granted quantity comes from PlatformBillingPolicy;
     an existing lifetime counter is not regranted/reset;
     policy changes after grant do not alter the existing counter;

8. the real PostgreSQL lifetime reservation concurrency regression still passes.
```

Those changes are architecturally correct.

##### Blocking defect 1 — replay status is not authoritative

The current `RecoveryBillingService` treats any replay outcome with known counter
ownership as admitted:

```ts
reservation.kind === "reserved" || isOwnedBy(reservation, "PURCHASED_RECOVERY_CREDITS")
reservation.kind === "reserved" || isOwnedBy(reservation, "LIFETIME_FREE_RECOVERY_CREDITS")
```

`isOwnedBy(...)` is true for all of:

```text
already-reserved
already-committed
already-released
already-ambiguous
```

That is unsafe.

A `RELEASED` reservation has already returned its quantity to the original counter.
The current flow can therefore:

```text
reserve purchased/lifetime
-> release quantity after pre-provider/definitive failure
-> retry same recovery
-> reserve() returns already-released + original counter
-> RecoveryBillingService admits without incrementing reservedQuantity again
-> provider send succeeds
-> commit() sees RELEASED and performs no counter transition
```

The recovery can therefore complete without consuming capacity.

This is reachable from existing checkout execution because
`CheckoutRecoveryService` calls `releaseBeforeProvider(...)` when conversation
creation fails or provider execution is suppressed, and definitive provider failures
also release the selected reservation.

`AMBIGUOUS` is also unsafe to admit. An ambiguous provider result means the external
effect may already have happened. A replay must not automatically issue another
provider action merely because bucket ownership is known.

##### Required correction 1 — status-aware replay semantics

Keep one canonical `UsageReservation.sourceKey`, but make **status + owner** authoritative.

Required behaviour:

```text
RESERVED / already-reserved
  -> preserve original bucket
  -> reuse the existing reservation
  -> do not increment reservedQuantity again

COMMITTED / already-committed
  -> preserve original bucket
  -> idempotent replay only
  -> do not reserve or consume a second bucket

AMBIGUOUS / already-ambiguous
  -> preserve original bucket
  -> return blocked: reservation-in-flight
  -> do not call the other reservation service
  -> do not send/retry provider execution from this admission path

RELEASED / already-released
  -> preserve original bucket
  -> re-reserve against the SAME original counter before admission
  -> only return admitted if that same bucket is successfully reserved again
  -> if that original bucket no longer has capacity, block
  -> NEVER fall through to the other bucket
```

A released purchased reservation must not become lifetime-Free merely because lifetime
capacity is now available.

A released lifetime-Free reservation must not become purchased merely because purchased
capacity appeared later.

##### Scope clarification — lifetime-Free accounting only

For `LIFETIME_FREE_RECOVERY_CREDITS`, this review makes decisions only about the
quantities that determine lifetime-Free availability:

```text
grantedQuantity
committedQuantity
reservedQuantity
```

BG11 must not add business rules, validation rules or arithmetic for unrelated generic
counter fields merely because those fields exist in the shared database model.

The task's lifetime-Free invariant is exactly:

```text
grantedQuantity >= 0
committedQuantity >= 0
reservedQuantity >= 0
committedQuantity + reservedQuantity <= grantedQuantity
```

and:

```text
remaining =
    grantedQuantity
    - committedQuantity
    - reservedQuantity
```

`PurchasedRecoveryReservationService` remains authoritative for its own internal
capacity accounting. BG11 orchestrates its outcome; it does not reproduce that
accounting.

##### Required correction 2 — released-row reactivation

Implement released-row reactivation transactionally.

For a reservation whose existing `counterId` belongs to the reservation service's own
counter:

```text
1. verify reservation.shopId;
2. verify reservation.quantity equals the requested quantity;
3. verify the existing counter type is exactly the expected owner;
4. recompute available capacity for that original counter;
5. if insufficient:
     return a deterministic exhausted result tied to the original owner;
6. if sufficient:
     CAS-increment that original counter.reservedQuantity;
     increment counter.version;
     update the SAME UsageReservation row:
       RELEASED -> RESERVED;
     keep the same sourceKey and counterId;
7. return reserved with the original owner.
```

For purchased capacity, preserve the existing
`PurchasedRecoveryReservationService` capacity semantics unchanged. BG11 must not
duplicate, reinterpret or redefine that service's internal accounting fields.

For lifetime Free, reactivation capacity is calculated only from:

```text
remaining =
    counter.grantedQuantity
    - counter.committedQuantity
    - counter.reservedQuantity
```

after validating only these lifetime-Free invariants:

```text
grantedQuantity >= 0
committedQuantity >= 0
reservedQuantity >= 0
committedQuantity + reservedQuantity <= grantedQuantity
```

No other generic counter field participates in BG11's lifetime-Free capacity
calculation or validation.

Do not delete/recreate the UsageReservation row and do not change `counterId`.

If a reservation service encounters a RELEASED row owned by the *other* recovery
counter, return the owner explicitly and let `RecoveryBillingService` invoke the
correct owning service once to perform reactivation.

Do not introduce recursion or a retry loop between the two reservation services.

##### Required correction 3 — ambiguous rows are a hard replay gate

For both purchased and lifetime-Free ownership:

```text
already-ambiguous
  -> blocked / reservation-in-flight
```

Required assertions:

```text
no counter increment
no reservation status change
no fallback to the other bucket
no provider admission
```

Do not reinterpret AMBIGUOUS as RELEASED.

##### Required correction 4 — consume Shared 0.11.0

The submitted Background repository is still pinned to:

```text
@modainteract/moda-interact-shared@0.10.0
```

but this task now depends on architect-complete `ARCH-010-SHARED-008`.

Update the Background repository to the published clean first-production contract:

```text
@modainteract/moda-interact-shared@0.11.0
```

Update both:

```text
package.json
package-lock.json
```

using the repository's normal npm workflow.

Do not use a range that can silently resolve back to `0.10.x`.

After installation verify:

```bash
node -p "require('./node_modules/@modainteract/moda-interact-shared/package.json').version"
```

Expected:

```text
0.11.0
```

Also run a Background source/test scan proving there is no active import/reference to
the SHARED-007 removed contracts:

```text
SUBSCRIPTION_CANCELLATION_MODES
SubscriptionCancellationModeSchema
SubscriptionCancellationMode
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

##### Required correction 5 — Completion Report wording

The Attempt-3 report still says:

```text
Paid admission uses lifetime Free after included and purchased capacity are exhausted.
```

That is no longer implemented by this task.

Correct it to state:

```text
BACKGROUND-011 supplies the plan-independent lifetime reservation primitive.
BACKGROUND-002 owns the Paid:
included -> purchased -> lifetime-Free
composition.
```

##### Required Attempt-4 regression matrix

At minimum add/prove:

```text
1. purchased RESERVED replay stays purchased without second reservation
2. lifetime RESERVED replay stays lifetime without second reservation
3. purchased COMMITTED replay stays purchased and does not consume again
4. lifetime COMMITTED replay stays lifetime and does not consume again

5. purchased AMBIGUOUS replay:
     blocked reservation-in-flight
     no lifetime fallback
     no counter mutation

6. lifetime AMBIGUOUS replay:
     blocked reservation-in-flight
     no purchased fallback
     no counter mutation

7. purchased RELEASED replay with purchased capacity available:
     same UsageReservation row becomes RESERVED
     same counterId
     purchased reservedQuantity increments once
     no lifetime reservation

8. purchased RELEASED replay with purchased capacity unavailable and lifetime available:
     blocked
     does not switch to lifetime

9. lifetime RELEASED replay with lifetime capacity available and purchased capacity now available:
     re-reserves lifetime
     same UsageReservation row/counterId
     does not switch to purchased

10. lifetime RELEASED replay with lifetime capacity unavailable:
      blocked
      does not switch to purchased

11. canonical source-key concurrent race still cannot create two reservation rows/buckets
12. definitive failure still releases the originally selected bucket
13. ambiguous failure still marks only the originally selected bucket ambiguous
14. Free + pack purchase disabled/null + purchased available -> purchased
15. Paid direct admission remains unchanged until BACKGROUND-002
16. first verified activation creates/preserves the lifetime counter correctly

17. lifetime availability uses only:
      grantedQuantity
      committedQuantity
      reservedQuantity

18. lifetime committedQuantity + reservedQuantity > grantedQuantity
    -> fail closed
    -> no reservation mutation
    -> no fallback caused by clamping an invalid counter to zero

19. Background uses @modainteract/moda-interact-shared@0.11.0
```

Keep the real PostgreSQL concurrency regression.

##### Validation

Use DATABASE-013 revision:

```text
014408e0402221f08a3961880b34e828a8bdc736
```

or a later architect-accepted DATABASE-013 `main` revision containing the same schema.

Run at minimum:

```text
focused effective-policy tests
focused purchased reservation tests
focused lifetime reservation tests
focused RecoveryBillingService tests
focused billing-subscription-reconciliation tests
guarded PostgreSQL reservation concurrency regression
npm run build
npm run test:unit
git diff --check
Shared removed-symbol source/test scan
```

Any diagnostic or test failure in an Attempt-4 changed file is a blocker.

Repository-wide unrelated baseline failures may remain only if unchanged and precisely
documented.

##### Scope guard

Do not:

```text
implement BACKGROUND-002 included-credit reservation/composition
implement BACKGROUND-014 FIFO purchased lots
implement BACKGROUND-019 promotional reservations
change DATABASE-013
stage the database gitlink
change Shared source code
change Shopify/Admin repositories
change accepted BACKGROUND-001 queue/retry/CAS/scheduling behaviour
republish Shared
```

##### VCS / report evidence

Preserve Attempt-3 evidence:

```text
implementation:
  db8cec1

latest submitted parent report:
  ba384a3

database:
  014408e0402221f08a3961880b34e828a8bdc736
```

For Attempt 4 record:

```text
new implementation commit
new parent claim commit
new parent report/status publication
canonical parent worktree
canonical implementation worktree
all physical-isolation declarations
all start-of-attempt synchronization outcomes
Shared dependency version 0.11.0
database revision
database gitlink staged: no
main branches modified: no
```

##### Architect Decision

**Changes Requested — Attempt 3.**

Return the task to:

```text
status: ready
attempt: 3
executor: null
claimed_at: null
```

The next valid claim is **Attempt 4**.

#### Attempt 4 — Accepted

##### Review Status

Accepted — Attempt 4.

##### Architect Review Summary

Architect independently reviewed the submitted Attempt-4 implementation and the
Attempt-3 -> Attempt-4 delta.

Accepted implementation evidence:

```text
implementation commit:
  e5d6f0bb114cc0de20c7e789aff71efafc1c8010

parent claim commit:
  7e42c4f038582c9a14f585be02d461bbfb454183

parent report commit:
  150a5577f0d00584f47a9a0d1615099fbe2e78fc

database revision:
  014408e0402221f08a3961880b34e828a8bdc736

Shared dependency:
  @modainteract/moda-interact-shared@0.11.0
```

Attempt 4 satisfies the outstanding correction contract.

Verified behaviour:

```text
canonical recovery identity:
  purchased and lifetime-Free admission use one
  createRecoveryIdempotencyKey(shopId, recoveryId) source identity

RESERVED replay:
  preserves the original funding bucket
  does not create a second reservation

COMMITTED replay:
  preserves the original funding bucket
  does not consume another capacity bucket

AMBIGUOUS replay:
  blocks as reservation-in-flight
  does not fall through to another bucket
  does not mutate counter ownership

RELEASED replay:
  reactivation occurs only on the original owning counter
  reuses the same UsageReservation row
  preserves sourceKey
  preserves counterId
  CAS-increments reservedQuantity only after capacity is available
  blocks instead of switching bucket when original capacity is unavailable

cross-bucket replay:
  a released reservation discovered through the non-owning service is handed once
  to the original owning reservation service for reactivation
  no recursive/fallback bucket switching is introduced
```

Lifetime-Free accounting is correctly bounded to the task's domain:

```text
remaining =
  grantedQuantity
  - committedQuantity
  - reservedQuantity
```

and the implementation validates only the lifetime quantities that participate in
that calculation:

```text
grantedQuantity >= 0
committedQuantity >= 0
reservedQuantity >= 0
committedQuantity + reservedQuantity <= grantedQuantity
```

Invalid lifetime state fails closed rather than being hidden by `max(..., 0)`.
No unrelated generic counter field is introduced into the lifetime-Free capacity formula.

Purchased-credit accounting remains owned by `PurchasedRecoveryReservationService`;
BG11 does not duplicate its accounting model.

The Paid routing boundary is preserved:

```text
BACKGROUND-011:
  plan-independent lifetime-Free reservation primitive
  Free purchased -> lifetime-Free fallback

BACKGROUND-002:
  Paid current-period included
  -> purchased
  -> lifetime-Free
  composition
```

Attempt 4 does not reintroduce the earlier partial Paid included-credit implementation.

Shared baseline conformance is complete:

```text
package.json:
  @modainteract/moda-interact-shared = 0.11.0

package-lock.json:
  resolved 0.11.0 package artifact

retired SHARED-007 symbols in Background src/tests:
  none
```

##### Validation Reviewed

Submitted validation:

```text
focused unit tests:
  5 files
  97 passed

guarded PostgreSQL lifetime reservation concurrency:
  1 passed

Shared package:
  0.11.0

removed-symbol scan:
  passed

git diff --check:
  passed
```

Repository-wide validation remains non-zero only because of the documented unchanged
DATABASE-013 schema-consumer baseline. No Attempt-4 changed file is in the reported
build diagnostic set or failing test set.

##### VCS / Isolation Review

Verified:

```text
implementation main modified: no
workspace main modified: no
database gitlink staged: no
database revision: 014408e0402221f08a3961880b34e828a8bdc736
implementation task commit: e5d6f0b
parent Attempt-4 claim: 7e42c4f
parent review publication: 150a557
```

The submitted archive's Completion Report contained a stale textual reference to the
Attempt-3 claim commit. GitHub history confirms the actual Attempt-4 claim is `7e42c4f`;
this acceptance record corrects the documentation evidence without reopening implementation.

##### Architecture Conformance

Conformant.

BG11 now supplies exactly the clean first-production lifetime-Free primitive required by
DATABASE-013 and Shared 0.11.0 while preserving ownership boundaries for Paid included
credits, FIFO purchased lots and promotional capacity.

##### Downstream Readiness

With `ARCH-010-BACKGROUND-011` Complete:

```text
ARCH-010-BACKGROUND-002 -> Ready
ARCH-010-BACKGROUND-014 -> Ready
```

Their other dependencies are already Complete.

`ARCH-010-BACKGROUND-019` remains Pending because it still depends on both
BACKGROUND-002 and BACKGROUND-014.

##### Architect Decision

**Accepted — Attempt 4. ARCH-010-BACKGROUND-011 is Complete.**

