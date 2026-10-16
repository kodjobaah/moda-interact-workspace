---
id: ARCH-041-API-011
architecture_id: ARCH-041
title: Extract merchant store-context HTTP route
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 62
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-041-API-010
enables:
  - ARCH-041-API-014
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-011 — Extract merchant store-context HTTP route

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `pending` according to explicit dependencies in this snapshot; readiness is re-gated by the launcher before an attempt.

## Objective

Extract `PUT /v1/merchant/store-context` into the merchant store-context domain while retaining its strict body validation, existing installation-generation guard and tenant conflict semantics.

## Context

The store-context service/schema already live in `src/merchant/store-context`, while `src/woocommerce/installation/routes.ts` handles HTTP request body, auth and errors. The endpoint is operationally distinct from bootstrap and deserves a separate bounded extraction.

## Scope

- Move the store-context HTTP request handler, bounded JSON parser and strict snapshot validation into a dedicated store-context routes module.
- Keep exact limits and content-type/encoding/length rules, UTF-8 validation, query rejection, bodyless 204 response and error mapping.
- Preserve installation/shop-scoped structured success/failure events and duration fields.
- Adjust delegation/injection only; application-wide composition follows in API-012.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- `MerchantStoreContextService.update` continues enforcing the authoritative Shop principal and conflict semantics.
- No alteration to store locale/default language semantics or to `Shop` writes.
- No tolerant fallback for malformed body, missing auth or different Shop.

## Work Items

- [ ] Extract route-specific parser/controller into `src/merchant/store-context/`.
- [ ] Update router delegation and focused route tests.
- [ ] Run invalid/oversized body, abort/stream failure, conflict and success/no-content cases.
- [ ] Run API-001 and existing store-context PostgreSQL tests.

## Interfaces / Contracts

`PUT /v1/merchant/store-context`, `openapi/merchant-store-context-v1.yaml`, `MerchantStoreContextService`, `isMerchantStoreContextSnapshot`, existing principal. No schema/contract changes.

## Dependencies

- `ARCH-041-API-010` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — auth imports are reconciled after all established feature route extractions.

## Acceptance Criteria

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] Woo installation router no longer directly handles store-context PUT.
- [ ] 204, 400, 401, 409 and 500 cases keep identical bounded responses and no-store/`nosniff` headers.
- [ ] Existing persistence tests show the same authorised shop context update and foreign shop failure.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] `src/merchant/store-context/routes.test.ts`, store-context service tests and conditional PostgreSQL tests when database is provisioned.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/merchant/store-context/routes.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/merchant/store-context/update.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing store-context service, Woo installation route and PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not reuse generic request-body primitives until API-013 has proven semantic equality; moving a parser wholesale with tests is preferable to accidental acceptance widening.

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
