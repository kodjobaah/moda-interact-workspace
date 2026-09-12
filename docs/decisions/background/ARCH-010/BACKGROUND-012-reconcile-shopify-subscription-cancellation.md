---
id: ARCH-010-BACKGROUND-012
architecture_id: ARCH-010
title: Reconcile Shopify cancellation, freeze and unfreeze lifecycle state
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 58
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-013
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-010
  - ARCH-010-SHARED-008
  - ARCH-010-BACKGROUND-015
enables:
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-018
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-BACKGROUND-012: Reconcile Shopify cancellation, freeze and unfreeze lifecycle state

## Consolidation

This task is the active owner of the work previously split between `ARCH-010-BACKGROUND-012` and `ARCH-010-BACKGROUND-016`.

`ARCH-010-BACKGROUND-016` is superseded and MUST NOT be implemented separately.

The reason for the merge is structural: both behaviours run inside the same `billing-subscription-reconcile` state machine, consume the same `BACKGROUND-015` provider snapshot, use the same durable scheduling fields, and must classify cancellation/freeze/unfreeze in one deterministic order to avoid contradictory writes.

## Objective

Extend the canonical `billing-subscription-reconcile` runtime so one reconciliation attempt deterministically converges an established merchant subscription across:

- scheduled Shopify cancellation;
- effective Shopify cancellation;
- Shopify FROZEN;
- Shopify UNFROZEN/restoration;
- ordinary active/trialing current state;
- pending/effective plan changes delegated to `BACKGROUND-010`;
- same-plan billing-cycle rollover delegated to `BACKGROUND-007`;
- provider ambiguity/transport failure without inventing provider truth.

Shopify is subscription lifecycle authority. Moda observes and reconciles. Moda MUST NOT create or execute a local subscription-cancellation workflow.

## Inspect before editing

Inspect these exact current files first:

```text
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/runtime/billing-scheduler.ts
src/workers/billing-subscription-reconciliation.worker.ts
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/services/recovery-credit-purchase.service.ts
src/services/shopify-usage-event-publisher.service.ts
```

Inspect these tests before adding coverage:

```text
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
tests/unit/runtime/billing-scheduler.test.ts
tests/unit/services/recovery-credit-purchase.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
```

Read the accepted/current task contracts before coding:

```text
ARCH-010-BACKGROUND-007
ARCH-010-BACKGROUND-010
ARCH-010-BACKGROUND-015
ARCH-010-DATABASE-013
ARCH-010-SHARED-008
```

Do not infer schema or queue names from chat history. Use the published Shared contract and generated Prisma client present in the repository.

## Hard first-production removals

Before implementing lifecycle reconciliation, search Background source/tests for any pre-production local cancellation executor or compatibility branch equivalent to:

```text
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
appSubscriptionCancel
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
```

If found, remove it in this task. Do not retain it behind a flag or adapter. If absent, record the negative search in the Completion Report.

## Canonical input

Use the single snapshot produced by `BACKGROUND-015` for a reconciliation attempt. It contains live Partner `activeSubscription` evidence plus the latest usable provider lifecycle event/evidence.

Do not make a second historical-events request from this state machine.

Before using a lifecycle event, compare it with persisted lifecycle event time/identity. Older provider evidence MUST NOT overwrite newer persisted evidence.

## Mandatory classification order

Evaluate in the following order. Do not reorder these branches.

### 0. Provider snapshot/transport failure

A transport, GraphQL, throttle, malformed-response or lifecycle-history failure proves no lifecycle transition.

Required behaviour:

```text
preserve current plan identity
preserve current BillingPeriod and counters
preserve pending plan intent
preserve cancellation/freeze state already known
record bounded sync error metadata
set/reuse deterministic next reconciliation time
retry through billing-subscription-reconcile
```

Never write `NO_CONTRACT`, restore FROZEN to ACTIVE, close a BillingPeriod, grant capacity or apply a pending plan because of an error.

### 1. Effective latest lifecycle = FROZEN

FROZEN wins even if a live `activeSubscription` object is temporarily present.

Within one replay-safe transaction:

```text
Subscription.status = FROZEN
preserve planId
preserve observedShopifyPlanHandle
preserve providerSubscriptionId
preserve current BillingPeriod pointer/state
preserve currentPeriodStart/currentPeriodEnd
preserve pendingShopifyPlanHandle/pendingPlanId/pendingEffectiveAt
preserve cancelAtPeriodEnd unless newer live provider truth proves a value
persist latest provider lifecycle id/time/state
lastSyncedAt = now
clear only lifecycle-specific sync error proven resolved by the complete snapshot
nextReconcileAt = now + FROZEN_RECONCILE_INTERVAL
```

Use `FROZEN_RECONCILE_INTERVAL = 1 hour` unless the integrated accepted code already exposes the canonical equivalent.

Do not mutate any included, purchased, lifetime-Free or campaign-linked promotional quantity.

### 2. Local FROZEN + latest lifecycle UNFROZEN + live activeSubscription = null

Remain `FROZEN`.

Persist the newer UNFROZEN evidence, record a precise bounded error equivalent to `UNFROZEN_LIVE_CONTRACT_PENDING`, set `nextReconcileAt = now + 1 hour`, and retry.

Historical UNFROZEN evidence alone never restores execution.

### 3. Usable live activeSubscription exists

First classify provider pending plan state.

#### 3A. `pendingUpdate` exists

This is plan-change ownership, not effective full cancellation.

- persist exact current provider state;
- persist pending provider handle/effective boundary;
- map `pendingPlanId` only when an active local BillingPlan mapping exists;
- preserve current period entitlement until the transition is effective;
- delegate effective transition semantics to `BACKGROUND-010`;
- do not close a period as `CONTRACT_ENDED`;
- do not write `NO_CONTRACT`;
- do not treat `cancelAtEndOfCycle=true` on the outgoing subscription as full cancellation when a pending update exists.

#### 3B. No pendingUpdate + `cancelAtEndOfCycle=true`

This is scheduled full cancellation.

Required projection:

```text
current plan/status/period = preserved from verified live contract
cancelAtPeriodEnd = true
pendingShopifyPlanHandle = null
pendingPlanId = null
pendingEffectiveAt = null
currentPeriodEnd = exact provider cycle end
nextReconcileAt = canonical pre-close/boundary schedule
```

Current entitlement remains usable through the current provider cycle.

New top-up purchase is not permitted while full cancellation is scheduled; existing purchased credits, lifetime-Free credits and usable selected promotion remain spendable until effective contract end according to normal recovery-capacity order.

#### 3C. No pendingUpdate + `cancelAtEndOfCycle=false`

Clear a previously scheduled cancellation if present.

If local status was FROZEN and lifecycle is no longer effectively FROZEN, restore using live provider truth:

- same mapped plan + same exact provider cycle -> set ACTIVE/TRIALING, preserve period/counters exactly and restore normal scheduling;
- same mapped plan + later provider cycle -> delegate to `BACKGROUND-007`; create/reuse only the current provider cycle and do not fabricate missed intermediate periods;
- mapped plan differs -> delegate to `BACKGROUND-010`;
- unmapped/invalid plan -> use existing fail-closed UNMAPPED/configuration path; do not restore executable business state.

For Paid catch-up after freeze, grant only the currently verified provider cycle's included allowance exactly once. For Free, rotate provider/App-Event cycle scope only and never reset `LIFETIME_FREE_RECOVERY_CREDITS`.

### 4. live activeSubscription = null + latest effective lifecycle = CANCELED

For a shop with an established current local contract, this is effective cancellation proof.

Execute one serializable/replay-safe transition.

#### 4A. Finalize current BillingPeriod

If an OPEN current BillingPeriod exists:

- release outstanding period-scoped included reservations using canonical period-close rules;
- Paid: set `forfeitedQuantity = granted - committed` after reservation release, subject to DATABASE-013 constraints;
- Free: do not touch the shop-lifetime Free counter;
- set `status=CLOSED`;
- set `closedAt=now`;
- set `closeReason=CONTRACT_ENDED`.

Do not create a successor BillingPeriod.

#### 4B. Transition Subscription to NO_CONTRACT

Using actual DATABASE-013 field names:

```text
planId = null
observedShopifyPlanHandle = null
status = NO_CONTRACT
billingPeriod/current period pointer = null
currentPeriodStart = null
currentPeriodEnd = null
trialEndsAt = null
cancelAtPeriodEnd = false
providerSubscriptionId = null
pendingShopifyPlanHandle = null
pendingPlanId = null
pendingEffectiveAt = null
nextReconcileAt = null
lastSyncedAt = now
lastSyncErrorCode = null
lastSyncErrorAt = null
```

Persist the CANCELED lifecycle evidence.

Do not set `Shop.status=UNINSTALLED`. Do not reset `ShopSettings.onboardingCompleted` for an already-onboarded merchant.

#### 4C. Preserve lifetime state

Do not delete, refund, reset or convert:

```text
LIFETIME_FREE_RECOVERY_CREDITS
purchased-credit lots/counters/refund history
campaign-linked PromotionalCreditGrant history
merchant promotion selection/history
existing merchant/recovery/conversation history
```

They become non-spendable because `BACKGROUND-013` denies execution while `NO_CONTRACT`.

### 5. live activeSubscription = null + latest lifecycle = FROZEN

Write/preserve `FROZEN` according to branch 1. Never interpret this as cancellation.

### 6. live activeSubscription = null + latest lifecycle = UNFROZEN/CREATED/UPDATED/CANCELLATION_SCHEDULED/unknown/null for an established contract

Provider truth is unresolved.

- if already FROZEN, remain FROZEN;
- otherwise preserve last-known plan/period/entitlement evidence and use the existing fail-closed sync state/error representation;
- do not write `NO_CONTRACT`;
- do not close a BillingPeriod;
- schedule a bounded retry.

For a genuinely fresh `NO_CONTRACT` merchant with no established contract, leave initial activation ownership to `BACKGROUND-001`/SHOPIFY activation flow; do not manufacture cancellation history.

## Frozen retry and startup repair

The existing durable scheduler/repair path must treat:

```text
Subscription.status = FROZEN
AND nextReconcileAt IS NOT NULL
```

as actionable. Recreate a missing deterministic delayed reconciliation job at `max(now, nextReconcileAt)`. Repeated repair must be idempotent.

Do not create a second queue/job schema.

## Pending pre-freeze billing work

For UsageEvent/top-up work durably committed before freeze:

- preserve original occurrence timestamp/idempotency identity;
- never retimestamp into a later provider cycle;
- if unfreeze returns to the same provider cycle, existing publication/reconciliation may continue;
- if the provider cycle advanced and the event is no longer billable, use the existing `PERIOD_CLOSED`/needs-attention path;
- pending top-up credits remain non-spendable until provider confirmation.

## Performance boundary

This task is lifecycle reconciliation, not the 22,000-webhook/minute checkout-event hot path.

Do not add subscription/lifecycle API calls or database reads to Shopify HTTP webhook ingress. `BACKGROUND-018` owns the separate early gate for queued checkout/cart/order events.

## Required tests

Prove all of the following with focused service/worker tests against real task-owned methods:

1. provider transport/history failure preserves state and schedules retry;
2. FROZEN evidence writes FROZEN while preserving plan/period/all capacity quantities;
3. repeated FROZEN is idempotent and advances one deterministic hourly retry;
4. older lifecycle evidence cannot overwrite newer evidence;
5. UNFROZEN + null live contract remains FROZEN/fail-closed;
6. FROZEN -> same plan/same cycle restores ACTIVE/TRIALING without grant/reset;
7. FROZEN -> later same-plan cycle delegates to BACKGROUND-007 and creates no intermediate periods;
8. Paid later-cycle restoration grants only current verified period once;
9. Free later-cycle restoration never resets lifetime Free;
10. effective changed plan delegates to BACKGROUND-010;
11. pendingUpdate takes precedence over cancellation interpretation;
12. scheduled full cancellation preserves current entitlement until exact boundary;
13. reversal of scheduled cancellation clears `cancelAtPeriodEnd` without granting anything;
14. provider null + CANCELED closes exactly one current period with CONTRACT_ENDED and writes NO_CONTRACT;
15. effective cancellation replay is idempotent;
16. provider null + FROZEN never writes NO_CONTRACT;
17. provider null + ambiguous lifecycle never writes NO_CONTRACT or closes period;
18. established cancellation preserves purchased/lifetime/promotion histories;
19. startup repair recreates a missing frozen reconciliation job exactly once effectively;
20. pre-freeze pending top-up remains non-spendable while frozen;
21. old-cycle UsageEvent is never retimestamped;
22. no `appSubscriptionCancel`/local cancellation executor remains;
23. no new queue schema is introduced;
24. no Shopify HTTP ingress lifecycle lookup is introduced.

## Non-goals

Do not implement merchant UI, new queue contracts, Admin cancellation/refund workflows, plan pricing, recovery-capacity reservation algorithms, raw checkout-event filtering, or deterministic shop re-identification.

## Validation

Inspect `package.json` and run the repository-declared focused tests covering the changed services/workers, then the declared unit/full test command, typecheck/build where present, and `git diff --check`. Do not invent scripts.

Record any unchanged repository baseline failure by its existing baseline ID.

## Stop conditions

STOP and return to `moda_architect` if any of these are true:

1. `BACKGROUND-015` cannot provide both live and lifecycle evidence under the installed Partner API contract;
2. `BACKGROUND-007` or `BACKGROUND-010` cannot be reused without changing their accepted invariants;
3. DATABASE-013 fields differ materially from the task contract;
4. the implementation would require a Shopify cancellation mutation;
5. the implementation would require adding lifecycle lookup to HTTP webhook ingress.

Do not solve those conditions by inventing compatibility state.

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
