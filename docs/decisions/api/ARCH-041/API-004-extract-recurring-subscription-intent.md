---
id: ARCH-041-API-004
architecture_id: ARCH-041
title: Extract recurring subscription intent persistence
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-16T03:15:35+0100
attempt: 1
depends_on:
  - ARCH-041-API-001
enables:
  - ARCH-041-API-005
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-004 — Extract recurring subscription intent persistence

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-004` by this developer-create invocation; publication is recorded in the claim section below.
- **Task state:** `in_progress`, Developer Attempt 1. Its only declared dependency, `ARCH-041-API-001`, was verified `complete` before claim.

### Developer Takeover

This task was defined with `execution_mode: agent` and `completion_mode: automatic`. The developer explicitly invoked `/moda_developer_create ARCH-041-API-004`, taking over execution and completion authority. The task scope, acceptance criteria and dependencies are unchanged; logical ownership remains `moda_api`.

## Objective

Extract the shop-locked, replay-safe recurring billing intent transaction from `RecurringSubscriptionCommandService` into a focused persistence collaborator.

## Context

`src/billing/commands/recurring-subscription-command.service.ts` combines `create`, `switchPlan`, `cancel`, idempotency replay, operational paid-plan materialisation, provider action and result updates. First isolate the transactional intent boundary only.

## Scope

- Extract `persistIntent` and necessary internal validation/replay helpers with an injected Prisma transaction-capable database and approved plan resolver.
- Preserve the shop and subscription `FOR UPDATE` locking sequence, tenant ownership, state predicates, plan eligibility, canonical request fingerprint and immutable quoted metadata.
- Keep `ReadCommitted` transaction boundary, Prisma P2002 mapping and one-time retry behaviour for known plan-materialisation races.
- Maintain `RecurringSubscriptionCommandService` public constructor and method calls; keep provider invocation and outcome updates in existing service for API-005.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- No provider/network call inside persistence transactions.
- Replay of the exact `(shopId, requestKey)` returns the same durable operation; conflicting fingerprint/kind/plan fails identically.
- Materialised plan resolution, failure code/HTTP mapping and operation creation remain byte-for-byte behaviour compatible.
- Existing row/advisory locks and uniqueness constraints are neither bypassed nor weakened.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [ ] Extract transactional intent handling and typed `CommandIntent` internal data.
- [ ] Keep/create focused tests for idempotency replay/conflicts, cancellation re-create gate, plan-switch eligibility, P2002/known-retry mapping and cross-tenant protection.
- [ ] Run recurring provider-mock and PostgreSQL tests; verify no new provider calls on replay.

## Interfaces / Contracts

API-local recurring intent persistence result consumed by `RecurringSubscriptionCommandService`; existing `RecurringCommandResponse` and `woocommerce-billing-commands-v1.yaml` unchanged. Existing Shared `recurringRequestFingerprint` helper remains canonical.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-005`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Recurring command signatures and error semantics are unchanged.
- [ ] Transaction locks, plan materialisation and replay are equivalent, including collisions and cancellation edge cases.
- [ ] No external billing request fires until the newly created durable intent transaction completes.
- [ ] Migration-backed PostgreSQL race/replay cases pass.

- [ ] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] Focused `src/billing/commands/recurring-command-primitives.test.ts` and `src/billing/commands/recurring-subscription-command.postgres.test.ts` using the API-001 migration-backed disposable database.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recurring-intent.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recurring-intent.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recurring-command-primitives and recurring subscription PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not share this workflow with recovery-credit purchases solely because both use billingOperation. Distinct eligibility and compensation semantics belong to their existing domains.

## Completion Report

### Status

In Progress — Developer Attempt 1 claimed on 2026-10-16 after verifying `ARCH-041-API-001` Complete. This invocation created the canonical parent and implementation worktrees from current `origin/main`, changed execution/completion ownership to developer, and recorded the claim. Implementation has not started.

### Files Changed

No implementation files changed during preparation. The task definition was updated for developer takeover and Attempt 1 claim.

### Work Completed

Canonical worktree preparation and claim are complete. Implementation remains outstanding and must follow the Work Items, Acceptance Criteria and Validation above.

### Validation Results

Not run; this invocation only prepared and claimed the task. Use the API repository toolchain and the migration-backed PostgreSQL runner required by this task during implementation validation. Pre-existing changes in the primary workspace were preserved and not included in either task worktree.

### Deviations

Developer takeover changes execution/completion ownership only; no scope or contract deviation.

### Assumptions

The supplied portable task definition was treated as a specification only. Before claim, the canonical task definition on fetched `origin/main`, active task state and accepted dependency were rechecked; the implementation worktree was prepared from current API `origin/main`.

### Unresolved Issues

No implementation blocker was identified during preparation. The primary workspace contains pre-existing unrelated changes, which were preserved; the canonical API implementation worktree is clean.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation evidence; developer Attempt 1 is active.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

After implementation, reconcile with `/moda_developer_update ARCH-041-API-004`; explicit developer completion is required because `completion_mode: developer`.

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T03:15:35+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`.
- `ARCH-041-API-001` was verified `complete` from the canonical task definition before claim.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-004`, branch `task/ARCH-041-API-004`, based on fetched `origin/main` at `07e9362b49e58bf7317869e4b5b85667ff5493d0`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-004`, repository `moda-interact-api`, branch `task/ARCH-041-API-004`, based on fetched `origin/main` at `195e9648061230fde2de5072e62977253f41c49a`.
- No task branch existed remotely before this invocation. Both task worktrees were clean at preparation; current `origin/main` was fetched before creation, and no merge was needed.
- The primary workspace and API source/reference checkout were restored to `main` after task branch creation; all pre-existing primary-workspace changes were preserved. No shared/default checkout was used for implementation, and no branch was merged to `main`.
- No implementation files changed during claim preparation. The developer now owns implementation in the canonical API worktree.
