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

# Add Messaging Service Health and Readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide deterministic liveness and Redis-aware readiness endpoints for the
Meta/WhatsApp ingress service in test and production.

## Context

Accepted discovery found no health/readiness route in
`moda-interact-messaging`.

The service requires Redis/BullMQ publication for accepted inbound work.

GATEWAY-003 needs concrete health paths rather than inferred routes.

## Scope

Implement:

```text
GET /health
GET /ready
```

`/health` is process liveness.

`/ready` reflects Redis availability required for normal ingress acceptance.

Add tests and document response/status semantics.

## Out of Scope

- Meta webhook processing changes;
- gateway routing;
- Render Blueprint configuration;
- background worker changes;
- Meta/provider health calls;
- returning secret dependency information.

## Requirements

`GET /health`:

- remains cheap;
- performs no Redis or Meta/provider calls;
- succeeds when the process/runtime is healthy;
- returns no secret/tenant data.

`GET /ready`:

- performs a bounded, non-mutating Redis readiness check;
- succeeds when required Redis/BullMQ infrastructure is ready;
- fails predictably when Redis is unavailable;
- performs no Meta/provider calls;
- returns no credential/connection-string details.

The same paths/semantics apply to test and production.

GATEWAY-003 decides infrastructure health-check wiring. This task does not
expose an otherwise private implementation service directly to the public
internet.

## Work Items

- [ ] implement `GET /health`;
- [ ] implement `GET /ready`;
- [ ] add bounded Redis readiness;
- [ ] add success/failure tests;
- [ ] verify liveness performs no dependency/provider work;
- [ ] add sensitive-response validation;
- [ ] document endpoints and status semantics.

## Interfaces / Contracts

Produces:

```text
GET /health
GET /ready
```

consumed by:

```text
ARCH-002-GATEWAY-003
ARCH-002-GATEWAY-004
ARCH-002-SYSTEM-TEST-001
```

Recommended Render deployment-health target:

```text
/ready
```

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] `GET /health` succeeds for a healthy process without external calls;
- [ ] `GET /ready` reflects Redis availability;
- [ ] readiness checks are bounded/non-mutating;
- [ ] no sensitive values are returned;
- [ ] Meta webhook behaviour is unchanged;
- [ ] test and production share the same health/readiness contract.

## Validation

- [ ] tests;
- [ ] typecheck;
- [ ] production build;
- [ ] Redis success/failure tests;
- [ ] liveness no-dependency-call test;
- [ ] sensitive-output review.

## Implementation Notes

Do not perform Meta/provider calls in health checks.

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
