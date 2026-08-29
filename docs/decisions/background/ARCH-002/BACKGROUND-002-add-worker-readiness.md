---
id: ARCH-002-BACKGROUND-002
architecture_id: ARCH-002
title: Add worker dependency readiness
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-BACKGROUND-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Add worker dependency readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide an operational readiness mechanism for each independently deployable worker unit.

## Context

Discovery found only simple process liveness and no Redis/PostgreSQL dependency readiness; BACKGROUND-001 changes deployment units.

## Scope

- define a shared readiness implementation for worker entrypoints;
- verify Redis readiness for all workers;
- verify PostgreSQL readiness where required;
- expose/record liveness/readiness in a form usable by infrastructure/system validation;
- add tests.

## Out of Scope

- Render Blueprint configuration;
- business queue processing changes;
- observability backend configuration.

## Requirements

Readiness checks must be bounded and must not mutate business state.

Failure of a dependency should be observable without leaking credentials.

Do not require provider API calls for readiness.

## Work Items

- [ ] implement shared worker readiness;
- [ ] wire it to all production worker units;
- [ ] add dependency-failure tests;
- [ ] document operational semantics.

## Interfaces / Contracts

Produces readiness behaviour consumed by GATEWAY-003/004 and system testing.

## Dependencies

- `ARCH-002-BACKGROUND-001`

## Enables

None.

## Acceptance Criteria

- [ ] Redis unavailability is reflected;
- [ ] PostgreSQL unavailability is reflected where applicable;
- [ ] checks are bounded/non-mutating;
- [ ] no secrets exposed;
- [ ] each worker unit has a usable readiness signal.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build.

## Implementation Notes

The exact delivery mechanism may be HTTP or another architecture-compatible worker health mechanism; keep it consistent across worker entrypoints.

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
