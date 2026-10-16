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
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-16T09:45:47Z
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
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-005` for dependency-frontier reconciliation; no implementation worktree or attempt has been started.
- **Task state:** `ready`, Attempt 0. Its sole declared dependency, `ARCH-041-API-004`, is complete; the normal launcher must re-gate dependencies before an attempt.

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

- [ ] Extract provider-result validation and transition collaborator.
- [ ] Keep orchestrator method bodies short, preserving each one-time provider call and branch.
- [ ] Add focused failure and interleaving tests for returned provider ID mismatch, collision, late confirmation, definite rejection, unknown outcome and concurrent update.
- [ ] Run existing recurring-route, provider-mock and PostgreSQL tests.

## Interfaces / Contracts

API-local provider/result collaborator and existing Woo Billing client. External request/response contract and existing `RecurringBillingCommandError` remain unchanged.

## Dependencies

- `ARCH-041-API-004` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — canonical auth move waits for stable consumer imports.
- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Same provider operations invoked exactly once for a newly accepted request, none for replay.
- [ ] All durable state changes and errors match previously characterised outcomes.
- [ ] No provider call occurs during a Prisma transaction.
- [ ] Guarded concurrent updates and provider-reference collision tests pass against PostgreSQL.

- [ ] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] Focused recurring command route and PostgreSQL tests, including mocked `WooBillingProviderError` failure outcomes and real-provider-reference collision concurrency fixtures.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recurring-outcome.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recurring-outcome.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recurring command provider-failure, replay and PostgreSQL concurrency suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not conflate provider call success with subscription entitlement activation; existing webhook/Background reconciliation owns authoritative future entitlement updates.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-16T09:45:47Z. Attempt 0 review history is preserved below.

### Files Changed

No implementation changes. The task record was materialised and its eligibility updated on the canonical parent task branch; no implementation worktree was created.

### Work Completed

None.

### Validation Results

Not run; this was a dependency-frontier status update only. Record exact commands, actual pass/fail/skip counts and any environment-specific blockers during implementation.

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

Not reviewed or accepted; task is ready for its first implementation attempt.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review.

## Dependency Frontier Reconciliation (2026-10-16)

- `ARCH-041-API-004` was explicitly completed by the developer after its passing Attempt 1 self-review; implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` is published on `origin/task/ARCH-041-API-004`.
- This task's only declared dependency is now `complete`, so API-005 is promoted from `pending` to `ready` at Attempt 0. No claim or implementation worktree was created.
- API-014 and `ARCH-041-SYSTEM-TEST-001` remain gated by API-005 completion. No other task status was changed, and no branch was merged into `main`.
