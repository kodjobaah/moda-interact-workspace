---
id: ARCH-040-DATABASE-005
architecture_id: ARCH-040
title: Persist platform-neutral conversation moderation assessments
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-18T02:26:07Z
attempt: 1
depends_on: []
enables:
  - ARCH-040-BACKGROUND-006
  - ARCH-040-API-002
  - ARCH-040-API-004
  - ARCH-040-SHOPIFY-001
  - ARCH-040-ADMIN-001
created: 2026-10-18
updated: 2026-10-18
---

# ARCH-040-DATABASE-005 — Persist platform-neutral conversation moderation assessments

## Architecture

Initiative: `ARCH-040`. Canonical plan: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. This task is materialized on its canonical parent task branch; implementation has not started. `DATABASE-001` and `BACKGROUND-001` are complete in the supplied 2026-10-18 snapshot and must remain unchanged.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-040-DATABASE-005` was invoked for developer execution. Ownership remains logically assigned to `moda_database`; execution and completion modes are now `developer`. The canonical launcher claimed Attempt 1 at `2026-10-18T02:26:07Z` after this parent-branch amendment was published. No implementation changes have been made.

## Objective

Add a durable, idempotent moderation-assessment record for an **existing** WhatsApp customer message, a merchant HUMAN send command, or a prepared AGENT/AUTOMATION outbound message. Support safety decisions and retry/review provenance **without** creating another `Conversation`, command queue, delivery system, credit ledger or platform-specific moderation data.

## Context

`moda-interact-database/prisma/schema.prisma` already contains `whatsapp.Conversation`, `ConversationMessage`, `MerchantConversationSendCommand`, `MessageSenderType`, and `commerce.ShopHumanMessagingRestriction`. HUMAN send intent is persisted before dispatch; customer inbound messages and reserved AGENT responses are persisted as `ConversationMessage`. The existing schema has **no durable semantic moderation assessment**. The October 18 snapshot has no moderation schema; this is new work, not a correction of accepted DATABASE-001.

Moderation is content classification, not WhatsApp provider acknowledgement. A verified CUSTOMER message is persisted and may be suppressed from normal AI handling, but cannot be undone at the Meta ingress. A HUMAN or AI outbound must receive the required decision before the existing final provider-admission fence may authorise its content.

## Scope

- Own the Prisma schema, new scoped migration, relational and SQL integrity constraints, indexes and durable state needed for moderation.
- Keep the schema independent of SHOPIFY/WOOCOMMERCE origin. Tenant identity comes from the existing conversation/recovery and shop, never from a user-supplied platform name.
- Define an independently reviewable PostgreSQL test fixture for content digest deduplication, retries, ownership and concurrent decisions.
- Normal clean development migrations only; no legacy backfill or upgrade rehearsal for this new capability.

## Out of Scope

- No OpenAI HTTP client, model calls, background worker, merchant UI, admin UI, notification or new queue in this database task.
- No edits to accepted DATABASE-001 or BACKGROUND-001 task records, existing provider dispatch/receipt/billing contracts, shop suspension status, merchant-role model, or `ConversationMessage.senderType`.
- No new media blobs, customer-content duplication, staff accounts, per-platform tables, new standalone human messaging, or new `_index.md` files.
- Moderation does not delete or rewrite a CUSTOMER inbound, remove an existing transcript or imply that an ALLOW outcome authorises provider delivery by itself.

## Requirements

### 1. Exact persistence contract (new schema only)

Implement equivalent Prisma declarations using the existing `whatsapp` schema and normal naming/mapping conventions. The following is the **required semantic model**; retain existing relation and schema conventions when adding the corresponding back-relations:

```prisma
enum ConversationModerationSubject {
  CUSTOMER_MESSAGE
  HUMAN_COMMAND
  AGENT_MESSAGE
  AUTOMATION_MESSAGE
  @@schema("whatsapp")
}

enum ConversationModerationDecision {
  PENDING
  CHECKING
  ALLOW
  BLOCK
  REVIEW_REQUIRED
  RETRYABLE_ERROR
  @@schema("whatsapp")
}

model ConversationModerationAssessment {
  id                       String @id @default(cuid())
  shopId                   String
  shop                     Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)
  conversationId           String
  conversation             Conversation @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  subject                  ConversationModerationSubject
  conversationMessageId    String?
  conversationMessage      ConversationMessage? @relation(fields: [conversationMessageId], references: [id], onDelete: Cascade)
  merchantSendCommandId    String?
  merchantSendCommand      MerchantConversationSendCommand? @relation(fields: [merchantSendCommandId], references: [id], onDelete: Cascade)
  contentSha256            String @db.VarChar(64)
  inputKind                String @db.VarChar(32)
  requestedModel           String @db.VarChar(96)
  returnedModel            String? @db.VarChar(96)
  policyVersion            String @db.VarChar(48)
  decision                 ConversationModerationDecision @default(PENDING)
  flagged                  Boolean?
  categories               Json?
  categoryScores           Json?
  reasonCode               String? @db.VarChar(96)
  providerRequestId        String? @db.VarChar(128)
  attemptCount             Int @default(0)
  nextAttemptAt            DateTime? @db.Timestamptz(3)
  leaseToken               String? @db.VarChar(128)
  leaseExpiresAt           DateTime? @db.Timestamptz(3)
  assessedAt               DateTime? @db.Timestamptz(3)
  reviewedAt               DateTime? @db.Timestamptz(3)
  reviewedByPlatformAdminId String?
  reviewedByPlatformAdmin PlatformAdmin? @relation(fields: [reviewedByPlatformAdminId], references: [id], onDelete: Restrict)
  reviewDisposition        String? @db.VarChar(32)
  createdAt                DateTime @default(now()) @db.Timestamptz(3)
  updatedAt                DateTime @updatedAt @db.Timestamptz(3)

  @@unique([conversationMessageId, policyVersion, contentSha256], map: "ConversationModeration_message_content_uq")
  @@unique([merchantSendCommandId, policyVersion, contentSha256], map: "ConversationModeration_command_content_uq")
  @@index([decision, nextAttemptAt, leaseExpiresAt, createdAt, id], map: "ConversationModeration_due_idx")
  @@index([shopId, createdAt, id], map: "ConversationModeration_shop_incidents_idx")
  @@index([conversationId, createdAt, id], map: "ConversationModeration_conversation_idx")
  @@index([reviewedByPlatformAdminId, reviewedAt], map: "ConversationModeration_review_idx")
  @@schema("whatsapp")
}
```

Required back-relations on existing `Shop`, `Conversation`, `ConversationMessage` and `MerchantConversationSendCommand`; require the nullable `PlatformAdmin` relation shown above and its matching back-relation using the established Prisma relation convention. A reviewer must be an existing platform admin; authenticated Admin mutations must verify privileges. **Do not modify existing message or command state enums.** `inputKind` is constrained to `TEXT`, `TRANSCRIPT` or `TEMPLATE_PARAMETERS`; v1 does not send raw audio/image content to OpenAI.

### 2. Mandatory SQL invariants

1. **Exactly one subject FK:** an assessment must reference exactly one of `conversationMessageId` or `merchantSendCommandId`, with a CHECK constraint.
2. **Correct subject pairing:** `HUMAN_COMMAND` requires command FK; `CUSTOMER_MESSAGE`, `AGENT_MESSAGE` and `AUTOMATION_MESSAGE` require message FK. Reject mismatched actor and data source.
3. **Real tenant binding:** `assessment.shopId`, `conversationId` and referenced message/command must resolve to the same shop/recovery. Recovery-linked subjects use `CheckoutRecovery.shopId` because `Conversation.shopId` may be NULL. Preserve supported inbound non-recovery WhatsApp threads by resolving their canonical shop; do not expand HUMAN command admission to standalone conversations. Use a transactional verification/trigger or equivalent proven database enforcement; only trusting callers is insufficient.
4. **Digest integrity:** require a 64-character lowercase hexadecimal SHA-256 of the exact UTF-8 content to classify (or deterministic template-parameter rendering when applicable). Store **no second copy of the text** in this table.
5. **Approval immutability:** an ALLOW for digest A does not approve digest B; implement immutable (or guarded) `subject`, link IDs, `shopId`, `conversationId`, `contentSha256`, `requestedModel` and `policyVersion` after creation. A new content digest/policy version generates a new assessment, not an in-place rewrite of the former approved digest.
6. **Terminal decisions:** `ALLOW`, `BLOCK`, `REVIEW_REQUIRED` are terminal for the automatic classifier on that assessment. `PENDING` -> `CHECKING` -> one terminal decision, or `RETRYABLE_ERROR` -> retry/`CHECKING`. Record `assessedAt`, model and bounded reason atomically. `REVIEW_REQUIRED` must not permit normal automated dispatch; human-admin review metadata is an audit annotation, not a silent send override.
7. **Lease safety:** only the lease holder can complete `CHECKING`; stale holders cannot overwrite a newer attempt. Recover expired leases without duplicate writes or duplicate provider sends. No long DB transaction spans OpenAI network I/O.
8. **Retention:** do not delete dedupe/assessment records while original content, provider dispatch, command, incident or credit remains relevant to reconciliation. Any future retention change requires a separate decision; do not invent a TTL for moderation approvals.
9. **Review identity:** `reviewedAt`, `reviewedByPlatformAdminId` and `reviewDisposition` must change together under an authenticated privileged action. Reviews must not erase the original moderation outcome; reasons are bounded and no raw content is stored in audit columns.

### 3. Read/projection and transaction contracts

- Upsert/reuse an assessment by `(subject-linked ID, policyVersion, contentSha256)`; concurrent identical submissions must converge on **one** record. A duplicate inbound webhook must not produce a second incident.
- Return assessment ID, decision, `reasonCode` and review flag to server-side callers. Merchant APIs must **not** expose raw category scores, provider request IDs, private admin annotations or privileged moderation metadata.
- Provide an indexed shop-scoped incident query for ADMIN-001: `shopId`, subject type, decision, category names, timestamps and review status; no customer text in routine list rows. The privileged Admin UI may link to existing records through authorised views rather than denormalising content.
- A command `CLAIMED` or `DISPATCH_ADMITTED` is not equivalent to moderation ALLOW; allow only when the decision matches the exact effective content and configured policy version. Existing provider fencing remains authoritative for handover/restriction/window/rate/billing.
- Unsupported/transcription-failed inbound media cannot be represented as `ALLOW` by fabricating empty text; BG006 must explicitly withhold it from normal AI context until safe text exists or an approved unsupported-content policy applies.

### 4. Required migration and repository surfaces

- Edit `moda-interact-database/prisma/schema.prisma`, adding declarations, relations and indexes above.
- Add one appropriately timestamped ARCH-040 moderation migration in `moda-interact-database/prisma/migrations/` with FKs, CHECKs and any trigger necessary for enforceable same-shop and immutable-content guarantees. Do **not** edit DATABASE-001's already accepted migration.
- Add focused SQL/PostgreSQL integration checks under the database repository's existing harness. Inspect `package.json` before choosing commands.
- No cross-repository schema duplication: Background consumes the generated Prisma client after normal DB submodule/publication sync. No ARCH-040 Shared package.

## Work Items

- [ ] Add exact moderation enum/model/relation/index contract and one fresh-development migration.
- [ ] Enforce one subject FK, subject pairing, tenant binding, digest validity, immutable identity and bounded review metadata in SQL.
- [ ] Add atomic create/reuse and lease/decision-transition integration checks using the actual Postgres harness.
- [ ] Prove multi-tenant isolation, duplicate-subject convergence, stale-lease rejection, changed-digest non-reuse and consistent review attribution.
- [ ] Check migration against clean development database; record actual commands and results separately from feature acceptance.

## Interfaces / Contracts

Producer/consumer identity: `ConversationModerationAssessment` keyed to existing `ConversationMessage.id` or `MerchantConversationSendCommand.id`, `shopId`, `conversationId`, content digest, model and policy version. Owning repo: `moda-interact-database`. The only runtime consumers in ARCH-040 are the platform-neutral Background service and shop-scoped read projections in Shopify/WooCommerce API and privileged Admin. No new Redis queue/envelope contract.

## Dependencies

None. DATABASE-001 was already accepted and is **not reopened**; this task is an additive schema extension.

## Enables

- ARCH-040-BACKGROUND-006
- ARCH-040-API-002
- ARCH-040-API-004
- ARCH-040-SHOPIFY-001
- ARCH-040-ADMIN-001

## Acceptance Criteria

- [ ] Existing conversation/message/command/attempt/restriction semantics remain intact, with one additional durable moderation assessment model.
- [ ] Identical content and policy on the same subject converge to one assessment; a changed payload cannot reuse an old ALLOW.
- [ ] The database rejects cross-shop, invalid subject-pairing, stale lease or immutable-identity mutations.
- [ ] Pending, checking, allowed, blocked, review-required and retryable states are persistently distinguishable and queryable without storing duplicate raw content.
- [ ] No provider send or credit is produced by database persistence alone.

## Validation

**Developer-owned validation, separate from implementation-task acceptance criteria.** The implementer records available focused checks and known gaps for handoff. Final fresh-PostgreSQL migration/testing and developer sign-off are performed separately by the developer; they are **not** acceptance criteria for this task. Do not represent unrun checks as passed.

Suggested developer checks: Prisma validation and generate; database schema/migration tests on clean PostgreSQL; concurrency/tenant negative tests; `git diff --check`.

## Stop Condition

After completing the bounded schema implementation and functional acceptance criteria, write the Completion Report, move this new task to review through its configured execution path and stop. Do not start BACKGROUND-006 or any other task automatically.

## Implementation Notes

- Use existing database repo versioned migrations and task worktree policy; no destruction of durable production resources is authorised by the development-only scope.
- Any missing persistence invariant required for the specified design must be returned to `moda_architect`, not silently implemented as service-only best-effort checks.
- Moderator input categories/model are **not** database enums: persist bounded vendor category keys and scores as structured JSON to accommodate model evolution; policy interpretation belongs to BG006.
- Use existing shared structured logging only at service boundaries; do not log raw content, customer phone or credentials.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-18T02:26:07Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; developer validation is separate.

### Deviations

None.

### Assumptions

New moderation only; no historical backfill.

### Unresolved Issues

None at task definition.

### Architectural Concerns

None at task definition.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
