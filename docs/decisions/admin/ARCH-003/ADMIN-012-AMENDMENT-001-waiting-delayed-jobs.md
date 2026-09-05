# ADMIN-012 Amendment 001 — Support Waiting and Delayed jobs

This is an architecture amendment to:

```text
ARCH-003-ADMIN-012
```

It is intentionally **not a second task** and has no task ID/frontmatter.

The current ADMIN-012 executor should continue the same attempt and incorporate
this amendment without resetting its claim or Completion Report.

## Why this amendment exists

Live runtime evidence:

```text
queue = pending-recovery-candidates

waiting = 0
active  = 0
delayed = 5
failed  = 0
```

RedisInsight showed `pending-recovery-*` jobs, while the Admin drawer returned
zero rows for Failed and Active.

Cause:

```text
existing generic queue-job status contract
    = failed | active
```

The jobs are in BullMQ state:

```text
delayed
```

so they are outside the reader contract.

## Required outcome

The read-only Admin queue diagnostics workflow must support:

```text
failed | active | waiting | delayed
```

end to end.

## Server changes

Extend the existing ADMIN-015 generic list reader and route so:

```text
GET /api/admin/queues/jobs
  ?queue=<allowlisted>
  &status=failed|active|waiting|delayed
  &shop=*
  &page=1
  &limit=10
  &direction=desc
```

accepts all four states.

Extend the ADMIN-016 selected-job detail reader and route so:

```text
GET /api/admin/queues/jobs/detail
  ?queue=<allowlisted>
  &status=failed|active|waiting|delayed
  &jobId=<id>
```

accepts all four states.

Keep the existing state-race rule:

```text
missing job
    -> not_found

actual state != requested state
    -> same safe not_found

actual state == requested state
    -> normalized detail
```

Do not expose additional infrastructure secrets and do not add mutation.

## Sorting / eventAt

Use:

```text
failed  -> finishedOn ?? processedOn ?? timestamp
active  -> processedOn ?? timestamp
waiting -> timestamp
delayed -> timestamp + max(delay, 0)
```

The Delayed value should therefore sort by scheduled execution time.

## Facets / pagination

The existing bounded-scan, filter-before-pagination behavior remains.

Shop facets must continue to be truthful across the selected state.

Jobs with no supported shop projection must still be returned when:

```text
shop=*
```

and represented explicitly as:

```text
Orphan / No shop
```

Do not discard a Delayed pending-recovery candidate merely because it currently
has no shopDomain projection.

## Drawer changes

Status selector:

```text
Failed
Active
Waiting
Delayed
```

Default remains:

```text
All shops
Failed
Descending
```

Changing Status:

- reloads recent jobs;
- clears stale selected-job detail;
- resets downstream pagination to page 1.

Recent summary remains bounded to at most 5 matching jobs.

## Status-aware row presentation

Use appropriate labels:

```text
Failed
  failed time + failure reason

Active
  processed/start time

Waiting
  queued time

Delayed
  scheduled time
```

Do not require a failure reason for non-Failed states.

## Copy correction

Remove fixed failure-only text from the generic workflow.

Do not render:

```text
View all failed jobs
```

when another status is selected.

Preferred stable copy:

```text
Recent jobs
View all jobs
```

A dynamic `Recent delayed jobs` heading is also acceptable if it remains
correctly synchronized with the selected state.

## Tests required

Add/extend focused tests proving:

- Failed list still works.
- Active list still works.
- Waiting list returns waiting jobs.
- Delayed list returns delayed jobs.
- Delayed `eventAt` uses scheduled execution time.
- `shop=*` does not hide orphan Delayed jobs.
- Explicit orphan filter still works.
- Waiting detail succeeds only while Waiting.
- Delayed detail succeeds only while Delayed.
- Waiting/Delayed state races return safe not_found.
- Unauthorized access is rejected before queue access.
- Status parser rejects unsupported values.
- UI exposes all four Status options.
- `View all failed jobs` does not remain as stale generic copy.

## Live acceptance evidence

With a real pending recovery present, the final live proof must show:

```text
Queue: pending-recovery-candidates
Status: Delayed
```

and at least one of the jobs counted under the queue's Delayed metric must be
visible in the recent-job list.

For the current observed environment, the queue snapshot showed:

```text
Delayed = 5
```

so `Status=Delayed` must not incorrectly report that no jobs exist.

## Out of scope

- retry/requeue/delete/pause/resume;
- changing BullMQ retention;
- changing the pending-recovery scheduling model;
- fabricating shopDomain values;
- changing Shopify event-envelope metadata;
- changing Background business behavior.
