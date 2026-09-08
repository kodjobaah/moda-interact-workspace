---
id: ARCH-006-DATABASE-001
architecture_id: ARCH-006
title: Add core merchant-support thread and message persistence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-006-DATABASE-002
created: 2026-09-05
updated: 2026-09-06T10:30:00Z
---
# ARCH-006-DATABASE-001: Add core merchant-support thread and message persistence

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Create the durable shop-scoped support thread/message domain, including exclusive PlatformAdmin ownership and pending-response boundaries, without yet adding translation-provider work state.

## Context

ARCH-006 uses one support thread per `Shop`. This domain is separate from shopper WhatsApp conversations. All active PlatformAdmins may read a thread; only its durable assigned owner may send an administrative reply. `readAt` is separate from `needsAdminResponse`. Translation/provider lifecycle is deliberately deferred to `ARCH-006-DATABASE-002` so this task has one schema outcome.

## Scope

Modify only `moda-interact-database` schema, migration, indexes, relations and generated ERD/schema artifacts required for the core support domain.

## Out of Scope

- Translation rows, OpenAI Batch records or reconciliation-request tables (`DATABASE-002`).
- Queue contracts or services.
- Admin/Shopify application behavior.
- WhatsApp conversation schema changes.
- Migration-time creation of support threads for existing shops.

## Requirements

Create PostgreSQL schema `support` and architecture-equivalent Prisma types:

```text
MerchantSupportThread
  id
  shopId UNIQUE
  lastMessageAt?
  lastMerchantMessageAt?
  lastAdministrativeMessageAt?
  needsAdminResponse Boolean DEFAULT false
  merchantMessageVersion Int DEFAULT 0
  assignedPlatformAdminId?
  assignedAt?
  createdAt
  updatedAt

MerchantSupportMessageKind
  ADMINISTRATIVE
  SYSTEM
  MERCHANT

MerchantSupportMessageState
  PROCESSING
  AVAILABLE
  FAILED

MerchantSupportMessage
  id
  threadId
  kind
  state
  originalBody Text                    // immutable at service layer
  sourceLanguageTag                    // trusted snapshot, canonical BCP-47
  displayLanguageTag?                  // outbound recipient snapshot
  platformAdminId?
  shopifyUserId?
  systemCode?
  systemVersion?
  sourceKey? UNIQUE when non-null
  availableAt?
  readAt?
  respondsThroughMerchantVersion?
  createdAt
  updatedAt
```

Relations to existing `Shop` and `PlatformAdmin` must follow repository conventions. Do not duplicate staff email/name fields.

Indexes must efficiently support bounded pending/admin-owner queries, including `needsAdminResponse + lastMerchantMessageAt` and `assignedPlatformAdminId`. Defaults must be rolling-safe.

## Work Items

- [x] Inspect current Prisma multi-schema conventions and related `Shop`, `ShopSettings`, `PlatformAdmin` and WhatsApp models.
- [x] Add the `support` schema and core support enums/models/relations.
- [x] Add uniqueness and bounded operational indexes.
- [x] Create migration using repository conventions; no support-thread backfill.
- [x] Regenerate Prisma/ERD artifacts required by the database repo.
- [x] Add/adjust focused schema or migration tests where the repository supports them.

## Interfaces / Contracts

Durable semantics consumed later:

```text
one Shop -> one MerchantSupportThread
one non-null SYSTEM sourceKey -> one MerchantSupportMessage
thread assignment survives logout/process/Redis loss
merchantMessageVersion is monotonically incremented by merchant sends
ADMINISTRATIVE.respondsThroughMerchantVersion is a response-boundary snapshot
```

The database does **not** enforce the 500-grapheme authored-body rule; that is a shared/server validation rule.

## Dependencies

None

## Enables

`ARCH-006-DATABASE-002`

## Acceptance Criteria

- [x] One support thread per Shop is database-enforced.
- [x] Message kinds/states and core fields match the architecture.
- [x] Durable optional PlatformAdmin assignment relation exists.
- [x] Pending-response/version fields have safe defaults.
- [x] `sourceKey` supports idempotent SYSTEM message creation.
- [x] Pending/owner queries have bounded supporting indexes.
- [x] Existing WhatsApp models are unchanged/reused for no ARCH-006 purpose.
- [x] Migration applies cleanly and generated artifacts are current.

## Validation

Run the validation declared by `moda-interact-database/package.json` and this repo's normal Prisma/ERD workflow. At minimum record Prisma format/validate/generate, migration/schema tests where available, typecheck/lint if declared, and `git diff --check`. Do not invent npm scripts.

## Implementation Notes

Luna stop condition: once the core support schema/migration/indexes validate, return for architect review. Do **not** continue into translation tables even if they are an obvious next step.

## Completion Report

### Status

Ready for Review.

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260906101500_add_merchant_support_persistence/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`

### Work Completed

- Added the `support` PostgreSQL schema and core support message enums.
- Added one-to-one Shop support threads with durable PlatformAdmin assignment, pending-response/version state, timestamps, and bounded indexes.
- Added support messages with administrative, system, and merchant kinds/states, source/display language snapshots, idempotent system source keys, response boundaries, and owner relations.
- Added an additive migration without existing-shop thread backfill; regenerated Prisma/ERD artifacts.

### Validation Results

- `npm run format` passed.
- `npm run validate` passed.
- `npm run prisma:generate` passed.
- `npm run erd:puml` passed.
- `npm run erd:png` passed.
- New migration SQL applied successfully inside a local PostgreSQL transaction and was rolled back.
- `git diff --check` passed.

### Deviations

The local database had previously applied migration files that differ from the current working tree, so `prisma migrate dev` refused to proceed without a destructive reset. The additive migration was created explicitly and validated transactionally instead; no migration history was rewritten and no reset was performed.

### Assumptions

The support schema is created by the migration. PostgreSQL permits multiple null values in the unique `sourceKey` index, while non-null SYSTEM keys are unique at the database layer; service validation remains responsible for restricting source keys to SYSTEM messages.

### Unresolved Issues

`prisma migrate dev` could not apply through the drifted local migration history without a reset. The new migration itself passed transactional PostgreSQL execution.

### Architectural Concerns

No architectural concerns identified within DATABASE-001. Translation/provider persistence remains deferred to DATABASE-002 as required.

## Architect Review

### Review Status

Accepted.

### Findings

- Core support persistence matches the ARCH-006 DATABASE-001 boundary: one thread per Shop, durable optional PlatformAdmin ownership, pending-response/version state, message attribution/language snapshots, idempotent non-null SYSTEM `sourceKey`, and bounded operational indexes.
- The migration is additive and does not backfill existing Shops. Translation/provider/reconciliation persistence remains correctly deferred to `ARCH-006-DATABASE-002`.
- The reported local `prisma migrate dev` drift is accepted as an existing development-history condition rather than a defect in this migration. The new migration was validated transactionally without resetting or rewriting migration history.
- Repository-agent self-approval is not the authoritative acceptance step; this section records the independent `moda_architect` review.

### Decision

`ARCH-006-DATABASE-001` is architect-accepted and Complete. `ARCH-006-DATABASE-002` is unblocked and may move to Ready.
