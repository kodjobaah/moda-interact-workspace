---
id: ARCH-010-BACKGROUND-016
architecture_id: ARCH-010
title: Reconcile Shopify subscription freeze and unfreeze without losing entitlement history
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 59
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-010
- ARCH-010-BACKGROUND-015
- ARCH-010-SHARED-008
enables:
- ARCH-010-BACKGROUND-017
- ARCH-010-BACKGROUND-018
- ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-016: Reconcile Shopify subscription freeze and unfreeze without losing entitlement history

## Objective

Teach the canonical `billing-subscription-reconcile` runtime to persist `FROZEN`, retry frozen subscriptions durably, and restore execution only after Shopify provides a usable live subscription again.

Freeze is temporary provider state. Do not model it as cancellation, uninstall or credit exhaustion.

## Inspect before editing

```text
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/workers/billing-worker.ts
existing billing-subscription-reconcile queue consumer/repair logic
canonical BACKGROUND-007 period rollover helper
canonical BACKGROUND-010 plan-change transition helper
Prisma Subscription/BillingPeriod/counter models
relevant unit/integration tests
```

## Canonical provider input

Use `BACKGROUND-015`'s reconciliation snapshot. Do not make a separate historical-event request in the service.

Before using a returned lifecycle event, compare it with persisted `lastProviderLifecycleEventAt`/ID. Never regress durable lifecycle evidence to an older event.

## Classification order

For a shop with a previously verified contract, classify in this order:

### 1. Effective lifecycle event = FROZEN

Transition/preserve local state as FROZEN even if `activeSubscription` is temporarily non-null.

Within one transaction:

```text
Subscription.status = FROZEN
preserve planId
preserve observedShopifyPlanHandle
preserve providerSubscriptionId
preserve current BillingPeriod pointer and its OPEN/CLOSED state
preserve currentPeriodStart/currentPeriodEnd snapshots
preserve pendingPlanId/pendingShopifyPlanHandle/pendingEffectiveAt
preserve cancelAtPeriodEnd unless newer live provider truth proves a value
persist latest provider lifecycle state/id/time
lastSyncedAt = now
clear lifecycle-specific sync error if provider snapshot is complete
nextReconcileAt = now + 1 hour
```

Do not touch any entitlement quantity.

### 2. Local status FROZEN + effective lifecycle event UNFROZEN, but activeSubscription = null

Remain FROZEN. Persist the newer UNFROZEN evidence, set a bounded sync error such as `UNFROZEN_LIVE_CONTRACT_PENDING`, set `nextReconcileAt = now + 1 hour`, and retry.

Historical unfreeze alone is not permission to restore execution.

### 3. Local status FROZEN + usable activeSubscription exists + lifecycle is no longer effectively FROZEN

Restore using provider truth:

#### Same mapped plan + exact same provider cycle

- update provider fields from live snapshot;
- set ACTIVE or TRIALING according to canonical provider rules;
- preserve BillingPeriod and all counters exactly;
- restore normal pre-close/boundary `nextReconcileAt` scheduling;
- persist latest lifecycle evidence;
- do not grant/reset credits.

#### Same mapped plan + provider current cycle is later than preserved local cycle

Delegate to canonical BACKGROUND-007 rollover.

Required catch-up semantics:

```text
old preserved period
   -> close once using normal same-plan rollover rules
provider current cycle
   -> create/reuse exactly one current period
```

Do NOT fabricate intermediate monthly BillingPeriods or grant allowances for cycles that elapsed while the subscription was frozen.

For Paid, grant only the current provider cycle's included allowance exactly once.
For Free, rotate provider/App-Event billing scope only and never reset shop-lifetime Free credits.

#### Effective mapped plan differs

Delegate to BACKGROUND-010. Do not invent proration or overlap periods. Purchased/lifetime Free balances survive.

#### Unmapped/invalid provider plan

Use existing UNMAPPED/configuration fail-closed path. Do not restore business execution.

### 4. activeSubscription = null + lifecycle CANCELED

This task does not finalize cancellation. Delegate/allow BACKGROUND-012 to own effective cancellation.

### 5. activeSubscription = null + lifecycle is CREATED / UPDATED / CANCELLATION_SCHEDULED / UNFROZEN / null for an established contract

Do not invent NO_CONTRACT.

Move to the existing fail-closed provider-sync state (`SYNC_ERROR` or the final accepted equivalent), preserve entitlement/counters/period/plan identity, set a precise `lastSyncErrorCode`, set `nextReconcileAt` for a short retry, and block business execution until the ambiguity resolves.

Do not close the BillingPeriod.

### 6. Provider transport/GraphQL failure

- if already FROZEN, remain FROZEN;
- otherwise preserve the existing last-known projection per ARCH-010 transport-failure rules;
- record error metadata;
- retry through the same queue;
- never restore execution from an error.

## Frozen retry schedule

Use one constant local to the billing reconciliation runtime unless an accepted shared scheduling policy already exists:

```text
FROZEN_RECONCILE_INTERVAL = 1 hour
```

Each confirmed still-frozen result advances `nextReconcileAt` by one hour and enqueues the deterministic delayed `billing-subscription-reconcile` job.

Do not create a new queue/job schema.

## Startup / Redis repair

Amend the existing repair selector so this row is actionable:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

Recreate a missing delayed job at `max(now, nextReconcileAt)` with the existing deterministic job identity. Repeated repair runs must not duplicate effective work.

## BillingPeriod and entitlement rules

While FROZEN:

- do not close the current provider BillingPeriod solely because wall-clock `periodEnd` passed;
- do not forfeit paid included credits;
- do not create a successor period;
- do not reset lifetime Free credits;
- do not mutate purchased-credit balances;
- do not activate pending top-up purchases without provider confirmation;
- do not apply a pending plan change merely because its old `pendingEffectiveAt` passed.

All effective provider transitions are resolved on unfreeze from the live current provider state.

## Pending billing events / top-ups

If a billable UsageEvent or top-up purchase was committed before the freeze:

- keep its original timestamp/idempotency identity;
- do not create a replacement event while frozen;
- if unfreeze occurs in the same provider cycle, normal publication/reconciliation may resume;
- if the provider cycle advanced and Shopify can no longer bill the old timestamp, use the existing `PERIOD_CLOSED`/attention path; do not retimestamp into the new cycle;
- pending top-up credits remain non-spendable until provider confirmation.

## Capacity-resume integration

After successful unfreeze and only after local Subscription is executable again, publish/use the existing best-effort capacity-resume hint from BACKGROUND-009 for recoveries that were already blocked for capacity before the freeze. Do not recreate business jobs that were intentionally dropped because the subscription itself was frozen.

## Required tests

At minimum prove:

1. FROZEN event sets local status FROZEN and preserves plan/period/counters;
2. FROZEN does not close/forfeit/grant BillingPeriod capacity;
3. FROZEN schedules one-hour reconciliation;
4. repeated FROZEN is idempotent;
5. older lifecycle event never overwrites newer persisted evidence;
6. UNFROZEN + null live contract remains fail-closed;
7. UNFROZEN + same plan/same cycle restores ACTIVE without credit reset;
8. unfreeze to later same-plan cycle delegates to BACKGROUND-007 and creates no intermediate periods;
9. unfreeze to later Paid cycle grants current allowance once only;
10. unfreeze Free later cycle never resets lifetime Free credits;
11. effective changed plan delegates to BACKGROUND-010;
12. null + CANCELED is not converted by this task and is available to BACKGROUND-012;
13. null + FROZEN never becomes NO_CONTRACT;
14. null + ambiguous lifecycle does not become NO_CONTRACT;
15. provider failure while FROZEN keeps FROZEN;
16. startup repair recreates missing frozen delayed job;
17. repair is idempotent;
18. pre-freeze pending top-up remains non-spendable;
19. old-cycle UsageEvent is never retimestamped into a new cycle;
20. successful unfreeze restores normal reconciliation scheduling.

## Non-goals

No merchant UI, no new queue, no new plan-pricing mechanism, no cancellation mutation, no deterministic shop-reidentification work and no Admin feature.

## Stop conditions

STOP if BACKGROUND-015 cannot provide both live and lifecycle evidence under the installed Partner API version.

STOP if canonical BACKGROUND-007/010 helpers cannot be reused without changing their accepted architectural invariants; return the required helper change to `moda_architect` instead of duplicating rollover/plan-change code.

## Completion Report

### Status
Not started.


## Final promotional balance across freeze

Freeze/unfreeze preserves the promotional counter and grant history exactly. FROZEN blocks promotional consumption even when remaining > 0. On verified unfreeze, the same balance becomes available again under the normal capacity order; do not grant or reset it as part of restoration.
