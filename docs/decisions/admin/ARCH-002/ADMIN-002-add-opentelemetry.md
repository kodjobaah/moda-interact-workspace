---
id: ARCH-002-ADMIN-002
architecture_id: ARCH-002
title: Add OpenTelemetry to admin runtime
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
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

# Add OpenTelemetry to admin runtime

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Add baseline HTTP/database OpenTelemetry instrumentation to the internal admin runtime.

## Context

ARCH-002 deploys the admin service as part of the managed topology and accepted discovery found no OTel implementation.

## Scope

- initialize OpenTelemetry once/early;
- instrument HTTP and relevant client/database operations;
- use canonical resource identity;
- validate failure isolation and data safety.

## Out of Scope

- internal Grafana UI/embedding;
- tenant analytics;
- OTLP infrastructure provisioning.

## Requirements

Use:
`service.namespace=moda-interact`
`service.name=moda-interact-admin`
`deployment.environment.name=<environment>`.

Do not emit admin credentials, auth tokens or cross-tenant sensitive payloads.

## Work Items

- [ ] initialize OTel;
- [ ] add baseline HTTP/client instrumentation;
- [ ] configure resource identity;
- [ ] add failure-isolation validation;
- [ ] validate sensitive data.

## Interfaces / Contracts

Emits OTel/OTLP telemetry consumed by GATEWAY-006.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] correct service identity;
- [ ] telemetry backend failure does not break admin requests;
- [ ] expected baseline telemetry is emitted;
- [ ] prohibited data is absent.

## Validation

- [ ] tests;
- [ ] typecheck/lint as applicable;
- [ ] production build.

## Implementation Notes

Keep telemetry collection separate from any future admin observability presentation task.

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
