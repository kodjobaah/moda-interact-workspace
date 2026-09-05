---
id: ARCH-003-ADMIN-016
architecture_id: ARCH-003
title: Add selected active and failed queue-job detail API
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 45
executor: copilot
claimed_at: 2026-09-04T22:54:05Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-015
enables:
  - ARCH-003-ADMIN-012
created: 2026-09-04
updated: 2026-09-04
---

# Add selected active and failed queue-job detail API

## Objective

Generalize selected-job diagnostics so a job selected from the new Status
filter can be inspected whether it is currently:

```text
failed
active
```

without weakening the existing server-side state invariant.

## Route

Add a generic protected route:

```text
GET /api/admin/queues/jobs/detail
```

Inputs:

```text
queue
status=failed|active
jobId
```

Keep the existing failed-only detail route intact during migration unless a
later cleanup task explicitly removes it.

## State invariant

The requested status is part of the security/read consistency contract.

Required flow:

```text
allowlisted queue + allowlisted status + job ID
        ↓
load job + current BullMQ state
        ↓
missing job
        -> safe not-found

actual state != requested status
        -> same safe not-found

actual state == requested status
        -> normalized detail
```

This deliberately handles races where an Active job completes or changes state
between list rendering and detail selection.

Do not reveal that a job exists in another state.

## Normalized detail model

Return:

```text
id
queueName
name
status
shop
attemptsMade
timestamp
processedOn
finishedOn
failedReason
stacktrace
data
```

`shop` must reuse the exact projection contract from ADMIN-015.

For Active jobs:

- `failedReason` may be empty/null;
- stacktrace is normally empty;
- job data remains read-only diagnostic data for platform administrators.

## Security

- platform-admin auth first;
- queue/status allowlist;
- safe not-found for state mismatch;
- generic unavailable errors;
- no Redis URL/env/provider credentials;
- no mutation controls.

This is an explicit architecture expansion from the previously accepted
failed-only detail endpoint. It is authorized because the product requirement
now includes inspection of Active jobs.

## Work Items

- [x] Add generic active/failed detail reader.
- [x] Reuse ADMIN-015 shop projection.
- [x] Enforce requested-status == current-state invariant.
- [x] Add protected route.
- [x] Add failed and active detail tests.
- [x] Add state-race/mismatch regression tests.
- [x] Run full Admin validation.
- [x] Return to `review` and STOP.

## Acceptance Criteria

- [x] Failed selected jobs remain inspectable.
- [x] Active selected jobs are inspectable.
- [x] A state mismatch returns safe not-found.
- [x] Shop projection is present and consistent with list rows.
- [x] No non-allowlisted status is accepted.
- [x] No job mutation is introduced.
- [x] Full validation passes.

## Completion Report

### Status
Ready for Review.

### Files Changed

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/jobs/detail/route.ts`
- `moda-interact-admin/tests/security/admin-queue-job-detail.test.mjs`

### Work Completed

Added a protected generic queue-job detail reader and route for `failed` and
`active` jobs. The reader validates the allowlisted queue, required status, and
job ID, loads the job and current BullMQ state, returns a safe not-found result
for missing/state-mismatched jobs, and reuses the ADMIN-015 explicit Shopify
tenant shop projection. The existing failed-only detail reader and route remain
unchanged.

### Validation Results

- `node --test tests/security/admin-queue-job-detail.test.mjs`: 4 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm test`: 69 passed.
- `npm run lint`: passed with two pre-existing `react-hooks/exhaustive-deps` warnings in `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed; existing workspace-root inference and optional BullMQ `@valkey/valkey-glide` warnings remain.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

- The generic detail request requires an explicit `status` query parameter so
        the requested-state invariant cannot be weakened by an implicit default.
- Active detail may include the read-only BullMQ `data` and stacktrace fields as
        authorized diagnostic output; active `failedReason` is normalized to empty.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation adds the generic selected queue-job detail contract
without weakening the existing failed-only detail API.

Accepted behavior:

```text
queue + requested status + jobId
        |
        v
allowlisted queue/status
        |
        v
load job + current BullMQ state
        |
        +-- missing job -----------------> 404 not_found
        |
        +-- current state != requested --> 404 not_found
        |
        `-- current state == requested --> normalized detail
```

The implementation:

- supports only `failed` and `active`;
- requires an explicit Status for detail reads;
- reuses ADMIN-015 `extractQueueJobShop(...)`;
- retains platform-admin authorization before queue access;
- returns generic invalid/not-found/unavailable errors;
- preserves the legacy failed-only route and reader;
- introduces no retry/requeue/delete/pause/resume behavior.

For Active jobs, `failedReason` is normalized to an empty value. Diagnostic
`data` remains read-only as explicitly authorized by the task.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/jobs/detail/route.ts`
- `moda-interact-admin/tests/security/admin-queue-job-detail.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-016-add-active-failed-queue-job-detail-api.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused detail tests: 4 passed;
- full Admin suite: 69 passed;
- TypeScript: pass;
- lint: pass with the two pre-existing hook warnings;
- production build: pass with previously documented warnings;
- `git diff --check`: pass.

### Architecture Conformance

Accepted.

The selected-job server boundary is now ready for the drawer UI to consume.

### Follow-up

`ARCH-003-ADMIN-012` is now Ready.

ADMIN-012 owns:

```text
Shop -> Status -> Direction
```

plus selected-queue metrics/info and at most five matching recent jobs in the
approved resizable drawer.

ADMIN-013 remains Pending and owns the full paginated browser/detail workflow.
