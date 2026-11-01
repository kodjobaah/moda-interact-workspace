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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
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

- [x] Implement route + strict schema + producer as small separate modules.
- [x] Add OpenAPI/fixture examples and scoped duplicate/error responses.
- [x] Test invalid and revoked installation, cross-tenant event ID, queue failure, bounded payload, replay and conflicting retained job.
- [x] Demonstrate existing Shopify/merchant API routes unchanged; focused route-composition tests pass with current route counts.

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

- [x] Real Woo installation principal determines shop; forged shop identifiers rejected.
- [x] Valid checkout event becomes a Woo-only BullMQ job before `202` response.
- [x] Failed enqueue does not report accepted; retry with same event ID is safe within retained job window.
- [x] No CheckoutRecovery, provider billing or outbound message is created.
- [x] No Shopify queue receives a Woo payload.

## Validation

- [x] Focused API route/schema/producer unit tests (12 passed).
- [x] Redis/BullMQ integration: authenticated enqueue, retained duplicate, failed queue, cross-tenant isolation (2 passed).
- [x] API typecheck, lint, build, changed-file diff check; focused route composition (6 passed).

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Use the established hosted API composition/authenticator and existing BullMQ infrastructure. If API Redis producer capability is absent, add the smallest bounded producer wiring in the API; Gateway owns deployment wiring. Do not create a DB receipt table or publish unrecognised jobs on the Shopify queue.

## Completion Report

### Status

Complete — Attempt 1 accepted and explicitly completed by the developer on 2026-10-20. Attempt 0 review history is preserved below.

### Files Changed

- `README.md`
- `openapi/woocommerce-activity-v1.yaml`
- `package.json`, `package-lock.json`
- `scripts/test-arch035-woo-activity-redis.mjs`
- `src/composition/routes.ts`, `src/composition/woocommerce.ts`, `src/index.ts`, `src/server.ts`
- `src/woocommerce/activity/contract.ts`
- `src/woocommerce/activity/producer.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/activity/request.ts`
- `src/woocommerce/activity/routes.ts`
- `tests/fixtures/woocommerce/activity/checkout-event.ts`
- `tests/fixtures/woocommerce/activity/checkout.json`
- `tests/fixtures/woocommerce/activity/reserved-order.json`
- `tests/integration/woocommerce/activity/redis-queue.test.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/composition/routes.test.ts`
- `tests/unit/woocommerce/activity/contract.test.ts`
- `tests/unit/woocommerce/activity/openapi.test.ts`
- `tests/unit/woocommerce/activity/producer.test.ts`
- `tests/unit/woocommerce/activity/routes.test.ts`

### Work Completed

- Added the authenticated `POST /v1/woocommerce/activity` checkout-capture route using the existing Woo installation principal and explicit Woo platform validation.
- Added strict bounded `woo.activity.v1` checkout parsing, documented OpenAPI and fixtures; order events remain reserved for API-019.
- Added an API-owned Woo-only BullMQ producer with shop/event-scoped deterministic job IDs, retained-job content-digest conflict detection, and retryable enqueue failures.
- Added route, producer, Redis/BullMQ integration tests and API documentation. No database receipt, recovery, billing or outbound messaging behavior was introduced.
- Corrected stale existing route-registration test counts discovered during task validation; verified actual route composition passes.

### Validation Results

- `npm run test:arch035-woo-activity:unit`: passed, 12 tests.
- `npm run test:arch035-woo-activity:redis`: passed, 2 tests, including transport failure without a `202` response.
- `npx tsx --test tests/unit/composition/routes.test.ts tests/unit/composition/real-route-registration.test.ts`: passed, 6 tests after correcting stale route counts.
- `npm run typecheck`: passed.
- `npm run lint`: passed with zero warnings.
- `npm run build`: passed.
- `git diff --check`: passed.
- Implementation task branch is clean except for an unrelated pre-existing `database` submodule gitlink modification. That pointer targets commit `69c0c8b` from ARCH-040-DATABASE-005 and was not staged or changed by this task.
- Implementation commits are published on `origin/task/ARCH-035-API-008`, ending at `e28e5d9e06a3ef38ae45e9ca842a3a58c5ccbe31`.

### Deviations

None.

### Assumptions

Developer must materialise and claim the task in its canonical isolated parent and implementation worktrees. Snapshot is not evidence of current remote task state.

### Unresolved Issues

None within API-008 scope. Redis job-ID deduplication remains intentionally bounded by the BullMQ retained-job window; this is documented and no permanent replay ledger is promised.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Developer Self-Review Accepted; developer completion decision recorded below.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. Attempt 1 satisfies its current API-008 checkout-only requirements; order events remain disabled for API-019. The implementation commit and all task-specific validation are published/recorded. The unrelated database gitlink modification was preserved and excluded from task commits.

### Reviewed Files

- Woo activity contract, request parser, route, producer, Redis adapter and route composition.
- API-008 OpenAPI and fixture files.
- Focused unit/integration tests and route registration test.

### Validation Reviewed

- Woo activity unit: 12 passed.
- Disposable Redis/BullMQ integration: 2 passed.
- API route composition: 6 passed.
- Typecheck, lint, build and diff check: passed.

### Architecture Conformance

Conforms to the capture-only API-008 scope: existing Woo installation authentication determines tenant identity; only checkout updates are enabled; jobs use a dedicated Woo queue; enqueue completion precedes `202`; no persistent receipt ledger, recovery processing, billing, or provider send is introduced. Existing route composition remains valid.

### Follow-up

API-019 and WooCommerce-007 are dependency-ready. Background-001 remains pending because it also depends on WooCommerce-007.

### Developer Self-Review Accepted

Attempt 1 passes review. All API-008 Work Items and Acceptance Criteria are complete, implementation commits are published on the canonical task branch, and the required focused validations pass. The implementation checkout's unrelated database gitlink modification remains untouched and uncommitted.

### Developer Completion Decision

On 2026-10-20, the developer explicitly completed ARCH-035-API-008 after the durable Attempt 1 Accepted review. Status is `complete`; executor and claimed_at are null; attempt remains 1. No merge to `main` was performed.
