---
id: ARCH-041-API-003
architecture_id: ARCH-041
title: Extract billing presentation projections
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
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
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `pending` according to explicit dependencies in this snapshot; readiness is re-gated by the launcher before an attempt.

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

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] `src/billing/presentation/billing-read.service.test.ts`, schema/openapi tests and the conditional billing-read PostgreSQL integration suite.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-projection.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing billing-read service, schema/OpenAPI and PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Keep any query-dependent validations inside the scope of the original snapshot. Extract pure calculations only when input shapes are explicit. Avoid sharing billing policy with another service absent a verified identical semantic contract.

## Completion Report

### Status

Not Started — portable definition; no implementation attempt.

### Files Changed

None. To be recorded by the executing agent.

### Work Completed

None.

### Validation Results

Not run; source snapshot inspection is not a test run. Record exact commands, actual pass/fail/skip counts and any environment-specific blockers.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

None at definition time. Execution-dependent blockers and newly discovered constraints must be recorded.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed or accepted; task is defined but not materialised.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review.
