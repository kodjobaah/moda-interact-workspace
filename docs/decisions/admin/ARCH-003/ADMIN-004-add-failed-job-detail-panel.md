---
id: ARCH-003-ADMIN-004
architecture_id: ARCH-003
title: Add bounded failed-job server reader and API
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-04T20:05:18Z
attempt: 1
depends_on:
  - ARCH-003-ADMIN-003
enables:
  - ARCH-003-ADMIN-005
created: 2026-09-04
updated: 2026-09-04
---

# Add bounded failed-job server reader and API

## Architecture

Architecture ID: `ARCH-003`

Architecture document:
`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator: `moda_architect`

## Objective

Implement the protected server-side capability required to read a bounded,
sortable page of failed jobs for one selected queue. Do not build the failed-job
browser UI in this task.

## Context

The queue summary screen can expose the failed count, but diagnosis requires
actual failed jobs. The server read boundary is separated from the UI so Luna
can focus only on safe BullMQ access, bounding and sorting semantics.

## Scope

- add an Admin server reader and protected API/route for failed jobs in one
  approved observed queue;
- enforce an explicit bounded page/limit;
- support approved sort fields:
  - `failedAt`
  - `attemptsMade`
  - `name`
  - `id`;
- support ascending/descending order;
- default to `failedAt desc`;
- return a compact failed-job summary model suitable for list rendering;
- reject unknown queue names rather than accepting arbitrary Redis queue input;
- keep Redis/BullMQ access server-side.

## Out of Scope

- failed-job browser UI;
- selected job full detail;
- rendering stack traces or payloads;
- job mutations.

## Requirements

The failed-job list model should contain only list-level fields such as:

```text
id
queueName
name
attemptsMade
failedAt
failedReason
```

Use actual BullMQ timestamps/fields available in the installed version and
normalize them in the Admin model where necessary.

The API must not accept arbitrary Redis key prefixes or URLs from the client.

## Work Items

- [x] Define the bounded failed-job list model.
- [x] Define allowed queue identifiers and sort parameters.
- [x] Implement the server reader.
- [x] Implement the protected read endpoint/interface.
- [x] Add tests for queue allowlisting, limits, sort behavior and default order.
- [x] Add safe unavailable/error behavior without leaking Redis configuration.

## Interfaces / Contracts

Produces an Admin-internal failed-job summary list consumed by
`ARCH-003-ADMIN-005`.

No new cross-service runtime contract is introduced.

## Dependencies

- `ARCH-003-ADMIN-003`

## Enables

- `ARCH-003-ADMIN-005`

## Acceptance Criteria

- [x] One approved queue can be queried for failed jobs.
- [x] Results are bounded.
- [x] Default ordering is most recently failed first.
- [x] Approved sort fields and direction are enforced.
- [x] Unknown queues/parameters fail safely.
- [x] Redis credentials and environment values are never returned.
- [x] No UI changes beyond any minimal test fixture are made.

## Validation

- [x] focused failed-job server-reader tests
- [x] focused protected API tests
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

The existing filename is retained because this task ID already existed as a
pending ARCH-003 task before refinement. The task body is authoritative.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/failed/route.ts`
- `moda-interact-admin/tests/security/admin-failed-jobs.test.mjs`

### Work Completed
- Added an allowlisted, bounded failed-job reader for the four observed Admin
  queues.
- Added approved sorting by `failedAt`, `attemptsMade`, `name` and `id`, with
  ascending/descending direction and `failedAt desc` as the default.
- Normalized failed jobs to list-level fields only and capped each response at
  50 jobs after a bounded 1,000-job scan.
- Added the protected `GET /api/admin/queues/failed` endpoint with auth-first
  handling, safe 400/401/503 responses and no Redis configuration exposure.
- Added focused tests for allowlisting, bounds, sorting, default order,
  payload exclusion and API security ordering.

### Validation Results
- `npm exec -- node --test tests/security/admin-failed-jobs.test.mjs` passed
  (4 tests).
- `npm test` passed (42 tests).
- `npm exec tsc -- --noEmit` passed.
- `npm run lint` passed.
- `npm run build` passed and included `/api/admin/queues/failed`.
- `git diff --check` passed.

### Deviations
The production build retains existing warnings for Next.js multiple-lockfile
workspace-root inference and BullMQ's optional `@valkey/valkey-glide` module.

### Assumptions
BullMQ `finishedOn` is the failure timestamp for failed jobs and is normalized
to the Admin `failedAt` ISO string.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The reviewed implementation satisfies the bounded ADMIN-004 server/API scope:

- only the four approved observed queue names are accepted;
- arbitrary Redis queue/key input is rejected;
- `page`, `limit`, `sort`, and `direction` are validated before queue access;
- failed-job reads are bounded to a maximum 1,000-job scan and a maximum
  50-job response page;
- default ordering is `failedAt desc`;
- approved sorting is limited to `failedAt`, `attemptsMade`, `name`, and `id`;
- list responses expose only list-level fields:
  `id`, `queueName`, `name`, `attemptsMade`, `failedAt`, and `failedReason`;
- job payload/data and stacktrace are not exposed by this list endpoint;
- the protected route performs platform-admin authorization before invoking the
  failed-job reader;
- invalid queries return a bounded 400 response;
- unavailable Redis/backend failures return a generic 503 response;
- no Redis URL, credential, environment value, payload, or stacktrace is
  returned by the route;
- no failed-job browser UI or selected-job detail work was started early.

The implementation remains read-only.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/failed/route.ts`
- `moda-interact-admin/tests/security/admin-failed-jobs.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-004-add-failed-job-detail-panel.md`

### Validation Reviewed

Implementing-agent evidence records:

- focused failed-job tests: 4 passed;
- full Admin tests: 42 passed;
- TypeScript: pass;
- lint: pass;
- production build: pass;
- source diagnostics: none;
- `git diff --check`: pass.

The supplied review archive does not contain installed `node_modules`, so the
architect inspected the current implementation and recorded validation rather
than reinstalling dependencies solely to rerun the repository suite.

### Architecture Conformance

Accepted.

The task remains confined to `moda-interact-admin`, introduces no cross-service
runtime contract, preserves the protected read-only boundary, and provides only
the server/list capability required by ADMIN-005.

### Follow-up

`ARCH-003-ADMIN-005` is now Ready.

ADMIN-005 must build only the sortable failed-job browser UI using this list
interface. It must not implement selected-job full detail retrieval, stacktrace
rendering, payload rendering, or job mutation.
