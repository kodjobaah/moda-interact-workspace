---
id: ARCH-010-SHOPIFY-015
architecture_id: ARCH-010
title: Handle Shopify-hosted upgrade and downgrade return without premature entitlement change
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 56
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-013
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-010
- ARCH-010-SHOPIFY-018
enables:
- ARCH-010-SHOPIFY-011
- ARCH-010-SHOPIFY-012
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-015: Handle Shopify-hosted upgrade and downgrade return without premature entitlement change

## Objective

Make the existing plan-management flow on `/app/billing/options` a real Shopify App Pricing flow:

```text
Manage/change plan CTA
  -> /app/billing/select
  -> Shopify-hosted App Pricing page
  -> Shopify redirects to configured callback/welcome route with plan_handle
  -> Moda queries Partner activeSubscription
  -> classify requested handle as CURRENT, PENDING, MISMATCH or UNVERIFIED
  -> persist/schedule only the safe state
  -> redirect merchant back to /app/billing/options
```

This task does not calculate proration and does not create subscriptions locally. Shopify owns commercial plan selection and charging.

## Inspect before editing

```text
app/routes/app/billing/select/route.jsx
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/routes/app/billing/options/route.tsx
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
```

Read implemented SHOPIFY-013 and BACKGROUND-010 before finalising types/result codes.

## Plan selection source of truth

Do not render or submit a local target-plan mutation.

The only merchant plan-selection entrypoint remains:

```text
/app/billing/select
```

which redirects to Shopify-hosted App Pricing.

A `plan_handle` URL parameter is context, not proof. Always query Partner `activeSubscription` after the redirect.

## Callback classification

Implement one explicit classifier equivalent to:

```text
CURRENT_MATCH
  provider.currentPlanHandle == requested plan_handle

PENDING_MATCH
  provider.pendingUpdate.planHandle == requested plan_handle

NO_ACTIVE_SUBSCRIPTION
  provider activeSubscription == null

MISMATCH
  provider exists but neither current nor pending handle equals requested handle

VERIFICATION_FAILED
  Partner API request failed/throttled/timed out/malformed
```

Do not collapse `NO_ACTIVE_SUBSCRIPTION` and `VERIFICATION_FAILED`.

## PENDING_MATCH behaviour

When Shopify reports the requested plan under `pendingUpdate`:

- preserve current `Subscription.planId` and current BillingPeriod entitlement;
- persist observed pending handle;
- map `pendingPlanId` only when the handle has an active Moda `BillingPlan` mapping;
- persist `pendingEffectiveAt` from the current Shopify cycle boundary;
- persist `nextReconcileAt` for the same boundary/pre-close scheduling contract already owned by ARCH-010;
- publish/reuse the deterministic `billing-subscription-reconcile` delayed job;
- redirect to `/app/billing/options?plan_change=pending`;
- do not grant new plan credits or features early.

Purchased lifetime credits and Free lifetime history are unchanged.

## CURRENT_MATCH behaviour

A requested plan can be returned as current Shopify state rather than pending.

The callback MUST NOT directly mutate paid entitlement counters/BillingPeriod allowance from the HTTP request.

Instead:

1. persist enough provider-observed current commercial state for reconciliation using the accepted billing service pattern;
2. schedule/reuse immediate `billing-subscription-reconcile` work;
3. let BACKGROUND-010 decide whether the provider current change is a safe boundary transition or an unexpected immediate-change condition;
4. redirect to `/app/billing/options?plan_change=confirming`.

Do not create/close BillingPeriod rows in this callback.

## NO_ACTIVE_SUBSCRIPTION behaviour

For an existing merchant who entered this route from plan management, a successful Partner response of `null` must not be invented into Free.

- preserve durable history;
- schedule immediate reconciliation through the existing queue contract;
- return merchant to billing options/onboarding according to the accepted current local access state;
- do not claim the requested plan was activated.

## MISMATCH behaviour

Do not update pending/current plan based on the URL parameter.

Return a localized `unable to verify selected plan` state and keep existing entitlements unchanged.

## VERIFICATION_FAILED behaviour

Preserve local subscription/entitlement state, surface verification unavailable and provide normal retry/navigation.

Do not write `NO_CONTRACT` simply because Partner API could not be reached.

## UI return/result codes

Use bounded application-owned query/result codes, not raw provider error text. At minimum support:

```text
plan_change=pending
plan_change=confirming
plan_change=unverified
```

`/app/billing/options` consumes these only as presentation hints; its loader still queries current provider truth through SHOPIFY-013.

## Upgrade/downgrade classification

Do NOT infer upgrade/downgrade from local plan rank or price.

For ARCH-010, UI may call the action generically `Change plan` / `Manage plan`.

The durable transition is determined by current provider plan kind and newly effective provider plan kind inside BACKGROUND-010.

## Required tests

At minimum prove:

1. `/app/billing/select` still redirects to Shopify-hosted pricing;
2. callback requires `plan_handle`;
3. callback re-queries activeSubscription and never trusts plan_handle alone;
4. pending requested handle stores pending state but leaves current plan/period entitlement unchanged;
5. pending mapped plan schedules deterministic reconciliation;
6. pending unmapped provider plan preserves handle and fails closed for entitlement mapping;
7. current requested handle schedules immediate reconciliation and does not open/close BillingPeriod in HTTP request;
8. current requested handle does not grant included credits in callback;
9. provider null is distinct from provider failure;
10. provider failure preserves local state;
11. mismatch does not mutate current/pending state from URL alone;
12. purchased lifetime balance is untouched;
13. Free lifetime committed usage is untouched;
14. no local upgrade/downgrade rank inference exists;
15. no `appSubscriptionCreate`/Billing API mutation is introduced;
16. merchant redirect targets `/app/billing/options` or accepted onboarding state, never Admin;
17. new merchant-visible result copy has i18n parity.

## Non-goals

Do not implement effective plan transition logic, proration calculation, top-up purchase, cancellation/refund handling, Shopify plan catalogue enumeration or Admin plan creation.

## Validation

Run focused callback/service/route tests, declared full tests, typecheck, build and `git diff --check`.

## Stop conditions

STOP if BACKGROUND-010's accepted transition contract is unavailable or materially different.

STOP if implementation would need to infer Shopify commercial timing from local plan price/rank rather than provider current/pending state.

## Completion Report

### Status
Not started.


## Final frozen plan-change guard

Do not initiate hosted plan change or process a plan-change return as executable while SHOPIFY-018 reports FROZEN or durable local Subscription remains FROZEN. Tell the merchant to resolve Shopify billing first. Historical UNFROZEN without a restored live activeSubscription is not sufficient.
