---
id: ARCH-027-WOOCOMMERCE-003
architecture_id: ARCH-027
title: Add WooCommerce purchase history and provider refund navigation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-WOOCOMMERCE-002
  - ARCH-027-API-006
enables: []
created: 2026-10-03
updated: 2026-10-05
---

# Add WooCommerce purchase history and provider refund navigation

## Objective

Complete the Woo purchased-credit merchant experience with history/status plus the correct provider-owned refund entry point.

The plugin does **not** create/cancel/reactivate a refund.

```text
Purchased credits
    -> Request refund on WooCommerce.com
    -> external https://woocommerce.com/my-account/orders/
```

Following that link performs no local billing mutation.

## Scope

Inside the existing Billing surface add:

- Purchased credits view;
- ACTIVE/WITHDRAWN/COMPLETED/REFUNDED/ALL filters;
- 5/10/20 pagination;
- merchant-safe purchase/refund status;
- `Request refund on WooCommerce.com` navigation when API-006 says eligible;
- copy explaining that the merchant must submit the request on WooCommerce.com and Moda/vendor then reviews it.

## Out of Scope

- Local refund POST.
- Batch refund selection.
- Refund confirmation dialog in Moda.
- Reactivate/cancel refund.
- Provider monetary calculation.
- Admin vendor approval/rejection.
- Provider IDs/raw evidence.

## Requirements

### R1 — Existing Billing internal view

Add/retain `Purchased credits` inside Billing; no new top-level WordPress page.

### R2 — Exact local history proxy

Expose GET only:

```text
GET /wp-json/moda-interact/v1/billing/recovery-credit-purchases
```

with exact `filter`, `page`, `pageSize` forwarding to API-006.

### R3 — Filters/pagination

Exact filters `ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL`; page sizes 5/10/20; defaults ACTIVE/1/5.

### R4 — Purchase cards

Render merchant-safe status, bundle/plan label, dates, credits granted/current/reserved/available/held, provider purchase amount when returned, latest/completed refund summaries and `refundAttempted`.

### R5 — External refund navigation

When:

```text
refundEligible = true
refundRequest.method = WOOCOMMERCE_ORDERS
```

show:

```text
Request refund on WooCommerce.com
```

using the exact API-provided HTTPS URL.

Open/navigate to the provider site through the accepted safe external-navigation helper.

The click MUST NOT call a Moda mutation endpoint and MUST NOT optimistically change purchase/refund state.

### R6 — Merchant guidance

Use copy equivalent to:

> Open your WooCommerce.com orders, find the Moda Interact purchase, and use Woo's refund-request option for that order. Moda will update the purchase after the provider/vendor refund workflow progresses.

Avoid depending on brittle provider UI details such as a specific icon/menu label.

### R7 — One attempt presentation

When:

```text
refundAttempted = true
```

no Request Refund action is shown, including after `latestRefund.status=REJECTED` and allowance has been restored.

Bounded text:

```text
This purchase has already had a refund request.
```

### R8 — No merchant undo

There is no:

```text
Reactivate credits
Cancel refund
refund batch submit
```

The vendor decision occurs outside the plugin.

### R9 — Status presentation

Map:

```text
ACTIVE                  -> Active
WITHDRAWN               -> Refund under review / credits held
COMPLETED               -> Used
REFUNDED                -> Refunded
latest refund REQUESTED -> Refund request being prepared
PROVIDER_ACTION_REQUIRED-> Awaiting vendor decision in Woo
REJECTED                -> Refund rejected; remaining credits restored when applicable
COMPLETED               -> Refund completed
NEEDS_ATTENTION         -> Refund needs review
```

### R10 — Connection/stale-response safety

Reuse WOO-001/002 connection generation, abort and stale-response protections. Clear purchase data after disconnect.

### R11 — No browser persistence/internal identifiers

No localStorage/sessionStorage/WordPress options for purchase/refund state; no provider contract/transaction/request-key leakage.

### R12 — i18n/accessibility

Use `@wordpress/i18n`, text domain `moda-interact`, accessible filter/status/external-link semantics.

## Work Items

- [ ] Add Purchased credits internal view/history proxy.
- [ ] Add filters/pagination/cards/statuses.
- [ ] Add external WooCommerce Orders refund link from API contract.
- [ ] Remove/avoid local refund/batch/reactivation controls.
- [ ] Add one-attempt/rejected-history presentation.
- [ ] Add connection/stale-response/i18n/accessibility tests.

## Dependencies

- `ARCH-027-WOOCOMMERCE-002`
- `ARCH-027-API-006`

## Acceptance Criteria

- [ ] Refund link is provider navigation only and creates no Moda hold.
- [ ] No merchant refund/reactivation POST route exists.
- [ ] Prior refund attempt permanently removes the Request refund action for that purchase.
- [ ] Rejected refund may show restored credits but no second refund action.
- [ ] History/filter/pagination/provider-safe presentation works.
- [ ] No internal/provider identifiers leak.
- [ ] `docs/architecture/_index.md` unchanged.

## Validation

Required categories: PHP history proxy permissions/query tests, React filter/pagination/status tests, refund external-link/no-mutation test, prior-attempt no-link test, disconnect/stale-response, build/lint/PHP tests/plugin ZIP as repository policy requires, and `git diff --check`.

## Stop Condition

Complete report -> review -> return to `moda_architect` -> STOP.

## Completion Report

### Status

Not Started

## Architect Review

### Review Status

Pending
