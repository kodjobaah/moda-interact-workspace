---
id: ARCH-002-SHOPIFY-007
architecture_id: ARCH-002
title: Wire shared BullMQ telemetry on Shopify queue producers
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 31
executor: codex
claimed_at: 2026-08-31 15:34:21+00:00
attempt: 1
depends_on:
- ARCH-002-SHOPIFY-006
enables:
- ARCH-002-GATEWAY-006
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: '2026-08-31'
---

# Wire shared BullMQ telemetry on Shopify queue producers

## Objective

Use the shared BullMQ telemetry adapter on Shopify-owned Queue producers so
OpenTelemetry context continues from webhook ingress into queued work.

## Scope

- import the shared BullMQ adapter from
  `@modainteract/moda-interact-shared/observability/bullmq`;
- construct the shared telemetry object once at the appropriate process/module
  boundary;
- pass it through BullMQ Queue's supported `telemetry` option;
- prove HTTP/webhook -> Queue producer trace continuity;
- preserve the existing business queue payload contract.

## Out of Scope

- Worker/consumer instrumentation;
- adding or changing business queue fields;
- new Shopify semantic metrics/spans;
- local BullMQOtel construction helpers;
- provider/exporter/sampler changes;
- background repository changes.

## Acceptance Criteria

- [x] Shopify Queue producers use the shared BullMQ telemetry adapter;
- [x] no BullMQ monkey-patching exists;
- [x] producer trace context is propagated through BullMQ telemetry;
- [x] queue business payload shape remains unchanged;
- [x] telemetry failure does not change queue/business correctness.

## Validation

- [x] focused Queue telemetry test;
- [x] HTTP/webhook -> Queue trace-continuity test;
- [x] affected repository tests;
- [x] repository-defined typecheck;
- [x] production build.

## Stop Condition

After the Queue producer integration is complete and validated, set this task to
`review`, write the Completion Report, return to `moda_architect`, and STOP.

Do not begin gateway or background work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/app/services/webhooks/shopify-webhook-queue.server.ts`
- `moda-interact/tests/unit/webhooks/shopify-webhook-queue.server.test.js`
- `moda-interact/tests/integration/shopify-webhook-queue-telemetry.test.ts`
- `docs/decisions/shopify/ARCH-002/SHOPIFY-007-wire-shared-bullmq-telemetry.md`

### Work Completed

- Constructed one shared BullMQ telemetry adapter at module scope with
  `serviceName=moda-interact`.
- Passed that adapter through BullMQ's supported `telemetry` option on both the
  checkout-events and order-events Queue producers.
- Preserved Queue names, job names, deterministic job IDs, retry policy,
  publication outcomes, and shared business event payloads.
- Extended focused Queue tests to verify both producers receive the same shared
  adapter and pass event data unchanged.
- Added a Redis-backed integration test proving one trace continues from an
  active webhook request span through the real ingress service, Queue producer,
  and Worker process span.
- Proved publication and processing still succeed after the telemetry provider
  is shut down.

### Validation Results

- `npm test -- tests/unit/webhooks/shopify-webhook-queue.server.test.js` passed:
  1 file, 7 tests.
- Redis-backed focused validation passed with `TEST_REDIS_URL` against an
  isolated `redis:7-alpine` container: 2 files, 8 tests.
- Redis-backed full `npm test` passed: 14 files, 77 tests.
- `npm run typecheck` ran the repository-defined contract and reported only the
  established TYPECHECK-001 baseline: 48 errors in 8 unrelated files, with no
  task-changed-file diagnostics.
- `npm run build` passed, including Prisma Client generation and the production
  React Router client/server bundles.
- Final source scan confirmed exactly one shared adapter construction, native
  Queue options only, no monkey-patching, and no trace metadata or payload-field
  additions in webhook ingress.

### Deviations

The established TYPECHECK-001 baseline remains unchanged.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular SHOPIFY-007 boundary:

- one shared BullMQ telemetry adapter is constructed at module scope through
  `@modainteract/moda-interact-shared/observability/bullmq`;
- both Shopify-owned Queue producers receive that adapter through BullMQ's
  supported `telemetry` option;
- no monkey-patching or repository-local BullMQ telemetry implementation was
  introduced;
- Queue names, job names, deterministic IDs, retry behaviour and publication
  outcomes remain unchanged;
- the business event object is passed to `queue.add()` unchanged; no trace
  metadata or other observability fields were added to the queue payload;
- the Redis-backed integration test demonstrates one trace across the active
  Shopify webhook span, BullMQ producer span and a test Worker consumer span;
- the Worker used for that proof exists only in test code and does not introduce
  Shopify-owned worker/consumer implementation;
- queue publication/processing remains functional when the OpenTelemetry
  provider is no longer active;
- no background, gateway, provider/exporter/sampler or new Shopify semantic
  telemetry work was introduced.

The Completion Report records focused tests and the Redis-backed full test suite
as passing, the production build as passing, and repository typecheck as matching
the existing TYPECHECK-001 baseline with no diagnostics in task-changed files.

`ARCH-002-SHOPIFY-007` is architecturally Complete.
