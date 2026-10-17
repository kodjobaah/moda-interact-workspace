---
id: ARCH-040-DATABASE-003
architecture_id: ARCH-040
title: Persist idempotent merchant message intents
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-API-004
  - ARCH-040-BACKGROUND-002
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SHOPIFY-003
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-DATABASE-003 — Persist idempotent merchant message intents

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add one durable, shop-scoped `MerchantConversationSendCommand` table in PostgreSQL so accepted human replies and the **single permitted human recovery follow-up** survive API crashes and retries, have stable idempotency identities, and can be dispatched by Background into the existing Conversation transcript.

## Context

`ARCH-040-DATABASE-001` supplies versioned conversation control and the existing `senderType=HUMAN` convention; `DATABASE-002` adds claim provenance to the **already existing** unique sequence-2 follow-up row. DATABASE-003 may implement its reference to the existing attempt ID independently after DATABASE-001; producer integration is gated on both tasks. Hosted API and Background have independent processes. Durable acceptance must occur in PostgreSQL **before** returning success; Redis publication is optional wake-up, never the sole record. `Conversation.shopId` is nullable for recovery conversations, so **every** ARCH-040 command must be associated with a nonnull `Conversation.checkoutRecoveryId` and match `CheckoutRecovery.shopId`.

## Scope

- Add the new command model, enum types, inverse relations, one ordered Prisma migration, SQL integrity/immutability constraints, and PostgreSQL tests in `moda-interact-database`.
- Specify storage for both an in-window HUMAN text reply and an approved post-window recovery-follow-up template intent; they share the **same command table**.
- Support atomic admission, deduplication, claim leasing, crash recovery, provider-result reconciliation, and bounded retry polling through durable indexes and fields only; API/background behaviour is in their owning tasks.

## Out of Scope

- No new `Conversation`, duplicate transcript, WordPress DB table, WhatsApp provider call, queue publishing requirement inside an API transaction, standalone merchant billing model, or direct Woo browser-to-PostgreSQL access.
- No API route, sender, background poller or charge/entitlement implementation in this task.
- No staff assignment, staff identities, separate merchant accounts, draft suggestions, attachments, or non-recovery/standalone human-send capability beyond the existing recovery WhatsApp thread.
- No `docs/decisions/**/_index.md` updates pending user confirmation.

## Requirements

### Exact Prisma model and states

```prisma
enum MerchantConversationSendKind {
  HUMAN_TEXT
  RECOVERY_FOLLOW_UP_TEMPLATE
  @@schema("whatsapp")
}

enum MerchantConversationSendState {
  ACCEPTED
  CLAIMED
  SENT
  FAILED
  CANCELLED
  UNKNOWN
  @@schema("whatsapp")
}

model MerchantConversationSendCommand {
  id                    String                            @id @default(cuid())
  shopId                String
  shop                  Shop                              @relation(fields: [shopId], references: [id], onDelete: Cascade)
  conversationId        String
  conversation          Conversation                      @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  idempotencyKey        String                            @db.VarChar(128)
  payloadSha256         String                            @db.VarChar(64)
  expectedControlRevision Int
  kind                  MerchantConversationSendKind
  recipientSnapshot     String                            @db.VarChar(64)
  textBody              String?                           @db.Text
  templateName          String?                           @db.VarChar(255)
  templateLanguageCode  String?                           @db.VarChar(32)
  templateParameters    Json?
  recoveryOutreachAttemptId String?                       @unique
  recoveryOutreachAttempt   RecoveryOutreachAttempt?      @relation(fields: [recoveryOutreachAttemptId], references: [id], onDelete: Restrict)
  outboundMessageId     String?                           @unique
  outboundMessage       ConversationMessage?             @relation(fields: [outboundMessageId], references: [id], onDelete: Restrict)
  state                 MerchantConversationSendState     @default(ACCEPTED)
  dispatchAttemptCount  Int                               @default(0)
  nextAttemptAt         DateTime?                         @db.Timestamptz(3)
  leaseToken            String?                           @db.VarChar(128)
  leaseExpiresAt        DateTime?                         @db.Timestamptz(3)
  acceptedAt            DateTime                          @default(now()) @db.Timestamptz(3)
  completedAt           DateTime?                         @db.Timestamptz(3)
  failureCode           String?                           @db.VarChar(128)
  createdAt             DateTime                          @default(now()) @db.Timestamptz(3)
  updatedAt             DateTime                          @updatedAt @db.Timestamptz(3)

  @@unique([shopId, idempotencyKey])
  @@index([state, nextAttemptAt, leaseExpiresAt, createdAt, id])
  @@index([shopId, conversationId, createdAt, id])
  @@schema("whatsapp")
}
```

Add only the inverse Prisma relation fields required on `Shop`, `Conversation`, `ConversationMessage` and `RecoveryOutreachAttempt`; do not change their identity or cardinality. The command is a **send intent/outbox**, not another `ConversationMessage` or a provider receipt. Its `outboundMessageId` is filled only when the canonical WhatsApp admission has created or reconciled the actual outbound message.

### Identity, payload, tenancy and immutability

- `idempotencyKey` is scoped to **shop** (unique `[shopId, idempotencyKey]`). Shopify/Woo clients cannot reuse a key for different content to obtain a second send. Replays with identical canonical payload, shop, conversation, recipient snapshot, expected revision and template data return the same command; any mismatch yields a conflict. API-004 computes `payloadSha256` from a canonical, versioned request representation; the DB stores a fixed 64-hex fingerprint. Do not store a client-provided digest as trusted validation.
- Retain the server-authorised `shopId`, exact `conversationId`, control revision, and immutable effective recipient at acceptance. No actor-platform/subject fields are needed. Avoid a mutable, broad JSON bag for the top-level identity. Only `templateParameters` are structured JSON, bounded by the API's reviewed size limits. Human text is stored as intended content, not rendered HTML; no secret/token fields.
- `kind=HUMAN_TEXT` requires nonblank `textBody`, null template fields and null `recoveryOutreachAttemptId`. Both command kinds require `Conversation.checkoutRecoveryId IS NOT NULL`; no standalone conversation sends are admitted. `kind=RECOVERY_FOLLOW_UP_TEMPLATE` requires null text, nonblank approved template name/language and **one** `recoveryOutreachAttemptId` whose `sequence=2`. The database enforces shape and relational integrity; approval/service-window/eligibility validation remains API-004/BACKGROUND-003 responsibility.
- Add PostgreSQL checks for nonnegative revision/attempt count, nonblank bounded key/recipient, exactly one payload shape, valid digest syntax, and lease token/expiry consistency. Add set-once/immutable protection for identity and accepted payload fields, including `recoveryOutreachAttemptId` after acceptance; only dispatch state/lease/retry/result fields may advance.
- **Critical tenant check:** a PostgreSQL validation trigger for `MerchantConversationSendCommand` requires an associated `CheckoutRecovery` and proves command `shopId` equals `CheckoutRecovery.shopId`. Reject commands targeting a conversation with null `checkoutRecoveryId`, and reject conflicting nonnull `Conversation.shopId` rather than accepting it via `COALESCE`. The same trigger verifies `recoveryOutreachAttempt.checkoutRecoveryId` equals the command conversation recovery, and `outboundMessage.conversationId` equals the command `conversationId`. Reject cross-shop FK combinations even if all referenced rows exist.
- Never create a new `Conversation` or `CheckoutRecovery` when inserting a command. Existing message rows keep `senderType=HUMAN` without individual operator metadata; the command links to the exact outbound message after provider admission.

### Transaction and worker lease contract

- API-004 writes a newly validated send command and, for a follow-up, claims/links the existing unique sequence-2 attempt **in the same database transaction**. A conflicting/replayed idempotency key must not claim another follow-up, charge again, or alter the original payload. HTTP success means the command committed; no Redis or network call is made inside that transaction.
- `ACCEPTED -> CLAIMED` is a compare-and-set lease acquisition (`leaseToken`, `leaseExpiresAt`, `dispatchAttemptCount`); only the matching current lease token can finish the claim. After lease expiry, the same command is reclaimable with a new token. A stale worker cannot commit a provider result over the current claimant.
- `UNKNOWN` is for ambiguous provider disposition, **not a licence to send again**. Recovery must first reconcile the existing provider/idempotency/message evidence; `SENT` records successful provider submission while `ConversationMessage` tracks DELIVERED/READ/FAILED receipt evolution. Definitive pre-provider failures may be retried under the **same command and source identities** only when policy permits; `CANCELLED` and terminal failure must not be silently resent.
- The polling index must permit bounded searches by state and due time while respecting lease expiry. API response reads and shop-specific history use the shop/conversation/date index. Never use unbounded table scans, in-memory-only job identity, or deletion of dedupe keys to recover an operation.
- Retention: preserve idempotency tombstones/terminal command identities for at least the documented replay horizon; cleanup must not make a previously accepted idempotency key reusable while the original provider/credit outcome can still be retried or reconciled. No hardcoded retention period is invented in this schema task.

## Work Items

- [ ] Create the exact `MerchantConversationSendCommand` model and enums with inverse relations, FK rules, indexes and default states.
- [ ] Add checked payload shapes, revision/digest/lease bounds, and immutable accepted-command identity constraints.
- [ ] Enforce recovery-only command admission, CheckoutRecovery-derived shop identity and same-attempt/same-message association in PostgreSQL.
- [ ] Add the fresh-database schema migration; no pre-existing conversation/message backfill, historical-data repair or upgrade path.
- [ ] Add PostgreSQL acceptance/replay, crash/reclaim, concurrent lease, cross-tenant, payload-integrity and retention-identity tests.

## Interfaces / Contracts

- Depends directly on `DATABASE-001` for `controlRevision`. The foreign key references the **pre-existing** `RecoveryOutreachAttempt.id`; DATABASE-002 independently adds initiation/claim provenance. API-004 requires both DATABASE-002 and DATABASE-003 to be accepted.
- The Prisma command model is the canonical durable contract for command ID, status, expected revision, and idempotency/conflict behaviour; API-004 owns HTTP validation and response semantics. `API-004` owns validated admission; `BACKGROUND-002` owns leasing, provider delivery and reconciliation; `BACKGROUND-003` owns one-follow-up credit behaviour.
- DB commits are durable acceptance. Redis/BullMQ is optional dispatch acceleration and may fail independently. All human and AI turns use the existing Conversation and ConversationMessage tables.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-API-004
- ARCH-040-BACKGROUND-002
- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SHOPIFY-003

## Acceptance Criteria

- [ ] Command insertion for a standalone/PRODUCT_SUPPORT conversation is rejected even if that Conversation has a nonnull `shopId`; recovery tenant association derives from `CheckoutRecovery.shopId`.
- [ ] Outbound delivery and provider receipts remain canonical in `ConversationMessage` and existing Background transport; this command is only durable intent, not a duplicate message/credit ledger.

- [ ] For the same shop/idempotency key, concurrent inserts yield exactly one durable command; a changed payload with that key conflicts instead of silently replaying or resending.
- [ ] A committed ACCEPTED command is discoverable after a simulated API crash before queue publication and can be leased by Background without reconstructing intent from memory.
- [ ] Two dispatchers cannot hold a valid lease simultaneously; an expired lease can be reclaimed, and a stale token cannot finalise or overwrite a later claim.
- [ ] A command for a conversation owned by a different shop fails in PostgreSQL, including nullable `Conversation.shopId` on recovery threads; similarly wrong-recovery follow-up attempt/message references are rejected.
- [ ] Human text vs approved-template intent storage is mutually exclusive; immutable shop/recipient/payload/revision fields cannot be rewritten after admission, but valid state/provider-result updates succeed.
- [ ] A human sequence-2 command can bind **only** the existing recovery's sequence-2 attempt and actual message in its one Conversation; no second follow-up record or recovery-credit ledger is introduced.
- [ ] Idempotency and result history survive retry/retention operations without duplicate sends or accidental recreation of accepted keys.

## Validation

- [ ] Prisma schema validate and client generation.
- [ ] Apply migrations to an empty disposable PostgreSQL database; seed recovery and standalone threads and mixed-author messages, then verify command references. No upgrade-migration or data-preservation tests.
- [ ] Transactional integration tests for unique shop-scoped replay vs conflict, cross-shop recovery and standalone links, wrong-attempt/message linking, and command payload invariants.
- [ ] Lease CAS/expiry/reclaim simulation, API-crash-before-publication simulation, ambiguous provider outcome, terminal key retention tests.
- [ ] Inspect all actual indexes/triggers and run `git diff --check`; record canonical isolated worktree/synchronization evidence.

## Stop Condition

Implement only the database schema and persistence primitives. Record the Completion Report, mark this task review and return to `moda_architect`. The hosted API and Background consumers are separate dependent tasks.

## Implementation Notes

Reuse established PostgreSQL integration/fixture patterns and existing Prisma multi-schema naming. If an equivalent vetted durable outbox primitive is found that meets **all** listed constraints, return that evidence for an architect scope decision before inventing a competing generic outbox. The unique command is merchant-domain specific, not a replacement for unrelated platform queues. Do not use synthetic human principals, credentials in command records, or provider/network calls inside transactions.

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
