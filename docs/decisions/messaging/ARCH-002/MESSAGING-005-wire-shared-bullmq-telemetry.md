---
id: ARCH-002-MESSAGING-005
architecture_id: ARCH-002
title: Wire shared BullMQ telemetry on inbound message queue
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 31
executor: codex
claimed_at: 2026-08-31 16:23:04+00:00
attempt: 1
depends_on:
- ARCH-002-MESSAGING-003
enables:
- ARCH-002-GATEWAY-006
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-31
updated: '2026-08-31'
---

# Wire shared BullMQ telemetry on inbound message queue

## Objective

Use the shared BullMQ telemetry adapter on the messaging ingress Queue so trace
context can continue from the inbound WhatsApp request into background work.

## Scope

- create shared BullMQ telemetry through
  `@modainteract/moda-interact-shared/observability/bullmq`;
- pass it through the inbound Queue's supported `telemetry` option;
- prove HTTP ingress -> Queue producer trace continuity;
- preserve the existing queue business payload contract.

## Out of Scope

- Meta ingress semantic metrics/spans;
- worker/consumer instrumentation;
- CommerceAgent/GenAI telemetry;
- queue payload contract changes;
- provider/exporter/sampler changes.

## Acceptance Criteria

- [x] inbound Queue uses the shared BullMQ telemetry adapter;
- [x] no local BullMQOtel helper or monkey-patching exists;
- [x] request -> Queue producer trace continuity is proven;
- [x] business queue payload shape is unchanged;
- [x] telemetry failure does not change queue/business correctness.

## Validation

- [x] focused Queue telemetry test;
- [x] HTTP ingress -> Queue trace-continuity test;
- [x] affected repository tests;
- [x] repository-defined typecheck;
- [x] production build.

## Stop Condition

After Queue telemetry is complete and validated, set this task to `review`, write
the Completion Report, return to `moda_architect`, and STOP.

Do not begin background or gateway work.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-messaging/app/lib/queues/whatsapp.queue.ts`
- `moda-interact-messaging/tests/whatsapp-queue-telemetry.test.mjs`
- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `docs/decisions/messaging/ARCH-002/MESSAGING-005-wire-shared-bullmq-telemetry.md`

### Work Completed

- Created one shared BullMQ telemetry adapter for
  `moda-interact-messaging` and passed it through the inbound Queue's native
  `telemetry` option.
- Preserved the `whatsapp-events` Queue name, normalized job payload, job name,
  retry/backoff policy, retention policy, and deterministic job identifier.
- Added focused contract coverage for the shared adapter and native Queue
  option with no local helper, manual context field, or prototype patching.
- Added Redis-backed coverage through the real signed WhatsApp action, Queue,
  and Worker proving request/producer/consumer trace continuity, exact payload
  identity, and successful processing after telemetry globals are disabled.

### Validation Results

- `TEST_REDIS_URL=redis://127.0.0.1:6382 node --import tsx --test tests/whatsapp-queue-telemetry.test.mjs`: 2 passed.
- `TEST_REDIS_URL=redis://127.0.0.1:6382 npm test`: 8 passed before the final
  independent contract assertion; the focused rerun passed both Queue tests.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `scripts/workspace-doctor.sh --quick`: 7 checks passed, with one existing
  informational local-link condition and one existing `shamefully-hoist`
  warning.

### Deviations

None.

### Assumptions

- Native BullMQ telemetry context serialization remains an internal transport
  concern and is not part of the business job payload contract.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular MESSAGING-005 boundary:

- one shared BullMQ telemetry adapter is created at module scope through
  `@modainteract/moda-interact-shared/observability/bullmq`;
- the inbound `whatsapp-events` Queue receives the adapter through BullMQ's
  supported native `telemetry` option;
- no repository-local BullMQ telemetry helper, prototype patching,
  `traceparent`, baggage or manual queue-context payload field was introduced;
- the existing queue name, `message-received` job name, deterministic job ID,
  retry/backoff policy and retention behaviour remain unchanged;
- the normalized `WhatsAppInboundEvent` business payload is passed to
  `queue.add()` unchanged;
- the Redis-backed integration test proves one trace across the active inbound
  request span, BullMQ Queue producer span and test Worker consumer span;
- the Worker exists only in test code to prove propagation and does not add
  messaging-owned worker/consumer runtime implementation;
- the same integration test verifies exact business payload identity at the
  Worker and successful request/queue processing after the telemetry globals
  are disabled;
- no CommerceAgent/GenAI, background, gateway, provider/exporter/sampler or
  additional ingress-semantic implementation was introduced.

The Completion Report records focused Queue telemetry tests, the Redis-backed
repository suite, typecheck and production build as passing. The workspace
doctor reported only previously known informational/baseline conditions.

The added `tsx`, `@opentelemetry/context-async-hooks` and
`@opentelemetry/sdk-trace-node` entries are dev-only test support for the
Redis-backed trace-continuity proof; they do not alter the production runtime
dependency boundary.

`ARCH-002-MESSAGING-005` is architecturally Complete.

The messaging observability consumer chain MESSAGING-003/004/005 is now
Complete. Downstream gateway/system-test tasks must still satisfy their other
cross-domain dependencies before becoming Ready.
