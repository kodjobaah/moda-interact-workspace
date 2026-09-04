---
id: ARCH-002-SYSTEM-TEST-005
architecture_id: ARCH-002
title: Add isolated ephemeral PostgreSQL test infrastructure
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 32
executor: copilot
claimed_at: 2026-09-03T08:12:07Z
attempt: 2
depends_on: []
enables:
  - ARCH-002-SYSTEM-TEST-002
created: 2026-09-03
updated: 2026-09-03
---

# Add Isolated Ephemeral PostgreSQL Test Infrastructure

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Provide a reusable, test-owned PostgreSQL runtime for deterministic local
integration/system tests that need the same database dependency class present in
the Render test and production topologies.

The immediate consumer is `ARCH-002-SYSTEM-TEST-002`, whose Admin production
bootstrap validation must exercise a reachable PostgreSQL dependency instead of
treating an absent developer-local database as representative of production.

Every test execution that needs real PostgreSQL semantics must be able to create
its own isolated PostgreSQL container, wait for readiness, obtain an injected
`DATABASE_URL`, execute the test callback, and destroy the container even when
the callback fails.

## Architectural Decision

Deployed environments remain unchanged:

```text
Render test
  -> moda-interact-postgres-test

Render production
  -> production Render PostgreSQL
```

The deterministic local system-test harness becomes:

```text
system-test run
    -> isolated ephemeral Redis
    -> isolated ephemeral PostgreSQL
    -> WhatsApp Cloud API emulator
    -> launch tested Moda processes with generated dependency URLs
    -> execute deterministic integration evidence
    -> teardown all disposable dependencies
```

`SYSTEM-TEST-005` is specifically the local deterministic PostgreSQL fixture.
It does **not** replace the Render PostgreSQL resource used by
`SYSTEM-TEST-001` when validating the deployed test topology.

The database is disposable test infrastructure, not durable application state.

## Required Reading Before Implementation

The assigned `moda_system_test` agent must read:

1. this task;
2. `docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`;
3. `SYSTEM-TEST-003-add-ephemeral-redis-test-infrastructure.md`;
4. `SYSTEM-TEST-004-add-whatsapp-cloud-api-emulator.md`;
5. the current `moda-interact-system-test` repository instructions and
   `package.json`;
6. the existing PostgreSQL helper/script(s), including
   `scripts/start-postgres-docker.sh`, where present.

Reuse the repository's existing Docker/container lifecycle conventions. Do not
introduce a second orchestration framework merely for PostgreSQL when the
existing Docker-CLI approach is adequate.

## Scope

Implement a reusable ephemeral PostgreSQL fixture in
`moda-interact-system-test`.

A suitable public test helper contract is logically equivalent to:

```text
EphemeralPostgres
  start()
  stop()/cleanup()
  connection details
  databaseUrl

withEphemeralPostgres(callback)
```

Exact filenames/API names are owned by `moda_system_test`, but the fixture must
be reusable by later ARCH-002 system-test scenarios rather than being embedded
only inside one test file.

## PostgreSQL Version Contract

Match the ARCH-002 PostgreSQL major-version contract used by the Render
environments: PostgreSQL 17.

The implementation must pin an explicit PostgreSQL 17 image tag. Do not use:

```text
postgres:latest
```

and do not silently use a different major version.

Record the exact selected image tag in the Completion Report and README.

## Lifecycle and Isolation Requirements

Each fixture instance must:

- create a unique container name;
- avoid requiring host port `5432`;
- use a dynamically allocated host port;
- create an isolated test database/user credential set;
- expose a complete PostgreSQL connection URL suitable for `DATABASE_URL`;
- wait for bounded PostgreSQL readiness before returning from `start()`;
- fail clearly when readiness is not reached within the configured timeout;
- remove the container and disposable volumes/state during cleanup;
- clean up after both callback success and callback failure;
- support consecutive runs with clean state;
- support parallel fixture instances without sharing ports or database state.

Tests must not silently fall back to:

```text
localhost:5432
an already-running developer PostgreSQL
shared CI PostgreSQL
Render test PostgreSQL
production PostgreSQL
```

A developer may explicitly opt into an externally managed database only if a
future task defines a separately named mode. This task's default contract is
isolated ephemeral PostgreSQL.

## Readiness

Use a bounded readiness probe that proves the server accepts database
connections. A suitable logical probe is:

```text
pg_isready
    +
optional bounded SELECT 1
```

Do not consider container-process existence alone to be database readiness.

## Consumer Environment Contract

The fixture must expose enough information for a consuming test runner to launch
Moda processes with at least:

```text
DATABASE_URL=<generated ephemeral PostgreSQL URL>
```

If additional values are exposed, keep them test-only and bounded, for example:

```text
host
port
database
user
password
containerName
```

The generated `databaseUrl` / `environment.DATABASE_URL` is the consumer-process
connection contract. Live validation must prove that a process outside the
container can connect through that URL and execute bounded `SELECT 1`.

Do not place any production or Render credential in the fixture or committed
test configuration.

## Schema / Migration Boundary

This task owns PostgreSQL lifecycle, not application schema ownership.

The fixture should make it possible for a consumer to execute the owning
repository's normal migration/schema-initialisation command when a scenario
requires application tables. Do not copy Prisma schema definitions or implement
a competing migration path inside `moda-interact-system-test`.

For the immediate ADMIN-009/SYSTEM-TEST-002 readiness path, a reachable
PostgreSQL server is sufficient because the Admin readiness boundary performs a
bounded connectivity query.

## SYSTEM-TEST-002 Integration Boundary

This task **enables** but does not complete `SYSTEM-TEST-002`.

After architect acceptance of `SYSTEM-TEST-005`, the existing blocked
`SYSTEM-TEST-002` task must consume this fixture so its Admin validation runs
with a generated reachable `DATABASE_URL`.

The expected successful-path evidence then becomes:

```text
ephemeral PostgreSQL ready
    -> Admin production bootstrap starts with DATABASE_URL
    -> Admin readiness database operation succeeds
    -> readiness returns the healthy path
    -> Prisma instrumentation emits Prisma span evidence
```

`SYSTEM-TEST-002` must not require third-party Prisma instrumentation to expose
the literal SQL string `SELECT 1`; that separate validation-contract correction
is recorded in `ARCH-002-ADMIN-009`.

Do not modify the existing `SYSTEM-TEST-002` runner as part of this task unless
this task explicitly needs a tiny compile/test fixture adapter. Integration of
the accepted fixture into the integrated scenario remains work inside the
existing `SYSTEM-TEST-002` task when it resumes.

## Out of Scope

- changing Render PostgreSQL resources;
- modifying `render.test.yaml` or `render.production.yaml`;
- changing application Prisma schemas or migrations;
- modifying Admin observability/runtime implementation;
- changing `SYSTEM-TEST-001` dependencies;
- using production customer data;
- adding PostgreSQL infrastructure to application repositories;
- changing production database credentials or connection pooling.

## Work Items

- [x] inspect current system-test Docker/container conventions;
- [x] inspect the existing PostgreSQL startup helper and avoid duplicating useful
      behaviour blindly;
- [x] choose and document an explicit PostgreSQL 17 container image tag;
- [x] implement reusable per-run PostgreSQL lifecycle;
- [x] implement unique container naming and dynamic host port allocation;
- [x] implement bounded readiness;
- [x] expose generated `DATABASE_URL`/connection details;
- [x] guarantee teardown after success and failure;
- [x] prove consecutive runs start with clean state;
- [x] prove parallel/distinct fixtures use isolated endpoints/state;
- [x] document Docker/CI prerequisites and the fixture contract;
- [x] add focused tests without weakening or replacing existing Redis/WhatsApp
      fixtures.

## Validation

At minimum prove:

```text
start
  -> PostgreSQL becomes ready

- [x] prove a consumer process can connect through the generated host
  -> bounded SELECT 1 succeeds

write known test marker/state
  -> visible in current instance

live validation proves the generated `DATABASE_URL` works from outside the container
  -> bounded SELECT 1 succeeds

teardown
  -> container removed

new run
  -> previous state absent

parallel/distinct fixture creation
  -> distinct endpoints and isolated state

callback throws
  -> fixture still cleaned up
```

Run the repository-defined validation applicable to the changed files. Inspect
`package.json` before choosing commands; do not assume every repository has the
same scripts.

Where live Docker validation is opt-in, provide and document an explicit test
environment switch analogous to the existing Redis fixture rather than making
ordinary unit tests depend silently on Docker.

## Acceptance Criteria

- [x] real PostgreSQL integration tests can use a test-owned PostgreSQL 17
  container;
- [x] every run starts from isolated PostgreSQL state;
- [x] no hardcoded host port 5432 is required;
- [x] a generated `DATABASE_URL` is exposed to consumer processes;
- [x] readiness is bounded and verifies database connectivity;
- [x] teardown occurs even when a consuming test fails;
- [x] consecutive runs do not retain previous database state;
- [x] parallel fixture instances do not share state/endpoints;
- [x] no developer, Render test or production PostgreSQL credential is required;
- [x] application schema/migration ownership is not duplicated;
- [x] `SYSTEM-TEST-001` deployed-Render PostgreSQL validation remains unchanged;
- [x] no application repository is modified;
- [x] implementation changes are ready for developer commit/push;
- [x] repository agent does not commit or push.

## Architect Correction Request — Attempt 2

The attempt-1 fixture implementation is structurally accepted and must be preserved.
The missing evidence is narrower than the implementation itself.

The live PostgreSQL validation currently performs SQL using:

```text
docker exec <postgres-container> psql ...
```

That proves the server is healthy *inside* the PostgreSQL container, but it does
not prove the fixture's generated host `DATABASE_URL` is usable by a consumer
process outside the container. `ARCH-002-SYSTEM-TEST-002` launches Admin as such
a consumer and therefore depends on the published host endpoint, not on
container-local `psql`.

For attempt 2, make only the smallest correction necessary to prove:

```text
EphemeralPostgres.start()
    -> generated postgres.databaseUrl
    -> test process connects through that URL
    -> bounded SELECT 1 succeeds
```

Requirements:

- preserve the existing PostgreSQL 17 image, lifecycle, dynamic port, unique
  credentials, cleanup, clean-state and parallel-isolation behaviour;
- preserve `databaseUrl` / `environment.DATABASE_URL` as the consumer contract;
- add a live test that uses the generated `DATABASE_URL` from outside the
  PostgreSQL container and executes a bounded `SELECT 1`;
- using `docker exec ... psql` may remain useful for container-side fixture
  diagnostics or marker setup, but it must not be the only proof of the consumer
  connection contract;
- if a PostgreSQL client library is needed for the test process, add only the
  smallest system-test-owned development dependency needed and update the lock
  file normally; do not copy application Prisma schema/runtime ownership into
  this repository;
- keep live Docker validation opt-in and bounded;
- rerun repository validation and the live PostgreSQL fixture validation;
- do not modify `SYSTEM-TEST-002` as part of this correction; it remains blocked
  until this task is architect-accepted Complete.

Additional Work Item:

- [x] prove a consumer process can connect through the generated host
      `DATABASE_URL` and execute bounded `SELECT 1`.

Additional Acceptance Criterion:

- [x] live validation proves the generated `DATABASE_URL` works from outside the
      PostgreSQL container, matching the consumer boundary used by Admin.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-system-test/src/ephemeral-postgres.js`,
`moda-interact-system-test/test/ephemeral-postgres.test.js`, and
`moda-interact-system-test/package.json`,
`moda-interact-system-test/package-lock.json`, and
`moda-interact-system-test/README.md`.

### Work Completed

Implemented the reusable Docker-CLI-backed `EphemeralPostgres` fixture with
the pinned `postgres:17.6-alpine` image. It generates unique container and
database credentials, maps port 5432 through Docker's dynamic host-port
allocation, waits for bounded `pg_isready` readiness, exposes a generated
`DATABASE_URL`, provides bounded container-side `psql` checks, and guarantees
cleanup after successful or failing callbacks. Focused tests cover lifecycle,
SQL readiness, clean consecutive state, parallel isolation, and opt-in live
Docker validation. Attempt 2 adds the smallest test-only `pg@8.16.3`
dependency and uses `pg.Client` from the test process to connect through the
generated host `DATABASE_URL` and execute bounded `SELECT 1`. The existing
static startup helper and deployed topology were left unchanged.

### Validation Results

`npm test` — pass, 14 tests passed and 2 existing opt-in Redis/PostgreSQL tests
skipped.
`npm run typecheck` — pass.
`npm run lint` — pass.
`RUN_LIVE_POSTGRES_TEST=1 node --test test/ephemeral-postgres.test.js` — pass,
5/5; the pinned PostgreSQL container became ready, an external `pg.Client`
connected through the generated host `DATABASE_URL` and completed bounded
`SELECT 1`, the marker was stored, the container was cleaned up, and the next
run started without the marker.

### Deviations

The fixture retains container-side `psql` for infrastructure marker assertions;
the live test independently proves the generated host `DATABASE_URL` as the
consumer-process contract.

### Assumptions

Docker Engine or a compatible Docker runtime is required for live validation.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted. The fixture preserves the architect-approved PostgreSQL
17 lifecycle and now proves the missing consumer boundary with an external
`pg.Client` connection through the generated host `DATABASE_URL` and bounded
`SELECT 1`. The `pg@8.16.3` dependency is test-only and does not introduce
application schema or Prisma ownership into the system-test repository.

The agent-recorded validation is accepted: the live PostgreSQL fixture passed
5/5, the full repository suite reported 14 passes with 2 explicit opt-in skips,
and typecheck/lint passed. The architect environment used for this review does
not provide Docker and exposes Node 22 rather than this repository's Node 24+
contract, so the live run was not redundantly re-executed here; actual changed
code and recorded evidence were inspected directly.
