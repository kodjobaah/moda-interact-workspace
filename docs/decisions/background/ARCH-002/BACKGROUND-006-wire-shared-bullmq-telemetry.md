---
id: ARCH-002-BACKGROUND-006
architecture_id: ARCH-002
title: Wire shared BullMQ telemetry in background processing
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 31
executor: codex
claimed_at: 2026-08-31 17:25:53+00:00
attempt: 1
depends_on:
- ARCH-002-BACKGROUND-005
enables:
- ARCH-002-BACKGROUND-007
- ARCH-002-BACKGROUND-008
created: 2026-08-31
updated: '2026-08-31'
---

# Wire shared BullMQ telemetry in background processing

## Objective

Use the shared BullMQ telemetry adapter on the actual background Queue/Worker
boundaries so trace context continues through asynchronous background work.

## Scope

Apply `@modainteract/moda-interact-shared/observability/bullmq` to:

- checkout Worker;
- order Worker;
- pending-recovery-candidate Worker;
- WhatsApp Worker;
- background-owned pending-recovery-candidate Queue producer.

Use BullMQ's supported native `telemetry` options.

Prove trace continuity across representative producer/consumer boundaries while
preserving the exact existing business payloads.

## Out of Scope

- worker operational counters/histograms;
- GenAI/CommerceAgent spans or metrics;
- manual `traceparent`/baggage fields in business payloads;
- queue/job name changes;
- retry/backoff/concurrency changes;
- provider/exporter/sampler changes;
- gateway/backend configuration.

## Acceptance Criteria

- [x] all actual background BullMQ Worker boundaries use the shared adapter;
- [x] the background-owned Queue producer uses the shared adapter;
- [x] no BullMQ monkey-patching or local telemetry adapter exists;
- [x] business queue payloads are unchanged;
- [x] representative producer -> consumer trace continuity is proven;
- [x] telemetry unavailability does not change BullMQ business correctness.

## Validation

- [x] focused Worker/Queue telemetry tests;
- [x] Redis-backed trace propagation test where practical;
- [x] payload identity test;
- [x] failure-isolation test;
- [x] affected repository tests;
- [x] typecheck;
- [x] production build.

## Stop Condition

After BullMQ telemetry is complete and validated, set this task to `review`,
complete the Completion Report, return to `moda_architect`, and STOP.

Do not begin BACKGROUND-007 or BACKGROUND-008.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/src/workers/checkout.worker.ts`
- `moda-interact-background/src/workers/orders.worker.ts`
- `moda-interact-background/src/workers/pending-recovery-candidate.worker.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/integration/bullmq-telemetry.integration.test.ts`
- `moda-interact-background/tests/unit/runtime/bullmq-telemetry.test.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-006-wire-shared-bullmq-telemetry.md`

### Work Completed

- Attached the published shared BullMQ adapter through BullMQ's native
	`telemetry` option on the checkout, order, pending-recovery-candidate and
	WhatsApp Workers.
- Attached the same shared adapter contract to the background-owned lazy
	pending-recovery-candidate Queue producer.
- Used canonical process identities: Shopify event for checkout/order and the
	pending-candidate producer, recovery for candidate materialization, and
	messaging for WhatsApp processing.
- Preserved all queue/job names, business payloads, delays, retry/backoff,
	retention and concurrency options.
- Added focused constructor, payload-identity, no-provider correctness and real
	Redis producer/consumer trace-continuity coverage.

### Validation Results

- Focused unit tests: 2 files and 14 tests passed.
- Redis-backed integration test against disposable Redis 7: 2 tests passed;
	producer and consumer spans inherited the active parent trace ID, the
	consumed payload remained equal to the published candidate, and processing
	succeeded without a registered telemetry provider.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed, including Prisma Client generation and TypeScript
	compilation.
- `npm test`: 13 files passed, 1 failed, 2 skipped; 79 tests passed, 1 failed,
	4 skipped. The sole failure is the pre-existing unrelated
	`recovery-routing.service.test.ts` mock omission for
	`prisma.customerPhone.findMany`; no BullMQ telemetry test failed.
- Source review found exactly five BullMQ constructors and five native
	telemetry options, with no `traceparent`, baggage, prototype patching, local
	`BullMQOtel`, worker metrics or GenAI instrumentation.
- VS Code diagnostics were clean for all changed production and test files.

### Deviations

The Redis integration test is gated by `TEST_REDIS_URL` for normal repository
runs. It was executed explicitly against a disposable local Redis 7 container.

### Assumptions

- The pending-recovery-candidate Queue is currently produced by the checkout
	path in the Shopify event process, so its telemetry adapter uses
	`moda-shopify-event-worker`.
- OpenTelemetry provider/exporter setup remains test-only and is not introduced
	into production service code.

### Unresolved Issues

- The existing recovery-routing unit-test mock still lacks
	`prisma.customerPhone.findMany`, leaving the unrelated full suite one test
	short of green.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular BACKGROUND-006 boundary:

- the checkout, order, pending-recovery-candidate and WhatsApp Workers all use
  `@modainteract/moda-interact-shared/observability/bullmq`;
- the background-owned pending-recovery-candidate Queue producer uses the same
  shared adapter;
- all five boundaries pass the adapter through BullMQ's supported native
  `telemetry` option;
- service identities match the accepted worker topology:
  `moda-shopify-event-worker`, `moda-recovery-worker`, and
  `moda-messaging-worker`;
- queue names, job names, deterministic IDs, delays, retries/backoff, retention
  and concurrency remain unchanged;
- business queue payloads are unchanged and no `traceparent`, baggage or other
  observability field is added to them;
- no BullMQ monkey-patching or repository-local telemetry adapter was
  introduced;
- the Redis-backed integration test proves an active parent trace continues
  through the Queue producer and Worker consumer while preserving exact payload
  identity;
- the same integration coverage proves BullMQ business processing succeeds when
  no telemetry provider is registered;
- no BACKGROUND-007 worker metrics or BACKGROUND-008 GenAI span integration was
  introduced.

The Completion Report records focused BullMQ tests as passing, Redis-backed
trace propagation and failure-isolation tests as passing, TypeScript typecheck
as passing, and the production build as passing.

The full repository suite still contains the previously known unrelated
`recovery-routing.service.test.ts` Prisma mock omission. No BullMQ telemetry
test failed.

The added OpenTelemetry SDK packages are development-only support for the
Redis-backed trace-continuity test and do not change the production runtime
dependency boundary.

`ARCH-002-BACKGROUND-006` is architecturally Complete.

`ARCH-002-BACKGROUND-007` and `ARCH-002-BACKGROUND-008` are now independently
unblocked and may move to `ready`.
