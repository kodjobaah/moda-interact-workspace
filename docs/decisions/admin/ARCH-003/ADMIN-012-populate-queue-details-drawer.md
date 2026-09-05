---
id: ARCH-003-ADMIN-012
architecture_id: ARCH-003
title: Populate queue details drawer with metrics and filtered recent jobs
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 42
executor: copilot
claimed_at: 2026-09-04T23:22:47Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-016
enables:
  - ARCH-003-ADMIN-013
created: 2026-09-04
updated: 2026-09-05
---

# Populate queue details drawer with metrics and filtered recent jobs

## Objective

Populate the approved Queue details drawer with the selected queue's operational
summary and a concise recent-job section driven by the new Shop / Status /
Direction model.

## Visual reference

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

## Scope

Render in the drawer:

- queue name;
- queue job labels/description;
- worker-online indicator;
- current waiting/active/delayed/failed/workers metrics;
- last snapshot/update time;
- queue information:
  - queue name
  - description
  - last Redis activity
  - worker count
  - safe BullMQ Redis key prefix where derived without exposing Redis URL;
- a filter bar in this exact left-to-right order:
  - Shop
  - Status
  - Direction;
- Shop default: `All shops`;
- Status default: `Failed`;
- Direction default: `Descending`;
- at most 5 recent jobs matching the current filters;
- job-list refresh;
- a `View all jobs` affordance.

## Filter interaction

The queue summary filter row must read:

```text
Shop | Status | Direction | Refresh jobs
```

Shop options:

```text
All shops
<discovered normalized shop values>
Orphan / No shop
```

Status options for this architecture revision:

```text
Failed
Active
Waiting
Delayed
```

Direction:

```text
Descending
Ascending
```

Changing Shop or Status resets selected job detail and any later pagination
state.

The summary list must show a visible `Shop` column. Rows whose projected shop is
null display an explicit treatment such as:

```text
Orphan / No shop
```

Do not render a blank shop cell.

The table's time/reason presentation is status-aware:

```text
Failed -> Failed at + failure reason
Active -> Started/processed at + no failure reason requirement
```

## Requirements

- reuse ADMIN-003/004 data contracts;
- the queue-summary drawer must show **at most 5** recent matching jobs;
- the summary must not render the entire job collection merely because the
  queue currently has a small number of jobs;
- `View all jobs` transitions to the full paginated browser owned by ADMIN-013;
- do not expose payload or stacktrace in the recent-job summary;
- do not expose Redis URLs, credentials, environment values, or provider secrets;
- failed counts should receive appropriate visual emphasis without turning the
  drawer into an alerting system;
- no job mutation controls.

## Acceptance Criteria

- [x] Drawer visibly matches the reference information hierarchy.
- [x] Current metric cards are shown.
- [x] Queue information section is shown.
- [x] Filter controls appear in Shop -> Status -> Direction order.
- [x] Default filters are All shops -> Failed -> Descending.
- [x] Summary is bounded to at most 5 matching jobs.
- [x] A Shop column is visible.
- [x] Orphan / No shop is explicit and filterable.
- [x] Active jobs can be shown without failure-specific labeling.
- [x] `View all jobs` is present.
- [x] Waiting and delayed jobs are supported end to end.
- [x] Delayed jobs sort by scheduled execution time.
- [x] No sensitive infrastructure configuration is exposed.
- [x] Full validation passes.

## Completion Report

### Status
Ready for Review.

### Files Changed

- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `moda-interact-admin/tests/security/admin-queue-details-drawer.test.mjs`
- `moda-interact-admin/tests/security/admin-failed-job-detail-panel.test.mjs`
- `moda-interact-admin/tests/security/admin-queue-jobs.test.mjs`
- `moda-interact-admin/tests/security/admin-queue-job-detail.test.mjs`

### Work Completed

Populated the approved queue details drawer with queue metrics, worker status,
queue information, snapshot/activity timestamps, and the bounded generic queue
job reader. The drawer now defaults to All shops, Failed, and Descending; exposes
Shop, Status, Direction, and Refresh jobs in the required order; supports
normalized shop facets and explicit orphan rows; renders active rows without
failure-specific reasons; resets selection when Shop or Status changes; and
routes selected jobs through the generic active/failed detail API. The recent
summary requests at most five jobs and retains read-only diagnostics plus the
View all jobs affordance.

### Amendment 001 Incorporated

Extended the same ADMIN-012 attempt to support `failed`, `active`, `waiting`,
and `delayed` states through the existing list and detail APIs. Delayed jobs
use `timestamp + max(delay, 0)` for `eventAt`, waiting jobs use their queued
timestamp, and facets scan the other supported states without discarding
orphaned delayed pending-recovery candidates. The drawer exposes all four
statuses, uses queued/scheduled time labels, and keeps generic `Recent jobs` /
`View all jobs` copy synchronized with the selected status.

### Validation Results

- Focused drawer/monitor tests: 17 passed.
- Focused amendment queue tests: 31 passed.
- Full Admin test suite: passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two pre-existing `react-hooks/exhaustive-deps`
  warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed with existing workspace-root inference and optional
  BullMQ `@valkey/valkey-glide` warnings.
- `git diff --check`: passed.
- Live acceptance: `pending-recovery-candidates` returned delayed jobs through
  `/api/admin/queues/jobs` with `status=delayed`, scheduled `eventAt`, and
  `hasOrphans: true`; a real delayed job also returned `status=delayed` through
  `/api/admin/queues/jobs/detail`.

### Deviations

The attached resolver cannot uniquely select ADMIN-012 while its amendment is
present because the resolver treats both filenames as task files. Amendment 001
has no frontmatter and explicitly remains part of this same attempt; no new
claim or attempt was created.

### Assumptions

- The existing ADMIN-013 route boundary remains `/observability/queues` with
  queue/status query parameters until that task provides the full paginated
  browser workflow.
- The safe BullMQ key prefix is not displayed because the existing snapshot
  contract does not expose one; no Redis URL or infrastructure configuration is
  derived in the browser.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status
Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The implementation and Amendment 001 are accepted on the available evidence.

Accepted behavior includes:

```text
Shop | Status | Direction | Refresh jobs
```

with:

```text
Status = Failed | Active | Waiting | Delayed
```

and a bounded recent-job list of at most five rows.

The accepted server/UI behavior includes:

- four-state generic list support;
- four-state selected-job detail state validation;
- delayed `eventAt` based on scheduled execution time;
- explicit `Orphan / No shop` handling;
- status-aware recent-job labels;
- generic `View all jobs` copy;
- no queue/job mutation controls;
- no sensitive Redis/provider configuration exposure.

Validation evidence recorded by the implementing agent:

- 31 focused amendment tests passed;
- full Admin suite passed;
- TypeScript passed;
- build passed;
- `git diff --check` passed;
- live API evidence returned real delayed pending-recovery jobs.

### Deferred visual proof

The previously requested screenshot showing a Delayed pending-recovery row in the
drawer is no longer a blocker for ADMIN-012.

That visual proof is explicitly transferred to ADMIN-013, which already owns the
final integrated drawer workflow and screenshot-level comparison.

ADMIN-013 must therefore include live visual evidence that:

```text
Queue  = pending-recovery-candidates
Status = Delayed
```

renders one or more real delayed jobs when such jobs are present.

### Result

`ARCH-003-ADMIN-012` is Complete.

`ARCH-003-ADMIN-013` may be promoted to Ready.
