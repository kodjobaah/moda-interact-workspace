---
id: ARCH-047-DATABASE-001
architecture_id: ARCH-047
title: Persist Moda-authored templates, translations, Meta registrations and publication
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 15
executor: developer
claimed_at: 2026-10-23T17:33:17Z
attempt: 1
depends_on: []
enables: []
created: 2026-10-23
updated: 2026-10-24
---

# Persist ARCH-047 template authoring and publication records

## Architecture

Architecture ID: `ARCH-047`

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`

Coordinator: `moda_architect`

**One consolidated Database implementation.** This task includes the database scope formerly proposed as `ARCH-047-DATABASE-001` through `DATABASE-004`. Do **not** create `DATABASE-002`–`004`. It amends the existing developer-owned `DATABASE-001` (in progress, Attempt 1) and preserves its claim. The parent ARCH-047 architecture and obsolete external-import Admin tasks require separate architect reconciliation; this task does not authorise their changes.

## Objective

Implement the **exact, simplified 11-table** Prisma/PostgreSQL persistence contract below in one additive ARCH-047 migration: Moda-authored template definitions and multilingual ASTs; background translation runs/items/Batch evidence; Meta registration and unified submission/status event history; resilient per-shop publication; one active pointer per internal conversation-wrapper audience; and existing Commerce audit integration. **No separate release or release-locale tables are introduced.** A new `WhatsAppTemplateDefinition` is the identity for each new content version; application services control its publication state.

The task is deliberately one cohesive database implementation. PostgreSQL owns technical relations, record-identity uniqueness and lookup indexes. **Template business rules are entirely application-owned**: authorisation, content immutability, supported types/languages, 20/20 review and Meta approval, active assignment choice, wrapper applicability and read-only checkout access.

## Context

Inspected 24 October task worktree:

- `whatsapp.WhatsAppTemplateVariant` is the existing shop-level sender/WABA/purpose/language assignment; it has no Moda-authored definition/registration provenance.
- `commerce.CommerceAuditEvent` and `CommerceAuditAction` already exist. Historical ARCH-047 migration `20261023173000_arch047_whatsapp_template_audit_actions` added six variant-action values; it must not be rewritten.
- `commerce.CommerceAuditEvent` has the legacy exhaustive `arch020_audit_targets` CHECK. New audit labels must be recognised without changing historical branches or adding new template-specific actor/shop checks.
- ARCH-031 owns the proven `CommerceStoreCategoryTranslationRun`, `Item`, `Batch`, `BatchItem` persistence pattern and `CommerceTranslationModelConfiguration`. Reuse the mechanics and model reference, not its store-category data or table names.

Agreed behaviour: **create immutable English content in Moda Admin → request Background translation → generate/review 19 further locales → submit Meta language versions → reconcile individual status webhooks → explicitly publish to eligible shops**. An AI/human conversation wrapper uses the same authoring/translation records but has no Meta registration; Admin activates its definition through an internal pointer. Templates created outside Moda are not adopted. Content changes require **Clone as New** with a new definition/provider name. The CommerceAgent remains read-only; checkout mutations are out of scope.

### Simplification from the previous DB001 design

| Previous model(s) | New approach |
|---|---|
| `WhatsAppTemplateRelease`, `WhatsAppTemplateReleaseLocale` | Removed. The immutable definition is the version; approved/published/retired state is recorded on it by the application. The English source AST is stored only in its locale row. |
| `WhatsAppTemplateMetaSubmission`, `MetaSubmissionAttempt`, `MetaStatusReceipt` | Replaced by `WhatsAppTemplateMetaRegistration` (current per-WABA/locale provider metadata and frozen submitted components) plus `WhatsAppTemplateMetaEvent` (one append-only event ledger for attempts, webhooks and reconciliation). |
| Shop publication referencing a release | `WhatsAppTemplatePublicationOperation.definitionId`, with target records and `WhatsAppTemplateVariant.metaRegistrationId` for deployed provider-language identity. |
| Wrapper active pointer referencing a release | `WhatsAppConversationWrapperActiveSlot.definitionId`; application checks definition kind and approval. |
| Four translation tables | Retained to support existing provider Batch retries, uncertain outcomes and per-language correlation. |

## Scope

Modify **only** `moda-interact-database/` for Prisma schema, additive migration, focused database validators and PostgreSQL proof. Required primary paths, relative to that repository:

```text
prisma/schema.prisma
prisma/migrations/20261024133000_arch047_template_persistence/migration.sql
scripts/validate-arch047-template-persistence-schema.mjs
scripts/validate-arch047-template-persistence-migration.mjs
scripts/test-arch047-template-persistence-validator-mutations.mjs
scripts/test-arch047-template-persistence-postgres.mjs
package.json
```

The migration path is fixed and follows the existing 2026-10-23 ARCH-047 audit migration. Test-only fixtures/helpers are permitted. Do not add unrequested tables, other domain services, SQL functions/triggers, or edit historical migrations. Regenerate ERD artifacts only when required by the repository's existing schema-generation workflow and record that change.

## Out of Scope

- Admin AST builder/permissions, Clone as New, translation review, publication approval and shop override decisions.
- Background translation execution, queues, provider Batch calls, Meta Graph API create/status requests, webhook consumption, retry policies and runtime parameter resolution.
- Shared AST contracts, typed variable registry, locale/Meta language mappings, schema/runtime validation, and provider event normalisation.
- External template adoption, Meta edit-existing-template requests, or merchant-created templates.
- Changes to `Conversation`/`CheckoutRecovery`; checkout/cart write capabilities; new generic audit tables.
- Any new DB template business constraint, including SQL rules based on kind, purpose, offer type, audience, approval, enabled state, WABA compatibility, 20-language completeness, or release eligibility; no business triggers, functions, or partial state-dependent unique indexes.
- Changes to `docs/decisions/**/_index.md`, parent architecture, or consumer repositories.

## Requirements

### R1. Database/application ownership boundary — exact

Database owns only primary keys, foreign keys, uniqueness of **technical identities**, nullable history/provenance references and ordinary indexes. `kind`, `purpose`, `offerType`, `audience`, workflow statuses, provider category and language tags are **strings**; their business meanings are validated in Admin/Background/Shared, not PostgreSQL enums or CHECK constraints. No new ARCH-047 business trigger/function/CHECK is permitted. The existing `WhatsAppTemplateStatus` enum for historical `WhatsAppTemplateVariant` is unchanged.

Application services must transactionally enforce Admin-only authorship, new-definition identity for changed content, source/target consistency, 20-language completeness/review, Meta approval, WABA/shop matching, publish and retire decisions, no external adoption, wrapper eligibility, and read-only commerce behaviour. PostgreSQL may store combinations that an application would reject; this is intentional.

### R2. Add `WhatsAppTemplateDefinition` and `WhatsAppTemplateLocale` **exactly**

```prisma
model WhatsAppTemplateDefinition {
  id                     String    @id @default(cuid()) @db.Text
  kind                   String    @db.VarChar(40)
  purpose                String?   @db.VarChar(96)
  offerType              String?   @db.VarChar(32)
  audience               String?   @db.VarChar(24)
  wabaId                 String?   @db.VarChar(191)
  providerTemplateName   String?   @db.VarChar(255)
  category               String?   @db.VarChar(32)
  sourceLanguageTag      String    @db.VarChar(16)
  astSchemaVersion       Int
  sourceHash             String    @db.VarChar(64)
  status                 String    @db.VarChar(32)
  publishedAt            DateTime? @db.Timestamptz(3)
  retiredAt              DateTime? @db.Timestamptz(3)
  createdByAdminId       String    @db.Text
  clonedFromDefinitionId String?   @db.Text
  createdAt              DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt              DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  createdByAdmin PlatformAdmin @relation("WhatsAppTemplateDefinitionCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  clonedFrom     WhatsAppTemplateDefinition? @relation("WhatsAppTemplateDefinitionClone", fields: [clonedFromDefinitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  clones         WhatsAppTemplateDefinition[] @relation("WhatsAppTemplateDefinitionClone")
  locales        WhatsAppTemplateLocale[]
  translationRuns WhatsAppTemplateTranslationRun[]
  publications   WhatsAppTemplatePublicationOperation[]
  activeWrappers WhatsAppConversationWrapperActiveSlot[]

  @@index([kind, purpose, createdAt])
  @@index([status, publishedAt])
  @@index([createdByAdminId, createdAt])
  @@index([clonedFromDefinitionId])
  @@schema("whatsapp")
}

model WhatsAppTemplateLocale {
  id                   String    @id @default(cuid()) @db.Text
  definitionId         String    @db.Text
  languageTag          String    @db.VarChar(16)
  providerLanguageCode String?   @db.VarChar(16)
  localeAst            Json?     @db.JsonB
  contentHash          String?   @db.VarChar(64)
  status               String    @db.VarChar(32)
  reviewedByAdminId    String?   @db.Text
  reviewedAt           DateTime? @db.Timestamptz(3)
  createdAt            DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt            DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  definition        WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  reviewedByAdmin   PlatformAdmin? @relation("WhatsAppTemplateLocaleReviewer", fields: [reviewedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  metaRegistrations WhatsAppTemplateMetaRegistration[]
  translationResults WhatsAppTemplateTranslationItem[] @relation("WhatsAppTemplateTranslationResultLocale")

  @@unique([definitionId, languageTag])
  @@index([status, updatedAt])
  @@index([reviewedByAdminId, reviewedAt])
  @@schema("whatsapp")
}
```

**One canonical AST per language.** The English AST is stored in the locale row whose `languageTag` equals the definition's `sourceLanguageTag`; it is **not** also copied to a definition-level `englishAst`. The definition retains the canonical source hash and authoring metadata, while the locale carries content. The application creates both in one transaction and prevents in-place content edits after save. The DB does not require an English locale, minimum/maximum locale count, or specific `kind`, `audience`, or language values. `clonedFromDefinitionId` is optional provenance; clone means a **new definition row**, not a write to the source.

### R3. Add translation run, item, batch and membership **exactly**

Use the ARCH-031 patterns with these new, independently owned tables:

```prisma
model WhatsAppTemplateTranslationRun {
  id                              String   @id @default(cuid()) @db.Text
  definitionId                    String   @db.Text
  translationModelConfigurationId String   @db.Text
  provider                        String   @db.VarChar(64)
  providerModelId                 String   @db.VarChar(255)
  modelConfigurationVersion       Int
  sourceSchemaVersion             Int
  sourceHash                      String   @db.VarChar(64)
  sourceSnapshot                  Json     @db.JsonB
  status                          String   @db.VarChar(32)
  requestedByAdminId              String   @db.Text
  requestedAt                     DateTime @default(now()) @db.Timestamptz(3)
  startedAt                       DateTime? @db.Timestamptz(3)
  completedAt                     DateTime? @db.Timestamptz(3)
  failureCode                     String?  @db.VarChar(128)
  createdAt                       DateTime @default(now()) @db.Timestamptz(3)
  updatedAt                       DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  definition       WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  translationModel CommerceTranslationModelConfiguration @relation(fields: [translationModelConfigurationId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  requestedBy      PlatformAdmin @relation("WhatsAppTemplateTranslationRunRequester", fields: [requestedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  items            WhatsAppTemplateTranslationItem[]
  batches          WhatsAppTemplateTranslationBatch[]

  @@index([definitionId, status, requestedAt])
  @@index([status, requestedAt])
  @@index([translationModelConfigurationId, requestedAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateTranslationItem {
  id                String    @id @default(cuid()) @db.Text
  runId             String    @db.Text
  targetLanguageTag String    @db.VarChar(16)
  translatedAst     Json?     @db.JsonB
  outputContentHash String?   @db.VarChar(64)
  resultLocaleId    String?   @db.Text
  status            String    @db.VarChar(32)
  failureCode       String?   @db.VarChar(128)
  retryCount        Int       @default(0)
  nextAttemptAt     DateTime? @db.Timestamptz(3)
  currentBatchId    String?   @db.Text
  completedAt       DateTime? @db.Timestamptz(3)
  createdAt         DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  run          WhatsAppTemplateTranslationRun @relation(fields: [runId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  resultLocale WhatsAppTemplateLocale? @relation("WhatsAppTemplateTranslationResultLocale", fields: [resultLocaleId], references: [id], onDelete: SetNull, onUpdate: Restrict)
  currentBatch WhatsAppTemplateTranslationBatch? @relation("WhatsAppTemplateTranslationItemCurrentBatch", fields: [currentBatchId], references: [id], onDelete: SetNull, onUpdate: Restrict)
  batchItems   WhatsAppTemplateTranslationBatchItem[]

  @@unique([runId, targetLanguageTag])
  @@index([status, currentBatchId, nextAttemptAt, createdAt])
  @@index([resultLocaleId])
  @@schema("whatsapp")
}

model WhatsAppTemplateTranslationBatch {
  id                   String    @id @default(cuid()) @db.Text
  runId                String    @db.Text
  provider             String    @db.VarChar(64)
  model                String    @db.VarChar(255)
  status               String    @db.VarChar(32)
  providerBatchId      String?   @db.Text
  inputFileId          String?   @db.Text
  outputFileId         String?   @db.Text
  errorFileId          String?   @db.Text
  submissionStartedAt  DateTime? @db.Timestamptz(3)
  lastSubmitAttemptAt  DateTime? @db.Timestamptz(3)
  submitAttemptCount   Int       @default(0)
  nextSubmitAt         DateTime? @db.Timestamptz(3)
  submittedAt          DateTime? @db.Timestamptz(3)
  lastPolledAt         DateTime? @db.Timestamptz(3)
  nextPollAt           DateTime? @db.Timestamptz(3)
  pollSequence         Int       @default(0)
  completedAt          DateTime? @db.Timestamptz(3)
  failureCode          String?   @db.VarChar(128)
  createdAt            DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt            DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  run          WhatsAppTemplateTranslationRun @relation(fields: [runId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  currentItems WhatsAppTemplateTranslationItem[] @relation("WhatsAppTemplateTranslationItemCurrentBatch")
  items        WhatsAppTemplateTranslationBatchItem[]

  @@unique([provider, providerBatchId])
  @@index([runId, status, createdAt])
  @@index([status, nextSubmitAt, createdAt])
  @@index([status, nextPollAt, createdAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateTranslationBatchItem {
  id                String   @id @default(cuid()) @db.Text
  batchId           String   @db.Text
  translationItemId String   @db.Text
  providerCustomId  String   @unique @db.VarChar(255)
  createdAt         DateTime @default(now()) @db.Timestamptz(3)

  batch           WhatsAppTemplateTranslationBatch @relation(fields: [batchId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  translationItem WhatsAppTemplateTranslationItem @relation(fields: [translationItemId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@unique([batchId, translationItemId])
  @@index([translationItemId, createdAt])
  @@schema("whatsapp")
}
```

These tables persist partial, interrupted, duplicated and retried provider work. Background owns the meaning of statuses, target-language count, model prompt construction, retry/deadline policy, source-hash comparisons and applying translated output to locales. Batch custom IDs and run/item keys are **technical correlation identifiers**, not content gates.

### R4. Add Meta registration and unified event history **exactly**

```prisma
model WhatsAppTemplateMetaRegistration {
  id                   String    @id @default(cuid()) @db.Text
  localeId             String    @db.Text
  wabaId               String    @db.VarChar(191)
  providerTemplateName String    @db.VarChar(255)
  providerLanguageCode String    @db.VarChar(16)
  category             String    @db.VarChar(32)
  componentsSnapshot   Json      @db.JsonB
  submittedContentHash String    @db.VarChar(64)
  providerTemplateId   String?   @db.VarChar(191)
  submissionState      String    @db.VarChar(32)
  providerStatus       String?   @db.VarChar(32)
  failureCode          String?   @db.VarChar(128)
  lastSubmittedAt      DateTime? @db.Timestamptz(3)
  nextRetryAt          DateTime? @db.Timestamptz(3)
  lastReconciledAt     DateTime? @db.Timestamptz(3)
  createdAt            DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt            DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  locale   WhatsAppTemplateLocale @relation(fields: [localeId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  events   WhatsAppTemplateMetaEvent[]
  variants WhatsAppTemplateVariant[] @relation("WhatsAppTemplateVariantMetaRegistration")

  @@unique([wabaId, providerTemplateName, providerLanguageCode])
  @@unique([wabaId, providerTemplateId])
  @@index([localeId, createdAt])
  @@index([submissionState, nextRetryAt, createdAt])
  @@index([providerStatus, updatedAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateMetaEvent {
  id                   String    @id @default(cuid()) @db.Text
  eventIdentity        String    @unique @db.VarChar(191)
  registrationId       String?   @db.Text
  source               String    @db.VarChar(32)
  eventType            String    @db.VarChar(64)
  outcome              String?   @db.VarChar(32)
  attemptNumber        Int?
  wabaId               String    @db.VarChar(191)
  providerTemplateId   String?   @db.VarChar(191)
  providerTemplateName String?   @db.VarChar(255)
  providerLanguageCode String?   @db.VarChar(16)
  requestDigest        String?   @db.VarChar(64)
  providerRequestId    String?   @db.VarChar(191)
  httpStatus           Int?
  providerStatus       String?   @db.VarChar(32)
  failureCode          String?   @db.VarChar(128)
  reasonCode           String?   @db.VarChar(128)
  evidence             Json?     @db.JsonB
  receivedAt           DateTime  @default(now()) @db.Timestamptz(3)
  processedAt          DateTime? @db.Timestamptz(3)

  registration WhatsAppTemplateMetaRegistration? @relation(fields: [registrationId], references: [id], onDelete: SetNull, onUpdate: Restrict)

  @@index([registrationId, receivedAt])
  @@index([wabaId, providerTemplateName, providerLanguageCode, receivedAt])
  @@index([processedAt, receivedAt])
  @@schema("whatsapp")
}
```

`WhatsAppTemplateMetaRegistration` is the mutable **current provider projection for a submitted locale on a specific WABA**. Its `componentsSnapshot`/`submittedContentHash` contain the exact frozen content originally submitted through Moda; provider status updates do not rewrite these payloads. App code ensures requests with changed content create a **new definition/name/registration**, never edit the old Meta template.

`WhatsAppTemplateMetaEvent` is one append-only **event ledger** for submission attempts/outcomes, Meta status webhooks and explicit provider reconciliation. `source`, `eventType`, `outcome`, `attemptNumber` and `providerStatus` are application-valued strings/numbers, not database workflow gates. `eventIdentity` deduplicates the same technical receipt/retry; `registrationId` is nullable so unmatched Meta notifications can be recorded **without importing/adopting external templates**. Persist bounded/redacted `evidence` only; never credentials, large raw webhook bodies or unnecessary customer data. After a timeout, application reconciliation checks Meta before retrying a create operation. Provider identity uniqueness is technical; approval and provenance are application checks.

### R5. Add shop publication operations and legacy assignment reference **exactly**

```prisma
model WhatsAppTemplatePublicationOperation {
  id                 String    @id @default(cuid()) @db.Text
  definitionId       String    @db.Text
  requestedByAdminId String    @db.Text
  operationKey       String    @unique @db.VarChar(128)
  scopeSnapshot      Json      @db.JsonB
  status             String    @db.VarChar(32)
  totalTargets       Int?
  succeededTargets   Int       @default(0)
  failedTargets      Int       @default(0)
  nextPageCursor     String?   @db.Text
  failureCode        String?   @db.VarChar(128)
  requestedAt        DateTime  @default(now()) @db.Timestamptz(3)
  completedAt        DateTime? @db.Timestamptz(3)
  createdAt          DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt          DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  definition  WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  requestedBy PlatformAdmin @relation("WhatsAppTemplatePublicationRequester", fields: [requestedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  targets     WhatsAppTemplatePublicationTarget[]

  @@index([definitionId, status, createdAt])
  @@index([status, updatedAt])
  @@schema("whatsapp")
}

model WhatsAppTemplatePublicationTarget {
  id                String    @id @default(cuid()) @db.Text
  operationId       String    @db.Text
  shopId            String    @db.Text
  previousVariantId String?   @db.Text
  newVariantId      String?   @db.Text
  status            String    @db.VarChar(32)
  failureCode       String?   @db.VarChar(128)
  retryCount        Int       @default(0)
  processedAt       DateTime? @db.Timestamptz(3)
  createdAt         DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  operation       WhatsAppTemplatePublicationOperation @relation(fields: [operationId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  shop            Shop @relation("WhatsAppTemplatePublicationTargetShop", fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  previousVariant WhatsAppTemplateVariant? @relation("WhatsAppTemplatePublicationPreviousVariant", fields: [previousVariantId], references: [id], onDelete: SetNull, onUpdate: Restrict)
  newVariant      WhatsAppTemplateVariant? @relation("WhatsAppTemplatePublicationNewVariant", fields: [newVariantId], references: [id], onDelete: SetNull, onUpdate: Restrict)

  @@unique([operationId, shopId])
  @@index([shopId, status, createdAt])
  @@index([status, updatedAt])
  @@schema("whatsapp")
}
```

Add to **existing** `WhatsAppTemplateVariant` (preserve all existing columns, enum values, uniqueness, indexes and historical rows):

```prisma
// New fields within existing WhatsAppTemplateVariant
metaRegistrationId String? @db.Text
metaRegistration   WhatsAppTemplateMetaRegistration? @relation("WhatsAppTemplateVariantMetaRegistration", fields: [metaRegistrationId], references: [id], onDelete: Restrict, onUpdate: Restrict)
publicationPreviousTargets WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationPreviousVariant")
publicationNewTargets      WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationNewVariant")

// New index within existing WhatsAppTemplateVariant
@@index([metaRegistrationId])
```

`metaRegistrationId` is **nullable, with no default**. A legacy or externally authored variant remains unlinked and is not silently adopted. Each new assignment uses a known Moda registration and the existing provider-template fields; Admin validates that registration, shop WABA, purpose and language match. No SQL release-locale table, state-dependent unique slot or Meta approval CHECK is added. Idempotent `operationKey` plus unique `(operationId, shopId)` permits retryable per-shop progress; authorised replacement is application logic.

### R6. Add platform-level conversation wrapper active pointer **exactly**

```prisma
model WhatsAppConversationWrapperActiveSlot {
  audience         String   @id @db.VarChar(24)
  definitionId     String   @db.Text
  editVersion      Int      @default(0)
  updatedByAdminId String   @db.Text
  updatedAt        DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  definition WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy  PlatformAdmin @relation("WhatsAppConversationWrapperSlotUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@index([definitionId])
  @@schema("whatsapp")
}
```

This is one current definition pointer per application audience (`SHARED`, `AI`, `HUMAN`), **as interpreted by Admin/Background**. `audience` is a string, not a database enum/CHECK, and the FK does not assert the definition is actually a wrapper. `editVersion` supports application-owned compare-and-swap. Wrapper content lives in the same Definition/Locale tables and never requires Meta registration.

### R7. Add named reverse Prisma relations **exactly**

Add to existing models; do not alter any pre-existing relation names/actions:

```prisma
// public.PlatformAdmin
createdWhatsAppTemplateDefinitions WhatsAppTemplateDefinition[] @relation("WhatsAppTemplateDefinitionCreator")
reviewedWhatsAppTemplateLocales WhatsAppTemplateLocale[] @relation("WhatsAppTemplateLocaleReviewer")
requestedWhatsAppTemplateTranslationRuns WhatsAppTemplateTranslationRun[] @relation("WhatsAppTemplateTranslationRunRequester")
requestedWhatsAppTemplatePublications WhatsAppTemplatePublicationOperation[] @relation("WhatsAppTemplatePublicationRequester")
updatedWhatsAppConversationWrapperSlots WhatsAppConversationWrapperActiveSlot[] @relation("WhatsAppConversationWrapperSlotUpdater")

// commerce.CommerceTranslationModelConfiguration
whatsAppTemplateTranslationRuns WhatsAppTemplateTranslationRun[]

// commerce.Shop
whatsAppTemplatePublicationTargets WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationTargetShop")
```

The `WhatsAppTemplateVariant` reverse fields are specified in R5. All **11 new models** use `@@schema("whatsapp")`, `String @db.Text` IDs, bounded provider/status strings and `@db.Timestamptz(3)` timestamps. Explicit new FKs use `ON UPDATE RESTRICT` and the declared `onDelete` actions; existing FKs/actions remain unchanged.

### R8. Reuse `CommerceAuditEvent` and extend `CommerceAuditAction` **exactly**

Keep all six existing ARCH-047 variant audit enum values from migration `20261023173000_arch047_whatsapp_template_audit_actions` unchanged. Append **only** these ten new values:

```prisma
CREATE_WHATSAPP_TEMPLATE_DEFINITION
CLONE_WHATSAPP_TEMPLATE_DEFINITION
REQUEST_WHATSAPP_TEMPLATE_TRANSLATION
REVIEW_WHATSAPP_TEMPLATE_LOCALE
REQUEST_WHATSAPP_TEMPLATE_META_SUBMISSION
PUBLISH_WHATSAPP_TEMPLATE_DEFINITION
ASSIGN_WHATSAPP_TEMPLATE_DEFINITION
RETIRE_WHATSAPP_TEMPLATE_DEFINITION
ACTIVATE_WHATSAPP_CONVERSATION_WRAPPER
DEACTIVATE_WHATSAPP_CONVERSATION_WRAPPER
```

No new ARCH-047 audit table, no `CommerceAuditEvent` column changes and no new audit FK target are permitted. Applications write the authenticated Admin actor, operation ID, optional shop ID, reason and bounded evidence (e.g. definition/registration/operation IDs). Meta webhook receipts belong to `WhatsAppTemplateMetaEvent`, **not** an audit entry falsely attributed to an Admin.

The inherited `arch020_audit_targets` CHECK is exhaustive (`ELSE false`); merely appending enum values would make inserts fail. In this **new additive migration only**, preserve every historical branch (including the six existing ARCH-047 actions), and add recognition for the ten new values with a neutral `THEN true` branch. Do not introduce new template business predicates or weaken old branches. Validate that old actions remain exactly as before and new actions round-trip.

### R9. Exact additive migration and preservation

Use this fixed migration:

```text
prisma/migrations/20261024133000_arch047_template_persistence/migration.sql
```

Create exactly the **11 new models** in R2–R6 (2 authoring + 4 translation + 2 Meta + 2 publication + 1 wrapper pointer) with all declared column types, defaults, PKs/FKs, technical unique keys and query indexes. Add nullable `WhatsAppTemplateVariant.metaRegistrationId` FK and index. Append the ten audit enum actions and minimally extend the existing audit-target CHECK as R8 describes. **Do not introduce or seed** a release table, release-locale table, separate Meta attempt/receipt table, templates, WABAs, language rows, publication pointers or initial shop assignments.

This is an additive change. Preserve all existing `Shop`, `PlatformAdmin`, `WhatsAppTemplateVariant`, `CommerceAuditEvent`, provider and ARCH-031 translation data. Do not rewrite predecessor SQL, rebuild existing tables or add ARCH-047 business CHECKs/triggers/stored procedures. The migration must support both fresh and upgrade application, with documented ordering and enum rollback limitations.

### R10. Exact Prisma and migration contract validators

Create:

```text
scripts/validate-arch047-template-persistence-schema.mjs
scripts/validate-arch047-template-persistence-migration.mjs
```

Register **exactly** these package script names and preserve existing ARCH-047 audit validators:

```json
"test:arch047-template-persistence-schema": "node scripts/validate-arch047-template-persistence-schema.mjs",
"test:arch047-template-persistence-migration": "node scripts/validate-arch047-template-persistence-migration.mjs",
"test:arch047-template-persistence-validator-mutations": "node scripts/test-arch047-template-persistence-validator-mutations.mjs",
"test:arch047-template-persistence:postgres:fresh": "node scripts/test-arch047-template-persistence-postgres.mjs --mode fresh",
"test:arch047-template-persistence:postgres:upgrade": "node scripts/test-arch047-template-persistence-postgres.mjs --mode upgrade"
```

The schema validator must check the **exact** 11-model field types, nullability, defaults and `@db` annotations, relation names and target columns, `onDelete`/`onUpdate`, reverse fields, model/table set, indexes/uniques, new audit enum values and nullable existing-variant FK. The migration validator must verify real DDL semantics/objects (not comments or arbitrary identifier strings), absence of the removed release/Meta history tables and absence of new business CHECKs/triggers/functions/conditional uniques. They must reject incorrect-but-plausible changes for the expected contract reason.

Mutation regressions must test at least these five changes on temporary copies: `WhatsAppTemplateLocale.localeAst` JsonB → String; a required FK `onDelete: Restrict` → `Cascade`; missing TranslationModelConfiguration FK; removed registration provider identity uniqueness; and `WhatsAppTemplateVariant.metaRegistrationId` changed from nullable to required. Include at least one probe introducing an obsolete `WhatsAppTemplateRelease` table. Do not change production files merely to execute mutation probes.

### R11. Fresh/upgrade PostgreSQL validation and negative tests

Create `scripts/test-arch047-template-persistence-postgres.mjs` using repository conventions and **disposable, task-owned PostgreSQL** targets, never a developer/shared/production database.

- **Fresh:** Apply the migrations in order through this one. Verify 11 tables, columns/FKs/indexes/audit actions, no template/locale/registration seeds and successful Prisma validation/generation.
- **Upgrade:** Apply predecessor migrations; seed representative historical `Shop`, `PlatformAdmin`, `WhatsAppTemplateVariant`, `CommerceAuditEvent` and ARCH-031 records where practicable. Snapshot them, apply ARCH-047 migration, and prove all historical IDs/data remain unchanged and old variants have `metaRegistrationId = NULL`.
- **Round-trip:** Create a `META_RECOVERY` definition and English locale; persist translation run, target item, batch and membership, then a translated locale. Create a Meta registration with frozen component snapshot, a failed/uncertain submission-attempt `MetaEvent`, another attempt and a status-webhook event. Create publication operation with targets for two shops and link newly published existing-variant rows to registrations. Separately create a `MODA_CONVERSATION_WRAPPER` definition/locale, activate its definition for an audience, and read the pointer back.
- **Technical negatives:** Reject duplicate `(definitionId, languageTag)`, duplicate `(runId, targetLanguageTag)`, duplicate provider Batch custom ID/membership, duplicate `(wabaId, providerTemplateName, providerLanguageCode)`, duplicate publication `operationKey`, duplicate `(operationId, shopId)`, duplicate `eventIdentity`, and invalid FK references. Prove valid rows and nullable unmatched events succeed.
- **Business non-enforcement:** Prove PostgreSQL can store one locale only; nonstandard `kind`/`audience`; a definition marked `PUBLISHED` without 20 approved locales; a wrapper active pointer referencing a definition of another kind; and a `MetaRegistration` whose WABA differs from its definition. App validation must reject such cases later; PostgreSQL does not.
- **Audit:** All ten new actions round-trip through the existing Commerce audit model, and historical actions/branches retain their previous behaviour.
- Clean up test databases and fixtures on failure/success. Record exact commands, PostgreSQL/Prisma versions and preservation evidence.

### R12. Persistence operations supported by schema (not business services)

The Database agent must demonstrate representative **Prisma/database storage operations**, not implement Admin/Background/Messaging runtime behaviour:

1. **Create / Clone as New:** Insert a new definition and its English locale in one transaction. Cloning creates a new definition ID; application safeguards any prohibition on editing the old one.
2. **Queue translation:** Insert a run with source snapshot and 19 target items, with progress/retry statuses stored durably; app chooses targets/model and decides when work may start.
3. **Batch correlation:** Insert Batch and BatchItem records; handle uncertain provider batches, polls and retried items without losing historical memberships.
4. **Store output:** Update item/output and locale AST with the verified translation; application checks stale source hashes and prohibits overwriting published content.
5. **Meta create and reconcile:** Insert a registration with frozen request components; append submission-attempt/unknown-outcome events and subsequent webhook/reconciliation events. App checks Meta before retrying unknown creates and chooses provider status transitions.
6. **Publish to shops:** Transactionally insert an operation, target rows and new/replaced `WhatsAppTemplateVariant` references through `metaRegistrationId`, plus an authorised `CommerceAuditEvent` where applicable. Admin handles approval, WABA matching, assignment override and concurrency.
7. **Activate wrapper:** Upsert audience's `WhatsAppConversationWrapperActiveSlot` referencing a definition with app-managed `editVersion` CAS and relevant audit event. App validates published wrapper kind and chooses the fallback policy.
8. **Read runtime:** Query variants by existing shop/provider/purpose/language indexes and include nullable registration → locale → definition provenance. Resolve active wrapper by audience and include its language content; no Meta fetch or checkout write.

These operations require no new stored procedure, database service or SQL business gate. Failures/retries are represented by persisted records; all orchestration belongs to the owning application.

### R13. Database-only ownership

Do not implement Admin UI, translation workers, Meta provider calls, approval policy, publication selection, templates for unknown external Meta records, response wrapping or checkout/cart mutations in this task. Shared/Background/Admin/Messaging consumers must use the published architecture-approved contracts. A newly discovered cross-repository data requirement must return to `moda_architect` for approval before extending this exact schema.

## Work Items

- [ ] Implement R2: Definition/Locale and reverse references; English AST lives only in `WhatsAppTemplateLocale`.
- [ ] Implement R3: Translation Run/Item/Batch/BatchItem with existing ARCH-031-compatible technical correlations.
- [ ] Implement R4: MetaRegistration + unified MetaEvent ledger, technical uniqueness and nullable unmatched events.
- [ ] Implement R5: PublicationOperation/Target and nullable `WhatsAppTemplateVariant.metaRegistrationId` with reverse relations.
- [ ] Implement R6: central wrapper audience pointer referencing a definition, not a release.
- [ ] Implement R7: all explicitly named reverse Prisma relation fields.
- [ ] Implement R8: ten new audit actions and the narrowly amended historical audit-target CHECK.
- [ ] Implement R9: one additive, seed-free migration with no obsolete release/Meta history tables or business constraints.
- [ ] Implement R10: exact schema/DDL validators and deterministic mutation regressions.
- [ ] Implement R11–R12: fresh/upgrade PostgreSQL rehearsals, valid/invalid technical writes and representative persistence flows.
- [ ] Record evidence for all groups and required dedicated parent/implementation worktrees in Completion Report.

## Interfaces / Contracts

**Produced:** Prisma models/columns, technical FKs/uniqueness/indexes and migration evidence. This task does not author any new queue, HTTP or Meta wire contract. Shared/Admin/Background own validation for `kind`, `purpose`, `offerType`, `audience`, provider-status strings, language tags and AST content. Database does not select the Meta template used for sending.

**Technical identities:**

```text
Definition / new content version     : WhatsAppTemplateDefinition.id
English AST / translated AST         : WhatsAppTemplateLocale(definitionId, languageTag)
Translation item                     : (runId, targetLanguageTag)
Provider Batch identity              : (provider, providerBatchId) and providerCustomId
Provider registration                : (wabaId, providerTemplateName, providerLanguageCode)
Meta event receipt or attempt        : eventIdentity
Publication request                  : operationKey
Per-shop publication target          : (operationId, shopId)
Live runtime assignment              : existing WhatsAppTemplateVariant identity + nullable metaRegistrationId
Internal wrapper selection          : audience primary key + definitionId; editVersion for app CAS
```

Applications keep published provider payload snapshots and the immutable definition/locale references for provenance. Historical `WhatsAppTemplateVariant` rows remain valid but **unlinked**, not silently imported or treated as compliant Admin-created templates.

## Dependencies

None. The task is developer-owned and already in progress at Attempt 1. The parent ARCH-047 document and old Admin import/copy tasks still need architect reconciliation before downstream execution; the task's own claimed state is not reset by this task-definition change.

## Enables

After architect acceptance and explicit developer completion, new Shared/Admin/Background/Messaging tasks may consume the schema once their dependencies are reconciled. No old import-only Admin task may be promoted. Keep `enables: []` until those tasks are canonically defined.

## Acceptance Criteria

- [ ] Exactly **11 new `whatsapp` tables**, the specified legacy variant FK/reverse fields, ten new Commerce audit enum actions and matching technical indexes exist; no release/release-locale/third Meta history table is created.
- [ ] Definition/Locale stores English and translated ASTs once per language; Meta registration stores submitted provider components; event ledger retains attempts/webhooks; shop targets and wrapper pointers reference definitions directly.
- [ ] All Prisma reverse relations are valid, FK delete/update actions and unique identities match R2–R7, and Prisma generates its client against the applied migration.
- [ ] Existing `Shop`, `PlatformAdmin`, `CommerceAuditEvent`, `WhatsAppTemplateVariant`, audit-action semantics and ARCH-031 translations survive upgrades intact.
- [ ] Legacy variants have `metaRegistrationId = NULL` until an explicitly authorised application migration/assignment; no external template is adopted by SQL.
- [ ] Missing approvals, wrong kinds/WABAs, one-language definitions and wrong-type wrapper pointers are **not** rejected by new SQL business rules; technical FK/identity violations are rejected.
- [ ] New audit actions work without altering old `arch020_audit_targets` branches or introducing a new audit model.
- [ ] Exact validators and mutation tests, isolated fresh/upgrade PostgreSQL tests, round-trip and negative cases, and `git diff --check` pass.

## Validation

- [ ] Inspect `moda-interact-database/package.json` and run its existing, actually supported Prisma validation/generation/format commands; regenerate ERD only if part of normal schema workflow.
- [ ] `npm run test:arch047-template-persistence-schema`.
- [ ] `npm run test:arch047-template-persistence-migration`.
- [ ] `npm run test:arch047-template-persistence-validator-mutations`.
- [ ] `npm run test:arch047-template-persistence:postgres:fresh`.
- [ ] `npm run test:arch047-template-persistence:postgres:upgrade`.
- [ ] Rerun pre-existing ARCH-047 audit migration tests and verify historical migration unchanged.
- [ ] `git diff --check`; verify no `_index.md`, parent architecture or consumer repository files changed.
- [ ] Record actual validation commands/results, versions, migration name, isolated launcher parent/implementation worktrees, claim/start synchronization and branch evidence in Completion Report.

## Stop Condition

When the prescribed database schema/migration/tests and Completion Report are complete, set the task to `review` and return to the developer's authorised completion path. Do **not** mark a developer-completion task `complete`, merge, push main, begin downstream work, modify `_index.md` or change the parent architecture.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the Database repo's local instructions. Start from the launcher-resolved dedicated parent and implementation task worktrees on mirrored `task/ARCH-047-DATABASE-001` branches. The developer's worktree claim metadata is preserved here; the patch changes task **definition only**, not an implementation branch. Use existing schema conventions; do not add generic framework helpers or duplicate ARCH-031 table ownership. If the current live branch/schema differs from the snapshot, resolve the difference with architect review before implementing. No `docs/decisions/**/_index.md` update until the architecture session is explicitly complete.

## Completion Report

### Status

In Progress — developer Attempt 1 claimed at 2026-10-23T17:33:17Z; no revised implementation completion claimed by this task-definition amendment.

### Execution Ownership Amendment

On 23 October 2026, the developer invoked `/moda_developer_create ARCH-047-DATABASE-001` while the original authoring definition still used agent execution. Execution and completion remain developer-owned for this attempt; assigned repository agent stays `moda_database`.

### Scope Amendment

24 October 2026: this task now combines all four proposed database tasks into one. The latest task-definition revision specifies the simplified 11-table contract, exact Prisma fields and migrations, and keeps all template business rules in applications. It does not attest to implementation. It does not attest to implemented database source or a successful migration.

### Files Changed

None recorded for revised implementation.

### Work Completed

None recorded for revised implementation.

### Validation Results

Not yet run against the revised complete contract.

### Deviations

None recorded.

### Assumptions

Snapshot from the developer task worktree ZIP supplied 24 October 2026; current live branch may have moved. Provider language mappings, AST/schema validation, Meta payload verification and release-eligibility checks are owned by Shared/Admin/Background, not Database.

### Unresolved Issues

Parent ARCH-047 architecture and old `ADMIN-001`/`ADMIN-002` task files require separate reconciliation to the Admin-only publishing workflow; they are not altered by this amendment.

### Architectural Concerns

Checkout conversation association and read-only CommerceAgent enforcement remain separately owned; this task does not create cart/checkout mutation capabilities.

## Architect Review

### Review Status

Pending — task definition amended; no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Implementation conformance not yet assessed; parent architecture reconciliation remains required.

### Follow-up

Use this exact DB001 contract as the single database prerequisite when revising downstream ARCH-047 task definitions. Do not create `DATABASE-002`–`004` or resume external-import tasks.
