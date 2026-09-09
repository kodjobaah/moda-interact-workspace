---
id: ARCH-008-RECOVERY-CREDIT-RECONCILIATION-PREFLIGHT
architecture_id: ARCH-008
title: Recovery-credit provider reconciliation architectural preflight
status: Complete
coordinator: moda_architect
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008 recovery-credit provider reconciliation preflight

## Decision

The accepted ARCH-007 data model is sufficient for deterministic recovery-credit
pack reconciliation. **No ARCH-008 database migration/task is required.**

One producer-side correction is required before
`ARCH-008-BACKGROUND-002` starts:

```text
ARCH-008-SHOPIFY-001
Require an exact current billing cycle before creating a new
recovery-credit-pack UsageEvent.
```

`ARCH-008-BACKGROUND-002` must depend on that task.

## Sources inspected

Accepted/current implementation evidence:

- `moda-interact` accepted SHOPIFY-004 implementation head:
  `ea39724f6d1436150b0a4b4ea3eea90db64e8d51`
- `moda-interact-background` ARCH-008-BACKGROUND-001 review snapshot,
  including accepted ARCH-007 B008/B009 capability
- `moda-interact-background/database/prisma/schema.prisma`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/recovery-credit-purchase.service.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-008-billing-worker-reconciliation.md`
- `docs/decisions/background/ARCH-007/BACKGROUND-009-activate-consume-recovery-credit-packs.md`
- `docs/decisions/shopify/ARCH-007/SHOPIFY-004-request-repeatable-recovery-credit-pack.md`

External contract verification:

- Shopify Partner API `activeSubscription`
- Shopify App Pricing documentation

The Partner API documents `currentBillingCycle` as nullable during trial. That
matters because a new pack purchase cannot be assigned to an exact provider
billing cycle while that value is absent.

## Existing durable identity is sufficient

### Provider side

The accepted Partner projection already exposes:

```text
shopifyShopId
planHandle
currentPeriodStart
currentPeriodEnd
providerUsageSnapshot[]:
  handle
  quantity
```

The pack reconciliation input can therefore be resolved as:

```text
shop
+ provider current cycle start/end
+ current Shopify plan handle
+ exact configured pack meter handle
+ provider meter usage.quantity
```

### Local billing-cycle identity

`BillingPeriod` already provides:

```text
id
shopId
periodStart
periodEnd
```

with:

```text
@@unique([shopId, periodStart, periodEnd])
```

The accepted subscription reconciliation upserts the local BillingPeriod from
the Partner `currentBillingCycle` boundaries and links the current Subscription
through `billingPeriodId`.

No extra provider-cycle table is required.

### Local purchase/candidate identity

A recovery-credit purchase already has:

```text
RecoveryCreditPurchase
  id
  shopId
  shopifyPlanHandleSnapshot
  shopifyEventHandleSnapshot
  creditsGranted
  status
  usageEventId
  activatedAt
```

and the linked UsageEvent already has:

```text
UsageEvent
  shopId
  billingPeriodId
  metric
  quantity
  shopifyReportState
  shopifyEventHandle
  shopifyIdempotencyKey
```

Therefore a current-cycle candidate can be selected without a date-window
heuristic:

```text
purchase.shopId == shop
AND usageEvent.billingPeriodId == exact current BillingPeriod.id
AND usageEvent.metric == RECOVERY_CREDIT_PACK_PURCHASE
AND usageEvent.quantity == +1
AND usageEvent.shopifyReportState == REPORTED
AND usageEvent.shopifyEventHandle == exact pack meter
AND purchase.shopifyEventHandleSnapshot == exact pack meter
AND purchase.shopifyPlanHandleSnapshot == current provider plan
```

The entitlement value/interchangeability rule already has the durable
`creditsGranted` snapshot.

### Already matched provider units

Each pack purchase represents exactly one App Events meter unit.

Already matched units can therefore be counted as ACTIVE purchases whose linked
UsageEvent belongs to the same exact billing period and exact pack meter.

No new `providerConfirmedEventId` or pack/provider correlation column is
required; Shopify does not expose such an identity.

## Exactly-once reconciliation is implementable without schema change

`RecoveryCreditPurchase.status`, `activatedAt`, the
`PURCHASED_RECOVERY_CREDITS` counter and the existing Serializable transaction
retry convention are sufficient.

`ARCH-008-BACKGROUND-002` should perform the provider-unit budget calculation
and candidate activation in one Serializable transaction per
shop/current-cycle/pack-meter reconciliation scope.

The transaction should:

```text
read current ACTIVE matched units
read exact eligible pending candidates
calculate confirmedDelta
apply ambiguity rule
CAS/update selected purchases to ACTIVE
increment purchased-credit counter by the sum of newly activated credits
commit
```

A serialization conflict retries the whole calculation, so a concurrent
reconciler observes the winning transaction before calculating its next grant.

## Proven producer gap

The accepted SHOPIFY-004 request path currently:

```text
allows ACTIVE or TRIALING subscription
does not require currentSubscription.billingPeriodId
does not require currentPeriodStart/currentPeriodEnd
verifies provider plan + meter
creates UsageEvent.billingPeriodId = currentSubscription.billingPeriodId
```

Consequently the created UsageEvent can legally have:

```text
billingPeriodId = null
```

The provider verification also does not require the provider current-cycle
boundaries to match the local current period before the event is created.

This is not a missing database field. It is an admission invariant.

### Required correction

Before creating a **new** pack purchase, Shopify must require:

```text
local Subscription.billingPeriodId != null
local Subscription.currentPeriodStart != null
local Subscription.currentPeriodEnd != null
linked BillingPeriod boundaries exactly match Subscription boundaries

provider currentPeriodStart != null
provider currentPeriodEnd != null
provider boundaries exactly match local Subscription/BillingPeriod boundaries
```

The same facts must be re-read and revalidated inside the purchase transaction.

Existing-purchase idempotent replay must remain before this check, so an already
created purchase is still replayable if the provider is temporarily
unavailable.

## Trial behavior

A new recovery-credit pack purchase is not admitted while Shopify has no
`currentBillingCycle`.

That is deliberate. It avoids inventing an upcoming billing cycle or assigning
a purchase by timestamp.

Existing purchased credits remain usable according to ARCH-007; this rule only
governs purchase of a **new** pack.

## Required task graph

```text
ARCH-007-SHOPIFY-004
        |
        v
ARCH-008-SHOPIFY-001
        |
        +--------------------+
                             |
ARCH-008-BACKGROUND-001      |
        |                    |
        +---------+----------+
                  |
                  v
ARCH-008-BACKGROUND-002
                  |
                  v
ARCH-008-ADMIN-001
                  |
                  v
ARCH-008-ADMIN-002
                  |
                  v
ARCH-008-ADMIN-003
                  |
                  v
ARCH-008-SYSTEM-TEST-001
```

System testing remains terminal/manual-gated.

## Database decision

Do **not** create `ARCH-008-DATABASE-001`.

A database task becomes necessary only if a later accepted-source change removes
one of the proven durable identities above. That is not the current state.

## B002 implementation consequences

`ARCH-008-BACKGROUND-002` no longer needs to discover whether the schema is
sufficient. The architect has resolved that question.

B002 must:

1. remove immediate pack activation from App Events transport success;
2. stop invoking global `reconcilePending()` before provider reconciliation;
3. reconcile packs per shop after Partner subscription/current-cycle sync;
4. select the exact current `BillingPeriod` from provider boundaries;
5. resolve the exact current configured pack meter;
6. validate provider meter quantity as finite integer >= 0;
7. calculate ACTIVE matched units and exact eligible candidates from existing
   relations;
8. use one Serializable reconciliation transaction for the provider-confirmed
   budget;
9. fail closed for ambiguous non-equivalent partial confirmation;
10. never activate a row with null/wrong billingPeriodId, wrong meter,
    non-REPORTED event or wrong provider plan snapshot;
11. preserve normal checkout recovery and messaging independence.

Legacy/unreconcilable null-period rows, if any are encountered, must never be
matched by occurredAt/date approximation. Surface attention/diagnostic state
instead.

## Preflight result

```text
DATABASE TASK REQUIRED: NO
SHOPIFY PRODUCER HARDENING REQUIRED: YES
BACKGROUND RECONCILIATION IMPLEMENTABLE AFTER SHOPIFY-001: YES
```
