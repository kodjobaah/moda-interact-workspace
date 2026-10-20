---
id: ARCH-035-API-008
architecture_id: ARCH-035
title: Accept Woo checkout snapshots into BullMQ
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: [ARCH-035-API-019, ARCH-035-WOOCOMMERCE-007, ARCH-035-BACKGROUND-001]
created: 2026-10-11
updated: 2026-10-20
---

# ARCH-035-API-008: Accept Woo checkout snapshots into BullMQ

## Developer Takeover

On 2026-10-20, the developer explicitly took ownership of Attempt 1 for implementation. The logical repository owner remains `moda_api`; this amendment changes only execution and completion authority to developer mode. The task scope, dependencies, acceptance criteria and architectural ownership are unchanged.

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Implement authenticated, bounded, idempotent checkout event acceptance by durably enqueuing validated Woo checkout snapshots.

## Context

The current Shopify webhooks enqueue to BullMQ; no WooCommerce activity receipt table is required by the agreed capture-only scope. The existing API Woo installation principal is the authentication authority. The Shopify recovery workers cannot parse Woo payloads.

## Scope

- Register `POST /v1/woocommerce/activity` through the existing API route composition, not a new HTTP server or billing endpoint.
- Validate only `CHECKOUT_UPDATED` in this task; document the complete envelope in OpenAPI with the order cases reserved for API-019.
- Use current Woo installation authentication and verify `Shop.platform === WOOCOMMERCE` before accepting events.
- Create an API-owned producer for a Woo-specific checkout BullMQ queue using the existing Redis connection/configuration; do not publish to Shopify queues.
- Provide bounded unit tests and producer/Redis integration proof.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.

## Requirements

- Accept only active, correctly authenticated installations; reject client-supplied shop identity, malformed bodies, unsupported types and oversized data.
- Canonical API schema fixes the meaning of checkoutKey, eventId, occurredAt, currency, total, optional bounded items and contact; it does not require consent flags.
- Use deterministic BullMQ job ID scoped to authenticated shop and event ID, and include a content digest to detect conflicting retained replays where possible.
- Acknowledge `202` only after BullMQ has accepted a job; Redis enqueue failure returns a retryable error and no success claim.
- Document that job-ID deduplication lasts only while the Redis job exists; do not promise a permanent replay ledger, unconditional `409`, or a durable HTTP receipt ID.
- Use the shared structured logger; do not log payloads, phone numbers, tokens or credentials.

## Work Items

- [ ] Implement route + strict schema + producer as small separate modules.
- [ ] Add OpenAPI/fixture examples and scoped duplicate/error responses.
- [ ] Test invalid and revoked installation, cross-tenant event ID, queue failure, bounded payload, replay and conflicting retained job.
- [ ] Demonstrate existing Shopify/merchant API routes unchanged.

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

None

## Enables

- `ARCH-035-API-019`
- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-BACKGROUND-001`

## Acceptance Criteria

- [ ] Real Woo installation principal determines shop; forged shop identifiers rejected.
- [ ] Valid checkout event becomes a Woo-only BullMQ job before `202` response.
- [ ] Failed enqueue does not report accepted; retry with same event ID is safe within retained job window.
- [ ] No CheckoutRecovery, provider billing or outbound message is created.
- [ ] No Shopify queue receives a Woo payload.

## Validation

- [ ] Focused API route/schema/producer unit tests.
- [ ] Redis/BullMQ integration: authenticated enqueue, retained duplicate, failed queue, cross-tenant isolation.
- [ ] API typecheck, lint, build, changed-file diff check.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Use the established hosted API composition/authenticator and existing BullMQ infrastructure. If API Redis producer capability is absent, add the smallest bounded producer wiring in the API; Gateway owns deployment wiring. Do not create a DB receipt table or publish unrecognised jobs on the Shopify queue.

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
