---
id: ARCH-002-BACKGROUND-005
architecture_id: ARCH-002
title: Adopt shared observability runtime in production workers
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 30
executor: codex
claimed_at: 2026-08-31 17:12:04+00:00
attempt: 1
depends_on:
- ARCH-002-BACKGROUND-001
- ARCH-002-BACKGROUND-002
- ARCH-002-BACKGROUND-004
- ARCH-002-SHARED-010
enables:
- ARCH-002-BACKGROUND-006
created: 2026-08-31
updated: '2026-08-31'
---

# Adopt shared observability runtime in production workers

## Objective

Install the published shared Node observability runtime before application
imports in each of the three ARCH-002 production background processes.

## Established Process Boundaries

Use the entrypoints accepted in `ARCH-002-BACKGROUND-001`:

| Service | Command | Worker set |
| --- | --- | --- |
| `moda-shopify-event-worker` | `npm run start:shopify-event-worker` | checkout + order |
| `moda-recovery-worker` | `npm run start:recovery-worker` | pending recovery candidate |
| `moda-messaging-worker` | `npm run start:messaging-worker` | WhatsApp + current CommerceAgent workflow |

## Scope

- consume exact `@modainteract/moda-interact-shared@0.4.0`;
- add a small preload/profile for each production worker process;
- initialize `@modainteract/moda-interact-shared/observability/node` before the
  corresponding compiled entrypoint/application imports;
- use canonical `service.name` values from the table above;
- use `service.namespace=moda-interact`;
- preserve environment identity through `deployment.environment.name`;
- enable generic HTTP/fetch/Undici and Prisma instrumentation where used by the
  process;
- preserve the worker commands established by BACKGROUND-001, adding only the
  required preload;
- prove there is one generic provider/exporter/sampler runtime per process.

## Out of Scope

- BullMQ Queue/Worker telemetry wiring;
- worker/domain operational metrics;
- GenAI/CommerceAgent semantic spans or metrics;
- Render/Grafana/OTLP credential wiring;
- worker topology/readiness changes;
- queue payload/contract changes.

## Acceptance Criteria

- [x] all three production processes preload shared observability before worker/library imports;
- [x] canonical service names are exact and environment-neutral;
- [x] generic runtime/provider/exporter/sampling ownership is shared, not service-local;
- [x] HTTP/fetch/Undici and Prisma generic instrumentation is enabled where required;
- [x] local/test hosted export remains disableable;
- [x] no BullMQ or GenAI integration work is implemented in this task.

## Validation

- [x] focused preload/startup tests for all three commands;
- [x] service/resource identity tests;
- [x] duplicate provider/exporter ownership review;
- [x] affected repository tests;
- [x] typecheck;
- [x] production build.

## Stop Condition

After runtime adoption and required validation are complete, set this task to
`review`, complete the Completion Report, return to `moda_architect`, and STOP.

Do not begin BACKGROUND-006 or any later observability task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/Dockerfile`
- `moda-interact-background/package.json`
- `moda-interact-background/observability/shopify-event.mjs`
- `moda-interact-background/observability/recovery.mjs`
- `moda-interact-background/observability/messaging.mjs`
- `moda-interact-background/src/entrypoints/shopify-event.ts`
- `moda-interact-background/src/entrypoints/recovery.ts`
- `moda-interact-background/src/entrypoints/messaging.ts`
- `moda-interact-background/src/runtime/observability.ts`
- `moda-interact-background/tests/unit/runtime/entrypoint-isolation.test.ts`
- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-005-adopt-shared-observability-runtime.md`

### Work Completed

- Added one small shared-runtime preload/profile for each accepted production
  worker process and prefixed the existing worker command with Node `--import`.
- Configured exact environment-neutral service names, explicit
  `service.namespace=moda-interact`, deployment-environment resolution through
  the shared runtime, and HTTP/fetch/Undici plus Prisma instrumentation.
- Integrated shared-runtime shutdown after graceful worker/resource drain and
  on pre-consumer readiness failure so instrumented processes terminate cleanly.
- Packaged all three preloads in the production Docker image.
- Added startup contract coverage for preload ordering, service/resource
  identity, instrumentation profiles, disablement, process singleton ownership,
  cleanup, package version and production packaging.
- Added no BullMQ telemetry or GenAI semantic instrumentation.

### Validation Results

- `npm test -- --run tests/unit/runtime/observability-startup.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/runtime/readiness.test.ts tests/unit/runtime/worker-process.test.ts`:
  passed, 4 files and 22 tests.
- Disabled-runtime subprocess probes passed for all three preloads with exact
  canonical service names and `deployment.environment.name=test`.
- Singleton probes confirmed repeated shared initialization returns the same
  process runtime.
- All three compiled production commands with `OTEL_SDK_DISABLED=true` and a
  deliberately failed Redis preflight exited `1` promptly with the existing
  sanitized readiness error; no worker consumer started.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed, including Prisma Client generation and production
  TypeScript compilation.
- `npm test`: 12 files passed, 1 failed, 1 skipped; 73 tests passed, 1 failed,
  2 skipped. The sole failure remains the unrelated existing
  `recovery-routing.service.test.ts` Prisma mock omission for
  `customerPhone.findMany`; no observability/startup test failed.
- Source ownership review found no service-local NodeSDK, provider, exporter,
  processor or sampler and no BullMQ/GenAI observability integration.
- VS Code diagnostics were clean for changed runtime, test and package files.

### Deviations

None.

### Assumptions

- Each current production worker graph uses external HTTP/fetch and Prisma, so
  the same generic instrumentation profile is appropriate for all three.
- The shared runtime's deployment environment resolver remains the canonical
  source for `deployment.environment.name`.

### Unresolved Issues

- The existing recovery-routing unit-test mock lacks
  `prisma.customerPhone.findMany`, leaving the unrelated full suite one test
  short of green.

### Architectural Concerns

None. Provider/exporter/sampler ownership remains exclusively in the shared
runtime; worker topology, readiness, queue contracts and business behavior are
unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation conforms to the granular BACKGROUND-005 boundary:

- all three architect-approved production commands preload the published shared
  Node observability runtime before their compiled worker entrypoints;
- the exact canonical service identities are used:
  - `moda-shopify-event-worker`;
  - `moda-recovery-worker`;
  - `moda-messaging-worker`;
- every preload uses `service.namespace=moda-interact`;
- deployment environment identity remains owned by the shared runtime resolver;
- the generic instrumentation profile enables HTTP, fetch/Undici and Prisma for
  the current worker graphs;
- the background service consumes the exact architect-approved
  `@modainteract/moda-interact-shared@0.4.0`;
- the production Docker image includes all three preload files;
- process shutdown invokes the shared runtime shutdown after BullMQ Workers have
  been gracefully closed, alongside the existing process-resource cleanup;
- readiness failure also shuts down the preloaded observability runtime before
  the process exits;
- repeated initialization resolves to the same process runtime, preserving
  singleton provider/exporter ownership;
- no service-local NodeSDK, provider, exporter, processor or sampler stack was
  introduced;
- no shared BullMQ telemetry adapter, worker operational metrics, GenAI spans or
  GenAI metrics were introduced.

The Completion Report records 22 focused startup/readiness/lifecycle tests as
passing, disabled-runtime subprocess probes for all three service identities as
passing, singleton checks as passing, TypeScript typecheck as passing and the
production build as passing.

The full repository suite still contains the same unrelated
`recovery-routing.service.test.ts` Prisma mock omission already observed in the
accepted BACKGROUND-001/002 work. No BACKGROUND-005 startup or observability
test failed.

`ARCH-002-BACKGROUND-005` is architecturally Complete.

`ARCH-002-BACKGROUND-006` is now unblocked and may move to `ready`.
