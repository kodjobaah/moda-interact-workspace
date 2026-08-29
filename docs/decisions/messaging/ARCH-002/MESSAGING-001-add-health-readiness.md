---
id: ARCH-002-MESSAGING-001
architecture_id: ARCH-002
title: Add messaging service health and readiness
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Add messaging service health and readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide liveness and Redis-aware readiness endpoints for the Meta/WhatsApp ingress service.

## Context

Accepted discovery found no health/readiness route in `moda-interact-messaging`, which depends on Redis to publish inbound work.

## Scope

- add cheap liveness;
- add readiness for Redis dependency;
- add tests and document semantics.

## Out of Scope

- Meta webhook processing changes;
- gateway routing;
- Render Blueprint;
- background worker changes.

## Requirements

Liveness must remain cheap.

Readiness must fail predictably when Redis is unavailable.

No secret/token values may be exposed.

## Work Items

- [ ] implement liveness;
- [ ] implement Redis-aware readiness;
- [ ] add tests;
- [ ] document endpoints.

## Interfaces / Contracts

Produces HTTP health/readiness routes consumed by GATEWAY-003.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] liveness succeeds for a healthy process;
- [ ] readiness reflects Redis availability;
- [ ] no sensitive values are returned;
- [ ] Meta webhook behaviour is unchanged.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build.

## Implementation Notes

Do not perform Meta provider calls in health checks.

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
