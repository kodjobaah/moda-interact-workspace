---
id: ARCH-041-API-001
architecture_id: ARCH-041
title: Characterize hosted API HTTP and billing contracts
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-041-API-002
  - ARCH-041-API-004
  - ARCH-041-API-006
  - ARCH-041-API-008
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-041-API-001 — Characterize hosted API HTTP and billing contracts

## Architecture

- Architecture ID: `ARCH-041`
- Parent document: `docs/architecture/ARCH-041-hosted-api-modular-refactor.md`
- Coordinator: `moda_architect`
- **Definition state:** materialised on parent branch `task/ARCH-041-API-001` in the canonical parent task worktree.
- **Task state:** `complete` after accepted Attempt 1 and the explicit developer completion decision.

### Developer Takeover

This task was defined with `execution_mode: agent` and `completion_mode: automatic`. The developer explicitly invoked `/moda_developer_create ARCH-041-API-001`, recording a takeover to `execution_mode: developer` and `completion_mode: developer`. Logical ownership remains `moda_api`; scope, dependencies, acceptance criteria and implementation requirements are unchanged. Attempt 1 was claimed by the developer after canonical worktree preparation.

## Objective

Create an executable regression guard for already-implemented hosted API routes and billing behaviours before extraction.

## Context

`src/server.ts` directly chains three routers and `src/woocommerce/installation/routes.ts` also handles merchant and billing endpoints; focused tests already exist but do not make the cross-router method/dispatch contract fully explicit. Add *missing* parity cases rather than duplicating the entire test suite.

## Scope

- Inventory the existing route/method pairs and corresponding published OpenAPI v1 documents, including health, Woo connection/probe, REST-read callbacks, billing webhook, merchant reads/commands and billing GET/POST/DELETE.
- Add a bounded `tests/unit/http/` cross-router characterization suite with injected handlers/services: cover route precedence, unknown/wrong-method responses and `/v1/billing/recovery-credit-purchases` GET-vs-POST ownership.
- Supply one small API-local `scripts/test-arch041-billing-postgres.mjs` runner for the existing billing-read, recurring and recovery-credit persistence suites and later billing integration cases. Base the disposable database, migrations and teardown on the existing REST-read authorization runner, **not** the installation runner that uses `prisma db push`.
- Capture representative byte/shape/header/error-code expectations for the existing Woo installation bearer principal (including absent/duplicate/wrong-shop/revoked/rotated credentials when testable), distinct webhook signature/callback denial paths, bounded request bodies, billing replay/provider failure and health/readiness paths; use existing domain tests where they already provide proof.
- Record any pre-existing failures as baselines without changing production behaviour or unrelated tests. Inventory current `WooInstallationAuthenticator` and `WooInstallationPrincipal` imports/credential codec uses so API-014 can later move ownership without altering the security contract.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.
- Implementation refactor, new DTOs, architectural new behavior, and changes to existing task status.

## Requirements

- No production source changes in this task; new unit tests under `tests/unit/`, persisted/concurrency tests under `tests/integration/`, the narrow billing-test runner under `scripts/`, and a concise evidence record only. Do not change `package.json` test globs to make a test discoverable when its agreed path is already covered.
- The billing runner uses an invocation-owned disposable PostgreSQL instance, real `prisma migrate deploy --schema database/prisma/schema.prisma` migrations (including SQL triggers), `DATABASE_URL` and `WOO_INSTALLATION_TEST_DATABASE_URL`, and reliable teardown; use the existing `pgvector/pgvector:pg17` pattern. It may run the three existing billing `*.postgres.test.ts` suites plus explicit new `tests/integration/billing/**` cases. Do not use `prisma db push` as migration-constraint evidence; do not build a generic cross-repository test framework.
- Existing feature/task YAML status is authoritative even when route source exists in the snapshot; do not certify open feature work as complete.
- Assertions must be deterministic and injection-based where possible, with no live provider/network dependency and no secret material.
- Ensure characterisation can be reused unchanged for later API-008 through API-013 refactors.

## Work Items

- [x] Inventory every relevant current path+method and its owning test/OpenAPI contract in `tests/contracts/http-billing-security-baseline.md`.
- [x] Add `tests/unit/http/` coverage for cross-router ordering, health dispatch, bounded 404 behavior and billing GET-vs-POST ownership without relocating `src/server.test.ts`.
- [x] Record the authenticator principal fields, raw-header validation, credential comparison, active/revoked Shop predicates and direct consumers as the API-014 extraction contract.
- [x] Record the route security policy matrix and add deterministic injected authentication negatives under `tests/unit/auth/woo-installation/`; existing domain tests retain webhook, callback and bounded-body coverage.
- [x] Add a disposable migration-backed billing PostgreSQL runner for the billing-read, recurring and recovery-credit suites.
- [x] Run relevant API tests and record exact baseline evidence in the Completion Report.

## Interfaces / Contracts

Consumes the existing OpenAPI v1 files in `moda-interact-api/openapi/`, `createApiRuntime`, Woo installation principal, established billing service response/error contracts. Produces **no new wire contract**; test assertions are the parity fence.

## Dependencies

None.

## Enables

- `ARCH-041-API-002`
- `ARCH-041-API-004`
- `ARCH-041-API-006`
- `ARCH-041-API-008`

## Acceptance Criteria

- [x] New tests follow the agreed `tests/unit/` layout; existing co-located suites remain runnable and no unrelated test migration was introduced.
- [x] No runtime application files are changed; changes are limited to tests, test helpers, the PostgreSQL runner, package test lifecycle and contract evidence.
- [x] Existing HTTP route precedence and bounded error envelopes are represented by executable assertions; fixtures use no secret material.
- [x] Baseline results distinguish the 42 database-gated skips in `npm test` from the separately executed PostgreSQL suites; no test failures were observed.
- [x] Installation, invalid/revoked bearer access, signed webhook, callback, billing and health suites pass in the available environment. Credential-rotation characterization is explicitly limited to separate requests, not in-flight commands.

## Validation

- [x] `npm test` — 352 tests, 310 passed, 0 failed, 42 skipped, 0 cancelled. The skips are existing PostgreSQL tests gated by their database environment variable; they are not counted as PostgreSQL validation.
- [x] `node --import tsx --test tests/unit/http/route-dispatch.test.ts tests/unit/auth/woo-installation/authentication-contract.test.ts` — 8 passed, 0 failed.
- [x] `npm run typecheck` — passed; Prisma Client generated.
- [x] `npm run lint` — passed with `--max-warnings=0`.
- [x] `npm run build` — passed.
- [x] `node scripts/test-arch041-billing-postgres.mjs` — 16 passed, 0 failed, 0 skipped. The invocation-owned `pgvector/pgvector:pg17` database applied all 49 Prisma migrations with `prisma migrate deploy`; runner teardown completed.
- [x] `git diff --check origin/main...HEAD` — passed for the implementation branch. Canonical parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-041-API-001` is on `task/ARCH-041-API-001` at claim commit `de10fff2`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-041-API-001` is on `task/ARCH-041-API-001` at `a3302f7383011d00bc23cc48da9354ad3d109e5e`. Both were clean before this report update. The implementation tip equals `origin/task/ARCH-041-API-001`; local branch tracking metadata points to `origin/main` and reports one commit ahead, so synchronization was verified by comparing the task ref directly. Recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/http/route-dispatch.test.ts`; filenames are examples, not compulsory placeholder files. If persisted installation-state/concurrency evidence is needed, place it in `tests/integration/auth/woo-installation/woo-installation-authentication.test.ts` and run it using an explicitly provisioned disposable PostgreSQL fixture; keep database-free negatives under `tests/unit/auth/woo-installation/`. Reuse `src/server.test.ts`, Woo installation routes and existing authentication/billing suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Place **new unit** tests in `tests/unit/http/` and, if needed, `tests/unit/auth/woo-installation/`; database-backed assertions belong under `tests/integration/` and are executed explicitly. Keep existing `src/server.test.ts` and co-located feature tests as legacy coverage; no new test belongs under `src/` solely because existing tests are there. Avoid enormous golden snapshots: assert bounded shape, method, status, security and important semantic fields. Do not claim database integration pass without a real database run.

## Completion Report

### Status

Completed — Attempt 1 passed developer self-review and the explicit Developer Completion Decision below was recorded. The implementation task branch remains separate from `main`.

### Files Changed

Implementation commit `a3302f7383011d00bc23cc48da9354ad3d109e5e` changes:

- `package.json`
- `scripts/test-arch041-billing-postgres.mjs`
- `src/billing/commands/recovery-credit-purchase-command.postgres.test.ts`
- `src/billing/commands/recurring-subscription-command.postgres.test.ts`
- `src/billing/presentation/billing-read.postgres.test.ts`
- `tests/contracts/http-billing-security-baseline.md`
- `tests/helpers/merchant-pricing-test-fixtures.ts`
- `tests/unit/auth/woo-installation/authentication-contract.test.ts`
- `tests/unit/http/route-dispatch.test.ts`

No runtime application source, schema, migration, or unrelated task files changed.

### Work Completed

Added the route/method/OpenAPI/test-owner inventory and security contract baseline, including the Woo installation principal, credential handling and direct consumers. Added injected cross-router dispatch and billing route-collision characterization plus raw-header authentication and separate-request credential-rotation tests. Added a disposable PostgreSQL runner that uses real Prisma migrations and runs the three existing billing persistence suites; updated those test fixtures for migration-enforced catalogue constraints and published pricing translations. No production behavior or wire contracts changed.

### Validation Results

All required checks passed; exact commands and results are recorded in Validation above. The normal suite skipped 42 database-gated PostgreSQL cases; the dedicated runner independently executed all 16 required billing persistence cases successfully against a fresh migration-backed database. No validation failure or pre-existing failure was observed. Docker was available and the disposable database container was removed by runner teardown.

### Deviations

No scope deviations. Existing PostgreSQL test fixtures were updated only where real migration constraints required valid catalogue positions/translations or where invalid fixture rows are now rejected by the database itself.

### Assumptions

The uploaded ZIP was treated only as an initial snapshot. The implementation was based on the live canonical task branch and launcher-prepared worktrees. Database-gated tests reported as skipped by `npm test` are covered only where separately executed by the dedicated runner; no broader PostgreSQL pass is inferred.

### Unresolved Issues

No task-scope issues remain. Local implementation branch upstream metadata points at `origin/main`, although its commit is identical to `origin/task/ARCH-041-API-001`; this did not prevent publication or validation and is recorded above.

### Architectural Concerns

None identified. Authentication characterization does not define policy for commands already in flight during credential rotation.

## Developer Self-Review

### Review Status

Accepted — Attempt 1 meets the task scope and acceptance criteria, and all required validation passed. The explicit developer completion action is recorded below.

### Reviewed Files

All nine implementation paths listed under Files Changed, including the implementation diff from `origin/main` to `a3302f7383011d00bc23cc48da9354ad3d109e5e`.

### Validation Reviewed

Focused characterization (8/8), typecheck, lint, full test suite (310 passed, 42 database-gated skips, 0 failed), build, migration-backed billing PostgreSQL runner (16/16), and implementation `git diff --check` all passed.

### Architecture Conformance

Conforms: test-only behavior characterization and evidence; no runtime behavior, schema, endpoint, dependency ownership, or unrelated task status changes.

### Follow-up

The explicit developer completion decision is recorded below. No enabled task was started.

## Developer Completion Decision

On 2026-10-16, the developer explicitly invoked `/moda_developer_update ARCH-041-API-001 complete`. Attempt 1 remains the accepted attempt; status is `complete`, with no implementation merge to `main`.

### Dependency Frontier

Promoted `ARCH-041-API-002`, `ARCH-041-API-004` and `ARCH-041-API-006` from `pending` to `ready`; each has no other declared dependency. `ARCH-041-API-008` remains `pending` because its other dependencies include pending `ARCH-026-API-006`, `ARCH-035-API-013`, and `ARCH-040-API-002`, `ARCH-040-API-003` and `ARCH-040-API-004`. No `_index.md` or implementation branch was changed.

## Architect Review

### Review Status

Pending; the Developer Self-Review above is accepted. No separate architect review is represented here.

### Review Notes

Developer self-review accepted for Attempt 1; task remains in `review` pending explicit developer completion. Separate architect assessment has not been recorded.

### Reviewed Files

The implementation paths listed in the Completion Report; parent task record is updated on the canonical parent task branch.

### Validation Reviewed

See the exact commands and results in Validation and Developer Self-Review above.

### Architecture Conformance

Developer self-review finds the changes conform to the test-only scope and produce no new wire contract. Separate architect assessment remains pending.

### Follow-up

The developer may explicitly record completion with `/moda_developer_update ARCH-041-API-001 complete`; do not start an enabled task before then.
