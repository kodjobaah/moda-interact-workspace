---
id: ARCH-024-DATABASE-001
architecture_id: ARCH-024
title: Persist Model Catalogue availability, Price Plan model assignment and OpenRouter credentials
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: copilot
claimed_at: 2026-10-01T14:29:54Z
attempt: 1
depends_on: []
enables:
  - ARCH-024-SHARED-001
created: 2026-09-30
updated: 2026-10-01
---

# Persist Model Catalogue availability, Price Plan model assignment and OpenRouter credentials

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-model-availability-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Evolve the existing ARCH-021 Commerce model persistence into the complete ARCH-024 database boundary in one pre-production breaking migration: persist Platform/Shop Model Availability, make every `CommerceModelCatalogueEntry` belong to exactly one Availability, replace the closed `CommerceModelProvider` enum with durable `provider + providerModelId` strings, add versioned JSON model configuration, add one optional `MerchantPricingPlan.commerceModelId` association for product-tier model selection, and persist one encrypted hot-swappable OpenRouter credential per `CommerceEnvironment`.

## Context

The current database already contains:

```text
commerce.CommerceModelCatalogueEntry
    id
    provider                 CommerceModelProvider enum: OPENAI | GROQ
    providerModelId
    displayName
    description
    enabled
    editVersion
    createdByAdminId
    updatedByAdminId

commerce.CommerceAgentConfiguration
    environment
    scope                    PLATFORM | SHOP
    shopId?
    modelId?                 FK -> CommerceModelCatalogueEntry.id
    activePromptRevisionId?
    modelEditVersion
    promptEditVersion
```

The current model catalogue is global. ARCH-024 separates three concepts:

```text
Model Availability
    where a model may be selected

Model Catalogue Entry
    which model exists and its validated runtime configuration

Agent Configuration
    which one available model is selected for Platform or a Shop

Merchant Pricing Plan
    which optional Platform-available model is the default benefit for subscribers to that pricing tier
```

The target ownership is:

```text
CommerceModelAvailability (PLATFORM)
        |
        +-- CommerceModelCatalogueEntry A
        +-- CommerceModelCatalogueEntry B
        +-- CommerceModelCatalogueEntry C

CommerceModelAvailability (SHOP -> shop X)
        |
        +-- CommerceModelCatalogueEntry D
        +-- CommerceModelCatalogueEntry E
```

Every catalogue entry belongs to exactly one Availability. One Platform Availability exists globally. A Shop may have at most one Shop Availability. An Availability may temporarily contain zero entries while an Admin is authoring it; the durable relationship is one Availability to zero-or-more entries, with every entry having exactly one non-null Availability.

ARCH-024 also adds this one-way product-tier association:

```text
billing.MerchantPricingPlan.commerceModelId?
    -> commerce.CommerceModelCatalogueEntry.id
```

`NULL` means the Price Plan has no model override. Runtime then falls through to Platform unless a Shop Agent Configuration has an explicit model override. The association is stored only on `MerchantPricingPlan`; no model field or FK is added to `BillingPlan`.

Model selection remains in the existing `CommerceAgentConfiguration.modelId`. This task MUST NOT create another active-model table or active flag. There is still at most one explicit model pointer per Platform/Shop Agent Configuration because the existing Agent Configuration uniqueness rules remain authoritative.

ARCH-024 uses OpenRouter for normal model execution. The credential is environment-specific, while catalogue entries are intentionally environment-independent. Therefore **do not add a single `credentialId` FK to `CommerceModelCatalogueEntry`**: one catalogue entry may be selected in LOCAL, TEST, DEVELOPMENT, STAGING and PRODUCTION, each of which has a different OpenRouter credential. The exact runtime association is:

```text
selected CommerceModelCatalogueEntry
        +
CommerceAgentConfiguration.environment
        |
        v
CommerceOpenRouterCredential(environment)
```

There is at most one configured OpenRouter credential row for each `CommerceEnvironment`. Credential removal deletes that environment's credential row. Credential replacement updates that row under CAS. No plaintext credential is stored.

ARCH-024 is being implemented while this functionality remains in development. This task is therefore a **PRE-PRODUCTION / BREAKING ROLLOUT**. Existing development-only model catalogue rows, model-selection pointers and model-related audit fixtures do not require preservation. Do not add backfill or compatibility machinery solely to preserve current development data. The migration may reset affected model-catalogue/model-selection development state where required to reach the target schema cleanly.

## Scope

Modify only `moda-interact-database` files required for the exact schema, migration, audit reconciliation, ERD and focused database validation.

Required primary files:

```text
prisma/schema.prisma
prisma/migrations/20260930120000_arch024_model_availability_openrouter/migration.sql
scripts/validate-arch024-model-availability-schema.mjs
scripts/validate-arch024-model-availability-migration.mjs
package.json
```

Update the generated ERD source/output if required by the repository's normal schema-change workflow.

Do not modify Admin, Commerce, Background, Gateway, Shopify or Shared implementation in this task.

## Out of Scope

- Admin UI or Admin server actions.
- Commerce Studio model selection UI.
- Merchant-facing model selection; merchants do not select models under ARCH-024.
- Test Conversation implementation.
- LangChain or OpenRouter SDK integration.
- Defining the semantic contents of model `configuration` JSON; ARCH-024-SHARED-001 owns the versioned validator.
- Encrypting/decrypting credentials in application code.
- Encryption keyring/environment configuration.
- Adding an `active` flag to a catalogue entry or Availability.
- Creating a replacement Platform/Shop model-selection table.
- Changing the existing `CommerceAgentConfiguration` Platform/Shop uniqueness rules.
- Adding `commerceModelId` or another model association to `BillingPlan`.
- Adding a physical `MerchantPricingPlan` <-> `BillingPlan` foreign key; accepted ARCH-017 same-`shopifyPlanHandle` identity remains authoritative.
- Automatically clearing or changing Agent Configuration or MerchantPricingPlan model associations when an Availability or catalogue entry is disabled/reassigned.
- A database trigger that silently falls back from an invalid explicit Shop model to the Platform model.
- A database trigger that prevents Admin from disabling/reassigning a selected model. Broken explicit selections must remain representable so later Commerce resolution can fail closed as `UNAVAILABLE`.
- A catalogue-entry-to-credential FK. Credential resolution is by Agent Configuration environment as described above.
- Rewriting any historical migration.

## Requirements

### R1 — Add `CommerceModelAvailabilityScope` exactly

Add this Prisma/PostgreSQL enum:

```prisma
enum CommerceModelAvailabilityScope {
  PLATFORM
  SHOP

  @@schema("commerce")
}
```

Do not reuse `CommerceAgentPromptScope` for Model Availability. The concepts have separate ownership and lifecycle.

### R2 — Add `CommerceModelAvailability` exactly

Add this Prisma model shape:

```prisma
model CommerceModelAvailability {
  id               String                         @id @default(cuid()) @db.Text
  scope            CommerceModelAvailabilityScope
  shopId           String?                        @unique @db.Text
  enabled          Boolean                        @default(true)
  editVersion      Int                            @default(1)
  createdByAdminId String?                        @db.Text
  updatedByAdminId String?                        @db.Text
  createdAt        DateTime                       @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime                       @default(now()) @updatedAt @db.Timestamptz(3)

  shop      Shop?                         @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy PlatformAdmin?                @relation("CommerceModelAvailabilityCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin?                @relation("CommerceModelAvailabilityUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  entries   CommerceModelCatalogueEntry[]
  auditEvents CommerceAuditEvent[]

  @@index([scope, enabled, id])
  @@schema("commerce")
}
```

Add inverse Prisma relations:

```prisma
// Shop
commerceModelAvailability CommerceModelAvailability?

// PlatformAdmin
createdCommerceModelAvailabilities CommerceModelAvailability[] @relation("CommerceModelAvailabilityCreator")
updatedCommerceModelAvailabilities CommerceModelAvailability[] @relation("CommerceModelAvailabilityUpdater")
```

The nullable Admin provenance is intentional only so the migration can create the one bootstrap Platform Availability without inventing a PlatformAdmin actor. Later Admin mutation code is expected to populate provenance and audit normally.

Create these exact database constraints/indexes:

```text
CommerceModelAvailability_scope_shop_check
    (scope = PLATFORM AND shopId IS NULL)
    OR
    (scope = SHOP AND shopId IS NOT NULL)

CommerceModelAvailability_edit_version_check
    editVersion > 0

CommerceModelAvailability_one_platform
    UNIQUE partial index ensuring exactly at most one row where scope = PLATFORM AND shopId IS NULL

CommerceModelAvailability_shopId_key
    unique shopId for non-null shopId, therefore at most one SHOP Availability per Shop

CommerceModelAvailability_scope_enabled_id_idx
    (scope, enabled, id)
```

`shopId` FK:

```text
commerce.CommerceModelAvailability.shopId
    -> commerce.Shop.id
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
```

Admin provenance FKs:

```text
createdByAdminId -> public.PlatformAdmin.id ON DELETE RESTRICT ON UPDATE RESTRICT
updatedByAdminId -> public.PlatformAdmin.id ON DELETE RESTRICT ON UPDATE RESTRICT
```

Add trigger/function:

```text
commerce.arch024_model_availability_guard()
arch024_model_availability_guard
```

with exact semantics:

1. `DELETE` is rejected.
2. `id`, `scope` and `shopId` are immutable after insert.
3. `enabled`, `editVersion`, `updatedByAdminId` and timestamps may change.
4. The trigger MUST NOT require an Availability to contain at least one catalogue entry.

### R3 — Bootstrap exactly one Platform Availability

The migration must create one enabled Platform Availability as part of establishing the target ARCH-024 schema.

Use the deterministic ID:

```text
arch024-platform-model-availability
```

Insert:

```text
id               = arch024-platform-model-availability
scope            = PLATFORM
shopId           = NULL
enabled          = true
editVersion      = 1
createdByAdminId = NULL
updatedByAdminId = NULL
```

The migration must be idempotent with respect to this deterministic bootstrap row inside a normal one-time Prisma migration: do not create a second Platform Availability if the row already exists during migration rehearsal recovery.

Do not create any Shop Availability during migration.

### R4 — Evolve `CommerceModelCatalogueEntry` exactly

The resulting Prisma model must contain these fields and relations:

```prisma
model CommerceModelCatalogueEntry {
  id                         String                    @id @default(cuid()) @db.Text
  availabilityId             String                    @db.Text
  provider                   String                    @db.VarChar(64)
  providerModelId            String                    @db.VarChar(255)
  displayName                String                    @db.VarChar(255)
  description                String                    @default("") @db.Text
  configurationSchemaVersion Int                       @default(1)
  configuration              Json                      @default("{}") @db.JsonB
  enabled                    Boolean                   @default(true)
  editVersion                Int                       @default(1)
  createdByAdminId           String                    @db.Text
  updatedByAdminId           String                    @db.Text
  createdAt                  DateTime                  @default(now()) @db.Timestamptz(3)
  updatedAt                  DateTime                  @default(now()) @updatedAt @db.Timestamptz(3)

  availability CommerceModelAvailability @relation(fields: [availabilityId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy     PlatformAdmin             @relation("CommerceModelCatalogueEntryCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy     PlatformAdmin             @relation("CommerceModelCatalogueEntryUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  configurations      CommerceAgentConfiguration[]
  merchantPricingPlans MerchantPricingPlan[] @relation("MerchantPricingPlanCommerceModel")
  auditEvents           CommerceAuditEvent[]

  @@unique([availabilityId, provider, providerModelId])
  @@index([availabilityId, enabled, displayName, id])
  @@index([provider, providerModelId])
  @@schema("commerce")
}
```

Do not add `credentialId`, `environment`, `active`, `selected`, `shopId` or another scope column to this table.

Create/retain these database checks:

```text
CommerceModelCatalogueEntry_provider_check
    provider ~ '^[a-z0-9][a-z0-9._-]{0,63}$'

CommerceModelCatalogueEntry_provider_model_id_check
    length(btrim(providerModelId)) > 0

CommerceModelCatalogueEntry_display_name_check
    length(btrim(displayName)) > 0

CommerceModelCatalogueEntry_description_length_check
    length(description) <= 4096

CommerceModelCatalogueEntry_configuration_schema_version_check
    configurationSchemaVersion > 0

CommerceModelCatalogueEntry_configuration_object_check
    jsonb_typeof(configuration) = 'object'

CommerceModelCatalogueEntry_edit_version_check
    editVersion > 0
```

FK:

```text
availabilityId
    -> commerce.CommerceModelAvailability.id
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
```

Change uniqueness from the existing global:

```text
(provider, providerModelId)
```

to:

```text
(availabilityId, provider, providerModelId)
```

This deliberately permits the same OpenRouter model identity to exist as separately configured catalogue entries in different Availability scopes, while forbidding duplicates inside one Availability.

`configuration` is durable versioned JSON but its semantic field validation is not a PostgreSQL responsibility. PostgreSQL enforces only that it is a JSON object and that `configurationSchemaVersion > 0`. ARCH-024-SHARED-001 owns the exact versioned schema used by Admin/Commerce/Background.

### R5 — Replace the closed provider enum with a canonical string

Remove `CommerceModelProvider` from `prisma/schema.prisma` and remove the PostgreSQL enum type from the resulting ARCH-024 schema.

The target catalogue column is:

```text
provider VARCHAR(64)
```

with the canonical lower-case provider constraint defined in R4. New ARCH-024 data therefore uses values such as:

```text
openai
groq
anthropic
google
```

Because this is a pre-production breaking migration, **do not add compatibility/backfill machinery solely to preserve existing `OPENAI`/`GROQ` development rows**. The implementation may convert retained development rows to lower-case strings or clear/recreate affected development model-catalogue state; either approach is acceptable provided the resulting schema contains no Prisma/PostgreSQL `CommerceModelProvider` enum and every surviving/new row satisfies the canonical provider check.

The application later derives the OpenRouter model slug as:

```text
provider + '/' + providerModelId
```

Do not persist an additional `openRouterModelId` column in this task.

### R6 — Preserve catalogue identity while allowing Availability assignment changes

Replace the current `arch021_model_catalogue_guard` with:

```text
commerce.arch024_model_catalogue_guard()
arch024_model_catalogue_guard
```

Exact semantics:

1. Catalogue-entry `DELETE` remains rejected.
2. `id`, `provider` and `providerModelId` remain immutable after insert.
3. `availabilityId` is mutable under normal CAS/service control so Admin can reassign an existing catalogue entry from one Availability to another in one atomic row update.
4. `displayName`, `description`, `configurationSchemaVersion`, `configuration`, `enabled`, `editVersion` and updater/timestamp metadata may change.
5. The database MUST NOT reject an Availability reassignment merely because an existing Agent Configuration currently references the entry. That explicit selection is allowed to become invalid and must later resolve `UNAVAILABLE` until corrected.

Drop the old trigger/function only after the ARCH-024 replacement is installed.

### R6A — Add the optional `MerchantPricingPlan` Commerce model association exactly

Modify the existing billing model with exactly this additive relation:

```prisma
model MerchantPricingPlan {
  // existing fields unchanged

  commerceModelId String? @db.Text
  commerceModel   CommerceModelCatalogueEntry? @relation(
    "MerchantPricingPlanCommerceModel",
    fields: [commerceModelId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )

  @@index([commerceModelId])
  @@schema("billing")
}
```

Add the inverse relation to the ARCH-024 target `CommerceModelCatalogueEntry`:

```prisma
merchantPricingPlans MerchantPricingPlan[] @relation("MerchantPricingPlanCommerceModel")
```

Create the FK exactly:

```text
billing.MerchantPricingPlan.commerceModelId
    -> commerce.CommerceModelCatalogueEntry.id
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
```

Migration semantics are exact:

1. every existing `MerchantPricingPlan` receives `commerceModelId = NULL`;
2. `NULL` means no Price Plan model override;
3. no existing `BillingPlan` row is changed;
4. do not add a `BillingPlan.commerceModelId`;
5. do not add a MerchantPricingPlan/BillingPlan FK;
6. do not infer a model from plan price, catalogue position, Feature set, existing Agent Configuration or any other state.

Database responsibility stops at referential integrity. Do **not** add a database trigger that requires the referenced Catalogue Entry to remain enabled or in Platform Availability. Admin write-time validation and Commerce/Background runtime resolution own those dynamic rules. Therefore a later Catalogue disablement or Availability reassignment may intentionally leave a durable now-invalid Price Plan selection that resolves `UNAVAILABLE` until an administrator repairs or clears it.

The association is global product configuration and is not keyed by `CommerceEnvironment`. Environment remains a property of Platform/Shop Agent Configuration and OpenRouter credentials.

### R7 — Add `CommerceOpenRouterCredential` exactly

Add:

```prisma
model CommerceOpenRouterCredential {
  id               String              @id @default(cuid()) @db.Text
  environment      CommerceEnvironment @unique
  ciphertext       Bytes
  nonce            Bytes
  authTag           Bytes
  keyId             String              @db.VarChar(64)
  editVersion       Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt         DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  updatedBy PlatformAdmin @relation("CommerceOpenRouterCredentialUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@schema("commerce")
}
```

Add inverse relation:

```prisma
// PlatformAdmin
updatedCommerceOpenRouterCredentials CommerceOpenRouterCredential[] @relation("CommerceOpenRouterCredentialUpdater")
```

Create these exact database constraints/indexes:

```text
CommerceOpenRouterCredential_environment_key
    UNIQUE(environment)

CommerceOpenRouterCredential_nonce_length_check
    octet_length(nonce) = 12

CommerceOpenRouterCredential_auth_tag_length_check
    octet_length(authTag) = 16

CommerceOpenRouterCredential_ciphertext_length_check
    octet_length(ciphertext) BETWEEN 1 AND 8192

CommerceOpenRouterCredential_key_id_check
    length(btrim(keyId)) > 0

CommerceOpenRouterCredential_edit_version_check
    editVersion > 0
```

FK:

```text
updatedByAdminId
    -> public.PlatformAdmin.id
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
```

Do not seed a credential and do not seed ciphertext. Absence of a row means that OpenRouter is not configured for that environment.

Credential lifecycle semantics supported by this schema are:

```text
SET      -> INSERT one row for environment
REPLACE  -> UPDATE existing row under editVersion CAS
REMOVE   -> DELETE existing row under editVersion CAS
```

The Admin/runtime tasks own the transaction/CAS commands. This database task owns only the durable constraints required to make duplicate environment credentials impossible and malformed encrypted envelopes invalid.

Do not add provider-specific credential columns to `CommerceModelCatalogueEntry`.

### R8 — Credential association is by Agent Configuration environment

The schema must preserve this exact relationship:

```text
CommerceAgentConfiguration
    environment
    modelId -> CommerceModelCatalogueEntry.id

CommerceOpenRouterCredential
    environment UNIQUE
```

No extra persisted link is required. Runtime resolution later performs:

```text
configuration.modelId
    -> CommerceModelCatalogueEntry

configuration.environment
    -> CommerceOpenRouterCredential
```

This is intentional because the same catalogue entry can be selected by Agent Configurations in more than one environment while each environment has a different credential.

Do not duplicate one credential per catalogue entry.

### R9 — Preserve existing Agent Configuration schema and uniqueness

Do not add, remove or rename any existing `CommerceAgentConfiguration` column.

Keep these existing relationships and indexes:

```text
modelId -> CommerceModelCatalogueEntry.id ON DELETE RESTRICT ON UPDATE RESTRICT

one Platform configuration per environment
one Shop configuration per (environment, shopId)
```

Do not add another model-selection record/table.

Do not make `modelId` non-null. A Shop `modelId = NULL` remains the durable representation of "inherit the Platform model". A Platform configuration may also temporarily have no model while configuration is incomplete, in which case later Commerce resolution returns unavailable.

Do not add a database trigger enforcing current Availability eligibility for `CommerceAgentConfiguration.modelId`. Eligibility is intentionally evaluated by the Commerce service when setting/resolving the model because Admin may later disable/reassign a selected entry and the explicit broken selection must remain durable for fail-closed detection.

### R10 — Extend Commerce audit targets exactly

Add nullable field/relation to `CommerceAuditEvent`:

```prisma
modelAvailabilityId String? @db.Text

modelAvailability CommerceModelAvailability?
  @relation(fields: [modelAvailabilityId], references: [id], onDelete: Restrict, onUpdate: Restrict)
```

Add index:

```text
CommerceAuditEvent_modelAvailabilityId_createdAt_id_idx
    (modelAvailabilityId, createdAt, id)
```

Do not add a credential FK to `CommerceAuditEvent`. Credential rows can be deleted by REMOVE. Existing `CommerceAuditEvent.environment` is the durable credential target identifier.

Extend `CommerceAuditAction` with exactly:

```text
CREATE_MODEL_AVAILABILITY
UPDATE_MODEL_AVAILABILITY
ENABLE_MODEL_AVAILABILITY
DISABLE_MODEL_AVAILABILITY
ASSIGN_MODEL_CATALOGUE_ENTRY_AVAILABILITY
SET_OPENROUTER_CREDENTIAL
REPLACE_OPENROUTER_CREDENTIAL
REMOVE_OPENROUTER_CREDENTIAL
```

Preserve all existing audit actions.

Update the existing `arch020_audit_targets` CHECK without dropping any supported prior branch. Add exact target requirements:

```text
CREATE_MODEL_AVAILABILITY
UPDATE_MODEL_AVAILABILITY
ENABLE_MODEL_AVAILABILITY
DISABLE_MODEL_AVAILABILITY
    -> modelAvailabilityId IS NOT NULL

ASSIGN_MODEL_CATALOGUE_ENTRY_AVAILABILITY
    -> modelCatalogueEntryId IS NOT NULL
       AND modelAvailabilityId IS NOT NULL

SET_OPENROUTER_CREDENTIAL
REPLACE_OPENROUTER_CREDENTIAL
REMOVE_OPENROUTER_CREDENTIAL
    -> environment IS NOT NULL
```

Credential audit metadata must never require or contain ciphertext, nonce, authTag, keyId plaintext material, decrypted secret or any secret fingerprint generated from plaintext. Later application tasks may record bounded non-secret status/version metadata only.

### R11 — Update Prisma inverse relations exactly

Add the required inverse relations to the existing root models and do not rename unrelated relations.

Required additions:

```prisma
// Shop
commerceModelAvailability CommerceModelAvailability?

// PlatformAdmin
createdCommerceModelAvailabilities     CommerceModelAvailability[]   @relation("CommerceModelAvailabilityCreator")
updatedCommerceModelAvailabilities     CommerceModelAvailability[]   @relation("CommerceModelAvailabilityUpdater")
updatedCommerceOpenRouterCredentials   CommerceOpenRouterCredential[] @relation("CommerceOpenRouterCredentialUpdater")
```

Keep the existing Model Catalogue creator/updater relations unchanged. The `CommerceModelCatalogueEntry.merchantPricingPlans` inverse relation required by R6A is also part of the target schema.

### R12 — Do not create model runtime or merchant-controlled selection persistence

`MerchantPricingPlan.commerceModelId` is Platform Admin product-tier configuration, not merchant-controlled selection.

This migration must not create:

```text
CommerceModelProvider table
CommerceModelAvailabilityAssignment join table
CommerceModelSelection replacement table
CommerceMerchantModelSelection
BillingPlan.commerceModelId
CommerceModelRuntime
CommerceModelClient configuration table
LangChain/OpenRouter request/response tables
Test Conversation snapshot tables
```

The agreed ARCH-024 relationship is direct:

```text
CommerceModelAvailability 1 ---- * CommerceModelCatalogueEntry
```

with existing `CommerceAgentConfiguration.modelId` remaining the explicit Platform/Shop model pointer and `MerchantPricingPlan.commerceModelId` remaining the optional product-tier pointer.

### R13 — Rollout classification is pre-production / breaking

This task is explicitly a **PRE-PRODUCTION / BREAKING ROLLOUT**. There is no production compatibility requirement for the existing `CommerceModelProvider` enum, current development catalogue rows or current development model-selection data.

Therefore:

1. do not add shadow provider columns;
2. do not add dual-write behaviour;
3. do not preserve legacy enum compatibility;
4. do not add model-catalogue backfill solely to preserve development IDs/selections;
5. prefer the smallest deterministic migration that establishes the target ARCH-024 schema.

The Completion Report must record that ARCH-024 intentionally uses a breaking development migration.

## Work Items

- [x] Add `CommerceModelAvailabilityScope`.
- [x] Add `CommerceModelAvailability` with exact Platform/Shop scope constraints, FKs, partial uniqueness and immutable identity guard.
- [x] Bootstrap the single Platform Availability with deterministic ID.
- [x] Add required Prisma inverse relations on `Shop`, `PlatformAdmin` and `CommerceModelCatalogueEntry`.
- [x] Add nullable `MerchantPricingPlan.commerceModelId` FK/index exactly as R6A and leave all existing Price Plans at NULL.
- [x] Establish the target non-null `availabilityId` relationship on `CommerceModelCatalogueEntry`; no pre-ARCH-024 development-data ID/backfill preservation is required.
- [x] Replace `CommerceModelCatalogueEntry.provider` enum storage with canonical lower-case `VARCHAR(64)` and remove `CommerceModelProvider`; development rows may be reset rather than preserved.
- [x] Add `configurationSchemaVersion` and `configuration JSONB` with database structural checks.
- [x] Replace global model uniqueness with Availability-scoped uniqueness.
- [x] Replace the ARCH-021 model catalogue guard with the ARCH-024 guard and preserve provider/model identity immutability.
- [x] Add `CommerceOpenRouterCredential` with one-row-per-environment uniqueness and encrypted-envelope constraints.
- [x] Extend `CommerceAuditEvent` with `modelAvailabilityId` and the new audit actions/target rules.
- [x] Preserve the `CommerceAgentConfiguration` schema and uniqueness rules; pre-ARCH-024 development `modelId` values may be cleared/reset if required by the breaking migration.
- [x] Prove no `BillingPlan` model column/FK and no MerchantPricingPlan/BillingPlan FK is introduced.
- [x] Add focused schema validation.
- [x] Add fresh PostgreSQL migration rehearsal.
- [x] Add a current-schema -> ARCH-024 development-upgrade rehearsal proving the breaking migration reaches the target schema without requiring data preservation.
- [x] Update package scripts for the focused ARCH-024 validators.
- [x] Regenerate ERD artifacts if required by repository workflow.

## Interfaces / Contracts

This task produces the durable database contract later consumed by ARCH-024 Shared/Admin/Commerce/Background tasks:

```text
commerce.CommerceModelAvailability
commerce.CommerceModelCatalogueEntry
commerce.CommerceOpenRouterCredential
commerce.CommerceAgentConfiguration        existing schema retained
commerce.CommerceAuditEvent                extended
```

Authoritative relationships:

```text
Shop 1 -------- 0..1 CommerceModelAvailability(scope=SHOP)

CommerceModelAvailability 1 -------- 0..* CommerceModelCatalogueEntry
CommerceModelCatalogueEntry * ------- 1 CommerceModelAvailability

CommerceAgentConfiguration 0..1 ----- 1 CommerceModelCatalogueEntry via modelId when non-null

CommerceEnvironment 1 --------------- 0..1 CommerceOpenRouterCredential
```

Model eligibility is not encoded as an Agent Configuration FK path. Later Commerce code computes:

```text
Platform configuration:
    selected model must belong to enabled PLATFORM Availability

Shop configuration:
    selected model may belong to enabled PLATFORM Availability
    OR enabled Availability for that exact Shop

No Shop override:
    inherit Platform selection

Broken explicit Shop override:
    UNAVAILABLE; no silent fallback
```

After ARCH-024 is established, the database preserves explicit selections needed to detect those states; later service tasks own the semantic resolution.

## Dependencies

None.

## Enables

- `ARCH-024-SHARED-001`

## Acceptance Criteria

- [x] `MerchantPricingPlan.commerceModelId` is nullable, indexed and FK-constrained to `CommerceModelCatalogueEntry` with `ON DELETE/UPDATE RESTRICT`.
- [x] Existing Price Plans migrate with `commerceModelId = NULL`; no model assignment is inferred.
- [x] `BillingPlan` remains physically independent of the Commerce model association and gains no model field/FK.
- [x] Disabling/reassigning a referenced Catalogue Entry does not rewrite the Price Plan association at database level.

- [x] Exactly one bootstrap Platform Model Availability exists after migration.
- [x] Database constraints prevent a second Platform Availability.
- [x] A Shop can have at most one Shop Availability.
- [x] PLATFORM Availability cannot carry a `shopId`, and SHOP Availability cannot omit one.
- [x] Availability IDs/scope/shop identity cannot be changed or deleted after creation.
- [x] Every `CommerceModelCatalogueEntry` has exactly one non-null `availabilityId`.
- [x] No migration requirement exists to preserve or backfill pre-ARCH-024 development catalogue IDs.
- [x] Persisted ARCH-024 provider values use the canonical lower-case string format; no closed provider enum remains.
- [x] The PostgreSQL/Prisma `CommerceModelProvider` enum no longer exists.
- [x] New provider strings satisfying the canonical provider check can be stored without another database migration.
- [x] `provider` and `providerModelId` remain immutable catalogue identity fields.
- [x] `availabilityId` can be reassigned atomically without changing catalogue entry ID.
- [x] Duplicate `(availabilityId, provider, providerModelId)` is rejected.
- [x] The same `(provider, providerModelId)` may exist in two different Availabilities.
- [x] `configuration` is non-null JSONB and only JSON objects are accepted.
- [x] `configurationSchemaVersion <= 0` is rejected.
- [x] New/retained ARCH-024 catalogue rows have `configurationSchemaVersion > 0` and object-valued `configuration`.
- [x] `CommerceAgentConfiguration` schema and Platform/Shop uniqueness semantics remain intact; pre-ARCH-024 development model selections need not be preserved.
- [x] `CommerceAgentConfiguration` remains capable of representing Shop inheritance with `modelId = NULL`.
- [x] No database trigger silently falls back, clears or rewrites an Agent Configuration because model availability changes.
- [x] At most one `CommerceOpenRouterCredential` can exist for each environment.
- [x] A valid OpenRouter credential envelope requires 12-byte nonce, 16-byte auth tag, 1..8192-byte ciphertext, nonblank key ID and positive editVersion.
- [x] No OpenRouter credential is seeded by the migration.
- [x] Removing a credential row does not delete or mutate any catalogue entry or Agent Configuration.
- [x] New Availability and credential audit actions satisfy the extended audit-target CHECK, while all pre-existing audit actions remain valid.
- [x] Prisma validation/generation passes.
- [x] Fresh and current-schema development-upgrade PostgreSQL rehearsals pass.
- [x] Development-upgrade rehearsal proves unrelated schema outside the explicitly breaking model-catalogue/model-selection boundary remains structurally valid.

## Validation

- [x] Static schema/migration validation proves the exact Price Plan model FK/index and absence of any `BillingPlan` model association.
- [x] Disposable PostgreSQL proof creates a Price Plan with null model, assigns a Catalogue Entry, leaves the Price Plan FK unchanged when the model/Availability is later disabled/reassigned, and proves no automatic model inference/backfill occurs.

The implementing agent must add these package scripts:

```json
"test:arch024-model-availability-schema": "node scripts/validate-arch024-model-availability-schema.mjs",
"test:arch024-model-availability-migration": "node scripts/validate-arch024-model-availability-migration.mjs"
```

Required validation:

- [x] `npm run prisma:validate`
- [x] `npm run prisma:generate`
- [x] `npm run test:arch024-model-availability-schema`
- [x] `npm run test:arch024-model-availability-migration`
- [x] `git diff --check`

The migration validator must perform both a **fresh** and a **current-schema development-upgrade** PostgreSQL rehearsal.

The development-upgrade rehearsal exists only to prove that the migration can be applied to the current development schema. It MUST NOT require preservation of existing model catalogue IDs, existing provider enum values, model-selection pointers or model-related audit fixture rows. The implementation may reset that development-only state as part of the breaking migration.

The migration validator must prove at minimum:

1. The migration applies successfully from the current pre-ARCH-024 development schema.
2. Exactly one bootstrap Platform Availability is present after migration.
3. A second Platform Availability is rejected.
4. A second Shop Availability for the same Shop is rejected.
5. Invalid scope/shop combinations are rejected.
6. Availability delete and identity mutation are rejected.
7. Every surviving/new catalogue row has exactly one non-null Availability.
8. Catalogue provider/providerModelId mutation is rejected.
9. Catalogue Availability reassignment succeeds when it does not collide with target scoped uniqueness.
10. Duplicate model identity inside one Availability is rejected.
11. The same provider/model identity in a different Availability succeeds.
12. JSON array/scalar configuration is rejected; JSON object succeeds.
13. Configuration schema version `0` is rejected.
14. A new provider string such as `anthropic` can be inserted without a provider enum migration.
15. Duplicate OpenRouter credential for one environment is rejected.
16. Invalid nonce/authTag/ciphertext/keyId/editVersion credential envelopes are rejected.
17. Valid credential INSERT, CAS-style UPDATE and DELETE are database-valid operations.
18. Credential removal leaves catalogue definitions and Agent Configuration schema intact.
19. New audit actions reject missing required targets and accept valid targets.
20. Pre-existing unrelated audit actions/constraint branches continue to validate.
21. PostgreSQL no longer contains type `commerce."CommerceModelProvider"`.
22. Unrelated ARCH-020/021/023 schema remains structurally valid after the development upgrade.

## Stop Condition

After the exact schema, migration, audit reconciliation, focused validators, Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP.

Do not begin ARCH-024 Shared, Admin, Commerce, Background, Gateway or System-Test work.

## Implementation Notes

- Treat `provider + providerModelId` as stable model identity. `availabilityId` is assignment and may change; provider identity may not.
- Do not duplicate an OpenRouter credential per catalogue entry. The agreed one-per-environment credential is resolved using `CommerceAgentConfiguration.environment` when the selected catalogue entry is executed.
- Do not put semantic model-configuration validation into PostgreSQL beyond `JSON object + positive schema version`; Shared owns the versioned schema.
- After ARCH-024 is live, later Availability changes must leave explicit selections durable so Commerce can detect broken overrides as `UNAVAILABLE`; this does not require preserving pre-ARCH-024 development selections during the breaking migration.
- Do not add compatibility columns or backfill machinery for the pre-ARCH-024 development state.

## Completion Report

### Status

Ready for Review

### Files Changed

- `prisma/schema.prisma`: added Model Availability, versioned model configuration, optional Price Plan model association, OpenRouter credentials and extended audit contract; removed the provider enum.
- `prisma/migrations/20260930120000_arch024_model_availability_openrouter/migration.sql`: implemented the pre-production breaking migration, deterministic Platform bootstrap, constraints, FKs, indexes, guards and audit target reconciliation.
- `scripts/validate-arch024-model-availability-schema.mjs`: added static schema, migration and ERD contract checks.
- `scripts/validate-arch024-model-availability-migration.mjs`: added safe fresh and development-upgrade PostgreSQL rehearsals and behavior cases.
- `package.json`: added the two required ARCH-024 validation scripts.
- `docs/generated/prisma-erd.puml`: regenerated the database ERD.

### Work Completed

- Implemented the exact ARCH-024 database boundary, retaining explicit Agent Configuration selections and existing uniqueness semantics while allowing Availability reassignment.
- Added the optional nullable Price Plan association without modifying `BillingPlan` or inferring assignments. Rehearsal confirms existing Price Plans remain NULL until explicitly assigned and stay assigned across Catalogue disablement/reassignment.
- Added one encrypted OpenRouter credential per environment with envelope checks, and extended audit targets while retaining prior branches.
- ARCH-024 intentionally uses a pre-production breaking development migration; no legacy provider-enum compatibility or model-selection preservation machinery was added.
- Implementation commit `6ef1ea2` is pushed to `task/ARCH-024-DATABASE-001`.
- No Admin, Commerce, Background, Gateway, Shopify, Shared or System-Test implementation was started.

Launcher-prepared evidence:
- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-DATABASE-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-DATABASE-001`; both branches `task/ARCH-024-DATABASE-001`.
- Parent and implementation worktrees were newly created and not reused. Shared workspace and shared implementation source checkouts were not switched or mutated for task work; another task worktree was not reused.
- Start synchronization: parent and implementation remote task branches were `not-needed` for fast-forward; `origin/main` was `already-current` in both worktrees. Parent claim commit `c4db25e6cced38dd947e60f854834406b236af0f` was committed and pushed by the launcher; claim executor `copilot`, Attempt 1, claimed `2026-10-01T14:29:54Z`.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; status `ready`, with no submodule entries.

### Validation Results

- Passed `npm run prisma:validate` and `npm run prisma:generate` with Prisma 6.19.3.
- Passed `npm run test:arch024-model-availability-schema`.
- Passed `npm run test:arch024-model-availability-migration` in both modes against isolated local `pgvector/pgvector:pg16` PostgreSQL databases on `127.0.0.1:55439`.
- Fresh rehearsal applied the complete 25-migration history and passed the behavior matrix. Upgrade rehearsal applied the 21-migration predecessor set, verified unrelated schema and billing fixtures, applied ARCH-024, passed the behavior matrix, then applied the three later migrations.
- The behavior matrix verified availability cardinality/scope/identity guards; catalogue non-null/FK/scoped uniqueness, cross-availability duplicate identity, mutable assignment and immutable provider identity; JSON/version checks; Agent Configuration uniqueness; Price Plan NULL/no-inference and stable pointer semantics; credential envelope rejection, uniqueness, INSERT/CAS UPDATE/DELETE isolation; all new audit target branches and an existing audit branch; and absence of the PostgreSQL provider enum.
- Passed `node --check scripts/validate-arch024-model-availability-migration.mjs` and `git diff --check`.

### Deviations

None. The migration retains existing ARCH-021 display-name, description-length and edit-version constraints rather than adding duplicate constraints; the static validator verifies the predecessor definitions.

### Assumptions

- ARCH-024 is explicitly pre-production and permits a breaking migration for the model-catalogue/model-selection development state.
- `CommerceModelAvailability` is global Platform/Shop availability and is not environment-scoped; environment-specific execution credentials remain separate.

### Unresolved Issues

None. PostgreSQL rehearsals require a local PostgreSQL instance with the `vector` extension; validation used the isolated `pgvector/pgvector:pg16` container.

### Architectural Concerns

None. Task is submitted at `review` for `moda_architect`; no main branch was updated and the Architect Review section was not edited.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

None.
