---
id: ARCH-041-API-009
architecture_id: ARCH-041
title: Extract billing command HTTP routes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 58
executor: null
claimed_at: null
attempt: 1
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
- **Task state:** `complete`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 passed developer self-review and was explicitly completed by the developer.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-041-API-009`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 was claimed after canonical worktree preparation and dependency verification.

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

- [x] Extract command HTTP handlers and focused decoder/error adapter while preserving established service injection.
- [x] Update Woo installation delegator/wiring only as necessary.
- [x] Add tests for idempotency-header cardinality, unknown fields, body bounds, provider unavailable and provider error redaction.
- [x] Run API-001 characterization and existing recurring/credit command-route tests.

## Interfaces / Contracts

Current command route paths and `openapi/woocommerce-billing-commands-v1.yaml`; `RecurringSubscriptionCommandService`, `RecoveryCreditPurchaseCommandService` existing methods and errors. No Shared/Prisma schema changes.

## Dependencies

- `ARCH-041-API-008` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-010`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] All billing command requests reach the extracted module with current authentication and response semantics.
- [x] `GET` purchase history and `POST` purchase intent remain distinct and both work.
- [x] No accidental retry, duplicated provider invocation or changed error envelope.
- [x] Unmatched paths/methods still reach appropriate next router/404.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); no PostgreSQL integration cases were added, so no database harness was required.
- [x] Existing `routes.test.ts` recurring and recovery-credit command cases, OpenAPI contract tests and API-001 router parity characterization.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/commands/subscription-routes.test.ts`, `tests/unit/billing/commands/recovery-credit-routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing Woo installation route, API-001 characterization and billing command contract tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not bundle orchestration/service cleanup into this HTTP task. Provider business logic was separately owned by API-004/005/006/007 and must not be redone here.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and was explicitly completed by the developer on 2026-10-16. `executor` and `claimed_at` are cleared; the accepted attempt number is unchanged.

### Files Changed

Implementation commit `26710132823f5f47aecc308f605166c1e77b602f` changes:

- `src/billing/commands/command-http.ts`
- `src/billing/commands/routes.ts`
- `src/woocommerce/installation/routes.ts`
- `tests/unit/billing/commands/command-route-fixtures.ts`
- `tests/unit/billing/commands/recovery-credit-routes.test.ts`
- `tests/unit/billing/commands/subscription-routes.test.ts`

### Work Completed

Moved subscription create/switch/cancel and recovery-credit purchase POST handling into the billing-owned command router, with a dedicated strict decoder/error adapter. The Woo installation router now delegates command methods while purchase-history GET remains on its existing read route. Authentication-before-service invocation, single idempotency-header validation, body/query rules, 200/202 transitions, bounded provider errors/logging, no-store responses and unmatched-method fallthrough are preserved. Added focused route suites for both command families.

### Validation Results

All required checks passed on the canonical implementation worktree:

- Focused route/contract/API-001 characterization: `./node_modules/.bin/tsx --test src/woocommerce/installation/routes.test.ts src/woocommerce/installation/openapi-contract.test.ts tests/unit/billing/commands/subscription-routes.test.ts tests/unit/billing/commands/recovery-credit-routes.test.ts tests/unit/http/route-dispatch.test.ts` — 35 passed, 0 failed, 0 skipped.
- `npm run typecheck` — passed; Prisma Client generated.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm test` — 430 tests, 388 passed, 0 failed, 42 skipped. These are existing PostgreSQL-gated skips; this routing-only task added no database integration cases, and the skips are not counted as database validation.
- `npm run build` — passed; Prisma Client generated.
- `git diff --check` — passed.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-009`, branch `task/ARCH-041-API-009`, is clean at `26710132823f5f47aecc308f605166c1e77b602f`, equal to `origin/task/ARCH-041-API-009`; base `origin/main` is `16ac951da5d45ed9e028fe2573ac45e8e51d4708`. Recursive `database` submodule is initialized at gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-009`, branch `task/ARCH-041-API-009`, published the passing review report as commit `906e0aff1c39aebdcb67eaf29754fbcc3dda27ea`. The explicit completion decision and dependency-frontier reconciliation are recorded below on this same parent task branch.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP was a snapshot only. The canonical task record and dependency were rechecked by the launcher; `ARCH-041-API-008` passed the dependency gate as `complete`.

### Unresolved Issues

No implementation or validation blockers. Separate architect review remains pending; the task is complete under the developer-controlled completion mode.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Accept

### Review Notes

Accept — developer self-review is accepted; no separate architect assessment is recorded.

### Reviewed Files

The six implementation paths listed in Files Changed, reviewed against `origin/main` and the API-001 HTTP/router characterization.

### Validation Reviewed

Focused route/contract/API-001 tests (35/35), typecheck, lint, full suite (388 passed, 0 failed, 42 PostgreSQL-gated skips), build and diff check passed.

### Architecture Conformance

The developer self-review found the implementation conforms to the API-009 route-extraction scope. No endpoint, service/provider behavior, persistence/schema, or unrelated task was changed. Architect review remains pending.

### Follow-up

Architect records Accepted / Changes Requested / Blocked. No enabled task was started.

## Developer Self-Review Passed / Accepted — Attempt 1

### Review Status

Passed — Attempt 1 satisfies the defined route-extraction scope and acceptance criteria. The developer explicitly completed this accepted attempt; `completion_mode: developer` remains unchanged.

### Reviewed Files

The six implementation paths listed in Files Changed, plus the existing Woo installation route tests, OpenAPI contract test and API-001 dispatcher characterization.

### Validation Reviewed

Focused route/contract/API-001 slice: 35 passed, 0 failed. Typecheck, lint, production build and `git diff --check` passed. Full suite: 430 tests, 388 passed, 0 failed and 42 PostgreSQL-gated skips. No new PostgreSQL integration cases were introduced.

### Architecture Conformance

Conforms to the bounded API-009 extraction. Purchase-history GET remains distinct from purchase POST; authenticated tenant identity and command response/error contracts are preserved; unmatched methods fall through. No database, provider, business-service, or unrelated task changes were included.

### Follow-up

The developer explicitly completed Attempt 1. API-010 remains `pending` because its declared dependency requires architect-accepted completion of API-009; architect review is still pending. Do not begin API-010 or merge either task branch to `main`.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-041-API-009 complete`. Attempt 1 remains the accepted attempt; `status` is `complete`, with `executor: null` and `claimed_at: null`. The implementation and parent task branches remain separate from `main`; no merge was performed.

### Dependency Frontier

- `ARCH-041-API-010` is the only declared downstream task and depends solely on API-009. It remains `pending`, unclaimed at Attempt 0, because its dependency explicitly requires architect-accepted `complete` status. API-009 is developer-complete, but its separate architect review remains pending; therefore API-010 is not yet eligible. Its `execution_mode: agent`, `completion_mode: automatic`, attempt and null claim are unchanged. No API-010 worktree was prepared and no implementation was started.
- No other task or `_index.md` was changed. No implementation or parent task branch was merged to `main`.

## Developer Claim — Attempt 1

- The developer explicitly took over from the prior agent/automatic lifecycle. `assigned_agent: moda_api` and task scope are unchanged; `execution_mode` and `completion_mode` are now `developer`.
- Claimed at `2026-10-16T12:58:46Z`; `status: in_progress`, `executor: developer`, `attempt: 1`. The launcher dependency gate passed for `ARCH-041-API-008` (`complete`).
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-009`, branch `task/ARCH-041-API-009`; reused and synchronized with current `origin/main`. Claim commit `fce434e00772814ba18009dc2e78a9975ffe899c` is pushed; parent worktree is clean.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-009`, repository `moda-interact-api`, branch `task/ARCH-041-API-009`; created at current `origin/main` commit `16ac951da5d45ed9e028fe2573ac45e8e51d4708`, clean at handoff.
- Recursive submodule sync and initialization passed. The `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`, matching the recorded gitlink.
- No implementation files were changed and no feature validation was run during claim preparation. The implementation task branch has not yet received implementation commits.

## Dependency Frontier Reconciliation — 2026-10-16

- Promoted `ARCH-041-API-009` from `pending` to `ready` at Attempt 0 because its sole declared dependency, `ARCH-041-API-008`, is `complete`.
- The API-008 completion record was published on `task/ARCH-041-API-008` at `3bda8e074618100f6774185d068360d6b7de2372`. Parent `origin/main` still records API-008 as `ready`; to make the authoritative dependency state available to this task's launcher gate without merging either branch to `main`, the API-008 parent task branch was merged into this unpublished API-009 parent task branch. This branch now contains the full completed API-008 task record.
- API-009 remains `execution_mode: agent`, `completion_mode: automatic`, `executor: null`, `claimed_at: null`, `attempt: 0`. No implementation worktree was created and no implementation work began.
- The launcher route-only resolver confirms API-009 is materialised and `ready`. No `_index.md` or `main` branch was changed.
