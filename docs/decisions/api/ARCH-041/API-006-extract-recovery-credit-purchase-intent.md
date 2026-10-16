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
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-16T02:14:02Z
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
- **Task state:** `in_progress`; Attempt 1 is claimed by the developer after canonical worktree preparation and dependency verification.

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

- [ ] Extract typed purchase intent repository/transaction method and its purely local eligibility helpers.
- [ ] Add focused tests for active Free/paid, invalid period, disabled/stale bundle, pending duplicate and tenant separation.
- [ ] Exercise idempotency replay and PostgreSQL concurrent intent admission.
- [ ] Run existing recovery-credit command and route tests.

## Interfaces / Contracts

Internal purchase-intent result consumed by existing `RecoveryCreditPurchaseCommandService`; `RecoveryCreditPurchaseCommandResponse`, `recoveryCreditPurchaseFingerprint`, Prisma models and OpenAPI billing command contract remain unchanged.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-007`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Same Shop/subscription ownership, period and bundle checks.
- [ ] One atomic purchase+operation intent with existing quote/provider snapshots.
- [ ] Replay and concurrent duplicate/race behaviour unchanged and no double provider charge.
- [ ] No changed purchase credit-accounting or billing reconciliation semantics.

- [ ] Migration-backed PostgreSQL integration proves this task’s relevant persisted transaction, replay, collision, concurrency and/or integrity invariants against actual applied schema migrations; an unexecuted run is not a pass.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); execute the accepted `node scripts/test-arch041-billing-postgres.mjs` runner for billing PostgreSQL evidence and record commands/results separately. This runner **must run `prisma migrate deploy`** (not `prisma db push`) to exercise actual migration-defined constraints/triggers. If Docker/PG cannot run, mark validation **not run/blocked**; neither mocks nor `db push` establish a PostgreSQL pass.
- [ ] Focused `src/billing/commands/recovery-credit-purchase-command.postgres.test.ts` under real disposable PG plus relevant route tests.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 4 — migration validation:** Use `node scripts/test-arch041-billing-postgres.mjs` for the relevant billing PostgreSQL suites, including legacy `src/billing/**/*.postgres.test.ts` tests and any new `tests/integration/billing/**` cases. The runner must deploy SQL migrations on its disposable database before execution; report exact pass/fail/blocked evidence.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/recovery-credit-intent.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/billing/commands/recovery-credit-intent.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing recovery-credit purchase command PostgreSQL and HTTP route suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Use the existing `BillingOperation` unique `shopId_requestKey` boundary. Never manufacture a second purchase on provider uncertainty; provider calls remain outside transactions.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at `2026-10-16T02:14:02Z` after canonical worktree preparation.

### Files Changed

No implementation files changed at claim time. Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-006`, branch `task/ARCH-041-API-006`. Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-006`, branch `task/ARCH-041-API-006`.

### Work Completed

None.

### Validation Results

Not run at claim time. Record exact commands and results during implementation reconciliation; validation must include the API-001 migration-backed billing PostgreSQL runner and the recovery-credit command and route tests.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. The current canonical task definition, API-001 completion and launcher-resolved paths were rechecked before the Attempt 1 claim.

### Unresolved Issues

No claim-time blockers. The implementation worktree's recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.

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
