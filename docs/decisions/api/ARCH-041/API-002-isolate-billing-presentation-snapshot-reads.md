---
id: ARCH-041-API-002
architecture_id: ARCH-041
title: Isolate billing presentation snapshot queries
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-001
enables:
  - ARCH-041-API-003
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-002 — Isolate billing presentation snapshot queries

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `ready`; its only declared dependency, `ARCH-041-API-001`, is complete. The launcher re-gates dependencies before an attempt.

## Objective

Extract the coherent transactional database-query portion of `BillingPresentationReadService` behind a small internal snapshot reader while keeping `RepeatableRead` and read semantics unchanged.

## Context

`src/billing/presentation/billing-read.service.ts` runs shop, subscription, counters, promotions, operations, purchase and catalogue reads alongside validation and projection in one long function. An internal snapshot structure allows the calculation stage to be separated safely in API-003.

## Scope

- Introduce an API-internal snapshot loader/query module with explicit typed data returned from the **single existing** `RepeatableRead` transaction.
- Keep every logically dependent catalogue, cancellation and operation lookup within that same transaction, including conditional queries.
- Keep shop ID/domain/platform/status/onboarding validation and bounded query ordering/limits at the established boundary.
- Keep the public `BillingPresentationReadService.read(principal, now)` signature and returned response stable; defer substantial projection relocation to API-003.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Exact current query filters, orderings, select fields, limits (including unresolved-purchase overflow detection) and transaction isolation are preserved.
- No additional database round trips or new writes; no Prisma/Shared/schema changes.
- Database snapshot must remain tenant-scoped to `principal.shopId` and `principal.canonicalSiteUrl`.
- Continue mapping integrity/conflict errors to existing `BillingPresentationError` codes.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [ ] Create the narrow snapshot-loading collaborator and move query-only logic into it.
- [ ] Adjust the existing service to use it inside the existing transaction.
- [ ] Add/update focused snapshot tests for invalid Shop, missing subscription, multiple unresolved operations, purchase overflow, and concurrent snapshot consistency.
- [ ] Run existing billing-read and catalogue tests, including migration-backed PostgreSQL tests against an actually provisioned instance.

## Interfaces / Contracts

Internal API-only module contracts; input `WooInstallationPrincipal`, Prisma transaction client and read clock. Existing `BillingPresentationResponse`, OpenAPI v1 and `BillingPresentationError` remain unchanged.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-003`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] One `RepeatableRead` transaction contains every dependent read for one billing response.
- [ ] All old billing response variants and integrity failures remain unchanged.
- [ ] Migration-backed PostgreSQL tests demonstrate no cross-tenant read, write or isolation regression.
- [ ] No changed public exports used by other repositories.

- [ ] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] Focused billing presentation unit tests and `src/billing/presentation/billing-read.postgres.test.ts` using the API-001 migration-backed runner; if PostgreSQL cannot run, record the task as blocked rather than passed.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-snapshot.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/presentation/billing-snapshot.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing `src/billing/presentation/billing-read.*.test.ts` suites and owned PostgreSQL fixtures. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not split into independent SQL reads across different transactions. An explicit internal snapshot type/selection helper is preferable to broad `any` casts. Preserve Shop and purchase integrity checks.

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
