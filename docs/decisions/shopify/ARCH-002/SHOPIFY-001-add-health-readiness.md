---
id: ARCH-002-SHOPIFY-001
architecture_id: ARCH-002
title: Add Shopify service health and readiness
domain: shopify
repository: moda-interact
assigned_agent: moda_app
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

# Add Shopify service health and readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide cheap liveness and dependency-aware readiness endpoints suitable for Render private-service deployment of `moda-interact`.

## Context

The accepted gateway discovery found no dedicated health/readiness route in the Shopify application.

## Scope

- add a cheap liveness endpoint;
- add dependency-aware readiness for required runtime dependencies;
- keep health routes outside merchant business workflows;
- document response semantics and status codes.

## Out of Scope

- gateway/reverse-proxy configuration;
- Render Blueprint changes;
- changing Shopify webhook business behaviour;
- database schema changes.

## Requirements

Liveness must not require expensive provider calls.

Readiness must reflect dependencies required for safe request handling, at minimum PostgreSQL and Redis where the application requires them.

Health endpoints must not expose secrets, tenant data or provider credentials.

## Work Items

- [ ] implement liveness endpoint;
- [ ] implement dependency-aware readiness;
- [ ] add focused tests;
- [ ] document semantics;
- [ ] verify no business/provider work is performed by liveness.

## Interfaces / Contracts

Produces HTTP health/readiness routes consumed by the Render topology.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] liveness returns success when the process is healthy;
- [ ] readiness fails predictably when a required dependency is unavailable;
- [ ] responses expose no sensitive data;
- [ ] normal Shopify routes are unchanged;
- [ ] tests cover success and dependency failure.

## Validation

- [ ] unit/integration tests;
- [ ] typecheck;
- [ ] production build.

## Implementation Notes

Use repository-local conventions. Do not add gateway behaviour here.

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
