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
status: review
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables: [ARCH-044-COMMERCE-007]
created: '2026-10-18'
updated: 2026-11-01
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

- [x] Inventory six baseline import failures, exact env variables and corresponding existing disposable scripts; confirm the existing ARCH-044 runners cover the required database/Redis cases.
- [x] Verify the existing opt-in combined integration/full paths, per-suite databases, isolated consumer runner, fail-closed report checks, and owner-label cleanup; no parallel fixture stack was added.
- [x] Verify `tests/tool-editor-dispatch.test.tsx` already uses partial `importOriginal()` and preserves `ResponseTemplateSchema`; its 9-test file passes unchanged.
- [x] Namespace-scope and instrument the discovery-admission test without changing 60/61 quota or the 30-second deadline. Attempt 2 verified the live 60/61 outcome and timing against disposable Redis.
- [x] Update reproducible command and fixture diagnostics documentation without logging secrets.

## Interfaces / Contracts

`COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL`, `COMMERCE_C20_REDIS_NAMESPACE`, and C20's `DATABASE_URL === COMMERCE_TEST_DATABASE_URL` invariant for its disposable path. `ResponseTemplateSchema` is the existing module export, not a new contract. Redis discovery admission retains `RATE_LIMITED` semantics.

## Dependencies

None.

## Enables

- `ARCH-044-COMMERCE-007`

## Acceptance Criteria

- [ ] Of the five PostgreSQL/Redis-gated suites, three passed (model 8/8, prompts 5/5, OpenRouter 1/1); C20 fixture timed out with 1 pass and 1 failure, and Studio timed out in `beforeAll` with 6 skipped. Tool Editor dispatch passed 9/9 in the earlier focused unit lane. The fixture-backed full lane also exposed unrelated general-suite failures; see Attempt 2 evidence below.
- [x] Separate unit/UI and integration workflows are documented with the declared npm scripts and no pnpm dependency.
- [x] Isolation/cleanup behavior is covered by harness contract tests and live disposable runs; the focus and full run each reported zero owned Docker resources after cleanup.
- [x] The discovery test requires the run namespace and the live run verified 60 allowed / 61st `RATE_LIMITED`, with elapsed and max-request timing diagnostics.
- [x] The full-suite planner inventories and partitions every test file and rejects missing/unexecuted suites; a full fixture-backed runtime result is not claimed.

## Validation

- [x] `npm ci` and `npm run prisma:generate` against the task's pinned database schema.
- [ ] Run all six named suites using the disposable test harness; capture setup and cleanup evidence (blocked before suite execution by pinned image pull timeout).
- [ ] `npx vitest run tests/tool-editor-dispatch.test.tsx tests/discovery-limits.test.ts` against appropriate isolated fixtures (Tool Editor passed in unit lane; discovery fixture was blocked before test execution).
- [ ] `npm test -- --maxWorkers=4` with full fixture environment; full-lane wrapper invocation returned no usable output/exit status, so no result is claimed.
- [x] Architect review ran `git diff --check origin/main...HEAD` and `git show --check dbaec9c`; both exited successfully with no whitespace errors.
- [ ] `npm run typecheck`: exit 1 after successful schema sync and Next route type generation. Existing unrelated error: `tests/system-commerce-tool-sync.test.ts:305:72`, TS2345, `{}` is not assignable to `ProcessEnv` because `NODE_ENV` is required. No change was made to that out-of-scope test.

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

Ready for Review — Attempt 2. Disposable infrastructure and discovery behavior were verified, but the full lane is not green: two of five formerly blocked PostgreSQL/Redis suites timed out and the general lane reported 35 failed assertions plus one unexecuted registered test. Acceptance criteria remain unchecked where not satisfied. The task is in `review`; execution claim cleared. Attempt 1 and its Architect Review remain preserved below.

### Files Changed

- `moda-interact-commerce/tests/discovery-limits.test.ts`: require the run-scoped namespace, use it in the synthetic admin identifier, and report admitted count, 61st-request rejection, elapsed time, and maximum per-request latency. The 60/61 contract and 30-second deadline are unchanged.
- `moda-interact-commerce/docs/arch044-disposable-tests.md`: refresh the discovered suite inventory and document the current namespace/timing diagnostics and four-suite general integration phase.
- The existing `tests/tool-editor-dispatch.test.tsx` partial mock already used `importOriginal()` and preserved all real exports, including `ResponseTemplateSchema`; it passed its focused file test and required no change.
- Existing `scripts/run-c20-fixture-disposable.mjs`, `scripts/rehearse-commerce-backend-postgres.sh`, `scripts/run-arch043-platform-configuration-disposable.mjs`, package scripts, and fixture entrypoints were inspected. The established ARCH-044 runners already provide the combined opt-in path and were retained.
- `moda-interact-commerce/scripts/arch044-disposable-suites.mjs`: relay the discovery test's single allow-listed 60/61 timing diagnostic from the runner's buffered successful child output; no other output or credentials are exposed.

### Work Completed

- Reused the established ARCH-044 disposable runner; pinned local PostgreSQL/pgvector and Redis images were available on Attempt 2. No production/shared database or Redis target was used.
- Verified the live discovery contract: `admitted=60/60`, `rejected61=true` (`RATE_LIMITED`), `elapsedMs=2294`, `maxRequestMs=77`, under the unchanged 30-second deadline.
- The run inventory was 201 Vitest files: 190 general, 9 isolated PostgreSQL suites, and 2 dedicated ARCH-043 consumer suites. The harness partitions the complete inventory and rejects missing/unexecuted suites.
- The harness contract suite verifies loopback Docker enforcement, run-owned cleanup after partial setup, report completeness, per-suite database isolation, and rejection of unsafe source/environment inputs.

### Validation Results

- Environment: macOS, prepared task worktrees; Node `v24.21.0`, npm `11.19.0`; repository `.nvmrc` specifies `24.19.0`. No alternate installer was used. The existing nested database submodule was at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- `npm run test:arch044:harness`: passed, 15/15 Node tests, 0 failed. Its synthetic full-suite negative case is not a live application result.
- `npm run test:arch044:focus -- tests/discovery-limits.test.ts`: passed, 1 file / 1 test; `admitted=60/60 rejected61=true elapsedMs=2294 maxRequestMs=77 result=completed`; disposable PostgreSQL/Redis setup succeeded and cleanup reported `zero owned Docker resources remain`.
- `npm run test:arch044:full`: exit 1. Disposable PostgreSQL/Redis setup succeeded. General phase: 190/190 files collected, 1,458 assertions passed, 35 failed, 0 skipped; `tests/system-commerce-tool-sync-postgres.test.ts` was unexecuted and reported as missing from the collected execution. The first reported failing titles include Admin Explore handoff cancellation, ARCH-021 bounded request processor cases, ARCH-020 response-processing cases, and QuickJS runtime cases. These are real test failures, not harness simulation results.
- Five formerly blocked PostgreSQL/Redis suites in that full run: `agent-configuration-model-postgres` passed 8/8; `agent-configuration-prompts-postgres` passed 5/5; `preview-openrouter-postgres` passed 1/1; `c20-integration-fixture` had 1 pass and 1 failure due a 60-second test timeout; `studio-integration-c20` had 0 passed and 6 skipped after a 10-second `beforeAll` hook timeout. The remaining isolated phases passed: merchant knowledge 1/1, merchant auth 3/3, templates 3/3, platform configuration 4/4. Dedicated consumer smoke passed 4/4 plus outage 1/1 and its owned PostgreSQL cleanup verification.
- Full and focused runner cleanup both reported `cleanup PASS; zero owned Docker resources remain`. Database and Redis were run-scoped, labeled, loopback-only and disposable; no shared resource was targeted.
- `npm run typecheck`: exit 1 after schema sync and route type generation. The unchanged error is `tests/system-commerce-tool-sync.test.ts:305:72`, TS2345: `{}` lacks required `NODE_ENV` in `ProcessEnv`.
- `git diff --check`: exit 0 after the runner diagnostic change.
- No production quota/deadline, integration suite selection, or test behavior was changed. The only Attempt 2 source change relays the existing discovery diagnostic so successful-run evidence is visible.

### Worktree / Synchronisation Evidence

- Launcher prepared execution packet: task `ARCH-044-COMMERCE-002`, Attempt 2, executor `copilot`; claim commit `50296e67001388e88caeb38bf3f2449214f24761`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-002`, branch `task/ARCH-044-COMMERCE-002`, Attempt 2 base/head before this change `dbaec9ccabbde0debfb8a4016388b82bd04d236b`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-002`, branch `task/ARCH-044-COMMERCE-002`, prepared base `410c9d55a1c1587bc0d836117a33efee4f9898de`, claim commit above.
- Prepared launcher confirmed the correct dedicated worktrees/branches and initialized recursive submodule at `af77c594ecbfc78c26d01c0021a090830884bbff`; no synchronization ritual was repeated.
- Attempt 2 implementation change: `scripts/arch044-disposable-suites.mjs` only; commit `5c79af6` (`test(commerce): report discovery fixture timing`), pushed to `origin/task/ARCH-044-COMMERCE-002`. Parent report changes are limited to this task file and will be committed/pushed on the matching parent task branch.
- No submodule gitlink, other task file, index, architecture document, or main branch was modified.

### Deviations

- The ARCH-044 fixture scripts and `tests/tool-editor-dispatch.test.tsx` mock were already present in the prepared implementation snapshot. Existing implementations were validated and reused rather than duplicated or rewritten.
- The pinned images and disposable resources were available on Attempt 2, so the infrastructure blocker was resolved. The full lane exposed actual C20 and Studio fixture timeouts, 35 general assertion failures and one unexecuted registered suite; no failures are suppressed or counted as passing.

### Assumptions

The named ARCH-044 opt-in scripts remain the approved fixture entrypoints. The PostgreSQL image pull timeout is an external local infrastructure/network blocker, not evidence of an application or test assertion failure.

### Unresolved Issues

- Diagnose the `c20-integration-fixture` 60-second test timeout and `studio-integration-c20` 10-second `beforeAll` timeout from focused disposable runs before making changes.
- Triage the 35 general-lane assertion failures and the unexecuted `tests/system-commerce-tool-sync-postgres.test.ts`; do not rerun unrelated full unit tests or treat harness negative cases as application failures.
- Resolve the pre-existing typecheck issue only through its owning task; it is in an untouched test outside this task's scope.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review — Attempt 1

### Review Status

Changes Requested — Attempt 1. The task returns to `ready`; `executor` and
`claimed_at` are cleared, and Attempt 1 is preserved for the next claim.

### Review Notes

The test-planner/harness changes and namespace/timing instrumentation are within
scope. The partial `importOriginal()` mock already preserves
`ResponseTemplateSchema`, and the Tool Editor unit suite passed. The current
submission does not meet its live-fixture acceptance evidence: the five
PostgreSQL/Redis-gated suites were not executed, the discovery test did not
prove the 60-allowed/61st-`RATE_LIMITED` behavior, and the full-lane invocation
returned no usable result. An image-pull timeout is a truthful environment
blocker, but it does not demonstrate that the new test workflow provisions,
runs and cleans up its disposable fixtures.

### Reviewed Files

- `tests/discovery-limits.test.ts`
- `scripts/arch044-test-plan.mjs`
- `scripts/run-c20-fixture-disposable.mjs`
- `docs/arch044-disposable-tests.md`
- The task Completion Report and validation evidence.

### Validation Reviewed

- Reported harness contract tests: 15/15 passed.
- Reported Tool Editor dispatch unit test: 9/9 passed.
- Reported build and strict i18n validation passed; Attempt 1 automated results remain applicable because Attempt 2 changed no application source.
- The disposable PostgreSQL image pull timed out before resource creation or test execution; live Redis 60/61 behavior and the full suite therefore remain unverified.
- Architect review ran `git diff --check origin/main...HEAD` and `git show --check dbaec9c`; both passed.
- The reported typecheck failure is in untouched `tests/system-commerce-tool-sync.test.ts` and remains outside this task's scope.

### Architecture Conformance

The submitted code does not change production quota or Redis behavior. The
synthetic admin identity includes the run namespace and the test preserves the
60/61 assertions and 30-second deadline. Acceptance still requires live
disposable-fixture evidence for the declared scenarios.

### Follow-up

On the next attempt, run the five blocked PostgreSQL/Redis suites with the
disposable harness, including `tests/discovery-limits.test.ts`; record the
actual 60 admissions, 61st rejection, timing and owned-resource cleanup. Run
the required fixture-backed full path and capture its exit status and suite
results. Preserve honest failure reporting; do not alter the quota, deadline,
or skip suites to manufacture a pass. The parent task remains `ready` at
Attempt 1 with no executor or claim. `ARCH-044-COMMERCE-007` remains pending.
