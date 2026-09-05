---
id: ARCH-003-ADMIN-007
architecture_id: ARCH-003
title: Add failed-job detail panel UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 70
executor: copilot
claimed_at: 2026-09-04T20:32:55Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-006
enables: []
created: 2026-09-04
updated: 2026-09-04
---

# Add failed-job detail panel UI

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Render the selected failed job's normalized diagnostic details in the agreed
read-only Admin side/split-panel experience.

## Context

ADMIN-006 provides a stable server detail model. This final task owns only the
presentation and interaction of that model.

## Scope

- when a failed-job row is selected, load its normalized detail model;
- render the job identity and lifecycle fields;
- render failed reason prominently;
- render stacktrace in a readable scrollable/collapsible section;
- render job payload/data as formatted JSON or equivalent structured view;
- provide safe copy affordances for useful identifiers/diagnostic blocks where
  straightforward;
- provide loading, missing-job and unavailable states;
- keep the selected queue and failed-job list context visible where practical.

## Out of Scope

- job retry/delete/pause/resume;
- editing payloads;
- bulk export;
- database changes.

## Requirements

The detail view must show, when available:

```text
Job ID
Queue
Job name
State
Attempts made
Created/timestamp
Processed at
Failed/finished at
Failed reason
Stack trace
Payload/job data
```

The UI must not expose Redis URLs, environment variables or unrelated service
secrets.

## Work Items

- [x] Connect selected failed-row state to the ADMIN-006 detail interface.
- [x] Build the detail panel/split region.
- [x] Render lifecycle fields and failed reason.
- [x] Render stacktrace.
- [x] Render formatted job data/payload.
- [x] Add safe loading/not-found/unavailable states.
- [x] Add focused detail-panel tests.

## Interfaces / Contracts

Consumes the normalized selected-job detail model from `ARCH-003-ADMIN-006`.

## Dependencies

- `ARCH-003-ADMIN-006`

## Enables

None.

## Acceptance Criteria

- [x] Selecting a failed job renders its diagnostic details.
- [x] Lifecycle fields, failed reason, stacktrace and payload/data are visible.
- [x] Large diagnostic fields remain readable without destroying the page layout.
- [x] Missing/disappeared job state is handled safely.
- [x] Queue context remains understandable.
- [x] No mutation controls are introduced.
- [x] Redis/environment secrets are not exposed.

## Validation

- [x] focused failed-job detail panel tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

Use existing Admin design tokens/components. Do not introduce a new UI framework
solely for the detail panel.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `moda-interact-admin/tests/security/admin-failed-job-detail-panel.test.mjs`

### Work Completed
- Connected selected failed-job rows to the protected ADMIN-006 detail endpoint
  with abortable loading and stale-selection cleanup.
- Added a read-only detail panel showing queue, identity, lifecycle timestamps,
  attempts, failed reason, stack trace and formatted job payload data.
- Added bounded scrollable regions for large diagnostics and safe copy controls
  for the job ID, failure reason, stack trace and payload.
- Added loading, disappeared-job/not-found and unavailable states while keeping
  the failed-job browser and queue context visible.
- Preserved the read-only boundary with no retry, delete, pause, resume or
  payload-editing controls.

### Validation Results
- Focused queue-monitor/detail-panel tests: 14 passed.
- `npm test`: 51 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two existing exhaustive-deps warnings in
  `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed and included `/observability/queues` and the protected
  detail endpoint.
- `git diff --check`: passed.

### Deviations
The existing ADMIN-005 source assertion that prohibited detail loading was
updated because ADMIN-007 is the authorized follow-up that owns this UI.

### Assumptions
The ADMIN-006 normalized payload is JSON-safe for display and copy, and the
protected endpoint remains the sole source of selected-job detail data.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation completes the ARCH-003 failed-job diagnostic
workflow while preserving the read-only and protected boundaries:

- selecting a failed-job row loads the protected ADMIN-006 detail endpoint;
- selected queue and failed-job-list context remain visible;
- job identity and lifecycle fields are shown;
- failure reason is prominent;
- stacktrace and job payload/data are rendered in bounded scrollable regions;
- copy controls are provided for useful diagnostic values without mutating job
  state;
- loading, disappeared/not-found, and unavailable states are handled safely;
- no retry, requeue, delete, pause, resume, payload edit, or other mutation
  controls are present;
- the component does not read Redis URLs, environment variables, authorization
  values, or service credentials directly.

This is the final ARCH-003 implementation task.

### Reviewed Files

- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `moda-interact-admin/tests/security/admin-failed-job-detail-panel.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-007-add-failed-job-detail-panel-ui.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused queue-monitor/detail-panel tests: 14 passed;
- full Admin tests: 51 passed;
- TypeScript: pass;
- lint: pass, with the two existing exhaustive-deps warnings;
- production build: pass;
- `git diff --check`: pass.

The focused detail-panel tests verify the protected detail endpoint wiring,
required diagnostic labels, bounded diagnostic regions, copy controls, the
read-only boundary, and absence of direct configuration-value access.

The supplied review archive does not include installed `node_modules`, so the
architect inspected the current source/tests and recorded validation rather than
reinstalling dependencies solely to rerun the repository suite.

### Architecture Conformance

Accepted.

The implementation is confined to `moda-interact-admin`, consumes the
architect-approved ADMIN-006 normalized detail interface, and completes the
read-only queue-observability workflow defined by ARCH-003.

### Follow-up

None for ARCH-003.

The parent architecture is architect-accepted Complete.
