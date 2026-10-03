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
attempt: 0
depends_on:
  - ARCH-025-ADMIN-011
enables:
  - ARCH-025-ADMIN-013
created: 2026-10-02
updated: 2026-10-02
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

- [ ] Move detail state/request lifecycle to dedicated hook.
- [ ] Rewire ADMIN-011 invalidation port to the hook without changing jobs semantics.
- [ ] Add focused state/error/abort tests without adding a React test framework.

## Interfaces / Contracts

ADMIN-012 closes the repository-internal jobs/detail coordination contract: jobs owns row/filter/page state; detail owns selection/detail state; jobs may only request detail invalidation through the accepted narrow interface.

## Dependencies

- `ARCH-025-ADMIN-011`

## Enables

- `ARCH-025-ADMIN-013`

## Acceptance Criteria

- [ ] No selected-job/detail request state remains duplicated in shell/jobs hook.
- [ ] Select/back/invalidation state transitions match current behaviour.
- [ ] 404, other non-OK and abort semantics remain exact.
- [ ] Jobs success/filter/queue/View-all invalidations remain at the same points as before extraction.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [ ] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [ ] The architect-accepted ADMIN-011 versions of `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs`, plus the accepted ADMIN-009 versions of `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs`, are unchanged.
- [ ] `node --experimental-strip-types --test tests/unit/queue-monitor-job-detail-state.test.ts` passes.

- [ ] `npm run test:unit` passes without task-introduced regression.
- [ ] `npm test` passes without task-introduced regression.
- [ ] targeted ESLint for every changed Admin source/test file passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
