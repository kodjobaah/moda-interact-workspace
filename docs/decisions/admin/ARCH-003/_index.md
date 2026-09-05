# ARCH-003 Admin Tasks

Architecture:

`docs/architecture/ARCH-003-admin-operational-ui.md`

Queue-overview readiness amendment:

`docs/architecture/ARCH-003-queue-overview-readiness-amendment.md`

Assigned Agent:

`moda_admin`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| ADMIN-001 | Add compact queue activity overview cards to Tenant Directory | Complete | ARCH-002-ADMIN-011 |
| ADMIN-002 | Move detailed queue diagnostics to Observability page shell | Complete | ARCH-003-ADMIN-001 |
| ADMIN-008 | Fix Tenant Directory queue overview readiness and unavailable-state containment | Complete | ARCH-003-ADMIN-002 |
| ADMIN-009 | Repair KPI card JSX compile regression | Superseded | Correction completed in ADMIN-008 Attempt 2 |
| ADMIN-003 | Present the four queues in a compact summary table | Complete | ARCH-003-ADMIN-008 |
| ADMIN-004 | Add bounded failed-job server reader/API | Complete | ARCH-003-ADMIN-003 |
| ADMIN-005 | Add sortable failed-job browser UI | Complete | ARCH-003-ADMIN-004 |
| ADMIN-006 | Add selected failed-job server detail reader | Complete | ARCH-003-ADMIN-005 |
| ADMIN-007 | Add failed-job detail panel UI | Complete | ARCH-003-ADMIN-006 |
| ADMIN-010 | Align Admin sidebar shell and Observability navigation with approved UI | Complete | ARCH-003-ADMIN-007 |
| ADMIN-014 | Fix detailed queue snapshot cold-connection readiness | Complete | ARCH-003-ADMIN-010 |
| ADMIN-011 | Recompose Shopify Queues into main table and right details drawer | Complete | ARCH-003-ADMIN-010, ARCH-003-ADMIN-014 |
| ADMIN-015 | Add bounded shop and status queue-job reader API | Complete | ARCH-003-ADMIN-011 |
| ADMIN-016 | Add selected active and failed queue-job detail API | Complete | ARCH-003-ADMIN-015 |
| ADMIN-012 | Populate queue details drawer with metrics and filtered recent jobs | Complete | ARCH-003-ADMIN-016 |
| ADMIN-013 | Integrate paginated filtered queue-job diagnostics into drawer workflow | Complete | ARCH-003-ADMIN-012 |

Execution chain:

```text
ARCH-003-ADMIN-001   Complete
    -> ARCH-003-ADMIN-002   Complete
        -> ARCH-003-ADMIN-008   Complete
            -> ARCH-003-ADMIN-003   Complete
                -> ARCH-003-ADMIN-004   Complete
                    -> ARCH-003-ADMIN-005   Complete
                        -> ARCH-003-ADMIN-006   Complete
                            -> ARCH-003-ADMIN-007   Complete
                                -> ARCH-003-ADMIN-010   Complete
                                    -> ARCH-003-ADMIN-014   Complete
                                        -> ARCH-003-ADMIN-011   Complete
                                            -> ARCH-003-ADMIN-015   Complete
                                                -> ARCH-003-ADMIN-016   Ready
                                                    -> ARCH-003-ADMIN-012   Pending
                                                        -> ARCH-003-ADMIN-013   Pending
```

## ADMIN-002 architect acceptance

`ARCH-003-ADMIN-002` is architect-accepted Complete after Attempt 1.

Accepted behavior:

```text
Tenant Directory
  -> no detailed QueueMonitor block

Observability
  -> discoverable Shopify Queues destination
  -> protected /observability/queues route
  -> existing read-only QueueMonitor and refresh behavior preserved
  -> existing Grafana navigation preserved
```

The separately observed queue-overview `Unavailable` issue is not part of
ADMIN-002. It is owned by `ARCH-003-ADMIN-008`, which was subsequently completed.

The individual task file is authoritative for task state.

## ADMIN-008 Attempt 2 architect acceptance

`ARCH-003-ADMIN-008` is architect-accepted Complete after Attempt 2.

Accepted behavior:

```text
cold queue
  -> bounded waitUntilReady()
  -> getJobCounts('active')
  -> healthy numeric KPI

genuine Redis failure
  -> bounded unavailable result
  -> compact contained `Unavailable` status

KpiCard
  -> valid TSX
  -> compact status branch
  -> unchanged healthy numeric branch
```

The accidental `ARCH-003-ADMIN-009` task is Superseded; its parser correction
was completed within ADMIN-008 Attempt 2.

`ARCH-003-ADMIN-003` was subsequently completed.

## ADMIN-003 architect acceptance

`ARCH-003-ADMIN-003` is architect-accepted Complete after Attempt 1.

Accepted behavior:

```text
Observability > Shopify Queues
  -> exactly four observed queue rows
  -> compact operational table
  -> waiting / active / delayed / failed / workers / last activity
  -> existing refresh controls preserved
  -> read-only queue selection via View details
  -> no failed-job retrieval yet
```

This satisfies the direct dependency for `ARCH-003-ADMIN-004`, which was subsequently completed.

`ARCH-003-ADMIN-005` through `ARCH-003-ADMIN-007` remain Pending.

## ADMIN-004 architect acceptance

`ARCH-003-ADMIN-004` is architect-accepted Complete after Attempt 1.

Accepted server boundary:

```text
GET /api/admin/queues/failed
  -> platform-admin authorization first
  -> allowlisted queue only
  -> bounded page / limit
  -> approved sort fields and direction
  -> default failedAt desc
  -> list-level failed-job summaries only
  -> no payload / stacktrace
  -> generic invalid/unavailable errors
```

This satisfies the direct dependency for `ARCH-003-ADMIN-005`, which was subsequently completed.

`ARCH-003-ADMIN-006` and `ARCH-003-ADMIN-007` remain Pending.

## ADMIN-005 architect acceptance

`ARCH-003-ADMIN-005` is architect-accepted Complete after Attempt 1.

Accepted UI boundary:

```text
selected queue
  -> bounded ADMIN-004 failed-job list API
  -> Failed at desc by default
  -> approved sorting controls
  -> bounded failed-job rows
  -> selectable failed job
  -> loading / empty / unavailable states
  -> no selected-job detail fetch yet
```

This satisfies the direct dependency for `ARCH-003-ADMIN-006`, which was subsequently completed.

`ARCH-003-ADMIN-007` was subsequently completed.

## ADMIN-006 Attempt 2 correction

Attempt 1 is not architect-accepted.

The selected-job detail reader correctly protects and normalizes the detail
response, but it does not yet enforce that the requested BullMQ job is actually
in the `failed` state.

`ARCH-003-ADMIN-006` is therefore Ready for Attempt 2 with its previous claim
cleared. The correction must map an existing non-failed job to the same safe
not-found contract used for a disappeared job.

`ARCH-003-ADMIN-007` was subsequently completed.

## ADMIN-006 Attempt 2 architect acceptance

`ARCH-003-ADMIN-006` is architect-accepted Complete after Attempt 2.

Accepted detail boundary:

```text
selected approved queue + failed-job ID
  -> protected server reader
  -> bounded queue readiness
  -> load job + current BullMQ state
  -> missing/non-failed => same safe not-found contract
  -> failed => normalized read-only detail
       id / queue / name / state / attempts
       timestamps / failed reason / stacktrace / data
```

The Attempt 1 failed-state boundary issue is resolved.

This satisfies the direct dependency for `ARCH-003-ADMIN-007`, which was promoted to Ready at that point.

## ADMIN-007 architect acceptance / ARCH-003 completion

`ARCH-003-ADMIN-007` is architect-accepted Complete after Attempt 1.

Accepted final diagnostic workflow:

```text
Observability > Shopify Queues
  -> four compact queue summary rows
  -> select queue
  -> bounded sortable failed-job list
  -> select failed job
  -> protected failed-job detail lookup
  -> lifecycle fields
  -> failed reason
  -> bounded stacktrace
  -> bounded formatted job data
  -> copy-only diagnostic affordances
  -> no queue/job mutations
```

All executable ARCH-003 tasks are now Complete.

`ARCH-003` is architect-accepted Complete.


## ARCH-003 reopened for approved UI parity

ARCH-003 was functionally complete but the rendered Shopify Queues composition
did not match the approved reference.

Approved reference:

`docs/architecture/ARCH-003-shopify-queues-approved-reference.png`

The completed Redis/API/security tasks remain accepted. The new 010-013 chain is
presentation/interaction correction only.

`ARCH-003-ADMIN-010` is the only Ready task.


## ADMIN-010 sidebar refinement

The approved visual target covers the complete left navigation shell, not only
the Shopify Queues child link.

ADMIN-010 therefore owns the branded persistent sidebar composition, nested
Observability hierarchy, active child state, and bottom administrator identity
area.

Dashboard, Billing, and Settings are visible in the reference but do not
currently have real Admin routes. They must not be fabricated as dead links;
their absence must be recorded as a visual-parity deviation unless separately
implemented.

## ADMIN-010 architect acceptance

`ARCH-003-ADMIN-010` is architect-accepted Complete after Attempt 1.

Accepted sidebar boundary:

```text
Moda Interact
  -> Tenant Directory
  -> Observability [active/expanded]
       Overview
       Shopify Queues
       Grafana
  -> bottom Administrator identity/role treatment
```

The shell intentionally does not fabricate Dashboard, Billing, or Settings
routes that do not exist in the Admin product.

The current authenticated principal does not expose a display name, so the
generic Administrator label is an accepted visual-reference deviation.

This satisfies the direct dependency for `ARCH-003-ADMIN-011`, which is now
Ready.


## ADMIN-011 review held / ADMIN-014 runtime prerequisite

ADMIN-011 has returned to review with the drawer composition present in source,
but current runtime evidence shows no queue snapshot, so the drawer cannot be
exercised or visually accepted.

Source inspection found that the detailed queue snapshot path has not yet
received the bounded cold-connection readiness treatment previously added to
the overview path.

`ARCH-003-ADMIN-014` is Ready as the only executable task. ADMIN-011 remains in
Review and must be re-reviewed after ADMIN-014 is Complete.

ADMIN-012 and ADMIN-013 remain Pending.

## ADMIN-014 Attempt 2 — live Redis integration required

Attempt 1 is not architect-accepted.

The mocked readiness regression passes, but the real Shopify Queues screen still
receives no queue snapshot while direct live Redis/BullMQ probes succeed.

ADMIN-014 is therefore Ready for Attempt 2.

Attempt 2 must identify the exact failing real operation and prove the real
production snapshot reader returns all four queue rows from the developer's
live Redis service. Unit/mocked tests alone are not sufficient.

If live integration still fails, ADMIN-014 must return Blocked rather than
Review.

ADMIN-011 remains in Review with visual acceptance held.


## ADMIN-014 architect acceptance / ADMIN-011 Attempt 2

`ARCH-003-ADMIN-014` is architect-accepted Complete after Attempt 2.

Live proof established that the real production reader and API return all four
queues. The runtime-data prerequisite is therefore closed.

The populated runtime screenshot then exposed a separate visual defect in
ADMIN-011: the Queue details panel is an in-flow flex sibling and compresses the
queue table.

`ARCH-003-ADMIN-011` is Ready for Attempt 2. The drawer must be a true fixed
overlay that does not participate in the table's width calculation.

Future drawer workflow refinement:

```text
ADMIN-012
  -> queue summary + metrics + at most 5 recent failures
  -> View all failed jobs

ADMIN-013
  -> sortable full failed-job browser
  -> pagination, default 10 rows/page
  -> selected failed-job diagnostics
```


## ADMIN-011 Attempt 3 — resizable full-workspace overlay

Attempt 2 proved the true-overlay architecture and zero table reflow, but the
fixed 560px geometry is not the final accepted interaction.

ADMIN-011 is Ready for Attempt 3.

Final interaction requirement:

```text
open
  -> overlay fills full Admin workspace to right of sidebar
  -> full viewport height

resize
  -> drag left edge to narrow/widen
  -> queue table underneath does not reflow

maximize
  -> restore full workspace width

close + reopen
  -> opens maximized again
```

The resize affordance must be keyboard accessible.

ADMIN-012 remains Pending and will reduce the summary view to at most 5 recent
failures.

ADMIN-013 remains Pending and owns the full paginated failed-job browser
(default 10 rows per page).

## ADMIN-011 Attempt 4 — queue-name switching

Attempt 3 established the accepted full-workspace, resizable, no-reflow overlay
mechanics.

ADMIN-011 remains Ready for one final interaction correction.

The queue table must remove its separate Actions/View details column. Each queue
name becomes the visible accessible selection control.

State contract:

```text
drawer closed + queue-name click
  -> open maximized

drawer open/narrowed + different queue-name click
  -> switch selected queue
  -> preserve drawer width
  -> preserve table width
  -> refresh queue-specific diagnostics
```

This is specifically intended to let an administrator narrow the overlay,
expose the queue names, and switch queues while still knowing exactly which
queue is being selected.

ADMIN-012 and ADMIN-013 remain Pending.


## ADMIN-011 Attempt 4 architect acceptance

`ARCH-003-ADMIN-011` is architect-accepted Complete after Attempt 4.

Accepted interaction:

```text
fresh queue-name click
  -> drawer opens maximized

resize narrower
  -> underlying queue table does not reflow

click another visible queue name
  -> selected queue changes
  -> drawer width is preserved

close + fresh open
  -> maximized again
```

The drawer mechanics are now closed.

## Shop / Status operational browser refinement

The Queue details workflow is expanded from failed-only browsing to:

```text
Shop -> Status -> Direction
```

Defaults:

```text
All shops -> Failed -> Descending
```

Initial statuses:

```text
Failed
Active
```

Jobs with no explicit stable shop association are not dropped. They are
classified as:

```text
Orphan / No shop
```

and must be filterable.

The revised execution chain is:

```text
ADMIN-011   Complete
    -> ADMIN-015   Ready
        -> ADMIN-016   Pending
            -> ADMIN-012   Pending
                -> ADMIN-013   Pending
```

ADMIN-015 owns the bounded generic list/facet server contract.
ADMIN-016 owns selected Failed/Active detail.
ADMIN-012 owns the filter/summary drawer UI.
ADMIN-013 owns the full paginated browser and integrated detail workflow.

## ADMIN-015 architect acceptance

`ARCH-003-ADMIN-015` is architect-accepted Complete after Attempt 1.

Live proof confirms both the previously accepted queue-summary API and the new
generic queue-job API are healthy:

```text
/api/admin/queues
  -> HTTP 200
  -> four queues

/api/admin/queues/jobs
  -> failed + active
  -> all shops + explicit orphan filter
  -> bounded pagination
  -> truthful orphan/facet metadata
```

Historical checkout jobs currently surface as `Orphan / No shop` when they lack
the documented explicit tenant-domain shape. This is intentional; no fuzzy
inference is performed.

`ARCH-003-ADMIN-016` is now Ready.

ARCH-004 separately owns producer-side tenant-identifiable queue metadata for
future Shopify jobs.


## End-of-session authoritative handoff

The executable ARCH-003 task at architecture-session close is:

```text
ARCH-003-ADMIN-016   Ready
```

Then, one at a time after architect acceptance:

```text
ARCH-003-ADMIN-012   Pending
ARCH-003-ADMIN-013   Pending
```

Do not promote a downstream task merely because its predecessor reports
implementation complete. The predecessor must first return to `review` and be
accepted by `moda_architect`.


## ADMIN-016 architect acceptance

`ARCH-003-ADMIN-016` is architect-accepted Complete after Attempt 1.

The selected-job server contract now supports:

```text
Failed
Active
```

with requested-state/current-state matching and safe not-found behavior on
state races.

Current execution:

```text
ADMIN-016   Complete
    -> ADMIN-012   Ready
        -> ADMIN-013   Pending
```

`ADMIN-012` is the only newly promoted ARCH-003 task in this overlay.


## ADMIN-012 live-runtime amendment

While implementing/testing ADMIN-012, live evidence showed that
`pending-recovery-candidates` contained Delayed jobs that the existing
`failed | active` reader contract could not return.

ADMIN-012 is therefore amended in place to support:

```text
Failed
Active
Waiting
Delayed
```

across the existing generic list/detail APIs and the drawer.

This is a same-task architectural correction. Do not create or claim a competing
ADMIN task for this behavior while ADMIN-012 is active.

ADMIN-013 remains downstream and must inherit the same four-state filter
contract.


## ADMIN-012 architect acceptance / ADMIN-013 promotion

`ARCH-003-ADMIN-012` Attempt 1 is architect-accepted Complete, including
Amendment 001.

Current authoritative remaining execution:

```text
ARCH-003-ADMIN-012   Complete
        |
        v
ARCH-003-ADMIN-013   Ready
```

ADMIN-013 inherits all four queue-job states:

```text
Failed | Active | Waiting | Delayed
```

The final live visual proof of a real delayed pending-recovery job is owned by
ADMIN-013 as part of its screenshot-level final comparison.

No later ARCH-003 task is executable.


## Scope correction: remaining tenant-attribution work stays in ARCH-003

The previously drafted ARCH-005 follow-up is withdrawn.

After `ARCH-003-ADMIN-013` is architect-accepted, the remaining ARCH-003 chain is:

```text
ARCH-003-BACKGROUND-001
    -> ARCH-003-ADMIN-017
        -> ARCH-003-ADMIN-018
            -> ARCH-003-SYSTEM-TEST-001
```

These tasks are Pending until their dependencies are architect-accepted.

No ARCH-005 task should remain in the workspace.


## ADMIN-013 architect acceptance

`ARCH-003-ADMIN-013` Attempt 1 is architect-accepted Complete.

The final Admin drawer workflow now includes:

```text
Recent jobs (5)
    -> View all jobs
    -> 10-row paginated browser
    -> selected job detail
```

with:

```text
Failed | Active | Waiting | Delayed
```

and Shop / Status / Direction preserved while paging.

The uploaded task file contained stale claim/report metadata; architect
acceptance reconciled it to the reviewed implementation state.

Current ARCH-003 execution:

```text
ADMIN-013                  Complete
    -> BACKGROUND-001      Ready
        -> ADMIN-017       Pending
            -> ADMIN-018   Pending
                -> SYSTEM-TEST-001 Pending
```

ARCH-003 remains In Progress.


## BACKGROUND-001 acceptance / ADMIN-017 promotion

`ARCH-003-BACKGROUND-001` is architect-accepted Complete.

Current remaining Admin execution:

```text
ARCH-003-ADMIN-017   Ready
        |
        v
ARCH-003-ADMIN-018   Pending
        |
        v
ARCH-003-SYSTEM-TEST-001   Pending
```

ADMIN-017 is the only newly executable Admin task.


## ADMIN-017 architect acceptance / ADMIN-018 promotion

`ARCH-003-ADMIN-017` Attempt 1 is architect-accepted Complete.

The pending-recovery queue now uses explicit `data.shopDomain` for Admin shop
attribution while historical jobs without the field remain `Orphan / No shop`.

Current authoritative execution:

```text
ARCH-003-ADMIN-017        Complete
        |
        v
ARCH-003-ADMIN-018        Ready
        |
        v
ARCH-003-SYSTEM-TEST-001  Pending
```

ADMIN-018 is the only newly executable task.


## ADMIN-018 architect acceptance / ADMIN-019 navigation correction

`ARCH-003-ADMIN-018` Attempt 1 is architect-accepted Complete.

The current live panel exposed one remaining navigation cleanup owned by
`ARCH-003-ADMIN-019`.

Final navigation target:

```text
Observability
  Shopify Queues
  Grafana
```

The Observability parent itself opens `/observability/queues`.

There is no `Overview` child, and the `/observability` Grafana/status page must
not contain a Shopify Queues promotional card or CTA.

Current authoritative execution:

```text
ARCH-003-ADMIN-018        Complete
        |
        v
ARCH-003-ADMIN-019        Ready
        |
        v
ARCH-003-SYSTEM-TEST-001  Pending
```
