---
id: ARCH-025-ADMIN-013
architecture_id: ARCH-025
title: Extract QueueMonitor resizable drawer hook
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
  - ARCH-025-ADMIN-012
enables:
  - ARCH-025-ADMIN-014
created: 2026-10-02
updated: 2026-10-03
---

# Extract QueueMonitor resizable drawer hook

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract viewport measurement, drawer-width/maximise/close support, pointer resize and keyboard resize mechanics into a dedicated hook with pure geometry helpers.

## Context

Drawer mechanics are independent from queue data reads and are currently mixed into the 1,058-line component. Existing source-based drawer tests already encode first-open, switch, close, maximize and keyboard behaviours and will follow the extracted module through the ADMIN-009 loader.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-resizable-drawer.ts
tests/unit/queue-monitor-drawer.test.ts
```

## Out of Scope

Queue/detail presentation extraction; changes to accepted data hooks/client/types/security loaders; styling redesign.

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

### R1 — geometry ownership

Move `DESKTOP_BREAKPOINT = 768`, `SIDEBAR_WIDTH = 240`, `MIN_DRAWER_WIDTH = 448`, `RESIZE_STEP = 32`, `getWorkspaceWidth()` and `clampDrawerWidth()` into the drawer module. Preserve exact calculations.

### R2 — hook lifecycle

Own viewport width, drawer width and resizing state. Register/unregister viewport resize listener. While resizing and a queue is selected, pointer movement computes `window.innerWidth - event.clientX` and clamps to current workspace width; pointer-up stops resizing.

### R3 — accepted shell operations

Expose operations sufficient for first-open/switch, pointer start, keyboard resize, maximize and close. Preserve first-open maximized (`drawerWidth = null`), queue-switch width preservation, close setting width null/resizing false, and ArrowLeft wider / ArrowRight narrower / Home min / End max semantics. Closing the drawer must not own or clear jobs/detail data.

## Work Items

- [x] Move geometry constants/helpers and viewport/pointer state to the hook.
- [x] Rewire queue selection/close/maximize/resize controls without changing data state.
- [x] Add pure geometry/keyboard transition tests.

## Interfaces / Contracts

Drawer hook consumes only selected-queue presence and browser viewport/pointer events. It owns no queue/job/detail data and does not call API clients.

## Dependencies

- `ARCH-025-ADMIN-012`

## Enables

- `ARCH-025-ADMIN-014`

## Acceptance Criteria

- [x] Current full-workspace drawer sizing and keyboard/pointer semantics remain exact.
- [x] Queue switch retains open width; first open/maximize/close semantics remain exact.
- [x] Drawer close still does not clear queue jobs or selected detail state.
- [x] No data hook/client code moves into drawer hook.

## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [x] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [x] The architect-accepted ADMIN-012 versions of `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs`, plus the accepted ADMIN-009 versions of `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs`, are unchanged.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-drawer.test.ts` passes.

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

`src/components/admin/queue-monitor.tsx`; `src/components/admin/queue-monitor/use-resizable-drawer.ts`; `tests/unit/queue-monitor-drawer.test.ts`.

### Work Completed

Extracted drawer geometry, viewport measurement, pointer listener lifecycle and keyboard resizing into `useResizableDrawer` plus pure helpers. QueueMonitor still owns selected-queue and presentation markup; first open remains maximized, switching queues retains width, close resets only selection/width/resizing, and maximize resets width to `null`. Queue/jobs/detail hooks and API behavior were not changed. Implementation commit: `1b2cdca9f313ae6f139e1bfb25b443a578779f72` (`refactor(admin): extract resizable queue drawer hook`).

### Validation Results

Focused drawer/unit/source tests: 23 passed, 0 failed. Targeted ESLint passed; the repository ignores `tests/unit` by default, and the new unit file also passed with `--no-ignore`. Prettier check passed for the two new files; `git diff --check` passed. All nine frozen SHA-256 values matched, the frozen-file diff was empty, and accepted ADMIN-009/012 tests were unchanged. `npm run test:unit`: 263 passed, 2 failed; both failures (`rejects stale metadata, locale/header changes, and highlight identity changes`, `returns all bounded validation issues in canonical order`) match `ARCH025-ADMIN-TEST-001`. `npm test`: 226 passed, 9 failed; all nine identifiers exactly match that documented baseline. `npm run build` succeeded with existing BullMQ optional-dependency/critical-dependency warnings.

### Deviations

None.

### Assumptions

The repository-wide full-test failures are accepted only as the documented `ARCH025-ADMIN-TEST-001` baseline; no task-specific test failed.

### Unresolved Issues

None task-specific. The inherited Admin baseline failures remain documented in `docs/development-baseline.md`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

ADMIN-013 is accepted Complete.

Architect inspection of implementation
`1b2cdca9f313ae6f139e1bfb25b443a578779f72` found exactly the three
task-authorised files changed:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-resizable-drawer.ts
tests/unit/queue-monitor-drawer.test.ts
```

The extraction preserves the established drawer mechanics while moving geometry,
viewport measurement, pointer listener lifecycle and keyboard resizing into the
dedicated hook.

The pure geometry contract remains exact:

```text
DESKTOP_BREAKPOINT = 768
SIDEBAR_WIDTH = 240
MIN_DRAWER_WIDTH = 448
RESIZE_STEP = 32
```

`getWorkspaceWidth()` retains the desktop-sidebar subtraction rule.
`clampDrawerWidth()` preserves the current minimum/maximum calculation.
Pointer resizing still computes `window.innerWidth - event.clientX` before clamping to
the current workspace width.

Keyboard semantics remain unchanged:

```text
ArrowLeft  -> wider by 32
ArrowRight -> narrower by 32
Home       -> minimum width
End        -> maximum workspace width
other key  -> no drawer update
```

The hook owns `drawerWidth`, `viewportWidth` and `isResizing`, installs/removes the
viewport resize listener, and owns the pointermove/pointerup listener lifecycle while
resizing. It contains no queue/jobs/detail data and calls no QueueMonitor HTTP client.

The remaining shell coordination is conformant with the task boundary. Selected queue
identity remains intentionally shell-owned. The shell uses the hook-owned width/
resizing setters only at the two coordination points where selected-queue state and
drawer state must change together:

- first open resets hook width to `null` before selecting the queue, so it starts
  maximized;
- close clears shell-owned `selectedQueueName` and resets only hook-owned width/
  resizing state.

Queue switching while already open therefore does not reset width. Close still does
not clear jobs/detail state. Maximize, pointer start and keyboard resizing delegate to
the hook's bounded operations.

This keeps the architect-accepted ADMIN-012 source-contract harness unchanged rather
than introducing a source-test migration solely to rename those two shell coordination
calls. No resize geometry/listener implementation remains in `QueueMonitor`.

Independent checks against the uploaded snapshot confirm:

```text
frozen QueueMonitor server/API/helper/test hashes
  9 / 9 exact

accepted ADMIN-012 drawer source-contract tests
  5 / 5 passed
```

The uploaded archive does not contain `node_modules`, so the architect sandbox cannot
independently execute `queue-monitor-drawer.test.ts` because its hook module imports
React. That environment limitation does not contradict the submitted complete
worktree result. The submitted focused drawer/unit/source validation is 23/23.

The submitted repository-wide results are baseline-conformant:

```text
npm run test:unit
  265 total
  263 passed
  2 failed
```

The two failures are the existing translation-workbook baseline failures.

```text
npm test
  235 total
  226 passed
  9 failed
```

All nine failures are the exact documented `ARCH025-ADMIN-TEST-001` identifiers. No
drawer-owned assertion fails.

Production build, targeted lint, frozen-file diff and `git diff --check` pass as
recorded. Existing BullMQ / optional Valkey build warnings are unchanged.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-013
  1b2cdca9f313ae6f139e1bfb25b443a578779f72

workspace task/ARCH-025-ADMIN-013
  9bdd55ccf31bc4d9eed2c8509d2f4b89daa2a2aa
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect reconciliation
clears those lifecycle fields directly; no additional attempt is required.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-resizable-drawer.ts`
- `tests/unit/queue-monitor-drawer.test.ts`
- architect-accepted ADMIN-012 QueueMonitor source-contract harness
- frozen QueueMonitor server/API/helper sources and dedicated server tests
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-014 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `1b2cdca9f313ae6f139e1bfb25b443a578779f72`: exactly three authorised files.
- Nine frozen QueueMonitor SHA-256 values independently reproduced: all exact.
- Independently rerun accepted drawer source-contract file: 5/5 passed.
- Submitted focused drawer/unit/source validation: 23/23 passed.
- Submitted unit suite: 263 passed / 2 exact inherited translation failures.
- Submitted broad suite: 226/235 with exactly the nine
  `ARCH025-ADMIN-TEST-001` failures.
- Submitted targeted lint, production build and `git diff --check`: passed.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-013 establishes the accepted drawer control boundary: geometry,
viewport state, resize state, viewport/pointer listener lifecycle, pointer calculation,
keyboard resizing and maximize behavior live in `useResizableDrawer`; the shell retains
only selected-queue coordination and presentation.

The accepted ADMIN-013 hook becomes a frozen control module for ADMIN-014/015. Those
later presentation tasks must not reopen drawer geometry or resize lifecycle mechanics.

### Follow-up

`ARCH-025-ADMIN-013` is Complete / Accepted at Attempt 1. Its sole dependant,
`ARCH-025-ADMIN-014`, has all declared dependencies satisfied and is promoted to
Ready, Attempt 0, claim clear. Do not start ADMIN-015 implicitly.
