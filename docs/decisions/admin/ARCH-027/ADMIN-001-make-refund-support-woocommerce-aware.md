---
id: ARCH-027-ADMIN-001
architecture_id: ARCH-027
title: Make recovery-credit refund support WooCommerce-aware
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-005
enables: []
created: 2026-10-04
updated: 2026-10-05
---

# Make recovery-credit refund support WooCommerce-aware

## Objective

Extend the existing Admin `Billing -> Refund requests` support surface so Moda can act as the Woo SaaS **vendor** while keeping the provider-money / Moda-allowance boundary explicit.

Woo merchant refund flow:

```text
merchant requests refund on WooCommerce.com Orders
    -> request appears for Moda/vendor in Woo SaaS Apps -> Pending Refunds
    -> SUPER_ADMIN correlates exact Moda purchase
    -> Prepare Woo refund in Moda
    -> allowance held / purchase WITHDRAWN
    -> reservations settle
    -> BACKGROUND-005 -> PROVIDER_ACTION_REQUIRED
    -> operator APPROVES or REJECTS in Woo
```

Approval is completed locally only from the trusted Woo `refunded` webhook. Rejection is a vendor decision; because the public Woo contract does not document a rejection webhook, Admin owns an audited `Record Woo refund rejected` fallback.

## Scope

Reuse the existing refund queue/detail UI. Add:

- provider-aware refund presentation/filtering;
- exact Woo purchase/provider evidence needed to correlate a Woo Pending Refund;
- SUPER_ADMIN `Prepare Woo refund` mutation;
- SUPER_ADMIN `Record Woo refund rejected` mutation;
- Woo `PROVIDER_ACTION_REQUIRED` guidance;
- completed/unmatched provider receipt attention.

Preserve Shopify automatic/manual flows.

## Out of Scope

- Initiating the merchant refund request with Woo.
- Calculating monetary refund amount.
- Merchant refund reactivation.
- Completing a Woo refund manually after approval; the signed `refunded` webhook owns completion.
- Inferring allowance from an unmatched provider monetary refund.
- New Admin navigation.
- `docs/architecture/_index.md`.

## Requirements

### R1 — Reuse existing Refund requests surface

No new top-level page.

### R2 — Provider-aware projection/filter

Expose `SHOPIFY|WOOCOMMERCE` provider safely and make Woo-nullable billing/Shopify snapshots truly nullable in Admin types.

### R3 — Correlating a Woo Pending Refund

The operator must identify the exact `RecoveryCreditPurchase` using bounded provider/purchase evidence.

Show at least:

```text
purchase ID
shop
bundle/plan label
provider charge reference
provider purchase amount/currency (audit only)
credits granted/current/reserved
refundAttemptedAt
```

SYSTEM-TEST-002 must certify which Woo Pending Refund identifier(s) are visible to the vendor. If the dashboard exposes an order/reference not currently persisted, stop and return that schema gap to `moda_architect`; do not correlate by price/time/customer PII.

### R4 — Prepare Woo refund is SUPER_ADMIN-only

Mutation conceptually:

```text
prepareWooPendingRefund({ purchaseId, confirmed, operatorNote })
```

Require:

```text
SUPER_ADMIN
provider = WOOCOMMERCE
purchase.status = ACTIVE
purchase.currentAmount > 0
purchase.refundAttemptedAt = NULL
valid provider purchase reference/evidence
confirmed = true
operatorNote 10..1000 chars
```

The operator confirmation explicitly states that a real matching Woo Pending Refund has been verified.

### R5 — Prepare transaction is the first/only attempt boundary

In one Serializable transaction:

```text
refundAttemptedAt: NULL -> now        # guarded CAS
available = currentAmount - reservedAmount
available > 0

create RecoveryCreditRefund:
    provider = WOOCOMMERCE
    source = ADMIN
    status = REQUESTED
    availableAmountAtRequestSnapshot = available
    expectedProviderAmount = NULL
    expectedProviderCurrency = NULL
    requestKey = deterministic purchase-based vendor-refund key

purchase.status: ACTIVE -> WITHDRAWN
counter.refundingQuantity += available
```

A second attempt fails closed even if the first refund later becomes REJECTED/CANCELLED.

### R6 — Existing reservations are not interrupted

The prepare action does not release or cancel `UsageReservation`s already RESERVED. BACKGROUND-005 waits for them to commit/release and then expands the hold if released credits become refundable.

### R7 — Vendor decision readiness

While refund is REQUESTED, tell the operator to wait.

When BACKGROUND-005 reaches:

```text
status = PROVIDER_ACTION_REQUIRED
finalCreditQuantity > 0
```

show:

> The Moda allowance hold is final. Approve or reject the matching request in Woo SaaS Apps → Pending Refunds.

No expected monetary amount is calculated by Moda.

### R8 — Approval has no Admin completion action

After the operator APPROVES in Woo, Admin only waits for provider evidence.

A signed `saas_billing_contract.refunded` event completes the allowance through BACKGROUND-005.

### R9 — Record Woo refund rejected

Mutation conceptually:

```text
recordWooRefundRejected({ refundId, confirmed, operatorNote })
```

Require SUPER_ADMIN and exact Woo refund/purchase ownership.

Allowed local states:

```text
refund.status = REQUESTED or PROVIDER_ACTION_REQUIRED
purchase.status = WITHDRAWN
```

The operator confirmation states the matching Pending Refund was actually REJECTED in Woo.

Determine held quantity:

```text
held = refund.finalCreditQuantity ?? refund.availableAmountAtRequestSnapshot
```

Atomically:

```text
refund.status = REJECTED
refund.reason = WOO_VENDOR_REFUND_REJECTED
refund.approvedByPlatformAdminId = principal.id
refund.approvedAt = now
refund.version += 1

counter.refundingQuantity -= held

if purchase.currentAmount > 0:
    purchase.status = ACTIVE
else:
    purchase.status = COMPLETED
purchase.version += 1
```

Do **not** clear `purchase.refundAttemptedAt`. Credits may become usable again, but the purchase is never eligible for another refund attempt.

### R10 — Rejection does not change provider money

Admin does not call a Woo refund API and does not calculate money. The operator has already rejected the request in Woo's vendor workflow.

### R11 — Refund-after-rejection is conflict/attention

If a signed `refunded` event later arrives for a locally REJECTED refund, do not remove allowance automatically. Surface a provider/local state conflict for support review.

### R12 — Shopify manual settlement remains Shopify-only

Preserve existing Shopify automatic/manual provider correction behavior. Crafted Woo refund IDs must not enter Shopify manual-settlement actions.

### R13 — Unmatched external Woo refund remains read-only attention

A provider `refunded` receipt with no local hold does not create a refund or mutate counters. Show bounded charge/purchase correlation evidence only.

### R14 — Audit

Prepare/reject are financial-support allowance mutations and must create bounded billing audit evidence with IDs, credit quantities and operator note; no provider secrets/customer payment data.

## Work Items

- [ ] Provider-aware queue/detail/filter and nullable Woo provenance.
- [ ] Exact Pending Refund purchase-correlation presentation.
- [ ] SUPER_ADMIN Prepare Woo refund action/CAS.
- [ ] One-attempt `refundAttemptedAt` enforcement.
- [ ] Final hold/provider-action guidance.
- [ ] SUPER_ADMIN Record Woo refund rejected action.
- [ ] Rejection hold release without clearing attempt history.
- [ ] Preserve Shopify flows/server-side guards.
- [ ] Keep unmatched provider refund read-only attention.
- [ ] Add audit/security/concurrency tests.

## Dependencies

- `ARCH-027-BACKGROUND-005`

## Enables

None.

## Acceptance Criteria

- [ ] Real Woo Pending Refund verification precedes local hold creation.
- [ ] Prepare action is SUPER_ADMIN-only and one-attempt CAS-safe.
- [ ] Existing reservations are not interrupted.
- [ ] Provider monetary amount is not calculated by Moda.
- [ ] Approval waits for signed refunded provider evidence.
- [ ] Recorded vendor rejection releases the exact allowance hold and restores ACTIVE purchase when credits remain.
- [ ] Rejection does not clear refundAttemptedAt or permit a second refund attempt.
- [ ] Refunded-after-rejection becomes attention, not double mutation.
- [ ] Shopify flows remain unchanged/provider-scoped.
- [ ] Unmatched provider refund remains non-mutating.
- [ ] `docs/architecture/_index.md` unchanged.

## Validation

Required categories include Prisma generation, typecheck/build/lint, provider/filter projection, prepare CAS/concurrency, reservation-present prepare, final-hold rejection, REQUESTED rejection, one-attempt replay denial, refunded-after-rejection conflict, Shopify regression, authorization and `git diff --check`.

## Stop Condition

Finish report -> review -> return to `moda_architect` -> STOP.

## Completion Report

### Status

Not Started

## Architect Review

### Review Status

Pending
