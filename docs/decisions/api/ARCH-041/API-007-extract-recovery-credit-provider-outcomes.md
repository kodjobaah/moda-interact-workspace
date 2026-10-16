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
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-16T11:24:18+0100
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
- **Definition state:** materialised on parent branch `task/ARCH-041-API-007` in the canonical parent task worktree. Developer Attempt 1 is active in the canonical API implementation worktree.
- **Task state:** `in_progress`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 claimed on 2026-10-16. Its sole explicit dependency, `ARCH-041-API-006`, is `complete`.

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

- [ ] Extract small provider-result interpreter and guarded persistence method.
- [ ] Add focused tests for malformed provider result, rejection, unknown outcome, provider ID collision, concurrent state update and original idempotent replay.
- [ ] Run credit-purchase PostgreSQL and route integration tests.

## Interfaces / Contracts

Internal API-only collaborator consumed by `RecoveryCreditPurchaseCommandService`. Existing Woo Billing client and `RecoveryCreditPurchaseCommandError` wire mapping remain authoritative.

## Dependencies

- `ARCH-041-API-006` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] No extra charge, no double-credit grant and no new background/reconciliation side effects.
- [ ] All original provider failure and collision behaviours remain identical.
- [ ] Transaction and provider invocation ordering unchanged; DB concurrency proofs pass.

- [ ] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] Focused recovery-credit command PostgreSQL tests and existing HTTP purchase-command contract tests.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recovery-credit-outcome.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recovery-credit-outcome.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recovery-credit command PostgreSQL and HTTP tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not change the role of the signed Woo billing webhook or when a purchase becomes active. Only extract existing synchronous command result processing.

## Completion Report

### Status

In Progress — the developer explicitly took over execution from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Logical ownership remains `assigned_agent: moda_api`; execution and completion modes are now `developer` and `developer`. Developer Attempt 1 is claimed. No implementation changes have been made during preparation.

### Files Changed

None during claim preparation. Implementation work will be recorded by the developer.

### Work Completed

None.

### Validation Results

No implementation validation was run during claim preparation.

### Deviations

Execution ownership was explicitly taken over by the developer as requested through `/moda_developer_create`. Task scope, dependencies and logical API ownership are unchanged.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

No claim-time blocker. The parent worktree's nested submodules and the API implementation worktree's `database` submodule are uninitialized. They were not needed to create or claim the task and were left untouched; initialize only if later task validation requires them.

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

Await architect review after developer implementation and required validation.

## Developer Takeover and Claim — Attempt 1

- Claimed at `2026-10-16T11:24:18+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`. The developer explicitly took over from `execution_mode: agent`, `completion_mode: automatic`; these are now `developer`/`developer`. `assigned_agent: moda_api` and `coordinator: moda_architect` are unchanged.
- Launcher-resolved parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-007`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-007`. Both use branch `task/ARCH-041-API-007`.
- Parent task branch fast-forwarded from remote task commit `c1095656cbffca1c0ec0b5f905c953d01c76d617` to current parent `origin/main` `fa5b8ecd61ec576653532ece32f914186c2c8b8d`. Parent worktree was clean before the claim edit; current `origin/main` is an ancestor of the task branch.
- API source checkout `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-api` was clean on `main` at `dae7abe729b62b1a98c736ac8aabc8949c9c89e5`, equal to fetched `origin/main`. No remote `origin/task/ARCH-041-API-007` existed. The canonical implementation worktree was created at the launcher-resolved path from current `origin/main`; its `HEAD` and local task branch point to `dae7abe729b62b1a98c736ac8aabc8949c9c89e5`.
- Dependency check: launcher resolved `ARCH-041-API-006` as `complete`, satisfying the sole explicit dependency.
- Recursive submodule evidence: parent task worktree nested submodules are uninitialized; API implementation worktree `database` submodule is uninitialized at gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`. No submodules were initialized or modified.
- No implementation files were changed and no implementation tests/builds were run during claim preparation. Required validation remains listed above.
