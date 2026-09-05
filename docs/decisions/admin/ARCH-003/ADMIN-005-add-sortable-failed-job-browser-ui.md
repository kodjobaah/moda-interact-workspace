---
id: ARCH-003-ADMIN-005
architecture_id: ARCH-003
title: Add sortable failed-job browser UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 50
executor: copilot
claimed_at: 2026-09-04T20:16:29Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-004
enables:
  - ARCH-003-ADMIN-006
created: 2026-09-04
updated: 2026-09-04
---

# Add sortable failed-job browser UI

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Build the read-only failed-job browser UI using the server list capability from
ADMIN-004. Do not implement selected-job full detail retrieval in this task.

## Context

The target design shows failed jobs for a selected queue in a side/split panel,
with sorting controls and selectable rows.

## Scope

- connect queue `View details` selection to the failed-job list capability;
- show the selected queue name and failed count/context;
- render the bounded failed-job list;
- provide sort field and direction controls;
- default the UI to `Failed at` descending;
- make one failed-job row selectable;
- preserve queue summary context while browsing failures;
- add loading, empty and unavailable states.

## Out of Scope

- loading/rendering full selected-job details;
- stack trace rendering;
- payload rendering;
- retry/delete/pause/resume actions.

## Requirements

Each row should show enough information to choose the relevant failure, for
example:

```text
Job ID
Job name
Failed at
Attempts
Reason
```

Long identifiers/reasons may be visually truncated while remaining accessible.

## Work Items

- [x] Add selected-queue UI state.
- [x] Add failed-job list fetch/use of ADMIN-004 interface.
- [x] Add sort field and direction controls.
- [x] Render failed-job rows.
- [x] Add selected-row state without requiring full job details yet.
- [x] Add focused browser/sorting/selection tests.

## Interfaces / Contracts

Consumes the failed-job summary API/model from `ARCH-003-ADMIN-004`.

Produces selected queue/job UI state consumed by `ARCH-003-ADMIN-006/007`.

## Dependencies

- `ARCH-003-ADMIN-004`

## Enables

- `ARCH-003-ADMIN-006`

## Acceptance Criteria

- [x] Selecting queue details reveals its failed-job browser.
- [x] Failed jobs are shown in a bounded list.
- [x] Sorting controls work using the approved fields.
- [x] Default sort is Failed at descending.
- [x] A failed row can be selected.
- [x] No full selected-job detail fetch is implemented yet.
- [x] The UI remains read-only.

## Validation

- [x] focused failed-job browser tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

Prefer the previously agreed right-side/split-panel interaction, but reuse the
existing Admin visual system rather than introducing a new design library.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`

### Work Completed
- Connected queue `View details` selection to the ADMIN-004 failed-job API.
- Added bounded failed-job rendering with queue context, job ID, name, failed
  time, attempts and truncated reason text.
- Added approved sort field and direction controls with `Failed at` descending
  as the default.
- Added selectable failed-job rows and explicit loading, empty and unavailable
  states.
- Kept the UI read-only and did not add selected-job detail retrieval,
  payload/stacktrace rendering or mutations.

### Validation Results
- `npm exec -- node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-failed-jobs.test.mjs` passed (15 tests).
- `npm test` passed (44 tests).
- `npm exec tsc -- --noEmit` passed.
- `npm run lint` passed with two existing-style exhaustive-deps warnings for
  the queue monitor's refresh function.
- `npm run build` passed and included `/api/admin/queues/failed`.
- `git diff --check` passed.

### Deviations
The task file was externally reverted to its pre-claim state during execution;
the claim metadata was restored before returning the task to review. The
production build retains existing warnings for Next.js multiple-lockfile
workspace-root inference and BullMQ's optional `@valkey/valkey-glide` module.

### Assumptions
The existing ADMIN-004 API response is the sole source for failed-job list
data; selected rows intentionally do not trigger a detail request.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation conforms to the bounded ADMIN-005 UI scope:

- queue `View details` selection drives the protected ADMIN-004 failed-job list API;
- the selected queue remains visible while browsing failures;
- failed jobs render in a bounded table with Job ID, Job name, Failed at,
  Attempts, and Reason;
- approved sorting controls are exposed for failed time, attempts, job name, and
  job ID;
- the default UI ordering is Failed at descending;
- individual failed-job rows can be selected;
- loading, empty, and unavailable states are present;
- long IDs/reasons are visually bounded while the complete value remains
  accessible through the existing title treatment;
- the UI remains read-only;
- no selected-job detail request, payload rendering, stacktrace rendering, or
  job mutation was introduced early.

The selected job ID state is sufficient input for ADMIN-006. ADMIN-006 remains
responsible only for the protected selected-job server detail capability.

### Reviewed Files

- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-005-add-sortable-failed-job-browser-ui.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused failed-job browser/API tests: 15 passed;
- full Admin tests: 44 passed;
- TypeScript: pass;
- lint: pass;
- production build: pass;
- `git diff --check`: pass.

The Completion Report notes two exhaustive-deps warnings and existing build
warnings; none are reported as task regressions or validation failures.

### Architecture Conformance

Accepted.

The implementation remains confined to `moda-interact-admin`, consumes only the
bounded ADMIN-004 list interface, remains read-only, and does not begin
ADMIN-006/007 detail work.

### Follow-up

`ARCH-003-ADMIN-006` is now Ready.

ADMIN-006 must implement only the protected selected failed-job server detail
reader/API and normalized detail model. It must not render the final detail UI.
