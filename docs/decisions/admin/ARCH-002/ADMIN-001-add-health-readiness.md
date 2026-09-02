---
id: ARCH-002-ADMIN-001
architecture_id: ARCH-002
title: Add admin service health and readiness
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-02T20:25:41Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-09-02
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

- [x] implement `GET /health`;
- [x] implement `GET /ready`;
- [x] add bounded PostgreSQL readiness;
- [x] add success/failure tests;
- [x] verify health/readiness do not require admin authentication;
- [x] verify liveness performs no database/provider work;
- [x] add sensitive-response validation;
- [x] document endpoint/status semantics.

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

- [x] `GET /health` succeeds for a healthy process without PostgreSQL/provider
      calls;
- [x] `GET /ready` reflects PostgreSQL availability;
- [x] readiness is bounded and non-mutating;
- [x] health/readiness routes do not require an admin session;
- [x] no sensitive/admin/tenant data is returned;
- [x] admin authentication/business behaviour is unchanged;
- [x] test and production share the same health/readiness contract;
- [x] production build succeeds.

## Validation

- [x] tests;
- [x] typecheck/lint as applicable;
- [x] production build;
- [x] PostgreSQL success/failure tests;
- [x] liveness no-dependency-call test;
- [x] unauthenticated operational-route test;
- [x] sensitive-output review.

## Implementation Notes

Use the repository's existing Next.js/runtime conventions.

Do not solve the gateway/admin base-path concern in this task.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-admin/src/app/health/route.ts`

`moda-interact-admin/src/app/ready/route.ts`

`moda-interact-admin/src/lib/health/readiness.ts`

`moda-interact-admin/tests/security/admin-health-readiness.test.mjs`

`moda-interact-admin/tests/security/admin-security-boundary.test.mjs`

`moda-interact-admin/README.md`

### Work Completed

Added dependency-free `/health` liveness and bounded PostgreSQL-aware `/ready`
readiness routes. Production readiness performs a non-mutating `SELECT 1`
through Prisma; tests validate the injectable database probe contract without
requiring PostgreSQL. Both routes remain outside admin authentication and
return only bounded status JSON. Added readiness success/failure/timeout
coverage, liveness and unauthenticated-route checks, sensitive-output checks,
and endpoint documentation.

### Validation Results

`npm test`: passed, 24 tests passed, including executable `/health` liveness and
readiness success, failure, and bounded-timeout probe evidence.

Focused health/readiness and security tests: passed, 12 tests passed.

The executable readiness checks use injected probes and verify `200
{"status":"ready"}`, `503 {"status":"unavailable"}`, and bounded handling of
a never-settling probe without requiring PostgreSQL.

`npm run lint`: passed with no warnings.

`npm run prisma:validate`: passed.

`npm run build`: passed, including Next.js TypeScript validation and route
generation for `/health` and `/ready`. Next.js emitted an existing warning about
multiple lockfiles and inferred workspace root; it did not affect the build.

Sensitive-output review: passed. Operational responses expose only documented
status values and no credentials, connection strings, tenant data, or admin
data.

Repository agent did not commit or push; changes are ready for developer-owned
VCS publication.

### Deviations

No deviations from the task contract. The repository has no standalone
typecheck script; the production build performed Next.js TypeScript validation.

### Assumptions

Production `/ready` requires the existing Prisma configuration and
`DATABASE_URL`. Repository tests use the injected probe seam and do not require
PostgreSQL.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-ADMIN-001` is architect-accepted.

The previously requested behavioral validation correction has been completed.

Architect inspection confirms the runtime contract:

```text
GET /health
  -> dependency-free liveness
  -> HTTP 200
  -> {"status":"ok"}

GET /ready
  -> prisma.$queryRaw`SELECT 1`
  -> bounded PostgreSQL readiness
  -> HTTP 200 {"status":"ready"} on success
  -> HTTP 503 {"status":"unavailable"} on failure or timeout
```

The routes remain outside the protected Admin route group and do not require a
platform-admin session.

### Behavioral Validation Independently Re-run

Architect independently executed:

```text
node --test tests/security/admin-health-readiness.test.mjs
```

against the submitted repository bundle.

Result:

```text
tests 5
pass 5
fail 0
```

The focused suite executes the real liveness route and the actual
`createReadinessResponse()` helper.

It proves:

```text
successful probe
  -> 200
  -> {"status":"ready"}
  -> probe invoked once

rejected probe
  -> 503
  -> {"status":"unavailable"}
  -> probe invoked once

never-settling probe
  -> bounded completion
  -> 503
  -> {"status":"unavailable"}
  -> probe invoked once

GET /health
  -> 200
  -> {"status":"ok"}
```

The source-level guards additionally verify that liveness does not import/call
Prisma, authentication or provider dependencies and that operational responses
do not expose sensitive values.

### Production Dependency Path Reviewed

The production `/ready` route remains:

```text
createReadinessResponse(
  () => prisma.$queryRaw`SELECT 1`
)
```

The injected probe seam is used only to make repository tests deterministic.

No real PostgreSQL instance is required for repository-level behavioral tests.

### Completion Report Reviewed

The repository agent reports:

```text
npm test
  PASS — 24 tests

focused health/readiness + security
  PASS — 12 tests

npm run lint
  PASS

npm run prisma:validate
  PASS

npm run build
  PASS
```

The repository has no separate typecheck script; the Next.js production build
performs TypeScript validation.

The existing Next.js multiple-lockfile/workspace-root warning is unrelated to
the bounded health/readiness task and did not prevent the build.

### Architecture Conformance

Accepted.

The Admin operational contract is now concrete for Render/gateway consumption:

```text
liveness target:
  /health

recommended deployment readiness target:
  /ready
```

`/ready` is bounded, dependency-specific and non-mutating.

No gateway routing, authentication behavior, database schema or Admin business
functionality was changed by this task.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted Admin changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-ADMIN-001` is Complete.

This satisfies the final known unresolved direct dependency edge for:

```text
ARCH-002-GATEWAY-003
```

Based on the currently accepted dependency graph, all declared direct
prerequisites of `GATEWAY-003` are now Complete.

`GATEWAY-003` is not automatically promoted in this acceptance overlay.
`moda_architect` must inspect the authoritative current `GATEWAY-003` task file
before changing its state from Pending to Ready.

No downstream task is automatically started.
