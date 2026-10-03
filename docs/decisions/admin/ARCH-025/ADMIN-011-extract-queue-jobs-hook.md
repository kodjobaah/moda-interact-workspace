---
id: ARCH-025-ADMIN-011
architecture_id: ARCH-025
title: Extract QueueMonitor jobs browsing hook
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: copilot
claimed_at: 2026-10-03T00:10:43Z
attempt: 1
depends_on:
  - ARCH-025-ADMIN-010
enables:
  - ARCH-025-ADMIN-012
created: 2026-10-02
updated: 2026-10-03
---

# Extract QueueMonitor jobs browsing hook

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract queue-job result/filter/page/recent-vs-full/loading/error/AbortController lifecycle into a dedicated hook while preserving the current asymmetric state transitions exactly.

## Context

The jobs browser currently combines request dependencies with queue switch, filter, direction, page, manual refresh and View all transitions. Those transitions intentionally do not all clear selection or set loading in the same way, so the hook must make the asymmetries explicit rather than normalising them.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-queue-jobs.ts
tests/unit/queue-monitor-jobs-state.test.ts
```

## Out of Scope

Selected-job detail hook, drawer/view extraction, ADMIN-009 client/type changes, accepted ADMIN-010 summary hook changes, server/API changes.

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

### R1 — jobs state ownership

The hook owns `queueJobs`, `showAllJobs`, page, shop filter, status filter, direction, jobs loading/error, refresh generation and jobs request AbortController. The shell continues to own `selectedQueueName` and supplies it as input.

### R2 — explicit transition operations

Expose bounded operations for queue selection preparation, manual refresh, Shop change, Status change, Direction change, View all and previous/next page. Preserve current behavior exactly: queue switch resets jobs/showAll/page/error and begins loading but retains filters; Shop/Status change begins loading, resets page and requests selection/detail clearing; Direction begins loading/resets page without immediate selection clearing; View all sets full mode/page 1 and requests selection/detail clearing but does not use the explicit prepare-loading transition; page moves do not use that explicit transition.

### R3 — request lifecycle

Use the accepted ADMIN-009 client with one AbortController per current dependency set. Abort stale work before replacement. Successful result replaces rows and requests selection/detail clearing. Non-abort failure sets `queue.jobsUnavailable` and clears rows. Loading is cleared only by the currently-owned controller.

### R4 — cross-hook compatibility port

Because selected-job state remains outside this hook until ADMIN-012, accept one narrow callback/port used only at the exact transitions where the monolith currently clears selected job/detail. Do not import a future detail hook or recreate detail state locally.

## Work Items

- [x] Move all jobs-browser state and request lifecycle to the hook.
- [x] Preserve every transition asymmetry through explicit operations.
- [x] Rewire shell/detail state through the narrow invalidation callback.
- [x] Add pure state-transition tests for queue switch, filters, direction, View all and pagination.

## Interfaces / Contracts

ADMIN-011 consumes accepted ADMIN-009 client/types and ADMIN-010 summary callback integration. Its state/actions become the accepted jobs-control contract for ADMIN-012/015.

## Dependencies

- `ARCH-025-ADMIN-010`

## Enables

- `ARCH-025-ADMIN-012`

## Acceptance Criteria

- [x] No jobs fetch/state implementation remains duplicated in the shell.
- [x] Filters, query values, limits, abort/error/loading behavior and selection-clearing asymmetries match the baseline.
- [x] Old rows remain eligible to stay visible during page/View all replacement exactly as today.
- [x] Later tasks can clear/select detail through the bounded callback/interface without changing jobs state internals.

## Validation

- [x] Frozen server/API/client-helper SHA-256 values all match the task's expected values.
- [x] The frozen server/API/helper/test diff is empty.
- [x] The architect-accepted ADMIN-009 QueueMonitor harness files are unchanged byte-for-byte.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-jobs-state.test.ts` passes: 6/6.

- [x] `npm run test:unit` completes with 254 passed and the two exact inherited `ARCH025-ADMIN-BUILDER-TEST-001` translation-workbook failures; no task regression.
- [ ] `npm test` completes with 235 tests: 222 passed and 13 failed. Nine failures exactly match the inherited `ARCH025-ADMIN-TEST-001` identifiers; four unchanged ADMIN-009 source-shape assertions fail because the required jobs state/request logic has moved out of `queue-monitor.tsx` into `use-queue-jobs.ts`.
- [x] Targeted ESLint passes for both changed production sources and the new unit test; the test file is ignored by default and passes when linted with `--no-ignore`.
- [x] `npm run build` succeeds, including TypeScript compilation. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review; implementation complete, with one test-contract conflict referred to the architect.

### Files Changed

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-jobs.ts`
- `tests/unit/queue-monitor-jobs-state.test.ts`

### Work Completed

- Extracted jobs results, filters, direction, recent/full mode, page, loading/error, refresh generation and request AbortController lifecycle into `useQueueJobs`.
- Rewired queue selection, refresh, filters, pagination and View all through explicit hook operations while keeping selected queue, detail state and drawer state in the shell.
- Preserved the transition-specific invalidation behavior and added six pure state reducer tests. Updated local imports to explicit `.ts` extensions to match native Node test resolution.

### Validation Results

- Focused jobs-state tests: 6 passed, 0 failed.
- Full unit suite: 254 passed, 2 failed. The exact inherited failures are `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order`, documented by `ARCH025-ADMIN-BUILDER-TEST-001` in accepted ADMIN-010 evidence.
- Full `npm test`: 235 tests, 222 passed, 13 failed. Nine failures exactly match the inherited `ARCH025-ADMIN-TEST-001` identifiers: `no Moda-owned span/metric creation exists in application code`, `accepts strict non-negative lifetime Free defaults`, `every RecoveryCreditPurchaseStatus has an ICU label and filter support`, `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups`, `Admin validates and consumes the published Shared ICU runtime`, `Admin canonical catalogue keys are independent and intentionally aligned`, `consumes the published shared release without a local declaration shim`, `identity, revocation, mutation, session, and route contracts are wired`, and `Tenant Directory KPIs are derived from durable business state`.
- Four additional failures are unchanged ADMIN-009 static source-shape assertions now incompatible with this extraction: `queue names switch diagnostics without resetting an open drawer` expects `setQueueJobs(null)` in the shell; `queue drawer uses the bounded Shop, Status, Direction filter contract` expects inline request fields; `queue drawer keeps the full browser paginated and state-safe` expects inline page setters; and `queue monitor renders a bounded four-state job summary without mutation actions` expects the request limit expression inline. Moving those implementations into the required hook is the task objective, while the task also forbids changing these accepted harness files. No duplicate/dead compatibility code was added.
- All nine frozen hashes matched; frozen source/API/helper/test diff was empty; accepted ADMIN-009 harness sources remained unchanged.
- Targeted ESLint passed for the shell, hook and new test (the test required `--no-ignore`). Production build passed. `git diff --check` passed. The initial test attempt was blocked by missing worktree dependencies; `npm ci` installed from the existing lockfile, and the build generated Prisma Client. No tracked dependency metadata changed.

### Deviations

- The four unchanged source-shape assertions prevent the required structural extraction from passing `npm test`. Architect direction is needed on whether to authorize updating the ADMIN-009 harness tests, amend their validation contract, or revise this task's extraction boundary. Until resolved, broad security acceptance remains incomplete.

### Assumptions

- No product behavior or security contract was intentionally changed. The source-shape test conflict is an incompatibility between this task's required ownership boundary and the frozen ADMIN-009 harness, not an implementation workaround request.

### Unresolved Issues

- Resolve whether the accepted ADMIN-009 QueueMonitor static tests may be updated for the ADMIN-011 hook boundary. Do not begin ADMIN-012 while this contract conflict remains unresolved.

### Architectural Concerns

The task simultaneously requires moving jobs state/request implementation out of `queue-monitor.tsx` and leaving accepted tests unchanged, although four of those tests assert that the moved implementation remains inline in `queue-monitor.tsx`. Architect review must resolve this validation-contract conflict before acceptance.

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
