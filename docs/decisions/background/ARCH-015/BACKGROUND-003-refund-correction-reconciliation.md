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
- ARCH-015-DATABASE-002
- ARCH-015-BACKGROUND-001
- ARCH-015-SHOPIFY-003
enables:
- ARCH-015-ADMIN-001
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-BACKGROUND-003

## Objective

Use the existing 60-second billing worker cycle to discover durable REQUESTED recovery-credit refunds, prepare and submit a safe negative/fractional Shopify App Event correction when provable, reconcile provider evidence, and complete the refund only after exact provider proof.

No new queue is authorized.

`RecoveryCreditRefund` is the authoritative settlement workflow/evidence record. `UsageEvent` is the provider-event submission record. Do not place authoritative refund settlement evidence in generic JSON metadata.

## Required prerequisite schema

`ARCH-015-DATABASE-002` must be architect-accepted Complete before this task can be claimed.

The integrated Prisma client must expose exactly:

```text
RecoveryCreditRefund.automaticCorrectionUsageEventId
RecoveryCreditRefund.automaticCorrectionUsageEvent
RecoveryCreditRefund.providerUsageQuantityBeforeCorrection
RecoveryCreditRefund.providerUsageCostBeforeCorrection
RecoveryCreditRefund.expectedProviderUsageQuantityAfterCorrection
RecoveryCreditRefund.expectedProviderUsageCostAfterCorrection
```

Reuse existing refund provenance/economic fields:

```text
providerSubscriptionIdSnapshot
planHandleSnapshot
billingPeriodIdSnapshot
eventHandleSnapshot
purchaseProviderAmountSnapshot
purchaseProviderCurrencySnapshot
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
```

If those ARCH-015-DATABASE-002 fields are unavailable, STOP. Do not replace them with `UsageEvent.metadata`, another JSON blob, or process-local state.

## Authorized implementation surface

```text
src/entrypoints/billing.ts
src/services/recovery-credit-refund-correction.service.ts    # new
src/services/shopify-usage-event-publisher.service.ts
src/providers/shopify-app-events.provider.ts
src/providers/shopify-partner-billing.provider.ts
src/services/billing-reconciliation.service.ts               # only shared provider read orchestration if needed
# directly required billing types/helpers
tests/unit/services/recovery-credit-refund-correction.service.test.ts
tests/unit/services/shopify-usage-event-publisher.service.test.ts
tests/unit/providers/shopify-app-events.provider.test.ts
# direct billing entrypoint/scheduler tests
```

No Prisma schema changes in this Background task.

## Invocation

Extend the existing billing cycle:

```text
billingReconciliationService.reconcileOnce()
recoveryCreditRefundCorrectionService.processDue()
subscriptionReconciliation.reconstruct()
```

Preserve the existing scheduler interval/worker lifecycle unless current code requires equivalent ordering for correctness.

`processDue()` selects a bounded deterministic page of:

```text
RecoveryCreditRefund.status = REQUESTED
ORDER BY createdAt ASC, id ASC
```

Do not automatically process `PROVIDER_ACTION_REQUIRED`, `COMPLETED`, `REJECTED` or `CANCELLED`.

A `NEEDS_ATTENTION` refund is reconciliation/operations work and must not automatically submit another correction.

## Two phases: PREPARE versus RECONCILE

Every REQUESTED refund must take exactly one of these paths:

```text
automaticCorrectionUsageEventId IS NULL
  -> PREPARE phase

automaticCorrectionUsageEventId IS NOT NULL
  -> RECONCILE phase
```

The worker MUST NOT recalculate/rewrite correction baseline or expected-after evidence after `automaticCorrectionUsageEventId` has been persisted.

That link is the durable boundary proving an automatic provider correction has been prepared.

## PREPARE phase — automatic correction eligibility

Reload refund + purchase + aggregate and require:

- refund still `REQUESTED`;
- `automaticCorrectionUsageEventId IS NULL`;
- purchase `WITHDRAWN`;
- purchase `currentAmount > 0` after any reserved usage has settled;
- purchase `reservedAmount == 0` before provider correction;
- positive original `providerPurchaseAmount`;
- current Shopify provider context matches frozen purchase/refund provenance;
- event handle exists in the live provider subscription;
- current provider usage quantity/cost/currency are available as exact Decimal-compatible values;
- current provider pricing can deterministically calculate the post-correction monetary state.

Final credit quantity:

```text
finalCreditQuantity = purchase.currentAmount
```

Correction ratio/value:

```text
ratio           = finalCreditQuantity / purchase.creditsGranted
correctionValue = -ratio
```

Require:

```text
0 < ratio <= 1
```

Use exact Decimal arithmetic. Do not use binary floating-point arithmetic for quantity/cost/refund proof.

## Safe provider-economics proof

Before preparing a correction:

1. capture exact live provider quantity/cost/currency;
2. derive `correctionValue` as exact Decimal;
3. calculate `expectedQuantityAfter = quantityBefore + correctionValue`;
4. calculate expected provider cost-after from the **live Shopify pricing structure**, not ARCH-014 stored pricing;
5. calculate expected provider monetary reduction;
6. derive proportional business refund from original `providerPurchaseAmount * ratio` using exact currency rounding;
7. require live provider cost currency == `purchaseProviderCurrencySnapshot`;
8. require calculated refund currency == that same currency;
9. require provider monetary reduction == calculated business refund exactly under the supported pricing mode.

If any proof is unavailable/ambiguous, transition to `PROVIDER_ACTION_REQUIRED` **before creating any correction UsageEvent**. Do not invent an App Event.

## Atomic automatic correction preparation

When safe automatic correction is proven, create the correction UsageEvent and freeze refund evidence in one transaction.

Create/reuse exactly one UsageEvent:

```text
metric = RECOVERY_CREDIT_PACK_PURCHASE
quantity = negative Decimal correctionValue
correctionOfUsageEventId = original purchase.usageEventId
sourceType = RECOVERY_CREDIT_REFUND
sourceId = refund.id
shopifyEventHandle = refund.eventHandleSnapshot
shopifyReportState = PENDING
idempotencyKey = deterministic from refund id
shopifyIdempotencyKey = deterministic stable Shopify key from refund id
```

In the **same transaction**, update `RecoveryCreditRefund` with:

```text
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
providerUsageQuantityBeforeCorrection
providerUsageCostBeforeCorrection
expectedProviderUsageQuantityAfterCorrection
expectedProviderUsageCostAfterCorrection
automaticCorrectionUsageEventId = correction UsageEvent.id
```

Exact ownership:

```text
RecoveryCreditRefund
  owns provider context / plan / period / meter provenance
  owns final credit quantity and expected monetary refund
  owns observed provider baseline and expected provider after-state
  points to exactly one automatic correction UsageEvent

UsageEvent
  owns correction quantity
  owns correctionOfUsageEventId
  owns provider event handle/idempotency/reporting state
  owns provider submission error/response summary
```

Do NOT add/use:

```text
UsageEvent.metadata
refund metadata JSON
process-local frozen evidence
```

Concurrent processors must converge on the same correction UsageEvent through `request/refund id` deterministic keys, the unique refund->UsageEvent link and existing transactional/CAS conventions. A losing concurrent processor must reload and enter RECONCILE rather than create a second logical correction.

## Immutability after preparation

Once `automaticCorrectionUsageEventId` is non-null:

- never change the linked UsageEvent id;
- never change its correction quantity for retry;
- never overwrite the four correction baseline/expected-after fields;
- never recalculate `finalCreditQuantity`, `expectedProviderAmount` or `expectedProviderCurrency` from current provider state;
- retries reuse the existing UsageEvent and Shopify idempotency key;
- provider reconciliation compares live state to frozen refund evidence only.

If frozen automatic evidence is structurally incomplete despite database constraints, move to `NEEDS_ATTENTION`/fail closed; do not repair it by guessing.

## App Events client

Allow finite non-zero Decimal-compatible event values, including negative/fractional values.

Examples:

```text
1
-1
-0.25
-0.5
```

Retain authentication, timestamp, handle and idempotency validation.

Normalize provider/App Event numeric inputs to exact Decimal-compatible canonical strings/values before arithmetic/submission. Do not round quantities to integers and do not use JS binary-float equality for reconciliation.

Purchase `+1` remains valid unchanged.

## 202 semantics

The existing publisher may transition the linked correction UsageEvent to `REPORTED` after Shopify accepts submission.

That means provider submission accepted only.

It MUST NOT transition the refund to `COMPLETED`.

The refund remains REQUESTED until a later RECONCILE cycle proves exact provider state.

## RECONCILE phase

For `REQUESTED` refunds with `automaticCorrectionUsageEventId != null`:

1. load the linked correction UsageEvent through the explicit relation;
2. validate it belongs to this refund:
   - `sourceType == RECOVERY_CREDIT_REFUND`;
   - `sourceId == refund.id`;
   - `correctionOfUsageEventId == purchase.usageEventId`;
   - `shopifyEventHandle == refund.eventHandleSnapshot`;
   - quantity is finite, negative and non-zero;
3. validate the typed frozen evidence is complete;
4. if UsageEvent is `PENDING`/`IN_FLIGHT`/`RETRYABLE`, leave refund REQUESTED and let the existing publisher/retry machinery operate;
5. if UsageEvent is `REPORTED`, read fresh Shopify provider state;
6. derive current provider context with Shared and require it still matches the frozen refund context;
7. require provider currency == `expectedProviderCurrency`;
8. compare exact current provider quantity with `expectedProviderUsageQuantityAfterCorrection`;
9. compare exact current provider cost with `expectedProviderUsageCostAfterCorrection`;
10. only exact proof may complete the refund.

If Shopify has not yet reflected the expected state, leave REQUESTED. Do not create another event and do not mutate frozen evidence.

If provider state irreconcilably conflicts with the frozen evidence after the correction has been reported, set `NEEDS_ATTENTION`. Do not route to manual monetary fallback because a provider correction may already have occurred.

If linked UsageEvent is itself `NEEDS_ATTENTION`, refund must not complete or fall back automatically; keep/transition refund to `NEEDS_ATTENTION` using existing safe conventions.

## Completion transaction

On exact provider proof, use existing transaction/CAS conventions and require:

```text
refund.status == REQUESTED
refund.automaticCorrectionUsageEventId == linked event id
purchase.status == WITHDRAWN
purchase.reservedAmount == 0
purchase.currentAmount == refund.finalCreditQuantity
```

Then atomically:

- set purchase `currentAmount = 0`;
- set purchase `REFUNDED`;
- decrement aggregate `refundingQuantity` by exact `finalCreditQuantity`;
- decrement aggregate `grantedQuantity` by exact `finalCreditQuantity`;
- persist reconciled automatic provider amount/currency into existing refund provider evidence fields;
- set `providerConfirmedAt`;
- leave `providerConfirmedByPlatformAdminId = null`;
- leave `providerActionKind = null` because no Admin REFUND/CREDIT action occurred;
- set refund `COMPLETED` and `completedAt`;
- preserve the automatic correction UsageEvent link/evidence permanently;
- write existing billing audit/system message using current conventions.

No Admin mutation is required on this automatic path.

## Unsafe PREPARE path

When a safe automatic correction cannot be derived **before** any automatic correction UsageEvent has been linked/submitted:

- freeze `finalCreditQuantity`, `expectedProviderAmount`, `expectedProviderCurrency` using existing typed refund fields;
- leave all four automatic correction baseline/expected-after fields null;
- leave `automaticCorrectionUsageEventId = null`;
- set refund `PROVIDER_ACTION_REQUIRED`;
- record bounded reason;
- leave purchase `WITHDRAWN` and aggregate refund hold intact;
- `ARCH-015-ADMIN-001` owns external REFUND/CREDIT evidence.

Once `automaticCorrectionUsageEventId` is non-null, this manual fallback is forbidden until architect/operator reconciliation proves no provider monetary action can have occurred.

## Required tests

### Invocation and selection

- billing scheduler invokes `processDue()`;
- no separate BullMQ refund queue is created;
- bounded deterministic REQUESTED scan;
- non-REQUESTED terminal/manual states are not auto-submitted.

### Preparation

- full unused pack => exact correction `-1` when safe;
- partially used pack => exact fractional correction (for example `-0.25`) when safe;
- provider quantity/cost inputs are normalized to exact Decimals;
- safe live Shopify pricing yields expected amount;
- ARCH-014 stored pricing is not used for provider settlement proof;
- unsafe/non-deterministic pricing routes `PROVIDER_ACTION_REQUIRED` before event creation;
- provider-context/period/event mismatch routes manual fallback before event creation;
- live currency mismatch routes safe manual fallback before event creation;
- preparation writes exactly one UsageEvent + typed refund evidence + FK atomically;
- no `UsageEvent.metadata` access exists;
- concurrent PREPARE calls converge on one linked correction event.

### Immutability/idempotency

- later cycles never overwrite baseline/expected-after evidence;
- later cycles never change correction quantity;
- deterministic Shopify idempotency key is reused;
- delayed publisher retry does not create another logical correction.

### Reconciliation

- HTTP 202 / UsageEvent REPORTED alone leaves refund REQUESTED;
- exact later provider quantity/cost/currency proof completes automatically;
- provider not yet caught up leaves REQUESTED with frozen evidence unchanged;
- conflicting post-submission provider evidence => NEEDS_ATTENTION;
- linked UsageEvent NEEDS_ATTENTION cannot complete or manual-fallback automatically;
- automatic completion decrements entitlement exactly once;
- automatic completion has `providerConfirmedByPlatformAdminId = null` and `providerActionKind = null`;
- automatic completion requires no Admin action.

### Regression

- purchase `+1` App Events remain supported;
- existing purchase reconciliation remains unchanged;
- integer and fractional provider quantities both reconcile exactly.

## Validation

Inspect `package.json`, then run exact repository scripts plus at minimum:

```text
npm test -- --runInBand   # adapt to current test runner syntax; do not invent unsupported flags
npm run typecheck
npm run build
git diff --check
```

Run focused suites for the correction service, publisher, App Events provider and billing scheduler. Record any unrelated baseline failure separately; do not weaken ARCH-015 focused assertions.

## Stop conditions

STOP and return evidence to `moda_architect` if:

- `ARCH-015-DATABASE-002` typed fields/relation are unavailable;
- exact safe correction needs provider information not exposed by the current Shopify provider surface;
- another queue/model/refund status/schema field is required;
- existing publisher semantics cannot reuse one deterministic linked UsageEvent safely;
- automatic correction attribution can be made safe only by inventing mutable/process-local baseline state;
- code would permit Admin monetary fallback after an automatic correction may have been submitted without first proving no provider action occurred;
- implementation would require `UsageEvent.metadata` or another untyped authoritative settlement payload.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
