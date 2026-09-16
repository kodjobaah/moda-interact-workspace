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
status: pending
priority: 64
executor: null
claimed_at: null
attempt: 0
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
