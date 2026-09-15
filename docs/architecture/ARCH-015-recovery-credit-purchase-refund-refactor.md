---
id: ARCH-015
title: Recovery-credit purchase, reconciliation, cross-subscription consumption and refund refactor
status: proposed
coordinator: moda_architect
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015: Recovery-credit purchase, reconciliation, cross-subscription consumption and refund refactor

## Purpose

Refactor recovery-credit top-up purchase, provider reconciliation, cross-plan consumption and refunds so that:

- Shopify App Pricing remains provider/subscription/monetary authority.
- ARCH-014 `MerchantPricingPlan` + `MerchantPricingUsageEvent` provide Moda's plan→meter→`creditsGrantedPerUnit` entitlement semantics.
- `RecoveryCreditPurchase` remains the durable ownership ledger.
- purchased credits survive plan and billing-cycle changes.
- only current-provider-context purchases are normally refundable.
- HTTP 202 from App Events is submission receipt only, never entitlement/refund completion.
- automated refund corrections complete only after provider reconciliation.
- Admin remains the explicit manual REFUND/CREDIT fallback.
- zero resolved top-up offers is a valid merchant state and renders "No top ups are currently available for this subscription."

## Authority boundary

```text
Shopify App Pricing
  current active subscription
  current plan handle
  live usage meter membership
  live pricing/currency
  current provider usage quantity/cost
  billing cycle
  pending subscription changes

ARCH-014 MerchantPricing*
  planHandle -> usage-event membership
  usage-event display/order semantics
  creditsGrantedPerUnit

RecoveryCreditPurchase / Refund
  immutable local purchase/refund provenance
  current owned credits
  reservation/consumption/refund state

Background
  App Event publication
  purchase provider reconciliation
  scheduled refund correction/reconciliation

Admin
  exceptional manual provider REFUND/CREDIT evidence path only
```

ARCH-014 MUST NOT replace Shopify live billing truth. Conversely, Shopify does not define how many Moda recovery credits one usage-event unit grants; that comes from ARCH-014.

## Canonical top-up offer correlation

Never resolve an offer globally by `eventHandle`.

Resolve:

```text
Shopify activeSubscription.planHandle
      ->
MerchantPricingPlan.shopifyPlanHandle

then intersect:

MerchantPricingPlan.usageEvents[].eventHandle
      WITH
Shopify activeSubscription.usageItems[].handle
```

A resolved offer receives:

```text
creditsGranted          <- ARCH-014 creditsGrantedPerUnit
cataloguePosition       <- ARCH-014 usage-event position
providerPrice           <- Shopify activeSubscription usage item
providerUsage           <- Shopify activeSubscription usage item
eventHandle             <- exact matched handle
```

For an already-contracted merchant, `MerchantPricingPlan.isActive` is NOT a contract-validity check. It is catalogue visibility. The live Shopify contract decides whether the merchant currently has the plan/meter.

## Empty-state rule

The top-up section is always rendered on the billing surface.

If there are zero valid intersections between current Shopify usage meters and ARCH-014 usage events:

```text
No top ups are currently available for this subscription.
```

This is not a provider error.

Provider/API verification failure is distinct and must render a temporary verification-unavailable state while purchases fail closed.

## Provider-context identity

Native App Pricing may have `legacySubscriptionId = null`.

Use one canonical Shared helper:

```text
legacy provider id present
  -> trimmed raw provider id

legacy provider id absent
  -> app-pricing:v1:<encoded planHandle>:<periodStart ISO>:<periodEnd ISO>
```

Store this derived identity in existing purchase provenance `providerSubscriptionIdSnapshot`. Do not overwrite the live `Subscription.providerSubscriptionId` with a fabricated Shopify id; that field continues to mirror the nullable provider value.

A purchase is "current provider context" only when all required facts agree:

```text
providerContextIdentity
shopifyPlanHandleSnapshot
billingPeriodId
```

and, for a specific refund/purchase action, the expected `shopifyEventHandleSnapshot` is present in the live subscription.

## Fractional correction schema amendment

The v1.1 design assumed no mandatory Prisma change. Current code inspection shows one exception if automated partial App Event corrections are retained:

```text
RecoveryCreditPurchase.providerUsageQuantityBeforeSnapshot Int
RecoveryCreditPurchase.providerUsageQuantityAfterSnapshot  Int?
```

A safe partial correction can make Shopify's subsequent meter quantity fractional (for example 4 -> 3.75). A later purchase must be able to snapshot that exact baseline.

Therefore ARCH-015 changes only these two provider evidence quantities to `Decimal`/`Decimal?`.

`UsageEvent.quantity` is already Decimal and needs no schema change. Moda entitlement counters remain Int because recovery credits are whole units.

No new ledger, lock, refund or catalogue model is authorized by ARCH-015.

## Purchase single-flight invariant

For genuine new purchases:

```text
at most one unresolved REQUESTED RecoveryCreditPurchase
per (shopId, shopifyEventHandleSnapshot)
```

The invariant is intentionally independent of current billing period and provider subscription identity.

Purchase admission uses the existing Subscription row lock for request-time serialization. The durable REQUESTED purchase maintains single-flight across the asynchronous reconciliation window.

Same shop + different event handles may proceed independently.

## Purchase lifecycle

```text
merchant selects resolved offer
  -> app verifies fresh Shopify + ARCH-014 correlation
  -> app snapshots provider before quantity/cost
  -> app creates REQUESTED purchase + PENDING UsageEvent(+1)
  -> existing background publisher submits App Event
  -> Shopify 202 => UsageEvent submission accepted, purchase still REQUESTED
  -> background provider reconciliation proves expected meter/cost delta
  -> purchase ACTIVE + currentAmount=creditsGranted
```

No merchant credits are granted merely because the App Event endpoint returned 202.

## Consumption rule

All ACTIVE purchased lots owned by the shop remain spendable regardless of current plan/billing period.

Selection order:

```text
1. historical/non-current-provider-context ACTIVE lots, oldest first
2. current-provider-context ACTIVE lots, oldest first
```

This preserves potentially refundable current-context value.

Spending purchased credits creates local consumption evidence only and MUST NOT emit Bronze/Silver/Gold top-up App Events.

## Refund eligibility

Normal merchant refund path requires:

```text
purchase ACTIVE
purchase provider monetary amount > 0
unused/unreserved credits exist
fresh Shopify current provider context matches purchase context
purchase planHandle matches live plan
purchase billingPeriodId matches current local billing period
purchase event handle is present in live subscription
```

Historical purchases remain ACTIVE/spendable and return a non-refund outcome; they are not placed on refund hold.

## Refund invocation and completion

`SHOPIFY-003` creates the durable refund request/hold only.

There is NO direct web->Background invocation.

The existing billing worker scheduler invokes `BACKGROUND-003` during its normal cycle.

```text
RecoveryCreditRefund.status = REQUESTED
      ->
existing billing scheduler
      ->
processDueRefundCorrections()
```

Automatic path:

```text
REQUESTED
  -> create/reuse deterministic correction UsageEvent
  -> existing publisher submits negative/fractional App Event
  -> 202 is receipt only
  -> later scheduler reads Shopify provider state
  -> exact expected quantity/cost movement proven
  -> COMPLETED
```

Unsafe automatic path:

```text
REQUESTED
  -> provider correction cannot be proved safe
  -> PROVIDER_ACTION_REQUIRED
  -> Admin performs external REFUND/CREDIT
  -> Admin records exact provider evidence
  -> system verifies evidence
  -> COMPLETED
```

Ambiguous/mismatching evidence -> `NEEDS_ATTENTION`, never speculative completion.

## Task graph

```text
ARCH-014-DATABASE-001
      |
      +--> ARCH-015-DATABASE-001

ARCH-015-SHARED-001  (independent/parallel)

ARCH-014-SHOPIFY-001
      |
      +--> ARCH-015-SHOPIFY-001
                 |
ARCH-015-SHARED-001 + ARCH-015-DATABASE-001
                 |
                 +--> ARCH-015-SHOPIFY-002
                              |
                              +--> ARCH-015-BACKGROUND-001
                                      |
                                      +--> ARCH-015-BACKGROUND-002
                                      |
                                      +--> ARCH-015-SHOPIFY-003
                                                |
                                                +--> ARCH-015-BACKGROUND-003
                                                          |
                                                          +--> ARCH-015-ADMIN-001

All accepted implementation tasks
      -> ARCH-015-SYSTEM-TEST-001
```

## Explicit non-goals

ARCH-015 MUST NOT:

- create a second merchant pricing catalogue;
- make ARCH-014 pricing rows authoritative for live Shopify charges;
- use singular `BillingPlan.recoveryCreditsPerPack` or `BillingPlan.shopifyRecoveryCreditPackEventHandle` as the new top-up source;
- mutate historical purchased lots on plan change;
- emit a top-up App Event when purchased credits are consumed;
- complete a purchase/refund from HTTP 202 alone;
- auto-refund a historical provider-context purchase;
- hide the top-up section merely because no offers are currently available;
- add another background queue solely to invoke refund processing;
- allow implementation agents to invent additional Prisma models/enum states without architect review.
