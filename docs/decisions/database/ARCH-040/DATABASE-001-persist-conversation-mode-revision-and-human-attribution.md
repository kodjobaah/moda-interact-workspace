---
id: ARCH-040-DATABASE-001
architecture_id: ARCH-040
title: Persist conversation mode, revision and human attribution
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
  - ARCH-040-SHARED-001
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-BACKGROUND-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-DATABASE-001 — Persist conversation mode, revision and human attribution

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Persist authoritative, versioned `AI`/`HUMAN` control on the **existing** `whatsapp.Conversation`, append immutable takeover/resume evidence, and attribute outbound human messages to a verified merchant staff principal. Do **not** create a new conversation or copy the message transcript.

## Context

Verified schema as of 2026-10-14: `Conversation` is in the `whatsapp` schema, its `shopId` is **nullable** for recovery conversations, and `@@unique([checkoutRecoveryId])` already prevents a second thread for one recovery. `ConversationMessage.senderType` already supports `HUMAN` but has no merchant actor provenance. `CheckoutRecovery.shopId` is authoritative for recovery conversation tenant ownership. No merchant staff table spans Shopify and WooCommerce; record bounded, authenticated external actor identifiers instead of inventing an internal user FK.

## Scope

1. Change `moda-interact-database/prisma/schema.prisma`, add **one** ordered Prisma migration, and add focused PostgreSQL schema/migration tests in the database repository.
2. Add durable control fields, control-history model, staff-principal identifier enum, and human-message author fields described below. Update necessary inverse Prisma relations only.
3. Retain the canonical existing `Conversation`/`ConversationMessage`/`CheckoutRecovery` relationships and one-conversation-per-recovery constraint; this is a fresh-development schema change, not a historical-data preservation project.

## Out of Scope

- No second `Conversation`, `ConversationMessage` history table, merchant-support inbox reuse, or new checkout-recovery generation.
- No API/controller, handover action implementation, Redis lock, CommerceAgent gating, message sending, billing, or Woo/Shopify interface.
- No staff-assignment system, human agent roles, operator profile records, or customer-facing UI.
- No updates to `docs/decisions/**/_index.md` until the user confirms the architecture session is complete.

## Requirements

### Exact Prisma schema contract

Add these *new* declarations; keep existing fields and constraints unchanged:

```prisma
enum ConversationControlMode {
  AI
  HUMAN
  @@schema("whatsapp")
}

enum MerchantConversationActorPlatform {
  SHOPIFY_STAFF
  WOOCOMMERCE_STAFF
  @@schema("whatsapp")
}

// New fields on existing Conversation:
controlMode         ConversationControlMode @default(AI)
controlRevision     Int                     @default(0)
controlChangedAt    DateTime?               @db.Timestamptz(3)
humanTakenOverAt    DateTime?               @db.Timestamptz(3)
controlEvents       ConversationControlEvent[]
// Additional index: @@index([shopId, controlMode, lastMessageAt, id])

model ConversationControlEvent {
  id              String                            @id @default(cuid())
  conversationId  String
  conversation    Conversation                      @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  fromMode        ConversationControlMode
  toMode          ConversationControlMode
  fromRevision    Int
  toRevision      Int
  actorPlatform   MerchantConversationActorPlatform
  actorSubject    String                            @db.VarChar(255)
  occurredAt      DateTime                          @default(now()) @db.Timestamptz(3)

  @@unique([conversationId, toRevision])
  @@index([conversationId, occurredAt, id])
  @@schema("whatsapp")
}

// New nullable fields on existing ConversationMessage:
humanActorPlatform MerchantConversationActorPlatform?
humanActorSubject  String? @db.VarChar(255)
```

- `controlMode=AI`, `controlRevision=0`, and null transition timestamps represent an existing thread that has never been taken over. `controlRevision` must never decrease or reset; `controlChangedAt` updates on **every actual transition**; `humanTakenOverAt` is set on transition to HUMAN and cleared on transition to AI. Audit history retains earlier takeover timestamps and actors. Treat `ConversationControlEvent` as insert-only for normal application roles: protect from UPDATE/direct DELETE (via privileges or triggers) while allowing explicitly authorised parent-record erasure according to retention policy.
- `ConversationControlEvent` represents exactly one real mode transition (`AI -> HUMAN` or `HUMAN -> AI`); `toRevision = fromRevision + 1`, revisions nonnegative, actor subject nonblank/bounded. Repeated no-op requests do not insert an event or increment the revision. Add PostgreSQL `CHECK` constraints for the scalar invariants that Prisma cannot express.
- The hosted API will perform `updateMany`/CAS on `(Conversation.id, controlRevision, controlMode)` and insert the matching `ConversationControlEvent` **inside the same PostgreSQL transaction**. A CAS winner must commit both updates or neither; concurrent stale writers update zero rows. The database task provides the schema and tests to support this, not the API endpoint itself.
- `actorPlatform` is the authenticated *merchant-side* system (`SHOPIFY_STAFF` or `WOOCOMMERCE_STAFF`); `actorSubject` is the stable authenticated staff identifier from that system (not a free-form display name). No `PlatformAdmin` relation; no browser-supplied actor treated as authoritative. A different staff member may take over a currently HUMAN conversation without creating a new thread or an assignment lock; v1 only records changes in control mode.
- For `ConversationMessage`, only `direction=OUTBOUND, senderType=HUMAN` receives a nonnull `humanActorPlatform` and `humanActorSubject`. CUSTOMER/AGENT/AUTOMATION do not fabricate human principals. Add PostgreSQL insert-time completeness/shape enforcement and immutability protection for both human actor columns (ordinary message-status/provider-receipt updates must remain possible). Do not re-use `senderType` to encode the control mode.
- Preserve `Conversation @@unique([checkoutRecoveryId])`. A recovery conversation's effective tenant comes from `CheckoutRecovery.shopId` if its own `Conversation.shopId` is null; standalone conversations use `Conversation.shopId`. Do not make `Conversation.shopId` nonnullable or filter recovery threads only by this nullable field.
- Retain existing message ordering indexes. The additional mode index is for standalone scoped queries; recovery inbox queries must continue to use the `CheckoutRecovery(shopId, ...)` indexes plus the recovery conversation unique relation. Do not add indexes duplicating a unique left-prefix.

### Development-only schema delivery

- **Pre-production, fresh database only.** Add the Prisma schema and the repository's normal schema-creation migration for fresh databases. No upgrade scripts, compatibility adapters, legacy `HUMAN` actor backfill, historical-data preflight, data-preservation rehearsal, or rollback plan are required for ARCH-040.
- Create the two enums, `Conversation` control fields, `ConversationControlEvent`, nullable `ConversationMessage` actor columns, and required SQL checks/indexes/triggers. Validate a clean database built from the repository's standard migrations; existing schema identity and one-conversation cardinality remain the intended model.
- Apply complete attribution rules to newly inserted `HUMAN` outbound messages. No accommodation for pre-ARCH-040 human-message rows is required. Use fresh representative fixtures for CUSTOMER, AGENT, AUTOMATION and HUMAN.
- Do not introduce a second thread or a parallel message history as a shortcut to schema changes.

## Work Items

- [ ] Add the exact control mode/actor enums, `Conversation` control fields, and tenant-appropriate index.
- [ ] Add `ConversationControlEvent` with conversation FK, unique revision, bounds/checks and ordered retrieval index.
- [ ] Add immutable, optional human actor fields to existing `ConversationMessage` plus safe check/trigger enforcement for new human outbound writes.
- [ ] Add the schema-creation migration for a fresh disposable development database; no historical preflight, backfill, rollback or upgrade coverage.
- [ ] Add focused PostgreSQL integration fixtures for recovery (nullable conversation shopId) and standalone conversations.

## Interfaces / Contracts

- Persisted names/types above are the baseline for `ARCH-040-SHARED-001`, `API-002`, `API-003`, and `BACKGROUND-001`. They must consume the schema via a published contract where applicable, not independently redefine the wire semantics.
- A mode transition reads `Conversation.id`, `controlMode`, `controlRevision`, and writes the matching `ConversationControlEvent` within one transaction. Tenant authorisation is owned by the hosted API; this schema **does not** make `Conversation.shopId` a reliable recovery tenant ID.
- Inbound CUSTOMER messages remain on the same `Conversation.id`; human sender provenance lives on the individual outbound `ConversationMessage`, not on `Conversation` or `CheckoutRecovery`.

## Dependencies

None.

## Enables

- ARCH-040-DATABASE-002
- ARCH-040-DATABASE-003
- ARCH-040-SHARED-001
- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-BACKGROUND-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] In fresh PostgreSQL fixtures, each recovery retains **exactly one** `Conversation.id` through initial outreach, follow-up and human/AI replies; default control mode is AI/revision 0. The schema does not create extra conversations.
- [ ] Two concurrent transitions from revision N can commit at most one N -> N+1 event and one mode update; losing CAS returns zero updated rows; no gaps or duplicate events.
- [ ] `AI -> HUMAN -> AI -> HUMAN` produces revisions 1, 2, 3 and three immutable, actor-attributed audit records; the last takeover timestamp reflects revision 3.
- [ ] Real no-op takeover/resume does not increment revision or append another event.
- [ ] Outbound HUMAN message is linked to one authenticated merchant actor; missing/blank human attribution is rejected for new writes; actor columns cannot be overwritten after insert; non-human messages and delivery-status updates still work.
- [ ] Recovery tenant ownership remains resolvable through `CheckoutRecovery.shopId` even when `Conversation.shopId IS NULL`; a shop cannot gain access by relying on a nullable conversation field.
- [ ] In a fresh deployment, `@@unique([checkoutRecoveryId])`, message ordering/indexes and recovery/provider message relationships remain valid; no second conversation is created by a follow-up.

## Validation

- [ ] Run the repository's actual Prisma validate and generate commands.
- [ ] Apply migrations to an empty disposable PostgreSQL instance; seed recovery, standalone and mixed-author message fixtures and verify defaults, FK associations and indexes. No upgrade-migration rehearsal.
- [ ] PostgreSQL negative constraint and concurrent CAS+audit transaction tests including failed transaction rollback and nonhuman message updates.
- [ ] Compare Prisma schema to applied SQL constraints/indexes and run `git diff --check`.
- [ ] Record canonical task-worktree, launcher synchronization and submodule evidence in Completion Report.

## Stop Condition

After this task’s Work Items, Acceptance Criteria and required Validation are complete, set status to review, record the Completion Report and return to `moda_architect`. Do not begin DATABASE-002/003 or another task.

## Implementation Notes

The owning agent is `moda_database`, repository `moda-interact-database`. Use the launcher-prepared isolated task worktree and inspect the actual `package.json` before selecting commands. This task **does not** implement the provider-send fence: `BACKGROUND-001` uses `controlRevision` at final outbound admission. Do not store full customer content or tokens in control-event audit fields; use bounded actor identifiers only.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
