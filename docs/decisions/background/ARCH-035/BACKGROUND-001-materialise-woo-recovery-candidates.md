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
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The supplied 2026-10-21 task-worktree snapshot records developer execution at Attempt 1; live Git branch publication and launcher worktree synchronization are not independently established by this snapshot.

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

- [x] Implement small Woo checkout job consumer + bootstrap wiring.
- [x] Add tests proving valid checkout event is processed once per retained job and invalid event fails safely.
- [x] Regression-test existing Shopify queues and worker start-up (Shopify contract adapter and entrypoint isolation tests; real Redis integration checks Shopify queue isolation).

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

- [x] Woo checkout jobs are routed only to Woo consumer.
- [x] No CheckoutRecovery row, pending candidate, credit usage or messaging side effects in the inspected capture-only worker path.
- [x] Invalid payload fails visibly; safe structured logs include bounded identifiers but not customer payloads.
- [x] Shopify checkout worker unaffected (distinct queue/worker, focused regression tests and Redis queue isolation).

## Validation

- [x] Focused unit + real Redis/BullMQ worker integration tests. The initial 26/27 unit result was followed by a passing targeted 4/4 worker-test correction; the unchanged 23 tests previously passed.
- [x] Background lint/build (including TypeScript compilation) and focused Shopify contract-adapter/entrypoint regression tests. The full unrelated Shopify test inventory was not rerun.
- [x] Git whitespace check reported no errors; the supplied implementation contains no database migration.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Do not register a second competing Worker on the same queue as the order worker: use the two Woo-specific queue boundaries published by API-008 and API-019. Only record an operation-level observation; future Woo recovery will need separate scoped tasks for current checkout state and existing candidate integration.

## Completion Report

### Status

Implementation and validation evidence recorded for **developer Attempt 1** on 2026-10-21; ready for the developer's review handoff after final branch/worktree evidence is reconciled. The task remains formally `in_progress`, `executor: developer`, `claimed_at: 2026-10-21T12:55:34Z`, `attempt: 1` in this source snapshot. No `review`, `Accepted`, `complete`, commit or push status is inferred from a ZIP and terminal captures. The existing review record remains pending.

### Files Changed

Implementation repository: `moda-interact-background/`. Files supplied in the implementation patch plus the worker-test correction:

- `src/entrypoints/shopify-event.ts`
- `src/events/woo-checkout-capture.ts`
- `src/index.ts`
- `src/observability/queue-performance.ts`
- `src/observability/worker-metrics.ts`
- `src/workers/woo-checkout-capture.worker.ts`
- `tests/integration/woo-checkout-capture.integration.test.ts`
- `tests/unit/events/woo-checkout-capture.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`
- `tests/unit/workers/woo-checkout-capture.worker.test.ts`

No schema migration, Shared contract or `docs/decisions/**/_index.md` change was included in these patches.

### Work Completed

- Added a Woo-specific validator for API-008 `woo.activity.v1` / `checkout-updated` jobs in the `woo-checkout-capture-v1` queue. It validates the authenticated `shopId`-bound job ID, SHA-256 content digest, schema version and bounded checkout/customer fields without using the Shopify parser.
- Added a dedicated BullMQ worker that observes and acknowledges valid checkout capture events. Invalid or tampered jobs fail visibly through BullMQ, with bounded structured logging and no recovery, candidate, billing, WhatsApp or database-write execution path.
- Registered the worker with existing Background entrypoint and worker-metrics/queue-performance instrumentation; the Shopify checkout worker remains independent.
- Added parser, worker, entrypoint isolation and disposable real Redis/BullMQ integration tests covering acceptance, duplicate job identity, invalid digest retries and isolation from the Shopify checkout queue.
- Corrected one worker unit-test assertion after it incorrectly matched the word `billing` in a comment. The correction excludes comments when checking executable source and does **not** change production runtime code.

### Validation Results

Evidence: terminal captures `typescript(20261021-132639)` and `typescript(20261021-134021)`; supplied implementation patches and the current developer task-worktree ZIP.

| Command / check | Observed result |
| --- | --- |
| `npx vitest run tests/unit/events/woo-checkout-capture.test.ts tests/unit/workers/woo-checkout-capture.worker.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/events/shopify-contract-adapter.test.ts` | Initial run: **26 passed / 1 failed** of 27. Parser 3/3, entrypoint isolation 10/10 and Shopify adapter 10/10 passed; worker tests were 3/4. Only the comment-matching static assertion failed. |
| `npx vitest run tests/unit/workers/woo-checkout-capture.worker.test.ts` | **PASS 4/4** after the test-only correction (one file, 511 ms). A combined post-correction 27-test run was not supplied. |
| `npm run test:integration -- tests/integration/woo-checkout-capture.integration.test.ts` | **PASS 1/1** real Redis/BullMQ integration. Valid event completed; invalid digest failed on both configured attempts; Shopify checkout queue unaffected. |
| `npm run lint` | ESLint returned without reported errors in the terminal capture. |
| `npm run build` (`npm run prisma:generate && tsc`) | Prisma Client v6.19.3 generation shown; command returned to shell without a reported TypeScript error. |
| `git diff --check` | No whitespace errors shown in the supplied terminal output. |
| Migration / Shared contract | None introduced by this implementation. |

### Deviations

- The initial worker test erroneously matched a prohibited word in an explanatory comment. A test-only correction was applied, and the affected worker suite passed 4/4 on rerun.
- Focused Shopify checkout adapter and entrypoint regressions were run; there is no claim that every unrelated Shopify test suite was rerun.

### Assumptions

- API-008 remains the authoritative producer of the authenticated `woo.activity.v1` checkout capture job; Background validates the queued job independently.
- The supplied ZIP shows the dedicated parent task worktree's document and implementation files, but does not establish current remote branch heads or independently prove launcher-resolved implementation worktree isolation/start-of-attempt synchronization.
- Capture consumption is observation-only rather than durable archival; later recovery functionality remains separately owned.

### Unresolved Issues

- Before submitting this developer-owned task for review, reconcile launcher worktree/synchronization evidence and confirm the final implementation and parent task branches have been committed and pushed. No commit SHA or remote publication evidence is invented in this report.
- The source task previously noted that no newer full workspace containing `ARCH-040-DATABASE-006` had been supplied; no schema change is assumed or requested in this capture-only task.

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
