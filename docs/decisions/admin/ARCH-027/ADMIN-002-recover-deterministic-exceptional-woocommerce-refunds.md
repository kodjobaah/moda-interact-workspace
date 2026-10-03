---
id: ARCH-027-ADMIN-002
architecture_id: ARCH-027
title: Recover deterministic exceptional WooCommerce refunds
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-ADMIN-001
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Recover deterministic exceptional WooCommerce refunds

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Add **two narrowly bounded SUPER_ADMIN recovery actions** for exceptional Woo one-time-charge refund cases where provider money has already moved and the normal BACKGROUND-005 path cannot finish automatically.

The allowed recovery cases are exactly:

```text
A. EXISTING LOCAL REFUND HOLD + PROVIDER OVER-REFUND

RecoveryCreditRefund
    provider = WOOCOMMERCE
    status = NEEDS_ATTENTION
    reason = WOO_PROVIDER_REFUND_AMOUNT_MISMATCH

actual provider refund > frozen expected amount

        -> SUPER_ADMIN explicitly accepts provider over-refund
        -> remove the already-frozen final credit quantity
        -> purchase REFUNDED
        -> refund COMPLETED
```

and:

```text
B. PROVIDER REFUND EXISTS + NO LOCAL REFUND HOLD

unprocessed refunded Woo receipt
    processingError = WOO_REFUND_REQUEST_NOT_FOUND
        |
        v
unique charge operation + purchase
        |
        v
purchase ACTIVE
reservedAmount = 0
currentAmount > 0
        |
        v
provider refunded amount is:
    exactly the amount required for ALL current unused credits
    OR greater than that amount with explicit over-refund acceptance
        |
        v
SUPER_ADMIN creates one audited ADMIN recovery refund
and removes ALL currently unused credits
```

ADMIN-002 MUST NOT introduce arbitrary partial-lot refund semantics.

If provider money is **less** than the amount required to refund all currently unused/unreserved credits:

```text
NO local completion action
NO inferred smaller credit quantity
NO counter mutation
```

The operator must correct/complete provider settlement first and wait for newer cumulative provider evidence.

The same restriction applies when:

```text
reservedAmount > 0
purchase has no remaining credits
provider transaction identity is ambiguous
local counter state is inconsistent
provider refund evidence cannot be proven
```

This is an exceptional accounting recovery task, not a generic "force refund" tool.

## Context

ADMIN-001 makes the existing Admin refund support surface Woo-aware and deliberately read-only for exceptional provider evidence.

It closes the unsafe generic manual-settlement path for Woo and exposes:

```text
Woo PROVIDER_ACTION_REQUIRED
Woo NEEDS_ATTENTION
unprocessed WOO_REFUND_* receipts
```

without credit mutation.

BACKGROUND-005 owns the normal path:

```text
local refund hold
    -> provider action
    -> signed refunded webhook
    -> exact amount
    -> local refund COMPLETED
```

and records a mismatch as:

```text
status = NEEDS_ATTENTION
reason = WOO_PROVIDER_REFUND_AMOUNT_MISMATCH
```

while preserving the local purchase hold.

BACKGROUND-005 also deliberately leaves an externally approved provider refund unmatched when no local refund exists:

```text
processingError = WOO_REFUND_REQUEST_NOT_FOUND
processedAt = NULL
```

### Product refund invariant

Moda's purchase-lot refund semantics refund the **remaining unused/unreserved portion of one exact purchase lot**.

They do not support:

```text
merchant chooses an arbitrary credit quantity
provider amount is heuristically converted to a smaller credit quantity
partial lot remains ACTIVE after a normal refund
```

Normal refund preparation therefore waits for reservations to settle and freezes:

```text
finalCreditQuantity = purchase.currentAmount
```

ADMIN-002 preserves that invariant for exceptional recovery.

### Why provider under-refund is not locally completed

Suppose:

```text
purchase creditsGranted = 10
purchase currentAmount  = 6
purchase reservedAmount = 0
provider purchase amount = 12.00

required refund for all remaining credits:
    12.00 * 6/10 = 7.20
```

If Woo reports only:

```text
amount_refunded = 4.80
```

Moda cannot safely decide that this should mean "refund four credits" without introducing a new arbitrary partial-lot product rule.

ADMIN-002 therefore does not do that.

The provider settlement must first become sufficient for the whole remaining local refund quantity.

### Cumulative provider refund evidence

Woo refund evidence is treated as cumulative `amount_refunded` on the original provider transaction.

The companion BACKGROUND-005 correction in this task allows a later **monotonically increasing** refund webhook to update a `NEEDS_ATTENTION` refund:

```text
under-refund
    -> later provider refund increases cumulative amount

if cumulative amount == frozen expected amount
    -> normal BACKGROUND completion

if cumulative amount still < expected
    -> remain NEEDS_ATTENTION with newer evidence

if cumulative amount > expected
    -> remain NEEDS_ATTENTION
    -> ADMIN-002 may explicitly accept the over-refund
```

A decreasing/non-monotonic amount or different provider transaction remains a provider-evidence conflict.

## Scope

Modify only `moda-interact-admin` implementation/tests required for:

1. explicit over-refund acceptance on an existing Woo `NEEDS_ATTENTION` refund;
2. deterministic recovery of an unmatched externally refunded Woo purchase;
3. exact audit/support-message recording;
4. safe mutation controls inside the ADMIN-001 support surface.

Expected implementation areas conceptually:

```text
src/lib/admin/
  woo-refund-exception-recovery.ts
  woo-refund-receipt-attention.ts

src/components/admin/
  recovery-credit-refunds.tsx
  woo-refund-receipt-attention.tsx

src/app/actions/recovery-credit-refunds.ts

tests/
```

Use the existing Admin refund settlement/audit/system-message conventions where safe.

No new database table/status enum is required.

## Out of Scope

- Normal Woo PROVIDER_ACTION_REQUIRED settlement.
- Calling Woo APIs.
- Woo credentials.
- Initiating/refunding provider money.
- Arbitrary partial-lot recovery.
- Completing provider under-refunds.
- Recovering a purchase with active reserved credits.
- Reversing consumed credit history.
- Restoring provider-refunded money.
- Resolving subscription refunds.
- Shopify refund behavior changes.
- Merchant-facing UI.
- Database schema/migration changes.
- Gateway/system-test implementation.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — SUPER_ADMIN only

Both ADMIN-002 mutations require:

```text
requirePlatformAdminMutation()
principal.role = SUPER_ADMIN
```

No `PLATFORM_ADMIN` mutation path exists.

Reads continue to use ADMIN-001's existing Platform Admin read boundary.

### R2 — Explicit confirmation and operator note

Every exceptional recovery action requires:

```text
confirmed = true
operatorNote
```

`operatorNote`:

```text
trimmed
10..1000 characters
```

The note is audit evidence, not provider evidence.

Do not accept an empty/generic click-through mutation.

### R3 — No caller-controlled credit or money amount

Neither action accepts:

```text
creditQuantity
refundAmount
currency
providerReference
providerTransactionId
shopId
purchaseId override
```

The server derives every financial/credit value from durable purchase/refund/receipt evidence.

The browser/Admin form selects only the durable entity:

```text
refundId
or
receiptId
```

plus confirmation/note and the explicit over-refund acknowledgement when required.

### R4 — Exact Decimal proportional expected amount helper

Use one server-side helper:

```text
expectedForCredits =
    providerPurchaseAmount
      * Decimal(creditQuantity)
      / Decimal(purchase.creditsGranted)

rounded to 2 decimal places
```

with exact Decimal arithmetic.

Do not use JS floating point.

Require:

```text
creditQuantity > 0
creditQuantity <= purchase.creditsGranted
providerPurchaseAmount > 0
currency = USD
```

### R5 — Existing NEEDS_ATTENTION action is over-refund only

Add a mutation conceptually:

```text
acceptWooProviderOverRefund({
  refundId,
  confirmed,
  operatorNote,
  acceptProviderOverRefund
})
```

Require:

```text
acceptProviderOverRefund = true
```

and all R6-R11 preconditions.

Do not provide a completion mutation for provider under-refund.

### R6 — Existing refund provider/state preconditions

For over-refund acceptance require exactly:

```text
refund.provider = WOOCOMMERCE
refund.status = NEEDS_ATTENTION
refund.reason = WOO_PROVIDER_REFUND_AMOUNT_MISMATCH

refund.providerActionKind = REFUND
refund.providerReference non-blank
refund.providerAmount non-null
refund.providerCurrency = USD
refund.providerConfirmedAt non-null

refund.finalCreditQuantity > 0
refund.expectedProviderAmount > 0
refund.expectedProviderCurrency = USD
```

`providerConfirmedByPlatformAdminId` is expected to remain null because provider confirmation came from the signed webhook.

### R7 — Over-refund amount must be strictly greater than expected

Require:

```text
refund.providerAmount > refund.expectedProviderAmount
```

If:

```text
providerAmount < expectedProviderAmount
```

reject with a bounded message equivalent to:

> Woo has refunded less than Moda's frozen expected amount. Complete/correct the provider refund first; Moda will not remove all held credits for an under-refund.

If equal, reject and instruct the operator to allow normal Background reconciliation/retry rather than using exceptional recovery.

### R8 — Existing over-refund purchase/counter preconditions

Lock/revalidate:

```text
purchase.provider = WOOCOMMERCE
purchase.status = WITHDRAWN
purchase.reservedAmount = 0
purchase.currentAmount = refund.finalCreditQuantity

counter = PURCHASED_RECOVERY_CREDITS
counter.refundingQuantity >= refund.finalCreditQuantity
counter.grantedQuantity >= refund.finalCreditQuantity
```

Require the refund/purchase/shop IDs match exactly.

No action is available if local purchase state changed.

### R9 — Over-refund completion preserves provider evidence

The exceptional action does **not** rewrite:

```text
providerReference
providerActionKind
providerAmount
providerCurrency
providerConfirmedAt
expectedProviderAmount
expectedProviderCurrency
finalCreditQuantity
```

Those preserve:

```text
what Moda expected
vs
what Woo actually refunded
```

Set:

```text
approvedByPlatformAdminId = principal.id
approvedAt = now
reason = ADMIN_ACCEPTED_WOO_PROVIDER_OVERREFUND
```

`providerConfirmedByPlatformAdminId` remains unchanged/null.

### R10 — Atomic over-refund local completion

In one Serializable transaction:

```text
RecoveryCreditPurchase:
    currentAmount = 0
    reservedAmount = 0
    status = REFUNDED
    version += 1

ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS):
    refundingQuantity -= refund.finalCreditQuantity
    grantedQuantity   -= refund.finalCreditQuantity
    version += 1

RecoveryCreditRefund:
    status = COMPLETED
    completedAt = now
    approvedByPlatformAdminId = principal.id
    approvedAt = now
    reason = ADMIN_ACCEPTED_WOO_PROVIDER_OVERREFUND
    version += 1
```

Preserve counter committed/reserved quantities.

Use CAS/version predicates.

### R11 — Over-refund action is state-idempotent

If a retry finds:

```text
refund.status = COMPLETED
refund.reason = ADMIN_ACCEPTED_WOO_PROVIDER_OVERREFUND
purchase.status = REFUNDED
purchase.currentAmount = 0
```

return the persisted completed result without another counter decrement/audit/system message duplication.

Other completed states are not treated as this action's replay.

### R12 — Unmatched recovery starts from one exact attention receipt

Add a mutation conceptually:

```text
recoverUnmatchedWooRefund({
  receiptId,
  confirmed,
  operatorNote,
  acceptProviderOverRefund
})
```

Require receipt:

```text
topic = saas_billing_contract.refunded
processedAt = NULL
processingError = WOO_REFUND_REQUEST_NOT_FOUND
normalizedPayload has exactly one charge wrapper
```

Do not permit this action for other `WOO_REFUND_*` processing errors.

### R13 — Selected receipt must be latest provider refund evidence for the charge

Before mutation, require there is no newer unprocessed:

```text
topic = saas_billing_contract.refunded
providerContractId = selected providerContractId
```

receipt ordered by:

```text
receivedAt
then id
```

If newer evidence exists, reject with:

```text
Newer Woo refund evidence exists. Refresh the attention queue.
```

This prevents recovery from a stale cumulative refund amount.

### R14 — Unmatched receipt must correlate uniquely

Resolve exactly:

```text
providerContractId
    -> ONE_TIME_CHARGE WooCommerceBillingOperation
    -> recoveryCreditPurchaseId
    -> RecoveryCreditPurchase
```

Require:

```text
one operation only
operation.state = CONFIRMED
operation.shopId = purchase.shopId

purchase.provider = WOOCOMMERCE
purchase.providerReference = providerContractId
```

Ambiguous/missing correlation has no mutation action.

### R15 — Exact provider transaction identity

Read BACKGROUND-004's accepted:

```text
purchase.providerPriceSnapshot
```

and require exact v1 Woo shape with:

```text
providerTransactionId
providerBillingIntentId
providerTransactionAmount
```

From the selected receipt require exactly one transaction with:

```text
id = providerTransactionId
completed_at non-blank
amount positive finite Decimal
amount_refunded positive finite Decimal
amount_refunded <= amount
```

Currency is:

```text
USD
```

No alternative provider transaction may be selected manually.

### R16 — Unmatched recovery requires an ACTIVE, fully unreserved purchase

Require:

```text
purchase.status = ACTIVE
purchase.currentAmount > 0
purchase.reservedAmount = 0
```

Do not recover:

```text
WITHDRAWN
COMPLETED
REFUNDED
REQUESTED
```

purchases through the unmatched action.

Do not recover while any purchase credits are currently reserved.

### R17 — No live local refund may exist

Before creating an exceptional recovery refund, require no local Woo refund for the purchase in:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

If one exists, the operator must resolve that local refund path instead.

Historical:

```text
CANCELLED
REJECTED
```

refunds may exist and remain audit history.

A prior `COMPLETED` refund for the same purchase is a hard conflict because the purchase should not still be ACTIVE.

### R18 — Unmatched expected amount is for ALL currently unused credits

Define:

```text
recoveryCreditQuantity = purchase.currentAmount

expectedProviderAmount =
    R4(
      providerPurchaseAmount = purchase.providerPurchaseAmount,
      creditQuantity = purchase.currentAmount,
      purchase.creditsGranted
    )
```

Require:

```text
expectedProviderAmount > 0
```

This action does not search for another credit quantity.

### R19 — Under-refunded unmatched provider evidence is not recoverable

If:

```text
actualProviderRefundAmount < expectedProviderAmount
```

do not mutate.

Return a bounded message equivalent to:

> Woo has refunded less than the amount required to refund all currently unused credits on this purchase. Complete/correct the provider refund first and wait for newer provider evidence.

Do not infer:

```text
actual amount -> smaller credit quantity
```

### R20 — Exact unmatched amount needs no over-refund acknowledgement

If:

```text
actualProviderRefundAmount = expectedProviderAmount
```

the exceptional recovery may proceed with:

```text
acceptProviderOverRefund = false
```

or omitted/false.

### R21 — Unmatched over-refund requires explicit acknowledgement

If:

```text
actualProviderRefundAmount > expectedProviderAmount
```

require:

```text
acceptProviderOverRefund = true
```

and show the operator both:

```text
expected provider refund
actual provider refund
```

before confirmation.

The local recovery still removes only:

```text
purchase.currentAmount
```

unused credits.

It does not attempt to claw back previously consumed credits.

### R22 — Deterministic exceptional recovery request key

Create the new Admin recovery refund with:

```text
canonicalIntent =
  "arch027-admin-unmatched-woo-refund-v1\n"
  + receiptId + "\n"
  + purchaseId + "\n"
  + providerTransactionId + "\n"

requestKey =
  "woo-external-refund-recovery-v1:"
  + lower-case hex SHA-256(canonicalIntent)
```

A retry of the same selected receipt resolves the same recovery row.

### R23 — Exact Admin recovery refund row

Create one:

```text
RecoveryCreditRefund
    provider = WOOCOMMERCE
    source = ADMIN
    sourceMessageId = NULL
    requestedByShopifyUserId = NULL

    shopId = purchase.shopId
    purchaseId = purchase.id

    purchaseCreditsGrantedSnapshot = purchase.creditsGranted
    currentAmountAtRequestSnapshot = purchase.currentAmount
    reservedAmountAtRequestSnapshot = 0
    availableAmountAtRequestSnapshot = purchase.currentAmount

    billingPeriodIdSnapshot = purchase.billingPeriodId
    providerSubscriptionIdSnapshot =
      purchase.providerSubscriptionIdSnapshot

    planHandleSnapshot = NULL
    eventHandleSnapshot = NULL
    shopifyPartnerDevelopmentSnapshot = false

    purchaseProviderAmountSnapshot =
      purchase.providerPurchaseAmount
    purchaseProviderCurrencySnapshot = USD

    finalCreditQuantity = purchase.currentAmount
    expectedProviderAmount = R18 expected
    expectedProviderCurrency = USD

    automaticCorrectionUsageEventId = NULL
    all Shopify correction evidence = NULL

    providerReference =
      "woocommerce:charge:"
      + providerContractId
      + ":transaction:"
      + providerTransactionId

    providerActionKind = REFUND
    providerAmount = actualProviderRefundAmount
    providerCurrency = USD
    providerConfirmedByPlatformAdminId = NULL
    providerConfirmedAt = receipt.receivedAt

    approvedByPlatformAdminId = principal.id
    approvedAt = now
    holdAppliedAt = now

    status = COMPLETED
    completedAt = now

    reason =
      ADMIN_RECOVERED_UNMATCHED_WOO_REFUND
      or
      ADMIN_RECOVERED_UNMATCHED_WOO_OVERREFUND
```

No intermediate REQUESTED/PROVIDER_ACTION_REQUIRED state is created because provider money has already moved.

### R24 — Atomic unmatched recovery credit mutation

In the same Serializable transaction:

```text
quantity = purchase.currentAmount
```

Require current aggregate:

```text
counter = PURCHASED_RECOVERY_CREDITS
counter.grantedQuantity >= quantity

counter.grantedQuantity - quantity
    >= counter.committedQuantity
       + counter.reservedQuantity
       + counter.refundingQuantity
```

Then:

```text
purchase:
    currentAmount = 0
    reservedAmount = 0
    status = REFUNDED
    version += 1

counter:
    grantedQuantity -= quantity
    version += 1

new recovery refund:
    COMPLETED

selected receipt:
    processedAt = now
    processingError = NULL
```

Do not decrement `refundingQuantity` because no local hold existed.

### R25 — Unmatched recovery action is state-idempotent

If a retry finds the deterministic R22 refund already:

```text
status = COMPLETED
purchase = REFUNDED
selected receipt processed
```

return the persisted recovery result.

Do not decrement the counter again.

### R26 — Audit every exceptional mutation

Reuse:

```text
BillingAuditAction.RECOVERY_CREDIT_REFUND
```

Create one idempotent audit record per exceptional recovery.

Audit must include bounded before/after evidence:

```text
refund/receipt id
purchase id
provider contract/transaction reference
expected provider amount
actual provider amount
credit quantity removed
operator note
resolution kind
```

Do not include full Woo payload/customer/payment data.

### R27 — Merchant completion system message

When either exceptional action completes local refund accounting, emit the existing idempotent:

```text
BILLING_SYSTEM_MESSAGE_CODES.REFUND_COMPLETED
```

merchant system message with provider-neutral text.

Do not tell the merchant that a Platform Admin manually repaired internal accounting.

### R28 — UI action for existing Woo over-refund

In ADMIN-001's Woo `NEEDS_ATTENTION` detail:

When all R6-R8 read predicates indicate:

```text
providerAmount > expectedProviderAmount
```

and local state is otherwise recoverable, show a SUPER_ADMIN-only action:

```text
Accept Woo over-refund and complete local refund
```

The confirmation UI must display:

```text
final credit quantity to remove
expected provider amount
actual provider amount
difference
```

plus:

```text
operator note
explicit confirmation checkbox
explicit over-refund acknowledgement checkbox
```

### R29 — Under-refund UI is remediation-only

When:

```text
providerAmount < expectedProviderAmount
```

show no completion button.

Show guidance equivalent to:

> Provider settlement is lower than Moda expected. Correct/complete the Woo refund in the provider workflow and wait for a newer refunded webhook. Moda will not reduce the held credit quantity to fit an under-refund.

### R30 — UI action for safely recoverable unmatched receipt

In ADMIN-001's receipt-attention detail for:

```text
WOO_REFUND_REQUEST_NOT_FOUND
```

show:

```text
Recover external Woo refund
```

only when server-projected recovery eligibility proves:

```text
unique operation/purchase
purchase ACTIVE
reservedAmount = 0
currentAmount > 0
no live refund
valid provider transaction
actual provider refund >= expected amount for all current credits
selected receipt is latest evidence
aggregate can safely remove quantity
```

Do not enable based only on client-side inspection.

### R31 — Server computes recovery eligibility

Add a read projection for each unmatched attention item/detail:

```text
recoveryEligible: boolean
recoveryUnavailableReason: bounded code | null
expectedProviderAmountForCurrentCredits: string | null
actualProviderRefundAmount: string | null
providerOverRefund: boolean
recoverableCreditQuantity: number | null
```

The mutation recomputes/revalidates everything transactionally.

Allowed unavailable reason codes include:

```text
NEWER_PROVIDER_EVIDENCE_EXISTS
CORRELATION_NOT_UNIQUE
PURCHASE_NOT_ACTIVE
PURCHASE_HAS_RESERVATIONS
NO_REMAINING_CREDITS
LIVE_REFUND_EXISTS
PROVIDER_EVIDENCE_INVALID
PROVIDER_UNDER_REFUND
COUNTER_STATE_CONFLICT
```

### R32 — No generic force-complete action

ADMIN-002 MUST NOT create a button/API concept such as:

```text
Force complete refund
Override credits
Set refund amount
Mark processed
```

Every mutation must be one of the exact deterministic actions above.

### R33 — Shopify remains unchanged

Do not alter Shopify:

```text
manual provider evidence flow
automatic correction flow
refund completion arithmetic
Admin authorization
```

except for shared helper extraction that is behavior-preserving.

### R34 — Structured logging/secrets

Use the existing Admin structured logger/audit conventions.

Never log:

```text
full normalized Woo payload
webhook signature
Woo credentials
customer/payment data
```

Bounded IDs, resolution kind and amount/credit audit values are permitted in the financial audit event.

## Work Items

- [ ] Add exact Decimal helper for expected amount of a specified credit quantity.
- [ ] Add SUPER_ADMIN over-refund acceptance service/action for existing Woo NEEDS_ATTENTION refund.
- [ ] Reject under-refund/exact-amount misuse of that exceptional action.
- [ ] Add CAS/idempotent purchase/counter/refund completion for accepted over-refund.
- [ ] Add latest-evidence/unique-correlation projection for unmatched WOO_REFUND_REQUEST_NOT_FOUND receipts.
- [ ] Add safe recovery eligibility projection and bounded unavailable reasons.
- [ ] Add SUPER_ADMIN unmatched-refund recovery action.
- [ ] Require ACTIVE/unreserved purchase and all-current-credit quantity.
- [ ] Reject provider under-refund rather than deriving a partial credit quantity.
- [ ] Require explicit over-refund acknowledgement when actual > expected.
- [ ] Create exact ADMIN RecoveryCreditRefund recovery row with deterministic requestKey.
- [ ] Atomically update purchase/counter/receipt.
- [ ] Add idempotent audit + REFUND_COMPLETED merchant message.
- [ ] Add exact Admin confirmation/warning UI for both exceptional actions.
- [ ] Add no-action remediation UI for provider under-refund.
- [ ] Preserve all Shopify behavior.
- [ ] Add focused financial/concurrency/security tests.

## Interfaces / Contracts

### Existing mismatch recovery

Input entity:

```text
RecoveryCreditRefund
provider = WOOCOMMERCE
status = NEEDS_ATTENTION
reason = WOO_PROVIDER_REFUND_AMOUNT_MISMATCH
```

Action:

```text
accept Woo provider over-refund
```

only when:

```text
providerAmount > expectedProviderAmount
```

### Unmatched provider recovery

Input entity:

```text
WooCommerceBillingWebhookReceipt
topic = refunded
processedAt = null
processingError = WOO_REFUND_REQUEST_NOT_FOUND
```

Correlates:

```text
receipt
 -> ONE_TIME_CHARGE operation
 -> ACTIVE Woo purchase
 -> PURCHASED_RECOVERY_CREDITS counter
```

Output:

```text
ADMIN RecoveryCreditRefund COMPLETED
purchase REFUNDED
counter grant reduced
receipt processed
```

### Under-refund

No Admin mutation.

Provider settlement must progress first.

## Dependencies

- `ARCH-027-ADMIN-001`

ADMIN-001 must be architect-accepted Complete before ADMIN-002 becomes Ready because it owns the provider-aware support projection, receipt-attention read model and Shopify-only manual settlement guard.

Through ADMIN-001, this task also depends on BACKGROUND-005's refund evidence semantics.

## Enables

None yet.

After ADMIN-002 the remaining ARCH-027 work should move to:

```text
Gateway/deployment wiring
Shopify regression/compatibility review
system/sandbox validation
architecture completion/index update
```

rather than adding broader refund machinery unless implementation/sandbox evidence exposes another gap.

## Acceptance Criteria

- [ ] Only SUPER_ADMIN may execute either exceptional recovery mutation.
- [ ] Both mutations require explicit confirmation plus a bounded operator note.
- [ ] No caller controls credit quantity, refund amount/currency or provider identity.
- [ ] Existing Woo NEEDS_ATTENTION can be exceptionally completed only when actual provider refund is strictly greater than frozen expected amount.
- [ ] Existing Woo under-refund cannot be completed by Admin.
- [ ] Existing over-refund completion removes exactly the already-frozen finalCreditQuantity and never changes provider/expected evidence.
- [ ] Existing over-refund completion is CAS-safe/idempotent and decrements purchased grant/refunding exactly once.
- [ ] Unmatched recovery is offered only for `WOO_REFUND_REQUEST_NOT_FOUND`.
- [ ] Selected unmatched receipt must be the latest refunded evidence for the provider charge.
- [ ] Operation/purchase correlation must be unique and trusted.
- [ ] Unmatched recovery requires ACTIVE Woo purchase with zero reserved credits and positive current amount.
- [ ] No live Woo refund may already exist.
- [ ] Provider transaction is selected only by BACKGROUND-004's frozen transaction ID.
- [ ] Provider `amount_refunded` must be positive and <= transaction amount.
- [ ] Expected unmatched refund is calculated only for all current unused credits.
- [ ] Provider under-refund cannot be mapped to a smaller partial credit quantity.
- [ ] Exact provider amount recovery succeeds without over-refund acknowledgement.
- [ ] Provider over-refund recovery requires explicit acknowledgement and still removes only all currently unused credits.
- [ ] Exceptional unmatched recovery creates one deterministic ADMIN COMPLETED RecoveryCreditRefund row.
- [ ] Unmatched recovery decrements grantedQuantity but not refundingQuantity because no prior hold existed.
- [ ] Counter invariant is proven before decrement.
- [ ] Selected unmatched receipt becomes processed only in the same successful accounting transaction.
- [ ] Replay cannot double-decrement credits/counter.
- [ ] Every exceptional mutation creates one bounded BillingAuditAction.RECOVERY_CREDIT_REFUND audit event.
- [ ] Every completed exceptional recovery emits the existing idempotent merchant refund-completed system message.
- [ ] No generic force-complete/mark-processed/arbitrary-amount UI exists.
- [ ] Shopify refund workflows remain behaviorally unchanged.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted Admin package/repository instructions before choosing exact commands.

Required validation categories:

- [ ] Prisma generate/validate against accepted ARCH-027 schema;
- [ ] repository typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] production build;
- [ ] existing Admin refund/security suites remain green;
- [ ] exact Decimal proportional expected amount tests;
- [ ] existing NEEDS_ATTENTION exact-amount exceptional-action rejection test;
- [ ] existing NEEDS_ATTENTION under-refund rejection test;
- [ ] existing NEEDS_ATTENTION over-refund completion integration test;
- [ ] existing over-refund replay no-double-decrement test;
- [ ] over-refund purchase/counter conflict rollback test;
- [ ] unmatched exact provider amount recovery integration test;
- [ ] unmatched provider over-refund with explicit acknowledgement integration test;
- [ ] unmatched provider over-refund without acknowledgement rejection test;
- [ ] unmatched provider under-refund no-mutation test;
- [ ] unmatched purchase reservedAmount>0 no-mutation test;
- [ ] unmatched inactive/completed/refunded purchase no-mutation tests;
- [ ] newer refunded receipt exists -> stale selected receipt rejection test;
- [ ] ambiguous/missing ONE_TIME_CHARGE correlation no-mutation tests;
- [ ] wrong provider transaction ID / malformed provider snapshot no-mutation tests;
- [ ] `amount_refunded > transaction.amount` rejection test;
- [ ] live local refund exists no-unmatched-recovery test;
- [ ] aggregate invariant conflict rollback test;
- [ ] deterministic requestKey/replay test;
- [ ] receipt processed atomically with unmatched accounting recovery test;
- [ ] BillingAuditAction financial before/after evidence test;
- [ ] REFUND_COMPLETED system-message idempotency test;
- [ ] PLATFORM_ADMIN mutation denial tests;
- [ ] crafted caller quantity/money/provider-input absence test;
- [ ] Shopify manual/automatic refund regression suites;
- [ ] no raw Woo payload/secrets/customer data logging test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Gateway or system-test work.

## Implementation Notes

The task is intentionally stricter than a generic financial support console.

Safe principle:

```text
provider money already moved
        |
        v
only perform a local credit mutation
when the exact purchase/transaction is proven
and the mutation remains the existing
"refund all remaining unused credits" product rule
```

Do not solve provider under-refund by inventing partial-lot credit semantics.

For existing over-refund, accepting the provider overage is an explicit SUPER_ADMIN financial exception; the local credit quantity remains the already-frozen full remaining quantity.

For unmatched recovery, the Admin-created refund row exists to restore durable audit/provenance after provider money moved first. It must never be silently synthesized by Background.

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

- BACKGROUND-005 is corrected/implemented to accept monotonic cumulative refunded evidence for an existing NEEDS_ATTENTION Woo refund.
- ADMIN-001 is accepted and supplies the provider-aware attention/support projection.
- Exceptional recovery preserves the current product rule of refunding all remaining unused/unreserved credits, not arbitrary partial credit quantities.

### Unresolved Issues

- A provider under-refund remains unresolved until the provider settlement increases sufficiently.
- A provider refund against a purchase with consumed-all/no remaining credits cannot be represented as a normal credit refund and remains an external financial/support exception.
- Provider money that cannot be uniquely tied to the frozen purchase transaction remains non-recoverable by this task.

### Architectural Concerns

None beyond those deliberately non-recoverable financial exception classes.

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
