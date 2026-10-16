---
id: ARCH-041-API-005
architecture_id: ARCH-041
title: Extract recurring subscription provider outcomes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-041-API-004
enables:
  - ARCH-041-API-014
  - ARCH-041-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-005 — Extract recurring subscription provider outcomes

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-005`.
- **Task state:** `review`, developer Attempt 1 passed self-review and is awaiting explicit developer completion. Its sole declared dependency, `ARCH-041-API-004`, is complete.

### Developer Takeover

This task was defined with `execution_mode: agent` and `completion_mode: automatic`. The developer explicitly invoked `/moda_developer_create ARCH-041-API-005`, recording a takeover to `execution_mode: developer` and `completion_mode: developer`. Logical ownership remains `moda_api`; scope, dependencies, acceptance criteria and implementation requirements are unchanged.

## Objective

Extract recurring subscription provider result validation and guarded operation outcome persistence into a focused collaborator.

## Context

After API-004, `RecurringSubscriptionCommandService` still owns provider operation selection, response validation, collision detection, guarded state transitions and replay-facing errors. Those provider-outcome responsibilities can be isolated without changing the flow.

## Scope

- Extract provider-response validation and durable transition handling for create/switch/cancel from the existing service.
- Preserve `INITIATING` compare-and-set, provider-reference advisory lock/collision checks and the distinction between provider definitive rejection and unknown outcome.
- Keep create/switch/cancel network calls strictly between intent commit and outcome transaction; do not introduce provider retries.
- Keep error-code redaction, operation IDs, `AWAITING_CONFIRMATION`/`CONFIRMED` response mapping and constructor injection behaviour unchanged.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Provider evidence must be validated against existing configured Woo environment; do not broaden accepted return URLs/IDs.
- A colliding external provider reference must not be assigned to the wrong merchant.
- Concurrent state transitions/replays remain guarded and honour the current persisted operation result.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [x] Extract provider-result validation and transition collaborator.
- [x] Keep orchestrator method bodies short, preserving each one-time provider call and branch.
- [x] Add focused failure and interleaving tests for returned provider ID mismatch, collision, late confirmation, definite rejection, unknown outcome and concurrent update.
- [x] Run existing recurring-route, provider-mock and PostgreSQL tests.

## Interfaces / Contracts

API-local provider/result collaborator and existing Woo Billing client. External request/response contract and existing `RecurringBillingCommandError` remain unchanged.

## Dependencies

- `ARCH-041-API-004` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Same provider operations invoked exactly once for a newly accepted request, none for replay.
- [x] All durable state changes and errors match previously characterised outcomes.
- [x] No provider call occurs during a Prisma transaction.
- [x] Guarded concurrent updates and provider-reference collision tests pass against PostgreSQL.

- [x] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [x] Focused recurring command route and PostgreSQL tests, including mocked `WooBillingProviderError` failure outcomes and real-provider-reference collision concurrency fixtures.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recurring-outcome.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recurring-outcome.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recurring command provider-failure, replay and PostgreSQL concurrency suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not conflate provider call success with subscription entitlement activation; existing webhook/Background reconciliation owns authoritative future entitlement updates.

## Completion Report

### Status

Review — Attempt 1 passed developer self-review and is awaiting explicit developer completion. The claim is cleared; Attempt 0 history is preserved below.

### Files Changed

Implementation commit `55275e3a1c7760e6c1639b4bdac08c7e88c274a1` is published on `origin/task/ARCH-041-API-005`. It adds `src/billing/commands/recurring-outcome.ts`, `tests/unit/billing/commands/recurring-outcome.test.ts`, and `tests/integration/billing/commands/recurring-outcome.test.ts`, and updates `src/billing/commands/recurring-subscription-command.service.ts`.

Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-005`, branch `task/ARCH-041-API-005`. Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-005`, branch `task/ARCH-041-API-005`.

### Work Completed

Extracted provider-result validation, replay response mapping, definite/ambiguous provider error handling, and guarded confirmation/cancellation outcome transactions into API-local `RecurringOutcomePersistence`. The service preserves its constructor and command methods, performs each provider request once between intent persistence and outcome persistence, and delegates replay and outcomes to the collaborator. Create-provider references remain protected by the advisory lock and cross-Shop collision check; CAS failures read and return the current persisted operation state. Added focused unit coverage for invalid provider evidence, switch-reference mismatch, collision, late confirmation/rejection, bounded errors and concurrent state updates, plus a migration-backed cross-Shop reference-race integration test. No schema, migration, endpoint, shared package, subscription projection or entitlement semantics changed.

### Validation Results

- `node --import tsx --test tests/unit/billing/commands/recurring-outcome.test.ts src/woocommerce/installation/routes.test.ts` — 33 passed, 0 failed.
- `node scripts/test-arch041-billing-postgres.mjs tests/integration/billing/commands/recurring-outcome.test.ts` — 17 passed, 0 failed, 0 skipped; applied all 49 migrations with `prisma migrate deploy` and ran the default billing persistence suites plus the API-005 concurrent provider-reference integration test.
- `npm run typecheck` — passed; Prisma Client generation succeeded.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm test` — 379 tests, 338 passed, 0 failed, 41 skipped (database-gated tests).
- `npm run build` — passed.
- `git diff --check origin/main...HEAD` — passed for the implementation diff; `git diff --check` passed for this parent report update.
- Canonical parent worktree is clean at `0aae7fafabbeb9f6dd2b6f4c5441a0d94896663c`, matching `origin/task/ARCH-041-API-005`. Canonical implementation worktree is clean at `55275e3a1c7760e6c1639b4bdac08c7e88c274a1`, matching `origin/task/ARCH-041-API-005`; recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.

### Deviations

No scope deviation. The new PostgreSQL integration file is not in the runner’s default suite list, so it was passed explicitly as an additional integration path to the accepted migration-backed runner.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

No task-scope blockers. The worktrees’ configured tracking metadata points to `origin/main` in places; all publication and synchronization checks used the explicit `origin/task/ARCH-041-API-005` refs, which match the local commits.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed or accepted; task is ready for its first implementation attempt.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review. Developer self-review passed; a separate architect review is not represented here.

## Developer Self-Review - Passed (Attempt 1)

### Review Status

Passed/Accepted. Attempt 1 satisfies the task scope, Work Items, Acceptance Criteria and required validation. Because `completion_mode: developer`, this review does not complete the task; explicit developer completion remains pending.

### Reviewed Files

The four implementation diff paths listed under Files Changed at `55275e3a1c7760e6c1639b4bdac08c7e88c274a1`, including the new unit and integration suites.

### Validation Reviewed

Focused outcome and route tests (33/33), migration-backed billing PostgreSQL runner including the additional API-005 collision integration test (17/17 after 49 migrations), typecheck, lint, full suite (338 passed, 41 skipped, 0 failed), build, diff checks, and clean synchronized canonical worktrees with the initialized `database` submodule.

### Architecture Conformance

Conforms to the API-005 provider-outcome extraction scope. Network calls remain outside Prisma transactions and occur once for newly accepted requests; replays do not call the provider. Existing guarded state transitions, bounded error mapping, provider-reference collision protection and subscription projection ownership are preserved. No schema, migration or public contract changed.

### Follow-up

Task status is `review`; `executor` and `claimed_at` are cleared and Attempt 1 is preserved. Explicit developer completion is pending. No enabled task was started and no task branch was merged to `main`.

## Dependency Frontier Reconciliation (2026-10-16)

- `ARCH-041-API-004` was explicitly completed by the developer after its passing Attempt 1 self-review; implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` is published on `origin/task/ARCH-041-API-004`.
- This task's only declared dependency is now `complete`, so API-005 is promoted from `pending` to `ready` at Attempt 0. No claim or implementation worktree was created.
- API-014 and `ARCH-041-SYSTEM-TEST-001` remain gated by API-005 completion. No other task status was changed, and no branch was merged into `main`.
