---
id: ARCH-035-SYSTEM-TEST-002
architecture_id: ARCH-035
title: Certify Woo checkout and order capture only
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-008, ARCH-035-API-019, ARCH-035-WOOCOMMERCE-007, ARCH-035-WOOCOMMERCE-008, ARCH-035-BACKGROUND-001, ARCH-035-BACKGROUND-002]
enables: []
created: 2026-10-11
updated: 2026-10-20
---

# ARCH-035-SYSTEM-TEST-002: Certify Woo checkout and order capture only

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Prove authenticated Woo checkout and order events travel through the plugin, hosted API and Woo-specific Background consumers without invoking recoveries.

## Context

The former SYSTEM-TEST-002 asserted recovery maturation, consent and WhatsApp outcomes. Those are out of scope for capture-only; the new test must prove the accepted queue boundary with real components.

## Scope

- Exercise guest/authenticated Classic checkout, Checkout Blocks and HPOS order lifecycle using reproducible WordPress/Woo fixtures.
- Run real plugin-to-API authenticated ingress, Redis/BullMQ producer and both Woo Background consumers.
- Exercise deterministic event ID/retries, transient API errors, duplicate submissions and order-first/checkout-first.
- Prove Shopify checkout and order existing scenarios still work.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- CheckoutRecovery/WhatsApp/usage/recovered revenue certification, allowlist/consent validation, recovery offer or UI analytics gating.

## Requirements

- Do not claim durable PostgreSQL receipts, replay after job retention expires or permanent order guards.
- Require evidence of queue acceptance and consumer execution (or retained failure) for each scenario.
- Assert capture sends no message, creates no recovery record or charges usage.
- Keep system-test terminal; no implementation task depends on this test.

## Work Items

- [ ] Build isolated WordPress/API/Redis/Background scenario orchestration and evidence assertions.
- [ ] Run source-level isolation and real broker tests, not just mocked hooks.
- [ ] Document unsupported Classic/Blocks/HPOS environments truthfully.

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
- `ARCH-035-API-019` — must be Complete and accepted before claiming.
- `ARCH-035-WOOCOMMERCE-007` — must be Complete and accepted before claiming.
- `ARCH-035-WOOCOMMERCE-008` — must be Complete and accepted before claiming.
- `ARCH-035-BACKGROUND-001` — must be Complete and accepted before claiming.
- `ARCH-035-BACKGROUND-002` — must be Complete and accepted before claiming.

## Enables

None

## Acceptance Criteria

- [ ] Every source scenario reaches authorised API, Woo-specific queue and correct consumer.
- [ ] Outage does not block checkout/order and retry resumes when API available.
- [ ] Cross-shop event isolation and no Shopify recovery regression.
- [ ] Zero capture-induced CheckoutRecovery, WhatsApp, billing or AI side effects.
- [ ] Evidence distinguishes successful queue acceptance from permanent archival.

## Validation

- [ ] Integrated disposable WordPress/Woo + API + Redis + Background tests, with live fixtures where possible.
- [ ] CI/manual environment prerequisites recorded and unsupported tests marked blocked.
- [ ] Regression suite + evidence artefacts and diff check.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Do not require obsolete WOO-009/010 analytics tasks or BG recovery materialisation as prerequisites for capture certification. Capture-only capability must be validated before its architecture is marked implemented.

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
