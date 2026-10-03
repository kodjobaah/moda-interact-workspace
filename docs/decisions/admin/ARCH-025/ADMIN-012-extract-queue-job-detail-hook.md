---
id: ARCH-025-ADMIN-012
architecture_id: ARCH-025
title: Extract QueueMonitor selected-job detail hook
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-03T09:00:46Z
attempt: 3
depends_on:
  - ARCH-025-ADMIN-011
enables:
  - ARCH-025-ADMIN-013
created: 2026-10-02
updated: 2026-10-03
---

# Extract QueueMonitor selected-job detail hook

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract selected-job identity/detail/loading/error/AbortController lifecycle into a dedicated hook and close the accepted ADMIN-011 selection-invalidation port.

## Context

The selected detail lifecycle is independent of jobs browsing but is cleared by specific jobs transitions. It also has a distinct 404 message and must abort stale requests when queue, selected job or current status changes.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-queue-jobs.ts
src/components/admin/queue-monitor/use-queue-job-detail.ts
tests/unit/queue-monitor-job-detail-state.test.ts

# Architect-authorised Attempt-3 assertion reconciliation only
tests/security/admin-queue-monitor.test.mjs
tests/security/admin-queue-details-drawer.test.mjs
```

## Out of Scope

Drawer/presentation extraction, accepted ADMIN-009 client/type changes, summary-hook changes, server/API changes. The ADMIN-009/011 source-loader mechanics, test names, unrelated jobs/read-only/security/i18n assertions, `admin-failed-job-detail-panel.test.mjs` and `admin-internationalization.test.mjs` remain out of scope; Attempt 3 may change only the three stale detail source-shape assertions identified by the Architect Review in the two explicitly authorised test files.

## Requirements

### Common ARCH-025 QueueMonitor invariants

- This is a **move-only structural refactor**. Do not change QueueMonitor product behaviour, server authorization, Redis/BullMQ reads, HTTP response shapes, queue-job normalization/redaction, i18n/catalogue semantics or diagnostic exposure.
- Preserve `QueueMonitor` at `src/components/admin/queue-monitor.tsx` with the same exported name/caller boundary. Existing protected-page callers do not migrate.
- QueueMonitor remains strictly read-only. Do not add retry, requeue, delete, pause, resume or other mutation controls.
- Preserve the existing protected endpoints exactly: `/api/admin/queues`, `/api/admin/queues/jobs`, `/api/admin/queues/jobs/detail`. Do not change their routes, authorization ordering or response semantics.
- Preserve `src/lib/admin/queue-monitor.ts` as the canonical server reader/type owner. Browser modules must not import it at runtime; the client uses a bounded local mirror of the HTTP response shapes.
- Preserve `src/components/admin/queue-monitor-refresh.ts` as the canonical refresh-option/default/storage helper. Do not duplicate or change `REFRESH_OPTIONS`, `DEFAULT_REFRESH_MS`, `STORAGE_KEY`, `isRefreshValue()` or `getInitialRefreshMs()`.
- Preserve summary semantics: initial refresh is scheduled immediately after mount; at most one summary request is in flight; manual/poll attempts while one is running return without starting another; `cache: "no-store"`; aborts do not surface as data errors; failures retain the last successful snapshot; successful summary refresh clears the summary error and, when a queue is open, requests a jobs refresh.
- Preserve jobs semantics: stale requests abort on dependency changes; query keys remain `queue`, `status`, `shop`, `page`, `limit`, `direction`; recent mode uses limit `5`, full mode `10`; successful row replacement clears selected-job/detail state; non-abort failure sets jobs unavailable and clears the jobs snapshot.
- Preserve current state-transition asymmetries exactly: queue switch resets jobs/recent/page/error/selection/detail while retaining shop/status/direction filters and an already-open drawer width; Shop/Status changes explicitly prepare loading, reset page and clear selection/detail; Direction changes explicitly prepare loading/reset page but do not immediately clear selected detail; page changes and View all do not use the same explicit prepare-loading transition as filters.
- Preserve detail semantics: stale selections abort; detail query keys remain `queue`, `status`, `jobId`; HTTP 404 maps to `queue.jobGone`; other non-OK responses map to `queue.jobDetailsUnavailable`; aborts do not surface a user error.
- Preserve drawer semantics: first open starts maximized, switching queues while open preserves the current drawer width, close clears only selected queue/width/resizing (not stored jobs/detail), maximize sets width back to `null`, and pointer/keyboard resizing retains current bounds and ArrowLeft/ArrowRight/Home/End meanings.
- Preserve catalogue/i18n ownership: queue job names continue through `adminQueueJobLabel`, statuses through `adminStatusLabel`, dates/times through `adminI18n`, and no raw locale/currency formatting is introduced.
- Preserve bounded diagnostic presentation: selected detail may show the current normalized lifecycle fields, failed reason, stacktrace and normalized payload with copy controls; do not expose Redis/configuration credentials or additional raw provider/queue internals.
- Do not add a Redux/global state store, generic client data framework, generic HTTP framework or new React/browser test framework solely for this extraction.
- Keep tests honest: no skipped tests, weakened assertions or changed expected behaviour merely because code moved. `npm run test:unit`, `npm test` and production build must introduce no task regression.
- These server/API sources are frozen byte-for-byte throughout ADMIN-009..015: `src/lib/admin/queue-monitor.ts` (`f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486`), `/api/admin/queues/route.ts` (`f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408`), `/api/admin/queues/jobs/route.ts` (`fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7`), `/api/admin/queues/jobs/detail/route.ts` (`c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab`).
- These dedicated server/API tests are frozen byte-for-byte throughout ADMIN-009..015: `admin-queue-jobs.test.mjs` (`3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc`), `admin-queue-job-detail.test.mjs` (`e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0`), `admin-failed-job-detail.test.mjs` (`da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195`), `admin-failed-jobs.test.mjs` (`fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609`).

### R1 — detail state ownership

The hook owns `selectedJobId`, normalized detail, detail error/loading and its request AbortController. It consumes current selected queue and current job status as request inputs.

### R2 — operations

Expose select-job, clear/back and invalidate-selection operations. Selecting a job immediately sets identity, clears old detail/error and sets loading true. Clear/back returns to rows and clears detail/error/loading. ADMIN-011 jobs transitions wire to the accepted invalidate operation at exactly the same transitions as the monolith.

### R3 — request semantics

When queue or selected job is absent, abort any current detail request and perform no new request. Otherwise abort stale work and use ADMIN-009 client. 404 => `queue.jobGone`; other non-OK => `queue.jobDetailsUnavailable`; abort => no user error. Success replaces detail/clears error. Loading is cleared only by the current controller.

### R4 — extraction-safe detail source assertions

ADMIN-011 established the accepted jobs-hook source assertions, but three assertions in
`admin-queue-monitor.test.mjs` / `admin-queue-details-drawer.test.mjs` still encode the
pre-ADMIN-012 inline selected-detail implementation. ADMIN-012 Attempt 3 is authorised
to update only those stale expectations so they assert the accepted
`useQueueJobDetail` reducer/operations/invalidation boundary while preserving the same
behavioural/security contract.

Do not change either source loader, any test name, unrelated ADMIN-011 jobs assertions,
read-only/mutation prohibitions, i18n/catalogue assertions, or either of
`admin-failed-job-detail-panel.test.mjs` / `admin-internationalization.test.mjs`.

## Work Items

- [x] Move detail state/request lifecycle to dedicated hook.
- [x] Rewire ADMIN-011 invalidation port to the hook without changing jobs semantics.
- [x] Add focused state/error/abort tests without adding a React test framework.
- [x] Reconcile only the three stale detail source-shape assertions to the accepted `useQueueJobDetail` boundary without weakening behaviour/security assertions.

## Interfaces / Contracts

ADMIN-012 closes the repository-internal jobs/detail coordination contract: jobs owns row/filter/page state; detail owns selection/detail state; jobs may only request detail invalidation through the accepted narrow interface.

## Dependencies

- `ARCH-025-ADMIN-011`

## Enables

- `ARCH-025-ADMIN-013`

## Acceptance Criteria

- [x] No selected-job/detail request state remains duplicated in shell/jobs hook.
- [x] Select/back/invalidation state transitions match current behaviour.
- [x] 404, other non-OK and abort semantics remain exact.
- [x] Jobs success/filter/queue/View-all invalidations remain at the same points as before extraction.
- [ ] The two architect-authorised source-contract files retain their loader/test names/security contract and assert selected-detail ownership through `useQueueJobDetail` rather than the retired inline setters/request lifecycle.

## Validation

- [x] Frozen source/test SHA-256 values match the task specification.
- [x] `git diff` for the frozen server/API sources, refresh helper, and dedicated server tests is empty.
- [x] The ADMIN-009/011 loader mechanics and all non-authorised assertions remain unchanged. Only the three stale detail source-shape assertions in `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs` changed under R4; `admin-failed-job-detail-panel.test.mjs` and `admin-internationalization.test.mjs` remain byte-identical to their accepted ADMIN-009 versions.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-job-detail-state.test.ts` passes (5/5).

- [x] `npm run test:unit` evidence from Attempt 1 remains baseline-conformant: 259 passed; the two failures match `ARCH025-ADMIN-BUILDER-TEST-001`. Attempt 2 introduced no QueueMonitor implementation/test change.
- [x] After the R4 harness correction, run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` and `npm test`. All QueueMonitor-owned assertions pass; only exact unchanged `ARCH025-ADMIN-TEST-001` failures remain in the broad suite.
- [x] Targeted ESLint passes for the changed Admin source files and the new test (`--no-ignore`).
- [x] `npm run build` succeeds. Existing BullMQ critical-dependency/optional Valkey resolution warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-job-detail.ts`
- `tests/unit/queue-monitor-job-detail-state.test.ts`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`

### Work Completed

- Extracted selected job identity, normalized detail, loading/error state, request cancellation, and detail fetching into `useQueueJobDetail`.
- Preserved selection, clear/back, reason-specific invalidation, 404/unavailable error mapping, abort suppression, and active-controller loading completion.
- Connected the existing `useQueueJobs` invalidation callback to the detail hook without changing the jobs hook or its transition points.
- Added reducer/error/abort tests without introducing a React test framework.
- Reconciled exactly the three Architect-authorized source-shape assertions to verify shell selection wiring, the detail reducer's selected/cleared/invalidated transitions, and the jobs-to-detail invalidation port.

### Validation Results

- Focused detail-state tests: 5/5 passed; all three changed source-contract tests: 3/3 passed.
- Required four-file QueueMonitor security run: 27 passed, 2 failed. Every QueueMonitor-owned assertion passed; both failures are the unchanged Shared ICU/version and canonical-catalogue assertions documented in `ARCH025-ADMIN-TEST-001`.
- Targeted ESLint with `--no-ignore` for both changed harness files: passed.
- All nine frozen QueueMonitor server/API/helper/test SHA-256 values matched; frozen-file diff: empty.
- `npm run test:unit`: 259 passed, 2 failed; both exact translation-workbook failures match `ARCH025-ADMIN-BUILDER-TEST-001`.
- `npm test`: 226 passed, 9 failed, 0 skipped; all nine exact failures match `ARCH025-ADMIN-TEST-001`, with no QueueMonitor-owned failure.
- `npm run build`: passed with existing BullMQ critical-dependency and optional Valkey resolution warnings.
- `git diff --check`: passed.

### Deviations

- Attempt 3 made only the three source-shape assertion changes explicitly authorized by Architect Review A2-R1. No test names, loader mechanics, expected runtime/security behavior, or unrelated assertions changed. The broad suites retain only their documented inherited baseline failures.

### Assumptions

- The reconciled ADMIN-012 versions of `admin-queue-monitor.test.mjs` and `admin-queue-details-drawer.test.mjs` are the authorized jobs-and-detail harness baseline for ADMIN-013..015 after architect acceptance.

### Unresolved Issues

- None within ADMIN-012 scope.

### Architectural Concerns

- No runtime/API or hook implementation changes were made in Attempt 3; the authorized source tests now assert the accepted hook ownership boundary.

### Attempt 2 Update (2026-10-03)

#### Outcome

Returned to `moda_architect` for a task/test-contract decision. No implementation source or test files were changed in Attempt 2; the Attempt 1 implementation remains intact and the existing Architect Review section below remains unchanged and Pending.

#### Work Completed

- Re-read the full task contract and pending Architect Review before inspecting implementation sources.
- Reproduced the unchanged accepted QueueMonitor source-contract failures. The assertions require the former inline `setSelectedJobId` / `setJobDetail` / `setJobDetailError` layout and do not recognize the required hook-owned invalidation operation.
- Did not weaken or modify the accepted security tests, add source-only compatibility shims, or alter the hook ownership contract.

#### Validation Results

- `node --experimental-strip-types --test tests/unit/queue-monitor-job-detail-state.test.ts`: 5/5 passed.
- `admin-queue-monitor.test.mjs` and `admin-queue-details-drawer.test.mjs`: 16/19 passed. The three failures are source-shape assertions in `queue monitor renders a bounded four-state job summary without mutation actions`, `queue names switch diagnostics without resetting an open drawer`, and `queue drawer keeps the full browser paginated and state-safe`.
- All nine task-frozen server/API/helper/test SHA-256 values match the task specification.
- Implementation worktree `git diff --check` passed and was clean of source changes. The required ADMIN-012 mainline synchronization was published on the task branch.
- Full unit/security suites and production build were not rerun because Attempt 2 made no implementation-source changes; Attempt 1's full-suite baseline evidence remains above.

#### Contract Decision Required

ADMIN-012 requires selected-job state and invalidation to be owned by `useQueueJobDetail`, with jobs transitions using its narrow invalidation operation. The accepted ADMIN-011 security tests instead require the old inline setter syntax in the QueueMonitor source and its callback. Those assertions are outside this task's authorized test-change boundary, while the task's Validation section requires accepted tests to remain unchanged. Please decide whether the accepted source-shape assertions may be updated to validate the extracted hook contract, or whether ADMIN-012's implementation contract should be amended to require a source-visible compatibility surface. Until that decision is durable, this attempt cannot satisfy both constraints without weakening tests or violating the ownership boundary.

#### Physical Worktree / Synchronization Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-012`, branch `task/ARCH-025-ADMIN-012`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-012`, branch `task/ARCH-025-ADMIN-012`.
- Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.
- Parent remote task branch fast-forwarded: not-needed. Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed. Implementation `origin/main` incorporated: yes.
- Recursive submodule sync: passed. Recursive submodule update: passed. Verified initialized submodule: `database` at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Attempt 3 Update (2026-10-03)

#### Outcome

Implemented the three A2-R1 assertion reconciliations and completed required validation. The accepted `useQueueJobDetail` implementation was not changed.

#### A2-R1 Disposition

- `queue names switch diagnostics without resetting an open drawer`: implemented in `tests/security/admin-queue-details-drawer.test.mjs`; verifies the existing `onSelectionInvalidated` forwarding callback, shell ref assignment to `jobDetailState.invalidateSelection`, reducer clearing of selected identity/detail, and reason-specific error/loading reset. The named test and ADMIN-011 queue-selection assertions remain unchanged.
- `queue drawer keeps the full browser paginated and state-safe`: implemented in `tests/security/admin-queue-details-drawer.test.mjs`; verifies the shell Back action invokes `clearSelection` and the reducer returns the complete initial detail state. Existing pagination/View-all assertions remain unchanged.
- `queue monitor renders a bounded four-state job summary without mutation actions`: implemented in `tests/security/admin-queue-monitor.test.mjs`; verifies row selection invokes `selectJob(job.id)` and the reducer sets selected identity, clears old detail/error, and starts loading. Existing bounds, labels, and read-only prohibitions remain unchanged.

#### Attempt 3 Validation

- Three changed source-contract tests: 3/3 passed.
- Detail reducer/error/abort unit tests: 5/5 passed.
- Four-file QueueMonitor security run: 27/29 passed; the only failures are the exact unchanged Shared ICU version and canonical-catalogue baseline failures from `ARCH025-ADMIN-TEST-001`. Every QueueMonitor-owned assertion passed.
- Full unit suite: 259/261 passed; both unchanged translation workbook failures are documented in `ARCH025-ADMIN-BUILDER-TEST-001`.
- Full security/observability suite: 226/235 passed; all nine unchanged failures match `ARCH025-ADMIN-TEST-001`.
- Targeted ESLint, all nine frozen SHA-256 checks, frozen-file diff, production build, and `git diff --check`: passed.
- Build retained only the known BullMQ critical-dependency and optional Valkey resolution warnings.

## Architect Review

### Review Status

Changes Requested — Attempt 2.

### Review Notes

Attempt 2 correctly stopped without changing source/tests because the task record did
not contain a durable architect decision authorising changes to the accepted
ADMIN-011 harness. The contract decision is now explicit:

**Keep the `useQueueJobDetail` implementation. Do not reintroduce inline detail state,
setters or request code. Reconcile only the three stale source-shape assertions.**

The substantive ADMIN-012 implementation
`1a1989051414376e23f7870f6557736df8a8ab46` remains accepted in substance. It owns
selected-job identity, normalized detail, detail error/loading and the detail request
AbortController behind `useQueueJobDetail`, while ADMIN-011 jobs state continues to
invalidate selection only through the narrow callback.

Old-vs-new inspection confirms the required semantics are preserved:

- `selectJob(jobId)` immediately sets identity, clears old detail/error and sets
  loading true;
- `clearSelection()` aborts current detail work and returns detail state to its initial
  state;
- queue/filter/View-all/jobs-replaced invalidation is still triggered at the exact
  ADMIN-011 transition points;
- `queue-selection` and `jobs-replaced` clear detail error/loading, while
  `filter-change` / `view-all` preserve their established asymmetric error/loading
  state after clearing identity/detail;
- detail request keys remain `queue`, `status`, `jobId`;
- stale requests abort;
- HTTP 404 maps to the existing `queue.jobGone` message;
- other `QueueJobDetailHttpError` failures map to
  `queue.jobDetailsUnavailable`;
- ordinary `Error.message` remains surfaced exactly as before;
- aborts never become user-facing errors;
- only the currently-owned AbortController clears loading.

The focused state/error/abort suite remains 5/5 and all nine frozen QueueMonitor
server/API/helper/test hashes reproduce exactly.

Attempt 2 also incorporated current `origin/main` into the implementation task branch.
GitHub comparison from reviewed detail-hook `1a198905...` to current task head
`66198c72085168275b5e3d0f290ced660a20caab` shows only unrelated ADMIN-005
Merchant Pricing files:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/usage-events-step.tsx
```

No QueueMonitor source/test, frozen file, package manifest, lockfile or dependency
configuration changed. The Attempt 1 implementation review therefore remains valid.

#### A2-R1 — update only the three stale detail source-shape assertions

Attempt 3 is authorised to modify only:

```text
tests/security/admin-queue-monitor.test.mjs
tests/security/admin-queue-details-drawer.test.mjs
```

Keep the existing ADMIN-009/011 source-loader functions, loader order/scope, all test
names and every unrelated jobs/read-only/security/i18n/catalogue assertion unchanged.

Update exactly these three tests:

1. `queue names switch diagnostics without resetting an open drawer`
   - keep the accepted ADMIN-011 queue-selection/jobs reducer assertions;
   - replace the old inline jobs-to-detail callback-body expectation with the shell
     forwarding contract:
     `onSelectionInvalidated: (reason) => invalidateSelectionRef.current(reason)`;
   - assert the shell effect wires `invalidateSelectionRef.current` to
     `jobDetailState.invalidateSelection`;
   - assert the detail reducer's `selection-invalidated` branch clears
     `selectedJobId` / `jobDetail` and applies the reason-specific
     error/loading behavior.

2. `queue drawer keeps the full browser paginated and state-safe`
   - keep all accepted ADMIN-011 pagination/View-all assertions;
   - replace the stale `setJobDetailError(null)` / inline Back-state shape with
     shell `onClick={clearSelection}` plus the detail reducer's
     `selection-cleared` -> initial-state contract.

3. `queue monitor renders a bounded four-state job summary without mutation actions`
   - preserve all existing route/query/status/catalogue/read-only assertions;
   - replace the stale inline `setSelectedJobId` selection expectation with
     `selectJob(job.id)` shell wiring plus the `job-selected` reducer contract
     proving selected ID, old detail/error clearing and loading start.

Do not modify:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-queue-job-detail.ts
src/components/admin/queue-monitor/use-queue-jobs.ts
tests/unit/queue-monitor-job-detail-state.test.ts
tests/security/admin-failed-job-detail-panel.test.mjs
tests/security/admin-internationalization.test.mjs
```

unless validation exposes a genuine ADMIN-012 runtime regression.

After the three assertion corrections, run:

```bash
node --experimental-strip-types --test   tests/unit/queue-monitor-job-detail-state.test.ts

node --test   tests/security/admin-queue-monitor.test.mjs   tests/security/admin-queue-details-drawer.test.mjs   tests/security/admin-failed-job-detail-panel.test.mjs   tests/security/admin-internationalization.test.mjs

npm test
```

All QueueMonitor-owned assertions must pass. The broad suite may retain only exact
unchanged `ARCH025-ADMIN-TEST-001` failures. Also rerun the frozen hash check, targeted
ESLint for the two changed harness files (`--no-ignore` if required), production
build and `git diff --check`.

No new baseline is authorised for these three failures.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-job-detail.ts`
- `src/components/admin/queue-monitor/use-queue-jobs.ts`
- `tests/unit/queue-monitor-job-detail-state.test.ts`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`
- accepted ADMIN-009 client/types and source-loader mechanics
- accepted ADMIN-011 jobs-harness assertions
- unchanged ADMIN-009 failed-detail/i18n harness files
- frozen QueueMonitor server/API/helper sources and dedicated server tests
- this task Completion Report and Attempt 2 update
- ARCH-025 parent architecture and ADMIN-013..015 downstream contracts

### Validation Reviewed

- Submitted focused detail-state/error/abort tests: 5/5 passed.
- Submitted two-file source-contract result: 16/19 with exactly the three stale inline
  detail assertions identified above.
- Nine frozen QueueMonitor SHA-256 values: exact.
- Attempt 2 implementation task branch: no QueueMonitor source/test change; GitHub
  shows only unrelated ADMIN-005 Merchant Pricing mainline synchronization.
- Attempt 1 unit/broad/build/lint evidence remains applicable to the reviewed
  implementation; Attempt 3 must re-run the harness/broad/build checks after changing
  test source.

### Architecture Conformance

Conformant in implementation. The unresolved failures are a source-test ownership
contradiction, not a runtime/API regression. The architect amends the harness freeze
narrowly: ADMIN-012 Attempt 3 may reconcile only the three identified detail
source-shape assertions. After ADMIN-012 acceptance, the resulting versions of
`admin-queue-monitor.test.mjs` and `admin-queue-details-drawer.test.mjs` become the
frozen jobs+detail harness baseline for ADMIN-013..015.

### Follow-up

Return this same task to Ready with Attempt 2 retained and claim clear. Reclaim through
`/moda-task ARCH-025-ADMIN-012`; the next claim must create Attempt 3 exactly once.

Attempt 3 is the authorised two-file harness reconciliation plus revalidation. Keep the
accepted detail-hook implementation unchanged unless validation exposes a genuine
runtime regression. Do not begin ADMIN-013 until ADMIN-012 is architect-accepted
Complete.

## Developer Override - Reopen (2026-10-03)

- Previous accepted attempt: none. Attempt 1 remains submitted for architect review and has not been accepted.
- Reopen reason: the developer explicitly requested reopening this task. The Attempt 1 Completion Report documents frozen QueueMonitor source-contract assertions that require the pre-extraction inline detail lifecycle and conflict with the required hook ownership; reopening allows the task's unresolved validation/contract gap to be addressed while preserving the submitted implementation and evidence.
- Reopen transition: `review` -> `ready`; `executor` and `claimed_at` are cleared; `attempt` remains `1`.
- This reopen is not a claim. The next `/moda-task` preparation may claim Attempt 2 after its normal synchronization and dependency gates pass.
