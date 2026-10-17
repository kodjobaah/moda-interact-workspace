---
id: ARCH-040-DATABASE-001
architecture_id: ARCH-040
title: Implement recovery conversation control, follow-up, send commands and restrictions
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-BACKGROUND-001
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SHOPIFY-001
  - ARCH-040-API-004
  - ARCH-040-BACKGROUND-002
  - ARCH-040-ADMIN-001
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-DATABASE-001 — Implement recovery conversation persistence and restrictions

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. The task definition was present in the canonical workspace baseline; developer execution is tracked on the canonical task branch.

## Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-040-DATABASE-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_database`, repository ownership, scope, dependencies, requirements, and acceptance criteria are unchanged. The canonical developer launcher records the execution attempt separately.

## Objective

Implement **all ARCH-040 database persistence in one bounded repository task**: (A) versioned AI/HUMAN control and events, (B) the existing recovery sequence-2 follow-up claim, (C) durable recovery-only human-send commands, and (D) platform-controlled shop-wide human-messaging restrictions and audit. Make one fresh-development schema change, with an integrated PostgreSQL suite. Do not implement application/Background/Admin runtime operations.

## Context

The October 17 snapshot already has one `whatsapp.Conversation` per `CheckoutRecovery` (`@@unique([checkoutRecoveryId])`), a shared message history with `MessageSenderType.HUMAN`, and one `commerce.RecoveryOutreachAttempt` per `(checkoutRecoveryId, sequence)`; neither human takeover nor a follow-up creates another Conversation. `Conversation.shopId` may be null for recovery threads: validate tenancy through `CheckoutRecovery.shopId`. Existing `RecoveryBillingService` credit identity is keyed to the original outreach attempt. The new restriction is distinct from `Shop.status=SUSPENDED` or merchant-editable `ShopFeaturePreference`. DATABASE-002/003/004 have been superseded and their full persistence contracts are consolidated below.

## Scope

- Own all four persistence capabilities within **`moda-interact-database/prisma/schema.prisma`** and required SQL constraints, indexes and trigger definitions.
- Supply **one coherent fresh-database Prisma migration** for the combined ARCH-040 schema; preserve the repository's normal migration ordering and existing unrelated schema.
- Deliver one integrated disposable-PostgreSQL test suite covering each model, FK/tenant integrity, concurrent state changes, immutable audit records, idempotency, follow-up ownership and recovery from claimed commands.
- Preserve existing recovery/WhatsApp/billing records and behaviours; the new send command is an intent/outbox, **not** a second message, conversation, provider receipt, or credit ledger.

## Out of Scope

- No API/controller endpoints, Shopify or WooCommerce interface, Admin control UI, Background worker, provider networking, billing charge execution, or new Shared package publication.
- No new merchant accounts/staff identity/assignment, separate Conversations inbox, generic standalone conversation sending, or new scheduled follow-up campaign.
- No historical-data migration/backfill/compatibility/rollback rehearsal for this pre-production rollout; do perform normal clean-database migrations.
- No `docs/decisions/**/_index.md` updates until the user explicitly closes this architecture session.

## Requirements

### A — Conversation mode and immutable transition history

### Exact Prisma schema contract

Add these *new* declarations; keep existing fields and constraints unchanged:

```prisma
enum ConversationControlMode {
  AI
  HUMAN
  @@schema("whatsapp")
}

// New fields on existing Conversation:
controlMode         ConversationControlMode @default(AI)
controlRevision     Int                     @default(0)
controlChangedAt    DateTime?               @db.Timestamptz(3)
controlEvents       ConversationControlEvent[]
// No new standalone-inbox index in ARCH-040; recovery reads use CheckoutRecovery(shopId, ...).

model ConversationControlEvent {
  id              String                            @id @default(cuid())
  conversationId  String
  conversation    Conversation                      @relation(fields: [conversationId], references: [id], onDelete: Cascade)
  fromMode        ConversationControlMode
  toMode          ConversationControlMode
  fromRevision    Int
  toRevision      Int
  occurredAt      DateTime                          @default(now()) @db.Timestamptz(3)

  @@unique([conversationId, toRevision])
  @@index([conversationId, occurredAt, id])
  @@schema("whatsapp")
}

// For a recovery-linked OUTBOUND message admitted through the canonical provider path,
// add optional dispatch evidence on existing ConversationMessage; no second message row:
// providerDispatchKey String? @unique @db.VarChar(128)
// providerDispatchAdmittedAt DateTime? @db.Timestamptz(3)
// providerDispatchControlRevision Int?
// Legacy/unrelated messages may leave these null. Existing senderType=HUMAN identifies merchant replies.
```

- `controlMode=AI`, `controlRevision=0`, and null transition timestamps represent an existing thread that has never been taken over. `controlRevision` must never decrease or reset; `controlChangedAt` updates on **every actual transition**. Audit history retains takeover/resume timestamps and mode transitions without redundant `humanTakenOverAt` state or naming an individual operator. Treat `ConversationControlEvent` as insert-only for normal application roles: protect from UPDATE/direct DELETE (via privileges or triggers) while allowing explicitly authorised parent-record erasure according to retention policy.
- `ConversationControlEvent` represents exactly one real mode transition (`AI -> HUMAN` or `HUMAN -> AI`); `toRevision = fromRevision + 1`, revisions nonnegative. Repeated no-op requests do not insert an event or increment the revision. Add PostgreSQL `CHECK` constraints for the scalar invariants that Prisma cannot express.
- Authenticated Shopify server actions and the Woo-hosted API will perform `updateMany`/CAS on `(Conversation.id, controlRevision, controlMode)` and insert the matching `ConversationControlEvent` **inside the same PostgreSQL transaction**. A CAS winner must commit both updates or neither; concurrent stale writers update zero rows. The database task provides the schema and tests to support this, not the API endpoint itself.
- Authentication and tenant authorisation remain the responsibility of Shopify/WooCommerce and the hosted API. The database stores no Shopify staff ID, WordPress user ID or source-platform identifier for mode transitions. `ConversationControlEvent` records mode/revision/time only; it is not a per-user audit log.
- Keep `ConversationMessage.senderType` untouched: `HUMAN` represents the merchant response; `AGENT`/`AUTOMATION` remain distinct. Do not create `humanActorPlatform`, `humanActorSubject`, a separate author table or an alternative message history. Existing provider-status updates must continue to work.
- Preserve `Conversation @@unique([checkoutRecoveryId])`. A recovery conversation's effective tenant comes from `CheckoutRecovery.shopId` if its own `Conversation.shopId` is null; standalone conversations use `Conversation.shopId`. Do not make `Conversation.shopId` nonnullable or filter recovery threads only by this nullable field.
- Retain existing message ordering indexes. ARCH-040 has no standalone conversation inbox; recovery detail queries use `CheckoutRecovery(shopId, ...)` and the recovery conversation unique relation. Do not introduce a speculative `[shopId, controlMode, lastMessageAt, id]` index or duplicate a unique left-prefix. Existing non-recovery conversations remain unchanged in behaviour, but are not in scope for human takeover/send.

### Development-only schema delivery

- **Pre-production, fresh database only.** Add the Prisma schema and the repository's normal schema-creation migration for fresh databases. No upgrade scripts, compatibility adapters, historical human-message backfill, historical-data preflight, data-preservation rehearsal, or rollback plan are required for ARCH-040.
- Create the single control enum, `Conversation` control fields, `ConversationControlEvent`, and required SQL checks/indexes/triggers. Validate a clean database built from the repository's standard migrations; existing schema identity and one-conversation cardinality remain the intended model.
- Keep the existing author enum for newly inserted `HUMAN` outbound messages. No per-user attribution or legacy-data accommodation is required. Use fresh representative fixtures for CUSTOMER, AGENT, AUTOMATION and HUMAN.
- Do not introduce a second thread or a parallel message history as a shortcut to schema changes.

### B — Recovery sequence-2 shared follow-up claim and credit identity

- ARCH-040 merchant follow-ups remain recovery-only. Preserve the scheduled `NO_RESPONSE_FOLLOW_UP` suppression after customer response. A merchant-initiated post-window attempt after previous engagement is **not** converted into a newly scheduled automatic follow-up; apply recovery eligibility and the existing unique sequence-2 claim. Neither branch can create sequence 3.

### Exact Prisma extension

```prisma
enum RecoveryOutreachInitiator {
  HUMAN
  AGENT
  AUTOMATION
  @@schema("commerce")
}

// Extend existing RecoveryOutreachTrigger with:
// POST_WINDOW_FOLLOW_UP
// Keep INITIAL and NO_RESPONSE_FOLLOW_UP for existing records/automated no-response.

// Add nullable fields on existing RecoveryOutreachAttempt:
initiatedBy           RecoveryOutreachInitiator?
initiationKey         String? @unique @db.VarChar(255)
claimedAt             DateTime? @db.Timestamptz(3)
```

- `sequence=1` stays `trigger=INITIAL`; `sequence=2` is the only permitted follow-up. Its trigger can be `NO_RESPONSE_FOLLOW_UP` for the existing automatic no-response schedule or `POST_WINDOW_FOLLOW_UP` for an otherwise eligible manual/AI post-window initiation. **Trigger describes the reason, `initiatedBy` describes the author**; never infer which actor sent the message solely from `trigger`.
- `initiationKey` is the stable durable **logical follow-up claim identity**, not the outbound Meta message ID and not the recovery credit reservation ID. A winning claim atomically writes `initiatedBy`, `initiationKey` and `claimedAt`. No staff principal or source-platform fields are persisted for any initiator. The key and initiator fields are immutable once populated. Use PostgreSQL constraints/trigger protection for set-once provenance; allow normal status/receipt reconciliation.
- The existing unique `(checkoutRecoveryId, sequence)` ensures **one** sequence-2 row per recovery; a conditional update against unclaimed `initiationKey IS NULL` ensures **one** initiator wins. If an automated job has created an unclaimed PENDING sequence-2 row first, a later human may atomically claim **that same row**, but cannot replace a winner. Do not treat an `upsert(..., update: {})` as ownership of the claim.
- Once claimed, any retry must reuse the original sequence-2 `id`, `initiationKey`, sender/author identity, and deterministic outbound and credit identities. Provider-uncertain sends remain claimed until reconciled; do not clear `initiationKey` after timeouts. A definitively failed send is not billable and may be retried only under the same logical attempt, according to BACKGROUND-001 policy as integrated by BACKGROUND-002; never create a fresh sequence-2 row or second distinct claim.
- Maintain existing provider-message relation. Add a PostgreSQL **constraint trigger** on setting/changing `outboundMessageId` that proves `ConversationMessage.conversationId` points to the `Conversation` whose `checkoutRecoveryId` equals this attempt's `checkoutRecoveryId`; a normal Prisma FK alone does not enforce this cross-table condition.
- Add `CHECK` rules: `sequence IN (1,2)`; sequence/trigger pairing; claim presence consistency (`initiationKey`, `claimedAt`, `initiatedBy` are collectively null or nonnull); `initiatedBy` restricted to HUMAN/AGENT/AUTOMATION (no staff actor fields). A claimed sequence-2 row does **not** need a sent message yet. Keep existing `PENDING`/`FAILED`/`CAPACITY_BLOCKED` states and `sentAt` unchanged: they express delivery lifecycle, not the right to claim. Preserve the existing `@@unique([outboundMessageId])` and existing indexes; add an index only if an actual query needs one not covered by them.
- **Credit invariant:** follow-up credit stays `createRecoveryIdempotencyKey(shopId, "recovery-outreach:" + outreachAttempt.id)` through existing `RecoveryBillingService`. Schema must neither charge by `initiationKey`, `HUMAN` staff identifier, nor create a new recovery-conversation record. One initial outreach may consume one recovery credit; successful sequence 2 consumes one more credit for the **same conversation thread**.

### Development-only schema delivery

- **Fresh development database only:** extend the existing `RecoveryOutreachAttempt` model and create its SQL checks/triggers through the repository's normal migrations. Do not implement historic sequence-2 initiator backfill, legacy-data inspection, upgrade-repair logic or rollback procedures.
- Fresh seed fixtures must cover sequence-1 INITIAL, unclaimed sequence-2 PENDING, and claimed sequence-2 by HUMAN/AGENT/AUTOMATION. A newly created sequence-2 row may start unclaimed; its claim fields become populated atomically when one initiator wins.
- Do not weaken `(checkoutRecoveryId, sequence)` uniqueness or the same-conversation `outboundMessageId` validation to simplify test setup.

### C — Durable recovery-only human message send command

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
  DISPATCH_ADMITTED
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
  // Authoritative provider admission is distinct from the worker lease.
  providerDispatchKey   String?                          @unique @db.VarChar(128)
  providerDispatchAdmittedAt DateTime?                    @db.Timestamptz(3)
  providerDispatchControlRevision Int?
  providerDispatchRestrictionRevision Int?
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

Add the inverse Prisma relation fields required on `Shop`, `Conversation`, `ConversationMessage` and `RecoveryOutreachAttempt`, plus the optional provider-dispatch evidence fields expressly defined in C.1 on the canonical `ConversationMessage`; do not change identity or cardinality. The command is a **send intent/outbox**, not another `ConversationMessage` or a provider receipt. Its `outboundMessageId` is filled only when the canonical WhatsApp admission has created or reconciled the actual outbound message.

### Identity, payload, tenancy and immutability

- `idempotencyKey` is scoped to **shop** (unique `[shopId, idempotencyKey]`). Shopify/Woo clients cannot reuse a key for different content to obtain a second send. Replays with identical canonical payload, shop, conversation, recipient snapshot, expected revision and template data return the same command; any mismatch yields a conflict. API-004 computes `payloadSha256` from a canonical, versioned request representation; the DB stores a fixed 64-hex fingerprint. Do not store a client-provided digest as trusted validation.
- Retain the server-authorised `shopId`, exact `conversationId`, control revision, and immutable effective recipient at acceptance. No actor-platform/subject fields are needed. Avoid a mutable, broad JSON bag for the top-level identity. Only `templateParameters` are structured JSON, bounded by the API's reviewed size limits. Human text is stored as intended content, not rendered HTML; no secret/token fields.
- `kind=HUMAN_TEXT` requires nonblank `textBody`, null template fields and null `recoveryOutreachAttemptId`. Both command kinds require `Conversation.checkoutRecoveryId IS NOT NULL`; no standalone conversation sends are admitted. `kind=RECOVERY_FOLLOW_UP_TEMPLATE` requires null text, nonblank approved template name/language and **one** `recoveryOutreachAttemptId` whose `sequence=2`. The database enforces shape and relational integrity; approval/service-window/eligibility validation remains API-004 and BACKGROUND-001/002 responsibility.
- Add PostgreSQL checks for nonnegative revision/attempt count, nonblank bounded key/recipient, exactly one payload shape, valid digest syntax, and lease token/expiry consistency. Add set-once/immutable protection for identity and accepted payload fields, including `recoveryOutreachAttemptId` after acceptance; only dispatch state/lease/retry/result fields may advance.
- **Critical tenant check:** a PostgreSQL validation trigger for `MerchantConversationSendCommand` requires an associated `CheckoutRecovery` and proves command `shopId` equals `CheckoutRecovery.shopId`. Reject commands targeting a conversation with null `checkoutRecoveryId`, and reject conflicting nonnull `Conversation.shopId` rather than accepting it via `COALESCE`. The same trigger verifies `recoveryOutreachAttempt.checkoutRecoveryId` equals the command conversation recovery, and `outboundMessage.conversationId` equals the command `conversationId`. Reject cross-shop FK combinations even if all referenced rows exist.
- Never create a new `Conversation` or `CheckoutRecovery` when inserting a command. Existing message rows keep `senderType=HUMAN` without individual operator metadata; the command links to the exact outbound message after provider admission.

### Transaction and worker lease contract

- API-004 writes a newly validated send command and, for a follow-up, claims/links the existing unique sequence-2 attempt **in the same database transaction**. A conflicting/replayed idempotency key must not claim another follow-up, charge again, or alter the original payload. HTTP success means the command committed; no Redis or network call is made inside that transaction.
- `ACCEPTED -> CLAIMED` is a compare-and-set lease acquisition (`leaseToken`, `leaseExpiresAt`, `dispatchAttemptCount`); only the matching current lease token can finish the claim. After lease expiry, only a never-dispatch-admitted command is reclaimable with a new token; an admitted/UNKNOWN command is reconciled without a second Meta submission. A stale worker cannot commit a provider result over the current claimant.
- `DISPATCH_ADMITTED` is a durable provider-send permission and not evidence of delivery; `UNKNOWN` is for ambiguous provider disposition, **not a licence to send again**. Recovery must first reconcile the existing provider/idempotency/message evidence; `SENT` records successful provider submission while `ConversationMessage` tracks DELIVERED/READ/FAILED receipt evolution. Definitive pre-provider failures may be retried under the **same command and source identities** only when policy permits; `CANCELLED` and terminal failure must not be silently resent.
- The polling index must permit bounded searches by state and due time while respecting lease expiry. API response reads and shop-specific history use the shop/conversation/date index. Never use unbounded table scans, in-memory-only job identity, or deletion of dedupe keys to recover an operation.
- Retention: preserve idempotency tombstones/terminal command identities for at least the documented replay horizon; cleanup must not make a previously accepted idempotency key reusable while the original provider/credit outcome can still be retried or reconciled. For v1, do not purge command/deduplication records; a later approved retention policy must define replay horizon and reconciliation-safe cleanup.

### C.1 — Mandatory cross-actor provider-admission persistence (not a new sender)

- **State distinction:** `ACCEPTED` is a committed merchant intent; `CLAIMED` is a revocable worker lease; `DISPATCH_ADMITTED` is the durable, one-way provider-submission permit; `SENT` means the existing Meta provider accepted a request. `DELIVERED`/`READ` remain on the linked `ConversationMessage`, not command states. Only a matching current lease can request the one-way transition into `DISPATCH_ADMITTED`; expiry/restart of an already admitted command must **not** submit a second provider request.
- Store `providerDispatchKey` (stable, globally unique for the logical provider submission), `providerDispatchAdmittedAt`, frozen `providerDispatchControlRevision`, and for HUMAN the observed active restriction revision (0 if the restriction row is absent). Set all permit fields **atomically once** with `DISPATCH_ADMITTED` and the canonical `ConversationMessage` dispatch evidence in a short transaction, while checking the current conversation mode/revision and relevant restriction against the frozen command/turn. An AI/AUTOMATION recovery outbound writes equivalent optional dispatch evidence on its **existing canonical `ConversationMessage`**, so both actors participate in the same final admission contract; do not create a second message, credit or dispatch table. The provider adapter receives only the admitted canonical message/identity.
- **Precedence:** For mode changes and outbound admission, serialize on the recovery `Conversation` row. For HUMAN suspension checks where the optional shop restriction row is absent, serialize the shop/merchant restriction creation and admission using the same shop-row lock. Use a documented deadlock-safe lock order (shop row when required -> recovery/conversation -> command/attempt/message), and a consistent short transaction for all three cases. No Meta HTTP or Redis call inside any database transaction. Admission committed before takeover/suspension may still result in a later HTTP request; admission **after** takeover/suspension must fail. Do not present this as an absolute cancellation guarantee.
- **Admitted-but-unknown:** If a process crashes after durable admission, even before a local transport result is persisted, the outcome is conservative `UNKNOWN` until existing provider status/idempotency evidence establishes the result. Do not infer the request was never made, release the permit, roll the command back to `ACCEPTED`, or blindly send again. Reconcile using existing provider receipt identifiers where available; if Meta does not support safe lookup/idempotent replay for that request, quarantine for operational review. Permit, command, message and credit identities remain stable.
- Add SQL `CHECK`/set-once constraints for the permit tuple, state transition ordering, digest/revision bounds and immutable dispatch identity; allow documented recovery handling `DISPATCH_ADMITTED -> SENT/UNKNOWN/FAILED` but never a second permit for the same command/message. Verify `MerchantConversationSendCommand.providerDispatchKey` equals the linked `ConversationMessage.providerDispatchKey` when present and both belong to the same recovery. No platform discriminator, platform-specific queue reference or duplicate `ConversationMessage` record.
- **Retention:** For the first release, do not schedule command/idempotency deletion. A future retention job needs a separate reviewed replay horizon and proof that no pending/provider-unknown outcome can be resurrected. Reclaim only leases *before* dispatch admission; preserve admitted tombstones.


### D — Platform-controlled shop human-messaging restriction

### Explicit data model

- `HumanMessagingRestrictionStatus = ACTIVE | SUSPENDED`; absent restriction row means ACTIVE (existing shops allowed by default). Do not derive this status from billing entitlements, user preferences, or `Shop.status`.
- `ShopHumanMessagingRestriction`: `shopId` primary/unique FK to `Shop`, `status`, `revision` (integer, monotonic), `reasonCode` (bounded), `reasonNote` (bounded, nullable, admin-only), `suspendedAt`, `restoredAt`, `updatedAt`. Once created, **never delete the row on restoration**; this prevents revision reset and stale replay.
- `ShopHumanMessagingRestrictionEvent`: immutable event ID, `shopId`, `fromStatus`, `toStatus`, `revision`, `reasonCode`, optional bounded `reasonNote`, `platformAdminId` FK to `PlatformAdmin`, `createdAt`; indexed by `(shopId, createdAt, id)`. No individual merchant staff identifiers. Existing administrative principal is legitimate because this is a *platform* action.
- Enforce only supported status values, unique shop restriction, unique `(shopId, revision)` event, bounded reasons and any nullable/timestamp invariants supported by Prisma/SQL. The event records the reason for **both** suspension and restoration.
- Updates use atomic compare-and-set plus event insertion in one PostgreSQL transaction and serialize the initial absent-row creation (e.g., lock the Shop row). A concurrent admin update yields a stable stale-revision conflict. `ACTIVE -> SUSPENDED -> ACTIVE -> SUSPENDED` revisions keep increasing.
- Use an explicit scoped lookup keyed by server-authenticated shop ID. Reads reveal only public status to merchant boundaries; admin-only notes and events must never reach merchant API DTOs.
- No irreversible deletion of records/receipts or conversion of existing `Conversation.controlMode`.

### Integrated schema and transaction invariants

- Use **one Prisma schema and one fresh-schema migration** that create the four compatible persistence capabilities together. Do not create sequential ARCH-040 database work items or duplicate migrations merely to mimic the superseded task boundaries.
- `Conversation.controlMode/controlRevision` and `ConversationControlEvent` must CAS-transition atomically. `RecoveryOutreachAttempt` is the only sequence-2 claim. A `MerchantConversationSendCommand` for a template follow-up must refer to that same recovery's attempt and Conversation. `ShopHumanMessagingRestriction` must retain a monotonic revision after restoration.
- Cross-model consistency checks must cover null `Conversation.shopId`, actual `CheckoutRecovery.shopId`, recovery/message/attempt association, immutable accepted intent and administrative audit, and failure/race recovery. Provider/network calls are prohibited inside database transactions.
- Preserve independent operational responsibilities: Admin owns privileged suspend/restore commands; API/Shopify server own shop-authenticated acceptance; Background owns final admission/WhatsApp/credit processing. The database owns persistence and constraints only.

### Follow-up claim transition matrix (shared HUMAN/automation)

| Existing sequence-2 state | Durable transition | Result |
|---|---|---|
| Absent | Insert `sequence=2` once, then claim within the same transaction | One attempt and one original recovery credit source |
| Existing unclaimed PENDING (including scheduled no-response) | Compare-and-set `initiationKey IS NULL`, set winner and only approved `trigger`/recipient/template snapshot fields atomically | HUMAN may take the same unclaimed row; no new attempt |
| Already claimed by HUMAN/AGENT/AUTOMATION | Preserve initiator, original trigger and snapshots | A different claimant loses; matching idempotent retry returns prior result |
| Provider dispatch admitted or UNKNOWN | Retain command/attempt/credit identity | Reconcile; no competing claim or blind second send |
| Definitively unsent failure | Retry same logical command/attempt if existing policy permits | No new claim, outbound identity or credit |
| Confirmed send / consumed follow-up | Terminal claim | No further follow-up for the recovery |

The claim transaction must bind the selected provider-approved follow-up template and frozen recipient under the recovery's current eligibility. It may replace **unclaimed scheduled** sequence-2 scheduling metadata only if no existing provider submission/claim has occurred; it must not overwrite a claimed offer, sender, recipient or provider receipt. Preserve automatic `NO_RESPONSE_FOLLOW_UP` suppression after any customer reply and recovery terminal-state checks. HUMAN initiation after earlier engagement is a deliberate post-window action, not an extra automatic campaign.


## Work Items

### A — Conversation mode and immutable transition history

- [ ] Add the `ConversationControlMode` enum and only `controlMode`, `controlRevision`, `controlChangedAt` to existing `Conversation`; keep indexes proven necessary for existing reads.
- [ ] Add `ConversationControlEvent` with conversation FK, unique revision, bounds/checks and ordered retrieval index.
- [ ] Verify existing `ConversationMessage.senderType=HUMAN` persists and remains distinguishable from `AGENT`/`AUTOMATION`; add no author columns.
- [ ] Add the schema-creation migration for a fresh disposable development database; no historical preflight, backfill, rollback or upgrade coverage.
- [ ] Add focused PostgreSQL integration fixtures for recovery (nullable conversation shopId), transition history and coexistence with existing non-recovery Conversation rows; do not implement standalone human controls.

### B — Recovery sequence-2 shared follow-up claim and credit identity

- [ ] Preserve the canonical sequence-1/sequence-2 unique key and add `POST_WINDOW_FOLLOW_UP` trigger variant without replacing existing enum values.
- [ ] Add initiator/claim fields, matching checks, set-once protections, and unique initiationKey.
- [ ] Add cross-table constraint trigger protecting outboundMessageId from belonging to another conversation/recovery.
- [ ] Add the fresh-database schema migration and seed-based constraints/tests; no historical attempt backfill or data-repair tooling.
- [ ] Add focused concurrency and FK/constraint tests for competing HUMAN vs AUTOMATION/AGENT claims.

### C — Durable recovery-only human message send command

- [ ] Create the exact `MerchantConversationSendCommand` model and enums with inverse relations, FK rules, indexes and default states.
- [ ] Add checked payload shapes, revision/digest/lease bounds, and immutable accepted-command identity constraints.
- [ ] Enforce recovery-only command admission, CheckoutRecovery-derived shop identity and same-attempt/same-message association in PostgreSQL.
- [ ] Add the fresh-database schema migration; no pre-existing conversation/message backfill, historical-data repair or upgrade path.
- [ ] Add PostgreSQL acceptance/replay, crash/reclaim, concurrent lease, cross-tenant, payload-integrity and retention-identity tests.

### D — Platform-controlled shop human-messaging restriction

- [ ] Implement the restriction enum, one-row-per-shop model, immutable admin audit model, FK/index/uniqueness constraints.
- [ ] Implement fresh database migration and keep existing recovery, message, and billing models intact.
- [ ] Prove atomic upsert/CAS monotonic revision and event insertion under concurrent admins and restore/re-suspend.
- [ ] Test default ACTIVE for legacy/fresh shops and absence of merchant-visible admin reason notes.

### Combined delivery

- [ ] Deliver one normal fresh Prisma migration and one comprehensive PostgreSQL validation report for all four work packages.
- [ ] Verify no duplicate persisted conversation, message, follow-up or recovery-credit ledger; no forbidden staff identities or stand-alone send capability.
- [ ] Record the one-task worktree isolation, start synchronisation and validation evidence in this task’s Completion Report.

## Interfaces / Contracts

`ARCH-040-DATABASE-001` is the **sole authoritative persistence contract** for:

- `ConversationControlMode`, `Conversation` control fields, and `ConversationControlEvent`;
- `RecoveryOutreachInitiator`, `RecoveryOutreachAttempt` follow-up claim fields and `POST_WINDOW_FOLLOW_UP` trigger;
- `MerchantConversationSendKind`, `MerchantConversationSendState`, `MerchantConversationSendCommand`;
- `HumanMessagingRestrictionStatus`, `ShopHumanMessagingRestriction`, and `ShopHumanMessagingRestrictionEvent`.

`API-002/003/004`, `SHOPIFY-001`, `BACKGROUND-001/002`, and `ADMIN-001` consume those canonical Prisma definitions. They retain their own API/transaction/runtime requirements; these are **not** independently implemented by the database agent. The WooCommerce plugin uses its existing hosted API and never directly imports Prisma or accesses PostgreSQL. Database models do not encode individual merchant staff identities. The existing `ConversationMessage` and `RecoveryOutreachAttempt` remain canonical for messages and credit identities.

## Dependencies

None.

## Enables

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-BACKGROUND-001
- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SHOPIFY-001
- ARCH-040-API-004
- ARCH-040-BACKGROUND-002
- ARCH-040-ADMIN-001

- [ ] The final provider-send permit exists as durable, immutable evidence for both HUMAN commands and canonical automated recovery outbound messages, distinct from `CLAIMED`, with one stable dispatch identity and no network I/O in its transaction.
- [ ] Fresh PostgreSQL contention tests prove mode/suspension-vs-admission ordering and admission-before-takeover residual race; a restarted worker cannot reissue an admitted/UNKNOWN provider send.
- [ ] The unclaimed sequence-2 row may be won once by HUMAN or automation with atomic trigger/recipient/template consistency; no overwrite of a claimed row or second credit identity.

## Acceptance Criteria

### A — Conversation mode and immutable transition history

- [ ] No redundant `humanTakenOverAt` and no standalone-conversation inbox index were added; controlChangedAt and immutable transition events suffice to reconstruct handovers.
- [ ] Existing non-recovery Conversation records and their current behaviour remain valid, but ARCH-040 does not enable human commands for them.

- [ ] In fresh PostgreSQL fixtures, each recovery retains **exactly one** `Conversation.id` through initial outreach, follow-up and human/AI replies; default control mode is AI/revision 0. The schema does not create extra conversations.
- [ ] Two concurrent transitions from revision N can commit at most one N -> N+1 event and one mode update; losing CAS returns zero updated rows; no gaps or duplicate events.
- [ ] `AI -> HUMAN -> AI -> HUMAN` produces revisions 1, 2, 3 and three immutable mode-transition audit records; the last takeover timestamp reflects revision 3.
- [ ] Real no-op takeover/resume does not increment revision or append another event.
- [ ] Outbound HUMAN message persists with `senderType=HUMAN` on the existing Conversation; no staff attribution fields are required. Other sender types and delivery-status updates remain valid.
- [ ] Recovery tenant ownership remains resolvable through `CheckoutRecovery.shopId` even when `Conversation.shopId IS NULL`; a shop cannot gain access by relying on a nullable conversation field.
- [ ] In a fresh deployment, `@@unique([checkoutRecoveryId])`, message ordering/indexes and recovery/provider message relationships remain valid; no second conversation is created by a follow-up.

### B — Recovery sequence-2 shared follow-up claim and credit identity

- [ ] Two competing initiators for the same recovery produce one `sequence=2` attempt and exactly one durable claimant; losing claimant cannot overwrite the winning actor/claim key.
- [ ] A row inserted as unclaimed PENDING may be claimed by one initiator; a claimed or provider-uncertain row cannot be re-claimed as another person's follow-up.
- [ ] An initial outreach and one follow-up still reference the **same existing Conversation** and independently identified messages; attempting to attach a foreign-conversation message fails at PostgreSQL level.
- [ ] Existing `status`, `sentAt`, provider message ID, credit reservation/source identity, and retry semantics remain usable; a provider-status update cannot mutate initiator evidence.
- [ ] Fresh schema rejects sequence 3, mismatched sequence/trigger pairs, invalid actor/claim combinations and attempts to change a winning claim.
- [ ] No new usage reservation/conversation row is introduced merely by claiming sequence 2; one confirmed follow-up is counted by existing recovery billing exactly once, independent of sender.

### C — Durable recovery-only human message send command

- [ ] Command insertion for a standalone/PRODUCT_SUPPORT conversation is rejected even if that Conversation has a nonnull `shopId`; recovery tenant association derives from `CheckoutRecovery.shopId`.
- [ ] Outbound delivery and provider receipts remain canonical in `ConversationMessage` and existing Background transport; this command is only durable intent, not a duplicate message/credit ledger.

- [ ] For the same shop/idempotency key, concurrent inserts yield exactly one durable command; a changed payload with that key conflicts instead of silently replaying or resending.
- [ ] A committed ACCEPTED command is discoverable after a simulated API crash before queue publication and can be leased by Background without reconstructing intent from memory.
- [ ] Two dispatchers cannot hold a valid lease simultaneously; an expired lease can be reclaimed, and a stale token cannot finalise or overwrite a later claim.
- [ ] A command for a conversation owned by a different shop fails in PostgreSQL, including nullable `Conversation.shopId` on recovery threads; similarly wrong-recovery follow-up attempt/message references are rejected.
- [ ] Human text vs approved-template intent storage is mutually exclusive; immutable shop/recipient/payload/revision fields cannot be rewritten after admission, but valid state/provider-result updates succeed.
- [ ] A human sequence-2 command can bind **only** the existing recovery's sequence-2 attempt and actual message in its one Conversation; no second follow-up record or recovery-credit ledger is introduced.
- [ ] Idempotency and result history survive retry/retention operations without duplicate sends or accidental recreation of accepted keys.

### D — Platform-controlled shop human-messaging restriction

- [ ] One shop has at most one current restriction and a complete immutable audit trail.
- [ ] An absent row is treated as ACTIVE; restoration does not reset revision or delete history.
- [ ] Concurrent conflicting admin updates cannot silently overwrite each other.
- [ ] Suspension state is independent of AI/HUMAN conversation mode, shop status, subscription and credits.

### Integrated persistence

- [ ] An existing recovery has **exactly one** Conversation and one sequence-2 follow-up candidate, independent of AI/HUMAN message authorship and restriction state.
- [ ] Fresh migration builds all models/checks/indexes/triggers together and allows safe consumer adoption after one architect acceptance; there is no separate database gate.
- [ ] A suspension prevents HUMAN admission/dispatch only when enforced by owning consumers; the database holds durable status and never mutates AI mode or billing automatically.

## Validation

### A — Conversation mode and immutable transition history

- [ ] Run the repository's actual Prisma validate and generate commands.
- [ ] Apply migrations to an empty disposable PostgreSQL instance; seed recovery, standalone and mixed-author message fixtures and verify defaults, FK associations and indexes. No upgrade-migration rehearsal.
- [ ] PostgreSQL negative constraint and concurrent CAS+audit transaction tests including failed transaction rollback and HUMAN/nonhuman message status updates.
- [ ] Compare Prisma schema to applied SQL constraints/indexes and run `git diff --check`.
- [ ] Record canonical task-worktree, launcher synchronization and submodule evidence in Completion Report.

### B — Recovery sequence-2 shared follow-up claim and credit identity

- [ ] Prisma validate and generate client for the new schema.
- [ ] Apply migrations to an empty disposable PostgreSQL database; seed PENDING, FAILED, SENT and CAPACITY_BLOCKED sequence-2 records and verify constraints. No historic/upgrade fixtures.
- [ ] Parallel transaction race tests (one HUMAN and one AUTOMATION), claim immutability, no third sequence, malformed initiator cases, cross-conversation message association, and idempotent rerun.
- [ ] Confirm `@@unique([checkoutRecoveryId, sequence])` and `outboundMessageId` uniqueness work on a clean database; run `git diff --check`.
- [ ] Record isolated task-worktree and migration/submodule synchronization evidence.

### C — Durable recovery-only human message send command

- [ ] Prisma schema validate and client generation.
- [ ] Apply migrations to an empty disposable PostgreSQL database; seed recovery and standalone threads and mixed-author messages, then verify command references. No upgrade-migration or data-preservation tests.
- [ ] Transactional integration tests for unique shop-scoped replay vs conflict, cross-shop recovery and standalone links, wrong-attempt/message linking, and command payload invariants.
- [ ] Lease CAS/expiry/reclaim simulation, API-crash-before-publication simulation, ambiguous provider outcome, terminal key retention tests.
- [ ] Inspect all actual indexes/triggers and run `git diff --check`; record canonical isolated worktree/synchronization evidence.

### D — Platform-controlled shop human-messaging restriction

- [ ] Prisma validate plus fresh-db migration replay
- [ ] PostgreSQL race/constraints/foreign-key tests
- [ ] Read/restore/re-suspend audit and privacy tests
- [ ] git diff --check and task worktree evidence

### Combined checks

- [ ] Prisma validate/generate; full clean disposable PostgreSQL migration; combined constraints, indexes and FK checks.
- [ ] Concurrency/race suite for control mode CAS, sequence-2 competing claims, send-command idempotency/leasing, admin suspend/restore revisions, and cross-recovery/tenant FK enforcement.
- [ ] `git diff --check`, all scoped tests, and task worktree/branch preparation evidence.

## Stop Condition

After implementing and validating **all four persistence packages within this one task**, complete this task's Completion Report, set it to `review`, return control to `moda_architect`, and STOP. Do not start Background, API, Shopify, WooCommerce or Admin implementation.

## Implementation Notes

The individual models remain modular inside `schema.prisma`; do not build a generic chat domain or extra services. Reuse existing PostgreSQL/Prisma multi-schema naming and fixtures, database-level checks and existing follow-up/credit identities. If a proposed additional mechanism duplicates an established reusable capability, return that finding to moda_architect rather than implementing it. All task write paths are workspace-relative, and normal task isolation/synchronisation evidence remains required. No `_index.md` edits. The superseded DATABASE-002/003/004 definitions are retained only for traceability; this combined task replaces their execution.

## Completion Report

### Status

Changes Requested — Developer Self-Review of Attempt 1. The task is returned to `ready`; attempt remains 1 and no new attempt has been claimed. Explicit completion is not approved because required provider-admission and idempotency race evidence is incomplete, and the implementation adds an upgrade-validation path contrary to this task's fresh-database-only validation scope.

### Files Changed
- `moda-interact-database/package.json`
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261017120000_arch040_recovery_human_handover/migration.sql`
- `moda-interact-database/scripts/validate-arch040-recovery-human-handover.mjs`
- `moda-interact-database/scripts/test-arch040-recovery-human-handover-postgres.mjs`

### Work Completed
- Added the conversation control mode/revision and audit-event schema, recovery sequence-2 initiator/claim fields, recovery-only merchant send-command schema, platform restriction/audit schema, and one combined Prisma migration with PostgreSQL checks and triggers.
- Added structural and disposable-PostgreSQL validation scripts. The fresh suite exercises migration replay, control CAS, follow-up claimant race, command constraints/lease and UNKNOWN handling, and restriction revision/audit behavior.
- Implementation is committed and published as `345b3ee` on `task/ARCH-040-DATABASE-001`; the canonical implementation worktree was clean and tracked its remote task branch at review. Current `origin/main` has one commit not yet incorporated into this task branch; the next attempt must perform the canonical start synchronization.

### Validation Results
- PASS: `node_modules/.bin/prisma validate --schema prisma/schema.prisma` (Prisma 6.19.3).
- PASS: `node_modules/.bin/prisma generate --schema prisma/schema.prisma`.
- PASS: `node scripts/validate-arch040-recovery-human-handover.mjs`.
- PASS: `node scripts/test-arch040-recovery-human-handover-postgres.mjs --mode fresh` (50 migrations applied; integrated suite passed; disposable container removed).
- PASS: ESLint for both ARCH-040 validation scripts with `--max-warnings=0`.
- PASS: `git diff --check origin/main...HEAD` on the implementation task branch.
- `corepack pnpm exec` was initially blocked by `ERR_PNPM_IGNORED_BUILDS`; the validation commands above were then run successfully through the local executables. The optional upgrade mode was not run because upgrade rehearsal is outside this task's validation scope.

### Deviations
- The implementation adds and registers `--mode upgrade` fixtures that insert pre-migration records and replay the ARCH-040 migration, although the task explicitly limits validation to a fresh database and says not to perform an upgrade-migration rehearsal.
- The PostgreSQL suite does not prove the required mode/restriction-versus-admission lock ordering or the admission-before-takeover residual race. It exercises mode CAS and restriction-update races separately, and exercises one HUMAN command admission, but does not contend those operations with admission.
- Automated recovery outbound admission is not exercised against the canonical `ConversationMessage` dispatch-evidence contract. Command idempotency is tested sequentially rather than with competing inserts; stale-token completion after lease reclamation is also not tested.

### Assumptions
Consumer transactions will take locks in the migration's documented shop -> recovery Conversation -> command/attempt/message order, with no network call inside a database transaction. That ordering is not yet demonstrated by the committed PostgreSQL contention suite.

### Unresolved Issues
- Required admission-ordering, automated dispatch-evidence, concurrent idempotency, and stale-lease regression evidence listed in `Developer Self-Review - Changes Requested`.
- Remove the upgrade rehearsal mode/script or obtain an explicit architect-approved scope amendment before retaining it.

### Architectural Concerns
No API, Background, Shopify, or Admin runtime operations were added. Downstream dependency promotion is deferred until this task receives an accepted review and explicit developer completion.

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

## Developer Self-Review - Changes Requested

### Decision

Attempt 1 does not pass self-review. Return the task to `ready` with `executor: null`, `claimed_at: null`, and `attempt: 1`. Do not claim Attempt 2 as part of this review. The implementation and its existing validation remain available on the task branch.

### Corrections Required

1. Keep ARCH-040 validation fresh-database-only. Remove the upgrade-mode historical-fixture/replay path and its package command; retain the fresh migration test and verify the clean migration chain.
2. Add deterministic disposable-PostgreSQL contention tests for both orderings of recovery provider admission versus conversation takeover, including the documented residual case where admission commits first and a later takeover cannot revoke the already-issued permit.
3. Add deterministic HUMAN admission contention tests against suspension, including initial restriction-row creation when no row exists. Verify the shop-row lock serializes absence/creation with admission, and that admission after suspension commits no dispatch permit.
4. Exercise an AI/AUTOMATION recovery outbound through the same canonical `ConversationMessage` dispatch-evidence fields and prove the operation creates no duplicate message or credit identity.
5. Race two command inserts using the same shop/idempotency key and prove exactly one durable intent wins. Reclaim an expired pre-admission lease, then prove the stale token cannot change the new claimant's state or result.

### Evidence Reviewed

- Reviewed the full task-owned implementation diff and migration in the canonical implementation worktree, plus the focused structural and PostgreSQL test scripts.
- Prisma validation/generation, structural validation, focused ESLint, fresh disposable-PostgreSQL suite, and implementation diff check passed as recorded in the Completion Report.
- The implementation task branch is clean and published at `345b3ee`. Current `origin/main` has the separate commit `87e7458` not incorporated; the next attempt must synchronize through the canonical launcher workflow before changes.
- Parent task branch changes for this review are limited to this task definition/report. No downstream task was promoted because this task is not complete.
