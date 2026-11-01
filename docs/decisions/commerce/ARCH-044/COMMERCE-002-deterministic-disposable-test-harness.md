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
attempt: 1
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
- [ ] Namespace-scope and instrument the discovery-admission test without changing 60/61 quota or the 30-second deadline. Live Redis timing and 60/61 outcome remain unverified because the disposable image pull timed out before test execution.
- [x] Update reproducible command and fixture diagnostics documentation without logging secrets.

## Interfaces / Contracts

`COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL`, `COMMERCE_C20_REDIS_NAMESPACE`, and C20's `DATABASE_URL === COMMERCE_TEST_DATABASE_URL` invariant for its disposable path. `ResponseTemplateSchema` is the existing module export, not a new contract. Redis discovery admission retains `RATE_LIMITED` semantics.

## Dependencies

None.

## Enables

- `ARCH-044-COMMERCE-007`

## Acceptance Criteria

- [ ] Five PostgreSQL/Redis-gated suites could not be exercised: the disposable runner timed out pulling the pinned PostgreSQL image before creating fixture resources or executing assertions. The sixth named suite, Tool Editor dispatch, passed 9/9 in the unit lane. Database-backed import/setup behavior is not claimed as live-verified.
- [x] Separate unit/UI and integration workflows are documented with the declared npm scripts and no pnpm dependency.
- [ ] Isolation/cleanup behavior is covered by harness contract tests, but successful live PostgreSQL/Redis setup and cleanup could not be evidenced in this attempt.
- [ ] The discovery test now requires the run namespace and emits 60/61 plus request timing diagnostics, but actual 60-allowed/61st-rejected behavior remains unverified due the infrastructure blocker.
- [x] The full-suite planner inventories and partitions every test file and rejects missing/unexecuted suites; a full fixture-backed runtime result is not claimed.

## Validation

- [x] `npm ci` and `npm run prisma:generate` against the task's pinned database schema.
- [ ] Run all six named suites using the disposable test harness; capture setup and cleanup evidence (blocked before suite execution by pinned image pull timeout).
- [ ] `npx vitest run tests/tool-editor-dispatch.test.tsx tests/discovery-limits.test.ts` against appropriate isolated fixtures (Tool Editor passed in unit lane; discovery fixture was blocked before test execution).
- [ ] `npm test -- --maxWorkers=4` with full fixture environment; full-lane wrapper invocation returned no usable output/exit status, so no result is claimed.
- [ ] `git diff --check`: command produced no diagnostic output, but the terminal did not return an explicit exit status; not counted as verified.
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

Ready for Review; disposable integration acceptance is blocked by the local pinned PostgreSQL image pull timeout. No acceptance is claimed for live PostgreSQL/Redis suites or the full suite.

### Files Changed

- `moda-interact-commerce/tests/discovery-limits.test.ts`: require the run-scoped namespace, use it in the synthetic admin identifier, and report admitted count, 61st-request rejection, elapsed time, and maximum per-request latency. The 60/61 contract and 30-second deadline are unchanged.
- `moda-interact-commerce/docs/arch044-disposable-tests.md`: refresh the discovered suite inventory and document the current namespace/timing diagnostics and four-suite general integration phase.
- The existing `tests/tool-editor-dispatch.test.tsx` partial mock already used `importOriginal()` and preserved all real exports, including `ResponseTemplateSchema`; it passed its focused file test and required no change.
- Existing `scripts/run-c20-fixture-disposable.mjs`, `scripts/rehearse-commerce-backend-postgres.sh`, `scripts/run-arch043-platform-configuration-disposable.mjs`, package scripts, and fixture entrypoints were inspected. The established ARCH-044 runners already provide the combined opt-in path and were retained.

### Work Completed

- Confirmed the six historical startup failures and their required fixture inputs from the task table and current test entrypoints.
- Verified the current inventory is 201 files: 186 unit/UI and 15 integration; the runner partitions all files and requires the isolated and dedicated suites to be registered.
- Added run namespace scoping and useful per-request timing/rejection evidence to the discovery test without altering production admission logic or test deadline.
- Documented that `test:arch044:unit` and `test:arch044:integration` / `test:arch044:full` are distinct paths, and that disposable fixture failures are non-success outcomes.
- Harness contract tests verify loopback Docker enforcement, run-owned resource cleanup after partial setup, report completeness, per-suite database isolation, and rejection of unsafe source/environment inputs. These are harness-level tests, not evidence that a live disposable run completed.

### Validation Results

- Environment: macOS; Node `v24.21.0` and npm `11.19.0` were available (repository `.nvmrc` pins Node `24.19.0`). No alternate installer was used.
- `npm ci`: completed successfully; 905 packages installed. npm emitted the pinned Node engine mismatch warning and dependency audit warnings; these were not remediated because dependency upgrades are outside scope.
- `npm run prisma:generate`: passed; generated Prisma Client `6.19.3` from `database/prisma/schema.prisma`. The prepared database submodule remained at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- `npm run test:arch044:harness`: passed, 15/15 Node tests, 0 failed. The test intentionally simulating a failing full-suite report named `tests/add-capability-route.test.tsx`; that is a harness negative-case fixture, not a live Vitest failure.
- `npm run test:arch044:unit -- tests/tool-editor-dispatch.test.tsx`: passed, 1 file / 9 tests, 0 failed or skipped.
- `npm run test:arch044:focus -- tests/discovery-limits.test.ts`: failed before test execution while pulling `pgvector/pgvector:pg17` (`pull postgres: TIMEOUT`, runner pull deadline 300 seconds). Output showed `Docker context PASS`, then the image pull, followed by `[C20-FIXTURE] FAILED`; no database/Redis test assertion ran and no fixture resources had been created. A subsequent invocation returned no usable output/exit status and is not counted as evidence. Therefore 60 permitted / 61st rejected and live cleanup remain unverified.
- `npm run test:arch044:full`: invoked once, but the terminal returned no usable output or exit status; no full-suite result is claimed. The required internal `npm test -- --maxWorkers=4` phase is therefore unverified.
- `npm run typecheck`: exit 1 after schema sync and Next route type generation. `tsc` reported `tests/system-commerce-tool-sync.test.ts:305:72`, TS2345 (`{}` is not assignable to `ProcessEnv`; required `NODE_ENV` missing). This is in an untouched, unrelated test. The editor diagnostic tool reported no errors in the modified `tests/discovery-limits.test.ts`.
- `git diff --check`: pending explicit exit evidence.
- The requested combined `npx vitest run tests/tool-editor-dispatch.test.tsx tests/discovery-limits.test.ts` was not run as a raw command because the files require different fixture lanes. Tool Editor was verified in the unit lane; discovery was invoked through the disposable focus lane and blocked before test execution.
- No assertion failures from live integration suites are known because the disposable PostgreSQL image pull prevented suite execution. The current attempt does not establish that the six named suites or all remaining tests pass.

### Worktree / Synchronisation Evidence

- Launcher prepared execution packet: task `ARCH-044-COMMERCE-002`, Attempt 1, executor `copilot`; claim commit `c61ad509466f3bddb44909884669f88782f082b6`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-002`, branch `task/ARCH-044-COMMERCE-002`, prepared HEAD `15d505ef0f84e8cab57af43dee0d78a83d969f93`.
- Implementation change commit: `dbaec9c` (`test(commerce): namespace discovery admission fixture`), pushed to `origin/task/ARCH-044-COMMERCE-002`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-002`, branch `task/ARCH-044-COMMERCE-002`, prepared pre-claim HEAD `d70081a49fdd91a85336d303fcac75502e42eea7`; launcher claim commit is above.
- Launcher evidence: dedicated worktrees, matching task branches, clean initial worktrees, dependency gate passed (no explicit dependencies), and recursive database submodule ready at `af77c594ecbfc78c26d01c0021a090830884bbff`. Prepared synchronization was not rerun.
- Parent report commit: `daedbab19` (`docs(ARCH-044-COMMERCE-002): record harness validation`), pushed to `origin/task/ARCH-044-COMMERCE-002`.
- Both remote task refs were verified at implementation `dbaec9c` and parent `daedbab19`; both task worktrees are clean. No submodule gitlink, other task file, index, architecture document, or main branch was modified.

### Deviations

- The ARCH-044 fixture scripts and `tests/tool-editor-dispatch.test.tsx` mock were already present in the prepared implementation snapshot. Existing implementations were validated and reused rather than duplicated or rewritten.
- Live disposable test evidence is blocked by the PostgreSQL image pull timeout. This task is being returned for review with that limitation explicit; no test result is inferred from fake-Docker harness simulations.

### Assumptions

The named ARCH-044 opt-in scripts remain the approved fixture entrypoints. The PostgreSQL image pull timeout is an external local infrastructure/network blocker, not evidence of an application or test assertion failure.

### Unresolved Issues

- Rerun `npm run test:arch044:focus -- tests/discovery-limits.test.ts` once the pinned image is available; record admitted count, 61st rejection, latency, and owned-resource cleanup.
- Run the six required PostgreSQL/Redis suites and `npm run test:arch044:full` with the disposable harness once image provisioning is available. Record each suite's actual totals and every failure; do not treat the harness's synthetic negative-case failure as an application result.
- Capture an explicit exit code for `git diff --check`; its invocation produced no diagnostic output but the terminal did not expose an exit status.

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
