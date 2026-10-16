---
id: ARCH-041-API-009
architecture_id: ARCH-041
title: Extract billing command HTTP routes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 58
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-008
enables:
  - ARCH-041-API-010
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-009 — Extract billing command HTTP routes

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-009` in its canonical parent task worktree. The completed API-008 dependency record is included on this task branch.
- **Task state:** `ready`, Attempt 0, unclaimed. Its sole explicit dependency, `ARCH-041-API-008`, is `complete` in this parent task worktree. The launcher will re-gate dependencies before execution.

## Objective

Move recurring-subscription and recovery-credit purchase POST/DELETE HTTP command handlers out of Woo installation routing into a separate billing command router.

## Context

After API-008 the legacy installation router still owns command request decoding and provider command error mapping for `POST/DELETE /v1/billing/subscription`, `POST /v1/billing/subscription/switch` and `POST /v1/billing/recovery-credit-purchases`.

## Scope

- Extract only the three logical command endpoint families into `src/billing/`-owned route module, using existing command services.
- Preserve `Idempotency-Key` single-header treatment, valid request payload keys, size/body limits and DELETE no-body requirement.
- Keep command error `operationId`, `purchaseId`, bounded `providerErrorCode`, logger metadata and `200` versus `202` transitions unchanged.
- Maintain existing `GET` purchase-history route at same purchase path; dispatcher must select by method and keep unrelated routers reachable.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Service provider availability checks and `503` behaviour must remain identical.
- Unauthorized, revoked, rotated or invalid installation requests cannot invoke a command service or provider under the **existing** auth contract. Do not introduce new mid-flight credential checks or provider retries under a structural extraction.
- No change to provider client, persistence, fingerprint or billing state in this task.
- Method matching must not consume an unhandled method as handled.

## Work Items

- [ ] Extract command HTTP handlers and focused decoder/error adapter while preserving established service injection.
- [ ] Update Woo installation delegator/wiring only as necessary.
- [ ] Add tests for idempotency-header cardinality, unknown fields, body bounds, provider unavailable and provider error redaction.
- [ ] Run API-001 characterization and existing recurring/credit command-route tests.

## Interfaces / Contracts

Current command route paths and `openapi/woocommerce-billing-commands-v1.yaml`; `RecurringSubscriptionCommandService`, `RecoveryCreditPurchaseCommandService` existing methods and errors. No Shared/Prisma schema changes.

## Dependencies

- `ARCH-041-API-008` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-010`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] All billing command requests reach the extracted module with current authentication and response semantics.
- [ ] `GET` purchase history and `POST` purchase intent remain distinct and both work.
- [ ] No accidental retry, duplicated provider invocation or changed error envelope.
- [ ] Unmatched paths/methods still reach appropriate next router/404.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] Existing `routes.test.ts` recurring and recovery-credit command cases, OpenAPI contract tests and API-001 router parity characterization.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/subscription-routes.test.ts`, `tests/unit/billing/commands/recovery-credit-routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing Woo installation route, API-001 characterization and billing command contract tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not bundle orchestration/service cleanup into this HTTP task. Provider business logic was separately owned by API-004/005/006/007 and must not be redone here.

## Completion Report

### Status

Ready — materialised on the canonical parent task branch at Attempt 0. Its sole dependency, `ARCH-041-API-008`, is complete in this parent task worktree. No implementation attempt has been claimed and no implementation worktree was created.

### Files Changed

None. To be recorded by the executing agent.

### Work Completed

None.

### Validation Results

Not run; source snapshot inspection is not a test run. Record exact commands, actual pass/fail/skip counts and any environment-specific blockers.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

No readiness blocker. Implementation and validation remain for the future executor.

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

## Dependency Frontier Reconciliation — 2026-10-16

- Promoted `ARCH-041-API-009` from `pending` to `ready` at Attempt 0 because its sole declared dependency, `ARCH-041-API-008`, is `complete`.
- The API-008 completion record was published on `task/ARCH-041-API-008` at `3bda8e074618100f6774185d068360d6b7de2372`. Parent `origin/main` still records API-008 as `ready`; to make the authoritative dependency state available to this task's launcher gate without merging either branch to `main`, the API-008 parent task branch was merged into this unpublished API-009 parent task branch. This branch now contains the full completed API-008 task record.
- API-009 remains `execution_mode: agent`, `completion_mode: automatic`, `executor: null`, `claimed_at: null`, `attempt: 0`. No implementation worktree was created and no implementation work began.
- The launcher route-only resolver confirms API-009 is materialised and `ready`. No `_index.md` or `main` branch was changed.
