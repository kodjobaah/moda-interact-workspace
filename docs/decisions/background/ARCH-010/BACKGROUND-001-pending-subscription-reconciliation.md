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
status: review
priority: 30
executor: copilot
claimed_at: 2026-09-12T00:00:00Z
attempt: 3
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

Implementation commit `2a3e8eff0833bc50ffe30a3cf387fca88cc8cec2` changes the following paths:


- `src/runtime/readiness.ts`

- `database` gitlink, preserved at database revision `6d5fb9adf2e5c1fb28333b330dd183c9cda41550`
- `src/entrypoints/billing-resources.ts`
- `tests/unit/runtime/billing-scheduler.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`
- `tests/unit/runtime/readiness.test.ts`
- `src/entrypoints/billing.ts`
- `src/observability/queue-performance.ts`

The database gitlink was not changed and remains at revision `6d5fb9adf2e5c1fb28333b330dd183c9cda41550`.
- `src/observability/worker-metrics.ts`
- `src/services/billing-reconciliation.service.ts`
Attempt 3 completed the requested corrections:

1. Corrections 1, 2 and 7: `billing.ts` now constructs one queue-aware reconciliation service, injects that instance into the BullMQ worker, runs reconstruction during startup and every billing cadence, starts shared queue-performance telemetry, and closes it with billing resources. Billing readiness requires Redis and PostgreSQL.
2. Correction 3: rotating reconciliation preserves unresolved initial Free activation when the provider reports the pending target before the delayed consumer runs.
3. Correction 4: the consumer requires the durable initial-activation source state and uses compare-and-set updates after the Partner call, preventing newer pending selections or schedules from being overwritten.
4. Correction 5: another provider current plan is projected through the existing status/plan/cycle rules without falsely completing the requested Free activation.
5. Correction 6: verified Free activation uses the durable policy for the one-time lifetime grant, fails closed when the first-grant policy is missing, preserves existing counters and period state, stores the complete Free period snapshot, creates no included-credit period counter, and schedules bounded cycle discovery when needed.
6. Correction 8 and the frozen-state addendum: focused coverage exercises the required stale guards, retry/expiry/error paths, Free entitlement and period semantics, provider-plan projection, race protection, startup/periodic reconstruction, deterministic repair, queue failure isolation, and the `FROZEN` durable repair selector.
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts`

Focused reconciliation/runtime tests: passed, 5 files and 49 tests.
Added the durable subscription reconciliation service and BullMQ worker to the
Full declared suite (`npm test`): 564 passed, 7 skipped, 6 failed. Four integration failures are blocked because database `moda_interact_test` does not exist. The remaining unit failure is the unchanged `tests/unit/runtime/observability-startup.test.ts` expectation of shared package version `0.9.0`, while the accepted repository dependency is `0.10.0`.
retries, clears expired activation intent, reconstructs delayed jobs from
PostgreSQL, and preserves existing subscription projection status on Partner
transport failures. Billing resources, scheduler integration, queue metrics, and
`npm run build`: blocked by 8 pre-existing nullable `counterId` type errors in
`src/services/free-recovery-reservation.service.ts` and
`src/services/purchased-recovery-reservation.service.ts`; no errors remain in
the task's touched files.

### Validation Results
Focused reconciliation and existing billing tests: passed, 2 files and 19 tests.

Full unit suite: 552 passed and 1 failed. The failure is the pre-existing
`tests/unit/runtime/observability-startup.test.ts` expectation of shared package
version `0.9.0`, while the repository declares `0.10.0`.

`npm run prisma:validate`: passed.

`npm run build`: remains blocked by 8 pre-existing nullable `counterId` type
errors in `src/services/free-recovery-reservation.service.ts` and
`src/services/purchased-recovery-reservation.service.ts`; no errors remain in
the task's touched reconciliation service after the local create-status repair.

`git diff --check`: passed.

### Git / VCS
Task branch: `task/ARCH-010-BACKGROUND-001`

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-001
  parent branch: task/ARCH-010-BACKGROUND-001
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-001
  implementation branch: task/ARCH-010-BACKGROUND-001
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: moda-interact-background
  commit: 2a3e8eff0833bc50ffe30a3cf387fca88cc8cec2
  remote branch: origin/task/ARCH-010-BACKGROUND-001
  pushed: yes
  database submodule revision: 6d5fb9adf2e5c1fb28333b330dd183c9cda41550

Parent workspace:
  task file: docs/decisions/background/ARCH-010/BACKGROUND-001-pending-subscription-reconciliation.md
  claim commit: cc4de24
  review-state commit: bc7c9bd
  remote branch: origin/task/ARCH-010-BACKGROUND-001
  pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architectural Concerns
The full repository build and unit suite retain unrelated baseline failures
listed under Validation Results. The implementation branch intentionally
preserves the database gitlink at the committed revision containing
`Subscription.nextReconcileAt`.

### Unresolved Issues
Repository validation retains the documented unrelated test/build baselines above; no bounded-task implementation issues remain.


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

## Final frozen-state repair rows

The startup/periodic delayed-job repair selector MUST also treat this durable row as actionable once DATABASE-008/BACKGROUND-016 are available:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

Recreate the existing deterministic `billing-subscription-reconcile` job. Do not introduce a second frozen queue.
