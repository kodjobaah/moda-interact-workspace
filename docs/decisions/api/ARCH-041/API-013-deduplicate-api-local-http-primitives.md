---
id: ARCH-041-API-013
architecture_id: ARCH-041
title: Deduplicate proven API-local HTTP primitives
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 68
executor: developer
claimed_at: 2026-10-16T20:56:41Z
attempt: 1
depends_on:
  - ARCH-041-API-012
enables:
  - ARCH-041-SYSTEM-TEST-001
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-013 — Deduplicate proven API-local HTTP primitives

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on the canonical parent `task/ARCH-041-API-013` branch.
- **Task state:** `in_progress`, Attempt 1, developer-executed in the inspected snapshot; `ARCH-041-API-012` is Complete. Completion and architect acceptance remain outstanding.

## Objective

Consolidate only demonstrably identical low-level API HTTP parsing/response mechanics after the route split, without widening request acceptance.

## Context

Following API-008 through API-012, `src/http/route-handler.ts` already exists as the shared dispatch interface and domain route handlers are independent, but may retain copies of the original `readBoundedBody`, `singleHeader`, `requestHasBody`, JSON response/error writers and error helpers. Consolidation must be evidence-led rather than an all-purpose abstract HTTP framework.

## Scope

- Inventory duplicates in API-local route modules after API-012; choose only primitives with identical strict semantics across consumers. Preserve the `src/http/route-handler.ts` created by API-012. If no additional helper qualifies, return to `moda_architect` for task narrowing/supersession rather than inventing artificial `src/http/` modules.
- Extract bounded request-stream/body, raw-header multiplicity and response-header writers into small Node-only API-local modules, preserving route-specific maximum sizes and validators.
- Leave distinct endpoint parsing/error-envelope rules in their domain handlers; retain route-level no-store, `nosniff`, 204 and safe JSON semantics.
- Remove only confirmed duplicate implementations; do not force Woo callback signature/streaming paths onto incompatible helpers.
- **Architect-approved scope reconciliation for the developer-requested cleanup (2026-10-16):** migrate all remaining `src/**/*.test.ts` tests into `tests/unit/` or `tests/integration/` with assertions and domain semantics preserved; update import/fixture paths and explicit PostgreSQL runners.
- Complete bounded structural residue: replace the two duplicate generic route-handler interfaces, remove only the obsolete Woo installation route-constant aliases after moving test imports, reuse `sendNoStoreJson` only for identical response writers, add an actual factory-composition route regression, and register all existing PostgreSQL integration suites for standard execution. No speculative deletion of dormant private Woo product-read capability.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup outside the expressly requested test migration and bounded deep-review findings.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- Use current shared logging/crypto utilities rather than introducing a competing service logger or encryption mechanism.
- Preserve duplicate-header detection from raw headers, strict content-type/encoding/content-length and malformed/aborted body behaviour.
- Never accept an HTTP payload or credential that was rejected before this task.
- No new runtime dependency or cross-service Shared publication without a separately accepted task.

## Work Items

- [ ] Document a table of mechanically equivalent HTTP helpers, existing use of `src/http/route-handler.ts`, and explicitly excluded security-sensitive differing cases in Completion Report.
- [ ] Extract only the common API-local helper(s) and update import sites.
- [ ] Add direct helper tests for malformed UTF-8, abort, oversized streaming content, multi-value header and completed/destroyed responses.
- [ ] Run domain route parity and API-001 characterization suites.
- [ ] Reconcile test relocation and reference paths without changing assertions; confirm `src/` contains zero test suites.
- [ ] Verify the actual factory composition registers the accepted routes and their trust boundaries.
- [ ] Register and run all 17 PostgreSQL suites in the standard integration chain, with migration-backed evidence where required.

## Interfaces / Contracts

API-local `node:http` request/response mechanics only; consume the canonical handler interface produced by API-012, do not redefine it. No cross-service runtime wire contract or generic logger. Existing OpenAPI and error JSON shapes remain unchanged.

## Dependencies

- `ARCH-041-API-012` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] New and relocated tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/`; no tests remain in `src/`; assertions and required fixtures are preserved.
- [ ] `src/http/route-handler.ts` from API-012 remains the single canonical handler contract; no duplicated generic helper remains *within the selected equivalent consumers*; incompatible security-sensitive mechanics remain separate.
- [ ] Request parsing, response codes/headers, credential validation and endpoint matching retain exact baseline behaviour.
- [ ] Helper tests cover truncation, stream abort, over-limit and duplicate headers without leaking values.
- [ ] No unrelated business controllers, webhook verification protocols, authentication policy, migrations or shared service contracts change.
- [ ] Every PostgreSQL integration suite has a standard runner registration and the migration-required suites execute under `prisma migrate deploy`.
- [ ] Real domain-factory tests cover the existing route inventory independently of synthetic route-handler checks.

## Validation

- [ ] Verify unit/contract tests via `npm test` (`tests/unit/**/*.test.ts` only); execute and record `npm run test:integration` separately, including the billing, Woo, merchant, discount-offers and provider-outcome PostgreSQL suites. Never count PostgreSQL checks as covered by `npm test`.
- [ ] Focused new API HTTP helper test suite plus API-001 characterization and existing Woo installation/billing/merchant route suites.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**2026-10-16 test-layout scope amendment:** The original architecture permitted legacy colocated tests, but the developer subsequently directed relocation of all remaining suites. `npm test` now discovers `tests/unit/**/*.test.ts`; `tests/integration/` is invoked explicitly through disposable PostgreSQL scripts. The relevant migration-backed suites must execute with `prisma migrate deploy`. The user also requested the bounded cleanup uncovered by the deep source audit. This amendment changes neither API surface nor domain business logic. It does not itself record validation success or a completion decision.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not chase arbitrary source-file size targets; prefer semantic modules. If no two remaining helpers are actually equivalent, report that finding and ask architect to narrow or supersede this task instead of creating unnecessary duplication.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-16T20:56:41Z. Attempt 0 review history is preserved below.

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

## Developer Execution Ownership Amendment

The developer explicitly requested preparation through `/moda_developer_create ARCH-041-API-013`. Execution ownership and completion authority are taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.

## Architect Review

### Review Status

Pending.

### Review Notes

Source-level deep review of the uploaded API-013 snapshot identified remaining compatible no-store JSON writers, duplicate route interfaces, obsolete Woo re-exports and four integration suites outside default runners. Targeted patches and actual validation are required; no architect acceptance decision is made here.

### Reviewed Files

Deep-review findings in the 2026-10-16 snapshot only; final review must inspect the applied source diffs and developer Completion Report.

### Validation Reviewed

Not run.

### Architecture Conformance

To be assessed against `ARCH-041`, the canonical task and actual implementation.

### Follow-up

Architect records Accepted / Changes Requested / Blocked and adjusts eligible dependencies only after review.
