---
id: ARCH-040
title: Merchant customer conversations and human handover
status: proposed
coordinator: moda_architect
created: 2026-10-14
updated: 2026-10-15
---

# ARCH-040: Merchant customer conversations and human handover

## Status

Proposed — portable architecture/task definitions for discussion. No task branches, worktrees, commits, pushes or implementation are claimed. This initiative does **not** supersede the existing recovery lifecycle or Shopify/WooCommerce UI parity programmes.

## Problem

Moda already persists a WhatsApp `Conversation` and `ConversationMessage` history and produces automated checkout-recovery and CommerceAgent replies. Merchants cannot yet own that customer thread and send human messages from Shopify/WooCommerce **on the existing Recovery Detail screen, alongside checkout basket information**. The existing outbound admission accepts `AGENT | AUTOMATION`, while the database already recognises `HUMAN`. Concurrent human takeover, AI processing, follow-up admission, and credit accounting require one consistent authority.

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

- **Shopify:** The existing `moda-interact` application authenticates the shop through its current Shopify admin session and extends **`/app/recoveries/:recoveryId`** and its existing Recovery Detail server-side loaders/actions to show saved basket and existing transcript. It never calls `moda-interact-api` for ARCH-040 and needs no signed shop assertion, new staff identity or Gateway secrets.
- **WooCommerce:** The existing `Recoveries > Recovery Detail` plugin screen is extended with basket, transcript and human controls; no new inbox/menu. The WordPress plugin authenticates its local WP-admin operator with its existing `manage_woocommerce` capability and nonce. PHP proxies to the existing hosted `moda-interact-api` using the existing Woo installation ID and Bearer installation credential; the API verifies active shop/installation and authorizes Prisma data by effective shop. The WordPress browser and merchant-hosted PHP never connect directly to Moda PostgreSQL or Redis.
- **Shared runtime:** Both paths write the **same** `Conversation.controlMode/controlRevision` + `ConversationControlEvent` and `MerchantConversationSendCommand`/`RecoveryOutreachAttempt` schema. Background processes the durable commands and the agent turns through the common Meta WhatsApp delivery, receipts, recipient and recovery-billing mechanism. There are no per-staff permissions, duplicate HTTP schemas in Shared, or second chat service.

A human Take Over is a PostgreSQL compare-and-set transition that commits before success is returned. Human sends are accepted into a durable command/outbox and not sent synchronously. Both Shopify and Woo must use identical request semantics and database transaction invariants; only the authentication/HTTP boundary differs. No browser or WordPress PHP receives provider credentials.

### Request / event flow

```text
Customer WhatsApp -> Messaging ingress -> Background -> same ConversationMessage

Shopify admin -> existing Shopify session -> Shopify app server -> Prisma PostgreSQL
                                                        |         |
                                                        |         +-- recovery detail/messages/control
                                                        +------------ durable send command

Woo WP admin -> WP nonce/capability -> WP PHP proxy -> hosted Woo API
                                                       |  existing Woo installation auth
                                                       v
                                                    Prisma PostgreSQL
                                                       |-- recovery detail/messages/control
                                                       +-- durable send command

Shared durable command/outreach attempt -> Background dispatcher
                                           |-- mode/revision + 24h window fence
                                           |-- same recovery sequence-2 follow-up/credit
                                           +-- Meta transport -> same ConversationMessage
```

**No new Shopify-to-hosted-API assertion or Gateway environment/secret integration is required.** `ARCH-040-API-001` and `ARCH-040-GATEWAY-001` are superseded records, not implementation dependencies.

## Data model

- `Conversation`: persisted `AI`/`HUMAN` mode, monotonically increasing control revision, change timestamps and immutable mode-transition history (without individual staff identifiers). Do not create a new conversation because of handover or follow-up.
- `CheckoutRecovery`: reuse `lineItems Json?` and existing `totalPrice`/`currency` as the saved checkout basket/value snapshot, with optional real variant/quantity/image/price metadata only when present and validated. No new basket schema or live-cart assumption.
- `ConversationMessage`: preserves existing sender types; `HUMAN` is sufficient human authorship attribution, without new human staff identity columns. Relate to the admitted send command/attempt if required. Never confuse author with the recovery credit identity.
- `RecoveryOutreachAttempt`: continue sequence 1 (initial) and sequence 2 (only follow-up); record whether HUMAN, AGENT or AUTOMATION initiated sequence 2, together with delivery/credit identity and safe retry state; do not persist a staff principal. Keep unique `(checkoutRecoveryId, sequence)` and validated message-to-conversation association.
- Durable merchant command/outbox (or equivalently correct existing primitive): unique idempotency key scoped to shop, immutable conversation ID and expected control revision; persisted acceptance/result and bounded dispatch/retry state. No correct-only-in-Redis state.
- Pre-production development: use normal Prisma migrations to create a fresh schema. Historical-data migration, backfill, old-queue compatibility and rollback rehearsals are not required for this initiative.

## Contract ownership decision (2026-10-14, revised)

`moda-interact-database`/Prisma owns persisted conversation, messages, control, outreach attempts, and durable merchant send-command model. No new ARCH-040-specific `moda-interact-shared` schemas or publication gate. `SHARED-001/002` remain superseded.

For **WooCommerce only**, `moda-interact-api` enriches the **existing ARCH-035 Recovery Detail read endpoints** with basket and conversation control (API-002), and owns command HTTP validation, responses and errors (API-003/004) using `WooInstallationAuthenticator`. There is no new generic conversations inbox/list GET endpoint. `ARCH-040-API-001`, previously planned to add Shopify assertion verification, is **superseded**. `ARCH-040-API-002/003/004` are independently testable Woo read, handover and send-admission tasks. `moda-interact-woocommerce` owns the authenticated WordPress REST facade and native Woo UI.

For **Shopify**, `moda-interact` owns the server-side loaders/actions and shop scoping via the existing Shopify admin session and direct Prisma database access. It does not call the hosted merchant API. `SHOPIFY-001` enriches the existing recovery-detail reader/actions; `SHOPIFY-002/003` extend that **same Recovery Detail UI** with basket and human controls. There is no new Conversations navigation item or standalone inbox.

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

### Independently executable streams (2026-10-15)

ARCH-040 has **three independent implementation streams after their applicable database prerequisites**. There is **no dependency in either direction** between `ARCH-040-SHOPIFY-*` and `ARCH-040-WOOCOMMERCE-*`, and Shopify does **not** depend on any `ARCH-040-API-*` task. Only the WooCommerce stream consumes the hosted Woo API.

```text
                            DATABASE
                               |
                +--------------+--------------+
                |              |              |
                v              v              v
            BACKGROUND       SHOPIFY          API (Woo-only)
                |              |              |
                |              |              v
                |              |          WOOCOMMERCE
                |              |              |
                +--------------+--------------+
                               |
                               v
                        SYSTEM TESTS
                  (independent terminal gates)
```

Dependency edges are **prerequisites, not a mandate to run the branches sequentially**:

- **Database -> Background:** `BACKGROUND-001` needs `DATABASE-001`; `BACKGROUND-002` needs `DATABASE-003` and `BACKGROUND-001`; `BACKGROUND-003` needs `DATABASE-002` and `BACKGROUND-002`. Background does not wait for API, Shopify or WooCommerce implementation.
- **Database -> Shopify:** `SHOPIFY-001` requires `DATABASE-001/002/003`; `SHOPIFY-002` requires `SHOPIFY-001`; `SHOPIFY-003` requires `SHOPIFY-002` and the common `BACKGROUND-003` send policy. No WooCommerce or hosted API tasks are prerequisites.
- **Database -> Woo API -> WooCommerce:** `API-002` requires `DATABASE-001` and existing `ARCH-035-API-013`; `API-003` requires only `DATABASE-001` (not superseded API-001); `API-004` requires `API-003` and `DATABASE-002/003`. `WOOCOMMERCE-001` uses those three API tasks plus existing `ARCH-035-API-013`, `WOOCOMMERCE-002` adds existing `ARCH-035-WOOCOMMERCE-013`, and `WOOCOMMERCE-003` requires `WOOCOMMERCE-002` plus common `BACKGROUND-003`.
- **Independent terminal certification:** `SYSTEM-TEST-001` checks the **database/Background runtime only**, using producer-neutral persisted commands without requiring either merchant app. `SYSTEM-TEST-002` checks Shopify after `SHOPIFY-003` and `BACKGROUND-003`. `SYSTEM-TEST-003` checks WooCommerce after `WOOCOMMERCE-003` and `BACKGROUND-003`. The two platform tests do not depend on `SYSTEM-TEST-001`, each other, or the other platform's implementation. Architectural completion reviews all three accepted results together.

Do not introduce an indirect cross-platform gate by making a shared-runtime test depend on both platform producers, or by making one platform system test depend on a test that requires the other platform.

| ID | Owner | Bounded outcome | Dependencies |
|---|---|---|---|
| ARCH-040-DATABASE-001 | moda_database | Durable control mode, revision, audit | — |
| ARCH-040-DATABASE-002 | moda_database | Existing sequence-2 follow-up claim/provenance | DATABASE-001 |
| ARCH-040-DATABASE-003 | moda_database | Durable idempotent human send command/outbox | DATABASE-001 |
| ARCH-040-SHARED-001 | moda_shared | **SUPERSEDED** redundant contract | — |
| ARCH-040-SHARED-002 | moda_shared | **SUPERSEDED** publication gate | — |
| ARCH-040-API-001 | moda_api | **SUPERSEDED** Shopify assertion | — |
| ARCH-040-API-002 | moda_api | Enrich existing Woo recovery detail with basket/control | DATABASE-001, ARCH-035-API-013 |
| ARCH-040-API-003 | moda_api | Woo-only control CAS Take Over/Resume | DATABASE-001 |
| ARCH-040-API-004 | moda_api | Woo-only idempotent human send acceptance | API-003, DATABASE-002, DATABASE-003 |
| ARCH-040-BACKGROUND-001 | moda_background | Fence AI against human takeover | DATABASE-001 |
| ARCH-040-BACKGROUND-002 | moda_background | Consume DB commands/provider dispatch from either platform | DATABASE-003, BACKGROUND-001 |
| ARCH-040-BACKGROUND-003 | moda_background | One shared follow-up claim/credit | DATABASE-002, BACKGROUND-002 |
| ARCH-040-GATEWAY-001 | moda_gateway | **SUPERSEDED** Shopify assertion secret/wiring | — |
| ARCH-040-SHOPIFY-001 | moda_app | Extend Recovery Detail server reader/basket/actions | DATABASE-001, DATABASE-002, DATABASE-003 |
| ARCH-040-SHOPIFY-002 | moda_app | Existing Recovery Detail: basket + read-only conversation | SHOPIFY-001 |
| ARCH-040-SHOPIFY-003 | moda_app | Takeover and composer on existing Recovery Detail | SHOPIFY-002, BACKGROUND-003 |
| ARCH-040-WOOCOMMERCE-001 | moda_woocommerce | WP REST proxy to existing Woo hosted API | API-002, API-003, API-004, ARCH-035-API-013 |
| ARCH-040-WOOCOMMERCE-002 | moda_woocommerce | Existing Woo Recovery Detail: basket + read-only thread | WOOCOMMERCE-001, ARCH-035-WOOCOMMERCE-013 |
| ARCH-040-WOOCOMMERCE-003 | moda_woocommerce | Woo Recovery Detail: takeover and human composer | WOOCOMMERCE-002, BACKGROUND-003 |
| ARCH-040-SYSTEM-TEST-001 | moda_system_test | Shared Database/Background one-thread, handover, follow-up and credit | DATABASE-001/002/003, BACKGROUND-001/002/003 |
| ARCH-040-SYSTEM-TEST-002 | moda_system_test | Independent Shopify Recovery Detail basket/conversation E2E | SHOPIFY-003, BACKGROUND-003 |
| ARCH-040-SYSTEM-TEST-003 | moda_system_test | Independent Woo Recovery Detail basket/conversation E2E | WOOCOMMERCE-003, BACKGROUND-003 |

All tasks remain **portable definitions** rather than Git task branches. `ARCH-035-API-013` and `ARCH-035-WOOCOMMERCE-013` are unchanged external prerequisites; neither is assumed complete. **API-002 explicitly depends on ARCH-035-API-013** before enriching its read DTO.

## Gateway and deployment

Reuse existing hosted Woo API ingress, Shopify app ingress, Background, PostgreSQL, Redis/BullMQ and Meta transport. **No Gateway task, new signing secret, new public API route for Shopify, separate chat deployment, database or WebSocket is required.** If future implementation establishes a concrete Woo API routing gap, document and route it to `moda_architect` rather than reviving the superseded Shopify assertion Gateway task.

Development delivery order: apply the fresh Prisma schema first; then run Background, Shopify server/UI and Woo-only API -> WooCommerce implementation in parallel as soon as each task’s own database and internal dependencies are satisfied. The two interactive composers also need accepted `BACKGROUND-003`; this is a **shared runtime gate**, not a Shopify/WooCommerce cross-dependency. After manual verification, run the three **independent terminal** system-test tasks as their respective prerequisites become Complete; no platform waits for the other platform’s system test. No historical data backfill, compatibility adapters or legacy migration rehearsals for this pre-production initiative; do not delete durable runtime data inadvertently.

## Observability, data protection and failure handling

Use canonical `@modainteract/moda-interact-shared/logging`; correlate shopId, conversationId, commandId, control revision, attemptId, send outcome and provider receipt without raw customer content or credentials. Capture handover conflicts, suppressed stale AI sends, merchant send queue lag, provider rejection and duplicate replay. Reuse approved OpenTelemetry/framework signals, adding only genuine domain telemetry. Bounded message pagination and retention, protected merchant/customer identities, provider-template selection and error states are required. Polling must stop while UI is inactive/disconnected.


## Merchant UI decision: extend Recoveries, not a separate inbox (2026-10-15)

The merchant already navigates `Recoveries -> select customer/recovery -> Recovery Detail`, where the existing read-only transcript, milestones and related recoveries live. **The initial ARCH-040 release must enhance that page**, not create a `Conversations` navigation item, `/app/conversations` route, new Woo conversation list, or second transcript. The basket is the saved `CheckoutRecovery.lineItems` snapshot; it can be absent/incomplete and must not be mistaken for a live cart or guessed price. Shopify reuses existing `RecoveryDetail.tsx` and recovery-detail server readers; Woo reuses `src/recoveries/detail/` and `ARCH-035` recovery read routes.

### Desktop ASCII acceptance layout (both platforms)

```text
+-------------------------------------------------------------------------------+
| < Back to Recoveries         Customer name    Recovery status / saved value   |
+--------------------------------------------+----------------------------------+
| CUSTOMER CONVERSATION                      | CHECKOUT BASKET                  |
| [AI or HUMAN] [Take Over / Resume AI]      | Saved checkout snapshot         |
| Last customer inbound / window advisory     | Item: name / variant / quantity |
|--------------------------------------------| Optional actual unit/line price |
| CommerceAgent: Can I help?                 | Saved recovery total           |
| Customer: Please check delivery.           +----------------------------------+
| Merchant: Yes, let me check.                | RECOVERY CONTEXT                |
| [Previous] [Latest] [Refresh]               | Status / milestones            |
|--------------------------------------------| Follow-up status / related      |
| [Human composer OR template OR no-send]     | recoveries                     |
+--------------------------------------------+----------------------------------+
```

### Narrow-screen ASCII acceptance layout

```text
+-------------------------------------------+
| < Recoveries       Customer / status      |
| [Checkout basket v]                       |
| [Recovery context v]                      |
| Conversation [AI/HUMAN] [Take Over/Resume]|
| Agent / Customer / Merchant messages      |
| [Previous] [Latest] [Refresh]             |
| [Human composer/template if eligible]     |
+-------------------------------------------+
```

The composer is introduced in SHOPIFY-003/WOOCOMMERCE-003; the read-only SHOPIFY-002/WOOCOMMERCE-002 stages cannot show working fake actions. Template-based closed-window follow-up is only available in HUMAN mode when the recovery's shared sequence-2 allowance is still eligible. Customer reply opens a new WhatsApp 24-hour service window but **does not** automatically return HUMAN ownership to AI.

Read API adjustment: Woo API-002 **extends** `GET /v1/merchant/recoveries/:recoveryId` with basket/control fields after ARCH-035-API-013 and reuses original `/messages` and `/related` endpoints; API-003/004 continue using conversation-ID scoped **commands only**. Shopify directly extends `/app/recoveries/:recoveryId`. No new generic inbox read endpoints are required.

## Non-goals

No separate Conversations page/list/API, no duplicated recovery transcript, no separate human chat database, no new Conversation per follow-up, no duplication of Meta webhook ingress, no new customer-facing channel, no agent-aided draft mode, no human media/voice attachments, no arbitrary multi-step campaigns, no new billing counter for individual active-window replies, no automatic AI ownership resumption on inbound customer response, and no changes to the Moda platform-support inbox.

## Open considerations before implementation

- Confirm business rule for a human follow-up if the customer had previously engaged but the 24-hour window subsequently closed. The proposed single sequence-2 allowance applies to any eligible closed-window follow-up while recovery remains actionable, not only no-response, while existing scheduled automation retains its no-response intent.
- First release uses the existing approved recovery follow-up template catalogue/selector, not arbitrary browser-selected template names.
- Inspect final ARCH-035 Woo detail prerequisites and existing Woo API route patterns before materialisation. Pending ARCH-035 tasks are not assumed accepted.
- Clarify CommerceAgent automatic escalation policy in a later extension; merchant-initiated takeover and manual release are mandatory for v1.

## Change history

2026-10-14: Drafted from provided workspace snapshot and user agreement. Explicitly preserved one Conversation per recovery generation while recognising initial/follow-up as separate billable outreach attempts, not new threads. No indexes reconciled pending user confirmation of architecture session completion.

2026-10-14: Superseded ARCH-040-SHARED-001/002; Prisma remains the durable model, Woo hosted API owns Woo HTTP contracts, Background consumes persisted commands; Shared logging remains.

2026-10-14: Corrected app boundaries: Shopify uses authenticated app server and direct Prisma; Woo alone uses hosted API and existing installation credentials. Superseded API-001/GATEWAY-001, detailed Woo API-002/003/004, and removed Background dependence on Woo API implementation.

2026-10-15: UI decision changed to extend the existing Shopify/Woo Recoveries Detail with saved checkout basket, conversation and human handover; removed separate inbox/read-route requirement. Added canonical desktop/mobile ASCII and linked Woo API-002 to ARCH-035-API-013.

2026-10-15: Clarified independent task streams: Database -> Background, Database -> Shopify, and Database -> Woo API -> WooCommerce. Removed API/Shopify implementation gates from the shared-runtime system test and removed SYSTEM-TEST-001 as a prerequisite of the independent Shopify and WooCommerce system tests; corrected obsolete API-001 reference in API-003 task body.
