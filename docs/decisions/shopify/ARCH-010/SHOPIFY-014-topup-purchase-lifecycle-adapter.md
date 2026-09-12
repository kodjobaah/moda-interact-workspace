---
id: ARCH-010-SHOPIFY-014
architecture_id: ARCH-010
title: Implement merchant recovery top-up lifecycle adapter and production panel
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 54
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-013
  - ARCH-010-SHOPIFY-007
  - ARCH-007-SHOPIFY-004
  - ARCH-010-SHOPIFY-018
enables:
  - ARCH-010-SHOPIFY-012
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-SHOPIFY-014: Implement merchant recovery top-up lifecycle adapter and production panel

## Consolidation

This task absorbs `ARCH-010-SHOPIFY-010`. `SHOPIFY-010` is superseded and MUST NOT be implemented separately.

The server adapter and `TopUpPurchasePanel` are one bounded merchant top-up capability: the adapter defines the exact production state contract and the panel is a pure renderer/callback consumer of that contract. `SHOPIFY-012` still owns route/hub composition.

## Objective

Implement the server-side merchant-safe read/action adapter for recovery-credit-pack purchases **and** refactor `TopUpPurchasePanel.jsx` to render that exact adapter state without mock/local-pricing assumptions.

Moda uses Shopify App Pricing/App Events. Do not introduce a Shopify Billing API one-time purchase.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
app/components/dashboard/billing-purchase.mock.js
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/billing-ui.test.ts
package.json
```

Read the implemented/current contracts before editing:

```text
ARCH-007-SHOPIFY-004
ARCH-010-SHOPIFY-007
ARCH-010-SHOPIFY-013
ARCH-010-SHOPIFY-018
ARCH-010-DATABASE-013
```

## Hard billing mechanism

Preserve this lifecycle exactly:

```text
merchant requests one pack
  -> Moda creates/reuses RecoveryCreditPurchase(PENDING_BILLING)
  -> Moda creates/reuses UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE, quantity=1, PENDING)
  -> HTTP request returns without publishing App Event directly
  -> Background publishes existing App Event to current Shopify pack meter
  -> Background/provider reconciliation proves provider quantity
  -> purchase becomes ACTIVE exactly once
  -> PURCHASED_RECOVERY_CREDITS granted quantity increases exactly once
```

Forbidden in this task/diff:

```text
appPurchaseOneTimeCreate
appSubscriptionCreate
billing.request
appUsageRecordCreate
client-supplied monetary price authority
direct App Events network publication from merchant HTTP action
```

## Server read model

Expose one merchant-safe state equivalent to the following, using integrated enum/type names rather than introducing a second vocabulary:

```ts
{
  configured: boolean;
  purchaseEligible: boolean;
  unavailableReason:
    | "NO_ACTIVE_SUBSCRIPTION"
    | "UNMAPPED_PLAN"
    | "PACK_DISABLED"
    | "PACK_METER_UNVERIFIED"
    | "BILLING_CYCLE_UNVERIFIED"
    | "DRAINING"
    | "RECONCILING"
    | "SHOPIFY_VERIFICATION_UNAVAILABLE"
    | null;
  creditsPerPack: number | null;
  purchasedCreditsAvailable: number;
  shopifyPackMeter: {
    handle: string;
    description: string | null;
    currency: string | null;
    price: /* exact SHOPIFY-013 provider price shape */;
    currentQuantity: number | null;
    currentCostAmount: string | null;
    currentCostCurrency: string | null;
  } | null;
  latestPurchase: {
    id: string;
    status: "PENDING_BILLING" | "ACTIVE" | "NEEDS_ATTENTION" | "CANCELLED";
    creditsGranted: number;
    createdAt: string;
    activatedAt: string | null;
    usageReportState: string;
  } | null;
}
```

### Authority

Shopify provider state is authority for:

- current subscription existence/current handle;
- exact current provider billing cycle;
- exact configured pack meter item;
- provider meter pricing/quantity/cost representation.

PostgreSQL/Moda is authority for:

- `recoveryCreditsPerPack`;
- durable purchased-credit balances;
- RecoveryCreditPurchase status;
- UsageEvent report state;
- ACTIVE/DRAINING/RECONCILING local cycle phase.

Never use local BillingPlan monetary values as Shopify commercial truth.

## Purchase eligibility

At mutation time, both mapped Free and Paid merchants require all of:

```text
Shop.status = ACTIVE
Subscription executable under current policy
provider current plan == mapped current BillingPlan handle
BillingPlan.recoveryCreditPackEnabled = true
BillingPlan.recoveryCreditsPerPack > 0
exact current local BillingPeriod exists
provider current cycle == local exact cycle
configured shopifyRecoveryCreditPackEventHandle is present in provider active usage items
cycle phase = ACTIVE (not DRAINING/RECONCILING)
no unresolved purchase state that blocks a second request under existing idempotency rules
```

Free-specific rules:

- do not require the Paid normal recovery meter;
- the BillingPeriod is provider/App-Event cycle scope only;
- never create/reset a Free included-credit counter;
- lifetime-Free quantities are not changed by pack purchase.

Scheduled cancellation/FROZEN/NO_CONTRACT restrictions defined by later merchant restriction task must remain enforceable server-side when integrated; do not weaken an existing guard.

## Purchase action

The action accepts only the minimal client identity/idempotency input already required by the existing purchase API. Ignore/reject client-supplied:

```text
price
currency
plan
meter handle
creditsPerPack
provider quantity
```

Delegate exactly once to the accepted `requestRecoveryCreditPack(...)`/equivalent lifecycle. Replaying the same purchase identity must reuse the existing purchase/event rather than create another.

Return PENDING as pending. Never claim capacity is ACTIVE before durable provider-confirmed state says ACTIVE.

## TopUpPurchasePanel production contract

Refactor `TopUpPurchasePanel.jsx` to consume explicit props equivalent to:

```ts
{
  merchantUi,
  currentPlanName,
  purchasedCreditsAvailable,
  creditsPerPack,
  purchaseAvailable,
  latestPurchase,
  providerPackPricing,
  unavailableReason,
  onPurchaseTopUp,
}
```

Use actual repository typing style.

The component MUST:

- render real `creditsPerPack` and purchased available balance;
- explain purchased credits are lifetime-until-used;
- explain purchased credits are consumed before remaining lifetime-Free capacity;
- render provider-derived pricing only when the server adapter supplies an exact safe display value;
- otherwise state that Shopify bills according to the current App Pricing meter without fabricating price/unit cost/currency;
- expose one purchase CTA only when `purchaseAvailable=true` and no unresolved purchase blocks it;
- render PENDING_BILLING as awaiting Shopify confirmation with zero newly activated credits;
- render ACTIVE only from durable ACTIVE state;
- render NEEDS_ATTENTION without a granted-credit claim;
- render DRAINING/RECONCILING/configuration-unavailable reason explicitly;
- invoke only the supplied callback; no `fetch`, Prisma, provider or billing service calls from the component;
- remove `billing-purchase.mock.js` import/default usage for this component;
- use merchant i18n for every new visible string.

The component MUST NOT sort fabricated pack cards, compute unit price from local data, label a fake featured pack, or show local BillingPlan monetary price as provider truth.

## Integration boundary

Do not complete `/app/billing/options` route/hub composition here. `SHOPIFY-012` consumes this adapter + component.

This task may edit the route only where a focused action/helper already lives there and is necessary for the adapter contract; it MUST NOT absorb the full billing-options composition task.

## Required tests

### Server/provider lifecycle

1. exact configured pack meter handle is required;
2. local BillingPlan monetary fields are never provider price truth;
3. `creditsPerPack` is distinct from provider price/cost;
4. purchased available balance comes from durable counters/lots;
5. PENDING_BILLING exposes zero newly activated credits;
6. ACTIVE is reflected only after durable activation;
7. NEEDS_ATTENTION grants/claims zero;
8. null provider subscription is ineligible;
9. unmapped provider plan is ineligible;
10. missing pack meter is ineligible;
11. provider verification failure does not fall back to local commercial truth;
12. DRAINING and RECONCILING reject new purchase creation;
13. action ignores client price/plan/meter/credits inputs;
14. action delegates to existing purchase request exactly once;
15. same purchase id replays without second UsageEvent;
16. no direct App Events network request occurs in HTTP transaction;
17. no Billing API one-time-charge mutation exists;
18. mapped Free with exact cycle+pack meter is eligible;
19. Free does not require Paid recovery meter;
20. Free missing exact cycle or pack meter is ineligible;
21. Free request references exact current Free BillingPeriod and creates/resets no Free included allowance.

### Component

22. real pack quantity and purchased balance render;
23. no monetary/unit price is fabricated;
24. provider price renders only from explicit adapter data;
25. available CTA invokes `onPurchaseTopUp` once;
26. disabled/unavailable CTA cannot invoke callback;
27. PENDING_BILLING blocks a second action and never renders success;
28. ACTIVE renders confirmed state only from durable ACTIVE input;
29. NEEDS_ATTENTION renders no granted-credit claim;
30. no mock import/default remains;
31. component performs no network/provider/database call;
32. no legacy one-time-charge terminology/API is introduced;
33. all new i18n keys have catalogue parity.

## Non-goals

Do not implement Background publication/provider confirmation, refund workflow, plan change, cancellation/freeze presentation, promotions, Admin UI, or full billing-options route composition.

## Validation

Inspect `package.json`. Run focused billing service/provider/component tests, then repository-declared test/typecheck/build/Prisma validation applicable to changed files and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP if:

1. current implementation no longer uses Shopify App Pricing/App Events for pack billing;
2. implementation would require a legacy one-time-charge API;
3. SHOPIFY-013 cannot expose the exact current pack meter safely;
4. integrated product model contains multiple production pack variants/local price authority not described by ARCH-010.

Return the mismatch to `moda_architect`; do not infer a new billing model.

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
