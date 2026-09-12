---
id: ARCH-010-BACKGROUND-019
architecture_id: ARCH-010
title: Reserve selected promotional campaign credits before every other capacity source
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 82
executor: copilot
claimed_at: '2026-09-12T23:25:08Z'
attempt: 3
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-011
- ARCH-010-BACKGROUND-014
enables:
- ARCH-010-BACKGROUND-008
- ARCH-010-BACKGROUND-009
- ARCH-010-SYSTEM-TEST-001
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-019: Reserve selected promotional campaign credits before every other capacity source

## Objective

Implement exact-grant promotional reservation/commit/release for the merchant's one currently selected promotion and make that promotion the **highest-priority recovery-capacity source**.

Canonical order:

```text
PAID
  selected promotional
  -> current BillingPeriod included
  -> purchased FIFO lot
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

FREE
  selected promotional
  -> purchased FIFO lot
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

## Inspect before editing

```text
src/services/recovery-billing.service.ts
src/services/effective-billing-policy.service.ts
src/services/*reservation*.ts
src/services/checkout-recovery.service.ts
database/prisma/schema.prisma
tests/unit/services/**billing**
tests/integration/*reservation*.test.ts
```

Read the implemented forms of BACKGROUND-002, BACKGROUND-011 and BACKGROUND-014, then use the exact campaign/grant schema from DATABASE-013. Reuse the same Serializable/CAS/idempotency architecture.

## 1. Resolve the selected campaign transactionally

Before reserving any other recovery-capacity bucket, resolve `MerchantPromotionSelection` and its exact `PromotionalCreditGrant`/`PromotionCampaign`.

A selected promotion is usable for a new reservation only if all are true in the reservation transaction:

```text
campaign.status = ACTIVE
campaign.startsAt <= now < campaign.expiresAt
grant.shopId = current shop
grant.campaignId = campaign.id
remaining grant quantity > 0
scope eligibility still holds
normal ARCH-010 shop/subscription execution gate is open
```

Scope eligibility:

```text
GLOBAL -> eligible
SHOP   -> campaign.targetShopId == shopId
PLAN   -> campaign.targetPlanId == current effective mapped BillingPlan.id
```

If the selection is expired/closed/ineligible/exhausted, treat promotional capacity as unavailable and continue to the next canonical source. Do not delete history in Background.

## 2. Exact promotional grant reservation

Use `UsageReservation.promotionalCreditGrantId` from DATABASE-013. Promotional capacity exists only on the exact selected campaign grant; there is no aggregate promotional `ShopEntitlementCounter` in the first-production schema.

Availability:

```text
remaining = quantity - committedQuantity - reservedQuantity
```

Reserve with bounded Serializable/CAS retry, deterministic recovery source identity, replay-before-allocation and exact grant versioning.

Every reserve/commit/release must update only the exact `PromotionalCreditGrant` identified by the reservation. Do not create, read or maintain `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` as compatibility accounting.

## 3. Commit/release around expiry

- reservation created while campaign is usable remains protected;
- that existing reservation may commit after campaign expiry/close/plan change because recovery was already admitted;
- definitive pre-provider failure releases exactly once;
- release after campaign is unusable does not make that quantity spendable unless the same campaign later becomes running/eligible again;
- committed reservation updates `firstUsedAt/lastUsedAt` and `exhaustedAt` when appropriate;
- duplicate commit never increments usage twice.

## 4. Promo-first routing

Refactor the one canonical recovery admission path to call promotional reservation **before** paid included capacity.

```text
if selected promotional reserve succeeds:
    fund from promotion
else if PAID:
    try current-period included
    -> purchased FIFO
    -> lifetime Free
else FREE:
    purchased FIFO
    -> lifetime Free
```

`BACKGROUND-002` remains owner of the period-included reservation primitive; it no longer owns top-level priority.

Do not leave another caller with the obsolete `paid included -> promotional` order.

## 5. Provider/App Event rule

Promotional-funded recovery:

- creates no normal paid Shopify recovery-meter App Event;
- creates no top-up purchase App Event;
- is never paid overage;
- keeps normal internal recovery/accounting evidence.

During the five-minute provider BillingPeriod DRAINING phase, a usable selected promo may still fund a new recovery because it creates no cycle-scoped App Event. If no promo is usable, Paid included remains unavailable during drain and routing proceeds to purchased/lifetime Free per BACKGROUND-008.

## 6. Lifecycle gates remain stronger

Positive/selected promotional capacity never bypasses:

```text
Shop.status != ACTIVE
Subscription = NO_CONTRACT
Subscription = FROZEN
reinstallPendingAt != null
other existing provider/configuration execution blocks
```

Preserve grant/history while blocked.

## Required tests

At minimum prove:

1. Paid selected promo + paid included available consumes promo first;
2. promo exhausted -> Paid included;
3. Free selected promo consumes promo first;
4. no usable promo -> Free purchased -> lifetime Free;
5. no usable promo -> Paid included -> purchased -> lifetime Free;
6. PLAN promo becomes unavailable after plan change without deleting grant;
7. GLOBAL/SHOP targeting is checked correctly;
8. expired/closed campaign cannot fund new reservation;
9. reservation made before expiry may commit after expiry;
10. released-after-expiry quantity is not currently spendable;
11. reopened same campaign can later make the original unused grant spendable again when reselected;
12. concurrent workers cannot overspend final promo credit;
13. duplicate reserve/commit is idempotent;
14. promo-funded recovery creates no Shopify usage App Event;
15. DRAINING may use promo before all other buckets;
16. FROZEN/NO_CONTRACT/inactive shop never consumes promo;
17. all buckets exhausted yields typed capacity-exhausted result;
18. no automatic paid overage exists.

## Non-goals

Do not implement Admin campaign management, merchant selection UI/action, promotion marketing delivery, automatic campaign selection or an expiry scheduler.

## Stop conditions

Stop if DATABASE-013 exact grant ownership is unavailable, or if implementing promo-first routing would require duplicating the accepted reservation architecture rather than composing existing primitives.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `src/services/promotional-recovery-reservation.service.ts`
- `src/services/recovery-billing.service.ts`
- `tests/unit/services/recovery-billing.service.test.ts`
- `tests/unit/services/promotional-recovery-reservation.service.test.ts`
- `tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts`

### Work Completed
- Added an exact campaign-grant promotional reservation primitive using Serializable transactions, versioned CAS updates, deterministic source keys, replay protection, and bounded conflict retries.
- Resolved the current merchant selection and grant transactionally, enforcing active time window, shop/plan/global scope, grant ownership, remaining quantity, and the effective shop/subscription execution gate.
- Routed selected promotional capacity before paid included, purchased FIFO, and lifetime Free capacity; promotional usage creates only internal usage evidence and no paid Shopify meter event.
- Routed promotional commit, release, and ambiguous-provider transitions through the exact grant service.
- Added focused coverage for promo-first paid admission, fallback to purchased capacity, and promotional lifecycle commit routing.
- Attempt 3 removed reservation-time mutation of selection-owned history fields and corrected post-transition `exhaustedAt` accounting with fail-closed negative-state checks.
- Added direct primitive coverage for scope/time/status eligibility, exact ownership, replay/lifecycle transitions, internal event semantics, timestamps, and exhaustion behavior.
- Added disposable PostgreSQL concurrency coverage proving one final-credit reservation wins without aggregate promotional entitlement accounting.
- Expanded router coverage for ordered fallback and promotional release, definitive failure, and ambiguous-provider ownership.

### Validation Results
- Attempt 3 claimed durably with `executor: copilot`, `attempt: 3`, and claim timestamp `2026-09-12T23:25:08Z`.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- Focused `vitest` primitive/router suite: passed, 55 tests.
- `npm run test:integration -- tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts`: passed, 1 test.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- Full `npm run test:unit`: 580 tests passed and 1 unrelated existing test failed because `tests/unit/runtime/observability-startup.test.ts` expects shared runtime `0.9.0` while `package.json` declares `0.11.0`.

### Deviations
- Full unit validation retains one pre-existing shared-runtime version assertion failure; no unrelated test or package metadata was changed.
- The unrelated shared-runtime version assertion remains unresolved; no unrelated test or package metadata was changed.

### Assumptions
- The initialized `database` submodule at accepted DATABASE-013 revision `014408e0402221f08a3961880b34e828a8bdc736` is the intended dependency state; its parent gitlink was intentionally not staged by this task.

### Unresolved Issues
- The architect should decide whether to reconcile the existing shared-runtime `0.9.0` test expectation separately; it is outside BACKGROUND-019.

### Git / VCS
Task branch: `task/ARCH-010-BACKGROUND-019`

Physical task isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-019`
  parent branch: `task/ARCH-010-BACKGROUND-019`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-019`
  implementation branch: `task/ARCH-010-BACKGROUND-019`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-background`
  implementation commit: `ed28c98`
  remote branch: `origin/task/ARCH-010-BACKGROUND-019`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-010/BACKGROUND-019-promotional-credit-reservations.md`
  claim commit: `d711795`
  review report commit: `c48c3ac`
  remote branch: `origin/task/ARCH-010-BACKGROUND-019`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architect Review

#### Attempt 2 — Changes Requested

##### Review Status

Changes Requested.

The top-level capacity direction is correct:

```text
PAID
  selected promotional
  -> current-period included
  -> purchased FIFO
  -> shop-lifetime Free
  -> block

FREE
  selected promotional
  -> purchased FIFO
  -> shop-lifetime Free
  -> block
```

`RecoveryBillingService` now calls the promotional reservation primitive before the previously accepted capacity sources, and promotional commit/provider-failure routing is wired to the exact-grant service.

Attempt 2 cannot be accepted because there are two production accounting/ownership defects inside `PromotionalRecoveryReservationService`, and the new exact-grant primitive has not been directly or concurrency tested.

This rework must stay inside BACKGROUND-019 ownership. Do not absorb SHOPIFY-021 merchant-selection behavior or BACKGROUND-008 billing-period DRAINING behavior.

##### Finding 1 — Do not mutate merchant selection-history fields while consuming credits

**Affected production file**

```text
src/services/promotional-recovery-reservation.service.ts
```

Current `reserveGrant(...)` mutates:

```text
firstSelectedAt
lastSelectedAt
selectionCount
```

on every credit reservation/reactivation.

That is architecturally incorrect.

These fields describe a merchant **selection action**, not a recovery-credit consumption action. Their writer is the merchant selection transaction owned by:

```text
ARCH-010-SHOPIFY-021
```

SHOPIFY-021 explicitly owns:

```text
update first/last selection timestamps/count exactly once per successful selection action
```

BACKGROUND-019 must therefore never mutate those three fields.

Change promotional credit reservation so a successful reserve changes only the accounting state owned by this task:

```text
PromotionalCreditGrant.reservedQuantity += quantity
PromotionalCreditGrant.version += 1
```

and creates/reactivates the exact `UsageReservation`.

Do not modify:

```text
firstSelectedAt
lastSelectedAt
selectionCount
```

during:

```text
reserve
reserve replay/reactivation
commit
release
markAmbiguous
```

Add direct tests proving all three fields remain unchanged while promotional credits are reserved/committed/released.

Do not move SHOPIFY-021 selection behavior into Background.

##### Finding 2 — Correct `exhaustedAt` calculation

**Affected production file**

```text
src/services/promotional-recovery-reservation.service.ts
```

Attempt 2 currently calculates:

```ts
const remainingAfterCommit =
  grant.quantity - grant.committedQuantity - grant.reservedQuantity;

exhaustedAt:
  remainingAfterCommit <= quantity ? now : grant.exhaustedAt
```

This can mark a grant exhausted while spendable capacity still remains.

Concrete example:

```text
quantity = 5
committedQuantity = 3
reservedQuantity = 1
commit quantity = 1
```

Before and after that commit:

```text
remaining = 5 - 3 - 1 = 1
```

One credit remains available, so `exhaustedAt` must not be set.

For commit, calculate the post-transition accounting explicitly:

```text
committedAfter = grant.committedQuantity + quantity
reservedAfter  = grant.reservedQuantity - quantity
remainingAfter = grant.quantity - committedAfter - reservedAfter
```

Required invariant:

```text
remainingAfter > 0  -> do not newly set exhaustedAt
remainingAfter == 0 -> set exhaustedAt to now when it is currently null
```

Preserve an already non-null historical `exhaustedAt`; do not rewrite its timestamp on duplicate/replayed commit.

Database constraints guarantee accounting cannot legitimately go negative. If the computed post-transition state is negative, fail closed rather than recording exhaustion.

Add direct tests for at least:

```text
a commit that leaves 1 remaining -> exhaustedAt remains null
a commit that leaves 0 remaining -> exhaustedAt is set
duplicate commit -> exhaustedAt timestamp/counters do not change again
```

##### Finding 3 — Add direct unit coverage for the exact promotional reservation primitive

Attempt 2 added no:

```text
tests/unit/services/promotional-recovery-reservation.service.test.ts
```

The 36 passing tests are almost entirely `RecoveryBillingService` tests with the promotional service mocked. They do not prove the new transaction/CAS/accounting implementation.

Create:

```text
tests/unit/services/promotional-recovery-reservation.service.test.ts
```

Use the existing direct reservation-service test style in:

```text
tests/unit/services/paid-included-recovery-reservation.service.test.ts
tests/unit/services/purchased-recovery-reservation.service.test.ts
tests/unit/services/free-recovery-reservation.service.test.ts
```

A small constructor seam equivalent to those accepted services is authorized if needed for deterministic testing:

```text
database
maxRetries
clock / now provider
policy-resolver factory
```

Do not change the external singleton/API contract merely to make tests easy.

Directly prove at minimum:

```text
1. GLOBAL campaign in ACTIVE window reserves the selected exact grant;
2. SHOP campaign reserves only for the matching shop;
3. PLAN campaign reserves only for the current effective BillingPlan.id;
4. wrong PLAN target returns unavailable without grant mutation;
5. campaign before startsAt returns unavailable;
6. campaign at/after expiresAt returns unavailable;
7. CLOSED campaign returns unavailable;
8. exhausted grant returns unavailable;
9. reservation writes promotionalCreditGrantId and no entitlement counter source;
10. duplicate reserve does not increment reserved quantity twice;
11. same-source released reservation can reactivate only when the same selected grant is usable again;
12. released reservation cannot reactivate while campaign is expired/CLOSED/plan-ineligible;
13. commit may succeed after campaign expiry/close because admission already occurred;
14. release decrements only the exact grant reservation once;
15. ambiguous keeps exact promotional capacity reserved;
16. duplicate commit creates no second UsageEvent and does not double-increment committed quantity;
17. committed UsageEvent uses RECOVERY_CONVERSATION and ShopifyReportState.NOT_APPLICABLE;
18. reserve/commit/release do not mutate firstSelectedAt/lastSelectedAt/selectionCount;
19. firstUsedAt/lastUsedAt update only on commit;
20. exhaustedAt behavior follows Finding 2;
21. shop mismatch fails closed;
22. reservation owned by a non-promotional source is not silently converted to promotional;
23. retryable CAS/P2034/P2002 conflicts are bounded and replay-safe.
```

The test may contain more than 23 individual assertions/cases; these are behavior obligations, not required test names.

##### Finding 4 — Add the required real PostgreSQL final-credit race

The Completion Report says database-backed concurrency validation was unavailable.

That is incorrect for this repository.

`package.json` declares:

```text
test:integration = node scripts/test-integration.mjs
```

and the repository already contains disposable PostgreSQL reservation tests:

```text
tests/integration/free-recovery-reservation.concurrency.integration.test.ts
tests/integration/paid-included-recovery-reservation.concurrency.integration.test.ts
tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts
```

Create:

```text
tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts
```

Use the same disposable infrastructure/pattern.

Required database race:

```text
one executable shop
one selected ACTIVE eligible campaign
one PromotionalCreditGrant with quantity=1
committedQuantity=0
reservedQuantity=0
two independent concurrent workers
two different recovery source keys
```

Race two real:

```text
PromotionalRecoveryReservationService.reserve(...)
```

calls.

After both settle, assert:

```text
exactly one call owns/reserves the final promotional credit
the other returns unavailable or the repository's defined exhausted-equivalent
grant.reservedQuantity == 1
grant.committedQuantity == 0
grant.reservedQuantity + grant.committedQuantity <= grant.quantity
exactly one promotional UsageReservation exists for the two competing source keys
no aggregate promotional ShopEntitlementCounter was created/mutated
```

Also add a same-source concurrent replay case if practical:

```text
two concurrent reserve calls for the same sourceKey
-> one durable reservation
-> reservedQuantity increments exactly once
```

Run the focused integration test with:

```bash
npm run test:integration -- \
  tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts
```

If disposable PostgreSQL infrastructure itself fails, return the exact infrastructure error. Do not claim the repository has no integration path.

##### Finding 5 — Expand promo routing/lifecycle coverage

The new routing coverage currently proves only a small subset of the task matrix.

Strengthen:

```text
tests/unit/services/recovery-billing.service.test.ts
```

to directly prove:

```text
1. Paid promo available -> promo before included;
2. Paid promo unavailable/exhausted -> included;
3. Paid promo unavailable + included exhausted -> purchased FIFO owner;
4. Paid promo + included + purchased unavailable -> lifetime Free;
5. Free promo available -> promo before purchased;
6. Free promo unavailable -> purchased before lifetime Free;
7. all applicable buckets unavailable -> typed allowance-exhausted/block result;
8. promotional already-ambiguous does not switch the same recovery to another capacity source;
9. promotional already-released does not silently switch the same recovery to another capacity source;
10. promotional commit never invokes paid-included/purchased/lifetime commit;
11. definitive provider failure releases promotional reservation exactly once;
12. ambiguous provider result marks promotional reservation ambiguous and retains ownership;
13. releaseBeforeProvider releases promotional reservation through the promotional service;
14. promo-funded admission does not invoke the normal paid included meter path.
```

Do not implement paid overage.

##### Finding 6 — Preserve current lifecycle gates without absorbing later tasks

BACKGROUND-019 must not become the owner of lifecycle mechanisms assigned to later tasks.

For this attempt:

```text
FROZEN
NO_CONTRACT
inactive/uninstalled shop
existing pause/configuration gates
```

must continue to fail before promotional capacity can be consumed. Add focused coverage where feasible.

However:

```text
ARCH-010-BACKGROUND-008
```

owns the explicit `ACTIVE / DRAINING / EXPIRED_RECONCILING` paid-period phases and pre-provider boundary revalidation.

Therefore **do not implement the five-minute DRAINING phase in BACKGROUND-019** merely to satisfy the original task's test-15 wording. BACKGROUND-008 depends on BACKGROUND-019 and must later prove:

```text
DRAINING:
promotional -> purchased FIFO -> lifetime Free
```

Likewise:

```text
ARCH-010-BACKGROUND-006
```

owns the durable `reinstallPendingAt` reconciliation/execution gate. Do not duplicate that future mechanism here.

BACKGROUND-019's responsibility is to leave one reusable exact promotional reservation primitive and one promo-first normal admission order for those later tasks to compose.

##### Finding 7 — Preserve exact campaign/grant ownership

Keep these Attempt 2 behaviors:

```text
campaign status/time evaluated transactionally for new reservation
grant.shopId == current shop
grant.campaignId == selected campaign
PLAN targeting uses current effective mapped BillingPlan.id
SHOP/GLOBAL targeting enforced
commit/release use reservation.promotionalCreditGrantId
commit does not re-check current campaign eligibility
no PROMOTIONAL_RECOVERY_CREDITS ShopEntitlementCounter
no normal Shopify recovery meter App Event for promo-funded usage
Serializable transaction + version CAS + bounded retries
```

Do not replace the exact selected grant with aggregate promotional accounting.

##### Finding 8 — Validation

The initialized `database` submodule at the recorded gitlink may remain.

Run:

```bash
npm run prisma:validate
npm run prisma:generate

./node_modules/.bin/vitest run \
  tests/unit/services/promotional-recovery-reservation.service.test.ts \
  tests/unit/services/recovery-billing.service.test.ts

npm run test:integration -- \
  tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts

./node_modules/.bin/tsc --noEmit
npm run build
npm run test:unit
git diff --check
```

The known unrelated observability runtime-version assertion:

```text
tests/unit/runtime/observability-startup.test.ts
0.9.0 expected vs package 0.11.0
```

may remain documented if unchanged.

Do not change Shared package metadata or that unrelated assertion in this task.

##### Finding 9 — Completion Report / final VCS evidence

Attempt 2 contains acceptable physical-worktree and start-of-attempt synchronization evidence.

Attempt 3 must record its own four synchronization outcomes.

The user handoff identifies the Attempt 2 final parent report HEAD as:

```text
89e2e9c
```

while the embedded Completion Report names:

```text
a01c489
```

For Attempt 3, record the **actual final parent task-branch HEAD after all report metadata is committed**. Do not leave a stale report-commit value.

Database gitlink must remain unchanged and unstaged.

##### Allowed Attempt 3 scope

Production:

```text
src/services/promotional-recovery-reservation.service.ts
```

only for Findings 1–2 and a minimal deterministic-test constructor seam if required.

Routing production source:

```text
src/services/recovery-billing.service.ts
```

should remain unchanged unless a strengthened routing test exposes a genuine BACKGROUND-019 defect.

Tests:

```text
tests/unit/services/promotional-recovery-reservation.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/integration/promotional-recovery-reservation.concurrency.integration.test.ts
```

Coordination:

```text
docs/decisions/background/ARCH-010/BACKGROUND-019-promotional-credit-reservations.md
```

Do not modify:

```text
database schema/migrations/gitlink
SHOPIFY-021 merchant selection implementation
BACKGROUND-008 DRAINING implementation
BACKGROUND-006 reinstall reconciliation
Admin campaign management
Shared contracts/package version
```

##### Stop conditions

Stop and return to `moda_architect` if:

```text
1. fixing selection-history ownership would require changing SHOPIFY-021's persistence contract;
2. the exact PromotionalCreditGrant cannot be raced using the repository's existing disposable PostgreSQL infrastructure;
3. a direct/integration test exposes a DATABASE-013 constraint that prevents the exact-grant model described by this task;
4. a correction would require implementing BACKGROUND-008 or BACKGROUND-006 prematurely.
```

##### Architect Decision

**Changes Requested — Attempt 2.**

Return the same task to:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next authorized:

```text
/moda-task ARCH-010-BACKGROUND-019
```

claim becomes Attempt 3.

`ARCH-010-BACKGROUND-008`, `ARCH-010-BACKGROUND-009`, and the dependent ARCH-010 system-test tasks remain gated until BACKGROUND-019 is architect-accepted Complete.
