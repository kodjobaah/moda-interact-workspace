---
id: ARCH-002-ADMIN-001
architecture_id: ARCH-002
title: Add admin service health and readiness
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
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

# Add admin service health and readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide liveness and PostgreSQL-aware readiness for the internal admin service.

## Context

Accepted discovery found no health/readiness route in `moda-interact-admin`.

## Scope

- add cheap liveness;
- add PostgreSQL-aware readiness;
- add tests/documentation.

## Out of Scope

- adding a Dockerfile solely for ARCH-002;
- gateway routing;
- admin feature changes;
- database schema changes.

## Requirements

ARCH-002 permits Render native Node runtime for the admin service; absence of a Dockerfile is not itself a blocker.

Health endpoints must not expose internal/admin data or credentials.

## Work Items

- [ ] implement liveness;
- [ ] implement DB-aware readiness;
- [ ] add tests;
- [ ] document endpoints.

## Interfaces / Contracts

Produces HTTP health/readiness routes for GATEWAY-003.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] liveness succeeds for healthy process;
- [ ] readiness reflects PostgreSQL availability;
- [ ] no sensitive/admin data exposed;
- [ ] admin authentication/business behaviour unchanged.

## Validation

- [ ] tests;
- [ ] typecheck/lint as applicable;
- [ ] production build.

## Implementation Notes

Use the repository's existing Next.js/runtime conventions.

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
