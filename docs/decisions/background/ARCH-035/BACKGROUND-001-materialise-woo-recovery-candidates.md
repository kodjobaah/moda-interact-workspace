---
id: ARCH-035-BACKGROUND-001
architecture_id: ARCH-035
title: Consume Woo checkout capture jobs safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 62
executor: developer
claimed_at: 2026-10-21T12:55:34Z
attempt: 1
depends_on: [ARCH-035-API-008, ARCH-035-WOOCOMMERCE-007]
enables: [ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-BACKGROUND-001: Consume Woo checkout capture jobs safely

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Introduce a Woo-specific checkout job consumer that validates enqueued checkout snapshots without triggering recovery workflows.

## Context

The current checkout.worker.ts consumes only published Shopify contracts and immediately invokes CheckoutRecoveryService. Adding Woo events to Shopify queues would be unsafe. This task is a capture-only queue consumer, not recovery materialisation.

## Scope

- Add a narrow Woo checkout worker/handler using existing Redis/BullMQ connections and worker lifecycle.
- Consume only API-008 Woo checkout queue and schemaVersion/kind; validate shop identity and bounded snapshots at the consumer boundary.
- Emit structured, non-sensitive accepted/ignored/failed processing outcomes and existing instrumentation, and permit normal retry of transient faults.
- Wire the worker to existing Background bootstrap without changing Shopify checkout worker behaviour.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- CheckoutRecoveryService calls, pending recovery candidates, GraphQL checkout lookup, recovery materialisation, billing, WhatsApp, or permanent event history.

## Requirements

- Job validation must be independent from Shopify parser and reject malformed/unknown schema versions.
- No DB writes merely to acknowledge capture; after successful consumption the job is not a future replay source.
- Do not import Shopify checkout adapters or call recovery pipeline as a side effect.
- A retryable infrastructure failure must fail the job rather than be swallowed; operator failure visibility through existing BullMQ facilities.

## Work Items

- [ ] Implement small Woo checkout job consumer + bootstrap wiring.
- [ ] Add tests proving valid checkout event is processed once per retained job and invalid event fails safely.
- [ ] Regression-test existing Shopify queues and worker start-up.

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
- `ARCH-035-WOOCOMMERCE-007` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Woo checkout jobs are routed only to Woo consumer.
- [ ] No CheckoutRecovery row, pending candidate, credit usage or messaging side effects.
- [ ] Invalid payload fails visibly; safe structured logs include IDs but no PII.
- [ ] Shopify checkout worker unaffected.

## Validation

- [ ] Focused unit + real Redis/BullMQ worker integration tests.
- [ ] Run background typecheck, lint/build and checkout Shopify regression suite.
- [ ] Diff check; no database migration.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Do not register a second competing Worker on the same queue as the order worker: use the two Woo-specific queue boundaries published by API-008 and API-019. Only record an operation-level observation; future Woo recovery will need separate scoped tasks for current checkout state and existing candidate integration.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T12:55:34Z. Attempt 0 review history is preserved below.

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

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_background`; execution ownership is changed from the
automatic agent path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

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
