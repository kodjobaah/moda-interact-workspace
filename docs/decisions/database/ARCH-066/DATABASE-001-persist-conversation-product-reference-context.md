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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
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
- [x] Fresh migration and upgrade with existing conversations succeed; old conversations have no new row and remain valid.
- [x] FK/cascade/check/unique/index tests pass; rollback guidance is drop new table after rolling services back, no unrelated reset.
- [x] Generate Prisma client and ERD; do not manually edit generated clients. Record migration hash and database submodule commit for consumers. No Render database mutation in this definition task.

## Execution boundary
Definition only. Do not claim or implement until explicit dependency tasks are Complete. Use the canonical launcher-resolved parent and implementation task worktrees; execution_mode and completion_mode are developer. Do not change unrelated work or another repository. Record exact Shared package version/integrity, database migration and provider schema artifact used. No production customer messages, Meta registrations or live mutations are authorized by this task.

## Completion Report
### Status
Complete — Accepted and explicitly developer-completed — Attempt 1.
### Files Changed
- prisma/schema.prisma: exact CommerceConversationProductContext model and two inverse relations.
- prisma/migrations/20261108173000_arch066_conversation_product_context/migration.sql.
- scripts/test-arch066-product-context-postgres.mjs and package.json focused command registration.
- docs/generated/prisma-erd.puml: new generator-produced entity and links only.
### Work Completed
Added one whatsapp reference-cache table with Conversation primary/FK one-to-one and cross-schema commerce.Shop FK, both cascading. Defaults/version/source/revision/storage checks and exact shopId/expiry index follow normative SQL. JSON holds entire Shared context; no SQL JSON schema/tenant equality/lock implementation. No extra columns/tables/enums, backfill, conversation deletion, seed or service code.
### Validation Results
- `npm ci --ignore-scripts`: PASS locked install; 9 existing audit findings (4 moderate,5 high), no dependency changes/remediation.
- `npm run prisma:validate`: PASS Prisma 6.19.3.
- `npm run prisma:generate`: PASS client generation; no generated client committed.
- `npm run erd:puml`: PASS; scoped generated entity/relations retained, unrelated stale-diagram catch-up excluded.
- `prisma migrate diff --from-schema-datamodel <accepted baseline schema> --to-schema-datamodel prisma/schema.prisma --script`: PASS DDL comparison: exact table/defaults/types/index/FK names/cross-schema cascades. Four specified SQL-only checks appended.
- `npm run test:arch066-product-context:postgres` (executed via exact canonical bootstrap-resolved Node): PASS fresh and upgrade on invocation-owned pgvector/pgvector:pg17 container, network none. Full predecessor migration history replayed in each database. Upgrade seeded existing real Shop/Conversation rows before target; JSON row snapshots equal afterward, old Conversation valid/no cache backfill. Both cases verify valid full context insertion, defaults1/1/source0, duplicate conversation PK rejection, absent Conversation/Shop FK rejection, schemaVersion2/revision0/source-1 rejection, oversized distinct-md5 JSON storage rejection, exact ordered shopId/expiresAt index, Conversation deletion cascade and Shop deletion cascade. Old unrelated Conversation survives. Container removed successfully. Initial fixture used unquoted reserved references identifier; corrected fixture only and final rerun passed. Historical chain identifier notices/readiness socket retries did not affect results; no new identifier truncation.
- `git diff --check`: PASS.
### Contract / Artifact Evidence
No Shared npm dependency/import or provider-schema artifact required by this SQL-only task. Normative accepted context identity comes from SHARED-001 source c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7; entire JSON payload and canonical tenant/version equality remain consumer-owned. Historical 5.6.0 receipt is preserved in architecture; future combined consumer release belongs to SHARED-005, not guessed or pinned by Database.
Migration: prisma/migrations/20261108173000_arch066_conversation_product_context/migration.sql
Migration SHA256: 3e99659d71c8e1d5933a95ad933a10bffea03bd25395795cc8de704f27ff686a
Consumer database source commit: b7f58d5a93e41d54b2fd92a5d483aec4c2c5b595 (published task branch).
### Rollout / Rollback
Apply additive migration through normal deploy process before updated Background consumer. No live/Render migration executed. Existing conversations remain valid without cache rows; no backfill required. Roll back updated consumers FIRST; only afterward may an authorized operator drop the new cache table. Do not reset unrelated data, delete conversations or drop cache while updated consumer remains active. Stored rows are disposable references, never grants/evidence.
### Deviations
Authored migration from Prisma-generated DDL comparison plus exact normative checks, tested full history and upgrade in disposable PostgreSQL rather than invoking migrate dev on user's shared local database. Scoped ERD retains actual generator output only for this model. No other scope deviation.
### Assumptions / Unresolved Issues
No unresolved implementation issues. Canonical tenant identity, payload identity/version equality, Shared UTF8 validation, FOR UPDATE/CAS/idempotency and expiry handling belong to Background; database existence FKs deliberately do not pretend to prove nullable Conversation ownership.
### Git / VCS
Task branch: task/ARCH-066-DATABASE-001.
Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-DATABASE-001
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-DATABASE-001
Both branches task/ARCH-066-DATABASE-001; no shared checkout switch/mutation or other task reuse.
Prepared synchronization: both remote task fast-forward not-needed, both origin/main already-current; recursive submodule sync/update passed, no submodules.
Claim ebcf7a7a6908c951ebbf8950a44bbf90c119a1a0 pushed Attempt1.
Implementation b7f58d5a93e41d54b2fd92a5d483aec4c2c5b595 pushed and remote hash verified. Parent report commit follows this edit on same task branch. No gitlink staged, no main merge, no follow-on execution.

## Dependency Reconciliation - 2026-11-08
SHARED-001 accepted Attempt2 explicitly developer-completed; sole explicit dependency satisfied. Ready at unchanged Attempt0, executor/claimed_at null; no claim or execution. Accepted Shared source c3f9f07cfcf9ff60817f89d5c3d2aaca2dddfbf7 published on task/ARCH-066-SHARED-001; separate publication still gated on SHARED-002.

## Deterministic implementation checklist
- [x] Exact Prisma model/backrelations and SQL above; consumer contract D fixes JSON contents, canonical equality, ownership and version-fence responsibility. No extra columns/tables/enums for merchandise or outreach.
- [x] Migration contains only new table/index/constraints/FKs; do not rewrite applied migrations. Generate Prisma client/schema ERD using repository scripts. Verify PostgreSQL namespace whatsapp with cross-schema Shop FK to commerce, not assumed same schema.
- [x] Disposable Postgres checks: second row same conversation fails PK; nonexistent conversation/shop fail FK; deleting Conversation and deleting Shop cascade context; schemaVersion2/revision0/sourceInboundVersion-1 fail; oversized JSON fails storage CHECK; valid old Conversation remains with no context row.
- [x] Record SQL migration filename/SHA256/database commit, schema validate/generate and exact test commands. No Render mutation, no dropping cache before consumer rollback; no application-level SQL lock logic in Database repository.

## Execution Ownership Amendment — 2026-11-08
Developer explicitly requested agent continuation through `/moda-task ARCH-066-DATABASE-001` and authorized synchronization plus task claim/source/review publication. No active claim exists (Ready, Attempt0); canonical implementation worktree absent, so no source edits to checkpoint. Delegate to moda_database through canonical preparation; completion_mode developer retained. Exact schema/constraint scope unchanged; no live migration/main/follow-on.

## Architect Review — Attempt1 (2026-11-08)
### Review Status
Accepted — explicitly developer-completed.
### Review Notes
Inspected actualb7f58d5a93e41d54b2fd92a5d483aec4c2c5b595 migration/schema/fixture and reporte5d6c3cf08b1895faa5edff08434472e867fcb08. Exact one new whatsapp cache model plus prescribed Conversation1:1/commerce.Shop backrelations/cascades, defaults, nonnegative/version checks, storage32KiB and shop-expiry index. No extra entity/evidence/tenant-ownership FK or SQL JSON schema. Existing Conversation rows untouched/no backfill. No correction outstanding.
### Reviewed Files
prisma/schema.prisma;20261108173000_arch066_conversation_product_context/migration.sql; scripts/test-arch066-product-context-postgres.mjs; package.json; scoped generated ERD and Completion Report.
### Validation Reviewed
Schema validate/client/ERD generation and generated DDL comparison passed. Full-history fresh and upgrade disposable pgvector PostgreSQL17 both pass valid context/defaults, PK/FKs, version/revision/source/storage checks, exact index and both cascades. Upgrade compares complete existing Conversation JSON row snapshots before/after target, no new cache rows; unrelated old row survives. Distinct-md5 oversized JSON avoids repeated-data compression. Fixture reserved-column quoting corrected and final rerun passed; container cleanup verified. MigrationSHA2563e99659d71c8e1d5933a95ad933a10bffea03bd25395795cc8de704f27ff686a.
### Architecture Conformance
Exact normative SQL/Prisma scope conforms; full Shared context JSON and canonical tenant/version equality/locks belong to consumer, deliberately not invented at DB layer. Prisma diff-derived migration plus disposable upgrade proof acceptable, no shared/live database mutation. Canonical isolated worktrees/sync/durable claim/publication verified. Rollback correctly requires consumer rollback before optional cache-table drop, no conversation reset. No main/gitlink/service/rollout execution.
### Follow-up
Explicit completion: `/moda_developer_update ARCH-066-DATABASE-001 complete`. Consumers remain gated by actual dependencies/new Shared release as architect contract specifies; no follow-on work automatically starts and no integrated/deployed completion claim.

## Developer Completion Decision — Attempt1
2026-11-08T17:30:56.721744+00:00 — Explicit `/moda_developer_update ARCH-066-DATABASE-001 complete` received. Durable Accepted87065e8ce5a0bf2106adfaa962a0e9f37be316ce and sourceb7f58d5a93e41d54b2fd92a5d483aec4c2c5b595 match clean canonical worktrees/remotes; all required criteria/checklist/validation satisfied. Complete unchanged Attempt1, claim cleared, modes preserved. Background001 remains Pending on Shared005 publication; MCP001 Complete, Shared004 Ready/Shared005 Pending. No newly Ready task from database completion. Concurrent Commerce001 Ready record preserved untouched despite pending Shared005 in snapshot dependencies; owner must reconcile before execution. System Test tasks remain terminal/manual-gated and Pending. No live migration/backfill/main/follow-on execution or integrated completion claim.
