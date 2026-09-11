---
id: ARCH-007-DATABASE-006
architecture_id: ARCH-007
title: Add durable conversation-turn settling and processing state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 39
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-DATABASE-005
enables:
  - ARCH-007-BACKGROUND-010
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-DATABASE-006: Add durable conversation-turn settling and processing state

## Purpose

Raw WhatsApp messages are not the same as one logical customer turn.

The existing Conversation already has:
```text
inboundVersion
lastProcessedVersion
lastInboundAt
lastMessageAt
```

Add only the minimum state needed to:
- remember when the current unprocessed burst started;
- prevent two CommerceAgent processors running concurrently for one conversation;
- recover a stale processor lease.

## Exact Conversation fields

Add:

```prisma
pendingTurnStartedAt     DateTime?
processingInboundVersion Int?
processingStartedAt      DateTime?
```

Add index:

```prisma
@@index([processingStartedAt])
```

Do not add a new ConversationTurn table.

Do not remove/change:
```text
inboundVersion
lastProcessedVersion
lastInboundAt
```

## Semantics

`pendingTurnStartedAt`:
- null when no unprocessed customer turn exists;
- set when the first inbound message arrives while `inboundVersion == lastProcessedVersion`;
- remains unchanged while additional fragments arrive before that turn is processed;
- cleared only when the current latest inbound version has been successfully terminally handled.

`processingInboundVersion` + `processingStartedAt`:
- identify one claimed conversation processor;
- null outside processing;
- may be replaced only after the Background-defined stale lease timeout.

No customer content is stored in these fields.

## Tests/migration

Generate normal migration/artifacts.

Focused schema tests prove nullable fields/index exist and existing Conversation rows remain valid.

Do not implement timers, BullMQ jobs, or agent behavior here.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-DATABASE-006` branch and the mirrored parent-workspace `task/ARCH-007-DATABASE-006` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 1)

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260908103000_add_conversation_turn_coalescing_state/migration.sql`
- `moda-interact-database/scripts/validate-recovery-credit-pack-schema.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`

### Work Completed
- Added nullable `pendingTurnStartedAt`, `processingInboundVersion`, and `processingStartedAt` fields to `Conversation`.
- Added the required `processingStartedAt` index and additive Prisma migration.
- Added deterministic focused assertions covering field/index presence, additive migration behavior, and preservation of existing rows.
- Regenerated the Prisma client and ERD artifacts.

### Validation Results
- `npm run format`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run erd`: passed.
- `npm run test:recovery-credit-packs`: passed, including DATABASE-006 assertions.
- `git diff --check`: passed.

### Deviations
- `prisma migrate dev` could not generate against the inherited remote Render `DATABASE_URL` because an applied DATABASE-005 migration differs from the working tree and Prisma requested a destructive reset. No reset occurred; the equivalent additive migration was authored manually and validated deterministically.

### Assumptions
- Existing Conversation rows remain valid because all three new fields are nullable and the migration performs no destructive alteration.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The DATABASE-006 implementation matches the exact durable turn-coalescing state contract.

Architect comparison against the accepted DATABASE-005 schema verified that the ONLY Prisma schema changes are:

```prisma
pendingTurnStartedAt     DateTime?
processingInboundVersion Int?
processingStartedAt      DateTime?

@@index([processingStartedAt])
```

The existing fields remain unchanged:

```text
inboundVersion
lastProcessedVersion
lastInboundAt
lastMessageAt
```

No `ConversationTurn` table or adjacent billing/conversation redesign was introduced.

The submitted migration is strictly additive:

```sql
ALTER TABLE "whatsapp"."Conversation"
ADD COLUMN "pendingTurnStartedAt" TIMESTAMP(3),
ADD COLUMN "processingInboundVersion" INTEGER,
ADD COLUMN "processingStartedAt" TIMESTAMP(3);

CREATE INDEX "Conversation_processingStartedAt_idx"
ON "whatsapp"."Conversation"("processingStartedAt");
```

Because all three fields are nullable:

- existing Conversation rows remain valid;
- no data backfill is required;
- no destructive table/column operation is present;
- the migration supplies exactly the persistence required by BACKGROUND-010's 3-second quiet / 10-second maximum settle / 120-second processing-lease algorithm.

The generated ERD contains all three new fields.

The focused deterministic validator asserts:

- all three Conversation fields;
- the processing-start index;
- the additive migration columns/index;
- absence of `DROP TABLE` / `DROP COLUMN`.

The existing DATABASE-004 standalone Conversation ownership/scope state and DATABASE-005 recovery-credit persistence remain unchanged.

### Migration-generation deviation

`prisma migrate dev` could not run to completion against the inherited remote `DATABASE_URL` because that database reports migration drift: its already-applied DATABASE-005 migration differs from the architect-accepted local DATABASE-005 migration, and Prisma requested a destructive reset.

The repository agent correctly refused the reset.

This does NOT invalidate DATABASE-006 because:

1. the accepted DATABASE-005 → DATABASE-006 Prisma schema delta was independently compared and contains only the required fields/index;
2. the manually authored migration is the direct additive SQL representation of that exact delta;
3. deterministic schema/migration assertions pass;
4. no migration was applied to the remote database during this task.

The migration remains unapplied.

### Operational migration-drift warning

The inherited remote database MUST be reconciled before attempting DATABASE-006 deployment there.

The drift specifically means an environment has an applied DATABASE-005 migration whose recorded/applied content differs from the accepted local DATABASE-005 migration.

Do not run a destructive reset against a non-disposable environment.

For a disposable test database, rebuilding from the accepted migration chain is the preferred clean reconciliation.

For a non-disposable environment, first inspect the actually applied DATABASE-005 schema/constraint and reconcile it explicitly before running later migrations.

This operational environment drift is separate from DATABASE-006 implementation acceptance.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260908103000_add_conversation_turn_coalescing_state/migration.sql`
- `moda-interact-database/scripts/validate-recovery-credit-pack-schema.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `docs/decisions/database/ARCH-007/DATABASE-006-conversation-turn-coalescing-state.md`

### Validation Reviewed

Repository-agent Completion Report records:

- `npm run format`: passed;
- Prisma validation: passed;
- Prisma client generation: passed;
- ERD generation: passed;
- focused deterministic schema/migration assertions: passed;
- `git diff --check`: passed.

Architect independently ran:

```text
node scripts/validate-recovery-credit-pack-schema.mjs
```

and it passed.

Architect independently compared the accepted DATABASE-005 Prisma schema with the submitted DATABASE-006 schema and verified that only the three nullable fields plus one index were added.

The architect did not run `prisma migrate dev` against the inherited remote database because the repository agent had already demonstrated that doing so requests a destructive reset due to pre-existing migration drift.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-010` is now Ready because both of its dependencies are architect-accepted Complete:

```text
ARCH-007-DATABASE-006 Complete
ARCH-007-BACKGROUND-004 Complete
```

`ARCH-007-BACKGROUND-011` remains Pending until BACKGROUND-010 is architect-accepted Complete.

`ARCH-007-SYSTEM-TEST-005` remains Pending and terminal/manual-gated.

No migration deployment and no system-test execution is authorised by this acceptance.
