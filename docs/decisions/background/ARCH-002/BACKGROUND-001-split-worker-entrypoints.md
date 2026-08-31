---
id: ARCH-002-BACKGROUND-001
architecture_id: ARCH-002
title: Create independently deployable worker entrypoints
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 15
executor: codex
claimed_at: 2026-08-31 16:38:02+00:00
attempt: 1
depends_on:
- ARCH-002-GATEWAY-001
enables:
- ARCH-002-BACKGROUND-002
- ARCH-002-BACKGROUND-003
created: 2026-08-29
updated: '2026-08-31'
---

# Create Independently Deployable Worker Entrypoints

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Expose three independently deployable background-worker entrypoints matching the
ARCH-002 scaling boundaries used by both test and production:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

## Context

Accepted discovery found checkout, order, recovery and WhatsApp/CommerceAgent
workers starting from one Node process.

That prevents independent horizontal scaling and makes a Shopify event surge
consume the same process resources as recovery and messaging/CommerceAgent work.

ARCH-002 deliberately starts with three deployment units rather than creating a
fourth CommerceAgent queue/service before measurements justify it.

## Scope

Create repository-supported entrypoints/commands for:

1. `moda-shopify-event-worker`
   - checkout-event worker;
   - order-event worker.

2. `moda-recovery-worker`
   - pending recovery candidate/materialization worker.

3. `moda-messaging-worker`
   - WhatsApp inbound worker;
   - current CommerceAgent workflow used by that worker.

Preserve existing queue/job contracts and business behaviour.

Retain a combined local-development worker command only if it remains useful.

Implement graceful process shutdown for each production entrypoint so a deploy,
scale-down or termination signal stops accepting new work and closes/drains the
owned worker/resource set using the repository's supported BullMQ semantics.

## Out of Scope

- splitting CommerceAgent into a new queue/service;
- creating `moda-commerce-agent-worker`;
- changing recovery/order/messaging business semantics;
- changing BullMQ queue/job names or payload contracts;
- Render Blueprint configuration;
- choosing Render instance plans;
- implementing queue-aware autoscaling;
- OpenTelemetry implementation, which belongs to BACKGROUND-003.

## Requirements

Each production entrypoint must start only its intended worker set.

The commands must be environment-neutral and usable unchanged by:

```text
render.test.yaml
render.production.yaml
```

Do not globally serialize or merge queue concurrency.

Existing worker-level concurrency values may remain repository-local unless
evidence requires a change.

Do not make a production worker depend on an inbound HTTP listener merely to be
deployable as a Render background worker.

A production entrypoint must fail clearly on unrecoverable startup configuration
errors and must not silently start unintended worker classes.

Graceful termination must avoid deliberately abandoning in-flight jobs where the
current BullMQ worker APIs support graceful close/drain behaviour.

Do not log credentials or full job payloads during startup/shutdown.

## Work Items

- [x] add the three production worker entrypoints;
- [x] expose deterministic package scripts/commands;
- [x] preserve a combined development entrypoint if useful;
- [x] ensure each production entrypoint imports/starts only its owned workers;
- [x] implement graceful shutdown for each production entrypoint;
- [x] add startup/isolation tests;
- [x] add shutdown tests where practical;
- [x] document queue ownership and command mapping per entrypoint.

## Interfaces / Contracts

Produces startup commands consumed by:

```text
ARCH-002-GATEWAY-003
```

and canonical worker identities consumed by:

```text
ARCH-002-BACKGROUND-003
```

Logical service identities:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

The same logical identities apply in both test and production. The environment is
represented separately through deployment configuration and telemetry resource
attributes.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-BACKGROUND-002`
- `ARCH-002-BACKGROUND-003`

## Acceptance Criteria

- [x] Shopify-event entrypoint starts checkout + order workers only;
- [x] recovery entrypoint starts recovery worker only;
- [x] messaging entrypoint starts WhatsApp/current CommerceAgent workflow only;
- [x] each production command is usable by both test and production deployment;
- [x] terminating one worker process closes only that process's owned workers and
      resources;
- [x] queue/job contracts are unchanged;
- [x] no new CommerceAgent queue/service boundary is introduced;
- [x] existing worker tests remain valid;
- [x] production build succeeds.

## Validation

- [x] unit/integration tests;
- [x] typecheck;
- [x] production build;
- [x] command/startup verification;
- [x] entrypoint isolation verification;
- [x] graceful-shutdown verification where practical.

## Implementation Notes

Do not create a separate CommerceAgent queue boundary in this task.

The target Render shape is multiple deployments of the same repository with
different worker start commands, not a single monolithic worker process.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/README.md`
- `moda-interact-background/src/index.ts`
- `moda-interact-background/src/entrypoints/messaging.ts`
- `moda-interact-background/src/entrypoints/recovery.ts`
- `moda-interact-background/src/entrypoints/resources.ts`
- `moda-interact-background/src/entrypoints/shopify-event.ts`
- `moda-interact-background/src/runtime/worker-process.ts`
- `moda-interact-background/src/workers/checkout.worker.ts`
- `moda-interact-background/src/workers/orders.worker.ts`
- `moda-interact-background/src/workers/pending-recovery-candidate.worker.ts`
- `moda-interact-background/tests/unit/runtime/entrypoint-isolation.test.ts`
- `moda-interact-background/tests/unit/runtime/worker-process.test.ts`
- `docs/decisions/background/ARCH-002/BACKGROUND-001-split-worker-entrypoints.md`

### Work Completed

- Added production entrypoints for `moda-shopify-event-worker`,
   `moda-recovery-worker` and `moda-messaging-worker`.
- Added deterministic `npm run start:*` commands for all three production
   entrypoints.
- Kept the combined `npm start` / `npm run dev` local worker entrypoint and its
   liveness server.
- Moved process signal/resource lifecycle ownership out of individual workers
   into a shared process helper. `SIGTERM`/`SIGINT` now close only the process's
   explicitly owned workers, wait for BullMQ graceful `Worker.close()`, then
   close Redis and Prisma resources.
- Added isolation, command mapping, idempotent shutdown, shutdown-failure and
   direct `SIGTERM` tests.
- Documented logical service commands and queue ownership.

### Validation Results

- `npm test -- --run tests/unit/runtime/worker-process.test.ts tests/unit/runtime/entrypoint-isolation.test.ts`
   passed: 2 files, 7 tests.
- `npm test` executed the full suite: 10 files passed, 1 file failed, 1 file
   skipped; 57 tests passed, 1 failed, 2 skipped. The sole failure is the
   pre-existing `recovery-routing.service.test.ts` Prisma mock omitting
   `customerPhone.findMany`; the test/service are clean in Git and outside this
   task's touched paths. No entrypoint/lifecycle test failed.
- `./node_modules/.bin/tsc --noEmit` passed.
- `npm run build` passed, including Prisma Client generation and TypeScript
   production compilation.
- Built command verification passed for `shopify-event`, `recovery` and
   `messaging`: with `REDIS_URL` deliberately absent, each resolved its compiled
   entrypoint, exited nonzero (`1`) and reported
   `REDIS_URL environment variable is required`.
- Entrypoint audit confirmed exact worker imports (2/1/1), no production HTTP
   listener and no remaining worker-local signal/resource shutdown handlers.
- VS Code diagnostics reported no errors in changed source/tests.
- Environment warning: one validation terminal inherited `PATH=tmp`; the
   workspace bootstrap initially could not resolve `tr`. Standard macOS utility
   paths were restored for the command and the workspace-owned bootstrap then
   selected `.nvmrc` Node `24.19.0`; no alternate Node setup was introduced.

### Deviations

None. The full-suite unrelated test failure is recorded under Validation Results
and Unresolved Issues rather than changed outside task scope.

### Assumptions

- BullMQ `Worker.close()` default non-forced behavior is the repository-supported
   graceful in-flight-job drain boundary.
- Redis and Prisma instances imported by an entrypoint are process-local shared
   resources and may be closed after every owned worker has closed.

### Unresolved Issues

- The existing `recovery-routing.service.test.ts` unit-test mock does not provide
   `prisma.customerPhone.findMany`, so the otherwise passing full suite remains
   one test short of green. This task did not modify recovery routing or its test.

### Architectural Concerns

None. Queue names, job names, payload contracts, concurrency values, business
semantics and the current WhatsApp/CommerceAgent boundary are unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation establishes the three ARCH-002 production worker boundaries
required by the architecture:

- `moda-shopify-event-worker` owns the checkout and order Workers;
- `moda-recovery-worker` owns the pending-recovery-candidate Worker;
- `moda-messaging-worker` owns the WhatsApp Worker and therefore the current
  CommerceAgent workflow executed from that Worker.

Each production entrypoint imports only its owned Worker set and does not start
an HTTP listener. Deterministic package commands exist for all three entrypoints.

Process lifecycle ownership is centralized in `startWorkerProcess()`.
`SIGTERM`/`SIGINT` close the explicitly owned BullMQ Workers first using graceful
`Worker.close()` semantics and only then close process Redis/Prisma resources.
The shutdown operation is idempotent and failure-aware.

The combined local-development process is retained separately with its liveness
HTTP server and does not alter the production deployment boundary.

### Reviewed Files

Reviewed the production entrypoints, package scripts, process lifecycle helper,
affected Worker modules, focused lifecycle/isolation tests, README command
mapping and Completion Report.

### Validation Reviewed

Accepted evidence:

- focused entrypoint/lifecycle suite: 7/7 passed;
- TypeScript typecheck passed;
- production build passed;
- compiled command/startup verification passed for all three entrypoints;
- entrypoint isolation audit passed;
- graceful shutdown tests passed.

The full repository suite reported one failure in the untouched
`recovery-routing.service.test.ts` Prisma mock (`customerPhone.findMany`
missing). The task did not change that service/test, while all task-specific
tests, typecheck and build passed. This unrelated pre-existing test condition
does not block acceptance of BACKGROUND-001.

### Architecture Conformance

Conforms.

Queue/job contracts, concurrency values, business semantics and the current
WhatsApp/CommerceAgent boundary remain unchanged. No fourth CommerceAgent
deployment unit was introduced.

### Follow-up

`ARCH-002-BACKGROUND-002` may now become Ready.

The broad `ARCH-002-BACKGROUND-003` must not be handed off. It is superseded by
the granular worker-observability tasks created after this acceptance.

`ARCH-002-BACKGROUND-004` remains an independent Ready prerequisite for the
observability rollout.