---
id: ARCH-009-SHOPIFY-001
architecture_id: ARCH-009
title: Add merchant plan-change, cancellation-request and pack-refund-request UX
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-008-SHOPIFY-001
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-009-ADMIN-001
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-009-SHOPIFY-001

## Objective

Merchant-safe:

```text
Change plan
Switch to Free
Request cancellation
Request full-pack refund
```

## Adopt

Exact Shared 0.9.0 and accepted ARCH-009 DB revision.

If unavailable, STOP.

## Change plan / Switch to Free

Use existing Shopify-hosted pricing route.

Do not introduce:

```text
appSubscriptionCreate
billing.request
appPurchaseOneTimeCreate
```

Merchant chooses/approves plan in Shopify.

## Cancellation request

Merchant exposes only:

```text
Request cancellation at end of billing cycle
```

Form:

```text
intent = REQUEST_SUBSCRIPTION_CANCELLATION
requestId = server/loader UUID
```

Browser cannot submit mode/provider ID/plan.

Server reloads Shop+Subscription and requires:

```text
ACTIVE or TRIALING
providerSubscriptionId non-null
observedShopifyPlanHandle non-null
```

Create/replay key:

```text
subscription-cancel:<shopId>:<providerSubscriptionId>
```

Persist:

```text
source MERCHANT_UI
providerSubscriptionIdSnapshot
planHandleSnapshot
currentPeriodEndSnapshot
mode END_OF_CYCLE
status REQUESTED
```

Create exactly one:

```text
BILLING_CANCELLATION_REQUEST_RECEIVED
```

SYSTEM message.

No Partner call.

## Refund request

Bounded same-shop purchase list.

Refund action only for ACTIVE purchase.

Form:

```text
intent = REQUEST_RECOVERY_CREDIT_REFUND
refundRequestId = server/loader UUID
purchaseId
```

Ignore client:

```text
credits
price
plan
meter
billingPeriod
settlementMode
```

Reload purchase+UsageEvent.

Create/replay:

```text
recovery-credit-refund:<purchaseId>
```

Snapshots:

```text
originalUsageEventIdSnapshot
billingPeriodIdSnapshot
planHandleSnapshot
eventHandleSnapshot
creditsSnapshot
status REQUESTED
```

Create one:

```text
BILLING_REFUND_REQUEST_RECEIVED
```

No hold/decrement/correction/provider call.

## Purchased-credit display

Use Shared availability including refundingQuantity.

Display:

```text
Granted
Committed
Reserved
Pending refund
Available
```

## Support CTA

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
-> /app/billing
-> Change plan
```

Unknown system code no action.

## i18n

All 20 merchant locales.

Required meanings:

```text
Change plan
Switch to Free
Request cancellation
Cancellation requested
Request refund
Refund requested
Pending refund
Full-pack refund only
Refund availability warning
```

Placeholder parity.

## Tests

1. paid plan does not mutate Free counter;
2. hosted Change plan;
3. hosted Switch to Free;
4. no forbidden create APIs;
5. cancellation always END_OF_CYCLE;
6. immediate mode cannot be supplied;
7. cancellation replay one row;
8. no provider call;
9. refund ignores client price/credits/meter;
10. cross-shop purchase rejected;
11. refund replay one row;
12. no hold/decrement on request;
13. availability subtracts refunding;
14. plan-change SYSTEM CTA exact;
15. all 20 locales resolve.

## Validation

```bash
npm test
npm run typecheck
npm run build
npm run prisma:validate
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
