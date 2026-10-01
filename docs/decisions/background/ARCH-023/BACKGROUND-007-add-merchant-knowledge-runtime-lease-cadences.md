---
id: ARCH-023-BACKGROUND-007
architecture_id: ARCH-023
title: Add Merchant Knowledge runtime lease cadences
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 31
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-023-DATABASE-005
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-10-01
updated: 2026-10-01
---

# Add Merchant Knowledge runtime lease cadences

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing shared Background runtime lease service so the two database-owned Merchant Knowledge lease identities enforce the exact global cadence windows already required by BACKGROUND-004, without implementing the Merchant Knowledge entrypoint itself.

## Context

`ARCH-023-BACKGROUND-004` Attempt 1 is blocked because its two `startDynamicLeasedScheduler` calls require lease names absent from the pinned database enum and absent from the lease service's PostgreSQL cadence `CASE`.

`ARCH-023-DATABASE-005` owns the enum/migration. After that task is accepted, this task adopts its database revision and adds only the Background runtime cadence semantics needed before BACKGROUND-004 can resume.

The local scheduler intervals and global lease cadences must agree:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION = 60 seconds
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP         = 3600 seconds
```

## Scope

```text
database                                      # gitlink/pin only to accepted DATABASE-005 revision
src/runtime/background-runtime-lease.ts
tests/unit/runtime/background-runtime-lease.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
```

Modify another existing runtime-lease-focused test only if required by the repository's actual test decomposition.

## Out of Scope

- `src/entrypoints/merchant-knowledge.ts`.
- Merchant Knowledge processing/acquisition/cleanup business logic.
- Database schema/migration edits inside this repository task.
- New `BackgroundRuntimeConfig` fields.
- Redis/advisory locks or another scheduler implementation.
- BACKGROUND-004 validation/completion.
- BACKGROUND-005 entitlement reconciliation.

## Requirements

### R1: adopt the accepted database contract

Pin the nested database dependency to the exact architect-accepted `ARCH-023-DATABASE-005` commit before implementation/validation.

Do not edit the nested schema/migration in this task.

### R2: exact global cadence mapping

Extend only the existing PostgreSQL `CASE` in `BackgroundRuntimeLeaseService.tryAcquire()` with:

```text
MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION -> 60
MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP         -> 3600
```

The values are seconds and must continue to gate reacquisition using persisted `lastFinishedAt` and PostgreSQL time.

Preserve all existing lease-name branches exactly.

### R3: no new runtime configuration

Do not add cadence fields to `BackgroundRuntimeConfig`, environment variables, config files or Admin controls. These two V1 schedules are fixed by ARCH-023/BACKGROUND-004.

### R4: unit regression

Extend the lease-service unit coverage to prove the generated acquisition SQL contains both exact enum labels and exact cadence values while preserving the existing checkout-expiry/billing/runtime mappings.

Do not weaken types with `as any` in production code.

### R5: disposable PostgreSQL lease proof

Extend/reuse the existing task-owned disposable integration path to prove for both new lease names:

1. first owner acquires the lease;
2. release persists `lastFinishedAt`;
3. immediate reacquisition is skipped inside the fixed cadence;
4. after backdating `lastFinishedAt` beyond that lease's cadence, exactly one competing owner reacquires with the next generation;
5. stale heartbeat/release fencing remains intact;
6. test rows and owned infrastructure are removed.

Use the accepted database migrations. Do not use an unverified developer `DATABASE_URL`.

## Work Items

- [x] Pin accepted DATABASE-005 revision.
- [x] Add the two exact lease cadence branches.
- [x] Add focused unit coverage.
- [x] Add/reuse disposable PostgreSQL cadence proof for both new names.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-005
public.BackgroundRuntimeLeaseName
```

Produces the runtime lease capability required by `ARCH-023-BACKGROUND-004` R14.

## Dependencies

- `ARCH-023-DATABASE-005`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [x] Both Merchant Knowledge lease identities compile without casts/workarounds.
- [x] Global cadence is exactly 60 seconds for PENDING reconciliation.
- [x] Global cadence is exactly 3600 seconds for upload cleanup.
- [x] Existing lease mappings and fencing semantics are unchanged.
- [x] No new runtime-config field or scheduler is introduced.
- [x] Disposable PostgreSQL cadence proof passes for both names.

## Validation

- [x] focused runtime-lease unit tests
- [x] disposable PostgreSQL runtime-lease cadence integration
- [x] Prisma generate against accepted database pin
- [x] TypeScript/typecheck or repository equivalent
- [x] production build
- [x] changed-file lint/diagnostics
- [x] `git diff --check`

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not resume BACKGROUND-004.

## Implementation Notes

The local `startDynamicLeasedScheduler` timer remains owned by BACKGROUND-004's entrypoint. This task only gives the distributed lease layer matching global cadence semantics.

## Completion Report

### Status
Ready for architect review. Attempt 1 implementation is committed and pushed; the task is returned to `review` with the claim cleared.

### Preparation Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-007`, branch `task/ARCH-023-BACKGROUND-007`. Launcher synchronized it at `0944355232ea09b649557716459668c0b8e97590`; claim commit `f948c2568da2adb1357a264a70fa3cd6ce3cd277` was pushed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-007`, branch `task/ARCH-023-BACKGROUND-007`, prepared at `a3851c2cb2b8069f36aa7baeac0a422bfae7df18` from current `origin/main`.
- Dependency gate passed: `ARCH-023-DATABASE-005` was Complete / Accepted at Attempt 2. Its architect-accepted implementation commit is `b34a563436bbc89b6ca3e26b43a0bd03116a1a66`.
- Recursive submodule preparation passed. The nested `database` submodule was initialized at `a5e633a6ed1631e64510b936b2b19e8e50c7a5de`, then pinned by this task to the exact accepted commit `b34a563436bbc89b6ca3e26b43a0bd03116a1a66`. It has no nested submodules.
- No task report review corrections existed; Architect Review was Pending before this attempt. Implementation commit `b39fc48c5a02e3b4f9d492f6d83e1650390ede53` was pushed to `origin/task/ARCH-023-BACKGROUND-007`.

### Files Changed
- `database`: nested database gitlink only, pinned to the accepted DATABASE-005 commit; no schema or migration edits.
- `src/runtime/background-runtime-lease.ts`
- `tests/unit/runtime/background-runtime-lease.test.ts`
- `tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts`

### Work Completed
- Added only the fixed PostgreSQL cadence branches: `MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION` = 60 seconds and `MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP` = 3600 seconds. Existing SQL branches, persisted `lastFinishedAt` gating, PostgreSQL `NOW()`, and fencing predicates remain unchanged.
- Added unit assertions for both exact enum labels/values and every pre-existing cadence mapping.
- Added disposable PostgreSQL cases for both new lease names, proving first acquisition, persisted release time, in-cadence skip, one generation-2 winner after cadence elapsed, stale heartbeat/release fencing, and row cleanup.
- Added no runtime configuration, scheduler, entrypoint, business logic, schema, or migration changes.

### Validation Results
- `npm run test -- tests/unit/runtime/background-runtime-lease.test.ts`: passed, 5 tests.
- Disposable PostgreSQL cadence integration: passed, 3 tests total, using the shared `withDisposableIntegrationInfrastructure` helper with `pgvector/pgvector:pg17`; both new cadence cases passed, and invocation-owned PostgreSQL/Redis containers were removed. The integration assertions clean their lease rows in `finally`.
- `npm run prisma:generate`: passed against the accepted nested database pin, Prisma Client v6.19.3.
- `npm run build`: passed; this runs Prisma generation and TypeScript compilation.
- Changed-file diagnostics: no errors in the runtime service or either changed test. `package.json` declares no lint script.
- `git diff --check`: passed.

The repository stock `npm run test:integration -- tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts` initially failed before test execution because its default `postgres:17.6-alpine` image lacks the `vector` extension required by the accepted migration chain. The same shared disposable harness was rerun with its supported `pgvector/pgvector:pg17` image option and passed. No harness source or cross-repository code was changed.

### Deviations
The focused disposable integration used the shared harness directly with its documented pgvector image option because the repository wrapper selects a plain PostgreSQL image that cannot apply the accepted migration chain. The wrapper remains unchanged.

### Assumptions
The accepted dependency revision is the exact implementation commit `b34a563436bbc89b6ca3e26b43a0bd03116a1a66` recorded as Accepted in the DATABASE-005 task, rather than the later database `main` commit.

### Unresolved Issues
The default image in `scripts/test-integration.mjs` does not include `vector`; the focused validation succeeded with the pgvector override. A broader default-image adjustment is outside this task bounded scope.

### Architectural Concerns
None. No cross-repository contract, schema, queue payload, or runtime configuration changes were required.

## Architect Review

### Review Status
Pending

### Review Notes
Pending.

### Reviewed Files
Pending.

### Validation Reviewed
Pending.

### Architecture Conformance
Pending.

### Follow-up
Pending.
