-- U3 standalone lock-mechanism fixture. NOT executed during the snapshot review.
-- Run only inside the disposable PostgreSQL 17 container in the accompanying
-- reproduction protocol. This is deliberately not the application schema.
-- Retained: parent PK, child FK/action/timing, provider-message uniqueness,
-- parent version/pending fields, and child identity/direction/sender/status.
-- Omitted: unrelated columns, enums, indexes, and application triggers. The
-- inspected current INBOUND/null-dispatch-key trigger path takes no parent
-- FOR UPDATE lock and does not eliminate the FK/upgrade interleaving.
\set ON_ERROR_STOP on
CREATE SCHEMA "whatsapp";

CREATE TABLE "whatsapp"."Conversation" (
  "id" text PRIMARY KEY,
  "inboundVersion" integer NOT NULL DEFAULT 0,
  "pendingTurnStartedAt" timestamp(3)
);

CREATE TABLE "whatsapp"."ConversationMessage" (
  "id" text PRIMARY KEY,
  "conversationId" text NOT NULL,
  "providerMessageId" text,
  "direction" text NOT NULL,
  "senderType" text NOT NULL,
  "status" text NOT NULL,
  "content" text NOT NULL,
  "createdAt" timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX "ConversationMessage_providerMessageId_key"
  ON "whatsapp"."ConversationMessage" ("providerMessageId");

-- Same FK definition as the accepted baseline, including omitted DEFERRABLE:
-- PostgreSQL therefore checks it after each statement, not at commit.
ALTER TABLE "whatsapp"."ConversationMessage"
  ADD CONSTRAINT "ConversationMessage_conversationId_fkey"
  FOREIGN KEY ("conversationId")
  REFERENCES "whatsapp"."Conversation" ("id")
  ON DELETE CASCADE ON UPDATE CASCADE;

INSERT INTO "whatsapp"."Conversation" ("id") VALUES ('u3-conversation');

SELECT current_setting('server_version') AS server_version,
       current_setting('server_version_num') AS server_version_num;

SELECT conname, condeferrable, condeferred, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conname = 'ConversationMessage_conversationId_fkey';
