---
id: ARCH-011-SHOPIFY-001
architecture_id: ARCH-011
title: Implement merchant same-cycle upgrade workflow, supersession, top-up gate and UI
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_shopify
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
- ARCH-011-SHARED-002
- ARCH-010-SHOPIFY-014
- ARCH-010-SHOPIFY-015
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-SHOPIFY-001: Implement merchant same-cycle upgrade workflow, supersession, top-up gate and UI

## Objective

Implement the **complete merchant-facing ARCH-011 feature in one Shopify task**: server request flow, plan-direction decisions, superseding an unverified target, top-up ambiguity gate, billing UI, current-cycle upgrade history and deferred-downgrade presentation.

Do not split API/server and UI work into a second Shopify task.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/types.ts
app/services/billing/repositories/subscription.repository.ts
app/routes/app/billing/route.tsx
app/components/dashboard/SubscriptionChangePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/billing-ui.test.ts
tests/unit/routes/billing-callback.test.ts

ARCH-010-SHOPIFY-014 accepted top-up flow
ARCH-010-SHOPIFY-015 accepted Shopify-hosted plan-change return flow
ARCH-011 Prisma models
published ARCH-011 Shared primitives
```

## A. Effective plan versus requested target

The local/provider-confirmed current plan is the only effective plan. A `REQUESTED` `SubscriptionPlanTransition` is intent only.

Never present an unverified target as already effective and never mutate included entitlement in this repository.

## B. Resolve canonical topology on the server

For every plan-change action:

1. read all active BillingPlans and active `BillingUpgradeEconomicsEdge` rows from server-side Prisma;
2. build the published Shared topology input;
3. call Shared canonical validator; invalid => fail closed with bounded merchant-safe error / operator logging;
4. call Shared direction classifier using current effective plan + selected target.

Never classify from price, name, allowance or UI order.

Adjacent chain defines order only. For `Free -> Starter -> Growth -> Scale`, offer direct immediate targets:

```text
Free: Starter, Growth, Scale
Starter: Growth, Scale
Growth: Scale
Scale: none
```

Do not force one-tier-at-a-time upgrades.

## C. Same/current/lower/higher action rules

```text
SAME
  no provider plan change; return deterministic no-op/current-plan result.

UPGRADE
  eligible for immediate Shopify-hosted change subject to unresolved-transition rules below.

DOWNGRADE
  never become effective mid-cycle under ARCH-011; use/preserve ARCH-010 next-cycle downgrade scheduling semantics.

UNRESOLVED
  fail closed; do not call provider plan-change action.
```

## D. Create upgrade intent before redirect/action

For an immediate upgrade, in a server-side transaction:

1. re-read current Subscription/effective plan;
2. re-run topology classification;
3. require no blocking unresolved transition;
4. snapshot source/target plan IDs, handles, kinds and included allowances into `SubscriptionPlanTransition`;
5. create unique deterministic `requestKey` using existing bounded-key/idempotency conventions;
6. status = `REQUESTED`;
7. only after durable request creation initiate the accepted Shopify-hosted plan-management/change flow.

Do not let browser-supplied plan price, allowance, subscription ID, provider ID or proration amount become authority. Browser may submit only the selected target identity/handle needed to resolve server-side.

## E. Supersede an unverified upgrade

A merchant may change their mind **before the previous requested target has been provider-verified/current**.

Example:

```text
effective Starter
REQUESTED Starter -> Growth
merchant now chooses Scale
```

Required server flow:

1. fresh Shopify provider read using accepted provider client;
2. if provider already reports Growth current, **do not supersede**; return reconciliation/pending state so Background applies Growth first;
3. if provider proves Starter still current and old Growth target is not current, atomically mark old REQUESTED transition `SUPERSEDED`;
4. classify new selection from **Starter**, not from Growth;
5. create new `Starter -> Scale` REQUESTED transition;
6. initiate provider plan flow for Scale.

A lower selection while a higher request is still unverified is evaluated from the still-effective current plan. Example Starter -> Growth REQUESTED, then Free selected: supersede Growth after fresh proof, then preserve/schedule Starter -> Free as the existing deferred downgrade flow.

`PROVIDER_CONFIRMED` or `NEEDS_ATTENTION` cannot be superseded from merchant UI. They block another immediate plan change until reconciliation.

## F. At most one unresolved transition

Treat database uniqueness as final authority. Catch/map a race where another request creates the unresolved transition first. Do not create a second unresolved row by retrying around the constraint.

## G. Top-up ambiguity gate

ARCH-010 top-up prices/meters can differ by plan. While a transition is unresolved in:

```text
REQUESTED
PROVIDER_CONFIRMED
NEEDS_ATTENTION
```

new `RecoveryCreditPurchase` initiation is blocked server-side **inside the same authoritative action path used by ARCH-010-SHOPIFY-014**.

Required result is a bounded retry-later/pending-plan message. Do not merely disable a button. Existing purchases/reservations/refunds continue unchanged.

After transition becomes `APPLIED`, new top-ups resolve the now-current provider tier/meter.

## H. Merchant billing UI

Update the existing billing route/panels rather than creating an unrelated second billing experience unless current route conventions require a child page.

Display at minimum:

```text
current effective plan
current Shopify provider billing cycle start/end
all transitively higher immediate-upgrade targets
lower plans as next-cycle downgrade choices according to ARCH-010
pending REQUESTED/PROVIDER_CONFIRMED/NEEDS_ATTENTION state
current-cycle actual plan-segment history
next-cycle scheduled lower plan when present
```

For history, render actual applied segments only. If merchant skipped Starter and went Free -> Scale, do not fabricate Starter/Growth segments.

UI copy must distinguish:

```text
"Upgrade requested" != "Upgrade active"
"Downgrade scheduled for next billing cycle" != current plan
```

Do not calculate or promise Shopify's monetary prorated charge locally. Shopify-hosted UI/provider remains cash authority.

## I. Free -> paid presentation

Do not tell the merchant Moda decides whether the paid plan starts a new cycle. After provider confirmation, Background determines from Shopify `currentBillingCycle` whether full-opening or same-cycle entitlement applies. UI may state that Shopify determines billing-cycle/prorated charging details.

## J. Current-cycle entitlement display

If showing included-credit grant history, read persisted transition/segment evidence. Do not recalculate historical target entitlement from today's plan config. Do not suggest prior committed usage affected the proration formula.

## Required tests

Prove at minimum:

1. topology chain produces all transitively higher choices;
2. Free -> Scale direct request;
3. Starter -> Scale direct request;
4. price/name changes do not change direction;
5. same-plan no-op;
6. lower target uses deferred downgrade, never same-cycle immediate application;
7. REQUESTED Growth superseded by Scale only after fresh provider proof;
8. old target already provider-current prevents supersession and returns reconciliation state;
9. lower selection during unverified upgrade is evaluated from still-effective plan;
10. DB unresolved-transition race mapped safely;
11. REQUESTED/PROVIDER_CONFIRMED/NEEDS_ATTENTION block top-up server-side;
12. APPLIED unblocks new top-up and current tier meter is used;
13. existing purchases/refunds remain accessible;
14. UI distinguishes requested/effective/scheduled;
15. actual current-cycle segments render without fabricated intermediate tiers;
16. no client price/allowance/provider IDs trusted;
17. no cash-proration calculation in Moda;
18. existing ARCH-010 Shopify billing tests remain green except documented unrelated baseline failures.

## Validation

Run repository-declared equivalents of:

```text
<focused billing service/provider/route/UI tests>
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
git diff --check
```

## Non-goals

No provider-confirmed entitlement mutation, no Background reconciliation implementation, no Admin topology mutation, no Shared/Database changes, no cash proration.

## Stop conditions

STOP if:

- accepted ARCH-010 Shopify plan-change/top-up flows cannot be extended without replacing them;
- fresh provider state cannot prove whether a REQUESTED target became current before supersession;
- topology is invalid/UNRESOLVED;
- client-side state would have to become billing authority.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
