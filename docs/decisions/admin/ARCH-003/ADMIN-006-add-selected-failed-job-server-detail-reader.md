---
id: ARCH-003-ADMIN-006
architecture_id: ARCH-003
title: Add selected failed-job server detail reader
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 60
executor: copilot
claimed_at: 2026-09-04T20:27:29Z
attempt: 2
depends_on:
  - ARCH-003-ADMIN-005
enables:
  - ARCH-003-ADMIN-007
created: 2026-09-04
updated: 2026-09-04
---

# Add selected failed-job server detail reader

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Implement the protected server-side capability to load one selected failed
BullMQ job and normalize its diagnostic details. Do not render the detail UI in
this task.

## Context

ADMIN-005 gives the UI a selected failed-job ID. This task owns only the server
read and normalized diagnostic model for that selection.

## Scope

- load one job using an approved queue name plus job ID;
- verify the queue is one of the observed queues;
- return a normalized diagnostic model containing at minimum:
  - `id`
  - `queueName`
  - `name`
  - `state`
  - `attemptsMade`
  - `timestamp`
  - `processedOn`
  - `finishedOn`
  - `failedReason`
  - `stacktrace`
  - `data`;
- include other safe BullMQ metadata only if clearly useful;
- return a safe not-found/unavailable result when the job has disappeared;
- keep all Redis access server-side and protected.

## Out of Scope

- rendering the detail panel;
- retry/delete/mutation actions;
- exposing Redis connection/configuration details.

## Requirements

- arbitrary Redis queues/keys must not be accepted from the browser;
- raw environment values must never be included in errors/responses;
- the reader must tolerate completed cleanup/disappearing job records;
- the response shape must be stable enough for ADMIN-007 to render without
  reaching into BullMQ objects directly in the browser.

## Attempt 2 Architect Correction

Attempt 1 is **not accepted**.

The selected-job detail capability is scoped to **failed jobs**, but the current
server reader loads any existing job from an approved queue and returns its
normalized detail regardless of BullMQ state.

Current behavior:

```text
approved queue + arbitrary existing job ID
  -> getJob(jobId)
  -> getJobState(jobId)
  -> state is returned but not enforced
  -> full normalized detail including `data` is returned
```

This permits a platform-admin caller to manually request the failed-job detail
endpoint for a waiting, active, delayed, or otherwise non-failed job. That
broadens the endpoint beyond the ARCH-003 failure-diagnosis boundary and can
expose payload data for jobs that were never selected from the failed-job list.

Attempt 2 must keep the correction inside this task and enforce the server-side
failed-job invariant.

Required behavior:

```text
approved queue + job ID
  -> load job and state
  -> job missing                 => safe not-found
  -> state != failed             => safe not-found
  -> state == failed             => return normalized failed-job detail
```

Use the existing safe not-found contract rather than disclosing whether a
non-failed job with that ID exists.

Do not change the ADMIN-004 list API or ADMIN-005 browser UI.

## Work Items

- [x] Define the selected failed-job detail model.
- [x] Implement approved queue + job lookup.
- [x] Normalize timestamps, stacktrace and data fields.
- [x] Implement the protected read interface/route.
- [x] Add not-found/unavailable handling.
- [x] Add focused detail-reader/API tests.

- [x] Attempt 2: enforce `state === 'failed'` before returning selected-job detail.
- [x] Attempt 2: treat an existing non-failed job as the existing safe not-found result.
- [x] Attempt 2: add focused regression coverage for a non-failed existing job.
- [x] Attempt 2: rerun the full Admin validation contract.

## Interfaces / Contracts

Consumes selected queue/job identity from the Admin UI.

Produces the Admin-internal detail model consumed by `ARCH-003-ADMIN-007`.

## Dependencies

- `ARCH-003-ADMIN-005`

## Enables

- `ARCH-003-ADMIN-007`

## Acceptance Criteria

- [x] An approved queue/job selection can be loaded server-side.
- [x] The required normalized detail fields are returned.
- [x] Missing/disappeared jobs fail safely.
- [x] Unknown queue names are rejected.
- [x] Redis/environment secrets are not exposed.
- [x] No detail-panel UI is implemented in this task.

- [x] An existing job whose BullMQ state is not `failed` does not return detail.
- [x] A non-failed job is mapped to the same safe not-found contract as a disappeared job.
- [x] No payload/stacktrace from a non-failed job can be returned by this endpoint.

## Validation

- [x] focused selected-job detail reader tests
- [x] focused protected route/API tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

Do not send live BullMQ class instances to the client. Return a plain normalized
Admin model.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/failed/detail/route.ts`
- `moda-interact-admin/tests/security/admin-failed-job-detail.test.mjs`

### Work Completed
- Added the allowlisted `readFailedJobDetail` server reader using approved queue
  definitions and BullMQ `getJob`/`getJobState` access.
- Added the stable plain `FailedJobDetail` model with normalized ISO timestamps,
  stacktrace, data, failure reason, attempts and state fields.
- Added safe invalid-query, not-found and unavailable handling for disappeared
  jobs and bounded infrastructure failures.
- Added the protected `/api/admin/queues/failed/detail` route with auth-first
  ordering and no-store responses.
- Kept the implementation read-only and did not modify the detail-panel UI.
- Enforced the failed-job boundary by rejecting any existing job whose BullMQ
  state is not `failed` with the same safe not-found error as a missing job.
- Added regression coverage proving non-failed jobs cannot return payload or
  stacktrace diagnostics.

### Validation Results
- Focused detail reader/API tests: 4 passed.
- `npm test`: 48 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two existing exhaustive-deps warnings in
  `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed and included `/api/admin/queues/failed/detail`.
- `git diff --check`: passed.

### Deviations
None.

### Assumptions
- BullMQ job data is already JSON-deserialized by BullMQ and is therefore safe
  to return as the normalized diagnostic payload; raw Queue/Job instances are
  never returned.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

The Attempt 1 boundary issue has been corrected. The selected-job detail reader
now enforces the failed-job invariant server-side:

```text
approved queue + job ID
  -> wait for bounded queue readiness
  -> load job + BullMQ state
  -> missing job       => safe not-found
  -> state != failed   => same safe not-found
  -> state == failed   => normalized diagnostic detail
```

This prevents waiting, active, delayed, or other non-failed jobs from returning
payload or stacktrace through the failure-diagnostics endpoint.

The remaining ADMIN-006 behavior is also conformant:

- queue names are restricted to the approved observed queue definitions;
- missing/invalid input is rejected before detail is returned;
- Redis/configuration failures collapse to the generic unavailable contract;
- the route performs platform-admin authorization before calling the reader;
- the route uses no-store responses;
- the normalized model is a plain object containing the agreed lifecycle,
  failure, stacktrace, and job-data fields;
- no selected-job detail UI or mutation controls were introduced early.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/failed/detail/route.ts`
- `moda-interact-admin/tests/security/admin-failed-job-detail.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-006-add-selected-failed-job-server-detail-reader.md`

### Validation Reviewed

Implementing-agent evidence records for Attempt 2:

- focused selected-job detail tests: 4 passed;
- full Admin tests: 48 passed;
- TypeScript: pass;
- lint: pass, with the two previously existing exhaustive-deps warnings;
- production build: pass;
- `git diff --check`: pass.

The focused regression test explicitly covers an existing non-failed job whose
payload and stacktrace must not be returned.

The supplied review archive does not include installed `node_modules`, so the
architect inspected the current source/test implementation and recorded
validation rather than reinstalling dependencies solely to rerun the suite.

### Architecture Conformance

Accepted.

The implementation remains read-only, confined to `moda-interact-admin`, and
provides the stable protected server model required by ADMIN-007 without
beginning its presentation work.

### Follow-up

`ARCH-003-ADMIN-007` is now Ready.

ADMIN-007 is the final ARCH-003 implementation task and should consume this
normalized detail endpoint to render the read-only failed-job diagnostic panel.
