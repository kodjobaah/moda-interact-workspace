---
id: ARCH-041-API-011
architecture_id: ARCH-041
title: Extract merchant store-context HTTP route
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 62
executor: null
claimed_at: null
attempt: 1
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
- **Definition state:** materialised on parent branch `task/ARCH-041-API-011` in the canonical parent task worktree.
- **Task state:** `ready` on the current canonical baseline after API-010 became Complete; the launcher re-gates explicit dependencies before each attempt.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-041-API-011` for this ready task. Execution and completion ownership are taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`. Scope, dependency, acceptance criteria and validation requirements are unchanged. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.

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

- [x] Extract route-specific parser/controller into `src/merchant/store-context/`.
- [x] Update router delegation and focused route tests.
- [x] Run invalid/oversized body, abort/stream failure, conflict and success/no-content cases.
- [x] Run API-001 and existing store-context PostgreSQL tests.

## Interfaces / Contracts

`PUT /v1/merchant/store-context`, `openapi/merchant-store-context-v1.yaml`, `MerchantStoreContextService`, `isMerchantStoreContextSnapshot`, existing principal. No schema/contract changes.

## Dependencies

- `ARCH-041-API-010` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-014` — auth imports are reconciled after all established feature route extractions.

## Acceptance Criteria

- [x] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [x] Woo installation router no longer directly handles store-context PUT.
- [x] 204, 400, 401, 409 and 500 cases keep identical bounded responses and no-store/`nosniff` headers.
- [x] Existing persistence tests show the same authorised shop context update and foreign shop failure.

## Validation

- [x] Verify new unit tests through the existing `npm test` globs; run PostgreSQL integration cases using an explicit disposable database harness and record results separately.
- [x] `src/merchant/store-context/routes.test.ts`, store-context service tests and conditional PostgreSQL test when database is provisioned.
- [x] `npm run typecheck` (includes Prisma generate).
- [x] `npm run lint`.
- [x] `npm test` (existing declared script).
- [x] `npm run build`.
- [x] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/merchant/store-context/routes.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/integration/merchant/store-context/update.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse existing store-context service, Woo installation route and PostgreSQL suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Do not reuse generic request-body primitives until API-013 has proven semantic equality; moving a parser wholesale with tests is preferable to accidental acceptance widening.

## Completion Report

### Status

Complete — Attempt 1 claimed by the developer at 2026-10-16T18:58:19Z and explicitly completed by the developer. Developer completion mode is retained.

### Files Changed

Implementation commit `53bc0ee50a0611e8b122d288cda4cb4b33e8f4c5` changes:

- `src/merchant/store-context/request.ts` (new strict bounded request parser)
- `src/merchant/store-context/routes.ts` (new authenticated feature route)
- `src/woocommerce/installation/routes.ts` (delegates store-context PUT)
- `src/merchant/store-context/openapi-contract.test.ts` (imports route path from feature owner)
- `tests/unit/merchant/store-context/routes.test.ts` (new extracted-route cases)

No schema, migration, shared package, background, provider or unrelated runtime changes.

### Work Completed

Extracted the authenticated `PUT /v1/merchant/store-context` handler and strict bounded JSON parser into `src/merchant/store-context/`. The installation router delegates after its existing connection/auth-probe handlers and before billing routes. The extracted route retains authentication-before-body/query validation, strict content-type/encoding/length and UTF-8 rules, bounded streaming, exact success/error response behavior, tenant conflict mapping, no-store/`nosniff` headers and structured bounded logs. The authenticated principal remains the sole tenant identity; service persistence behavior is unchanged.

### Validation Results

Validation results:

- Focused route, existing installation route, store-context service and OpenAPI tests: `node --import tsx --test --test-concurrency=1 tests/unit/merchant/store-context/routes.test.ts src/merchant/store-context/routes.test.ts src/merchant/store-context/store-context.service.test.ts src/merchant/store-context/openapi-contract.test.ts src/woocommerce/installation/routes.test.ts` — 36 passed, 0 failed.
- Store-context PostgreSQL persistence: an invocation-owned disposable `pgvector/pgvector:pg17` container with a random database/user/password and loopback-only ephemeral port; `CREATE EXTENSION vector`; `npx prisma db push --schema database/prisma/schema.prisma --skip-generate --accept-data-loss`; then `WOO_INSTALLATION_TEST_DATABASE_URL=<disposable URL> node --import tsx --test --test-concurrency=1 src/merchant/store-context/store-context.service.postgres.test.ts` — 1 passed, 0 failed. The temporary database/container was removed after the run. This validates existing persistence behavior, not migration constraints.
- `npm run typecheck` — passed; Prisma Client generated.
- `npm run lint` — passed with `--max-warnings=0`.
- `npm test` — 443 tests, 401 passed, 0 failed, 42 database-gated skipped. The API-001 characterization and normal unit/regression suites ran under the declared globs.
- `npm run build` — passed.
- `git diff --check origin/main...HEAD` — passed.
- `npm run test:integration` — one unrelated existing recovery-credit PostgreSQL case failed (`recovery-credit-purchase-command.postgres.test.ts`, “Missing expected rejection”); the harness stopped before reaching store-context. The failing billing test and implementation are unchanged from `origin/main`. The task-required store-context PostgreSQL test was then run independently and passed as reported above. The temporary harness container cleaned itself up.
- Canonical worktree evidence: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-011` is clean before this report edit on `task/ARCH-041-API-011`, commit `5ac98b5c0342a77b07aea1f73df67e688e30542e`, equal to `origin/task/ARCH-041-API-011`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-011` is clean on the same branch at `53bc0ee50a0611e8b122d288cda4cb4b33e8f4c5`, equal to `origin/task/ARCH-041-API-011`. `origin/main` is an ancestor of both task tips. The implementation repository's recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c` (`heads/main`). The implementation branch's local tracking display references `origin/main`; publication was verified directly against the task remote ref. API-010 is `complete` on the canonical baseline and satisfied the declared dependency at claim.

### Deviations

The aggregate `npm run test:integration` invocation encountered the unrelated recovery-credit billing PostgreSQL failure described above. No API-011 changed file or store-context test failed. No scope deviation was made.

### Assumptions

The 2026-10-16 uploaded ZIP was treated as a snapshot only. The live task route was re-resolved; dependency API-010 is Complete on the canonical parent baseline; implementation and parent state were checked in their launcher-resolved task worktrees.

### Unresolved Issues

The aggregate PostgreSQL harness has the unrelated recovery-credit failure detailed in Validation Results. No task-scoped issue remains; API-011's own persistence case passed against the disposable database.

### Architectural Concerns

Return any contract/ownership/security/data/queue or new infrastructure gap to `moda_architect`; do not independently widen this task.

## Architect Review

### Review Status

Developer self-review passed; the task is returned to the architect for review. No separate architect acceptance is represented here.

### Review Notes

Developer self-review has inspected the implementation diff and validation. A separate architect decision remains pending.

### Reviewed Files

`src/merchant/store-context/request.ts`, `src/merchant/store-context/routes.ts`, `src/woocommerce/installation/routes.ts`, `src/merchant/store-context/openapi-contract.test.ts`, and `tests/unit/merchant/store-context/routes.test.ts`.

### Validation Reviewed

See exact commands, pass/skip counts and the unrelated integration-harness failure in the Completion Report above.

### Architecture Conformance

Developer self-review finds the extraction bounded to the existing store-context HTTP operation. No endpoint, HTTP contract, auth policy, persistence behavior, schema or unrelated task changed. Architect assessment remains pending.

### Follow-up

Architect review was not separately evidenced in this update. The developer supplied the acceptance statement “Architect Review Accepted”; see the Developer Completion Decision below. API-014 is not started.

## Developer Completion Decision

### Decision

Complete — the developer explicitly requested completion of `ARCH-041-API-011` and supplied the acceptance text “Architect Review Accepted.” Attempt 1 is retained; `executor` and `claimed_at` remain null.

### Review Evidence

The durable Developer Self-Review above passed. This completion record captures the developer-supplied acceptance statement; it does not claim a separate architect review process or review artifact beyond the evidence recorded in this task report.

### Dependency Frontier

API-014's declared dependencies API-003, API-005, API-007 and API-011 are now all `complete`. API-014 remains unclaimed: its portable definition states that it is not materialised, and no API-014 task worktree or branch is registered in the canonical workspace. Materialize and re-gate it through the canonical task workflow before claiming. No API-014 files or branches were changed.

## Developer Self-Review

### Review Status

Passed — Attempt 1 meets the task scope and acceptance criteria. Focused route tests, the API-001 `npm test` regression suite, store-context PostgreSQL persistence, typecheck, lint, build and diff checks passed. The aggregate PostgreSQL harness failure is disclosed and is isolated to an unchanged recovery-credit test. Explicit developer completion remains pending.

### Reviewed Files

All five implementation paths listed above, including the diff from `origin/main` to `53bc0ee50a0611e8b122d288cda4cb4b33e8f4c5`.

### Validation Reviewed

Focused API-011/regression tests (36/36); isolated store-context PostgreSQL persistence (1/1); `npm run typecheck`; `npm run lint`; `npm test` (401 passed, 42 skipped, 0 failed); `npm run build`; and `git diff --check`. `npm run test:integration` had one unrelated unchanged recovery-credit test failure, recorded in Validation Results.

### Architecture Conformance

Conforms to the bounded route extraction. No wire semantics, schema, tenant/auth behavior, persistence contract or out-of-scope repository was changed.

### Follow-up

Return to `moda_architect` for review. Because `completion_mode: developer`, explicit `/moda_developer_update ARCH-041-API-011 complete` remains pending.
