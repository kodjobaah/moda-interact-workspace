---
id: ARCH-007-DATABASE-004
architecture_id: ARCH-007
title: Add durable standalone WhatsApp conversation ownership and active-scope identity
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-DATABASE-003
enables:
  - ARCH-007-BACKGROUND-004
  - ARCH-007-DATABASE-005
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-DATABASE-004: Add durable standalone WhatsApp conversation ownership and active-scope identity

## Architecture

Canonical architecture:

```text
docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md
```

## Why this task exists

Architect review of `ARCH-007-BACKGROUND-004` found that the accepted ARCH-007 automated-outbound hard cap is explicitly **per conversation**, but the current durable `Conversation` model can only identify recovery-linked conversations through `checkoutRecoveryId`.

Background also sends Moda-originated WhatsApp messages for non-recovery/product/clarification flows. Those flows currently cannot resolve and reuse a durable tenant/customer conversation across inbound turns. Creating a fresh `Conversation` for every outbound attempt resets a per-conversation safety cap; counting all such sends by `shopId` incorrectly turns a per-conversation limit into a merchant-wide lifetime limit.

This task adds the smallest database capability needed for Background to own a stable, expirable standalone conversation lifecycle without inventing a second billing metric.

## Objective

Allow a non-recovery WhatsApp conversation to carry explicit tenant/customer ownership and one unique active standalone scope identity while preserving all existing recovery-conversation behaviour.

## Exact schema changes

Modify only the existing Prisma `Conversation`, `Shop`, and `Customer` relation surfaces required by this task.

### `Conversation`

Add nullable standalone ownership fields:

```prisma
shopId String?
shop   Shop? @relation(
  "StandaloneConversationShop",
  fields: [shopId],
  references: [id],
  onDelete: Cascade
)

customerId String?
customer   Customer? @relation(
  "StandaloneConversationCustomer",
  fields: [customerId],
  references: [id],
  onDelete: Cascade
)

standaloneScopeKey String? @unique @db.VarChar(255)
```

Add indexes:

```prisma
@@index([shopId, customerId, type, outcome])
@@index([customerId, lastMessageAt])
```

Keep the existing:

```prisma
checkoutRecoveryId
checkoutRecovery
@@unique([checkoutRecoveryId])
```

unchanged.

### `Shop`

Add only the inverse relation required by Prisma:

```prisma
standaloneConversations Conversation[] @relation("StandaloneConversationShop")
```

### `Customer`

Add only the inverse relation required by Prisma:

```prisma
standaloneConversations Conversation[] @relation("StandaloneConversationCustomer")
```

Do not rename or repurpose existing recovery relations.

## Database invariants

The database must enforce:

1. `standaloneScopeKey` is unique when non-null.
2. A row with non-null `standaloneScopeKey` must also have non-null `shopId` and `customerId`.
3. A row with non-null `standaloneScopeKey` must have `checkoutRecoveryId IS NULL`.
4. Existing recovery-linked conversations remain valid with `standaloneScopeKey = NULL`.
5. This task does NOT require every historical/non-recovery conversation to gain a scope key.

Prisma cannot express every CHECK invariant directly. It is acceptable for the normal Prisma migration generated for this task to contain the database CHECK constraint. This is migration/schema ownership, not application raw SQL.

Use a named constraint equivalent in meaning to:

```text
standaloneScopeKey IS NULL
OR (
  shopId IS NOT NULL
  AND customerId IS NOT NULL
  AND checkoutRecoveryId IS NULL
)
```

Do not add triggers or stored procedures.

## Standalone scope semantics

`standaloneScopeKey` is an opaque application-computed active-scope identity. The database does not compute timestamps, inactivity windows or business routing.

Background will own lifecycle behaviour after this task:

```text
active standalone conversation
    -> standaloneScopeKey is non-null and unique

conversation expires
    -> outcome becomes EXPIRED
    -> standaloneScopeKey becomes null

new lifecycle for same shop/customer/type
    -> new Conversation may reuse the former scope-key value
```

The nullable unique key is intentional: PostgreSQL permits multiple nulls, while only one active row may hold a given non-null scope identity.

Do not add `COMMERCE_AGENT_TURN`, `INBOUND_AUTOMATED_MESSAGE`, or another UsageMetric in this task.

## Work Items

- [x] Add the exact nullable Conversation ownership/scope fields and named inverse relations.
- [x] Add the two exact indexes.
- [x] Generate the normal Prisma migration for the schema change.
- [x] Add the standalone-scope CHECK invariant to the task migration if Prisma does not generate it.
- [x] Regenerate normal Prisma/database artifacts used by this repository, including the ERD where repository scripts require it.
- [x] Add focused schema/migration validation proving uniqueness and CHECK semantics.
- [x] Run the repository-declared validation required below.
- [x] Complete the task report, set only this task to `review`, and STOP.

## Acceptance Criteria

- [x] `Conversation.standaloneScopeKey` exists, is nullable and unique.
- [x] Standalone scoped conversations can carry explicit `shopId` and `customerId`.
- [x] A non-null scope key cannot exist without shop/customer ownership.
- [x] A non-null scope key cannot coexist with `checkoutRecoveryId`.
- [x] Existing recovery conversation identity/uniqueness remains unchanged.
- [x] Required indexes exist.
- [x] A normal Prisma migration exists.
- [x] No application/runtime raw SQL, trigger or stored procedure is introduced.
- [x] Validation passes.

## Validation

Inspect `moda-interact-database/package.json` before running commands and use only scripts that actually exist.

At minimum run the repository's declared equivalents of:

```text
Prisma format
Prisma validate
migration/schema tests required by this task
typecheck/build/test where declared
git diff --check
```

If a PostgreSQL integration test harness already exists, add a bounded test proving:

```text
same non-null standaloneScopeKey twice -> rejected
standaloneScopeKey + null shop/customer -> rejected
standaloneScopeKey + checkoutRecoveryId -> rejected
multiple rows with standaloneScopeKey null -> allowed
```

Do not invent an infrastructure dependency if the repository has no such test harness; inspect migration SQL deterministically instead.

## Luna deterministic-execution guardrails

- Implement exactly the schema capability above; do not redesign Conversation.
- Do not add an inbound billing metric.
- Do not implement Background routing/lifecycle in the database repository.
- Do not change checkout recovery semantics.
- Do not make `shopId`, `customerId`, or `standaloneScopeKey` globally required for all Conversation rows.
- Do not add a trigger.
- Do not modify another repository.
- Do not begin `ARCH-007-BACKGROUND-004`.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-DATABASE-004` branch and the mirrored parent-workspace `task/ARCH-007-DATABASE-004` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status

Review handoff completed; implementation submitted for architect review.

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260908074037_add_standalone_whatsapp_conversation_scope/migration.sql`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`
- `docs/decisions/database/ARCH-007/DATABASE-004-standalone-whatsapp-conversation-scope.md`

### Work Completed

- Added nullable standalone `shopId` / `customerId` ownership to `Conversation` with the exact named inverse Prisma relations.
- Added nullable unique `standaloneScopeKey`.
- Added the required `[shopId, customerId, type, outcome]` and `[customerId, lastMessageAt]` indexes.
- Preserved existing recovery-linked `checkoutRecoveryId` relation and uniqueness.
- Generated the normal Prisma migration.
- Added named `Conversation_standalone_scope_invariant` CHECK semantics requiring shop/customer ownership and no checkout recovery whenever `standaloneScopeKey` is non-null.
- Regenerated Prisma ERD artifacts.

### Validation Results

Repository-agent handoff reported:

- Prisma formatting/validation: passed.
- Deterministic migration assertions: passed.
- ERD generation/artifact refresh: passed.
- `git diff --check`: passed.
- Migration intentionally remains unapplied.

Architect inspection additionally verified the submitted migration contains the required columns, unique index, both bounded indexes, both foreign keys, the exact CHECK predicates, and no trigger/stored-procedure escape hatch.

The review archive did not contain installed `node_modules`, so the architect did not rerun Prisma CLI validation from the extracted archive.

### Deviations

The submitted ZIP contained stale task handoff metadata (`status: in_progress` and an empty Completion Report) despite the explicit repository-agent handoff stating the task had been returned for review. The architect reconciled that documentation drift during acceptance because the implementation and submitted validation evidence were complete; no no-code Attempt 2 was created.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The submitted schema and migration satisfy the exact DATABASE-004 contract:

1. `Conversation.shopId` and `Conversation.customerId` are nullable and use the required named standalone relations.
2. `Conversation.standaloneScopeKey` is nullable, unique and bounded to `VARCHAR(255)`.
3. Existing `checkoutRecoveryId` relation and `@@unique([checkoutRecoveryId])` remain unchanged.
4. Required indexes exist:
   - `[shopId, customerId, type, outcome]`;
   - `[customerId, lastMessageAt]`.
5. Migration adds both foreign keys with the specified cascading delete semantics.
6. Named CHECK `Conversation_standalone_scope_invariant` enforces:
   - null scope key is allowed;
   - non-null scope key requires non-null shop;
   - non-null scope key requires non-null customer;
   - non-null scope key requires `checkoutRecoveryId IS NULL`.
7. No trigger, stored procedure or application/runtime raw SQL was introduced.
8. Existing historical/recovery Conversation rows remain valid because all new ownership/scope fields are nullable.
9. ERD artifacts include the new standalone ownership/scope fields.

The migration remaining unapplied is acceptable for this implementation task; developer-controlled migration deployment is a separate operational action.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260908074037_add_standalone_whatsapp_conversation_scope/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `docs/decisions/database/ARCH-007/DATABASE-004-standalone-whatsapp-conversation-scope.md`

### Validation Reviewed

- repository-agent reported Prisma format/validate passing;
- deterministic migration assertions reported passing;
- ERD regeneration reported passing;
- `git diff --check` reported passing;
- architect performed static migration/schema contract checks against the submitted archive.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-DATABASE-005` is now Ready because its sole dependency, DATABASE-004, is Complete.

`ARCH-007-BACKGROUND-004` is returned from Blocked to Ready on the SAME task. Its `attempt` remains `1`; the next repository-agent claim becomes Attempt 2 and must implement only the existing bounded correction contract already recorded in its Architect Review.

No system-test task is automatically promoted or run.
