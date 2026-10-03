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
claimed_at: 2026-10-03T01:03:48Z
attempt: 2
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

# Architect-authorised Attempt-2 assertion reconciliation only
tests/security/admin-queue-monitor.test.mjs
tests/security/admin-queue-details-drawer.test.mjs
```

## Out of Scope

Selected-job detail hook, drawer/view extraction, ADMIN-009 client/type changes, accepted ADMIN-010 summary hook changes, server/API changes. The ADMIN-009 source-loader mechanics, test names, read-only/security/i18n assertions, `admin-failed-job-detail-panel.test.mjs` and `admin-internationalization.test.mjs` remain out of scope; Attempt 2 may change only the stale jobs source-shape assertions identified by the Architect Review in the two explicitly authorised test files.

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

### R5 — extraction-safe source assertions after jobs ownership moves

ADMIN-009 established the bounded source loader, but four assertions in `admin-queue-monitor.test.mjs` / `admin-queue-details-drawer.test.mjs` still encode the pre-extraction inline `useState`/request shape. ADMIN-011 Attempt 2 is authorised to update only those stale source-shape expectations so they assert the accepted `useQueueJobs` reducer/actions/request boundary while preserving the same behavioural/security contract.

Do not change either loader, any test name, any read-only/mutation prohibition, any i18n/catalogue assertion, or any unrelated QueueMonitor assertion. Do not modify `admin-failed-job-detail-panel.test.mjs` or `admin-internationalization.test.mjs`.

## Work Items

- [x] Move all jobs-browser state and request lifecycle to the hook.
- [x] Preserve every transition asymmetry through explicit operations.
- [x] Rewire shell/detail state through the narrow invalidation callback.
- [x] Add pure state-transition tests for queue switch, filters, direction, View all and pagination.
- [x] Reconcile only the four stale ADMIN-009 jobs source-shape assertions to the accepted hook/reducer boundary without weakening behaviour/security assertions.

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
- [x] The two architect-authorised harness files retain their loader/test names/security contract and assert jobs ownership through `useQueueJobs` rather than the retired inline setters/request block.

## Validation

- [x] Frozen server/API/client-helper SHA-256 values all match the task's expected values.
- [x] The frozen server/API/helper/test diff is empty.
- [x] The ADMIN-009 loader mechanics and all non-authorised assertions remain unchanged. Only the stale jobs source-shape assertions in `tests/security/admin-queue-monitor.test.mjs` and `tests/security/admin-queue-details-drawer.test.mjs` changed under R5; `admin-failed-job-detail-panel.test.mjs` and `admin-internationalization.test.mjs` remain byte-identical to their accepted ADMIN-009 versions.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-jobs-state.test.ts` passes: 6/6.

- [x] `npm run test:unit` completes with 254 passed and the two exact inherited `ARCH025-ADMIN-BUILDER-TEST-001` translation-workbook failures; no task regression.
- [x] After the R5 harness correction, run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` and `npm test`. All QueueMonitor-owned assertions pass; only exact unchanged `ARCH025-ADMIN-TEST-001` failures remain in the broad suite.
- [x] Targeted ESLint passes for both changed production sources and the new unit test; the test file is ignored by default and passes when linted with `--no-ignore`.
- [x] `npm run build` succeeds, including TypeScript compilation. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review; Attempt 2 harness reconciliation and required validation are complete. Implementation sources remain unchanged from the architect-reviewed submission.

### Files Changed

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-jobs.ts`
- `tests/unit/queue-monitor-jobs-state.test.ts`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`

### Work Completed

- Extracted jobs results, filters, direction, recent/full mode, page, loading/error, refresh generation and request AbortController lifecycle into `useQueueJobs`.
- Rewired queue selection, refresh, filters, pagination and View all through explicit hook operations while keeping selected queue, detail state and drawer state in the shell.
- Preserved the transition-specific invalidation behavior and added six pure state reducer tests. Updated local imports to explicit `.ts` extensions to match native Node test resolution.
- Reconciled exactly four architect-authorized stale source-shape assertions to check shell action wiring, reducer transitions, the selection invalidation port and hook request query construction. Preserved both source loaders, every test name, and all unrelated UI/security/i18n assertions.

### Validation Results

- Focused jobs-state tests: 6 passed, 0 failed.
- Focused four-file QueueMonitor/security harness: 29 tests, 27 passed, 2 failed. All QueueMonitor-owned assertions passed. The two failures are the unchanged `Admin validates and consumes the published Shared ICU runtime` and `Admin canonical catalogue keys are independent and intentionally aligned` baseline failures.
- Full `npm test`: 235 tests, 226 passed, 9 failed. The exact inherited `ARCH025-ADMIN-TEST-001` failures are `no Moda-owned span/metric creation exists in application code`, `accepts strict non-negative lifetime Free defaults`, `every RecoveryCreditPurchaseStatus has an ICU label and filter support`, `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups`, `Admin validates and consumes the published Shared ICU runtime`, `Admin canonical catalogue keys are independent and intentionally aligned`, `consumes the published shared release without a local declaration shim`, `identity, revocation, mutation, session, and route contracts are wired`, and `Tenant Directory KPIs are derived from durable business state`. No QueueMonitor-owned assertion failed.
- Full unit suite: 254 passed, 2 failed. The exact inherited failures are `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order`, documented by `ARCH025-ADMIN-BUILDER-TEST-001` in accepted ADMIN-010 evidence.
- All nine frozen hashes matched, including the queue refresh helper; the frozen source/API/helper/test diff is empty. The two amended ADMIN-011 harnesses preserve the ADMIN-009 loader mechanics, and `admin-failed-job-detail-panel.test.mjs` plus `admin-internationalization.test.mjs` remain unchanged.
- Targeted ESLint passed for both changed harness files with `--no-ignore`. Production build passed, including TypeScript compilation; existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain. `git diff --check` passed. No tracked dependency metadata changed.

### Deviations

- The full test command retains the nine exact `ARCH025-ADMIN-TEST-001` inherited failures listed above. The focused harness also includes two of those unchanged internationalization failures; all QueueMonitor-owned cases pass.

### Assumptions

- No product behavior or security contract was intentionally changed. The source-shape test conflict is an incompatibility between this task's required ownership boundary and the frozen ADMIN-009 harness, not an implementation workaround request.

### Unresolved Issues

- No ADMIN-011 implementation or QueueMonitor harness issue remains unresolved. The nine inherited broad-suite failures remain tracked under `ARCH025-ADMIN-TEST-001`.

### Architectural Concerns

The architect-authorized Attempt-2 harness changes now check the extracted hook ownership boundary without changing product behavior, security assertions, or the accepted source-loader mechanics.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The ADMIN-011 implementation is accepted in substance. The jobs hook extraction should
**not** be reverted and no dead compatibility code should be added to satisfy the
pre-extraction source shape.

Architect inspection of implementation
`1a3c75744f20b90911a49659b449db4a3136b7d2` found exactly the three original
task-authorised implementation/test files changed. The hook owns the required jobs
state/request lifecycle, and old-vs-new inspection confirms the intentional
asymmetries are preserved:

- queue switch clears rows/recent mode/page/error, starts loading, retains filters,
  preserves an already-open drawer width, aborts stale jobs/detail work and clears
  selected detail;
- manual refresh clears jobs error, starts loading and advances request generation
  without clearing current rows;
- Shop/Status changes start loading, clear jobs error, reset page, retain rows/mode and
  invalidate selected detail;
- Direction starts loading, clears jobs error and resets page without immediate detail
  invalidation;
- View all switches to full mode/page 1 and invalidates selected detail without the
  explicit prepare-loading transition;
- previous/next page preserve rows/loading/error while changing page;
- successful replacement clears selected detail through the narrow callback;
- non-abort failure clears rows and sets `queue.jobsUnavailable`;
- stale requests are aborted and only the currently-owned controller clears loading.

All nine frozen QueueMonitor hashes independently reproduce exactly from the uploaded
snapshot. The focused jobs-state tests are 6/6 as submitted. GitHub independently
confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-011
  1a3c75744f20b90911a49659b449db4a3136b7d2

workspace task/ARCH-025-ADMIN-011
  db3a0e79afcff0f1e7deffe626b33009e2dab14b
```

The four additional broad-suite failures are not product/security regressions. They
are stale source-shape assertions in the accepted ADMIN-009 harness. The loader already
reads the shell plus direct QueueMonitor modules, but these assertions still require
the pre-ADMIN-011 inline implementation (`setQueueJobs`, inline query fields/limit,
`setShowAllJobs`, and `setQueueJobPage` setters).

The architecture itself created the contradiction: ADMIN-011 requires jobs ownership
to move into `use-queue-jobs.ts`, while the prior coordination rule froze assertions
that require that ownership to remain inline. The architect resolves that conflict in
favour of the explicit ADMIN-011 ownership boundary.

#### A1-R1 — update only the stale jobs source-shape assertions

**Test-harness correction required. Implementation source is accepted as submitted.**

Attempt 2 is authorised to modify only:

```text
tests/security/admin-queue-monitor.test.mjs
tests/security/admin-queue-details-drawer.test.mjs
```

The existing ADMIN-009 `readQueueMonitorSources()` loader must remain unchanged, as
must every test name and every unrelated read-only/security/i18n/catalogue assertion.

Update the four failing tests so they assert the new accepted ownership rather than
the retired inline setters:

1. `queue names switch diagnostics without resetting an open drawer`
   - keep the drawer-width / queue-selection shell assertions;
   - assert the shell delegates jobs reset to `prepareForQueueSelection()`;
   - assert the bounded hook `queue-selected` transition clears rows/recent mode/page/
     error and starts loading, and the `queue-selection` invalidation port clears
     selected detail.

2. `queue drawer uses the bounded Shop, Status, Direction filter contract`
   - assert the shell wires `changeShop`, `changeStatus`, `changeDirection`, `viewAll`;
   - assert `useQueueJobs` constructs `status/shop/page/limit/direction` from its
     reducer state (`state.showAllJobs ? "10" : "5"`);
   - preserve all existing UI label, pagination, orphan/unresolved and mutation
     prohibitions.

3. `queue drawer keeps the full browser paginated and state-safe`
   - replace direct `setQueueJobPage` shape requirements with the explicit
     `page-previous`, `page-next`, and `view-all` reducer/action contract plus shell
     wiring to `previousPage`, `nextPage`, and `viewAll`;
   - preserve the existing `knownTotal`, `scanTruncated`, back-to-detail and
     state-safety assertions.

4. `queue monitor renders a bounded four-state job summary without mutation actions`
   - update only the stale inline limit expectation to the accepted jobs-hook request
     shape (`state.showAllJobs ? "10" : "5"`), preserving all route/query/status/
     catalogue/read-only assertions.

Do **not**:
- weaken or remove a test;
- rename tests;
- change loader scope/order;
- add a new baseline for these four failures;
- modify `admin-failed-job-detail-panel.test.mjs` or
  `admin-internationalization.test.mjs`;
- change ADMIN-011 implementation merely to satisfy source regexes.

After the two test files are corrected, run:

```bash
node --test   tests/security/admin-queue-monitor.test.mjs   tests/security/admin-queue-details-drawer.test.mjs   tests/security/admin-failed-job-detail-panel.test.mjs   tests/security/admin-internationalization.test.mjs

npm test
```

All QueueMonitor-owned assertions must pass. The broad suite may retain only the exact
unchanged `ARCH025-ADMIN-TEST-001` failures. Rerun the 6-test jobs-state suite, frozen
hash check, targeted lint, production build and `git diff --check` because test source
changes are being made.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-jobs.ts`
- `tests/unit/queue-monitor-jobs-state.test.ts`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`
- accepted ADMIN-009 client/types and extraction-safe loader mechanics
- accepted ADMIN-010 summary hook boundary
- frozen QueueMonitor server/API/helper sources and dedicated server tests
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-012..015 downstream validation contracts

### Validation Reviewed

- GitHub implementation commit
  `1a3c75744f20b90911a49659b449db4a3136b7d2`: exactly three submitted task files.
- Nine frozen QueueMonitor SHA-256 values independently reproduced: all exact.
- Submitted focused jobs-state tests: 6/6 passed.
- Submitted unit suite: 254 passed / two exact inherited builder-translation failures.
- Submitted broad suite: 235 tests / 222 passed / 13 failed; nine exact
  `ARCH025-ADMIN-TEST-001` failures plus four stale source-shape assertions.
- Independently reran `admin-queue-details-drawer.test.mjs` from the uploaded snapshot:
  the same three jobs source-shape tests fail while the two non-jobs drawer tests pass.
- Direct source review confirms the fourth failure in
  `admin-queue-monitor.test.mjs` is the stale inline limit regex.
- Submitted targeted lint, production build and `git diff --check`: passed as recorded.

### Architecture Conformance

Conformant in implementation. The four extra failures arise from a validation-contract
contradiction, not from changed QueueMonitor behaviour. The architect amends the
harness freeze narrowly: ADMIN-011 Attempt 2 may reconcile only the identified jobs
source-shape assertions; after acceptance, those two updated test files become frozen
for ADMIN-012..015 alongside the unchanged ADMIN-009 harness files.

### Follow-up

Return this same task to Ready, Attempt 1 retained and claim clear. Reclaim through
`/moda-task ARCH-025-ADMIN-011`, which must create Attempt 2 exactly once.

Attempt 2 is test-harness reconciliation plus revalidation; keep implementation
`1a3c75744f20b90911a49659b449db4a3136b7d2` unchanged unless validation exposes a
genuine runtime regression. Do not begin ADMIN-012 until ADMIN-011 is
architect-accepted Complete.
