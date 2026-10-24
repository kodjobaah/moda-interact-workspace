---
id: ARCH-047-DATABASE-001
architecture_id: ARCH-047
title: Persist immutable Moda-authored templates, translation, Meta approval and publication
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

**Single consolidated Database implementation.** This task contains all previously proposed `ARCH-047-DATABASE-001` through `DATABASE-004` database work; do **not** create separate `DATABASE-002`–`004`. It replaces the former audit-only scope and preserves the existing developer-owned Attempt 1 claim. The parent architecture still describes the superseded external-import workflow and requires separate architect reconciliation; do not interpret this task as authorisation to alter other domains.

## Objective

Implement the **exact** Prisma/PostgreSQL persistence contract below in one additive ARCH-047 migration: Moda-authored recovery templates and conversation wrappers; English AST and per-language content; translation runs, items and Batch evidence; Meta submissions, attempts and status receipts; immutable release *records*; resumable merchant publication; active conversation-wrapper pointers; and existing Commerce audit actions.

The task intentionally consolidates all ARCH-047 database work so downstream services consume one coherent schema. **No template business logic is enforced by new PostgreSQL constraints, triggers or functions.** All rules about who may author, what may be edited, supported purposes/variables/languages, which provider statuses qualify, 20/20 completeness, approval, activation, and allowed shop/WABA association belong to application services.

## Context

The inspected October 24 task worktree has:

- `whatsapp.WhatsAppTemplateVariant` with shop/provider/purpose/language/status/enabled data, but no Moda-authored release provenance.
- `commerce.CommerceAuditEvent` and `CommerceAuditAction`. The existing ARCH-047 audit-only migration `20261023173000_arch047_whatsapp_template_audit_actions` already added six legacy variant actions; **do not edit or replay that historical migration**.
- ARCH-031 translation modelling in `CommerceStoreCategoryTranslationRun`, `CommerceStoreCategoryTranslationItem`, `CommerceStoreCategoryTranslationBatch`, and `CommerceStoreCategoryTranslationBatchItem`, including `CommerceTranslationModelConfiguration` ownership.
- A pre-existing exhaustive `commerce.CommerceAuditEvent` CHECK named `arch020_audit_targets`. Any new audit-action enum values must be permitted by that legacy CHECK; preserve every existing branch without adding new template-specific actor/shop/business gates.

The proposed flow is **Admin create English AST → persist new definition → queue Background translation → persist 19 target languages → Admin review → submit each language to Meta → reconcile webhook/provider status → create approved release in the application → assign release to shops**. Internal AI/human response wrappers use the same authoring/translation data, but internal application approval and a separate active audience pointer. No externally created Meta templates enter Moda's catalogue; a content change creates a new definition/Meta name rather than editing an existing template. The AI's commerce operations remain read-only.

## Scope

Modify **only** `moda-interact-database/` for the schema, additive migration, focused validators and database-level proofs. Required primary paths, relative to that repository:

```text
prisma/schema.prisma
prisma/migrations/20261024133000_arch047_template_persistence/migration.sql
scripts/validate-arch047-template-persistence-schema.mjs
scripts/validate-arch047-template-persistence-migration.mjs
scripts/test-arch047-template-persistence-postgres.mjs
scripts/test-arch047-template-persistence-validator-mutations.mjs
package.json
```

The migration path above is fixed for this task, after the existing 2026-10-23 ARCH-047 audit migration. Required related Prisma reverse fields are enumerated below. Additional **test-only** helpers/fixtures are permitted, but no additional domain models, functions, triggers or historical migration edits. Reuse repository scripts and disposable PostgreSQL conventions. Regenerate `docs/generated/prisma-erd.puml` and `docs/generated/erd.png` only if the repository's normal schema regeneration workflow requires them and record this explicitly.

## Out of Scope

- Admin authoring UI, Clone as New, AST validation, template editing controls, role checks, translation review and release approval.
- Background translation, LLM/Batch calls, Meta Graph API create/reconcile, queue workers, runtime parameter binding, offer evaluation, provider webhooks and credit/final-send rules.
- Shared runtime schemas, WhatsApp variable registry, supported language/Meta-code mapping and Meta event normalisation.
- External template import/adoption, Meta edit-existing-template API and merchant-authored templates.
- Checkout or cart mutations, modifications to `Conversation`, or new generic audit storage.
- **Any new DB business enforcement**, including content immutability triggers; type/purpose/audience/WABA compatibility CHECKs; supported-locale or 20/20 approval gates; Meta submission/approval predicates; template activation/override rules; conditional unique indexes based on `APPROVED` or `enabled`; privileged-role enforcement; or any SQL procedure that decides release eligibility.
- Modifying `docs/decisions/**/_index.md` or implementing consumer repositories.

## Requirements

### R1. Database/application ownership boundary — exact

Prisma and PostgreSQL own **data shape and technical relational integrity only**: primary keys, foreign keys, record-identity uniqueness, nullable history references and ordinary query indexes. Values stored as `kind`, `purpose`, `offerType`, `audience`, workflow `status`, provider category and language tags remain **strings**, not closed Prisma enums or DB CHECK rules. Do not infer a workflow decision from a stored value inside SQL. No new trigger, SQL function or CHECK is to validate ARCH-047 business rules.

Applications must validate and transactionally enforce, in their owning tasks: Admin-only authorship; new identity/version for any content change; 20-language generation and review; Meta-approved language/status; WABA/shop/definition-kind compatibility; no provider edit-existing call; controlled merchant assignment, replacement and rollback; wrapper audience suitability; and read-only AI tools. This database task merely persists the values and evidence. The existing `WhatsAppTemplateStatus` enum used by historical `WhatsAppTemplateVariant` remains untouched.

### R2. Add `WhatsAppTemplateDefinition` and `WhatsAppTemplateLocale` **exactly**

Add these models to `prisma/schema.prisma`:

```prisma
model WhatsAppTemplateDefinition {
  id                     String   @id @default(cuid()) @db.Text
  kind                   String   @db.VarChar(40)
  purpose                String?  @db.VarChar(96)
  offerType              String?  @db.VarChar(32)
  audience               String?  @db.VarChar(24)
  wabaId                 String?  @db.VarChar(191)
  providerTemplateName   String?  @db.VarChar(255)
  category               String?  @db.VarChar(32)
  sourceLanguageTag      String   @db.VarChar(16)
  astSchemaVersion       Int
  englishAst             Json     @db.JsonB
  sourceHash             String   @db.VarChar(64)
  createdByAdminId       String   @db.Text
  clonedFromDefinitionId String?  @db.Text
  createdAt              DateTime @default(now()) @db.Timestamptz(3)

  createdByAdmin PlatformAdmin @relation("WhatsAppTemplateDefinitionCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  clonedFrom     WhatsAppTemplateDefinition? @relation("WhatsAppTemplateDefinitionClone", fields: [clonedFromDefinitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  clones         WhatsAppTemplateDefinition[] @relation("WhatsAppTemplateDefinitionClone")
  locales        WhatsAppTemplateLocale[]
  translationRuns WhatsAppTemplateTranslationRun[]
  releases       WhatsAppTemplateRelease[]

  @@index([kind, purpose, createdAt])
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

  definition      WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  reviewedByAdmin PlatformAdmin? @relation("WhatsAppTemplateLocaleReviewer", fields: [reviewedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  metaSubmissions WhatsAppTemplateMetaSubmission[]
  translationResults WhatsAppTemplateTranslationItem[] @relation("WhatsAppTemplateTranslationResultLocale")
  releaseLocales  WhatsAppTemplateReleaseLocale[]

  @@unique([definitionId, languageTag])
  @@index([status, updatedAt])
  @@index([reviewedByAdminId, reviewedAt])
  @@schema("whatsapp")
}
```

These tables deliberately store the English source **and** the English locale entry. The app establishes which locale represents the English master; PostgreSQL does not require the presence/count/content of any particular language. JSONB payload semantics, source hashes, provider name conventions and the rule not to edit saved ASTs are application responsibilities. `clonedFromDefinitionId` is provenance only and does not change the source row.

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

### R4. Add Meta submission, attempt and webhook receipt tables **exactly**

```prisma
model WhatsAppTemplateMetaSubmission {
  id                     String    @id @default(cuid()) @db.Text
  localeId               String    @db.Text
  wabaId                 String    @db.VarChar(191)
  providerTemplateName   String    @db.VarChar(255)
  providerLanguageCode   String    @db.VarChar(16)
  category               String    @db.VarChar(32)
  componentsSnapshot     Json      @db.JsonB
  submittedContentHash   String    @db.VarChar(64)
  providerTemplateId     String?   @db.VarChar(191)
  submissionState        String    @db.VarChar(32)
  providerStatus         String?   @db.VarChar(32)
  failureCode            String?   @db.VarChar(128)
  submittedAt            DateTime? @db.Timestamptz(3)
  nextRetryAt            DateTime? @db.Timestamptz(3)
  lastReconciledAt       DateTime? @db.Timestamptz(3)
  createdAt              DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt              DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  locale   WhatsAppTemplateLocale @relation(fields: [localeId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  attempts WhatsAppTemplateMetaSubmissionAttempt[]
  receipts WhatsAppTemplateMetaStatusReceipt[]

  @@unique([wabaId, providerTemplateName, providerLanguageCode])
  @@unique([wabaId, providerTemplateId])
  @@index([localeId, createdAt])
  @@index([submissionState, nextRetryAt, createdAt])
  @@index([providerStatus, updatedAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateMetaSubmissionAttempt {
  id                String    @id @default(cuid()) @db.Text
  submissionId      String    @db.Text
  attemptNumber     Int
  outcome           String    @db.VarChar(32)
  requestDigest     String    @db.VarChar(64)
  providerRequestId String?   @db.VarChar(191)
  httpStatus        Int?
  failureCode       String?   @db.VarChar(128)
  evidence          Json?     @db.JsonB
  startedAt         DateTime  @default(now()) @db.Timestamptz(3)
  finishedAt        DateTime? @db.Timestamptz(3)

  submission WhatsAppTemplateMetaSubmission @relation(fields: [submissionId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@unique([submissionId, attemptNumber])
  @@index([submissionId, startedAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateMetaStatusReceipt {
  id                   String    @id @default(cuid()) @db.Text
  eventIdentity        String    @unique @db.VarChar(191)
  submissionId         String?   @db.Text
  wabaId               String    @db.VarChar(191)
  providerTemplateId   String?   @db.VarChar(191)
  providerTemplateName String?   @db.VarChar(255)
  providerLanguageCode String?   @db.VarChar(16)
  eventType            String    @db.VarChar(64)
  providerStatus       String?   @db.VarChar(32)
  reasonCode           String?   @db.VarChar(128)
  reconciliationInfo   Json?     @db.JsonB
  receivedAt           DateTime  @default(now()) @db.Timestamptz(3)
  processedAt          DateTime? @db.Timestamptz(3)

  submission WhatsAppTemplateMetaSubmission? @relation(fields: [submissionId], references: [id], onDelete: SetNull, onUpdate: Restrict)

  @@index([submissionId, receivedAt])
  @@index([wabaId, providerTemplateName, providerLanguageCode, receivedAt])
  @@index([processedAt, receivedAt])
  @@schema("whatsapp")
}
```

A nullable `submissionId` permits persistence of unmatched status events **without adopting** any externally created template. Application reconciliation decides association and status application. Submission `componentsSnapshot` is the request sent to Meta; it does not authorise modifying the source AST. `providerTemplateId` may be unknown after a network timeout. All provider evidence must be bounded and redacted **before** storage by Messaging/Background; never persist access tokens, unbounded webhook bodies or customer details. No SQL constraint validates kind, approval, WABA consistency with the definition or retries. Multiple submission records may reference one locale; the application prohibits content-edit/resubmit-in-place semantics and selects the authoritative attempt. Database uniqueness covers Meta provider identity, not the approved submission workflow.

### R5. Add releases and constituent-language membership **exactly**

```prisma
model WhatsAppTemplateRelease {
  id               String    @id @default(cuid()) @db.Text
  definitionId     String    @db.Text
  sourceHash       String    @db.VarChar(64)
  releaseDigest    String    @db.VarChar(64)
  status           String    @db.VarChar(32)
  createdByAdminId String    @db.Text
  releasedAt       DateTime? @db.Timestamptz(3)
  retiredAt        DateTime? @db.Timestamptz(3)
  createdAt        DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  definition   WhatsAppTemplateDefinition @relation(fields: [definitionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdByAdmin PlatformAdmin @relation("WhatsAppTemplateReleaseCreator", fields: [createdByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  locales       WhatsAppTemplateReleaseLocale[]
  publications WhatsAppTemplatePublicationOperation[]
  activeWrappers WhatsAppConversationWrapperActiveSlot[]

  @@index([status, releasedAt])
  @@index([definitionId, createdAt])
  @@index([createdByAdminId, createdAt])
  @@schema("whatsapp")
}

model WhatsAppTemplateReleaseLocale {
  id            String   @id @default(cuid()) @db.Text
  releaseId     String   @db.Text
  localeId      String   @db.Text
  contentDigest String   @db.VarChar(64)
  createdAt     DateTime @default(now()) @db.Timestamptz(3)

  release WhatsAppTemplateRelease @relation(fields: [releaseId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  locale  WhatsAppTemplateLocale @relation(fields: [localeId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  variants WhatsAppTemplateVariant[] @relation("WhatsAppTemplateVariantReleaseLocale")

  @@unique([releaseId, localeId])
  @@index([localeId])
  @@schema("whatsapp")
}
```

A saved definition is intended to lead to one approved release, with content changes producing a **new definition**, but **PostgreSQL does not enforce release counts**; application transactions enforce that lifecycle. Membership and digest fields are stored provenance, **not** database proof that 20 languages are present, reviewed or Meta-approved. Internal wrappers reuse the same release and member tables; they do not produce Meta submissions.

### R6. Add resumable per-shop publication and link existing variants **exactly**

```prisma
model WhatsAppTemplatePublicationOperation {
  id                 String    @id @default(cuid()) @db.Text
  releaseId          String    @db.Text
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

  release     WhatsAppTemplateRelease @relation(fields: [releaseId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  requestedBy PlatformAdmin @relation("WhatsAppTemplatePublicationRequester", fields: [requestedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  targets     WhatsAppTemplatePublicationTarget[]

  @@index([releaseId, status, createdAt])
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

Add **only** these fields to the **existing** `WhatsAppTemplateVariant`, keeping every existing key/index, shop/provider field and historical row unchanged:

```prisma
// New fields in WhatsAppTemplateVariant
releaseLocaleId String? @db.Text
releaseLocale   WhatsAppTemplateReleaseLocale? @relation("WhatsAppTemplateVariantReleaseLocale", fields: [releaseLocaleId], references: [id], onDelete: Restrict, onUpdate: Restrict)
publicationPreviousTargets WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationPreviousVariant")
publicationNewTargets      WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationNewVariant")

// Additional index within WhatsAppTemplateVariant
@@index([releaseLocaleId])
```

`releaseLocaleId` **must** be nullable with no default on existing rows. A legacy/external variant is not automatically adopted as Moda-authored. No DB uniqueness over approved/enabled *business* slots is introduced. Application code validates the selected release locale's kind, purpose, WABA, shop eligibility, provider approval, override confirmation and replacement transaction.

### R7. Add platform-level conversation wrapper pointer **exactly**

```prisma
model WhatsAppConversationWrapperActiveSlot {
  audience         String   @id @db.VarChar(24)
  releaseId        String   @db.Text
  editVersion      Int      @default(0)
  updatedByAdminId String   @db.Text
  updatedAt        DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  release   WhatsAppTemplateRelease @relation(fields: [releaseId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin @relation("WhatsAppConversationWrapperSlotUpdater", fields: [updatedByAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@index([releaseId])
  @@schema("whatsapp")
}
```

This is a global current pointer for `SHARED`, `AI` or `HUMAN`, **as interpreted by Admin/Background**. `audience` is a string, not a database enum or CHECK, and a FK does not assert that the release actually contains a conversation wrapper. The application handles CAS (`editVersion`), internal approval, supersession and choosing whether a shared or source-specific wrapper applies. Wrapper content remains in the common Definition/Locale/Release tables; no second wrapper-template table is created.

### R8. Add named reverse Prisma relations **exactly**

Add these fields to the existing models; retain all previous fields and relation names:

```prisma
// public.PlatformAdmin
createdWhatsAppTemplateDefinitions WhatsAppTemplateDefinition[] @relation("WhatsAppTemplateDefinitionCreator")
reviewedWhatsAppTemplateLocales   WhatsAppTemplateLocale[] @relation("WhatsAppTemplateLocaleReviewer")
requestedWhatsAppTemplateTranslationRuns WhatsAppTemplateTranslationRun[] @relation("WhatsAppTemplateTranslationRunRequester")
createdWhatsAppTemplateReleases   WhatsAppTemplateRelease[] @relation("WhatsAppTemplateReleaseCreator")
requestedWhatsAppTemplatePublications WhatsAppTemplatePublicationOperation[] @relation("WhatsAppTemplatePublicationRequester")
updatedWhatsAppConversationWrapperSlots WhatsAppConversationWrapperActiveSlot[] @relation("WhatsAppConversationWrapperSlotUpdater")

// commerce.CommerceTranslationModelConfiguration
whatsAppTemplateTranslationRuns WhatsAppTemplateTranslationRun[]

// commerce.Shop
whatsAppTemplatePublicationTargets WhatsAppTemplatePublicationTarget[] @relation("WhatsAppTemplatePublicationTargetShop")
```

`WhatsAppTemplateVariant` reverse relations are defined in R6. All new models use `@@schema("whatsapp")` and follow existing `String @db.Text` IDs, `@db.VarChar` bounded metadata and `@db.Timestamptz(3)` timestamp conventions. All new explicit FKs use `ON UPDATE RESTRICT`; `ON DELETE` follows each field's Prisma declaration. Do not change any old FK or delete action.

### R9. Reuse `CommerceAuditEvent` and extend `CommerceAuditAction` **exactly**

Keep the existing six enum values from migration `20261023173000_arch047_whatsapp_template_audit_actions` **unchanged**. Append only these ten additional enum values to the **existing** `commerce.CommerceAuditAction`:

```prisma
CREATE_WHATSAPP_TEMPLATE_DEFINITION
CLONE_WHATSAPP_TEMPLATE_DEFINITION
REQUEST_WHATSAPP_TEMPLATE_TRANSLATION
REVIEW_WHATSAPP_TEMPLATE_LOCALE
REQUEST_WHATSAPP_TEMPLATE_META_SUBMISSION
PUBLISH_WHATSAPP_TEMPLATE_RELEASE
ASSIGN_WHATSAPP_TEMPLATE_RELEASE
RETIRE_WHATSAPP_TEMPLATE_RELEASE
ACTIVATE_WHATSAPP_CONVERSATION_WRAPPER
DEACTIVATE_WHATSAPP_CONVERSATION_WRAPPER
```

Do **not** create an ARCH-047 audit model, change `CommerceAuditEvent` columns, or add new FK targets to it. The application writes the real Admin actor, operation ID, optional shop, reason and bounded metadata including template/release IDs. Provider status webhooks are recorded in `WhatsAppTemplateMetaStatusReceipt`, not falsely attributed to a human admin.

**Required compatibility with the existing legacy CHECK:** `arch020_audit_targets` currently has `ELSE false` and will reject every new action even though the enum accepts it. In this *new* additive migration, preserve all existing branches, including those for the six old ARCH-047 variant actions, and extend the exhaustive action recognition for the ten new enum values with a **neutral `THEN true` branch**, imposing **no new action-specific business predicates**. Do not remove or weaken the historical branches; do not add new `actorType`, `shopId`, Meta approval or template state tests for these new actions. This adjustment merely prevents an inherited policy CHECK from rejecting new stored action labels. Any wider removal of legacy application-policy CHECKs is outside this task.

### R10. Exact additive migration and preservation

Implement the fixed migration:

```text
prisma/migrations/20261024133000_arch047_template_persistence/migration.sql
```

It must create the **14 new tables** in R2–R7, all fields and the specified PK/FK/unique/index declarations, add the nullable `WhatsAppTemplateVariant.releaseLocaleId` FK/index, add the ten audit-action enum values, and adjust only the existing exhaustive audit-target CHECK as narrowly described in R9. PostgreSQL column types, nullability, defaults and FK actions must match the displayed Prisma declarations exactly. Use no seed data: **no sample templates, no 20-locale rows, no approvals, no WABA, no default active wrapper or shop assignments are inserted**. Preserve all existing `Shop`, `PlatformAdmin`, `WhatsAppTemplateVariant`, `CommerceAuditEvent`, provider and ARCH-031 translation data/IDs. Don't edit historical migrations or rebuild existing tables.

The migration must work for both fresh environments and upgrades from the immediately preceding schema; record its deployment ordering and irreversible aspects of adding enum values. Cross-service application rollout/reconciliation remains an architect concern. No arbitrary new trigger, CHECK, stored procedure, implicit Meta request or release gate.

### R11. Exact static Prisma and migration validators

Create:

```text
scripts/validate-arch047-template-persistence-schema.mjs
scripts/validate-arch047-template-persistence-migration.mjs
```

Register exactly these package script names (retain existing ARCH-047 audit validators):

```json
"test:arch047-template-persistence-schema": "node scripts/validate-arch047-template-persistence-schema.mjs",
"test:arch047-template-persistence-migration": "node scripts/validate-arch047-template-persistence-migration.mjs",
"test:arch047-template-persistence-validator-mutations": "node scripts/test-arch047-template-persistence-validator-mutations.mjs",
"test:arch047-template-persistence:postgres:fresh": "node scripts/test-arch047-template-persistence-postgres.mjs --mode fresh",
"test:arch047-template-persistence:postgres:upgrade": "node scripts/test-arch047-template-persistence-postgres.mjs --mode upgrade"
```

Both validators must check the **exact** approved contract, not just name presence: model/table set, enum additions, every field type/nullability/`@db` annotation/default, relation names and FK target/delete/update actions, all reverse fields, unique/index columns, nullable legacy FK, correct new audit enum values, and preserved old data/model structure. The migration validator checks real SQL objects/DDL semantics and proves no added ARCH-047 business trigger/CHECK/function, partial state-dependent unique index, or unsupported seed/legacy-migration rewrite.

Mutation regression tests must change at least five realistic specifications in temporary copies—e.g. `englishAst` JsonB → String, locale FK `RESTRICT` → `CASCADE`, translation model FK omitted, unique provider-language identity removed, `releaseLocaleId` made required—and verify the relevant validator fails for the specific contract reason. Do not let validators merely search for names in comments.

### R12. Focused fresh/upgrade PostgreSQL proof and negative cases

Create `scripts/test-arch047-template-persistence-postgres.mjs` using the repository's isolated/disposable PostgreSQL test approach (not the developer's or production database):

- **Fresh:** Apply migrations in order through the new fixed migration. Verify all new tables/fields/FKs/indexes/audit actions, no seeded templates, and Prisma validates/generates against the applied schema.
- **Upgrade:** Apply all predecessor migrations, create representative historical `Shop`, `PlatformAdmin`, `WhatsAppTemplateVariant`, audit event and ARCH-031 records where practical; snapshot those rows; apply the new migration; assert all historical rows are byte/logically unchanged and the legacy assignment's new `releaseLocaleId` is NULL.
- **Round-trip:** Insert one `META_RECOVERY` definition and locale, one translation run/item/batch/batch membership with an optional result locale, a Meta submission plus uncertain/retried attempts and provider receipts, an approved *recorded* release with locale membership, a two-shop publication operation/targets, nullable linkage from new variants, and a separate `MODA_CONVERSATION_WRAPPER` definition/release/active audience pointer. Verify relationships, timestamps and JSONB payloads round-trip.
- **Technical negatives:** Duplicate `(definitionId, languageTag)`; duplicate `(runId, targetLanguageTag)`; duplicate batch membership/custom ID; duplicate `(wabaId, providerTemplateName, providerLanguageCode)`; duplicate `(releaseId, localeId)`; duplicate `(operationId, shopId)`; duplicate webhook event identity; and broken FK each fail for the intended unique/FK reason. Prove matching valid inserts succeed.
- **Business-rule non-enforcement:** Prove the database permits, as pure persisted data, an incomplete locale set, a nonstandard `kind`/`audience`, a release referencing a template with zero approved locales, and a wrapper slot pointing to a release whose definition has another `kind`. Applications must reject those conditions; **PostgreSQL must not**. This proof is deliberate and must not be mistaken for recommended service behaviour.
- **Audit:** Verify all ten new actions insert/query with bounded Admin-provided metadata while old actions and their existing CHECK behaviour remain intact.
- Clean up every test fixture/disposable database even on failure; record PostgreSQL/Prisma versions and exact commands/results.

### R13. Exact persistence operations to be supported by the schema

The Database agent must prove that Prisma transactions can perform the following **storage operations** with the defined models and keys. The app layer owns all permissions/eligibility decisions; this is **not** a request to implement a new Database service, stored procedure or trigger:

1. **Create / Clone as New:** insert `WhatsAppTemplateDefinition`, link `clonedFromDefinitionId` if applicable, and insert an English `WhatsAppTemplateLocale` in one application transaction. A later content revision uses a **new** definition ID; the database does not reject direct content updates by trigger.
2. **Request translation:** insert `WhatsAppTemplateTranslationRun` with frozen source snapshot and model reference; create target `WhatsAppTemplateTranslationItem` rows. Persist queued/processing/failure states and retry timestamps; app decides targets and retries.
3. **Record Batch delivery:** insert/reconcile a `WhatsAppTemplateTranslationBatch` and its membership rows, handling unknown provider submission and delayed results without losing technical correlation; `currentBatchId` may be updated by the application.
4. **Store translation output:** update an item with translated AST/content hash and optionally link the resulting locale. The application verifies source revision, locale code and protected published content.
5. **Submit to Meta:** insert a `WhatsAppTemplateMetaSubmission` with frozen component JSONB; insert numbered attempts and outcome evidence, including submission-unknown states; application reconciles provider identity before replaying any API request.
6. **Receive Meta status:** insert `WhatsAppTemplateMetaStatusReceipt` by deterministic event identity, optionally attach to a known submission and update the current provider status. An unmatched receipt is retained without creating an externally authored definition.
7. **Record release:** insert `WhatsAppTemplateRelease` plus `WhatsAppTemplateReleaseLocale` membership in a transaction. App validates language count, review, Meta approval, template kind and digests before doing so.
8. **Publish to merchant shops:** insert one `WhatsAppTemplatePublicationOperation`, its targeted shop rows, and conditionally insert/update shop-scoped `WhatsAppTemplateVariant.releaseLocaleId`. Record successful/failed targets and `CommerceAuditEvent` transactionally where practical; Admin app handles slot selection, WABA, override confirmation and concurrency.
9. **Activate wrapper:** insert/upsert `WhatsAppConversationWrapperActiveSlot` with application-managed `editVersion` CAS and write the corresponding `CommerceAuditEvent`. App verifies the release is an internally approved wrapper and chooses shared/AI/human fallback.
10. **Read for runtime:** resolve `WhatsAppTemplateVariant` by existing shop/provider/purpose/language indexes, include its optional release-locale/definition provenance, and resolve the relevant active wrapper pointer. Reads do not call Meta and do not perform writes to the checkout.

Test evidence should cover at least the representative create/translate/submit/release/publish/pointer round trips in R12. Persistence keys must allow idempotent retries and partial progress without putting the business-policy predicates in SQL.

### R14. No application implementation in this task

These models are a schema contract for subsequent Admin/Background/Messaging/Shared tasks. Do not insert Admin permissions, translation scheduling, provider network I/O, approval calculations, shop assignment policy, wrapper selection or checkout mutation in SQL or Database repository runtime. If another repository's business requirements need a schema change, return it for architect approval before broadening this exact contract.

## Work Items

- [ ] Add the exact Definition/Locale models and reverse relations (R2).
- [ ] Add the exact translation run/item/batch/batch-item models with ARCH-031-compatible foreign keys/correlation fields (R3).
- [ ] Add Meta submission/attempt/receipt models and their technical identity indexes (R4).
- [ ] Add Release/ReleaseLocale plus publication operation/target records, the nullable existing-variant FK, and wrapper active slot (R5–R7).
- [ ] Add all existing-model reverse relations (R8).
- [ ] Extend `CommerceAuditAction` without changing old action semantics; narrowly accommodate new labels in the inherited exhaustive audit CHECK (R9).
- [ ] Deliver one exact additive migration with no seed/trigger/business checks and preserve predecessor rows (R10).
- [ ] Implement exact Prisma/DDL validators and wrong-but-plausible mutation regressions (R11).
- [ ] Execute fresh and upgrade PostgreSQL rehearsals, technical/boundary SQL cases (R12), and representative persistence operation sequences (R13).
- [ ] Record changed paths, test outputs, migrations and dedicated-worktree execution evidence in the Completion Report.

## Interfaces / Contracts

**Produced by this task:** Prisma models, their exact SQL columns, FK targets, PKs, identity indexes and ordinary access indexes. The inter-repository contract is generated Prisma schema only; no new queue event or Meta API contract is authored here. The application treats `kind`, `purpose`, `offerType`, `audience`, workflow statuses, AST JSONB and locale codes as externally defined domain values validated via the owning Shared/Admin/Background services.

**Identity and lookup:**

```text
Definition: id; optional clone source: clonedFromDefinitionId
Locale: unique(definitionId, languageTag)
Translation item: unique(runId, targetLanguageTag)
Batch correlation: unique(provider, providerBatchId); unique(providerCustomId)
Meta submission: primary key id, indexed localeId; unique(wabaId, providerTemplateName, providerLanguageCode)
Provider receipt: unique(eventIdentity)
Release: primary key id, indexed definitionId; membership unique(releaseId, localeId)
Shop publication: unique(operationKey); unique(operationId, shopId)
Runtime assignment: existing unique(shop, WABA, purpose, Meta name, Meta language); optional releaseLocaleId FK
Wrapper pointer: audience primary key; editVersion for application CAS
```

**Cross-schema references:** `public.PlatformAdmin`, `commerce.Shop`, `commerce.CommerceTranslationModelConfiguration` are reused via Prisma relation fields; existing `commerce.CommerceAuditEvent` remains the audit sink. Consumer tasks must depend on this **one** `ARCH-047-DATABASE-001` after it is accepted and developer-completed. `DATABASE-002`–`004` are not tasks.

## Dependencies

None. The current canonical task worktree snapshot has `execution_mode: developer`, `completion_mode: developer`, `status: in_progress`, `executor: developer`, `attempt: 1`; this documentation amendment preserves that claim. Before completing implementation and promoting consumers, moda_architect must reconcile the old parent architecture and supersede the external-import/copy `ADMIN-001`/`ADMIN-002` paths. Do not claim a new implementation attempt solely because this task's scope was clarified.

## Enables

After this task is implemented, reviewed and explicitly developer-completed, architect may mark the separately defined Shared/Admin/Background/Messaging consumers Ready as dependencies permit. No consumers are started within DB001; the existing `enables: []` remains unchanged until architect materialises the new task graph.

## Acceptance Criteria

- [ ] All 14 required new tables, one nullable extension to `WhatsAppTemplateVariant`, all Prisma reverse fields, ten new `CommerceAuditAction` labels and exact indexes exist as R2–R10 specify.
- [ ] Existing historical audit actions, six earlier ARCH-047 variant actions, `CommerceAuditEvent`, Shop/template rows and ARCH-031 data remain unchanged after upgrade.
- [ ] Every new table passes Prisma schema validation/client generation and matches actual SQL column types, FKs and identity/index contracts.
- [ ] No new ARCH-047 database business rules, trigger/function, type/audience CHECK, locale-count or Meta approval gate exist. The R12 business-rule **permissive** cases round-trip as pure data.
- [ ] Interrupted translation batches, uncertain/retried Meta calls and unmatched status receipts are durably representable/queryable.
- [ ] New audit actions round-trip through `CommerceAuditEvent` with platform actor metadata without changing the old audit-target CHECK's historical branches.
- [ ] Focused validators, mutation regressions, fresh + upgrade PostgreSQL rehearsals, technical uniqueness/FK negative writes and `git diff --check` pass.

## Validation

- [ ] Read the current `moda-interact-database/package.json` and run the supported `npm run format`, `npm run validate`, `npm run prisma:generate` as appropriate. Regenerate ERD only if applicable to changed schema.
- [ ] `npm run test:arch047-template-persistence-schema`.
- [ ] `npm run test:arch047-template-persistence-migration`.
- [ ] `npm run test:arch047-template-persistence-validator-mutations`.
- [ ] `npm run test:arch047-template-persistence:postgres:fresh` and `npm run test:arch047-template-persistence:postgres:upgrade` using task-specific disposable databases.
- [ ] Existing ARCH-047 audit validation and PostgreSQL proof still pass (the old migration is unchanged).
- [ ] `git diff --check`, check no docs `_index.md`, no unrelated migrations and no implementation from consumer repositories.
- [ ] Completion Report records every command/result, fresh/upgrade fixtures and preservation evidence, new migration filename, Prisma/PG versions, canonical launcher parent/implementation worktrees, synchronization, claim and mirrored branch commits.

## Stop Condition

After the specified schema/migration/tests and Completion Report are complete, set this task to `review`, return the developer-owned implementation for architect inspection and **STOP**. Do not auto-complete a `completion_mode: developer` task, edit domain `_index.md`, change parent architecture or begin Shared/Admin/Background/Messaging work.

## Implementation Notes

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the database repository's local validation conventions. The uploaded snapshot's developer claim is authoritative; the architect does not reset it. Do not manufacture an implementation commit to match this specification. If the parent architecture conflicts with this revised Admin-only workflow, return the reconciliation to moda_architect rather than silently adding DB business enforcement or changing another repository.

## Completion Report

### Status

In Progress — developer Attempt 1 claimed at 2026-10-23T17:33:17Z; no revised implementation completion claimed by this task-definition amendment.

### Execution Ownership Amendment

On 23 October 2026, the developer invoked `/moda_developer_create ARCH-047-DATABASE-001` while the original authoring definition still used agent execution. Execution and completion remain developer-owned for this attempt; assigned repository agent stays `moda_database`.

### Scope Amendment

24 October 2026: this task now combines all four proposed database tasks into one. This subsequent task-definition revision fixes exact Prisma fields, relations, migration actions and validation expectations to the style of the supplied ARCH-023 DATABASE-001 example and delegates all template business rules to applications. It does not attest to implemented database source or a successful migration.

### Files Changed

None recorded for revised implementation.

### Work Completed

None recorded for revised implementation.

### Validation Results

Not yet run against the revised complete contract.

### Deviations

None recorded.

### Assumptions

Snapshot from the developer task worktree ZIP supplied 24 October 2026; current live branch may have moved. Provider language mappings, AST/schema validation and Meta payload verification are owned by Shared/Admin/Background, not Database.

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
