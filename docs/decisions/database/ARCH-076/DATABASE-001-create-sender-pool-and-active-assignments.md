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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-076-ADMIN-001", "ARCH-076-BACKGROUND-001"]
created: 2026-11-13
updated: 2026-11-15
---

# Persist shop sender routes, checkout members and reply clarification

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinated by `moda_architect`.

## Objective

Persist one active sender route per shop and customer, any number of active checkout conversations as its members, and durable handling of ambiguous replies. Persist the original sender and prompt scope for admitted outbound messages, including neutral prompts on a shared customer/sender thread.

## Context

The merchant's platform and shop decide which checkouts can coexist. Distinct recoveries admitted by existing merchant/platform rules each retain their own recovery, attempt, credit and conversation. One shop and customer share a single Moda number across those recoveries. A different shop serving the same customer preferentially uses an unused enabled number. If all enabled numbers are in use by that customer, it joins the least-occupied enabled number with its own merchant route. A customer/sender thread has a stable generation ID independent of its shops. Its final live shop route closing releases the thread with no cooldown. Each incoming question can be retained before its shop is known. Within this application each environment has a separate database.

## Scope

Implement the Prisma shape, one forward migration, explicit SQL constraints/indexes, schema checks, disposable PostgreSQL fresh/upgrade/concurrency tests, package scripts and corresponding ERD relationships described below.

## Out of Scope

Do not mutate the API or worker, administer Meta assets or enrol a sender, update submodule pins in consumers, deploy or alter old migrations. Background owns checkout lifecycle, permission and message routing.

## Requirements

### Platform configuration and write ownership

`WhatsAppPoolSender` is platform configuration for the current deployment. A row identifies one already-registered Meta **phone-number ID** and its owning WhatsApp Business Account (WABA). The environment already selects its database. Omit shop and environment columns. The existing encrypted `public."PlatformConfiguration"` entry keyed by `messaging.sender` supplies credentials. Keep that record and its audit history as they are. Pool membership has one source, `whatsapp."WhatsAppPoolSender"`. Store no token, displayed telephone number, copied credential document or second list of senders. The migration creates an empty inventory. ADMIN-001 owns verified enrolment, allocation enablement and priority on the existing Platform Configuration page.

| Record | Writer and purpose |
| --- | --- |
| `WhatsAppPoolSender` | A platform super-admin manages availability through Admin. Changing priority or disabling allocation has no cascading effect on existing routes. |
| `RecoverySenderThread` | Background binds a canonical customer number and receiving Meta number for one active period. |
| `RecoverySenderRoute` | Background binds a shop to that thread. Each customer/shop can have one open route. Different shops may share a thread when all eligible numbers are already in use by this customer. |
| `RecoverySenderAssignment` | Background attaches each recovery conversation to its route. Several eligible baskets from one shop can share that route. |
| `RecoveryBasketRoutingTurn` | Background records the original inbound question and links later clarification replies to it until the correct shop and recovery conversation can be selected. Independent questions have separate inbound IDs. |

### Database repository change list

| Action | Path in `moda-interact-database` |
| --- | --- |
| Edit | `prisma/schema.prisma` |
| Create | `prisma/migrations/20261113120000_whatsapp_sender_pool/migration.sql` |
| Edit | `package.json` (two script entries) |
| Create | `scripts/validate-whatsapp-sender-pool.mjs` |
| Create | `scripts/test-whatsapp-sender-pool-postgres.mjs` |
| Edit | `docs/generated/prisma-erd.puml` |
| Render | `docs/generated/erd.png` |

The portable parent task is the source of the schema edits and SQL. The implementation agent records its report on the mirrored parent task branch. All historical migrations, the lockfile, the parent indexes and consumer submodule pins are outside the implementation change list.

### Exact edits to `prisma/schema.prisma`

Make these three insertions in the existing file. In the snippets below, retain the model header and surrounding existing fields as anchors. The relation fields on `Shop` and `Conversation` are inverse Prisma relations. They create no PostgreSQL columns on those tables.

1. Immediately inside `model Shop {`, before `commerceProductContexts`, insert the single `recoverySenderRoutes` line at the start of the block.

   ```prisma
   model Shop {
     recoverySenderRoutes       RecoverySenderRoute[]
     commerceProductContexts CommerceConversationProductContext[]
   ```

2. Immediately inside `model Conversation {`, before `commerceProductContext`, insert `basketRoutingSelections` and `recoverySenderAssignment`, in that order.

   ```prisma
   model Conversation {
     basketRoutingSelections    RecoveryBasketRoutingTurn[]
     recoverySenderAssignment   RecoverySenderAssignment?
     commerceProductContext CommerceConversationProductContext?
   ```

3. In `model ConversationMessage`, insert both nullable sender fields immediately after `providerDispatchAdmittedAt` and before `providerDispatchControlRevision`. Match these four lines.

   ```prisma
     providerDispatchAdmittedAt      DateTime? @db.Timestamptz(3)
     dispatchProviderAccountId     String?
     dispatchProviderPhoneNumberId String?
     providerDispatchControlRevision Int?
   ```

   These fields capture the WhatsApp Business Account (WABA) and Meta phone-number ID on a durable provider permit when the message lacks recovery assignment evidence. The writer sets the pair together. Existing messages read SQL NULL for both fields. Leave `MerchantConversationSendCommand.providerDispatchAdmittedAt` as it is.

Insert the next complete block immediately **before** `model Conversation {`, after the closing brace of `enum ConversationOutcome`. Use the five models in the printed order and the exact field names, relation actions, database types, defaults, and mapped index and foreign key names. PostgreSQL owns the partial indexes, CHECKs and identity trigger listed in the forward SQL. Prisma 6.19.3 supplies the `cuid()` for new thread and route IDs client-side. A raw SQL insert supplies those IDs explicitly.

```prisma
model WhatsAppPoolSender {
  providerPhoneNumberId String   @id
  providerAccountId     String
  allocationEnabled     Boolean  @default(false)
  priority              Int
  createdAt             DateTime @default(now()) @db.Timestamptz(3)
  updatedAt             DateTime @default(now()) @updatedAt @db.Timestamptz(3)
  threads               RecoverySenderThread[]

  @@schema("whatsapp")
}

model RecoverySenderThread {
  id                    String @id @default(cuid())
  canonicalRecipient    String @db.VarChar(15)
  providerPhoneNumberId String
  openedAt              DateTime @default(now()) @db.Timestamptz(3)
  closedAt              DateTime? @db.Timestamptz(3)
  sender                WhatsAppPoolSender @relation(fields: [providerPhoneNumberId], references: [providerPhoneNumberId], onDelete: Restrict, onUpdate: Restrict)
  routes                RecoverySenderRoute[]
  routingTurns          RecoveryBasketRoutingTurn[]

  @@unique([id, canonicalRecipient, providerPhoneNumberId], map: "RecoverySenderThread_route_target_key")
  @@schema("whatsapp")
}

model RecoverySenderRoute {
  id                    String @id @default(cuid())
  shopId                String
  threadId              String
  canonicalRecipient    String @db.VarChar(15)
  providerPhoneNumberId String
  openedAt              DateTime @default(now()) @db.Timestamptz(3)
  closedAt              DateTime? @db.Timestamptz(3)
  shop                  Shop @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Cascade)
  thread                RecoverySenderThread @relation(fields: [threadId, canonicalRecipient, providerPhoneNumberId], references: [id, canonicalRecipient, providerPhoneNumberId], onDelete: Cascade, onUpdate: Restrict, map: "RecoverySenderRoute_threadId_canonicalRecipient_fkey")
  assignments           RecoverySenderAssignment[]

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
  threadId                 String
  routeId                  String?
  promptScopeRouteId       String?
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
  thread                   RecoverySenderThread @relation(fields: [threadId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  parent                   RecoveryBasketRoutingTurn? @relation("BasketRoutingQuestionReplies", fields: [parentProviderMessageId], references: [inboundProviderMessageId], onDelete: SetNull, onUpdate: NoAction)
  replies                  RecoveryBasketRoutingTurn[] @relation("BasketRoutingQuestionReplies")
  selectedConversation     Conversation? @relation(fields: [selectedConversationId], references: [id], onDelete: SetNull, onUpdate: Cascade)

  @@index([threadId, state, occurredAt], map: "RecoveryBasketRoutingTurn_thread_state_time_idx")
  @@schema("whatsapp")
}
```

### Forward migration

The sole new migration is `prisma/migrations/20261113120000_whatsapp_sender_pool/migration.sql`. Its entire file content is the SQL block below, including `BEGIN;` and `COMMIT;`. It is atomic on PostgreSQL. The two message fields are nullable and have no database default. Existing rows require no update. There are no seed inserts, backfill, credential changes or down migration.

**Authoring order.** Apply the schema edits first. Install dependencies with `npm ci --ignore-scripts` under the parent workspace's Node 24.19.0. From the dedicated Database worktree, set `TASK_DEFINITION` to the absolute path of **this Markdown file in the matching parent task worktree**. Run the following Bash block with a local Docker engine and interactive terminal for Prisma. It deploys the existing history to its own local database, runs the Database role's create-only step, then replaces the generated draft with the prescribed complete SQL. The launcher provides both worktree paths. The script never reads the host environment's database URL.

```bash
(
  set -euo pipefail
  : "${TASK_DEFINITION:?Set TASK_DEFINITION to this file in the parent task worktree}"
  test -r "$TASK_DEFINITION"
  shopt -s nullglob
  pool_drafts=(prisma/migrations/*_whatsapp_sender_pool)
  if (( ${#pool_drafts[@]} )); then
    echo 'Sender-pool migration already exists. Check its contents and migration status before authoring.' >&2
    exit 1
  fi
  pool_db_id=$(docker run -d --label moda.task=ARCH-076-DATABASE-001 \
    -p 127.0.0.1::5432 -e POSTGRES_DB=sender_pool_author \
    -e POSTGRES_PASSWORD=fixture_only pgvector/pgvector:pg17)
  trap 'docker rm -f "$pool_db_id" >/dev/null' EXIT
  pool_port=$(docker port "$pool_db_id" 5432/tcp)
  [[ "$pool_port" == 127.0.0.1:* ]]
  export DATABASE_URL="postgresql://postgres:fixture_only@${pool_port}/sender_pool_author"
  for ((i=0; i<60; i++)); do
    if docker exec "$pool_db_id" pg_isready -q -h 127.0.0.1 -U postgres -d sender_pool_author; then break; fi
    sleep 1
  done
  docker exec "$pool_db_id" pg_isready -q -h 127.0.0.1 -U postgres -d sender_pool_author
  npx --no-install prisma migrate deploy --schema prisma/schema.prisma
  npx --no-install prisma migrate dev --schema prisma/schema.prisma \
    --name whatsapp_sender_pool --create-only --skip-generate
  pool_drafts=(prisma/migrations/*_whatsapp_sender_pool)
  (( ${#pool_drafts[@]} == 1 ))
  pool_target=prisma/migrations/20261113120000_whatsapp_sender_pool
  if [[ "${pool_drafts[0]}" != "$pool_target" ]]; then mv "${pool_drafts[0]}" "$pool_target"; fi
  node --input-type=module - "$TASK_DEFINITION" "$pool_target/migration.sql" <<'NODE'
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
const [definition, migration] = process.argv.slice(2);
const task = readFileSync(definition, 'utf8').replace(/\r\n/g, '\n');
const blocks = [...task.matchAll(/^`{3}sql\n([\s\S]*?)^`{3}$/gm)];
assert.equal(blocks.length, 1, 'Expected one authoritative SQL block');
const sql = blocks[0][1];
assert.ok(sql.startsWith('BEGIN;\n') && sql.endsWith('COMMIT;\n'));
writeFileSync(migration, sql);
NODE
  npx --no-install prisma migrate deploy --schema prisma/schema.prisma
  npx --no-install prisma migrate status --schema prisma/schema.prisma
)
```

On a resumed attempt with the canonical file already present, compare it byte-for-byte with the SQL block. When identical, continue with validation on the invocation-owned fresh and upgrade databases. If a sender-pool migration with different SQL has already been applied, its name collides, a required existing field has changed incompatibly, or Prisma asks to reset, record the exact conflict for the architect. Preserve the existing history. If an earlier create-only attempt left a draft, first verify that its only migration directory was created by this task and was never applied. Resume at the directory-normalisation and exact SQL copy steps, then validate on a new disposable database. The supplied snapshot's predecessor is `20261113111320_arch075_meta_app_operation_state`.

```sql
BEGIN;

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

CREATE TABLE "whatsapp"."RecoverySenderThread" (
  "id" TEXT PRIMARY KEY,
  "canonicalRecipient" VARCHAR(15) NOT NULL,
  "providerPhoneNumberId" TEXT NOT NULL,
  "openedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "closedAt" TIMESTAMPTZ(3),
  CONSTRAINT "RecoverySenderThread_canonical_recipient" CHECK ("canonicalRecipient" ~ '^[1-9][0-9]{1,14}$'),
  CONSTRAINT "RecoverySenderThread_close_order" CHECK ("closedAt" IS NULL OR "closedAt" >= "openedAt"),
  CONSTRAINT "RecoverySenderThread_providerPhoneNumberId_fkey" FOREIGN KEY ("providerPhoneNumberId")
    REFERENCES "whatsapp"."WhatsAppPoolSender" ("providerPhoneNumberId") ON UPDATE RESTRICT ON DELETE RESTRICT
);
CREATE UNIQUE INDEX "RecoverySenderThread_route_target_key"
  ON "whatsapp"."RecoverySenderThread" ("id","canonicalRecipient","providerPhoneNumberId");
CREATE UNIQUE INDEX "RecoverySenderThread_open_recipient_sender_key"
  ON "whatsapp"."RecoverySenderThread" ("canonicalRecipient","providerPhoneNumberId") WHERE "closedAt" IS NULL;

CREATE TABLE "whatsapp"."RecoverySenderRoute" (
  "id" TEXT PRIMARY KEY,
  "shopId" TEXT NOT NULL,
  "threadId" TEXT NOT NULL,
  "canonicalRecipient" VARCHAR(15) NOT NULL,
  "providerPhoneNumberId" TEXT NOT NULL,
  "openedAt" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "closedAt" TIMESTAMPTZ(3),
  CONSTRAINT "RecoverySenderRoute_canonical_recipient" CHECK ("canonicalRecipient" ~ '^[1-9][0-9]{1,14}$'),
  CONSTRAINT "RecoverySenderRoute_close_order" CHECK ("closedAt" IS NULL OR "closedAt" >= "openedAt"),
  CONSTRAINT "RecoverySenderRoute_shopId_fkey" FOREIGN KEY ("shopId")
    REFERENCES "commerce"."Shop" ("id") ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT "RecoverySenderRoute_threadId_canonicalRecipient_fkey" FOREIGN KEY ("threadId","canonicalRecipient","providerPhoneNumberId")
    REFERENCES "whatsapp"."RecoverySenderThread" ("id","canonicalRecipient","providerPhoneNumberId") ON UPDATE RESTRICT ON DELETE CASCADE
);
CREATE UNIQUE INDEX "RecoverySenderRoute_open_recipient_shop_key"
  ON "whatsapp"."RecoverySenderRoute" ("canonicalRecipient", "shopId") WHERE "closedAt" IS NULL;
CREATE INDEX "RecoverySenderRoute_open_thread_shop_idx"
  ON "whatsapp"."RecoverySenderRoute" ("threadId","shopId") WHERE "closedAt" IS NULL;

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
  "threadId" TEXT NOT NULL,
  "routeId" TEXT,
  "promptScopeRouteId" TEXT,
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
  CONSTRAINT "RecoveryBasketRoutingTurn_threadId_fkey" FOREIGN KEY ("threadId")
    REFERENCES "whatsapp"."RecoverySenderThread" ("id") ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT "RecoveryBasketRoutingTurn_prompt_scope" CHECK (
    "promptScopeRouteId" IS NULL OR ("promptAdmittedAt" IS NOT NULL AND "routeId" IS NOT NULL AND "promptScopeRouteId" = "routeId")),
  CONSTRAINT "RecoveryBasketRoutingTurn_parentProviderMessageId_fkey" FOREIGN KEY ("parentProviderMessageId")
    REFERENCES "whatsapp"."RecoveryBasketRoutingTurn" ("inboundProviderMessageId") ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT "RecoveryBasketRoutingTurn_selectedConversationId_fkey" FOREIGN KEY ("selectedConversationId")
    REFERENCES "whatsapp"."Conversation" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "RecoveryBasketRoutingTurn_promptProviderMessageId_key"
  ON "whatsapp"."RecoveryBasketRoutingTurn" ("promptProviderMessageId");
CREATE INDEX "RecoveryBasketRoutingTurn_thread_state_time_idx"
  ON "whatsapp"."RecoveryBasketRoutingTurn" ("threadId","state","occurredAt");
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

COMMIT;
```

The inventory identity guard preserves the original WABA/number. A `RecoverySenderThread` is one immutable generation of the canonical customer and receiving number. `RecoverySenderRoute` identifies the shop within that generation. Its repeated recipient and sender support the open customer/shop constraint and historical queries. The composite FK and its exact unique target prevent mismatched route and thread identities. A number may serve many shops on the same thread. Use the non-unique open thread/shop index to count those routes and enumerate their shop identities. Refer to BACKGROUND-001 for locks, ranking and positive consent/dispatch eligibility.

While a route/member exists, its identity is insert-once. To reuse after closure, create a new ID. Under the established owning locks then thread → route → member, release by original membership key, close its route only after its last live member, and close the thread only after its last live route. A single conditional release cannot free another shop's route. Lock and recheck original parents before each insert or terminal CAS. Acquire no other merchant's business locks while holding these locks. For route/member rows removed by cascade, Background repairs any resulting empty parent before allocating a new generation. Physical deletion of one merchant cascades only that shop's own routes, conversations and dependent memberships. Thread evidence is independent of the lifetime of a particular merchant. Remove its transient data under BACKGROUND-004's scoped cleanup and existing lifecycle rules. Resolving an active turn always rechecks the original thread generation and the selected shop/member. Closing an entire thread immediately invalidates every pending turn there. Closing one route prevents selection of that old route without suppressing independent questions for surviving shops.

Deploy the additive database migration before Admin or Background use a newly generated client. Existing writers can omit both dispatch identity fields. If an application version is rolled back, leave the new migration and rows in place. Background supplies the original sender pair on permit admission and preserves it on retries. SQL enforces completeness of the pair. The existing dispatch guard and the SQL identity trigger have distinct scopes. The latter protects only the enrolled WABA and phone ID.

The filtered waiter index belongs to the existing `commerce."RecoveryOutreachAttempt"` table. Only an initial pending attempt carrying the exact pool-exhausted code qualifies. A new shop with zero eligible enabled senders waits. A customer already using every enabled sender can share one of those senders with the new shop. Allocation, expiry, last-member release and disambiguation stay with Background. Database fixtures demonstrate the allowed records, lock interactions and uniqueness rules.

## Work Items

- [ ] Implement the specified models, message fields, constraints, relations and indexes in one new forward migration.
- [ ] Run the schema, concurrency and fresh/upgrade tests and ERD validation.
- [ ] Record actual migrations, database image, branch SHA, worktree path, changed files and cleanup in the Completion Report.
- [ ] Publish implementation and task report on their launcher-resolved mirrored branches for architect review.

## Interfaces / Contracts

Admin manages platform sender configuration through `messaging.sender`. Background reads the open `RecoverySenderRoute` by canonical recipient and shop to reuse an assigned number. A verified inbound resolves one open `RecoverySenderThread` by canonical recipient and receiving provider phone under its inventory WABA. Its active shop routes are then read by threadId. Multiple checkouts can join the same merchant route and multiple merchant routes can share the same generation. `RecoverySenderAssignment` pins the exact checkout to its original merchant and number. Original non-pooled proofs stay on `ConversationMessage`.

Use `RecoveryBasketRoutingTurn.threadId` for mandatory immutable customer/sender generation ownership. `routeId` begins NULL on an unresolved merchant and may become non-null once, by a compare-and-set after verifying that route's thread, authenticated recipient/sender, current shop identity and event-time evidence. It is preset for an already-verified merchant. `promptScopeRouteId` is a separate nullable text stamp for the specific outbound prompt. Set it once when its permit is admitted, to NULL for a neutral merchant-unknown prompt, or the verified route ID for shop-specific copy. Any earlier unadmitted draft does not establish authority. Neither an answer's later shop selection nor final transcript projection may rewrite that original admitted prompt scope. Validate the immutable stored prompt ID/receipt, original receiving pair and historical route/shop evidence when using a quote for consent. A neutral prompt never supplies merchant-specific consent scope.

The optional route and prompt scope stamps deliberately have no deleting or nullifying route FK. A verified shop binding and a historic merchant-specific prompt must remain distinguishable from an always-neutral turn after route/shop deletion. Applications check the referenced ID belongs to the immutable thread under thread/route locks on creation and use; a deleted/stale shop binding cannot become unbound or resolve using another merchant. No turn/pending message is deleted merely because a peer merchant was deleted. `parentProviderMessageId` identifies a specific original or clarification on this thread; check the matching thread, permitted route/ancestry and confirmed prompt at every bind. Several pending roots (including unbound roots) may coexist. Preserve the exact words and provider IDs in the existing bounded pending fields, and store pre-shop candidate evidence as verified route-generation IDs, safe shop identifiers/labels and receipt stamps; business basket contents are loaded only after the merchant is bound. BACKGROUND-004 owns JSON shapes, clarification linkage and dispositions.

`RecoveryBasketRoutingTurn` is the durable question on the customer/sender thread from receipt through merchant and checkout selection. Use exactly the content shapes and state machine owned by BACKGROUND-004. Null is SQL NULL for absent/erased JSON, not JSON `null`. Its primary key is the original inbound provider message ID, also used by the existing unique ConversationMessage ID when an inbound is ultimately attached. Lock/check both records on retry; a duplicate must never move to a later route or checkout. A RESOLVED selectionOnly row used solely for merchant identification may record its final selectedConversationId for idempotent provenance without a matching ConversationMessage. The thread retains that control; no other shop names or neutral selection instructions enter a merchant transcript. Never synthesize a merchant message merely to satisfy this correlation. A clarification answer links to its exact parent inbound. Store and reuse the option order actually shown. A prompt has at most one provider admission and one receipt recorded on that original turn. Scrub customer text, transcripts, candidates and prompt text in the same transaction as terminal handling. On IGNORED use SQL NULL for inputJson. On RESOLVED replace it with a content-free versioned role marker as defined by BACKGROUND-004. Its complete shape is one of `{v:1,role:"objective"}`, `{v:1,role:"selectionOnly"}` or, for a verified reply containing a choice and a same-basket substantive request, `{v:1,role:"mixedObjective",startCodePoint,endCodePoint}`. The half-open Unicode code-point offsets identify the exact substantive suffix of the separately moderated original ConversationMessage text or transcript. Set terminal moderationJson to SQL NULL except for a mixedObjective. There retain only the versioned, content-free proof for the complete source and exact model-visible suffix defined in BACKGROUND-004. Keep the ordinary ConversationModerationAssessment bound to the full authentic message. Refreshing an outdated policy proof must preserve the original RESOLVED admission timestamp. The role marker contains no customer text and is frozen with the selected conversation, timestamps and original provider ID. This remains unambiguous if the parent FK later becomes null. Missing, invalid or mismatched evidence grants no model objective. No additional Prisma field, migration, payload copy or model-generated text is required. Expire pending content at its immutable first database receipt time (`createdAt + 24 hours`). The separate customer-service send window is bounded by the verified provider occurrence time. Duplicate delivery, later attempts and scrubbing never renew either clock. Freeze `updatedAt` at RESOLVED in the same transaction as normal conversation pending-turn admission. Later replay observes that admission stamp without issuing another update to the terminal routing row. BACKGROUND-004 owns the bounded sweep. The SQL-only pending-age index lets the maintenance worker read oldest-first without scanning terminal tombstones. Immutable IDs, time stamps and terminal state may remain while the thread history exists to prevent duplicate effects. A timeout after prompt admission stays uncertain: do not reset the admit time or resend automatically. A thread may contain multiple independent unresolved originals for different merchants and multiple questions for one merchant. No uniqueness constraint limits the number of outstanding questions, shops on a thread, or baskets per shop.

`selectedConversationId` and the optional `parentProviderMessageId` FK protect existence. Background's locked commit also verifies same immutable thread, matching bound route ID, eligible membership/ownership and event time. A status update or answer arriving after route reuse cannot select another shop's recovery. All billing, checkout-linked message authorisation and AI routing remain outside this database-only task.

## Dependencies

None.

## Enables

`ARCH-076-ADMIN-001` and `ARCH-076-BACKGROUND-001` consume the accepted schema.

## Acceptance Criteria

- [ ] Only the declared new forward migration, schema, targeted ERD and validation files/scripts change. Each Prisma model matches the SQL and the PostgreSQL partial indexes have the exact declared keys and predicates.
- [ ] Both runner modes pass on PostgreSQL 17 with pgvector. Show same-shop co-membership, separate and shared sender routes, concurrent admissions, release and immediate reuse, and persistence of the original question through clarification. Exercise the database contracts directly. The allocation algorithm and the choice of basket are tested by Background.
- [ ] Old conversations, recipients, attempts and message proofs remain readable; old writers and both-null/frozen-pair data work. Fresh and upgrade assertions reject half-filled dispatch evidence and mutating a sender identity.
- [ ] Original credentials and customer rows are preserved, migration creates zero inventory records, and the temporary runner resources are removed after success or failure.

## Validation

Create the two validation scripts listed above. Append these two entries inside the existing `scripts` object in `package.json`. Keep existing script names and dependency versions.

- `test:sender-pool:schema` → `node scripts/validate-whatsapp-sender-pool.mjs`
- `test:sender-pool:postgres` → `node scripts/test-whatsapp-sender-pool-postgres.mjs`

For the two-mode PostgreSQL runner, reuse `scripts/test-arch075-delivery-parts-postgres.mjs`'s container and history-replay pattern. A single `npm run test:sender-pool:postgres` invocation runs both `fresh` and `upgrade` and reports each result. Start a unique invocation-labelled container with `--network none`; use `docker exec -i` with `psql -X -v ON_ERROR_STOP=1` for all connections. Ignore any inherited connection URL. In `fresh`, replay every SQL migration through the target in lexical order before fixture creation. In `upgrade`, replay through the predecessor, create baseline fixtures, capture rows ordered by primary key, and replay the **same target file** before assertions. If later migrations exist on the task branch, run the target assertions at its boundary, then apply those later migrations in order and recheck the catalog at the tip. The supplied history snapshot gives 81 migrations through target. Run assertions in each database and exit nonzero on a failed command or assertion. Close psql sessions then remove only the owned container in `finally` and preserve the original command error if cleanup also fails. Run the new command against this target. The historical command asserts its own migration tip.

Create shops A and B in both modes. Give each its own customer/phone row for recipient X (`447700900101`). Use `447700900102` for the second recipient Y. Seed three distinct recoveries for X and one `RECOVERY` conversation per recovery, A1 and A2 for shop A, and B1 for shop B. Link recovery conversations via `checkoutRecoveryId` using the existing recovery ownership rules. Seed two old messages with receipts `wamid.fixture.A1` and `wamid.fixture.B1`. For A1, seed a `RecoveryOutreachAttempt` with `sequence=1`, `trigger=INITIAL`, `status=PENDING` and `configuredOfferMode=NONE`. Add a test `public."PlatformConfiguration"` row with `environment='test'`, `key='messaging.sender'`, version `3` and the fake sealed envelope shape from `scripts/test-arch043-platform-configuration-postgres.mjs`. Capture all fixture-row columns via `to_jsonb`, ordered by ID. After upgrade compare equality for every row, excluding only the two introduced fields on `ConversationMessage`, and assert those fields are SQL NULL. Assert all five new tables start empty. Insert a message through the old writer shape with both dispatch fields omitted and verify both read SQL NULL. Insert a message with both fields set and verify the exact pair. Exercise each half-filled pair separately. Then enrol enabled senders S1 (`100000001`, priority 0) and S2 (`100000002`, priority 1) under WABA `900000001`. Isolate the distinct-sender and shared-sender cases in different fixtures.

Inspect the names and definitions in the frozen SQL. Expect five new primary keys, eight foreign keys, thirteen CHECKs (including the dispatch pair), nine explicit indexes (six partial), and one user-defined identity trigger/function. Read the generated `Prisma.dmmf.datamodel.models` for the field names, types, nullability, defaults, relation targets and inverses. Inspect PostgreSQL catalogs for SQL-only objects. Check schema/table, ordered keys, predicate, uniqueness, FK actions, and CHECK meaning. Catalog representations may have casts or normalized expressions. For each expected violation, assert SQLSTATE **and the applicable named constraint/index**, with isolated failed statements so a prior transaction error cannot satisfy the case. Duplicate live thread/route, membership primary key, and duplicate inbound/prompt IDs return `23505`. Wrong route/thread identity and deleting a referenced sender return `23503`. Negative priority, non-digit/too-short sender or WABA IDs, malformed recipient within VARCHAR(15), reversed time order, invalid state, incomplete dispatch pair, inconsistent prompt evidence/scope and self-parent return `23514`. The immutability trigger raises `23514` with message `Immutable WhatsApp pool sender identity` rather than setting a `CONSTRAINT_NAME`.

Use two independent PostgreSQL backend sessions plus an observer for contention, following `scripts/arch040-postgres-lock-sessions.mjs`. Session A inserts an uncommitted open (X,S1) thread. Session B attempts the same key with a different ID. The observer must see B waiting on A via `pg_blocking_pids` before A commits. The contender then gets `23505`, leaving one thread. Repeat on a different fixture key with A rolling back. B succeeds, leaving only B's row. Keep statements with expected failure inside a savepoint or a PL/pgSQL exception block. Use the active-route and membership cases to test conditional old-generation updates and non-unique shared-sender occupancy. Exercise the allowed SQL representation for positive membership, coexisting roots, terminal scrubs and stale compare-and-set. Sender ranking, shop eligibility, payload bounds, expiry scheduling, prompt scope immutability through the worker, and AI decisions are Background behaviour. Use the single prescribed DB trigger. Check writer-owned behaviour through fixture state and conditional updates. No provider connection is needed.

Verify these lifecycle cases in both modes.

1. Check PostgreSQL catalog definitions using `pg_get_expr`, `pg_get_indexdef` and `pg_constraint`. Verify closed historical routes can coexist for the same shop and recipient, and that customers can reuse a sender across shops and across recipients.
2. Insert merchants A and B on the same X/S1 thread. A second active A route for X must conflict on either S1 or S2. Two independent checkout conversations A1 and A2 join A's route. B1 joins B's route. Y's own S1 thread succeeds. Also represent X using different senders for A and B in a separate fixture. A route with a different recipient or sender from its thread fails the composite foreign key. After a concurrent claim/release, assert one current route per shop/customer and an open parent for every current membership.
3. Release A1 alone, then release A2 and close only A's original route. B and the X/S1 thread survive with their original generation. Closing B's last member and route closes that original thread. A subsequent X/S1 admission gets a new thread ID. Historic quotes still trace to the earlier thread, merchant and basket. Delayed closes and conditional updates on the old IDs leave the new generation untouched. Validate canonical phone grammar, negative priority rejection, close-after-open constraints, immutable enrolled phone/WABA and normal priority/drain edits. Delete a merchant and verify its own routes/members disappear while another merchant's records, the shared thread and its unrelated questions survive. Deleting an inventory row that still has any thread fails.
4. Under an open shared thread insert two distinct inbound roots with routeId NULL and separate children. Enforce unique inbound and prompt provider IDs. Pin only the intended root/chain to proven route B, leaving the other unresolved. Admit a neutral prompt, then bind its turn to B; its promptScopeRouteId remains NULL in normal writer operation. Prove the CHECK rejects shop-specific prompt evidence before admission or for a different selected shop. Preserve a scoped historic prompt stamp after physical merchant deletion; it cannot be rebound. Resolve a merchant-selection control using the original provider ID without inserting a merchant ConversationMessage. Check terminal content scrub, RESOLVED role markers, IGNORED input SQL NULL and full lifecycle after parent/selected conversation deletion. Check pending-age index and thread/state/time index, original released historical proof, receipt consistency and waiter predicates. With zero enabled inventory for a new route, persist the sequence-1 PENDING waiter with the specified failure code. A positive count of occupied enabled numbers with no idle number is a normal shared admission.

### ERD and execution evidence

The supplied schema contains 138 Prisma models and the tracked PUML has 108 entities before ARCH-076. Follow the scoped generator workflow from ARCH-068-DATABASE-001. In a temporary copy run the existing `npm run erd:puml` against the pre-change schema, save that output, repeat against the patched schema, and take only the ARCH-076 changes. From the generated delta add the five new entities, their actual Prisma relations (including the turn self-relation), and the two fields of `ConversationMessage` to the tracked `docs/generated/prisma-erd.puml`. Include the three new inverse fields if the generator represents them in its entity blocks. Route and prompt-scope stamps remain scalar text. Render the scoped tracked file with `npm run erd:png`. The PUML’s `@startuml erd` produces `docs/generated/erd.png`. Inspect that the PNG is non-empty, opens, and corresponds to that PUML. Save the generated before/after copies outside the repository. Only the scoped PUML and its rendered PNG belong in the change set.

The architect authorises the Database agent to run the bounded, single-container PostgreSQL test for this task once per implementation attempt under `docs/agent-validation-execution-policy.md`. Capture exit status, separate fresh/upgrade results, observed blocking and cleanup. For Prisma checks that only validate or generate, use the loopback fixture URL below. The PostgreSQL runner creates and connects to its own isolated databases.

```bash
(
  set -euo pipefail
  export DATABASE_URL=postgresql://postgres:fixture_only@127.0.0.1:1/sender_pool_schema_only
  npm run prisma:validate
  npm run prisma:generate
  npm run test:sender-pool:schema
  npm run test:sender-pool:postgres
  npm run lint
  npm run erd:png
  test -s docs/generated/erd.png
  git diff --check
)
```

Record each command and any actual failing SQLSTATE or Prisma error in the Completion Report. If the environment prevents an acceptance command, record it as pending with its exact command. Acceptance requires both fresh and populated-upgrade evidence.

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

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Current-main definition review — 15 November 2026

Architect read-only compatibility review against Database `2e14f866` found no conflicting Prisma anchor, table, foreign-key target or prescribed SQL name. The predecessor has 80 migration SQL files ending at `20261113111320_arch075_meta_app_operation_state`; the prescribed unused `20261113120000_whatsapp_sender_pool` target is the 81st through that migration. Upgrade fixtures replay all 80 predecessors and preserve the existing `ConversationDeliveryPart`, `ConversationDeliveryStatusReceipt` and Meta operation-state tables/rows in addition to the ordinary seeded ownership, consent, billing and message rows. Expected source counts are 138 Prisma models and 108 tracked PUML entities before this task.

The SQL contract remains five new tables, eight foreign keys, thirteen CHECKs, nine explicit indexes (six partial) and one identity trigger/function. Required fresh/upgrade/concurrency validation belongs to the Database implementation attempt; this read-only definition review is not evidence those tests passed.

DATABASE-001 is independently Ready: it supplies sender-pool storage only. The same-Conversation renewed-credit amendment belongs to separate DATABASE-002 and BACKGROUND-005 definitions and does not authorize adding allowance fields or billing policy here. No downstream task is promoted by this definition review. No implementation worktree, claim, schema migration or live mutation has been performed by the architect.
