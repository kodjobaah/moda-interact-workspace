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
status: review
priority: 25
executor: null
claimed_at: null
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
- **Task state:** `review`; Developer Attempt 1 passed self-review. Its only declared dependency, `ARCH-041-API-001`, was verified `complete` before claim.

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

- [x] Extract transactional intent handling into `RecurringIntentPersistence` with typed `RecurringCommandIntent` data.
- [x] Add focused tests for idempotency replay/conflicts, cancellation re-create gate, plan-switch eligibility, P2002/known-retry mapping and Shop identity isolation.
- [x] Run recurring provider-mock, HTTP route and migration-backed PostgreSQL tests; verify no new provider calls on replay.

## Interfaces / Contracts

API-local recurring intent persistence result consumed by `RecurringSubscriptionCommandService`; existing `RecurringCommandResponse` and `woocommerce-billing-commands-v1.yaml` unchanged. Existing Shared `recurringRequestFingerprint` helper remains canonical.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-005`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Recurring command signatures and error semantics remain unchanged; `RecurringBillingCommandError` is re-exported from its existing service module.
- [x] Transaction locks, plan materialisation and replay remain equivalent, including collisions and cancellation edge cases.
- [x] No external billing request fires until the newly created durable intent transaction completes; the provider-mock test asserts the transaction has ended before invocation and that replay makes no additional provider call.
- [x] Migration-backed PostgreSQL race/replay cases pass.

- [x] Migration-backed PostgreSQL integration proves persisted recurring transaction, replay, collision and concurrency invariants against actual applied schema migrations.

## Validation

- [x] `node --import tsx --test tests/unit/billing/commands/recurring-intent.test.ts src/billing/commands/recurring-command-primitives.test.ts` — 15 passed, 0 failed.
- [x] `node --import tsx --test src/woocommerce/installation/routes.test.ts` — 19 passed, 0 failed, including recurring command route contracts.
- [x] `node scripts/test-arch041-billing-postgres.mjs` — 16 passed, 0 failed, 0 skipped. The disposable PostgreSQL database applied all 49 migrations with `prisma migrate deploy`, then ran the billing read, recurring, and recovery-credit persistence suites; teardown completed.
- [x] `npm run typecheck` — passed; Prisma Client generated.
- [x] `npm run lint` — passed with `--max-warnings=0`.
- [x] `npm test` — 362 tests, 320 passed, 0 failed, 42 skipped, 0 cancelled. The skips are existing PostgreSQL tests gated in the normal suite; the separate migration-backed runner above provides PostgreSQL evidence.
- [x] `npm run build` — passed.
- [x] `git diff --check origin/main...HEAD` — passed. Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-004` on `task/ARCH-041-API-004` is clean at `1de2a332c8e3ca0afb22ac64018f1c1c4f8c325e`, matching `origin/task/ARCH-041-API-004`. Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-004` is clean at `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b`, matching `origin/task/ARCH-041-API-004`; its `database` submodule is at `139765042baad3901682cfe9c54a3d6bba73e75c`.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recurring-intent.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recurring-intent.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recurring-command-primitives and recurring subscription PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not share this workflow with recovery-credit purchases solely because both use billingOperation. Distinct eligibility and compensation semantics belong to their existing domains.

## Completion Report

### Status

Passing developer self-review — Attempt 1 is submitted for review. Because `completion_mode` is `developer`, the task remains in `review` until the developer explicitly records the completion decision.

### Files Changed

Implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` changes:

- `src/billing/commands/recurring-command-error.ts`
- `src/billing/commands/recurring-command-primitives.ts`
- `src/billing/commands/recurring-intent.ts`
- `src/billing/commands/recurring-subscription-command.service.ts`
- `tests/unit/billing/commands/recurring-intent.test.ts`

The implementation branch is pushed. No schema, migration, Shared package, endpoint, or unrelated task changes were made.

### Work Completed

Extracted shop-locked intent persistence into `RecurringIntentPersistence`, retaining the `ReadCommitted` transaction, row locks, eligibility checks, quote/fingerprint, retry and P2002 mapping. `RecurringSubscriptionCommandService` delegates intent creation and continues to own provider execution and outcome persistence. Moved `RecurringBillingCommandError` to an API-local module while re-exporting it from the existing service path. Added intent tests covering replay/conflict, cancellation re-create, plan switches, Shop identity, resolver retry/error mapping, P2002, and provider-after-commit/no-replay-call behavior.

### Validation Results

All required validation passed; exact commands and results are recorded above. The normal suite skipped 42 database-gated PostgreSQL tests; the accepted disposable migration-backed runner separately passed all 16 selected billing PostgreSQL cases after deploying 49 migrations. The implementation task branch is published and both canonical task worktrees are clean.

### Deviations

No scope deviation. The error class was moved to preserve a stable import/re-export surface while separating the intent persistence collaborator.

### Assumptions

The supplied task specification and canonical parent task definition agree on scope. API-001 was complete before this attempt; both task branches were created from current `origin/main` and published independently.

### Unresolved Issues

No unresolved task-scope issue. Pre-existing unrelated changes in the primary workspace were preserved and excluded from both task worktrees.

### Architectural Concerns

No contract or architectural issue identified. The collaborator remains API-local, the public service constructor and methods are unchanged, and provider execution remains outside the intent transaction.

## Developer Self-Review

### Review Status

Accepted — Attempt 1 meets the task scope and acceptance criteria, and all required validation passed. The task remains `review` pending the explicit developer completion action required by `completion_mode: developer`.

### Reviewed Files

All five implementation paths listed under Files Changed, comparing `origin/main` with `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b`.

### Validation Reviewed

Focused intent/primitives tests (15/15), installation routes (19/19), full suite (320 passed, 42 database-gated skips, 0 failed), typecheck, lint, build, migration-backed billing PostgreSQL runner (16/16), and implementation `git diff --check` passed.

### Architecture Conformance

Conforms: API-local persistence extraction only; recurring command behavior and provider boundary are preserved, with no schema or public wire-contract change.

### Follow-up

Explicit developer completion is pending. Do not start enabled API-005 until completion is explicitly recorded.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending separate architect review; developer self-review is accepted and the task remains in `review`.

### Reviewed Files

The five implementation paths listed in the Completion Report; parent task record reconciled on the canonical parent task branch.

### Validation Reviewed

See exact commands and results in Validation and Developer Self-Review above.

### Architecture Conformance

Developer self-review confirms API-local intent persistence separation, unchanged public service behavior, and post-transaction provider invocation. A separate architect review remains pending.

### Follow-up

The developer may explicitly complete with `/moda_developer_update ARCH-041-API-004 complete`. Do not start API-005 before then.

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T03:15:35+0100`; `status: in_progress`, `executor: developer`, `attempt: 1`.
- `ARCH-041-API-001` was verified `complete` from the canonical task definition before claim.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-004`, branch `task/ARCH-041-API-004`, based on fetched `origin/main` at `07e9362b49e58bf7317869e4b5b85667ff5493d0`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-004`, repository `moda-interact-api`, branch `task/ARCH-041-API-004`, based on fetched `origin/main` at `195e9648061230fde2de5072e62977253f41c49a`.
- No task branch existed remotely before this invocation. Both task worktrees were clean at preparation; current `origin/main` was fetched before creation, and no merge was needed.
- The primary workspace and API source/reference checkout were restored to `main` after task branch creation; all pre-existing primary-workspace changes were preserved. No shared/default checkout was used for implementation, and no branch was merged to `main`.
- No implementation files changed during claim preparation. The developer now owns implementation in the canonical API worktree.
