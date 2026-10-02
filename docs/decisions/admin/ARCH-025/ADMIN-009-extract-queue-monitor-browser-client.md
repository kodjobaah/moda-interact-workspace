---
id: ARCH-025-ADMIN-009
architecture_id: ARCH-025
title: Extract QueueMonitor browser contracts and client boundary
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-025-ADMIN-010
created: 2026-10-02
updated: 2026-10-02
---

# Extract QueueMonitor browser contracts and client boundary

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the QueueMonitor browser response types and HTTP request construction/parsing into bounded client modules, and make existing source-based QueueMonitor security/internationalisation assertions extraction-safe before hook or JSX extraction begins.

## Context

The 1,058-line QueueMonitor currently defines browser response types inline and performs all three fetch lifecycles directly in the component. Later hook/view tasks need one stable browser contract/client boundary. Several existing security tests read only `queue-monitor.tsx`, so their source loader must first follow the bounded QueueMonitor module set without weakening read-only/security/i18n assertions.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/queue-monitor.types.ts
src/components/admin/queue-monitor/queue-monitor.client.ts
tests/unit/queue-monitor-client.test.ts
tests/security/admin-queue-monitor.test.mjs
tests/security/admin-queue-details-drawer.test.mjs
tests/security/admin-failed-job-detail-panel.test.mjs
tests/security/admin-internationalization.test.mjs
```

## Out of Scope

Hook extraction, drawer extraction, table/detail JSX extraction, server reader/API route changes, new runtime validation schemas or Shared contracts.

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

### R1 — browser-local response contracts

Create browser-safe type mirrors for the current `/api/admin/queues`, `/jobs` and `/jobs/detail` responses (`QueueMonitorSnapshot`, queue-job status/direction/shop/attribution shapes, `QueueJobSnapshot`, `QueueJobDetail`). The module must contain no Redis/BullMQ/server-reader import and no runtime dependency on `src/lib/admin/queue-monitor.ts`.

### R2 — bounded HTTP client

Create client functions for summary, jobs and selected-job detail requests. Preserve exact endpoint paths, `cache: "no-store"`, supplied `AbortSignal`, jobs query names/values and detail query names/values. Preserve the ability for hooks to distinguish detail 404 from other non-OK responses without changing user-facing message keys. Do not add retries, caching, deduplication or additional requests.

### R3 — extraction-safe source assertions

Change only QueueMonitor source-loading mechanics in the four authorised source-based tests so QueueMonitor assertions read the public `queue-monitor.tsx` plus direct `.ts`/`.tsx` files under `src/components/admin/queue-monitor/` in deterministic order. Do not broaden to unrelated Admin source. Preserve all existing test names and security/read-only/i18n assertions, including the prohibition on mutation controls/config secrets and catalogue-owned job labels. ADMIN-010..015 must not modify the accepted ADMIN-009 versions.

### R4 — focused client tests

Add Node tests proving exact paths/query parameters, recent/full limits, direction/status/shop/page serialization, `cache: "no-store"`, AbortSignal forwarding and detail 404/non-OK distinction. No React test framework is required.

## Work Items

- [ ] Introduce browser-only QueueMonitor response types.
- [ ] Introduce bounded HTTP client functions and rewire the monolith without changing request lifecycle ownership yet.
- [ ] Add focused pure/client tests.
- [ ] Make the four source-based QueueMonitor test loaders extraction-safe without weakening assertions.
- [ ] Prove frozen server/API sources and dedicated server tests remain byte-identical.

## Interfaces / Contracts

Repository-internal browser HTTP contract only. Protected API endpoints and server reader remain unchanged and authoritative. No cross-repository/Shared contract is introduced.

## Dependencies

None

## Enables

- `ARCH-025-ADMIN-010`

## Acceptance Criteria

- [ ] `QueueMonitor` renders through the same public export and still performs the same three requests.
- [ ] Browser modules have no server/BullMQ/Redis runtime import.
- [ ] Client tests prove exact current request construction/error distinctions.
- [ ] All existing QueueMonitor source/security/i18n assertions remain present and pass through the bounded module-set loader.
- [ ] No server/API source or dedicated server test changes.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [ ] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [ ] For ADMIN-009 only, `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` passes with all existing test names/assertions retained.
- [ ] `node --experimental-strip-types --test tests/unit/queue-monitor-client.test.ts` passes.

- [ ] `npm run test:unit` passes without task-introduced regression.
- [ ] `npm test` passes without task-introduced regression.
- [ ] targeted ESLint for every changed Admin source/test file passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
