---
id: ARCH-015-BACKGROUND-003
architecture_id: ARCH-015
title: Scheduled recovery-credit refund correction and provider reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-001
- ARCH-015-BACKGROUND-001
- ARCH-015-SHOPIFY-003
enables:
- ARCH-015-ADMIN-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-BACKGROUND-003

## Objective

Use the existing 60-second billing worker cycle to discover durable REQUESTED recovery-credit refunds, submit a safe negative/fractional App Event correction when provable, reconcile provider evidence, and complete the refund only after exact provider proof.

No new queue is authorized.

## Authorized implementation surface

```text
src/entrypoints/billing.ts
src/services/recovery-credit-refund-correction.service.ts    # new
src/services/shopify-usage-event-publisher.service.ts
src/providers/shopify-app-events.provider.ts
src/providers/shopify-partner-billing.provider.ts
src/services/billing-reconciliation.service.ts               # only shared provider read orchestration if needed
tests/unit/services/recovery-credit-refund-correction.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
tests/unit/providers/shopify-app-events.provider.test.ts
# direct billing entrypoint/scheduler tests
```

No Prisma schema changes.

## Invocation

Extend the existing billing cycle:

```text
billingReconciliationService.reconcileOnce()
recoveryCreditRefundCorrectionService.processDue()
subscriptionReconciliation.reconstruct()
```

Preserve existing scheduler interval/worker lifecycle unless a current code dependency requires equivalent ordering.

`processDue()` selects a bounded deterministic page of:

```text
RecoveryCreditRefund.status = REQUESTED
ORDER BY createdAt ASC, id ASC
```

Do not process `PROVIDER_ACTION_REQUIRED`, `COMPLETED`, `REJECTED`, `CANCELLED` as automatic corrections.

## Automatic correction eligibility

Reload refund + purchase + aggregate.

Require:

- purchase `WITHDRAWN`;
- refund still REQUESTED;
- purchase currentAmount > 0 after any reserved usage has settled;
- purchase reservedAmount == 0 before provider correction;
- positive original providerPurchaseAmount;
- current Shopify provider context still matches purchase snapshots;
- event handle exists live;
- current provider usage/cost/currency available;
- current provider pricing can deterministically calculate the expected post-correction monetary state.

Final credit quantity for refund is purchase.currentAmount once reservations have drained.

Correction ratio:

```text
ratio = finalCreditQuantity / purchase.creditsGranted
correctionValue = -ratio
```

Require `0 < ratio <= 1`.

## Safe provider-economics proof

Before creating correction UsageEvent:

1. capture exact current provider quantity/cost/currency;
2. calculate `expectedQuantityAfter = quantityBefore + correctionValue`;
3. calculate expected provider cost-after from the live Shopify pricing structure, not ARCH-014 stored price;
4. calculate expected monetary reduction;
5. compare expected provider reduction with proportional business refund amount derived from original `providerPurchaseAmount * ratio` using exact currency rounding;
6. only automatic-submit when the expected amounts agree exactly under the supported pricing mode.

If pricing cannot be evaluated exactly/safely, transition the refund to `PROVIDER_ACTION_REQUIRED`; do not invent an App Event.

## Correction UsageEvent

Create/reuse exactly one deterministic UsageEvent for refund:

```text
metric = RECOVERY_CREDIT_PACK_PURCHASE
quantity = negative Decimal correctionValue
correctionOfUsageEventId = original purchase.usageEventId
sourceType = RECOVERY_CREDIT_REFUND
sourceId = refund.id
shopifyEventHandle = purchase.shopifyEventHandleSnapshot
shopifyReportState = PENDING
idempotencyKey = deterministic from refund id
shopifyIdempotencyKey = deterministic stable key
```

Store immutable correction baseline/expected evidence in `UsageEvent.metadata` as decimal strings:

```text
schemaVersion
refundId
providerContextIdentity
providerPlanHandle
billingPeriodId
eventHandle
quantityBefore
costBefore
currency
correctionValue
expectedQuantityAfter
expectedCostAfter
expectedRefundAmount
expectedRefundCurrency
```

Concurrent processors must reuse the existing correction event through unique idempotency handling.

## App Events client

Allow finite non-zero numeric/decimal event values, including negative/fractional.

Retain all existing authentication, timestamp, handle and idempotency validation.

Purchase +1 remains valid unchanged.

## 202 semantics

Existing publisher may mark correction UsageEvent `REPORTED` when Shopify accepts submission. That means submitted/accepted only.

Refund remains REQUESTED.

On a later scheduler cycle, if correction event is REPORTED:

1. re-read Shopify provider usage;
2. compare exact quantity/cost/currency with frozen correction metadata;
3. only when exact expected after-state is observed complete locally.

If provider has not caught up, keep REQUESTED and do not create another logical correction.

If provider state conflicts irreconcilably with frozen evidence, move refund to NEEDS_ATTENTION; do not issue a second correction.

## Completion transaction

On exact provider proof:

- require purchase still WITHDRAWN;
- require reservedAmount == 0;
- require currentAmount == frozen finalCreditQuantity;
- reduce purchase currentAmount to 0;
- set purchase REFUNDED;
- decrement aggregate `refundingQuantity` and `grantedQuantity` by final quantity;
- persist refund provider evidence/confirmedAt from reconciled automatic correction;
- set refund COMPLETED/completedAt;
- write existing billing audit/system message using existing conventions.

No Admin action is required for this automatic path.

## Unsafe path

When safe automatic correction cannot be derived BEFORE any correction event submission:

- freeze finalCreditQuantity/expectedProviderAmount/currency using existing fields;
- set refund `PROVIDER_ACTION_REQUIRED`;
- record bounded reason;
- leave purchase WITHDRAWN and aggregate hold intact;
- ADMIN-001 owns external REFUND/CREDIT evidence.

Once a correction event has been submitted, do not fall back to a second monetary action merely because reconciliation is delayed. Use REQUESTED/NEEDS_ATTENTION reconciliation path.

## Required tests

- billing scheduler invokes processDue;
- no separate BullMQ queue required;
- bounded deterministic REQUESTED scan;
- full unused pack => correction -1 when safe;
- partially used pack => fractional correction, e.g. -0.25, when safe;
- Decimal quantity baseline/after-state;
- safe live pricing yields expected amount;
- unsafe tier/nonlinear case routes PROVIDER_ACTION_REQUIRED before submission;
- period/provider-context mismatch routes manual fallback before submission;
- deterministic one correction event under concurrent processors;
- App Events client accepts negative/fractional non-zero;
- 202 leaves refund REQUESTED;
- later exact provider proof completes automatically;
- delayed provider reflection does not duplicate correction;
- conflicting post-submission provider evidence => NEEDS_ATTENTION;
- automatic completion decrements entitlement exactly once;
- automatic completion requires no Admin mutation.

## Stop conditions

STOP if:

- exact safe partial correction requires provider information not exposed by the current Partner API;
- a new queue/model/refund status is required;
- code would permit Admin monetary fallback after a correction event may already have been accepted without first proving no provider action occurred.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
