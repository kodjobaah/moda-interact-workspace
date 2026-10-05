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
enables:
  - ARCH-027-API-006
  - ARCH-027-ADMIN-001
created: 2026-10-03
updated: 2026-10-04
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

Keep Shopify's existing provider-scoped refund behavior and add the Woo **allowance** side of one-time-charge refunds.

```text
provider -> owns monetary refund/tax/amount
Moda     -> owns unused recovery allowance
```

Woo flow:

1. API-006 creates a local allowance hold.
2. BACKGROUND-005 waits for reservations to settle.
3. BACKGROUND-005 freezes `finalCreditQuantity` and moves to `PROVIDER_ACTION_REQUIRED`.
4. Woo/provider workflow handles money.
5. Trusted provider refund completion removes exactly the held allowance.

Moda does not calculate an expected Woo monetary refund and does not compare provider money with a locally expected amount. Unmatched provider refunds remain attention-only because money cannot be converted into a trusted credit quantity.

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

The same provider documentation also states that SaaS refund requests, including one-time charges, have **no limit on the number of days after payment**. BACKGROUND-005 therefore does not require the purchase's acquisition BillingPeriod to remain current/open; API-006 owns the purchase-local refund admission rule.

Therefore ARCH-027 v1 uses:

```text
Moda local refund hold
    -> PROVIDER_ACTION_REQUIRED
    -> provider dashboard action
    -> signed refunded webhook
    -> Background reconciliation
```

and retains the existing `NEEDS_ATTENTION` safety state when provider settlement does not match Moda's frozen business expectation.

### Provider monetary evidence is audit-only for Woo allowance correctness

BACKGROUND-004 may persist real provider purchase/transaction amount for support/audit. Woo may add tax.

ARCH-027 does not derive Woo refund allowance from that money. Provider `amount_refunded`, when present, may be stored as bounded audit evidence but never determines, increases, decreases or blocks `finalCreditQuantity`.

Shopify's existing provider correction implementation remains unchanged.

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

### R1 — Shopify automatic refund processing remains explicitly Shopify-only

Preserve existing Shopify behavior.

### R2 — Woo refund work uses the existing leased billing cycle

No new worker/queue/cron.

### R3 — Prepare bounded Woo REQUESTED allowance holds

Claim provider=WOOCOMMERCE REQUESTED refunds in bounded batches.

### R4 — Exact ADMIN-001 producer contract

ADMIN-001 creates the first and only local Woo refund row only after an operator has verified a real Woo Pending Refund for the exact purchase. That transaction sets `refundAttemptedAt`, withdraws the purchase and holds the currently unused/unreserved allowance. `expectedProviderAmount/currency` are null.

### R5 — Reserved credits delay provider action

Keep REQUESTED while purchase.reservedAmount > 0.

### R6 — Zero remaining credits cancels the local refund

If no refundable allowance remains after reservations settle, cancel the local refund and release hold accounting through the existing no-credits path.

### R7 — Freeze exact final allowance quantity

When currentAmount > 0 and reservedAmount = 0:

```text
finalCreditQuantity = purchase.currentAmount
expectedProviderAmount = NULL
expectedProviderCurrency = NULL
status = PROVIDER_ACTION_REQUIRED
reason = WOO_VENDOR_DASHBOARD_REFUND_REQUIRED
```

Before setting `PROVIDER_ACTION_REQUIRED`, make the aggregate allowance hold equal exactly `finalCreditQuantity`. If reservations released after the initial Admin hold, increment `ShopEntitlementCounter.refundingQuantity` by the additional now-unused quantity inside the same transaction. If reservations committed, the initial held quantity already excludes them.

### R8 — Provider action is external monetary settlement

Do not call Woo and do not calculate a refund amount.

### R9 — Correlate signed refunded charge evidence exactly

Use exact provider charge operation -> purchase -> live Woo refund. Never match by amount/time/customer PII.

### R10 — Existing local hold is required for automatic allowance completion

No local hold -> `WOO_REFUND_REQUEST_NOT_FOUND`, no purchase/counter mutation, no refund invented.

### R11 — Provider amount is optional audit evidence

Validate/store bounded provider monetary evidence when supplied. Never compare it with a Moda expected amount and never derive `finalCreditQuantity` from money.

### R12 — Exact allowance completion preconditions

Require provider=WOOCOMMERCE, status=PROVIDER_ACTION_REQUIRED, finalCreditQuantity>0, WITHDRAWN purchase with zero reservations/currentAmount equal finalCreditQuantity, and sufficient counter grant/refunding hold.

### R13 — Atomic allowance completion

Set purchase REFUNDED/currentAmount=0; decrement counter grant/refunding exactly by finalCreditQuantity; set refund COMPLETED/provider reference/action/confirmed timestamp; store provider amount/currency only if available; mark receipt processed.

### R14 — Idempotency

Duplicate/reordered monetary evidence cannot decrement allowance twice. Later provider amount changes are audit/support evidence only.

### R15 — Vendor rejection releases the allowance hold through Admin

Woo's normal refund rejection decision is made by Moda as the vendor. BACKGROUND does not guess that decision.

ADMIN-001 owns the audited `Record Woo refund rejected` mutation after the operator has actually rejected the Pending Refund in Woo. That mutation releases the exact local hold and restores purchase spendability when credits remain.

A later signed `refunded` receipt after a recorded rejection is an exceptional provider/local conflict and must remain attention-only; never remove allowance a second time.

### R16 — Free-plan provenance remains valid

Woo Free top-up refunds may have null BillingPeriod/provider-subscription snapshots.

### R17 — No provider network dependency / bounded logging

Process durable provider evidence only.

## Work Items

- [ ] Keep Shopify refund correction provider-scoped.
- [ ] Claim bounded Woo REQUESTED holds.
- [ ] Wait for reservations.
- [ ] Freeze finalCreditQuantity only; keep Woo expectedProviderAmount/currency null.
- [ ] Move ready refunds to PROVIDER_ACTION_REQUIRED.
- [ ] Correlate signed refunded charge evidence to exact purchase/local hold.
- [ ] Complete exact held allowance independent of provider monetary amount.
- [ ] Store provider money only as optional audit evidence.
- [ ] Leave unmatched provider refund attention non-mutating.
- [ ] Prove duplicate/reordered evidence cannot double-decrement.
- [ ] Keep vendor rejection hold release owned by ADMIN-001 and treat refunded-after-rejection as attention/conflict.

## Interfaces / Contracts

### Local Woo hold

```text
provider=WOOCOMMERCE
status=REQUESTED
purchase=WITHDRAWN
refundingQuantity holds allowance
expectedProviderAmount/currency = NULL
```

### Prepared hold

```text
status=PROVIDER_ACTION_REQUIRED
finalCreditQuantity > 0
```

### Provider input

Trusted refund outcome for the exact charge. Provider money is optional audit evidence only.

### Completed allowance

```text
purchase=REFUNDED
refund=COMPLETED
counter grant/refunding reduced by finalCreditQuantity
```

No Woo monetary equality invariant exists.

## Dependencies

- `ARCH-027-BACKGROUND-004`

BACKGROUND-004 must be architect-accepted Complete so Woo purchase activation/evidence and charge receipt ordering are stable before refund reconciliation is introduced.

Through BACKGROUND-004, this task also relies on API-005 signed receipt acceptance and the ARCH-027 database provider-neutral refund schema.

## Enables

- `ARCH-027-API-006`
- `ARCH-027-ADMIN-001`

ADMIN-001 produces the `provider=WOOCOMMERCE`, `status=REQUESTED` allowance holds consumed here after vendor verification of a real Woo Pending Refund. API-006 is read-only history/refund navigation.

ADMIN-001 makes the existing Platform Admin refund queue/provider-evidence support surface Woo-aware and exposes bounded read-only attention for unmatched/exceptional refunded receipts.

Further follow-ons remain:

- exceptional Admin Woo unmatched/NEEDS_ATTENTION recovery;
- Woo billing UI purchase-history/provider-refund navigation;
- Woo sandbox certification of provider partial-refund capability.

## Acceptance Criteria

- [ ] Shopify refund behavior unchanged/provider-scoped.
- [ ] Woo preparation freezes finalCreditQuantity only.
- [ ] Woo expectedProviderAmount/currency remain null.
- [ ] PROVIDER_ACTION_REQUIRED means allowance held while provider handles money.
- [ ] Trusted refunded outcome completes exact held allowance independent of provider amount.
- [ ] Monetary evidence, when stored, is audit-only.
- [ ] Unmatched provider refund creates no local refund/allowance mutation.
- [ ] Duplicate/reordered provider evidence cannot remove allowance twice.
- [ ] Provider rejection release is not guessed.
- [ ] Free Woo refund null-period provenance remains valid.
- [ ] No provider network call.
- [ ] `_index.md` unchanged.

## Validation

- [ ] Shopify refund regression;
- [ ] reservation wait / zero-remaining cancel;
- [ ] REQUESTED -> PROVIDER_ACTION_REQUIRED finalCreditQuantity;
- [ ] Woo expectedProviderAmount/currency null proof;
- [ ] exact charge/purchase/refund correlation;
- [ ] refunded evidence completes allowance with monetary amount absent/different;
- [ ] unmatched provider refund no-mutation attention;
- [ ] duplicate/reordered evidence no-double-decrement;
- [ ] Free null-period refund;
- [ ] no provider HTTP/credentials;
- [ ] `git diff --check` + worktree/submodule/push evidence.

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
