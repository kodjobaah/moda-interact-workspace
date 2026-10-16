---
id: ARCH-041-API-012
architecture_id: ARCH-041
title: Compose domain routers at the API server boundary
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
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
- **Definition state:** portable canonical task definition; defined but **not materialised** (no task worktree, Git branch, commit or push in this session).
- **Task state:** `pending` according to explicit dependencies in this snapshot; readiness is re-gated by the launcher before an attempt.

## Objective

Remove unrelated merchant/billing route delegation from Woo installation routing and register independently owned domain routes in an explicit top-level HTTP chain.

## Context

API-008 through API-011 extract the remaining billing and merchant handlers. `src/index.ts` and `src/server.ts` can then become a clear composition root and route dispatcher instead of using `createWooInstallationRoutes` as an umbrella router for all unrelated services. API-014 has already established the canonical `src/auth/woo-installation/` identity boundary, so this task must **consume** it rather than move auth a second time.

## Scope

- Define one API-local shared Node HTTP route interface at `src/http/route-handler.ts` with the existing `handle(IncomingMessage, ServerResponse): Promise<boolean>` semantics; adopt that exact type for server route registration without changing existing `false` fallthrough.
- Introduce a small explicit `src/composition/` dependency-assembly module (e.g. `merchant.ts`, `billing.ts`, `woocommerce.ts`, `routes.ts` as justified) and ordered HTTP handler collection wired from `src/index.ts` to `src/server.ts`. Only construct collaborators used by accepted routes; no placeholder files.
- Register health, Woo REST-read authorisation/callback, signed billing webhook, all merchant handlers, billing handlers and finally install/connect/probe with correct method routing. Use the *accepted* upstream ARCH-026/035/036/040 route inventory (refreshed by API-008), not a stale route list from API-001.
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
- No missing existing API route even when introduced by accepted ARCH-026/035/036/040 tasks. Keep existing canonical bearer principal/credential-version semantics and protect callback/webhook endpoints from installation-router fallthrough.

## Work Items

- [ ] Compare the post-API-011 accepted route inventory and API-008 characterization updates with the proposed final route composition; register every accepted route and test its method, security boundary, denial and error fallthrough. Record coverage in the Completion Report.

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

- [ ] Every accepted ARCH-026/035/036/040 endpoint existing at composition time has a registered handler and path+method/security characterization; callback and webhook routes retain distinct guards and wrong methods fall through as before.

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
