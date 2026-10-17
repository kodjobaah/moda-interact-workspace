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
status: complete
priority: 68
executor: null
claimed_at: null
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
- **Task state:** `complete`, Attempt 1, developer-executed; `ARCH-041-API-012` is Complete. Developer self-review passed and explicit developer completion is recorded below. The Architect Review section remains unchanged.

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

- [x] Document a table of mechanically equivalent HTTP helpers, existing use of `src/http/route-handler.ts`, and explicitly excluded security-sensitive differing cases in Completion Report.
- [x] Extract only the common API-local helper(s) and update import sites.
- [x] Add direct helper tests for malformed UTF-8, abort, oversized streaming content, multi-value header and completed/destroyed responses.
- [x] Run domain route parity and API-001 characterization suites.
- [x] Reconcile test relocation and reference paths without changing assertions; confirm `src/` contains zero test suites.
- [x] Verify the actual factory composition registers the accepted routes and their trust boundaries.
- [x] Register and run all 17 PostgreSQL suites in the standard integration chain, with migration-backed evidence where required.

## Interfaces / Contracts

API-local `node:http` request/response mechanics only; consume the canonical handler interface produced by API-012, do not redefine it. No cross-service runtime wire contract or generic logger. Existing OpenAPI and error JSON shapes remain unchanged.

## Dependencies

- `ARCH-041-API-012` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] New and relocated tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/`; no tests remain in `src/`; assertions and required fixtures are preserved.
- [x] `src/http/route-handler.ts` from API-012 remains the single canonical handler contract; no duplicated generic helper remains *within the selected equivalent consumers*; incompatible security-sensitive mechanics remain separate.
- [x] Request parsing, response codes/headers, credential validation and endpoint matching retain exact baseline behaviour.
- [x] Helper tests cover truncation, stream abort, over-limit and duplicate headers without leaking values.
- [x] No unrelated business controllers, webhook verification protocols, authentication policy, migrations or shared service contracts change.
- [x] Every PostgreSQL integration suite has a standard runner registration and the migration-required suites execute under `prisma migrate deploy`.
- [x] Real domain-factory tests cover the existing route inventory independently of synthetic route-handler checks.

## Validation

- [x] Verify unit/contract tests via `npm test` (`tests/unit/**/*.test.ts` only); execute and record `npm run test:integration` separately, including the billing, Woo, merchant, discount-offers and provider-outcome PostgreSQL suites. Never count PostgreSQL checks as covered by `npm test`.
- [x] Focused new API HTTP helper test suite plus API-001 characterization and existing Woo installation/billing/merchant route suites.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**2026-10-16 test-layout scope amendment:** The original architecture permitted legacy colocated tests, but the developer subsequently directed relocation of all remaining suites. `npm test` now discovers `tests/unit/**/*.test.ts`; `tests/integration/` is invoked explicitly through disposable PostgreSQL scripts. The relevant migration-backed suites must execute with `prisma migrate deploy`. The user also requested the bounded cleanup uncovered by the deep source audit. This amendment changes neither API surface nor domain business logic. It does not itself record validation success or a completion decision.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not chase arbitrary source-file size targets; prefer semantic modules. If no two remaining helpers are actually equivalent, report that finding and ask architect to narrow or supersede this task instead of creating unnecessary duplication.

## Completion Report

### Status

Complete — Attempt 1. Developer self-review passed; all Work Items, Acceptance Criteria and Validation items are checked. The developer explicitly completed the task using the supplied wording “Architect Review Accepted”; the distinct Architect Review section remains as recorded, and no separate architect review artifact is asserted.

### Files Changed

The implementation commit range is `origin/main..task/ARCH-041-API-013` and contains the API-local HTTP helpers and route consumers, real route-composition and helper tests, relocation of all existing `src/**/*.test.ts` suites, PostgreSQL runner registration/harness updates, and the HTTP security characterization documentation. The final focused consolidation is commit `a24202a` (`src/woocommerce/rest-read/authorization.routes.ts` now consumes the shared raw-header counter).

### Work Completed

- Consolidated mechanically equivalent bounded-body reading/strict JSON decoding, raw-header multiplicity counting, and identical no-store JSON response writing into `src/http/body.ts`, `src/http/headers.ts`, and `src/http/response.ts`, retaining caller-specific size limits and error mapping.
- Removed the duplicate generic route-handler interfaces; production route registration and tests consume the `ApiRouteHandler` contract from `src/http/route-handler.ts`. Removed obsolete Woo installation route-constant aliases while retaining the active connect/probe constants.
- Added direct helper tests for exact and oversized bodies, malformed UTF-8/JSON, aborted/error streams, raw multi-value headers (including non-disclosure of duplicated credentials), and completed/destroyed responses.
- Added `tests/unit/composition/real-route-registration.test.ts`, which exercises production domain factories, accepted route registrations, authentication boundaries, callbacks/webhook precedence, and wrong-method fallthrough.
- Relocated the existing test suites into `tests/unit/` and `tests/integration/`; confirmed zero test files remain under `src/`. Git rename similarity and the full unit suite were checked to verify the moves retained the test contents and assertions.
- Registered all 17 PostgreSQL integration test files exactly once through the default integration runner chain; migration-backed runners use `prisma migrate deploy` where required.

HTTP helper equivalence and exclusions:

| Mechanic | Shared helper and migrated consumers | Deliberately retained separately |
| --- | --- | --- |
| Bounded request body and strict JSON decoding | `src/http/body.ts`; billing command, merchant store-context/category-selection, and Woo installation connect request parsing, with each caller supplying its established byte limit and 400/413 mapping | Woo REST-read callback retains its callback-specific stream/error path and 4 KiB credential-payload boundary; signed Woo billing webhook retains raw-byte signature verification. |
| Raw header multiplicity | `src/http/headers.ts`; billing, merchant request parsing, Woo installation, and Woo REST-read authorization (including the final `a24202a` deduplication) | No normalized-header fallback was introduced; endpoint-specific body-presence checks remain separate where their malformed/zero-length semantics differ. |
| JSON response writing | `src/http/response.ts` used for identical no-store JSON writers across billing and merchant route consumers | Woo REST-read keeps CSP/referrer protections; recoveries keeps `private, no-store`; server health/404 writers preserve their existing exact header contract. |
| Route handler interface | The existing API-012 `src/http/route-handler.ts` `ApiRouteHandler` is the sole interface; domain factories and dispatcher consume it. | No endpoint-specific handler behavior or security policy is merged into the interface. |

### Validation Results

- `npm test` — passed, 419 tests; 419 passed, 0 failed. Includes the integration-runner registration assertion.
- API-001 characterization and Woo installation authentication: `node --import tsx --test tests/unit/http/route-dispatch.test.ts tests/unit/auth/woo-installation/authentication-contract.test.ts` — passed, 8 tests.
- Final shared-header focused regression: `node --import tsx --test tests/unit/woocommerce/rest-read/authorization.routes.test.ts tests/unit/woocommerce/rest-read/authorization.test.ts tests/unit/http/headers.test.ts` — passed, 15 tests.
- `npm run test:integration` — passed. All 17 discovered PostgreSQL integration test files are registered once and the complete standard runner chain completed; migration-backed runners successfully applied migrations.
- `npm run typecheck` — passed (Prisma client generation and TypeScript check).
- `npm run lint` — passed.
- `npm run build` — passed (Prisma client generation and production TypeScript build).
- `git diff --check` — passed after the final source change.
- Final review-state check: parent and implementation worktrees are clean; implementation commit is pushed to `origin/task/ARCH-041-API-013`; recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.

### Deviations

No implementation deviation from the architect-approved scope reconciliation. Callback streaming/signature validation and response security headers were intentionally kept separate where their contracts differ.

### Assumptions

The uploaded ZIP was treated only as a source snapshot; implementation and validation were reconciled against the canonical API-013 task worktree and live task branch.

### Unresolved Issues

None at definition time. Execution-dependent blockers and newly discovered constraints must be recorded.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Developer Execution Ownership Amendment

The developer explicitly requested preparation through `/moda_developer_create ARCH-041-API-013`. Execution ownership and completion authority were taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`. Scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher subsequently claimed Attempt 1 after worktree synchronization and dependency verification.

## Developer Self-Review

### Review Status

Passed — Attempt 1 satisfies the defined Work Items and Acceptance Criteria. The final remaining shared raw-header implementation was consolidated in `a24202a`; required unit, focused characterization, PostgreSQL integration, typecheck, lint, build and diff validations passed. The developer's explicit completion decision is recorded below. This self-review does not claim a separate architect review.

### Reviewed Files

All implementation changes in `origin/main..task/ARCH-041-API-013`, including helper modules and consumers, route composition, migrated test suites, integration runner scripts, and security characterization documentation.

### Validation Reviewed

See the exact commands and results in Completion Report / Validation Results. The standard integration chain separately exercised all 17 registered PostgreSQL test files; it is not counted as part of `npm test`.

### Architecture Conformance

The API-012 handler contract remains canonical; strict body/header parsing, route-specific limits, callback/webhook authentication, response security headers, and method fallthrough remain owned by their existing routes. No runtime dependency, database schema, shared contract, or unrelated business controller was added or changed.

### Follow-up

`ARCH-041-SYSTEM-TEST-001` remains pending and unclaimed under the system-test manual gate. No enabled task was started.

## Developer Completion Decision

### Decision

Complete — the developer explicitly invoked `/moda_developer_update ARCH-041-API-013 complete` and supplied the acceptance wording “Architect Review Accepted.” Attempt 1 is preserved; `executor` and `claimed_at` are null. `completion_mode: developer` remains unchanged.

### Review Evidence

The durable Developer Self-Review above passed, and all Work Items, Acceptance Criteria and Validation items are checked with results recorded in this report. The supplied acceptance wording is recorded as part of the developer's completion instruction; this record does not claim that a separate architect review process or artifact occurred. The Architect Review section below is preserved unchanged.

### Dependency Frontier

The direct dependencies API-003, API-005, API-007, API-012 and API-014 resolve `complete`. The enabled `ARCH-041-SYSTEM-TEST-001` remains `pending` and unclaimed under its manual system-test gate; its other explicit dependencies also resolve `complete`. No downstream task was promoted, claimed, or modified.

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
