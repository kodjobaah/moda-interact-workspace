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
status: ready
priority: 62
executor: null
claimed_at: null
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

Developer Attempt 1 was reviewed on 2026-10-21. Focused implementation tests, integration, lint and build pass, but review is **Changes Requested** because the implementation worktree is dirty, its local task branch tracks `origin/main` instead of a published task branch, no remote `origin/task/ARCH-035-BACKGROUND-001` exists, and there are unexplained out-of-scope dirty paths. The task transitions to `ready`, clears the active claim, and preserves `attempt: 1`; a subsequent valid developer claim will increment to Attempt 2. No implementation change was committed or pushed during this review.

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

Evidence: current canonical implementation worktree at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-BACKGROUND-001`, rerun on 2026-10-21 during developer self-review. The implementation is still uncommitted, so validation confirms current worktree behavior only and is not a published task-branch result.

| Command / check | Observed result |
| --- | --- |
| `npx vitest run tests/unit/events/woo-checkout-capture.test.ts tests/unit/workers/woo-checkout-capture.worker.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/events/shopify-contract-adapter.test.ts` | **PASS 27/27** on the current dirty worktree (2026-10-21). |
| `npm run test:integration -- tests/integration/woo-checkout-capture.integration.test.ts` | **PASS 1/1** real Redis/BullMQ integration. Valid event completed; invalid digest failed on both configured attempts; Shopify checkout queue unaffected. |
| `npm run lint` | **PASS**, ESLint reported no errors. |
| `npm run build` (`npm run prisma:generate && tsc`) | **PASS**, Prisma Client v6.19.3 generated and TypeScript compilation completed without errors. |
| `git diff --check` | **PASS** for the current dirty worktree. |
| Canonical task branch/publication check | **BLOCKED**: local `task/ARCH-035-BACKGROUND-001` points to the same commit as `origin/main` and is configured to track `origin/main`; `origin/task/ARCH-035-BACKGROUND-001` does not exist. The source/task changes are uncommitted. |
| Migration / Shared contract | None introduced by this implementation. |

### Deviations

- The initial worker test erroneously matched a prohibited word in an explanatory comment. A test-only correction was applied, and the affected worker suite passed 4/4 on rerun.
- Focused Shopify checkout adapter and entrypoint regressions were run; there is no claim that every unrelated Shopify test suite was rerun.

### Assumptions

- API-008 remains the authoritative producer of the authenticated `woo.activity.v1` checkout capture job; Background validates the queued job independently.
- The actual canonical implementation directory exists, but its task branch topology is not valid: it tracks `origin/main`, is at the same SHA as `origin/main`, and no remote task branch exists. Do not infer synchronization/publication from the local branch name.
- Capture consumption is observation-only rather than durable archival; later recovery functionality remains separately owned.

### Unresolved Issues

- Reconcile the canonical implementation branch topology and safely publish only the intended Background task implementation. Do not commit the current worktree wholesale: the `database` gitlink points from `caee3df` to `807af33`, and that database submodule is on `main` with ARCH-040 operational-diagnostics changes; this is outside this task's scope. The untracked root `typescript` file is also unexplained and must be identified. Preserve both until their owner/source is established; do not discard or stage them as part of BACKGROUND-001.
- The implementation currently has task source/test files uncommitted and no `origin/task/ARCH-035-BACKGROUND-001` branch. Establish the correct dedicated task branch/upstream without losing the current task changes, then commit and push only the intended Background files and verify clean canonical worktree state.
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

Pending architect review. Developer Self-Review — Changes Requested (Attempt 1) is recorded below; no architect acceptance is implied.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

None.

### Validation Reviewed

Not reviewed by the architect. Focused developer self-review validation results and publication limitations are recorded above.

### Architecture Conformance

Not evaluated by the architect. The developer self-review found the implementation scope capture-only, but cannot accept it while the implementation is unpublished, the task worktree tracks `origin/main`, and unrelated/unexplained dirty paths prevent safe publication.

### Follow-up

Resolve the implementation branch/upstream and dirty-path ownership, publish only intended task changes, then claim Attempt 2 through `/moda_developer_create ARCH-035-BACKGROUND-001` and rerun focused validation before the next review.

## Developer Self-Review - Changes Requested

**Reviewed 2026-10-21T14:17:54Z, Attempt 1.** The task's focused behavior checks pass on the current implementation worktree: unit/regression suite 27/27, real Redis/BullMQ integration 1/1, ESLint, TypeScript build, and `git diff --check`. The task's three Work Items and four Acceptance Criteria are implemented in the current source tree. However, the implementation is not durably attributable to the task branch: the canonical worktree's `task/ARCH-035-BACKGROUND-001` is configured to track `origin/main`, has the same commit as `origin/main` (`c5e6da4`), and there is no `origin/task/ARCH-035-BACKGROUND-001`; the implementation and test files remain uncommitted. The worktree also contains a database gitlink change (`caee3df` to `807af33`) whose submodule includes unrelated ARCH-040 diagnostics changes, plus an unexplained untracked root `typescript` file. These were not modified or discarded.

Required, testable corrections before resubmitting:

1. Restore valid isolation/publication for the canonical implementation worktree: ensure `task/ARCH-035-BACKGROUND-001` is based on the appropriate task/mainline history and tracks `origin/task/ARCH-035-BACKGROUND-001`; preserve the current task changes while doing so. Do not switch/reset a shared checkout or force-push.
2. Identify and preserve the owner/source of the changed `database` gitlink and untracked `typescript` file. Exclude both from BACKGROUND-001 unless an architect-approved scope change establishes they belong here; do not delete or revert them as part of the correction.
3. Commit and push only the intended BACKGROUND-001 implementation and test files on the correct implementation task branch, then verify both canonical worktrees are clean and synchronized and update the report with the resulting commit evidence.
4. After branch/scope correction, rerun the focused unit/regression and real Redis integration tests, lint, build, and whitespace check against the committed task branch.

Transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1` (unchanged). The next developer claim may begin Attempt 2; no claim is created by this review.
