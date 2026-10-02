---
id: ARCH-025-ADMIN-010
architecture_id: ARCH-025
title: Extract QueueMonitor summary polling hook
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
attempt: 1
depends_on:
  - ARCH-025-ADMIN-009
enables:
  - ARCH-025-ADMIN-011
created: 2026-10-02
updated: 2026-10-02
---

# Extract QueueMonitor summary polling hook

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract queue-summary snapshot/loading/error/refresh preference and single-flight polling lifecycle into a dedicated hook behind the accepted ADMIN-009 client boundary.

## Context

Summary refresh has distinct semantics from jobs/detail reads: immediate post-mount refresh, persisted interval, single-flight admission, last-good-snapshot retention, abort-safe errors and a successful-refresh callback that currently refreshes jobs when a queue is open.

## Scope

Authorised implementation surface:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-queue-monitor-summary.ts
tests/unit/queue-monitor-summary.test.ts
```

## Out of Scope

Jobs/detail/drawer/view extraction; changes to `queue-monitor.client.ts`, response types, refresh-option helper, accepted ADMIN-009 security loaders or server/API code.

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

### R1 — hook ownership

The hook owns `refreshMs`, summary `snapshot`, summary `error`, summary `loading`, summary request AbortController and single-flight admission. It exposes the accepted refresh selection plus a manual `refresh()` operation and accepts one bounded callback invoked only after a successful new snapshot has been accepted so the shell can preserve the current "selected queue => refresh jobs" coupling.

### R2 — exact polling lifecycle

Preserve mount `setTimeout(..., 0)`, unmount abort, localStorage write on refresh-value changes, `refreshMs === 0` meaning no interval, one interval otherwise, and the current no-overlap rule. Do not queue a second refresh behind an in-flight one.

### R3 — error/convergence semantics

Abort does not set an error. Non-abort failures set `queue.dataUnavailable` but retain the previous successful snapshot. Success replaces snapshot and clears the error. Loading is cleared exactly when the current admitted request finishes.

## Work Items

- [x] Move summary state/request/polling lifecycle into the hook.
- [x] Rewire QueueMonitor without changing selected-queue/jobs behaviour.
- [x] Add focused tests for pure/request-state helpers used to implement single-flight/abort/convergence semantics without adding a React test framework.

## Interfaces / Contracts

ADMIN-010 consumes ADMIN-009 `queue-monitor.client.ts` and existing `queue-monitor-refresh.ts`. The hook interface becomes the accepted summary-control contract for later QueueMonitor tasks.

## Dependencies

- `ARCH-025-ADMIN-009`

## Enables

- `ARCH-025-ADMIN-011`

## Acceptance Criteria

- [x] No summary fetch implementation remains duplicated in `queue-monitor.tsx`.
- [x] Single-flight, immediate load, paused polling, preference persistence, abort and last-good-snapshot semantics are preserved.
- [x] Successful summary refresh still triggers the shell callback used to refresh jobs for an open queue.
- [x] Accepted ADMIN-009 browser client/types/security harness remain unchanged.

## Validation

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [x] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [x] The architect-accepted ADMIN-009 versions of `tests/security/admin-queue-monitor.test.mjs`, `tests/security/admin-queue-details-drawer.test.mjs`, `tests/security/admin-failed-job-detail-panel.test.mjs` and `tests/security/admin-internationalization.test.mjs` are unchanged.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-summary.test.ts` passes for the pure/request-state helpers introduced by this task.

- [x] `npm run test:unit` passes without task-introduced regression.
- [ ] `npm test` completes without task-introduced regression. If the monolithic Node test runner is interrupted again before a terminal result, deterministic execution of the complete `tests/observability/*.test.mjs` + `tests/security/*.test.mjs` file set is an accepted equivalent only when every matched file is executed and every failure is either fixed or an exact unchanged `ARCH025-ADMIN-TEST-001` failure.
- [x] targeted ESLint for every changed Admin source/test file passes.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-monitor-summary.ts`
- `tests/unit/queue-monitor-summary.test.ts`

### Work Completed

- Extracted summary refresh preference, snapshot/error/loading state, AbortController ownership, single-flight admission, immediate mount refresh, interval/pause lifecycle, localStorage persistence, abort-safe error handling and last-good-snapshot convergence into `useQueueMonitorSummary`.
- Kept the shell callback boundary: an accepted summary snapshot requests a jobs refresh only when a queue is selected. Queue selection, filters, jobs requests and drawer behavior remain in the existing shell.
- Added pure request-gate, abort classification and reducer tests; no React/browser test framework was added.
- Implementation commit `0b3b540873b4ab59098d95ea3efb5088b1e16fbf` was pushed to `origin/task/ARCH-025-ADMIN-010`.

### Validation Results

- Focused summary test: 3 passed, 0 failed.
- Accepted QueueMonitor/drawer/detail/internationalization harness: 27 passed, 2 failed. The two failures are the existing ADMIN baseline ICU runtime/catalogue expectations; all QueueMonitor, drawer and detail assertions passed.
- Full unit suite: 248 passed, 2 failed. The exact failures are `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order`, both documented by `ARCH025-ADMIN-BUILDER-TEST-001`; no new failure appeared.
- Full `npm test`: baseline failures were observed in the already documented observability, billing-pack status, ICU catalogue, shared-release, security-boundary and tenant-KPI contracts. QueueMonitor-specific assertions passed. A later repeat was interrupted by Node's test runner before completion and is not counted as a separate result.
- All required frozen hashes matched; frozen source/API/helper/test diff was empty; accepted ADMIN-009 queue harness files were unchanged.
- Targeted ESLint, editor diagnostics and `git diff --check` passed.
- `npm run build` passed. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- Launcher preparation claimed Attempt 1 at `2026-10-02T22:23:49Z` with executor `copilot`; claim commit `72b8b2324cab98efeff8aa429ce830bde1886080` was committed and pushed. Dependency gate passed for `ARCH-025-ADMIN-009` (`complete`).
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-010` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-010` were separately created on `task/ARCH-025-ADMIN-010`. Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent and implementation start synchronization reported remote task-branch fast-forward `not-needed` and `origin/main` `already-current`. Recursive submodule sync/update passed; `database` was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`. Shared/default checkouts and other task worktrees were not used or mutated.

### Deviations

- The broad Admin suites retain the exact baseline failures described above; no unrelated baseline behavior was changed.

### Assumptions

- Summary helper tests are valid under the task's Node test command without introducing React test infrastructure.

### Unresolved Issues

- The existing external `origin/main` upstream mapping for the implementation worktree does not match the task branch. The implementation commit was explicitly pushed only to `origin/task/ARCH-025-ADMIN-010`; no main ref was changed.

### Architectural Concerns

- None within the bounded ADMIN-010 scope.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The ADMIN-010 implementation is accepted in substance. No hook, shell, client, type,
security-test or frozen-source correction is requested.

Architect inspection of implementation
`0b3b540873b4ab59098d95ea3efb5088b1e16fbf` found exactly the three
task-authorised files changed:

```text
src/components/admin/queue-monitor.tsx
src/components/admin/queue-monitor/use-queue-monitor-summary.ts
tests/unit/queue-monitor-summary.test.ts
```

The implementation parent `a0f7e6c7ffa3ca094dc5bb8e64eaa11f9629df89` is one
commit ahead of accepted ADMIN-009 integration head
`b09d421d4c18484c33fd70d6929c50bc43b6afcd` with **no file delta**, so the
accepted ADMIN-009 client/types/security/frozen boundary is the functional base.

The extraction preserves the required ownership and lifecycle:

- the hook owns refresh preference, snapshot/error/loading state, summary
  AbortController and single-flight admission;
- `fetchQueueMonitorSnapshot()` remains the accepted ADMIN-009 client boundary;
- initial `setTimeout(..., 0)`, localStorage persistence, pause-at-zero and interval
  lifecycle remain explicit;
- non-abort failures retain the last successful snapshot and set the bounded
  unavailable error;
- aborts do not surface a data error;
- success replaces the snapshot and clears the prior error;
- the shell retains the selected-queue callback and all jobs/detail/drawer state;
- no summary fetch implementation remains duplicated in `queue-monitor.tsx`;
- no accepted ADMIN-009 source/security loader, client/type file, frozen server/API
  source, frozen server test, package manifest or lockfile changed.

The focused summary proof is 3/3 as submitted. The four-file QueueMonitor harness
reported 27/29 with only the two exact inherited global ICU/catalogue failures from
`ARCH025-ADMIN-TEST-001`; QueueMonitor/drawer/detail assertions were green. The unit
suite completed with 248 passes and the two exact inherited
`ARCH025-ADMIN-BUILDER-TEST-001` translation failures. All nine frozen QueueMonitor
hashes independently match in the uploaded snapshot.

Acceptance is withheld for two evidence/repository-state items only.

#### A1-R1 — complete the broad security/observability coverage

The authoritative Validation checklist currently marks `npm test` complete, but the
Completion Report and handoff explicitly state that the broad rerun was interrupted
and no terminal count is claimed. That is not sufficient evidence for the requirement
that the task introduce no broad security/observability regression.

Attempt 2 must produce **complete coverage** of the script's file set:

```text
tests/observability/*.test.mjs
tests/security/*.test.mjs
```

Preferred evidence is one `npm test` run to terminal completion. If the monolithic
Node runner is interrupted again for environment/tooling reasons, run the exact
expanded file set deterministically (individually or in bounded batches), record
every file executed and its exit/result, and prove that every remaining failure is
either fixed or an exact unchanged `ARCH025-ADMIN-TEST-001` identifier/reason. No
matched file may be omitted.

Do not modify unrelated source/tests merely to make inherited failures green. If any
new or worsened failure appears, investigate and correct only an ADMIN-010 regression
before resubmission.

#### A1-R2 — align implementation branch upstream with its task remote

The implementation HEAD is correctly pushed to
`origin/task/ARCH-025-ADMIN-010`, but the report records that the local task branch's
configured upstream still points to `origin/main`.

Attempt 2 must correct repository tracking without changing source:

```bash
git branch --set-upstream-to=origin/task/ARCH-025-ADMIN-010 task/ARCH-025-ADMIN-010
```

and record:

```text
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git rev-parse HEAD
git rev-parse origin/task/ARCH-025-ADMIN-010
git status --short
```

The expected upstream is `origin/task/ARCH-025-ADMIN-010`, local HEAD must equal the
task remote, and the implementation worktree must be clean.

No source/test implementation change is requested merely for A1-R1/A1-R2. If the
launcher incorporates new source/dependency state before Attempt 2, record that drift
and rerun any validation materially affected by it.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/use-queue-monitor-summary.ts`
- `tests/unit/queue-monitor-summary.test.ts`
- accepted ADMIN-009 `queue-monitor.client.ts` and `queue-monitor.types.ts`
- accepted ADMIN-009 extraction-safe security/i18n harness
- frozen QueueMonitor server/API/helper sources and dedicated server tests
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-011 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `0b3b540873b4ab59098d95ea3efb5088b1e16fbf`: exactly three authorised files.
- GitHub comparison accepted ADMIN-009 integration
  `b09d421d4c18484c33fd70d6929c50bc43b6afcd` ->
  ADMIN-010 prepared base `a0f7e6c7ffa3ca094dc5bb8e64eaa11f9629df89`:
  one commit, zero file delta.
- All nine required frozen QueueMonitor SHA-256 values independently reproduced from
  the uploaded snapshot.
- Submitted focused summary helper tests: 3/3 passed.
- Submitted QueueMonitor source/security/i18n harness: 27 passed / 2 inherited global
  i18n failures; QueueMonitor-owned assertions passed.
- Submitted full unit suite: 248 passed / 2 exact inherited builder-translation
  failures.
- Submitted targeted ESLint, diagnostics, production build and `git diff --check`:
  passed as recorded.
- Broad `npm test`: incomplete terminal evidence; A1-R1 required.
- GitHub confirms implementation task ref
  `0b3b540873b4ab59098d95ea3efb5088b1e16fbf` and parent task ref
  `5ecfb10c0fae71dc3e2ab30b4fecd2c5371e6e90`.

### Architecture Conformance

Conformant in implementation. ADMIN-010 establishes the intended summary-control hook
behind the accepted ADMIN-009 client boundary without moving jobs/detail/drawer
ownership or changing protected API/server behaviour. Acceptance is pending only
complete broad-suite evidence and deterministic task-branch upstream alignment.

### Follow-up

Return this same task to Ready, Attempt 1 retained and claim clear. Reclaim through
`/moda-task ARCH-025-ADMIN-010`, which must create Attempt 2 exactly once.

Attempt 2 is evidence/repository-state work unless A1-R1 reveals a genuine regression.
Do not begin ADMIN-011 until ADMIN-010 is architect-accepted Complete.
