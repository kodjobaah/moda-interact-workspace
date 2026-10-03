---
id: ARCH-027-BACKGROUND-004
architecture_id: ARCH-027
title: Reconcile WooCommerce one-time-charge acquisition receipts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-003
enables:
  - ARCH-027-BACKGROUND-005
created: 2026-10-03
updated: 2026-10-03
---

# Reconcile WooCommerce one-time-charge acquisition receipts

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Consume durably accepted Woo **charge-wrapper acquisition lifecycle** receipts and activate the already-requested Moda `RecoveryCreditPurchase` lot only after verified Woo provider payment evidence.

This task owns exactly these one-time-charge topics:

```text
saas_billing_contract.activated
saas_billing_contract.canceled
saas_billing_contract.prepaid_term_ended
```

when:

```text
normalizedPayload.charge exists
```

The successful acquisition flow is:

```text
WooCommerceBillingWebhookReceipt
    topic = activated
    charge.id = provider charge-contract UUID
        |
        v
resolve exactly one trusted ONE_TIME_CHARGE operation
        |
        v
resolve its exactly linked REQUESTED RecoveryCreditPurchase
        |
        v
validate charge status + completed payment evidence
        |
        v
atomically:
    operation -> CONFIRMED
    purchase  -> ACTIVE
    purchased-credit counter += creditsGranted
    receipt   -> processed
        |
        v
after commit:
    schedule recovery-capacity resume
```

This task also consumes charge `canceled` / `prepaid_term_ended` receipts so abandoned/unconfirmed provider contracts do not leave the selected bundle permanently blocked.

It deliberately does **not** process:

```text
saas_billing_contract.refunded
```

Refund settlement has different business rules and remains a separate task.

## Context

ARCH-027 already establishes:

- API-004 creates one `REQUESTED` Woo `RecoveryCreditPurchase` plus one linked `ONE_TIME_CHARGE` operation before `POST /charges`;
- one operation means one predefined bundle; there is no purchase quantity;
- a merchant may be on local Free with no recurring Woo contract or BillingPeriod;
- API-005 verifies Woo webhook HMACs and persists provider-shaped charge receipts without business mutation;
- DATABASE-001 makes Woo purchase acquisition evidence provider-neutral while preserving Shopify meter evidence for Shopify;
- API-002 treats a REQUESTED Woo purchase whose linked operation is `FAILED` as historical failed intent rather than unresolved checkout.

### Current source purchase behavior

The current `RecoveryCreditPurchaseService` is Shopify-specific. Its confirmed-purchase path proves a Shopify meter quantity/cost delta, activates the lot, increments `PURCHASED_RECOVERY_CREDITS`, and schedules capacity resume.

Woo `/charges` has no Shopify meter proof. BACKGROUND-004 therefore uses Woo charge evidence but converges onto the same durable Moda business state:

```text
RecoveryCreditPurchase
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
```

### Woo provider facts

Woo's Marketplace SaaS Billing documentation, verified 3 October 2026, states:

- one-time charges are intended for non-renewable purchases such as credit packs;
- successful checkout sends `saas_billing_contract.activated` with a `charge` object;
- `activated` means checkout/payment succeeded;
- charge payloads contain billing intents and transactions;
- transactions expose `amount` and `amount_refunded`;
- Woo adds merchant tax on top of the original price supplied by Moda;
- only USD is currently supported;
- `canceled` may apply to a charge;
- `refunded` applies to one-time charges and reports refunded amount through transaction evidence.

Provider reference:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

Because Woo may add tax on top of Moda's stored retail quote, this task MUST NOT require provider transaction total to equal `quotedAmountMinor`.

## Scope

Modify only `moda-interact-background` implementation/tests required for:

1. bounded PostgreSQL claiming of unprocessed Woo **charge** acquisition receipts;
2. trusted charge-contract -> operation -> purchase correlation;
3. one-time purchase activation;
4. abandoned/unconfirmed charge termination;
5. receipt processed/error bookkeeping;
6. integration into the existing leased billing cycle.

Expected implementation areas:

```text
src/services/woocommerce-billing/
  charge-receipt-reconciliation.service.ts
  charge-payment-evidence.ts
  purchase-activation.service.ts

src/entrypoints/billing.ts
```

Exact filenames may differ where accepted BACKGROUND-002/BACKGROUND-003 code provides a clearer owner.

Reuse accepted receipt-claiming/transaction helpers from BACKGROUND-002 where they exist.

Update the nested `database/` gitlink to the newest compatible architect-accepted database main commit and regenerate Prisma before source changes.

## Out of Scope

- Woo `subscription` receipt processing.
- `saas_billing_contract.refunded` charge receipts.
- Creating/approving `RecoveryCreditRefund`.
- Woo refund provider initiation.
- Arbitrary partial Woo refund support.
- Woo provider HTTP calls/credentials.
- Recomputing bundle price from Admin tiers.
- Reloading current catalogue price to replace the frozen operation quote.
- Subscription/BillingPlan/BillingPeriod mutation.
- Included-recovery allowance mutation.
- Any purchase-acquisition `UsageEvent`.
- Woo UI/API purchase-history/refund commands.
- Gateway changes.
- Prisma schema/migration edits.
- New worker/queue/cron deployment.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Existing billing worker and exact execution order

Run inside the existing `BILLING_RECONCILIATION` leased cycle.

Order:

```text
1. BACKGROUND-002 recurring subscription receipt reconciliation
2. BACKGROUND-003 local Woo entitlement-period rollover
3. BACKGROUND-004 one-time-charge acquisition reconciliation
```

No new worker/lease/queue/cron is permitted.

### R2 — Exact scan bound

Define:

```text
MAX_WOO_CHARGE_ACQUISITION_RECEIPTS_PER_CYCLE = 50
```

Eligibility:

```text
processedAt IS NULL
normalizedPayload has top-level key "charge"
topic IN (
  saas_billing_contract.activated,
  saas_billing_contract.canceled,
  saas_billing_contract.prepaid_term_ended
)
```

Do not select `saas_billing_contract.refunded`.

Order:

```text
receivedAt ASC,
id ASC
```

### R3 — Claim one receipt per transaction

Reuse BACKGROUND-002's accepted `FOR UPDATE SKIP LOCKED` receipt-claim pattern and in-cycle `(receivedAt,id)` cursor behavior.

One unresolved receipt may be attempted at most once by one process during one leased cycle and retried in a later cycle.

### R4 — Transition and receipt completion are atomic

For successful activation, terminal cancellation handling, or valid idempotent replay, the same transaction commits:

```text
business/operation/purchase/counter mutation
+
receipt.processedAt = reconciliation now
+
receipt.processingError = NULL
```

Never mark the receipt processed before business mutation commits.

### R5 — Bounded reconciliation errors

A recognized receipt that cannot yet reconcile keeps:

```text
processedAt = NULL
```

and stores one canonical code:

```text
CHARGE_CORRELATION_NOT_READY
CHARGE_OPERATION_AMBIGUOUS
CHARGE_OPERATION_STATE_CONFLICT
CHARGE_PURCHASE_LINK_CONFLICT
CHARGE_PURCHASE_STATE_CONFLICT
CHARGE_PAYMENT_EVIDENCE_INCOMPLETE
CHARGE_PAYMENT_EVIDENCE_AMBIGUOUS
CHARGE_PAYMENT_AMOUNT_INVALID
CHARGE_PROVIDER_STATUS_CONFLICT
CHARGE_TENANT_CONFLICT
PURCHASED_COUNTER_STATE_CONFLICT
```

Never store provider JSON, transaction URLs or exception stacks in `processingError`.

### R6 — Provider charge wrapper revalidation

Require:

```text
normalizedPayload is object
exactly one `charge` object
charge.id = receipt.providerContractId
charge.id non-blank
charge.status non-blank
```

Topic/status compatibility:

```text
activated          -> active
canceled           -> canceled
prepaid_term_ended -> canceled
```

Mismatch -> `CHARGE_PROVIDER_STATUS_CONFLICT`.

### R7 — Correlate only through the trusted ONE_TIME_CHARGE operation

Resolve:

```text
kind = ONE_TIME_CHARGE
providerContractId = receipt.providerContractId
```

Require exactly one matching operation.

None -> `CHARGE_CORRELATION_NOT_READY`.

More than one -> `CHARGE_OPERATION_AMBIGUOUS`.

Do not infer a Shop from provider JSON, domain, Subscription or bundle price.

This explicitly leaves provider-response-loss cases with no locally captured contract ID unresolved rather than guessed.

### R8 — Deterministic lock order

After non-locking correlation identifies one Shop, lock:

```text
1. commerce.Shop
2. WooCommerceBillingOperation
3. linked RecoveryCreditPurchase
4. ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS), if present
```

Then re-read/revalidate all predicates.

Use Serializable transaction/retry behavior consistent with existing purchased-credit mutation paths where required.

### R9 — Exact operation/purchase linkage

Require:

```text
operation.shopId = Shop.id
operation.kind = ONE_TIME_CHARGE
operation.recoveryCreditPurchaseId non-null
operation.merchantPricingUsageEventId non-null
operation.quotedAmountMinor positive safe integer
operation.quotedCurrency = USD
```

Require the linked purchase:

```text
purchase.id = operation.recoveryCreditPurchaseId
purchase.shopId = operation.shopId
purchase.provider = WOOCOMMERCE
purchase.creditsGranted positive safe integer
```

Cross-Shop/provider mismatch fails closed.

Do not reload `MerchantPricingUsageEvent` to replace the frozen grant/quote.

### R10 — New activation source state

New `activated` transition requires:

```text
operation.state IN (
  AWAITING_CONFIRMATION,
  OUTCOME_UNKNOWN
)

purchase.status = REQUESTED
purchase.currentAmount = 0
purchase.reservedAmount = 0

purchase.providerReference IS NULL
purchase.providerPurchaseAmount IS NULL
purchase.providerPurchaseCurrency IS NULL
purchase.providerValuationConfirmedAt IS NULL
purchase.providerPriceSnapshot IS NULL
purchase.usageEventId IS NULL
```

### R11 — Idempotent activated replay

A receipt is a processed no-op when:

```text
operation.state = CONFIRMED

purchase.status IN (
  ACTIVE,
  WITHDRAWN,
  COMPLETED,
  REFUNDED
)

purchase.provider = WOOCOMMERCE
purchase.providerReference = receipt.providerContractId
purchase.providerPurchaseAmount IS NOT NULL
purchase.providerPurchaseCurrency = USD
purchase.providerValuationConfirmedAt IS NOT NULL
purchase.providerPriceSnapshot IS NOT NULL
```

Do not increment purchased capacity again.

Any partial/incompatible shape is `CHARGE_PURCHASE_STATE_CONFLICT`.

### R12 — Exact completed-payment evidence

For `activated`, require non-empty:

```text
charge.billing_intents
charge.transactions
```

Completed billing intent:

```text
id = positive safe integer
status = "completed"
```

Completed transaction candidate:

```text
id = positive safe integer
billing_intent_id = one completed intent id
completed_at = non-blank string
amount = finite positive decimal
amount_refunded = finite decimal >= 0
```

Initial activation additionally requires:

```text
amount_refunded = 0
```

Require exactly **one** completed transaction candidate associated with a completed billing intent.

Zero -> `CHARGE_PAYMENT_EVIDENCE_INCOMPLETE`.

More than one -> `CHARGE_PAYMENT_EVIDENCE_AMBIGUOUS`.

### R13 — Exact provider money parsing

Parse provider money using exact Decimal semantics:

```text
Prisma.Decimal(String(value))
```

or an equivalent exact path.

Require:

```text
amount > 0
amount_refunded = 0
```

for activation.

Never use JS floating-point multiplication for persisted provider valuation.

### R14 — Provider total is distinct from the Moda quote

The operation quote:

```text
quotedAmountMinor
quotedCurrency
```

is the exact pre-tax Moda retail price sent to Woo.

Woo may add merchant tax.

Therefore do **not** require:

```text
provider amount * 100 == quotedAmountMinor
```

Activation requires a positive completed provider transaction, not equality with the pre-tax quote.

Persist the two pieces of evidence separately.

### R15 — Exact v1 providerPriceSnapshot

On activation store exactly:

```json
{
  "schemaVersion": 1,
  "provider": "WOOCOMMERCE",
  "kind": "ONE_TIME_CHARGE",
  "merchantPricingUsageEventId": "<operation value>",
  "quotedAmountMinor": 1234,
  "quotedCurrency": "USD",
  "providerBillingIntentId": "17",
  "providerTransactionId": "42",
  "providerTransactionAmount": "14.81",
  "providerAmountRefunded": "0"
}
```

Rules:

- provider integer IDs become base-10 strings;
- Decimal values are canonical non-exponential decimal strings;
- do not store transaction URL;
- do not store customer/payment data;
- do not store webhook signature/raw body.

### R16 — Atomic purchase activation

Compare-and-set from the pristine REQUESTED state to:

```text
providerReference            = receipt.providerContractId
providerPurchaseAmount       = completed transaction amount
providerPurchaseCurrency     = USD
providerValuationConfirmedAt = receipt.receivedAt
providerPriceSnapshot        = exact R15 JSON

currentAmount = creditsGranted
reservedAmount = 0
status = ACTIVE
activatedAt = receipt.receivedAt
version += 1
```

Do not populate Shopify meter fields.

Do not create any `UsageEvent`.

### R17 — Purchased capacity increments exactly once

In the same transaction increment/create:

```text
ShopEntitlementCounter
counter = PURCHASED_RECOVERY_CREDITS
```

by:

```text
grantedQuantity += purchase.creditsGranted
version += 1
```

Preserve:

```text
committedQuantity
reservedQuantity
refundingQuantity
```

If absent, create one counter with grant equal to this purchase and all consumed/reserved/refunding quantities zero.

Lock an existing counter before update and handle serialization/unique races with bounded retry.

### R18 — Confirm operation atomically

In the same activation transaction:

```text
AWAITING_CONFIRMATION | OUTCOME_UNKNOWN
    -> CONFIRMED

lastErrorCode = NULL
```

Do not rewrite immutable intent/quote/provider-contract fields.

### R19 — Resume recovery only after new activation commits

After commit:

```text
recoveryCapacityResumeService.schedule({
  shopId,
  trigger: "woo-purchase-activation-<purchaseId>"
})
```

Scheduling failure does not roll back activation.

Idempotent replay does not schedule again.

### R20 — Canceled/prepaid before activation terminates checkout

For:

```text
topic = canceled | prepaid_term_ended
purchase.status = REQUESTED
operation.state IN (
  AWAITING_CONFIRMATION,
  OUTCOME_UNKNOWN
)
```

set:

```text
operation.state = FAILED
operation.lastErrorCode = "WOO_CHARGE_CANCELED_BEFORE_ACTIVATION"
```

Leave purchase as historical REQUESTED/zero intent.

Mark the receipt processed.

This makes the bundle eligible for a deliberate new API attempt with a new idempotency key.

### R21 — Canceled/prepaid after activation never revokes credits

When:

```text
operation.state = CONFIRMED
purchase.status IN (
  ACTIVE,
  WITHDRAWN,
  COMPLETED,
  REFUNDED
)
```

charge `canceled` / `prepaid_term_ended` receipts are processed no-ops.

Do not decrement credits, withdraw the lot or create a refund.

### R22 — Cancellation replay

If operation is already:

```text
FAILED
lastErrorCode = WOO_CHARGE_CANCELED_BEFORE_ACTIVATION
```

and purchase is still REQUESTED/zero, later canceled/prepaid receipts for the same contract are processed no-ops.

Other incompatible states remain unprocessed with `CHARGE_OPERATION_STATE_CONFLICT`.

### R23 — Refunded charge receipts remain for the later refund task

Do not select or mark processed:

```text
saas_billing_contract.refunded
+ charge wrapper
```

A `canceled` receipt that accompanies a refund may be processed as the R21 no-op for an already-active purchase; the separate `refunded` receipt remains the authoritative refund-settlement input.

### R24 — Free and paid acquisition are both valid

Activation must not require a recurring Woo contract or current OPEN BillingPeriod.

A Free purchase may have:

```text
providerSubscriptionIdSnapshot = NULL
billingPeriodId = NULL
```

A paid purchase may reference the BillingPeriod that existed when API-004 created it even if that period has since closed before the merchant completes Woo checkout.

Purchase ownership is defined by the purchase/operation Shop relation, not by the current Subscription state.

### R25 — No provider network dependency

Do not re-fetch the charge from Woo.

The signed durable receipt plus trusted local operation/purchase state are sufficient.

### R26 — Structured logging

Use the Shared structured logger.

Allowed bounded fields:

```text
receiptId
topic
providerContractId
shopId
operationId
purchaseId
transition outcome
processingError code
```

Never log full provider JSON, transaction URLs, credentials, signatures or customer/payment data.

## Work Items

- [ ] Reuse accepted receipt-claiming helpers from BACKGROUND-002 where available.
- [ ] Add charge-acquisition reconciliation after BACKGROUND-003 in the existing billing worker.
- [ ] Add exact 50-receipt scan for activated/canceled/prepaid_term_ended charge wrappers.
- [ ] Exclude refunded charge receipts.
- [ ] Revalidate provider charge status and payment evidence.
- [ ] Resolve exactly one ONE_TIME_CHARGE operation by provider contract ID.
- [ ] Add exact Shop/operation/purchase linkage checks and deterministic locks.
- [ ] Add exact Decimal provider transaction parsing.
- [ ] Preserve pre-tax Moda quote separately from provider transaction total.
- [ ] Persist the exact v1 providerPriceSnapshot.
- [ ] Activate one REQUESTED purchase atomically with purchased-counter increment and operation confirmation.
- [ ] Create no purchase-acquisition UsageEvent.
- [ ] Schedule recovery-capacity resume only after new activation commit.
- [ ] Mark canceled/prepaid unconfirmed operations FAILED so checkout gating clears.
- [ ] Treat canceled/prepaid after activation as no-op.
- [ ] Leave refunded receipts unprocessed.
- [ ] Add focused concurrency/idempotency/tax/cancellation tests.

## Interfaces / Contracts

### Durable input

Owner: `ARCH-027-DATABASE-001`

Producer: `ARCH-027-API-005`

Consumed:

```text
processedAt = NULL
normalizedPayload.charge exists

topic =
  activated
  canceled
  prepaid_term_ended
```

### Trusted local command

Producer: `ARCH-027-API-004`

```text
WooCommerceBillingOperation
kind = ONE_TIME_CHARGE
providerContractId
merchantPricingUsageEventId
quotedAmountMinor
quotedCurrency
recoveryCreditPurchaseId
```

### Purchase activation output

```text
RecoveryCreditPurchase
REQUESTED -> ACTIVE

currentAmount = creditsGranted
providerReference = Woo charge contract ID
providerPurchaseAmount = observed provider transaction amount
providerPurchaseCurrency = USD
providerValuationConfirmedAt = receipt.receivedAt
providerPriceSnapshot = exact R15 snapshot
```

### Purchased capacity

```text
ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS)
grantedQuantity += creditsGranted
```

## Dependencies

- `ARCH-027-BACKGROUND-003`

This serializes implementation in the same Background repository/entrypoint after accepted recurring receipt and local-period tasks.

Through BACKGROUND-003/BACKGROUND-002 it also relies on API-005 durable receipt acceptance, API-004 one-time-charge intent and DATABASE-001 Woo purchase evidence.

## Enables

- `ARCH-027-BACKGROUND-005`

BACKGROUND-005 owns Woo refund-hold preparation plus verified `refunded` charge receipt settlement against the existing `RecoveryCreditRefund` lifecycle.

## Acceptance Criteria

- [ ] Existing billing worker executes BACKGROUND-004 after BACKGROUND-003; no new worker/queue/lease exists.
- [ ] At most 50 eligible charge-acquisition receipts are attempted per leased cycle.
- [ ] Only activated/canceled/prepaid_term_ended charge wrappers are selected.
- [ ] Refunded charge receipts remain unprocessed.
- [ ] Receipt claiming reuses the accepted SKIP LOCKED/in-cycle cursor pattern.
- [ ] Transition + receipt completion commit atomically.
- [ ] Missing operation correlation remains retryable/unprocessed.
- [ ] More than one matching charge operation fails closed.
- [ ] Shop/operation/purchase linkage is revalidated under deterministic locks.
- [ ] New activated purchase requires unresolved operation plus pristine REQUESTED purchase.
- [ ] Confirmed/active activated replay is idempotent and does not increment purchased credits twice.
- [ ] Exactly one completed transaction associated with a completed billing intent is required.
- [ ] Provider amount uses exact Decimal parsing.
- [ ] Initial activation requires `amount_refunded = 0`.
- [ ] Activation does not require provider transaction total to equal the pre-tax Moda quote.
- [ ] Provider price snapshot stores both quote and provider transaction evidence with no transaction URL/customer data.
- [ ] Purchase activation creates no Shopify/usage-meter evidence and no UsageEvent.
- [ ] Purchase becomes ACTIVE with `currentAmount = creditsGranted`.
- [ ] Purchased Shop counter increments exactly once.
- [ ] Operation becomes CONFIRMED atomically.
- [ ] Recovery-capacity resume is scheduled once only after new activation commits.
- [ ] Canceled/prepaid before activation sets operation FAILED and leaves historical REQUESTED purchase at zero.
- [ ] That failed acquisition no longer blocks a deliberate new purchase attempt.
- [ ] Canceled/prepaid after active purchase does not revoke/refund credits.
- [ ] Free-plan purchase activation works with null recurring contract/null acquisition BillingPeriod.
- [ ] Paid purchase activation does not require acquisition BillingPeriod still to be current/open.
- [ ] No Woo provider HTTP/credential access occurs.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted Background repository state/package scripts before choosing exact commands.

Required categories:

- [ ] repository production build/typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] activated Woo charge happy-path integration test;
- [ ] Free null-contract/null-period activation test;
- [ ] paid purchase whose acquisition period has closed still activates test;
- [ ] operation/purchase linkage negative tests;
- [ ] cross-Shop contract/link conflict tests;
- [ ] missing-operation retry test;
- [ ] OUTCOME_UNKNOWN activation test;
- [ ] confirmed/active duplicate activated idempotency test;
- [ ] partial-activation conflict test;
- [ ] completed billing-intent/transaction positive test;
- [ ] no completed transaction negative test;
- [ ] multiple completed transaction ambiguity test;
- [ ] zero/negative/non-finite provider amount tests;
- [ ] `amount_refunded > 0` activation rejection test;
- [ ] provider transaction amount greater than quoted amount (tax scenario) positive test;
- [ ] exact providerPriceSnapshot test;
- [ ] purchased-counter create test;
- [ ] purchased-counter existing/concurrent update test;
- [ ] two-worker same-receipt SKIP LOCKED/idempotency test;
- [ ] purchase/counter/operation/receipt atomic rollback test;
- [ ] canceled-before-activation -> FAILED test;
- [ ] prepaid-term-ended-before-activation -> FAILED/replay test;
- [ ] canceled-after-ACTIVE no-credit-revocation test;
- [ ] refunded receipt exclusion test;
- [ ] resume only-after-commit and once-only test;
- [ ] resume scheduling failure does not roll back activation;
- [ ] no UsageEvent creation assertion;
- [ ] no Woo provider network/credential assertion;
- [ ] bounded processingError/no-payload logging test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

Real Woo sandbox transaction/tax shape remains a terminal certification gate.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo refund reconciliation, Woo UI or Gateway work.

## Implementation Notes

Do not route Woo activation through Shopify's meter-based `reconcileProviderConfirmed()` path.

That method proves Shopify usage quantity/cost delta, which does not exist for Woo `/charges`.

The target is:

```text
Woo charge evidence
    -> RecoveryCreditPurchase ACTIVE
    -> PURCHASED_RECOVERY_CREDITS counter
```

Keep current Shopify purchase activation unchanged.

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

- API-004 persists one linked REQUESTED Woo purchase per charge.
- API-005 preserves enough signed `charge` payload structure for billing-intent/transaction validation.
- Woo transaction `amount` may include merchant tax in addition to Moda's quoted base price.
- Refunded charge handling remains separate.

### Unresolved Issues

- Exact Woo sandbox transaction/tax representation remains to be certified.
- Provider response-loss with no locally captured contract ID cannot be safely correlated from webhook alone.
- Arbitrary partial one-time-charge refund initiation remains a separate sandbox capability gate.

### Architectural Concerns

None beyond the recorded provider transaction/tax and response-loss validation gates.

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
