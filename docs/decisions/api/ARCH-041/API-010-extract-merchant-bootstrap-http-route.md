---
id: ARCH-041-API-010
architecture_id: ARCH-041
title: Extract merchant bootstrap HTTP route
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-009
enables:
  - ARCH-041-API-011
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-010 — Extract merchant bootstrap HTTP route

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-010` in the canonical parent task worktree.
- **Task state:** `ready` at Attempt 0 because its sole dependency, API-009, is architect-accepted `complete`; no execution claim has been made.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-041-API-010` on 2026-10-16, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. `assigned_agent: moda_api` and the task scope, dependency, acceptance criteria and validation requirements are unchanged. This amendment records ownership only; Attempt 0 remains unclaimed until canonical preparation succeeds.

## Objective

Extract `GET /v1/merchant/bootstrap` into the merchant bootstrap domain so Woo installation router no longer owns the merchant bootstrap read HTTP handler.

## Context

The Woo connection router still authenticates and serves the merchant bootstrap read model. `MerchantBootstrapReadService` and its schema/OpenAPI exist under `src/merchant/bootstrap/`, but route ownership is split across the Woo installation module.

## Scope

- Add a narrow route handler in `src/merchant/bootstrap/` with existing `WooInstallationAuthenticator` (still in `src/woocommerce/installation/authenticator.ts`), read service and logger injection; no `src/auth/` move.
- Preserve authentication, strict query rejection, response shape, integrity-error classification and existing logging fields.
- Wire the new merchant route through existing delegation; do not yet redesign application-wide route order or composition.
- Update focused tests to target the new public handler, retaining existing installation-route parity tests.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Only authenticated current installation Shop can read its own bootstrap model.
- No fallback ShopSettings writes, category assignment, plan activation or new bootstrap fields.
- Keep `GET /v1/merchant/bootstrap` response unchanged for the Woo plugin and existing OpenAPI.

## Work Items

- [ ] Move merchant bootstrap route logic and error map into a merchant-domain module.
- [ ] Update minimal route injection/delegation.
- [ ] Add bootstrapping route tests covering auth, tenant restriction, query invalidity, no writes, integrity failures.
- [ ] Run API-001 and existing bootstrap OpenAPI and service tests.

## Interfaces / Contracts

`GET /v1/merchant/bootstrap`, `openapi/merchant-bootstrap-v1.yaml`, `MerchantBootstrapReadService`, existing Woo principal. No new DTO.

## Dependencies

- `ARCH-041-API-009` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-011`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Woo installation router no longer contains merchant bootstrap HTTP handler.
- [ ] Existing auth and response/error/logging contracts remain identical.
- [ ] Bootstrap read stays side-effect free and tenant-scoped; existing tests remain green.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] Existing `src/merchant/bootstrap/*.test.ts` and Woo installation router parity tests.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/merchant/bootstrap/routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing merchant bootstrap service and Woo installation router tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Preserve the route-specific secure logging and no-store response. Do not combine bootstrap with category selection writes just because their endpoints share `/v1/merchant`.

## Completion Report

### Status

Not Started — materialised task definition; no implementation attempt.

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

None at definition time. Execution-dependent blockers and newly discovered constraints must be recorded.

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
