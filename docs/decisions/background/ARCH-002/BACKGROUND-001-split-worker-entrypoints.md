---
id: ARCH-002-BACKGROUND-001
architecture_id: ARCH-002
title: Create independently deployable worker entrypoints
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-001
enables:
  - ARCH-002-BACKGROUND-002
  - ARCH-002-BACKGROUND-003
created: 2026-08-29
updated: 2026-08-29
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

- [ ] add the three production worker entrypoints;
- [ ] expose deterministic package scripts/commands;
- [ ] preserve a combined development entrypoint if useful;
- [ ] ensure each production entrypoint imports/starts only its owned workers;
- [ ] implement graceful shutdown for each production entrypoint;
- [ ] add startup/isolation tests;
- [ ] add shutdown tests where practical;
- [ ] document queue ownership and command mapping per entrypoint.

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

- [ ] Shopify-event entrypoint starts checkout + order workers only;
- [ ] recovery entrypoint starts recovery worker only;
- [ ] messaging entrypoint starts WhatsApp/current CommerceAgent workflow only;
- [ ] each production command is usable by both test and production deployment;
- [ ] terminating one worker process closes only that process's owned workers and
      resources;
- [ ] queue/job contracts are unchanged;
- [ ] no new CommerceAgent queue/service boundary is introduced;
- [ ] existing worker tests remain valid;
- [ ] production build succeeds.

## Validation

- [ ] unit/integration tests;
- [ ] typecheck;
- [ ] production build;
- [ ] command/startup verification;
- [ ] entrypoint isolation verification;
- [ ] graceful-shutdown verification where practical.

## Implementation Notes

Do not create a separate CommerceAgent queue boundary in this task.

The target Render shape is multiple deployments of the same repository with
different worker start commands, not a single monolithic worker process.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
