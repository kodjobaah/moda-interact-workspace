---
id: ARCH-041-API-002
architecture_id: ARCH-041
title: Isolate billing presentation snapshot queries
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 25
executor: null
claimed_at: null
attempt: 1
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
- **Definition state:** materialised on parent branch `task/ARCH-041-API-002` in the canonical parent task worktree.
- **Task state:** `review`; Developer Attempt 1 self-review passed and is awaiting architect review. The execution claim is cleared; explicit developer completion remains pending.

### Developer Takeover

The task was defined for agent execution with automatic completion. The developer explicitly invoked `/moda_developer_create ARCH-041-API-002`, taking over implementation and completion authority. `assigned_agent: moda_api`, scope, dependencies, acceptance criteria and validation requirements are unchanged. The task is now `execution_mode: developer` and `completion_mode: developer`.

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

- [x] Create the narrow snapshot-loading collaborator and move query-only logic into it.
- [x] Adjust the existing service to use it inside the existing transaction.
- [x] Add/update focused snapshot tests for invalid Shop, missing subscription, multiple unresolved operations, purchase overflow, and concurrent snapshot consistency.
- [x] Run existing billing-read and catalogue tests, including migration-backed PostgreSQL tests against an actually provisioned instance.

## Interfaces / Contracts

Internal API-only module contracts; input `WooInstallationPrincipal`, Prisma transaction client and read clock. Existing `BillingPresentationResponse`, OpenAPI v1 and `BillingPresentationError` remain unchanged.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-003`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] One `RepeatableRead` transaction contains every dependent read for one billing response.
- [x] All old billing response variants and integrity failures remain unchanged.
- [x] Migration-backed PostgreSQL tests demonstrate no cross-tenant read, write or isolation regression.
- [x] No changed public exports used by other repositories.

- [x] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [x] Focused billing presentation unit tests and `src/billing/presentation/billing-read.postgres.test.ts` using the API-001 migration-backed runner; if PostgreSQL cannot run, record the task as blocked rather than passed.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-snapshot.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/presentation/billing-snapshot.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing `src/billing/presentation/billing-read.*.test.ts` suites and owned PostgreSQL fixtures. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not split into independent SQL reads across different transactions. An explicit internal snapshot type/selection helper is preferable to broad `any` casts. Preserve Shop and purchase integrity checks.

## Completion Report

### Status

Attempt 1 implementation and self-review are complete; submitted for architect review on 2026-10-16. The task is `review`, and explicit developer completion remains pending because `completion_mode: developer`.

### Files Changed

- `src/billing/presentation/billing-read.service.ts`
- `src/billing/presentation/billing-snapshot.reader.ts`
- `src/billing/presentation/billing-read.postgres.test.ts`
- `tests/unit/billing/presentation/billing-snapshot.test.ts`

Implementation commit `829c0a17635addb0734b6fb6e0df5aa92d4b611d` is pushed to API branch `task/ARCH-041-API-002`. Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-002`, branch `task/ARCH-041-API-002`. Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-002`, branch `task/ARCH-041-API-002`.

### Work Completed

Extracted query-only billing presentation reads into the internal, transaction-bound `BillingSnapshotReader`, retaining one `RepeatableRead` transaction and moving the shop, six bounded core reads, conditional catalogue lookups and confirmed-cancellation lookup behind it. Shop validation, error precedence and response projection remain in `BillingPresentationReadService`. Added focused selector/tenant/limit/error tests and a PostgreSQL concurrent-update test demonstrating the response continues to use its established MVCC snapshot. No schema, migration, Shared, public API or unrelated changes were made.

### Validation Results

- `node --import tsx --test src/billing/presentation/billing-read.service.test.ts tests/unit/billing/presentation/billing-snapshot.test.ts`: 17 passed, 0 failed, 0 skipped.
- `npm test`: 356 total; 314 passed, 0 failed, 42 skipped (database-dependent suites skipped without their configured DB URL).
- `node scripts/test-arch041-billing-postgres.mjs`: 16 passed, 0 failed, 0 skipped. The runner created disposable PostgreSQL, applied all 49 migrations with `prisma migrate deploy`, and ran billing read/catalogue plus recurring and recovery-credit PostgreSQL suites. This includes the same-RepeatableRead concurrent-update snapshot assertion.
- `npm run typecheck`: passed (includes Prisma Client generation).
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check origin/main...HEAD`: passed.
- At implementation reconciliation, both canonical task worktrees were clean and each task branch matched its remote. API implementation branch `task/ARCH-041-API-002` remains at `829c0a17635addb0734b6fb6e0df5aa92d4b611d`. This parent task/report update is being published on the same parent task branch. Recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`. No merge to `main` was performed.

### Deviations

None. Implementation remains within API-002 scope; no assigned-agent assistance was used.

### Assumptions

Validation was run in the canonical launcher-resolved implementation worktree against the checked-out current API mainline and applied migrations. Skipped tests in `npm test` are existing database-dependent suites; the dedicated disposable PostgreSQL runner executed the required billing suites successfully.

### Unresolved Issues

None known. Explicit developer completion is pending architect review and a later `/moda_developer_update ARCH-041-API-002 complete` decision.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending architect review of the submitted Attempt 1 implementation.

### Review Notes

Developer self-review passed for Attempt 1; architect review is requested. Explicit developer completion is pending.

### Reviewed Files

The four implementation/test files listed in the Completion Report; API branch `task/ARCH-041-API-002` at `829c0a17635addb0734b6fb6e0df5aa92d4b611d`.

### Validation Reviewed

17 focused presentation unit tests, 314 passed/42 skipped in `npm test`, 16 migration-backed PostgreSQL suites, typecheck, lint, build and `git diff --check` all passed as detailed in the Completion Report.

### Architecture Conformance

Developer self-review found the API-002 scope and acceptance criteria satisfied; architect assessment remains pending.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review. If accepted, explicit developer completion remains required.

## Developer Self-Review - Passed (Attempt 1)

Attempt 1 satisfies the defined Work Items and Acceptance Criteria. The database reads remain tenant-scoped and within the existing `RepeatableRead` transaction; selectors, ordering, limits, conditional query order, error mapping and the public response contract are preserved. Required unit, PostgreSQL migration, typecheck, lint, build and diff validations passed. Implementation is committed and pushed, and both canonical worktrees are clean and synchronized. No deviation or known unresolved implementation issue remains. This is a passing self-review submitted for architect review; because `completion_mode: developer`, explicit developer completion is pending.
