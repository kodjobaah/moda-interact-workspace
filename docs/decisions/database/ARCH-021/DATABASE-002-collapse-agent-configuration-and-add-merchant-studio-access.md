---
id: ARCH-021-DATABASE-002
architecture_id: ARCH-021
title: Collapse Agent Configuration persistence and add merchant Studio access
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-DATABASE-001
enables:
  - ARCH-021-COMMERCE-025
  - ARCH-021-COMMERCE-026
  - ARCH-021-COMMERCE-027
created: 2026-09-24
updated: 2026-09-24
---

# Collapse Agent Configuration persistence and add merchant Studio access

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the fragmented Phase-2 model-selection/prompt-pointer/template-revision persistence with one Agent Configuration model, keep prompt revisions and template categories, add the shop-scoped merchant Studio authorization record, and make audit events support both platform-admin and merchant actors plus lightweight operation reconciliation.

## Context

ARCH-021 is still pre-production. The current Phase-2 schema uses separate platform/shop model-selection tables, separate platform/shop prompt-pointer tables, `generationId` ABA protection, and template revisions. Those structures are more complex than the product requires. The replacement must preserve current data while reducing the runtime configuration model.

The target invariants are:

```text
model catalogue                    durable / platform managed
CommerceAgentConfiguration         one row per environment+scope
CommerceAgentPromptRevision        immutable after publish
CommercePromptTemplateCategory     first-class taxonomy
CommercePromptTemplate             current reusable authoring text
CommerceStudioMerchantAccess       Auth.js authorization step-up only
CommerceAuditEvent                 audit + lightweight reconciliation receipt
```

## Scope

Modify only `moda-interact-database` files required for this schema reduction and migration.

Required primary files:

```text
prisma/schema.prisma
prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql
scripts/validate-arch021-simplification-schema.mjs
scripts/validate-arch021-simplification-migration.mjs
package.json
```

Existing ARCH-021 schema validators may be updated only where necessary to reflect the replacement schema.

## Out of Scope

- Commerce service/UI implementation.
- Auth.js callbacks or authorization resolvers.
- Merchant self-service onboarding.
- Background/MCP authentication.
- Tool/capability/release/grant schema changes.
- Removing historical `CommerceAuditAction` enum values.
- Prompt-template category removal.
- Any destructive migration that discards current Phase-2 prompt/model/template content before deterministic backfill.

## Requirements

### R1. Add exactly one `CommerceAgentConfiguration` model

Add this Prisma model, using these field names and semantics:

```prisma
model CommerceAgentConfiguration {
  id                     String                   @id @default(cuid()) @db.Text
  environment            CommerceEnvironment
  scope                  CommerceAgentPromptScope
  shopId                 String?                  @db.Text
  modelId                String?                 @db.Text
  activePromptRevisionId String?                 @db.Text
  modelEditVersion       Int                      @default(1)
  promptEditVersion      Int                      @default(1)
  createdAt              DateTime                 @default(now()) @db.Timestamptz(3)
  updatedAt              DateTime                 @default(now()) @updatedAt @db.Timestamptz(3)

  shop                 Shop?                         @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  model                CommerceModelCatalogueEntry?  @relation(fields: [modelId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  activePromptRevision CommerceAgentPromptRevision?  @relation(fields: [activePromptRevisionId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  auditEvents          CommerceAuditEvent[]

  @@index([environment, scope, shopId])
  @@index([modelId])
  @@index([activePromptRevisionId])
  @@schema("commerce")
}
```

Do not add `generationId`. Do not add separate model/prompt selection/pointer models.

The migration must create these partial unique indexes exactly:

```sql
CREATE UNIQUE INDEX "CommerceAgentConfiguration_one_platform_per_environment"
ON commerce."CommerceAgentConfiguration" ("environment")
WHERE "scope" = 'PLATFORM' AND "shopId" IS NULL;

CREATE UNIQUE INDEX "CommerceAgentConfiguration_one_shop_per_environment"
ON commerce."CommerceAgentConfiguration" ("environment", "shopId")
WHERE "scope" = 'SHOP' AND "shopId" IS NOT NULL;
```

Add check constraint exactly named `CommerceAgentConfiguration_scope_shop_check` with semantics:

```text
scope=PLATFORM -> shopId IS NULL
scope=SHOP     -> shopId IS NOT NULL
```

### R2. Preserve independent model/prompt CAS

`modelEditVersion` is changed only by model/default mutations.

`promptEditVersion` is changed only by prompt/default mutations.

Changing a model must not create a CAS conflict with an unrelated prompt change, and vice versa.

### R3. Backfill configuration rows deterministically

Before dropping old tables, create/upsert configuration rows from the union of existing rows.

Platform key:

```text
(environment, scope=PLATFORM, shopId=NULL)
```

Data mapping:

```text
modelId                <- CommercePlatformModelSelection.modelId or NULL
activePromptRevisionId <- CommercePlatformPromptPointer.promptRevisionId or NULL
modelEditVersion       <- CommercePlatformModelSelection.editVersion or 1
promptEditVersion      <- CommercePlatformPromptPointer.editVersion or 1
createdAt              <- earliest non-null source createdAt, otherwise migration timestamp
updatedAt              <- latest non-null source updatedAt, otherwise createdAt
```

The shop source row set is the FULL OUTER JOIN of `CommerceShopModelSelection` and `CommerceShopPromptPointer` on `(environment, shopId)`, with the analogous mappings and `generationId` intentionally not migrated.

### R4. Database-enforce prompt scope ownership

Create function exactly `commerce.arch021_agent_configuration_guard` and trigger exactly `CommerceAgentConfiguration_guard_trigger`.

On INSERT/UPDATE, when `activePromptRevisionId` is non-null:

1. resolve its `CommerceAgentPromptRevision` and parent `CommerceAgentPrompt`;
2. PLATFORM configuration may reference only a PLATFORM prompt with `shopId IS NULL`;
3. SHOP configuration may reference only a SHOP prompt whose `shopId` equals configuration `shopId`;
4. referenced revision must have `status='PUBLISHED'`.

Reject violations with a PostgreSQL exception. Service-layer validation does not replace this guard.

### R5. Keep template category; simplify template content

Keep `CommercePromptTemplateCategory` unchanged as the first-class category/classification model.

Modify `CommercePromptTemplate` by adding:

```prisma
promptText String @default("") @db.Text
```

Remove the `revisions CommercePromptTemplateRevision[]` relation.

Backfill `CommercePromptTemplate.promptText` using exactly this precedence per template:

1. highest `revisionNumber` with `status='PUBLISHED'`;
2. otherwise highest `revisionNumber` of any status;
3. otherwise empty string.

### R6. Remove template-revision runtime persistence

Add to `CommerceAgentPromptRevision`:

```prisma
sourceTemplateId String? @db.Text
sourceTemplate   CommercePromptTemplate? @relation(fields: [sourceTemplateId], references: [id], onDelete: Restrict, onUpdate: Restrict)
```

For every current `sourceTemplateRevisionId`, backfill `sourceTemplateId` from the referenced `CommercePromptTemplateRevision.templateId`.

Then remove `CommerceAgentPromptRevision.sourceTemplateRevisionId` and the `CommercePromptTemplateRevision` model/table. Keep prompt revisions themselves unchanged and immutable after publish.

### R7. Remove PlatformAdmin-only creator fields from merchant-editable prompt runtime models

Remove `createdByAdminId` and `createdBy` from `CommerceAgentPrompt`.

Remove `createdByAdminId`, `createdBy`, `publishedByAdminId`, and `publishedBy` from `CommerceAgentPromptRevision`.

Actor history for new operations is represented by `CommerceAuditEvent`. Do not replace these fields with another polymorphic creator column.

### R8. Add merchant Studio authorization enum/model exactly

Add enum `CommerceStudioMerchantRole` with `ADMIN`, `EDITOR`, and `VIEWER` in schema `commerce`.

Add model `CommerceStudioMerchantAccess` with shop, provider, providerSubject, normalized email, role, active, platform-admin creator/updater, login and timestamps; unique `[shopId, email]`, unique `[shopId, provider, providerSubject]`, indexes `[email, active]`, `[provider, providerSubject, active]`, `[shopId, active, role]`, and schema `commerce`. Use the exact relation names `CommerceStudioMerchantAccessCreator`, `CommerceStudioMerchantAccessUpdater`, and `CommerceAuditMerchantActor`, with restrictive foreign keys.

Email values must be normalized by service code to trimmed lowercase. Add check exactly named `CommerceStudioMerchantAccess_email_normalized_check` requiring `email = lower(btrim(email))` and non-empty.

Create function exactly `commerce.arch021_merchant_access_identity_guard` and trigger `CommerceStudioMerchantAccess_identity_guard_trigger`.

The trigger must allow `providerSubject` transitions only `NULL -> non-empty` and same non-empty value -> same value. It must reject non-null A -> non-null B and non-null -> NULL.

### R9. Make Commerce audit actor-compatible and reconciliation-capable

Add enum `CommerceAuditActorType` with `PLATFORM_ADMIN` and `MERCHANT_ACCESS` in schema `commerce`.

Change `CommerceAuditEvent` to add `actorType` defaulting to `PLATFORM_ADMIN`, make `actorAdminId` nullable, and add nullable `actorMerchantAccessId`, `operationId` (`VarChar(128)`), `agentConfigurationId`, and `merchantAccessId` relations as specified. Keep `promptTemplateRevisionId` as an optional raw historical identifier without a Prisma relation/FK.

Create partial unique index exactly:

```sql
CREATE UNIQUE INDEX "CommerceAuditEvent_operation_id_unique"
ON commerce."CommerceAuditEvent" ("operationId")
WHERE "operationId" IS NOT NULL;
```

Backfill `actorType='PLATFORM_ADMIN'` for all existing rows. For existing Phase-2 Agent Configuration/template actions, set `operationId=id` when null; do not modify unrelated historical audit rows. Add check exactly named `CommerceAuditEvent_actor_check` requiring exactly one actor according to `actorType`.

### R10. Audit action compatibility

Do not remove current `CommerceAuditAction` values. Add exactly:

```text
UPSERT_AGENT_CONFIGURATION
SET_AGENT_MODEL
CLEAR_AGENT_MODEL
SET_AGENT_PROMPT
CLEAR_AGENT_PROMPT
UPDATE_PROMPT_TEMPLATE_CONTENT
GRANT_MERCHANT_STUDIO_ACCESS
UPDATE_MERCHANT_STUDIO_ACCESS
DISABLE_MERCHANT_STUDIO_ACCESS
BIND_MERCHANT_STUDIO_IDENTITY
```

### R11. Drop obsolete tables only after successful backfill

After all backfills and new FKs/guards are valid, drop exactly `CommercePlatformModelSelection`, `CommerceShopModelSelection`, `CommercePlatformPromptPointer`, `CommerceShopPromptPointer`, and `CommercePromptTemplateRevision`.

Do not drop model catalogue, prompt lineage/revisions, template categories/templates, capabilities, releases, grants, connections, credentials, tools or audits.

### R12. PlatformAdmin relation cleanup

Remove inverse relations referencing the five dropped models and removed prompt creator/publisher relations.

Add:

```text
createdCommerceStudioMerchantAccess CommerceStudioMerchantAccess[] @relation("CommerceStudioMerchantAccessCreator")
updatedCommerceStudioMerchantAccess CommerceStudioMerchantAccess[] @relation("CommerceStudioMerchantAccessUpdater")
```

Keep existing model-catalogue/template-category/template admin relations.

### R13. One migration only

Create exactly `prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql` and perform add/backfill/guard/drop in one deterministic migration. Do not create a second ARCH-021 simplification migration.

### R14. Deterministic validators

Add scripts `scripts/validate-arch021-simplification-schema.mjs` and `scripts/validate-arch021-simplification-migration.mjs`.

Add package scripts exactly:

```json
"test:arch021-simplification-schema": "node scripts/validate-arch021-simplification-schema.mjs",
"test:arch021-simplification-migration": "node scripts/validate-arch021-simplification-migration.mjs"
```

Migration validation must use disposable PostgreSQL and prove fresh schema application and upgrade from current Phase-2 schema with seeded platform/shop model+prompt/template data. The upgrade fixture must prove all mapped IDs/text/edit versions and audit `operationId` backfills exactly.

## Work Items

- [ ] Implement R1-R14 exactly.
- [ ] Generate Prisma client and validate schema.
- [ ] Prove fresh migration.
- [ ] Prove seeded Phase-2 upgrade migration.
- [ ] Prove prompt-scope and merchant-identity DB guards.
- [ ] Prove obsolete five tables no longer exist after migration.

## Interfaces / Contracts

Producer/consumer schema contract for subsequent tasks:

```text
CommerceAgentConfiguration
CommercePromptTemplate.promptText
CommerceAgentPromptRevision.sourceTemplateId
CommerceStudioMerchantAccess
CommerceAuditEvent.operationId + actorType
```

No Shared-package contract is introduced.

## Dependencies

- ARCH-021-DATABASE-001

## Enables

- ARCH-021-COMMERCE-025
- ARCH-021-COMMERCE-026
- ARCH-021-COMMERCE-027

## Acceptance Criteria

- [ ] Exactly one Agent Configuration table replaces the four selection/pointer tables.
- [ ] Model and prompt CAS remain independent through separate version fields.
- [ ] Existing Phase-2 model/prompt selections resolve identically after migration.
- [ ] `CommercePromptTemplateCategory` remains first-class.
- [ ] Template text is preserved without `CommercePromptTemplateRevision`.
- [ ] Published Agent Prompt revisions remain immutable.
- [ ] Merchant Studio access supports multiple shop rows for one Auth.js identity.
- [ ] Bound merchant provider subjects cannot be reassigned.
- [ ] Commerce audit events support platform and merchant actors.
- [ ] `operationId` can prove transaction commit without storing mutation results/payload hashes.
- [ ] No unrelated Commerce domain schema is changed.

## Validation

- [ ] `npx prisma format --schema prisma/schema.prisma`
- [ ] `npx prisma validate --schema prisma/schema.prisma`
- [ ] `npm run test:arch021-simplification-schema`
- [ ] `npm run test:arch021-simplification-migration`
- [ ] repository-declared focused database tests for changed models
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Do not retain old selection/pointer/template-revision models behind compatibility views. ARCH-021 is pre-production and this task is an intentional breaking simplification after deterministic data migration.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
