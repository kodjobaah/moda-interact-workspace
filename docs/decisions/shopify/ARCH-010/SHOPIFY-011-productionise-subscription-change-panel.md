---
id: ARCH-010-SHOPIFY-011
architecture_id: ARCH-010
title: Productionise Shopify-hosted plan management panel component
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 53
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-015
enables: []
created: 2026-09-11
updated: '2026-09-12'
superseded_by: ARCH-010-SHOPIFY-015
---

# ARCH-010-SHOPIFY-011: Productionise Shopify-hosted plan management panel component

> **Superseded by `ARCH-010-SHOPIFY-015`. Do not implement this task.**
> Its complete unimplemented scope has been absorbed into `ARCH-010-SHOPIFY-015` as part of the 2026-09-12 Luna-oriented task consolidation. The original definition is retained below as design provenance only.

## Original superseded definition

## Objective

Replace the mock/local-pricing assumptions inside `SubscriptionChangePanel.jsx` with a presentation component whose **current and pending commercial subscription facts come from Shopify**, while plan selection/change remains on Shopify's hosted App Pricing page.

This task is component-only. It performs no network calls. SHOPIFY-015 owns the Shopify-hosted plan-selection/return flow and BACKGROUND-010 owns the effective entitlement transition.

## Inspect before editing

```text
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
tests/unit/billing-ui.test.ts
```

Read implemented SHOPIFY-013 before defining final prop names.

## Current component behaviour that must be removed

The inspected component currently:

- expects a locally priced/ranked `plans[]` catalogue;
- formats mock/local `monthlyPriceMinor`/`currency` values;
- classifies upgrade/downgrade from local `rank`;
- emits a local plan object through `onChangePlan`;
- logs selected plans to the console;
- contains duplicated allowance/benefit blocks;
- treats local plan cards as if they were Shopify's commercial catalogue.

## Authority boundary

The component receives **Shopify current/pending commercial state** from its parent. It may additionally receive Moda mapping metadata to explain the entitlement mapping.

It MUST NOT derive Shopify commercial truth from `BillingPlan[]`.

## Required production component contract

Accept explicit props equivalent to:

```ts
{
  merchantUi,
  shopifySubscription: {
    planHandle: string;
    description: string | null;
    price: { amount: string; currency: string | null };
    billingPeriod: string;
    cancelAtEndOfCycle: boolean;
    pendingUpdate: {
      planHandle: string;
      price: { amount: string; currency: string | null };
      effectiveAt: string | null;
    } | null;
  } | null,
  modaMapping: {
    name: string;
    kind: "FREE" | "PAID_METERED";
  } | null,
  mappingStatus: "MAPPED" | "UNMAPPED" | "NO_ACTIVE_SUBSCRIPTION",
  managePlansHref: string,
}
```

Use actual integrated type names from SHOPIFY-013.

## Required rendering

### Active mapped subscription

Render:

- Shopify current plan handle or mapped display name;
- current Shopify flat-rate price/currency when available;
- current billing interval;
- `cancelAtEndOfCycle` state when true;
- Shopify pending update handle/price/effective date when present;
- localized CTA to `managePlansHref`.

The price shown here is allowed because it comes from Shopify `activeSubscription`, not local mock/config data.

### Active but unmapped Shopify subscription

Render the Shopify plan handle/price/cycle faithfully and a localized configuration-unavailable explanation. Do not pretend the contract is absent. Do not show Moda entitlement promises that require a mapping.

### No active Shopify subscription

Render a localized no-active-plan state plus the Shopify-hosted plan-management CTA.

## Plan management CTA

The CTA must use the supplied href, which integration sets to:

```text
/app/billing/select
```

That route redirects to Shopify-hosted App Pricing.

The component performs no local plan mutation. After the merchant returns from Shopify, current/pending state is supplied by the parent from SHOPIFY-013/015; pending state must clearly say the current entitlement remains unchanged until Shopify makes the new plan effective.

## Prohibited behaviour

Do not:

- render a local `plans[]` catalogue as Shopify plans;
- use local price/rank fields;
- infer upgrade/downgrade from local ranking;
- submit a local target plan;
- make a network request;
- fall back to a first plan;
- link merchants to Admin.

Remove duplicate prototype content and console logging.

## Required tests

At minimum prove:

1. current Shopify handle/price/currency render from explicit props;
2. mapped Moda plan name may decorate, but not replace, Shopify truth;
3. pending Shopify plan/effective date render when supplied;
4. `cancelAtEndOfCycle` renders when true;
5. unmapped current Shopify plan renders as existing-but-unmapped;
6. no-active-subscription state renders separately;
7. no local price/rank/catalogue is required;
8. no upgrade/downgrade classification is invented;
9. CTA uses the supplied Shopify-hosted management href;
10. no local mutation/network call is made by the component;
11. duplicate prototype blocks are removed;
12. no mock fallback/import exists;
13. i18n catalogue parity is preserved.

## Non-goals

Do not implement paid->paid or paid->Free state transitions, route loaders/actions, Shopify callback reconciliation, full Shopify plan catalogue retrieval or Admin UI.

## Validation

Run focused component/source tests, typecheck, build and `git diff --check` using declared repository commands.

## Stop conditions

STOP if SHOPIFY-013's accepted contract differs materially. Return to `moda_architect` rather than inventing a substitute local commercial source.

## Completion Report

### Status
Not started.
