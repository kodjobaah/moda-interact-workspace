---
id: ARCH-006-SHARED-005
architecture_id: ARCH-006
title: Standardise disposable PostgreSQL and Redis integration-test infrastructure
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-006-SHARED-004
enables:
  - ARCH-006-SHARED-006
created: 2026-09-06
updated: 2026-09-06
---
# ARCH-006-SHARED-005: Standardise disposable PostgreSQL and Redis integration-test infrastructure

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Create one reusable Node-only test-support module that starts isolated disposable PostgreSQL and Redis containers on dynamic ports, applies the authoritative Prisma migration chain to the fresh PostgreSQL instance, exposes test connection environment, and always cleans up.

## Context

BACKGROUND-004 required manual creation/configuration of `TEST_DATABASE_URL`. The workspace already contains proven Docker-backed ephemeral PostgreSQL and Redis helpers in `moda-interact-system-test/src/ephemeral-postgres.js` and `src/ephemeral-redis.js`, but application repositories must not depend on the manual-gated system-test repository. The reusable home is therefore the published Shared package under a Node-only testing subpath.

This is integration-test infrastructure, not a system-test scenario. It must not gate BACKGROUND-005 or other product implementation tasks.

## Storage / Ownership

Implement in `moda-interact-shared` under a dedicated Node-only testing boundary, for example:

```text
moda-interact-shared/
  src/testing/
    node.ts
    ...focused helpers/tests...
```

Expose it only through a Node-only package subpath such as:

```text
@modainteract/moda-interact-shared/testing/node
```

Do not import this module from the browser-safe root/shared runtime entrypoints.

## Scope

- disposable PostgreSQL lifecycle with dynamic host port and unique database/credentials;
- disposable Redis lifecycle with dynamic host port;
- bounded readiness checks;
- authoritative Prisma migration deployment to the disposable PostgreSQL database;
- returned connection URLs/environment for consumer integration tests;
- deterministic cleanup on success and failure;
- focused tests for orchestration/error/cleanup behavior.

## Out of Scope

- changing production database migrations;
- `prisma db push`;
- copying migrations into Shared;
- application-specific fixture rows;
- running ARCH-006 system-test scenarios;
- modifying Background/Admin/Shopify repositories;
- requiring a persistent local `moda_interact_test` database;
- production Docker/Render infrastructure.

## Requirements

1. PostgreSQL and Redis must be fresh/disposable per harness run and use dynamically mapped host ports so parallel/CI runs do not require fixed local ports.
2. PostgreSQL starts empty. Before consumer tests run, the harness must execute the real Prisma migration history using `prisma migrate deploy` against a caller-supplied authoritative schema path. The expected consumer path is the repository's database submodule, e.g. `database/prisma/schema.prisma`.
3. The harness must never use `prisma db push`, synthetic DDL, copied migration files, or a schema generated independently from `moda-interact-database`.
4. The caller supplies/controls the Prisma schema path and working directory; Shared must not hard-code a sibling workspace layout.
5. Return enough environment for consumers to set both standard/runtime and test aliases where needed, conceptually:

```text
DATABASE_URL=<ephemeral postgres>
TEST_DATABASE_URL=<ephemeral postgres>
REDIS_URL=<ephemeral redis>
TEST_REDIS_URL=<ephemeral redis>
```

6. If migration deployment fails, do not run consumer tests; surface the migration error and still clean up both containers.
7. Cleanup must run on normal completion and thrown/rejected consumer work.
8. Reuse/adapt the behavior of the existing system-test ephemeral helpers where useful, but do not create an import/dependency from Shared to `moda-interact-system-test`. That repository remains a separate consumer/validation surface.
9. Prefer the smallest implementation that meets the contract. A Testcontainers library may be used only if it remains test-only/Node-only and does not impose an unnecessary production-runtime dependency on ordinary Shared consumers. The existing Docker-CLI approach is acceptable and already proven in this workspace.
10. Do not expose Docker credentials, database passwords or connection URLs in ordinary logs beyond what a local integration-test runner requires.

## Work Items

- [x] Add Node-only disposable PostgreSQL helper.
- [x] Add Node-only disposable Redis helper.
- [x] Add migration-deploy helper accepting caller-supplied schema path/cwd.
- [x] Add one orchestration helper that starts both services, applies migrations, exposes environment and guarantees cleanup.
- [x] Add package build/export wiring for `testing/node` without changing browser-safe entrypoints.
- [x] Add focused unit tests using injected process/Docker runners where possible.
- [x] Add one opt-in/live Docker validation proving fresh PostgreSQL + migrations + Redis readiness + cleanup.

## Interfaces / Contracts

Conceptual API only; exact names are implementation-owned:

```ts
await withDisposableIntegrationInfrastructure(
  {
    prismaSchemaPath,
    cwd,
  },
  async ({ databaseUrl, redisUrl, environment }) => {
    // consumer integration tests
  },
);
```

The migration runner must operate against `databaseUrl` and `prismaSchemaPath` using `migrate deploy`.

## Dependencies

Explicit dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SHARED-006`

## Acceptance Criteria

- [x] One call can create isolated PostgreSQL and Redis endpoints without preconfigured fixed ports.
- [x] A fresh PostgreSQL instance receives the complete authoritative Prisma migration chain before callback/consumer work starts.
- [x] Migration failure aborts consumer execution and both containers are cleaned up.
- [x] Success/failure paths clean up both containers.
- [x] Two parallel harness instances use distinct container identities/endpoints.
- [x] Browser-safe Shared imports do not load Docker/Testcontainers/process-spawn code.
- [x] No production application repository or system-test scenario is modified by this task.

## Validation

Shared build, typecheck, focused tests, package-export validation, one opt-in/live Docker migration run when Docker is available, and `git diff --check`.

## Implementation Notes

Repository agent may inspect the existing `moda-interact-system-test/src/ephemeral-postgres.js` and `ephemeral-redis.js` read-only as prior art. Do not modify that repository in this task.

Luna stop condition: once the reusable Node-only harness and its focused validation are complete, return this task to `review` and STOP. Do not publish a release; SHARED-006 owns publication.

## Completion Report

### Status

Ready for Review.

### Files Changed

 - [moda-interact-shared/src/testing/node.ts](../../../../moda-interact-shared/src/testing/node.ts)
 - [moda-interact-shared/src/testing/node.test.ts](../../../../moda-interact-shared/src/testing/node.test.ts)
 - [moda-interact-shared/package.json](../../../../moda-interact-shared/package.json)
 - [moda-interact-shared/tsup.config.ts](../../../../moda-interact-shared/tsup.config.ts)
 - [moda-interact-shared/scripts/validate-testing-node.mjs](../../../../moda-interact-shared/scripts/validate-testing-node.mjs)
 - [moda-interact-shared/scripts/validate-testing-node-live.mjs](../../../../moda-interact-shared/scripts/validate-testing-node-live.mjs)

### Work Completed

 - Added injectable Docker-backed PostgreSQL and Redis lifecycle helpers with dynamic ports, unique identities, bounded command/readiness checks and forced volume cleanup.
 - Added caller-controlled Prisma `migrate deploy` orchestration and standard/test environment aliases.
 - Added failure-safe orchestration that prevents callback execution after migration failure and cleans both services.
 - Added the Node-only `@modainteract/moda-interact-shared/testing/node` package export without changing browser-safe roots.
 - Added Docker-free focused tests, package export validation, and an opt-in live Docker migration validation.

### Validation Results

 - `npm run typecheck`: passed.
 - `npm test`: 98 passed, 1 existing Redis-dependent test skipped.
 - Focused `src/testing/node.test.ts`: 6 passed.
 - `npm run build`: passed.
 - `npm run validate:testing-node`: passed, including packed-artifact validation.
 - Live validation with `MODA_TEST_PRISMA_SCHEMA_PATH=../moda-interact-database/prisma/schema.prisma` and `MODA_TEST_PRISMA_CWD=../moda-interact-database`: passed.
 - `git diff --check`: passed.

### Deviations

None.

### Assumptions

Docker or a compatible local container runtime is used only for the opt-in/live validation path; unit tests do not require Docker.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Complete

### Decision

`moda_architect` independently reviewed ARCH-006-SHARED-005 Attempt 1 and accepts the implementation.

Accepted evidence:

- reusable infrastructure is implemented only in the Shared Node-only `testing/node` entrypoint and is not re-exported through browser-safe roots;
- disposable PostgreSQL and Redis use unique identities and dynamically assigned host ports;
- PostgreSQL starts empty and migration deployment invokes `prisma migrate deploy` against a caller-supplied schema path and working directory, preserving `moda-interact-database` as the authoritative migration owner;
- no `prisma db push`, copied migration chain, synthetic DDL or dependency on `moda-interact-system-test` was introduced;
- migration failure prevents callback/consumer execution and cleanup is guaranteed through the orchestration `finally` path;
- Docker/process operations have bounded defaults and lifecycle helpers suppress cleanup-only failures without masking the primary failure;
- focused tests cover dynamic endpoints, forced cleanup, caller-controlled migration arguments, migration-failure cleanup and parallel harness identity/endpoints;
- package/export validation proves `@modainteract/moda-interact-shared/testing/node` is emitted and included in the packed artifact;
- the recorded live Docker validation successfully started fresh PostgreSQL and Redis and applied the real database migration chain;
- package source remains at `0.7.1`; publication/versioning is correctly deferred to SHARED-006;
- no application repository or system-test implementation was modified by this task.

SHARED-006 is now Ready. No product implementation task is gated by this quality-infrastructure publication chain.
