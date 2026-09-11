---
id: ARCH-010-SHOPIFY-019
architecture_id: ARCH-010
title: Present frozen Shopify subscription state and disable business billing actions
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 61
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-017
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-012
  - ARCH-010-SHOPIFY-018
enables:
  - ARCH-010-SYSTEM-TEST-002
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-019: Present frozen Shopify subscription state and disable business billing actions

## Objective

Keep an onboarded frozen merchant inside the normal merchant application for read/history/support purposes while clearly explaining the Shopify billing hold and preventing product/billing mutations until Background restores an executable subscription.

Merchants never access `moda-interact-admin`.

## Inspect before editing

```text
app/routes/app*/ dashboard route/components
app/routes/app.billing*/ billing routes
/app/billing/options route and BillingPurchaseHub
TopUpPurchasePanel
SubscriptionChangePanel
merchant support route/components
SHOPIFY-009 local capacity projection
SHOPIFY-012 production billing-options integration
SHOPIFY-018 provider lifecycle read model
i18n locale files/tests
```

Use the exact actual filenames discovered in the repository. Do not create duplicate billing screens.

## Dashboard behaviour

When durable local Subscription.status is FROZEN:

- `/app` remains the normal landing/dashboard route;
- usage, events, recovery history and historical conversation/recovery detail remain readable;
- show a prominent localized frozen-subscription message;
- explain that Shopify has paused the app subscription because of a store billing issue/non-payment and that the merchant must resolve Shopify billing before Moda resumes;
- provide navigation to `/app/billing/options` and `/app/merchant-support`;
- do not redirect to first-time onboarding;
- do not represent the state as credit exhaustion or cancellation.

Do not require a Partner API call on every dashboard render solely to show the frozen banner; Background's durable projection is sufficient for the operational dashboard warning.

## `/app/billing/options` behaviour

Use SHOPIFY-018 provider lifecycle truth.

For provider state FROZEN:

- display provider/Moda mapped current plan identity when available;
- display a clear `Subscription paused by Shopify` state;
- explain that plan/top-up actions are unavailable until billing is resolved;
- keep balances/history visible;
- keep support navigation available;
- disable/hide the top-up mutation control;
- disable/hide the Shopify plan-change action;
- do not offer a Moda cancellation/refund mutation as a workaround;
- do not fabricate a direct Shopify billing URL unless the existing code already has an architecture-approved URL builder for that exact destination.

If provider says UNFROZEN/ACTIVE but durable local Subscription is still FROZEN, show a `Restoring access` state and keep mutations disabled until Background has reconciled local execution state. A page read must not directly mutate Subscription to ACTIVE.

If provider verification fails, use SHOPIFY-012 verification-unavailable behaviour, not local commercial fallback.

## Capacity read model

Amend/use SHOPIFY-009 so FROZEN is represented distinctly, e.g.:

```text
availability = CONTRACT_FROZEN
```

The projection may still return informational balances, but `canStartRecovery=false` regardless of remaining Paid/purchased/lifetime Free credits.

Do not consume or zero balances for presentation.

## Server action guards

UI disabling is not sufficient.

Top-up purchase and plan-change server actions must reject when either:

- provider lifecycle read says FROZEN; or
- durable local Subscription is FROZEN/restoration-pending.

Use typed domain errors/results. Do not rely on disabled HTML controls for correctness.

## Required merchant text semantics

Use localized copy equivalent to:

```text
Your Shopify app subscription is temporarily paused because of a Shopify billing issue.
Your Moda data and credit balances are preserved, but recovery and messaging are paused.
Resolve the billing issue in Shopify. Moda will restore access automatically after Shopify reactivates the subscription.
```

Do not promise an exact reactivation time.

## Required tests

At minimum prove:

1. FROZEN merchant lands on `/app`, not onboarding;
2. dashboard/history/usage remain readable;
3. frozen banner is shown from durable local status without Partner call on ordinary dashboard render;
4. `/app/billing/options` renders provider FROZEN distinctly;
5. purchased/lifetime/monthly balances remain visible but non-spendable;
6. top-up button/action is unavailable while frozen;
7. server-side top-up action rejects even if called directly;
8. plan-change control/action is unavailable while frozen;
9. server-side plan-change action rejects direct invocation while frozen;
10. support remains available;
11. no Admin route/link is exposed;
12. provider ACTIVE + local FROZEN shows restoring state and keeps mutations disabled;
13. local ACTIVE after successful unfreeze removes frozen warning on next normal read;
14. provider verification failure does not claim cancellation/active plan from local mapping;
15. exhaustion and cancellation banners remain distinct from frozen;
16. all new copy is covered by the repository's locale/i18n contract.

## Non-goals

No provider mutation, no Background reconciliation, no credit changes, no shop-identity redesign and no new merchant Admin access.

## Stop conditions

STOP if the billing-options action handlers cannot consume SHOPIFY-018 without duplicating a separate Partner API implementation. Return the service-boundary issue to `moda_architect`.

## Completion Report

### Status
Not started.
