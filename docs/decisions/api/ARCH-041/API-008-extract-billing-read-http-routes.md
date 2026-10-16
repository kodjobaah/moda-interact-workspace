---
id: ARCH-041-API-008
architecture_id: ARCH-041
title: Extract authenticated billing read HTTP routes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-001
  - ARCH-026-API-005
  - ARCH-026-API-006
  - ARCH-026-API-008
  - ARCH-035-API-002
  - ARCH-035-API-009
  - ARCH-035-API-013
  - ARCH-036-API-004
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
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
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `pending` according to explicit dependencies in this snapshot; readiness is re-gated by the launcher before an attempt.

## Objective

Move the billing presentation and plan-catalogue GET handlers out of the Woo installation router into an independently testable billing HTTP read router.

## Context

`src/woocommerce/installation/routes.ts` directly handles `GET /v1/billing` and `GET /v1/billing/plans` even though domain read services and schemas already exist. This task begins the structurally disruptive route stream only after existing API feature work using the same route/composition files is accepted.

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

- Before start, compare current source with accepted `ARCH-026/035/036/040` implementations and ensure each exact external dependency is **complete**, not merely review/present in the ZIP. `ARCH-036-API-004` was already Complete at Attempt 2 in the 2026-10-16 snapshot; it is a satisfied historical gate, **not** an outstanding blocker. Recheck live task YAML.
- Unmatched methods/paths must return `false`, allowing the next router to handle them; authenticated reads must use the principal, not caller-supplied tenant keys.
- Keep strict `locale` cardinality and unsupported query/body rejection; no billing service query/projection logic changes.
- All established v1 OpenAPI paths, request headers, result schemas and no-store response headers remain unchanged.

## Work Items

- [ ] Extract the billing presentation and plan-catalogue read handler blocks into focused billing route file(s).
- [ ] Update only the minimal necessary Woo installation-router delegation and injection.
- [ ] Add route-parity tests for expected success, invalid query/body, auth failure, integrity/catalogue failure, and unrelated/method mismatch.
- [ ] Run API-001 characterization and existing billing/installation route tests.

## Interfaces / Contracts

`GET /v1/billing`, `GET /v1/billing/plans` and `openapi/woocommerce-billing-presentation-v1.yaml`; producer `moda-interact-api`, consumer Woo PHP client. Read service constructor/response DTO remains the established API contract. This task changes module ownership only.

## Dependencies

- `ARCH-041-API-001` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-026-API-005` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-026-API-006` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-026-API-008` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-035-API-002` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-035-API-009` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-035-API-013` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-036-API-004` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-040-API-002` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-040-API-003` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.
- `ARCH-040-API-004` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-009`

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] `src/woocommerce/installation/routes.ts` no longer contains those GET handlers and the same HTTP contract is served by a billing read router.
- [ ] Tests prove no route collision or auth/query regression.
- [ ] No database/provider/business changes or additional HTTP endpoints.
- [ ] Canonical open feature task prerequisites were architect accepted before execution started.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] Focused existing `src/woocommerce/installation/routes.test.ts`, billing schema/OpenAPI tests and API-001 cross-router test suite.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/billing/presentation/billing-routes.test.ts`, `tests/unit/billing/presentation/catalogue-routes.test.ts`; filenames are examples, not compulsory placeholder files. Reuse existing Woo installation routes, billing schema/OpenAPI and API-001 characterization tests. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

The external dependency list is intentionally conservative because `index.ts` and installation-router dispatch are used by open feature tasks. If a listed task is superseded rather than completed, stop and ask the architect to reconcile the dependency formally; never silently treat superseded as complete. Keep billing plan catalog within the billing domain and retain existing `WooInstallationAuthenticator`.

## Completion Report

### Status

Not Started — portable definition; no implementation attempt.

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
