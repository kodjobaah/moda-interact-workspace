---
id: ARCH-010-SHOPIFY-009
architecture_id: ARCH-010
title: Add local merchant recovery-capacity projection
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-004
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-008
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-020
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-009: Add local merchant recovery-capacity projection

## Objective

Create one canonical **PostgreSQL-only operational projection** answering one narrow question:

> Can Moda admit another abandoned-checkout recovery for this merchant right now, and which Moda recovery-capacity bucket would fund it?

Before evaluating Paid included capacity, resolve whether the Shop has a currently selected, running, target-eligible campaign grant with remaining quantity. That exact grant is the highest-priority capacity source. There is no aggregate promotional entitlement counter in the first-production baseline; the exact usable selected campaign grant is promotional spendability authority.

This projection is for dashboard/runtime capacity presentation. It is **not** the authority for:

- which Shopify App Pricing plans exist;
- the merchant's live Shopify commercial subscription;
- Shopify plan price/currency/trial terms;
- Shopify pending plan changes.

Shopify remains authoritative for those commercial subscription facts through Partner `activeSubscription`. Local `Subscription`/`BillingPlan` rows are reconciled operational projection and Moda entitlement mapping/configuration only.

This task does not change UI and must not call Shopify.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

Also inspect implemented SHOPIFY-004 and the final DATABASE-013 period/counter schema before naming fields.

## Authority boundary — hard invariant

Treat the data sources as follows:

```text
Shopify Partner activeSubscription
  authority for commercial subscription existence/current plan/pending plan/cycle/price

shopify.Subscription + billing.BillingPlan
  reconciled local projection + mapping from Shopify plan handle to Moda entitlements/features

BillingPeriodEntitlementCounter / ShopEntitlementCounter
  authority for Moda recovery-capacity consumption/reservation accounting
```

A `BillingPlan` row MUST NOT be interpreted as proof that the corresponding Shopify plan currently exists or that the merchant is currently subscribed to it.

A local `Subscription.planId` is usable here only because Background and merchant runtime require a fast local operational projection. It must be labelled/treated as the **reconciled Moda mapping**, not as live commercial Shopify truth.

## Existing implementation constraint

`BillingService.getMerchantBillingState()` currently calls `BillingProvider.getActiveSubscription()` when recovery-credit-pack configuration is present. Do **not** call that provider-verifying method from `/app` merely to render a recovery-capacity warning.

Add a dedicated method such as:

```ts
getMerchantRecoveryCapacityState(shopId: string)
```

or an equivalently explicit local-only API.

The implementation MUST NOT silently rename an existing provider-backed method into a local-only method if that would change existing billing-route semantics.

## Required projection

Return a typed projection equivalent to:

```ts
type MerchantRecoveryCapacityState = {
  availability: "AVAILABLE" | "EXHAUSTED" | "CONTRACT_REQUIRED" | "CONFIGURATION_UNAVAILABLE";
  capacitySource:
    | "FREE_LIFETIME"
    | "PAID_INCLUDED"
    | "PROMOTIONAL"
    | "PURCHASED"
    | "EXHAUSTED"
    | null;

  // This is a Moda entitlement mapping, NOT Shopify commercial authority.
  reconciledPlanMapping: {
    id: string;
    shopifyPlanHandle: string;
    name: string;
    kind: "FREE" | "PAID_METERED";
  } | null;

  observedShopifyPlanHandle: string | null;

  freeLifetime: {
    granted: number;
    committed: number;
    reserved: number;
    remaining: number;
  } | null;

  paidIncluded: {
    billingPeriodId: string;
    periodStart: string;
    periodEnd: string;
    granted: number;
    committed: number;
    reserved: number;
    forfeited: number;
    remaining: number;
  } | null;

  promotional: {
    granted: number;
    committed: number;
    reserved: number;
    remaining: number;
  };

  purchased: {
    granted: number;
    committed: number;
    reserved: number;
    refunding: number;
    available: number;
  };

  topUpConfiguration: {
    enabled: boolean;
    creditsPerPack: number | null;
  };
};
```

Use actual integrated enum/type names if they differ; preserve these semantics exactly.

Do **not** include Shopify price, currency, trial, pending-update commercial details or a local plan catalogue in this projection.

## Availability calculations

### Free

Use only the shop-lifetime `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` snapshot and durable committed/reserved state. DATABASE-013 removes plan-owned allowance and signed-adjustment compatibility. This lifetime source is available under both Free and Paid subscriptions.

```text
remaining = max(granted - committed - reserved, 0)
```

A reserved Free credit is not available for another recovery.

### Paid

Use the unique current OPEN `BillingPeriodEntitlementCounter`, not shop-wide `UsageEvent` aggregation.

```text
remaining = max(granted - committed - reserved - forfeited, 0)
```

### Promotional

Resolve the current `MerchantPromotionSelection` and exact campaign-linked `PromotionalCreditGrant`. Promotional capacity is available only when the selection/campaign/grant is currently usable under DATABASE-013 targeting/status/time-window rules.

```text
remaining = max(grant.quantity - grant.committedQuantity - grant.reservedQuantity, 0)
```

No selected usable campaign grant means zero promotional spendability. There is no aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` fallback. Promotional credits are non-refundable and have no `refundingQuantity`.

### Purchased

Subtract every quantity unavailable for spending, including `refundingQuantity` when present in the integrated schema.

```text
available = max(granted - committed - reserved - refunding, 0)
```

## Capacity source order

```text
FREE mapped operational projection:
  if promotional remaining > 0 -> PROMOTIONAL
  else if purchased available > 0 -> PURCHASED
  else if lifetime Free remaining > 0 -> FREE_LIFETIME
  else -> EXHAUSTED

PAID mapped operational projection:
  if promotional remaining > 0 -> PROMOTIONAL
  else if current-period included remaining > 0 -> PAID_INCLUDED
  else if purchased available > 0 -> PURCHASED
  else if lifetime Free remaining > 0 -> FREE_LIFETIME
  else -> EXHAUSTED
```

If `Subscription.status=NO_CONTRACT`, return `CONTRACT_REQUIRED` regardless of preserved local lifetime balances. Do not report NO_CONTRACT as `EXHAUSTED`, and do not expose purchased or lifetime Free balances as spendable while there is no verified current Shopify contract. The balances may still be returned for presentation/history, but `capacitySource` must be `null` and recovery admission remains unavailable.

If the local operational projection is ACTIVE/TRIALING but the mapped plan/period/counter needed for deterministic capacity is missing, return `CONFIGURATION_UNAVAILABLE`. Do not invent a plan, allowance or balance.

## No-contract semantics

For a previously onboarded merchant whose Shopify contract has ended:

```text
Subscription.status = NO_CONTRACT
availability        = CONTRACT_REQUIRED
capacitySource       = null
```

Preserved purchased/lifetime balances remain visible values only. This projection must not claim they are currently spendable until Shopify verifies a new contract. Fresh never-activated merchants may also be NO_CONTRACT, but routing/onboarding presentation is owned by the merchant route tasks.

## No provider calls — hard requirement

Focused tests MUST spy on the configured `BillingProvider` and prove this method does not call:

```ts
provider.getActiveSubscription(...)
```

Provider/commercial verification belongs to SHOPIFY-013 and mutation/reconciliation flows.

## Required tests

At minimum prove:

1. no usable selected promotion + Free purchased available + lifetime Free available -> `PURCHASED`;
2. no usable selected promotion + Free purchased exhausted + lifetime Free available -> `FREE_LIFETIME`;
3. Free fully exhausted -> `EXHAUSTED`;
4. Free reserved quantity reduces spendable lifetime remaining;
5. no signed lifetime-Free adjustment or plan-owned allowance is queried;
6. no usable selected promotion + Paid included available -> `PAID_INCLUDED`;
7. Paid included exhausted + purchased available -> `PURCHASED`;
8. selected promotional unavailable + Paid included/purchased exhausted + lifetime Free available -> `FREE_LIFETIME`;
9. Paid fully exhausted -> `EXHAUSTED`;
10. Paid reserved and forfeited quantities reduce included remaining correctly;
11. purchased `refundingQuantity` reduces purchased available;
12. missing Paid period -> `CONFIGURATION_UNAVAILABLE`;
13. missing Paid period counter -> `CONFIGURATION_UNAVAILABLE`;
14. returned plan information is explicitly the local reconciled mapping;
15. no pending Shopify/commercial plan catalogue is fabricated from `BillingPlan` rows;
16. provider `getActiveSubscription()` is never called;
17. no BillingPlan lifetime-free allowance field exists or is used to derive lifetime capacity.

Additional required cases:

- NO_CONTRACT + preserved purchased credits -> `CONTRACT_REQUIRED`, not PURCHASED;
- NO_CONTRACT + preserved lifetime Free credits -> `CONTRACT_REQUIRED`, not FREE_LIFETIME;
- NO_CONTRACT + zero balances -> `CONTRACT_REQUIRED`, not EXHAUSTED;
- Shopify provider is still not called for those cases.

## Non-goals

No route/component changes, no Partner verification, no commercial plan catalogue, no price retrieval, no purchase mutation and no Background admission changes.

## Validation

Run focused billing-service tests, then repository-declared typecheck/build/full tests and `git diff --check`.

## Stop conditions

STOP if the integrated period/counter schema differs materially from DATABASE-013; report the exact mismatch rather than inferring another capacity source.

STOP if implementing this task would require treating `BillingPlan` as Shopify plan-existence authority. Return to `moda_architect` instead.

## Completion Report

### Status
Not started.


## Final frozen capacity projection

Add a distinct operational availability result such as `CONTRACT_FROZEN`. When durable Subscription.status is FROZEN, informational balances may still be returned, but `canStartRecovery=false` regardless of remaining monthly included, promotional, purchased or lifetime Free capacity. Do not report ordinary `EXHAUSTED` and do not zero balances.


## Required promotional cases

Add focused coverage proving:

- Free promotional + purchased + lifetime Free -> `PROMOTIONAL`;
- Free promo zero + purchased -> `PURCHASED`;
- usable selected promotional > 0 returns `PROMOTIONAL` even when Paid included remains;
- no usable selected promotional + Paid included > 0 -> `PAID_INCLUDED`;
- selected grant reserved quantity reduces its remaining allocation;
- no selected usable campaign means zero promotional spendability and no aggregate promotional counter is queried;
- FROZEN/NO_CONTRACT returns the lifecycle availability state even when promotional remaining > 0;
- provider `getActiveSubscription()` remains uncalled.
