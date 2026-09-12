---
id: ARCH-010-BACKGROUND-001
architecture_id: ARCH-010
title: Reconcile pending subscription activation with durable BullMQ recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-010-DATABASE-006
  - ARCH-010-DATABASE-001
  - ARCH-010-DATABASE-004
  - ARCH-010-SHARED-002
  - ARCH-007-BACKGROUND-008
enables:
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-007
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-001: Reconcile pending subscription activation with durable BullMQ recovery

## Objective

Add a dedicated BullMQ consumer to the existing `moda-billing-worker` so an unresolved initial Shopify plan selection can be verified asynchronously and its delayed work reconstructed from PostgreSQL after Redis loss/restart.

## Inspect before editing

```text
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/runtime/billing-scheduler.ts
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/runtime/worker-process.ts
src/runtime/readiness.ts
src/runtime/redis.ts or actual existing Redis helper(s), if present
src/observability/worker-metrics.ts
src/observability/queue-performance.ts
package.json
```

Inspect existing BullMQ workers/services before creating queue/connection helpers. Reuse the architecture-approved Redis/BullMQ and observability conventions; do not invent a competing runtime framework.

## Current baseline to correct, not duplicate

The existing billing worker:

- starts `billingReconciliationService.reconcileOnce()`;
- then executes rotating reconciliation approximately every 60 seconds;
- currently has no BullMQ workers in its returned `workers` array;
- `applySubscription(..., null)` clears all pending plan fields;
- Partner API exceptions currently flow through `markSyncError()` which sets projection `status = SYNC_ERROR`.

For ARCH-010 initial activation this is insufficient. Do not create a second billing deployable process; extend the existing billing worker.

## Queue contract

Import only the accepted published contract from:

```text
@modainteract/moda-interact-shared/billing
```

Use its queue name, job name, schema/parser and deterministic ID helper. Do not duplicate payload validation locally.

## Consumer algorithm

For each `reconcile-subscription` job:

1. parse payload with Shared runtime schema;
2. load `Shop`, `ShopSettings`, `Subscription`, current plan and pending plan;
3. no-op success if any stale guard is true:
   - Shop missing or `Shop.status != ACTIVE`;
   - Subscription missing;
   - `pendingPlanId == null` or `pendingShopifyPlanHandle == null`;
   - `nextReconcileAt == null`;
   - DB `nextReconcileAt.toISOString() != payload.expectedNextReconcileAt`;
4. call existing Partner provider `getActiveSubscription(shop.shopifyShopId)`;
5. never infer activation from the queued pending plan alone.

### Successful current Free verification

When Shopify returns a current subscription whose plan handle equals `pendingShopifyPlanHandle`, and that handle maps to the same active local `pendingPlanId` with `BillingPlan.kind = FREE`:

transactionally:

```text
Subscription.planId                  = verified Free plan id
Subscription.observedShopifyPlanHandle = provider current handle
Subscription.status                  = ACTIVE/TRIALING per provider
Subscription provider/cycle fields   = provider truth
Subscription.pendingShopifyPlanHandle = null
Subscription.pendingPlanId           = null
Subscription.pendingEffectiveAt      = null
Subscription.nextReconcileAt         = null
Subscription.lastSyncedAt            = now
Subscription.lastSyncErrorCode/At    = null
ShopSettings.onboardingCompleted     = true
```

Ensure the one-time shop-lifetime `FREE_RECOVERY_LIFETIME` counter exists as part of first verified activation. If absent, create it with `grantedQuantity = PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`; if present, preserve every quantity exactly. Preserve purchased credits and promotional balances. Do not tie the grant to Free plan entry or regrant it on replay.

If provider truth contains an exact `currentBillingCycle`, create/reuse the exact Free BillingPeriod in the same transaction using DATABASE-004 rules:

```text
planKindSnapshot = FREE
includedRecoveryCreditsGranted = null
no INCLUDED_RECOVERY_CREDITS period counter
```

Persist the Subscription current-period pointer and timestamps. If the mapped Free plan enables recovery-credit-pack purchases, set `nextReconcileAt = max(now, periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)` and enqueue the deterministic future reconciliation after commit instead of clearing scheduling permanently.

If the current Free plan is verified but the exact provider cycle is absent, onboarding/lifetime Free entitlement may still complete; however pack purchase remains ineligible. For a pack-enabled Free plan, schedule a bounded retry for cycle discovery. Do not manufacture a BillingPeriod from local dates.

### Shopify successfully returns null

If current durable state is `NO_CONTRACT + pendingPlanId` and Shopify successfully returns no current subscription:

- keep status `NO_CONTRACT`;
- keep pending target;
- do not set onboarding complete;
- clear sync-error metadata because the provider request itself succeeded;
- compute the next retry from `pendingEffectiveAt` using the architecture retry tiers;
- if still inside the 24-hour window, atomically update `nextReconcileAt`, then best-effort add the next deterministic delayed job;
- at/after 24 hours, clear `pendingShopifyPlanHandle`, `pendingPlanId`, `pendingEffectiveAt`, `nextReconcileAt`, remain `NO_CONTRACT`, and enqueue nothing.

### Partner API transport/error failure

Do NOT set `Subscription.status = SYNC_ERROR` solely for a Partner transport/throttle/5xx/timeout failure.

Preserve existing projection state and entitlement fields. Update only:

```text
lastSyncErrorCode = PARTNER_API_ERROR (or existing canonical equivalent)
lastSyncErrorAt   = now
nextReconcileAt   = computed retry time
```

Then best-effort enqueue the next job. At 24-hour initial activation expiry, stop/clear only the pending activation target/schedule; never destroy a previously verified current subscription.

### Provider returns another current plan

Apply provider current truth using the existing reconciliation projection rules. Do not falsely activate the requested Free target. If Shopify no longer reports that pending target, clear the stale local pending initial-activation target. Do not implement Paid onboarding completion or upgrade/downgrade behaviour in this task.

## Make existing rotating reconciliation compatible

Refactor narrowly so the 60-second ARCH-007 reconciliation path cannot erase a valid initial activation pending target while Shopify still returns null and the retry window remains live.

Also change the generic Partner transport-error path so last-known ACTIVE/TRIALING entitlement is preserved instead of being replaced by `SYNC_ERROR`. Keep `SYNC_ERROR` for verified projection incompatibilities already represented by the service (for example required usage meter mismatch).

Do not remove usage publication, purchased-pack reconciliation or usage discrepancy reconciliation.

## Queue reconstruction

Implement a focused function/service that queries only:

```text
Shop.status = ACTIVE
Subscription.pendingPlanId != null
Subscription.nextReconcileAt != null
```

For each result, add the deterministic job with:

```text
delay = max(0, nextReconcileAt.getTime() - Date.now())
```

Run reconstruction:

1. once during billing-worker startup after DB/Redis resources are available;
2. periodically while the process is alive. Reuse the existing billing scheduler cadence if practical instead of introducing another unbounded timer.

The reconstruction operation MUST NOT call Shopify for every future item; it restores BullMQ jobs. Overdue jobs are added with zero delay and the consumer performs Shopify verification.

Queue-add failure must be logged/observed but must not roll back PostgreSQL billing state. A later repair pass must be capable of reconstructing it.

## Redis/BullMQ lifecycle

Add Queue/Worker resources to `billing-resources.ts` or the repository's existing equivalent and close them cleanly with the billing process. Use the canonical Shared queue name. Do not create a Redis client per job.

The deployed REDIS_URL wiring is owned by `ARCH-010-GATEWAY-001`; if REDIS_URL is unavailable in the execution environment during implementation tests, use dependency injection/test Redis patterns rather than modifying gateway files.

## Required tests

At minimum prove:

1. valid due pending Free activation is verified and completes onboarding;
2. null provider response keeps NO_CONTRACT/pending during retry window;
3. null response schedules the correct tiered nextReconcileAt;
4. 24-hour expiry clears pending activation and leaves onboarding false;
5. provider transport failure preserves ACTIVE/TRIALING current status;
6. provider transport failure preserves NO_CONTRACT pending intent;
7. transport failure records error metadata and schedules retry;
8. stale job with changed nextReconcileAt is no-op;
9. stale job after pending target cleared is no-op;
10. uninstalled shop job is no-op;
11. current verified Free transition clears initial pending target and sets onboarding complete;
12. exact provider Free cycle creates/reuses one Free BillingPeriod and schedules the next pre-close reconciliation when pack billing is enabled;
13. Free period creation creates no included-credit counter; first verified merchant activation creates the lifetime Free counter exactly once, while later period creation/replay does not modify it;
14. verified Free with missing exact cycle remains top-up-ineligible and schedules bounded cycle reconciliation when pack billing is enabled;
15. startup reconstruction enqueues future job with correct delay;
16. startup reconstruction enqueues overdue job immediately;
17. reconstruction ignores NO_CONTRACT rows with no pending plan;
18. reconstruction ignores rows with null nextReconcileAt;
19. deterministic duplicates do not create semantically duplicate work;
20. queue-add failure does not roll back durable DB state;
21. periodic repair can recreate a missing delayed job after startup;
22. existing usage publication/reconciliation tests remain passing.

## Validation

Inspect `package.json`; run focused tests first, then declared test/build/typecheck/Prisma validation required by repository/task conventions plus `git diff --check`.

## Non-goals

Do not implement Paid first activation, billing-period rollover, upgrade/downgrade execution, cancellation, top-up refund changes, promotional-credit rules, Admin UI, or Render wiring.

## Stop conditions

STOP if accepted Shared contract is unavailable, Prisma client lacks `nextReconcileAt`, implementing BullMQ requires a new deployable service rather than extending the billing worker, or existing provider semantics cannot distinguish transport failure from successful null without cross-repository redesign.

## Completion Report

### Status
Attempt 4 complete; returned to review.

### Implementation
Changed files:
- `src/services/billing-subscription-reconciliation.service.ts`
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`

Implemented Corrections 1-6 and the Attempt-4 acceptance matrix: exact initial-source and post-Partner CAS guards; established-plan rejection before Partner; executable five-minute Free cycle discovery with exact-cycle snapshots and pre-close scheduling; transport-failure state preservation; race-safe lifetime-counter upsert with replay policy independence; provider pending-truth projection; `removeOnFail: true`; periodic PostgreSQL-driven reconstruction; and production proof that the Worker and repair cadence use one queue-aware service with queue telemetry and readiness wiring.

### Validation Results
- Focused reconciliation/runtime tests: passed, 4 files and 48 tests.
- Full `npm test`: 575 passed, 7 skipped, 6 unchanged baseline failures: five integration failures are blocked because database `moda_interact_test` does not exist, and one unit failure is the unchanged `tests/unit/runtime/observability-startup.test.ts` expectation of shared package version `0.9.0` while the accepted dependency is `0.10.0`.
- `npm run prisma:validate`: passed.
- `npm run build`: blocked only by 8 unchanged nullable `counterId` errors in `src/services/free-recovery-reservation.service.ts` and `src/services/purchased-recovery-reservation.service.ts`; no errors in task-touched files.
- `git diff --check`: passed.

### Git / VCS
- Canonical parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-001`, `task/ARCH-010-BACKGROUND-001`.
- Canonical implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-001`, `task/ARCH-010-BACKGROUND-001`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.
- Parent remote task branch fast-forwarded: not-needed; parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed; implementation `origin/main` incorporated: already-current.
- Implementation commit: `f877f81473ccd5bb9d073446b9307b995ee8fecf`.
- Parent report commit: `649150cf8ce292275771258c0e7c95566b212437`.
- Parent claim commit: `cc4de24`; prior review/report commit: `bc7c9bd`.
- Database submodule revision: `6d5fb9adf2e5c1fb28333b330dd183c9cda41550`.
- Submodule gitlink staged: no.
- Merged to implementation main: no; merged to workspace main: no.

### Architectural Concerns
The full repository build and test suite retain only the documented unrelated database, observability-version, and nullable-`counterId` baseline failures. The database gitlink remains at the accepted revision.

### Unresolved Issues
No bounded-task implementation issues remain.


### Architect Review

#### Review Status

Changes Requested

#### Attempt 2 — Changes Requested

The dependency correction is accepted: the implementation now uses database revision
`6d5fb9adf2e5c1fb28333b330dd183c9cda41550`, which contains
`Subscription.nextReconcileAt`. The Shared dependency is also on the accepted
`@modainteract/moda-interact-shared@0.10.0` contract, and the reported nullable
`counterId` build diagnostics / observability-version unit failure are outside the
changed reconciliation implementation and are not the reason for this decision.

Attempt 2 cannot be accepted because the runtime wiring and several required
reconciliation invariants are still incomplete.

##### Correction 1 — use one queue-aware reconciliation service in the production worker

`billing.ts` constructs a queue-aware:

```ts
new BillingSubscriptionReconciliationService(..., billingSubscriptionQueue)
```

but that instance is used only for `reconstruct()`.

`billing-subscription-reconciliation.worker.ts` instead imports the module-level:

```ts
billingSubscriptionReconciliationService
```

whose default constructor has no Queue.

Therefore, in the actual production consumer:

```text
provider null
provider transport failure
verified Free pack-period follow-up
```

may update PostgreSQL `nextReconcileAt`, but `publishNext()` calls `enqueue()` on a
service with no Queue and silently returns. The BullMQ retry/pre-close job is not
published.

Wire the Worker and reconstruction path to the same queue-aware service (or inject the
Queue through one unambiguous runtime-owned factory). Do not keep a queue-less
production consumer singleton.

Add a runtime/wiring regression proving a processed job can publish its deterministic
next job through the production service instance.

##### Correction 2 — run queue reconstruction periodically, not only at startup

The task and parent architecture require PostgreSQL-driven queue repair:

```text
once at startup
and periodically while the billing worker is alive
```

Current `billing.ts` does:

```text
await runBillingCycle()
await subscriptionReconciliation.reconstruct()
startBillingReconciliationScheduler(runBillingCycle, ...)
```

but `runBillingCycle()` does not call `reconstruct()`.

A Redis flush/replacement after startup therefore remains unrepaired until process
restart. This directly fails Required Test 21.

Include bounded reconstruction in the existing billing scheduler cadence (or an
equally bounded existing scheduler path). Queue-add failure must remain isolated from
the rest of billing reconciliation.

Add tests for:

- startup reconstruction;
- periodic repair after a missing delayed job;
- future delay calculation;
- overdue zero-delay reconstruction;
- deterministic duplicate repair.

##### Correction 3 — prevent the generic rotating reconciliation path from stealing an initial activation

The generic `BillingReconciliationService.applySubscription(...)` now preserves local
pending fields when Shopify returns `null`, which is correct.

However, if Shopify begins reporting the selected Free plan as current before the
dedicated delayed job executes, the generic 60-second reconciliation path writes
provider `pendingPlanHandle` (normally `null`) into the local projection. That can
clear:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
```

while leaving `nextReconcileAt` behind and without setting onboarding complete or
creating the lifetime entitlement.

The dedicated consumer then sees no pending target and no-ops. This can strand an
otherwise verified merchant with `onboardingCompleted=false`.

The startup order makes this especially important because the generic billing cycle
runs before reconstruction.

Preserve an unresolved **initial activation** intent until the dedicated activation
transition completes, or refactor the current-plan verification so the generic path
cannot partially consume that transition.

Do not implement later upgrade/downgrade execution here.

Add a regression proving:

```text
NO_CONTRACT + onboarding false + pending Free target
provider now reports that Free target as current
generic reconciliation runs before the delayed worker
=> pending activation remains recoverable and the dedicated path can complete onboarding
```

##### Correction 4 — enforce initial-activation source/state and revalidate staleness after the Partner call

This task owns unresolved first activation, not future plan changes.

The consumer currently loads `ShopSettings.onboardingCompleted` but does not use it to
guard the transition. A later `ACTIVE/TRIALING + pendingPlanId` future plan-change row
could therefore enter the initial-Free completion path.

For initial activation, require the durable source to remain consistent with the
Iteration-2 contract, including onboarding not already completed and no established
different current plan.

Also revalidate the pending target / `nextReconcileAt` immediately before each durable
outcome after the Partner network call. The current pre-call stale check is not enough:

```text
job A passes stale guard
merchant/callback writes newer pending selection B
Partner response for A returns
job A updates/clears the now-newer state
```

The completion, null-provider and transport-failure paths must not overwrite a newer
selection or schedule. Use a transactional re-read or compare-and-set equivalent.

Add race regressions for a changed `nextReconcileAt` / pending target while the Partner
request is in flight.

##### Correction 5 — apply authoritative provider truth when Shopify reports another current plan

The task explicitly requires:

```text
Provider returns another current plan
-> apply provider current truth using the existing reconciliation projection rules
-> do not falsely activate the requested Free target
```

The current dedicated service only updates:

```text
observedShopifyPlanHandle
sync metadata
pending fields
nextReconcileAt
```

and leaves the existing `planId`, projection `status`, provider/cycle fields and
current-period pointer untouched.

That can leave a `NO_CONTRACT` projection while simultaneously recording an observed
current provider plan.

Reuse/refactor the existing projection logic so another verified current plan is
projected consistently, while keeping Paid first activation and future plan-change
execution outside this task.

Add a focused test for this branch.

##### Correction 6 — make verified Free entitlement/period creation match the canonical ARCH-010 database rules

Two issues remain in `completeVerifiedFree(...)`.

First, the lifetime counter currently uses:

```ts
policy?.lifetimeFreeRecoveryAllowance ?? 5
```

The one-time grant must snapshot the durable
`PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`. A missing policy row must not
silently fabricate `5`. Fail closed for first creation; if the lifetime counter
already exists, preserve every quantity without requiring the current policy merely to
replay it.

Second, a newly created Free `BillingPeriod` does not populate the complete
DATABASE-004 plan snapshot. A new Free period must record, when exact provider/current
plan identity is known:

```text
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = FREE
includedRecoveryCreditsGranted = null
```

and must create no `INCLUDED_RECOVERY_CREDITS` period counter.

Reuse an existing exact period without resetting historical entitlement/usage state.

Add direct regressions for:

- first lifetime grant from platform policy;
- missing-policy fail-closed behaviour;
- existing lifetime counter quantity preservation;
- exact Free period full plan snapshot;
- no included-credit period counter;
- replay of the exact period without resetting state;
- pack-enabled verified Free with no exact cycle retaining bounded cycle discovery.

##### Correction 7 — make Redis an actual billing-worker readiness dependency and finish queue observability wiring

`moda-billing-worker` now creates BullMQ Queue/Worker resources and cannot run this
architecture without Redis, but:

```ts
WORKER_DEPENDENCIES["moda-billing-worker"]
```

still declares only PostgreSQL.

Update the existing readiness contract so billing-worker readiness requires Redis as
well as PostgreSQL. `ARCH-010-GATEWAY-001` owns Render environment wiring; this task
owns the worker runtime dependency declaration.

The implementation also extends queue/worker metric vocabularies for
`billing-subscription-reconcile` but does not start the repository's existing
`startQueuePerformanceTelemetry(...)` convention for the billing worker. Wire the new
queue into the existing queue-performance lifecycle and close it with the process.
Do not create a competing telemetry mechanism.

##### Correction 8 — satisfy the canonical Required Tests, not only aggregate counts

The task explicitly says "At minimum prove" 22 behaviours. The current dedicated
reconciliation test file contains only eight tests, and several required behaviours
are not exercised.

Attempt 3 must add focused coverage for every item in the task's `Required tests`
section, including at minimum:

- stale job after pending target is cleared;
- inactive/uninstalled shop no-op;
- NO_CONTRACT transport failure preserving pending intent;
- Free exact-period reuse and lifetime-counter one-time semantics;
- missing-cycle bounded retry for pack-enabled Free;
- future and overdue reconstruction delays;
- rows excluded from reconstruction when pending/next schedule is absent;
- deterministic duplicate work;
- periodic repair after startup;
- provider returns another current plan;
- post-Partner-call stale/race protection;
- production queue-aware worker wiring.

The existing usage publication/reconciliation suite must continue to pass.

##### Workflow / scope

This remains the same task and same mirrored branches.

Do not create a new task for these corrections and do not implement:

- Paid first activation;
- billing-period rollover;
- upgrade/downgrade execution;
- cancellation;
- promotional-credit rules;
- Admin UI;
- Render environment wiring.

Keep the accepted database submodule revision required for this task and do not modify
historical database migrations.

Reclaim through `/moda-task`. The next valid claim is:

```text
attempt: 3
```

Run the task-declared focused/full test, build/typecheck/Prisma validation that the
repository actually provides, plus `git diff --check`. Unchanged repository baseline
failures may be documented by their existing baseline status, but changed
reconciliation/runtime files must be clean.

**Architect decision: Changes Requested — Attempt 2.**

#### Attempt 3 — Changes Requested

Attempt 3 correctly implements a substantial part of the Attempt-2 review contract:

- `billing.ts` creates one queue-aware `BillingSubscriptionReconciliationService` and
  passes that same instance to `createBillingSubscriptionReconciliationWorker(...)`;
- reconstruction is invoked during startup and from the recurring billing cadence;
- `moda-billing-worker` readiness now requires both Redis and PostgreSQL;
- queue-performance telemetry is started and included in shutdown resources;
- the rotating ARCH-007 reconciliation path no longer consumes a matching unresolved
  initial Free activation when Shopify first reports that selected Free plan as current;
- the dedicated consumer now re-reads durable state before the verified-Free and
  other-current-plan write transactions;
- provider current-plan projection is materially more complete;
- first Free activation fails closed when the platform policy is absent;
- exact Free BillingPeriod creation now records the canonical Free snapshot and does
  not create an included-credit period counter;
- the frozen-state reconstruction selector required by the task addendum is present;
- the accepted database gitlink remains at
  `6d5fb9adf2e5c1fb28333b330dd183c9cda41550`.

The reported repository-wide nullable-`counterId` build failures and unavailable
integration test database remain outside the changed task files and are not the reason
for this decision.

Attempt 3 cannot be accepted because several correctness requirements are still not
implemented, and some of the new tests assert mocks rather than the required runtime
state transitions.

##### Correction 1 — make the post-Partner initial-activation CAS exact

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

`recordMissingSubscription(...)` and `recordProviderFailure(...)` currently call
`casPendingUpdate(...)`, but that update predicate only requires:

```text
id
pendingEffectiveAt
status = NO_CONTRACT
planId = null
pendingPlanId != null
pendingShopifyPlanHandle != null
```

It does **not** compare the exact target or the exact schedule that was verified before
the Partner network call.

Therefore this race is still possible:

```text
job A loads:
  pendingPlanId = plan-A
  pendingShopifyPlanHandle = free-A
  pendingEffectiveAt = T
  nextReconcileAt = R1

job A calls Partner

newer callback/job B writes:
  pendingPlanId = plan-B
  pendingShopifyPlanHandle = free-B
  pendingEffectiveAt = T        # equality is possible and must not be relied on
  nextReconcileAt = R2

job A receives null/error
job A updateMany matches "pending fields are non-null"
=> A overwrites B's nextReconcileAt/error/expiry state
```

For the initial-activation branch, capture one immutable expected state before the
Partner call:

```text
subscriptionId
expectedPendingPlanId
expectedPendingShopifyPlanHandle
expectedPendingEffectiveAt
expectedNextReconcileAt
```

Every post-Partner `updateMany` for null/error/expiry MUST compare all of these exact
values plus:

```text
status = NO_CONTRACT
planId = null
```

Required predicate shape:

```text
id = subscriptionId
status = NO_CONTRACT
planId = null
pendingPlanId = expectedPendingPlanId
pendingShopifyPlanHandle = expectedPendingShopifyPlanHandle
pendingEffectiveAt = expectedPendingEffectiveAt
nextReconcileAt = Date(expectedNextReconcileAt)
```

Do not use `{ not: null }` for the target fields in this CAS.

If `updateMany.count === 0`:

```text
do not mutate
do not enqueue a replacement job
return success/no-op
```

Also classify the initial-activation source **before** calling Partner. It is valid only
when:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = false
Subscription.status = NO_CONTRACT
Subscription.planId = null
pendingPlanId != null
pendingShopifyPlanHandle != null
nextReconcileAt exactly equals payload.expectedNextReconcileAt
```

An `ACTIVE`/`TRIALING` subscription with an established current plan is not an
initial-activation job. Do not make a Partner request for it through this branch.

Keep the existing generic `BillingReconciliationService` transport-failure behaviour
that preserves an established ACTIVE/TRIALING projection.

Required focused tests:

1. changed `nextReconcileAt` after Partner call -> null/error result performs no DB
   mutation and no enqueue;
2. changed `pendingPlanId`/`pendingShopifyPlanHandle` after Partner call while
   `pendingEffectiveAt` is unchanged -> no mutation and no enqueue;
3. ACTIVE/TRIALING + current `planId` + onboarding incomplete -> this initial branch
   does not call Partner.

##### Correction 2 — make the verified-Free missing-cycle retry executable

Files:

```text
src/services/billing-subscription-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Attempt 3 schedules a retry when a pack-enabled Free plan is verified without an exact
provider cycle, but the scheduled job can never execute the cycle-discovery work.

Current first activation correctly writes:

```text
onboardingCompleted = true
status = ACTIVE/TRIALING
planId = verified Free plan
pendingPlanId = null
pendingShopifyPlanHandle = null
billingPeriodId = null
nextReconcileAt != null
```

but `reconcileJob(...)` currently requires:

```text
onboardingCompleted = false
pendingPlanId != null
pendingShopifyPlanHandle != null
```

before it calls Partner.

Therefore the cycle-discovery job is dead-on-arrival and the merchant can remain
permanently top-up-ineligible.

Add an explicit second job-state branch for **Free cycle discovery**.

A payload is a cycle-discovery job only when the reloaded durable state is exactly:

```text
Shop.status = ACTIVE
subscription.id = payload.subscriptionId
ShopSettings.onboardingCompleted = true
Subscription.status IN (ACTIVE, TRIALING)
Subscription.planId != null
Subscription.pendingPlanId = null
Subscription.pendingShopifyPlanHandle = null
Subscription.billingPeriodId = null
Subscription.nextReconcileAt exactly equals payload.expectedNextReconcileAt
current BillingPlan.active = true
current BillingPlan.kind = FREE
current BillingPlan.recoveryCreditPackEnabled = true
```

Use a single explicit retry cadence for this state:

```ts
const FREE_CYCLE_DISCOVERY_RETRY_MS = 5 * 60 * 1000;
```

When Partner returns the **same current Free plan**:

A. Exact cycle now exists:

```text
currentPeriodStart != null
currentPeriodEnd != null
```

Inside one transaction, re-read and compare the exact state/schedule above, then
create/reuse the canonical Free BillingPeriod:

```text
shopId
subscriptionId
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = FREE
includedRecoveryCreditsGranted = null
periodStart = provider currentPeriodStart
periodEnd = provider currentPeriodEnd
```

Do not create `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`.

Update:

```text
Subscription.billingPeriodId = exact period
currentPeriodStart/currentPeriodEnd = provider truth
providerSubscriptionId/trialEndsAt/cancelAtPeriodEnd = provider truth
lastSyncedAt = now
lastSyncErrorCode/At = null
nextReconcileAt =
  max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)
```

Commit first; then best-effort enqueue the deterministic next job.

Do **not** reset or modify `FREE_RECOVERY_LIFETIME` in this branch.

B. Same current Free plan still has no exact cycle:

```text
preserve onboarding = true
preserve ACTIVE/TRIALING plan
preserve lifetime/purchased/promotional balances
billingPeriodId remains null
lastSyncedAt = now
lastSyncErrorCode/At = null
nextReconcileAt = now + FREE_CYCLE_DISCOVERY_RETRY_MS
```

Commit, then enqueue that deterministic retry.

C. Partner transport failure during cycle discovery:

```text
preserve current plan/status/onboarding/entitlements
lastSyncErrorCode = PARTNER_API_ERROR
lastSyncErrorAt = now
nextReconcileAt = now + FREE_CYCLE_DISCOVERY_RETRY_MS
```

Commit/CAS only if the expected schedule still matches; enqueue after commit.

Do not implement same-plan period rollover/pre-close processing here.
`ARCH-010-BACKGROUND-007` owns that transition. This task only needs to make the
missing-cycle discovery state executable and leave the exact-period pre-close schedule
for BACKGROUND-007.

Extend `reconstruct()` so Redis repair also selects this exact cycle-discovery state.
Do not broaden reconstruction to every ACTIVE subscription.

Required focused tests:

1. first verified pack-enabled Free with no cycle completes onboarding and schedules
   cycle discovery;
2. processing that **next** cycle-discovery job actually calls Partner;
3. still-missing cycle advances the schedule by exactly 5 minutes and does not mutate
   entitlements;
4. a later exact cycle creates/reuses the Free BillingPeriod and schedules pre-close;
5. cycle-discovery transport failure preserves ACTIVE/TRIALING state and schedules
   exactly 5 minutes;
6. reconstruction includes the Free/no-period cycle-discovery row after Redis loss.

##### Correction 3 — make first lifetime-counter creation race-safe

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

The current sequence is:

```text
findUnique(FREE_RECOVERY_LIFETIME)
if missing:
  create(...)
```

Two first-activation executions can both observe no counter and race on the unique:

```text
@@unique([shopId, counter])
```

This can occur when the synchronous Shopify callback and the Background retry overlap.

Use this deterministic create/reuse pattern:

```text
1. findUnique(shopId, FREE_RECOVERY_LIFETIME)
2. if it exists:
     preserve it exactly;
     do not require current PlatformBillingPolicy
3. if it does not exist:
     read PlatformBillingPolicy.default
     if policy missing -> fail closed
     upsert on shopId_counter:
       update: {}
       create:
         shopId
         counter = FREE_RECOVERY_LIFETIME
         grantedQuantity = policy.lifetimeFreeRecoveryAllowance
```

Do not use `create(...)` after the initial absence check.

The `upsert(... update: {})` is required so a concurrent creator wins safely without
rewriting any existing:

```text
grantedQuantity
committedQuantity
reservedQuantity
refundingQuantity
version
```

Required focused tests:

1. existing lifetime counter + missing current policy -> activation succeeds and the
   existing counter is untouched;
2. initial lookup reports no counter, policy exists, race-safe `upsert` is used with
   `update: {}`;
3. replay never changes any existing lifetime-counter quantity.

##### Correction 4 — project provider pending truth when another current plan is returned

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

`applyOtherCurrentPlan(...)` currently clears:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
```

unconditionally.

The task contract is narrower:

```text
"If Shopify no longer reports that pending target, clear the stale local pending
initial-activation target."
```

When provider current truth is another plan, project provider pending truth using the
same rules as the existing rotating reconciliation path.

Required behaviour after the exact transaction stale guard succeeds:

1. map `provider.pendingPlanHandle` through active `BillingPlan` when non-null;
2. set current `planId/status/provider/cycle` from provider truth;
3. set pending fields to provider truth:

```text
pendingShopifyPlanHandle = provider.pendingPlanHandle
pendingPlanId =
  mapped provider pending plan when active
  otherwise null
pendingEffectiveAt = provider.pendingEffectiveAt
```

4. clear this task's initial-activation retry schedule:

```text
nextReconcileAt = null
```

5. do not set onboarding complete;
6. do not grant Paid included credits or execute the future plan change.

Therefore:

```text
provider current = Paid-A
provider pending = requested Free-B
```

must result in:

```text
current plan = Paid-A
pending target = Free-B
onboarding remains incomplete
nextReconcileAt = null
```

while:

```text
provider current = Paid-A
provider pending = null
```

must clear the stale initial Free target.

Add focused tests for both cases.

##### Correction 5 — failed deterministic jobs must remain reconstructable

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

The queue producer currently uses:

```ts
removeOnFail: 100
```

with a deterministic `jobId`.

That is incompatible with PostgreSQL-driven repair after a processor failure. BullMQ
does not add a new job when the same custom job ID still exists in the queue, including
a retained failed job. Keeping the failed job therefore prevents the periodic
reconstruction pass from recreating the same durable `expectedNextReconcileAt` work.

For this PostgreSQL-authoritative repair queue use:

```ts
removeOnFail: true
```

Keep:

```text
deterministic jobId
delay
removeOnComplete: 100
```

Do not introduce a second retry queue.

Unexpected processor failure then removes the failed BullMQ record; PostgreSQL still
contains the durable schedule, and the next periodic repair can recreate the same
deterministic job.

Add a focused test that asserts the exact enqueue options include:

```text
removeOnFail: true
```

and preserve the deterministic job ID.

##### Correction 6 — prove the production wiring and periodic repair, not only a generic scheduler callback

Files:

```text
tests/unit/runtime/entrypoint-isolation.test.ts
tests/unit/runtime/billing-scheduler.test.ts
```

The current scheduler test proves only that an arbitrary callback *can* call a mocked
`reconstruct()`. It does not prove the production billing entrypoint actually wires the
same queue-aware service to both the Worker and repair cadence.

Add a deterministic source/wiring regression for `src/entrypoints/billing.ts` proving
all of the following are present together:

```text
const subscriptionReconciliation =
  new BillingSubscriptionReconciliationService(... billingSubscriptionQueue)

createBillingSubscriptionReconciliationWorker(subscriptionReconciliation)

runBillingCycle contains:
  await subscriptionReconciliation.reconstruct()

startQueuePerformanceTelemetry is started for the billing subscription queue

stopQueuePerformanceTelemetry is included in closeResources
```

The test may follow the repository's existing source-inspection pattern in
`entrypoint-isolation.test.ts`; no new runtime framework is required.

Keep the existing Redis+PostgreSQL readiness regression.

##### Correction 7 — normalize the Attempt-4 Completion Report

The current task document does not contain one clean `## Completion Report` for
Attempt 3. Attempt-3 text is interleaved with the previous Attempt-2 report, and the
Git/VCS section still records older parent report evidence (`bc7c9bd`) rather than the
published Attempt-3 parent report supplied for review (`5ffc65f`).

On Attempt 4, rewrite only the mutable Completion Report area so it contains one
coherent current report with:

```text
## Completion Report

### Status
Attempt 4 complete; returned to review.

### Implementation
- exact changed files
- exact behaviour implemented for Corrections 1-6

### Validation Results
- focused command(s) and exact pass counts
- full npm test result with each unchanged baseline ID/reason
- npm run prisma:validate
- npm run build result, explicitly identifying only unchanged baseline errors
- git diff --check

### Git / VCS
- canonical parent worktree/branch
- canonical implementation worktree/branch
- all 3 isolation declarations
- all 4 synchronization outcomes
- implementation commit
- parent claim commit
- parent review/report commit
- database submodule revision
- submodule gitlink staged: no
```

Preserve all historical `### Architect Review` sections unchanged.

##### Attempt-4 focused acceptance matrix

Before returning Attempt 4 to `review`, the focused tests must explicitly prove all of
these cases:

```text
INITIAL ACTIVATION
1. due valid Free activation completes onboarding
2. provider null preserves exact pending target and schedules correct tier
3. 24h expiry clears exact target and leaves onboarding false
4. transport failure preserves NO_CONTRACT target and records error/retry
5. changed target after Partner call -> old job cannot mutate
6. changed schedule after Partner call -> old job cannot mutate
7. uninstalled/inactive -> no-op
8. established ACTIVE/TRIALING current plan -> initial branch does not call Partner

FREE ENTITLEMENT / PERIOD
9. first lifetime counter snapshots platform policy once
10. existing lifetime counter is preserved without requiring policy
11. concurrent/racing creation uses upsert update:{}
12. exact Free cycle creates/reuses full canonical period
13. no INCLUDED_RECOVERY_CREDITS period counter is created
14. lifetime quantities are unchanged on period replay

MISSING-CYCLE DISCOVERY
15. first verification with no cycle completes onboarding but remains period-less
16. its subsequent queued job is executable after onboarding
17. still-missing cycle schedules exactly +5 minutes
18. later exact cycle creates/reuses period and schedules pre-close
19. cycle-discovery transport failure preserves current entitlement
20. Redis reconstruction includes cycle-discovery rows

OTHER CURRENT PROVIDER PLAN
21. current other plan + provider pending requested target preserves mapped pending truth
22. current other plan + provider pending null clears stale initial target
23. neither branch completes onboarding or grants Paid included allowance

QUEUE / RUNTIME
24. startup reconstruction uses correct future/overdue delays
25. deterministic duplicates use the same job ID
26. queue-add failure does not roll back PostgreSQL state
27. enqueue options use removeOnFail:true
28. periodic repair is wired in the actual billing entrypoint
29. Worker and repair use the same queue-aware service instance
30. billing-worker readiness requires Redis + PostgreSQL
31. queue-performance telemetry is started and closed
32. frozen repair selector remains present
```

The existing ARCH-007 usage publication/reconciliation tests must continue to pass.

##### Scope guard

Attempt 4 remains `ARCH-010-BACKGROUND-001` only.

Do not implement:

- Paid first activation;
- same-plan period rollover/pre-close execution owned by BACKGROUND-007;
- upgrade/downgrade execution;
- cancellation;
- freeze/unfreeze transition logic owned by BACKGROUND-016;
- promotional-credit consumption;
- Admin UI;
- Render environment wiring.

Do not modify historical database migrations and do not change/stage the database
gitlink.

Reclaim this same task through `/moda-task`. The next valid claim is:

```text
attempt: 4
```

**Architect decision: Changes Requested — Attempt 3.**

#### Attempt 4 — Changes Requested

Attempt 4 satisfies most of the Attempt-3 correction contract. Architect review
accepts the following corrections as implemented:

- initial-activation source classification now occurs before the Partner request and
  rejects an established `ACTIVE`/`TRIALING` current plan;
- null/error initial-activation writes use an exact atomic `updateMany` predicate over
  `subscriptionId`, `NO_CONTRACT`, `planId=null`, exact pending plan id/handle,
  exact `pendingEffectiveAt`, and exact `nextReconcileAt`;
- a failed exact CAS performs no replacement enqueue;
- an explicit post-onboarding Free cycle-discovery branch exists;
- later missing-cycle and cycle-discovery transport failures use
  `FREE_CYCLE_DISCOVERY_RETRY_MS = 5 * 60 * 1000`;
- later exact-cycle discovery creates/reuses the canonical Free BillingPeriod and
  schedules the period drain;
- first lifetime Free grant creation now uses `upsert(..., update: {})` and existing
  counters do not require the current platform policy;
- another provider current plan now projects provider pending handle/id/effective time
  instead of unconditionally clearing pending truth;
- deterministic BullMQ jobs use `removeOnFail: true`;
- production `billing.ts` uses the same queue-aware reconciliation service for the
  Worker and periodic reconstruction;
- billing-worker readiness requires Redis + PostgreSQL;
- queue-performance telemetry is started and stopped with the billing process;
- the frozen repair selector remains present;
- the implementation diff from Attempt 3 is bounded to:
  `src/services/billing-subscription-reconciliation.service.ts`,
  `tests/unit/services/billing-subscription-reconciliation.service.test.ts`, and
  `tests/unit/runtime/entrypoint-isolation.test.ts`;
- database revision
  `6d5fb9adf2e5c1fb28333b330dd183c9cda41550` is preserved and no database gitlink is
  staged.

The reported eight nullable-`counterId` build diagnostics and the six documented
full-suite baseline failures remain outside the task-touched implementation and are not
the reason for this decision.

Attempt 4 still cannot be accepted because the remaining cycle-discovery scheduling and
concurrency rules do not match the binding Attempt-3 contract.

##### Correction 1 — first verified Free/no-cycle schedule MUST be exactly five minutes

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

The current `completeVerifiedFree(...)` computes a pack-enabled/no-cycle schedule with:

```ts
pendingEffectiveAt
  ? nextSubscriptionReconcileAt(pendingEffectiveAt, now)
  : null
```

That is the **initial activation retry algorithm**, not the post-onboarding
cycle-discovery algorithm.

It is observably wrong in the current focused test:

```text
now                = 2026-09-12T12:00:00.000Z
pendingEffectiveAt = 2026-09-12T11:00:00.000Z
currentPeriodEnd   = null
```

The implementation/test currently produce:

```text
nextReconcileAt = 2026-09-12T12:30:00.000Z
```

The required result is:

```text
nextReconcileAt = 2026-09-12T12:05:00.000Z
```

Use this exact scheduling rule after Shopify has verified the Free plan:

```ts
let nextReconcileAt: Date | null = null;

if (recoveryCreditPackEnabled) {
  if (provider.currentPeriodEnd) {
    nextReconcileAt = new Date(
      Math.max(
        now.getTime(),
        provider.currentPeriodEnd.getTime()
          - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS,
      ),
    );
  } else {
    nextReconcileAt = new Date(
      now.getTime() + FREE_CYCLE_DISCOVERY_RETRY_MS,
    );
  }
}
```

Do **not** call `nextSubscriptionReconcileAt(...)` after the Free plan has been
verified and onboarding is completing.

The initial-activation retry tiers remain unchanged for:

```text
provider null before activation
Partner transport failure before activation
```

Update the existing test:

```text
"uses bounded cycle discovery retry when a pack-enabled Free provider omits the exact cycle"
```

to assert exactly:

```text
2026-09-12T12:05:00.000Z
```

Also assert the deterministic queued payload uses that same
`expectedNextReconcileAt`.

##### Correction 2 — bind every cycle-discovery retry to the exact current Free plan

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

The current cycle-discovery null/error CAS uses:

```ts
planId: { not: null }
```

That is not an exact stale guard. An older cycle-discovery Partner request can return
after the Subscription has moved to another non-null plan while retaining the same
schedule timestamp.

Define a separate exact expected state for cycle discovery. The type/shape must contain:

```text
subscriptionId
currentPlanId
nextReconcileAt
```

The cycle-discovery state being verified is:

```text
status IN (ACTIVE, TRIALING)
planId = currentPlanId
billingPeriodId = null
pendingPlanId = null
pendingShopifyPlanHandle = null
pendingEffectiveAt = null
nextReconcileAt = expectedNextReconcileAt
```

`recordMissingCycle(...)` and `recordCycleDiscoveryFailure(...)` MUST use:

```ts
planId: expected.currentPlanId
```

and MUST NOT use:

```ts
planId: { not: null }
```

If the exact CAS returns `count === 0`:

```text
do not mutate
do not enqueue
return success/no-op
```

Required focused tests:

1. cycle-discovery Partner returns null, but `planId` changed while the request was in
   flight -> `updateMany.count = 0` -> no enqueue;
2. cycle-discovery Partner throws, but `planId` changed while the request was in flight
   -> no enqueue;
3. both CAS predicates contain the exact original `currentPlanId`.

##### Correction 3 — make the reconstruction selector match the exact cycle-discovery state

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

The current reconstruction branch includes:

```text
ACTIVE/TRIALING
planId != null
billingPeriodId = null
pendingPlanId = null
pendingShopifyPlanHandle = null
nextReconcileAt != null
active Free pack-enabled plan
```

but it does not require:

```text
ShopSettings.onboardingCompleted = true
Subscription.pendingEffectiveAt = null
```

The Attempt-3 contract required reconstruction of the **exact** post-onboarding
cycle-discovery state, not every superficially similar ACTIVE Free row.

Restructure the `shop.findMany` `where` clause into a top-level `OR` so the
cycle-discovery branch can include the ShopSettings predicate without incorrectly
applying it to frozen/initial rows.

Required logical shape:

```text
Shop.status = ACTIVE
AND
(
  initial-repair branch:
    Subscription.pendingPlanId != null
    AND Subscription.nextReconcileAt != null

  OR frozen-repair branch:
    Subscription.status = FROZEN
    AND Subscription.nextReconcileAt != null

  OR Free-cycle-discovery branch:
    ShopSettings.onboardingCompleted = true
    AND Subscription.status IN (ACTIVE, TRIALING)
    AND Subscription.planId != null
    AND Subscription.billingPeriodId = null
    AND Subscription.pendingPlanId = null
    AND Subscription.pendingShopifyPlanHandle = null
    AND Subscription.pendingEffectiveAt = null
    AND Subscription.nextReconcileAt != null
    AND current BillingPlan.active = true
    AND current BillingPlan.kind = FREE
    AND current BillingPlan.recoveryCreditPackEnabled = true
)
```

Do not remove the frozen branch.

Update the reconstruction source/query regression to prove both:

```text
onboardingCompleted = true
pendingEffectiveAt = null
```

are required for the cycle-discovery branch.

##### Correction 4 — remove the read/check/write race from successful transactional outcomes

Files:

```text
src/services/billing-subscription-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Three successful write paths currently do:

```text
transaction.subscription.findUnique(...)
compare expected state
perform other writes
transaction.subscription.update({ where: { id } ... })
```

The comparison and final update are separate PostgreSQL statements. Under the default
transaction isolation, another transaction can change the Subscription after the
`findUnique` check and before the final `update`, allowing the stale job to overwrite
newer durable state.

The affected paths are:

```text
completeVerifiedFree(...)
applyOtherCurrentPlan(...)
reconcileFreeCycle(...)
```

Use PostgreSQL row locks. Do not add a schema field and do not hold a database lock
across the Partner network request.

Add these helpers in this service (names may differ; lock behaviour/order may not):

```ts
private async lockShopSettings(
  transaction: Prisma.TransactionClient,
  shopId: string,
): Promise<void> {
  await transaction.$queryRaw(Prisma.sql`
    SELECT "shopId"
    FROM "shopify"."ShopSettings"
    WHERE "shopId" = ${shopId}
    FOR UPDATE
  `);
}

private async lockSubscription(
  transaction: Prisma.TransactionClient,
  subscriptionId: string,
): Promise<void> {
  await transaction.$queryRaw(Prisma.sql`
    SELECT "id"
    FROM "billing"."Subscription"
    WHERE "id" = ${subscriptionId}
    FOR UPDATE
  `);
}
```

Because `Prisma.sql` is needed at runtime, change the Prisma import from type-only as
required.

For **initial/onboarding transactions** (`completeVerifiedFree` and
`applyOtherCurrentPlan`) the lock order is mandatory:

```text
1. ShopSettings
2. Subscription
3. re-read ShopSettings + Subscription
4. compare exact expected state
5. perform writes
```

This lock order is the cross-service ARCH-010 lock order and must not be reversed.

After the locks, require:

```text
ShopSettings.onboardingCompleted = false
Subscription.status = NO_CONTRACT
Subscription.planId = null
pendingPlanId = exact expected pendingPlanId
pendingShopifyPlanHandle = exact expected pendingShopifyPlanHandle
pendingEffectiveAt = exact expected pendingEffectiveAt
nextReconcileAt = exact expected nextReconcileAt
```

If any comparison fails:

```text
return/no-op
do not create/reuse lifetime counter
do not create/reuse BillingPeriod
do not update Subscription
do not update ShopSettings
do not enqueue
```

For **cycle discovery** (`reconcileFreeCycle`) lock the Subscription before its final
state read and require the exact cycle-discovery state including:

```text
planId = expected.currentPlanId
nextReconcileAt = exact expected schedule
```

No lock is held while `partner.getActiveSubscription(...)` runs.

Required focused tests:

1. `completeVerifiedFree` acquires ShopSettings lock before Subscription lock;
2. after locking, a changed pending target causes a full no-op before entitlement,
   period, onboarding or subscription writes;
3. `applyOtherCurrentPlan` uses the same ShopSettings -> Subscription lock order;
4. `reconcileFreeCycle` locks the Subscription before re-reading and writing its exact
   period state.

The unit harness transaction mock must expose `$queryRaw`.

##### Correction 5 — add the missing initial transport-failure acceptance test

The canonical task requires both:

```text
provider transport failure preserves NO_CONTRACT pending intent
transport failure records error metadata and schedules retry
```

The current focused file has an initial transport-error test only for the stale-CAS
`count=0` case. It does not prove the normal successful retry write.

Add one exact test with:

```text
initial state:
  onboardingCompleted = false
  status = NO_CONTRACT
  planId = null
  pendingPlanId = plan-free
  pendingShopifyPlanHandle = free-2026
  pendingEffectiveAt = 2026-09-12T11:00:00.000Z
  nextReconcileAt = 2026-09-12T12:00:00.000Z

Partner:
  throws timeout/error

updateMany.count:
  1
```

Assert the `updateMany.where` contains the exact original target/effective time/schedule
and the `data` contains:

```text
lastSyncErrorCode = PARTNER_API_ERROR
lastSyncErrorAt = now
nextReconcileAt = 2026-09-12T12:30:00.000Z
```

Assert the mutation data does **not** clear:

```text
pendingPlanId
pendingShopifyPlanHandle
pendingEffectiveAt
```

and assert one deterministic delayed job is enqueued for:

```text
expectedNextReconcileAt = 2026-09-12T12:30:00.000Z
```

This 30-minute expectation is correct here because this is still the **initial**
activation retry tier. It must not be confused with Correction 1's five-minute
post-onboarding cycle-discovery cadence.

##### Correction 6 — keep queue telemetry on the canonical Shared queue name

File:

```text
src/entrypoints/billing.ts
```

The current telemetry wiring contains the literal:

```ts
queueNames: ["billing-subscription-reconcile"]
```

Do not duplicate the Shared queue contract in runtime wiring.

Use either:

```ts
queueNames: [billingSubscriptionQueue.name]
```

or the imported:

```ts
BILLING_SUBSCRIPTION_RECONCILE_QUEUE_NAME
```

Prefer `billingSubscriptionQueue.name` because the Queue has already been created from
the canonical Shared constant in `billing-resources.ts`.

Update the source/wiring regression accordingly.

##### Correction 7 — Attempt-5 Completion Report and validation evidence

The current Attempt-4 Completion Report is coherent and its implementation scope is
bounded. Preserve that historical evidence.

For Attempt 5, replace only the mutable current Completion Report with one exact report
containing:

```text
### Status
Attempt 5 complete; returned to review.

### Implementation
- exact changed files
- Corrections 1-6 implemented

### Validation Results
- exact focused command(s) and pass count
- full npm test totals and each unchanged baseline failure
- npm run prisma:validate
- npm run build result
- git diff --check

### Git / VCS
- canonical parent worktree/branch
- canonical implementation worktree/branch
- shared workspace checkout switched/mutated: no
- shared implementation checkout switched/mutated: no
- another task worktree reused: no
- all four start-of-attempt synchronization outcomes
- implementation commit
- parent claim commit
- parent report/review commit
- final metadata commit, if one is created
- database revision
- submodule gitlink staged: no
```

The review submission supplied for Attempt 4 reports:

```text
implementation commit: f877f81
parent report commit: 649150c
final metadata commit: 02f5607
```

Do not copy those hashes into Attempt 5; record the new immutable Attempt-5 hashes.

##### Attempt-5 focused stop gate

Do not return Attempt 5 to `review` until all of these are true:

```text
A. VERIFIED FREE / CYCLE DISCOVERY
1. first verified pack-enabled Free with exact cycle -> pre-close schedule
2. first verified pack-enabled Free with NO cycle -> exactly now + 5 minutes
3. the queued +5 minute cycle-discovery job is executable after onboarding
4. still-missing cycle -> exactly another +5 minutes
5. later exact cycle -> canonical period + pre-close schedule
6. cycle transport failure -> exactly +5 minutes and current entitlement preserved

B. STALE/RACE PROTECTION
7. initial null response exact CAS rejects changed target
8. initial error response exact CAS rejects changed schedule
9. cycle null response exact CAS rejects changed current plan
10. cycle error response exact CAS rejects changed current plan
11. successful Free completion uses ShopSettings -> Subscription row-lock order
12. successful other-current projection uses the same lock order
13. exact-cycle projection locks Subscription before final state read/write

C. RECONSTRUCTION
14. future job delay is correct
15. overdue job delay is zero
16. deterministic duplicate job ID is stable
17. exact post-onboarding Free cycle-discovery selector requires onboarding=true
18. exact cycle-discovery selector requires pendingEffectiveAt=null
19. frozen repair selector remains present

D. ENTITLEMENT / PROVIDER TRUTH
20. first lifetime counter snapshots platform policy once
21. existing lifetime counter is unchanged and does not require current policy
22. Free period contains the full Free snapshot and no included-credit counter
23. provider-other-current + provider pending target maps that pending truth
24. provider-other-current + provider pending null clears stale initial target
25. neither other-current branch completes onboarding or grants Paid included credits

E. QUEUE / RUNTIME
26. `removeOnFail: true`
27. durable DB state survives queue-add failure
28. Worker and repair cadence use the same queue-aware service
29. periodic reconstruction is wired in the actual billing entrypoint
30. Redis + PostgreSQL readiness remains required
31. queue telemetry uses the canonical queue name and is closed at shutdown

F. ORIGINAL TRANSPORT REQUIREMENT
32. normal initial Partner transport failure preserves NO_CONTRACT pending intent,
    records PARTNER_API_ERROR and schedules the correct tiered retry
```

The existing ARCH-007 billing/usage reconciliation tests must continue to pass.

##### Scope guard

Attempt 5 remains `ARCH-010-BACKGROUND-001` only.

Do not implement:

- Paid first activation;
- same-plan billing-period rollover/pre-close execution owned by BACKGROUND-007;
- upgrade/downgrade execution;
- cancellation;
- freeze/unfreeze transition logic owned by BACKGROUND-016;
- promotional-credit consumption;
- Admin UI;
- Render environment wiring.

Do not modify historical database migrations and do not stage/change the database
gitlink.

Stop and return to `moda_architect` instead of inventing another design if the
ShopSettings/Subscription row locks cannot be implemented with the existing Prisma
transaction client.

Reclaim this same task through `/moda-task`. The next valid claim is:

```text
attempt: 5
```

**Architect decision: Changes Requested — Attempt 4.**

## Final frozen-state repair rows

The startup/periodic delayed-job repair selector MUST also treat this durable row as actionable once DATABASE-008/BACKGROUND-016 are available:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

Recreate the existing deterministic `billing-subscription-reconcile` job. Do not introduce a second frozen queue.
