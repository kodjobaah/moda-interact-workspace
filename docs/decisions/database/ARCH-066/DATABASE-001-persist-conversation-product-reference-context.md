---
id: ARCH-066-DATABASE-001
architecture_id: ARCH-066
title: Persist tenant-scoped conversation product references
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
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
