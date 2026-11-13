---
id: ARCH-076-DATABASE-001
architecture_id: ARCH-076
title: Persist shop sender routes, checkout members and reply clarification
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-076-ADMIN-001", "ARCH-076-BACKGROUND-001"]
created: 2026-11-13
updated: 2026-11-13
---

# Persist shop sender routes, checkout members and reply clarification

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Persist one active sender route per shop and customer, any number of active checkout conversations as its members, and durable handling of ambiguous replies. Preserve original sender proof on every admitted outbound.

## Context

Preserved from original local commit `59705bb589342f31054e6c1fd011dacf9d495ae6` under root-authorized ARCH-076 collision correction. Defined portable design only; Pending/unclaimed until current-main compatibility review and explicit architect promotion. No runtime implementation or launch is authorized by preservation.

The merchant's platform and shop decide which checkouts can coexist. Distinct recoveries admitted by existing merchant/platform rules each retain their own recovery, attempt, credit and conversation. One shop and customer share a single Moda number across those recoveries. A different shop serving the same phone must use a different number while the first route has any active member. Closing one member leaves all others intact. The last member closing releases the route for reuse without a cooldown. Within this application each environment has a separate database.

## Scope

Implement the Prisma shape, one forward migration, explicit SQL constraints/indexes, schema checks, disposable PostgreSQL fresh/upgrade/concurrency tests, package scripts and corresponding ERD relationships described below.

## Out of Scope

Do not mutate the API or worker, administer Meta assets or enrol a sender, update submodule pins in consumers, deploy or alter old migrations. Checkout lifecycle, permission and message routing remain Background-owned.

## Requirements

Paths below are in `moda-interact-database`. Add `recoverySenderRoutes RecoverySenderRoute[]` to `Shop`. Add `basketRoutingSelections RecoveryBasketRoutingTurn[]` and `recoverySenderAssignment RecoverySenderAssignment?` to the existing `Conversation` model in `prisma/schema.prisma`. Add the following fields immediately after `ConversationMessage.providerDispatchAdmittedAt`. They are the WABA and phone chosen on a durable provider permit when its message lacks recovery assignment evidence; callbacks use the original pair. They are nullable for historical rows and are updated together. No default, backfill, provider ID inference or extra index.

```prisma
  dispatchProviderAccountId     String?
  dispatchProviderPhoneNumberId String?
```

Place the following models beside `Conversation`. Keep partial indexes SQL-only in this Prisma 6.19.3 schema. A client-generated `cuid()` does not produce a PostgreSQL DEFAULT. Supply the ID on raw inserts.

```prisma
model WhatsAppPoolSender {
  providerPhoneNumberId String   @id
  providerAccountId     String
  allocationEnabled     Boolean  @default(false)
  priority              Int
  createdAt             DateTime @default(now()) @db.Timestamptz(3)
  updatedAt             DateTime @default(now()) @updatedAt @db.Timestamptz(3)
  routes                RecoverySenderRoute[]

  @@schema("whatsapp")
}

model RecoverySenderRoute {
  id                    String @id @default(cuid())
  shopId                String
  canonicalRecipient    String @db.VarChar(15)
  providerPhoneNumberId String
  openedAt              DateTime @default(now()) @db.Timestamptz(3)
  closedAt              DateTime? @db.Timestamptz(3)
  shop                  Shop @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Cascade)
  sender                WhatsAppPoolSender @relation(fields: [providerPhoneNumberId], references: [providerPhoneNumberId], onDelete: Restrict, onUpdate: Restrict)
  assignments           RecoverySenderAssignment[]
  routingTurns          RecoveryBasketRoutingTurn[]

  @@schema("whatsapp")
}

model RecoverySenderAssignment {
  conversationId        String @id
  routeId               String
  assignedAt            DateTime @default(now()) @db.Timestamptz(3)
  releasedAt            DateTime? @db.Timestamptz(3)
  conversation          Conversation @relation(fields: [conversationId], references: [id], onDelete: Cascade, onUpdate: Cascade)
  route                 RecoverySenderRoute @relation(fields: [routeId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  @@schema("whatsapp")
}

model RecoveryBasketRoutingTurn {
  inboundProviderMessageId String @id
  routeId                  String
  occurredAt               DateTime @db.Timestamptz(3)
  inputJson                Json? @db.JsonB
  candidatesJson           Json? @db.JsonB
  moderationJson           Json? @db.JsonB
  parentProviderMessageId  String?
  state                    String @default("RECEIVED")
  selectedConversationId   String?
  promptText               String?
  promptAdmittedAt         DateTime? @db.Timestamptz(3)
  promptSentAt             DateTime? @db.Timestamptz(3)
  promptProviderMessageId   String? @unique
  createdAt                DateTime @default(now()) @db.Timestamptz(3)
  updatedAt                DateTime @default(now()) @updatedAt @db.Timestamptz(3)
  route                    RecoverySenderRoute @relation(fields: [routeId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  parent                   RecoveryBasketRoutingTurn? @relation("BasketRoutingQuestionReplies", fields: [parentProviderMessageId], references: [inboundProviderMessageId], onDelete: SetNull, onUpdate: NoAction)
  replies                  RecoveryBasketRoutingTurn[] @relation("BasketRoutingQuestionReplies")
  selectedConversation     Conversation? @relation(fields: [selectedConversationId], references: [id], onDelete: SetNull, onUpdate: Cascade)

  @@index([routeId, state, occurredAt], map: "RecoveryBasketRoutingTurn_route_state_time_idx")
  @@schema("whatsapp")
}
```

### Forward migration

Create **only** `prisma/migrations/20261113120000_whatsapp_sender_pool/migration.sql` for this change. In a disposable development database generate `prisma migrate dev --create-only` against the updated schema, normalize the new directory name, and supplement that new SQL with the CHECKs, indexes and narrow identity guard below. Historical migrations are immutable. In particular preserve `20261111090000_arch038_initial_outreach_tool_call_budget` at the snapshot tip. Equivalent formatting is allowed. Apply these exact table names, types, constraints, predicate and actions.

```sql
ALTER TABLE "whatsapp"."ConversationMessage"
  ADD COLUMN "dispatchProviderAccountId" TEXT,
  ADD COLUMN "dispatchProviderPhoneNumberId" TEXT,
  ADD CONSTRAINT "ConversationMessage_dispatch_sender_pair"
    CHECK (("dispatchProviderAccountId" IS NULL) = ("dispatchProviderPhoneNumberId" IS NULL));

CREATE TABLE "whatsapp"."WhatsAppPoolSender" (
  "providerPhoneNumberId" TEXT PRIMARY KEY,
  "providerAccountId" TEXT NOT NULL,
  "allocationEnabled" BOOLEAN NOT NULL DEFAULT false,
  "priority" INTEGER NOT NULL,
  "createdAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "WhatsAppPoolSender_phone_format" CHECK ("providerPhoneNumberId" ~ '^[0-9]{4,32}$'),
  CONSTRAINT "WhatsAppPoolSender_account_format" CHECK ("providerAccountId" ~ '^[0-9]{4,32}$'),
  CONSTRAINT "WhatsAppPoolSender_nonnegative_priority" CHECK ("priority" >= 0)
);

CREATE TABLE "whatsapp"."RecoverySenderRoute" (
  "id" TEXT PRIMARY KEY,
  "shopId" TEXT NOT NULL,
  "canonicalRecipient" VARCHAR(15) NOT NULL,
  "providerPhoneNumberId" TEXT NOT NULL,
  "openedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "closedAt" TIMESTAMPTZ(3),
  CONSTRAINT "RecoverySenderRoute_canonical_recipient" CHECK ("canonicalRecipient" ~ '^[1-9][0-9]{1,14}$'),
  CONSTRAINT "RecoverySenderRoute_close_order" CHECK ("closedAt" IS NULL OR "closedAt" >= "openedAt"),
  CONSTRAINT "RecoverySenderRoute_shopId_fkey" FOREIGN KEY ("shopId")
    REFERENCES "commerce"."Shop" ("id") ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT "RecoverySenderRoute_providerPhoneNumberId_fkey" FOREIGN KEY ("providerPhoneNumberId")
    REFERENCES "whatsapp"."WhatsAppPoolSender" ("providerPhoneNumberId") ON UPDATE RESTRICT ON DELETE RESTRICT
);
CREATE UNIQUE INDEX "RecoverySenderRoute_open_recipient_shop_key"
  ON "whatsapp"."RecoverySenderRoute" ("canonicalRecipient", "shopId") WHERE "closedAt" IS NULL;
CREATE UNIQUE INDEX "RecoverySenderRoute_open_recipient_sender_key"
  ON "whatsapp"."RecoverySenderRoute" ("canonicalRecipient", "providerPhoneNumberId") WHERE "closedAt" IS NULL;

CREATE TABLE "whatsapp"."RecoverySenderAssignment" (
  "conversationId" TEXT PRIMARY KEY,
  "routeId" TEXT NOT NULL,
  "assignedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "releasedAt" TIMESTAMPTZ(3),
  CONSTRAINT "RecoverySenderAssignment_release_order" CHECK ("releasedAt" IS NULL OR "releasedAt" >= "assignedAt"),
  CONSTRAINT "RecoverySenderAssignment_conversationId_fkey" FOREIGN KEY ("conversationId")
    REFERENCES "whatsapp"."Conversation" ("id") ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT "RecoverySenderAssignment_routeId_fkey" FOREIGN KEY ("routeId")
    REFERENCES "whatsapp"."RecoverySenderRoute" ("id") ON UPDATE RESTRICT ON DELETE CASCADE
);
CREATE INDEX "RecoverySenderAssignment_open_route_member_idx"
  ON "whatsapp"."RecoverySenderAssignment" ("routeId","conversationId") WHERE "releasedAt" IS NULL;

CREATE TABLE "whatsapp"."RecoveryBasketRoutingTurn" (
  "inboundProviderMessageId" TEXT PRIMARY KEY,
  "routeId" TEXT NOT NULL,
  "occurredAt" TIMESTAMPTZ(3) NOT NULL,
  "inputJson" JSONB,
  "candidatesJson" JSONB,
  "moderationJson" JSONB,
  "parentProviderMessageId" TEXT,
  "state" TEXT NOT NULL DEFAULT 'RECEIVED',
  "selectedConversationId" TEXT,
  "promptText" TEXT,
  "promptAdmittedAt" TIMESTAMPTZ(3),
  "promptSentAt" TIMESTAMPTZ(3),
  "promptProviderMessageId" TEXT,
  "createdAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "RecoveryBasketRoutingTurn_state" CHECK ("state" IN
    ('RECEIVED','NEEDS_CLARIFICATION','PROMPT_ADMITTED','AWAITING_REPLY','RESOLVED','IGNORED')),
  CONSTRAINT "RecoveryBasketRoutingTurn_prompt_evidence" CHECK (
    ("promptSentAt" IS NULL) = ("promptProviderMessageId" IS NULL)
    AND ("promptSentAt" IS NULL OR "promptAdmittedAt" IS NOT NULL)),
  CONSTRAINT "RecoveryBasketRoutingTurn_distinct_parent" CHECK ("inboundProviderMessageId" <> "parentProviderMessageId"),
  CONSTRAINT "RecoveryBasketRoutingTurn_routeId_fkey" FOREIGN KEY ("routeId")
    REFERENCES "whatsapp"."RecoverySenderRoute" ("id") ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT "RecoveryBasketRoutingTurn_parentProviderMessageId_fkey" FOREIGN KEY ("parentProviderMessageId")
    REFERENCES "whatsapp"."RecoveryBasketRoutingTurn" ("inboundProviderMessageId") ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT "RecoveryBasketRoutingTurn_selectedConversationId_fkey" FOREIGN KEY ("selectedConversationId")
    REFERENCES "whatsapp"."Conversation" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "RecoveryBasketRoutingTurn_promptProviderMessageId_key"
  ON "whatsapp"."RecoveryBasketRoutingTurn" ("promptProviderMessageId");
CREATE INDEX "RecoveryBasketRoutingTurn_route_state_time_idx"
  ON "whatsapp"."RecoveryBasketRoutingTurn" ("routeId","state","occurredAt");
CREATE INDEX "RecoveryBasketRoutingTurn_pending_age_idx"
  ON "whatsapp"."RecoveryBasketRoutingTurn" ("createdAt","inboundProviderMessageId")
  WHERE "state" IN ('RECEIVED','NEEDS_CLARIFICATION','PROMPT_ADMITTED','AWAITING_REPLY');

CREATE INDEX "RecoveryOutreachAttempt_sender_pool_wait_idx"
  ON "commerce"."RecoveryOutreachAttempt" ("updatedAt", "id")
  WHERE "sequence" = 1 AND "status" = 'PENDING'
    AND "failureCode" = 'WHATSAPP_SENDER_POOL_EXHAUSTED';

CREATE FUNCTION "whatsapp"."prevent_pool_sender_identity_change"()
RETURNS TRIGGER LANGUAGE plpgsql AS $func$
BEGIN
  IF OLD."providerPhoneNumberId" IS DISTINCT FROM NEW."providerPhoneNumberId"
     OR OLD."providerAccountId" IS DISTINCT FROM NEW."providerAccountId" THEN
    RAISE EXCEPTION USING ERRCODE = '23514', MESSAGE = 'Immutable WhatsApp pool sender identity';
  END IF;
  RETURN NEW;
END;
$func$;

CREATE TRIGGER "WhatsAppPoolSender_immutable_identity"
BEFORE UPDATE OF "providerPhoneNumberId", "providerAccountId"
ON "whatsapp"."WhatsAppPoolSender" FOR EACH ROW
EXECUTE FUNCTION "whatsapp"."prevent_pool_sender_identity_change"();
```

The inventory identity guard preserves the WABA/phone provenance of historic messages. Route identity (`id, shopId, canonicalRecipient, providerPhoneNumberId`) and an admitted member's `conversationId, routeId` are insert-once in the application. For reuse insert a new route ID; do not move or reopen a closed one. At an existing recovery/permit boundary join Conversation with its CheckoutRecovery and verify its shop, canonical phone and conversation match the route before attaching it. Use an explicit CAS with `closedAt IS NULL` or `releasedAt IS NULL` plus original route/member identity for closure. A single short transaction under the route row lock releases a member, rechecks other non-released members and closes that same route only when none remain. A cascade delete can remove the final member without application code. Under the route lock, Background's next allocation closes an empty open route before returning pool exhaustion. Closure immediately invalidates that generation's pending questions. BACKGROUND-004 checks the generation on each use and owns bounded cleanup of invalidated turns; releasing a member or a route does not scan or lock sibling routing turns. No route-closing SQL trigger or materialized member count is required. Duplicate recovery replay, member reallocation and operator settings never mutate past message ownership.

The existing `RecoveryOutreachAttempt` waiter predicate and non-pooled permit fields are unchanged. This development baseline has no installed ARCH-076 migrations. Add one new forward migration at the specified path against the original uploaded workspace. Create empty new tables. Do not seed inventory or infer past sender identity. Initial schema changes are additive to existing data, with no down migration.

## Work Items

- [ ] Implement the specified models, message fields, constraints, relations and indexes in one new forward migration.
- [ ] Run the schema, concurrency and fresh/upgrade tests and ERD validation.
- [ ] Record actual migrations, database image, branch SHA, worktree path, changed files and cleanup in the Completion Report.
- [ ] Publish implementation and task report on their launcher-resolved mirrored branches for architect review.

## Interfaces / Contracts

Admin reads and writes `whatsapp."WhatsAppPoolSender"`. Background resolves `RecoverySenderRoute` by open (recipient, shop) to allocate or open (recipient, sender) to receive. `RecoverySenderAssignment` is the per-conversation membership and pins original sender through its route even after either row closes. Multiple same-shop conversations with the same recipient and sender are valid and deliberately exercise the same route row. Partial unique indexes are on open routes, never on individual checkouts in that route. Original non-pooled transport evidence remains on `ConversationMessage`.

`RecoveryBasketRoutingTurn` is the durable, shop-scoped record when a reply must be interpreted within the route, before it has a checkout owner. Use exactly the content shapes and state machine owned by BACKGROUND-004. Null is SQL NULL for absent/erased JSON, not JSON `null`. Its primary key is the original inbound provider message ID, also used by the existing unique ConversationMessage ID when an inbound is ultimately attached. Lock/check both records on retry; a duplicate must never move to a later route or checkout. A clarification answer links to its exact parent inbound. Store and reuse the option order actually shown. A prompt has at most one provider admission and one receipt recorded on that original turn. Scrub customer text, transcripts, candidates and prompt text in the same transaction as terminal handling. On IGNORED use SQL NULL for inputJson. On RESOLVED replace it with a content-free versioned role marker as defined by BACKGROUND-004. Its complete shape is one of `{v:1,role:"objective"}`, `{v:1,role:"selectionOnly"}` or, for a verified reply containing a choice and a same-basket substantive request, `{v:1,role:"mixedObjective",startCodePoint,endCodePoint}`. The half-open Unicode code-point offsets identify the exact substantive suffix of the separately moderated original ConversationMessage text or transcript. Set terminal moderationJson to SQL NULL except for a mixedObjective. There retain only the versioned, content-free proof for the complete source and exact model-visible suffix defined in BACKGROUND-004. Keep the ordinary ConversationModerationAssessment bound to the full authentic message. Refreshing an outdated policy proof must preserve the original RESOLVED admission timestamp. The role marker contains no customer text and is frozen with the selected conversation, timestamps and original provider ID. This remains unambiguous if the parent FK later becomes null. Missing, invalid or mismatched evidence grants no model objective. No additional Prisma field, migration, payload copy or model-generated text is required. Expire pending content at its immutable first database receipt time (`createdAt + 24 hours`). The separate customer-service send window is bounded by the verified provider occurrence time. Duplicate delivery, later attempts and scrubbing never renew either clock. Freeze `updatedAt` at RESOLVED in the same transaction as normal conversation pending-turn admission. Later replay observes that admission stamp without issuing another update to the terminal routing row. BACKGROUND-004 owns the bounded sweep. The SQL-only pending-age index lets the maintenance worker read oldest-first without scanning terminal tombstones. Immutable IDs, time stamps and terminal state may remain while the route history exists to prevent duplicate effects. A timeout after prompt admission stays uncertain: do not reset the admit time or resend automatically. A route may contain two unresolved originals. There is no per-shop or per-route one-question uniqueness and no arbitrary sibling-recovery limit.

`selectedConversationId` and the optional `parentProviderMessageId` FK protect existence. Background's locked commit also verifies matching route ID, eligible membership/ownership and event time. A status update or answer arriving after route reuse cannot select another shop's recovery. All billing, checkout-linked message authorisation and AI routing remain outside this database-only task.

## Dependencies

None.

## Enables

`ARCH-076-ADMIN-001` and `ARCH-076-BACKGROUND-001` consume the accepted schema.

## Acceptance Criteria

- [ ] Only the declared new forward migration, schema, targeted ERD and validation files/scripts change. Each Prisma model matches the SQL and the PostgreSQL partial indexes have the exact declared keys and predicates.
- [ ] Both independent runner modes pass on PostgreSQL 17 with pgvector: same-shop co-membership, cross-shop exclusion, last-member release and immediate number reuse, concurrent reservations, durable clarification and stale messages under real database constraints.
- [ ] Old conversations, recipients, attempts and message proofs remain readable; old writers and both-null/frozen-pair data work. Fresh and upgrade assertions reject half-filled dispatch evidence and mutating a sender identity.
- [ ] Original credentials and customer rows are preserved, migration creates zero inventory records, and the temporary runner resources are removed after success or failure.

## Validation

Add `scripts/validate-whatsapp-sender-pool.mjs`, `scripts/test-whatsapp-sender-pool-postgres.mjs` and these two `package.json` scripts.

- `test:sender-pool:schema` → `node scripts/validate-whatsapp-sender-pool.mjs`
- `test:sender-pool:postgres` → `node scripts/test-whatsapp-sender-pool-postgres.mjs`

Use the fresh/upgrade patterns in `scripts/test-arch068-conversation-delivery-plan-postgres.mjs`. Run both paths within the new command in an invocation-owned disposable `pgvector/pgvector:pg17` container with loopback-only or container-internal access. Never run migrations against a developer or hosted database. For upgrade, apply all migrations through the immediate predecessor, seed two shops, recoveries, conversations, old messages, an existing pending attempt and existing sender configuration with fixture values, then apply the new migration. For fresh, deploy the entire history and build equivalent fixtures. Check old records/receipt IDs/config are byte/value preserved, both dispatch columns read NULL on old rows and new tables are empty before pool fixtures. Insert a whole non-null dispatch pair on a new message, allow both-null, reject either half alone, prove the old writer still works. Verify each case below.

1. Inspect Prisma DMMF names, fields, defaults, relations and nullability. Use PostgreSQL catalogs (`pg_get_expr`, `pg_get_indexdef`, `pg_indexes`, `pg_constraint`) to verify partial index predicates and keys and all FKs/checks. Check there is no unique constraint on individual recovery memberships by sender, no global uniqueness of customer phone and no table-level unique `(shopId,canonicalRecipient)` that would reject historical closed routes.
2. With independent database connections, concurrently open (X, Shop A, S1) twice, then (X, Shop A, S2) and (X, Shop B, S1) against an existing committed A/S1. Check duplicate OPEN rows violate SQLSTATE 23505 under the appropriate unique index. Multiple memberships A1 + A2 on the same A/S1 route succeed. X/Shop B/S2 and Y/Shop A/S1 also succeed; X/Shop C/S1 conflicts while A/S1 is open. Test rollback visibility.
3. Release only A1, show A2 remains open and X/Shop C/S1 is still unavailable. Release A2 and close A's original route in one transaction; adding X/Shop C/S1 then succeeds immediately. Historical A quotes still map to A's older route ID. A delayed close of old A cannot release C. FKs and canonical-recipient grammar, negative priority and invalid time order fail correctly. A CAS replay of an open/member insert cannot change its owner. Deleting the parent shop cascades only its route/member and route-local inbound evidence. Deleting an inventory row that retains a route fails. Ordinary priority/drain operations succeed; changing persisted phone/WABA raises 23514.
4. Create two unresolved turns with different provider IDs on the same route. Reject duplicate inbound IDs, reuse of a non-null confirmed outbound prompt ID across turns and impossible receipt/admit combinations. Allow a question and scoped answer to retain original linkage. Verify terminal content scrub, exact content-free RESOLVED role markers and IGNORED input SQL NULL, including preserved classification after parent deletion. Confirm deduplication and original IDs survive, selected conversation deletion sets selection NULL, route/shop deletion cascades only its rows and invalid states fail. Verify the pending-age index excludes terminal states and sorts unresolved rows by first database receipt and provider ID. Assert the existing durable pool waiter partial predicate by including matching and nonmatching attempt states, sequences and failure codes. Retain other billing wait behavior.
5. Refresh the tracked `docs/generated/prisma-erd.puml` and render `docs/generated/erd.png` following the established generator workflow (the PUML declares `@startuml erd`; the snapshot omits the generated PNG). Include the new entities and owned relationship changes only; record pre-existing unrelated diagram drift separately. Destroy only the container/work dir this invocation created in finally on pass/failure. Record the run and cleanup evidence.

From the prepared Database worktree, use the repository's Node/npm baseline and run:

```bash
npm ci --ignore-scripts
npm run prisma:validate
npm run prisma:generate
npm run test:sender-pool:schema
npm run test:sender-pool:postgres
npm run lint
npm run erd
git diff --check
```

Use a disposable local connection for commands requiring `DATABASE_URL`. No application code, consumer submodule update, release, production migration or previous-migration edits are in the Database task.

## Implementation Notes

Ready, defined but not materialised. Run `/moda-task ARCH-076-DATABASE-001` using the parent portable definition and normal prepared packet. On a genuine schema conflict, report the exact schema/SQL and failing command to the architect rather than changing the invariant. On acceptance, consumer tasks use the accepted Database commit after the developer's normal integration. No agent merges main.

After the Work Items, Acceptance Criteria and Validation pass, set status to review, send the Completion Report to `moda_architect` and stop. Do not execute a downstream task.

## Completion Report

### Status

Not Started.

### Files Changed

Pending implementation.

### Work Completed

Pending implementation. Record launcher-resolved parent and implementation worktrees, mirrored branch names, start sync and final SHAs, consumer submodule pin where applicable, and cleanup.

### Validation Results

Pending. Record exact commands, exit status, container IDs, cleanup, failures and warnings. Report baseline issues separately from this change.

### Deviations

None recorded.

### Assumptions

None recorded.

### Unresolved Issues

None recorded.

### Architectural Concerns

None recorded.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
