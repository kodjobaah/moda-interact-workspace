---
id: ARCH-010-SHOPIFY-003
architecture_id: ARCH-010
title: Activate first verified paid plan with exact billing period
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 44
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-002
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-003
- ARCH-008-SHOPIFY-001
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-004
- ARCH-010-SHOPIFY-007
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-003: Activate first verified paid plan with exact billing period

## Objective

Extend the billing callback/fast-path subscription sync so a merchant with no current plan can complete onboarding into a paid plan only after Shopify verifies the exact current paid plan, normal usage meter, and current billing cycle. Atomically create the first period-scoped included-credit counter before paid product access becomes available.

## Inspect before editing

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/services/shop/shop.service.ts
app/services/shop/shop-access-policy.ts
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
package.json
```

Read the implemented ARCH-010-SHOPIFY-002 result before editing; reuse its pending-intent and best-effort reconciliation producer instead of creating another queue path.

## Source-state guard

This task is only for first paid activation:

```text
ShopSettings.onboardingCompleted = false
and no existing current mapped plan is active for Moda entitlement
```

If the shop already has a current active Free/Paid plan, a different requested handle is an upgrade/downgrade transition and MUST NOT be applied immediately by this task.

## Callback intent

A locally mapped active `BillingPlan.kind = PAID_METERED` callback handle may be persisted as pending initial-selection intent using the same ARCH-010-SHOPIFY-002 mechanism:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt = now
nextReconcileAt = now
```

The URL parameter alone never sets current paid entitlement or onboarding complete.

## Fast-path verification

Perform one Partner `activeSubscription` query using the existing provider.

Activation requires all of:

```text
current provider flat-rate plan handle == requested plan_handle
mapped local plan exists and active
plan.kind == PAID_METERED
configured normal recovery meter exists
provider current subscription exposes that exact meter
currentPeriodStart/currentPeriodEnd are both non-null
start < end
includedRecoveryConversationAllowance is a non-negative safe integer
provider is not an unsupported paid trial/no-cycle state
```

Do not calculate a billing cycle locally.

## Successful first paid activation transaction

Refactor `BillingService.syncSubscription()` narrowly so the paid first-activation apply path cannot create an incomplete period.

In one Prisma transaction:

1. reload local Shop/Settings/Subscription/target plan;
2. confirm this remains an initial activation rather than a plan change;
3. upsert/reuse the exact `BillingPeriod` from Shopify `currentBillingCycle`;
4. require period OPEN; do not reopen CLOSED historical periods;
5. populate/verify DATABASE-004 ownership/snapshots: `subscriptionId`, `planId`, Shopify handle/name/kind snapshots and `includedRecoveryCreditsGranted`;
6. create/reuse `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`;
7. new counter grant = `BillingPlan.includedRecoveryConversationAllowance`;
8. replay never resets committed/reserved/forfeited quantities;
9. conflicting existing period snapshot or counter grant fails closed rather than being overwritten;
10. update current Subscription projection/cycle/current period pointer;
11. clear initial pending target;
12. set `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)`;
13. clear successful sync error metadata;
14. set `ShopSettings.onboardingCompleted = true` only after all billing state above is valid.

Return/redirect to `/app` only after the transaction succeeds. After commit, best-effort enqueue the existing deterministic subscription-reconciliation job at the new `nextReconcileAt`. Queue failure must not roll back activation; Background queue repair reconstructs it.

## Provider null / transport failure

Reuse the initial-activation verification behaviour from `ARCH-010-SHOPIFY-002` / `ARCH-010-BACKGROUND-001` exactly:

- successful provider null -> stay onboarding/NO_CONTRACT, retain pending target and delayed reconciliation;
- Partner API transport failure -> preserve local state, retain pending target and delayed reconciliation;
- BullMQ enqueue failure -> durable DB intent remains, queue repair recovers it later.

Do not add a second retry implementation.

## Unsupported paid trial

Shopify documents `currentBillingCycle = null` during a trial. ARCH-010 does not support paid trial entitlements.

If the current paid plan is verified but `trialEndsAt` is future/current cycle absent:

- do not create a BillingPeriod;
- do not set onboarding complete;
- do not expose paid recovery services;
- persist/return a safe billing configuration state compatible with BACKGROUND-003's `UNSUPPORTED_PAID_TRIAL` handling;
- do not fabricate an upcoming cycle from trial end.

Do not implement trial entitlement in this task.

## Free/purchased/promotional balance preservation

First paid activation MUST NOT:

- reset or delete an existing `LIFETIME_FREE_RECOVERY_CREDITS` grant/usage;
- reset purchased top-up credits;
- consume purchased credits;
- grant promotional credits;
- skip the one-time shop-lifetime Free grant merely because the first verified plan is Paid;
- copy Free allowance into the paid period.

The new paid period receives only its configured paid `includedRecoveryConversationAllowance` in the period counter.

In the same first-activation transaction, ensure `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` exists. If absent, create it with `grantedQuantity = PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` and zero committed/reserved/refunding quantities. If it exists, never rewrite its grant or usage. This lifetime grant is independent of the paid period counter.

## No incomplete paid subscription state

After this task, the application fast path must never commit:

```text
ACTIVE paid subscription + onboardingCompleted=true
```

unless the exact current BillingPeriod and unique included-credit counter both exist and match the observed Shopify cycle.

## Required tests

At minimum prove:

1. paid callback records pending intent before activation;
2. callback parameter alone does not activate;
3. current matching paid plan + exact cycle + meter activates;
4. first BillingPeriod created with exact Shopify boundaries;
5. first period counter created with configured included grant;
6. onboarding completes only after period/counter transaction;
7. replay does not reset committed/reserved/forfeited values;
8. conflicting existing period grant fails closed;
9. provider null uses existing delayed-reconciliation path;
10. Partner API failure uses existing delayed-reconciliation path;
11. queue failure does not lose durable intent;
12. wrong current handle does not activate requested paid plan;
13. pending-only paid handle does not activate first onboarding;
14. already-current Free/Paid merchant requesting another plan is not handled as first activation;
15. missing provider usage meter fails closed;
16. missing current cycle fails closed;
17. paid trial/no-cycle fails closed without synthetic period;
18. invalid included allowance fails closed;
19. direct-to-Paid first activation creates the one-time lifetime Free grant exactly once; replay does not regrant it;
19. Free lifetime and purchased balances remain unchanged;
20. no merchant route points to `moda-interact-admin`;
21. first BillingPeriod contains DATABASE-004 ownership/snapshot fields;
22. successful activation schedules nextReconcileAt at periodEnd minus the Shared drain window;
23. queue-add failure does not roll back successful activation.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test -- tests/unit/routes/billing-callback.test.ts tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts
npm run typecheck
npm run build
git diff --check
```

If Vitest argument forwarding differs in the integrated package, use the actual declared Vitest invocation without inventing an npm script; document the command used.

## Non-goals

Do not implement paid reservation routing, period rollover execution (BACKGROUND-007 owns it), upgrade/downgrade, cancellation, top-up refunds, promotional-credit grants, Admin UI or a new queue contract.

## Stop conditions

STOP if:

- ARCH-010 period counter is not available in generated Prisma client;
- callback source state cannot distinguish first activation from a plan change;
- the existing billing provider cannot expose exact current cycle/meter identity;
- successful activation would require synthetic trial-period dates.

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
