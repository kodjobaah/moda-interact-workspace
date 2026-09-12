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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-12T08:17:23Z
attempt: 2
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
In Progress.

### Files Changed
None. Implementation source was not changed.

### Work Completed
Eligibility and dependency verification completed. The canonical implementation
worktree was created and synchronized, but implementation stopped at the task's
explicit Prisma capability stop condition.

### Validation Results
All five explicit dependencies were verified complete. The implementation
worktree is pinned to database submodule commit
`6e916806649ab0cbf705656746f0aba02f67dc72`, whose schema does not define
`Subscription.nextReconcileAt`. The current database repository `main` contains
that field, but consuming it here requires a submodule gitlink update owned by
the developer/architect workflow.

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
  commit: e0ca1c7492a37de3b30d50010446156bf8ee135c
  remote branch: origin/task/ARCH-010-BACKGROUND-001 (not created; no source commit)
  pushed: no implementation changes

Parent workspace:
  task file: docs/decisions/background/ARCH-010/BACKGROUND-001-pending-subscription-reconciliation.md
  claim commit: cc4de24
  blocked-state commit: pending
  remote branch: origin/task/ARCH-010-BACKGROUND-001
  pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Architectural Concerns
The accepted ARCH-010 database schema capability is not yet reachable from
this background branch because its pinned database gitlink remains on the older
ARCH-009 commit. The developer/architect must update the background repository's
database submodule pointer to a database revision containing
`Subscription.nextReconcileAt` before this task can safely implement durable
reconciliation.

### Unresolved Issues
After the database gitlink is advanced, rerun the task on the same mirrored
branches and attempt history; no implementation source or tests have been
changed in this attempt.

### Architect Review
Pending.


## Final frozen-state repair rows

The startup/periodic delayed-job repair selector MUST also treat this durable row as actionable once DATABASE-008/BACKGROUND-016 are available:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

Recreate the existing deterministic `billing-subscription-reconcile` job. Do not introduce a second frozen queue.
