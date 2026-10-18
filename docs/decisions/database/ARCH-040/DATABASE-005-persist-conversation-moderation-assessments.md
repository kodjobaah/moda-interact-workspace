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
claimed_at: 2026-10-18T09:38:44Z
attempt: 2
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

Initiative: `ARCH-040`. Canonical plan: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. This task is materialized on its canonical parent task branch. `DATABASE-001` and `BACKGROUND-001` are complete in the supplied 2026-10-18 snapshot and remain unchanged. Attempt 1 implementation is published as `b7a3b2679483fc96806ee78680f5d19f6869df06` on `task/ARCH-040-DATABASE-005`.

### Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-040-DATABASE-005` was invoked for developer execution. Ownership remains logically assigned to `moda_database`; execution and completion modes are `developer`. The canonical launcher claimed Attempt 1 at `2026-10-18T02:26:07Z`. Attempt 1 implementation was committed and pushed. Developer self-review found one required persistence invariant incomplete: template-parameter content digests are not verified against deterministic rendering in SQL. The review therefore requests changes and returns the task to `ready`; attempt remains 1.

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

- [x] Add exact moderation enum/model/relation/index contract and one fresh-development migration.
- [ ] Enforce one subject FK, subject pairing, tenant binding, digest validity (including deterministic template-parameter rendering), immutable identity and bounded review metadata in SQL. Text/transcript digest checks are enforced; template-parameter digests are currently caller-supplied and unverified.
- [x] Add atomic create/reuse and lease/decision-transition integration checks using the actual Postgres harness.
- [x] Prove multi-tenant isolation, duplicate-subject convergence, stale-lease rejection, changed-digest non-reuse and consistent review attribution for tested text subjects.
- [x] Check migration against clean development database; record actual commands and results separately from feature acceptance.

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

- [x] Existing conversation/message/command/attempt/restriction semantics remain intact, with one additional durable moderation assessment model.
- [ ] Identical content and policy on the same subject converge to one assessment; a changed payload cannot reuse an old ALLOW. The harness proves distinct digest rows for changed text, but does not first make the old assessment ALLOW; template-parameter digests are also not verified by persistence.
- [x] The database rejects cross-shop, invalid subject-pairing, stale lease or immutable-identity mutations.
- [x] Pending, checking, allowed, blocked, review-required and retryable states are persistently distinguishable and queryable without storing duplicate raw content.
- [x] No provider send or credit is produced by database persistence alone.

## Validation

**Developer-owned validation, separate from implementation-task acceptance criteria.** The implementer records available focused checks and known gaps for handoff. Final fresh-PostgreSQL migration/testing and developer sign-off are performed separately by the developer; they are **not** acceptance criteria for this task. Do not represent unrun checks as passed.

Attempt 1 checks run in the canonical implementation worktree:

- `npm run validate` — PASS.
- `npm run prisma:generate` — PASS (Prisma Client 6.19.3).
- `npm run test:arch040-moderation-schema` — PASS.
- `npm run lint` — PASS.
- `npm run test:arch040-moderation:postgres:fresh` — PASS; all 55 migrations applied to the harness's isolated fresh PostgreSQL 17 container, followed by the moderation tenant, subject, dedupe/concurrency, digest, lease/retry, and review checks.
- `git diff --check origin/main...HEAD` — PASS.

These checks do not close the template-parameter digest gap. No broader deployment or production database validation is claimed.

## Stop Condition

After completing the bounded schema implementation and functional acceptance criteria, write the Completion Report, move this new task to review through its configured execution path and stop. Do not start BACKGROUND-006 or any other task automatically.

## Implementation Notes

- Use existing database repo versioned migrations and task worktree policy; no destruction of durable production resources is authorised by the development-only scope.
- Any missing persistence invariant required for the specified design must be returned to `moda_architect`, not silently implemented as service-only best-effort checks.
- Moderator input categories/model are **not** database enums: persist bounded vendor category keys and scores as structured JSON to accommodate model evolution; policy interpretation belongs to BG006.
- Use existing shared structured logging only at service boundaries; do not log raw content, customer phone or credentials.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-18T09:38:44Z. Attempt 1 review history is preserved below.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261018030000_arch040_conversation_moderation_assessments/migration.sql`
- `moda-interact-database/scripts/test-arch040-moderation-postgres.mjs`
- `moda-interact-database/scripts/validate-arch040-moderation-schema.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/scripts/validate-arch043-platform-configuration-schema.mjs` (allows later migrations after the ARCH-043 forward migration so the new ARCH-040 migration can coexist)

### Work Completed

- Added the moderation schema, relations, indexes, SQL subject/tenant checks, text/transcript digest checks, immutable assessment identity, state/lease procedures, review attribution, idempotent creation, and a fresh-PostgreSQL integration harness.
- Published implementation commit `b7a3b2679483fc96806ee78680f5d19f6869df06` to `origin/task/ARCH-040-DATABASE-005`.

### Validation Results

All commands listed under Validation above passed, including the full 55-migration fresh PostgreSQL chain and integration assertions.

### Deviations

The migration verifies SHA-256 against stored effective text for `TEXT` and `TRANSCRIPT`. For `TEMPLATE_PARAMETERS`, the SQL guard accepts the supplied digest without verifying a canonical rendering of the template name, language, and parameters. The migration comment delegates rendering to BG006; this does not satisfy this task's mandatory database digest-integrity requirement and is not accepted as a scope change.

### Assumptions

New moderation only; no historical backfill.

### Unresolved Issues

- Required: define and enforce the deterministic template-parameter rendering/digest contract for HUMAN commands and prepared AGENT/AUTOMATION messages, then add PostgreSQL positive and negative digest tests. Return the persistence invariant to `moda_architect` for resolution as required by the Implementation Notes. Do not start BG006 to compensate for this database gap.

### Architectural Concerns

The task currently requires database-verifiable digest integrity for deterministic template-parameter content, while the implementation leaves that verification to a consumer. The architecture must choose the canonical serialization/rendering boundary or amend the contract before this task can pass review.

## Architect Review

### Review Status

Developer Self-Review - Changes Requested.

### Review Notes

Schema and migration validation passed. Required evidence/invariants remain incomplete: template-parameter digests are not recomputed/validated by SQL, and the changed-content test does not explicitly verify non-reuse after the prior assessment has reached ALLOW. Therefore Acceptance Criterion 2 and Work Item 2 remain unchecked; this task is not accepted and is not complete.

### Reviewed Files

`prisma/schema.prisma`, `prisma/migrations/20261018030000_arch040_conversation_moderation_assessments/migration.sql`, `scripts/test-arch040-moderation-postgres.mjs`, `scripts/validate-arch040-moderation-schema.mjs`, `package.json`, and `scripts/validate-arch043-platform-configuration-schema.mjs` in the published implementation commit.

### Validation Reviewed

Prisma validate/generate, moderation structural validator, ESLint, fresh PostgreSQL migration/integration harness, and implementation branch diff check all passed. The harness does not test invalid template-parameter digests, confirming that this invariant remains unproven and unenforced.

### Architecture Conformance

Partial. The moderation persistence model and tested text/transcript paths conform. Template-parameter digest integrity does not meet the mandatory persistence contract.

### Follow-up

Return the missing invariant to `moda_architect`; keep this task `ready` and do not mark it complete until the persistence contract is enforced and the focused PostgreSQL tests pass.
