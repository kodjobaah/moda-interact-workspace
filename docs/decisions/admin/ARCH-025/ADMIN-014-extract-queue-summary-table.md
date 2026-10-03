---
id: ARCH-025-ADMIN-014
architecture_id: ARCH-025
title: Extract QueueMonitor summary table
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
claimed_at: 2026-10-03T11:09:41Z
attempt: 1
depends_on:
  - ARCH-025-ADMIN-013
enables:
  - ARCH-025-ADMIN-015
created: 2026-10-02
updated: 2026-10-03
---

# Extract QueueMonitor summary table

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the read-only queue summary table into a focused presentation component consuming the accepted summary snapshot and queue-selection callback.

## Context

After ADMIN-009..013 establish all data/control boundaries, the top-level component still owns a substantial summary table. This task moves presentation only and must not alter queue labels, counts, activity formatting, selection styling or drawer-opening semantics.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/queue-summary-table.tsx
```

## Out of Scope

Hook/client/type changes; details drawer/jobs/detail extraction; API/server changes; visual redesign.

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

### R1 — presentation-only component

Create `QueueSummaryTable` with bounded props for the current `QueueMonitorSnapshot`, selected queue name and `onSelectQueue`. Keep all eight current columns/caption/counts/activity presentation and row-selection styling.

### R2 — catalogue/i18n ownership

Continue rendering `queue.jobNames.map(adminQueueJobLabel).join(", ")`; do not introduce a local job-name map. Continue using current translated labels/time formatting.

### R3 — read-only interaction

Queue-name buttons continue to invoke only the supplied queue-selection callback and carry the current accessible `queue.openDetails` label. No mutation/control behaviour is added.

## Work Items

- [x] Extract summary table markup into focused component.
- [x] Rewire shell using accepted snapshot/selection callback.
- [x] Keep accepted hooks/client/types untouched.

## Interfaces / Contracts

Presentation-only repository-internal React props. `QueueMonitor` remains the public export/caller boundary.

## Dependencies

- `ARCH-025-ADMIN-013`

## Enables

- `ARCH-025-ADMIN-015`

## Acceptance Criteria

- [x] Summary table content/labels/counts/activity/selection remain unchanged.
- [x] Queue opening still uses the same shell selection path and drawer behavior.
- [x] No data request/state logic is duplicated in the table component.
- [x] Accepted ADMIN-009..013 control modules remain unchanged.

## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [x] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [x] The architect-accepted ADMIN-012 versions of `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs`, plus the accepted ADMIN-009 versions of `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs`, are unchanged.
- [x] Run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-internationalization.test.mjs`; all QueueMonitor-owned assertions pass against the accepted ADMIN-012 jobs+detail harness baseline, with only exact `ARCH025-ADMIN-TEST-001` inherited global i18n failures.

- [x] `npm run test:unit` passes without task-introduced regression.
- [x] `npm test` passes without task-introduced regression.
- [x] targeted ESLint for every changed Admin source/test file passes.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

`src/components/admin/queue-monitor.tsx`; `src/components/admin/queue-monitor/queue-summary-table.tsx`.

### Work Completed

Extracted the read-only eight-column queue summary table into `QueueSummaryTable`, typed against the accepted `QueueMonitorSnapshot` and receiving only the selected queue and shell selection callback. Moved the shared queue timestamp formatter with the presentation module so the shell's remaining activity labels preserve the same locale formatting. The job label remains catalogue-owned through `adminQueueJobLabel`; queue opening continues through `selectQueue`. No data/control module changed. Implementation submitted on `task/ARCH-025-ADMIN-014` at `e5c5844884fb883d526fae74a96a2c8097b39371`. Prepared via the deterministic launcher as `moda_admin` / `copilot`, Attempt 1; dependency gate passed (`ARCH-025-ADMIN-013` Complete), both dedicated worktrees synchronized and recursive `database` submodule ready. Launcher claim commit: `5038290b4497986804d364753e20a72065cad67f`.

### Validation Results

Focused QueueMonitor tests: 14 passed, 0 failed. Required paired command `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-internationalization.test.mjs`: 19 passed, 2 failed; both are the documented inherited global i18n failures (`1.1.0` versus stale expected `1.0.1`, and missing required `billing.refund.*` catalogue keys). `npm run test:unit`: 263 passed, 2 failed; both exact failures match `ARCH025-ADMIN-TEST-001`. `npm test`: 226 passed, 9 failed; all nine identifiers match `ARCH025-ADMIN-TEST-001`, with no task-only failure. Targeted ESLint passed; Prettier check for the new component and `git diff --check` passed. All nine frozen SHA-256 values matched, frozen-file diff was empty, and accepted ADMIN-009..013 modules/tests were unchanged. `npm run build` passed TypeScript and production generation; existing BullMQ critical-dependency and optional `@valkey/valkey-glide` warnings remain.

### Deviations

None.

### Assumptions

The repository-wide full-test failures are accepted only as the documented `ARCH025-ADMIN-TEST-001` baseline; the QueueMonitor-owned tests passed and no task-specific failure remains.

### Unresolved Issues

None task-specific. The documented inherited Admin validation failures remain unchanged.

### Architectural Concerns

None.

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
