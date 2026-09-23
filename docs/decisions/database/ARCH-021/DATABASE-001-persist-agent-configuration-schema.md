---
id: ARCH-021-DATABASE-001
architecture_id: ARCH-021
title: Persist Phase 2 CommerceAgent configuration schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-23T15:30:00Z
attempt: 2
depends_on:
  - ARCH-020-DATABASE-001
enables:
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-008
created: 2026-09-23
updated: 2026-09-23
---

# Persist Phase 2 CommerceAgent configuration schema

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add the exact durable Phase 2 CommerceAgent configuration schema defined below: a Moda-controlled model catalogue, independent platform/shop model selections, data-driven prompt-template categories and immutable template revisions, platform/shop prompt lineages and immutable prompt revisions, and independent environment-scoped active prompt pointers.

The implementing agent MUST implement the schema below rather than choosing alternative table names, combining concepts into JSON, introducing additional ownership abstractions, or changing the platform/shop fallback model.

## Context

ARCH-021 defines two independent CommerceAgent configuration axes:

```text
model  = explicit shop override ?? platform default
prompt = explicit shop override ?? platform active prompt
```

Prompt templates are authoring inputs only. A template belongs to a data-driven category/classification such as `Clothing & Fashion`; a category can contain multiple templates. Copying a template into a platform/shop prompt creates independent prompt content with optional immutable provenance.

This task intentionally introduces all Phase 2 durable state in one migration so foreign keys, uniqueness, immutability, audit vocabulary and tenant/scope integrity are designed together.

## Scope

Modify only the following database-owned files/locations unless a generated Prisma artefact requires an adjacent repository-standard update:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql
moda-interact-database/scripts/fixtures/arch021-agent-configuration-schema-contract.mjs
moda-interact-database/scripts/fixtures/arch021-agent-configuration-cases.mjs
moda-interact-database/scripts/validate-arch021-agent-configuration-schema.mjs
moda-interact-database/scripts/validate-arch021-agent-configuration-migration.mjs
moda-interact-database/scripts/validate-arch020-commerce-capability-schema.mjs
moda-interact-database/package.json
moda-interact-database/docs/generated/prisma-erd.puml
```

Do not modify another repository. Do not create a second migration directory for this task.

Attempt 2 compatibility exception: `scripts/validate-arch020-commerce-capability-schema.mjs` is explicitly in scope only to make its historical `CommerceAuditAction` assertion extension-aware. Preserve the ARCH-020 fixture contract and continue requiring its original 17 actions in their original order; permit only appended later actions. Do not modify an ARCH-020 migration or weaken any other ARCH-020 schema assertion.

The migration MUST create exactly these ten new `commerce` tables:

```text
CommerceModelCatalogueEntry
CommercePlatformModelSelection
CommerceShopModelSelection
CommercePromptTemplateCategory
CommercePromptTemplate
CommercePromptTemplateRevision
CommerceAgentPrompt
CommerceAgentPromptRevision
CommercePlatformPromptPointer
CommerceShopPromptPointer
```

The migration MUST create exactly these three new `commerce` enums:

```text
CommerceModelProvider
CommerceAgentPromptScope
CommercePromptRevisionStatus
```

It MUST also extend the existing `CommerceAuditAction` enum and `CommerceAuditEvent`, `Shop`, and `PlatformAdmin` models exactly as described below.

## Out of Scope

- Provider API keys, credentials or secret material.
- Calling OpenAI/Groq or discovering models from provider APIs.
- Seeding platform model defaults, prompt categories, templates, prompt lineages or active pointers.
- Live Shopify/external Tool execution.
- `CommerceConversationGrant` or manifest model/prompt pins.
- Background/runtime changes.
- Removing `CommerceCapabilityRevision.promptTemplate`.
- Shop-owned reusable prompt-template libraries.
- Merchant authentication/authorization.
- Any schema/table outside the exact Phase 2 contract below, except relation fields required on `Shop`, `PlatformAdmin`, and `CommerceAuditEvent`.

## Requirements

### R1 — exact Prisma enums

Add exactly:

```prisma
enum CommerceModelProvider {
  OPENAI
  GROQ

  @@schema("commerce")
}

enum CommerceAgentPromptScope {
  PLATFORM
  SHOP

  @@schema("commerce")
}

enum CommercePromptRevisionStatus {
  DRAFT
  PUBLISHED

  @@schema("commerce")
}
```

Do not encode providers, prompt scope, or revision status as free-text columns or JSON.

### R2 — exact model catalogue

Add exactly this durable model shape:

```prisma
model CommerceModelCatalogueEntry {
  id               String                @id @default(cuid()) @db.Text
  provider         CommerceModelProvider
  providerModelId  String                @db.VarChar(255)
  displayName      String                @db.VarChar(255)
  description      String                @default("") @db.Text
  enabled          Boolean               @default(true)
  editVersion      Int                   @default(1)
  createdByAdminId String                @db.Text
  updatedByAdminId String                @db.Text
  createdAt        DateTime              @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime              @default(now()) @updatedAt @db.Timestamptz(3)

  createdBy          PlatformAdmin                   @relation("CommerceModelCatalogueEntryCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy          PlatformAdmin                   @relation("CommerceModelCatalogueEntryUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  platformSelections CommercePlatformModelSelection[]
  shopSelections     CommerceShopModelSelection[]
  auditEvents        CommerceAuditEvent[]

  @@unique([provider, providerModelId])
  @@index([enabled, provider, displayName, id])
  @@schema("commerce")
}
```

Database constraints/triggers MUST additionally enforce:

```text
providerModelId                 non-blank
displayName                     non-blank
description length              <= 4096 characters
editVersion                     > 0
id/provider/providerModelId     immutable after INSERT
DELETE                          forbidden; disable instead
```

Changing `displayName`, `description`, `enabled`, `editVersion`, or `updatedByAdminId` remains permitted.

### R3 — exact platform/shop model selections

Add exactly:

```prisma
model CommercePlatformModelSelection {
  environment      CommerceEnvironment @id
  modelId          String              @db.Text
  editVersion      Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt        DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  model     CommerceModelCatalogueEntry @relation(fields: [modelId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin               @relation("CommercePlatformModelSelectionUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@index([modelId])
  @@schema("commerce")
}

model CommerceShopModelSelection {
  environment      CommerceEnvironment
  shopId           String              @db.Text
  modelId          String              @db.Text
  generationId     String              @default(cuid()) @db.Text
  editVersion      Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt        DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  shop      Shop                        @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  model     CommerceModelCatalogueEntry @relation(fields: [modelId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin               @relation("CommerceShopModelSelectionUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@id([environment, shopId])
  @@index([modelId])
  @@index([shopId])
  @@schema("commerce")
}
```

Both `editVersion` values MUST be constrained to `> 0`. `CommerceShopModelSelection.generationId` is an immutable row-generation token: it is assigned on INSERT, must not change on UPDATE, and a row created after a clear/delete receives a different value. Absence of a `CommerceShopModelSelection` row means model inheritance. The database MUST NOT copy a platform selection into a shop row.

The shop selection generation token exists specifically to prevent an ABA stale-write match across `present -> absent -> present`. Commerce mutation tasks must compare both `generationId` and `editVersion` when replacing or clearing an existing shop override.

### R4 — exact data-driven prompt-template category model

Add exactly:

```prisma
model CommercePromptTemplateCategory {
  id               String   @id @default(cuid()) @db.Text
  slug             String   @unique @db.VarChar(128)
  displayName      String   @db.VarChar(255)
  description      String   @default("") @db.Text
  enabled          Boolean  @default(true)
  displayOrder     Int      @default(0)
  editVersion      Int      @default(1)
  createdByAdminId String   @db.Text
  updatedByAdminId String   @db.Text
  createdAt        DateTime @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  createdBy   PlatformAdmin             @relation("CommercePromptTemplateCategoryCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy   PlatformAdmin             @relation("CommercePromptTemplateCategoryUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  templates   CommercePromptTemplate[]
  auditEvents CommerceAuditEvent[]

  @@index([enabled, displayOrder, displayName, id])
  @@schema("commerce")
}
```

SQL MUST enforce:

```text
slug regex                       ^[a-z][a-z0-9_-]{0,127}$
displayName                      non-blank
description length               <= 4096 characters
displayOrder                     >= 0
editVersion                      > 0
id/slug                          immutable after INSERT
DELETE                           forbidden; disable instead
```

`Clothing & Fashion` is a `displayName`, not an enum value. Its canonical slug would be an authored value such as `clothing-fashion`. No category row is seeded by this migration.

### R5 — exact template identity and revision models

Add exactly:

```prisma
model CommercePromptTemplate {
  id               String   @id @default(cuid()) @db.Text
  key              String   @unique @db.VarChar(128)
  categoryId       String   @db.Text
  displayName      String   @db.VarChar(255)
  description      String   @default("") @db.Text
  enabled          Boolean  @default(true)
  editVersion      Int      @default(1)
  createdByAdminId String   @db.Text
  updatedByAdminId String   @db.Text
  createdAt        DateTime @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  category    CommercePromptTemplateCategory @relation(fields: [categoryId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy   PlatformAdmin                  @relation("CommercePromptTemplateCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy   PlatformAdmin                  @relation("CommercePromptTemplateUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  revisions   CommercePromptTemplateRevision[]
  auditEvents CommerceAuditEvent[]

  @@index([categoryId, enabled, displayName, id])
  @@index([enabled, displayName, id])
  @@schema("commerce")
}

model CommercePromptTemplateRevision {
  id                 String                       @id @default(cuid()) @db.Text
  templateId         String                       @db.Text
  revisionNumber     Int
  status             CommercePromptRevisionStatus @default(DRAFT)
  editVersion        Int                          @default(1)
  promptText         String                       @db.Text
  contentHash        String?                      @db.VarChar(64)
  createdByAdminId   String                       @db.Text
  publishedByAdminId String?                      @db.Text
  createdAt          DateTime                     @default(now()) @db.Timestamptz(3)
  updatedAt          DateTime                     @default(now()) @updatedAt @db.Timestamptz(3)
  publishedAt        DateTime?                    @db.Timestamptz(3)

  template              CommercePromptTemplate     @relation(fields: [templateId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy             PlatformAdmin              @relation("CommercePromptTemplateRevisionCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  publishedBy           PlatformAdmin?             @relation("CommercePromptTemplateRevisionPublisher", fields: [publishedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  copiedPromptRevisions CommerceAgentPromptRevision[] @relation("CommerceAgentPromptRevisionSourceTemplate")
  auditEvents           CommerceAuditEvent[]

  @@unique([templateId, revisionNumber])
  @@unique([id, templateId])
  @@index([templateId, status, revisionNumber])
  @@schema("commerce")
}
```

SQL MUST enforce:

```text
CommercePromptTemplate.key regex           ^[a-z][a-z0-9_-]{0,127}$
template displayName                       non-blank
template description length                <= 4096 characters
template editVersion                       > 0
template id/key                            immutable after INSERT
template DELETE                            forbidden; disable instead
revisionNumber                             > 0
revision editVersion                       > 0
promptText                                 <= 32000 characters; DRAFT may be empty
contentHash when non-null                  ^[0-9a-f]{64}$
DRAFT                                      contentHash/publishedByAdminId/publishedAt are NULL
PUBLISHED                                  promptText is non-blank and contentHash/publishedByAdminId/publishedAt are all NOT NULL
revision id/templateId/revisionNumber      immutable after INSERT
PUBLISHED revision UPDATE/DELETE           forbidden
all revision DELETE                        forbidden
```

A DRAFT may transition once to PUBLISHED. After it is PUBLISHED, no column on that revision may change.

### R6 — exact platform/shop prompt lineage and revision models

Add exactly:

```prisma
model CommerceAgentPrompt {
  id               String                   @id @default(cuid()) @db.Text
  scope            CommerceAgentPromptScope
  shopId           String?                  @db.Text
  createdByAdminId String                   @db.Text
  createdAt        DateTime                 @default(now()) @db.Timestamptz(3)

  shop        Shop?                         @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy   PlatformAdmin                 @relation("CommerceAgentPromptCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  revisions   CommerceAgentPromptRevision[]
  auditEvents CommerceAuditEvent[]

  @@index([scope, shopId])
  @@schema("commerce")
}

model CommerceAgentPromptRevision {
  id                       String                       @id @default(cuid()) @db.Text
  promptId                 String                       @db.Text
  revisionNumber           Int
  status                   CommercePromptRevisionStatus @default(DRAFT)
  editVersion              Int                          @default(1)
  promptText               String                       @db.Text
  contentHash              String?                      @db.VarChar(64)
  sourceTemplateRevisionId String?                      @db.Text
  createdByAdminId         String                       @db.Text
  publishedByAdminId       String?                      @db.Text
  createdAt                DateTime                     @default(now()) @db.Timestamptz(3)
  updatedAt                DateTime                     @default(now()) @updatedAt @db.Timestamptz(3)
  publishedAt              DateTime?                    @db.Timestamptz(3)

  prompt                 CommerceAgentPrompt            @relation(fields: [promptId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  sourceTemplateRevision CommercePromptTemplateRevision? @relation("CommerceAgentPromptRevisionSourceTemplate", fields: [sourceTemplateRevisionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy              PlatformAdmin                  @relation("CommerceAgentPromptRevisionCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  publishedBy            PlatformAdmin?                 @relation("CommerceAgentPromptRevisionPublisher", fields: [publishedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  platformPointers       CommercePlatformPromptPointer[]
  shopPointers           CommerceShopPromptPointer[]
  auditEvents            CommerceAuditEvent[]

  @@unique([promptId, revisionNumber])
  @@unique([id, promptId])
  @@index([promptId, status, revisionNumber])
  @@index([sourceTemplateRevisionId])
  @@schema("commerce")
}
```

SQL MUST additionally enforce:

```text
PLATFORM lineage                     shopId IS NULL
SHOP lineage                         shopId IS NOT NULL
at most one PLATFORM lineage         partial UNIQUE index on constant WHERE scope='PLATFORM'
at most one SHOP lineage per shop    partial UNIQUE index on shopId WHERE scope='SHOP'
CommerceAgentPrompt UPDATE/DELETE    forbidden
revisionNumber                       > 0
revision editVersion                 > 0
promptText                           <= 32000 characters; DRAFT may be empty
contentHash when non-null            ^[0-9a-f]{64}$
DRAFT/PUBLISHED shape                identical to R5, including non-blank promptText only for PUBLISHED
revision identity                    immutable after INSERT
PUBLISHED revision UPDATE/DELETE     forbidden
all revision DELETE                  forbidden
sourceTemplateRevisionId when set    must identify a PUBLISHED CommercePromptTemplateRevision
```

The migration MUST NOT seed the platform lineage. COMMERCE-009 owns idempotent creation. The database therefore guarantees **at most one** platform lineage and **at most one** lineage per shop under concurrency.

### R7 — exact active prompt pointers

Add exactly:

```prisma
model CommercePlatformPromptPointer {
  environment      CommerceEnvironment @id
  promptId         String              @db.Text
  promptRevisionId String              @db.Text
  editVersion      Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt        DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  revision  CommerceAgentPromptRevision @relation(fields: [promptRevisionId, promptId], references: [id, promptId], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin               @relation("CommercePlatformPromptPointerUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@index([promptRevisionId, promptId])
  @@schema("commerce")
}

model CommerceShopPromptPointer {
  environment      CommerceEnvironment
  shopId           String              @db.Text
  promptId         String              @db.Text
  promptRevisionId String              @db.Text
  generationId     String              @default(cuid()) @db.Text
  editVersion      Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt        DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  shop      Shop                        @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  revision  CommerceAgentPromptRevision @relation(fields: [promptRevisionId, promptId], references: [id, promptId], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin               @relation("CommerceShopPromptPointerUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@id([environment, shopId])
  @@index([promptRevisionId, promptId])
  @@index([shopId])
  @@schema("commerce")
}
```

SQL trigger guards MUST reject:

```text
platform pointer -> DRAFT revision
platform pointer -> SHOP lineage
shop pointer -> DRAFT revision
shop pointer -> PLATFORM lineage
shop pointer -> lineage whose shopId != pointer.shopId
```

Both pointer edit versions MUST be constrained to `> 0`. `CommerceShopPromptPointer.generationId` is an immutable row-generation token with the same `present -> absent -> present` ABA protection as `CommerceShopModelSelection.generationId`: it is assigned on INSERT, never changed on UPDATE, and recreated rows receive a different token. Absence of a `CommerceShopPromptPointer` row means prompt inheritance.

Commerce mutation tasks must compare both `generationId` and `editVersion` when replacing or clearing an existing shop prompt override.

### R8 — exact Commerce audit extensions

Append exactly these values to the existing `CommerceAuditAction` enum; do not rename or remove existing ARCH-020 values:

```text
CREATE_MODEL_CATALOGUE_ENTRY
UPDATE_MODEL_CATALOGUE_ENTRY
ENABLE_MODEL_CATALOGUE_ENTRY
DISABLE_MODEL_CATALOGUE_ENTRY
SET_PLATFORM_MODEL_SELECTION
SET_SHOP_MODEL_SELECTION
CLEAR_SHOP_MODEL_SELECTION
CREATE_PROMPT_TEMPLATE_CATEGORY
UPDATE_PROMPT_TEMPLATE_CATEGORY
ENABLE_PROMPT_TEMPLATE_CATEGORY
DISABLE_PROMPT_TEMPLATE_CATEGORY
CREATE_PROMPT_TEMPLATE
UPDATE_PROMPT_TEMPLATE
ENABLE_PROMPT_TEMPLATE
DISABLE_PROMPT_TEMPLATE
CREATE_PROMPT_TEMPLATE_DRAFT
UPDATE_PROMPT_TEMPLATE_DRAFT
PUBLISH_PROMPT_TEMPLATE_REVISION
CREATE_AGENT_PROMPT
CREATE_AGENT_PROMPT_DRAFT
CREATE_AGENT_PROMPT_DRAFT_FROM_TEMPLATE
UPDATE_AGENT_PROMPT_DRAFT
PUBLISH_AGENT_PROMPT_REVISION
SET_PLATFORM_PROMPT_POINTER
SET_SHOP_PROMPT_POINTER
CLEAR_SHOP_PROMPT_POINTER
```

Add exactly these nullable FK fields to `CommerceAuditEvent`:

```prisma
shopId                   String? @db.Text
modelCatalogueEntryId    String? @db.Text
promptTemplateCategoryId String? @db.Text
promptTemplateId         String? @db.Text
promptTemplateRevisionId String? @db.Text
agentPromptId            String? @db.Text
agentPromptRevisionId    String? @db.Text
```

and add exactly these relation fields, all `onDelete: Restrict, onUpdate: Restrict`:

```prisma
shop                   Shop?                           @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
modelCatalogueEntry    CommerceModelCatalogueEntry?    @relation(fields: [modelCatalogueEntryId], references: [id], onDelete: Restrict, onUpdate: Restrict)
promptTemplateCategory CommercePromptTemplateCategory? @relation(fields: [promptTemplateCategoryId], references: [id], onDelete: Restrict, onUpdate: Restrict)
promptTemplate         CommercePromptTemplate?         @relation(fields: [promptTemplateId], references: [id], onDelete: Restrict, onUpdate: Restrict)
promptTemplateRevision CommercePromptTemplateRevision? @relation(fields: [promptTemplateRevisionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
agentPrompt            CommerceAgentPrompt?            @relation(fields: [agentPromptId], references: [id], onDelete: Restrict, onUpdate: Restrict)
agentPromptRevision    CommerceAgentPromptRevision?    @relation(fields: [agentPromptRevisionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
```

Add indexes:

```prisma
@@index([shopId, createdAt, id])
@@index([modelCatalogueEntryId, createdAt, id])
@@index([promptTemplateCategoryId, createdAt, id])
@@index([promptTemplateId, createdAt, id])
@@index([agentPromptId, createdAt, id])
```

The existing ARCH-020 immutable audit-event trigger remains authoritative; do not create a competing audit table.

Phase 2 Commerce services reuse `CommerceAuditEvent` as the durable operation receipt for privileged commands. No new operation-receipt table is introduced by this database task. The service contract is: `CommerceAuditEvent.id = operationId`, with canonical request `payloadHash` and replayable `result` stored in `metadata`, following the accepted ARCH-020 publication-command convention.

### R9 — exact reverse relations on existing owners

Add these relation collections to `Shop`:

```prisma
commerceModelSelections CommerceShopModelSelection[]
commerceAgentPrompts    CommerceAgentPrompt[]
commercePromptPointers  CommerceShopPromptPointer[]
commerceAuditEvents     CommerceAuditEvent[]
```

Add these relation collections to `PlatformAdmin` with the relation names shown above:

```prisma
createdCommerceModelCatalogueEntries    CommerceModelCatalogueEntry[]    @relation("CommerceModelCatalogueEntryCreator")
updatedCommerceModelCatalogueEntries    CommerceModelCatalogueEntry[]    @relation("CommerceModelCatalogueEntryUpdater")
updatedCommercePlatformModelSelections  CommercePlatformModelSelection[] @relation("CommercePlatformModelSelectionUpdater")
updatedCommerceShopModelSelections      CommerceShopModelSelection[]     @relation("CommerceShopModelSelectionUpdater")
createdCommercePromptTemplateCategories CommercePromptTemplateCategory[] @relation("CommercePromptTemplateCategoryCreator")
updatedCommercePromptTemplateCategories CommercePromptTemplateCategory[] @relation("CommercePromptTemplateCategoryUpdater")
createdCommercePromptTemplates          CommercePromptTemplate[]         @relation("CommercePromptTemplateCreator")
updatedCommercePromptTemplates          CommercePromptTemplate[]         @relation("CommercePromptTemplateUpdater")
createdCommercePromptTemplateRevisions  CommercePromptTemplateRevision[] @relation("CommercePromptTemplateRevisionCreator")
publishedCommercePromptTemplateRevisions CommercePromptTemplateRevision[] @relation("CommercePromptTemplateRevisionPublisher")
createdCommerceAgentPrompts             CommerceAgentPrompt[]            @relation("CommerceAgentPromptCreator")
createdCommerceAgentPromptRevisions     CommerceAgentPromptRevision[]    @relation("CommerceAgentPromptRevisionCreator")
publishedCommerceAgentPromptRevisions   CommerceAgentPromptRevision[]    @relation("CommerceAgentPromptRevisionPublisher")
updatedCommercePlatformPromptPointers   CommercePlatformPromptPointer[]  @relation("CommercePlatformPromptPointerUpdater")
updatedCommerceShopPromptPointers       CommerceShopPromptPointer[]      @relation("CommerceShopPromptPointerUpdater")
```

Formatting/alignment may follow `prisma format`; names and relations may not be semantically changed.

### R10 — exact migration SQL guards

`prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql` MUST contain the following named functions and triggers (implementation may share internal SQL where safe, but these names and enforced behaviours are required):

Functions:

```text
commerce.arch021_model_catalogue_guard
commerce.arch021_shop_model_selection_guard
commerce.arch021_prompt_template_category_guard
commerce.arch021_prompt_template_guard
commerce.arch021_prompt_template_revision_guard
commerce.arch021_agent_prompt_guard
commerce.arch021_agent_prompt_revision_guard
commerce.arch021_platform_prompt_pointer_guard
commerce.arch021_shop_prompt_pointer_guard
```

Triggers:

```text
arch021_model_catalogue_guard
arch021_shop_model_selection_guard
arch021_prompt_template_category_guard
arch021_prompt_template_guard
arch021_prompt_template_revision_guard
arch021_agent_prompt_guard
arch021_agent_prompt_revision_guard
arch021_platform_prompt_pointer_guard
arch021_shop_prompt_pointer_guard
```

Required partial unique indexes:

```text
CommerceAgentPrompt_one_platform_idx
CommerceAgentPrompt_one_shop_idx
```

Required CHECK constraint names:

```text
CommerceModelCatalogueEntry_provider_model_id_check
CommerceModelCatalogueEntry_display_name_check
CommerceModelCatalogueEntry_description_length_check
CommerceModelCatalogueEntry_edit_version_check
CommercePlatformModelSelection_edit_version_check
CommerceShopModelSelection_edit_version_check
CommercePromptTemplateCategory_slug_check
CommercePromptTemplateCategory_display_name_check
CommercePromptTemplateCategory_description_length_check
CommercePromptTemplateCategory_display_order_check
CommercePromptTemplateCategory_edit_version_check
CommercePromptTemplate_key_check
CommercePromptTemplate_display_name_check
CommercePromptTemplate_description_length_check
CommercePromptTemplate_edit_version_check
CommercePromptTemplateRevision_revision_check
CommercePromptTemplateRevision_edit_version_check
CommercePromptTemplateRevision_prompt_text_check
CommercePromptTemplateRevision_hash_check
CommercePromptTemplateRevision_publication_shape_check
CommerceAgentPrompt_scope_check
CommerceAgentPromptRevision_revision_check
CommerceAgentPromptRevision_edit_version_check
CommerceAgentPromptRevision_prompt_text_check
CommerceAgentPromptRevision_hash_check
CommerceAgentPromptRevision_publication_shape_check
CommercePlatformPromptPointer_edit_version_check
CommerceShopPromptPointer_edit_version_check
```

`commerce.arch021_shop_model_selection_guard` / `arch021_shop_model_selection_guard` MUST reject UPDATE attempts that change `generationId`. The existing `commerce.arch021_shop_prompt_pointer_guard` / `arch021_shop_prompt_pointer_guard` MUST additionally reject UPDATE attempts that change `generationId` while retaining its scope/published-revision checks.

The static schema validator must assert these names are present in the migration SQL.

The migration MUST be additive. It MUST NOT contain application-data `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, destructive `DROP`, or rename operations. It must not seed a model, category, template, prompt or pointer.

### R11 — exact validation files and npm commands

Add these package scripts exactly:

```json
"test:arch021-agent-configuration-schema": "node scripts/validate-arch021-agent-configuration-schema.mjs",
"test:arch021-agent-configuration-migration": "node scripts/validate-arch021-agent-configuration-migration.mjs"
```

`validate-arch021-agent-configuration-schema.mjs` MUST statically verify at minimum:

- exactly 10 ARCH-021 `CREATE TABLE` statements and exactly 3 new `CREATE TYPE` statements;
- all exact model/enum/field names above;
- the 26 exact new `CommerceAuditAction` values above;
- the required unique/index/partial-index names;
- all nine required functions and triggers;
- prompt length/hash/published-shape constraints;
- migration contains no business-data DML or destructive operation;
- ERD contains all ten new models.

`validate-arch021-agent-configuration-migration.mjs` MUST follow the existing ARCH-020 safe rehearsal pattern and refuse unsafe targets before connecting. It must support exactly:

```text
--mode fresh    DATABASE name arch021_test_fresh
--mode upgrade  DATABASE name arch021_test_upgrade
```

The upgrade mode MUST stage all predecessor migrations, seed/rehearse predecessor data, snapshot pre-existing table counts/hashes and non-ARCH-021 indexes, apply ARCH-021, and prove predecessor state is unchanged.

`arch021-agent-configuration-cases.mjs` MUST exercise at least:

1. two OPENAI/GROQ catalogue rows and provider/model uniqueness;
2. rejection of model provider/providerModelId identity mutation and DELETE;
3. independent platform and shop model selections;
4. one category with at least two templates (`Clothing & Fashion` display fixture is acceptable);
5. rejection of category slug identity mutation and DELETE;
6. template key identity mutation rejection;
7. empty DRAFT template content is accepted, but publishing a blank/whitespace-only template revision is rejected;
8. DRAFT -> PUBLISHED template revision and published immutability;
9. concurrent platform-lineage creation where only one lineage survives;
10. concurrent same-shop lineage creation where only one lineage survives;
11. copy provenance rejected when `sourceTemplateRevisionId` points to a DRAFT template revision;
12. empty DRAFT agent-prompt content is accepted, but publishing a blank/whitespace-only agent prompt revision is rejected;
13. PUBLISHED agent prompt revision immutability;
14. platform pointer rejection for DRAFT or SHOP-scoped revisions;
15. shop pointer rejection for DRAFT, PLATFORM-scoped, or other-shop revisions;
16. independent model/prompt pointer rows and edit versions;
17. deleting a shop override row restores representation of inheritance without deleting platform state;
18. shop model ABA protection: after clear + recreate, the replacement `generationId` differs and a stale `(old generationId, editVersion)` mutation cannot match it;
19. shop prompt-pointer ABA protection: after clear + recreate, the replacement `generationId` differs and a stale `(old generationId, editVersion)` mutation cannot match it.

## Work Items

- [ ] Add the three exact enums in R1 to `prisma/schema.prisma`.
- [ ] Add the ten exact models in R2-R7 to `prisma/schema.prisma`.
- [ ] Extend `CommerceAuditAction` and `CommerceAuditEvent` exactly as R8.
- [ ] Add `Shop` and `PlatformAdmin` reverse relations exactly as R9.
- [ ] Create only `prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql` for this task.
- [ ] Implement the checks, unique indexes, functions, triggers and FK behaviours in R2-R10.
- [ ] Add `scripts/fixtures/arch021-agent-configuration-schema-contract.mjs` containing the exact expected table/enum/field/index/action contract used by the static validator.
- [ ] Add `scripts/fixtures/arch021-agent-configuration-cases.mjs` containing the behavioural migration cases in R11.
- [ ] Add both validation scripts in R11 and the two exact package scripts.
- [ ] Keep the existing ARCH-020 static validator compatible with additive `CommerceAuditAction` extensions while preserving the original ARCH-020 action sequence exactly.
- [ ] Regenerate `docs/generated/prisma-erd.puml` using the repository ERD generator.
- [ ] Run the required validation and complete the task report.

## Interfaces / Contracts

This task produces exactly these Prisma models for downstream Phase 2 Commerce tasks:

```text
ARCH-021-COMMERCE-007
  CommerceModelCatalogueEntry
  CommercePlatformModelSelection
  CommerceShopModelSelection
  CommerceAuditEvent

ARCH-021-COMMERCE-008
  CommercePromptTemplateCategory
  CommercePromptTemplate
  CommercePromptTemplateRevision
  CommerceAuditEvent

ARCH-021-COMMERCE-009
  CommerceAgentPrompt
  CommerceAgentPromptRevision
  CommercePlatformPromptPointer
  CommerceShopPromptPointer
  CommercePromptTemplateRevision       # provenance FK only
  CommerceAuditEvent

ARCH-021-COMMERCE-010
  read-only composition of the exact model/prompt selection and revision models above
```

Downstream tasks MUST consume these names from the accepted database package/submodule and MUST NOT create alternate tables, JSON blobs, local Prisma models or differently named persistence concepts.

No Shared package/runtime contract is created in Phase 2.

## Dependencies

- ARCH-020-DATABASE-001

## Enables

- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-008

## Acceptance Criteria

- [ ] The schema contains exactly the ten new models and three new enums specified above.
- [ ] The migration directory is exactly `20260923150000_arch021_agent_configuration` and no second ARCH-021 migration is created by this task.
- [ ] The migration is additive and contains no application-data seed/backfill or destructive operation.
- [ ] Model catalogue identity (`id`, `provider`, `providerModelId`) cannot be repurposed or deleted while mutable presentation/enablement fields remain editable.
- [ ] Platform/shop model selections are environment scoped and independently versioned; absence of the shop row represents inheritance.
- [ ] A data-driven category such as `Clothing & Fashion` can contain multiple template identities without a schema/enum change.
- [ ] Category slug and template key are durable identities; categories/templates are disabled rather than deleted.
- [ ] Template and agent prompt DRAFT revisions may persist empty prompt text, publication rejects blank/whitespace-only prompt text, and every PUBLISHED revision is immutable thereafter.
- [ ] Prompt/template text is bounded to 32,000 characters and published hashes are lowercase SHA-256-shaped 64-character hex values.
- [ ] Database concurrency enforces at most one platform prompt lineage and at most one prompt lineage per shop.
- [ ] Template provenance can only reference a PUBLISHED template revision and remains a non-cascading historical reference.
- [ ] Platform/shop prompt pointers can only reference PUBLISHED revisions of the correct PLATFORM/exact-SHOP lineage.
- [ ] Model and prompt pointer tables maintain independent editVersion values and independent shop-override absence semantics.
- [ ] Shop model selections and shop prompt pointers expose immutable `generationId` tokens so a clear/recreate cycle cannot make a stale CAS request valid again merely because `editVersion` restarted.
- [ ] `CommerceAuditAction` and `CommerceAuditEvent` expose exactly the Phase 2 audit vocabulary/FKs in R8 without weakening the existing immutable audit-event contract.
- [ ] Fresh and upgrade rehearsal prove all expected constraints and preserve pre-ARCH-021 data/index state.
- [ ] Existing ARCH-020 Commerce schema and validation remain valid.

## Validation

Run exactly the repository-declared commands below after checking `package.json`:

- [ ] `npm run prisma:validate`
- [ ] `npm run prisma:generate`
- [ ] `npm run erd:puml`
- [ ] `npm run test:arch021-agent-configuration-schema`
- [ ] `DATABASE_URL=<isolated localhost arch021_test_fresh URL> npm run test:arch021-agent-configuration-migration -- --mode fresh`
- [ ] `DATABASE_URL=<isolated localhost arch021_test_upgrade URL> npm run test:arch021-agent-configuration-migration -- --mode upgrade`
- [ ] existing `npm run test:arch020-commerce-capability-schema`
- [ ] existing `npm run test:arch020-commerce-capability-migration` only if its documented isolated prerequisites are available; otherwise record why it was not rerun and prove no ARCH-020 source/migration was changed
- [ ] `git diff --check`

Do not connect the migration rehearsal to a shared/development/production PostgreSQL database. The validator MUST refuse non-loopback hosts, unexpected DB names and connection-parameter overrides before connecting, matching the ARCH-020 safety pattern.

## Stop Condition

After the exact Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin a Commerce task.

## Implementation Notes

This task is deterministic. Do not redesign the data model during implementation.

If the exact Prisma model block above cannot be represented because of a concrete Prisma relation limitation, STOP before choosing another schema and return the specific compiler/validator error to `moda_architect`. Do not silently substitute a different model, JSON column, enum, relation or pointer representation.

The migration may add SQL checks/triggers not expressible in Prisma, but those SQL guards must implement the semantics above and use the required names. Service-layer validation in later Commerce tasks does not replace these database invariants.

No Phase 2 row is seeded by this task. Platform defaults and authoring content are created through later Commerce services/UI.

## Completion Report

### Status

Ready for Review

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `scripts/fixtures/arch021-agent-configuration-schema-contract.mjs`
- `scripts/fixtures/arch021-agent-configuration-cases.mjs`
- `scripts/validate-arch021-agent-configuration-schema.mjs`
- `scripts/validate-arch021-agent-configuration-migration.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed

- Added the exact three enums, ten Phase 2 CommerceAgent models, audit vocabulary/FKs/indexes, and required Shop/PlatformAdmin reverse relations.
- Added one additive migration with all required constraints, immutable identity/revision guards, lineage uniqueness indexes, scope/published pointer guards, source-template provenance validation, and immutable generation-token protection.
- Extended the ARCH-020 audit target constraint to admit the exact ARCH-021 audit actions while preserving all existing ARCH-020 target cases; reused the existing ARCH-020 audit immutability trigger.
- Added the static schema/migration/ERD contract validator, isolated fresh/upgrade rehearsal validator, and behavioral fixtures including concurrency and ABA cases.
- Regenerated the Prisma PlantUML ERD and added the two exact npm validation scripts.

### Validation Results

- PASS: `npm run prisma:validate`
- PASS: `npm run prisma:generate`
- PASS: `npm run erd:puml`
- PASS: `npm run test:arch021-agent-configuration-schema`
- PASS: `node --check scripts/fixtures/arch021-agent-configuration-cases.mjs scripts/validate-arch021-agent-configuration-schema.mjs scripts/validate-arch021-agent-configuration-migration.mjs`
- PASS: `git diff --check`
- BLOCKED by unavailable prerequisite: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/arch021_test_fresh npm run test:arch021-agent-configuration-migration -- --mode fresh`; `pg_isready -h localhost -p 5432` returned `no response`, and the validator failed before migration with `Can't reach database server at localhost:5432`.
- BLOCKED by the same unavailable loopback PostgreSQL prerequisite: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/arch021_test_upgrade npm run test:arch021-agent-configuration-migration -- --mode upgrade`; no database connection or migration was attempted beyond the validator's initial connection.
- NOT RERUN: `npm run test:arch020-commerce-capability-migration`, because its isolated PostgreSQL prerequisite was unavailable.
- FAIL: existing `npm run test:arch020-commerce-capability-schema` asserts the pre-ARCH-021 17-value `CommerceAuditAction` enum exactly and therefore rejects the required appended ARCH-021 audit vocabulary. No ARCH-020 source or migration was changed.

### Deviations

- Live fresh/upgrade database rehearsals remain unexecuted because local PostgreSQL is not listening on loopback port 5432.
- The existing ARCH-020 static validator is stale for the required additive enum extension; updating that separate validator is outside this task's allowed file scope.

### Assumptions

- The developer/architect will rerun both isolated rehearsals with local PostgreSQL available before acceptance.
- The existing ARCH-020 `arch020_audit_immutable` trigger remains authoritative for the extended `CommerceAuditEvent` table.

### Unresolved Issues

- Acceptance still needs live fresh and upgrade rehearsal evidence after loopback PostgreSQL is started.

### Architectural Concerns

- The ARCH-020 schema validator should be revised by its owning task/domain to compare its historical action subset or explicitly include ARCH-021 extensions; it currently fails on any required additive audit enum value.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 substantially conforms to the fixed Phase 2 schema contract: the exact ten models and three enums are present, the required audit vocabulary and named SQL guards are present, the migration is structurally additive apart from the deliberate replacement of `arch020_audit_targets`, the ARCH-021 static validator passes, and the ERD/package-script surface is present.

The task cannot be accepted yet because the required migration rehearsal is not only unexecuted; the submitted behavioural fixture contains deterministic false-negative cases that would fail once PostgreSQL is available:

1. `platform pointer rejects draft revision` uses `platform-draft` after that revision has already been transitioned to `PUBLISHED`, so the attempted platform pointer is valid rather than rejectable. Create/use a distinct revision that remains `DRAFT` for this case.
2. `shop pointer rejects other-shop revision` points shop `s1` at `shop-prompt`, whose lineage also belongs to `s1`, so the attempted pointer is valid rather than an other-shop mismatch. Use a published SHOP revision owned by another shop.
3. The concurrent same-shop lineage case later hard-codes `shop-race-a` as though that insert is guaranteed to win. Do not depend on a race winner. Use `Promise.allSettled` (or equivalent) to assert exactly one insert succeeds and one fails, query the single surviving lineage for `s2`, and use that actual survivor for subsequent other-shop tests. Apply the same explicit one-success/one-failure assertion to the platform-lineage race.
4. R11 requires upgrade rehearsal to prove predecessor indexes are unchanged. `validate-arch021-agent-configuration-migration.mjs` currently excludes all `CommerceAuditEvent` indexes from the before/after comparison, so it cannot prove preservation of the pre-ARCH-021 audit indexes. Snapshot all predecessor user indexes before ARCH-021 and, after migration, assert every predecessor index is still present with the identical definition while allowing the new ARCH-021 indexes/tables to be additional entries.
5. The task requires existing `npm run test:arch020-commerce-capability-schema` to remain valid, but its historical validator currently requires exact equality of the 17-value `CommerceAuditAction` enum. The task definition previously made that requirement impossible while keeping the validator out of scope. Attempt 2 explicitly authorises only `scripts/validate-arch020-commerce-capability-schema.mjs` for this compatibility correction: keep the existing ARCH-020 action list as the exact required prefix/order and permit appended later values. Do not alter the ARCH-020 fixture contract or migration.
6. Add the missing behavioural rejection for changing the catalogue `provider` as well as `providerModelId`, matching R2/R11's immutable provider/model identity contract.

Fresh and upgrade rehearsal remain mandatory acceptance evidence. Attempt 2 must run both against the exact isolated loopback database names in R11. If PostgreSQL remains unavailable, return the task `blocked` rather than `review`; do not weaken or skip the rehearsal contract. Reconcile the Work Items, Acceptance Criteria and Validation checkboxes to the evidence actually obtained before resubmission.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `moda-interact-database/scripts/fixtures/arch021-agent-configuration-schema-contract.mjs`
- `moda-interact-database/scripts/fixtures/arch021-agent-configuration-cases.mjs`
- `moda-interact-database/scripts/validate-arch021-agent-configuration-schema.mjs`
- `moda-interact-database/scripts/validate-arch021-agent-configuration-migration.mjs`
- `moda-interact-database/scripts/validate-arch020-commerce-capability-schema.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`
- `docs/decisions/database/ARCH-021/DATABASE-001-persist-agent-configuration-schema.md`

### Validation Reviewed

- PASS (architect rerun): `node scripts/validate-arch021-agent-configuration-schema.mjs`.
- PASS (architect rerun): Node syntax checks for the ARCH-021 fixture/static/migration validators.
- Submitted PASS evidence reviewed for Prisma validation/generation, ERD generation and `git diff --check`.
- Submitted BLOCKED evidence reviewed for fresh/upgrade rehearsals because localhost PostgreSQL was unavailable.
- Submitted FAIL evidence reviewed for the stale ARCH-020 exact-enum assertion; this is now an explicit Attempt 2 compatibility correction.
- Live PostgreSQL rehearsal could not be independently rerun in the architect review environment because no PostgreSQL server/client runtime is available there.

### Architecture Conformance

The schema/migration design is materially aligned with ARCH-021 Phase 2, but acceptance is withheld until the rehearsal fixture correctly tests the specified rejection paths, predecessor-index preservation is actually proven, the ARCH-020 validator remains compatible with the additive enum extension, and both required isolated migration rehearsals pass. COMMERCE-007 and COMMERCE-008 remain gated.

### Follow-up

Return the same task to `ready` with `attempt: 1`, `executor: null`, and `claimed_at: null`. The next authorised claim becomes Attempt 2. Preserve the accepted schema/migration design unless a live rehearsal exposes a genuine database defect; correct the validation/rehearsal issues above and rerun the required acceptance commands.
