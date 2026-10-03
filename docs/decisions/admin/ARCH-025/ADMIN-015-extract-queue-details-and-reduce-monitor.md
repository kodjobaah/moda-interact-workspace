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
status: complete
priority: 20
executor: null
claimed_at: null
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

- [x] Extract drawer/jobs/detail presentation modules.
- [x] Reduce public shell to hook/view composition and selected-queue coordination.
- [x] Preserve all accepted source/security/i18n assertions through the ADMIN-009 loader.
- [x] Prove accepted control modules are unchanged.

## Interfaces / Contracts

Final internal presentation props consume only accepted hook/view-model state/actions. Public contract remains `QueueMonitor`; protected API/server contracts remain unchanged.

## Dependencies

- `ARCH-025-ADMIN-014`

## Enables

None

## Acceptance Criteria

- [x] `queue-monitor.tsx` is a thin public shell and contains no full jobs/detail/poll/resize implementation.
- [x] Drawer, jobs table/pagination/filtering and job detail remain behaviourally/read-only compatible.
- [x] All architect-accepted QueueMonitor source/security/i18n assertions (ADMIN-012 jobs+detail harness baseline plus unchanged ADMIN-009 remaining harness) pass without modification; only the exact inherited global i18n baseline failures remain.
- [x] No accepted ADMIN-009..014 control module is reopened to finish presentation extraction.
- [x] No API/server source or dedicated server test changes.

## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [x] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [x] The architect-accepted ADMIN-012 versions of `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs`, plus the accepted ADMIN-009 versions of `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs`, are unchanged.
- [x] Run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` using the accepted ADMIN-009 loader mechanics and ADMIN-012 jobs+detail harness assertions; 27 passed, 2 exact inherited global i18n baseline failures. All QueueMonitor-owned assertions pass.

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

`src/components/admin/queue-monitor.tsx`; `src/components/admin/queue-monitor/queue-detail-drawer.tsx`; `src/components/admin/queue-monitor/queue-jobs-table.tsx`; `src/components/admin/queue-monitor/queue-job-detail.tsx`.

### Work Completed

Extracted drawer shell/resizing controls and queue information into `QueueDetailDrawer`, queue filters/table/pagination into `QueueJobsTable`, and selected job metadata/failed reason/stacktrace/payload/copy controls into `QueueJobDetail`. `queue-monitor.tsx` now retains the public `QueueMonitor` boundary, summary refresh controls/status, selected queue coordination and accepted summary/jobs/detail/drawer hook composition (154 lines after formatting versus 656 before). All presentation components receive the accepted hooks' current snapshots/state/actions; no state, request lifecycle, endpoint, response type or control hook was moved or modified. Read-only and catalogue-owned presentation semantics remain intact. Implementation submitted on `task/ARCH-025-ADMIN-015` at `774908cf3c616882302d8f9481fbac39d5fa4299`.

### Validation Results

Focused QueueMonitor-owned source/security validation: 22 passed, 0 failed. Required paired QueueMonitor/i18n command: 27 passed, 2 failed, both exact inherited global i18n baseline failures (Shared package `1.1.0` versus stale expected `1.0.1`; required `billing.refund.*` keys absent). `npm run test:unit`: 263 passed, 2 failed; both match documented `ARCH025-ADMIN-TEST-001`. `npm test`: 226 passed, 9 failed; all nine identifiers match the same documented baseline and none is QueueMonitor-specific. Targeted ESLint, Prettier check and `git diff --check` passed. All nine frozen SHA-256 values matched; frozen-file diff was empty and accepted ADMIN-009..014 hooks/client/types/table and security tests were unchanged. `npm run build` passed TypeScript and production generation; existing BullMQ critical-dependency and optional `@valkey/valkey-glide` warnings remain.

### Deviations

None.

### Assumptions

The exact global i18n failures and the two unit/nine full-suite failures are inherited `ARCH025-ADMIN-TEST-001` baseline results; QueueMonitor-owned assertions pass and the extraction introduces no new failure.

### Unresolved Issues

None task-specific. The documented inherited Admin catalogue/test baseline remains unchanged.

### Architectural Concerns

None task-specific.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

ADMIN-015 is accepted Complete and closes the ADMIN-009..015 QueueMonitor
maintainability tranche.

Architect inspection of implementation
`774908cf3c616882302d8f9481fbac39d5fa4299` found exactly the four
task-authorised presentation files changed:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/queue-detail-drawer.tsx
src/components/admin/queue-monitor/queue-jobs-table.tsx
src/components/admin/queue-monitor/queue-job-detail.tsx
```

No accepted ADMIN-009..014 client/type/hook/table/control module, server/API source,
dedicated server test or accepted QueueMonitor source/security/i18n harness changed.

The public `QueueMonitor` shell is now the intended thin composition boundary. It
retains:

```text
public QueueMonitor export
selected queue identity
summary refresh controls/status
accepted summary/jobs/detail/drawer hook composition
QueueSummaryTable
QueueDetailDrawer
```

It no longer contains the full drawer/jobs/detail presentation or any summary/jobs/
detail fetch lifecycle or resize implementation.

`QueueDetailDrawer` consumes only the accepted snapshot, selected queue identity,
accepted jobs/detail/drawer hook return values and shell selected-queue setter. It
preserves:

- full-workspace fixed drawer markup and current width style;
- accepted separator pointer/keyboard resize operations;
- maximize through the accepted ADMIN-013 drawer operation;
- close semantics that clear only selected queue plus drawer width/resizing state,
  without clearing stored jobs/detail state;
- queue counts, worker indicator, queue/job labels and last-activity/snapshot
  formatting through accepted catalogue/i18n helpers;
- composition of `QueueJobsTable` and `QueueJobDetail`.

`QueueJobsTable` remains presentation-only over accepted ADMIN-011/012 operations. It
preserves:

- recent/full mode and bounded Shop/Status/Direction filters;
- refresh, previous/next and View-all operations through the accepted jobs hook;
- loading/error/empty-state ordering;
- the existing six-column jobs table;
- status-dependent event-time and reason/status headings;
- selected-row styling and row selection through `selectJob(job.id)`;
- known/unresolved/orphan attribution fallbacks;
- status labels through `adminStatusLabel`;
- locale time formatting through the accepted queue time helper;
- full-mode pagination and current known-total/page-of-more text.

The jobs browser remains hidden while a selected detail is open, exactly as in the
pre-extraction shell.

`QueueJobDetail` preserves the bounded read-only diagnostic contract:

- Back delegates only to the accepted `clearSelection` operation;
- metadata remains queue, job name, status, shop attribution, attempts and normalized
  lifecycle timestamps;
- failed reason remains rendered only for failed jobs;
- stacktrace and normalized payload remain bounded by the existing `max-h-72
  overflow-auto` presentation;
- payload formatting remains bounded `JSON.stringify(..., null, 2)` with the existing
  translated fallback;
- Copy continues to use `navigator.clipboard.writeText`;
- copied state still resets after 1.5 seconds;
- Copy failures remain silent apart from clearing the copied indicator;
- no retry, requeue, delete, pause, resume or other mutation controls exist;
- no Redis credentials, environment/configuration values or additional raw queue
  internals are exposed.

Independent checks against the exact uploaded snapshot confirm all nine frozen
QueueMonitor server/API/helper/test SHA-256 values exactly.

Static review of the extracted modules also confirms the required Copy/timer/bounded
overflow and failed-only diagnostic shapes and finds no mutation/configuration control
surface.

The uploaded archive does not contain the installed TypeScript/React/Shared runtime
needed to authoritatively replay every source-security test that dynamically imports
runtime `.ts` modules. Source-only assertions execute from the archive, while dynamic
imports fail only because of that archive environment. This does not contradict the
submitted complete-worktree validation:

```text
QueueMonitor-owned security/source assertions
  22 / 22 passed

required four-file QueueMonitor/i18n run
  29 total
  27 passed
  2 failed
```

The two remaining failures are the exact inherited global i18n/catalogue baseline
failures; every QueueMonitor-owned assertion passes.

The repository-wide results are likewise baseline-conformant:

```text
npm run test:unit
  265 total
  263 passed
  2 failed
```

The two unit failures are the existing inherited translation-workbook baseline
failures.

```text
npm test
  235 total
  226 passed
  9 failed
```

All nine failures are the exact documented `ARCH025-ADMIN-TEST-001` identifiers and
none is QueueMonitor-specific.

Targeted ESLint, Prettier, production build, frozen-file diff and
`git diff --check` pass as recorded. Existing BullMQ critical-dependency / optional
Valkey warnings remain unchanged.

GitHub independently confirms the final pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-015
  774908cf3c616882302d8f9481fbac39d5fa4299

workspace task/ARCH-025-ADMIN-015
  b0b93404d80c42d9234ba32a9960fe3764d6fb32
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect completion
reconciliation clears those lifecycle fields directly; no additional attempt is
required.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/queue-detail-drawer.tsx`
- `src/components/admin/queue-monitor/queue-jobs-table.tsx`
- `src/components/admin/queue-monitor/queue-job-detail.tsx`
- accepted ADMIN-009..014 client/types/hooks/table/control boundaries
- accepted ADMIN-012 jobs+detail source-contract harness
- accepted ADMIN-009 failed-detail/i18n harness
- frozen QueueMonitor server/API/helper sources and dedicated server tests
- this task Completion Report
- ARCH-025 parent architecture and Admin task index

### Validation Reviewed

- GitHub implementation commit
  `774908cf3c616882302d8f9481fbac39d5fa4299`: exactly four authorised
  presentation files.
- Nine frozen QueueMonitor SHA-256 values independently reproduced: all exact.
- Independent static read-only/diagnostic inspection: Copy/timer/bounded payload/
  stacktrace and failed-only reason contracts preserved; no mutation/configuration
  controls introduced.
- Submitted QueueMonitor-owned source/security validation: 22/22 passed.
- Submitted four-file QueueMonitor/i18n validation: 27/29 with only the two exact
  inherited global catalogue/i18n failures.
- Submitted unit suite: 263/265 with only the two inherited translation-workbook
  failures.
- Submitted broad suite: 226/235 with exactly the nine
  `ARCH025-ADMIN-TEST-001` failures.
- Submitted targeted lint, Prettier, production build and `git diff --check`: passed.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-015 completes the QueueMonitor decomposition without reopening any
accepted control/network boundary. The public shell is now a thin orchestration
component over accepted summary/jobs/detail/drawer controls and presentation modules.

The complete ADMIN-009..015 QueueMonitor tranche is now architect-accepted. Together
with the already-complete ADMIN-001..008 Merchant Pricing tranche, ARCH-025 has no
remaining Admin implementation frontier.

### Follow-up

`ARCH-025-ADMIN-015` is Complete / Accepted at Attempt 1. It has no declared
dependants. The ADMIN-009..015 QueueMonitor chain is closed.

Both ARCH-025 Admin maintainability tranches are now fully architect-accepted. Do not
start adjacent ARCH-025 work implicitly; continue only from another independently
Ready non-Admin frontier when explicitly launched.
