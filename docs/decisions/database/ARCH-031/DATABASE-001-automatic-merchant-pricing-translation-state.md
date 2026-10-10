---
id: ARCH-031-DATABASE-001
architecture_id: ARCH-031
title: Persist automatic Merchant Pricing translation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-031-ADMIN-001
  - ARCH-031-ADMIN-002
  - ARCH-031-BACKGROUND-001
created: 2026-10-10
updated: 2026-10-10
---

# Persist automatic Merchant Pricing translation state

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Provide all durable PostgreSQL state required for automatic Merchant Pricing translation: a centrally designated automatic/default translation model plus dedicated run/item/batch staging state, without creating incomplete `MerchantPricingPlan` rows or weakening the existing exact-20-locale completeness invariant.

## Context

The current database already owns `CommerceTranslationProviderCredential` and `CommerceTranslationModelConfiguration`, but no model is designated as the automatic default. The inspected snapshot also contains a durable Store Category translation state machine and a proven Background Batch provider runtime, while Merchant Pricing itself has only final `MerchantPricingPlanTranslation` / `MerchantPricingPlanHighlightTranslation` rows and currently requires a complete workbook before the final plan transaction.

ARCH-031 needs both pieces of database capability before Admin or Background can implement the automatic workflow:

```text
CommerceTranslationModelConfiguration
    + automatic/default designation

MerchantPricingTranslationRun
MerchantPricingTranslationItem
MerchantPricingTranslationBatch
MerchantPricingTranslationBatchItem
```

They form one bounded database outcome: the durable state contract consumed by the ARCH-031 Admin and Background tasks. The staging state is not merchant-facing plan data and remains separate from the existing final Merchant Pricing tables.

## Scope

Within `moda-interact-database` only:

- extend `CommerceTranslationModelConfiguration` with a durable automatic/default designation;
- add database constraints/indexes enforcing the default-model invariant;
- define Merchant Pricing translation run lifecycle enum(s);
- define translation item identity/status persistence;
- define Batch and historical Batch-item membership persistence;
- relate runs to the existing `CommerceTranslationModelConfiguration` and requesting `PlatformAdmin`;
- retain bounded model/provider/source snapshots for reproducibility;
- add indexes/checks/partial uniqueness needed for reconciliation, retry, polling and final consumption;
- add forward migration(s) plus focused validators/rehearsals;
- validate fresh-empty-database and current-schema upgrade paths using repository conventions.

Expected conceptual models:

```text
MerchantPricingTranslationRun
MerchantPricingTranslationItem
MerchantPricingTranslationBatch
MerchantPricingTranslationBatchItem
```

Use the existing `billing` schema for Merchant Pricing translation work unless inspection establishes a concrete database-integrity reason otherwise. Cross-schema references to the existing translation model configuration are permitted when represented safely by Prisma/PostgreSQL.

## Out of Scope

- Admin UI/actions for choosing the automatic/default model;
- Admin request/status/final-apply services;
- Background workers/reconciliation;
- final `MerchantPricingPlan` schema redesign;
- allowing incomplete or partially translated Merchant Pricing plans;
- translating or writing provider output;
- changing provider credential encryption or provider identity;
- changing Store Category translation run semantics;
- Store Category translation table refactor/rename;
- genericising all historical translation tables into one polymorphic super-table;
- cleanup/retention jobs for old terminal runs;
- hard-coding or seeding a provider model ID, credential or automatic default;
- Shared contracts or queue definitions;
- any `_index.md` update.

## Requirements

### R1 — automatic/default translation model designation

Add a boolean field to `CommerceTranslationModelConfiguration` with a clear schema name representing the automatic/default designation. Prefer `automaticDefault` unless repository naming conventions establish a better equivalent.

Required invariants:

```text
at most one automatic default per exact (environment, provider)
automaticDefault = true -> enabled = true
```

Additional rules:

1. Existing rows default to `false`; the migration must not guess among existing enabled models.
2. Use a partial unique index or equivalent database constraint that permits multiple non-default rows for the same environment/provider.
3. Do not make all model rows mutually unique by a boolean composite key.
4. Preserve existing uniqueness on `(environment, provider, providerModelId)` and `(environment, displayName)`.
5. Preserve existing credential foreign-key behaviour and `editVersion` semantics.
6. A fresh production database legitimately has no automatic default until a `SUPER_ADMIN` configures one.
7. Do not seed provider credentials, provider model IDs or a default model.
8. No existing Store Category translation run may be rewritten merely because this designation is added.

### R2 — run identity and lifecycle

Persist a Merchant Pricing translation run with at least:

```text
id
shopifyPlanHandle
environment
translationModelConfigurationId
provider
providerModelId
modelConfigurationVersion
sourceSchemaVersion
sourceHash
sourceSnapshot
status
requestedByAdminId
requestedAt
startedAt?
readyToApplyAt?
appliedAt?
completedAt?
appliedMerchantPricingPlanId?
failureCode?
createdAt
updatedAt
```

The exact physical field names may follow repository conventions, but the semantics above are required.

Required status vocabulary:

```text
PENDING
PROCESSING
READY_TO_APPLY
APPLIED
FAILED
STALE
```

`APPLIED`, `FAILED` and `STALE` are terminal for provider work. A final plan mutation may consume only `READY_TO_APPLY`.

### R3 — source identity

`sourceHash` is lowercase SHA-256 hex and represents the canonical translatable source snapshot. The run is also bound to an exact `shopifyPlanHandle`.

`sourceSnapshot` is JSONB and contains bounded English plan/highlight source sufficient for deterministic validation/reconstruction. The database need not validate every JSON field semantically, but it must bound the schema version/hash/provider/model metadata structurally.

Do not persist browser XLSX bytes or arbitrary provider request/response bodies.

### R4 — active/reusable duplicate protection

Permit a new run after source changes, but prevent duplicate active work for the same exact plan handle/source hash.

Required uniqueness concept:

```text
(shopifyPlanHandle, sourceHash)
WHERE status IN (PENDING, PROCESSING, READY_TO_APPLY)
```

An already `APPLIED`, `FAILED` or `STALE` run must not block a later run.

### R5 — item model

Every item identifies exactly one source field and target locale. The schema must distinguish:

```text
plan description
highlight title
highlight description
```

and preserve the stable highlight `contentKey` where the source belongs to a highlight.

Each item stores at least:

```text
runId
source kind/key/field
sourceLanguageTag
targetLanguageTag
sourceText
translatedText?
status
failureCode?
retryCount
nextAttemptAt?
currentBatchId?
completedAt?
createdAt
updatedAt
```

Required item statuses:

```text
PENDING
AVAILABLE
FAILED
```

The unique item identity must prevent duplicate entries for the same run/source-field/target-language combination.

English and retained existing translations may be inserted as `AVAILABLE` immediately by Admin; the database must allow this.

### R6 — Batch lifecycle

Batch persistence must preserve the existing translation provider safety model:

```text
READY
SUBMITTING
SUBMISSION_UNKNOWN
SUBMITTED
PROVIDER_COMPLETED
COMPLETED
FAILED
EXPIRED
CANCELLED
```

Store at least:

```text
runId
provider
model
providerBatchId?
inputFileId?
outputFileId?
errorFileId?
submissionStartedAt?
lastSubmitAttemptAt?
submitAttemptCount
nextSubmitAt?
submittedAt?
lastPolledAt?
nextPollAt?
pollSequence
completedAt?
failureCode?
```

Historical `MerchantPricingTranslationBatchItem` membership is immutable evidence and uses a unique provider custom id per historical Batch membership/attempt.

### R7 — indexes and query patterns

Add bounded indexes supporting:

- pending runs ordered by request time;
- processing/ready runs;
- pending/retry-due items;
- run+target-locale item reads;
- ready/next-submit Batch reads;
- submitted/next-poll Batch reads;
- provider Batch identity/correlation;
- final run lookup by exact id/status;
- active/reusable run lookup by handle+source hash.

Do not create broad indexes without a documented query.

### R8 — existing final Merchant Pricing integrity remains unchanged

The migration MUST NOT weaken/drop/disable any ARCH-014 completeness constraint or trigger governing:

```text
MerchantPricingPlan
MerchantPricingPlanTranslation
MerchantPricingPlanHighlight
MerchantPricingPlanHighlightTranslation
```

No existing plan translation row is migrated into staging work. Existing development plans remain untouched.

### R9 — relations and deletion

- translation model configuration and requesting admin use restrictive durable provenance relations;
- run -> item/batch and batch -> membership may cascade on run deletion if run deletion is ever explicitly allowed by Prisma, but this task does not add a normal delete workflow;
- `appliedMerchantPricingPlanId` is provenance and MUST NOT introduce a foreign key that prevents legitimate plan deletion unless the parent architecture is explicitly amended. Prefer bounded text/id snapshot semantics or `SET NULL` only if a concrete relation is justified.

## Work Items

- [ ] Inspect the current `CommerceTranslationModelConfiguration` schema and originating migration.
- [ ] Inspect current Store Category translation migration/schema solely to reuse proven integrity patterns without coupling the domains.
- [ ] Add the automatic/default field to Prisma.
- [ ] Add Merchant Pricing translation enums/models to Prisma.
- [ ] Add forward SQL migration(s) with automatic-default integrity, run/item/batch checks, indexes and partial uniqueness.
- [ ] Add any required inverse relations on `CommerceTranslationModelConfiguration` / `PlatformAdmin` without changing their runtime semantics.
- [ ] Add focused schema/migration validator coverage for the default designation, statuses, constraints, indexes and final-plan non-regression.
- [ ] Rehearse migration on a fresh empty PostgreSQL database.
- [ ] Rehearse upgrade from the current snapshot schema with existing translation model rows defaulting safely to non-default.
- [ ] Record exact validation evidence in the Completion Report.

## Interfaces / Contracts

Produces durable database capability consumed by:

- `ARCH-031-ADMIN-001` — audited automatic/default model selection;
- `ARCH-031-ADMIN-002` — automatic model resolution plus Merchant Pricing translation request/status/final-package state;
- `ARCH-031-BACKGROUND-001` — Merchant Pricing translation execution/reconciliation state.

No queue payload crosses repository ownership; Background owns its own queue jobs.

Canonical language values remain `@modainteract/moda-interact-shared/internationalization` at application/runtime level. The database stores bounded BCP-47 strings and does not create a second language enum.

No Shared package contract is introduced.

## Dependencies

None.

## Enables

- `ARCH-031-ADMIN-001`.
- `ARCH-031-ADMIN-002`.
- `ARCH-031-BACKGROUND-001`.

## Acceptance Criteria

- [ ] Two non-default model configurations can coexist in the same environment/provider.
- [ ] One enabled model may be marked automatic default.
- [ ] A second automatic default in the same environment/provider is rejected by PostgreSQL.
- [ ] A default model cannot be persisted disabled.
- [ ] Defaults in different environments remain independent.
- [ ] Existing model/credential uniqueness and foreign keys are unchanged.
- [ ] A durable Merchant Pricing translation run may exist before any `MerchantPricingPlan` exists.
- [ ] No incomplete `MerchantPricingPlan` row is required for translation processing.
- [ ] Duplicate active work for the same handle/source hash is rejected or safely reusable by the database invariant.
- [ ] Changed source hash can create a separate new run.
- [ ] Every translation item has one unambiguous source field and target locale.
- [ ] One item can belong to only one current Batch while retaining historical Batch membership.
- [ ] Provider Batch identity is unique when present and retry/poll counters cannot be negative.
- [ ] The schema supports reconstructing pending/retry/poll work after Redis loss.
- [ ] Existing ARCH-014 exact-20 translation/completeness constraints are byte-for-byte or semantically unchanged by the migration.
- [ ] Existing Merchant Pricing rows require no backfill.
- [ ] A fresh migration deployment succeeds with no translation configuration rows and no hard-coded provider/model/default seed.
- [ ] Fresh and upgrade migration rehearsals pass.

## Validation

- [ ] repository Prisma validation command.
- [ ] focused ARCH-031 schema/migration validator covering automatic-default and Merchant Pricing translation work state.
- [ ] fresh PostgreSQL migration rehearsal.
- [ ] current-schema upgrade rehearsal.
- [ ] explicit assertion that no existing ARCH-014 completeness object is removed/weakened.
- [ ] `git diff --check`.

If Docker/PostgreSQL is unavailable, do not represent migration rehearsal as passed; record the exact blocked check in the Completion Report.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Admin or Background implementation.

## Implementation Notes

The automatic default is configuration policy, not a model capability. Keep the existing translation model row as the owner rather than introducing a hard-coded `gpt-*` setting. Prisma does not need to model a partial unique index as a normal `@@unique`; preserve the PostgreSQL invariant even if Prisma cannot fully express it declaratively.

Use the Store Category state machine as evidence for proven Batch fields/index patterns, not as a table to overload with a second subject type. ARCH-031 intentionally uses dedicated Merchant Pricing staging tables because Store Category publication has category/template/mapping semantics that Merchant Pricing does not share.

The combined task is intentionally one database unit: both the default-model designation and translation work state are required to expose the complete durable schema contract consumed by Admin and Background.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.
