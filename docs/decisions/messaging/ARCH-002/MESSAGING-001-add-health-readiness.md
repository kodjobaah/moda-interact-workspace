---
id: ARCH-002-MESSAGING-001
architecture_id: ARCH-002
title: Add messaging service health and readiness
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-02T19:31:18Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-09-02
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

- [x] implement `GET /health`;
- [x] implement `GET /ready`;
- [x] add bounded Redis readiness;
- [x] add success/failure tests;
- [x] verify liveness performs no dependency/provider work;
- [x] add sensitive-response validation;
- [x] document endpoints and status semantics.

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

- [x] `GET /health` succeeds for a healthy process without external calls;
- [x] `GET /ready` reflects Redis availability;
- [x] readiness checks are bounded/non-mutating;
- [x] no sensitive values are returned;
- [x] Meta webhook behaviour is unchanged;
- [x] test and production share the same health/readiness contract.

## Validation

- [x] tests;
- [x] typecheck;
- [x] production build;
- [x] Redis success/failure tests;
- [x] liveness no-dependency-call test;
- [x] sensitive-output review.

## Implementation Notes

Do not perform Meta/provider calls in health checks.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-messaging/app/routes.ts`

`moda-interact-messaging/app/routes/health.ts`

`moda-interact-messaging/app/routes/ready.ts`

`moda-interact-messaging/tests/health-readiness.test.mjs`

`moda-interact-messaging/tests/route-config.test.mjs`

`moda-interact-messaging/README.md`

### Work Completed

Added dependency-free `/health` liveness and bounded Redis-aware `/ready`
readiness routes with stable JSON responses. Production readiness uses
`getRedis().ping()`; tests inject a Redis probe so they do not create a
long-lived ioredis reconnect loop. Added route-module separation coverage,
success/failure/timeout readiness coverage, liveness coverage, and endpoint
documentation.

### Validation Results

`npm test`: passed, 13 tests passed and 1 unrelated trace-continuation test
skipped.

Focused health/readiness tests: passed, 5 tests passed.

`npm run typecheck`: passed.

`npm run build`: passed. Vite emitted existing browser-externalization warnings
for Node dependencies imported by ioredis; client and SSR bundles were generated
successfully.

Sensitive-output review: passed. Health/readiness responses contain only the
documented status values, and no dead-port Redis test remains.

### Deviations

No deviations from the task contract. Real Redis outage/recovery and BullMQ
integration remain system-test concerns as specified by the corrected test
boundary.

### Assumptions

Production `/ready` requires `REDIS_URL` through the existing Redis helper.
Repository-level tests use the injected probe seam and do not require a live
Redis instance.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-MESSAGING-001` is architect-accepted.

Architect inspection of the submitted source confirms the required health and
readiness contract is implemented as separate React Router route modules:

```text
GET /health
  -> app/routes/health.ts

GET /ready
  -> app/routes/ready.ts
```

This avoids the earlier duplicate file-derived React Router route ID.

### Liveness Contract Reviewed

`GET /health`:

- returns HTTP `200`;
- returns only `{"status":"ok"}`;
- sets `Cache-Control: no-store`;
- imports/calls no Redis helper;
- performs no Meta/provider operation.

The liveness path is therefore dependency-free as required.

### Readiness Contract Reviewed

Production `GET /ready` executes:

```text
getRedis().ping()
```

through a bounded readiness helper.

Success returns:

```text
HTTP 200
{"status":"ready"}
```

Failure or timeout returns:

```text
HTTP 503
{"status":"unavailable"}
```

No Redis URL, credential, provider token, exception detail, tenant identifier or
connection information is returned.

The readiness operation is non-mutating.

### Corrected Test Boundary Reviewed

The repository-level tests no longer simulate Redis failure by connecting the
production long-lived ioredis/BullMQ singleton to a deliberately dead TCP port.

The accepted repository-test seam injects a Redis `PING` probe and validates:

```text
successful probe
  -> 200 ready

rejected probe
  -> 503 unavailable

never-settling probe
  -> bounded timeout
  -> 503 unavailable

/health
  -> dependency-free success
```

An unresolved injected Promise does not create an ioredis socket or reconnect
timer, so the Node test runner can terminate normally.

Real Redis connectivity, outage/recovery and BullMQ integration remain owned by:

```text
ARCH-002-SYSTEM-TEST-003
```

which provides isolated ephemeral Redis test infrastructure.

### Route Configuration Reviewed

Architect inspected:

```text
app/routes.ts
app/routes/health.ts
app/routes/ready.ts
tests/route-config.test.mjs
```

The route configuration is:

```text
health -> routes/health.ts
ready  -> routes/ready.ts
```

and no longer maps both URLs to one route module.

The regression test asserts the two routes use distinct route files.

### Existing Redis Runtime Contract

The production Redis helper remains the existing long-lived ioredis connection:

```text
new Redis(REDIS_URL, {
  maxRetriesPerRequest: null
})
```

This task does not weaken or replace the BullMQ-oriented production connection
behavior merely to simplify unit testing.

### Validation Reviewed

The repository agent reports:

```text
focused health/readiness tests
  PASS — 5 tests

npm test
  PASS — 13 tests
  1 unrelated trace-continuation test skipped

npm run typecheck
  PASS

npm run build
  PASS
```

The reported Vite browser-externalization warnings did not prevent generation
of the client and SSR bundles.

Architect source inspection also confirms the previously problematic dead-port
test:

```text
redis://127.0.0.1:1
```

is absent from the final health/readiness test.

### Architecture Conformance

Accepted.

The final boundary is:

```text
repository tests
  -> deterministic injected Redis probe

production readiness
  -> real getRedis().ping()

architecture/system tests
  -> real ephemeral Redis container
```

The task stayed within `moda-interact-messaging` ownership and did not modify
gateway routing, Render infrastructure, background workers or Meta provider
health behavior.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted Messaging changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-MESSAGING-001` is Complete.

Its direct dependency edge for:

```text
ARCH-002-GATEWAY-003
```

is satisfied.

With `GATEWAY-005`, `GATEWAY-007` and `MESSAGING-001` now accepted, the only
remaining unresolved direct prerequisite for `ARCH-002-GATEWAY-003` is:

```text
ARCH-002-ADMIN-001
```

`GATEWAY-003` remains Pending until that task is architect-accepted Complete.

No downstream task is automatically started.
