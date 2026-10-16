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
status: complete
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
- **Definition state:** materialised in the canonical parent task worktree on `task/ARCH-041-API-004`; the implementation task branch is published.
- **Task state:** `complete`, Developer Attempt 1. Its only declared dependency, `ARCH-041-API-001`, was complete before execution.

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

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration was introduced.
- [x] Recurring command signatures and error semantics remain unchanged; `RecurringBillingCommandError` is re-exported from its existing service module.
- [x] Transaction locks, plan materialisation and replay remain equivalent, including collisions and cancellation edge cases.
- [x] No external billing request fires until the newly created durable intent transaction completes; replay makes no additional provider call.
- [x] Migration-backed PostgreSQL race/replay cases pass.

- [x] Migration-backed PostgreSQL integration proves persisted recurring transaction, replay, collision and concurrency invariants against actual applied schema migrations.

## Validation

- [x] `node --import tsx --test tests/unit/billing/commands/recurring-intent.test.ts src/billing/commands/recurring-command-primitives.test.ts` — 15 passed, 0 failed.
- [x] `node --import tsx --test src/woocommerce/installation/routes.test.ts` — 19 passed, 0 failed.
- [x] `node scripts/test-arch041-billing-postgres.mjs` — 16 passed, 0 failed, 0 skipped; 49 migrations deployed with `prisma migrate deploy`.
- [x] `npm run typecheck`, `npm run lint`, and `npm run build` — passed.
- [x] `npm test` — 362 tests, 320 passed, 0 failed, 42 database-gated PostgreSQL tests skipped; the migration-backed runner separately passed the required PostgreSQL cases.
- [x] `git diff --check origin/main...HEAD` passed. Implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` is published to `origin/task/ARCH-041-API-004`; the canonical implementation worktree is clean with database submodule `139765042baad3901682cfe9c54a3d6bba73e75c`.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recurring-intent.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recurring-intent.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recurring-command-primitives and recurring subscription PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not share this workflow with recovery-credit purchases solely because both use billingOperation. Distinct eligibility and compensation semantics belong to their existing domains.

## Completion Report

### Status

Complete — Developer Attempt 1 passed self-review and the developer explicitly recorded completion.

### Files Changed

Implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` changes five API implementation/test paths; see the canonical API-004 completion report for the exact list.

### Work Completed

Extracted shop-locked recurring intent persistence into `RecurringIntentPersistence`; provider execution and outcome persistence remain in `RecurringSubscriptionCommandService`.

### Validation Results

Required validation passed: focused tests 15/15, route tests 19/19, migration-backed PostgreSQL 16/16 after 49 migrations, full suite 320 passed/42 database-gated skips/0 failed, typecheck, lint, build, and diff check.

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

Developer self-review Accepted for Attempt 1; explicit developer completion is recorded. Separate architect review remains pending.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review.

## Developer Completion Decision

- Date: 2026-10-16. The developer explicitly invoked `/moda_developer_update ARCH-041-API-004 complete` and accepts Attempt 1 following the passing self-review.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`; the accepted attempt is unchanged.
- Implementation commit `bb83012e4443b6ef68c2bdf0d5415e8c1e9ba19b` is published to `origin/task/ARCH-041-API-004`. No branch was merged into `main`.
