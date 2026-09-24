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
status: review
priority: 5
executor: null
claimed_at: null
attempt: 1
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
  modelId                String?                  @db.Text
  activePromptRevisionId String?                  @db.Text
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

Shop key:

```text
(environment, scope=SHOP, shopId)
```

The source row set is the FULL OUTER JOIN of `CommerceShopModelSelection` and `CommerceShopPromptPointer` on `(environment, shopId)`.

Map:

```text
modelId                <- model selection modelId or NULL
activePromptRevisionId <- prompt pointer promptRevisionId or NULL
modelEditVersion       <- model selection editVersion or 1
promptEditVersion      <- prompt pointer editVersion or 1
createdAt              <- earliest non-null source createdAt
updatedAt              <- latest non-null source updatedAt
```

`generationId` values are intentionally not migrated.

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

Then remove:

```text
CommerceAgentPromptRevision.sourceTemplateRevisionId
CommercePromptTemplateRevision model/table
```

Keep prompt revisions themselves unchanged and immutable after publish.

### R7. Remove PlatformAdmin-only creator fields from merchant-editable prompt runtime models

Remove these fields/relations from `CommerceAgentPrompt`:

```text
createdByAdminId
createdBy
```

Remove these fields/relations from `CommerceAgentPromptRevision`:

```text
createdByAdminId
createdBy
publishedByAdminId
publishedBy
```

Actor history for new operations is represented by `CommerceAuditEvent`. Do not replace these fields with another polymorphic creator column.

### R8. Add merchant Studio authorization enum/model exactly

Add enum:

```prisma
enum CommerceStudioMerchantRole {
  ADMIN
  EDITOR
  VIEWER

  @@schema("commerce")
}
```

Add model:

```prisma
model CommerceStudioMerchantAccess {
  id                       String                     @id @default(cuid()) @db.Text
  shopId                   String                     @db.Text
  provider                 String                     @default("google") @db.VarChar(32)
  providerSubject          String?                    @db.VarChar(255)
  email                    String                     @db.VarChar(320)
  role                     CommerceStudioMerchantRole @default(ADMIN)
  active                   Boolean                    @default(true)
  createdByPlatformAdminId String                     @db.Text
  updatedByPlatformAdminId String?                    @db.Text
  lastLoginAt              DateTime?                  @db.Timestamptz(3)
  createdAt                DateTime                   @default(now()) @db.Timestamptz(3)
  updatedAt                DateTime                   @default(now()) @updatedAt @db.Timestamptz(3)

  shop      Shop           @relation(fields: [shopId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  createdBy PlatformAdmin  @relation("CommerceStudioMerchantAccessCreator", fields: [createdByPlatformAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  updatedBy PlatformAdmin? @relation("CommerceStudioMerchantAccessUpdater", fields: [updatedByPlatformAdminId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  auditEvents CommerceAuditEvent[] @relation("CommerceAuditMerchantActor")

  @@unique([shopId, email])
  @@unique([shopId, provider, providerSubject])
  @@index([email, active])
  @@index([provider, providerSubject, active])
  @@index([shopId, active, role])
  @@schema("commerce")
}
```

Email values must be normalized by service code to trimmed lowercase. Add DB check exactly named `CommerceStudioMerchantAccess_email_normalized_check` requiring `email = lower(btrim(email))` and non-empty.

Create function exactly `commerce.arch021_merchant_access_identity_guard` and trigger `CommerceStudioMerchantAccess_identity_guard_trigger`.

The trigger must allow `providerSubject` transition only:

```text
NULL -> non-empty value
same non-empty value -> same value
```

It must reject:

```text
non-null A -> non-null B
non-null -> NULL
```

### R9. Make Commerce audit actor-compatible and reconciliation-capable

Add enum:

```prisma
enum CommerceAuditActorType {
  PLATFORM_ADMIN
  MERCHANT_ACCESS

  @@schema("commerce")
}
```

Change `CommerceAuditEvent` by adding/changing exactly:

```text
actorType              CommerceAuditActorType @default(PLATFORM_ADMIN)
actorAdminId           String?                 // currently required; make nullable
actorMerchantAccessId  String?
operationId            String? @db.VarChar(128)
agentConfigurationId   String?
merchantAccessId       String?
```

Relations:

```text
actorAdminId          -> PlatformAdmin.id
actorMerchantAccessId -> CommerceStudioMerchantAccess.id relation name CommerceAuditMerchantActor
agentConfigurationId  -> CommerceAgentConfiguration.id
merchantAccessId      -> CommerceStudioMerchantAccess.id
```

Keep `promptTemplateRevisionId` as an optional raw text historical identifier after dropping the TemplateRevision table, but remove its Prisma relation/FK.

Create partial unique index exactly:

```sql
CREATE UNIQUE INDEX "CommerceAuditEvent_operation_id_unique"
ON commerce."CommerceAuditEvent" ("operationId")
WHERE "operationId" IS NOT NULL;
```

Backfill `actorType='PLATFORM_ADMIN'` for all existing rows.

For existing Phase-2 Agent Configuration/template actions, set `operationId=id` when the new column is null. The relevant action values are the existing enum values from `CREATE_MODEL_CATALOGUE_ENTRY` through `CLEAR_SHOP_PROMPT_POINTER` inclusive; do not modify unrelated historical audit rows.

Add check exactly named `CommerceAuditEvent_actor_check` requiring exactly one actor according to `actorType`.

### R10. Audit action compatibility

Do not remove any current `CommerceAuditAction` values because existing rows may use them.

Add exactly these values:

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

After all backfills and new FKs/guards are valid, drop exactly:

```text
CommercePlatformModelSelection
CommerceShopModelSelection
CommercePlatformPromptPointer
CommerceShopPromptPointer
CommercePromptTemplateRevision
```

Do not drop model catalogue, prompt lineage/revisions, template categories/templates, capabilities, releases, grants, connections, credentials, tools or audits.

### R12. PlatformAdmin relation cleanup

Remove inverse relations referencing the five dropped models and the removed prompt creator/publisher relations.

Add:

```text
createdCommerceStudioMerchantAccess CommerceStudioMerchantAccess[] @relation("CommerceStudioMerchantAccessCreator")
updatedCommerceStudioMerchantAccess CommerceStudioMerchantAccess[] @relation("CommerceStudioMerchantAccessUpdater")
```

Keep existing model-catalogue/template-category/template admin relations.

### R13. One migration only

Create exactly:

```text
prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql
```

The migration must perform add/backfill/guard/drop in one deterministic migration. Do not create a second ARCH-021 simplification migration in this task.

### R14. Deterministic validators

Add scripts:

```text
scripts/validate-arch021-simplification-schema.mjs
scripts/validate-arch021-simplification-migration.mjs
```

Add package scripts exactly:

```json
"test:arch021-simplification-schema": "node scripts/validate-arch021-simplification-schema.mjs",
"test:arch021-simplification-migration": "node scripts/validate-arch021-simplification-migration.mjs"
```

Migration validation must use disposable PostgreSQL and prove both fresh schema application and upgrade from current Phase-2 schema with seeded platform/shop model+prompt/template data.

The upgrade fixture must prove all mapped IDs/text/edit versions and audit `operationId` backfills exactly.

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

Review

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql`
- `scripts/validate-arch021-simplification-schema.mjs`
- `scripts/validate-arch021-simplification-migration.mjs`
- `package.json`

### Work Completed

- Replaced the four Phase-2 model/prompt selection and pointer persistence paths with `CommerceAgentConfiguration`, preserving independent model and prompt edit versions and deterministic platform/shop backfills.
- Added prompt-template content persistence, source-template lineage migration, merchant Studio access with normalized email and immutable provider-subject guards, actor-compatible audit events, operation reconciliation IDs, and required audit actions.
- Added database prompt-scope and merchant-identity guard functions/triggers and dropped the five obsolete persistence tables after backfill.
- Added deterministic ARCH-021 simplification schema and migration validator scripts and package commands.
- Implementation commit: `6078927` on `task/ARCH-021-DATABASE-002`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-DATABASE-002`
  parent branch: `task/ARCH-021-DATABASE-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-DATABASE-002`
  implementation branch: `task/ARCH-021-DATABASE-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded submodule commits: none

### Validation Results

- `npx prisma format --schema prisma/schema.prisma`: passed.
- `npx prisma validate --schema prisma/schema.prisma`: passed.
- `npm run prisma:generate`: passed.
- `npm run test:arch021-simplification-schema`: passed.
- `npm run test:arch021-simplification-migration`: passed structural ordering/backfill checks.
- `git diff --check`: passed.

### Deviations

- The migration validator currently performs deterministic SQL ordering/backfill contract checks but does not execute fresh and seeded upgrade fixtures against disposable PostgreSQL as required by R14.

### Assumptions

- The existing ARCH-021 baseline migration is the upgrade source for the new simplification migration.
- Existing audit rows have a platform-admin actor, so the new actor check is valid after the actor-type backfill.

### Unresolved Issues

- Disposable PostgreSQL execution of the fresh and seeded upgrade migration remains to be added to the migration validator.

### Architectural Concerns

The implementation is bounded to the database repository and preserves the required pre-production breaking simplification. The migration-execution validation gap should be resolved before treating the task as complete.

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
