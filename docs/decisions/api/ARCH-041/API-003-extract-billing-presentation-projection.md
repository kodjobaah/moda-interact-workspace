---
id: ARCH-041-API-003
architecture_id: ARCH-041
title: Extract billing presentation projections
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-16T10:08:51Z
attempt: 2
depends_on:
  - ARCH-041-API-002
enables:
  - ARCH-041-API-014
  - ARCH-041-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-003 — Extract billing presentation projections

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-003`.
- **Task state:** `in_progress`, developer Attempt 1; its sole dependency, `ARCH-041-API-002`, is complete at parent commit `9bf352337bb5d8d4d951bea7a83652643abe7fbb`.

### Developer Takeover

This task was defined with `execution_mode: agent` and `completion_mode: automatic`. The developer explicitly invoked `/moda_developer_create ARCH-041-API-003`, recording a takeover to `execution_mode: developer` and `completion_mode: developer`. Logical ownership remains `moda_api`; scope, dependencies, acceptance criteria and implementation requirements are unchanged.

## Objective

Separate deterministic billing state validation and API response projection from the transactional snapshot loader.

## Context

API-002 isolates database acquisition. The remainder of `billing-read.service.ts` still projects Free/paid balances, cancellation, pending operations, purchased/refunding capacity, promotions and top-up offers. Extract those calculations into focused, testable API-local pure functions.

## Scope

- Move domain projection helpers to `src/billing/presentation/` modules owned by the API, with a stable snapshot input from API-002.
- Preserve all existing `BillingPresentationResponse` v1 fields and optional/null/value representations.
- Keep billing integrity decisions, promotional timing, top-up eligibility, purchase pending/unresolved state and `BillingPresentationError` codes identical.
- Thin `BillingPresentationReadService` orchestrates snapshot acquisition and pure projection; no presentation function makes Prisma, provider or network calls.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Preserve `now` as an injectable explicit timestamp; avoid implicit `Date.now()` semantics inside projections.
- No arithmetic, rounding, threshold, priority or currency changes to balances, cancellation flags or offers.
- The source `BillingPresentationReadService.read` public signature and runtime response validator remain stable.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [x] Extract `projectBalance`, purchased/paid-included/promotional/purchase helpers and top-up eligibility into cohesive small modules.
- [x] Separate remaining integrity validation/projection from snapshot acquisition without changing when failures occur.
- [x] Add explicit pure-table tests for Free, paid, frozen, cancellation, pending operation, expired promotion and refunding capacity.
- [x] Run existing route, schema, read unit and PostgreSQL tests.

## Interfaces / Contracts

Internal snapshot input/`BillingPresentationResponse` output only; OpenAPI `woocommerce-billing-presentation-v1.yaml` remains byte/semantic compatible. No cross-repository contract.

## Dependencies

- `ARCH-041-API-002` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Projection functions do not access Prisma, clock globals, HTTP or provider clients.
- [x] Every existing response field and integrity/error category remains semantically unchanged.
- [x] Existing BillingPresentationReadService constructor/callers continue working without API route changes.
- [x] Focused plus current real PostgreSQL cases pass.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [x] `src/billing/presentation/billing-read.service.test.ts`, schema/openapi tests and the migration-backed billing-read PostgreSQL integration suite.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Reuse the accepted API-001 billing runner for existing billing-read PostgreSQL coverage, without creating a new harness. Keep projection unit tests pure.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-projection.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing billing-read service, schema/OpenAPI and PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Keep any query-dependent validations inside the scope of the original snapshot. Extract pure calculations only when input shapes are explicit. Avoid sharing billing policy with another service absent a verified identical semantic contract.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-16T10:08:51Z. Attempt 1 review history is preserved below.

### Files Changed

Attempt 1 extracted billing projections into API-local pure modules, preserved the read-service constructor and response contracts, and added projection coverage. All implementation changes are committed and pushed on the API task branch.

### Work Completed

Extracted capacity, purchase, validation, and response projection logic from `BillingPresentationReadService`. The service retains the original `RepeatableRead` transaction, staged validation/query order, injectable `now`, exported response/error identities, and constructor signature. Added pure table tests for Free and paid balances, frozen state, cancellation/pending states, time-bounded promotions, unresolved purchases, and refunding capacity.

### Validation Results

Validation passed: focused projection test `./node_modules/.bin/tsx --test tests/unit/billing/presentation/billing-projection.test.ts` (7 passed); `npm run typecheck`; `npm run lint`; `npm test` (372 total, 331 passed, 41 PostgreSQL-dependent tests skipped, 0 failed); `npm run build`; and `node scripts/test-arch041-billing-postgres.mjs` (16 passed, 0 skipped, 0 failed). The PostgreSQL runner applied all 49 Prisma migrations with `prisma migrate deploy` and exited successfully after its disposable-container cleanup. `git diff --check origin/main...HEAD` passed. Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-003` on `task/ARCH-041-API-003` (remote fast-forward not needed; `origin/main` already incorporated); implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-003` on `task/ARCH-041-API-003` (remote task branch at `ad9cbdb8d9891d3983e16d357dcf54ae060ec6c4`; `origin/main` already incorporated). Both worktrees are clean. Recursive submodule sync and initialization passed; `database` is ready at `139765042baad3901682cfe9c54a3d6bba73e75c`.

### Deviations

None.

### Assumptions

API-002's explicit completion is durable on its parent task branch at `9bf352337bb5d8d4d951bea7a83652643abe7fbb`; API-003 has no other declared dependencies. The task is developer-executed with logical owner `moda_api` and developer-owned completion.

### Unresolved Issues

Current `origin/main` includes API-006 merge commit `7485ad8`. That merge removes the API-003 projection modules and changes `billing-read.service.ts`, while API-003 remains a separate task commit. Reconcile the task branch with current mainline and preserve API-006 behavior before another self-review.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Implementation has not been reviewed. This update only recalculates dependency eligibility.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Developer execution may begin through `/moda_developer_create ARCH-041-API-003`. No implementation branch was created and no branch was merged to `main`.

## Dependency Frontier Reconciliation

- `ARCH-041-API-002` was explicitly completed by the developer on 2026-10-16; its parent task branch is published at `9bf352337bb5d8d4d951bea7a83652643abe7fbb`.
- API-003's only declared dependency is API-002. It was unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`) and `pending` before this reconciliation, so its status became `ready`; ownership was unchanged at that point. The later Developer Takeover section records the current execution and completion modes.
- At frontier reconciliation, only the canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-003` existed. Developer preparation has since created the canonical implementation worktree as recorded above.

## Developer Self-Review

### Review Result

Passed. Explicit developer completion is pending.

### Attempt

1

### Reviewed Scope

The API-local billing presentation contract, pure capacity/purchase/response projections, staged integrity validation, and `BillingPresentationReadService` orchestration, including the new projection table tests.

### Validation Evidence

Focused projection tests, the full API unit suite, typecheck, lint, production build, migration-backed billing PostgreSQL runner, and `git diff --check` passed. The full API suite reported 41 PostgreSQL-dependent skips; the approved PostgreSQL runner passed all 16 selected billing suites with no skips. Implementation commit `ad9cbdb8d9891d3983e16d357dcf54ae060ec6c4` is pushed to `origin/task/ARCH-041-API-003`; both canonical worktrees are clean and the database submodule is initialized at the launcher-recorded commit.

### Decision

Transition Attempt 1 to `review` under `completion_mode: developer`; explicit developer completion remains pending. No enabled task was started, and neither task branch was merged to `main`.

## Developer Self-Review - Changes Requested

### Review Result

Changes Requested. Attempt 1's focused and migration-backed validations passed against its prepared baseline, but mainline advanced before review and now overlaps the task's implementation files.

### Attempt

1

### Required Corrections

- Synchronize `task/ARCH-041-API-003` with current `origin/main` in the permitted direction. Preserve API-006's recovery-credit command extraction and its tests.
- Reconcile API-003's projection extraction with the API-006 version of `src/billing/presentation/billing-read.service.ts`; do not restore the pre-API-006 service wholesale or remove API-006 behavior.
- Restore or adapt the API-003 pure projection modules and tests so the task's Work Items and Acceptance Criteria remain satisfied on top of current mainline.
- Re-run the focused projection and billing-read/OpenAPI tests, `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`, and `node scripts/test-arch041-billing-postgres.mjs`; record the exact outcomes after reconciliation.

### Evidence

Current `origin/main` is `7485ad8` (merge pull request #17 for API-006). `git diff HEAD..origin/main` shows API-006's merge deletes `billing-capacity.projection.ts`, `billing-presentation.contract.ts`, `billing-projection.ts`, `billing-purchase.projection.ts`, and the pure projection test, while rewriting `billing-read.service.ts`. API-003's published implementation commit `ad9cbdb8d9891d3983e16d357dcf54ae060ec6c4` is not an ancestor of current `origin/main`.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Do not create Attempt 2 during this reconciliation. Explicit developer completion remains pending.
