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
status: ready
priority: 54
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-007
- ARCH-007-SHOPIFY-004
- ARCH-010-SHOPIFY-018
- ARCH-010-DATABASE-014
enables:
- ARCH-010-SHOPIFY-012
- ARCH-010-BACKGROUND-021
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-SHOPIFY-014: Implement merchant recovery top-up lifecycle adapter and production panel

## Consolidation

This task absorbs superseded `ARCH-010-SHOPIFY-010`. Do not implement SHOPIFY-010 separately.

## Objective

Implement the merchant-safe top-up read/action adapter and production `TopUpPurchasePanel` while creating every new `RecoveryCreditPurchase` in the final first-production `REQUESTED` lifecycle with immutable purchase-time commercial context.

Moda uses Shopify App Pricing/App Events. Do not introduce Shopify Billing API one-time purchases.

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

Read implemented/current contracts:

```text
ARCH-010-DATABASE-014
ARCH-010-SHOPIFY-007
ARCH-010-SHOPIFY-013
ARCH-010-SHOPIFY-018
```

## Canonical purchase lifecycle

Use exactly:

```text
REQUESTED
ACTIVE
COMPLETED
WITHDRAWN
REFUNDED
```

This task creates only `REQUESTED` purchases. BACKGROUND-021 is the sole owner of provider-confirmed `REQUESTED -> ACTIVE` activation.

Hard lifecycle:

```text
merchant requests one pack
  -> resolve one exact verified local/provider billing context
  -> snapshot exact provider subscription/cycle/meter and BEFORE usage/cost evidence
  -> create/reuse RecoveryCreditPurchase(REQUESTED, currentAmount=0, reservedAmount=0)
  -> create/reuse UsageEvent(RECOVERY_CREDIT_PACK_PURCHASE, quantity=1, PENDING)
  -> HTTP request returns without direct provider publication
  -> Background publishes/reconciles App Event
  -> BACKGROUND-021 proves exact provider AFTER quantity/cost/currency
  -> immutable purchase monetary basis frozen
  -> currentAmount = creditsGranted
  -> REQUESTED -> ACTIVE exactly once
```

Forbidden:

```text
appPurchaseOneTimeCreate
appSubscriptionCreate
billing.request
appUsageRecordCreate
client-supplied monetary authority
direct App Events network publication from merchant HTTP action
HTTP-side ACTIVE transition
```

## Server read model

Expose one merchant-safe top-up state using current repository types. At minimum include:

```ts
{
  configured: boolean;
  purchaseEligible: boolean;
  unavailableReason: string | null;
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
    status: "REQUESTED" | "ACTIVE" | "COMPLETED" | "WITHDRAWN" | "REFUNDED";
    creditsGranted: number;
    currentAmount: number;
    reservedAmount: number;
    createdAt: string;
    activatedAt: string | null;
    usageReportState: string;
  } | null;
}
```

Provider `NEEDS_ATTENTION`/retry state is exposed through `usageReportState` or a bounded derived unavailable/attention field; do not invent a sixth purchase lifecycle state.

## Authority

Shopify provider state is authority for:

- current provider subscription identity/current handle;
- exact current provider billing cycle;
- exact configured recovery-pack usage item;
- provider price/tier shape;
- current provider usage quantity/cost/currency.

Moda/PostgreSQL is authority for:

- `recoveryCreditsPerPack`;
- durable purchase lifecycle/balances;
- local BillingPeriod/plan mapping;
- UsageEvent report state;
- local cycle phase.

Current local BillingPlan monetary values are never provider purchase/refund truth.

## Purchase eligibility

At mutation time both Free and Paid merchants require:

```text
Shop ACTIVE
executable current subscription policy
provider current plan == mapped current BillingPlan handle
recovery-credit pack enabled and creditsPerPack > 0
exact current local BillingPeriod
provider current cycle == exact local BillingPeriod
configured pack event handle exists on exact provider usage item
cycle phase ACTIVE, not DRAINING/RECONCILING
provider usage item returns unambiguous quantity/cost/currency BEFORE evidence
no unresolved REQUESTED top-up purchase that would make before/after valuation ambiguous
```

The last guard is server-side, concurrency-safe and not merely a disabled button. Two simultaneous purchase clicks must not create two unresolved purchases whose provider cost deltas cannot be attributed uniquely.

Free plan rules remain: no Paid recovery meter requirement and no Free included-period grant/reset.

## One verified billing-context read

Before creating the purchase, resolve one coherent provider/local context and use it for all snapshots. Do not query one plan, then later independently pick another period/meter.

Capture from that same verified context:

```text
billingPeriodId
providerSubscriptionIdSnapshot
planId
shopifyPlanHandleSnapshot
shopifyEventHandleSnapshot
providerUsageQuantityBeforeSnapshot
providerUsageCostBeforeSnapshot
providerUsageCostCurrencyBeforeSnapshot
providerPriceSnapshot
creditsGranted = local configured recoveryCreditsPerPack
```

The provider-before quantity/cost/currency are required. Missing provider cost must not be silently treated as zero.

## Purchase action transaction

The action accepts only minimal idempotency/client operation identity already used by the repository. Reject/ignore client:

```text
price
currency
plan
meter handle
creditsPerPack
provider quantity/cost
refund fields
```

Create/reuse in one transaction equivalent state:

```text
RecoveryCreditPurchase:
  status = REQUESTED
  currentAmount = 0
  reservedAmount = 0
  immutable commercial-before snapshots

UsageEvent:
  metric = RECOVERY_CREDIT_PACK_PURCHASE
  quantity = 1
  exact billingPeriodId/meter
  shopifyReportState = PENDING
```

Replay of the same client operation returns the same purchase/event. Concurrency must enforce at most one unresolved valuation candidate for the same shop/provider subscription/BillingPeriod/pack meter according to DATABASE-014/runtime invariant.

Return REQUESTED as pending. Never claim credits are usable before durable ACTIVE state exists.

## `TopUpPurchasePanel` production contract

Refactor the component to consume explicit server props. It must:

- render real pack credit quantity and current aggregate purchased available balance;
- explain top-ups are lifetime-until-used;
- render provider-derived pricing only from exact adapter data;
- otherwise say Shopify bills through the current App Pricing meter without fabricating price/unit cost/currency;
- expose one purchase CTA only when `purchaseEligible=true` and no unresolved REQUESTED purchase blocks valuation;
- render REQUESTED as awaiting Shopify confirmation and show zero newly activated credits;
- render ACTIVE only from durable ACTIVE state;
- render COMPLETED/WITHDRAWN/REFUNDED as historical latest-purchase states without treating them as newly purchased capacity;
- use bounded provider report/attention copy without introducing an extra purchase lifecycle state;
- call only supplied callbacks; no network/Prisma/provider calls from component;
- remove mock/default pricing imports;
- localize every new string.

Add/link to the future dedicated purchase-management page only in SHOPIFY-026, not here.

## Required tests

At minimum prove:

1. exact configured pack meter required;
2. provider subscription/cycle/meter are coherent and current;
3. missing provider BEFORE quantity/cost/currency is ineligible;
4. BillingPlan local money is never authority;
5. REQUESTED purchase snapshots exact BillingPeriod/provider subscription/plan/meter/before usage evidence;
6. REQUESTED initializes `currentAmount=0,reservedAmount=0`;
7. HTTP action never sets ACTIVE;
8. same operation replays one purchase/event;
9. concurrent unresolved purchase creation is prevented server-side;
10. direct App Event network publication does not occur in HTTP transaction;
11. client money/quantity/context cannot override server snapshots;
12. mapped Free exact cycle+meter remains eligible without Paid meter;
13. DRAINING/RECONCILING/missing cycle/missing meter fail closed;
14. panel renders provider price only from explicit provider state;
15. no local/fabricated price or mock remains;
16. REQUESTED prevents misleading success/duplicate action;
17. all five canonical statuses can be rendered safely when latest historical purchase has them;
18. focused tests, repository validation/build and `git diff --check` pass.

## Non-goals

Do not implement Background provider activation/valuation, refund lifecycle/actions/UI, plan change, cancellation, promotions, Admin or full billing-options composition.

## Stop conditions

STOP if Shopify App Pricing/App Events is no longer the actual mechanism, exact provider before-cost evidence is unavailable from the accepted provider read model, or implementing this task requires guessing a purchase price.

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
