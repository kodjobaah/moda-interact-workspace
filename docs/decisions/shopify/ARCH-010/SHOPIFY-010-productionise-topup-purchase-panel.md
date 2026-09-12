---
id: ARCH-010-SHOPIFY-010
architecture_id: ARCH-010
title: Productionise recovery top-up purchase panel component
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
- ARCH-010-SHOPIFY-014
enables: []
created: 2026-09-11
updated: '2026-09-12'
superseded_by: ARCH-010-SHOPIFY-014
---

# ARCH-010-SHOPIFY-010: Productionise recovery top-up purchase panel component

> **Superseded by `ARCH-010-SHOPIFY-014`. Do not implement this task.**
> Its complete unimplemented scope has been absorbed into `ARCH-010-SHOPIFY-014` as part of the 2026-09-12 Luna-oriented task consolidation. The original definition is retained below as design provenance only.

## Original superseded definition

## Objective

Replace the prototype assumptions inside `TopUpPurchasePanel.jsx` with a production presentation component for the real top-up purchase lifecycle defined by SHOPIFY-014.

This task is **component-only**. It does not own provider reads, purchase creation, App Event publication or `/app/billing/options` loader/action; SHOPIFY-012 integrates it.

## Current component behaviour that must be removed

The inspected component currently assumes:

- an array of multiple `topUpOffers` per plan;
- local `chargeAmountMinor` and `currency` are authoritative;
- cards are sorted by local monetary price;
- unit price is calculated in the browser;
- the largest-priced mock pack is labelled featured;
- the buy button includes a local price.

Those assumptions conflict with the current real model, where `BillingPlan` exposes one configured `recoveryCreditsPerPack` plus a Shopify App Pricing event handle and does not own the monetary price.

## Required component contract

Refactor `TopUpPurchasePanel` to accept explicit production props equivalent to:

```ts
{
  merchantUi,
  currentPlanName,
  purchasedCreditsAvailable,
  creditsPerPack,
  purchaseAvailable,
  latestPurchase: {
    id,
    status,
    creditsGranted,
    createdAt,
    activatedAt,
    usageReportState,
  } | null,
  providerPackPricing,
  unavailableReason,
  onPurchaseTopUp,
}
```

Use the actual project typing style. Do not import `billing-purchase.mock.js` and do not provide mock defaults.

## Rendering

When a pack is configured:

- show the real `creditsPerPack` quantity;
- show current purchased-credit availability;
- explain that purchased credits do not expire until used;
- explain that purchased credits are consumed before the merchant's remaining lifetime Free recovery grant;
- explain that this is a one-off capacity top-up billed through the current Shopify App Pricing recovery-credit-pack meter;
- never describe the operation as a legacy Shopify `appPurchaseOneTimeCreate` charge;
- render provider-derived pricing only when SHOPIFY-014 supplies an exact safe display value; otherwise say Shopify bills according to the current App Pricing meter and do **not** fabricate price/currency/unit cost;
- expose one purchase CTA when `purchaseAvailable=true` and no unresolved latest purchase blocks a repeat action;
- render `PENDING_BILLING` as "being confirmed by Shopify" and do not show newly purchased credits as active;
- render `ACTIVE` as confirmed and rely on the refreshed durable purchased balance;
- render `NEEDS_ATTENTION` with support/retry guidance and no granted-credit claim;
- show a localized unavailable explanation for DRAINING/RECONCILING/configuration-ineligible states.

The component must not call `fetch`, Shopify, Prisma or `billingService`; it invokes the provided callback only.

## Accessibility / i18n

All merchant-visible copy uses the existing merchant i18n runtime. Controls remain keyboard-operable and have an explicit disabled/pending state.

## Required tests

At minimum prove:

1. real pack quantity renders;
2. purchased balance renders;
3. no monetary price/unit price is fabricated;
4. CTA calls `onPurchaseTopUp` once when available;
5. disabled/unavailable state does not call callback;
6. PENDING_BILLING prevents a second purchase action and never renders success;
7. ACTIVE renders confirmed state only when durable state says ACTIVE;
8. NEEDS_ATTENTION renders no credit-granted claim;
9. provider price is rendered only from explicit SHOPIFY-014 data and no price is fabricated;
10. no mock import/default exists;
11. no network/provider/database call exists in the component;
12. no Billing API one-time-charge terminology/API is introduced;
13. new i18n keys have catalogue parity.

## Non-goals

Do not edit route loaders/actions, `BillingPurchaseHub`, `SubscriptionChangePanel`, billing service business rules or Shopify provider code.

## Validation

Run focused component/source tests, typecheck, build and `git diff --check` using declared repository commands.

## Stop conditions

STOP if the integrated BillingPlan model exposes multiple production pack variants or local monetary pricing not present in the inspected architecture; return that mismatch to `moda_architect`.

## Completion Report

### Status
Not started.
