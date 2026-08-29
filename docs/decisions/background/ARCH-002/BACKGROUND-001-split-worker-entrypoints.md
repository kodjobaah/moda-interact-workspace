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

# Create independently deployable worker entrypoints

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Expose three independently deployable background worker entrypoints matching ARCH-002 scaling boundaries.

## Context

Accepted discovery found checkout, order, recovery and WhatsApp/CommerceAgent workers all start from one Node process, preventing independent horizontal scaling.

## Scope

Create repository-supported entrypoints/commands for:

1. `moda-shopify-event-worker` — checkout + order workers;
2. `moda-recovery-worker` — pending recovery candidate/materialization worker;
3. `moda-messaging-worker` — WhatsApp + current CommerceAgent workflow.

Preserve existing queue contracts and business behaviour.

Retain a local combined-worker command only if useful for development.

## Out of Scope

- splitting CommerceAgent into a new queue/service;
- changing recovery/order/messaging business semantics;
- Render Blueprint configuration;
- queue contract redesign.

## Requirements

Each production entrypoint must start only its intended worker set.

Do not globally serialize or merge queue concurrency.

Existing worker-level concurrency values may remain repository-local unless a concrete reason requires change.

## Work Items

- [ ] add three production worker entrypoints;
- [ ] expose package scripts/commands;
- [ ] preserve combined dev entrypoint if useful;
- [ ] add startup tests;
- [ ] document queue ownership per entrypoint.

## Interfaces / Contracts

Produces startup commands consumed by GATEWAY-003 and service identities consumed by BACKGROUND-003.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-BACKGROUND-002`
- `ARCH-002-BACKGROUND-003`

## Acceptance Criteria

- [ ] Shopify-event entrypoint starts checkout+order only;
- [ ] recovery entrypoint starts recovery only;
- [ ] messaging entrypoint starts WhatsApp/CommerceAgent only;
- [ ] queue/job contracts are unchanged;
- [ ] existing worker tests remain valid;
- [ ] production build succeeds.

## Validation

- [ ] unit/integration tests;
- [ ] typecheck;
- [ ] production build;
- [ ] command/startup verification.

## Implementation Notes

Do not create a separate CommerceAgent queue boundary in this task.

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
