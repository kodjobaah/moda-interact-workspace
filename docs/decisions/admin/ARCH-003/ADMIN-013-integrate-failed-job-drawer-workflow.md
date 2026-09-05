---
id: ARCH-003-ADMIN-013
architecture_id: ARCH-003
title: Integrate paginated filtered queue-job diagnostics into drawer workflow
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 43
executor: copilot
claimed_at: 2026-09-05
attempt: 1
depends_on:
  - ARCH-003-ADMIN-012
enables: []
created: 2026-09-04
updated: 2026-09-05
---

# Integrate paginated filtered queue-job diagnostics into drawer workflow

## Objective

Preserve the existing diagnostic capabilities while presenting a generalized,
paginated queue-job workflow for the selected Shop / Status / Direction
filters.

## Visual reference

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

## Scope

- `View all jobs` exposes the **paginated** queue-job browser
  within the queue-details workflow;
- default full-list page size is 10 jobs;
- filters remain visible in the order Shop -> Status -> Direction;
- the selected Shop and Status are preserved while paging;
- every row visibly identifies its Shop, including `Orphan / No shop`;
- selecting a row exposes the ADMIN-016 generalized detail:
  lifecycle fields, failed reason, stacktrace, and formatted job data;
- preserve loading, empty, not-found, unavailable, and copy-only states;
- preserve bounded scroll regions;
- preserve the selected queue context;
- remove the old inline-below-table diagnostic presentation;
- perform final visual comparison against the approved reference.

## Requirements

- consume the ADMIN-012-amended generic four-state queue-job contracts;
- keep the legacy ADMIN-004/006 routes protected and unchanged during this
  migration unless a later cleanup is explicitly approved;
- do not expose a job whose current state differs from the requested Status;
- do not add retry/requeue/delete/pause/resume controls;
- the full queue-job list MUST be paginated rather than rendered as one long
  scroll-only collection;
- default page size is 10;
- expose clear `Previous` / `Page X of Y` / `Next` controls, or an equivalent
  compact accessible pagination treatment;
- changing queue, Shop, Status, or Direction resets the queue-job page to 1;
- Previous is disabled on the first page;
- Next is disabled on the final page;
- reuse ADMIN-015 bounded page/limit metadata;
- extend the list response with bounded pagination metadata only as needed
  (`total`, `totalPages`, `hasNext`, or equivalent);
- if the existing bounded scan cap is reached, pagination metadata must not
  falsely claim an exact uncapped total;
- stacktrace/job-data regions remain bounded and readable;
- drawer/subview navigation must make it obvious how to return from job detail
  to the queue failure list and queue summary;
- desktop composition must keep the queue table and drawer relationship from the
  approved reference;
- small screens may use an overlay/full-width drawer while preserving the same
  information hierarchy.

## Acceptance Criteria

- [ ] Shop / Status / Direction filters remain available in the full browser.
- [ ] Failed, Active, Waiting, and Delayed jobs are all browseable.
- [ ] Shop is visible on every row.
- [ ] Orphan / No shop rows are visible and filterable.
- [ ] Full queue-job list is paginated with a default 10 rows per page.
- [ ] Previous/current-page/Next navigation is present and correctly disabled.
- [ ] Queue/sort/direction changes reset pagination to page 1.
- [ ] Pagination metadata remains truthful under the bounded server scan.
- [ ] Selected Failed, Active, Waiting, and Delayed job detail remains available through the amended generic detail boundary.
- [ ] Both are integrated into the right-drawer workflow rather than duplicated inline.
- [ ] Queue context remains visible/understandable.
- [ ] Back/close affordances are clear.
- [ ] No security/read-only regression.
- [ ] Final screenshot-level comparison confirms the approved table + drawer composition.
- [ ] Full Admin tests, typecheck, lint, production build, and `git diff --check` pass.

## ADMIN-012 Amendment inheritance

ADMIN-013 inherits the complete four-state contract accepted in ADMIN-012:

```text
Failed
Active
Waiting
Delayed
```

The full paginated browser MUST preserve the currently selected:

```text
Shop -> Status -> Direction
```

while paging.

Status-aware time semantics remain:

```text
Failed  -> failed/finished time
Active  -> processed/start time
Waiting -> queued time
Delayed -> scheduled execution time
```

Do not regress the corrected generic copy back to fixed failure-only wording.

## Required live visual evidence

As part of the final ARCH-003 screenshot-level comparison, capture the real
drawer/browser showing:

```text
Queue  = pending-recovery-candidates
Status = Delayed
```

with at least one real delayed job visible when delayed jobs exist in the queue.

This closes the visual proof deferred from ADMIN-012.

## Completion Report

### Status

Ready for Review / architect-accepted Complete.

### Implementation Summary

Implemented the final in-drawer paginated queue-job browser while preserving the
selected queue context and the accepted four-state diagnostics contract.

Implemented behavior:

- `View all jobs` switches the drawer from the 5-row recent view to a 10-row
  paginated browser;
- Shop / Status / Direction remain visible in the full browser;
- Failed / Active / Waiting / Delayed remain supported;
- changing queue, Shop, Status, or Direction resets the page to 1;
- Previous / Page X of Y-or-more / Next navigation is present;
- pagination uses the bounded server metadata without inventing an uncapped
  exact total;
- selecting a job opens generalized read-only job detail inside the drawer;
- Back returns to the prior recent/all-jobs context;
- no queue mutation controls were introduced.

### Files Changed

- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- Admin queue diagnostics regression tests
- this task coordination report

### Validation Results

Implementing-agent evidence:

- full Admin suite: 73 tests passed;
- TypeScript: passed;
- production build: passed;
- `git diff --check`: passed;
- lint: passed with the two pre-existing hook warnings.

Live evidence:

- paginated browser rendered and navigated correctly;
- `pending-recovery-candidates` + `Delayed` rendered the truthful empty state
  because no delayed jobs existed at the time of capture.

### Deviations / Notes

The task file inside the submitted ZIP remained stale at `status: ready`,
`executor: null`, `attempt: 0`. The architect reconciled that coordination state
during acceptance because the reviewed runtime source, tests, and reported
validation demonstrate the completed Attempt 1 implementation.

The conditional live requirement was:

```text
show a real delayed job when delayed jobs exist
```

No delayed job existed at capture time, so an empty Delayed state is not a
failure.

The final end-to-end delayed candidate proof is carried by
`ARCH-003-SYSTEM-TEST-001` after the pending-recovery metadata task is complete.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation conforms to the final ARCH-003 Admin workflow:

```text
Queue details
    -> Recent jobs (5)
    -> View all jobs
    -> Paginated jobs (10/page)
    -> Selected job detail
    -> Back to browser
```

Accepted characteristics:

- all four BullMQ states remain browsable;
- Shop / Status / Direction context is preserved while paging;
- page resets occur on queue/filter changes;
- Previous/Next disable truthfully from API metadata;
- unknown bounded totals are not represented as exact totals;
- job detail remains state-safe and read-only;
- queue context remains visible;
- no retry/requeue/delete/pause/resume controls exist.

### Final visual evidence disposition

The Delayed empty-state screenshot is accepted for ADMIN-013 because the queue
contained no delayed jobs at capture time.

A real delayed pending-recovery row is still required before ARCH-003 itself can
close, but that proof belongs to `ARCH-003-SYSTEM-TEST-001`, after the
Background tenant-attribution correction creates/verifies the canonical
candidate shape.

### Result

`ARCH-003-ADMIN-013` is Complete.

`ARCH-003-BACKGROUND-001` is promoted to Ready.
