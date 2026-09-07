---
id: ARCH-006-BACKGROUND-007
architecture_id: ARCH-006
title: Add self-healing translation reconciliation and worker runtime
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 50
executor: copilot
claimed_at: 2026-09-06T19:39:04Z
attempt: 3
depends_on:
  - ARCH-006-BACKGROUND-006
enables:
  - ARCH-006-GATEWAY-001
  - ARCH-006-ADMIN-002
  - ARCH-006-ADMIN-004
  - ARCH-006-SHOPIFY-003
  - ARCH-006-SYSTEM-TEST-003
created: 2026-09-05
updated: 2026-09-06T19:47:27Z
---

# ARCH-006-BACKGROUND-007: Add self-healing translation reconciliation and worker runtime

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Make the translation subsystem reconstruct all required BullMQ execution from PostgreSQL on startup and periodically, including durable Admin-triggered reconciliation, while reusing healthy deterministic jobs and recreating failed/stale ones.

## Context

Redis/BullMQ can be lost completely. Worker restart must discover translations awaiting dispatch, READY batches awaiting submit, overdue provider polls, provider-completed batches awaiting result processing, ambiguous submissions, retryable failures and durable Admin reconciliation requests. Reconciliation itself must not depend solely on a BullMQ scheduled job.

## Scope

New merchant-communications worker entrypoint/runtime, startup + periodic PostgreSQL reconciler, deterministic queue job inspection/repair, `SUBMISSION_UNKNOWN` provider metadata recovery, readiness/resources and reuse of existing queue-performance telemetry.

## Out of Scope

- New business schema/contracts.
- Direct Admin manipulation of Redis/OpenAI.
- Provider webhooks/public HTTP callbacks.
- Unbounded full-table scans.
- Deleting durable failed Batch/translation history.
- Custom duplicate queue telemetry already provided by approved framework/shared helpers.

## Requirements

Add `start:merchant-communications-worker` (or repository-conventional equivalent) as an independently deployable background worker. It owns **one process-level BullMQ Worker/router for the `merchant-communications` queue**, routing by `job.name` to the accepted dispatch/submit/poll/results/reconcile handlers. Do not create competing per-job-name Worker instances on the same queue. Horizontal replicas each run the same complete router so any replica can safely process any merchant-communications job. The process also runs reconciliation once after dependencies are ready, then on a configurable **minute** interval.

PostgreSQL determines expected work. Reconcile bounded/indexed pages for at least:

```text
PENDING translation, no current Batch        -> dispatch
READY Batch with nextSubmitAt due/null      -> submit
SUBMISSION_UNKNOWN                           -> provider correlation lookup/recovery only
SUBMITTED/nonterminal Batch with nextPollAt due -> poll current sequence
PROVIDER_COMPLETED                           -> results
PENDING translation retry due              -> appropriate dispatch/recovery
PENDING admin reconciliation request         -> targeted/global bounded failed-translation recovery
```

Deterministic BullMQ job repair rule:

```text
missing                         -> add
waiting/delayed/active healthy  -> reuse; do not add duplicate
failed                          -> remove queue job, then add same deterministic job ID
completed but DB still needs it -> remove stale completed job, then add same deterministic job ID
```

Never delete the durable DB record merely because its BullMQ execution failed.

For `SUBMISSION_UNKNOWN`, use `BACKGROUND-001.findBatchByCorrelation` with provider metadata `moda_translation_batch_id` and the persisted provider `inputFileId` where available. OpenAI's Batch list API is cursor/limit based rather than exposing a documented metadata-filter parameter, so lookup must scan a bounded recent/paginated window and stop once results are older than the relevant submission-attempt horizon plus a safety margin. If exactly one match is found, atomically adopt its provider Batch ID/status and continue normal polling. If no match is found yet, keep `SUBMISSION_UNKNOWN` and revisit reconciliation; **do not blindly call create again**. If multiple matches are found, persist/report a reconciliation conflict and do not choose one arbitrarily.

Manual requests: claim durable `MerchantTranslationReconciliationRequest` idempotently. For `TRANSLATION`, inspect the targeted failed translation/current Batch. If its current Batch is definitely terminal (`FAILED`/`EXPIRED`/`CANCELLED`) or no current Batch exists, transactionally clear the current-attempt pointer, increment retry count, return the translation to `PENDING`/due-now, and restore deterministic dispatch. If its Batch is still SUBMITTED/unknown/provider-completed, restore that existing lifecycle instead of creating a new attempt. For `FAILED_TRANSLATIONS`, apply the same rule to a bounded page of eligible failed translations and continue through bounded follow-up work until the request is complete. Record outcome. If Redis is down, the request remains PENDING/retryable.

Automatic periodic reconciliation may restore translations already returned to `PENDING` by the bounded automatic retry policy in `BACKGROUND-006`, but it does **not** reset durable provider-result `FAILED` translations after retry exhaustion/non-retryable failure. Those require explicit durable reconciliation intent. Failed/stale BullMQ execution jobs for otherwise nonterminal DB state are still repaired automatically.

Use the existing shared/framework queue-performance telemetry for the new queue; do not build a parallel telemetry implementation.

## Work Items

- [x] Add dedicated worker entrypoint/script/readiness resource wiring for `merchant-communications`.
- [x] Register accepted dispatch/submit/poll/results/reconcile handlers behind one shared-queue Worker/router keyed by `job.name`.
- [x] Implement startup + periodic minute-scale bounded reconciliation loop independent of BullMQ scheduling.
- [x] Implement deterministic job-state inspection/reuse/remove+recreate rules.
- [x] Implement bounded `SUBMISSION_UNKNOWN` metadata+input-file correlation recovery with no provider re-create and conflict detection.
- [x] Process durable Admin reconciliation requests through the same recovery engine.
- [x] Wire existing queue-performance telemetry to this queue/worker.
- [x] Add focused healthy-reuse, failed-job-repair, and completed-stale-job-repair tests.

## Interfaces / Contracts

Durable source of truth: DB002 models.
Execution contracts: SHARED-001 queue schemas/job IDs.
Provider correlation/recovery: BACKGROUND-001 adapter.

The reconciler may enqueue jobs, but must not directly duplicate the implementation of dispatch/submit/poll/results processors; it restores the correct deterministic work and lets the canonical processor run.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-GATEWAY-001`, `ARCH-006-ADMIN-002`, `ARCH-006-ADMIN-004`, `ARCH-006-SHOPIFY-003`, `ARCH-006-SYSTEM-TEST-003`

## Acceptance Criteria

- [x] DB-committed translation is reconstructed when initial enqueue is absent.
- [x] Complete Redis job loss can be reconstructed by the startup/periodic database scan.
- [x] Healthy existing deterministic jobs are reused.
- [x] Failed/stale queue jobs are removed and recreated with the same logical ID.
- [x] `SUBMISSION_UNKNOWN` uses correlation only and never blindly re-submits.
- [x] OpenAI completion while workers are offline is discovered by overdue polling reconciliation.
- [x] Admin reconciliation requests remain durable/retryable when Redis operations fail before claim.
- [x] Reconciliation queries are bounded/index-backed and use minute-scale cadence.
- [x] New worker uses existing readiness/telemetry conventions and is independently deployable.

## Validation

Focused recovery/runtime tests, repository-declared full validation, startup/readiness tests if present, and `git diff --check`. Simulate Redis loss/failure with test doubles/fixtures; do not require destructive real Redis testing.

## Implementation Notes

This is the final background integration task. Do not add a provider callback/webhook service; ARCH-006 intentionally uses polling.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/observability/merchant-communications.mjs`
- `moda-interact-background/src/entrypoints/merchant-communications.ts`
- `moda-interact-background/src/observability/queue-performance.ts`
- `moda-interact-background/src/observability/worker-metrics.ts`
- `moda-interact-background/src/runtime/readiness.ts`
- `moda-interact-background/src/services/translation-reconciliation.service.ts`
- `moda-interact-background/src/workers/merchant-communications.worker.ts`
- `moda-interact-background/src/workers/translation-reconcile.worker.ts`
- `moda-interact-background/tests/unit/services/translation-reconciliation.service.test.ts`

### Work Completed

- Added the independently deployable merchant-communications worker with one BullMQ Worker/router for all accepted job names.
- Added readiness, dedicated observability identity, graceful resource cleanup, existing queue-performance telemetry, and configurable minute-scale reconciliation.
- Added bounded PostgreSQL-driven recovery for pending translations, READY/submitted/provider-completed batches, durable admin requests, and deterministic queue repair.
- Added provider correlation adoption/conflict handling for `SUBMISSION_UNKNOWN` without blind provider creation.
- Attempt 2 corrected fair status-specific scans, bounded correlation horizons, guarded correlation CAS handling, canonical poll/results restoration, exact and stale durable request claiming, failed-only reset semantics, multi-page continuation, and queue-failure rollback.
- Attempt 3 replaced the unbounded `COUNT(*)` continuation query for `FAILED_TRANSLATIONS` with a bounded existence probe using `LIMIT 1`, preserving the eligible-row predicate and durable continuation/completion behavior.

### Validation Results

- Focused reconciliation/runtime/provider validation: 7 files, 42 tests passed.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Workspace diagnostics: no errors in touched source files.
- `npm run test:unit`: 215 passed, 3 pre-existing failures in recovery-routing/pending-recovery-candidate tests outside this task's files.
- Attempt 2 focused reconciliation and accepted translation suite: 7 files, 56 tests passed.
- Attempt 2 `npm run build`: passed.
- Attempt 2 `npm run prisma:validate`: passed.
- Attempt 2 touched-file diagnostics: no errors found.
- Attempt 2 `git diff --check`: passed.
- Attempt 3 focused reconciliation/runtime/provider validation: 7 files, 57 tests passed.
- Attempt 3 `npm run build`: passed.
- Attempt 3 `npm run prisma:validate`: passed.
- Attempt 3 touched-file diagnostics: no errors found.
- Attempt 3 `git diff --check`: passed.

### Deviations

- Redis-loss behavior is implemented with queue-availability gating and durable request state; the regression uses queue doubles rather than a destructive live Redis-loss fixture.

### Assumptions

- The existing BullMQ queue connection and shared telemetry conventions remain the process-level ownership boundary.
- Bounded follow-up reconciliation continues work across minute-scale passes when a single page cannot exhaust a durable request.

### Unresolved Issues

- Full repository unit validation retains three unrelated recovery-service failures from the prior baseline; the Attempt 3 correction suite and accepted translation tests are green.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending architect review after Attempt 3 correction.

### Attempt 1 Decision

The worker/router, readiness wiring, telemetry reuse, deterministic queue repair helper and startup/periodic PostgreSQL-driven reconciliation shape are acceptable. The task is not accepted because the reconciliation service can still strand durable work or complete durable Admin requests before all required recovery has been restored.

### Blocking Findings

1. **Correlated `SUBMISSION_UNKNOWN` completion loses provider result-file state.** A matched provider Batch in `completed` state is moved to `PROVIDER_COMPLETED` without persisting `outputFileId` / `errorFileId`. The canonical results processor then has no provider result file to read.
2. **Correlated terminal provider state can strand translations.** A matched `failed` / `expired` / `cancelled` Batch is written directly to the terminal local Batch status, but the canonical poll processor is not invoked, so its translation retry/failure transition is never applied. Reconciliation must restore canonical poll/results work rather than implement a second terminal-result algorithm.
3. **Correlation adoption ignores its guarded-write result and does not immediately restore the next deterministic job.** A lost `SUBMISSION_UNKNOWN` CAS must be treated as stale, and no follow-up job may be scheduled from stale provider data.
4. **The combined Batch page can starve other required work.** Old unresolved `SUBMISSION_UNKNOWN` rows can permanently occupy the shared `LIMIT` and prevent newer READY, overdue SUBMITTED, or PROVIDER_COMPLETED rows from being reconciled. Each durable work class needs its own bounded/fair scan (or an equivalent bounded fairness strategy).
5. **`FAILED_TRANSLATIONS` is not a durable multi-page operation.** It processes one page, does not increment retry count using the targeted rule, ignores failed translations whose current Batch is definitively terminal, and then marks the request `COMPLETED` even when additional eligible failed translations remain.
6. **Targeted reconciliation can complete without restoring an existing lifecycle.** `TRANSLATION` requests whose current Batch is READY/SUBMITTED/SUBMISSION_UNKNOWN/PROVIDER_COMPLETED currently fall through and are marked complete instead of repairing the existing submit/poll/results/correlation work.
7. **Targeted request hints are incorrectly constrained by the global first page.** When `reconciliationRequestId` is supplied, the outer exact-ID filter is still intersected with a separate global `LIMIT` subquery. A requested ID outside that first page is not claimed.
8. **A process crash after request claim can strand `PROCESSING` forever.** Startup/periodic reconciliation must be able to reclaim stale PROCESSING requests after a bounded timeout; Redis failure must still return the request to retryable PENDING state.
9. **Manual translation reset is too broad.** The reset path must operate on durable `FAILED` translations only; it must not increment retry state for an arbitrary non-failed translation whose `currentBatchId` is null.

### Attempt 2 Correction Contract

Attempt 2 is a bounded reconciliation-correctness correction. Do not rewrite the accepted worker/router, readiness, telemetry, package scripts, provider adapter, poll service, results service, schema, or downstream tasks.

Allowed implementation files:

- `moda-interact-background/src/services/translation-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/translation-reconciliation.service.test.ts`

Required behavior:

- Keep deterministic queue repair in the reconciler and canonical business transitions in the accepted dispatch/submit/poll/results processors.
- Replace the starvation-prone combined Batch scan with bounded fair/status-specific recovery so unresolved ambiguous submissions cannot prevent READY submit, overdue poll, or PROVIDER_COMPLETED result repair.
- Apply a bounded safety margin when supplying the provider-correlation submission horizon. Do not blind-create a provider Batch.
- For a correlation match, use a guarded `SUBMISSION_UNKNOWN` CAS and inspect its affected-row result:
  - provider `completed`: persist provider Batch ID, input-file ID and output/error file IDs, move to `PROVIDER_COMPLETED`, then restore the deterministic results job;
  - provider `nonterminal`: persist/adopt the provider Batch, make poll work due, and restore the current deterministic poll job;
  - provider `failed` / `expired` / `cancelled`: adopt the provider Batch into the canonical pollable path and restore the deterministic poll job so `translation-batch-poll.service.ts` remains the sole owner of terminal translation retry/failure semantics;
  - lost CAS: return stale/no-op and do not enqueue work from stale data;
  - conflict: persist/report conflict and never choose or re-create blindly.
- When a specific reconciliation request ID is supplied, claim that exact eligible request directly rather than requiring it to fall inside the unrelated global first page.
- Reclaim stale `PROCESSING` reconciliation requests after a bounded minute-scale timeout so process death cannot strand durable intent.
- `TRANSLATION` scope must first inspect the failed translation/current Batch:
  - no current Batch or definitively terminal Batch -> atomically reset only the `FAILED` translation, clear current attempt, increment retry count, make it due now, then restore deterministic dispatch;
  - READY/SUBMITTED/SUBMISSION_UNKNOWN/PROVIDER_COMPLETED current Batch -> repair that existing canonical lifecycle; do not create a new attempt;
  - non-failed/stale request -> do not increment retry state.
- `FAILED_TRANSLATIONS` must apply the same eligible failed-translation reset semantics to a bounded page, increment retry count consistently, include translations whose current Batch is definitively terminal, and leave/requeue the durable request for bounded continuation while further eligible rows remain. Mark it `COMPLETED` only when the bounded global recovery is exhausted.
- Successful request completion should clear transient failure state; Redis/queue failure after claim must return the request to retryable `PENDING` rather than losing intent.
- Preserve the current single shared BullMQ Worker/router and do not promote `BACKGROUND-007` enables.

Required focused regressions:

- completed correlation persists `outputFileId`/`errorFileId` and restores results;
- terminal correlation restores canonical poll processing and does not strand a PENDING translation on a terminal Batch;
- lost correlation CAS schedules nothing;
- an old unresolved `SUBMISSION_UNKNOWN` row cannot starve READY/SUBMITTED/PROVIDER_COMPLETED repair;
- exact targeted request ID is claimed even when outside the normal first global page;
- targeted failed translation with an existing nonterminal/current Batch repairs that existing lifecycle instead of creating a new attempt;
- reset is restricted to `FAILED` and increments retry count once;
- `FAILED_TRANSLATIONS` with more than one configured page remains retryable/continuable until every eligible page is drained, including terminal-current-Batch rows;
- stale `PROCESSING` request can be reclaimed after the bounded timeout;
- queue/Redis failure after claim returns durable request state to `PENDING`.

Validation:

- focused reconciliation tests;
- existing accepted translation dispatch/submit/poll/results tests remain green;
- `npm run build`;
- `npm run prisma:validate`;
- `git diff --check`.

Return `ARCH-006-BACKGROUND-007` to `review` and STOP. Do not modify or promote Gateway, Admin, Shopify, or system-test tasks.


### Attempt 2 Decision

Attempt 2 correctly resolves the provider-correlation, fairness, stale-request, exact-request, failed-only reset, canonical lifecycle and queue-failure findings from Attempt 1. The single shared Worker/router and downstream boundaries remain acceptable. One bounded scalability defect remains before this final Background task can be accepted.

### Attempt 2 Remaining Blocking Finding

1. **`FAILED_TRANSLATIONS` continuation detection performs an unbounded aggregate scan.** After processing one bounded page, the reconciler executes `SELECT COUNT(*)` across every remaining eligible failed translation. That defeats the task's bounded/index-backed reconciliation invariant and can make one Admin recovery request perform work proportional to the entire failed-translation backlog. The reconciler only needs to know whether more eligible work exists, not the total count.

### Attempt 3 Correction Contract

Attempt 3 is a narrow bounded-query correction. Do not change the accepted worker/router, provider correlation logic, request ownership semantics, queue repair rules, poll/results processors, schema, package scripts, readiness, telemetry, or downstream tasks.

Allowed implementation files:

- `moda-interact-background/src/services/translation-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/translation-reconciliation.service.test.ts`

Required behavior:

- Replace the unbounded `COUNT(*)` continuation query for `FAILED_TRANSLATIONS` with a bounded existence probe, for example an indexed eligibility query using `SELECT 1 ... LIMIT 1` or an equivalent bounded construct.
- Preserve the current eligible-row predicate exactly: only durable `FAILED` translations with no current Batch or a current Batch in `FAILED` / `EXPIRED` / `CANCELLED` count as remaining manual-reset work.
- If one or more eligible rows remain after the current page, return the durable reconciliation request to retryable `PENDING`; otherwise mark it `COMPLETED`.
- Preserve the existing queue-failure recovery behavior and all Attempt 2 provider/request corrections.
- Do not promote any `BACKGROUND-007` enables.

Required focused regression:

- prove multi-page continuation uses a bounded remaining-work probe rather than an aggregate count and still leaves the request `PENDING` when at least one eligible row remains;
- prove the request becomes `COMPLETED` when the bounded remaining-work probe returns no row.

Validation:

- focused reconciliation tests;
- accepted translation dispatch/submit/poll/results tests remain green;
- `npm run build`;
- `npm run prisma:validate`;
- `git diff --check`.

Return `ARCH-006-BACKGROUND-007` to `review` and STOP. Do not modify or promote Gateway, Admin, Shopify, or system-test tasks.

### Attempt 3 Implementation Note

Replaced the `FAILED_TRANSLATIONS` continuation `COUNT(*)` query with a bounded existence probe using the unchanged eligible-row predicate and `LIMIT 1`. Added regressions covering both retryable continuation and completion when no eligible row remains.


### Attempt 3 Final Decision

**Review Status: Accepted — Complete**

Independent `moda_architect` review confirms Attempt 3 satisfies the final bounded-reconciliation correction. The `FAILED_TRANSLATIONS` continuation check now uses the existing indexed eligibility predicate with an ordered `LIMIT 1` existence probe rather than an unbounded aggregate. The request remains `PENDING` when one eligible row remains and becomes `COMPLETED` when none remains.

Attempt 3 changes are confined to `translation-reconciliation.service.ts`, its focused reconciliation test, and task/index reporting. The accepted Attempt 2 provider-correlation recovery, exact/stale request ownership, canonical terminal poll routing, failed-only reset semantics, queue-failure rollback, fair per-state scans, single BullMQ Worker/router, readiness and telemetry boundaries remain intact. The database index `@@index([status, currentBatchId, nextAttemptAt, createdAt])` supports the bounded failed-translation eligibility scan.

Validation evidence recorded by the implementation task: 57 focused tests passed; build passed; Prisma validation passed; touched-file diagnostics were clean; `git diff --check` passed. The three previously documented unrelated recovery-service baseline failures remain outside this task.

Architect outcome: `ARCH-006-BACKGROUND-007` is Complete. Its implementation dependants may now be released according to their own dependency lists. System-test tasks remain manual-gated and are not automatically started.
