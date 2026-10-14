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

One authoritative PostgreSQL `Conversation` and ordered message stream, accessed through two merchant UIs. Hosted `moda-interact-api` owns central merchant conversation reads and commands. Shopify authenticates access to its existing merchant app and issues a **server-only, short-lived, shop-bound assertion** to the hosted API; WooCommerce uses its existing WordPress `manage_woocommerce` capability, nonce checks and server-side installation authentication. Both resolve one authoritative `shopId` at the hosted API. Neither introduces per-staff identities, custom Moda roles, assignment or conversation-level permissions. No provider or server-to-server secret is exposed to a browser.

A synchronous, versioned PostgreSQL handover transaction changes the authoritative mode before acknowledging Take Over. `MerchantConversationSendCommand` durably records a send request; it does **not** confer permission to send: the authenticated `shopId`, current `controlMode=HUMAN`, and `controlRevision` determine whether the request is admitted/dispatched. Background checks that mode/version at final outbound admission. Human send requests are authenticated, deduplicated and durably accepted into a transactional command/outbox record before Background dispatches through the established WhatsApp delivery and provider-status pipeline. A human message enters the same `ConversationMessage` stream. Read APIs return bounded shop-scoped inbox/message pages and eligibility, not raw tenant-spanning telemetry. No direct WordPress connection to Moda PostgreSQL, Redis or secret material.

For a **post-window follow-up**, the command path atomically claims the same recovery sequence-2 attempt whether initiated by HUMAN or AGENT/AUTOMATION. The confirmation/credit lifecycle remains owned by Background and existing recovery billing; it is not replicated by the Shopify or Woo UI. Any active-window replies are ordinary messages subject to mode, provider and entitlement rules; they do not masquerade as new outreach attempts.

### Request / event flow

```text
Customer WhatsApp -> Messaging ingress -> Background -> ConversationMessage(INBOUND)
                                                       -> lastInboundAt/window update
Shopify authenticated server --signed merchant assertion--+
                                                           v
Woo WP nonce/capability -> server-side installation auth -> Hosted API
                                                           |
                           +-- read inbox + messages ------+-- PostgreSQL (shop scoped)
                           +-- Take Over / Resume AI ------+-- mode/version + audit CAS
                           +-- Send Human Reply ------------+-- durable command/outbox
                                                                  |
                                                                  v
                                                       Background send consumer
                                                         |    |    |
                                                         |    |    +-- 24h/template policy
                                                         |    +------- shared recovery sequence-2 claim and credit
                                                         +------------ existing outbound WhatsApp delivery
                                                                        |
                                                                        v
                                                               SAME ConversationMessage history
```

## Data model

- `Conversation`: persisted `AI`/`HUMAN` mode, monotonically increasing control revision, change timestamps and immutable mode-transition history (without individual staff identifiers). Do not create a new conversation because of handover or follow-up.
- `ConversationMessage`: preserves existing sender types; `HUMAN` is sufficient human authorship attribution, without new human staff identity columns. Relate to the admitted send command/attempt if required. Never confuse author with the recovery credit identity.
- `RecoveryOutreachAttempt`: continue sequence 1 (initial) and sequence 2 (only follow-up); record whether HUMAN, AGENT or AUTOMATION initiated sequence 2, together with delivery/credit identity and safe retry state; do not persist a staff principal. Keep unique `(checkoutRecoveryId, sequence)` and validated message-to-conversation association.
- Durable merchant command/outbox (or equivalently correct existing primitive): unique idempotency key scoped to shop, immutable conversation ID and expected control revision; persisted acceptance/result and bounded dispatch/retry state. No correct-only-in-Redis state.
- Pre-production development: use normal Prisma migrations to create a fresh schema. Historical-data migration, backfill, old-queue compatibility and rollback rehearsals are not required for this initiative.

## Concurrency and consistency

- Takeover/Resume is an authorised monotonic compare-and-set transaction with audit history. Releasing AI must not resurrect stale agent responses from earlier mode revisions.
- At final send admission, AI generation must verify current mode/revision; protect the provider handoff against takeover in the defined ordering boundary. An already submitted Meta request cannot be cancelled.
- Human message requests carry stable idempotency identity. A duplicate request returns the original operation; a conflicting payload for the same key fails. Never send during API request/database transaction.
- Human and AI follow-up claim must use the same `RecoveryOutreachAttempt` sequence 2 and shared credit source key. Concurrent claim wins one record; loser returns an explicit already-used/conflict result.
- Most-recent verified inbound controls customer-service-window eligibility. Server clock and bounded provider timestamp skew must be considered. Do not infer service-window opening from an outbound template.
- Disconnected Woo installations, invalid WordPress nonce/capability, invalid Shopify app sessions, expired shop assertions, cross-shop conversation IDs and stale control revisions fail closed.

## Repository responsibilities and execution plan

| ID | Owner | Bounded outcome | Dependencies |
|---|---|---|---|
| ARCH-040-DATABASE-001 | moda_database | Durable conversation control + human audit fields | — |
| ARCH-040-DATABASE-002 | moda_database | Single follow-up provenance and invariants | DATABASE-001 |
| ARCH-040-DATABASE-003 | moda_database | Durable human command/outbox schema | DATABASE-001 |
| ARCH-040-SHARED-001 | moda_shared | Versioned control/read/message/send contracts | DATABASE-001, DATABASE-002, DATABASE-003 |
| ARCH-040-SHARED-002 | moda_shared | Publish accepted Shared contracts | SHARED-001 |
| ARCH-040-GATEWAY-001 | moda_gateway | Safe API/Shopify assertion environment wiring | SHARED-002 |
`ARCH-040-API-001 | moda_api | Shopify-to-hosted API shop assertion verifier | SHARED-002 |
| ARCH-040-API-002 | moda_api | Tenant-scoped paginated inbox and message reads | SHARED-002, DATABASE-001 |
| ARCH-040-API-003 | moda_api | CAS Take Over / Resume AI command | API-001, DATABASE-001, SHARED-002 |
| ARCH-040-API-004 | moda_api | Idempotent merchant send admission/outbox | API-003, DATABASE-003, DATABASE-002 |
| ARCH-040-BACKGROUND-001 | moda_background | AI turn/send handover fencing | DATABASE-001, SHARED-002 |
| ARCH-040-BACKGROUND-002 | moda_background | Durable human send consumption/provider delivery | API-004, BACKGROUND-001 |
| ARCH-040-BACKGROUND-003 | moda_background | Unified one post-window follow-up and credit flow | DATABASE-002, BACKGROUND-002 |
| ARCH-040-SHOPIFY-001 | moda_app | Session-verified Shopify server API bridge | API-001, API-002, API-003, API-004, GATEWAY-001 |
| ARCH-040-SHOPIFY-002 | moda_app | Customer conversation inbox/read UI | SHOPIFY-001 |
| ARCH-040-SHOPIFY-003 | moda_app | Takeover/release and human composer UI | SHOPIFY-002, BACKGROUND-003 |
| ARCH-040-WOOCOMMERCE-001 | moda_woocommerce | Secure WP REST proxy/read/command facade | API-002, API-003, API-004, ARCH-035-API-013 |
| ARCH-040-WOOCOMMERCE-002 | moda_woocommerce | Native Woo customer inbox and detail transcript | WOOCOMMERCE-001, ARCH-035-WOOCOMMERCE-013 |
| ARCH-040-WOOCOMMERCE-003 | moda_woocommerce | Woo takeover/release and human composer UI | WOOCOMMERCE-002, BACKGROUND-003 |
| ARCH-040-SYSTEM-TEST-001 | moda_system_test | One-thread, takeover race and shared credit E2E | All API/Background/Database/Shared/Gateway implementation |
| ARCH-040-SYSTEM-TEST-002 | moda_system_test | Shopify customer inbox E2E | SHOPIFY-003 + SYSTEM-TEST-001 |
| ARCH-040-SYSTEM-TEST-003 | moda_system_test | Woo customer inbox E2E | WOOCOMMERCE-003 + SYSTEM-TEST-001 |

This is a 22-task provisional plan. Task definitions are **defined but not materialised**: no Git tasks have been launched. Existing `ARCH-035-API-013` and `ARCH-035-WOOCOMMERCE-013` are external readiness gates and must reach `complete`; neither should be silently rewritten or marked complete.

## Gateway and deployment

Reuse existing hosted API, Background, PostgreSQL, Redis/BullMQ and Meta transport. No new chat server, WebSocket or database is required. Gateway task is limited to version-controlled route/secret environment declarations for the new signed Shopify server-to-API assertion, and preproduction/prod isolation if new config is needed. No plaintext secrets in Git. Do not introduce an extra deployment if the inspected topology already satisfies routing.

Deployment order: database migrations -> published Shared contract -> API/Gateway merchant auth and commands -> Background handover/send policy -> Shopify/Woo server facades -> Shopify/Woo UI -> developer manual verification -> terminal independent system tests. Deploy and validate the fresh-development schema and consumers together. Existing provider receipts and durable queues must not be silently discarded if the deployed environment contains them.

## Observability, data protection and failure handling

Use canonical `@modainteract/moda-interact-shared/logging`; correlate shopId, conversationId, commandId, control revision, attemptId, send outcome and provider receipt without raw customer content or credentials. Capture handover conflicts, suppressed stale AI sends, merchant send queue lag, provider rejection and duplicate replay. Reuse approved OpenTelemetry/framework signals, adding only genuine domain telemetry. Bounded message pagination and retention, protected merchant/customer identities, provider-template selection and error states are required. Polling must stop while UI is inactive/disconnected.

## Non-goals

No separate human chat database, no new Conversation per follow-up, no duplication of Meta webhook ingress, no new customer-facing channel, no agent-aided draft mode, no human media/voice attachments, no arbitrary multi-step campaigns, no new billing counter for individual active-window replies, no automatic AI ownership resumption on inbound customer response, and no changes to the Moda platform-support inbox.

## Open considerations before implementation

- Confirm business rule for a human follow-up if the customer had previously engaged but the 24-hour window subsequently closed. The proposed single sequence-2 allowance applies to any eligible closed-window follow-up while recovery remains actionable, not only no-response, while existing scheduled automation retains its no-response intent.
- Confirm whether post-window follow-up templates are individually merchant-selected or chosen from the existing approved recovery template catalogue; first release should reuse the canonical selector.
- Inspect final deployed ARCH-035 Woo detail prerequisites and the real Gateway auth/secret configuration before materialisation. Definitions must not be treated as acceptance of pending ARCH-035 tasks.
- Clarify CommerceAgent automatic escalation policy in a later extension; merchant-initiated takeover and manual release are mandatory for v1.

## Change history

2026-10-14: Drafted from provided workspace snapshot and user agreement. Explicitly preserved one Conversation per recovery generation while recognising initial/follow-up as separate billable outreach attempts, not new threads. No indexes reconciled pending user confirmation of architecture session completion.
