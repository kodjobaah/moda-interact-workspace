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
status: in_progress
priority: 15
executor: developer
claimed_at: 2026-10-16T00:46:22Z
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
- **Task state:** `ready` according to explicit dependencies; readiness is re-gated by the launcher before an attempt.

### Developer Takeover

This task was defined with `execution_mode: agent` and `completion_mode: automatic`. The developer explicitly invoked `/moda_developer_create ARCH-041-API-001`, recording a takeover to `execution_mode: developer` and `completion_mode: developer`. Logical ownership remains `moda_api`; scope, dependencies, acceptance criteria and implementation requirements are unchanged. This record is materialized before the attempt claim; the launcher will claim only after preparation succeeds.

## Objective

Create an executable regression guard for already-implemented hosted API routes and billing behaviours before extraction.

## Context

`src/server.ts` directly chains three routers and `src/woocommerce/installation/routes.ts` also handles merchant and billing endpoints; focused tests already exist but do not make the cross-router method/dispatch contract fully explicit. Add *missing* parity cases rather than duplicating the entire test suite.

## Scope

- Inventory the existing route/method pairs and corresponding published OpenAPI v1 documents, including health, Woo connection/probe, REST-read callbacks, billing webhook, merchant reads/commands and billing GET/POST/DELETE.
- Add a bounded `tests/unit/http/` cross-router characterization suite with injected handlers/services: cover route precedence, unknown/wrong-method responses and `/v1/billing/recovery-credit-purchases` GET-vs-POST ownership.
- Capture representative byte/shape/header/error-code expectations for the existing Woo installation bearer principal (including absent/duplicate/wrong-shop/revoked/rotated credentials when testable), distinct webhook signature/callback denial paths, bounded request bodies, billing replay/provider failure and health/readiness paths; use existing domain tests where they already provide proof.
- Record any pre-existing failures as baselines without changing production behaviour or unrelated tests. Inventory current `WooInstallationAuthenticator` and `WooInstallationPrincipal` imports/credential codec uses so API-014 can later move ownership without altering the security contract.

## Out of Scope

- No database schema or migration, Shared package, Background, Shopify, WooCommerce plugin, Commerce or Gateway changes.
- No new endpoints, endpoint renames, changed HTTP semantics, feature work, or unrelated cleanup.
- No `docs/decisions/**/_index.md` changes before the user explicitly confirms this architecture session complete.
- Implementation refactor, new DTOs, architectural new behavior, and changes to existing task status.

## Requirements

- No production source changes in this task; new tests under `tests/unit/`, plus a concise evidence record only. Do not change `package.json` test globs to make a test discoverable when its agreed path is already covered.
- Existing feature/task YAML status is authoritative even when route source exists in the snapshot; do not certify open feature work as complete.
- Assertions must be deterministic and injection-based where possible, with no live provider/network dependency and no secret material.
- Ensure characterisation can be reused unchanged for later API-008 through API-013 refactors.

## Work Items

- [ ] Inventory every relevant current path+method and its owning test/OpenAPI contract.
- [ ] Add `tests/unit/http/` coverage for observable gaps in cross-router ordering and billing method collision; do not relocate `src/server.test.ts` merely for layout consistency.
- [ ] Record current `woocommerce/installation/authenticator.ts` principal fields, raw-header validation, credential comparison, active/revoked Shop predicates and direct consumers as the contract for the later `src/auth/woo-installation/` extraction.
- [ ] Record the route security policy matrix (public health; connect/site proof; installation bearer; signed billing webhook; one-time REST-read callback capability) and add `tests/unit/auth/` or owner-specific negative tests only where coverage is missing; preserve existing semantics.
- [ ] Run relevant API tests and record baseline evidence in the Completion Report.

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

- [ ] New tests follow `tests/unit/<domain>/<feature>/` or `tests/integration/<domain>/<feature>/` as applicable; existing co-located suites remain runnable and no unrelated test migration is introduced.
- [ ] No runtime application files are changed.
- [ ] Existing HTTP route precedence and error envelopes are represented by executable assertions and no sensitive payloads appear in fixtures/logs.
- [ ] Baseline results identify genuine pre-existing failures separately from newly written test failures.
- [ ] Existing tests for installation, invalid/revoked bearer access, signed webhooks, callback capability denials, billing and health continue to pass in the available environment. Authentication characterisation must not assert a new policy for in-flight credential rotation.

## Validation

- [ ] Verify any new unit tests through the existing `npm test` globs (`src/**/*.test.ts` plus `tests/unit/**/*.test.ts`); run required new PostgreSQL integration cases using an explicit disposable database harness and record command/results separately (never count them as covered by `npm test`).
- [ ] Focused `node --test`/`tsx --test` command chosen from package scripts for the new characterization suite and the affected existing test files.
- [ ] `npm run typecheck` (includes Prisma generate).
- [ ] `npm run lint`.
- [ ] `npm test` (existing declared script).
- [ ] `npm run build`.
- [ ] `git diff --check` and canonical launcher-prepared parent/implementation worktree, sync and recursive-submodule evidence.

## Stop Condition

After this task’s defined Work Items, Acceptance Criteria and required Validation are completed, update its Completion Report, set `status: review`, clear the execution claim as required by the workflow, and return to `moda_architect`. **STOP.** Do not begin a task listed under Enables. Publication/merge into `main` and the final Gitlink update remain developer-owned.

## Implementation Notes

**ARCH-041 revision 2 — test placement:** New unit assertions belong in `tests/unit/http/route-dispatch.test.ts`; filenames are examples, not compulsory placeholder files. If additional persisted/concurrency evidence is needed, place it in `tests/unit/auth/woo-installation-authentication.test.ts` and execute it through an explicit disposable PostgreSQL runner. Reuse `src/server.test.ts`, Woo installation routes and existing authentication/billing suites. Do **not** bulk-migrate existing `src/**/*.test.ts` tests: the current `npm test` discovers them and `tests/unit/**/*.test.ts`. New `tests/integration/**` suites are **not** covered by `npm test`, and `tsconfig.build.json` remains production-source only.

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the parent architecture and this task before a claim. The launcher preparation packet is valid start-of-attempt evidence; record its resolved parent/implementation worktree paths, synchronization and submodule details. Do not infer paths from the ZIP. Re-check the live mainline before editing.

Place **new** tests in `tests/unit/http/` and, if needed, `tests/unit/auth/`. Keep existing `src/server.test.ts` and co-located feature tests as legacy coverage; no new test belongs under `src/` solely because existing tests are there. Avoid enormous golden snapshots: assert bounded shape, method, status, security and important semantic fields. Do not claim database integration pass without a real database run.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-16T00:46:22Z. Attempt 0 review history is preserved below.

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
