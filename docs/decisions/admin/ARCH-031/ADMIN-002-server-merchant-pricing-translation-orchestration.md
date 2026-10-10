---
id: ARCH-031-ADMIN-002
architecture_id: ARCH-031
title: Add server-side Merchant Pricing translation orchestration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-DATABASE-001
enables:
  - ARCH-031-ADMIN-003
created: 2026-10-10
updated: 2026-10-10
---

# Add server-side Merchant Pricing translation orchestration

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Add the Admin server/service boundary that creates or reuses durable Merchant Pricing translation runs, exposes bounded run status, preserves unchanged edit translations, and reconstructs a ready canonical translation package for later final plan application.

## Context

The current builder owns a browser-facing XLSX adapter around `parseCompletedMerchantPricingTranslationPackage(...)`. ARCH-031 keeps that strict canonical parser as defence-in-depth but removes the human translation step in a later task.

DATABASE-001 introduces the automatic/default model designation and durable Merchant Pricing translation work. This task makes Admin the producer of that work and the server-side reader/assembler of completed work. It deliberately leaves the existing workbook UI/final action behaviour intact so this task can be accepted independently before ADMIN-003 switches the builder.

## Scope

Within `moda-interact-admin` only:

- canonical Merchant Pricing translation source snapshot/hash helpers;
- default-model resolution for automatic translation requests;
- request/reuse transaction for run/items;
- existing-translation retention for unchanged fields on edit;
- bounded status read model/server action;
- server-only reconstruction of a ready schema-v2 Merchant Pricing translation package;
- strict validation of ready results using the existing canonical parser;
- focused tests and shared-logger semantic events.

Expected new/focused modules may include:

```text
src/lib/admin/merchant/merchant-pricing-automatic-translations.ts
src/lib/admin/merchant/merchant-pricing-translation-runs.ts
src/app/actions/merchant-pricing-translations.ts
focused unit/security tests
```

Exact local decomposition is owned by `moda_admin`; keep request validation, persistence access and UI/action wrappers separated rather than creating another monolithic builder file.

## Out of Scope

- replacing/removing the XLSX UI; owned by `ARCH-031-ADMIN-003`;
- changing `mutateMerchantPricingPlanAction` to consume a run; owned by ADMIN-003 final integration;
- Background Batch execution;
- Prisma/migration edits;
- Store Category translation behaviour;
- Promotion translation workbook;
- client-side polling/state;
- a new shared package contract;
- any `_index.md` update.

## Requirements

### R1 — canonical source identity

Define one canonical server-safe source shape:

```text
schemaVersion: 1
shopifyPlanHandle
englishDescription
highlights[]:
  contentKey
  title
  description
```

Normalize using the same trim/source semantics as existing Merchant Pricing translation validation.

For hashing, highlights MUST be canonicalized by stable `contentKey`, not catalogue display order, so reordering a highlight alone preserves translation validity as ARCH-014 already requires.

`sourceHash` is SHA-256 of deterministic canonical JSON. `displayName`, pricing, economics, feature mappings, Commerce model and usage events are not translatable source and MUST NOT invalidate a ready translation run.

The exact `shopifyPlanHandle` is part of the run binding and must be included in or separately enforced alongside the hash.

### R2 — prove locale-set equivalence

Automatic work uses `MODA_SUPPORTED_LANGUAGE_TAGS` from `@modainteract/moda-interact-shared/internationalization`.

Add a focused assertion proving the existing `MERCHANT_PRICING_LOCALES` set is exactly equal to the Shared supported-language set. Order may differ, but no locale may be missing/extra. Do not introduce a third locale registry.

### R3 — automatic-default model resolution

Resolve the translation model server-side for the current Commerce environment:

```text
provider = existing supported translation provider
active/enabled model
automaticDefault = true
credential exists
```

If no valid default exists, return a bounded client message such as:

```text
Automatic translation is not configured. Choose an automatic-default translation model in System Controls / Translations.
```

Do not select the first enabled row and do not accept a browser-supplied model id for Merchant Pricing automatic translation.

### R4 — request/reuse transaction

The request path requires `SUPER_ADMIN` and validates the current Merchant Pricing builder payload/source with existing canonical helpers.

Inside one bounded PostgreSQL transaction:

1. resolve/verify the automatic-default model and credential state;
2. build canonical source/hash;
3. find a reusable run for exact handle+source hash in `PENDING`, `PROCESSING` or `READY_TO_APPLY` and return it if present;
4. otherwise create one run with snapshotted environment/provider/model/model-version/source metadata;
5. create the exact required item set;
6. write bounded audit evidence if the accepted database audit model supports it; if a new audit enum/action is required but DATABASE-001 did not authorize it, STOP and return that schema dependency rather than inventing unaudited work.

No Redis/BullMQ/provider call occurs in this transaction.

### R5 — item generation and retention

For a brand-new plan:

- English source fields are `AVAILABLE` immediately with source text;
- every non-English required field is `PENDING`.

For an existing plan edit:

- compare current English plan description to persisted English source;
- compare highlights by stable `contentKey` and source title/description;
- for every unchanged source field, populate all 20 item values from existing persisted translations as `AVAILABLE`;
- for changed/new source fields, English is `AVAILABLE` and only 19 non-English items are `PENDING`;
- removed highlights create no items;
- reorder only does not cause retranslation.

If existing persisted translations violate the current exact-locale invariant, fail closed rather than manufacturing fallback values.

### R6 — status read

Expose a bounded status result suitable for client polling, including at least:

```text
runId
status
model display name
completeLocaleCount   # locale complete only when all fields for that locale are AVAILABLE
localeCount = 20
pendingItemCount
failedItemCount
failureCode?
```

Status reads require platform-admin authorization and do not expose source/translated text, provider file ids, credentials or raw provider errors.

### R7 — ready-package reconstruction

Add a server-only helper used later by ADMIN-003 that:

1. loads the run and exact item set;
2. requires `READY_TO_APPLY`;
3. requires exact handle/source hash supplied by the current authoritative draft;
4. verifies every required field exists exactly once for each exact Merchant Pricing locale;
5. reconstructs `MerchantPricingTranslationPackage` schemaVersion 2 keyed by current highlight `contentKey`;
6. calls `parseCompletedMerchantPricingTranslationPackage(...)` against the current expected source;
7. returns only a valid canonical package or fails closed.

Do not trust `translatedText` merely because a run status is ready.

### R8 — observability

Use the Shared logger. Emit bounded semantic request/failure events such as:

```text
admin.merchant_pricing.translation_requested
admin.merchant_pricing.translation_request_failed
```

Log run id, handle/source hash only when policy permits bounded identifiers, model configuration id and counts. Do not log full source/translated text or provider credential material.

## Work Items

- [ ] Consume accepted DATABASE-001 schema/gitlink.
- [ ] Add canonical source snapshot/hash helpers with reorder-invariant tests.
- [ ] Add Shared-vs-MerchantPricing locale equality test.
- [ ] Add automatic-default model resolver.
- [ ] Add request/reuse persistence service with edit retention semantics.
- [ ] Add authorized request/status server actions.
- [ ] Add ready-package reconstruction + strict parser validation helper.
- [ ] Add structured logging and bounded error mapping.
- [ ] Add focused unit/security tests for create, partial edit retention, reorder-only retention, stale source, missing default and duplicate request reuse.
- [ ] Run repository-focused validation and record results.

## Interfaces / Contracts

Consumes database state from:

- `ARCH-031-DATABASE-001` automatic-default field plus Merchant Pricing translation runs/items/batches.

Consumes existing Shared:

```text
@modainteract/moda-interact-shared/internationalization
@modainteract/moda-interact-shared/logging
```

Produces server functions/actions consumed by `ARCH-031-ADMIN-003`.

Background has no dependency on an Admin-specific TypeScript contract; it consumes the database state directly.

## Dependencies

- `ARCH-031-DATABASE-001`.


## Enables

- `ARCH-031-ADMIN-003`.

## Acceptance Criteria

- [ ] Merchant Pricing automatic requests never accept a browser-selected translation model id.
- [ ] Missing/disabled default or missing credential fails before provider work exists.
- [ ] A create run has English available and exactly the required non-English pending items.
- [ ] Editing one source field reuses all unchanged persisted translations and translates only changed/new non-English fields.
- [ ] Highlight reorder alone requires no new translation content.
- [ ] Repeated request for identical active handle/source reuses durable work rather than creating duplicate active runs.
- [ ] Status response exposes progress but no translation/provider secret content.
- [ ] A ready run from another handle or old source hash cannot reconstruct a valid package.
- [ ] Reconstructed package passes the existing strict schema-v2 parser and exact 20-locale/highlight checks.
- [ ] Existing workbook UI and current final mutation remain operational in this intermediate task state.

## Validation

- [ ] focused unit tests for canonical source/hash and retention.
- [ ] focused unit/integration tests for request/reuse/status/ready-package services using repository-supported database fixtures where available.
- [ ] security tests for SUPER_ADMIN mutation boundary and bounded status reads.
- [ ] `npm run lint` or exact repository-declared lint for changed files.
- [ ] `npm run build` if required by repository validation conventions.
- [ ] `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, set status to `review`, return the Completion Report to `moda_architect` and STOP. Do not remove the workbook UI or switch the final mutation yet.

## Implementation Notes

Preserve the existing strict translation parser as the final content validator; automatic translation changes how the canonical package is produced, not what a valid Merchant Pricing translation package means.

Do not put Prisma/database calls into React components. Keep the request/status/persistence boundary server-side and modular so ADMIN-003 remains mostly UI/controller integration.

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
