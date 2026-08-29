---
id: ARCH-002-BACKGROUND-003
architecture_id: ARCH-002
title: Add OpenTelemetry to background workers
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-BACKGROUND-001
enables: 
  - ARCH-002-GATEWAY-006
created: 2026-08-29
updated: 2026-08-29
---

# Add OpenTelemetry to background workers

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument each ARCH-002 background worker unit with OpenTelemetry, BullMQ telemetry and asynchronous trace-context propagation.

## Context

Accepted discovery found no OTel implementation; BACKGROUND-001 establishes the canonical worker deployment/service identities.

## Scope

- initialize OTel once per worker process;
- instrument BullMQ consumer/producer boundaries as required;
- propagate trace context across queue jobs where architecture-compatible;
- emit job duration/failure/retry/throughput telemetry;
- use worker-specific canonical resource identity;
- validate telemetry failure isolation and data safety.

## Out of Scope

- OTLP backend provisioning;
- changing queue business payload semantics without architect-approved contract work;
- creating a separate CommerceAgent worker.

## Requirements

Resource identities:
`moda-shopify-event-worker`
`moda-recovery-worker`
`moda-messaging-worker`

with:
`service.namespace=moda-interact`
and `deployment.environment.name=<environment>`.

Telemetry backend failure must never fail a BullMQ business job solely because telemetry export failed.

## Work Items

- [ ] initialize OTel in each worker entrypoint;
- [ ] instrument BullMQ execution;
- [ ] add async trace propagation;
- [ ] add bounded job metrics;
- [ ] configure resource identity;
- [ ] add telemetry outage tests;
- [ ] validate sensitive-data handling.

## Interfaces / Contracts

Emits OTel/OTLP telemetry consumed by GATEWAY-006.

## Dependencies

- `ARCH-002-BACKGROUND-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] worker service names are correct;
- [ ] queue/job telemetry is emitted;
- [ ] trace context propagates where required;
- [ ] telemetry outage does not create job failures;
- [ ] retry metrics do not create unbounded cardinality;
- [ ] secrets/customer payloads are not leaked.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test.

## Implementation Notes

Prefer low-cardinality queue/job labels and deterministic correlation identifiers.

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
