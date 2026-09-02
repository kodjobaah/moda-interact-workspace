---
id: ARCH-002-SYSTEM-TEST-003
architecture_id: ARCH-002
title: Add isolated ephemeral Redis test infrastructure
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-002-SYSTEM-TEST-001
  - ARCH-002-SYSTEM-TEST-002
created: 2026-09-02
updated: 2026-09-02
---

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

- container creation;
- deterministic readiness checking;
- dynamic host-port allocation;
- generated per-run Redis connection details;
- test-process environment injection;
- explicit outage simulation;
- teardown after successful and failed tests;
- parallel test-run isolation;
- actionable Docker/runtime preflight failures.

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

- have no persistent host volume;
- have no shared application/test data directory;
- use a unique container identity per test run;
- use a dynamically mapped host port rather than assuming host port `6379`;
- become usable only after a bounded Redis health/readiness probe succeeds;
- be removable without manual cleanup.

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

- Redis container identity;
- mapped host port;
- database contents;
- BullMQ keys/jobs;
- delayed/retry state.

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

- modifying Shopify, Messaging, Background or Gateway application code;
- replacing production Redis Cloud;
- changing queue names or payload contracts;
- implementing business-worker tests owned by another task;
- retaining Redis state after the test run;
- using production/customer data.

## Work Items

- [ ] inspect the current system-test orchestration/runtime;
- [ ] choose the smallest compatible container lifecycle mechanism;
- [ ] add a pinned Redis 7 Alpine test dependency;
- [ ] implement per-run container startup;
- [ ] implement bounded readiness;
- [ ] expose generated connection details to test processes;
- [ ] implement teardown in success/failure paths;
- [ ] support explicit stop/outage testing;
- [ ] prove two consecutive runs start with clean state;
- [ ] prove dynamic-port/no-hardcoded-6379 behavior;
- [ ] document CI/Docker prerequisites and lifecycle.

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

- [ ] real Redis/BullMQ tests can use a test-owned container;
- [ ] every run starts from isolated Redis state;
- [ ] no hardcoded host Redis port is required;
- [ ] readiness is bounded and deterministic;
- [ ] teardown occurs even when a test fails;
- [ ] outage simulation is supported;
- [ ] no Redis Cloud or production credential is required;
- [ ] parallel runs do not share Redis state;
- [ ] no application repository is modified;
- [ ] implementation changes are ready for developer commit/push;
- [ ] repository agent does not commit or push.

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

Docker-compatible container execution is available in the intended integration
test/CI environment.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending
