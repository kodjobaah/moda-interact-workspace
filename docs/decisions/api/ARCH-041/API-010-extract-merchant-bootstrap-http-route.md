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
status: review
priority: 60
executor: null
claimed_at: null
attempt: 1
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
- **Initial task state:** `ready` at Attempt 0 because its sole dependency, API-009, was architect-accepted `complete`. The developer claimed Attempt 1 after canonical preparation; current review state and evidence are recorded below.

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

- [x] Move merchant bootstrap route logic and error map into a merchant-domain module.
- [x] Update minimal route injection/delegation.
- [x] Add bootstrapping route tests covering auth, tenant restriction, query invalidity, no writes, integrity failures.
- [x] Run API-001 and existing bootstrap OpenAPI and service tests.

## Interfaces / Contracts

`GET /v1/merchant/bootstrap`, `openapi/merchant-bootstrap-v1.yaml`, `MerchantBootstrapReadService`, existing Woo principal. No new DTO.

## Dependencies

- `ARCH-041-API-009` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-011`

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Woo installation router no longer contains merchant bootstrap HTTP handler.
- [x] Existing auth and response/error/logging contracts remain identical.
- [x] Bootstrap read stays side-effect free and tenant-scoped; existing tests remain green.

## Validation

- [x] Verify new unit tests through the existing `npm test` globs. No new PostgreSQL integration cases were added; the existing bootstrap PostgreSQL service suite was run separately using the disposable database harness and its results are recorded below.
- [x] Existing `src/merchant/bootstrap/*.test.ts` and Woo installation router parity tests.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical parent/implementation worktree, publication and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/merchant/bootstrap/routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing merchant bootstrap service and Woo installation router tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Preserve the route-specific secure logging and no-store response. Do not combine bootstrap with category selection writes just because their endpoints share `/v1/merchant`.

## Completion Report

### Status

In Review — Attempt 1 passed developer self-review. `completion_mode: developer` is retained, so explicit developer completion remains pending. Attempt 0 review history is preserved below.

### Files Changed

Implementation commit `3b68ec16f4e30b7308dcd549bf63db2f2a375cd5`, published as `origin/task/ARCH-041-API-010`, changes:

- `src/merchant/bootstrap/openapi-contract.test.ts`
- `src/merchant/bootstrap/routes.ts`
- `src/woocommerce/installation/routes.ts`
- `tests/unit/merchant/bootstrap/routes.test.ts`

### Work Completed

Extracted the authenticated `GET /v1/merchant/bootstrap` handler and its bounded error mapping into `src/merchant/bootstrap/routes.ts`; the Woo installation router now creates and delegates to that route while continuing to re-export the public path constant. The existing authentication order, strict query rejection, principal-based tenant read, response shape, secure logging fields, bounded integrity/internal errors, and no-store/security headers are preserved. Added focused route coverage for authentication, tenant scope, query rejection, no writes, integrity and unexpected failures, and fall-through for unrelated methods and paths. Updated the OpenAPI contract test to import the route path from its new owner. No service, schema, endpoint, or database behavior changed.

### Validation Results

- `npx tsx --test tests/unit/http/route-dispatch.test.ts src/merchant/bootstrap/bootstrap-read.service.test.ts src/merchant/bootstrap/openapi-contract.test.ts src/woocommerce/installation/routes.test.ts tests/unit/merchant/bootstrap/routes.test.ts` — 35 passed, 0 failed, 0 skipped. Covers API-001 route-dispatch characterization, bootstrap service/OpenAPI contracts, Woo installation parity, and the new route suite.
- `npm test -- --test-name-pattern='bootstrap|merchant bootstrap|installation routes'` — the package script's declared globs caused the full suite to run rather than applying the requested name filter; 436 tests, 394 passed, 0 failed, 42 PostgreSQL-gated skips.
- `npm run typecheck` — passed; Prisma Client generated.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm run build` — passed.
- `node scripts/test-woocommerce-installation-postgres.mjs` — disposable PostgreSQL harness: installation 13/13 passed; merchant bootstrap service 2/2 passed; billing read 1/1 passed; recurring subscription 7/7 passed; recovery-credit purchase 8/9 passed, then the harness exited non-zero on the untouched test `src/billing/commands/recovery-credit-purchase-command.postgres.test.ts` (“PostgreSQL catalogue validation hides foreign bundles and rejects non-FIXED or non-USD offers”, missing expected rejection). The failure is outside this task's changed files; no broader PostgreSQL pass is claimed.
- `git diff --check` — passed in the implementation worktree before report update; the parent task worktree was clean and passed `git diff --check` before this edit.
- Canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-010`, branch `task/ARCH-041-API-010`, clean before report update at claim commit `d84b51256`, published to `origin/task/ARCH-041-API-010`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-010`, branch `task/ARCH-041-API-010`, clean at implementation commit `3b68ec16f4e30b7308dcd549bf63db2f2a375cd5`; that commit equals `origin/task/ARCH-041-API-010` and is one commit ahead of `origin/main` by design.
- Both worktrees report the initialized recursive `database` submodule at `139765042baad3901682cfe9c54a3d6bba73e75c`. Validation runtime: Node `v24.21.0`, npm `11.19.0`.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

No task-scope implementation issues remain. The composite PostgreSQL harness failure described above is in an untouched recovery-credit purchase test and should be assessed separately; the bootstrap PostgreSQL tests passed.

### Architectural Concerns

None identified. The unrelated composite-harness failure is recorded above and does not alter this route-only task scope.

## Architect Review

### Review Status

Pending.

### Review Notes

No separate architect review has been recorded. Developer self-review accepted Attempt 1; the user has not invoked the explicit completion action.

### Reviewed Files

The four implementation paths listed in Files Changed, reviewed against `origin/main` at `97861de` and the task requirements.

### Validation Reviewed

Focused API-001/bootstrap suite (35/35), full `npm test` (394 passed, 0 failed, 42 gated skips), typecheck, lint, build and `git diff --check` passed. The disposable PostgreSQL harness passed the bootstrap suite (2/2) but later failed in the unrelated recovery-credit purchase suite as detailed above.

### Architecture Conformance

Conforms to the bounded route-ownership extraction in ARCH-041. No endpoint, DTO, response, auth policy, persistence behavior or unrelated task was changed; bootstrap remains authenticated, tenant-scoped and side-effect free.

### Follow-up

Await an explicit `/moda_developer_update ARCH-041-API-010 complete` before recording developer completion. Do not start enabled API-011 or update an architecture `_index.md`.

## Developer Self-Review

### Review Status

Accepted — Attempt 1 meets the defined scope and acceptance criteria. All task-scoped checks passed; the unrelated PostgreSQL harness failure is disclosed above. `completion_mode: developer` remains unchanged, and explicit completion is pending.

### Reviewed Files

All four implementation paths listed in Files Changed, including the diff from `origin/main` at `97861de` to `3b68ec16f4e30b7308dcd549bf63db2f2a375cd5`.

### Validation Reviewed

Focused API-001/bootstrap route, service and OpenAPI tests (35/35); full `npm test` (436 total, 394 passed, 0 failed, 42 PostgreSQL-gated skips); typecheck; lint; build; implementation diff check; and disposable PostgreSQL bootstrap service tests (2/2). The broader disposable harness's unrelated recovery-credit failure is recorded in Validation Results.

### Architecture Conformance

Conforms to the route-ownership-only change. Authentication, tenant binding, query rejection, response/error/logging contracts, no-store behavior and read-only service behavior remain intact. No out-of-scope endpoint or persistence work was added.

### Follow-up

Task is in `review` with Attempt 1 unchanged. Await the developer's explicit completion invocation; no enabled task was started.
