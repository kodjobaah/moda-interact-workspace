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
claimed_at: 2026-10-16T09:38:53Z
attempt: 1
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
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-003`; this frontier update is being published on that branch. The implementation worktree remains absent until execution starts.
- **Task state:** `ready`; its sole dependency, `ARCH-041-API-002`, was explicitly completed by the developer at parent commit `9bf352337bb5d8d4d951bea7a83652643abe7fbb`.

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

- [ ] Extract `projectBalance`, purchased/paid-included/promotional/purchase helpers and top-up eligibility into cohesive small modules.
- [ ] Separate remaining integrity validation/projection from snapshot acquisition without changing when failures occur.
- [ ] Add explicit pure-table tests for Free, paid, frozen, cancellation, pending operation, expired promotion and refunding capacity.
- [ ] Run existing route, schema, read unit and PostgreSQL tests.

## Interfaces / Contracts

Internal snapshot input/`BillingPresentationResponse` output only; OpenAPI `woocommerce-billing-presentation-v1.yaml` remains byte/semantic compatible. No cross-repository contract.

## Dependencies

- `ARCH-041-API-002` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Projection functions do not access Prisma, clock globals, HTTP or provider clients.
- [ ] Every existing response field and integrity/error category remains semantically unchanged.
- [ ] Existing BillingPresentationReadService constructor/callers continue working without API route changes.
- [ ] Focused plus current real PostgreSQL cases pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] `src/billing/presentation/billing-read.service.test.ts`, schema/openapi tests and the migration-backed billing-read PostgreSQL integration suite.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Reuse the accepted API-001 billing runner for existing billing-read PostgreSQL coverage, without creating a new harness. Keep projection unit tests pure.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-projection.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing billing-read service, schema/OpenAPI and PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Keep any query-dependent validations inside the scope of the original snapshot. Extract pure calculations only when input shapes are explicit. Avoid sharing billing policy with another service absent a verified identical semantic contract.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-16T09:38:53Z. Attempt 0 review history is preserved below.

### Files Changed

Only this task's eligibility/report metadata changed. No implementation files changed; no implementation worktree was created.

### Work Completed

Recalculated the sole explicit dependency and marked API-003 ready. Implementation remains outstanding and must follow the defined Work Items, Acceptance Criteria and Validation.

### Validation Results

No implementation validation was run because this was an eligibility-only frontier update. `git diff --check` was run on the task record before publication.

### Deviations

None.

### Assumptions

API-002's explicit completion is durable on its parent task branch at `9bf352337bb5d8d4d951bea7a83652643abe7fbb`; API-003 has no other declared dependencies. The task is developer-executed with logical owner `moda_api` and developer-owned completion.

### Unresolved Issues

No frontier blockers. API-003 has not been claimed; its implementation worktree has intentionally not been created.

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
- API-003's only declared dependency is API-002. It was unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`) and `pending` before this reconciliation, so its status is now `ready`; execution and completion modes and logical owner are unchanged.
- Created only the canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-003` on `task/ARCH-041-API-003` from fetched `origin/main` `07e9362b49e58bf7317869e4b5b85667ff5493d0`. The implementation worktree remains absent until claim.
