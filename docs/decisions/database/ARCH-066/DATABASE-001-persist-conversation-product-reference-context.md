---
id: ARCH-066-DATABASE-001
architecture_id: ARCH-066
title: Persist tenant-scoped conversation product references
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-001"]
enables: ["ARCH-066-BACKGROUND-001"]
created: 2026-11-08
updated: 2026-11-08
---
# Persist tenant-scoped conversation product references

## Objective and read first
Implement only the owned work below. Read `docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md` first: its numbered contract decisions are normative and must not be redesigned by the implementor.

## Touch points
`prisma/schema.prisma`, NEW migration `prisma/migrations/<timestamp>_arch066_conversation_product_context/migration.sql`, affected ERD/schema documentation and schema tests. No tool, UI or service code.

## Exact schema
Decision 6: model CommerceConversationProductContext in whatsapp schema with conversationId String @id FK Conversation.id onDelete Cascade, shopId String FK Shop.id onDelete Cascade, schemaVersion Int @default(1), revision Int @default(1), sourceInboundVersion Int, references Json @db.JsonB, expiresAt DateTime @db.Timestamptz(3), createdAt DateTime @default(now()) @db.Timestamptz(3), updatedAt DateTime @updatedAt @db.Timestamptz(3). Add Conversation optional one-to-one relation and Shop backrelation. Add index (shopId,expiresAt), CHECK schemaVersion=1, revision>=1, sourceInboundVersion>=0 and pg_column_size(references)<=32768. Do not use SQL JSON schema validation; Shared validates payload before writes.
- Migration adds new table only, without backfill or deleting conversations. Ownership invariant: Background resolves canonical tenant from standalone shopId or checkoutRecovery.shopId; SQL service transactions must verify that invariant (specified in Background task). No fake FK to model-returned IDs.
- Row is disposable reference cache, not evidence, inventory, consent or a grant. No tokens, prices, raw tool results or customer text in references. Expired rows are ignored/removed lazily; Conversation cascade handles deletion. No new scheduled cleanup worker.

## Prisma implementation block

Add this model to prisma/schema.prisma and preserve all existing fields on the related models:

```prisma
model CommerceConversationProductContext {
  conversationId       String       @id
  conversation         Conversation @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  shopId               String
  shop                 Shop         @relation(fields: [shopId], references: [id], onDelete: Cascade)
  schemaVersion        Int          @default(1)
  revision             Int          @default(1)
  sourceInboundVersion Int
  references           Json         @db.JsonB
  expiresAt            DateTime     @db.Timestamptz(3)
  createdAt            DateTime     @default(now()) @db.Timestamptz(3)
  updatedAt            DateTime     @updatedAt @db.Timestamptz(3)

  @@index([shopId, expiresAt], map: "CommerceConversationProductContext_shopId_expiresAt_idx")
  @@schema("whatsapp")
}
```

```prisma
// Add inside existing Conversation:
commerceProductContext CommerceConversationProductContext?
// Add inside existing Shop:
commerceProductContexts CommerceConversationProductContext[]
```

Append migration constraints after generated CREATE TABLE:

```sql
ALTER TABLE "whatsapp"."CommerceConversationProductContext"
  ADD CONSTRAINT "CommerceConversationProductContext_schemaVersion_check" CHECK ("schemaVersion" = 1),
  ADD CONSTRAINT "CommerceConversationProductContext_revision_check" CHECK ("revision" >= 1),
  ADD CONSTRAINT "CommerceConversationProductContext_sourceInboundVersion_check" CHECK ("sourceInboundVersion" >= 0),
  ADD CONSTRAINT "CommerceConversationProductContext_references_bytes_check" CHECK (pg_column_size("references") <= 32768);
```

references holds the entire Shared context object, not only its nested array; its shopId/conversationId/schemaVersion must match row columns. Shared serialized UTF8 bound and PostgreSQL storage bound both apply. JSON updatedAt is observation time; row updatedAt is persistence time. Foreign keys prove existence, while canonical Conversation/CheckoutRecovery ownership is checked under the Background transaction lock; do not use nullable Conversation.shopId as a composite FK. No merchandise facts or outreach preview records in this table.

## Acceptance / validation
- [ ] Fresh migration and upgrade with existing conversations succeed; old conversations have no new row and remain valid.
- [ ] FK/cascade/check/unique/index tests pass; rollback guidance is drop new table after rolling services back, no unrelated reset.
- [ ] Generate Prisma client and ERD; do not manually edit generated clients. Record migration hash and database submodule commit for consumers. No Render database mutation in this definition task.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
Status: Not started. Attempt: 0. Implementation commit: none. Validation evidence: none. Remaining work: all unchecked acceptance criteria. Document isolated worktree, package, test and deployment evidence when implemented; do not mark Complete merely from source inspection.

## Dependency Reconciliation - 2026-11-08
SHARED-001 accepted Attempt2 explicitly developer-completed; sole explicit dependency satisfied. Ready at unchanged Attempt0, executor/claimed_at null; no claim or execution. Accepted Shared source c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7 published on task/ARCH-066-SHARED-001; separate publication still gated on SHARED-002.

## Deterministic implementation checklist
- [ ] Exact Prisma model/backrelations and SQL above; consumer contract D fixes JSON contents, canonical equality, ownership and version-fence responsibility. No extra columns/tables/enums for merchandise or outreach.
- [ ] Migration contains only new table/index/constraints/FKs; do not rewrite applied migrations. Generate Prisma client/schema ERD using repository scripts. Verify PostgreSQL namespace whatsapp with cross-schema Shop FK to commerce, not assumed same schema.
- [ ] Disposable Postgres checks: second row same conversation fails PK; nonexistent conversation/shop fail FK; deleting Conversation and deleting Shop cascade context; schemaVersion2/revision0/sourceInboundVersion-1 fail; oversized JSON fails storage CHECK; valid old Conversation remains with no context row.
- [ ] Record SQL migration filename/SHA256/database commit, schema validate/generate and exact test commands. No Render mutation, no dropping cache before consumer rollback; no application-level SQL lock logic in Database repository.

## Execution Ownership Amendment — 2026-11-08
Developer explicitly requested agent continuation through `/moda-task ARCH-066-DATABASE-001` and authorized synchronization plus task claim/source/review publication. No active claim exists (Ready, Attempt0); canonical implementation worktree absent, so no source edits to checkpoint. Delegate to moda_database through canonical preparation; completion_mode developer retained. Exact schema/constraint scope unchanged; no live migration/main/follow-on.
