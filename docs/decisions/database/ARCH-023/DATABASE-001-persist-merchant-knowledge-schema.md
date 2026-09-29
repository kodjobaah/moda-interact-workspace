---
id: ARCH-023-DATABASE-001
architecture_id: ARCH-023
title: Persist Merchant Knowledge and Store Profile schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: 2026-09-29
updated: 2026-09-29
---

# Persist Merchant Knowledge and Store Profile schema

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator:

`moda_architect`

## Objective

Implement the complete ARCH-023 PostgreSQL/Prisma persistence boundary in one additive migration: generic plan-feature configuration, Store Category/Profile persistence, Merchant Knowledge Purpose/Data Format catalogue and compatibility data, private-upload metadata, revision/chunk/pgvector persistence, and the exact database-enforceable keys, foreign keys, indexes and checks defined below.

## Context

ARCH-023 introduces one coherent durable data boundary consumed later by Admin, Shopify, Background and Commerce. Splitting the database work would force later repository tasks to depend on partially materialised schema and would duplicate migration rehearsal. This task therefore owns the whole ARCH-023 database shape.

The target remains intentionally generic:

```text
billing plan-feature configuration
        |
        +--> Store Category / Shop Profile prompt lifecycle
        |
        +--> Merchant Knowledge Purpose/Data Format catalogue
        |
        +--> Merchant Knowledge sources
                 |
                 +--> immutable uploaded-asset metadata
                 |
                 +--> source revisions
                          |
                          +--> normalized content
                          +--> semantic chunks + pgvector
```

Important boundaries:

1. `merchant_knowledge` remains an ordinary `Feature`; this database task MUST NOT make that Feature structurally required.
2. This task seeds only the architecture-owned Merchant Knowledge Purpose/Data Format catalogue and supported pair rows. It MUST NOT seed the `merchant_knowledge` Feature, `MerchantPricingPlanFeature`, `BillingPlanFeature`, Commerce capability, Commerce Tool or release data.
3. `MerchantPricingPlanFeature.configuration` is mutable Moda catalogue configuration.
4. `BillingPlanFeature.configuration` is materialised runtime configuration.
5. PostgreSQL is authoritative for Merchant Knowledge metadata/lifecycle/normalized content/embeddings. R2 object bytes are external and are represented only by `MerchantKnowledgeUploadedAsset` metadata.
6. Cross-table business rules that the target schema cannot express without database procedures are explicitly identified below as application/runtime validation. The database agent MUST NOT invent additional triggers or tables for those rules.

## Scope

Modify only `moda-interact-database` files required for the exact schema, migration, seed data and focused database validation.

Required primary files:

```text
prisma/schema.prisma
prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql
scripts/validate-arch023-merchant-knowledge-schema.mjs
scripts/validate-arch023-merchant-knowledge-migration.mjs
package.json
```

The migration directory name above is fixed for this task.

Existing validation helpers may be reused. Do not modify unrelated domain schema or historical migrations.

## Out of Scope

- Creating or seeding the `Feature` row whose key is `merchant_knowledge`.
- Adding `merchant_knowledge` to Merchant Pricing Plans.
- Materialising Merchant Pricing Plan features into Billing Plans.
- Validating the semantic shape of generic `configuration` JSON in PostgreSQL.
- Admin, Shopify, Background or Commerce application code.
- R2 bucket creation, object upload/download or credentials.
- BullMQ contracts/workers.
- Embedding-provider implementation.
- Commerce capability, Tool, Tool revision, capability revision or release bootstrap.
- Store Category UI/localization.
- Prompt publication/business workflow implementation.
- Automatic source ordering/reordering UI.
- ANN/HNSW/IVFFlat indexes.
- Any `merchant_knowledge`-specific database trigger, required-feature constraint or plan-name rule.
- Any additional Merchant Knowledge table not specified in this task.

## Requirements

### R1. Add generic plan-feature configuration exactly

Modify `billing.BillingPlanFeature` by adding:

```prisma
configuration Json @default("{}") @db.JsonB
```

Modify `billing.MerchantPricingPlanFeature` by adding:

```prisma
configuration Json @default("{}") @db.JsonB
```

Do not change their existing primary/unique keys, foreign keys, `enabled`, `createdAt`, indexes or delete behaviour.

The migration must add both columns as:

```sql
jsonb NOT NULL DEFAULT '{}'::jsonb
```

Existing rows must survive unchanged apart from receiving `{}` as configuration.

Do not add a JSON CHECK that branches on `Feature.key`.

### R2. Extend `CommercePromptTemplateCategory` and disambiguate both category/template relations

Add to `commerce.CommercePromptTemplateCategory`:

```prisma
defaultTemplateId String? @unique @db.Text

defaultTemplate CommercePromptTemplate?
  @relation(
    "CommercePromptTemplateCategoryDefault",
    fields: [defaultTemplateId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )
```

Because this creates a second relation between `CommercePromptTemplateCategory` and `CommercePromptTemplate`, rename the existing category-membership relation in Prisma exactly:

```prisma
// CommercePromptTemplateCategory
templates CommercePromptTemplate[]
  @relation("CommercePromptTemplateCategoryTemplates")

// CommercePromptTemplate
category CommercePromptTemplateCategory
  @relation(
    "CommercePromptTemplateCategoryTemplates",
    fields: [categoryId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )
```

Add to `CommercePromptTemplate`:

```prisma
defaultForCategory CommercePromptTemplateCategory?
  @relation("CommercePromptTemplateCategoryDefault")
```

The database FK for `defaultTemplateId` must use `ON DELETE RESTRICT ON UPDATE RESTRICT`.

Do not add a database trigger to enforce template `enabled` state or `template.categoryId == category.id`; those cross-row authoring checks belong to Admin/service validation.

### R3. Add prompt-template edit provenance

Add to `commerce.CommerceAgentPromptRevision`:

```prisma
sourceTemplateEditVersion Int?
```

Do not backfill existing revisions.

Do not change `sourceTemplateId`, `sourceTemplate`, revision uniqueness, status, prompt ownership or publication fields.

### R4. Add `CommerceStoreCategoryTaxonomyMapping` exactly

Add:

```prisma
model CommerceStoreCategoryTaxonomyMapping {
  id                        String   @id @default(cuid()) @db.Text
  categoryId                String   @db.Text
  shopifyTaxonomyCategoryId String   @unique @db.VarChar(255)
  weight                    Int      @default(1)
  createdAt                 DateTime @default(now()) @db.Timestamptz(3)
  updatedAt                 DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  category CommercePromptTemplateCategory
    @relation(
      fields: [categoryId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  @@index([categoryId])
  @@schema("commerce")
}
```

Add to `CommercePromptTemplateCategory`:

```prisma
taxonomyMappings CommerceStoreCategoryTaxonomyMapping[]
```

Add database CHECK exactly named:

```text
CommerceStoreCategoryTaxonomyMapping_weight_positive
```

with semantics:

```text
weight > 0
```

### R5. Add `CommerceShopProfile` exactly

Add:

```prisma
model CommerceShopProfile {
  id                         String    @id @default(cuid()) @db.Text
  shopId                     String    @unique @db.Text
  activeCategoryId           String?   @db.Text
  activeCategoryActivatedAt  DateTime? @db.Timestamptz(3)
  pendingCategoryId          String?   @db.Text
  pendingPromptRevisionId    String?   @db.Text
  pendingSelectionGeneration Int       @default(0)
  pendingSelectedAt          DateTime? @db.Timestamptz(3)
  createdAt                  DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt                  DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  shop Shop
    @relation(
      fields: [shopId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  activeCategory CommercePromptTemplateCategory?
    @relation(
      "CommerceShopProfileActiveCategory",
      fields: [activeCategoryId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  pendingCategory CommercePromptTemplateCategory?
    @relation(
      "CommerceShopProfilePendingCategory",
      fields: [pendingCategoryId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  pendingPromptRevision CommerceAgentPromptRevision?
    @relation(
      "CommerceShopProfilePendingPromptRevision",
      fields: [pendingPromptRevisionId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  @@index([activeCategoryId])
  @@index([pendingCategoryId])
  @@index([pendingPromptRevisionId])
  @@schema("commerce")
}
```

Add reverse relation fields exactly:

```prisma
// Shop
commerceShopProfile CommerceShopProfile?

// CommercePromptTemplateCategory
activeShopProfiles  CommerceShopProfile[]
  @relation("CommerceShopProfileActiveCategory")
pendingShopProfiles CommerceShopProfile[]
  @relation("CommerceShopProfilePendingCategory")

// CommerceAgentPromptRevision
pendingForShopProfiles CommerceShopProfile[]
  @relation("CommerceShopProfilePendingPromptRevision")
```

Add CHECK constraints exactly:

```text
CommerceShopProfile_pending_generation_nonnegative
CommerceShopProfile_pending_tuple_check
CommerceShopProfile_active_category_timestamp_check
```

with semantics:

```text
pendingSelectionGeneration >= 0

(
  pendingCategoryId IS NULL
  AND pendingPromptRevisionId IS NULL
  AND pendingSelectedAt IS NULL
)
OR
(
  pendingCategoryId IS NOT NULL
  AND pendingPromptRevisionId IS NOT NULL
  AND pendingSelectedAt IS NOT NULL
)

activeCategoryId IS NULL
  iff
activeCategoryActivatedAt IS NULL
```

Do not add a database trigger for the following cross-row invariants; later application tasks must enforce them transactionally:

```text
pendingPromptRevision belongs to the same shop's SHOP prompt lineage
pendingPromptRevision.status = DRAFT
pendingPromptRevision.sourceTemplateId equals the selected category defaultTemplateId at selection time
pendingPromptRevision.sourceTemplateEditVersion is non-null for ARCH-023-seeded revisions
```

### R6. Add Merchant Knowledge enums exactly

Add:

```prisma
enum MerchantKnowledgeInputKind {
  REMOTE_URL
  UPLOAD

  @@schema("commerce")
}

enum MerchantKnowledgeRevisionReason {
  CREATE
  URL_CHANGE
  FILE_REPLACE
  REFRESH
  REPROCESS
  ENTITLEMENT_CHANGE

  @@schema("commerce")
}

enum MerchantKnowledgeRevisionStatus {
  PENDING
  PROCESSING
  ACTIVE
  FAILED
  SUPERSEDED

  @@schema("commerce")
}

enum MerchantKnowledgeUploadedAssetStatus {
  PENDING_UPLOAD
  AVAILABLE
  FAILED
  DELETED

  @@schema("commerce")
}
```

Do not add a `MerchantKnowledgePurpose` Prisma enum.

### R7. Add `MerchantKnowledgePurpose` exactly

Add:

```prisma
model MerchantKnowledgePurpose {
  id           String   @id @default(cuid()) @db.Text
  key          String   @unique @db.VarChar(64)
  displayName  String   @db.VarChar(160)
  active       Boolean  @default(true)
  displayOrder Int      @default(0)
  createdAt    DateTime @default(now()) @db.Timestamptz(3)
  updatedAt    DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  dataFormats MerchantKnowledgePurposeDataFormat[]
  sources     MerchantKnowledgeSource[]

  @@index([active, displayOrder, key])
  @@schema("commerce")
}
```

### R8. Add `MerchantKnowledgeDataFormat` exactly

Add:

```prisma
model MerchantKnowledgeDataFormat {
  id                   String                     @id @default(cuid()) @db.Text
  key                  String                     @unique @db.VarChar(32)
  displayName          String                     @db.VarChar(160)
  inputKind            MerchantKnowledgeInputKind
  canonicalExtension   String?                    @db.VarChar(16)
  acceptedContentTypes Json                       @db.JsonB
  active               Boolean                    @default(true)
  displayOrder         Int                        @default(0)
  createdAt            DateTime                   @default(now()) @db.Timestamptz(3)
  updatedAt            DateTime                   @default(now()) @updatedAt @db.Timestamptz(3)

  purposes       MerchantKnowledgePurposeDataFormat[]
  sources        MerchantKnowledgeSource[]
  uploadedAssets MerchantKnowledgeUploadedAsset[]

  @@index([active, displayOrder, key])
  @@schema("commerce")
}
```

Do not treat `acceptedContentTypes` as a database trust boundary. Do not add content-sniffing logic to this task.

### R9. Add `MerchantKnowledgePurposeDataFormat` exactly

Add:

```prisma
model MerchantKnowledgePurposeDataFormat {
  purposeId    String   @db.Text
  dataFormatId String   @db.Text
  createdAt    DateTime @default(now()) @db.Timestamptz(3)

  purpose MerchantKnowledgePurpose
    @relation(
      fields: [purposeId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  dataFormat MerchantKnowledgeDataFormat
    @relation(
      fields: [dataFormatId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  sources MerchantKnowledgeSource[]
    @relation("MerchantKnowledgeSourcePurposeDataFormat")

  @@id([purposeId, dataFormatId])
  @@index([dataFormatId, purposeId])
  @@schema("commerce")
}
```

This composite primary key is the database authority for globally supported Purpose/Data Format pairs.

### R10. Seed the exact Purpose catalogue deterministically

The migration must insert these rows if absent by `key`.

Use the following exact seed values:

| id | key | displayName | active | displayOrder |
|---|---|---|---|---:|
| `mk-purpose-company-information` | `COMPANY_INFORMATION` | `Company information` | true | 10 |
| `mk-purpose-customer-support` | `CUSTOMER_SUPPORT` | `Customer support` | true | 20 |
| `mk-purpose-policies` | `POLICIES` | `Policies` | true | 30 |
| `mk-purpose-faq` | `FAQ` | `FAQ` | true | 40 |
| `mk-purpose-product-information` | `PRODUCT_INFORMATION` | `Product information` | true | 50 |
| `mk-purpose-shipping-and-delivery` | `SHIPPING_AND_DELIVERY` | `Shipping and delivery` | true | 60 |
| `mk-purpose-pricing` | `PRICING` | `Pricing` | true | 70 |

The fixed ids above exist only to make migration seed data deterministic. Runtime contracts use `key`, not these ids.

If the migration encounters an existing row with the same key but a different id, it MUST preserve the existing row and resolve compatibility seed inserts by looking up the row by key rather than assuming the fixed id.

### R11. Seed the exact Data Format catalogue deterministically

The migration must insert these rows if absent by `key`.

| id | key | displayName | inputKind | canonicalExtension | acceptedContentTypes | active | displayOrder |
|---|---|---|---|---|---|---|---:|
| `mk-format-web-page` | `WEB_PAGE` | `Web page` | `REMOTE_URL` | NULL | `["text/html","text/plain"]` | true | 10 |
| `mk-format-csv` | `CSV` | `CSV spreadsheet` | `UPLOAD` | `.csv` | `["text/csv","application/csv"]` | true | 20 |
| `mk-format-xlsx` | `XLSX` | `Excel spreadsheet (.xlsx)` | `UPLOAD` | `.xlsx` | `["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]` | true | 30 |

If an existing row has the same key, preserve its id and use that id when creating compatibility rows.

### R12. Seed the exact Purpose/Data Format compatibility rows

After resolving Purpose/Data Format ids by key, ensure these exact pairs exist:

```text
COMPANY_INFORMATION    + WEB_PAGE
CUSTOMER_SUPPORT       + WEB_PAGE
POLICIES               + WEB_PAGE
FAQ                    + WEB_PAGE
PRODUCT_INFORMATION    + WEB_PAGE
PRODUCT_INFORMATION    + CSV
PRODUCT_INFORMATION    + XLSX
SHIPPING_AND_DELIVERY  + WEB_PAGE
PRICING                + WEB_PAGE
PRICING                + CSV
PRICING                + XLSX
```

Do not seed any other pair.

Do not encode plan entitlement here. These rows mean "globally supported", not "allowed on every plan".

### R13. Add `MerchantKnowledgeUploadedAsset` exactly

Add:

```prisma
model MerchantKnowledgeUploadedAsset {
  id               String                               @id @default(cuid()) @db.Text
  shopId           String                               @db.Text
  dataFormatId     String                               @db.Text
  status           MerchantKnowledgeUploadedAssetStatus @default(PENDING_UPLOAD)
  objectKey        String                               @unique @db.Text
  originalFileName String                               @db.VarChar(255)
  contentType      String?                              @db.VarChar(128)
  sizeBytes        BigInt?
  sha256           String?                              @db.VarChar(64)
  uploadExpiresAt  DateTime                             @db.Timestamptz(3)
  availableAt      DateTime?                            @db.Timestamptz(3)
  failureCode      String?                              @db.VarChar(128)
  createdAt        DateTime                             @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime                             @default(now()) @updatedAt @db.Timestamptz(3)

  shop Shop
    @relation(
      fields: [shopId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  dataFormat MerchantKnowledgeDataFormat
    @relation(
      fields: [dataFormatId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  revisions MerchantKnowledgeSourceRevision[]

  @@index([shopId, status, createdAt])
  @@index([dataFormatId, status])
  @@schema("commerce")
}
```

Add to `Shop`:

```prisma
merchantKnowledgeUploadedAssets MerchantKnowledgeUploadedAsset[]
```

Add CHECK exactly named:

```text
MerchantKnowledgeUploadedAsset_available_fields_check
```

with semantics:

```text
status != AVAILABLE
OR
(
  contentType IS NOT NULL
  AND btrim(contentType) <> ''
  AND sizeBytes IS NOT NULL
  AND sizeBytes > 0
  AND sha256 IS NOT NULL
  AND sha256 matches lowercase 64-hex
  AND availableAt IS NOT NULL
)
```

Do not database-validate R2 existence, bytes, hash correctness, key ownership prefix or actual file format.

### R14. Add `MerchantKnowledgeSource` exactly

Add:

```prisma
model MerchantKnowledgeSource {
  id                String   @id @default(cuid()) @db.Text
  shopId            String   @db.Text
  purposeId         String   @db.Text
  dataFormatId      String   @db.Text
  name              String   @db.VarChar(160)
  languageTag       String   @db.VarChar(16)
  position          Int
  currentGeneration Int      @default(0)
  createdAt         DateTime @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  shop Shop
    @relation(
      fields: [shopId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  purpose MerchantKnowledgePurpose
    @relation(
      fields: [purposeId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  dataFormat MerchantKnowledgeDataFormat
    @relation(
      fields: [dataFormatId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  purposeDataFormat MerchantKnowledgePurposeDataFormat
    @relation(
      "MerchantKnowledgeSourcePurposeDataFormat",
      fields: [purposeId, dataFormatId],
      references: [purposeId, dataFormatId],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  revisions MerchantKnowledgeSourceRevision[]

  @@unique([shopId, position])
  @@index([shopId, purposeId, position])
  @@index([shopId, dataFormatId, position])
  @@index([shopId, languageTag])
  @@schema("commerce")
}
```

Add to `Shop`:

```prisma
merchantKnowledgeSources MerchantKnowledgeSource[]
```

Add CHECK constraints exactly:

```text
MerchantKnowledgeSource_position_nonnegative
MerchantKnowledgeSource_generation_nonnegative
```

with semantics:

```text
position >= 0
currentGeneration >= 0
```

The composite FK to `MerchantKnowledgePurposeDataFormat` must exist in the migration in addition to the individual Purpose and Data Format FKs.

### R15. Add `MerchantKnowledgeSourceRevision` exactly

Add:

```prisma
model MerchantKnowledgeSourceRevision {
  id                  String                          @id @default(cuid()) @db.Text
  sourceId            String                          @db.Text
  uploadedAssetId     String?                         @db.Text
  generation          Int
  reason              MerchantKnowledgeRevisionReason
  requestedUrl        String?                         @db.VarChar(2048)
  resolvedUrl         String?                         @db.VarChar(2048)
  status              MerchantKnowledgeRevisionStatus @default(PENDING)
  contentType         String?                         @db.VarChar(128)
  httpStatus          Int?
  normalizedContent   String?                         @db.Text
  contentUnits        Int?
  contentHash         String?                         @db.VarChar(64)
  truncated           Boolean                         @default(false)
  failureCode         String?                         @db.VarChar(128)
  requestedAt         DateTime                        @default(now()) @db.Timestamptz(3)
  processingStartedAt DateTime?                       @db.Timestamptz(3)
  fetchedAt           DateTime?                       @db.Timestamptz(3)
  completedAt         DateTime?                       @db.Timestamptz(3)
  createdAt           DateTime                        @default(now()) @db.Timestamptz(3)
  updatedAt           DateTime                        @default(now()) @updatedAt @db.Timestamptz(3)

  source MerchantKnowledgeSource
    @relation(
      fields: [sourceId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  uploadedAsset MerchantKnowledgeUploadedAsset?
    @relation(
      fields: [uploadedAssetId],
      references: [id],
      onDelete: Restrict,
      onUpdate: Restrict
    )

  chunks MerchantKnowledgeChunk[]

  @@unique([sourceId, generation])
  @@index([sourceId, status, generation])
  @@index([uploadedAssetId])
  @@index([status, requestedAt])
  @@schema("commerce")
}
```

Create partial unique index exactly:

```sql
CREATE UNIQUE INDEX "MerchantKnowledgeSourceRevision_one_active_per_source"
ON commerce."MerchantKnowledgeSourceRevision" ("sourceId")
WHERE "status" = 'ACTIVE';
```

Add CHECK constraints exactly named:

```text
MerchantKnowledgeSourceRevision_locator_check
MerchantKnowledgeSourceRevision_resolved_url_check
MerchantKnowledgeSourceRevision_generation_positive
MerchantKnowledgeSourceRevision_active_content_check
```

with semantics:

```text
exactly one of requestedUrl / uploadedAssetId is non-null

resolvedUrl IS NULL OR requestedUrl IS NOT NULL

generation > 0

status NOT IN (ACTIVE, SUPERSEDED)
OR
(
  contentUnits IS NOT NULL
  AND contentUnits >= 0
  AND contentHash IS NOT NULL
  AND contentHash matches lowercase 64-hex
)
```

Do not database-enforce reason/input-kind compatibility, same-shop asset ownership, matching asset/source Data Format, or asset `AVAILABLE` state. Later application/worker code must validate those cross-table rules.

### R16. Enable pgvector before creating Merchant Knowledge chunks

The migration must execute before creating the vector column:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Do not add another vector extension/schema.

### R17. Add `MerchantKnowledgeChunk` exactly

Add:

```prisma
model MerchantKnowledgeChunk {
  id                    String   @id @default(cuid()) @db.Text
  revisionId            String   @db.Text
  ordinal               Int
  content               String   @db.Text
  contentUnits          Int
  contentHash           String   @db.VarChar(64)
  embedding             Unsupported("vector")
  embeddingProvider     String   @db.VarChar(64)
  embeddingModel        String   @db.VarChar(255)
  embeddingDimensions   Int
  embeddingIndexVersion String   @db.VarChar(64)
  createdAt             DateTime @default(now()) @db.Timestamptz(3)

  revision MerchantKnowledgeSourceRevision
    @relation(
      fields: [revisionId],
      references: [id],
      onDelete: Cascade,
      onUpdate: Restrict
    )

  @@unique([revisionId, ordinal])
  @@index([revisionId, ordinal])
  @@index([embeddingIndexVersion, embeddingDimensions])
  @@schema("commerce")
}
```

Add CHECK constraints exactly named:

```text
MerchantKnowledgeChunk_ordinal_nonnegative
MerchantKnowledgeChunk_content_units_positive
MerchantKnowledgeChunk_embedding_dimensions_positive
MerchantKnowledgeChunk_embedding_dimensions_match
MerchantKnowledgeChunk_content_hash_check
```

with semantics:

```text
ordinal >= 0
contentUnits > 0
embeddingDimensions > 0
vector_dims(embedding) = embeddingDimensions
contentHash matches lowercase 64-hex
```

Do not add HNSW, IVFFlat or another ANN index.

### R18. Preserve existing data and use one additive migration

The migration must be additive with respect to all existing Shop, billing, prompt, capability, Tool, release and grant data.

Upgrade behaviour must satisfy all of the following:

```text
existing BillingPlanFeature rows preserved
existing MerchantPricingPlanFeature rows preserved
new configuration columns = {} for existing rows

existing CommercePromptTemplateCategory rows preserved
defaultTemplateId = NULL for existing rows unless already populated by this migration fixture

existing CommercePromptTemplate rows preserved
existing CommerceAgentPromptRevision rows preserved
sourceTemplateEditVersion = NULL for existing rows

no existing Shop/Subscription/Prompt/Capability/Tool/Release/Grant row deleted
new Merchant Knowledge tables initially contain only the architecture seed catalogue rows
```

Do not rebuild or replace unrelated tables.

### R19. Add exact focused schema validator

Create:

```text
scripts/validate-arch023-merchant-knowledge-schema.mjs
```

It must fail unless the checked-in Prisma schema contains exactly the ARCH-023 additions required by this task, including:

```text
both configuration JsonB fields
all four Merchant Knowledge enums
CommerceStoreCategoryTaxonomyMapping
CommerceShopProfile
MerchantKnowledgePurpose
MerchantKnowledgeDataFormat
MerchantKnowledgePurposeDataFormat
MerchantKnowledgeUploadedAsset
MerchantKnowledgeSource
MerchantKnowledgeSourceRevision
MerchantKnowledgeChunk
all required reverse relation fields
all required relation names
all required Prisma indexes/unique keys
```

It must also fail if any of the following are introduced:

```text
MerchantKnowledgePurpose enum
merchant_knowledge-specific required-plan constraint
merchant_knowledge-specific trigger
Merchant Knowledge ANN index
additional Merchant Knowledge entitlement table
```

### R20. Add exact focused migration validator

Create:

```text
scripts/validate-arch023-merchant-knowledge-migration.mjs
```

It must inspect the fixed migration and fail unless it contains:

```text
CREATE EXTENSION IF NOT EXISTS vector
all required tables/enums/columns/FKs
the composite Purpose/Data Format FK
the one-ACTIVE partial unique index
all exact CHECK constraint names from this task
the exact Purpose seed keys
the exact Data Format seed keys
the exact eleven Purpose/Data Format compatibility pairs
no HNSW/IVFFlat index
no Feature/plan/capability/Tool/release seed for merchant_knowledge
```

Add package scripts exactly:

```json
"test:arch023-merchant-knowledge-schema": "node scripts/validate-arch023-merchant-knowledge-schema.mjs",
"test:arch023-merchant-knowledge-migration": "node scripts/validate-arch023-merchant-knowledge-migration.mjs"
```

Do not rename existing scripts.

### R21. Rehearse both fresh and upgrade migration paths

Use isolated/disposable PostgreSQL targets.

Fresh rehearsal:

```text
empty database
-> apply all migrations including ARCH-023
-> Prisma schema validates
-> all ARCH-023 seed catalogue rows exist exactly once
-> pgvector extension exists
-> vector_dims constraint accepts matching dimensions and rejects mismatch
```

Upgrade rehearsal:

```text
database at the migration immediately before ARCH-023
-> create representative existing:
   Shop
   BillingPlan + BillingPlanFeature
   MerchantPricingPlan + MerchantPricingPlanFeature
   CommercePromptTemplateCategory
   CommercePromptTemplate
   CommerceAgentPrompt + CommerceAgentPromptRevision
   CommerceCapability/Tool/Release data where fixtures already support them
-> apply ARCH-023 migration
-> prove all pre-existing rows survive
-> prove new additive columns have expected NULL/{} defaults
-> prove seed catalogue rows/pairs exist exactly once
```

The upgrade fixture does not need to manufacture every platform table. It must cover every existing table modified by this task and enough related rows to detect accidental destructive migration.

### R22. Exercise database-enforceable negative cases

Focused migration validation/rehearsal must prove PostgreSQL rejects at least these invalid writes:

```text
CommerceStoreCategoryTaxonomyMapping.weight <= 0

CommerceShopProfile.pendingSelectionGeneration < 0
partial pending tuple
activeCategoryId without activeCategoryActivatedAt
activeCategoryActivatedAt without activeCategoryId

MerchantKnowledgeUploadedAsset AVAILABLE without required metadata
MerchantKnowledgeUploadedAsset AVAILABLE with sizeBytes <= 0
MerchantKnowledgeUploadedAsset AVAILABLE with non-lowercase/non-64-hex sha256

MerchantKnowledgeSource.position < 0
MerchantKnowledgeSource.currentGeneration < 0
MerchantKnowledgeSource with unsupported Purpose/Data Format composite pair

MerchantKnowledgeSourceRevision with both locators null
MerchantKnowledgeSourceRevision with both locators non-null
MerchantKnowledgeSourceRevision.resolvedUrl without requestedUrl
MerchantKnowledgeSourceRevision.generation <= 0
second ACTIVE revision for the same source
ACTIVE/SUPERSEDED revision without contentUnits/contentHash

MerchantKnowledgeChunk.ordinal < 0
MerchantKnowledgeChunk.contentUnits <= 0
MerchantKnowledgeChunk.embeddingDimensions <= 0
MerchantKnowledgeChunk vector dimension mismatch
MerchantKnowledgeChunk malformed contentHash
```

Also prove the corresponding valid cases succeed.

## Work Items

- [x] Add the two generic plan-feature `configuration` JsonB columns without changing existing plan-feature keys/relations.
- [x] Add Store Category default-template persistence and explicitly name both Category/Template Prisma relations.
- [x] Add `sourceTemplateEditVersion` provenance.
- [x] Add `CommerceStoreCategoryTaxonomyMapping` and its positive-weight check.
- [x] Add `CommerceShopProfile`, exact reverse relations and local-field checks.
- [x] Add the four Merchant Knowledge enums.
- [x] Add Purpose, Data Format and compatibility models.
- [x] Seed the seven Purpose rows exactly.
- [x] Seed the three Data Format rows exactly.
- [x] Seed the eleven supported Purpose/Data Format pairs exactly.
- [x] Add uploaded-asset metadata persistence and AVAILABLE-state check.
- [x] Add Merchant Knowledge source persistence and composite compatibility FK.
- [x] Add source revision persistence, locator/content checks and one-ACTIVE partial unique index.
- [x] Enable pgvector and add Merchant Knowledge chunk persistence/checks.
- [x] Add required reverse relation fields to existing models.
- [x] Create the focused schema validator and package script.
- [x] Create the focused migration validator and package script.
- [x] Rehearse fresh migration.
- [x] Rehearse upgrade migration preserving modified-table data.
- [x] Exercise all required database-enforceable negative cases.
- [x] Record exact migration/validation evidence in the Completion Report.

## Interfaces / Contracts

This task produces the database contract consumed by later ARCH-023 repository tasks.

### Generic billing feature configuration

```text
billing.MerchantPricingPlanFeature.configuration JsonB
billing.BillingPlanFeature.configuration         JsonB
```

The database does not own the JSON semantic contract.

### Merchant Knowledge catalogue identity

Stable cross-application identity is by:

```text
MerchantKnowledgePurpose.key
MerchantKnowledgeDataFormat.key
```

Database ids are persistence identities only.

### Supported Purpose/Data Format pair

Authoritative database key:

```text
MerchantKnowledgePurposeDataFormat(
  purposeId,
  dataFormatId
)
```

### Shop-scoped Merchant Knowledge ownership

```text
Shop.id
  -> MerchantKnowledgeSource.shopId
  -> MerchantKnowledgeUploadedAsset.shopId
```

### Revision identity

```text
MerchantKnowledgeSourceRevision:
  unique(sourceId, generation)
  at most one ACTIVE per source
```

### Uploaded original

```text
MerchantKnowledgeSourceRevision.uploadedAssetId
  -> MerchantKnowledgeUploadedAsset.id
```

The database stores metadata only; R2 bytes are out of scope.

### Vector persistence

```text
MerchantKnowledgeChunk.embedding = pgvector vector
```

No ANN index in v1.

## Dependencies

None.

This is the first ARCH-023 database prerequisite.

Later task definitions may add this task to their `depends_on`; do not modify future task files from this task.

## Enables

Planned downstream areas after architect acceptance:

```text
ARCH-023 Shared Merchant Knowledge contracts
ARCH-023 Admin plan/category authoring
ARCH-023 Shopify BillingPlan materialisation/onboarding/source management
ARCH-023 Background ingestion/reconciliation
ARCH-023 Commerce lookup/bootstrap
```

No downstream task may be started by the database agent.

## Acceptance Criteria

- [x] One additive migration owns the complete ARCH-023 database shape.
- [x] Existing `BillingPlanFeature` and `MerchantPricingPlanFeature` rows survive and receive `{}` configuration.
- [x] Store Category/default-template persistence is Prisma-valid with explicitly named dual Category/Template relations.
- [x] `CommerceShopProfile` has exactly one row per shop and the required active/pending local invariants.
- [x] There is no `MerchantKnowledgePurpose` enum.
- [x] Purpose/Data Format identity is table-backed and the composite compatibility pair is database-enforced.
- [x] Exactly seven Purpose keys, three Data Format keys and eleven compatibility pairs are seeded.
- [x] No plan entitlement is encoded in the Purpose/Data Format seed table.
- [x] Uploaded R2 bytes are not stored in PostgreSQL; only immutable asset metadata is persisted.
- [x] A source cannot reference a globally unsupported Purpose/Data Format pair.
- [x] A source revision has exactly one locator and at most one ACTIVE revision exists per source.
- [x] ACTIVE/SUPERSEDED revisions require bounded content metadata.
- [x] pgvector is enabled and chunk vector dimensions are database-checked against `embeddingDimensions`.
- [x] No ANN index is added.
- [x] No `merchant_knowledge` Feature/plan/capability/Tool/release row is seeded by this task.
- [x] No `merchant_knowledge`-specific database invariant is introduced.
- [x] Fresh migration rehearsal passes.
- [x] Upgrade rehearsal preserves all existing rows in tables modified by this task.
- [x] Required negative database cases fail for the intended constraint/index reason.
- [x] No unrelated schema or migration is changed.

## Validation

- [x] `./node_modules/.bin/prisma format --schema prisma/schema.prisma` (passed before final validation).
- [x] `./node_modules/.bin/prisma validate --schema prisma/schema.prisma` (passed).
- [x] `npm run test:arch023-merchant-knowledge-schema` (passed).
- [x] `npm run test:arch023-merchant-knowledge-migration` (static contract passed).
- [x] Fresh isolated PostgreSQL 15.19 + pgvector migration rehearsal passed on `arch023_test_fresh`.
- [x] Upgrade isolated PostgreSQL 15.19 + pgvector rehearsal passed on `arch023_test_upgrade`, preserving every predecessor table and seeded rows in all modified tables.
- [x] Required valid and invalid direct-SQL cases passed, including vector dimension controls and exact catalogue counts.
- [x] `git diff --check` passed.

If the repository's current package scripts or migration harness differ from assumptions, inspect and use the repository-declared mechanism while preserving the exact behavioural validation above. Do not invent an unrelated test framework.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, clear the active execution claim as required by the normal handoff protocol, return the Completion Report to `moda_architect` and STOP. Do not begin any Shared, Admin, Shopify, Background, Commerce, Gateway or system-test work.

## Implementation Notes

This task intentionally combines the ARCH-023 database work because the schema is one coherent durable boundary and all later repositories require the complete shape.

Architectural choices fixed by this task:

```text
one additive ARCH-023 migration
no Merchant Knowledge Purpose enum
Purpose/Data Format catalogue is table-backed
supported pair is a composite database relationship
plan-specific allowedSourceTypes stays in generic JsonB configuration
R2 bytes remain outside PostgreSQL
source revisions own normalized content lifecycle
chunks own pgvector embeddings
no ANN index in v1
no merchant_knowledge-specific database rule
```

The exact seed `displayName` and `displayOrder` values in R10/R11 make previously unspecified catalogue metadata deterministic for implementation. Cross-application contracts continue to use stable keys.

Do not "simplify" the schema by:

```text
replacing Purpose/Data Format tables with enums
removing the composite supported-pair FK
storing uploaded file bytes in PostgreSQL
adding separate WEB_PAGE/CSV/XLSX source tables
adding a Merchant Knowledge entitlement table
moving plan source-type entitlement out of BillingPlanFeature.configuration
adding plan-name-specific fields
adding per-shop embedding model fields
adding ANN indexes
```

Do not "strengthen" the database by inventing cross-row triggers for rules explicitly deferred to application/runtime validation in this task.

## Completion Report

### Status

Implementation complete; returned to `review` for `moda_architect` acceptance. Attempt 1; active claim cleared.

### Files Changed

Implementation repository (`moda-interact-database`):

- `prisma/schema.prisma`
- `prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql`
- `scripts/validate-arch023-merchant-knowledge-schema.mjs`
- `scripts/validate-arch023-merchant-knowledge-migration.mjs`
- `scripts/fixtures/arch023-merchant-knowledge-cases.mjs`
- `package.json`

Parent workspace task record: this task file only. No parent submodule gitlink was staged.

### Work Completed

- Added the complete additive ARCH-023 Prisma/PostgreSQL schema, exact keys, relations, checks, indexes, pgvector storage and key-based catalogue seeds in the fixed migration.
- Added focused schema and migration contract validators and package scripts.
- Added direct-SQL fixture coverage for required valid and invalid database writes, JSONB defaults/round-trip, catalogue counts and vector dimension enforcement.
- Updated fixture setup to satisfy the existing ARCH-014 deferred pricing catalogue constraint and active revision foreign-key ordering.

### Validation Results

- `./node_modules/.bin/prisma format --schema prisma/schema.prisma` — passed.
- `./node_modules/.bin/prisma validate --schema prisma/schema.prisma` — passed.
- `npm run test:arch023-merchant-knowledge-schema` — passed.
- `npm run test:arch023-merchant-knowledge-migration` — passed.
- `node --check` on both validators and the fixture — passed.
- Fresh rehearsal: all 21 migrations applied to isolated `arch023_test_fresh`; 7 purposes, 3 formats and 11 pairs verified; all valid/invalid controls passed.
- Upgrade rehearsal: 20 predecessor migrations applied, representative legacy rows seeded, then ARCH-023 applied; every predecessor table snapshot and modified-table row snapshot was preserved; all ARCH-023 checks passed.
- `git diff --check` — passed.
- Environment: PostgreSQL 15.19 with `pgvector/pg15`; Prisma CLI/Client 6.19.3; Node.js 24.21.0.
- Published implementation commit: `1e12bb3507f507579e15a6782c9620956609801c` on `task/ARCH-023-DATABASE-001`.

### Launcher and Worktree Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-DATABASE-001`, `task/ARCH-023-DATABASE-001`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-DATABASE-001`, `task/ARCH-023-DATABASE-001`.
- Shared workspace and shared implementation checkouts switched or mutated for task work: no.
- Another task worktree reused: no.
- Start synchronization: launcher preparation passed; both new task branches were based on their respective `origin/main`, and the parent claim was pushed before implementation. No startup synchronization/preparation was repeated.
- `git submodule sync --recursive` and `git submodule update --init --recursive`: passed during preparation. The database repository has no recursive submodule entries.

### Deviations

The isolated rehearsal fixture inserts all required ARCH-014 pricing translations in one transaction because that predecessor schema uses deferred catalogue validation. No production schema/migration scope deviation.

### Assumptions

Disposable rehearsal databases were task-owned local targets `arch023_test_fresh` and `arch023_test_upgrade` on `127.0.0.1:55432`; no shared database was used.

### Unresolved Issues

`npm ci` reported 3 high-severity audit findings and lifecycle-script approval warnings. These were not introduced or changed by this task; Prisma Client was explicitly generated from the task schema for rehearsal.

### Architectural Concerns

None identified. The Architect Review section below remains untouched.

## Architect Review

### Review Status

Pending

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
