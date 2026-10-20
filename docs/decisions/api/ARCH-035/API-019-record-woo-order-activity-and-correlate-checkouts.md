---
id: ARCH-035-API-019
architecture_id: ARCH-035
title: Accept Woo order lifecycle events
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-008]
enables: [ARCH-035-WOOCOMMERCE-008, ARCH-035-BACKGROUND-002]
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-035-API-019: Accept Woo order lifecycle events

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Extend the accepted Woo activity API producer to validate and enqueue authoritative Woo order lifecycle events.

## Context

API-008 owns route, authentication and checkout envelope. API-019 extends only the event type cases and a dedicated Woo order-event producer; order semantics must not be mistaken for payment status or recovery-state transitions.

## Scope

- Extend `POST /v1/woocommerce/activity` to accept `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` using the same installation auth and validated envelope.
- Route order events to a separate Woo-specific order queue using existing BullMQ/Redis integration.
- Retain eventId/orderId/checkoutKey/occurredAt, and order state in bounded payload; reject uncorrelated or foreign-shop claims.
- Extend OpenAPI and producer tests without recreating API-008 route/authentication modules.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- Durable order tombstones or permanent checkout correlation ledger.
- Mapping Woo cancellation to automatic reopening of a recovery.

## Requirements

- An order event without a meaningful shop-scoped checkoutKey is rejected or explicitly handled under a documented non-correlated outcome; do not match customers by phone/email.
- Different Woo order events with the same checkoutKey remain distinct; retries of one event keep its eventId.
- Return success only after order-queue acceptance; queue failures are retryable.
- Order-before-checkout is accepted independently; no permanent ordering or terminal fencing claimed without durable state.

## Work Items

- [ ] Implement order branches using API-008 route and strict contract.
- [ ] Add order-only producer/Redis tests including order-first, replay, malformed and unrelated shop.
- [ ] Prove no live recovery operation or Shopify event publication occurs.

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

- `ARCH-035-API-008` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-BACKGROUND-002`

## Acceptance Criteria

- [ ] Validated Woo events independently enqueue to Woo order queue for all three kinds.
- [ ] No duplicate queue entry for identical retained eventId; no cross-tenant collision.
- [ ] Queue-down path does not acknowledge receipt.
- [ ] No recovery/order-completion database writes or WhatsApp operations.

## Validation

- [ ] Focused API and Redis producer integration tests.
- [ ] OpenAPI contract conformance tests for all four supported events.
- [ ] Typecheck/lint/build and regression checks.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Reuse exactly one authenticated HTTP endpoint. Do not add a second `/orders` route, SQL write or synthetic Shopify `order.completed` event.

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
