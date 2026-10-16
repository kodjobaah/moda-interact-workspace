---
id: ARCH-041-API-008
architecture_id: ARCH-041
title: Extract authenticated billing read HTTP routes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-041-API-001
enables:
  - ARCH-041-API-009
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-008 — Extract authenticated billing read HTTP routes

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-008` in the canonical parent task worktree.
- **Task state:** `complete`, `execution_mode: developer`, `completion_mode: developer`; Attempt 1 is accepted and explicitly completed by the developer. The canonical launcher verified the live API-001 dependency as `complete` before the attempt.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-041-API-008`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`, and the task scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 was claimed after canonical worktree preparation and dependency verification.

## Objective

Move the billing presentation and plan-catalogue GET handlers out of the Woo installation router into an independently testable billing HTTP read router.

## Context

`src/woocommerce/installation/routes.ts` directly handles `GET /v1/billing` and `GET /v1/billing/plans` even though domain read services and schemas already exist. This task begins the route-extraction stream **before new API feature work**, using the endpoints that actually exist in the execution baseline. Outstanding ARCH-026/035/040 feature tasks are not prerequisites.

## Scope

- Extract exactly the two GET handlers, their strict query/body rules, authentication and response/error mapping into `src/billing/`-owned HTTP route module.
- Wire the extracted router as a delegated handler without yet redesigning `src/server.ts` composition (API-012 owns final unnesting).
- Keep existing purchase-history `GET /v1/billing/recovery-credit-purchases` in its already separate handler.
- Preserve logger event names, fields, duration, response validator and status codes from existing implementation.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Before touching routing, compare the API-001 path+method/security inventory with the **routes actually served by the execution baseline**, including existing ARCH-026/035/036/040 code where present. Add missing unit characterization for authorized/denied paths, status/error shapes, wrong methods and GET/POST overlaps. Record inspected routes and relevant task states in the Completion Report; source presence is not evidence that a separate task was accepted.
- Only `ARCH-041-API-001` gates execution. Do **not** wait for unfinished feature tasks, implement their proposed endpoints, or silently adopt unfinished source changes. If another active task is concurrently editing the same routing files, stop and coordinate the collision with `moda_architect` before proceeding.
- Unmatched methods/paths must return `false`, allowing the next router to handle them; authenticated reads must use the principal, not caller-supplied tenant keys.
- Keep strict `locale` cardinality and unsupported query/body rejection; no billing service query/projection logic changes.
- All established v1 OpenAPI paths, request headers, result schemas and no-store response headers remain unchanged.

## Work Items

- [x] Refresh API-001 route characterization against the existing HTTP handlers in the execution baseline, and add regression cases under `tests/unit/http/` for any currently served route missing from that coverage. The completed API-001 inventory and cross-router suite were compared with the live `origin/main` baseline; the existing anchors covered the route/method/auth cases, so no duplicate test was needed in `tests/unit/http/`.

- [x] Extract the billing presentation and plan-catalogue read handler blocks into focused billing route file(s).
- [x] Update only the minimal necessary Woo installation-router delegation and injection.
- [x] Add route-parity tests for expected success, invalid query/body, auth failure, integrity/catalogue failure, and unrelated/method mismatch.
- [x] Run API-001 characterization and existing billing/installation route tests.

## Interfaces / Contracts

`GET /v1/billing`, `GET /v1/billing/plans` and `openapi/woocommerce-billing-presentation-v1.yaml`; producer `moda-interact-api`, consumer Woo PHP client. Read service constructor/response DTO remains the established API contract. This task changes module ownership only.

## Dependencies

- `ARCH-041-API-001` — Complete in the reviewed snapshot; must remain `complete` when the launcher re-gates the task. No external feature task is a prerequisite.

## Enables

- `ARCH-041-API-009`

## Acceptance Criteria

- [x] Every route currently served by the API (including existing ARCH-026/035/036/040 implementations, if present) is inventoried and either characterized already or covered by new path+method/security/denial assertions before any routing change.

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] `src/woocommerce/installation/routes.ts` no longer contains those GET handlers and the same HTTP contract is served by a billing read router.
- [x] Tests prove no route collision or auth/query regression.
- [x] No database/provider/business changes or additional HTTP endpoints.
- [x] No unfinished feature task is implemented as part of this refactor, and no external feature task is required to reach Complete before API-008 starts.

## Validation

- [x] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); no PostgreSQL integration cases were added, so no database harness was required.
- [x] Focused existing `src/woocommerce/installation/routes.test.ts`, billing schema/OpenAPI tests and API-001 cross-router test suite.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-routes.test.ts`, `tests/unit/billing/presentation/catalogue-routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing Woo installation routes, billing schema/OpenAPI and API-001 characterization tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Refactor-first coordination: preserve all already-served handlers in the execution baseline while leaving unfinished ARCH-026/035/040 feature requirements for later tasks. Future feature work resumes after ARCH-041 integrated validation by a separate developer/architect coordination decision; this task does not modify their YAML statuses. Keep billing plan catalogue within the billing domain and retain the existing `WooInstallationAuthenticator` until API-014.

## Completion Report

### Status

In Review — Attempt 1 passed developer self-review. `completion_mode: developer` is retained, so explicit developer completion remains pending. Attempt 0 review history is preserved below.

### Files Changed

Implementation commit `3342fc23ba75ac7e2285c17e05b04c2b03c2ae09` changes:

- `src/billing/presentation/routes.ts`
- `src/woocommerce/installation/routes.ts`
- `tests/unit/billing/presentation/billing-routes.test.ts`
- `tests/unit/billing/presentation/catalogue-routes.test.ts`
- `tests/unit/billing/presentation/route-fixtures.ts`

### Work Completed

Extracted the authenticated billing presentation and plan-catalogue GET handlers into a focused billing read router. The Woo installation router now delegates to it before continuing with its remaining routes; purchase-history GET and purchase-command POST remain separately owned. Existing principal-based tenant selection, strict query/body handling, response validation, status/error mapping, logger names/fields, and no-store response headers are preserved. Added focused route tests covering success, authentication, invalid query/body, schema/service failures, and fall-through for unrelated paths and methods.

Before the route edit, compared the completed API-001 route/method/security inventory in `tests/contracts/http-billing-security-baseline.md` and its `tests/unit/http/route-dispatch.test.ts` coverage with the live `origin/main` execution baseline. The inventory already covered served paths and methods, including purchase-history GET versus purchase POST; no uncovered route required a duplicate characterization test. Relevant non-gating task states at review: `ARCH-026-API-006` complete; `ARCH-035-API-013` review; `ARCH-036-API-001` superseded; `ARCH-040-API-002`, `API-003`, and `API-004` pending. No feature work from those tasks was added.

### Validation Results

All required checks passed on the canonical implementation worktree:

- Focused route characterization: `./node_modules/.bin/tsx --test src/woocommerce/installation/routes.test.ts src/billing/presentation/billing-read.service.test.ts src/billing/presentation/plan-catalogue-read.service.test.ts tests/unit/billing/presentation/billing-routes.test.ts tests/unit/billing/presentation/catalogue-routes.test.ts tests/unit/http/route-dispatch.test.ts` — 51 passed, 0 failed.
- `npm run typecheck` — passed; Prisma Client generated.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm test` — final rerun: 420 tests, 378 passed, 0 failed, 42 database-gated skips. An earlier full-suite run had one transient `ECONNRESET` in the unchanged Woo webhook body-boundary test; the isolated webhook file passed 8/8 and the full-suite rerun passed.
- `npm run build` — passed.
- `git diff --check origin/main...HEAD` — passed.
- No PostgreSQL integration case was added by this route-only change; no PostgreSQL runner was needed. The 42 existing database-gated skips are not counted as database validation.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-008` is clean on `task/ARCH-041-API-008`, commit `7c25bc0fa83f870b7c0700e1b5e0581255ba391b`, equal to `origin/task/ARCH-041-API-008`; its base `origin/main` is `84ba39e14e4ac8e9f020d67271e031d123de108a`.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-008` is clean on `task/ARCH-041-API-008`, implementation commit `3342fc23ba75ac7e2285c17e05b04c2b03c2ae09`, equal to `origin/task/ARCH-041-API-008`; base `origin/main` is `5649da212690248b65e3a7bb08e57ff382490b72`. Recursive `database` submodule is initialized at gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.

### Deviations

None.

### Assumptions

The 2026-10-16 00:01:47 uploaded ZIP is a **snapshot only**. At execution the canonical Git mainline, active task state and accepted dependencies must be rechecked; do not assume this snapshot represents the live developer worktree.

### Unresolved Issues

No unresolved task-scope or implementation issues. The full-suite transient reset did not reproduce in isolation or on the full-suite rerun.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Pending.

### Review Notes

No separate architect review is recorded. The developer self-review passed and the developer explicitly completed Attempt 1 below.

### Reviewed Files

None — review will inspect the exact source diff and task/report branches.

### Validation Reviewed

The developer self-review recorded focused route tests (51/51), typecheck, lint, full suite (378 passed, 0 failed, 42 database-gated skips), build and diff check as passing.

### Architecture Conformance

The developer self-review records conformance to the API-008 module-ownership-only refactor. No separate architect assessment is recorded here.

### Follow-up

No enabled task was started. API-009 remains pending on its current parent `origin/main` baseline until API-008 completion is integrated there.

## Developer Self-Review

### Review Status

Passed — Attempt 1 satisfies the defined route-extraction scope and acceptance criteria. The developer explicitly completed the accepted attempt; `completion_mode: developer` remains unchanged.

### Reviewed Files

All five implementation paths listed in Files Changed, reviewed against `origin/main` and the API-001 HTTP/security characterization baseline.

### Validation Reviewed

Focused route suites: 51/51 passed. Typecheck, lint, build and diff check passed. Final full suite: 378 passed, 0 failed, 42 database-gated skips. The transient initial webhook `ECONNRESET` passed in isolated and full-suite reruns.

### Architecture Conformance

Conforms to API-008's module-ownership-only refactor. No endpoint, wire contract, business/service behavior, schema, provider, database or unrelated task status was changed. Authenticated reads continue to use the principal; unrelated paths and methods fall through.

### Follow-up

The developer explicitly completed Attempt 1 below. API-009 remains pending in its current parent `origin/main` baseline because that baseline still records API-008 as ready; do not promote it until the completed API-008 task record is integrated by the developer.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-041-API-008 complete`. Attempt 1 remains the accepted attempt; status is `complete`, with `executor: null` and `claimed_at: null`. The implementation and parent task branches remain separate from `main`; no merge was performed.

### Dependency Frontier

- `ARCH-041-API-009` is the only declared downstream task and depends solely on API-008. Its current canonical parent task branch was created from parent `origin/main` `84ba39e14e4ac8e9f020d67271e031d123de108a`, where API-008 is still `ready`. Therefore API-009 remains `pending` on that baseline; it must not be marked `ready` until the developer integrates the completed API-008 task record into the parent mainline or otherwise updates the canonical dependency baseline. No implementation worktree or claim was created for API-009.
- No other task or `_index.md` was changed. No implementation or parent task branch was merged to `main`.
