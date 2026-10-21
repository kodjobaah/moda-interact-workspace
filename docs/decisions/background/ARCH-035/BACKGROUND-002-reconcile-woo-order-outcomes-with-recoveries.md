---
id: ARCH-035-BACKGROUND-002
architecture_id: ARCH-035
title: Consume Woo order capture jobs safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 64
executor: developer
claimed_at: 2026-10-21T18:03:26Z
attempt: 1
depends_on: [ARCH-035-API-019, ARCH-035-WOOCOMMERCE-008]
enables: [ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-BACKGROUND-002: Consume Woo order capture jobs safely

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task definition is materialized on its canonical parent task branch; the implementation worktree remains deferred until execution preparation.

## Objective

Introduce a Woo-specific order-event consumer for placed, paid and cancelled events, without changing recovery state.

## Context

The Shopify order worker parses a Shopify contract and invokes recovery completion. This Woo-specific capture consumer must not map Woo order events to the Shopify completed-order handler. Processing only observes validated queue jobs.

## Scope

- Add a narrow Woo order consumer for API-019 queue using existing worker bootstrap and observability.
- Validate schemaVersion, authenticated shop identity, checkoutKey, orderId, event ID and event kind in queued jobs.
- Preserve placed/paid/cancelled distinctions and observe order-first and duplicated delivery without asserting durable ordering.
- Use bounded normal BullMQ retry/failure behaviour.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- Calling `CheckoutRecoveryService.handleOrderCompletedContract`, terminal recovery guards, candidate cancellation, revenue attribution, outreach suppression or reactivation.

## Requirements

- Never fabricate an earlier checkout or mark order paid on ORDER_PLACED.
- No durable terminal fence is promised; final recovery integration requires a separately agreed order guard strategy.
- Order payloads must not go to the Shopify order worker.

## Work Items

- [ ] Implement order consumer and focused validation/observability tests.
- [ ] Check repeated, out-of-order, cross-tenant and bad event kinds.
- [ ] Prove no recovery/business-state changes and Shopify order worker parity.

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
- `ARCH-035-WOOCOMMERCE-008` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] All three events are processed as capture outcomes by Woo order worker.
- [ ] Duplicate/late events do not initiate recovery business effects.
- [ ] Unknown/invalid jobs fail visibly.
- [ ] Existing Shopify order completion behaviour is unchanged.

## Validation

- [ ] Real Redis/BullMQ integration: place/paid/cancelled, retries and invalid jobs.
- [ ] Focused background unit + Shopify order regression tests; typecheck/lint/build.
- [ ] Diff check and log-safety checks.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Developer Execution Ownership Amendment

The developer invoked `/moda_developer_create ARCH-035-BACKGROUND-002` for this ready agent-owned task, explicitly taking over implementation execution. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, task scope and dependencies are unchanged.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

## Implementation Notes

Use the existing BullMQ setup; do not introduce SQL tombstones, claim loops, offer logic or a fresh status table. Do not equate job completion with durable order correlation history.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T18:03:26Z. Attempt 0 review history is preserved below.

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
