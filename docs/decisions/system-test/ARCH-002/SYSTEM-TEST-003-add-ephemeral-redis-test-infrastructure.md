---
id: ARCH-002-SYSTEM-TEST-003
architecture_id: ARCH-002
title: Add isolated ephemeral Redis test infrastructure
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-02T22:19:58Z
attempt: 1
depends_on: []
enables:
  - ARCH-002-SYSTEM-TEST-001
  - ARCH-002-SYSTEM-TEST-002
created: 2026-09-02
updated: 2026-09-02

# Add Isolated Ephemeral Redis Test Infrastructure

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide a reusable, test-owned Redis runtime for Moda integration and system
tests.

Every test execution that needs real Redis/BullMQ semantics must be able to
create its own isolated Redis container, wait for readiness, inject its
connection details into the tested processes, and destroy the container when
the run finishes.

The system-test harness must not depend on developer-local Redis state or a
shared Redis Cloud test instance.

## Architectural Decision

Production remains:

```text
Moda services/workers
    -> Redis Cloud
```

System/integration testing becomes:

```text
system-test run
    -> create isolated ephemeral Redis container
    -> wait for Redis readiness
    -> inject generated REDIS_URL / connection contract
    -> execute real BullMQ/Redis scenarios
    -> stop/remove Redis container
```

The test Redis instance is disposable infrastructure, not durable application
state.

## Scope

Implement reusable Redis test infrastructure in
`moda-interact-system-test`.

The fixture/orchestrator must support:


The implementation may use Testcontainers or an existing repository-owned
Docker orchestration abstraction.

Do not introduce a second orchestration framework if the repository already has
an adequate equivalent.

## Container Requirements

Use an explicitly pinned Redis 7 Alpine image tag.

Do not use:

```text
redis:latest
```

The container must:


A suitable readiness probe is logically:

```text
redis-cli ping
    -> PONG
```

The exact implementation is owned by `moda_system_test`.

## Isolation Requirements

Tests must not silently fall back to:

```text
localhost:6379
developer Redis
shared CI Redis
Redis Cloud
production Redis
```

unless a separate explicitly named test mode is architect-approved.

Each independent run must receive its own Redis instance or otherwise prove
equivalent isolation.

Parallel CI runs must not share:


## BullMQ / Failure-Test Support

The fixture must expose enough lifecycle control for later system tests to
validate:

```text
normal queue operation
Redis unavailable
Redis restarted/recreated
queue state starts clean
```

This task does not itself own all BullMQ business scenarios.

It owns the infrastructure needed by `SYSTEM-TEST-001` and
`SYSTEM-TEST-002` to exercise those scenarios against real Redis semantics.

## Out of Scope


## Work Items

- [x] inspect the current system-test orchestration/runtime;
- [x] choose the smallest compatible container lifecycle mechanism;
- [x] add a pinned Redis 7 Alpine test dependency;
- [x] implement per-run container startup;
- [x] implement bounded readiness;
- [x] expose generated connection details to test processes;
- [x] implement teardown in success/failure paths;
- [x] support explicit stop/outage testing;
- [x] prove two consecutive runs start with clean state;
- [x] prove dynamic-port/no-hardcoded-6379 behavior;
- [x] document CI/Docker prerequisites and lifecycle.


## Validation

At minimum prove:

```text
start
  -> Redis becomes ready

write known key/job marker
  -> visible in current instance

teardown
  -> container removed

new run
  -> previous marker absent

parallel/distinct fixture creation
  -> distinct connection endpoints

forced Redis stop
  -> client/test sees dependency unavailable
```

Run the repository's normal:

```text
tests
typecheck
lint
```

where available.

## Acceptance Criteria

- [x] real Redis/BullMQ tests can use a test-owned container;
- [x] every run starts from isolated Redis state;
- [x] no hardcoded host Redis port is required;
- [x] readiness is bounded and deterministic;
- [x] teardown occurs even when a test fails;
- [x] outage simulation is supported;
- [x] no Redis Cloud or production credential is required;
- [x] parallel runs do not share Redis state;
- [x] no application repository is modified;
- [x] implementation changes are ready for developer commit/push;
- [x] repository agent does not commit or push.


## Completion Report

### Status

Ready for Review

### Files Changed

`src/ephemeral-redis.js`, `test/ephemeral-redis.test.js`, `package.json`, and
`README.md`.

### Work Completed

Implemented a Docker-CLI-backed `EphemeralRedis` fixture using the pinned
`redis:7.4.2-alpine` image. Each fixture generates a unique container name,
maps container port `6379` to host port `0`, waits for bounded `redis-cli ping`
readiness, exposes `REDIS_URL`, supports stop/restart and Redis command
execution for failure tests, and removes the container and volumes during
cleanup. `withEphemeralRedis` guarantees cleanup after callback success or
failure.

Added deterministic tests for lifecycle, dynamic ports, parallel isolation,
outage stop, cleanup, and live marker/state validation. Documented Docker/CI
prerequisites and the test-only Redis contract.

### Validation Results

`npm test`: PASS, 5 passed, 0 failed. With `RUN_LIVE_REDIS_TEST=1`, the live
Docker test created the pinned Redis container, verified readiness, wrote and
read a marker, verified forced-stop unavailability, recreated a new instance
with a clean database, and cleaned up both containers.

`npm run typecheck`: PASS.

`npm run lint`: PASS.

### Deviations

None.

### Assumptions

Docker-compatible container execution is available in the intended integration
test/CI environment.

### Unresolved Issues

No unresolved implementation issues. Docker Engine or a compatible Docker
runtime is required for live fixture use.

### Architectural Concerns

None. No application repository was modified, and no new cross-service or
durable-state contract was introduced.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-SYSTEM-TEST-003` is architect-accepted.

The implementation provides test-owned disposable Redis infrastructure without
depending on developer Redis, shared CI Redis, Redis Cloud or production Redis.

### Fixture Contract Reviewed

The accepted fixture:

```text
EphemeralRedis
  -> docker run redis:7.4.2-alpine
  -> --publish 0:6379
  -> dynamically discover mapped host port
  -> bounded redis-cli ping readiness
  -> expose REDIS_URL
  -> support stop/restart
  -> support redis-cli commands for test assertions
  -> remove container/volumes during cleanup
```

Each fixture receives a UUID-based container identity.

The helper:

```text
withEphemeralRedis(...)
```

wraps startup/callback/cleanup in a `finally` lifecycle.

### Isolation / Failure Support Reviewed

The source and tests cover:

```text
dynamic host port
unique container names
distinct fixture endpoints
bounded readiness
explicit Redis stop
restart support
cleanup after callback success
cleanup after callback failure
fresh-instance state isolation
```

No host port `6379` is required.

The only `6379` value is the Redis container's internal port.

No Redis Cloud or production credential is required.

### Live Redis Evidence Reviewed

The repository-agent Completion Report records an opt-in live Docker run using:

```text
RUN_LIVE_REDIS_TEST=1
```

that successfully:

```text
started the pinned Redis image
waited for PONG
wrote/read a marker
forced Redis unavailable
removed the first container
created a new Redis instance
proved the prior marker absent
cleaned up the new container
```

### Independent Architect Validation

The architect independently ran the repository checks in an environment without
Docker:

```text
npm test
  4 passed
  1 live-Docker test explicitly skipped
  0 failed

npm run typecheck
  PASS

npm run lint
  PASS
```

Docker is not available in the architect review environment, so the live
container scenario was not independently re-executed.

The live scenario is explicitly opt-in and the submitted Completion Report
provides the required Docker execution evidence.

### Architecture Conformance

Accepted.

This task changes only:

```text
moda-interact-system-test
ARCH-002 system-test coordination documentation
```

It introduces no application runtime contract and does not modify production
Redis behavior.

Production remains:

```text
Moda runtime -> Redis Cloud
```

System/integration testing can now use:

```text
test run -> isolated ephemeral Redis container
```

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted system-test changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-SYSTEM-TEST-003` is Complete.

Its dependency edges for:

```text
ARCH-002-SYSTEM-TEST-001
ARCH-002-SYSTEM-TEST-002
```

are satisfied.

Neither downstream task is promoted yet.

`SYSTEM-TEST-001` still directly depends on:

```text
ARCH-002-ADMIN-004
ARCH-002-SYSTEM-TEST-004
```

in addition to already-complete infrastructure prerequisites.

`SYSTEM-TEST-002` still directly depends on:

```text
ARCH-002-SYSTEM-TEST-004
```

plus its already accepted telemetry/infrastructure prerequisites.

No downstream task is automatically started.
