---
id: ARCH-010-SHOPIFY-012
architecture_id: ARCH-010
title: Integrate real billing options route and purchase hub
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-010
  - ARCH-010-SHOPIFY-011
  - ARCH-010-SHOPIFY-013
  - ARCH-010-SHOPIFY-018
  - ARCH-010-SHOPIFY-014
  - ARCH-010-SHOPIFY-015
  - ARCH-010-SHOPIFY-007
  - ARCH-008-SHOPIFY-001
enables:
  - ARCH-010-SHOPIFY-008
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SHOPIFY-017
  - ARCH-010-SHOPIFY-019
  - ARCH-010-SHOPIFY-020
  - ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-012: Integrate real billing options route and purchase hub

## Objective

Convert the existing `/app/billing/options` route and `BillingPurchaseHub` from the ARCH-008 mock prototype into a real merchant capacity-management surface by composing **two deliberately different read models**:

1. Shopify-authoritative commercial subscription state from SHOPIFY-013;
2. Moda-authoritative operational recovery-capacity state from SHOPIFY-009.

This task owns integration, not child-component redesign.

## Authority matrix — hard invariant

```text
Question                                         Authority
------------------------------------------------ -------------------------------
Does the Shopify contract exist?                Shopify activeSubscription
What is the current/pending Shopify plan?       Shopify activeSubscription
What price/currency/billing interval applies?   Shopify activeSubscription
What Shopify billing cycle is current?          Shopify activeSubscription
Does Moda know how to entitle that handle?      PostgreSQL BillingPlan mapping
How many Moda included credits remain?          PostgreSQL entitlement counters
How many purchased credits remain?              PostgreSQL entitlement counters
How many lifetime Free credits remain?           PostgreSQL entitlement counters (available under Free or Paid)
May another recovery start?                     SHOPIFY-009 local capacity projection
```

A local `BillingPlan` row is **not** proof that a Shopify plan exists.

## Inspect before editing

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/BillingPurchaseHub.css
app/components/dashboard/billing-purchase.mock.js
app/routes/app/billing/route.tsx
app/routes/app/billing/select/route.jsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes.ts
tests/unit/billing-ui.test.ts
```

Read implemented SHOPIFY-009/010/011/013/007 first.

## Current defects to remove

The inspected route currently:

- constructs hard-coded plan and top-up arrays;
- returns one `billing` object from the loader but ignores it in the component;
- passes `mockBillingState` instead;
- uses console-only top-up and plan-change handlers.

`BillingPurchaseHub` currently:

- imports mock plans/offers/state directly;
- has mock default props;
- silently falls back to `plans[0]` when `currentPlanId` is unknown;
- wraps its content in another `<s-page>` even though the route already renders an `<s-page>`;
- assumes child component contracts that no longer match production billing.

## Loader — required algorithm

Authenticate and resolve the shop using existing policies.

Then perform exactly these conceptual reads:

```text
A. SHOPIFY-013 getMerchantShopifySubscriptionState(shop.id)
   -> live Shopify current/pending commercial subscription truth

B. SHOPIFY-009 getMerchantRecoveryCapacityState(shop.id)
   -> local recovery-capacity/credit accounting projection

C. SHOPIFY-007 local billing-cycle UI phase
   -> ACTIVE / DRAINING / RECONCILING presentation/guards
```

The loader is allowed and expected to call Shopify Partner API because this is a dedicated billing-management surface.

Do not add another direct GraphQL/fetch call in the route. Use the billing service/provider abstraction from SHOPIFY-013.

## Provider verification failure — deterministic UI behaviour

If SHOPIFY-013 cannot verify Shopify because of timeout, throttling, HTTP/API error or malformed provider response:

- do not substitute `Subscription.plan`/`BillingPlan` as live Shopify commercial truth;
- do not show a local plan as though Shopify confirmed it;
- render a localized **billing verification unavailable** state;
- keep non-mutating navigation/support available;
- disable top-up purchase and other billing mutations on this screen;
- offer retry by normal page reload/navigation;
- do not change durable subscription/entitlement state from this loader failure.

## `activeSubscription = null`

Render an explicit **no active Shopify subscription** state.

Do not present a local `BillingPlan` mapping as the merchant's active plan.

Plan-management CTA goes to:

```text
/app/billing/select
```

## Active Shopify plan mapped by Moda

When SHOPIFY-013 returns `mappingStatus = MAPPED`:

- Shopify plan handle/price/currency/billing interval/cycle/pending update are the commercial facts;
- local `BillingPlan` mapping supplies Moda name/kind/features/allowance/pack configuration;
- SHOPIFY-009 supplies current spendable recovery capacity;
- render both without conflating them.

## Active Shopify plan not mapped by Moda

When SHOPIFY-013 returns `mappingStatus = UNMAPPED`:

- render the Shopify plan handle/price/cycle faithfully;
- show localized **Moda configuration unavailable for this Shopify plan**;
- do not classify the Shopify contract as absent;
- do not fabricate included credits/features/top-up eligibility;
- disable top-up purchase;
- keep plan-management and support navigation available.

## Top-up action and lifecycle

Use SHOPIFY-014 as the server-side top-up lifecycle adapter. The route action ultimately reuses the existing:

```text
billingService.requestRecoveryCreditPack(...)
```

Business validation remains in the service. Do not duplicate provider/cycle/meter verification in JSX.

The action remains provider-authoritative for the exact purchase attempt and may make its own current Shopify verification because mutations must not trust loader-time state.

Preserve existing idempotency and SHOPIFY-007 drain/reconciliation guards.

Return the SHOPIFY-014 typed merchant-safe result so the route can show `PENDING_BILLING`, `ACTIVE` and `NEEDS_ATTENTION` correctly. Never claim credits are active immediately after App Event HTTP 202 acceptance. The options route does not call App Events directly.

## Loader purchase eligibility vs mutation verification

The loader may display the current local pack configuration and provider-backed Shopify contract state, but the mutation service remains final authority for whether a purchase is accepted at submission time.

Do not duplicate mutation rules in browser code.

## BillingPurchaseHub integration

Remove every import/default dependency on `billing-purchase.mock.js`.

Require explicit production props representing:

- Shopify commercial subscription state from SHOPIFY-013;
- local Moda mapping status;
- SHOPIFY-009 capacity summary;
- current billing-cycle UI phase;
- local pack configuration;
- a fresh idempotent `purchaseId` when a purchase may be attempted;
- typed action result/pending purchase state.

Compose:

- real capacity summary;
- SHOPIFY-010 `TopUpPurchasePanel`;
- SHOPIFY-011 `SubscriptionChangePanel`.

Preserve the top-up/plan tab/switch behaviour if useful, but its data/actions must be real.

Avoid nested duplicate `<s-page>` wrappers; exactly one page-level wrapper owns the screen heading.

## Plan-change action

The plan tab/CTA MUST use the SHOPIFY-015 flow:

```text
/app/billing/select
  -> Shopify-hosted pricing
  -> callback/welcome return with plan_handle
  -> Partner activeSubscription verification
  -> current/pending classification
  -> Background reconciliation for effective transition
```

Do not submit a local target plan, do not call `appSubscriptionCreate`, and do not change included-credit counters in the HTTP route.

When Shopify returns a pending update, render current and pending plans separately with effective date; current recovery entitlement remains current until BACKGROUND-010 confirms the effective transition.

## No local Shopify plan catalogue

Do not populate plan-management UI with `BillingPlan.findMany()` and label those rows as Shopify plans.

`/app/billing/select` remains the plan discovery/selection surface hosted by Shopify.

This task only displays the merchant's **current and pending** live contract returned by `activeSubscription`.

## Mock removal

After integration:

- production code must not import `billing-purchase.mock.js`;
- hard-coded `starter`, `84`, `18`, `£5/£10/£20`, mock plan prices and console actions are removed;
- if the mock file is unused outside obsolete tests, delete it and move necessary fixtures into tests.

## Free top-up composition

For a Shopify-authoritative current Free subscription, compose the page exactly like Paid for top-up lifecycle purposes:

- current plan/price/cycle and pack usage item come from SHOPIFY-013;
- lifetime Free recovery capacity comes from SHOPIFY-009/local counters and is shop-lifetime, not Free-plan-owned;
- purchased credits are displayed/consumed ahead of lifetime Free credits;
- purchase eligibility/lifecycle comes from SHOPIFY-014;
- the Buy CTA is available only when SHOPIFY-014 says the exact Free pack meter and exact current provider/local BillingPeriod are verified and the phase is ACTIVE.

Do not hide the top-up panel merely because `modaMapping.kind = FREE`. Do not display a monthly Free recovery allowance.

## Required tests

At minimum prove:

1. loader calls SHOPIFY-013 authoritative commercial read;
2. loader calls SHOPIFY-009 local capacity read;
3. loader performs no direct Partner fetch outside the service abstraction;
4. Shopify active plan handle/price/currency/billing interval are rendered from provider state;
5. Shopify pending update is rendered from provider state;
6. a local `BillingPlan` existing without a Shopify active contract is not displayed as the current commercial plan;
7. active Shopify plan + matching Moda mapping renders combined commercial + entitlement state;
8. active Shopify plan + no Moda mapping renders `UNMAPPED` configuration state while preserving Shopify plan facts;
9. Partner verification failure does not fall back to local commercial truth and disables billing mutations;
10. `activeSubscription = null` renders no-active-subscription state;
11. route no longer uses `mockBillingState`;
12. no production mock imports remain;
13. current plan is never replaced by `plans[0]` fallback;
14. real Free capacity renders from SHOPIFY-009;
15. real Paid current-period capacity renders from SHOPIFY-009;
16. purchased balance renders separately;
17. top-up action delegates through SHOPIFY-014 to the existing billing service exactly once per submitted request;
18. PENDING_BILLING, ACTIVE and NEEDS_ATTENTION purchase states render correctly;
19. App Event 202/pending state is never rendered as activated credits;
20. DRAINING/RECONCILING prevents a new purchase through existing service contract;
21. plan management points to `/app/billing/select`;
22. returned pending plan is displayed separately while current entitlement remains current;
23. no local target-plan mutation or Billing API subscription creation exists;
24. no local monetary price is fabricated;
25. no local Shopify plan catalogue is fabricated;
26. no console-only billing actions remain;
27. screen contains only one page-level wrapper;
28. no merchant link targets Admin;
29. production build/typecheck has no task-introduced diagnostics.

## Additional required Free tests

Prove that an eligible Free subscription renders the real top-up action; an ineligible/missing-cycle/missing-meter Free subscription renders a truthful unavailable reason; and no Free screen invents a monthly Free allowance.

## Non-goals

Do not implement Background purchase confirmation, effective plan-transition logic, refunds, cancellation, promotional credits, Admin UI or an API to enumerate every Shopify plan. Those lifecycle behaviours are owned by existing Background reconciliation and BACKGROUND-010.

## Validation

Run focused billing route/component/service tests, then declared full tests, typecheck, build and `git diff --check`.

## Stop conditions

STOP if SHOPIFY-009/010/011/013 integrated contracts differ materially from the task assumptions.

STOP if the route can only present a current commercial plan by treating local `BillingPlan` as Shopify truth.

STOP if `requestRecoveryCreditPack` cannot be reused without changing its accepted billing semantics.

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


## Final lifecycle composition

Compose SHOPIFY-018 lifecycle state with SHOPIFY-013 commercial state. A provider FROZEN result is neither `NO_ACTIVE_SUBSCRIPTION` nor ordinary verification failure. Render frozen billing-management state and keep mutations disabled until durable Background reconciliation restores an executable subscription.


## Final promotional balance composition

When SHOPIFY-009 exposes promotional capacity, compose it into the production billing-options read model as a separate Moda-owned balance. Do not treat it as Shopify commercial truth, price it, make it purchasable/refundable, or expose internal grant provenance. SHOPIFY-020 owns the detailed merchant-facing wording/components.
