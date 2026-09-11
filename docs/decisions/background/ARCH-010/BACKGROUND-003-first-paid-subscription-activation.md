---
id: ARCH-010-BACKGROUND-003
architecture_id: ARCH-010
title: Reconcile first paid activation and create the first paid period
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 43
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-006
  - ARCH-010-BACKGROUND-001
  - ARCH-010-DATABASE-002
  - ARCH-010-DATABASE-004
  - ARCH-010-BACKGROUND-007
  - ARCH-010-SHARED-002
  - ARCH-007-BACKGROUND-008
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-010
  - ARCH-010-SHOPIFY-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-BACKGROUND-003: Reconcile first paid activation and create the first paid period

## Objective

Extend the ARCH-010 subscription-reconciliation path so `NO_CONTRACT + pending paid plan` can become a fully usable first paid subscription only after Shopify confirms the paid plan as current **and** supplies an exact current billing cycle.

Reuse the queue/consumer/runtime created by `ARCH-010-BACKGROUND-001`; do not create another queue or Render worker.

## Inspect before editing

```text
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/runtime/billing-scheduler.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
package.json
```

Read the implemented ARCH-010-BACKGROUND-001 code before editing. Its exact service/file decomposition is authoritative if names differ from the portable task definition.

## Applicable source state only

This task handles initial paid activation when durable state indicates:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = false
Subscription is NO_CONTRACT initial activation state
pendingPlanId/pendingShopifyPlanHandle identify an active local PAID_METERED BillingPlan
nextReconcileAt matches the queued job
```

Do not use this path for an already-active Free/Paid subscription changing plan. Upgrade/downgrade is a later ARCH-010 transition.

## Provider verification

Call the existing Partner provider. Activation succeeds only when all are true:

```text
provider current plan handle == pendingShopifyPlanHandle
local pending plan id maps to that same active BillingPlan
BillingPlan.kind == PAID_METERED
provider contains the exact configured normal recovery usage meter
provider currentPeriodStart/currentPeriodEnd are both non-null
currentPeriodStart < currentPeriodEnd
BillingPlan.includedRecoveryConversationAllowance is a non-negative safe integer
```

Provider `null` and transport failure retain the bounded initial-activation retry policy owned by `ARCH-010-BACKGROUND-001` / `ARCH-010-SHOPIFY-002`.

## Unsupported paid trials

Shopify Partner API documents `currentBillingCycle = null` while the subscription is in trial. ARCH-010 does not support a synthetic trial billing period.

If provider truth identifies the requested paid plan as current but `trialEndsAt` is future and current cycle is null:

- do not set onboarding complete;
- do not create a BillingPeriod/counter;
- do not grant paid recovery entitlement;
- record a bounded configuration/synchronization error code such as `UNSUPPORTED_PAID_TRIAL` using the repository's established error-code style;
- do not run the ordinary 1-minute "Shopify has not activated yet" propagation retry loop for the entire trial;
- log an operationally actionable structured event without secrets.

Do not invent trial credits. If the product later wants paid trials, return to architecture.

## First paid period transaction

Once provider verification is valid, perform one transaction that:

1. reloads Subscription/ShopSettings/pending BillingPlan and confirms this is still initial activation;
2. upserts/reuses the exact BillingPeriod keyed by existing canonical `(shopId, periodStart, periodEnd)` identity;
3. require BillingPeriod status OPEN; do not reopen a CLOSED historical period;
4. populate/verify DATABASE-004 period ownership/snapshots: `subscriptionId`, `planId`, Shopify handle/name/kind snapshots and `includedRecoveryCreditsGranted`;
5. upserts/reuses the unique `BillingPeriodEntitlementCounter` for `INCLUDED_RECOVERY_CREDITS`;
6. on create, set `grantedQuantity = BillingPlan.includedRecoveryConversationAllowance`, other quantities zero;
7. on replay, never reset committed/reserved/forfeited quantities;
8. if an existing period snapshot or counter grant disagrees with the expected current plan/grant, fail closed rather than rewriting it;
9. ensure `ShopEntitlementCounter(FREE_RECOVERY_LIFETIME)` exists; create it only when absent with `grantedQuantity = PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`, otherwise preserve its grant/usage exactly;
9. update Subscription current plan, observed handle, ACTIVE status, exact cycle, provider fields, and current billing period pointer;
10. clear pending initial-selection fields;
11. set `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)` for canonical rollover scheduling;
12. clear transient sync-error metadata on success;
13. set `ShopSettings.onboardingCompleted = true` last within the same transaction.

If any step fails, the transaction rolls back and the merchant remains unavailable for paid recovery.

## Billing-period end scheduling

Persist exact `currentPeriodEnd` as provider truth. After the successful activation transaction, schedule the already-defined canonical rollover lifecycle:

```text
nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)
```

Commit this durable timestamp with activation, then best-effort enqueue the existing deterministic reconciliation job after commit. BACKGROUND-007 owns what the pre-close/boundary job does; this task must not duplicate close/open logic.

Do not alter the current rotating reconciliation cadence solely to simulate rollover.

## Existing rotating reconciliation compatibility

The existing `reconcileOnce()` path may observe this same provider state. Refactor so applying a valid first paid subscription uses the same idempotent transaction/helper as the BullMQ job rather than creating a period without its required included counter.

After this task, no Background code path may produce:

```text
ACTIVE PAID_METERED subscription
+ current BillingPeriod
+ missing INCLUDED_RECOVERY_CREDITS counter
```

for a newly applied ARCH-010 paid subscription.

Do not duplicate Shopify calls inside the transaction. Provider observation occurs before the DB transaction; the transaction revalidates local state and applies that immutable observation.

## Required tests

Prove at least:

1. due pending paid target + matching current provider plan/cycle activates successfully;
2. exact BillingPeriod is created once;
3. included counter is created with configured grant and zero consumption;
4. onboarding becomes true only in the successful transaction;
5. replay reuses period/counter and does not reset usage;
6. provider null retains existing pending retry policy;
7. Partner transport failure retains existing pending retry policy and local state;
8. wrong current plan does not activate requested paid plan;
9. unknown/inactive plan mapping fails closed;
10. missing configured normal usage meter fails closed;
11. provider missing required meter fails closed;
12. missing currentBillingCycle does not create period;
13. paid TRIALING/no-cycle does not grant access and emits the explicit unsupported-trial error;
14. invalid cycle start >= end fails closed;
15. null/negative/non-integer included allowance fails closed;
15a. direct-to-Paid first activation creates the lifetime Free grant exactly once;
16. existing period counter with conflicting grant is not rewritten;
17. stale BullMQ job remains no-op;
18. uninstalled shop remains no-op;
19. Free activation behavior from BACKGROUND-001 remains passing;
20. no new queue/service/runtime process is created.
21. created first period contains DATABASE-004 subscription/plan snapshot fields;
22. successful activation sets nextReconcileAt to periodEnd minus the Shared drain window and best-effort enqueues the deterministic job;
23. queue-add failure does not roll back activation and reconstruction can recreate the scheduled job.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run build
git diff --check
```

Run relevant existing integration tests through `npm run test:integration` when required dependencies are available.

## Non-goals

Do not implement paid recovery reservation routing (BACKGROUND-002 owns it), merchant callback/UI, period rollover implementation (BACKGROUND-007 owns it), upgrade/downgrade, cancellation, top-up refund changes, promotional credits, or Admin UI.

## Stop conditions

STOP if:

- the integrated ARCH-010-BACKGROUND-001 consumer cannot be extended without changing the Shared payload;
- the database client lacks BillingPeriodEntitlementCounter;
- current BillingPeriod identity has changed since the inspected workspace;
- correct activation would require inventing a billing cycle during a trial.

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
