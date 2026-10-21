---
id: ARCH-035-API-019
architecture_id: ARCH-035
title: Accept Woo order lifecycle events
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-008]
enables: [ARCH-035-WOOCOMMERCE-008, ARCH-035-BACKGROUND-002]
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-035-API-019: Accept Woo order lifecycle events

## Developer Takeover

On 2026-10-20, the developer explicitly took ownership of Attempt 1 for implementation. The logical repository owner remains `moda_api`; this amendment changes only execution and completion authority to developer mode. The task scope, dependencies, acceptance criteria and architectural ownership are unchanged.

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task was subsequently materialised, reviewed, accepted and completed in the canonical task worktrees.

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

- [x] Implement order branches using API-008 route and strict contract in the current implementation worktree.
- [x] Add order-only producer/Redis tests including order-first, replay, malformed and unrelated shop.
- [x] Prove no live recovery operation or Shopify event publication occurs through the dedicated queue and capture-only integration coverage.

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

- [x] Validated Woo events independently enqueue to Woo order queue for all three kinds.
- [x] No duplicate queue entry for identical retained eventId; no cross-tenant collision.
- [x] Queue-down path does not acknowledge receipt.
- [x] No recovery/order-completion database writes or WhatsApp operations.

## Validation

- [x] Focused API and Redis producer integration tests (20 unit tests and 2 disposable Redis/BullMQ integration tests passed).
- [x] OpenAPI contract conformance tests for all four supported events.
- [x] Typecheck/lint/build and regression checks. `npm run typecheck` passed after generating Prisma Client v6.19.3 from the local database checkout containing `ConversationModerationAssessment`; lint, build and committed diff checks passed as recorded below.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Reuse exactly one authenticated HTTP endpoint. Do not add a second `/orders` route, SQL write or synthetic Shopify `order.completed` event.

## Completion Report

### Status

Complete — Attempt 1 accepted and explicitly completed by the developer on 2026-10-20. The earlier Changes Requested review and Attempt 0 history are preserved below.

### Files Changed

- `README.md`
- `openapi/woocommerce-activity-v1.yaml`
- `scripts/test-arch035-woo-activity-redis.mjs`
- `src/composition/woocommerce.ts`
- `src/index.ts`
- `src/woocommerce/activity/contract.ts`
- `src/woocommerce/activity/order-producer.ts`
- `src/woocommerce/activity/producer.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/activity/request.ts`
- `src/woocommerce/activity/routes.ts`
- Woo activity fixtures, unit tests and Redis integration test under `tests/`
- `tests/fixtures/woocommerce/activity/order-event.ts`
- `tests/fixtures/woocommerce/activity/order-placed.json`
- `tests/unit/woocommerce/activity/order-producer.test.ts`

### Work Completed

- Extended the API-008 activity contract to accept `ORDER_PLACED`, `ORDER_PAID`, and `ORDER_CANCELLED` with a bounded order snapshot and matching checkout correlation key.
- Added a distinct Woo order queue and deterministic shop/event-scoped replay behavior; checkout and order jobs remain separate from Shopify queues.
- Extended the existing authenticated route, OpenAPI, fixtures, unit coverage and disposable Redis integration.
- API-019 implementation is committed and published on `origin/task/ARCH-035-API-019` at `d7786dcedceab0ab3d02f5b525a2f4f2ddaad81c`.

### Validation Results

- `npm run test:arch035-woo-activity:unit`: passed, 20 tests.
- `npm run test:arch035-woo-activity:redis`: passed, 2 tests.
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: passed after the API-019 commit was synchronized with the canonical task state.
- Redis regression resolved: `typescript(20261020-122844)` records 20/20 unit tests and 2/2 disposable Redis/BullMQ tests passing; the unavailable-Redis HTTP 503 test completed in approximately 4.02 seconds rather than hanging.
- Typecheck evidence: `typescript(20261020-143025)` records local database checkout `807af33` with `ConversationModerationAssessment` at `database/prisma/schema.prisma:694`, successful Prisma Client v6.19.3 generation, and `tsc --noEmit` returning without diagnostics. That log also shows the `database` gitlink modified but unstaged; it does not prove a database gitlink commit.
- `git diff --check origin/main...HEAD`: passed.
- Implementation branch `task/ARCH-035-API-019` tracks `origin/task/ARCH-035-API-019` and is published at `d7786dcedceab0ab3d02f5b525a2f4f2ddaad81c`.
- The only remaining implementation worktree modification is the `database` submodule pointer at `69c0c8b`, unrelated to API-019 and preserved unstaged.

### Deviations

- No unresolved API-019 implementation or validation issue remains. The unrelated database gitlink modification is preserved and excluded from the task commit.

### Assumptions

The canonical parent and implementation task worktrees were used. Published branch state and current validations were verified for this completion decision.

### Unresolved Issues

None within API-019 scope.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Developer Self-Review Accepted; explicit developer completion recorded below.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. The API-019 order implementation is committed and published on its canonical task branch. The initial Changes Requested findings were resolved: task branch/upstream is correct, implementation is durable, and typecheck now passes. Focused unit/Redis integration, lint, build, typecheck and diff checks pass. The unrelated database submodule pointer was preserved and excluded.

### Reviewed Files

- `src/woocommerce/activity/contract.ts`
- `src/woocommerce/activity/order-producer.ts`
- `src/woocommerce/activity/producer.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/activity/routes.ts`
- OpenAPI and activity unit/Redis integration coverage in the implementation worktree.

### Validation Reviewed

- Woo activity/order unit tests: 20 passed.
- Disposable Redis/BullMQ integration: 2 passed.
- Lint and production build: passed.
- Typecheck: passed.
- Committed implementation diff check: passed.
- Implementation commit `d7786dcedceab0ab3d02f5b525a2f4f2ddaad81c` is present on `origin/task/ARCH-035-API-019`.

### Architecture Conformance

Conforms to API-019 capture-only scope: the existing authenticated route accepts all three bounded order event types, derives shop identity from the Woo installation, routes to a dedicated Woo order queue, preserves event/correlation identity, accepts order-before-checkout independently, and does not write recovery state or call provider flows. Checkout events continue using their separate queue; no Shopify queue or permanent replay ledger was introduced.

### Follow-up

`ARCH-035-WOOCOMMERCE-008` remains pending because it also depends on `ARCH-035-WOOCOMMERCE-007`, which is ready but incomplete. `ARCH-035-BACKGROUND-002` remains pending because it depends on WOOCOMMERCE-008. No downstream task was promoted prematurely.

### Developer Self-Review - Changes Requested (Historical)

1. Synchronize the canonical implementation worktree to `task/ARCH-035-API-019` and configure its upstream as `origin/task/ARCH-035-API-019`; do not push task code to `main`.
2. Preserve the untracked `typescript` path and commit/push only verified API-019-owned implementation files. Confirm the task branch remote contains the implementation commit(s).
3. Resolve the typecheck failure in the generated Prisma client contract (`conversationModerationAssessment` missing from `PrismaClient`) or record verified baseline evidence showing why this is unrelated and obtain the authorized validation decision. Do not edit unrelated tests/schema merely to suppress the failure.
4. Rerun and record focused unit, Redis/BullMQ integration, OpenAPI, typecheck, lint, build and `git diff --check` after branch synchronization/commit.
5. Update the Completion Report from the committed diff, then request review again. Do not complete the task until a durable passing Accepted review exists.

All five corrections were verified as resolved before the Accepted review below: the implementation commit is published on the canonical task branch, typecheck passes, and the required focused validations are recorded.

### Developer Self-Review Accepted (Final)

Attempt 1 passes review. All API-019 Work Items and Acceptance Criteria are complete; the implementation branch is committed and pushed; the previous branch tracking and typecheck blockers are resolved; and task-focused validation passes. The unrelated database gitlink remains untouched.

### Developer Completion Decision

On 2026-10-20, the developer explicitly completed ARCH-035-API-019 after the durable Attempt 1 Accepted review. Status is `complete`; executor and claimed_at are null; attempt remains 1. No merge to `main` was performed.
