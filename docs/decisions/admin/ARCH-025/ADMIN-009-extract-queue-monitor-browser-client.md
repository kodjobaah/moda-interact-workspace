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
attempt: 2
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

- [x] Introduce browser-only QueueMonitor response types.
- [x] Introduce bounded HTTP client functions and rewire the monolith without changing request lifecycle ownership yet.
- [x] Add focused pure/client tests.
- [x] Make the four source-based QueueMonitor test loaders extraction-safe without weakening assertions.
- [x] Prove frozen server/API sources and dedicated server tests remain byte-identical.

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

- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'src/lib/admin/queue-monitor.ts':'f2270a0c76992059793ce1a3184b4e424675d8ea0dc2a3bbef03a0fadd202486','src/app/api/admin/queues/route.ts':'f0eaed7214b6d57341f37a04afcc6636efa325358c0ea62321b09c086c6df408','src/app/api/admin/queues/jobs/route.ts':'fd6413d4afd37a4c46208d397f9bc5903a0766a651866ba414acedb1b95368a7','src/app/api/admin/queues/jobs/detail/route.ts':'c367a8e6ac3674f54df815ee05ecfe682f65e7e5f8eb0f2feeff80a05b298bab','tests/security/admin-queue-jobs.test.mjs':'3bfc3954b2938ea6f7028f2db51cae26e943ea5d8845e1d7cab2eb87b96bd6bc','tests/security/admin-queue-job-detail.test.mjs':'e567406ccace44955ef9ff43c3e5b138e19f4be92677f13fd1e47d47ec3011e0','tests/security/admin-failed-job-detail.test.mjs':'da8dccc08b3981c45f39ca39cd0d6a0a98121e4f8b283c0cccb32db39a20e195','tests/security/admin-failed-jobs.test.mjs':'fad750721202bd646b13c1aba6c37464e0698618e6707775265f8fdb0f281609','src/components/admin/queue-monitor-refresh.ts':'14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values.
- [x] `git diff -- src/lib/admin/queue-monitor.ts src/app/api/admin/queues/route.ts src/app/api/admin/queues/jobs/route.ts src/app/api/admin/queues/jobs/detail/route.ts src/components/admin/queue-monitor-refresh.ts tests/security/admin-queue-jobs.test.mjs tests/security/admin-queue-job-detail.test.mjs tests/security/admin-failed-job-detail.test.mjs tests/security/admin-failed-jobs.test.mjs` is empty.
- [x] For ADMIN-009 only, run `node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` with all existing test names/assertions retained. QueueMonitor-owned assertions pass; the two global Admin i18n failures are the exact inherited identifiers documented by `ARCH025-ADMIN-TEST-001` and reproduced at pre-task/current revisions.
- [x] `node --experimental-strip-types --test tests/unit/queue-monitor-client.test.ts` passes (Attempt 2 rerun: 3/3).

- [x] `npm run test:unit` passes without task-introduced regression; the two exact inherited failures are documented by `ARCH025-ADMIN-TEST-001` and were reproduced at the pre-task revision.
- [x] `npm test` passes without task-introduced regression; the nine exact inherited failures are documented by `ARCH025-ADMIN-TEST-001` and were reproduced at the pre-task revision.
- [x] targeted ESLint for every changed Admin source/test file passes (Attempt 1: zero errors; two hook-dependency warnings).
- [x] `npm run build` succeeds (Attempt 1; no source changes in Attempt 2).
- [x] `git diff --check` passes (Attempt 1 and Attempt 2 parent report).

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Attempt 2 completed as evidence-only rework. A1-R1 is satisfied by the same-revision comparison recorded below and baseline `ARCH025-ADMIN-TEST-001`; QueueMonitor-owned focused assertions pass, while only its two documented global Admin i18n failures remain red. A1-R2 prepared execution provenance is recorded below. No implementation source or test changes were made in Attempt 2. Returned to review for architect acceptance.

### Files Changed

Implementation commit `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1` (pushed to `task/ARCH-025-ADMIN-009`):

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/queue-monitor.client.ts`
- `src/components/admin/queue-monitor/queue-monitor.types.ts`
- `tests/security/admin-failed-job-detail-panel.test.mjs`
- `tests/security/admin-internationalization.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/unit/queue-monitor-client.test.ts`

### Work Completed

- Added browser-local QueueMonitor response types and a bounded client for the existing summary, jobs and detail endpoints; rewired the component while leaving request lifecycle ownership in place.
- Updated only source loaders in the four authorized security/i18n tests and added the focused client tests. No server/API source or dedicated server test was changed.
- Implementation branch is clean at `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1` and matches its origin task branch.
- Launcher preparation succeeded for attempt 1 with canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-009`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-009`, and task branch `task/ARCH-025-ADMIN-009` in both worktrees. The dedicated worktrees were used; the shared workspace and shared implementation checkout were not used for task edits, and no other task worktree was reused.
- The preparation packet's individual parent/implementation fast-forward and origin/main incorporation fields were not retained in the available session record. The implementation starting revision recorded for attribution was `b8da632a1fcaef7e364be1dc5cca40dfafde4703`. The prepared launcher's recursive submodule synchronization/initialization completed before handoff; its complete recorded submodule list was not retained.
- Attempt 2 followed the full prepared packet: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-009`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-009`; matching `task/ARCH-025-ADMIN-009` branches. Both worktrees were reused, not created. Parent task-branch fast-forward was `not-needed`, `origin/main` was `already-current`, and start HEAD was `1b3204eb242af3f22264d9ba296749d5ed4450f3`. Implementation task-branch fast-forward was `not-needed`, `origin/main` was `already-current`, and start HEAD was `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`.
- Launcher ran `git submodule sync --recursive` and `git submodule update --init --recursive` successfully; recursive submodule status was `ready`. The initialized `database` gitlink is `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Attempt 2 claim: from `ready`, attempt 1 to `in_progress`, attempt 2; executor `copilot`; claimed at `2026-10-02T21:34:30Z`; parent claim commit `7dc93bd9a19e265e1e882e0db6cba714bf1d21de`, committed and pushed. The shared workspace and shared implementation checkout were not used for implementation edits; no other task worktree was reused.
- No-drift validation rerun in Attempt 2: the client test passed 3/3; all nine frozen source/test hashes matched their required SHA-256 values, and the frozen-source/test `git diff` was empty. The prior same-revision comparison remains authoritative; broad suite archaeology was not repeated per Architect Review.

### Validation Results

Same-revision attribution comparison recorded 2026-10-02. Current task revision: `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`; starting baseline revision: `b8da632a1fcaef7e364be1dc5cca40dfafde4703`.

Current-task commands and retained summaries:

- `cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-009 && node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` — 27 passed, 2 failed. Underlying process exit code: **not retained**.
- `cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-009 && npm run test:unit` — 231 passed, 2 failed. Underlying process exit code: **not retained**.
- `cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-009 && npm test` — 226 passed, 9 failed. Underlying process exit code: **not retained**. The retained capture command redirected output to `/tmp/arch-025-admin-009-npm-test-current.log`, printed `npm test exit=%s`, then ended with `exit 0`; that log was subsequently removed, so the printed child exit code is unavailable. The capture wrapper's shell exit code was 0.

Baseline commands and retained summaries:

- `cd /tmp/moda-admin-ARCH-025-ADMIN-009-baseline.rdNGfx && node --test tests/security/admin-queue-monitor.test.mjs tests/security/admin-queue-details-drawer.test.mjs tests/security/admin-failed-job-detail-panel.test.mjs tests/security/admin-internationalization.test.mjs` — 27 passed, 2 failed. Underlying process exit code: **not retained**.
- `cd /tmp/moda-admin-ARCH-025-ADMIN-009-baseline.rdNGfx && npm run test:unit` — 228 passed, 2 failed. The capture wrapper printed `npm run test:unit exit=%s` from the child result and then explicitly returned shell exit code 0. The captured log was removed; the child process exit code is **not retained**.
- The valid baseline check for the nine named `npm test` failures was this filtered Node test run, not an unfiltered baseline `npm test`:

```sh
cd /tmp/moda-admin-ARCH-025-ADMIN-009-baseline.rdNGfx && node --test --test-name-pattern='no Moda-owned span/metric creation exists in application code|accepts strict non-negative lifetime Free defaults|every RecoveryCreditPurchaseStatus has an ICU label and filter support|purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups|Admin validates and consumes the published Shared ICU runtime|Admin canonical catalogue keys are independent and intentionally aligned|consumes the published shared release without a local declaration shim|identity, revocation, mutation, session, and route contracts are wired|Tenant Directory KPIs are derived from durable business state' tests/observability/shared-runtime-ownership.test.mjs tests/security/admin-billing-controls.test.mjs tests/security/admin-billing-pack-status.test.mjs tests/security/admin-internationalization.test.mjs tests/security/admin-merchant-support.test.mjs tests/security/admin-security-boundary.test.mjs tests/security/admin-tenant-business-kpis.test.mjs > /tmp/arch-025-admin-009-named-baseline.log 2>&1; result=$?; printf 'named baseline cases exit=%s\n' "$result"; rg -n '^✖|^test at |^ℹ tests|^ℹ pass|^ℹ fail|^ℹ skipped' /tmp/arch-025-admin-009-named-baseline.log; exit 0
```

The retained prior-session comparison summary reports 9 of 9 selected tests failing with the same assertion categories as the current revision. The wrapper explicitly returned shell exit code 0; the printed `result` value and detailed baseline log were removed and are **not retained**, so the underlying Node test exit code cannot be stated. Exact test names retained in the comparison are `no Moda-owned span/metric creation exists in application code`, `accepts strict non-negative lifetime Free defaults`, `every RecoveryCreditPurchaseStatus has an ICU label and filter support`, `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups`, `Admin validates and consumes the published Shared ICU runtime`, `Admin canonical catalogue keys are independent and intentionally aligned`, `consumes the published shared release without a local declaration shim`, `identity, revocation, mutation, session, and route contracts are wired`, and `Tenant Directory KPIs are derived from durable business state`.

The exact retained failures at the task revision were:

- Focused security/i18n: `Admin validates and consumes the published Shared ICU runtime` (actual `1.1.0`, expected `1.0.1`) and `Admin canonical catalogue keys are independent and intentionally aligned` (22 expected `billing.refund.*` keys absent).
- Unit: `rejects stale metadata, locale/header changes, and highlight identity changes` (`assert.ok(...)` false) and `returns all bounded validation issues in canonical order` (no `PLAN_HANDLE_MISMATCH` issue).
- `npm test`: `no Moda-owned span/metric creation exists in application code` (translation-workbook source matched `/\bsanitize/i`); `accepts strict non-negative lifetime Free defaults` (actual `accepted: null`, expected `accepted: 7`); `every RecoveryCreditPurchaseStatus has an ICU label and filter support` (missing `/Object\.values\(RecoveryCreditPurchaseStatus\)/`); `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups` (missing `/export function adminBillingPackStatusLabel/`); `Admin validates and consumes the published Shared ICU runtime` (actual `1.1.0`, expected `1.0.1`); `Admin canonical catalogue keys are independent and intentionally aligned` (catalogue key equality failure); `consumes the published shared release without a local declaration shim` (actual `1.1.0`, expected `1.0.1`); `identity, revocation, mutation, session, and route contracts are wired` (`assert.ok(...)` false); and `Tenant Directory KPIs are derived from durable business state` (missing `/type:\s*["']RECOVERY["']/`).

Same-revision comparison reports the same focused failures at `b8da632a1fcaef7e364be1dc5cca40dfafde4703`, the same two merchant-pricing unit failures, and all nine selected package-suite failures with the same assertion categories. This supports that the failures predate ADMIN-009, but does not make the required focused suite pass or waive acceptance. The named package-suite check was filtered to those nine cases; no claim is made that a full baseline `npm test` passed. Raw temporary logs and the disposable baseline snapshot have been removed. Exit codes not retained are explicitly recorded as unavailable above.

Attempt 1 implementation validation: focused client test 3/3; production build passed; targeted ESLint reported zero errors and two hook-dependency warnings; `git diff --check` passed; frozen hashes and frozen-source diffs passed. Attempt 2 reran the client test (3/3), all frozen hashes (all match), the frozen-source diff (empty), and report `git diff --check` (passed).

The prior same-environment comparison established that the two global i18n failures in the focused four-file command, two unit failures, and nine `npm test` failures have matching identities/reasons at the starting revision. Architect Review records these inherited identifiers as `ARCH025-ADMIN-TEST-001`; no broad baseline archaeology was repeated in Attempt 2. The baseline-aware focused criterion is met because all QueueMonitor-owned assertions pass and only the two specifically permitted global i18n assertions remain red. No implementation/test source changed.

### Deviations

None

### Assumptions

None

### Unresolved Issues

The repository retains the documented `ARCH025-ADMIN-TEST-001` Admin baseline failures. They are unchanged from the pre-task revision and do not include QueueMonitor-owned focused assertions.

### Architectural Concerns

None identified in the bounded implementation. Validation disposition remains with `moda_architect`.

### Final Branch State

- Implementation branch `task/ARCH-025-ADMIN-009`: HEAD `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`, equal to its task remote and clean; Attempt 2 made no implementation commit.
- Parent task branch before report publication: claim HEAD `7dc93bd9a19e265e1e882e0db6cba714bf1d21de`, equal to its task remote and clean apart from this report edit. Final report commit and post-push refs will be verified after publication.

## Architect Review

### Review Status

Changes Requested — Attempt 2.

### Review Notes

Attempt 2 satisfies the substantive evidence-only correction contract from Attempt 1:
the implementation remains unchanged at
`eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`; `ARCH025-ADMIN-TEST-001` is cited for
the inherited red assertions; the Attempt 2 launcher/worktree/synchronization/
submodule packet is durably recorded; the client no-drift rerun is 3/3; all frozen
hashes match; and the frozen-source diff is empty.

GitHub independently confirms the current remote task heads are:

```text
workspace task/ARCH-025-ADMIN-009
  9df2fa00ae8ac222f5c351d2d6ec045312d0e14b

Admin implementation task/ARCH-025-ADMIN-009
  eda069b4b165f0b6cbb0c3fa3ac821aef32662e1
```

No implementation/test correction or validation rerun is requested.

Acceptance is withheld only because two report-owned items from A1-R1 remain
unreconciled in the authoritative task file:

1. all five `## Acceptance Criteria` checkboxes are still unchecked even though the
   report evidence supports them;
2. `### Final Branch State` still says the final parent report commit/post-push refs
   "will be verified after publication" instead of recording the already-published
   parent commit `9df2fa00ae8ac222f5c351d2d6ec045312d0e14b`, local==remote and final clean state.

Those fields belong to the implementing agent's durable task report/checklist, so the
architect does not check or rewrite them on the agent's behalf.

#### A2-R1 — final task-record reconciliation only

Return the same task to Ready, Attempt 2 retained and claim clear. The next launcher
claim must create Attempt 3 exactly once.

Attempt 3 must make **no implementation or test source changes** unless repository
state has unexpectedly drifted. It must only:

1. check all five Acceptance Criteria truthfully;
2. update `### Final Branch State` to record:
   - implementation HEAD `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`,
     equal to its remote and clean;
   - final parent report commit
     `9df2fa00ae8ac222f5c351d2d6ec045312d0e14b`,
     equal to its remote and clean;
3. record the Attempt 3 prepared claim/provenance generated by the launcher;
4. return to `review` and stop.

No repeat of client tests, frozen hashes, focused/broad baseline comparison, lint or
build is required when no source/dependency/environment state changes. A final
`git diff --check` on the report-only change is sufficient.

The detailed Attempt 1 implementation review below remains valid historical evidence.

The ADMIN-009 implementation is accepted in substance. Architect inspection of
submitted Admin commit `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1` against
starting revision `b8da632a1fcaef7e364be1dc5cca40dfafde4703` found exactly the
eight task-authorised files changed and no server/API/frozen regression surface.

The browser-local response mirrors match the protected QueueMonitor API shapes, the
bounded client preserves the three exact endpoint paths, query names/order,
`cache: "no-store"`, AbortSignal forwarding and detail HTTP status distinction, and
the public `QueueMonitor` shell retains request-lifecycle ownership. The four
authorised source-based tests were changed only so QueueMonitor assertions read the
public shell plus sorted direct `.ts`/`.tsx` modules in the bounded
`src/components/admin/queue-monitor/` directory.

The task was blocked only because the four-file focused command returned 27/29 and
the broader suites were red. Same-revision comparison proves those failures pre-date
ADMIN-009. The two failures in the focused command are global Admin
internationalisation assertions co-located in `admin-internationalization.test.mjs`;
they are not QueueMonitor assertions:

```text
Admin validates and consumes the published Shared ICU runtime
  actual Shared 1.1.0 versus stale expected 1.0.1

Admin canonical catalogue keys are independent and intentionally aligned
  pre-existing catalogue/required-key mismatch
```

All QueueMonitor-specific assertions in that file and the three dedicated QueueMonitor
security/detail files pass. The same two global failures reproduce at
`b8da632a1fcaef7e364be1dc5cca40dfafde4703`.

The two `npm run test:unit` failures and all nine submitted `npm test` failing
identifiers were likewise reproduced at the starting revision with the same assertion
categories. That establishes no ADMIN-009 task-introduced regression. The architect
records this state durably as `ARCH025-ADMIN-TEST-001`; this baseline does not permit
weakening or skipping QueueMonitor-owned assertions.

No implementation or test source correction is requested.

#### A1-R1 — evidence-only lifecycle reconciliation

Return the same task to Ready, Attempt 1 retained and claim clear. The next normal
launcher claim must create Attempt 2 exactly once.

Attempt 2 must not change ADMIN-009 implementation/test files unless new evidence
contradicts this review. It must:

1. record the complete prepared Attempt 2 launcher packet, including canonical
   workspace, dedicated parent/Admin worktrees, synchronization identities, recursive
   submodule/database-gitlink evidence and claim identity;
2. reference `ARCH025-ADMIN-TEST-001` for the inherited red assertions;
3. reconcile Work Items, Acceptance Criteria and Validation checkboxes truthfully
   under the amended baseline-aware focused validation;
4. preserve implementation
   `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`;
5. record final parent/implementation local-equals-remote and clean-worktree evidence;
6. return to `review` and stop.

No repeat of broad baseline archaeology is required without an intervening source,
dependency or environment change. A short no-drift rerun of the frozen hashes and
3-test client suite is sufficient for the evidence-only retry.

### Reviewed Files

- `src/components/admin/queue-monitor.tsx`
- `src/components/admin/queue-monitor/queue-monitor.client.ts`
- `src/components/admin/queue-monitor/queue-monitor.types.ts`
- `tests/unit/queue-monitor-client.test.ts`
- `tests/security/admin-queue-monitor.test.mjs`
- `tests/security/admin-queue-details-drawer.test.mjs`
- `tests/security/admin-failed-job-detail-panel.test.mjs`
- `tests/security/admin-internationalization.test.mjs`
- frozen QueueMonitor server/API sources and dedicated server tests
- this task Completion Report
- ARCH-025 parent architecture and downstream ADMIN-010..015 contracts

### Validation Reviewed

- Git commit identity: `eda069b4b165f0b6cbb0c3fa3ac821aef32662e1`
  has parent `b8da632a1fcaef7e364be1dc5cca40dfafde4703` and changes exactly
  the eight authorised ADMIN-009 files.
- Frozen QueueMonitor server/API source and dedicated-test SHA-256 values:
  independently reproduced, all exact.
- `node --experimental-strip-types --test tests/unit/queue-monitor-client.test.ts`:
  independently rerun against the uploaded snapshot, 3/3 passed.
- Submitted focused source/security/i18n command: 27/29; both failures proven
  inherited/global and recorded in `ARCH025-ADMIN-TEST-001`.
- Submitted `npm run test:unit`: two failures; both reproduced at the starting
  revision.
- Submitted `npm test`: nine failing identifiers; all nine reproduced at the
  starting revision with the same assertion categories.
- Submitted production build, targeted ESLint and `git diff --check`: passed as
  recorded; ESLint warnings are non-error hook-dependency warnings.

### Architecture Conformance

Conformant in implementation. ADMIN-009 establishes the required browser-local
contract/client boundary and extraction-safe QueueMonitor source harness without
changing server/API/runtime behaviour. The former validation block is reclassified as
documented inherited Admin baseline debt, not an ADMIN-009 defect.

### Follow-up

Reclaim this same task through `/moda-task ARCH-025-ADMIN-009` for a final report-only
Attempt 3. Do not start ADMIN-010 until ADMIN-009 is architect-accepted Complete.
No source/test change or broad validation rerun is requested.
