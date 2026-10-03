---
id: ARCH-027-BACKGROUND-005
architecture_id: ARCH-027
title: Prepare and reconcile WooCommerce one-time-charge refunds
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-004
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Prepare and reconcile WooCommerce one-time-charge refunds

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing purchase-lot refund workflow to Woo one-time charges without inventing a second refund ledger or fabricating Shopify correction evidence.

The task has two bounded responsibilities:

```text
A. PREPARE LOCAL WOO REFUND HOLDS

RecoveryCreditRefund(provider = WOOCOMMERCE, status = REQUESTED)
        |
        | wait until reserved credits settle/release
        v
freeze:
    finalCreditQuantity
    expectedProviderAmount
    expectedProviderCurrency
        |
        v
status = PROVIDER_ACTION_REQUIRED
        |
        v
vendor/admin performs the refund in Woo's SaaS vendor dashboard
```

and:

```text
B. RECONCILE VERIFIED WOO REFUND WEBHOOK

WooCommerceBillingWebhookReceipt
    topic = saas_billing_contract.refunded
    normalizedPayload.charge exists
        |
        v
resolve exact ONE_TIME_CHARGE operation + purchase
        |
        v
resolve exact existing Woo RecoveryCreditRefund hold
        |
        v
read amount_refunded from the originally activated provider transaction
        |
        +-- exact frozen expected amount
        |      -> purchase REFUNDED
        |      -> purchased counter decremented
        |      -> refund COMPLETED
        |
        `-- mismatch
               -> refund NEEDS_ATTENTION
               -> preserve provider evidence
        |
        v
receipt processed atomically with the local transition
```

This task does **not** initiate a refund through a Woo HTTP API.

Woo's public SaaS Billing documentation currently describes merchant refund requests and vendor approval/rejection through the Woo vendor dashboard. It does not document a vendor refund-initiation endpoint that Moda can safely call for this workflow.

Automatic arbitrary partial Woo refund initiation therefore remains a sandbox/provider capability gate.

## Context

ARCH-027 preserves the existing ARCH-015 business rule:

```text
refundableCredits =
    currentAmount
    - reservedAmount
```

A refund belongs to one exact `RecoveryCreditPurchase`.

Consumed credits are never restored.

Reserved credits may finish or release while the purchase is on refund hold. The existing purchased-credit reservation service already preserves this invariant:

- commit reduces the withdrawn lot's `currentAmount`;
- release increases the aggregate `refundingQuantity` for a withdrawn lot;
- when no credits remain the live refund is canceled as `NO_CREDITS_REMAINING`.

The current Shopify refund architecture is deliberately more complex at the provider edge:

```text
REQUESTED
    -> prepare negative/fractional Shopify correction UsageEvent
    -> provider App Event reporting/reconciliation
    -> exact settlement proof
```

Woo must not use that path.

### Provider facts

Woo's current Marketplace SaaS Billing documentation, verified 3 October 2026, states:

- merchants may request refunds for one-time charges;
- the vendor receives a notification and reviews pending requests in the vendor dashboard;
- the vendor approves or rejects the refund in that provider workflow;
- approving a refund cancels the underlying SaaS contract;
- Woo sends `saas_billing_contract.refunded` and `saas_billing_contract.canceled`;
- the refunded amount is available in `amount_refunded` on the latest transaction.

Provider reference:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

The public documentation does **not** establish that the vendor can programmatically initiate an arbitrary proportional refund amount for a one-time charge.

Therefore ARCH-027 v1 uses:

```text
Moda local refund hold
    -> PROVIDER_ACTION_REQUIRED
    -> provider dashboard action
    -> signed refunded webhook
    -> Background reconciliation
```

and retains the existing `NEEDS_ATTENTION` safety state when provider settlement does not match Moda's frozen business expectation.

### Tax / provider amount basis

BACKGROUND-004 stores:

```text
RecoveryCreditPurchase.providerPurchaseAmount
```

as the provider transaction amount observed after Woo checkout.

That amount may include Woo-added merchant tax.

Woo refund expectation is therefore calculated from the frozen **provider purchase amount**, not from `WooCommerceBillingOperation.quotedAmountMinor`.

For a fully unused 10-credit purchase:

```text
provider purchase amount = 12.00
finalCreditQuantity      = 10
creditsGranted           = 10

expected provider refund = 12.00
```

For 4 remaining credits:

```text
12.00 * (4 / 10) = 4.80
```

using the same exact Decimal proportional-money semantics already accepted by ARCH-015.

This preserves the distinction:

```text
operation quotedAmountMinor
    = Moda pre-tax catalogue quote sent to Woo

purchaseProviderAmountSnapshot
    = provider transaction value used for provider refund economics
```

## Scope

Modify only `moda-interact-background` implementation/tests required for:

1. provider-aware routing of existing refund-correction work;
2. Woo refund-hold preparation;
3. bounded claiming of Woo `refunded` charge receipts;
4. Woo provider refund evidence reconciliation;
5. exact local refund completion / needs-attention state;
6. integration into the existing leased billing cycle.

Expected production areas conceptually:

```text
src/services/
  recovery-credit-refund-correction.service.ts
  woocommerce-billing/
    charge-refund-reconciliation.service.ts
    charge-refund-evidence.ts

src/entrypoints/billing.ts
```

Exact filenames may differ where the accepted Background refactor gives a clearer owner.

Reuse:

- existing refund/purchase/counter transaction patterns;
- accepted Woo receipt-claiming helpers;
- existing `RecoveryCreditRefundStatus`;
- existing `RecoveryCreditProviderActionKind`;
- existing refund support-message code;
- Shared structured logging.

Update the nested `database/` gitlink to the newest compatible architect-accepted ARCH-027 database main commit and regenerate Prisma.

## Out of Scope

- Creating the merchant-facing Woo refund request.
- Purchase-history/refund API.
- Woo Admin refund UI.
- Automatically approving/rejecting Woo vendor-dashboard refund requests.
- Calling an undocumented Woo refund API.
- Partial-refund provider initiation.
- Subscription refunds.
- Shopify automatic correction redesign.
- Creating a Woo-specific refund table/status enum.
- Re-granting consumed credits.
- Refunding reserved credits before they settle/release.
- Admin resolution UX for `NEEDS_ATTENTION`.
- Gateway/infrastructure changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Existing Shopify automatic refund worker becomes explicitly Shopify-only

The current `RecoveryCreditRefundCorrectionService` selects:

```text
status = REQUESTED
```

and assumes Shopify plan/meter/provider state.

Before any Woo refund producer is introduced, narrow that existing automatic correction scan to:

```text
provider = SHOPIFY
status = REQUESTED
```

Preserve all accepted ARCH-015 Shopify behavior, ordering, meter serialization, correction `UsageEvent`, provider proof and completion semantics.

A Woo `REQUESTED` refund MUST NOT create:

```text
automaticCorrectionUsageEventId
shopify correction UsageEvent
shopifyEventHandle
shopifyIdempotencyKey
```

or call Shopify provider reconciliation.

### R2 — Run Woo refund work in the existing leased billing cycle

Use the existing `BILLING_RECONCILIATION` leased cycle.

Execution order is:

```text
1. BACKGROUND-002 recurring subscription receipts
2. BACKGROUND-003 local Woo period rollover
3. BACKGROUND-004 Woo charge acquisition
4. BACKGROUND-005 Woo refund preparation/reconciliation
5. existing Shopify refund correction processing
```

The final Shopify step remains provider-filtered by R1.

Do not create a new worker, queue, lease or cron.

### R3 — Prepare at most 50 Woo refund requests per cycle

Define:

```text
MAX_WOO_REFUNDS_TO_PREPARE_PER_CYCLE = 50
```

Select:

```text
RecoveryCreditRefund.provider = WOOCOMMERCE
RecoveryCreditRefund.status = REQUESTED
```

ordered by:

```text
createdAt ASC,
id ASC
```

Attempt each selected refund at most once in one leased cycle.

Preparation is local database work only and does not require a webhook receipt.

### R4 — Woo refund producer contract

A future Woo purchase-history/refund API task will create the local hold.

BACKGROUND-005 expects the producer to have atomically created:

```text
RecoveryCreditRefund
    provider = WOOCOMMERCE
    status = REQUESTED
    source = MERCHANT_UI | MERCHANT_SUPPORT | ADMIN
    purchaseId = exact purchase lot
    purchaseCreditsGrantedSnapshot = purchase.creditsGranted
    currentAmountAtRequestSnapshot = purchase.currentAmount
    reservedAmountAtRequestSnapshot = purchase.reservedAmount
    availableAmountAtRequestSnapshot =
        purchase.currentAmount - purchase.reservedAmount

    billingPeriodIdSnapshot =
        purchase.billingPeriodId  # nullable for Woo Free

    providerSubscriptionIdSnapshot =
        purchase.providerSubscriptionIdSnapshot

    planHandleSnapshot = NULL
    eventHandleSnapshot = NULL
    shopifyPartnerDevelopmentSnapshot = false

    purchaseProviderAmountSnapshot =
        purchase.providerPurchaseAmount

    purchaseProviderCurrencySnapshot =
        purchase.providerPurchaseCurrency

    holdAppliedAt != NULL
```

and:

```text
purchase.status = WITHDRAWN

ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
    refundingQuantity += availableAmountAtRequestSnapshot
```

BACKGROUND-005 does not create the initial merchant/admin refund hold.

### R5 — Refund/purchase provider identity must match

Before preparation require:

```text
refund.provider = WOOCOMMERCE
purchase.provider = WOOCOMMERCE
refund.shopId = purchase.shopId
```

Require the purchase has:

```text
providerReference non-blank
providerPurchaseAmount > 0
providerPurchaseCurrency = USD
providerValuationConfirmedAt non-null
providerPriceSnapshot non-null
creditsGranted > 0
```

The refund snapshots must match the referenced purchase's frozen acquisition evidence.

Provider mismatch is a bounded `NEEDS_ATTENTION` preparation failure; do not call Shopify.

### R6 — Reserved credits delay provider action

If:

```text
purchase.status = WITHDRAWN
purchase.currentAmount > 0
purchase.reservedAmount > 0
```

leave the refund:

```text
status = REQUESTED
```

and do not freeze provider amount yet.

Existing reservation commit/release semantics continue to evolve the held lot.

No provider action should be requested while reserved credits remain.

### R7 — Zero remaining credits cancel the refund

If:

```text
purchase.status IN (WITHDRAWN, COMPLETED)
purchase.currentAmount = 0
purchase.reservedAmount = 0
```

atomically:

```text
refund.status = CANCELLED
refund.reason = "NO_CREDITS_REMAINING"
refund.version += 1
```

If the purchase is still `WITHDRAWN`, ensure it is `COMPLETED` in the same transaction when consistent with existing purchase invariants.

No provider action is required because there is no remaining credit quantity to refund.

### R8 — Freeze exact Woo business refund evidence when reservations reach zero

For an eligible purchase:

```text
status = WITHDRAWN
currentAmount > 0
reservedAmount = 0
```

define:

```text
finalCreditQuantity = purchase.currentAmount

ratio =
    Decimal(finalCreditQuantity)
    / Decimal(purchase.creditsGranted)

expectedProviderAmount =
    refund.purchaseProviderAmountSnapshot
      .mul(ratio)
      .toDecimalPlaces(2)

expectedProviderCurrency =
    uppercase(refund.purchaseProviderCurrencySnapshot)
```

Require:

```text
0 < ratio <= 1
expectedProviderAmount > 0
expectedProviderCurrency = USD
```

Use exact Decimal arithmetic. Do not use JS floating point.

The expected amount is based on the provider purchase amount snapshot, not the pre-tax operation quote.

### R9 — Prepared Woo refunds require provider dashboard action

Atomically compare-and-set:

```text
refund.status:
    REQUESTED -> PROVIDER_ACTION_REQUIRED
```

and freeze:

```text
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
reason = "WOO_VENDOR_DASHBOARD_REFUND_REQUIRED"
version += 1
```

Keep:

```text
providerReference = NULL
providerActionKind = NULL
providerAmount = NULL
providerCurrency = NULL
providerConfirmedAt = NULL
providerConfirmedByPlatformAdminId = NULL
automaticCorrectionUsageEventId = NULL
```

This status means:

> Moda has frozen the refundable credit quantity/economic expectation. A vendor/admin must perform the provider refund in Woo's SaaS Pending Refunds workflow.

BACKGROUND-005 itself does not contact Woo.

### R10 — Exact refunded-receipt scan

Define:

```text
MAX_WOO_REFUNDED_CHARGE_RECEIPTS_PER_CYCLE = 50
```

After preparation, select unprocessed receipts where:

```text
normalizedPayload has top-level key "charge"
topic = saas_billing_contract.refunded
```

Order:

```text
receivedAt ASC,
id ASC
```

Reuse the accepted `FOR UPDATE SKIP LOCKED` + in-cycle `(receivedAt,id)` cursor pattern.

### R11 — Revalidate minimum refunded charge shape

Require:

```text
charge.id = receipt.providerContractId
charge.id non-blank
charge.transactions is a non-empty array
```

Do not require a specific charge `status` value for refund settlement because Woo's public refund documentation makes `amount_refunded` the settlement evidence and does not define a separate refund-status value that ARCH-027 can safely depend on.

### R12 — Correlate through the trusted one-time-charge operation

Resolve exactly one:

```text
WooCommerceBillingOperation.kind = ONE_TIME_CHARGE
WooCommerceBillingOperation.providerContractId
    = receipt.providerContractId
```

Then resolve its exact linked `RecoveryCreditPurchase`.

Missing operation:

```text
WOO_REFUND_CHARGE_CORRELATION_NOT_READY
```

Multiple operations:

```text
WOO_REFUND_CHARGE_OPERATION_AMBIGUOUS
```

Do not infer Shop/purchase from provider JSON or amount.

### R13 — Exact provider transaction identity comes from purchase activation evidence

Require `purchase.providerPriceSnapshot` is the accepted BACKGROUND-004 v1 shape and read:

```text
providerTransactionId
providerBillingIntentId
providerTransactionAmount
providerAmountRefunded
```

The refund receipt must contain exactly one transaction whose:

```text
id == providerTransactionId
```

after canonical base-10 string normalization.

Require that transaction:

```text
completed_at non-blank
amount is finite positive Decimal
amount_refunded is finite Decimal >= 0
```

Do not switch to a different transaction merely because it has a refund.

Missing exact transaction:

```text
WOO_REFUND_PROVIDER_TRANSACTION_NOT_FOUND
```

More than one exact ID match:

```text
WOO_REFUND_PROVIDER_TRANSACTION_AMBIGUOUS
```

### R14 — Provider refund amount is exact Decimal evidence

Parse:

```text
transaction.amount_refunded
```

through exact Decimal semantics.

Require:

```text
actualProviderRefundAmount > 0
```

Zero means provider settlement is not yet proven:

```text
WOO_REFUND_PROVIDER_AMOUNT_NOT_READY
```

and leaves the receipt unprocessed.

Currency is exactly:

```text
USD
```

under ARCH-027 Woo-v1.

### R15 — Existing local refund hold is required

Find the refund for the linked purchase where:

```text
provider = WOOCOMMERCE
status IN (
  REQUESTED,
  PROVIDER_ACTION_REQUIRED,
  NEEDS_ATTENTION,
  COMPLETED
)
```

ordered deterministically by:

```text
createdAt DESC,
id DESC
```

Require at most one live/non-terminal refund according to the existing database uniqueness rule.

If no Woo refund exists:

```text
WOO_REFUND_REQUEST_NOT_FOUND
```

leave the provider receipt unprocessed and make **no credit mutation**.

Do not silently invent a `RecoveryCreditRefund` after provider money has already moved.

A later Admin/support task may provide an explicit recovery path for an externally approved unmatched Woo refund.

### R16 — Inline preparation is allowed only when the hold is ready

If the matched refund is still `REQUESTED`:

- if `purchase.reservedAmount > 0`, return:
  ```text
  WOO_REFUND_HOLD_NOT_READY
  ```
  and leave the receipt unprocessed;
- if `purchase.reservedAmount = 0` and `purchase.currentAmount > 0`, perform R8/R9 preparation in the same receipt transaction and continue reconciliation;
- if no credits remain, perform R7 and then classify the provider refund as:
  ```text
  WOO_REFUND_LOCAL_STATE_CONFLICT
  ```
  because provider money moved after no local refundable credits remained.

### R17 — Deterministic refund reconciliation lock order

After receipt/operation correlation identifies the Shop, lock:

```text
1. commerce.Shop
2. WooCommerceBillingOperation
3. RecoveryCreditPurchase
4. RecoveryCreditRefund
5. ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
```

Then revalidate:

```text
operation.shopId
purchase.shopId
refund.shopId
purchase.provider
refund.provider
purchase.providerReference
```

all refer to the same Woo charge/Shop.

Use Serializable/bounded retry semantics consistent with existing refund/purchase mutations.

### R18 — Exact completion preconditions

Automatic completion from the refunded webhook requires:

```text
refund.status = PROVIDER_ACTION_REQUIRED

refund.finalCreditQuantity > 0
refund.expectedProviderAmount > 0
refund.expectedProviderCurrency = USD

purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount = refund.finalCreditQuantity

counter.refundingQuantity >= refund.finalCreditQuantity
counter.grantedQuantity >= refund.finalCreditQuantity

actualProviderRefundAmount
    = refund.expectedProviderAmount
```

Any purchase/counter mismatch is:

```text
WOO_REFUND_LOCAL_STATE_CONFLICT
```

and remains unprocessed.

### R19 — Provider reference for Woo refund settlement

On provider evidence use exactly:

```text
providerReference =
  "woocommerce:charge:"
  + providerContractId
  + ":transaction:"
  + providerTransactionId
```

Require the resulting string is <= 512 characters.

Persist:

```text
providerActionKind = REFUND
providerAmount = actualProviderRefundAmount
providerCurrency = USD
providerConfirmedByPlatformAdminId = NULL
providerConfirmedAt = receipt.receivedAt
```

### R20 — Exact Woo refund completion transaction

When R18 matches exactly, atomically:

```text
RecoveryCreditPurchase:
    currentAmount = 0
    reservedAmount = 0
    status = REFUNDED
    version += 1

ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS):
    refundingQuantity -= finalCreditQuantity
    grantedQuantity   -= finalCreditQuantity
    version += 1

RecoveryCreditRefund:
    providerReference = R19
    providerActionKind = REFUND
    providerAmount = actualProviderRefundAmount
    providerCurrency = USD
    providerConfirmedByPlatformAdminId = NULL
    providerConfirmedAt = receipt.receivedAt
    status = COMPLETED
    completedAt = receipt.receivedAt
    version += 1

WooCommerceBillingWebhookReceipt:
    processedAt = reconciliation now
    processingError = NULL
```

Do not modify purchased counter `committedQuantity` or `reservedQuantity`.

Consumed credits remain consumed and are not restored.

### R21 — Completed refund emits the existing merchant completion notification

Reuse:

```text
BILLING_SYSTEM_MESSAGE_CODES.REFUND_COMPLETED
```

and the existing support-thread idempotency/source-key convention.

Use provider-neutral message text, e.g.:

```text
Your recovery-credit refund has completed. The refundable purchased credits have been removed and provider refund confirmation is recorded.
```

Do not emit Shopify-specific completion wording for Woo.

Notification persistence belongs in the same successful business transaction where practical under existing conventions.

### R22 — Provider amount mismatch becomes NEEDS_ATTENTION, not speculative completion

If:

```text
actualProviderRefundAmount
    != refund.expectedProviderAmount
```

the provider has already moved money but it does not match the frozen Moda business expectation.

Atomically record:

```text
refund.providerReference = R19
refund.providerActionKind = REFUND
refund.providerAmount = actualProviderRefundAmount
refund.providerCurrency = USD
refund.providerConfirmedByPlatformAdminId = NULL
refund.providerConfirmedAt = receipt.receivedAt
refund.status = NEEDS_ATTENTION
refund.reason = "WOO_PROVIDER_REFUND_AMOUNT_MISMATCH"
refund.version += 1

receipt.processedAt = reconciliation now
receipt.processingError = NULL
```

Preserve:

```text
purchase.status = WITHDRAWN
purchase.currentAmount
counter.refundingQuantity
counter.grantedQuantity
```

Do not silently remove a different credit quantity to make the provider amount fit.

A later Admin support task owns explicit resolution of this attention state.

### R23 — NEEDS_ATTENTION replay

If the refund is already `NEEDS_ATTENTION` and its frozen provider evidence exactly matches the same provider contract/transaction/refunded amount, a duplicate refunded receipt is a processed no-op.

If a later receipt presents different provider refunded evidence for the same local refund:

```text
WOO_REFUND_PROVIDER_EVIDENCE_CONFLICT
```

leave it unprocessed for operator review.

### R24 — COMPLETED replay

If:

```text
refund.status = COMPLETED
purchase.status = REFUNDED
purchase.currentAmount = 0
purchase.reservedAmount = 0
```

and stored provider evidence exactly matches the refunded receipt, process the duplicate receipt as a no-op.

Never decrement the purchased counter twice.

### R25 — Local cancellation/rejection conflicts are not overridden

If the matched local refund is:

```text
CANCELLED
REJECTED
```

but Woo sends a positive `amount_refunded`, the provider and Moda business state disagree.

Return:

```text
WOO_REFUND_LOCAL_STATE_CONFLICT
```

and leave the receipt unprocessed.

Do not silently reopen or complete a canceled/rejected refund.

### R26 — No provider network dependency

Do not call Woo to re-fetch the charge/refund.

Do not load Woo billing credentials.

The signed durable refund receipt plus local purchase/refund/operation evidence are sufficient for this task.

### R27 — No automatic provider refund initiation

BACKGROUND-005 MUST NOT:

```text
POST a refund
DELETE a charge
approve a Woo refund request
```

or infer that a partial refund can be initiated programmatically.

The provider action remains manual/vendor-dashboard until Woo sandbox certification proves a safe automated mechanism.

### R28 — Free-plan Woo refunds require nullable refund BillingPeriod provenance

A Woo top-up bought while the merchant was on local Free has:

```text
purchase.billingPeriodId = NULL
```

The local refund row must therefore allow:

```text
refund.billingPeriodIdSnapshot = NULL
```

for:

```text
refund.provider = WOOCOMMERCE
```

Shopify refund rows continue to require a non-null billing-period snapshot.

This database contract is corrected in the companion `ARCH-027-DATABASE-001` definition update included with this patch.

### R29 — Structured logging

Use the Shared structured logger.

Allowed bounded identifiers:

```text
refundId
purchaseId
receiptId
providerContractId
shopId
operationId
transition outcome
processingError code
```

Never log:

```text
full provider payload
transaction URL
Woo credentials/signature
customer/payment data
```

## Work Items

- [ ] Restrict the existing Shopify automatic refund-correction scan to `provider=SHOPIFY`.
- [ ] Add bounded Woo refund preparation for REQUESTED rows.
- [ ] Wait for reserved credits to settle/release before freezing final quantity/economics.
- [ ] Freeze finalCreditQuantity and proportional expected provider amount using exact Decimal arithmetic.
- [ ] Move prepared Woo refunds to PROVIDER_ACTION_REQUIRED without creating a Shopify correction UsageEvent.
- [ ] Add refunded charge receipt claiming after acquisition reconciliation.
- [ ] Resolve exact ONE_TIME_CHARGE operation/purchase/refund linkage.
- [ ] Read the exact original provider transaction ID from BACKGROUND-004 providerPriceSnapshot.
- [ ] Parse amount_refunded with exact Decimal semantics.
- [ ] Require an existing local Woo refund hold before credit mutation.
- [ ] Complete exact provider-amount matches atomically.
- [ ] Move provider amount mismatches to NEEDS_ATTENTION with frozen provider evidence.
- [ ] Preserve unmatched provider refunds as unprocessed rather than inventing a local refund.
- [ ] Add idempotent replay for COMPLETED / matching NEEDS_ATTENTION evidence.
- [ ] Emit provider-neutral refund-completed support message.
- [ ] Add focused Shopify regression, partial/full/mismatch, Free-plan and concurrency tests.

## Interfaces / Contracts

### Local Woo refund hold producer

Future owner:

Woo purchase-history/refund API task.

The producer creates the existing generic:

```text
RecoveryCreditRefund(provider = WOOCOMMERCE)
```

and moves the exact purchase lot to `WITHDRAWN` while increasing `refundingQuantity`.

BACKGROUND-005 owns later preparation/provider settlement.

### Provider input

Producer:

`ARCH-027-API-005`

Input:

```text
WooCommerceBillingWebhookReceipt
topic = saas_billing_contract.refunded
normalizedPayload.charge
```

### Trusted acquisition evidence

Producer:

`ARCH-027-BACKGROUND-004`

```text
RecoveryCreditPurchase.providerReference
RecoveryCreditPurchase.providerPurchaseAmount
RecoveryCreditPurchase.providerPurchaseCurrency
RecoveryCreditPurchase.providerPriceSnapshot
```

### Refund output

Exact match:

```text
RecoveryCreditRefund -> COMPLETED
RecoveryCreditPurchase -> REFUNDED
PURCHASED_RECOVERY_CREDITS grant/refunding reduced
```

Provider mismatch:

```text
RecoveryCreditRefund -> NEEDS_ATTENTION
purchase/counter remain held
```

No local refund:

```text
receipt remains unprocessed
```

## Dependencies

- `ARCH-027-BACKGROUND-004`

BACKGROUND-004 must be architect-accepted Complete so Woo purchase activation/evidence and charge receipt ordering are stable before refund reconciliation is introduced.

Through BACKGROUND-004, this task also relies on API-005 signed receipt acceptance and the ARCH-027 database provider-neutral refund schema.

## Enables

None yet.

Expected follow-on tasks:

- Woo purchase-history/refund API that creates the local Woo refund hold;
- Admin Woo refund/provider-attention support;
- Woo billing UI refund/reactivation parity;
- Woo sandbox certification of provider partial-refund capability.

## Acceptance Criteria

- [ ] Existing Shopify refund correction service selects only provider SHOPIFY and all ARCH-015 behavior remains green.
- [ ] Woo REQUESTED refunds never create Shopify correction UsageEvents.
- [ ] Woo refund preparation is bounded to 50 rows/cycle and ordered deterministically.
- [ ] Reserved Woo credits keep refund REQUESTED until reservations settle/release.
- [ ] Zero remaining credits cancel the local refund without provider action.
- [ ] Prepared Woo refund freezes current final credit quantity after reservations settle.
- [ ] Expected provider amount is exact providerPurchaseAmountSnapshot * finalCreditQuantity / creditsGranted rounded to 2 decimal places.
- [ ] Prepared Woo refund moves to PROVIDER_ACTION_REQUIRED and preserves null provider confirmation fields.
- [ ] Refunded charge scan is bounded to 50/cycle and uses accepted SKIP LOCKED/in-cycle cursor semantics.
- [ ] Refund reconciliation uses the exact one-time-charge operation and purchase.
- [ ] Refund reconciliation uses the exact transaction ID stored in the purchase providerPriceSnapshot.
- [ ] Positive `amount_refunded` is parsed using exact Decimal arithmetic.
- [ ] No local refund hold -> no credit mutation and receipt remains unprocessed.
- [ ] Exact provider refund amount match completes purchase/refund/counter atomically.
- [ ] Completion records automated Woo provider evidence with `providerConfirmedByPlatformAdminId = NULL`.
- [ ] Consumed credits are never restored.
- [ ] Purchased-credit counter is decremented exactly once.
- [ ] Provider amount mismatch records NEEDS_ATTENTION and preserves held local credits/counter.
- [ ] Duplicate matching NEEDS_ATTENTION/refunded evidence is idempotent.
- [ ] Duplicate COMPLETED refund evidence is idempotent and never double-decrements.
- [ ] Canceled/rejected local refund is never silently overridden by provider evidence.
- [ ] Woo Free refund works with null billingPeriodIdSnapshot.
- [ ] Shopify refund continues to require non-null billingPeriodIdSnapshot.
- [ ] No Woo provider HTTP/credential use occurs.
- [ ] No automated partial refund initiation is implemented.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted Background repository state/package scripts before selecting exact commands.

Required validation categories:

- [ ] repository production build/typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] existing ARCH-015 Shopify refund-correction focused tests remain green;
- [ ] explicit provider=SHOPIFY scan regression test;
- [ ] Woo refund REQUESTED with reserved credits waits test;
- [ ] withdrawn reservation commit/release -> final quantity preparation tests;
- [ ] Woo exact expected-provider-amount Decimal test;
- [ ] Woo Free null-billing-period refund preparation test;
- [ ] prepared -> PROVIDER_ACTION_REQUIRED evidence test;
- [ ] refunded receipt exact charge/transaction correlation test;
- [ ] no-local-refund receipt remains unprocessed test;
- [ ] amount_refunded=0 remains unprocessed test;
- [ ] exact provider amount completion integration test;
- [ ] provider amount mismatch -> NEEDS_ATTENTION integration test;
- [ ] provider amount greater/less than expected tests;
- [ ] provider amount includes tax proportional calculation test;
- [ ] purchase/counter/refund/receipt atomic rollback test;
- [ ] duplicate COMPLETED receipt idempotency test;
- [ ] duplicate matching NEEDS_ATTENTION evidence idempotency test;
- [ ] conflicting later provider evidence negative test;
- [ ] canceled/rejected local state conflict test;
- [ ] purchased counter decrement exactly once concurrency test;
- [ ] no Shopify correction UsageEvent for Woo assertion;
- [ ] no Woo provider HTTP/credential assertion;
- [ ] provider-neutral support-message assertion;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence.

Real Woo partial-refund controls remain a terminal sandbox capability gate.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo refund API/UI/Admin support implementation.

## Implementation Notes

Keep Woo refund settlement separate from Shopify correction mechanics:

```text
Shopify:
    refund hold
    -> negative/fractional App Event
    -> provider meter proof
    -> complete

Woo:
    refund hold
    -> PROVIDER_ACTION_REQUIRED
    -> vendor dashboard provider action
    -> signed refunded webhook
    -> complete / NEEDS_ATTENTION
```

Both converge on the same durable business outcome:

```text
RecoveryCreditPurchase REFUNDED
RecoveryCreditRefund COMPLETED
PURCHASED_RECOVERY_CREDITS reduced
```

Do not create a Woo refund table.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- A future Woo refund API creates the local refund hold before provider action for the normal merchant flow.
- Woo `amount_refunded` is cumulative provider settlement evidence on the originally activated one-time-charge transaction.
- BACKGROUND-004's providerPriceSnapshot identifies the exact provider transaction used for the purchase.
- Provider partial refund initiation remains manual/sandbox-gated.

### Unresolved Issues

- Exact arbitrary partial-refund controls in the Woo vendor workflow remain a sandbox capability gate.
- A Woo provider refund approved without any local Moda refund request remains intentionally unmatched/unprocessed until an explicit Admin/support recovery path is designed.

### Architectural Concerns

None beyond the explicit unmatched-provider-refund and partial-provider-refund gates above.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
