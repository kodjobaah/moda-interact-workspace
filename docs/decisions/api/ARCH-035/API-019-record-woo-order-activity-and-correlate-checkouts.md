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
status: ready
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
- [ ] Typecheck/lint/build and regression checks. Lint and build pass; typecheck is blocked by a generated Prisma client missing `conversationModerationAssessment` in the existing `tests/integration/merchant/conversations/messages.service.postgres.test.ts`.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Reuse exactly one authenticated HTTP endpoint. Do not add a second `/orders` route, SQL write or synthetic Shopify `order.completed` event.

## Completion Report

### Status

Changes Requested — Attempt 1 reviewed on 2026-10-20. Attempt remains 1; executor and claimed_at are cleared. Attempt 0 review history is preserved below.

### Files Changed

- `README.md`
- `openapi/woocommerce-activity-v1.yaml`
- `scripts/test-arch035-woo-activity-redis.mjs`
- `src/composition/woocommerce.ts`
- `src/index.ts`
- `src/woocommerce/activity/contract.ts`
- `src/woocommerce/activity/order-producer.ts` (untracked)
- `src/woocommerce/activity/producer.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/activity/request.ts`
- `src/woocommerce/activity/routes.ts`
- Woo activity fixtures, unit tests and Redis integration test under `tests/`
- `typescript` untracked path is present in the implementation worktree and was not inspected, staged or changed.

### Work Completed

- Extended the API-008 activity contract to accept `ORDER_PLACED`, `ORDER_PAID`, and `ORDER_CANCELLED` with a bounded order snapshot and matching checkout correlation key.
- Added a distinct Woo order queue and deterministic shop/event-scoped replay behavior; checkout and order jobs remain separate from Shopify queues.
- Extended the existing authenticated route, OpenAPI, fixtures, unit coverage and disposable Redis integration.
- Implementation remains uncommitted in the worktree; no API-019 source changes are yet durably recorded on its task branch.

### Validation Results

- `npm run test:arch035-woo-activity:unit`: passed, 20 tests.
- `npm run test:arch035-woo-activity:redis`: passed, 2 tests.
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: failed in `tests/integration/merchant/conversations/messages.service.postgres.test.ts` because generated Prisma type `PrismaClient` lacks `conversationModerationAssessment`.
- The implementation task worktree contains uncommitted API-019 changes and currently tracks `origin/main`; it is not synchronized to `origin/task/ARCH-035-API-019`. No implementation changes were staged, committed or pushed during this review.
- The parent task record is in its canonical task worktree. No task implementation changes were made by this review.

### Deviations

- The required validation gate is incomplete because typecheck fails against the currently generated Prisma client. The current implementation worktree also has no durable API-019 implementation commit and has an incorrect upstream tracking reference.

### Assumptions

Developer must materialise and claim the task in its canonical isolated parent and implementation worktrees. Snapshot is not evidence of current remote task state.

### Unresolved Issues

- Establish the correct API task branch tracking/synchronization and commit/push only task-owned implementation files; preserve the pre-existing untracked `typescript` path.
- Resolve the generated Prisma client/schema mismatch or document a verified baseline/environment blocker, then obtain a passing API typecheck.
- Rerun the required regression checks after committing the implementation and verify the remote task branch contains those commits.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Changes Requested.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. The API-019 order implementation is present and focused tests, Redis integration, lint and build pass; however, no durable implementation commit exists in its task worktree, the worktree tracks `origin/main`, and typecheck fails against the generated Prisma client. A passing/Accepted review and explicit completion are therefore not authorized. The unrelated/untracked `typescript` path was preserved untouched.

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
- Typecheck: failed on missing generated Prisma client member `conversationModerationAssessment` in an existing PostgreSQL integration test.
- Source remains uncommitted and unpublished for API-019.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.

### Developer Self-Review - Changes Requested

1. Synchronize the canonical implementation worktree to `task/ARCH-035-API-019` and configure its upstream as `origin/task/ARCH-035-API-019`; do not push task code to `main`.
2. Preserve the untracked `typescript` path and commit/push only verified API-019-owned implementation files. Confirm the task branch remote contains the implementation commit(s).
3. Resolve the typecheck failure in the generated Prisma client contract (`conversationModerationAssessment` missing from `PrismaClient`) or record verified baseline evidence showing why this is unrelated and obtain the authorized validation decision. Do not edit unrelated tests/schema merely to suppress the failure.
4. Rerun and record focused unit, Redis/BullMQ integration, OpenAPI, typecheck, lint, build and `git diff --check` after branch synchronization/commit.
5. Update the Completion Report from the committed diff, then request review again. Do not complete the task until a durable passing Accepted review exists.

Transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. Do not claim Attempt 2 in this review.
