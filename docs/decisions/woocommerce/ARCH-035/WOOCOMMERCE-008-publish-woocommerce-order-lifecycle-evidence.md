---
id: ARCH-035-WOOCOMMERCE-008
architecture_id: ARCH-035
title: Capture Woo order lifecycle events
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 58
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-019, ARCH-035-WOOCOMMERCE-007]
enables: [ARCH-035-BACKGROUND-002, ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-20
---

# ARCH-035-WOOCOMMERCE-008: Capture Woo order lifecycle events

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Emit authoritative placed, paid and cancelled Woo order events using the already accepted checkout identity and plugin publisher.

## Context

This task extends WOOCOMMERCE-007 without building a separate HTTP client or queue. Woo orders need source-of-truth hook observation and HPOS-compatible checkout-key correlation.

## Scope

- Observe authoritative Woo order placement, payment completion and cancellation using supported WooCommerce APIs and hooks.
- Retrieve the checkoutKey recorded by WOOCOMMERCE-007 from order metadata; use existing installation PHP API client and retry facility.
- Generate distinct stable event IDs per order event occurrence, and preserve them on delivery retries.
- Use the shared `/v1/woocommerce/activity` route with API-019 order event schema.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- Recovery completion, suppression or reopening, revenue attribution and refund reconciliation.

## Requirements

- Do not infer payment success from order creation or status strings alone; source events must reflect Woo evidence.
- Order ID and checkoutKey must stay tenant-scoped; never correlate by phone/address.
- Duplicate Woo hook invocation cannot create extra event identities for the same logical transition when source identity can be determined.
- API/network failure never breaks an order transition.

## Work Items

- [ ] Implement narrow Woo order hook adapter, reusing existing publisher.
- [ ] Add order fixture tests for HPOS, retry, placed/paid/cancelled and Woo status repetitions.
- [ ] Validate order-first and checkout-first deliveries against API fixtures.

## Interfaces / Contracts

**API-owned `woo.activity.v1` contract** (published as strict OpenAPI + integration fixtures, not a new Shared package in this bounded scope):

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "stable-opaque-event-id",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "stable-shop-scoped-key",
  "occurredAt": "2026-10-20T12:00:00.000Z",
  "checkout": { "currency": "GBP", "total": "29.99", "items": [] }
}
```

`eventType` is one of `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`. For orders, use an `order` object with `orderId`, status and same `checkoutKey`; `checkout` is absent. A Woo producer sends no shop ID: API resolves Shop from installation credentials. Bounded customer/contact fields and line-item fields must be explicitly defined in the authoritative API schema; omit unavailable fields rather than fabricating them. Correlation key is `(authenticated shopId, checkoutKey)`. Stable `eventId` is retained on retries of the **same emitted event**; later genuine updates use a new `eventId`.

The hosted API owns `POST /v1/woocommerce/activity`. Checkouts are implemented by API-008; order event types are enabled by API-019 on the same route. Queue payloads retain `schemaVersion`, authenticated `shopId`, event identity, kind, checkout key and bounded validated snapshot. Background must validate the queued payload again and must **not** call the Shopify event parser. These contracts are specific to this API/Background integration; if a published cross-service primitive becomes necessary, stop and return the new ownership requirement to the architect rather than implement a competing Shared module.

## Dependencies

- `ARCH-035-API-019` — must be Complete and accepted before claiming.
- `ARCH-035-WOOCOMMERCE-007` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-BACKGROUND-002`
- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Placed, paid and cancelled order events carry matching checkoutKey and canonical orderId.
- [ ] Repeated hook/retry does not create a new event for same transition.
- [ ] Missing correlation is visible and not guessed from personal data.
- [ ] Existing Woo checkout/order processing remains operational during Moda outage.

## Validation

- [ ] PHPUnit and Woo HPOS integration tests; PHP lint/plugin build.
- [ ] Real order lifecycle fixture or documented environment limitation.
- [ ] Existing plugin regression suite and diff check.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

No new WordPress tables or custom recovery scheduler. Match hooks to actual Woo integration; avoid incorrect assumptions about Blocks event timing.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Developer must materialise and claim the task in its canonical isolated parent and implementation worktrees. Snapshot is not evidence of current remote task state.

### Unresolved Issues

No newer full workspace containing `ARCH-040-DATABASE-006` was provided with this request. Do not silently introduce schema changes or infer its implementation.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Pending.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.
