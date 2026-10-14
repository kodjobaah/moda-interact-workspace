---
id: ARCH-040
title: Merchant customer conversations and human handover
status: proposed
coordinator: moda_architect
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040: Merchant customer conversations and human handover

## Status

Proposed — portable architecture/task definitions for discussion. No task branches, worktrees, commits, pushes or implementation are claimed. This initiative does **not** supersede the existing recovery lifecycle or Shopify/WooCommerce UI parity programmes.

## Problem

Moda already persists a WhatsApp `Conversation` and `ConversationMessage` history and produces automated checkout-recovery and CommerceAgent replies. Merchants cannot yet own that customer thread and send human messages from Shopify/WooCommerce. The existing outbound admission accepts `AGENT | AUTOMATION`, while the database already recognises `HUMAN`. Concurrent human takeover, AI processing, follow-up admission, and credit accounting require one consistent authority.

## Agreed invariants

1. **ONE conversation for each CheckoutRecovery generation.** Its `checkoutRecoveryId` is unique; initial outreach, AI turns, human turns and follow-up are messages on that same `Conversation.id`. No follow-up or takeover creates a `Conversation`. A *different* recovery generation may have another conversation under the existing lifecycle; this initiative does not silently change that rule.
2. **Message author is independent of conversation identity.** Preserve `ConversationMessage.senderType` (`CUSTOMER`, `AGENT`, `AUTOMATION`, `HUMAN`); identify human replies by `senderType=HUMAN` without storing staff identities or introducing Moda merchant accounts; existing store authentication is sufficient.
3. **Human takeover is always available** to a merchant using the connected store’s existing authenticated administration interface. The takeover is durable and versioned, and it blocks subsequent automated sending until explicitly released. It does not bypass a terminal recovery, WhatsApp restrictions or subscription/entitlement checks.
4. **One eligible post-window follow-up per recovery** across human and AI initiation; use the same unique sequence-2 outreach attempt. This consumes one *recovery-conversation credit*, not a new `Conversation` row. Initial outreach remains sequence 1. Ordinary permitted replies inside the customer-service window do not each consume another recovery-conversation credit.
5. **24-hour window is based on the most recent authenticated CUSTOMER inbound WhatsApp message**, not on the time of the initial outbound recovery template. When closed, a proactive follow-up requires a provider-approved template; free-form text is not sent. The existing follow-up timing/configuration must be reconciled to this new rule rather than silently retained.
6. **Credits and provider delivery are idempotent.** Follow-up ownership is by recovery/outreach-attempt identity, not sender. Reserve before provider dispatch; use existing confirmed-send/compensation semantics and reconcile uncertain results. Repeated clicks, queue retries, handovers and cross-channel concurrent attempts must not add a second follow-up or duplicate charge.
7. **Provider-send precedence is fenced.** If handover commits before final outbound admission, an AI send is suppressed; if a provider request was irreversibly dispatched first, it cannot be recalled. Surface this bounded race honestly in the UI and tests.
8. **AI mode and Human mode only for v1.** Draft suggestions/assist mode, media attachments, arbitrary new outbound campaigns, staff accounts/assignment, per-staff permissions, and live push sockets are out of scope. Polling is an acceptable v1 refresh approach.

## Verified 2026-10-14 code baseline

- `moda-interact-database/prisma/schema.prisma`: `Conversation @@unique([checkoutRecoveryId])`, `CheckoutRecovery.conversation Conversation?`, `ConversationMessage.senderType` with `HUMAN`; `RecoveryOutreachAttempt @@unique([checkoutRecoveryId, sequence])` and `outboundMessageId`.
- `moda-interact-background/src/services/conversation.service.ts`: `getOrCreateRecoveryConversation` uses `prisma.conversation.upsert({where: {checkoutRecoveryId}, update: {}})`.
- `moda-interact-background/src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`: selects the existing `recovery.conversation` and calls `sendTemplate({conversationId: recovery.conversation.id, idempotencyKey: recovery-outreach:<attempt.id>, ...})`; it does not create another conversation.
- `moda-interact-background/src/services/outbound-whatsapp-admission/outbound-whatsapp-admission.types.ts`: sender type is restricted to `AGENT | AUTOMATION`; human messages require a deliberate safe route, not a cast into existing agent admission.
- Shopify recovery-detail provides read-only history. Woo ARCH-035 recovery-detail implementation is staged (list, detail shell, hosted read API and subsequent wiring); avoid hiding pending ARCH-035 work inside ARCH-040.
- Existing ARCH-016 follow-up is defined as a no-response follow-up with configurable timing; extend/reconcile its semantics rather than creating a parallel human allowance.

## Proposed architecture

**Shopify and WooCommerce have distinct authenticated application boundaries, but share the same database and Background runtime.**

- **Shopify:** The existing `moda-interact` application authenticates the shop through its current Shopify admin session and reads/updates canonical Prisma records in its own **server-side** loaders/actions. It never calls `moda-interact-api` for ARCH-040 and needs no signed shop assertion, new staff identity or Gateway secrets.
- **WooCommerce:** The WordPress plugin authenticates its local WP-admin operator with its existing `manage_woocommerce` capability and nonce. PHP proxies to the existing hosted `moda-interact-api` using the existing Woo installation ID and Bearer installation credential; the API verifies active shop/installation and authorizes Prisma data by effective shop. The WordPress browser and merchant-hosted PHP never connect directly to Moda PostgreSQL or Redis.
- **Shared runtime:** Both paths write the **same** `Conversation.controlMode/controlRevision` + `ConversationControlEvent` and `MerchantConversationSendCommand`/`RecoveryOutreachAttempt` schema. Background processes the durable commands and the agent turns through the common Meta WhatsApp delivery, receipts, recipient and recovery-billing mechanism. There are no per-staff permissions, duplicate HTTP schemas in Shared, or second chat service.

A human Take Over is a PostgreSQL compare-and-set transition that commits before success is returned. Human sends are accepted into a durable command/outbox and not sent synchronously. Both Shopify and Woo must use identical request semantics and database transaction invariants; only the authentication/HTTP boundary differs. No browser or WordPress PHP receives provider credentials.

### Request / event flow

```text
Customer WhatsApp -> Messaging ingress -> Background -> same ConversationMessage

Shopify admin -> existing Shopify session -> Shopify app server -> Prisma PostgreSQL
                                                        |         |
                                                        |         +-- inbox/messages/control
                                                        +------------ durable send command

Woo WP admin -> WP nonce/capability -> WP PHP proxy -> hosted Woo API
                                                       |  existing Woo installation auth
                                                       v
                                                    Prisma PostgreSQL
                                                       |-- inbox/messages/control
                                                       +-- durable send command

Shared durable command/outreach attempt -> Background dispatcher
                                           |-- mode/revision + 24h window fence
                                           |-- same recovery sequence-2 follow-up/credit
                                           +-- Meta transport -> same ConversationMessage
```

**No new Shopify-to-hosted-API assertion or Gateway environment/secret integration is required.** `ARCH-040-API-001` and `ARCH-040-GATEWAY-001` are superseded records, not implementation dependencies.

## Data model

- `Conversation`: persisted `AI`/`HUMAN` mode, monotonically increasing control revision, change timestamps and immutable mode-transition history (without individual staff identifiers). Do not create a new conversation because of handover or follow-up.
- `ConversationMessage`: preserves existing sender types; `HUMAN` is sufficient human authorship attribution, without new human staff identity columns. Relate to the admitted send command/attempt if required. Never confuse author with the recovery credit identity.
- `RecoveryOutreachAttempt`: continue sequence 1 (initial) and sequence 2 (only follow-up); record whether HUMAN, AGENT or AUTOMATION initiated sequence 2, together with delivery/credit identity and safe retry state; do not persist a staff principal. Keep unique `(checkoutRecoveryId, sequence)` and validated message-to-conversation association.
- Durable merchant command/outbox (or equivalently correct existing primitive): unique idempotency key scoped to shop, immutable conversation ID and expected control revision; persisted acceptance/result and bounded dispatch/retry state. No correct-only-in-Redis state.
- Pre-production development: use normal Prisma migrations to create a fresh schema. Historical-data migration, backfill, old-queue compatibility and rollback rehearsals are not required for this initiative.

## Contract ownership decision (2026-10-14, revised)

`moda-interact-database`/Prisma owns persisted conversation, messages, control, outreach attempts, and durable merchant send-command model. No new ARCH-040-specific `moda-interact-shared` schemas or publication gate. `SHARED-001/002` remain superseded.

For **WooCommerce only**, `moda-interact-api` owns HTTP validation, response formats, error codes, cursor semantics and route tests using the existing `WooInstallationAuthenticator`. `ARCH-040-API-001`, previously planned to add Shopify assertion verification, is **superseded**. `ARCH-040-API-002/003/004` are independently testable Woo read, handover and send-admission tasks. `moda-interact-woocommerce` owns the authenticated WordPress REST facade and native Woo UI.

For **Shopify**, `moda-interact` owns the server-side loaders/actions and shop scoping via the existing Shopify admin session and direct Prisma database access. It does not call the hosted merchant API. `SHOPIFY-001` is the server-side read/command capability; `SHOPIFY-002/003` are the separate inbox and human-control UI tasks.

`moda-interact-background` consumes durable Prisma send commands from either platform, using the same queue/WhatsApp provider transport; Background does not depend on completion of the Woo HTTP API to implement the relay. Already-published Shared logging and unrelated packages remain in use. `ARCH-040-GATEWAY-001` is **superseded** because there is no new Shopify assertion/secret/route to deploy; a future observed routing gap would require a specific new architectural decision.

There are **22 task records: 18 active, 4 superseded** (`SHARED-001/002`, `API-001`, `GATEWAY-001`). No new sign-in flow, Shopify API assertion or API package publication is required.

## Concurrency and consistency

- Takeover/Resume is an authorised monotonic compare-and-set transaction with audit history. Releasing AI must not resurrect stale agent responses from earlier mode revisions.
- At final send admission, AI generation must verify current mode/revision; protect the provider handoff against takeover in the defined ordering boundary. An already submitted Meta request cannot be cancelled.
- Human message requests carry stable idempotency identity. A duplicate request returns the original operation; a conflicting payload for the same key fails. Never send during API request/database transaction.
- Human and AI follow-up claim must use the same `RecoveryOutreachAttempt` sequence 2 and shared credit source key. Concurrent claim wins one record; loser returns an explicit already-used/conflict result.
- Most-recent verified inbound controls customer-service-window eligibility. Server clock and bounded provider timestamp skew must be considered. Do not infer service-window opening from an outbound template.
- Disconnected Woo installations, invalid WordPress nonce/capability, invalid Shopify app sessions, cross-shop conversation IDs and stale control revisions fail closed.

## Repository responsibilities and execution plan

| ID | Owner | Bounded outcome | Dependencies |
|---|---|---|---|
| ARCH-040-DATABASE-001 | moda_database | Durable control mode, revision, audit | — |
| ARCH-040-DATABASE-002 | moda_database | Existing sequence-2 follow-up claim/provenance | DATABASE-001 |
| ARCH-040-DATABASE-003 | moda_database | Durable idempotent human send command/outbox | DATABASE-001 |
| ARCH-040-SHARED-001 | moda_shared | **SUPERSEDED** redundant contract | — |
| ARCH-040-SHARED-002 | moda_shared | **SUPERSEDED** publication gate | — |
| ARCH-040-API-001 | moda_api | **SUPERSEDED** Shopify assertion | — |
| ARCH-040-API-002 | moda_api | Woo-only inbox/detail/message reads | DATABASE-001 |
| ARCH-040-API-003 | moda_api | Woo-only control CAS Take Over/Resume | DATABASE-001 |
| ARCH-040-API-004 | moda_api | Woo-only idempotent human send acceptance | API-003, DATABASE-002, DATABASE-003 |
| ARCH-040-BACKGROUND-001 | moda_background | Fence AI against human takeover | DATABASE-001 |
| ARCH-040-BACKGROUND-002 | moda_background | Consume DB commands/provider dispatch from either platform | DATABASE-003, BACKGROUND-001 |
| ARCH-040-BACKGROUND-003 | moda_background | One shared follow-up claim/credit | DATABASE-002, BACKGROUND-002 |
| ARCH-040-GATEWAY-001 | moda_gateway | **SUPERSEDED** Shopify assertion secret/wiring | — |
| ARCH-040-SHOPIFY-001 | moda_app | Session-authenticated Shopify server Prisma reads/commands | DATABASE-001, DATABASE-002, DATABASE-003 |
| ARCH-040-SHOPIFY-002 | moda_app | Shopify merchant inbox/readonly thread UI | SHOPIFY-001 |
| ARCH-040-SHOPIFY-003 | moda_app | Shopify takeover and reply composer UI | SHOPIFY-002, BACKGROUND-003 |
| ARCH-040-WOOCOMMERCE-001 | moda_woocommerce | WP REST proxy to existing Woo hosted API | API-002, API-003, API-004, ARCH-035-API-013 |
| ARCH-040-WOOCOMMERCE-002 | moda_woocommerce | Native Woo customer inbox and detail thread | WOOCOMMERCE-001, ARCH-035-WOOCOMMERCE-013 |
| ARCH-040-WOOCOMMERCE-003 | moda_woocommerce | Woo takeover and human reply composer | WOOCOMMERCE-002, BACKGROUND-003 |
| ARCH-040-SYSTEM-TEST-001 | moda_system_test | Integrated shared runtime, both producer boundaries and credit | All DB, Woo API-002/003/004, Background-001/002/003, Shopify-001 |
| ARCH-040-SYSTEM-TEST-002 | moda_system_test | Shopify customer inbox E2E | SHOPIFY-003, SYSTEM-TEST-001 |
| ARCH-040-SYSTEM-TEST-003 | moda_system_test | Woo customer inbox E2E | WOOCOMMERCE-003, SYSTEM-TEST-001 |

All tasks remain **portable definitions** rather than Git task branches. `ARCH-035-API-013` and `ARCH-035-WOOCOMMERCE-013` are unchanged external prerequisites; neither is assumed complete.

## Gateway and deployment

Reuse existing hosted Woo API ingress, Shopify app ingress, Background, PostgreSQL, Redis/BullMQ and Meta transport. **No Gateway task, new signing secret, new public API route for Shopify, separate chat deployment, database or WebSocket is required.** If future implementation establishes a concrete Woo API routing gap, document and route it to `moda_architect` rather than reviving the superseded Shopify assertion Gateway task.

Development delivery order: fresh Prisma schema -> shared Background protections and command relay; in parallel, Woo hosted API and Shopify server actions after their database dependencies -> Woo WordPress proxy and Shopify/Woo UI -> manual developer verification -> terminal independent system tests. No historical data backfill, compatibility adapters or legacy migration rehearsals for this pre-production initiative; do not delete durable runtime data inadvertently.

## Observability, data protection and failure handling

Use canonical `@modainteract/moda-interact-shared/logging`; correlate shopId, conversationId, commandId, control revision, attemptId, send outcome and provider receipt without raw customer content or credentials. Capture handover conflicts, suppressed stale AI sends, merchant send queue lag, provider rejection and duplicate replay. Reuse approved OpenTelemetry/framework signals, adding only genuine domain telemetry. Bounded message pagination and retention, protected merchant/customer identities, provider-template selection and error states are required. Polling must stop while UI is inactive/disconnected.

## Non-goals

No separate human chat database, no new Conversation per follow-up, no duplication of Meta webhook ingress, no new customer-facing channel, no agent-aided draft mode, no human media/voice attachments, no arbitrary multi-step campaigns, no new billing counter for individual active-window replies, no automatic AI ownership resumption on inbound customer response, and no changes to the Moda platform-support inbox.

## Open considerations before implementation

- Confirm business rule for a human follow-up if the customer had previously engaged but the 24-hour window subsequently closed. The proposed single sequence-2 allowance applies to any eligible closed-window follow-up while recovery remains actionable, not only no-response, while existing scheduled automation retains its no-response intent.
- First release uses the existing approved recovery follow-up template catalogue/selector, not arbitrary browser-selected template names.
- Inspect final ARCH-035 Woo detail prerequisites and existing Woo API route patterns before materialisation. Pending ARCH-035 tasks are not assumed accepted.
- Clarify CommerceAgent automatic escalation policy in a later extension; merchant-initiated takeover and manual release are mandatory for v1.

## Change history

2026-10-14: Drafted from provided workspace snapshot and user agreement. Explicitly preserved one Conversation per recovery generation while recognising initial/follow-up as separate billable outreach attempts, not new threads. No indexes reconciled pending user confirmation of architecture session completion.

2026-10-14: Superseded ARCH-040-SHARED-001/002; Prisma remains the durable model, Woo hosted API owns Woo HTTP contracts, Background consumes persisted commands; Shared logging remains.

2026-10-14: Corrected app boundaries: Shopify uses authenticated app server and direct Prisma; Woo alone uses hosted API and existing installation credentials. Superseded API-001/GATEWAY-001, detailed Woo API-002/003/004, and removed Background dependence on Woo API implementation.
