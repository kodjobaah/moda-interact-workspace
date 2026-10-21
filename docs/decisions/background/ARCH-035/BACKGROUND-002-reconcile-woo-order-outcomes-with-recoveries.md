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
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task definition and developer claim are materialized in the canonical task worktree. The Background implementation is published on `origin/task/ARCH-035-BACKGROUND-002` at `05c026f915b9c5e7cfdf627bf56833fe3cb1dd4f`; completion remains subject to authorized review.

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

- [x] Implement a separate Woo order consumer, strict queue-payload validator, runtime wiring and focused observability tests.
- [x] Validate repeated, out-of-order, cross-tenant and malformed events, including digest/identity checks and BullMQ retry behavior.
- [x] Verify capture-only behavior and Shopify order-worker isolation with focused source/dependency and entrypoint tests; no recovery-state mutation is introduced.

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

- [x] All three order event types are accepted as capture outcomes by the dedicated Woo worker.
- [x] Duplicate/late/order-first events are observed without initiating recovery, billing or WhatsApp business effects.
- [x] Unknown, malformed and tampered jobs fail visibly with bounded, redacted reason codes and BullMQ retry behavior.
- [x] The existing Shopify `orders.worker.ts` was not changed; worker isolation and forbidden-import checks confirm the Woo capture path cannot call its recovery-completion handler.

## Validation

- [x] Disposable Redis/BullMQ integration (2/2 passed): `ORDER_PAID` before `ORDER_PLACED`, `ORDER_CANCELLED`, shop isolation, retained-event replay, malformed/tampered jobs and configured retries.
- [x] Focused Background unit tests (20/20 passed), Shopify order regression tests (30/30 passed across contract adapter, order/recovery correlation and worker isolation), lint and TypeScript build passed.
- [x] `git diff --check` reported no errors; focused worker tests validate bounded logging and suppression of raw payloads or secrets. Committed task change list is scoped to Background.

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

Ready for developer self-review — Attempt 1 is implemented and published on `origin/task/ARCH-035-BACKGROUND-002` at `05c026f915b9c5e7cfdf627bf56833fe3cb1dd4f` (`feat(background)`). Woo order-capture, Shopify regression, lint, build and diff validation now pass. Task YAML remains `in_progress` until the authorized `/moda_developer_update ARCH-035-BACKGROUND-002` review transition; no Accepted review or completion decision is claimed.

### Files Changed

Implementation commit `05c026f915b9c5e7cfdf627bf56833fe3cb1dd4f` changes only the following Background files:

- `package.json`
- `src/entrypoints/shopify-event.ts`
- `src/events/woo-order-capture.ts`
- `src/index.ts`
- `src/observability/queue-performance.ts`
- `src/observability/worker-metrics.ts`
- `src/workers/woo-order-capture.worker.ts`
- `tests/integration/woo-order-capture.integration.test.ts`
- `tests/unit/events/woo-order-capture.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`
- `tests/unit/workers/woo-order-capture.worker.test.ts`

### Work Completed

- Added the isolated `woo-order-capture-v1` BullMQ consumer for `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED`, with strict validation of API-019 event shape, shop-scoped job identity, checkout-key consistency and content digest.
- Registered the consumer in existing production/local startup and queue-performance telemetry. The worker observes and logs bounded metadata without database writes, recovery completion, billing, messaging or Shopify order-parser calls.
- Added focused validation, worker, entrypoint-isolation and disposable Redis tests covering order-first arrival, cancellation, duplicates/replay, cross-tenant IDs, tampered digests, invalid jobs, retries and log redaction.
- Corrected an unused Zod schema declaration and narrowed a source-dependency test so the legitimate `moda-shopify-event-worker` telemetry identity is not mistaken for a forbidden Shopify event import.

### Validation Results

Supplied local execution log: `typescript(20261021-182452)`, dated 2026-10-21.

- `npm run test:arch035-woo-order-capture:unit`: **PASS**, 20/20 tests (6 event-validator, 4 worker, 10 existing/runtime-entrypoint tests).
- `npm run test:arch035-woo-order-capture:redis`: **PASS**, 2/2 disposable Redis/BullMQ tests. `digest_mismatch` and `invalid_payload` are expected tested failure outcomes, including the configured second-attempt retries.
- `npm run lint`: **PASS** with no reported errors.
- `npm run build`: **PASS**, Prisma Client v6.19.3 generated and TypeScript compiled without reported errors.
- `git diff --check`: **PASS**, command produced no whitespace errors in the recorded terminal output.
- GitHub `origin/task/ARCH-035-BACKGROUND-002` resolves to commit `05c026f915b9c5e7cfdf627bf56833fe3cb1dd4f`. Its committed diff contains only the 11 task-scoped Background files listed above, and pins the database submodule at `caee3df61dbb38c8319ebcd3cfaf68522743245e` without changing its gitlink in the task commit.
- Targeted Shopify regression: `npx vitest run tests/unit/events/shopify-contract-adapter.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/runtime/entrypoint-isolation.test.ts` — **PASS, 30/30** (10 Shopify contract mappings, 10 Shopify order/recovery correlation cases, 10 worker entrypoint isolation cases); evidence `typescript(20261021-184419)`.
- Shopify unchanged-source verification: `git diff --exit-code origin/main...HEAD -- src/workers/orders.worker.ts src/events/shopify-contract-adapter.ts src/services/checkout-recovery.service.ts` — **PASS** (no changed output).
- `git diff --check origin/main...HEAD` — **PASS**, no whitespace errors.
- Git state: `task/ARCH-035-BACKGROUND-002` at `05c026f915b9c5e7cfdf627bf56833fe3cb1dd4f`, synchronized with `origin/task/ARCH-035-BACKGROUND-002`; `git status` reports no tracked changes, with only the untracked `typescript` terminal log (excluded from the implementation commit).
- Existing `npm run test:shopify` is **not a passing test**: it exits 1 with `No test files found` because the default Vitest configuration excludes `tests/integration/**`; that legacy script targets a live Shopify product lookup rather than the Shopify order-processing contract. The targeted order-specific regression suite above is the successful validation evidence. No unrelated script was modified in BG002.
- Physical launcher/synchronization evidence for both canonical worktrees remains for the authorized developer review to verify; a passing unit test is not a substitute for that workflow evidence.

### Deviations

No changes beyond the capture-only scope. Tests and observability use the existing worker and BullMQ infrastructure; no new database table, Shared contract or provider workflow was added.

### Assumptions

- `ARCH-035-API-019` and `ARCH-035-WOOCOMMERCE-008` are complete prerequisites as recorded in the supplied task state.
- The user's validation logs and published implementation revision refer to the same developer task cycle. The latest local Git status directly verifies no tracked modifications in the dedicated Background implementation worktree; its untracked `typescript` terminal log is not task code.

### Unresolved Issues

No known Woo order-capture behavior failure remains. The Shopify order-specific regression and implementation Git state have been evidenced; the legacy `test:shopify` discovery failure is an unrelated script configuration limitation and does not demonstrate an order regression. Authorized review must still reconcile the parent/implementation worktree preparation evidence before acceptance.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable. No durable Woo order-to-recovery correlation or terminal recovery fences are implemented by this task.

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
