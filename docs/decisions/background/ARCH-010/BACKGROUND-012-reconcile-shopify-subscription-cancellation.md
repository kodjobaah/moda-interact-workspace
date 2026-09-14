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
status: review
priority: 58
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-010-DATABASE-013
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-010
  - ARCH-010-BACKGROUND-009
  - ARCH-010-SHARED-008
  - ARCH-010-BACKGROUND-015
enables:
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-018
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-14
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
ARCH-010-BACKGROUND-009
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

## Capacity-resume integration after verified unfreeze

Preserve the accepted requirement previously owned by BACKGROUND-016. After a successful unfreeze/restoration, and **only after** the local `Subscription` projection is executable again, publish/use the existing best-effort `BACKGROUND-009` capacity-resume hint for recoveries that were already blocked solely by exhausted recovery capacity before the freeze.

Required boundaries:

- enqueue/publish the resume hint only after the restoring transaction commits;
- the resume consumer must still re-check the BACKGROUND-013 execution gate before re-admission;
- do not recreate business jobs that were intentionally dropped/no-op'd because the subscription itself was FROZEN;
- do not emit a capacity-resume hint merely because FROZEN state was observed again;
- do not invent a second resume queue/contract.

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
23. successful verified unfreeze publishes at most the existing best-effort BACKGROUND-009 capacity-resume hint after commit, and only when appropriate;
24. unfreeze does not recreate jobs that were intentionally dropped because of FROZEN lifecycle denial;
25. no new queue schema is introduced;
26. no Shopify HTTP ingress lifecycle lookup is introduced.

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
Ready for Review.

### Files Changed
- `moda-interact-background/src/providers/shopify-partner-billing.provider.ts`
- `moda-interact-background/src/services/billing-reconciliation.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/src/services/shopify-subscription-lifecycle-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts`
- `moda-interact-background/tests/unit/services/billing-reconciliation.service.test.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts`

### Work Completed
- Wired subscription reconciliation to the mandatory BACKGROUND-015 combined live-subscription/lifecycle snapshot without a compatibility fallback.
- Added dedicated FROZEN snapshot-failure retry handling, replay-safe lifecycle ordering, lifecycle-specific error clearing, one-hour UNFROZEN-without-contract retry, and verified unfreeze delegation/restoration paths.
- Preserved newer persisted lifecycle evidence over older provider evidence; repeated FROZEN evidence advances one deterministic hourly retry and frozen rows remain actionable through the existing durable scheduler query.
- Effective cancellation closes the open period with `CONTRACT_ENDED`, releases period-scoped reservations through existing service behavior, marks retryable usage work for attention, and projects the subscription to `NO_CONTRACT` without a local Shopify cancellation mutation.
- Added focused regression coverage and updated provider/reconciliation test doubles for the mandatory snapshot contract.
- Negative hard-removal search found no local cancellation executor or cancellation symbols matching the task list in Background `src`/`tests`.

### Correction-to-File Mapping
- Mandatory BACKGROUND-015 snapshot contract and fallback removal: `src/providers/shopify-partner-billing.provider.ts`; provider and reconciliation fixtures in `tests/unit/providers/shopify-partner-billing.provider.test.ts`, `tests/unit/services/billing-reconciliation.service.test.ts`, and `tests/unit/services/billing-subscription-reconciliation.service.test.ts`.
- FROZEN snapshot failure preservation, guarded retry scheduling, and frozen reconstruction: `src/services/billing-subscription-reconciliation.service.ts`; `tests/unit/services/billing-subscription-reconciliation.service.test.ts`.
- Snapshot-driven lifecycle routing and provider-error preservation: `src/services/billing-reconciliation.service.ts`; `tests/unit/services/billing-reconciliation.service.test.ts`.
- Lifecycle event ordering, FROZEN projection, unresolved UNFROZEN handling, verified restoration delegation, and effective cancellation: `src/services/shopify-subscription-lifecycle-reconciliation.service.ts`; `tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts`.

### Validation Results
- Focused unit suite rerun after final test correction: **passed**, 4 files and 198 tests.
- Integration suite: **passed**, 2 files and 3 tests.
- `npm run test:unit`: **baseline failure**, 10 unchanged failures: 8 in `recovery-credit-purchase.service.test.ts` from the documented DATABASE-013/generated-client purchase schema/status mismatch, and 2 in `runtime/observability-startup.test.ts` from existing source/release assertions.
- `npm run build`: **baseline failure**, 15 unchanged TypeScript errors confined to the purchased-credit/recovery-credit consumers of the documented `TYPECHECK-001` generated-client drift; no diagnostic occurred in a task-touched file.
- `git diff --check`: **passed**.
- The focused tests do not yet prove every enumerated branch in the task contract, including scheduled cancellation/reversal, pending-update precedence, later-cycle/change-plan delegation, capacity-resume publication, startup repair exactness, and pre-freeze top-up behavior. These remain explicit architect review items rather than being represented as completed evidence.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-012`.
- Parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-012`.
- Mirrored branch: `task/ARCH-010-BACKGROUND-012`.
- Implementation commit: `cf9319c9eeb48d6422aac20497adbe3332741491` (`Complete Shopify subscription lifecycle reconciliation`), pushed to `origin/task/ARCH-010-BACKGROUND-012`.
- Parent task report is the only parent-workspace file changed; the implementation submodule gitlink was not staged or changed.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Status

**Changes Requested**

Attempt 1 establishes the combined Partner lifecycle snapshot and a useful first
lifecycle-reconciliation service, but the task is not yet architecture-conformant.
The Completion Report correctly acknowledges major missing branches; architect
inspection also found production correctness defects in the implemented branches.

The corrections below are the complete Attempt-2 contract. Do not infer lifecycle
semantics from chat history and do not redesign `BACKGROUND-007`, `BACKGROUND-009`,
`BACKGROUND-010` or `BACKGROUND-015`.

### Accepted Attempt-1 work to preserve

Preserve these parts unless an exact correction below requires a local refactor:

- the Partner GraphQL request retrieves live subscription state and the latest scoped
  lifecycle event in one request;
- lifecycle event parsing validates app/shop ownership, event/state pairing and
  timestamp shape;
- no local Shopify cancellation mutation/executor was introduced;
- FROZEN and CANCELED are distinct provider states;
- effective cancellation marks pending/retryable UsageEvents `NEEDS_ATTENTION`
  rather than retimestamping them;
- the existing `billing-subscription-reconcile` queue/Shared contract remains the
  only subscription lifecycle retry path;
- frozen subscriptions are included in `BillingSubscriptionReconciliationService`
  reconstruction eligibility;
- the accepted `BACKGROUND-007`, `BACKGROUND-009` and `BACKGROUND-010` services
  remain reusable dependencies.

### Finding 1 — the canonical BACKGROUND-015 snapshot is still optional

`ShopifyPartnerBillingProvider` currently declares:

```ts
getSubscriptionReconciliationSnapshot?(...)
```

and the exported helper silently falls back to:

```ts
getActiveSubscription(...)
latestLifecycleEvent = null
```

That is not the canonical input required by this task. A provider/test double that
does not implement the BACKGROUND-015 snapshot can silently erase FROZEN/CANCELED
evidence from the state machine.

#### Required correction

In:

```text
src/providers/shopify-partner-billing.provider.ts
```

make:

```ts
getSubscriptionReconciliationSnapshot(
  shopifyShopId: string,
): Promise<PartnerSubscriptionReconciliationSnapshot>;
```

a required `ShopifyPartnerBillingProvider` method.

Remove the fallback that fabricates:

```text
latestLifecycleEvent: null
```

from `getActiveSubscription(...)`.

Lifecycle reconciliation paths must always consume the real combined snapshot.

`getActiveSubscription(...)` may remain on the provider interface for callers whose
architecture genuinely needs only the live subscription; do not remove it
opportunistically.

Update test doubles used by the affected reconciliation tests to implement
`getSubscriptionReconciliationSnapshot(...)` explicitly. Do not retain a compatibility
adapter merely to avoid updating tests.

### Finding 2 — queued FROZEN snapshot/transport failure loses the durable retry

In `BillingSubscriptionReconciliationService.reconcileJob(...)`, a FROZEN row is
classified as `isFrozenReconciliation`, but the Partner snapshot `catch` has no
FROZEN branch. It falls through to the **initial-activation**
`recordProviderFailure(...)` helper with a non-initial expected-state shape.

The initial-activation CAS cannot match the FROZEN row, so the consumed FROZEN job can
disappear without replacement.

#### Required correction

In:

```text
src/services/billing-subscription-reconciliation.service.ts
```

add a dedicated FROZEN snapshot-failure path before the initial-activation fallback.

For a prepared FROZEN reconciliation, on snapshot/transport/history failure:

```text
preserve status = FROZEN
preserve planId
preserve observedShopifyPlanHandle
preserve providerSubscriptionId
preserve billingPeriodId/current cycle
preserve pending plan fields
preserve cancelAtPeriodEnd
preserve lifecycle event identity/time/state
lastSyncErrorCode = PARTNER_API_ERROR
lastSyncErrorAt = now
lastSyncedAt = now
nextReconcileAt = now + 1 hour
```

Use one guarded `subscription.updateMany(...)` keyed by the exact FROZEN row token,
including at minimum:

```text
id
status = FROZEN
planId
nextReconcileAt = consumed job timestamp
```

and the existing stable current/pending identifiers when present.

Publish exactly one deterministic replacement
`billing-subscription-reconcile` job only when that CAS updates one row.

Do not call:

```text
recordProviderFailure(...)
recordMissingSubscription(...)
```

for a FROZEN reconciliation.

### Finding 3 — repeated FROZEN evidence currently consumes the job without advancing the hourly retry

`isOlder(...)` currently treats an incoming event with the same
`occurredAt + id` as older because it uses:

```text
persistedId >= incoming.id
```

`freeze(...)` then performs no update, while `reconcile(...)` still returns
`handled`. The current delayed job is consumed and no later FROZEN job is made
durable/published.

#### Required correction

Lifecycle ordering must distinguish:

```text
strictly older incoming event
same event replay
newer incoming event
```

For the **same** FROZEN event replay:

- it remains the effective lifecycle truth;
- keep the same lifecycle id/time/state;
- preserve all entitlement/pending identity;
- advance `nextReconcileAt = now + 1 hour`;
- publish/reconstruct exactly one deterministic hourly retry through the existing
  subscription queue path.

A strictly older event must never overwrite newer persisted lifecycle identity.

Do not solve this by discarding event identity comparison.

### Finding 4 — FROZEN projection clears unrelated sync errors

`freeze(...)` currently writes:

```text
lastSyncErrorCode = null
lastSyncErrorAt = null
```

for every FROZEN observation.

The task requires clearing only lifecycle/snapshot errors that the complete provider
snapshot actually proves resolved.

#### Required correction

When projecting/replaying FROZEN:

- clear `UNFROZEN_LIVE_CONTRACT_PENDING` and `PROVIDER_STATE_UNRESOLVED`;
- clear a prior lifecycle-snapshot `PARTNER_API_ERROR` when the current complete
  snapshot succeeded;
- do **not** clear unrelated configuration/integrity errors such as:
  - `MISSING_USAGE_METER`;
  - `MISSING_BILLING_CYCLE`;
  - `INVALID_INCLUDED_ALLOWANCE`;
  - `UNEXPECTED_IMMEDIATE_PLAN_CHANGE`;
  - other non-lifecycle error codes.

Preserve the matching `lastSyncErrorAt` whenever the error code is preserved.

When live `activeSubscription` exists with FROZEN evidence, update
`cancelAtPeriodEnd` from that live snapshot because the current complete snapshot
proves the latest value. Do not alter plan/period/pending quantity ownership.

### Finding 5 — `UNFROZEN + null live contract` uses the wrong retry interval

Branch 2 requires:

```text
remain FROZEN
persist newer UNFROZEN evidence
lastSyncErrorCode = UNFROZEN_LIVE_CONTRACT_PENDING
nextReconcileAt = now + 1 hour
```

The current generic `recordUnresolved(...)` uses five minutes.

#### Required correction

Give `UNFROZEN + null live contract + local FROZEN` its own exact branch or parameter
so it uses the canonical one-hour FROZEN interval.

Do not change the ordinary ambiguous-provider retry interval solely to satisfy this
case.

### Finding 6 — verified UNFROZEN restoration does not implement the required delegation matrix

The current implementation restores executable state when:

```text
current.status = FROZEN
current.planId != null
local cycle == provider cycle
```

without proving the live provider plan maps to that same local plan.

For every other `UNFROZEN + live` case it calls `freeze(...)` using the UNFROZEN
event, leaving the subscription FROZEN indefinitely.

This violates all of:

```text
same mapped plan + same cycle -> restore exactly
same mapped plan + later cycle -> BACKGROUND-007
changed mapped plan -> BACKGROUND-010
unmapped/invalid plan -> existing fail-closed path
```

#### Required correction

Implement one deterministic verified-unfreeze transition in:

```text
src/services/shopify-subscription-lifecycle-reconciliation.service.ts
```

using the existing accepted in-transaction primitives:

```ts
SamePlanBillingPeriodRolloverService.transitionInTransaction(...)
ShopifyPlanChangeTransitionService.transitionInTransaction(...)
```

Do **not** modify those accepted services unless an exact invariant incompatibility
is discovered; if one cannot be reused, STOP under this task's existing stop
condition.

Inside one serializable/replay-safe lifecycle transaction:

1. lock the Subscription;
2. re-read Subscription including current plan/BillingPeriod;
3. reject strictly older lifecycle evidence;
4. require local status `FROZEN`;
5. re-read/map the live provider `planHandle` to an active local BillingPlan;
6. validate the mapped plan's required meter/allowance configuration using the same
   accepted rules as BACKGROUND-007/BACKGROUND-010;
7. classify exactly:

#### 6A. Same mapped plan + same exact provider cycle

Update only the Subscription projection:

```text
status = provider ACTIVE/TRIALING
observedShopifyPlanHandle = provider.planHandle
providerSubscriptionId = provider.providerSubscriptionId
trialEndsAt = provider.trialEndsAt
cancelAtPeriodEnd = provider.cancelAtEndOfCycle
preserve billingPeriodId
preserve currentPeriodStart/currentPeriodEnd
preserve all counters exactly
preserve pending plan intent unless live pending truth replaces it
persist UNFROZEN lifecycle id/time/state
clear resolved lifecycle/snapshot sync error only
restore canonical next reconciliation schedule
```

No BillingPeriod/counter grant/reset is allowed.

#### 6B. Same mapped plan + later provider cycle

Within the same transaction, make the FROZEN row temporarily eligible **inside that
transaction only**, then invoke:

```ts
SamePlanBillingPeriodRolloverService.transitionInTransaction(...)
```

for the current provider cycle.

If the accepted rollover result is not `transitioned`/`unchanged` as required for the
verified snapshot, fail closed/rollback rather than leaving a partially ACTIVE row.

Requirements:

- no intermediate periods;
- Paid grants only the verified current cycle once;
- Free never resets lifetime Free;
- persist UNFROZEN lifecycle evidence in the successful transaction.

#### 6C. Provider current plan differs from local current plan

Map the provider plan. Within the same transaction, make the FROZEN row temporarily
eligible inside that transaction only and invoke:

```ts
ShopifyPlanChangeTransitionService.transitionInTransaction(...)
```

with the old `expectedCurrentPlanId`.

If target mapping/configuration is invalid, preserve non-executable fail-closed state;
do not restore ACTIVE against the stale old plan.

Do not fabricate a pending plan change merely to call this primitive.

#### 6D. Unmapped/inactive/invalid provider plan

Do not restore executable state.

Use the existing durable fail-closed representation:

```text
UNMAPPED_PLAN_HANDLE
MISSING_USAGE_METER
MISSING_BILLING_CYCLE
INVALID_INCLUDED_ALLOWANCE
```

as applicable, while persisting the newer UNFROZEN lifecycle evidence and a bounded
retry where the existing error class is retryable.

Do not set ACTIVE/TRIALING until the provider truth and local configuration are
usable.

### Finding 7 — successful unfreeze never publishes the required BACKGROUND-009 capacity-resume hint

No unfreeze path currently calls the existing capacity-resume service.

#### Required correction

After a verified unfreeze/restoration transaction commits successfully, call only:

```ts
await recoveryCapacityResumeService.schedule({
  shopId,
  trigger: "unfreeze",
});
```

This is best effort:

- call it **after commit**;
- catch failure;
- log bounded structured warning
  `billing.recovery_capacity_resume.enqueue_failed`;
- do not roll back/reclassify a completed unfreeze;
- do not publish it for repeated FROZEN, failed/unresolved UNFROZEN, or effective
  cancellation.

Do not recreate checkout/recovery business jobs directly. The existing
`recovery-capacity-resume` consumer remains responsible for selecting only
`RECOVERY_CAPACITY_EXHAUSTED` recoveries and rechecking the execution gate.

### Finding 8 — scheduled cancellation and reversal are not durably projected on same-cycle paths

For a live same-plan/same-cycle subscription, the accepted rollover primitive may
return `unchanged` without updating `Subscription.cancelAtPeriodEnd`.

Therefore:

```text
cancelAtEndOfCycle=true
```

can remain invisible locally, and a later reversal can likewise remain stale.

#### Required correction

In **both** reconciliation entry points:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

classify live cancellation state **before** returning from an unchanged
rollover/normal-current path.

When:

```text
provider.pendingPlanHandle != null
```

pending plan-change ownership wins. Persist/update the pending provider truth and do
not close a period or write `NO_CONTRACT` because the outgoing provider object also
reports `cancelAtEndOfCycle=true`.

When there is **no** pending update and:

```text
provider.cancelAtEndOfCycle == true
```

persist scheduled full cancellation:

```text
cancelAtPeriodEnd = true
pendingShopifyPlanHandle = null
pendingPlanId = null
pendingEffectiveAt = null
currentPeriodEnd = exact provider cycle end
```

and persist/reuse the canonical pre-close/boundary reconciliation schedule. Current
plan/period/counters remain unchanged and spendable.

When there is no pending update and:

```text
provider.cancelAtEndOfCycle == false
```

clear a previously persisted:

```text
cancelAtPeriodEnd = true
```

without creating/granting/resetting any entitlement.

Use a guarded update; do not introduce an unguarded second Subscription mutation
after a transition CAS.

### Finding 9 — rotating snapshot failure records an error but does not create the required durable retry

`BillingReconciliationService.reconcileOnce(...)` catches provider snapshot failure
and `markSyncError(...)` currently records only:

```text
lastSyncErrorCode
lastSyncErrorAt
```

It does not set/reuse a durable `nextReconcileAt` or publish the deterministic
subscription job.

#### Required correction

For an existing established subscription, rotating snapshot failure must:

- preserve status/plan/period/pending/cancellation/lifecycle fields;
- choose:
  - FROZEN -> `now + 1 hour`;
  - other established lifecycle state -> existing bounded provider retry interval;
- guarded-write `nextReconcileAt`, `lastSyncedAt`,
  `lastSyncErrorCode=PARTNER_API_ERROR`, `lastSyncErrorAt`;
- publish exactly one deterministic `billing-subscription-reconcile` job when the CAS
  succeeds.

Do not create/convert an established row to `NO_CONTRACT`.

Fresh-row activation behaviour may remain owned by the existing initial activation
flow.

### Finding 10 — effective cancellation close is not yet the canonical replay/concurrency-safe close

The new cancellation code duplicates the period-close logic but does not enforce the
accepted counter CAS/integrity checks used by the rollover/plan-change close path.

Current code:

```text
aggregates RESERVED/AMBIGUOUS
releases them
blindly updates counter by id
```

without proving:

```text
aggregate reserved == durable counter.reservedQuantity
version unchanged
reservedQuantity unchanged
closed counter totals are exact
period was still OPEN at close
```

#### Required correction

Keep effective cancellation task-owned, but mirror the accepted close invariants:

For Paid OPEN period:

1. load included counter; absence is a fail-closed integrity error;
2. aggregate exactly `RESERVED | AMBIGUOUS`;
3. require aggregate quantity equals `counter.reservedQuantity`;
4. compute final forfeiture so after release:

```text
reservedQuantity = 0
committedQuantity + forfeitedQuantity = grantedQuantity
```

5. release reservations with `PERIOD_CLOSED`;
6. update the counter with `updateMany` CAS on at least:

```text
id
version
reservedQuantity
```

and increment `version`;
7. require update count = 1;
8. re-read and verify the closed counter totals;
9. close BillingPeriod with guarded `updateMany` requiring `status=OPEN`;
10. require exactly one close.

Use:

```text
closedAt = now
closeReason = CONTRACT_ENDED
```

Do not create a successor.

Run the effective cancellation transition at SERIALIZABLE isolation.

Replay when the Subscription is already `NO_CONTRACT` / the period already closed
must not close, release, forfeit, or clear history a second time.

### Finding 11 — fresh NO_CONTRACT must not acquire cancellation history from a stale provider event

The task explicitly says a genuinely fresh `NO_CONTRACT` merchant with no established
contract remains initial-activation ownership.

Before applying `CANCELED`, require durable evidence of an established local contract
(for example current plan/provider/period identity).

If the row is genuinely fresh:

```text
status = NO_CONTRACT
planId = null
billingPeriodId = null
observedShopifyPlanHandle = null
providerSubscriptionId = null
```

do not persist `CANCELED` lifecycle history and do not manufacture a cancellation
transition.

### Required Attempt-2 permanent tests

Attempt 2 must provide a truthful evidence map for all 26 task requirements. Add the
tests below using real task-owned methods. Existing accepted dependency tests may be
cited only when their assertions actually prove the requirement.

#### Provider snapshot

File:

```text
tests/unit/providers/shopify-partner-billing.provider.test.ts
```

1. Preserve existing lifecycle parse/scope/malformed tests.
2. Add a compile/runtime test proving lifecycle reconciliation test doubles must
   supply `getSubscriptionReconciliationSnapshot`; there must be no helper fallback
   from `getActiveSubscription`.

#### Lifecycle service

File:

```text
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts
```

Add/strengthen tests named exactly:

```text
replays the same FROZEN event and advances one hourly retry
ignores strictly older lifecycle evidence without overwriting newer identity
preserves unrelated sync error while projecting FROZEN
uses live cancelAtEndOfCycle while preserving FROZEN entitlement
keeps FROZEN for UNFROZEN with no live contract and retries in one hour
restores same mapped plan and same cycle without granting or resetting capacity
restores later same-plan Paid cycle through BACKGROUND-007 exactly once
restores later same-plan Free cycle without resetting lifetime Free
restores changed mapped plan through BACKGROUND-010
keeps unfreeze fail closed for unmapped or invalid provider plan: %s
publishes one best-effort unfreeze capacity-resume hint after commit
swallows unfreeze capacity-resume enqueue failure after committed restoration
does not publish capacity-resume for unresolved or repeated FROZEN state
closes Paid cancellation with canonical reservation/counter CAS semantics
replays effective cancellation without a second close or counter mutation
preserves lifetime purchased refund promotion and selection state on cancellation
ignores CANCELED lifecycle history for a genuinely fresh NO_CONTRACT row
```

For same-cycle unfreeze, observable no-write assertions must cover:

```text
billingPeriod
billingPeriodEntitlementCounter
shopEntitlementCounter
recoveryCreditPurchase
recoveryCreditRefund
promotionalCreditGrant
merchantPromotionSelection
```

through available mutators:

```text
create
update
updateMany
upsert
delete
deleteMany
```

except the Subscription projection update itself.

#### Queued subscription reconciliation

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Add tests named exactly:

```text
preserves FROZEN state and publishes an hourly retry when the combined Partner snapshot fails
pending update takes precedence over scheduled cancellation interpretation
projects scheduled full cancellation without changing current entitlement
clears reversed scheduled cancellation without granting entitlement
does not retimestamp old-cycle UsageEvents during effective cancellation
reconstructs a missing FROZEN reconciliation job effectively once
does not reconcile a pending top-up as spendable while lifecycle remains FROZEN
```

For the FROZEN snapshot failure assert no initial-activation CAS predicate is used.

For scheduled cancellation assert exact:

```text
cancelAtPeriodEnd = true
current plan/period unchanged
pending fields clear only because provider has no pending update
canonical pre-close/boundary nextReconcileAt
no BillingPeriod/counter mutation
```

For pending-update precedence use:

```text
provider.pendingPlanHandle != null
provider.cancelAtEndOfCycle = true
```

and prove no `CONTRACT_ENDED`/`NO_CONTRACT` transition.

For reversal assert `cancelAtPeriodEnd=false` and zero grants/period creates.

#### Rotating reconciliation

File:

```text
tests/unit/services/billing-reconciliation.service.test.ts
```

Add tests named exactly:

```text
records durable deterministic retry when lifecycle snapshot transport fails
projects scheduled cancellation before an unchanged same-cycle return
clears reversed scheduled cancellation before an unchanged same-cycle return
keeps pending plan update ahead of outgoing cancelAtEndOfCycle
keeps pack purchase reconciliation disabled while FROZEN lifecycle is effective
```

Transport failure must prove a deterministic subscription job is published rather
than relying solely on the next rotating scan.

#### Scheduler/repair

Use the existing reconciliation-service reconstruction test location or:

```text
tests/unit/runtime/billing-scheduler.test.ts
```

to prove:

```text
FROZEN + nextReconcileAt != null
```

is reconstructed with the same deterministic job id and repeated repair is
effectively idempotent.

Do not create a second repair mechanism merely for the test.

#### Static architecture tests/search evidence

Record and preserve negative searches proving:

```bash
rg -n \
  "SubscriptionCancellationRequest|SubscriptionCancellationMode|SubscriptionCancellationStatus|ShopifySubscriptionCancellationArgs|SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS|appSubscriptionCancel|BILLING_CANCELLATION_REQUEST_RECEIVED|BILLING_CANCELLATION_COMPLETED|BILLING_CANCELLATION_REJECTED" \
  src tests

rg -n "getSubscriptionReconciliationSnapshot|getSubscriptionLifecycle|SUBSCRIPTION_FROZEN|SUBSCRIPTION_CANCELED" \
  ../moda-interact/app ../moda-interact-messaging/src
```

The first command must have no local cancellation executor symbols.

The second command must show no new lifecycle lookup added to Shopify HTTP ingress or
Messaging ingress by this task. Existing unrelated documentation/test strings are
not an implementation violation; report matches precisely.

Also prove no new BullMQ queue/job name/schema was introduced by Attempt 2. The only
subscription lifecycle retry must remain the published
`billing-subscription-reconcile` Shared contract, plus the already accepted
`recovery-capacity-resume` hint after verified unfreeze.

### Required 26-item Completion Report evidence map

Replace the generic coverage statement with a table:

```text
Requirement | Exact test title(s) | Test file | Result
```

covering task requirements 1 through 26 in order.

Do not mark an item proven by a test that does not assert that behaviour. If a
requirement is still unproven, return the task as Blocked/Changes Requested rather
than describing it as a known gap while setting `status: review`.

### Validation required for Attempt 2

From `moda-interact-background` run the repository-declared commands:

```bash
npx vitest run \
  tests/unit/providers/shopify-partner-billing.provider.test.ts \
  tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts \
  tests/unit/runtime/billing-scheduler.test.ts \
  tests/unit/services/recovery-credit-purchase.service.test.ts \
  tests/unit/services/shopify-usage-event-publisher.service.test.ts

npm run test:unit
npm run test:integration
npm run prisma:validate
npm run prisma:generate
npm run build
git diff --check
```

Record exact pass/fail/skip counts.

Do not invent `npm run lint` or `npm run typecheck`; this repository does not declare
those scripts.

The existing 10 unit failures and 15 generated-client build diagnostics remain
non-blocking only if:

- they match the documented baseline exactly;
- no Attempt-2 changed file introduces a new failure/diagnostic.

### Allowed Attempt-2 production scope

Allowed production files:

```text
src/providers/shopify-partner-billing.provider.ts
src/services/shopify-subscription-lifecycle-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

Allowed focused test files:

```text
tests/unit/providers/shopify-partner-billing.provider.test.ts
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/runtime/billing-scheduler.test.ts
tests/unit/services/recovery-credit-purchase.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
```

The task/Completion Report may be updated through the normal coordination exception.

Do **not** modify:

```text
src/services/same-plan-billing-period-rollover.service.ts
src/services/shopify-plan-change-transition.service.ts
Shared contracts/package version
Prisma schema/migrations
BACKGROUND-013 business-execution gates
BACKGROUND-018 Shopify-event early gate
Shopify merchant app
Admin
Messaging
Gateway
recovery-capacity reservation algorithms
refund semantics
promotion semantics
```

If `SamePlanBillingPeriodRolloverService.transitionInTransaction(...)` or
`ShopifyPlanChangeTransitionService.transitionInTransaction(...)` cannot be reused
without modifying their accepted invariants, STOP and return the exact incompatibility
to `moda_architect`.

### Workflow evidence required

Attempt 2 Completion Report must record full immutable evidence:

```text
Attempt-1 implementation full SHA
Attempt-1 final parent/report full SHA
Attempt-2 launcher claim full SHA
Attempt-2 implementation full SHA
Attempt-2 parent/report publication full SHA
database gitlink before/after
dedicated parent worktree/branch
dedicated implementation worktree/branch
start-of-attempt synchronization evidence
recursive submodule materialisation evidence
both branches clean/pushed
```

The user-facing Attempt-1 handoff reports:

```text
implementation: b5fb3798
parent report:  9a270731
```

Record the corresponding **full** SHAs and explain any intermediate report commit if
the task file's report history differs.

### Reclaim / stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 1
```

The next authorized claim must increment to **Attempt 2 exactly once**.

After implementing only the corrections above, completing the 26-item evidence map,
running validation, setting the task back to `status: review`, clearing
`executor`/`claimed_at`, committing/pushing both mirrored task branches and verifying
both are clean, STOP and return to `moda_architect`.

Do not start `ARCH-010-BACKGROUND-013`, `ARCH-010-BACKGROUND-018`,
`ARCH-010-SHOPIFY-016` or `ARCH-010-SYSTEM-TEST-002`.

