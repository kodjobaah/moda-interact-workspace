---
id: ARCH-044-COMMERCE-002
architecture_id: ARCH-044
title: Provide isolated disposable PostgreSQL Redis and complete Vitest fixtures
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: [ARCH-044-COMMERCE-007]
created: '2026-10-18'
updated: '2026-10-18'
---

# Provide isolated disposable PostgreSQL Redis and complete Vitest fixtures

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Make the Commerce test harness capable of running its complete intended test suite with safely isolated disposable PostgreSQL/Redis fixtures and complete Vitest mocks, without relying on incidental developer environment variables.

## Context

The unchanged-baseline full run had six suites that failed during import/startup rather than running assertions: `agent-configuration-model-postgres`, `agent-configuration-prompts-postgres`, `preview-openrouter-postgres` require `COMMERCE_TEST_DATABASE_URL`; `c20-integration-fixture` and `studio-integration-c20` require disposable PostgreSQL and Redis plus `COMMERCE_C20_REDIS_NAMESPACE`; `tool-editor-dispatch` provides an incomplete `../src/commerce/tool-definition` mock lacking `ResponseTemplateSchema`. The baseline also timed out at 30 seconds in `tests/discovery-limits.test.ts` after up to 60 sequential calls to `withDiscoveryAdmission()` when `REDIS_URL` was present. A prior mix of `npm ci` with `pnpm exec` triggered `ERR_PNPM_IGNORED_BUILDS` and blocked an earlier comparison. The later npm-run baseline completed: 188 test files, 38 failed assertions and six suite setup failures.

## Scope

- Inspect existing `scripts/run-c20-fixture-disposable.mjs`, `scripts/rehearse-commerce-backend-postgres.sh`, `scripts/run-arch043-platform-configuration-disposable.mjs` and test fixture entrypoints before designing orchestration; reuse existing disposable mechanisms rather than creating another stack.
- Provide a safe, discoverable, reproducible opt-in command for **all integration suites** that require PostgreSQL/Redis and clearly separate it from fast unit/UI suites. Make failures state missing prerequisite or intentionally skipped only where existing architecture authorises it.
- Repair `tests/tool-editor-dispatch.test.tsx`'s partial module mock to retain the real `ResponseTemplateSchema` export while mocking only intended behavior.
- Rework discovery-admission test setup/diagnostics or measured pacing so 60 permitted requests and the 61st rejection are tested deterministically against an isolated Redis namespace; investigate genuine performance failure before changing its deadline.

## Out of Scope

- No production database/Redis target, no committed secrets, no shared Redis flush or global database reset.
- No changing functional admission quotas from 60 to satisfy the test and no skipping all integration suites just to make `npm test` green.
- No general build or UI refactors owned by other ARCH-044 tasks.

## Requirements

1. Test databases and Redis namespace must be identifiable as disposable, checked before writes, isolated per run, bounded and cleaned on success/failure.
2. Missing Docker or required test tools must yield a documented non-success reason, not a false PASS.
3. Existing package scripts remain authoritative; new scripts must not depend on globally installed pnpm or mix installers without justification.
4. The `ResponseTemplateSchema` mock must use partial `importOriginal()` as needed and preserve all required production exports.
5. Redis/discovery rate limits remain 60 sequential permitted / 61st rejected in the window, tested with stable isolation and useful diagnostics.

## Work Items

- [ ] Inventory six baseline import failures, exact env variables and corresponding existing disposable scripts.
- [ ] Implement a safe, reproducible combined test-environment path that provisions required fixtures and runs intended suites.
- [ ] Repair the partial tool-definition mock without changing production contracts.
- [ ] Diagnose `discovery-limits` 30-second timeout and correct fixture or test synchronization (or a proven runtime issue).
- [ ] Capture reproducible local/CI commands, cleanup, and failure diagnostics without secrets.

## Interfaces / Contracts

`COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL`, `COMMERCE_C20_REDIS_NAMESPACE`, and C20's `DATABASE_URL === COMMERCE_TEST_DATABASE_URL` invariant for its disposable path. `ResponseTemplateSchema` is the existing module export, not a new contract. Redis discovery admission retains `RATE_LIMITED` semantics.

## Dependencies

None.

## Enables

- `ARCH-044-COMMERCE-007`

## Acceptance Criteria

- [ ] All six suites can collect and execute under their intended disposable fixture environment, or record an explicit external infrastructure blocker; no import-time missing-env or mock failures.
- [ ] Separate unit/UI and integration test workflows are documented and reproducible on a clean worktree.
- [ ] Disposable database and Redis isolation, non-production assertions, cleanup and no-secret-logging are verified.
- [ ] `tests/discovery-limits.test.ts` proves 60 allowed calls and 61st rejected without intermittent 30-second timeout.
- [ ] Other tests are not silently omitted from a purported full-suite result.

## Validation

- [ ] `npm ci` and `npm run prisma:generate` against the task's pinned database schema.
- [ ] Run all six named suites using the disposable test harness; capture setup and cleanup evidence.
- [ ] `npx vitest run tests/tool-editor-dispatch.test.tsx tests/discovery-limits.test.ts` against appropriate isolated fixtures.
- [ ] `npm test -- --maxWorkers=4` with full fixture environment; record pass/fail per test and suite.
- [ ] `git diff --check`; typecheck if scripts/tests edited.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

This task owns test environment scaffolding, not all the failures revealed when test suites finally run. Follow-on `ARCH-044-COMMERCE-007` must use the resulting fixture path for durable PostgreSQL acceptance. Do not run broad suites against merchant or production Redis/PostgreSQL.

### Six baseline suite-setup failures (zero test assertions executed)

| Test file | Known diagnostic |
|---|---|
| `tests/agent-configuration-model-postgres.test.ts` | `COMMERCE_TEST_DATABASE_URL` missing |
| `tests/agent-configuration-prompts-postgres.test.ts` | `COMMERCE_TEST_DATABASE_URL` missing |
| `tests/c20-integration-fixture.test.ts` | `C20_FIXTURE_UNSAFE_ENVIRONMENT` — disposable PostgreSQL/Redis/namespace missing |
| `tests/preview-openrouter-postgres.test.ts` | `COMMERCE_TEST_DATABASE_URL` missing |
| `tests/studio-integration-c20.test.ts` | `C20_FIXTURE_UNSAFE_DATABASE_TARGET` — disposable targets missing |
| `tests/tool-editor-dispatch.test.tsx` | Partial `vi.mock` omits `ResponseTemplateSchema` |

Additionally: `tests/discovery-limits.test.ts` timed out at 30,000 ms under Redis-enabled execution.

## Completion Report

### Status

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run. Record each exact command, environment, exit code, test totals and any known-baseline differences. Baseline failures may not be silently treated as task successes.

### Worktree / Synchronisation Evidence

Not yet materialised. Record launcher-resolved canonical workspace root, dedicated parent and implementation worktrees, initial branch/commit identities and recursive submodule state when execution begins.

### Deviations

None yet.

### Assumptions

Task definition based on the 2026-10-18 source snapshot and supplied baseline/task logs; re-inspect current implementation when executing.

### Unresolved Issues

None beyond the explicitly described diagnostics to investigate.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation evidence.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Not assessed.

### Follow-up

None yet.
