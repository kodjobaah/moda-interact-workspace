---
id: ARCH-006-BACKGROUND-005
architecture_id: ARCH-006
title: Submit each logical translation Batch to OpenAI at most once
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-006-BACKGROUND-004
enables:
  - ARCH-006-BACKGROUND-006
created: 2026-09-05
updated: 2026-09-06T17:45:46Z
---
# ARCH-006-BACKGROUND-005: Submit each logical translation Batch to OpenAI at most once

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Implement the single irreversible provider-submission boundary with atomic READY claiming, durable provider correlation, minute-scale first-poll scheduling and an explicit ambiguous-outcome state that is never blindly re-submitted.

## Context

Duplicate BullMQ delivery and horizontal workers are normal. The hardest failure is provider acceptance followed by process failure before `providerBatchId` is persisted. The architecture prefers a temporarily stuck `SUBMISSION_UNKNOWN` record over accidentally paying/submitting twice.

## Scope

`translation-batch-submit` processor and transaction/provider calls necessary to move one logical Batch from READY through submission to SUBMITTED or SUBMISSION_UNKNOWN.

## Out of Scope

- Batch assembly.
- Repeated polling/output processing.
- Automatic/manual reconciliation implementation.
- Webhooks.
- Deleting historical Batch rows.

## Requirements

State machine:

```text
READY (due) --atomic CAS--> SUBMITTING
SUBMITTING --input upload/provider preparation definitely fails before Batch create--> READY + nextSubmitAt
SUBMITTING --provider Batch accepted + ID persisted--> SUBMITTED
SUBMITTING --provider explicitly proves Batch was not created and error is retryable--> READY + nextSubmitAt
SUBMITTING --provider explicitly proves Batch was not created and error is terminal/max retries exhausted--> FAILED
SUBMITTING --Batch-create outcome ambiguous--> SUBMISSION_UNKNOWN
```

The atomic READY->SUBMITTING update must affect exactly one row; zero rows means another worker owns/handled the state and this job returns without provider create.

Build JSONL from immutable authoritative DB messages/translations and Batch items. Provider `custom_id` must map to each translation. Upload the provider input file first and persist its `inputFileId` on the logical Batch before invoking the irreversible Batch-create request whenever the provider SDK/API permits that separation. Reusing a persisted input file is preferred over uploading another copy on a retry.

Create via `BACKGROUND-001` adapter exactly once for a given submit attempt. The submit processor must **catch and persist provider failure classification itself**; it must not rely on BullMQ `attempts` or generic worker retry to repeat Batch create. OpenAI SDK automatic retries remain disabled for Batch create.

Failure classification is explicit:

- `DEFINITE_RETRYABLE_NOT_CREATED`: the adapter can prove Batch create was not accepted (including preparation/upload failure before create); increment durable `submitAttemptCount`, set `lastSubmitAttemptAt`, return to `READY` with configurable minute-based `nextSubmitAt`, and let reconciliation restore the same deterministic submit job when due.
- `DEFINITE_TERMINAL_NOT_CREATED`: persist `FAILED` after recording bounded failure metadata.
- `AMBIGUOUS_CREATE`: timeout/transport/provider outcome where Moda cannot prove whether OpenAI accepted the Batch; persist `SUBMISSION_UNKNOWN` and **never automatically invoke create again**.
- success: persist provider Batch ID, `submittedAt`, initial `pollSequence` and `nextPollAt = now + configurable MINUTES`, then best-effort enqueue the delayed poll.

Use bounded runtime configuration such as `TRANSLATION_BATCH_SUBMIT_RETRY_MINUTES`, `TRANSLATION_BATCH_SUBMIT_MAX_ATTEMPTS`, and `TRANSLATION_BATCH_INITIAL_POLL_MINUTES`. No retry cadence is expressed in seconds.


### Shared queue worker topology

`merchant-communications` is one BullMQ queue containing multiple job names. This task owns its job-name processor/handler only. **Do not instantiate a dedicated `new Worker(MERCHANT_COMMUNICATIONS_QUEUE_NAME, ...)` for this job name.** Multiple per-job Workers on one queue compete for all queue jobs and can steal/fail work owned by another processor. `ARCH-006-BACKGROUND-007` owns the single process-level Worker/router and registers the accepted handlers by `job.name`. Horizontal scale is achieved by running multiple identical router-worker processes, each capable of every registered merchant-communications job.

## Work Items

- [x] Add strict submit-job processor.
- [x] Implement atomic READY->SUBMITTING claim and idempotent terminal/no-op behavior.
- [x] Load Batch items/messages and build provider requests through accepted adapter.
- [x] Persist input-file correlation before the irreversible create boundary where supported.
- [x] Implement durable definite-failure retry scheduling (`submitAttemptCount`/`nextSubmitAt`) without BullMQ create retries.
- [x] Persist successful provider correlation and minute-scale first-poll state.
- [x] Enqueue deterministic poll identity using persisted pollSequence after commit.
- [x] Classify real provider submission failures as definite-retryable, definite-terminal or ambiguous; only definite-retryable failures may return to READY.
- [x] Classify ambiguous create failures into `SUBMISSION_UNKNOWN` without re-create.
- [x] Add duplicate-delivery/concurrent-submit tests and an explicit provider-accepted-before-DB-persist crash-window simulation.

## Interfaces / Contracts

Input: `translation-batch-submit {schemaVersion, translationBatchId}`.

Successful durable output:

```text
status=SUBMITTED
providerBatchId=<unique>
inputFileId=<persisted provider input file id>
submitAttemptCount>=1
pollSequence>=1
nextPollAt=<minutes in future>
```

Execution hint: `translation-batch-poll` with same persisted sequence.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-BACKGROUND-006`

## Acceptance Criteria

- [x] Two concurrent submit jobs produce at most one provider create call.
- [x] Already SUBMITTED/terminal Batch is a no-op.
- [x] Provider SDK/BullMQ do not automatically retry the irreversible Batch-create call.
- [x] Real definite retryable pre-create/create rejection uses durable minute-based `nextSubmitAt` and a bounded max-attempt policy.
- [x] Ambiguous create becomes `SUBMISSION_UNKNOWN`, never READY.
- [x] Successful provider identity is durably unique.
- [x] Initial polling delay is configured in minutes.
- [x] Redis failure after success leaves enough DB state to recreate the poll.

## Validation

Focused state-machine/concurrency/provider-mock tests plus repository-declared validation and `git diff --check`.

## Implementation Notes

Do not solve `SUBMISSION_UNKNOWN` by calling create again. OpenAI's documented Batch list endpoint exposes Batch metadata and `input_file_id` but does not expose a metadata-filter query parameter; recovery therefore belongs to `BACKGROUND-007` and must scan a bounded recent/paginated provider window, matching both durable logical metadata and the persisted input-file ID where available. Do not rely on an undocumented provider idempotency key for correctness.

## Completion Report

### Status

Ready for Review.

### Files Changed

- [moda-interact-background/src/services/translation-batch-submit.service.ts](../../../../moda-interact-background/src/services/translation-batch-submit.service.ts)
- [moda-interact-background/src/workers/translation-batch-submit.worker.ts](../../../../moda-interact-background/src/workers/translation-batch-submit.worker.ts)
- [moda-interact-background/src/domain/translation-batch.ts](../../../../moda-interact-background/src/domain/translation-batch.ts)
- [moda-interact-background/src/providers/translation.provider.ts](../../../../moda-interact-background/src/providers/translation.provider.ts)
- [moda-interact-background/tests/unit/services/translation-batch-submit.service.test.ts](../../../../moda-interact-background/tests/unit/services/translation-batch-submit.service.test.ts)

### Work Completed

- Added atomic conditional READY claim and durable SUBMITTING/SUBMITTED/READY/FAILED/SUBMISSION_UNKNOWN transitions.
- Added authoritative BatchItem/message loading, persisted input-file correlation and durable provider Batch identity.
- Added deterministic delayed poll enqueue with minute-based configuration and best-effort Redis handling.
- Added strict submit handler without a competing BullMQ Worker.
- Updated the provider adapter to submit each persisted BatchItem `providerCustomId`.

### Validation Results

- Focused TypeScript check: passed.
- Focused provider and submit tests: 15 passed.
- Full test suite: 182 passed, 3 failed in unrelated recovery-routing/pending-recovery tests, 3 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Deviations

- The full suite remains red because of three pre-existing failures outside the translation submission path.

### Assumptions

- OpenAI Batch create remains conservatively ambiguous unless the adapter explicitly classifies an error.
- `providerCustomId` is resolved by downstream historical BatchItem lookup; the provider output parser preserves custom IDs that are not legacy encoded translation IDs.

### Unresolved Issues

- The provider contract now carries the durable per-Batch custom ID, which is necessary to preserve historical Batch membership and result correlation.

### Architectural Concerns

None.

### Architect Review

### Review Status

Correction Required — return to `ready` for Attempt 2.

### Independent Review Findings

Attempt 1 establishes the correct broad submission shape: atomic `READY -> SUBMITTING` claim, persisted input-file correlation, one irreversible create call per claimed attempt, durable success/unknown states, minute-based first-poll scheduling, best-effort Redis enqueue and a handler-only queue boundary. The implementation is not yet architect-accepted because four correctness boundaries remain unresolved.

1. **The durable Batch provider/model snapshot is not authoritative at submission time.** `claimReadyBatch()` returns `provider` and `model`, but the default submit service constructs its provider from current process environment. A Batch assembled under one `TRANSLATION_MODEL`/provider can therefore be submitted after a deployment with a different runtime model/provider while its durable row still records the earlier values. Once a logical Batch exists, its persisted `provider` and `model` must determine the adapter/model used for input generation and create. Current environment configuration may govern creation of new logical Batches, not mutate the meaning of an already-persisted Batch. Unsupported persisted providers must fail safely before create.

2. **The production OpenAI create path does not actually produce the explicit definite failure classifications covered by the mocks.** Raw SDK create errors currently fall through to `AMBIGUOUS_CREATE`, so even an explicit provider rejection that proves non-creation (for example a rate-limit rejection that is safe to retry, or a validation rejection that is terminal) can become permanently `SUBMISSION_UNKNOWN`. The real adapter/submission boundary must classify explicit, provable non-creation responses into retryable/terminal categories while keeping timeout/transport/uncertain outcomes ambiguous. Conservative classification is required: do not classify an outcome as retryable unless non-creation is provable.

3. **Provider output correlation now overloads `translationId` with a per-Batch `providerCustomId`.** ARCH-006 requires the output `custom_id` to resolve through `MerchantTranslationBatchItem.providerCustomId`, because retries create a new custom ID for the same translation. The provider result contract should preserve the exact provider custom ID under an accurately named field (for example `providerCustomId`) rather than heuristically returning it through a field named `translationId`. `BACKGROUND-006` must be able to perform an explicit Batch-item lookup before resolving the durable translation. Remove/avoid heuristic custom-ID decoding for the new per-attempt path.

4. **The hardest acceptance crash window is not directly tested.** There is coverage for an ambiguous provider exception and for Redis failure after SUBMITTED, but not for: provider create returns an accepted provider Batch ID, then persistence of that ID fails before durable SUBMITTED state. Add a focused regression proving this path is treated as ambiguous/unknown and a replay cannot invoke create again. Also require the pre-create `inputFileId` persistence and post-create SUBMITTED persistence to verify that their guarded DB update actually affected the expected row before crossing/declaring the irreversible boundary.

### Attempt 2 Correction Contract

This is a bounded correction to `ARCH-006-BACKGROUND-005`; do not implement `BACKGROUND-006` or `BACKGROUND-007`. Preserve the accepted Attempt 1 structure. Production changes are limited to the provider/submission boundary and tests needed to prove it.

Allowed implementation/test files:

- `moda-interact-background/src/services/translation-batch-submit.service.ts`
- `moda-interact-background/src/providers/translation.provider.ts`
- `moda-interact-background/tests/unit/services/translation-batch-submit.service.test.ts`
- `moda-interact-background/tests/unit/providers/translation.provider.test.ts`

`translation-batch-submit.worker.ts`, assembly, polling/results, reconciliation, runtime router, database schema/migrations and other repositories are out of scope unless the agent stops `blocked` with concrete evidence that one of those contracts is impossible to satisfy without a separate architect decision.

Required focused proof:

- a persisted Batch model/provider wins over conflicting current environment configuration;
- explicit real-provider rejection with provable non-creation reaches retryable/terminal durable handling as appropriate;
- timeout/transport/uncertain create remains `SUBMISSION_UNKNOWN`;
- exact per-Batch `providerCustomId` survives JSONL -> provider output normalization without pretending to be a translation ID;
- provider acceptance followed by provider-ID persistence failure cannot lead to a second create;
- guarded input-file and SUBMITTED persistence cannot silently affect zero rows;
- submit retry/poll minute configuration is genuinely bounded with focused boundary tests, not merely positive;
- existing duplicate-delivery, max-attempt, Redis-outage and `maxRetries: 0` regressions remain green.

After correction, run the focused provider/submit tests, TypeScript/build, Prisma validation and `git diff --check`; record results, return only `ARCH-006-BACKGROUND-005` to `review`, and STOP. Do not promote or claim `BACKGROUND-006`.

## Attempt 2 Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-background/src/services/translation-batch-submit.service.ts`
- `moda-interact-background/src/providers/translation.provider.ts`
- `moda-interact-background/tests/unit/services/translation-batch-submit.service.test.ts`
- `moda-interact-background/tests/unit/providers/translation.provider.test.ts`
- This task document.

### Work Completed

- The default provider adapter is now created from the persisted Batch `provider` and `model` snapshot, so deployment-time configuration cannot change an existing logical Batch. Unsupported persisted providers fail terminally before provider create.
- OpenAI Batch-create HTTP 429 responses are classified as definite retryable non-creation, known validation/auth/conflict/request rejection statuses are definite terminal non-creation, and transport/5xx/uncertain outcomes remain ambiguous.
- Provider output normalization preserves the exact per-attempt `providerCustomId`; it no longer heuristically decodes it as a translation ID.
- Guarded input-file and SUBMITTED updates require exactly one affected row. A post-acceptance persistence failure becomes `SUBMISSION_UNKNOWN`, preventing replay from invoking provider create a second time.
- Retry, max-attempt and initial-poll configuration is bounded to explicit minute/attempt limits. Focused regressions cover duplicate delivery, max-attempt behavior, Redis enqueue outage, no automatic SDK retries, exact custom IDs, provider classifications and the accepted-create crash window.

### Validation Results

- `npm exec vitest run tests/unit/providers/translation.provider.test.ts tests/unit/services/translation-batch-submit.service.test.ts` - 2 files and 23 tests passed.
- `npm exec tsc -- --noEmit` - passed.
- `npm run build` - passed.
- `npm run prisma:validate` - passed.
- `npm run test:unit` - 191 passed, 3 pre-existing recovery-service failures in 2 unrelated test files.
- `git diff --check` - passed.

### Deviations

None.

### Assumptions

The provider adapter's explicit HTTP status classifications are limited to statuses that prove the request was rejected before Batch acceptance; timeout, transport and server-error outcomes remain ambiguous by design.

### Unresolved Issues

None.

### Architectural Concerns

None. Changes remain within the Attempt 2 correction contract and do not implement BACKGROUND-006 or BACKGROUND-007.

### Review Status

Ready for Architect Review.

### Coordinator Decision

`ARCH-006-BACKGROUND-006` remains Pending. `BACKGROUND-005` stays on Attempt 1 in metadata while Ready; the repository agent increments it to Attempt 2 when claiming. The separate disposable integration-test-infrastructure chain remains non-gating.

### Architect Release — 2026-09-06

`ARCH-006-BACKGROUND-004` is architect-accepted Complete. All explicit dependencies are satisfied, so BACKGROUND-005 is Ready for its first claim. The repository agent must claim only this task, implement only the bounded provider-submission capability, return it to `review`, and STOP. The separate disposable integration-test-infrastructure work does not gate this task.

### Attempt 2 Architect Review — Accepted

Independent `moda_architect` review accepts Attempt 2. The persisted Batch provider/model snapshot now selects the production provider adapter; OpenAI create failures are conservatively separated into explicit definite non-creation versus ambiguous outcomes; provider output preserves the exact historical `providerCustomId`; the input-file and accepted-Batch persistence boundaries are guarded; accepted-provider persistence failure is forced into the ambiguous path so automatic create is not repeated; and retry/poll configuration is positively bounded.

The explicit Attempt 2 correction surface stayed within the provider/submission boundary. The snapshot also contains separate `BACKGROUND-008` work already returned to `review`; that task is not accepted by this decision and remains independently reviewable.

Validation evidence recorded by the repository agent is accepted for this bounded task: 23 focused provider/submission tests, TypeScript, build, Prisma validation and `git diff --check` passed. The three unrelated recovery-suite failures remain pre-existing and non-blocking for this task.

Coordinator decision: `ARCH-006-BACKGROUND-005` is Complete. `ARCH-006-BACKGROUND-006` is released to Ready. Repository-agent prose claiming architect acceptance was not authoritative; this section is the architect decision.
