---
id: ARCH-027-API-006
architecture_id: ARCH-027
title: Expose WooCommerce purchase history and refund navigation
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-027-WOOCOMMERCE-003
created: 2026-10-03
updated: 2026-10-05
---

# Expose WooCommerce purchase history and refund navigation

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Expose the merchant-safe Woo purchased-credit history needed by the Woo Billing UI and provide the **external WooCommerce.com refund-request navigation**.

This task is read-only for refunds.

It MUST NOT create a `RecoveryCreditRefund`, withdraw a purchase, hold credits, call Woo, or reactivate/cancel a refund.

Woo's v1 refund initiation is:

```text
Moda purchase history
    -> link to https://woocommerce.com/my-account/orders/
    -> merchant submits real refund request on WooCommerce.com
    -> Moda/vendor receives it in Woo Pending Refunds
    -> ADMIN-001 prepares the local allowance hold
```

## Scope

Add exactly:

```text
GET /v1/billing/recovery-credit-purchases
```

using the accepted Woo installation authentication boundary.

The response owns:

- ACTIVE/WITHDRAWN/COMPLETED/REFUNDED history;
- exact 5/10/20 page sizes and bounded pagination;
- provider-safe purchase/refund summaries;
- purchase-local refund eligibility presentation;
- the WooCommerce Orders refund-navigation URL;
- one-attempt history (`refundAttemptedAt`).

## Out of Scope

- `POST /v1/billing/recovery-credit-refunds` for Woo merchants.
- Any refund-reactivation endpoint.
- Batch refund commands.
- Monetary refund calculation.
- Creating the Woo provider refund request.
- Admin vendor approval/rejection.
- Provider webhook reconciliation.
- Shopify merchant refund routes.
- `docs/architecture/_index.md`.

## Requirements

### R1 — Exact endpoint/query contract

Accept only:

```text
GET /v1/billing/recovery-credit-purchases
  ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
  &page=<positive integer>
  &pageSize=5|10|20
```

Defaults:

```text
filter=ACTIVE
page=1
pageSize=5
```

Reject unknown query parameters.

### R2 — Authentication / tenant isolation

Authenticate with the accepted ARCH-026 Woo installation authenticator and derive `shopId` only from that principal.

Query only:

```text
purchase.shopId = principal.shopId
purchase.provider = WOOCOMMERCE
```

### R3 — Strict versioned response

Return `schemaVersion=1`, bounded pagination metadata and merchant-safe purchase rows.

Do not expose provider contract/transaction IDs, request keys, raw price snapshots, Shopify handles or internal billing-period IDs.

### R4 — Merchant-safe purchase row

Each row may expose:

```text
id
status
createdAt
activatedAt
bundleLabel | null
planName
creditsGranted
currentAmount
reservedAmount
availableAmount
heldForRefundAmount
refundEligible
refundUnavailableReason
refundAttempted
latestRefund | null
completedRefund | null
originalProviderPurchase amount/currency | null
```

`refundAttempted = purchase.refundAttemptedAt != null`.

### R5 — Woo refund request navigation is provider-owned

Return one bounded top-level contract:

```json
{
  "method": "WOOCOMMERCE_ORDERS",
  "url": "https://woocommerce.com/my-account/orders/"
}
```

The URL is navigation only. API-006 performs no mutation when the merchant follows it.

### R6 — Refund eligibility is local purchase guidance only

A Woo purchase may be presented as eligible to request a provider refund only when:

```text
status = ACTIVE
availableAmount > 0
valid Woo acquisition/provider evidence exists
refundAttemptedAt = NULL
```

Refund eligibility does not require the acquisition BillingPeriod/current recurring subscription to remain current.

If a prior refund attempt exists, return:

```text
refundEligible = false
refundUnavailableReason = REFUND_ALREADY_ATTEMPTED
```

even when the prior refund was REJECTED/CANCELLED and allowance was restored.

Other bounded reasons include:

```text
NO_AVAILABLE_CREDITS
PROVIDER_EVIDENCE_UNAVAILABLE
REFUND_IN_PROGRESS
```

### R7 — Requesting a refund is not a Moda API mutation

There is no Woo merchant refund POST in this task.

The merchant is told to submit the provider request in WooCommerce.com Orders. A local hold begins only after the vendor/operator verifies the real Pending Refund and ADMIN-001 prepares it.

### R8 — No merchant reactivation

Do not expose:

```text
reactivationAvailable
providerActionStarted as a merchant action gate
POST .../reactivate
```

The merchant cannot undo a refund attempt in Moda.

A vendor rejection may later restore held allowance through ADMIN-001, while the purchase remains permanently ineligible for another refund attempt.

### R9 — Refund summaries are status/history only

Return bounded refund status/reason/final credit quantity/provider-reported money when appropriate, but never calculate a Moda expected monetary refund.

### R10 — Pagination/order

Order by:

```text
createdAt DESC, id DESC
```

Clamp an over-high requested page to the last available page; empty result uses page 1.

## Work Items

- [ ] Add authenticated provider-scoped history query.
- [ ] Add strict filters/pagination/versioned response validation.
- [ ] Add merchant-safe refund history/status projection.
- [ ] Add `refundAttempted` / `REFUND_ALREADY_ATTEMPTED` semantics.
- [ ] Add WooCommerce Orders navigation contract.
- [ ] Remove/avoid Woo merchant refund and reactivation mutations.
- [ ] Update OpenAPI.
- [ ] Add focused tenant/provider/history/refund-navigation tests.

## Dependencies

- `ARCH-027-BACKGROUND-005`

BACKGROUND-005 fixes the authoritative Woo refund statuses and provider-refund completion semantics consumed by the history projection.

## Enables

- `ARCH-027-WOOCOMMERCE-003`

## Acceptance Criteria

- [ ] Exactly one GET purchase-history endpoint is owned by API-006.
- [ ] Woo merchant refund initiation performs no Moda mutation.
- [ ] Response contains the WooCommerce Orders URL.
- [ ] History is shop+WOOCOMMERCE scoped.
- [ ] A previous refund attempt permanently disables another refund request for the purchase.
- [ ] Rejected refund history may coexist with restored ACTIVE allowance but remains `refundEligible=false`.
- [ ] No merchant reactivation endpoint/field exists.
- [ ] Historical Woo purchase can remain refund-eligible after recurring plan/period changes when it has no prior attempt.
- [ ] No internal/provider/Shopify identifiers leak.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Required categories:

- [ ] OpenAPI validation;
- [ ] authentication/tenant isolation;
- [ ] filter/page-size/page-clamp tests;
- [ ] provider=WOOCOMMERCE exclusion/inclusion tests;
- [ ] refundAttempted/REFUND_ALREADY_ATTEMPTED tests;
- [ ] Orders URL response test;
- [ ] proof no refund/reactivation mutation routes were added;
- [ ] typecheck/build/lint/test according to repository scripts;
- [ ] `git diff --check`.

## Stop Condition

Complete the report, set `review`, return to `moda_architect`, STOP.

## Completion Report

### Status

Not Started

## Architect Review

### Review Status

Pending
