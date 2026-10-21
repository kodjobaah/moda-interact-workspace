---
id: ARCH-035-WOOCOMMERCE-008
architecture_id: ARCH-035
title: Capture Woo order lifecycle events
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 58
executor: developer
claimed_at: 2026-10-21T15:40:53Z
attempt: 1
depends_on: [ARCH-035-API-019, ARCH-035-WOOCOMMERCE-007]
enables: [ARCH-035-BACKGROUND-002, ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-WOOCOMMERCE-008: Capture Woo order lifecycle events

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task is materialised on its canonical parent task branch; developer Attempt 1 is claimed below.

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

In Progress — developer Attempt 1 claimed on 2026-10-21. Implementation has not yet been reviewed; validation remains pending.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The canonical parent and implementation task worktrees were verified and synchronized for this claim. Current implementation state must be established from the implementation task branch, not from the portable snapshot.

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

## Developer Execution Ownership Amendment

The developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-008` for this ready agent-owned task, explicitly taking over implementation execution. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, task scope and dependencies are unchanged.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

## Developer Claim — Attempt 1

**Claimed — 2026-10-21T15:40:53Z.** The developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-008` from the canonical `ready` state. The task transitioned to `in_progress`, Attempt 1, `executor: developer`; `assigned_agent: moda_woocommerce` remains the logical owner.

- Dependency gate: `ARCH-035-API-019` and `ARCH-035-WOOCOMMERCE-007` both resolve `complete` through the canonical launcher.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-008`, branch `task/ARCH-035-WOOCOMMERCE-008`, clean before claim and fast-forwarded from current `origin/main` to `88cc0a830518b3c07fbb143a7850ff91870412e3`. The branch's upstream was corrected from `origin/main` to `origin/task/ARCH-035-WOOCOMMERCE-008`; the task branch already matched its remote before mainline synchronization.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-008`, branch `task/ARCH-035-WOOCOMMERCE-008`, created at `1a402a30c6d5fae0c9ccba898db5c5bd0da99015` from refreshed `origin/main`. No local or remote implementation task branch existed before preparation; this canonical branch will be published with the claim.
- Both worktrees were clean and correctly mapped before the task record was updated. No implementation changes have been made by this claim.
- Required validation remains: PHPUnit and Woo HPOS integration tests, PHP lint/plugin build, a real order lifecycle fixture or documented environment limitation, existing plugin regressions, and `git diff --check`.
