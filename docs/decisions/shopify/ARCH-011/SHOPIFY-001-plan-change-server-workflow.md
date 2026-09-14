---
id: ARCH-011-SHOPIFY-001
architecture_id: ARCH-011
title: Implement server-side plan-change intent, redirect and callback reconciliation trigger
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
- ARCH-011-DATABASE-002
- ARCH-011-SHARED-002
enables:
- ARCH-011-SHOPIFY-002
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-SHOPIFY-001

## Authorized implementation surface
```text
app/services/billing/plan-change.service.ts                         # new
app/services/billing/billing-reconciliation.service.ts
app/services/billing/billing.service.ts                            # only top-up gate/state helper; do not rewrite syncSubscription
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx                            # keep generic hosted redirect; no target deep link
app/routes/app/billing/callback/route.tsx
tests/unit/services/plan-change.service.test.ts                    # new
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
tests/unit/billing-ui.test.ts                                     # route contract only, not presentation task
```

## Exact service API
Create `PlanChangeService` with:

```text
getPlanChangeOptions(shopId)
requestPlanChange({shopId,targetPlanId,requestKey})
handleEstablishedSubscriptionCallback({shopId,planHandleHint})
```

`getPlanChangeOptions` loads current Subscription.plan, all active BillingPlans and active BillingUpgradeEconomicsEdges, validates via Shared, and returns every active plan plus Shared direction from current. No price/name/rank inference.

`requestPlanChange` runs server-side only. Validate UUID `requestKey`. Re-read current plan/topology in one DB transaction.
- SAME => return `{kind:"same"}`, no write.
- UNRESOLVED => throw bounded configuration error, no redirect token/write.
- DOWNGRADE => create **no SubscriptionPlanTransition**; return `{kind:"redirect"}` only. Shopify pendingUpdate will become authority after callback/reconciliation.
- UPGRADE => if unresolved transition exists:
  - exact same requestKey => idempotent replay;
  - REQUESTED + provider has not been freshly checked => do not overwrite; caller must use fresh-provider supersession flow below;
  - PROVIDER_CONFIRMED/NEEDS_ATTENTION => reject new request as transition in progress.
  Otherwise create MERCHANT_REQUEST/REQUESTED with source/request snapshots, `requestedAt=now`, and atomically set `Subscription.nextReconcileAt=now+APP_PRICING_UPGRADE_INITIAL_RECONCILE_DELAY_MS`. Then return redirect.

Superseding a REQUESTED intent requires `getMerchantShopifySubscriptionState` fresh provider read first: only when provider current still equals local source may old REQUESTED -> SUPERSEDED and new UPGRADE request be created in one transaction. If provider is already different, do not supersede; schedule immediate background reconciliation.

## Callback rule — critical
Preserve the existing initial-onboarding callback path exactly. For an **established** subscription, do **not** call `billingService.syncSubscription`, because it mutates `Subscription.planId` directly and would bypass ARCH-011 proration.

Established callback does:
1. require bounded `plan_handle` string (hint only);
2. call read-only `billingService.getMerchantShopifySubscriptionState(shop.id)`;
3. compare local current -> provider current via Shared;
4. UPGRADE or same-cycle lower inconsistency => CAS set `Subscription.nextReconcileAt=now`, enqueue `billing-subscription-reconcile` immediately; no local plan/credit mutation;
5. SAME + mapped lower `pendingUpdate` => call new narrow helper `billingService.projectPendingPlanUpdate(...)` that updates only `pendingShopifyPlanHandle`, `pendingPlanId`, `pendingEffectiveAt`, `lastSyncedAt`; current `planId/billingPeriodId/counters` untouched;
6. SAME no pending => no billing mutation;
7. redirect `/app/billing`.
Callback hint never overrides fresh provider truth.

## Top-up gate
In `BillingService.requestRecoveryCreditPack`, before any provider verification or UsageEvent/Purchase creation, query unresolved transition for the shop. If status is REQUESTED, PROVIDER_CONFIRMED or NEEDS_ATTENTION, throw exact bounded error `BILLING_PLAN_TRANSITION_IN_PROGRESS`. Existing purchase replay by exact purchaseId may return before this gate; new purchases must not start.

## `/app/billing/options`
Replace hard-coded/mock plan data. Loader calls `getPlanChangeOptions`. Action accepts exact fields `intent=CHANGE_PLAN`, `targetPlanId`, `requestKey`; calls service then redirects to `/app/billing/select` for SAME? SAME stays page; UPGRADE/DOWNGRADE redirect to generic hosted selector. Do not pass target in Shopify URL.

## Validation
```text
npx vitest run tests/unit/services/plan-change.service.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/services/billing.service.test.ts tests/unit/billing-ui.test.ts
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

STOP if established callback cannot avoid `syncSubscription` direct-plan mutation or if the hosted selector requires a fabricated target-specific URL.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
