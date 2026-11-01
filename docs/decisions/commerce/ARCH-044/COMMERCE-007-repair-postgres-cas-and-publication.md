---
id: ARCH-044-COMMERCE-007
architecture_id: ARCH-044
title: Repair durable agent-configuration CAS and publication transaction validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on: [ARCH-044-COMMERCE-002]
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Repair durable agent-configuration CAS and publication transaction validation

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Resolve the two existing PostgreSQL-backed correctness failures involving retained agent-configuration versions and publication transaction lifecycle while preserving CAS, rollback and idempotency guarantees.

## Context

Baseline `tests/agent-configuration-retained-read.test.ts:93` expected `{kind:"ok"}` during model/prompt pointer clear/set across one retained row, but received `{kind:"error"}`. This uses an in-memory Prisma substitute; determine whether the service contract, test-double methods/versions or real database behavior diverge. Separately `tests/backend-postgres-rehearsal.test.ts` failed in `src/commerce/integration/backend/publication-storage.ts:139` during `commerceAuditEvent.create()` with Prisma `Transaction not found` (closed/expired transaction) after roughly 50 seconds. No evidence yet proves whether this reflects timeout, test-fixture loading or actual transaction design. These are two specific cases of durable-state test correctness; if their root causes prove independent and substantial, report a bounded split to the architect instead of opportunistic refactoring.

## Scope

- Use ARCH-044-COMMERCE-002 disposable test infrastructure for controlled PostgreSQL reproduction; inspect `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/publication/lifecycle.ts`, and the model/prompt configuration services.
- Compare test-double capabilities and accepted state transitions for retained model and prompt pointers, CAS versions and replay behavior; verify real PostgreSQL semantics where relevant.
- Reproduce publication audit write transaction expiry under measured conditions, including query count/duration, isolation, retries, event ownership and rollback semantics; correct bounded implementation/test setup as evidence requires.
- Preserve durable idempotency, stale-version denial, audit write atomicity and rollback. Do not mask Transaction-not-found by ignoring failed writes.

## Out of Scope

- No Prisma schema/migrations in Commerce, no global transaction-timeout override without measurement, and no production database mutation during tests.
- No changes to unrelated Studio form/UI tests or Redis admission quota.

## Requirements

1. Model and prompt mutations have separate CAS versions on one retained row; clear actions preserve the counterpart's version and pointer.
2. Replayed operation IDs must be idempotent, stale versions rejected and audit effects not duplicated.
3. Publication writes and audits must remain atomic, with rollback after injected failure and no partial commit after transaction expiry.
4. PostgreSQL integration must use isolated disposable data, bounded concurrency and cleanup, and record effective transaction settings before changing them.

## Work Items

- [ ] Reproduce the historical retained-read `{kind:"error"}` and establish its exact cause. On the current generated Prisma Client, the focused test passes; this does not establish why the historical failure occurred.
- [x] Validate model/prompt pointer and edit-version semantics in real disposable PostgreSQL: the isolated model suite passed 8/8.
- [ ] Reproduce the historical publication transaction expiry. The bounded profile runs passed without `Transaction not found`; query counts, durations and effective transaction settings were captured.
- [x] Make only evidence-supported changes. No production storage behavior, timeout, isolation setting or schema was changed; the task added bounded opt-in diagnostic instrumentation because the historical expiry did not reproduce.
- [x] Verify regression coverage for idempotency, CAS races and audit rollback in the existing PostgreSQL rehearsal; its scenarios passed in repeated disposable runs.

## Interfaces / Contracts

PostgreSQL durable state via canonical `moda-interact-database` Prisma schema; model/prompt `modelEditVersion` and `promptEditVersion`; `CommerceAuditEvent`, publication CAS and operation IDs. No database-owned schema edits allowed in Commerce; refer migration need to moda_architect/moda_database.

## Dependencies

- `ARCH-044-COMMERCE-002` — accepted Complete, with a reproducible fixture handoff.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] `tests/agent-configuration-retained-read.test.ts` passes; separate model/prompt CAS behavior also passed the real disposable PostgreSQL model suite. The historical in-memory `{kind:"error"}` cause remains unproven.
- [x] `tests/backend-postgres-rehearsal.test.ts` passed repeatedly using disposable PostgreSQL without closed/expired transaction errors.
- [x] Publication rollback, replay, stale CAS and two-client race scenarios pass and remain atomic in the rehearsal.
- [x] No test suppresses errors, extends transaction settings arbitrarily or writes to non-disposable resources.
- [ ] Complete evidence distinguishes environment, fixture and production defects for each original failure.

## Validation

- [ ] `npx vitest run tests/agent-configuration-retained-read.test.ts`.
- [ ] Existing `npm run test:arch020-backend-integration:postgres` rehearsal and `tests/backend-postgres-rehearsal.test.ts` under disposable infrastructure (follow actual script requirements).
- [ ] `npx vitest run tests/agent-configuration-model.test.ts tests/agent-configuration-effective.test.ts tests/commerce-lifecycle.test.ts`.
- [ ] `npm run typecheck`, affected integration validation, `git diff --check`.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

Dependent on ARCH-044-COMMERCE-002 so tests have an explicit disposable PostgreSQL path. If investigation requires a Prisma model/constraint change, stop and return the ownership gap to moda_architect for a database-owned task rather than editing nested `database/` schema source.

### Exact failing tests

- `tests/agent-configuration-retained-read.test.ts` — `tracks model and prompt CAS versions on one retained row across clear operations`.
- `tests/backend-postgres-rehearsal.test.ts` — `publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure`.

## Completion Report

### Attempt 1 Status

Ready for architect review — Attempt 1. Current focused tests pass and diagnostic profiling did not reproduce the historical publication expiry. The exact causes of the historical retained-read error and publication `Transaction not found` remain unproven, so the final acceptance criterion is unchecked and no root-cause claim is made. The task lifecycle is `review`; execution claim cleared.

### Files Changed

- `scripts/arch044-disposable-suites.mjs`: relay only the bounded, allow-listed publication profile metrics from the focused disposable runner.
- `scripts/arch044-test-plan.test.mjs`: verify the profile output format and that credentials, SQL and fixture markers are not relayed.
- `tests/backend-postgres-rehearsal.test.ts`: collect per-proof query durations and report elapsed time, query count/durations and the effective `ReadCommitted`, 1,000 ms max-wait and 10,000 ms timeout values when `ARCH044_C007_PROFILE=1`. Default runs do not emit these diagnostics.

### Work Completed

- Reused the ARCH-044-COMMERCE-002 disposable runner, which provisions isolated, run-owned PostgreSQL/pgvector and Redis resources, checks the host loopback PostgreSQL port before exposing the database URL, and cleans up owned resources.
- The retained-read test passes with the current generated Prisma Client. The executor reported running `npm run prisma:generate`; neither the historical `{kind:"error"}` nor its cause was independently reproduced, so regeneration is not claimed as the proven fix.
- The real PostgreSQL model suite verified model/prompt configuration behavior and passed 8/8.
- The existing publication rehearsal covers durable replay, operation reuse conflict, stale CAS, a two-client same-row race, audit effects, and rollback after an injected failure. It passed repeatedly; no `publication-storage.ts` or lifecycle production behavior was changed.
- No schema, transaction timeout, isolation level, test deadline, or application behavior was changed. No shared or production database/Redis resource was used.

### Validation Results

- Environment: macOS, Node `v24.21.0`, npm `11.19.0`; package `engines.node` specifies `24.19.0`. Recursive `database` submodule was initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- `npx vitest run tests/agent-configuration-retained-read.test.ts`: passed, 1 file / 1 test.
- `npm run test:arch044:focus -- tests/agent-configuration-model-postgres.test.ts`: passed, 1 file / 8 tests against disposable PostgreSQL; cleanup reported zero owned Docker resources.
- `ARCH044_C007_PROFILE=1 npm run test:arch044:focus -- tests/backend-postgres-rehearsal.test.ts`: passed, 1 file / 3 tests. The publication/replay/CAS/rollback proof measured 2,002 ms elapsed, 215 queries, 2,004 ms total query time and 61 ms maximum query time. The narrow create/duplicate/race/rollback proof measured 685 ms elapsed, 62 queries, 677 ms total query time and 59 ms maximum query time. Both reported `ReadCommitted`, `maxWaitMs=1000`, `timeoutMs=10000`; cleanup reported zero owned Docker resources. The executor reported two additional profiled disposable rehearsal runs passing 3/3 each; the historical expiry did not recur.
- `npx vitest run tests/agent-configuration-model.test.ts tests/agent-configuration-effective.test.ts tests/commerce-lifecycle.test.ts`: passed, 3 files / 53 tests.
- `npm run test:arch044:harness`: passed, 16/16 contract tests, including bounded metric relay/redaction and full planner completeness contracts. Synthetic planner results are harness contract evidence, not live application test results.
- `git diff --check`: passed for the implementation change.
- `npm run typecheck`: exited 2 on the existing unrelated `tests/system-commerce-tool-sync.test.ts:305:72` TS2345 error (`{}` lacks required `NODE_ENV` in `ProcessEnv`). This file was not changed by this task.
- The separate legacy `npm run test:arch020-backend-integration:postgres` wrapper was not invoked because it requires a caller-supplied `DATABASE_URL`; the prescribed ARCH-044 disposable focus was used instead to guarantee isolated provisioning and cleanup. The focused run executed `tests/backend-postgres-rehearsal.test.ts` against that disposable target.
- Historical failure caveat: current focused runs do not reproduce the retained-read `{kind:"error"}` or the publication `Transaction not found` after roughly 50 seconds. Measurements show the current rehearsal completing within the unchanged 10-second transaction timeout, but this is not proof of the historical failure's cause.

### Worktree / Synchronisation Evidence

- Prepared launcher result: `prepared_execution=true`, dependency gate passed because `ARCH-044-COMMERCE-002` was `complete`; task claimed as Attempt 1, executor `copilot`, claim timestamp `2026-11-01T17:59:30Z`, claim commit `1aa6857e7604624da6e524f0fb364d24a8214b15`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-007`, branch `task/ARCH-044-COMMERCE-007`, initial head `d0ade086b60b42a4145cc7e50836c2b2c8258de5`, recursive submodule ready at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-007`, branch `task/ARCH-044-COMMERCE-007`, initial head `f680efdf759de244027570d07d0bf8213c4b3b3b`.
- Implementation commit `04b2a1309bc74081bb1907b5794bfc2332ffbdf6` (`test(commerce): relay publication rehearsal diagnostics`) is published on `origin/task/ARCH-044-COMMERCE-007`. Only the three files listed above were changed in the implementation repository; no nested database gitlink or `main` branch was changed.
- Parent report is the only parent-worktree file changed for completion; the Attempt 1 claim is cleared in frontmatter and this report is submitted at `review`.

### Deviations

- The baseline error causes could not be reproduced on the current checkout. Diagnostic instrumentation and repeated focused proof runs were added to capture bounded evidence without changing application behavior or transaction settings. Acceptance criterion 5 remains open for architect disposition.

### Assumptions

The named ARCH-044 disposable focus is the approved isolated PostgreSQL path. The historical baseline descriptions are accurate records but are not independently replayable from the current task base with the evidence available in this attempt.

### Unresolved Issues

- Establish the historical cause of the in-memory retained-read `{kind:"error"}` and the approximately 50-second publication `Transaction not found`; current passing focused tests and measured transaction timings do not establish that root cause.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

No schema, database ownership, cross-service contract, or deployment changes were required.

### Attempt 2 — Historical evidence comparison

#### Status

Ready for architect disposition — Attempt 2. The publication-expiry criterion remains unproven, so the task is `ready`, not review-ready. The Attempt 2 claim is cleared. No implementation files changed and no implementation commit was created. Attempt 1 validation and this complete Architect Review are preserved.

#### Evidence table

| Evidence source | Historical/baseline evidence | Prepared snapshot comparison | Result and uncertainty |
|---|---|---|---|
| `baseline-vitest.log` and `typescript(20261018-183033)` | The task and ARCH-044 document describe the retained-read `{kind: "error"}` and publication `Transaction not found` after roughly 50 seconds. The baseline Git SHA was not recorded. | Searched the canonical workspace and both prepared worktrees, including hidden/ignored paths, for `baseline-vitest.log`, `20261018-183033`, and task-named artifacts. No matching artifact was available. | Original stack details, runner profile, fixture contents, and environment cannot be cross-checked. The architecture confirms the logs were external and the exact baseline SHA was unknown. |
| Retained-read test double and service contract | The pre-correction test at `7dfc284^` has no `shop` delegate; its model has no `availabilityId`, `configurationSchemaVersion`, `configuration`, or availability relation. | Commit `7dfc284` (2026-10-19) adds `shop.findUnique`, those model/availability fields and relation, and current provider casing. `assertModelSelectable` calls `shop.findUnique` and queries the model with `include: { availability: true }`; the configuration service maps an uncaught fake-method/shape failure to `{kind: "error"}`. `git diff --stat 7dfc284^ HEAD` shows only the retained-read test changed among the scoped model/prompt source, availability helper and test paths. The current focused test passed 1/1 in Attempt 1. | A concrete test-double contract mismatch is identified and is sufficient to produce an error with the unchanged service; the fixture correction aligns the fake to the required service calls. The exact baseline SHA/log is unavailable, so linkage to the recorded historical assertion is strong but not independently auditable against that log. No production defect is demonstrated. |
| Publication storage and rehearsal | The report describes an audit-create failure after about 50 seconds, but supplies no historical query timeline, row counts, or execution profile. | `15d505e` (2026-10-31) changes `publication-storage.ts`: it avoids per-release/feature/member existence queries, uses initial release/audit IDs to persist only new immutable rows, and batches audit inserts. The source change is explicitly intended to avoid history-proportional work exhausting the fixed deadline. Attempt 1's current disposable profile passed 3/3 with `ReadCommitted`, `maxWaitMs=1000`, `timeoutMs=10000`; measured proofs were 2,002 ms / 215 queries / 2,004 ms total query time / 61 ms max query, and 685 ms / 62 queries / 677 ms total / 59 ms max. | The historical query-amplification path and later optimization are established, making transaction-duration pressure plausible. No baseline metrics or original invocation/environment were found, and the historical source/profile was not safely replayable from available artifacts. Therefore the optimization cannot be claimed as the proven cause of the reported expiry. |
| Prisma client and database schema | No historical generated-client artifact was available. | At `7dfc284^`, `package.json` and `package-lock.json` declare `prisma` and `@prisma/client` 6.19.3; current declarations and generated client are also 6.19.3. The known submodule pin changed from `aa3fd024db3a1484f72f8033b87f56ad27f4640d` to `af77c594ecbfc78c26d01c0021a090830884bbff`; the scoped schema diff contains no changes to agent configuration CAS fields or model availability fields. | No Prisma version change is evidenced across those known snapshots. An exact baseline-generated-client comparison remains unavailable because the baseline SHA and generated artifact were not supplied. |

#### Commands and validation

- Scoped Git history/diffs: inspected `7dfc284^..7dfc284` for the retained-read test double and publication rehearsal, and `15d505e` for publication storage, package declarations, and schema reference. The retained-read implementation paths were unchanged in the scoped `7dfc284^..HEAD` comparison.
- Artifact search: no baseline log or named historical run artifact was present in the canonical workspace, parent worktree, or implementation worktree. The implementation artifact directory contains ARCH-020-COMMERCE-008 screenshots, not these baseline logs.
- Package scripts were read from the implementation `package.json` before deciding on validation. No tests were rerun because no code changed and the Attempt 1 passing results remain the current implementation evidence. The unrelated `npm run typecheck` TS2345 failure remains as recorded in Attempt 1; it was not rerun.
- No disposable database was provisioned during Attempt 2, so no database cleanup was required. Attempt 1 reports zero owned Docker resources after its disposable runs.
- No implementation commit or push was made. This parent task report is the only Attempt 2 change and will be committed and pushed on the mirrored task branch.

#### Disposition requested

The retained-read fake's missing required methods/availability data is a specific, code-supported explanation, but the original baseline log and source SHA are unavailable for exact historical confirmation. The publication failure's root cause remains unknown; only a plausible history-sensitive query cost and a later optimization are evidenced. Acceptance Criterion 5 remains unchecked. Request explicit architect disposition on whether the retained-read comparison is sufficient and what historical publication evidence or bounded follow-up is required before this criterion can be completed.

## Architect Review — Attempt 1

### Review Status

Changes Requested — Attempt 1. The task returns to `ready`; `executor` and
`claimed_at` are cleared. Attempt 1 and its validation evidence remain
preserved.

### Review Notes

The bounded diagnostics and disposable PostgreSQL validation are in scope, and
current focused runs pass without changing production transaction behavior.
However, the explicit Work Item to establish the cause of the historical
retained-read `{kind:"error"}` and publication `Transaction not found` remains
unchecked. The Acceptance Criterion requiring evidence that distinguishes an
environment, fixture or production defect for each original failure is also
unchecked. Current tests passing after Prisma generation, and short focused
profiles completing within the existing 10-second transaction timeout, prove
that the failures do not reproduce in this prepared snapshot; they do not
explain the historical failures.

### Reviewed Files

- `tests/agent-configuration-retained-read.test.ts`
- `tests/backend-postgres-rehearsal.test.ts`
- `src/commerce/integration/backend/publication-storage.ts`
- `src/commerce/publication/lifecycle.ts`
- `scripts/arch044-disposable-suites.mjs`
- `scripts/arch044-test-plan.test.mjs`
- The Completion Report and Attempt 1 validation evidence.

### Validation Reviewed

- Retained-read test: 1/1 passed; the historical `{kind:"error"}` was not
  reproduced.
- Disposable model PostgreSQL suite: 8/8 passed.
- Disposable publication rehearsal: 3/3 passed; measured transaction
  isolation, max-wait and timeout remained `ReadCommitted`, 1000 ms and
  10000 ms. The profiled proofs completed in 2002 ms and 685 ms, with no
  `Transaction not found` error.
- Related model/effective/lifecycle tests: 53 passed; harness contract tests:
  16/16 passed.
- `git diff --check` passed. The existing unrelated TS2345 typecheck error is
  accurately attributed outside this task.

### Architecture Conformance

No production transaction, schema, isolation or timeout behavior changed.
The instrumentation is opt-in and relays only bounded query count/duration and
fixed transaction settings. No SQL, credentials or fixture identifiers are
relayed. The implementation remains within scope, but the root-cause evidence
required for acceptance is incomplete.

### Follow-up

Compare each original failure with its historical baseline evidence. For the
retained-read case, identify the relevant source/test-double/generated-client
change between the failing baseline and the prepared snapshot, or provide a
reproducible before/after comparison. For publication expiry, run the historical
rehearsal under the original execution profile and capture the bounded
transaction/query timeline, or compare the archived baseline invocation and
environment with the current disposable focused path. If the historical
artifacts cannot reproduce, record which evidence is unavailable and request
an explicit disposition before marking the criterion complete. Do not change
transaction settings or suppress the failures to force a pass. No downstream
dependency status changed.
