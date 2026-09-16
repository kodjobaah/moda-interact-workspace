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
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 2
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

## Completion Report

Status: Ready for architect review

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-BACKGROUND-003`

Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-BACKGROUND-003`

Claim commit: `6626d55eaa9c608b3cdb1b4046c30d3c19862df9`

Implementation commit: `d313ab2`

Implementation branch: `task/ARCH-015-BACKGROUND-003` (pushed)

Database submodule commit used: `47232f6876469f209c7efde4cefbb8a47d864e6a`

Implemented:

- Extended the existing billing cycle with bounded deterministic REQUESTED refund processing.
- Added exact Decimal PREPARE/RECONCILE processing using typed `RecoveryCreditRefund` evidence and the unique linked `UsageEvent` relation.
- Added live provider context, usage, pricing, currency, and post-correction economics proof.
- Added deterministic idempotency, atomic event/evidence preparation, concurrent CAS convergence, immutable reconciliation, and exact completion CAS.
- Added negative/fractional App Events support without changing positive purchase behavior.
- Preserved publisher retry/202 semantics; no separate queue, schema, metadata, or automatic Admin fallback was introduced.

Validation:

- Focused correction/provider/publisher/scheduler tests: 45 passed.
- `npm run test:unit`: 953 passed; 2 existing unrelated observability-startup assertions remain failing (recovery entrypoint source-shape expectation and stale Shared `0.9.0` expectation; repository dependency is `0.11.2`).
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed.
- No `typecheck` script is declared; the build runs `tsc` directly.

The prior blocked report was superseded because the integrated database submodule now exposes all required typed refund fields and the automatic correction relation. No `UsageEvent.metadata`, process-local settlement evidence, new queue, Prisma schema change, or Admin monetary fallback was used.


## Architect Review — Attempt 2

### Status

**Changes Requested — bounded Attempt 3 rework**

The overall automatic-refund workflow is directionally correct and the following Attempt-2
work is accepted and MUST NOT be redesigned:

```text
bounded deterministic REQUESTED scan on the existing billing cycle
PREPARE versus RECONCILE split by automaticCorrectionUsageEventId
negative/fractional UsageEvent support
exact Prisma.Decimal arithmetic for provider quantity/cost comparisons
typed RecoveryCreditRefund baseline / expected-after evidence
unique explicit automaticCorrectionUsageEventId relation
no UsageEvent.metadata / refund JSON settlement evidence
deterministic refund and Shopify idempotency keys
HTTP 202 / UsageEvent REPORTED is submission receipt only
exact provider quantity/cost/currency required before completion
WITHDRAWN purchase + zero reservations completion precondition
atomic purchase REFUNDED + counter decrement + refund COMPLETED CAS
providerConfirmedByPlatformAdminId = null on automatic completion
providerActionKind = null on automatic completion
no new queue / schema / Admin automatic provider action
```

Attempt 3 is limited to the five corrections below plus directly required focused tests.

---

### Finding 1 — native App Pricing provider context is incorrectly rejected

`readProvider()` currently derives provider context only when all of these are truthy:

```text
provider.providerSubscriptionId
provider.currentPeriodStart
provider.currentPeriodEnd
```

That reintroduces the legacy-id dependency removed elsewhere in ARCH-015. A valid native
App Pricing subscription may have:

```text
provider.providerSubscriptionId = null
planHandle = current provider plan
currentPeriodStart / currentPeriodEnd = valid provider cycle
```

while the frozen refund owns the Shared-derived:

```text
app-pricing:v1:<encoded planHandle>:<startIso>:<endIso>
```

Required correction:

1. Require valid provider period start/end for the cycle proof.
2. Call `deriveShopifyProviderContextIdentity(...)` with
   `providerSubscriptionId: provider.providerSubscriptionId` **even when it is null**.
3. Catch Shared derivation failure and return an unsafe/fail-closed provider proof; do not
   throw from the scheduler.
4. Compare the derived identity, plan, local BillingPeriod dates and exact event handle to
   the frozen refund provenance exactly as today.

Do not fabricate the derived identity into local `Subscription.providerSubscriptionId`.

Required regression:

```text
native App Pricing + null legacy provider id + matching plan/period/event
  -> PREPARE remains eligible
  -> correction can be prepared
```

---

### Finding 2 — RECONCILE incorrectly depends on live pricing after evidence is frozen

`readProviderState()` currently calls `readProvider()`, and `readProvider()` requires a
matching `providerUsagePricingSnapshot` entry. That requirement is correct for PREPARE,
because PREPARE must calculate expected post-correction economics from live Shopify
pricing. It is not correct for RECONCILE.

After `automaticCorrectionUsageEventId` and the typed expected-after fields are frozen,
RECONCILE must use only:

```text
fresh canonical provider context
frozen plan / period / event identity
exact live provider quantity
exact live provider cost
exact live provider currency
```

It must compare those values to:

```text
expectedProviderUsageQuantityAfterCorrection
expectedProviderUsageCostAfterCorrection
expectedProviderCurrency
```

It MUST NOT require current pricing to still be present or unchanged, and MUST NOT
recalculate the frozen expected-after economics.

Required implementation shape:

```text
readProviderState(refund)
  -> context + quantity + cost + currency only
  -> no providerUsagePricingSnapshot requirement

readProviderForPrepare(refund)
  -> call/read the same state proof
  -> additionally require the exact live pricing entry/currency
  -> expose pricing only to PREPARE calculation
```

Equivalent names are acceptable, but PREPARE and RECONCILE authority must be separated in
this way.

Required regression:

```text
linked REPORTED correction
+ exact matching live quantity/cost/currency/context
+ providerUsagePricingSnapshot absent/changed after submission
  -> refund can still complete from frozen evidence
```

---

### Finding 3 — unsafe PREPARE freezes the wrong expected monetary amount for partial packs

`markProviderActionRequired()` currently writes:

```text
expectedProviderAmount = purchaseProviderAmountSnapshot
```

for every manual fallback. This is incorrect when only part of the purchased credit pack
remains.

Example:

```text
creditsGranted = 4
finalCreditQuantity/currentAmount = 1
purchaseProviderAmountSnapshot = 20.00
ratio = 1 / 4
```

The frozen business refund evidence must be:

```text
expectedProviderAmount = 5.00
```

not `20.00`.

Required correction:

- derive the local business refund evidence before provider-dependent automatic proof;
- use the same exact Decimal ratio/value calculation for both the automatic and unsafe
  PREPARE paths;
- freeze:

```text
finalCreditQuantity = purchase.currentAmount
ratio = finalCreditQuantity / purchase.creditsGranted
expectedProviderAmount = purchaseProviderAmountSnapshot * ratio
expectedProviderCurrency = purchaseProviderCurrencySnapshot
```

using the same currency-rounding rule as the automatic path;
- do not use current Shopify pricing to derive the manual fallback amount;
- keep all four automatic correction baseline/expected-after fields null;
- keep `automaticCorrectionUsageEventId = null`.

Required regressions:

```text
partial pack + unsafe/ambiguous provider pricing
  -> PROVIDER_ACTION_REQUIRED
  -> no UsageEvent
  -> proportional expectedProviderAmount frozen

full unused pack + unsafe proof
  -> expectedProviderAmount equals original purchase amount
```

---

### Finding 4 — losing the refund-link CAS can commit a publishable orphan correction event

PREPARE currently performs:

```text
UsageEvent upsert
-> RecoveryCreditRefund updateMany(link event)
-> return linked: linked.count === 1
```

without rolling back when `linked.count !== 1`.

This is safe only for the narrow two-safe-worker race where another worker already linked
the same deterministic event. It is unsafe for a safe-versus-unsafe race:

```text
worker A proves safe automatic correction
worker B proves unsafe provider state
worker B first moves refund -> PROVIDER_ACTION_REQUIRED with no link
worker A upserts PENDING correction UsageEvent
worker A link CAS returns 0 because refund is no longer REQUESTED
worker A transaction currently commits the unlinked PENDING UsageEvent
existing publisher selects all due PENDING/RETRYABLE UsageEvents
-> Shopify correction may be submitted after manual fallback was selected
```

This violates the ARCH-015 no-double-settlement boundary.

Required correction:

- a PREPARE transaction that cannot establish the refund->UsageEvent link MUST NOT commit
  a newly prepared unlinked correction event;
- use the existing transaction/CAS pattern so a lost link CAS causes the transaction to
  roll back before reloading the current refund state;
- one acceptable deterministic implementation is:

```text
inside transaction:
  upsert deterministic correction event
  conditional refund link update
  if link count != 1:
    throw a dedicated internal prepare-race signal
    -> transaction rolls back this worker's event creation

outside transaction:
  catch only that dedicated race signal
  reload refund
  if automaticCorrectionUsageEventId is now non-null:
    enter RECONCILE
  else if refund is no longer REQUESTED:
    stop without creating/submitting an event
  else:
    leave for a later bounded retry / existing retry convention
```

A row-lock/re-read implementation is also acceptable if it proves the same invariant.
Do not merely delete an orphan after commit: the publisher may race that cleanup.

Required regressions:

```text
two safe PREPARE processors
  -> converge on one linked logical correction

safe PREPARE loses to concurrent PROVIDER_ACTION_REQUIRED transition
  -> no committed unlinked PENDING/RETRYABLE correction can remain publishable
  -> refund remains manual fallback
```

---

### Finding 5 — automatic completion omits the required billing system message/audit evidence

The task contract requires automatic completion to write the existing billing audit/system
message using current conventions. `complete()` currently updates the purchase, aggregate
counter and refund only.

Background already has the merchant billing system-message convention using:

```text
ARCH007_BILLING_CONTRACT_SCHEMA_VERSION
BILLING_SYSTEM_MESSAGE_CODES
createMerchantBillingSystemSourceKey(...)
MerchantSupportMessageKind.SYSTEM
MerchantSupportMessageState.AVAILABLE
merchantSupportThread upsert
merchantSupportMessage upsert
```

Attempt 3 must use that existing convention for automatic refund completion.

Required behavior:

- use `BILLING_SYSTEM_MESSAGE_CODES.REFUND_COMPLETED`;
- deterministic event identity must include the refund id (using `refund.id` directly is
  sufficient);
- create the bounded source key with `createMerchantBillingSystemSourceKey(...)`;
- upsert the merchant support thread for `refund.shopId`;
- upsert exactly one SYSTEM/AVAILABLE merchant support message with:

```text
systemCode = BILLING_REFUND_COMPLETED
systemVersion = current billing contract schema version
sourceLanguageTag = en-GB
sourceKey = deterministic refund-completion source key
```

- use a stable generic body such as:

```text
Your recovery-credit refund has completed. The refundable purchased credits have been removed and Shopify provider reconciliation is complete.
```

- update `merchantSupportThread.lastMessageAt` using the same completion timestamp;
- perform these writes in the successful completion transaction so a message failure does
  not leave financial state completed without the corresponding system evidence;
- replay/CAS must not create duplicate messages because the source key is deterministic.

Do not introduce a new audit table, queue or schema field.

Required regression:

```text
exact automatic completion
  -> one REFUND_COMPLETED system message
  -> replay does not duplicate it
  -> failed financial CAS does not publish completion message
```

---

### Attempt-3 authorized implementation surface

Keep changes within the existing BACKGROUND-003 surface:

```text
src/services/recovery-credit-refund-correction.service.ts
src/providers/shopify-partner-billing.provider.ts        # only if type/read separation requires it
src/services/shopify-usage-event-publisher.service.ts    # tests/compatibility only unless required
src/providers/shopify-app-events.provider.ts             # preserve accepted decimal behavior
tests/unit/services/recovery-credit-refund-correction.service.test.ts
# directly required provider/publisher/scheduler focused tests
```

The existing `src/entrypoints/billing.ts` invocation is accepted and should not be churned
unless a mechanical import/test adjustment is required.

No Prisma schema change. No new queue. No new refund status. No `UsageEvent.metadata`.
No Admin implementation in this attempt.

---

### Validation required for Attempt 3

Run the current repository commands and record exact results:

```bash
npm run test -- tests/unit/services/recovery-credit-refund-correction.service.test.ts
npm run test -- tests/unit/services/shopify-usage-event-publisher.service.test.ts
npm run test -- tests/unit/providers/shopify-app-events.provider.test.ts
npm run build
npm run test:unit
git diff --check
```

If the repository exposes additional focused billing scheduler/provider suites used in
Attempt 2, rerun those too.

The two documented unrelated observability baseline failures remain non-blocking only if
unchanged.

The pre-existing database P3009 remains a deployment/integration prerequisite and must not
be repaired inside this Background task.

### Stop condition

Return this SAME task through `/moda-task`.

Preserve:

```text
attempt: 2
status: ready
executor: null
claimed_at: null
```

The next authorized claim must increment to **Attempt 3 exactly once**.

Attempt 3 may return to review only when all five corrections above are implemented,
focused regression evidence passes, the task claim is cleared, and both worktrees are
clean and pushed.

`ARCH-015-ADMIN-001` remains Pending until BACKGROUND-003 is architect-accepted Complete.
