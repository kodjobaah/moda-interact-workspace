---
id: ARCH-010-BACKGROUND-007
architecture_id: ARCH-010
title: Implement canonical same-plan App Pricing BillingPeriod rollover for Paid and
  Free
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 47
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-BACKGROUND-001
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-008
- ARCH-010-BACKGROUND-009
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-008-BACKGROUND-001
enables:
- ARCH-010-BACKGROUND-003
- ARCH-010-BACKGROUND-006
- ARCH-010-BACKGROUND-010
- ARCH-010-BACKGROUND-012
- ARCH-010-SHOPIFY-007
- ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-007: Canonical same-plan App Pricing BillingPeriod rollover for Paid and Free

## Objective

Implement one canonical Background transition for an existing mapped Shopify App Pricing subscription moving from one exact provider `currentBillingCycle` to a later exact cycle on the **same mapped plan**.

The same transition service must support two explicit plan-kind branches:

```text
PAID_METERED
  -> rotate Shopify BillingPeriod
  -> close/forfeit old monthly included entitlement
  -> open new BillingPeriod
  -> grant new monthly included allowance exactly once

FREE
  -> rotate Shopify BillingPeriod for commercial/App-Event scope
  -> open new BillingPeriod
  -> DO NOT create/refill a period included-credit counter
  -> DO NOT reset LIFETIME_FREE_RECOVERY_CREDITS
```

The service must be reusable by:

- normal scheduled cycle rollover;
- rotating subscription reconciliation that observes a later same-plan cycle;
- authenticated reinstall reconciliation when Shopify advanced cycles while Moda was uninstalled.

Do not create a second queue or deployable process. Extend the existing ARCH-010 subscription reconciliation queue/consumer in `moda-billing-worker`.

## Inspect before editing

```text
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/runtime/billing-scheduler.ts
src/services/billing-reconciliation.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/services/recovery-credit-purchase.service.ts
src/services/paid-included-recovery-reservation.service.ts   # exact integrated name
src/services/effective-billing-policy.service.ts
src/providers/shopify-partner-billing.provider.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
tests/unit/services/recovery-credit-purchase.service.test.ts
package.json
```

Read implemented BACKGROUND-001/002/008/009, DATABASE-004 and published Shared billing contract before editing. Reuse their DB/queue/retry/logging patterns.

## Shared contract

Import from:

```text
@modainteract/moda-interact-shared/billing
```

Use the accepted `reconcile-subscription` payload and deterministic job ID.

Import exactly:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

Do not define a local five-minute constant.

## Which subscriptions get scheduled

### Paid

Every mapped active `PAID_METERED` subscription with an exact current OPEN BillingPeriod is scheduled.

### Free

A mapped active `FREE` subscription is scheduled for monthly provider-period rollover when:

```text
BillingPlan.recoveryCreditPackEnabled = true
AND Subscription.billingPeriodId != null
AND Subscription.currentPeriodStart/currentPeriodEnd are exact
```

Reason: the Free BillingPeriod is required to scope recovery-credit-pack App Events. Free recovery entitlement itself remains lifetime.

## Scheduling

For either scheduled kind:

```text
preCloseAt = currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
nextReconcileAt = max(now, preCloseAt)
```

### Pre-close job

When:

```text
now < currentPeriodEnd
AND now >= preCloseAt
```

perform only:

1. stale-guard against `expectedNextReconcileAt`;
2. re-read exact current Subscription/BillingPeriod;
3. flush reportable Shopify billing `UsageEvent` rows for that BillingPeriod;
4. do not close the period;
5. set `nextReconcileAt = currentPeriodEnd`;
6. commit;
7. best-effort enqueue exact-boundary job after commit.

If the job runs before `preCloseAt`, reschedule to `preCloseAt` without changing period state.

## Behaviour during DRAINING

### Paid

Existing ARCH-010 paid boundary rules continue:

- block a new recovery that would consume Paid included allowance and create the normal recovery App Event;
- block new recovery-credit-pack purchase creation;
- allow recovery funded by an already-active purchased lifetime credit;
- preserve read/history/support and existing non-billable conversation processing.

### Free

Do **not** block ordinary recovery admission merely because the Shopify Free billing cycle is draining.

Allowed:

- recovery from remaining `LIFETIME_FREE_RECOVERY_CREDITS` capacity;
- recovery from already-active purchased lifetime credits;
- existing conversations;
- dashboard/history/support.

Blocked:

- new recovery-credit-pack purchase creation;
- any other action that creates an App Event tied to the closing cycle.

## Boundary provider query

At/after `currentPeriodEnd`, query Partner `activeSubscription` outside the DB transaction.

Require:

```text
provider != null
provider current plan handle == local mapped current plan handle
mapped BillingPlan.active = true
provider currentBillingCycle.startTime/endTime != null
start < end
```

Additional Paid requirement:

```text
plan.kind = PAID_METERED
configured normal recovery meter is present in provider usage items
```

Additional Free requirement:

```text
plan.kind = FREE
if recoveryCreditPackEnabled=true:
  configured pack meter is present in provider usage items
```

Do not require the Paid normal recovery meter for Free.

## Provider still reports old exact cycle

Do not close/open.

- preserve current plan/period;
- record bounded reconciliation lag metadata;
- schedule short retry (start at 60 seconds, then accepted bounded tiers);
- best-effort enqueue retry.

During this lag:

- Paid remains fail-closed for new cycle-dependent recovery/top-up work;
- Free keeps lifetime/purchased recovery admission available but pack purchase remains blocked because the current App Event cycle is expired/unverified.

## Provider reports later same-plan non-overlapping cycle

Accept only when:

```text
providerStart >= oldPeriodEnd
providerEnd > providerStart
```

`providerStart == oldPeriodEnd` is ordinary renewal.

`providerStart > oldPeriodEnd` is recovery after downtime. Create only the provider's current exact cycle; do not synthesize missed intermediate periods.

Overlapping-but-not-identical cycles fail closed.

## Other provider outcomes

This task does NOT apply different-plan or no-contract transitions.

```text
provider current mapped different plan -> BACKGROUND-010
provider current unmapped plan          -> existing fail-closed UNMAPPED path
provider null/no contract               -> ARCH-010-BACKGROUND-012 cancellation/no-contract transition
provider transport failure              -> preserve last known state + retry
```

A current `FREE` result is supported by this task **when the local current plan is the same mapped Free plan**. Do not treat that same-plan Free renewal as unsupported.

## Canonical internal transition service

Create/refactor one focused service (exact filename may follow repository conventions) that accepts already-verified provider current-cycle facts and performs no external network calls.

It must be called by:

- BullMQ subscription reconciliation;
- rotating reconciliation;
- authenticated reinstall reconciliation.

Do not duplicate period close/open SQL in callers.

## Transaction boundary

Provider query happens before transaction.

Inside one transaction:

1. row-lock Subscription using the repository-approved pattern;
2. re-read Subscription/current BillingPeriod/current mapped plan;
3. stale/no-op if exact provider successor is already current;
4. fail closed if local source period/plan changed since provider query;
5. branch by plan kind;
6. finalize old-period billing events;
7. close old BillingPeriod;
8. create/reuse exact successor BillingPeriod;
9. for Paid only, create/reuse fresh included-credit counter;
10. update Subscription current pointer/cycle/provider/scheduling fields;
11. commit.

No Shopify, Redis or telemetry network I/O inside transaction.

## Shared old-period App Event finalization

Pre-close attempts to flush due reportable `UsageEvent` rows for the old BillingPeriod.

Once Shopify proves a later current cycle, remaining old-period `PENDING`/`RETRYABLE` billing events cannot be retried as current-cycle events. Mark them using the repository's bounded needs-attention state, e.g.:

```text
shopifyReportState = NEEDS_ATTENTION
nextReportAt = null
providerErrorCode = PERIOD_CLOSED_BEFORE_REPORT
```

Do not overwrite REPORTED.

Do not steal a genuinely current IN_FLIGHT claim; emit bounded operational evidence and let normal claim recovery finish.

If the event is `RECOVERY_CREDIT_PACK_PURCHASE`, the linked purchase must not become ACTIVE and must enter/remain its existing `NEEDS_ATTENTION` workflow.

This rule applies to both Free and Paid periods.

## Paid branch

### Finalize included entitlement

Require the unique old `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`.

At boundary:

1. release outstanding `RESERVED`/`AMBIGUOUS` period reservations with `PERIOD_CLOSED`;
2. decrement exact reserved quantity;
3. forfeit every remaining unused included unit;
4. require final:

```text
reservedQuantity = 0
committedQuantity + forfeitedQuantity = grantedQuantity
```

Counter/reservation mismatch aborts transition.

### Successor paid BillingPeriod

Create/reuse exact provider period with:

```text
subscriptionId
shopId
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = PAID_METERED
includedRecoveryCreditsGranted = BillingPlan.includedRecoveryConversationAllowance
periodStart = providerStart
periodEnd = providerEnd
status = OPEN
closedAt = null
closeReason = null
```

Create/reuse exactly one period counter:

```text
counter = INCLUDED_RECOVERY_CREDITS
grantedQuantity = includedRecoveryConversationAllowance
committedQuantity = 0
reservedQuantity = 0
forfeitedQuantity = 0
```

Never reset an already-existing matching successor counter during replay.

After commit, send one best-effort BACKGROUND-009 capacity-resume hint because a fresh Paid monthly allowance may unblock recoveries.

## Free branch

### Old Free entitlement

Do not load/finalize a period included-credit counter. None should exist.

Preserve exactly:

```text
LIFETIME_FREE_RECOVERY_CREDITS counter/usage
purchased lifetime credits
refund/purchase history
```

### Successor Free BillingPeriod

Create/reuse exact provider period with:

```text
subscriptionId
shopId
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = FREE
includedRecoveryCreditsGranted = null
periodStart = providerStart
periodEnd = providerEnd
status = OPEN
closedAt = null
closeReason = null
```

Create **no** `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`.

Do not send a BACKGROUND-009 capacity-resume hint solely because the Free provider cycle changed. The five lifetime Free recoveries do not replenish.

## Close old BillingPeriod

For either same-plan branch:

```text
status = CLOSED
closedAt = old.periodEnd
closeReason = RENEWED_SAME_PLAN
```

Do not alter old start/end/snapshots.

## Subscription update

Set from verified provider truth:

```text
planId = same mapped current plan
observedShopifyPlanHandle = provider current handle
status = ACTIVE (or accepted current projection)
billingPeriodId = successor.id
currentPeriodStart = providerStart
currentPeriodEnd = providerEnd
providerSubscriptionId = provider truth
cancelAtPeriodEnd = provider truth
lastSyncedAt = now
lastSyncErrorCode/At = null
```

Project provider pending update fields normally; do not execute a pending different plan here.

Scheduling:

```text
Paid -> nextReconcileAt = max(now, providerEnd - drainWindow)
Free with recoveryCreditPackEnabled -> same schedule
Free without pack billing -> may clear cycle-specific nextReconcileAt unless another pending/reinstall reason exists
```

Best-effort enqueue after commit. Redis failure never rolls back DB state.

## Reconstruction

Startup/periodic repair must restore missing delayed jobs for:

```text
Shop.status = ACTIVE
Subscription.status = ACTIVE
Subscription.billingPeriodId != null
Subscription.nextReconcileAt != null
AND (
  plan.kind = PAID_METERED
  OR (plan.kind = FREE AND plan.recoveryCreditPackEnabled = true)
)
```

Retain initial-activation and reinstall reconstruction classes.

## Rotating reconciliation compatibility

Remove blind `BillingPeriod.upsert(... OPEN ...)` as an independent later-cycle creation path.

After this task:

```text
same exact provider cycle -> projection metadata may refresh; no period mutation
later same-plan Paid cycle -> canonical transition
later same-plan Free cycle -> canonical transition
current different mapped plan -> BACKGROUND-010
null/unmapped/error -> corresponding fail-closed lifecycle path
```

No code path may leave two OPEN periods for one Subscription.

## Required tests

### Common

1. pre-close schedule reconstruction works;
2. early job reschedules to drain start;
3. drain job flushes old-period billable events and schedules exact boundary;
4. stale expectedNextReconcileAt is no-op;
5. provider old exact cycle does not close/open and retries;
6. provider transport failure preserves known state and retries;
7. contiguous later same-plan cycle transitions atomically;
8. gap later cycle creates only current provider cycle;
9. overlapping non-identical cycle fails closed;
10. concurrent duplicate rollover creates one successor OPEN period;
11. replay never reopens a CLOSED target or duplicates grants;
12. old PENDING/RETRYABLE billing events become NEEDS_ATTENTION after provider advances;
13. REPORTED remains REPORTED;
14. IN_FLIGHT isn't overwritten;
15. unreported pack event never activates its purchase;
16. enqueue failure leaves committed transition and repair reconstructs job;
17. rotating reconciliation no longer blindly creates later OPEN periods.

### Paid

18. old reservations release with PERIOD_CLOSED;
19. old included counter ends reserved=0 and committed+forfeited=granted;
20. mismatch aborts close;
21. successor paid snapshots/grant are exact;
22. successor included counter created exactly once;
23. paid rollover sends one post-commit capacity-resume hint;
24. Paid DRAINING/RECONCILING prevents new included-meter recovery and pack purchase.

### Free

25. later same-plan Free cycle closes old period and opens one successor;
26. successor Free period has `planKindSnapshot=FREE` and `includedRecoveryCreditsGranted=null`;
27. no Free included-credit period counter is created;
28. lifetime Free quantities are unchanged across rollover;
29. purchased lifetime credits are unchanged;
30. Free DRAINING blocks pack purchase but permits remaining lifetime-Free recovery admission;
31. Free RECONCILING blocks pack purchase but does not mark lifetime Free entitlement expired;
32. Free old-period unreported pack event enters NEEDS_ATTENTION;
33. Free pack-enabled successor schedules next pre-close job;
34. Free rollover sends no capacity-resume hint solely for cycle change;
35. startup/repair reconstructs a missing Free pack-cycle job.

## Non-goals

Do not implement:

- different-plan transition (BACKGROUND-010 owns it);
- effective cancellation/no-contract transition owned by BACKGROUND-012;
- merchant plan-change UI;
- top-up refunds;
- promotional-credit model;
- Admin UI;
- another queue/deployable worker.

## Validation

Inspect `package.json`; run focused unit/integration tests, declared repository test/build/Prisma validation as applicable, and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-004 one-OPEN-period ownership is unavailable;
- provider cannot expose exact current cycle;
- billable UsageEvents cannot be scoped to BillingPeriod;
- correct transition requires network I/O inside DB transaction;
- Free pack billing cannot be distinguished from Free lifetime entitlement;
- an implementation would need to create/reset a Free period included-credit counter.

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


## Final frozen-cycle interaction

Canonical rollover MUST NOT close/grant a period merely because wall-clock `periodEnd` passes while the Subscription is FROZEN. BACKGROUND-012 owns the frozen retry.

When unfreeze later proves the same mapped plan in a later Shopify currentBillingCycle, this rollover implementation MUST support direct catch-up from the preserved old period to the exact provider current cycle without fabricating intermediate monthly periods. Paid grants the provider current cycle allowance once; Free rotates provider billing scope only.
