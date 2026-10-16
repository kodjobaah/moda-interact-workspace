---
id: ARCH-041-API-007
architecture_id: ARCH-041
title: Extract recovery-credit provider outcome persistence
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-041-API-006
enables:
  - ARCH-041-API-014
  - ARCH-041-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-007 — Extract recovery-credit provider outcome persistence

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-007` in the canonical parent task worktree. Developer Attempt 1 is complete in the canonical API implementation worktree; its implementation remains published on the task branch.
- **Task state:** `complete`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 passed developer self-review and was explicitly completed on 2026-10-16. Its sole explicit dependency, `ARCH-041-API-006`, is `complete`.

## Objective

Separate Woo one-time charge response validation and guarded provider-outcome updates from credit-purchase orchestration.

## Context

API-006 isolates purchase intent. The command service still combines the Woo charge transport result, provider reference collision guard and durable operation transition logic.

## Scope

- Extract bounded Woo charge-response validation, provider-error classification and transaction-safe outcome persistence.
- Preserve advisory provider-reference collision protection, `INITIATING` compare-and-set, idempotent duplicate/late results, `AWAITING_CONFIRMATION`, `FAILED` and `OUTCOME_UNKNOWN` semantics.
- Keep provider call outside DB transactions; service returns the same safe response/error envelope, including `purchaseId` when appropriate.
- Retain provider-environment URL validation and no premature credit grant.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Definite provider rejection cannot become a confirmed purchase; uncertain outcome is not retried as a fresh charge.
- Provider reference collision across shops remains fail-safe and bounded.
- Status/result mapping and safe provider error code exposure remain unchanged.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [x] Extract small provider-result interpreter and guarded persistence method.
- [x] Add focused tests for malformed provider result, rejection, unknown outcome, provider ID collision, concurrent state update and original idempotent replay.
- [x] Run credit-purchase PostgreSQL and route integration tests.

## Interfaces / Contracts

Internal API-only collaborator consumed by `RecoveryCreditPurchaseCommandService`. Existing Woo Billing client and `RecoveryCreditPurchaseCommandError` wire mapping remain authoritative.

## Dependencies

- `ARCH-041-API-006` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] No extra charge, no double-credit grant and no new background/reconciliation side effects.
- [x] All original provider failure and collision behaviours remain identical.
- [x] Transaction and provider invocation ordering unchanged; DB concurrency proofs pass.

- [x] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [x] Focused recovery-credit command PostgreSQL tests and existing HTTP purchase-command contract tests.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recovery-credit-outcome.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recovery-credit-outcome.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recovery-credit command PostgreSQL and HTTP tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not change the role of the signed Woo billing webhook or when a purchase becomes active. Only extract existing synchronous command result processing.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and the developer explicitly recorded completion on 2026-10-16. Logical ownership remains `assigned_agent: moda_api`; execution and completion modes remain `developer` and `developer`. The claim is cleared. No implementation branch was merged to `main`.

### Files Changed

The implementation branch changes exactly four task-scoped paths: `src/billing/commands/recovery-credit-outcome.ts` (new), `src/billing/commands/recovery-credit-purchase-command.service.ts`, `tests/unit/billing/commands/recovery-credit-outcome.test.ts` (new), and `tests/integration/billing/commands/recovery-credit-outcome.test.ts` (new). The extracted collaborator validates bounded charge evidence, classifies provider failures, performs guarded persistence and collision protection, and supplies persisted replay/response mapping. The command service persists intent before the external provider call, which remains outside database transactions.

### Work Completed

Extracted provider-result validation and persistence without schema, endpoint, Shared, Background, or cross-repository changes. No material assigned-agent assistance was used.

### Validation Results

All required validation passed during reconciliation:

- `node --import tsx --test tests/unit/billing/commands/recovery-credit-outcome.test.ts src/woocommerce/installation/routes.test.ts` — 31 passed, 0 failed, 0 skipped.
- `node scripts/test-arch041-billing-postgres.mjs tests/integration/billing/commands/recovery-credit-outcome.test.ts` — `prisma migrate deploy` applied the actual migrations; 18 passed, 0 failed, 0 skipped. This included the new simultaneous cross-Shop provider-reference test and the existing billing PostgreSQL suites.
- `npm run typecheck` — passed; Prisma Client generated and TypeScript reported no errors.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm test` — 395 total, 353 passed, 42 skipped, 0 failed.
- `npm run build` — passed; Prisma Client generated and production TypeScript build succeeded.
- `git diff --check origin/main...HEAD` in the implementation worktree and `git diff --check` in the parent worktree — passed.

The focused HTTP route suite is included in the 31-test focused run. The PostgreSQL run asserts exactly one cross-Shop reference is accepted, no credit is granted, and replay performs no additional provider call.

### Deviations

Execution ownership was explicitly taken over by the developer as requested through `/moda_developer_create`. Task scope, dependencies and logical API ownership are unchanged.

### Assumptions

No additional assumptions beyond the task contract were required.

### Unresolved Issues

None. Required tests, PostgreSQL migrations, package gates, and publication checks completed successfully.

### Architectural Concerns

No new contract, ownership, security, data, queue, or infrastructure gap was identified.

## Architect Review

### Review Status

Pending; the developer self-review and explicit completion are recorded below. No separate architect-agent review is represented here.

### Review Notes

No separate architect-agent assessment has been recorded. Developer self-review passed and explicit completion was recorded; architect review remains pending.

### Reviewed Files

No files reviewed in the separate architect-review capacity. The developer self-review covers the implementation paths listed in the Completion Report.

### Validation Reviewed

No separate architect validation review has been recorded. Developer validation evidence is listed in the Completion Report.

### Architecture Conformance

Pending separate architect assessment against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Await separate architect review; explicit developer completion does not represent architect acceptance.

## Developer Takeover and Claim — Attempt 1

- Claimed at `2026-10-16T11:24:18+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`. The developer explicitly took over from `execution_mode: agent`, `completion_mode: automatic`; these are now `developer`/`developer`. `assigned_agent: moda_api` and `coordinator: moda_architect` are unchanged.
- Launcher-resolved parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-007`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-007`. Both use branch `task/ARCH-041-API-007`.
- Parent task branch fast-forwarded from remote task commit `c1095656cbffca1c0ec0b5f905c953d01c76d617` to current parent `origin/main` `fa5b8ecd61ec576653532ece32f914186c2c8b8d`. Parent worktree was clean before the claim edit; current `origin/main` is an ancestor of the task branch.
- API source checkout `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-api` was clean on `main` at `dae7abe729b62b1a98c736ac8aabc8949c9c89e5`, equal to fetched `origin/main`. No remote `origin/task/ARCH-041-API-007` existed. The canonical implementation worktree was created at the launcher-resolved path from current `origin/main`; its `HEAD` and local task branch point to `dae7abe729b62b1a98c736ac8aabc8949c9c89e5`.
- Dependency check: launcher resolved `ARCH-041-API-006` as `complete`, satisfying the sole explicit dependency.
- Recursive submodule evidence: parent task worktree nested submodules are uninitialized; API implementation worktree `database` submodule is uninitialized at gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`. No submodules were initialized or modified.
- No implementation files were changed and no implementation tests/builds were run during claim preparation. Required validation remains listed above.

## Developer Self-Review Passed / Accepted — Attempt 1

- Outcome: accepted for architect review. All task Work Items, Acceptance Criteria and required Validation are satisfied by the implementation and evidence above; no task-introduced regression or unresolved issue was found.
- Changed behavior is limited to extracting charge-response validation, provider failure classification, guarded outcome persistence, cross-Shop provider-reference protection and persisted replay/response mapping. External provider invocation remains outside database transactions. Definite rejection remains terminal `FAILED`; ambiguous results remain `OUTCOME_UNKNOWN`; accepted provider outcomes do not grant credits.
- Focused unit and HTTP route tests passed 31/31; the migration-backed billing PostgreSQL runner passed 18/18 after applying actual migrations; typecheck, lint, full package tests and production build all passed. The full package suite had 42 existing/skipped tests and no failures.
- Implementation task branch `task/ARCH-041-API-007` is published at `7a11ba9186369889c534b1e3c9e72272cda29d64`, matching its remote. It is clean and contains only the four task-scoped paths listed above; `git diff --check origin/main...HEAD` passes.
- Parent task branch was synchronized at `5519f0a2dab5aae930f2b2aaca7eaba663b62821`, matching its remote before this report update. The launcher-resolved parent and implementation worktrees are the canonical paths recorded in the claim section; both use `task/ARCH-041-API-007`. The API-007 implementation worktree is clean, the shared/default implementation checkout was not switched or mutated for task work, and no other task worktree was reused.
- Launcher claim evidence records the parent task branch synchronization and the implementation branch creation from then-current `origin/main`; the claim section also records dependency verification and original worktree setup. At reconciliation, the parent and implementation task refs matched their published remotes. Recursive implementation submodule `database` is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`; the PostgreSQL migration-backed validation completed successfully.
- No material assigned-agent assistance, scope amendment, deviation, or unresolved issue.
- Because `completion_mode: developer`, this passing review does not complete the task. Explicit developer completion remains pending; Attempt 1 is unchanged.

### Review Decision

Passing developer self-review submitted to `moda_architect`. Transition to `status: review`, `executor: null`, `claimed_at: null`, `attempt: 1`. Do not start enabled tasks or merge either task branch to `main`.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-041-API-007 complete`. Attempt 1 remains the accepted attempt; status is `complete`, with `executor` and `claimed_at` cleared. The implementation branch remains separate from `main`.

### Dependency Frontier

- `ARCH-041-API-014` remains `pending`: its other explicit dependency, `ARCH-041-API-011`, is `pending`.
- `ARCH-041-SYSTEM-TEST-001` remains `pending`: its explicit dependencies `ARCH-041-API-013` and `ARCH-041-API-014` are still `pending`. The task also remains manual-gated until all declared dependencies are complete.
- No downstream task became eligible for promotion. No other task record was changed, and neither task branch was merged to `main`.
