---
id: ARCH-041-API-012
architecture_id: ARCH-041
title: Compose domain routers at the API server boundary
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 65
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-041-API-014
enables:
  - ARCH-041-API-013
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-012 — Compose domain routers at the API server boundary

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on the canonical parent `task/ARCH-041-API-012` branch and published with the task report.
- **Task state:** `complete`, Attempt 1; its sole explicit dependency, `ARCH-041-API-014`, was complete before the implementation attempt.

## Objective

Remove unrelated merchant/billing route delegation from Woo installation routing and register independently owned domain routes in an explicit top-level HTTP chain.

## Context

API-008 through API-011 extract the remaining billing and merchant handlers. `src/index.ts` and `src/server.ts` can then become a clear composition root and route dispatcher instead of using `createWooInstallationRoutes` as an umbrella router for all unrelated services. API-014 has already established the canonical `src/auth/woo-installation/` identity boundary, so this task must **consume** it rather than move auth a second time.

## Scope

- Define one API-local shared Node HTTP route interface at `src/http/route-handler.ts` with the existing `handle(IncomingMessage, ServerResponse): Promise<boolean>` semantics; adopt that exact type for server route registration without changing existing `false` fallthrough.
- Introduce a small explicit `src/composition/` dependency-assembly module (e.g. `merchant.ts`, `billing.ts`, `woocommerce.ts`, `routes.ts` as justified) and ordered HTTP handler collection wired from `src/index.ts` to `src/server.ts`. Only construct collaborators required by routes that exist in the execution baseline; no placeholder files or prospective feature endpoints.
- Register health, Woo REST-read authorisation/callback, signed billing webhook, all merchant handlers, billing handlers and finally install/connect/probe with correct method routing. Use the **actual served route inventory** characterized by API-008 and refreshed after API-011; do not synthesize handlers for pending ARCH-026/035/040 tasks.
- Keep domain services constructed once at startup, with injected Prisma client, config, authenticator and logger; do not construct per request.
- Preserve server start/shutdown idempotence, readiness deadline, error handling and signal shutdown behaviour.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.

## Requirements

- No new HTTP framework, reflection-based route discovery, global catch-all auth or generic provider credential handler.
- Preserve the route security matrix: public health, Woo site proof for connect, installation bearer/principal for merchant/billing and probe, HMAC-signed billing webhook, and one-time REST-read callback capabilities. No global authentication wrapper, no *new* auth implementation or policy: consume the authenticator and principal already relocated by API-014; no Woo PHP/Shopify changes.
- On routes that share a path but differ by method, respect each handler’s `false` result and never shadow GET with POST.
- No missing existing API route, including any already implemented under ARCH-026/035/036/040. Preserve canonical bearer principal/credential-version semantics and protect callback/webhook endpoints from installation-router fallthrough; do not add routes solely from pending feature specifications.

## Work Items

- [ ] Compare the routes actually served after API-011 and API-008 characterization updates with the proposed final composition; register every existing route and test its method, security boundary, denial and error fallthrough. Record coverage in the Completion Report.

- [ ] Establish `src/http/route-handler.ts` as a single narrow handler contract consumed by the top-level dispatcher and feature-owned routes.
- [ ] Move the nested merchant/billing route registry out of `createWooInstallationRoutes` and shrink the Woo installation router to connect/probe responsibility.
- [ ] Compose and inject domain handlers at the API application boundary, with explicit ordering and no duplicate registrations.
- [ ] Add `tests/unit/http/` dispatch-interface and `tests/unit/composition/` registration tests for all known route families, wrong method, error fallback, callbacks and health while preserving lifecycle tests.
- [ ] Run cross-router characterization and existing installed route suites.

## Interfaces / Contracts

Canonical API-local `src/http/route-handler.ts` with `handle(IncomingMessage, ServerResponse): Promise<boolean>`, existing route modules, `createApiRuntime` and API-014 Woo installation principal. No wire-contract/API OpenAPI changes.

## Dependencies

- `ARCH-041-API-014` — must be architect-accepted `complete`; `review`, `ready`, `pending` and `superseded` do **not** satisfy a dependency.

## Enables

- `ARCH-041-API-013`

## Acceptance Criteria

- [ ] Every endpoint already served at composition time has a registered handler and path+method/security characterization, regardless of its historical initiative; pending feature endpoints not yet implemented are not introduced. Callback and webhook guards and wrong-method fallthrough are preserved.

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] `src/composition/` and `src/http/route-handler.ts` exist with exercised, genuinely used production responsibilities; do not create placeholder files or a generic framework.
- [ ] Installation route factory accepts only its installation/auth-probe dependencies, not billing or unrelated merchant services.
- [ ] `src/index.ts` remains a bounded composition entrypoint; dependencies built once and correct routes registered.
- [ ] Every previously supported request/path/method continues to resolve with same status/body/headers/auth.
- [ ] Readiness/shutdown and callback-specific authentication isolation preserved.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] `src/server.test.ts`, API-001 characterization, all existing Woo/merchant/billing route tests, plus existing `npm run test:integration` if the required disposable PostgreSQL/Docker environment is available.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

The mandatory `src/http/route-handler.ts` is only a minimal TypeScript HTTP handler interface; API-013 owns any further strict body/header/response helper consolidation. Use the auth exports accepted in API-014 and preserve distinct connect/webhook/callback mechanisms. No re-authentication query or policy change is permitted.

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/composition/routes.test.ts`, `tests/unit/http/route-dispatch.test.ts` (extend the existing API-001 characterization suite if appropriate rather than duplicate it); filenames are examples, not compulsory placeholder files. Reuse existing `src/server.test.ts`, API-001 characterization and affected feature route suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

This is the integration boundary for earlier route extractions. Do not allow the architecture to imply that the new general router authenticates signed provider callbacks with Woo installation credentials. Record all handler registrations including any newly accepted ARCH-040 routes.

## Developer Execution Ownership Amendment

The developer explicitly requested preparation through `/moda_developer_create ARCH-041-API-012`. Execution ownership is changed from `agent` to `developer`, and completion authority from `automatic` to `developer`. `assigned_agent: moda_api`, `repository: moda-interact-api`, task scope, dependencies, acceptance criteria and validation requirements remain unchanged. This amendment does not represent implementation or architectural review.

## Completion Report

### Status

Complete — Attempt 1 implementation passed developer self-review, Architect Review was accepted as supplied with the explicit completion request, and the developer recorded completion on 2026-10-16. Attempt 0 review history is preserved below.

### Files Changed

15 files changed in implementation commit `f0f496f567fa577fc5c9902881b1cb810986d2d9`: added `src/http/route-handler.ts` and four `src/composition/` modules; updated `src/index.ts`, `src/server.ts`, and the Woo installation router; adjusted directly affected route tests; added `tests/unit/composition/routes.test.ts` and updated `tests/unit/http/route-dispatch.test.ts`. No API schema, endpoint contract, database, or cross-repository changes.

### Work Completed

Extracted a canonical `ApiRouteHandler` contract and moved app assembly to explicit billing, merchant, and Woo route factories. The top-level order places REST-read callbacks and signed billing webhook before merchant/billing routes and installation connect/probe last. Health endpoints remain handled directly by the server. The Woo installation router now handles only connect and auth probe. Services are constructed once at startup and injected into route factories. Composition characterization covers implemented route families, method collisions/fallthrough, callback and webhook precedence, health behavior, and bounded error handling.

### Validation Results

Passed focused command `npx tsx --test tests/unit/composition/routes.test.ts tests/unit/http/route-dispatch.test.ts src/server.test.ts src/woocommerce/installation/routes.test.ts src/billing/commands/routes.test.ts src/billing/presentation/routes.test.ts` (34/34).

Passed `npm test` (407 passed, 0 failed, 42 skipped; skips are conditional PostgreSQL cases), `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check origin/main...HEAD`.

Passed `npm run test:integration` with disposable PostgreSQL: Woo installation (13), bootstrap (2), store context (1), category reads (1), category writes (3), REST-read authorization (4), and ARCH-041 billing (17); 41 integration tests passed, 0 failed. Disposable infrastructure was cleaned up.

Implementation commit `f0f496f567fa577fc5c9902881b1cb810986d2d9` is published to `origin/task/ARCH-041-API-012`. The canonical parent task branch is synchronized and published; parent and implementation worktrees were clean at review. Launcher preparation recorded the canonical worktree paths, dependency gate and recursive-submodule synchronization evidence.

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

Accepted.

### Review Notes

The developer explicitly supplied “Architect Review Accepted” with the completion request. Acceptance is recorded against implementation commit `f0f496f567fa577fc5c9902881b1cb810986d2d9` and the validation evidence in the Completion Report; no additional architect review notes were supplied.

### Reviewed Files

`src/composition/billing.ts`, `merchant.ts`, `routes.ts`, `woocommerce.ts`, `src/http/route-handler.ts`, `src/index.ts`, `src/server.ts`, `src/woocommerce/installation/routes.ts`, affected route tests, and the API-012 task/report branch.

### Validation Reviewed

Reviewed focused composition/dispatch/server/Woo/billing tests (34/34), full `npm test` (407 passed, 0 failed, 42 skipped), `npm run typecheck`, `npm run lint`, `npm run build`, `git diff --check origin/main...HEAD`, and `npm run test:integration` (41 disposable-PostgreSQL tests passed).

### Architecture Conformance

Accepted for the bounded composition refactor. Route ownership, method fallthrough, health/readiness, callback/webhook authentication isolation, and lifecycle behavior are covered; no wire-contract or schema changes were made.

### Follow-up

Accepted. API-013 is promoted to `ready` as the sole direct downstream task. ARCH-041-SYSTEM-TEST-001 remains `pending` until API-013 is complete.

### Developer Self-Review - Passed

- Attempt: 1.
- Reviewed implementation commit: `f0f496f567fa577fc5c9902881b1cb810986d2d9`.
- Result: scope, route inventory, security boundaries, lifecycle behavior and validation passed; task moved to `review` before the explicit completion decision.

### Developer Completion Decision

- Decision: Complete.
- Authorized action: `/moda_developer_update ARCH-041-API-012 complete`.
- Date: 2026-10-16.
- Accepted review: Architect Review Accepted, as explicitly supplied by the developer with this completion request.
- Attempt: 1, unchanged.
- Implementation commit: `f0f496f567fa577fc5c9902881b1cb810986d2d9`, published to `origin/task/ARCH-041-API-012`.
- Parent task/report branch: `task/ARCH-041-API-012`.
- Dependency frontier: API-013 promoted to `ready`; ARCH-041-SYSTEM-TEST-001 remains `pending` because API-013 is not complete.
- No task branch was merged to `main`.
