---
id: ARCH-006-DATABASE-002
architecture_id: ARCH-006
title: Add durable translation, Batch and reconciliation lifecycle state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-006-DATABASE-001
enables:
  - ARCH-006-SHARED-001
  - ARCH-006-BACKGROUND-001
  - ARCH-006-ADMIN-001
  - ARCH-006-SHOPIFY-001
created: 2026-09-05
updated: 2026-09-06T12:23:15Z
---
# ARCH-006-DATABASE-002: Add durable translation, Batch and reconciliation lifecycle state

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Add the PostgreSQL state machine that makes translation work reconstructible after Redis loss, worker restart, failed enqueue or provider-processing interruption.

## Context

PostgreSQL is the durable ledger; BullMQ is execution/scheduling only. A BullMQ job must never be the sole evidence that translation work exists. Provider Batch history is retained even when retries create a later logical batch.

## Scope

Translation records, logical provider Batch records/membership, provider-correlation fields, due-work indexes and durable Admin reconciliation requests in `moda-interact-database`.

## Out of Scope

- Queue/job schemas and job-ID helpers (`SHARED-001`).
- Provider/API calls (`BACKGROUND-*`).
- Runtime reconciliation logic.
- Deleting failed historical database Batch records.
- A database lease solely for reconciliation; correctness must not depend on one.

## Requirements

Add architecture-equivalent durable types:

```text
MerchantTranslationDirection
  MERCHANT_TO_ADMIN
  ADMIN_TO_MERCHANT
  SYSTEM_TO_MERCHANT

MerchantMessageTranslationStatus
  PENDING
  AVAILABLE
  FAILED

MerchantTranslationBatchStatus
  READY
  SUBMITTING
  SUBMISSION_UNKNOWN
  SUBMITTED
  PROVIDER_COMPLETED
  COMPLETED
  FAILED
  EXPIRED
  CANCELLED

MerchantMessageTranslation
  id
  messageId
  direction
  sourceLanguageTag
  targetLanguageTag
  status
  translatedBody? Text
  failureCode?
  retryCount DEFAULT 0
  nextAttemptAt?
  currentBatchId?
  completedAt?
  createdAt
  updatedAt
  UNIQUE(messageId, targetLanguageTag)

MerchantTranslationBatch
  id
  provider
  model
  status
  providerBatchId?
  inputFileId?
  outputFileId?
  errorFileId?
  submissionStartedAt?
  lastSubmitAttemptAt?
  submitAttemptCount DEFAULT 0
  nextSubmitAt?
  submittedAt?
  lastPolledAt?
  nextPollAt?
  pollSequence DEFAULT 0
  completedAt?
  failureCode?
  createdAt
  updatedAt

MerchantTranslationBatchItem
  batchId
  translationId
  providerCustomId
  createdAt

MerchantTranslationReconciliationRequest
  id
  requestedByPlatformAdminId
  scope
  translationId?
  status
  failureCode?
  requestedAt
  startedAt?
  completedAt?
```

Use a bounded scope enum supporting at least `TRANSLATION` and `FAILED_TRANSLATIONS`; request statuses at least `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`.

Provider identity must prevent two DB rows from claiming the same non-null provider Batch identity (provider + providerBatchId or equivalent). Batch membership must preserve history. `currentBatchId` is the current-attempt pointer and may be cleared only by later service logic after a definite terminal failure.

## Work Items

- [x] Inspect DB001 schema and current index/migration naming conventions.
- [x] Add translation/direction/status types and translation model.
- [x] Add logical Batch and Batch-item models with provider correlation.
- [x] Add durable reconciliation-request model related to `PlatformAdmin`.
- [x] Add indexes for bounded due-work queries: PENDING/retry-due translations, READY/nextSubmitAt batches, Batch status/nextPollAt, reconciliation request status/requestedAt.
- [x] Add uniqueness preventing duplicate message/target translations and duplicate provider identities/membership.
- [x] Create migration and regenerate normal DB artifacts.

## Interfaces / Contracts

Required recovery queries must be indexable and bounded, conceptually:

```text
translations requiring dispatch/retry
  status=PENDING AND currentBatchId IS NULL AND nextAttemptAt <= now/null

batches requiring submit/retry
  status=READY AND nextSubmitAt <= now/null

batches requiring poll
  status IN (SUBMITTED, ...) AND nextPollAt <= now

manual requests
  status=PENDING ordered by requestedAt
```

`SUBMISSION_UNKNOWN` is a first-class durable state: it means the provider may have accepted the create request but Moda did not safely persist the returned provider ID. It must not be represented as `READY`.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SHARED-001`, `ARCH-006-BACKGROUND-001`, `ARCH-006-ADMIN-001`, `ARCH-006-SHOPIFY-001`

## Acceptance Criteria

- [x] Direction/source/target are durable before provider work.
- [x] Translation uniqueness is `(messageId,targetLanguageTag)`.
- [x] Historical Batch membership survives retries.
- [x] `SUBMISSION_UNKNOWN` exists explicitly.
- [x] Provider Batch identity is unique when present.
- [x] Definite pre-create submission failures can be retried from durable `submitAttemptCount` + `nextSubmitAt` without relying on BullMQ retry state.
- [x] Minute-scale polling can be reconstructed from `nextPollAt` + `pollSequence`.
- [x] Admin reconciliation intent survives Redis outage.
- [x] Due-work/recovery queries have supporting indexes.
- [x] No raw provider prompt/response or credentials are persisted.

## Validation

Run repository-declared Prisma/migration/generation validation and focused tests. Verify indexes/constraints in the generated migration and run `git diff --check`.

## Implementation Notes

Do not encode authored-message grapheme length as a DB `length()` check: the rule is user-perceived Unicode graphemes and belongs in shared/server validation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260906122000_add_translation_batch_recovery_persistence/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`

### Work Completed

- Added translation direction/status, Batch lifecycle, reconciliation scope/status enums under the `support` schema.
- Added durable message translations with source/target snapshots, retry state, current-Batch pointer, completion/failure state, and `(messageId, targetLanguageTag)` uniqueness.
- Added logical provider Batches with explicit `SUBMISSION_UNKNOWN`, provider correlation fields, durable submission/poll timing and sequences, and unique non-null provider identity semantics.
- Added historical Batch membership with unique provider custom IDs and durable PlatformAdmin reconciliation requests.
- Added bounded due-work, Batch, membership, and reconciliation indexes without provider or queue runtime code.

### Validation Results

- `npm run format` passed.
- `npm run validate` passed.
- `npm run prisma:generate` passed.
- `npm run erd:puml` passed.
- `npm run erd:png` passed.
- DATABASE-001 followed by DATABASE-002 migration SQL executed successfully in one local PostgreSQL transaction and rolled back.
- `git diff --check` passed.

### Deviations

`prisma migrate dev` was not used because the local database has previously applied migration-history drift and would require a destructive reset. The additive migration was created explicitly and validated transactionally in dependency order without resetting or rewriting history.

### Assumptions

PostgreSQL nullable unique composite indexes provide uniqueness for non-null provider identities while allowing unsubmitted Batches with null `providerBatchId`; service logic owns lifecycle transitions and retry classification.

### Unresolved Issues

No blocking implementation issues. The repository has no declared focused test script for database migrations; SQL and schema validation were used as the available focused checks.

### Architectural Concerns

None within DATABASE-002. Queue contracts, provider calls, reconciliation runtime, and translation prompt/response persistence remain outside this repository task.

## Architect Review

### Review Status

Accepted by `moda_architect` on 2026-09-06 after independent review.

### Review Findings

- The schema and migration implement the DATABASE-002 durability boundary without leaking provider/queue runtime behaviour into the database repository.
- Translation direction, source/target language snapshots, retry state, `currentBatchId`, and `(messageId, targetLanguageTag)` uniqueness satisfy the architecture contract.
- Logical Batch lifecycle includes `SUBMISSION_UNKNOWN`, durable submission/poll timing, provider correlation and nullable provider identity with uniqueness for non-null `(provider, providerBatchId)`.
- Historical Batch membership is preserved independently from the translation's current Batch pointer.
- Due-work indexes support bounded translation dispatch/retry, Batch submit/poll and reconciliation-request queries.
- Durable Admin reconciliation intent survives Redis loss.
- No provider prompt/response body or credential persistence was introduced.
- The reported local `prisma migrate dev` drift is an existing environment/history condition rather than a DATABASE-002 migration defect; no destructive reset was required.

### Clarification for downstream tasks

`MerchantTranslationBatchItem.providerCustomId` is unique per historical Batch item/provider attempt. A translation retried in a later logical Batch must receive a new Batch-item custom ID while still resolving deterministically back to the same durable translation. Downstream agents must not assume one translation-stable provider `custom_id` can be reused across historical retry Batches.

### Decision

`ARCH-006-DATABASE-002` is architect-accepted and Complete. No correction attempt is required.
