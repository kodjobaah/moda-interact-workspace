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

# Add Admin Service Health and Readiness

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide deterministic process liveness and PostgreSQL-aware readiness endpoints
for the internal `moda-interact-admin` service in both test and production.

## Context

Accepted discovery found no health/readiness route in `moda-interact-admin`.

ARCH-002 permits Render's native Node runtime for the admin application; the
absence of a Dockerfile is not itself a deployment blocker.

GATEWAY-003 requires concrete health paths rather than inferred routes.

## Scope

Implement the operational contract:

```text
GET /health
GET /ready
```

`/health` represents process/runtime liveness.

`/ready` represents bounded PostgreSQL dependency readiness required before the
admin runtime should receive normal internal traffic.

Add tests and document response/status semantics.

## Out of Scope

- adding a Dockerfile solely for ARCH-002;
- gateway routing/base-path implementation;
- fixing the unresolved production `/admin/*` base-path/host-routing contract;
- admin feature/business changes;
- database schema changes;
- returning internal/admin data through health endpoints;
- external provider health calls.

## Requirements

`GET /health`:

- must remain cheap;
- must not query PostgreSQL merely to prove process liveness;
- must not require an authenticated admin session;
- returns success when the runtime process is healthy;
- exposes no admin, tenant or credential information.

`GET /ready`:

- must perform a bounded, non-mutating PostgreSQL readiness check;
- must not query business/admin records merely for readiness;
- must not require an authenticated admin session;
- returns success only when the required database dependency is available;
- returns a predictable non-success status when PostgreSQL is unavailable;
- exposes no connection string, credential, tenant or internal record details.

The same paths and semantics apply in test and production.

Only environment configuration changes between environments.

GATEWAY-003 decides Render health-check wiring and routing. This task does not
make the admin service public.

The operational health routes do not resolve the separate production admin
application route/base-path question.

## Work Items

- [ ] implement `GET /health`;
- [ ] implement `GET /ready`;
- [ ] add bounded PostgreSQL readiness;
- [ ] add success/failure tests;
- [ ] verify health/readiness do not require admin authentication;
- [ ] verify liveness performs no database/provider work;
- [ ] add sensitive-response validation;
- [ ] document endpoint/status semantics.

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

The admin user-facing route/base-path contract remains separate.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [ ] `GET /health` succeeds for a healthy process without PostgreSQL/provider
      calls;
- [ ] `GET /ready` reflects PostgreSQL availability;
- [ ] readiness is bounded and non-mutating;
- [ ] health/readiness routes do not require an admin session;
- [ ] no sensitive/admin/tenant data is returned;
- [ ] admin authentication/business behaviour is unchanged;
- [ ] test and production share the same health/readiness contract;
- [ ] production build succeeds.

## Validation

- [ ] tests;
- [ ] typecheck/lint as applicable;
- [ ] production build;
- [ ] PostgreSQL success/failure tests;
- [ ] liveness no-dependency-call test;
- [ ] unauthenticated operational-route test;
- [ ] sensitive-output review.

## Implementation Notes

Use the repository's existing Next.js/runtime conventions.

Do not solve the gateway/admin base-path concern in this task.

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
