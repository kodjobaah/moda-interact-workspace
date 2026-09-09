---
id: ARCH-009
title: Merchant billing lifecycle, cancellations and recovery-credit refunds
status: Agreed
coordinator: moda_architect
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-009: Merchant billing lifecycle, cancellations and recovery-credit refunds

## Status

Agreed.

ARCH-009 is a pre-production lifecycle architecture layered on:

- accepted ARCH-007 commercial billing/entitlement rules;
- ARCH-008 truthful App Events receipt semantics and provider-confirmed
  recovery-pack activation/reconciliation.

ARCH-009 does not replace Shopify App Pricing and does not create a second
commercial price source.

## Product invariants

### INV-009-001 — Free lifetime allowance survives plan changes

Free lifetime usage remains attached to the durable Shop.

Example:

```text
Free lifetime allowance = 5
consume 3
remaining Free = 2

upgrade to Growth
Free remaining remains durably 2
but is not consumed while Growth is current

later Shopify makes Free current
remaining Free resumes = 2
```

A fully cancelled Shopify contract is:

```text
NO_CONTRACT
```

It is never interpreted as Free.

### INV-009-002 — purchased credits survive plan/cycle changes

Purchased recovery credits:

- do not reset on paid billing-period rollover;
- do not reset on upgrade;
- do not reset on downgrade;
- do not reset on paid -> Free;
- do not reset on Free -> paid;
- remain attached to the durable Shop.

For a PAID_METERED plan the existing consumption order remains:

```text
1. current billing-period included recovery allowance
2. purchased recovery credits
3. ordinary paid overage
```

Therefore a new paid billing period uses fresh included capacity before spending
remaining purchased credits.

### INV-009-003 — paid -> Free is a plan change

```text
Paid -> Free
```

uses Shopify-hosted plan selection/pending update.

It is not implemented with `appSubscriptionCancel`.

### INV-009-004 — full cancellation requires human approval

V1:

```text
merchant request
-> human Admin triage
-> SUPER_ADMIN approval
-> Background Partner API call
-> provider/local verification
```

No support-message body or LLM classification may directly cancel.

### INV-009-005 — full-pack refund only

V1 supports one complete historical RecoveryCreditPurchase at a time.

No arbitrary credit quantity and no partial pack refund.

### INV-009-006 — pending refund capacity is held

After refund approval, selected credits must become unavailable before any
provider-side refund/correction begins.

Canonical purchased-credit availability after ARCH-009:

```text
available =
  max(
    grantedQuantity
    - committedQuantity
    - reservedQuantity
    - refundingQuantity,
    0
  )
```

### INV-009-007 — provider receipt is not refund completion

A negative App Event reaching `REPORTED` means submitted to Shopify.

It is not treated as proof of a completed cash refund.

V1 requires explicit human provider confirmation before local purchased capacity
is finally revoked.

### INV-009-008 — plan changes remain merchant-approved

For plan upgrades/downgrades, Moda sends the merchant to Shopify-hosted App
Pricing.

Admin may assist by sending the Change plan CTA.

Admin does not directly select or approve a merchant plan.

## External Shopify contract

### Hosted App Pricing

Merchant plan selection remains Shopify-owned.

Moda must not implement plan-change flows using:

```text
appSubscriptionCreate
billing.request
appPurchaseOneTimeCreate
```

### Partner appSubscriptionCancel

ARCH-009 uses Partner API cancellation with:

```text
appId
shopId
deferCancellation
prorate
skipFinalUsageCharge
```

Moda exposes exactly four cancellation modes:

| Moda mode | deferCancellation | prorate | skipFinalUsageCharge |
|---|---:|---:|---:|
| END_OF_CYCLE | true | false | false |
| IMMEDIATE_NO_PRORATION | false | false | false |
| IMMEDIATE_PRORATED | false | true | false |
| IMMEDIATE_SKIP_FINAL_USAGE | false | false | true |

No other boolean combination is legal.

In particular:

```text
prorate = true
AND
skipFinalUsageCharge = true
```

must never be emitted.

Shared owns this mapping.

### Negative App Events

A current-cycle pack usage correction is represented locally as:

```text
metric = RECOVERY_CREDIT_PACK_PURCHASE
quantity = -1
correctionOfUsageEventId = original +1 UsageEvent id
shopifyEventHandle = exact pack-meter snapshot
new permanent Shopify idempotency key
```

The existing Background App Events publisher remains the only App Events network
publisher.

### Cash refund of an already-paid charge

V1 uses Shopify Partner Dashboard.

Moda stores no duplicated refund amount/price.

`appCreditCreate` is not treated as a cash refund.

## Human approval boundary

### Merchant/support request

Creates durable REQUESTED state only.

### Admin

ADMIN may:

```text
read/triage
send Change plan action
create typed REQUESTED cancellation/refund lifecycle row
```

### SUPER_ADMIN

SUPER_ADMIN may:

```text
approve/reject cancellation
approve/reject refund
choose bounded cancellation mode
choose bounded refund settlement mode
record provider refund/correction confirmation
```

### Background

Background owns:

```text
Partner cancellation network call
refund hold/finalization
negative App Event creation
provider-aware reconciliation
```

Admin browser code never calls Shopify Partner API directly.

## Durable state

ARCH-009-DATABASE-001 adds:

```text
SubscriptionCancellationRequest
RecoveryCreditRefund
ShopEntitlementCounter.refundingQuantity
RecoveryCreditPurchaseStatus.REFUNDED
```

Cancellation identity:

```text
requestKey =
subscription-cancel:<shopId>:<providerSubscriptionIdSnapshot>
```

Refund identity:

```text
requestKey =
recovery-credit-refund:<purchaseId>
```

## Cancellation lifecycle

```text
REQUESTED
   |
   | SUPER_ADMIN approve
   v
APPROVED
   |
   v
PROCESSING
   |
   +---- retryable error ----> RETRYABLE
   |
   +---- permanent/identity problem ----> NEEDS_ATTENTION
   |
   +---- Partner accepted ----> PROVIDER_ACCEPTED
                                   |
                                   | provider projection confirms
                                   v
                                COMPLETED
```

Pre-provider terminal states:

```text
REJECTED
WITHDRAWN
```

Before cancellation, re-read Partner activeSubscription and require exact
provider-subscription and plan-handle snapshot identity.

If a newer subscription replaced the original, do not cancel it.

## Refund lifecycle

```text
REQUESTED
   |
   | SUPER_ADMIN approve
   v
APPROVED
   |
   | Background applies hold
   v
PROCESSING
   |
   +---- CURRENT_CYCLE_APP_EVENT_CORRECTION
   |       |
   |       +--> negative UsageEvent
   |       +--> PROVIDER_PENDING
   |       +--> correction REPORTED
   |       +--> PROVIDER_ACTION_REQUIRED
   |
   +---- PARTNER_DASHBOARD_REFUND
           |
           +--> PROVIDER_ACTION_REQUIRED

PROVIDER_ACTION_REQUIRED
   |
   | SUPER_ADMIN verifies provider-side action
   v
PROVIDER_CONFIRMED
   |
   | Background exactly-once finalization
   v
COMPLETED
```

Attention/terminal alternatives:

```text
REJECTED
WITHDRAWN
NEEDS_ATTENTION
```

### Refund hold

Approval processing:

```text
available >= purchase.creditsGranted
```

then:

```text
counter.refundingQuantity += purchase.creditsGranted
```

Purchase remains ACTIVE until provider confirmation.

### Completion

```text
counter.grantedQuantity   -= creditsSnapshot
counter.refundingQuantity -= creditsSnapshot
purchase.status            = REFUNDED
refund.status              = COMPLETED
```

Exactly once.

### Full-pack eligibility

Because purchased credits are pooled, V1 proves safe removal by:

```text
availablePurchasedRecoveryCredits(counter)
>=
purchase.creditsGranted
```

No per-credit provenance is invented.

## Refund settlement modes

### CURRENT_CYCLE_APP_EVENT_CORRECTION

Allowed only if:

```text
purchase ACTIVE
original +1 UsageEvent REPORTED
original billingPeriodId non-null
original billingPeriodId == current Subscription.billingPeriodId
current exact pack meter == purchase meter snapshot
current provider plan == purchase plan snapshot
```

Create one linked -1 UsageEvent.

`REPORTED` does not finalize the local refund.

### PARTNER_DASHBOARD_REFUND

Used for cash refund/already-paid charge or when current-cycle negative App Event
is not the right provider operation.

No synthetic negative UsageEvent.

Admin performs provider-side refund and records bounded provider confirmation.

## Refund-aware reconciliation

Pending refund:

```text
purchase remains ACTIVE
refund hold blocks entitlement use
```

Completed App Event correction:

```text
REFUNDED purchase is not reactivated
linked -1 represents provider meter reversal
```

Completed Partner Dashboard refund:

```text
historical +1 may remain visible in provider usage
do not regrant/refund again automatically
treat as explained historical operation
```

## Generic billing correction guard

Generic ARCH-007 Admin correction must reject:

```text
RECOVERY_CREDIT_PACK_PURCHASE
```

and direct to ARCH-009 refund workflow.

## Shared target

ARCH-009-SHARED-001 targets:

```text
@modainteract/moda-interact-shared@0.9.0
```

Shared owns:

```text
new billing SYSTEM codes
SubscriptionCancellationMode
mode -> Shopify cancellation args
availablePurchasedRecoveryCredits(...)
```

## Task graph

```text
ARCH-008-BACKGROUND-002
          |
          v
ARCH-009-DATABASE-001
          |
          v
ARCH-009-SHARED-001
       /      |       \
      v       v        v
SHOPIFY-001 BACKGROUND-001 BACKGROUND-002
      \       |        /
       \      |       /
        v     v      v
        ARCH-009-ADMIN-001
                 |
                 v
        ARCH-009-ADMIN-002
                 |
                 +----------------------+
                                        |
ARCH-007-ADMIN-004 ---------------------+
                                        |
                                        v
                               ARCH-009-ADMIN-003
                                        |
                                        v
                          ARCH-009-SYSTEM-TEST-001
                          terminal / manual-gated
```

ADMIN-001 also depends on ARCH-008-ADMIN-001 safe read primitives.

## Non-goals

- no automatic NLP financial approval;
- no Admin-selected merchant plan;
- no Billing API subscription creation;
- no partial pack refund;
- no arbitrary consumed-credit refund;
- no duplicated Shopify price/refund amount;
- no automatic refund completion inferred from REPORTED.

## Rollout order

1. complete ARCH-008-BACKGROUND-002;
2. DATABASE-001;
3. SHARED-001 and publish 0.9.0;
4. SHOPIFY-001, BACKGROUND-001, BACKGROUND-002;
5. ADMIN-001;
6. ADMIN-002;
7. complete/verify ARCH-007-ADMIN-004 if still pending;
8. ADMIN-003;
9. developer manual verification;
10. terminal/manual SYSTEM-TEST-001.

## Deterministic implementation-agent rule

Implementation agents must not invent:

- table/enum names;
- cancellation modes/provider booleans;
- refund settlement modes;
- plan-change mechanism;
- refund completion semantics;
- automatic financial authorization.

On genuine source-contract drift, STOP and return exact evidence.
