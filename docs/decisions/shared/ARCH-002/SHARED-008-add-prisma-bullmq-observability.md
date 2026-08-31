---
id: ARCH-002-SHARED-008
architecture_id: ARCH-002
title: Add Prisma and BullMQ observability adapters
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 20
executor: codex
claimed_at: 2026-08-31T13:19:18Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-007
enables:
  - ARCH-002-SHARED-010
created: 2026-08-31
updated: 2026-08-31
---

# Add Prisma and BullMQ observability adapters

## Objective

Add reusable Prisma and BullMQ adapters on top of the architect-accepted base
Node runtime.

## Boundary

SHARED-007 intentionally contains no Prisma/BullMQ implementation. This task is
the only shared task in ARCH-002 that introduces those generic integrations.

## Scope

- add optional Prisma instrumentation to the shared Node service profile;
- modify the accepted shared Node runtime only as required to register Prisma
  before application Prisma imports;
- BullMQ OpenTelemetry adapter using BullMQ's native telemetry interface;
- BullMQ metrics enabled through the same global meter provider;
- producer/consumer trace context continuity;
- queue/worker helpers that do not require each service to construct `BullMQOtel`;
- no queue payload mutation solely for tracing unless required by BullMQ itself.

## Requirements

Use `@prisma/instrumentation` compatible with the workspace Prisma major and
`bullmq-otel` compatible with the workspace BullMQ version. Current reference
versions are documented in the supplied dependency file; verify the committed
consumer versions before publication.

BullMQ telemetry must be passed through Queue/Worker options. Do not monkey-patch
BullMQ.

The final post-SHARED-008 Node profile may expose:

```ts
instrument: {
  http?: boolean;
  fetch?: boolean;
  prisma?: boolean;
}
```

The `prisma` property and `PrismaInstrumentation` registration are introduced by
this task, not retroactively attributed to SHARED-007.

Reference integration delta:

`docs/decisions/shared/ARCH-002/reference-observability/moda-interact-shared/prisma-node-extension.reference.md`

## Reference API

```ts
const telemetry = createBullMQTelemetry({
  serviceName: "moda-messaging-worker",
  enableMetrics: true,
});

new Worker(queueName, processor, {
  connection,
  telemetry,
});
```

## Acceptance Criteria

- [x] Prisma profile support is introduced only in SHARED-008;
- [x] Prisma spans are emitted when Prisma is enabled and imported after preload;
- [x] BullMQ producer and worker spans join the same distributed trace where supported;
- [x] BullMQ metrics are emitted without high-cardinality Moda IDs as labels;
- [x] adapters are safe when telemetry/exporters are disabled;
- [x] no service-local BullMQOtel constructor helper is required;
- [x] tests/typecheck/build pass.

## Validation

- [x] Prisma smoke test;
- [x] local Redis BullMQ producer/worker trace test where practical;
- [x] metric attribute/cardinality review;
- [x] package build/typecheck/tests.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `moda-interact-shared/tsup.config.ts`
- `moda-interact-shared/README.md`
- `moda-interact-shared/src/observability/node.ts`
- `moda-interact-shared/src/observability/bullmq.ts`
- `moda-interact-shared/src/observability/adapters.test.ts`
- `moda-interact-shared/src/observability/bullmq.integration.test.ts`
- `moda-interact-shared/src/observability/test-fixtures/adapters-preload.ts`
- `moda-interact-shared/src/observability/test-fixtures/adapters-app.ts`
- `moda-interact-shared/src/observability/test-fixtures/bullmq-live-app.ts`
- `docs/decisions/shared/ARCH-002/SHARED-008-add-prisma-bullmq-observability.md`

### Work Completed

- Added opt-in Prisma instrumentation to the accepted Node service profile and
  registered it with the SDK before application imports.
- Added a Node-only `./observability/bullmq` export whose factory constructs
  `BullMQOtel` for BullMQ's native Queue and Worker `telemetry` option.
- Kept Redis connections and propagation metadata under BullMQ/service
  ownership; the adapter does not patch BullMQ or mutate job payloads.
- Added no-op-provider, Prisma span, synthetic BullMQ trace/metric, and live
  Queue/Worker integration coverage.
- Documented preload ordering, native BullMQ usage, and bounded metric
  dimensions.

### Validation Results

- `npm test` — pass, 59/59 active tests; the Redis-gated test skips when
  `TEST_REDIS_URL` is absent.
- Live Redis integration test — pass, 1/1 using BullMQ Queue and Worker against
  a temporary `redis:7-alpine` container; root, producer, and worker spans
  shared one trace.
- Prisma/BullMQ adapter smoke — pass; Prisma client span, joined BullMQ spans,
  and BullMQ completion metrics exported to local OTLP receivers.
- Metric cardinality review — pass; queue name, bounded job name, and state are
  present, while BullMQ job and Moda shop, checkout, conversation, and message
  IDs are absent.
- `npm run typecheck` — pass.
- `npm run build` — pass; BullMQ JS and declaration entries emitted.
- `npm pack --dry-run` — pass, 32-file package artifact.
- Node package-export import of `./observability/bullmq` — pass.
- Editor diagnostics for touched TypeScript files — no errors.
- `scripts/workspace-doctor.sh --quick` — 6 checks pass; existing warning for
  `moda-interact/.npmrc` `shamefully-hoist` configuration.

### Deviations

None. `ioredis` and `bullmq` are development-only dependencies used by the live
adapter test; production connection ownership remains service-side.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect review completed 2026-08-31.

The implementation is accepted against the SHARED-008 task as defined before the
workspace-wide task-granularity policy was strengthened.

Verified architecture boundaries:

- Prisma support is introduced as an opt-in extension of the accepted shared Node
  runtime and remains preload-dependent.
- BullMQ integration uses BullMQ's native `telemetry` option via `bullmq-otel`;
  it does not monkey-patch BullMQ.
- The adapter does not mutate Moda queue payloads solely to propagate tracing
  context.
- BullMQ tracing and metrics use the global OpenTelemetry providers installed by
  the shared Node runtime.
- BullMQ metric dimensions exclude job IDs and Moda shop, checkout,
  conversation and message identifiers.
- the published runtime dependency range is compatible with the workspace's
  BullMQ 6.x consumers and Prisma 6.19.x baseline.
- the package export remains Node-only and does not contaminate the browser-safe
  observability entry point.

The submitted Completion Report records passing package tests, typecheck, build,
package dry-run, Prisma adapter smoke coverage, and a live Redis Queue/Worker
trace-continuity test. The review environment did not rerun those commands from
the compressed archive because installed dependencies are not included.

No corrective implementation is required.

`ARCH-002-SHARED-008` is architect-accepted Complete.

