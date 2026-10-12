---
id: ARCH-031
title: Automatic Merchant Pricing translations
status: implemented
coordinator: moda_architect
created: 2026-10-10
updated: 2026-10-12
---

# ARCH-031: Automatic Merchant Pricing translations

## Status

Implemented. All seven repository implementation tasks are architect-reconciled Complete and the developer manually exercised the final saved-draft -> translation -> automatic publication -> explicit activation lifecycle. During final close-out, the developer confirmed that no implementation work remains and only architectural cleanup is outstanding. `ARCH-031-SYSTEM-TEST-001` is therefore superseded rather than executed as a separate certification task; no unrun system-test evidence is claimed. For this pre-production initiative, the recorded developer integration exercise plus repository-level validation is the accepted final architectural verification.

This initiative replaces the human XLSX translation step in the Admin `MerchantPricingPlan` builder with the platform's existing durable translation runtime. During implementation the persistence boundary was deliberately revised: a saved pricing plan may exist as an **inactive English-only publication draft** while translation is running, and Background atomically publishes the exact 20-locale translation set before the plan becomes `READY`. A `READY` plan still preserves the ARCH-014 exact-completeness invariant.

This is a **pre-production / breaking rollout**. Moda Interact is still in development and no production compatibility with the manual Merchant Pricing workbook workflow is required. Existing persisted development plans remain valid and do not require backfill.

`ARCH-031` is intentionally used for this initiative. The inspected snapshot already reserves `ARCH-030` in the database migration `20261005210000_arch030_commerce_capability_shop_platform` and related Commerce capability source/validation references. This architecture does not reinterpret or rename that existing identifier.

## Problem

The current Merchant Pricing builder requires a platform administrator to:

```text
finish English merchant content
        -> download a pre-populated XLSX workbook
        -> manually translate/fill 19 non-English language rows
        -> upload the XLSX workbook
        -> validate 20/20
        -> create/save the plan
```

That workflow is now inconsistent with the current platform. The inspected 2026-10-10 snapshot already contains:

- encrypted translation provider credentials in `CommerceTranslationProviderCredential`;
- selectable translation model profiles in `CommerceTranslationModelConfiguration`;
- a generic OpenAI Batch translation provider in Background;
- durable Store Category translation run/item/batch state;
- Background reconciliation, retry, provider-correlation and result-processing machinery;
- the canonical 20 supported Moda language tags in `@modainteract/moda-interact-shared/internationalization`.

ARCH-014 correctly requires every **published/READY** `MerchantPricingPlan` and every persisted plan highlight to have an exact, complete 20-locale translation set. ARCH-031 now introduces an explicit publication lifecycle so an inactive non-READY plan may temporarily persist only its canonical English source while translation is running or failed.

The architecture therefore automates translation **without weakening the completeness invariant for READY/activatable plans and without performing external provider calls inside the Admin request or publication transaction**.

## Goals

1. The administrator authors English Merchant Pricing content only; Moda generates the other 19 supported translations automatically.
2. Keep the existing seven-step Merchant Pricing builder and keep final plan creation/save as an explicit administrator action.
3. Preserve exact 20-locale plan-description and highlight-title/description completeness before a plan becomes `READY` or active; persisted translation drafts remain inactive and English-only.
4. Preserve unchanged translations when editing only part of existing English content; do not retranslate unchanged fields unnecessarily.
5. Use the existing encrypted translation credential, model profile, OpenAI Batch provider, retry/runtime controls and merchant-communications worker rather than creating another translation provider/runtime.
6. Select the automatic translation model centrally from System Controls; the pricing-plan author does not choose a model per plan.
7. Make translation work durable before provider execution so Redis/BullMQ loss or worker restart does not lose the request.
8. Fail closed when translation is unavailable, incomplete, stale, invalid or failed. Never fall back to English for a supported merchant locale.
9. Prevent a translation result generated for stale English source or another plan handle from being applied to a different/current draft.
10. Remove the manual Merchant Pricing XLSX download/upload workflow from the normal builder after automatic translation is integrated.

## Non-Goals

- Changing Promotion Campaign XLSX translation workflow.
- Redesigning Store Category translation/enablement or its publication semantics.
- Changing Shopify/WooCommerce merchant-facing locale resolution.
- Changing the exact 20 supported Moda languages.
- Calling OpenAI synchronously from the Admin server action or inside a PostgreSQL transaction.
- Introducing a new public API, Gateway route, queue service, Redis instance or worker deployment.
- Changing provider credentials to environment variables or exposing them to browser code.
- Renaming historical migrations/source comments that already use an ARCH identifier inconsistently; that pre-existing documentation drift is outside this initiative.

## Current Architecture

### Merchant Pricing authoring

`moda-interact-admin` currently owns the seven-step builder:

```text
1 Plan
2 Catalogue placement
3 Shopify pricing
4 Usage events
5 Merchant content
6 Portfolio economics
7 Translations & review
```

Step 7 mounts `MerchantPricingTranslationWorkbook`. The client keeps `translationJson` plus a parsed validation result. `mutateMerchantPricingPlanAction` parses the canonical schema-v2 package and, when translatable content changed, creates/replaces the plan-description and highlight translation rows inside the final plan transaction.

The original builder expected the final plan write itself to be atomic and complete. Implementation evolved this into a publication lifecycle: draft persistence and translation publication are separate durable steps, while the exact-20 invariant remains authoritative for `READY` plans.

### Translation runtime already available

Current Admin/Database/Background code already provides:

```text
System Controls / Translations
        -> CommerceTranslationProviderCredential
        -> CommerceTranslationModelConfiguration

Admin Store Category translation request
        -> PostgreSQL run/item state
        -> Background TRANSLATION_RECONCILIATION lease
        -> merchant-communications queue
        -> OpenAI Batch provider
        -> durable retry / poll / results
```

Background already contains domain-neutral provider and Batch helper modules under `src/services/translation-batch-runtime/`. New Merchant Pricing work must reuse those mechanics rather than copy provider submission/correlation/retry logic.

### Existing completeness boundary

`MerchantPricingPlanTranslation` and `MerchantPricingPlanHighlightTranslation` remain the merchant-facing source of truth. The final plan transaction must still commit:

```text
20 exact plan-description translations
+ 20 exact translations for every current highlight
```

No incomplete-plan exception is introduced.

## Proposed Architecture

### A. Central automatic translation model

Extend `CommerceTranslationModelConfiguration` with one environment/provider-scoped automatic-default designation.

Required invariant:

```text
at most one enabled automatic-default translation model
per CommerceEnvironment + provider
```

The default designation is platform configuration, not part of a Merchant Pricing draft. System Controls displays the default and lets a `SUPER_ADMIN` change it with normal CAS/audit semantics.

A model may not remain the automatic default while disabled. Automatic pricing translation fails closed with a clear configuration error if there is no enabled default model or provider credential.

Store Category translation may continue to offer explicit selectable models; this initiative does not force it to use the default.

### B. Durable Merchant Pricing translation work

Add dedicated durable Merchant Pricing translation work in PostgreSQL. Do **not** reuse Store Category run tables and do not create an incomplete `MerchantPricingPlan`.

The run records at minimum:

```text
MerchantPricingTranslationRun
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
  requestedAt / startedAt / readyToApplyAt / appliedAt / completedAt
  appliedMerchantPricingPlanId?   # provenance only; no lifecycle-changing FK required
  failureCode?
```

The source snapshot contains only bounded canonical source needed to reproduce/validate translation work:

```text
English plan description
ordered current highlights:
  contentKey
  English title
  English description
```

The run is also bound to the exact `shopifyPlanHandle`. A ready run for another handle cannot be consumed.

Use dedicated item/batch/batch-item persistence parallel to the existing Store Category pattern:

```text
MerchantPricingTranslationItem
MerchantPricingTranslationBatch
MerchantPricingTranslationBatchItem
```

Items identify one translatable field and one target locale. English source items are immediately available. For edits, unchanged source fields are populated from existing persisted translations as immediately available items; only changed/new non-English fields are submitted to the provider.

A run becomes ready only when every required item for the exact canonical 20-language set is available and none failed.

### C. Automatic request from the Admin builder

When Step 7 is first entered:

```text
if edit + all English translatable content unchanged
    -> retain existing 20/20 translations
    -> no translation run
else
    -> automatically request/reuse a durable translation run
       using the configured automatic-default model
```

The browser must not send provider credentials or provider model IDs. Admin resolves the configured default server-side and snapshots the model identity/version into the run.

The request service computes a deterministic source hash from the canonical translatable source and binds it to the exact plan handle. Repeated requests for the same active/ready handle+source may reuse the same durable run; a changed source may create a new run without treating an older run as valid.

The builder polls only while its current run is non-terminal, using bounded database-backed status reads. It stops polling on ready/failed/unmount/source invalidation. Do not reload the whole billing page to poll.

Normal Step 7 UI becomes:

```text
Translations
Moda Interact translates the English merchant content automatically.

Model: <automatic default display name>
Status: Translating / 20 of 20 ready / Failed

[Retry translations]       # terminal failure only
```

The XLSX download/dropzone/import UI is removed from normal Merchant Pricing authoring.

### D. Background execution

The existing `moda-merchant-communications-worker` remains the deployment boundary.

Its existing `TRANSLATION_RECONCILIATION` leased scheduler additionally reconciles Merchant Pricing translation runs. The same merchant-communications queue carries deterministic Merchant Pricing translation Batch submit/poll/results jobs.

Reuse:

- `createOpenAITranslationProvider`;
- encrypted translation credential resolution;
- runtime-configured Batch size/poll/retry controls;
- provider submission-unknown correlation handling;
- result-file membership validation;
- item retry disposition;
- shared structured logging and existing BullMQ instrumentation.

Do not create a second OpenAI client abstraction, another queue, another translation scheduler or duplicate generic retry/correlation logic.

Provider output is validated before an item becomes available:

```text
trimmed non-empty text
plan description <= 2000
highlight title <= 120
highlight description <= 500
```

Invalid provider output follows the bounded item retry/failure policy and never reaches final Merchant Pricing persistence.

### E. Atomic final application

The canonical Merchant Pricing server mutation no longer trusts browser-supplied translated JSON for changed content.

For changed/new translatable content it receives only the selected `translationRunId`. Before committing:

1. require the run exists and is `READY_TO_APPLY`;
2. require exact `shopifyPlanHandle` match;
3. recompute the canonical source hash from the current authoritative builder payload and require exact match;
4. reconstruct the canonical schema-v2 translation package server-side from durable run items;
5. run the existing strict Merchant Pricing translation parser/validator as defence-in-depth;
6. inside the final serializable plan transaction, lock/recheck the run and prevent double consumption;
7. create/update the `MerchantPricingPlan`, exact 20 plan translations and exact highlight translations;
8. mark that run `APPLIED` with the resulting plan id in the **same transaction**.

If any recheck fails, no plan/catalogue write commits.

Edits whose translatable English source is unchanged continue to retain the existing translations without creating or consuming a run.

### F. Stale-source handling

A translation run is valid only for its snapshotted source hash and plan handle.

If an administrator navigates back and changes English description/highlight title/highlight description or adds/removes a highlight, the client invalidates the current run association. A later ready result from the old source is not silently applied.

Server-side source-hash validation is the correctness boundary; client state is only UX.

Changing non-translatable pricing/economics/model/feature fields does not invalidate an otherwise ready translation run.

### G. Failure handling

Expected states:

```text
PENDING
PROCESSING
READY_TO_APPLY
APPLIED
FAILED
STALE          # when deliberately invalidated/retired where applicable
```

A provider or item failure never creates a partial plan. The UI shows a bounded failure state and allows a new run/retry after the failure is terminal.

Background/Redis failure is recoverable from PostgreSQL reconciliation. Provider Batch submission ambiguity uses existing correlation recovery semantics.

### H. Observability

Use `@modainteract/moda-interact-shared/logging` and existing worker/BullMQ telemetry.

Required semantic events include bounded identifiers only, for example:

```text
admin.merchant_pricing.translation_requested
admin.merchant_pricing.translation_applied
background.merchant_pricing_translation.run_started
background.merchant_pricing_translation.batch_assembled
background.merchant_pricing_translation.batch_completed
background.merchant_pricing_translation.run_ready
background.merchant_pricing_translation.run_failed
```

Do not log provider credentials, full source/translated text, XLSX contents or raw provider error bodies. No new custom metric is required where existing BullMQ/HTTP instrumentation already provides the technical signal.

## Request / Event Flow

```text
SUPER_ADMIN completes valid English pricing plan
        |
        v
Save draft
        |
        v
single PostgreSQL transaction
  MerchantPricingPlan (inactive)
  publicationStatus = TRANSLATING
  currentTranslationRunId = run
  English plan/highlight translations only
        |
        v
PostgreSQL MerchantPricingTranslationRun + Items
        |
        | durable acceptance point
        v
Background reconciliation / merchant-communications jobs
        |
        v
OpenAI Batch provider
        |
        v
PostgreSQL translation items AVAILABLE / FAILED
        |
        +---- terminal failure ----> run FAILED/STALE
        |                            plan TRANSLATION_FAILED / inactive
        |
        v
run READY_TO_APPLY
        |
        v
Background publication transaction
  lock run + linked draft
  revalidate handle/source/hash/exact item set
  replace plan/highlight translations with exact 20 locales
  plan publicationStatus -> READY
  plan remains inactive
  currentTranslationRunId -> null
  run -> APPLIED with plan provenance
        |
        v
Admin explicitly activates READY plan
```

Translation starts only after an explicit draft save. Merely entering Step 7 does not create work. Reorder-only or non-translatable edits preserve existing translations and avoid provider work where source identity is unchanged.

## Repository Responsibilities

### `moda-interact-database`

- `DATABASE-001`: automatic-default model invariant plus durable Merchant Pricing translation run/item/batch persistence;
- `DATABASE-002`: explicit Merchant Pricing publication lifecycle (`TRANSLATING`, `TRANSLATION_FAILED`, `READY`), linked current run, inactive-draft constraints and READY exact-completeness enforcement;
- migration/schema validators and fresh/upgrade PostgreSQL rehearsals.

### `moda-interact-admin`

- configure the automatic-default translation model;
- create/reuse durable translation runs and expose bounded status reads;
- save an inactive English-only plan draft linked to the current run;
- start/retry translation only from explicit save/retry actions;
- poll persisted work without page reload or workbook controls;
- preserve translations on reorder-only/non-translatable edits;
- require explicit activation after the plan becomes `READY`.

### `moda-interact-background`

- `BACKGROUND-001`: reconcile Merchant Pricing translation runs, assemble/submit/poll/process Batch work and advance runs to terminal translation state;
- `BACKGROUND-002`: atomically publish a `READY_TO_APPLY` run into the linked inactive draft, revalidate source identity/exact results, leave the plan `READY` and inactive, and record failure/stale outcomes without partial publication.

### `moda-interact-system-test`

- terminally validate the integrated saved-draft -> translation -> automatic publication -> explicit activation workflow, stale-source protection, retries/failure, exact 20-locale persistence and unchanged-edit retention without live paid credentials.

### No new task required

- `moda-interact-shared`: existing internationalization/logging contracts are sufficient; no new cross-service runtime contract is required because Admin and Background coordinate through PostgreSQL and Background-owned queue jobs.
- `moda-interact-gateway`: no new service, route, environment variable or deployment topology is required.
- `moda-interact`: merchant-facing reads continue to consume only READY/active complete plans.

## Data Model

Translation work is durable staging/provenance. Merchant Pricing now also has an explicit publication state:

```text
MerchantPricingPlanPublicationStatus
  TRANSLATING
  TRANSLATION_FAILED
  READY

MerchantPricingPlan.currentTranslationRunId?
```

Required integrity includes:

- an active plan must be `READY`;
- a non-READY plan must remain linked to its current translation run;
- the linked run handle must match the plan handle;
- `READY` plans/highlights must have the exact canonical 20-locale set;
- non-READY plans/highlights contain only canonical English source rows;
- provider/model/source identifiers are bounded and nonblank;
- source hash is lowercase SHA-256 hex;
- one item per run/source field/target locale;
- Batch membership is immutable historical evidence;
- provider Batch identity is unique where non-null;
- retry/poll counters are non-negative;
- an automatic-default model must be enabled;
- at most one automatic-default model exists per environment/provider.

## Contracts

No new published Shared package contract is required.

Cross-repository coordination is PostgreSQL state owned by `moda-interact-database`:

```text
Admin producer:
  MerchantPricingPlan publication draft
  MerchantPricingTranslationRun / Item

Background consumer/updater:
  MerchantPricingTranslationRun / Item / Batch / BatchItem

Background publisher:
  READY_TO_APPLY run + linked TRANSLATING plan
  -> exact 20-locale READY plan + APPLIED run

Admin activation:
  READY inactive plan -> active plan
```

Background queue payloads remain internal to `moda-interact-background`, because Background is both producer and consumer of those jobs.

Canonical language identifiers come from `@modainteract/moda-interact-shared/internationalization`.

## Consistency and Transactions

- Draft save persists the inactive plan/source and durable translation linkage transactionally; it is the durable acceptance boundary for a saved translation draft.
- Redis/BullMQ publication is asynchronous/reconstructible; no Redis operation belongs inside the Admin transaction.
- Background assumes duplicate, delayed and retried jobs and uses deterministic identities/reconciliation.
- Translation publication is a serializable PostgreSQL transaction that locks/revalidates the run and linked plan before replacing translations and transitioning the run/plan together.
- No external provider call occurs inside a database transaction.
- `READY_TO_APPLY` is not sufficient by itself; plan handle, source schema/hash/snapshot, current English source and exact available item membership are revalidated at publication.
- A published plan remains inactive until an administrator explicitly activates it.

## Ordering

No global serialization is required.

- Translation Batch work may execute concurrently across pricing plans/runs.
- One translation item belongs to one current Batch at a time.
- Final publication serializes only the run/linked plan transaction being finalized.
- Catalogue ordering continues to use the existing Merchant Pricing transaction rules; translation work does not become the catalogue-order authority.

## Failure Handling

- Missing automatic-default model/credential: Admin fails closed before provider work exists.
- Provider definite retryable failure: existing bounded retry policy applies.
- Ambiguous Batch submission: existing provider correlation recovery applies.
- Invalid/missing/duplicate provider result membership: fail closed using existing Batch safety rules.
- Invalid/oversized translated text: item retry/failure; never publish invalid translations.
- Background crash/Redis loss: PostgreSQL reconciliation repairs work.
- Source changed after request: publication marks/rejects the stale run rather than applying it to changed source.
- Terminal run failure/stale state: linked draft becomes `TRANSLATION_FAILED` and remains inactive.
- Double publication: row locks/status predicates plus run/plan transition guards prevent double consumption.
- Publication success: plan becomes `READY` but remains inactive; activation is a separate Admin action.

## Scalability

Merchant Pricing translation is low-frequency internal Admin work and is not tied to Shopify webhook volume. It reuses the existing merchant-communications worker and Batch limits.

Avoid translating unchanged fields. For a plan with `H` highlights, a brand-new plan has at most:

```text
19 * (1 + 2H)
```

provider translation requests because English is immediately available. Existing Background `translationBatchMaxRequests`, reconciliation page size, retry and poll controls continue to bound work.

## Security

- All configuration and Merchant Pricing mutations remain `SUPER_ADMIN` protected.
- Provider credentials remain encrypted at rest and server-side only.
- Browser receives only bounded run/model status, never credentials/ciphertext/provider API responses.
- Do not log source/translated merchant text by default.
- Server-side source/hash validation prevents translated result substitution or stale publication.
- Non-READY plans cannot be activated.

## Observability

Application semantic logging belongs to Admin and Background respectively and uses the Shared logger. Background records translation/publication outcome identifiers and counts without translation text or provider secrets. Existing OpenTelemetry/BullMQ telemetry remains the technical transport/queue signal. No new Gateway observability task is required.

## Rollout / Migration

Classification: **PRE-PRODUCTION / BREAKING ROLLOUT**.

Final implementation sequence:

```text
1. ARCH-031-DATABASE-001    automatic default + durable translation work state
2. ARCH-031-ADMIN-001       configure automatic default
3. ARCH-031-ADMIN-002       request/status/server translation orchestration
4. ARCH-031-BACKGROUND-001  execute durable translation runs
5. ARCH-031-DATABASE-002    add persisted pricing publication lifecycle
6. ARCH-031-ADMIN-003       save inactive English draft; automatic UI/retry/poll flow
7. ARCH-031-BACKGROUND-002  automatically publish completed translations into draft
8. developer manual validation
9. final architect reconciliation; `ARCH-031-SYSTEM-TEST-001` superseded as no longer required for this pre-production close-out
```

No existing Merchant Pricing rows require backfill in development. The publication lifecycle migration defaults existing rows to `READY`; new/changed translatable drafts use the new lifecycle. Backwards compatibility with the removed manual Merchant Pricing XLSX workflow is not required.

The developer manually exercised the final lifecycle as:

```text
complete valid plan
-> Save draft
-> translation starts only after save
-> Draft · Translating / inactive
-> 20/20 translation
-> automatic finalisation
-> READY / inactive
-> Admin explicitly activates
-> Active
```

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-031-DATABASE-001 | moda_database | Complete | - |
| ARCH-031-ADMIN-001 | moda_admin | Complete | ARCH-031-DATABASE-001 |
| ARCH-031-ADMIN-002 | moda_admin | Complete | ARCH-031-DATABASE-001 |
| ARCH-031-BACKGROUND-001 | moda_background | Complete | ARCH-031-DATABASE-001 |
| ARCH-031-DATABASE-002 | moda_database | Complete | ARCH-031-DATABASE-001, ARCH-031-BACKGROUND-001 |
| ARCH-031-ADMIN-003 | moda_admin | Complete | ARCH-031-ADMIN-001, ARCH-031-ADMIN-002, ARCH-031-DATABASE-002 |
| ARCH-031-BACKGROUND-002 | moda_background | Complete | ARCH-031-BACKGROUND-001, ARCH-031-DATABASE-002, ARCH-031-ADMIN-003 |
| ARCH-031-SYSTEM-TEST-001 | moda_system_test | Superseded | all seven ARCH-031 implementation tasks |

Execution graph:

```text
ARCH-031-DATABASE-001
        |
        +------> ARCH-031-ADMIN-001
        +------> ARCH-031-ADMIN-002
        +------> ARCH-031-BACKGROUND-001 ----+
                                              v
                                  ARCH-031-DATABASE-002
                                              |
ARCH-031-ADMIN-001 ---------------------------+
ARCH-031-ADMIN-002 ---------------------------+--> ARCH-031-ADMIN-003
                                                       |
ARCH-031-BACKGROUND-001 -------------------------------+
ARCH-031-DATABASE-002 ---------------------------------+--> ARCH-031-BACKGROUND-002
                                                               |
                                                               v
                                                 final architect reconciliation
                                                 SYSTEM-TEST-001 superseded
```

## Open Questions

None. The developer confirmed at final close-out that no implementation work remains. No separate ARCH-031 system-test execution is required for this pre-production initiative; `SYSTEM-TEST-001` is superseded without claiming test evidence that was not produced.

## Change History

- 2026-10-10: Initial agreed architecture based on inspection of `moda-interact-workspace(20261010-091041).zip`; automatic Merchant Pricing translation reuses the existing durable translation provider/runtime and preserves complete-plan publication.
- 2026-10-10: Task decomposition simplified by combining the default-model designation and Merchant Pricing translation work-state schema into `ARCH-031-DATABASE-001`; no architectural runtime behaviour changed.
- 2026-10-11: Implementation reconciliation recorded the persisted publication-draft lifecycle discovered during implementation: draft save persists English-only inactive state; Background performs atomic 20-locale publication; explicit activation follows `READY`. Added retrospective `DATABASE-002` and `BACKGROUND-002` task records.
- 2026-10-11: All seven implementation tasks reconciled Complete after source review and developer validation; `SYSTEM-TEST-001` promoted to Ready. Architecture remains In Progress pending terminal system-test acceptance.

- 2026-10-12: Final architectural close-out. Developer confirmed only architectural cleanup remained; all seven implementation tasks stay Complete, `SYSTEM-TEST-001` is explicitly Superseded without fabricated execution evidence, and ARCH-031 is marked Implemented based on repository-level validation plus the recorded end-to-end manual lifecycle exercise.
