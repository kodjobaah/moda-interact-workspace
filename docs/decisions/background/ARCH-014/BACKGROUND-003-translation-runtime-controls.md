---
id: ARCH-014-BACKGROUND-003
architecture_id: ARCH-014
title: Move translation operational tuning from environment variables to runtime configuration
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 64
attempt: 2
depends_on:
- ARCH-014-BACKGROUND-001
enables:
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-003

## Objective

Make translation scheduling, batching and retry policy Admin-tunable without redeploy while retaining deployment-only provider/model credentials.

## Files in scope

At minimum:

```text
src/entrypoints/merchant-communications.ts
src/services/translation-reconciliation.service.ts
src/services/translation-batch-assembly.service.ts
src/services/translation-batch-submit.service.ts
src/services/translation-batch-poll.service.ts
src/services/translation-batch-results.service.ts
```

Update directly related tests.

## Global reconciliation scheduler

Replace merchant-communications `setInterval` reconciliation with the common dynamic leased scheduler:

```text
lease = TRANSLATION_RECONCILIATION
interval = translationReconciliationIntervalSeconds
```

Startup reconciliation MUST also acquire the lease.

With multiple merchant-communications replicas, only one global reconciliation pass runs while the lease is valid.

## Remove runtime authority from these environment variables

After this task these names must not be read by production source:

```text
TRANSLATION_RECONCILIATION_INTERVAL_MINUTES
TRANSLATION_RECONCILIATION_PAGE_SIZE
TRANSLATION_RECONCILIATION_CLAIM_TIMEOUT_MINUTES
TRANSLATION_BATCH_MAX_REQUESTS
TRANSLATION_BATCH_SUBMIT_RETRY_MINUTES
TRANSLATION_BATCH_SUBMIT_MAX_ATTEMPTS
TRANSLATION_BATCH_INITIAL_POLL_MINUTES
TRANSLATION_BATCH_POLL_INTERVAL_MINUTES
TRANSLATION_MAX_AUTO_RETRIES
```

Do not keep env-over-DB or DB-over-env precedence. The database is authoritative.

These remain deployment environment configuration and MUST NOT move:

```text
TRANSLATION_PROVIDER
TRANSLATION_MODEL
OPENAI_API_KEY / provider credentials
```

## Exact runtime mapping

```text
translationReconciliationIntervalSeconds
  -> periodic reconciliation wait

translationReconciliationPageSize
  -> every reconciliation query LIMIT / failed-translation restoration page

translationClaimTimeoutSeconds
  -> stale reconciliation request claim and ambiguous submission correlation lookback

translationBatchMaxRequests
  -> translation batch assembly LIMIT

translationSubmitRetrySeconds
  -> failed definite/retryable submission nextSubmitAt

translationSubmitMaxAttempts
  -> terminal submission-attempt threshold

translationInitialPollSeconds
  -> first provider batch poll nextPollAt + BullMQ delay

translationPollIntervalSeconds
  -> subsequent provider batch polling and poll-read retry

translationResultRetrySeconds
  -> failed provider result application / translation item nextAttemptAt

translationMaxAutoRetries
  -> terminal provider/item automatic retry count
```

`translationResultRetrySeconds` is deliberately separate. Do not reuse the provider poll interval for result-application retries.

## Configuration access

Services that make a decision per job/request must read from the process last-known-good snapshot at the decision point.

Do not query PostgreSQL separately for every translated message.

For testability, services may accept an injectable minimal runtime-config reader, but production defaults to `backgroundRuntimeConfigService`.

## Seconds, not minutes

Persisted runtime values are seconds.

Convert once at scheduling boundaries:

```text
seconds * 1000
```

Do not round to minutes. This allows e.g. 90-second operational tuning.

## Provider safety invariants remain fixed

Do not migrate:

```text
MAX_CORRELATION_PAGES
MAX_PAGE_SIZE in provider correlation API
MAX_OUTPUT_BYTES
MAX_OUTPUT_LINES
provider endpoint/completion window
failure retryability classification
```

## Mandatory tests

1. translation reconciliation is globally lease-protected across two schedulers;
2. 300 -> 60 second interval update works without restart;
3. page size uses config;
4. claim timeout uses config;
5. batch assembly max requests uses config;
6. submit retry seconds uses config;
7. max submission attempts uses config;
8. initial poll uses config;
9. recurring poll uses config;
10. max automatic retries uses config;
11. result retry uses `translationResultRetrySeconds`, not poll interval;
12. provider/model remain environment-configured;
13. config refresh failure retains prior values;
14. no migrated environment-variable name is read from `src/`;
15. existing concurrency/`SKIP LOCKED` batch assembly semantics remain unchanged.

## Validation

```bash
npm run test:unit
npm run test:integration --if-present
npm run build
git diff --check
```

## Stop conditions

STOP rather than creating another settings source or weakening provider-output safety bounds.

## Completion Report

Status: Ready for Review

Implementation commits: `f575ed5`, `44590e2` on `task/ARCH-014-BACKGROUND-003`, pushed to `origin`.

### Requirements

- Replaced merchant-communications reconciliation `setInterval` with `startDynamicLeasedScheduler`, using `TRANSLATION_RECONCILIATION` and `translationReconciliationIntervalSeconds`; startup also runs through lease acquisition.
- Migrated reconciliation page size, claim timeout, batch assembly limit, submission retry/attempt policy, initial poll, recurring poll/read retry, result retry, and automatic retry limits to the process last-known-good runtime-config snapshot at decision points.
- Preserved decimal seconds via `seconds * 1000`, `FOR UPDATE SKIP LOCKED`, concurrent batch assembly semantics, provider retry classification, and provider output safety/provider correlation bounds.
- Kept `TRANSLATION_PROVIDER`, `TRANSLATION_MODEL`, and provider credentials deployment-configured; no retired translation environment-variable names are read from `src/`.
- Kept `translationResultRetrySeconds` distinct from `translationPollIntervalSeconds` for result/item retry scheduling.
- Attempt 2 correction: captured one last-known-good runtime snapshot per valid submit or poll job and threaded it through failure, persistence, and enqueue helpers; initial and recurring poll database schedules now use the exact same seconds value as their BullMQ delays.
- Attempt 2 regression tests prove one `current()` call and identical persisted/enqueued timing for successful submission, nonterminal polling, and provider-read-failure polling; terminal item retry continues to use `translationResultRetrySeconds` separately from the poll interval.

### Validation

- Focused submit/poll regression tests: PASS, 2 files / 24 tests.
- `npm run test:unit`: 949 passed; 2 pre-existing failures in `tests/unit/runtime/observability-startup.test.ts` (recovery entrypoint source-text expectation and shared dependency version expectation `0.9.0` versus repository `0.11.2`). No failures were in task-owned translation files.
- `npm run test:integration --if-present`: PASS, 2 files / 3 tests, including PostgreSQL concurrent `SKIP LOCKED` batch assembly.
- `npm run build`: PASS (`prisma:generate` and `tsc`).
- `git diff --check`: PASS.
- Retired environment-name scan under `src/`: PASS, no matches. Provider/model/credential scan confirms retained reads.

### Evidence and limitations

- Launcher supplied and used the canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-BACKGROUND-003` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-BACKGROUND-003`.
- Launcher reported the initialized database submodule at `47232f6876469f209c7efde4cefbb8a47d864e6a`; no database files or parent submodule gitlink were changed.
- Implementation worktree is clean after publication at `44590e2`. Parent worktree contains only this task report change before its report commit.
- The full unit suite retains the two unrelated observability baseline failures listed above; integration infrastructure was available and passed.

## Architect Review

### Review Status

Changes Requested

### Functional finding

The runtime mappings are present, but initial and recurring provider-poll scheduling can use two different `BackgroundRuntimeConfig` versions inside one job.

`TranslationBatchSubmitService` currently reads `translationInitialPollSeconds` once while persisting `MerchantTranslationBatch.nextPollAt`, then reads the runtime config again after the database await when enqueuing the BullMQ poll job. `TranslationBatchPollService` has the same split for `translationPollIntervalSeconds`: the database `nextPollAt` is persisted first, then the queue delay is calculated from another `current()` call.

`BackgroundRuntimeConfigService` refreshes asynchronously every five seconds. Therefore a config version change can occur while either service is awaiting the database. Example: the database can persist `nextPollAt = now + 300 seconds`, the process refreshes to `60 seconds`, and the BullMQ job is then enqueued with a 60-second delay. The poll worker does not reject a job merely because persisted `nextPollAt` is still in the future, so provider polling can run materially earlier than the database schedule. The inverse change produces a materially late poll.

This violates the task's paired mappings:

```text
translationInitialPollSeconds
  -> first provider batch poll nextPollAt + BullMQ delay

translationPollIntervalSeconds
  -> subsequent provider batch polling and poll-read retry
```

The issue is runtime consistency, not test breadth.

### Required Attempt 2 correction

Keep the correction limited to the translation submit/poll scheduling paths. Do not redesign translation batching, provider safety rules, environment configuration, retryability classification, leases, database schema, or queue topology.

#### 1. `src/services/translation-batch-submit.service.ts`

For one `submit(...)` job, capture one runtime-config snapshot before making runtime-policy decisions:

```ts
const runtimeConfig = currentTranslationRuntimeConfig(this.runtimeConfig);
```

Use that same object for all task-owned submit policy in that job, including:

```text
translationSubmitMaxAttempts
translationSubmitRetrySeconds
translationInitialPollSeconds
```

Change helper signatures as necessary so the same snapshot/value is passed into:

```text
persistFailure(...)
persistSubmitted(...)
enqueuePoll(...)
```

The successful provider-create path MUST use the exact same `runtimeConfig.translationInitialPollSeconds` value for both:

```text
MerchantTranslationBatch.nextPollAt
BullMQ TRANSLATION_BATCH_POLL delay
```

Do not call `currentTranslationRuntimeConfig(...)` independently in those two helpers for the same submit job.

#### 2. `src/services/translation-batch-poll.service.ts`

For one valid `poll(...)` job, capture one runtime-config snapshot and pass it through the job's runtime-policy helpers.

For both provider-read failure and provider `nonterminal` outcomes, the exact same `runtimeConfig.translationPollIntervalSeconds` value MUST drive:

```text
persisted MerchantTranslationBatch.nextPollAt
BullMQ replacement poll-job delay
```

Thread the snapshot/value into:

```text
rescheduleAfterReadFailure(...)
advanceNonterminal(...)
enqueuePoll(...)
```

Do not independently re-read `current()` between persisting the schedule and enqueuing the replacement poll job.

The existing terminal provider/item behavior must remain unchanged apart from using the captured job snapshot where runtime retry values are needed. Preserve:

```text
failureIsRetryable(...)
translationMaxAutoRetries
translationResultRetrySeconds
message failure-state semantics
```

#### 3. Preserve exact scope boundaries

Do not change:

```text
TRANSLATION_PROVIDER
TRANSLATION_MODEL
OPENAI_API_KEY / provider credentials
MAX_CORRELATION_PAGES
provider MAX_PAGE_SIZE
MAX_OUTPUT_BYTES
MAX_OUTPUT_LINES
provider endpoint/completion window
failure retryability classification
FOR UPDATE SKIP LOCKED batch assembly
translation reconciliation lease/scheduler
```

Do not reintroduce any retired translation environment-variable read.

### Focused regression evidence

Add focused tests using a runtime-config reader whose `current()` would return different values on successive calls. Prove at minimum:

1. successful batch submission persists and enqueues the first poll with one identical `translationInitialPollSeconds` value;
2. nonterminal provider polling persists and enqueues the next poll with one identical `translationPollIntervalSeconds` value;
3. provider-read-failure polling uses the same one-snapshot recurring poll interval;
4. the correction does not merge `translationResultRetrySeconds` into the provider poll interval.

The tests should verify functional timing consistency; no broad expansion of translation coverage is required.

### Stop condition

Return the same task as Attempt 2 after this correction. Do not start `ARCH-014-BACKGROUND-004` or `ARCH-014-BACKGROUND-005` until BACKGROUND-003 is architect-accepted.
