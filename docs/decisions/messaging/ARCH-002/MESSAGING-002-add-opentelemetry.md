---
id: ARCH-002-MESSAGING-002
architecture_id: ARCH-002
title: Add OpenTelemetry to Meta ingress
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: 
  - ARCH-002-GATEWAY-006
created: 2026-08-29
updated: 2026-08-29
---

# Add OpenTelemetry to Meta ingress

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument Meta/WhatsApp HTTP ingress and queue publication with OpenTelemetry and correlation propagation.

## Context

Accepted discovery found no OpenTelemetry implementation in the messaging ingress.

## Scope

- initialize OpenTelemetry once/early;
- instrument inbound HTTP handling and Redis/BullMQ publication where supported;
- emit bounded acceptance/failure/latency telemetry;
- use canonical resource identity;
- validate failure isolation and sensitive-data handling.

## Out of Scope

- OTLP backend provisioning;
- background consumer instrumentation;
- tenant-facing analytics.

## Requirements

Use:
`service.namespace=moda-interact`
`service.name=moda-interact-messaging`
`deployment.environment.name=<environment>`.

Telemetry failure must not fail valid Meta webhook processing.

Do not record Meta access tokens, authorization headers or complete inbound payloads by default.

## Work Items

- [ ] initialize OTel;
- [ ] instrument HTTP ingress;
- [ ] instrument/propagate queue publication context where required;
- [ ] add resource identity;
- [ ] add failure-isolation tests;
- [ ] validate sensitive data.

## Interfaces / Contracts

Emits OTel/OTLP telemetry consumed by GATEWAY-006 infrastructure.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] service identity is correct;
- [ ] ingress telemetry is emitted;
- [ ] backend outage does not break ingress;
- [ ] context propagation works where required;
- [ ] secrets/payloads are not leaked.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test.

## Implementation Notes

Keep application instrumentation backend-neutral.

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
