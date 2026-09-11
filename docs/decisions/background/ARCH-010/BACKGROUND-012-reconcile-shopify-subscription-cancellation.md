---
id: ARCH-010-BACKGROUND-012
architecture_id: ARCH-010
title: Reconcile Shopify subscription cancellation and close the final provider billing period
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
  - ARCH-010-DATABASE-004
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-010
  - ARCH-010-SHARED-002
  - ARCH-010-BACKGROUND-015
enables:
  - ARCH-010-BACKGROUND-013
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-012: Reconcile Shopify subscription cancellation and close the final provider billing period

## Objective

Extend the canonical Shopify App Pricing reconciliation runtime so a merchant-initiated Shopify cancellation is reflected in Moda exactly once without calling any Shopify cancellation mutation.

Shopify is cancellation authority. Moda only observes and reconciles provider state.

## Product invariants

1. Moda MUST NOT call `appSubscriptionCancel` for ARCH-010 cancellation.
2. Moda MUST NOT create a local human-approval cancellation workflow.
3. `activeSubscription.cancelAtEndOfCycle=true` does not end current entitlement early.
4. A mapped `pendingUpdate` takes precedence over full-cancellation interpretation. Paid -> Free and other plan changes remain BACKGROUND-010 plan-change transitions.
5. Full cancellation scheduled means:

```text
provider activeSubscription exists
cancelAtEndOfCycle = true
pending mapped/unmapped plan update = null
```

6. While that current provider contract remains active, current recovery entitlement remains usable through the current provider cycle.
7. New top-up purchases are disabled once full cancellation is scheduled; existing purchased credits and lifetime Free credits remain spendable until the contract actually ends.
8. Effective full cancellation does not delete or refund purchased credits and does not reset lifetime Free usage.
9. Paid monthly included credits do not survive effective full cancellation.
10. `Shop.status` remains ACTIVE while the app remains installed.
11. A merchant who has previously completed onboarding keeps `ShopSettings.onboardingCompleted=true` after effective cancellation.
12. Effective cancellation makes Subscription `NO_CONTRACT`; all business execution is then fail-closed by BACKGROUND-013.
13. Provider/API transport failure is never interpreted as cancellation.
14. No merchant access to `moda-interact-admin` is introduced.

## Inspect before editing

```text
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/workers/billing-worker.ts
existing ARCH-010 billing-subscription-reconcile consumer/runtime
existing canonical BillingPeriod rollover helper/service created by BACKGROUND-007
existing effective plan-change transition created by BACKGROUND-010
relevant unit/integration tests
```

Also read:

```text
docs/decisions/background/ARCH-010/BACKGROUND-007-canonical-paid-billing-period-rollover.md
docs/decisions/background/ARCH-010/BACKGROUND-010-apply-shopify-plan-change-transition.md
docs/decisions/database/ARCH-010/DATABASE-004-billing-period-lifecycle-history.md
```

## Provider classification

Every reconciliation attempt MUST query Partner `activeSubscription` unless it is handling only a deterministic stale-job no-op.

Classify provider state in this exact order.

### A. Active contract + pendingUpdate exists

This is not full cancellation ownership for this task.

- persist current provider `cancelAtEndOfCycle` truth as required by the existing projection;
- delegate effective plan-transition semantics to BACKGROUND-010;
- do not clear or convert `pendingPlanId`;
- do not close the period as CONTRACT_ENDED;
- do not create NO_CONTRACT.

This covers Paid -> Free as a plan change even if Shopify also reports cancellation-scheduled semantics for the outgoing paid subscription.

### B. Active contract + `cancelAtEndOfCycle=true` + no pendingUpdate

Full cancellation is scheduled.

Required local projection:

```text
Subscription.planId/current plan     = unchanged
Subscription.status                  = current valid ACTIVE/TRIALING projection
Subscription.cancelAtPeriodEnd       = true
Subscription.pendingPlanId           = null
Subscription.pendingShopifyPlanHandle= null
Subscription.pendingEffectiveAt      = null
Subscription.currentPeriodEnd        = provider exact current cycle end
Subscription.nextReconcileAt         = accepted pre-close/boundary schedule
```

Do not revoke current entitlement early.

### C. Active same plan + `cancelAtEndOfCycle=false`

If local cancellation had previously been scheduled, Shopify has reversed/removed that schedule.

- clear `cancelAtPeriodEnd`;
- preserve current plan, period and counters;
- restore normal rollover scheduling;
- do not grant anything;
- do not write cancellation history that Shopify no longer asserts.

### D. Provider `null` + latest lifecycle `CANCELED`

This is the effective-cancellation proof for an established merchant. Transition to effective no-contract state atomically using the rules below.

`activeSubscription = null` by itself is NOT cancellation proof because Shopify App Pricing also has a temporary FROZEN lifecycle state.

### E. Provider `null` + latest lifecycle `FROZEN`

Do not cancel. Delegate to BACKGROUND-016 frozen reconciliation. Preserve the current plan/period/counters and keep execution fail-closed as FROZEN.

### F. Provider `null` + latest lifecycle `UNFROZEN`, `CREATED`, `UPDATED`, `CANCELLATION_SCHEDULED`, or no usable lifecycle event for an established contract

Do not cancel and do not close the BillingPeriod. Treat provider state as unresolved/fail-closed and retry through canonical reconciliation.

### G. Partner transport/history failure

- preserve durable entitlement evidence;
- do not write NO_CONTRACT;
- do not close the BillingPeriod;
- retry using canonical reconciliation.

### H. Legacy transport/throttle/5xx/malformed response handling

- preserve last-known subscription/entitlement state;
- persist bounded sync-error metadata through existing fields;
- retry using the existing deterministic reconciliation queue/backoff;
- do NOT write NO_CONTRACT;
- do NOT close the BillingPeriod.

## Scheduled cancellation behaviour before the boundary

When provider contract is still current and full cancellation is scheduled:

- recovery admission continues according to the normal current plan capacity order;
- existing conversations continue;
- current paid included credits remain valid until effective contract end;
- purchased credits remain usable;
- lifetime Free credits remain usable after higher-priority sources;
- new recovery-credit-pack purchases MUST be considered ineligible by the merchant-server purchase adapter/UI task;
- canonical App Pricing drain semantics from BACKGROUND-007 still apply before the current provider period closes.

Do not create a separate cancellation queue. Reuse `billing-subscription-reconcile` and durable `nextReconcileAt`.

## Effective full-cancellation transaction

When Partner returns `activeSubscription=null` AND BACKGROUND-015 reports latest effective lifecycle `CANCELED` for a shop with an existing local current contract, execute one serializable/replay-safe transaction.

### 1. Finalize the current BillingPeriod

If an OPEN current BillingPeriod exists:

- release any outstanding period-scoped included reservations using canonical period-close semantics;
- for a paid period, set `forfeitedQuantity = granted - committed` after reservation release, subject to DATABASE-004 constraints;
- for a Free provider BillingPeriod, do not touch the shop-lifetime Free counter;
- set period `status=CLOSED`;
- set `closedAt=now`;
- set `closeReason=CONTRACT_ENDED`.

Do not create a successor BillingPeriod.

### 2. Update Subscription

Set:

```text
planId                     = null
observedShopifyPlanHandle  = null
status                     = NO_CONTRACT
currentBillingPeriodId     = null
billingPeriod/current pointer fields = null according to final DATABASE-004 schema
currentPeriodStart         = null
currentPeriodEnd           = null
trialEndsAt                = null
cancelAtPeriodEnd          = false
providerSubscriptionId     = null
pendingShopifyPlanHandle   = null
pendingPlanId              = null
pendingEffectiveAt         = null
nextReconcileAt            = null
lastSyncedAt               = now
lastSyncErrorCode          = null
lastSyncErrorAt            = null
```

Use the actual final ARCH-010 schema field names; do not invent duplicate current-period fields.

### 3. Preserve lifetime state

Do not change:

```text
FREE_RECOVERY_LIFETIME granted/committed/reserved history
PURCHASED_RECOVERY_CREDITS granted/committed/reserved/refunding history
RecoveryCreditPurchase rows
RecoveryCreditRefund rows
historical BillingPeriods
CheckoutRecovery / Conversation history
ShopSettings.onboardingCompleted
```

## Idempotency

Replaying provider `null` + lifecycle `CANCELED` after effective cancellation must:

- not close another period;
- not change lifetime credit balances;
- not create any new BillingPeriod;
- not create duplicate cancellation rows/events;
- leave Subscription NO_CONTRACT;
- succeed as a no-op apart from safe sync timestamps.

## Redis/BullMQ loss

Cancellation correctness MUST be reconstructable from PostgreSQL.

Before effective cancellation:

```text
cancelAtPeriodEnd=true
currentPeriodEnd=<provider boundary>
nextReconcileAt=<scheduled reconciliation>
```

must be sufficient for existing worker startup/repair logic to recreate the delayed `billing-subscription-reconcile` job.

After effective cancellation `nextReconcileAt=null`; there is nothing to reconstruct until the merchant initiates a new Shopify plan activation.

## Required tests

At minimum prove:

1. `cancelAtEndOfCycle=true` + no pending update stores scheduled cancellation but keeps current plan entitlement active;
2. scheduled cancellation does not close BillingPeriod early;
3. scheduled cancellation does not consume/reset lifetime counters;
4. pending provider plan change takes precedence and is delegated to BACKGROUND-010;
5. provider cancellation schedule reversal clears local `cancelAtPeriodEnd` without granting/resetting credits;
6. transport failure preserves last-known entitlement and does not become NO_CONTRACT;
7. provider null + latest CANCELED closes one paid period with CONTRACT_ENDED and forfeits only unused paid included capacity;
8. provider null + latest CANCELED closes one Free provider period without changing lifetime Free usage;
9. provider null + latest CANCELED creates no successor BillingPeriod;
10. provider null + latest CANCELED sets Subscription NO_CONTRACT and clears current/pending provider pointers;
11. effective cancellation preserves purchased credits exactly;
12. effective cancellation preserves lifetime Free credits exactly;
13. effective cancellation preserves onboardingCompleted;
14. replay of provider null is idempotent;
15. deterministic queue reconstruction includes scheduled cancellation rows before contract end;
16. effective cancellation leaves no delayed cancellation-specific job requirement;
17. no `appSubscriptionCancel` call exists in this implementation;
18. no Admin approval/cancellation request is created.

## Non-goals

Do not implement:

- a merchant cancellation button that calls Shopify Billing API;
- ARCH-009 human-approved cancellation execution;
- top-up refunds;
- resubscription after full cancellation;
- Shopify freeze/interruption classification beyond the safe provider-state rules above;
- deterministic shop re-identification;
- merchant Admin access.

## Stop conditions

Stop and return to `moda_architect` if:

- the implemented Partner provider cannot expose `cancelAtEndOfCycle` or exact current cycle;
- Shopify provider state shows ordinary production cancellation behavior that cannot be represented by current/pending/null classification;
- DATABASE-004 does not provide `CONTRACT_ENDED` or equivalent close reason;
- implementing this requires a new cancellation mutation or local approval workflow.


## Final provider-null cancellation classification

This task MUST consume BACKGROUND-015 lifecycle evidence. `activeSubscription=null` may represent a frozen subscription and must never be finalized as cancellation unless latest effective provider lifecycle evidence is `CANCELED`. Latest `FROZEN` belongs to BACKGROUND-016. Ambiguous/null lifecycle evidence for an established contract remains fail-closed and retryable.


## Final promotional preservation on cancellation

Effective full cancellation preserves promotional-credit ownership/history exactly, alongside purchased and lifetime Free balances. While local state is `NO_CONTRACT`, preserved promotional credits are non-spendable and MUST NOT prevent the `CONTRACT_REQUIRED` execution gate.

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
