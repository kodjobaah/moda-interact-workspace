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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
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
```

## Out of Scope

Drawer/presentation extraction, accepted ADMIN-009 client/type changes, summary-hook changes, server/API changes.

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

## Work Items

- [x] Move detail state/request lifecycle to dedicated hook.
- [x] Rewire ADMIN-011 invalidation port to the hook without changing jobs semantics.
- [x] Add focused state/error/abort tests without adding a React test framework.

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

## Validation

- [x] Frozen source/test SHA-256 values match the task specification.
- [x] `git diff` for the frozen server/API sources, refresh helper, and dedicated server tests is empty.
- [x] The architect-accepted ADMIN-011 QueueMonitor security tests and accepted ADMIN-009 detail/i18n security tests are unchanged.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-job-detail-state.test.ts` passes (5/5).

- [ ] `npm run test:unit` passes without task-introduced regression. Result: 259 passed; the two failures match `ARCH025-ADMIN-BUILDER-TEST-001`.
- [ ] `npm test` passes without task-introduced regression. The two documented `ARCH025-ADMIN-TEST-001` failures remain; one QueueMonitor source-shape assertion also expects the pre-extraction inline detail lifecycle. The isolated accepted QueueMonitor source-contract files report 16/19 passing, with three stale inline-state/invalidation assertions.
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

### Work Completed

- Extracted selected job identity, normalized detail, loading/error state, request cancellation, and detail fetching into `useQueueJobDetail`.
- Preserved selection, clear/back, reason-specific invalidation, 404/unavailable error mapping, abort suppression, and active-controller loading completion.
- Connected the existing `useQueueJobs` invalidation callback to the detail hook without changing the jobs hook or its transition points.
- Added reducer/error/abort tests without introducing a React test framework.

### Validation Results

- Focused detail-state tests: 5 passed.
- Targeted ESLint and `git diff --check`: passed.
- Frozen QueueMonitor server/API/helper/test hashes: all matched; frozen-file diff: empty.
- `npm run build`: passed with existing BullMQ dependency warnings.
- `npm run test:unit`: 259 passed, 2 documented builder-baseline failures.
- `npm test`: documented global baseline failures plus a QueueMonitor source-shape assertion tied to the old inline lifecycle. Running the two accepted QueueMonitor source-contract files in isolation produced 16 passes and 3 failures in assertions that require inline detail setters/invalidation code.

### Deviations

- The frozen accepted QueueMonitor source-contract tests assert the pre-extraction source layout. They cannot be updated within the task's authorized file scope and conflict with the required dedicated detail-hook ownership. No test assertions were weakened or changed.

### Assumptions

- The source-shape assertions require Architect guidance on whether their frozen status remains appropriate after ADMIN-012's required structural move.

### Unresolved Issues

- Architect decision is needed on reconciling the unchanged ADMIN-011 source-contract tests with ADMIN-012's hook ownership requirement. Implementation is otherwise ready for review.

### Architectural Concerns

- No runtime/API contract changes were made. The remaining concern is test-contract alignment only.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None

## Developer Override - Reopen (2026-10-03)

- Previous accepted attempt: none. Attempt 1 remains submitted for architect review and has not been accepted.
- Reopen reason: the developer explicitly requested reopening this task. The Attempt 1 Completion Report documents frozen QueueMonitor source-contract assertions that require the pre-extraction inline detail lifecycle and conflict with the required hook ownership; reopening allows the task's unresolved validation/contract gap to be addressed while preserving the submitted implementation and evidence.
- Reopen transition: `review` -> `ready`; `executor` and `claimed_at` are cleared; `attempt` remains `1`.
- This reopen is not a claim. The next `/moda-task` preparation may claim Attempt 2 after its normal synchronization and dependency gates pass.
