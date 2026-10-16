---
id: ARCH-041-API-006
architecture_id: ARCH-041
title: Extract recovery-credit purchase intent persistence
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
  - ARCH-041-API-007
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-006 — Extract recovery-credit purchase intent persistence

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-006` in the canonical parent task worktree.
- **Task state:** `complete`; Attempt 1 passed developer self-review and was explicitly completed by the developer after canonical worktree preparation and dependency verification.

### Developer Takeover

The task was defined for agent execution with automatic completion. The developer explicitly invoked `/moda_developer_create ARCH-041-API-006`, taking over implementation and completion authority. `assigned_agent: moda_api`, scope, dependencies, acceptance criteria and validation requirements are unchanged. The task is now `execution_mode: developer` and `completion_mode: developer`.

## Objective

Isolate the shop-locked recovery-credit purchase and billing-operation intent transaction behind a dedicated internal collaborator.

## Context

`RecoveryCreditPurchaseCommandService` currently handles Shop locks, subscription validation, plan catalogue/bundle eligibility, pending-charge suppression, idempotency, recoveryCreditPurchase row creation and provider invocation in one file.

## Scope

- Extract `persistIntent` into an API-local collaborator while preserving the Shop/subscription locking and `ReadCommitted` transaction.
- Keep Free-versus-paid subscription validation, billing period/provider snapshot semantics, pending purchase per bundle, purchase and billingOperation atomic creation, fingerprint and replay logic unchanged.
- Keep provider client outside the transaction and the `initiate` public signature unchanged.
- Preserve on-database unique conflict mapping, immutable amount/currency/credit quote and `REQUESTED` purchase lifecycle.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- A new purchase and operation either both persist or neither persists.
- Replay with the same shop/key/payload performs no second purchase row, provider call or charge; mismatched replay fails the same way.
- No extra grants/credits, subscription mutation or cross-shop leakage.
- Do not add a new shared billing abstraction where recurring command semantics differ.

The accepted API-001 migration-backed billing test runner is the shared database proof for this task. Reuse it for relevant existing and new billing PostgreSQL tests; do not create another per-task disposable database harness, and do not accept `prisma db push` alone as proof of persisted billing locks, integrity or replay behavior.

## Work Items

- [x] Extract typed purchase intent repository/transaction method and its purely local eligibility helpers.
- [x] Add focused tests for active Free/paid, invalid period, disabled/stale bundle, pending duplicate and tenant separation.
- [x] Exercise idempotency replay and PostgreSQL concurrent intent admission.
- [x] Run existing recovery-credit command and route tests.

## Interfaces / Contracts

Internal purchase-intent result consumed by existing `RecoveryCreditPurchaseCommandService`; `RecoveryCreditPurchaseCommandResponse`, `recoveryCreditPurchaseFingerprint`, Prisma models and OpenAPI billing command contract remain unchanged.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-007`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Same Shop/subscription ownership, period and bundle checks.
- [x] One atomic purchase+operation intent with existing quote/provider snapshots.
- [x] Replay and concurrent duplicate/race behaviour unchanged and no double provider charge.
- [x] No changed purchase credit-accounting or billing reconciliation semantics.

- [x] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [x] Focused `src/billing/commands/recovery-credit-purchase-command.postgres.test.ts` under real disposable PG plus relevant route tests.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recovery-credit-intent.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recovery-credit-intent.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recovery-credit purchase command PostgreSQL and HTTP route suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Use the existing `BillingOperation` unique `shopId_requestKey` boundary. Never manufacture a second purchase on provider uncertainty; provider calls remain outside transactions.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and the developer explicitly recorded completion on 2026-10-16. The claim is cleared; no implementation branch was merged to `main`.

### Files Changed

Implementation task branch `task/ARCH-041-API-006` contains the extraction and tests in commits `26400ee9b1b32a48ee9b668b71afe6c24ce10213` and `7c461edcfc9b8b815d2910eedfe22b089865a2b1` (published to `origin/task/ARCH-041-API-006`). Changed paths:

- `src/billing/commands/recovery-credit-command-error.ts`
- `src/billing/commands/recovery-credit-intent.ts`
- `src/billing/commands/recovery-credit-purchase-command.postgres.test.ts`
- `src/billing/commands/recovery-credit-purchase-command.service.ts`
- `tests/unit/billing/commands/recovery-credit-intent.test.ts`

Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-006`, branch `task/ARCH-041-API-006`. Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-006`, branch `task/ARCH-041-API-006`.

### Work Completed

Extracted `persistIntent` into the API-local `RecoveryCreditIntentPersistence` collaborator, retaining the Shop/subscription locks and `ReadCommitted` transaction, existing tenant/plan/bundle/period and idempotency checks, pending-purchase suppression, and atomic purchase plus billing-operation creation. `RecoveryCreditPurchaseCommandService.initiate` retains its public signature and provider invocation remains after transaction commit. Added focused unit coverage and expanded the existing migration-backed recovery-credit PostgreSQL suite for persistence, replay, rollback, concurrency, and provider-reference collision behavior. No schema, migration, endpoint, accounting, credit-grant, or billing-reconciliation semantics changed.

### Validation Results

- `node --import tsx --test tests/unit/billing/commands/recovery-credit-intent.test.ts` — 10 passed, 0 failed.
- `node scripts/test-arch041-billing-postgres.mjs` — 17 passed, 0 failed, 0 skipped; deployed all 49 migrations with `prisma migrate deploy` before executing the billing persistence suites.
- `node --import tsx --test src/woocommerce/installation/routes.test.ts` — 19 passed, 0 failed.
- `npm run typecheck` — passed after widening the test fixture’s enum property types; Prisma Client generation succeeded.
- `npm run lint` — passed.
- `npm test` — 320 passed, 0 failed, 43 skipped (database-gated tests).
- `npm run build` — passed.
- `git diff --check origin/main...HEAD` — passed for the implementation diff; the one typecheck-driven fixture correction was committed and pushed as `7c461ed`.
- Canonical worktrees: parent path and implementation path recorded above; both task branches match their respective `origin/task/ARCH-041-API-006` refs and both worktrees are clean. Recursive implementation submodule `database` is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c` (`heads/main`).

### Deviations

Typecheck exposed overly narrow inferred enum literal types in the new unit fixture. The fixture was widened to the corresponding generated enum types in commit `7c461ed`; typecheck and all subsequent required gates passed. No scope deviation.

### Assumptions

The canonical task definition, dependency state, launcher-resolved worktree paths, task refs and recursive implementation submodule were used as the source of truth. The uploaded ZIP was not used as implementation state.

### Unresolved Issues

No task-scope blockers. The task worktrees’ configured upstream metadata points to `origin/main`; publication and synchronization were verified against the explicit `origin/task/ARCH-041-API-006` refs, which match the local commits. The implementation `database` submodule is initialized at the recorded commit.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Developer Self-Review - Passed (Attempt 1)

### Review Status

Passed/Accepted. Attempt 1 satisfies the defined scope, Work Items, Acceptance Criteria and required validation. Because `completion_mode: developer`, this review does not complete the task; explicit developer completion remains pending.

### Reviewed Files

The five implementation paths listed under Files Changed, including the final task-branch diff published through `7c461ed`.

### Validation Reviewed

Focused unit tests (10/10), migration-backed PostgreSQL runner (17/17 after 49 migrations), recovery-credit route suite (19/19), typecheck, lint, full test suite (320 passed, 43 skipped, 0 failed), build, implementation diff check, and clean/synchronized canonical worktrees with the initialized recursive `database` submodule.

### Architecture Conformance

Conforms to the API-006 extraction scope. Persistence remains atomic and shop-scoped; provider calls remain outside the transaction; public command and HTTP contracts and credit/accounting semantics are unchanged. No schema, migration, shared abstraction, endpoint, or unrelated test migration was added.

### Follow-up

Task status is `review`, with `executor` and `claimed_at` cleared and Attempt 1 preserved. The developer may explicitly complete with `/moda_developer_update ARCH-041-API-006 complete`. No enabled task was started and neither task branch was merged to `main`.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-041-API-006 complete`. Attempt 1 remains the accepted attempt; status is `complete`, with `executor` and `claimed_at` cleared. The implementation branch remains separate from `main`.

### Dependency Frontier

Promoted `ARCH-041-API-007` from `pending` to `ready` at Attempt 0 on its own canonical parent task branch because its only declared dependency, API-006, is now complete. API-007 was not claimed or started; no implementation worktree was created. No other downstream task was eligible for promotion, and neither task branch was merged to `main`.

## Architect Review

### Review Status

Pending; the developer self-review and explicit completion are recorded above. No separate architect-agent review is represented here.

### Review Notes

Developer self-review passed and explicit developer completion was recorded for Attempt 1. No separate architect-agent acceptance is represented here.

### Reviewed Files

The five implementation paths listed in the Completion Report and the parent task record on `task/ARCH-041-API-006`.

### Validation Reviewed

See the exact commands and results in Validation Results and Developer Self-Review above.

### Architecture Conformance

Developer self-review found the implementation conforms to `ARCH-041` and the canonical task. No separate architect-agent assessment is represented here.

### Follow-up

No separate architect-agent review was performed. API-007 readiness was reconciled in the Developer Completion Decision above.
