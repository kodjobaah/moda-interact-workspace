---
id: ARCH-006-BACKGROUND-008
architecture_id: ARCH-006
title: Adopt disposable integration-test infrastructure in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 80
executor: copilot
claimed_at: 2026-09-06T17:22:58Z
attempt: 1
depends_on:
  - ARCH-006-BACKGROUND-004
  - ARCH-006-SHARED-006
enables: []
created: 2026-09-06
updated: 2026-09-06T17:30:00Z
---

# ARCH-006-BACKGROUND-008: Adopt disposable integration-test infrastructure in Background
## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Make Background integration tests self-provision a fresh migrated PostgreSQL database and Redis instance through the published Shared testing harness, removing the normal requirement for manually configured `TEST_DATABASE_URL`/`TEST_REDIS_URL`.

## Context
## Out of Scope

- translation production behavior;
- provider submission/poll/reconciliation implementation;
- database schema/migrations;
- Shared implementation/publication;
- system-test scenarios;
- production Docker/Render infrastructure.

## Requirements

1. Pin the exact Shared release accepted from SHARED-006.
2. Add a bounded Background integration-test entrypoint/script that starts the Shared disposable PostgreSQL + Redis harness, points it at the authoritative database submodule schema (`database/prisma/schema.prisma` or equivalent resolved path), applies `prisma migrate deploy`, then runs the selected Vitest integration slice in a child process/environment where connection URLs are visible before application modules load.
3. The normal disposable path must not require a developer to pre-create `moda_interact_test` or manually export `TEST_DATABASE_URL`/`TEST_REDIS_URL`.
4. Existing explicit external test URLs may remain as an opt-in override if useful for CI/debugging, but they must not be the only runnable integration path.
5. Exercise at least:
   - `translation-batch-assembly.concurrency.integration.test.ts` against the fresh migrated PostgreSQL container;
   - the repository's existing Redis/BullMQ integration coverage against the fresh Redis container.
6. Teardown must occur if Vitest succeeds, fails or is interrupted through the normal wrapper error path.
7. Do not make ordinary unit tests require Docker. Keep disposable-container tests behind a dedicated integration command.
8. Do not make BACKGROUND-005/006/007 depend on this task. This is parallel quality infrastructure, not a product capability gate.

## Work Items

- [x] Add exact Shared testing release dependency.
- [x] Add Background integration runner using the Shared harness and database submodule migration path.
- [x] Wire a dedicated npm integration-test command.
- [x] Convert the PostgreSQL concurrency test from manual-env-only to the disposable runner path while preserving optional direct URL execution if useful.
- [x] Run an existing Redis/BullMQ integration test through the same disposable Redis instance.
- [x] Document local prerequisite: Docker-compatible container runtime only.
- [x] Add focused runner validation that does not require live Docker where practical.

## Interfaces / Contracts

Expected developer flow:

```text
npm run test:integration
  -> disposable PostgreSQL
  -> prisma migrate deploy using database/prisma/schema.prisma
  -> disposable Redis
  -> Vitest integration slice with TEST_DATABASE_URL/TEST_REDIS_URL
  -> cleanup
```

## Dependencies
## Acceptance Criteria

- [x] A developer with Docker but no local PostgreSQL/Redis test services can run the dedicated Background integration command successfully.
- [x] The disposable PostgreSQL begins fresh and receives the real migration chain before tests.
- [x] The BACKGROUND-004 concurrency integration test passes through the disposable runner.
- [x] Redis/BullMQ integration coverage passes through the disposable Redis instance.
- [x] Both containers are removed after pass and failure.
- [x] Unit tests remain runnable without Docker.
- [x] No production Background code changes are required.

## Validation

Focused runner/unit tests, one live disposable integration run, typecheck, repository-declared relevant validation and `git diff --check`.

## Implementation Notes

Architect release on 2026-09-06: SHARED-006 is accepted Complete at exact registry version `0.7.2`. This task must pin `@modainteract/moda-interact-shared@0.7.2` and consume `@modainteract/moda-interact-shared/testing/node`; do not use a workspace/source fallback.

Prefer a wrapper process over relying on late mutation of `process.env` inside Vitest global setup: the child Vitest process should receive database/Redis URLs before importing modules that construct Prisma/Redis clients.

Luna stop condition: once the existing Background integration slice runs from freshly migrated disposable PostgreSQL/Redis and cleans up, return this task to `review` and STOP.

## Completion Report

### Status

Ready for Review.

### Files Changed

`package.json`, `package-lock.json`, `scripts/test-integration.mjs`, `tests/unit/runtime/observability-startup.test.ts`, and the `database` submodule pointer. Existing BACKGROUND-004 implementation files in the worktree were pre-existing and were not modified by this task.

### Work Completed

Pinned `@modainteract/moda-interact-shared` to exact `0.7.2` and added `npm run test:integration`. The runner uses `withDisposableIntegrationInfrastructure` from `@modainteract/moda-interact-shared/testing/node`, starts fresh dynamic PostgreSQL and Redis containers, deploys the real migrations from `database/prisma/schema.prisma`, launches Vitest in a child process with test URLs set before module loading, forwards interrupts, propagates the child result, and relies on the harness `finally` cleanup. The Background database submodule was advanced from DATABASE-001 commit `7d6e006` to accepted DATABASE-002 commit `23fff6d` so the real translation tables are migrated. The existing exact-version assertion was updated to `0.7.2`.

### Validation Results

Focused affected unit tests: 19 passed. Dedicated `npm run test:integration`: 2 test files and 3 tests passed against fresh migrated PostgreSQL/Redis. `npm run build`: passed. `npm run prisma:validate`: passed. `node --check scripts/test-integration.mjs`: passed. `git diff --check`: passed. The post-run Docker container check returned no disposable containers. Full `npm run test:unit` had 182 passed and 4 failures: three existing recovery-related baseline failures and the version assertion before this task's correction; the directly affected slice is now green.

### Deviations

The disposable runner requires a Docker-compatible runtime, as specified by the task. The Background repository's existing unit suite contains unrelated failures; no unrelated production code was changed.

### Assumptions

The accepted DATABASE-002 schema revision is available through the database submodule remote and may be adopted by updating the submodule pointer in Background.

### Unresolved Issues

No unresolved task issues. Existing unrelated unit failures remain outside this task's scope and are recorded above.

### Architectural Concerns

No new architectural concerns. The runner uses the shared lifecycle owner and leaves production worker behavior unchanged.

### Review Status

Ready for Architect Review.


## Architect Review

### Decision

Accepted Complete.

### Review

Independent architect review confirmed that the Background repository pins the exact accepted Shared testing release `@modainteract/moda-interact-shared@0.7.2` and consumes the Node-only `@modainteract/moda-interact-shared/testing/node` entrypoint. The dedicated `npm run test:integration` wrapper resolves the authoritative database submodule schema, invokes the Shared disposable PostgreSQL/Redis lifecycle, applies the real Prisma migration chain with `prisma migrate deploy`, and starts Vitest as a child process with `DATABASE_URL`, `TEST_DATABASE_URL`, `REDIS_URL`, and `TEST_REDIS_URL` populated before application modules load.

The accepted DATABASE-002 submodule revision is present, including `20260906122000_add_translation_batch_recovery_persistence`, so the fresh disposable PostgreSQL instance is migrated to the schema required by the ARCH-006 translation integration test. The selected integration slice covers the BACKGROUND-004 PostgreSQL concurrency path and existing BullMQ/Redis telemetry path. Cleanup is owned by the accepted Shared harness and the wrapper forwards normal SIGINT/SIGTERM received while Vitest is running so control returns through the harness `finally` cleanup path.

The task remains a non-gating quality-infrastructure capability. It does not alter translation production behavior and does not gate or promote BACKGROUND-006 or BACKGROUND-007.

### Validation Evidence

Accepted evidence from the repository task report: dedicated disposable integration run passed 2 files / 3 tests against freshly migrated PostgreSQL and Redis; build, Prisma validation, script syntax validation, and `git diff --check` passed; the post-run disposable-container check was clean. Existing unrelated recovery-unit failures remain outside this task.
