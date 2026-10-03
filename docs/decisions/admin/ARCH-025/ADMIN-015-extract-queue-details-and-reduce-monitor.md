---
id: ARCH-025-ADMIN-015
architecture_id: ARCH-025
title: Extract QueueMonitor details presentation and reduce final shell
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-03T11:46:38Z
attempt: 1
depends_on:
  - ARCH-025-ADMIN-014
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Extract QueueMonitor details presentation and reduce final shell

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the selected-queue drawer, jobs table/filter/pagination presentation and selected-job detail presentation, leaving `queue-monitor.tsx` as the thin public shell coordinating accepted hooks and views.

## Context

The preceding tasks establish stable browser client, summary/jobs/detail hooks, drawer mechanics and summary table. The final task moves the remaining substantial presentation without changing any accepted control interface or network behaviour.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/queue-detail-drawer.tsx
src/components/admin/queue-monitor/queue-jobs-table.tsx
src/components/admin/queue-monitor/queue-job-detail.tsx
```

## Out of Scope

Changes to accepted ADMIN-009..014 client/types/hooks/table contracts; server/API changes; product redesign; mutation controls.

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

### R1 — final shell

`queue-monitor.tsx` remains the public `QueueMonitor` export and should primarily wire summary/jobs/detail/drawer hooks, selected queue identity, refresh controls, summary status/error text, `QueueSummaryTable` and `QueueDetailDrawer`. It must not reimplement fetch, polling, jobs/detail state or resize mechanics.

### R2 — detail drawer composition

Extract the current fixed full-workspace aside, resize separator/header/maximize/close controls, selected queue counts/information, filters, job loading/error/empty states, recent/full controls, pagination and selected detail composition. Closing still clears only selected queue and drawer state; queue switch continues through the shell's accepted selection path.

### R3 — jobs table

Extract the current six-column jobs table, status-dependent time/reason labels, attribution fallback, row selection, recent/full pagination/View all controls and bounded filters. Presentation calls only accepted ADMIN-011/012 operations; it does not mutate hook internals.

### R4 — job detail

Extract Back, metadata, failed reason, stacktrace, normalized payload and copy controls. Preserve `navigator.clipboard.writeText`, 1.5-second copied indicator, bounded overflow classes, status-conditional failed reason and exact read-only/no-configuration restrictions.

### R5 — accepted-interface stop rule

If the final presentation needs a control/state capability not established by ADMIN-009..014, STOP and return the gap to `moda_architect`; do not expand accepted earlier interfaces or reintroduce state into the shell opportunistically.

## Work Items

- [ ] Extract drawer/jobs/detail presentation modules.
- [ ] Reduce public shell to hook/view composition and selected-queue coordination.
- [ ] Preserve all accepted source/security/i18n assertions through the ADMIN-009 loader.
- [ ] Prove accepted control modules are unchanged.

## Interfaces / Contracts

Final internal presentation props consume only accepted hook/view-model state/actions. Public contract remains `QueueMonitor`; protected API/server contracts remain unchanged.

## Dependencies

- `ARCH-025-ADMIN-014`

## Enables

None

## Acceptance Criteria

- [ ] `queue-monitor.tsx` is a thin public shell and contains no full jobs/detail/poll/resize implementation.
- [ ] Drawer, jobs table/pagination/filtering and job detail remain behaviourally/read-only compatible.
- [ ] All architect-accepted QueueMonitor source/security/i18n assertions (ADMIN-012 jobs+detail harness baseline plus unchanged ADMIN-009 remaining harness) pass without modification.
- [ ] No accepted ADMIN-009..014 control module is reopened to finish presentation extraction.
- [ ] No API/server source or dedicated server test changes.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [ ] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [ ] The architect-accepted ADMIN-012 versions of `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs`, plus the accepted ADMIN-009 versions of `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs`, are unchanged.
- [ ] Run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` using the accepted ADMIN-009 loader mechanics and ADMIN-012 jobs+detail harness assertions; QueueMonitor-owned assertions pass, with only exact `ARCH025-ADMIN-TEST-001` inherited global i18n failures permitted when unchanged.

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
