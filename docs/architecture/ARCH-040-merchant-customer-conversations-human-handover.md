---
id: ARCH-040
title: Merchant customer conversations and human handover
status: proposed
coordinator: moda_architect
created: 2026-10-14
updated: 2026-10-18
---

# ARCH-040: Merchant customer conversations and human handover

## Status

Proposed — portable architecture/task definitions for discussion. No task branches, worktrees, commits, pushes or implementation are claimed. This initiative does **not** supersede the existing recovery lifecycle or Shopify/WooCommerce UI parity programmes.

## Problem

Moda already persists a WhatsApp `Conversation` and `ConversationMessage` history and produces automated checkout-recovery and CommerceAgent replies. Merchants cannot yet own that customer thread and send human messages from Shopify/WooCommerce **on the existing Recovery Detail screen, alongside checkout basket information**. The existing outbound admission accepts `AGENT | AUTOMATION`, while the database already recognises `HUMAN`. Concurrent human takeover, AI processing, follow-up admission, and credit accounting require one consistent authority.

## Agreed invariants

1. **ONE conversation for each CheckoutRecovery generation.** Its `checkoutRecoveryId` is unique; initial outreach, AI turns, human turns and follow-up are messages on that same `Conversation.id`. No follow-up or takeover creates a `Conversation`. A *different* recovery generation may have another conversation under the existing lifecycle; this initiative does not silently change that rule.
2. **Message author is independent of conversation identity.** Preserve `ConversationMessage.senderType` (`CUSTOMER`, `AGENT`, `AUTOMATION`, `HUMAN`); identify human replies by `senderType=HUMAN` without storing staff identities or introducing Moda merchant accounts; existing store authentication is sufficient.
3. **Human takeover is available unless the platform has suspended that shop’s human-messaging access**. A merchant uses the connected store’s existing authenticated administration interface. The takeover is durable and versioned, and it blocks subsequent automated sending until explicitly released. It does not bypass a terminal recovery, WhatsApp restrictions or subscription/entitlement checks.
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

## October 17 scope reconciliation — recovery-only, reuse-first

This revision narrows **ARCH-040 v1 merchant interaction** to existing checkout-recovery conversations displayed on the existing Shopify/WooCommerce Recovery Detail screen. Other Conversation types continue to exist and work as before, but do **not** acquire human-send controls in ARCH-040. Do not add a generic conversations inbox, new route, new standalone conversation ownership policy or new API identity for them. `Conversation.checkoutRecoveryId` and `CheckoutRecovery.shopId` are the authoritative recovery and tenant association (never rely on the nullable `Conversation.shopId` alone).

Build on existing `ConversationMessage` sender types, sequence-2 `RecoveryOutreachAttempt`, recovery credit source keyed by attempt ID, Background outbound admission/Meta transport/receipts, and existing recovery read URLs/component hierarchy. `MerchantConversationSendCommand` is a **durable accepted instruction**, not a second message, provider receipt, credit ledger or transport; retain only fields needed for deduplication, ownership fencing and recoverable dispatch. Avoid introducing separate human billing, a second WhatsApp sender, new global chat service or a semantic/LLM moderation dependency.

**Follow-up policy boundary:** keep the existing **scheduled** `NO_RESPONSE_FOLLOW_UP` suppression when the customer has replied. Separately, a deliberate **merchant-initiated** post-window template may be eligible after earlier engagement, but only where recovery status and existing business rules allow it and the single sequence-2 attempt remains unclaimed. Neither branch may make a second follow-up or credit. This specifies the distinct policies rather than silently converting all scheduled follow-ups into re-engagement campaigns. Service-window eligibility always uses most recent verified inbound CUSTOMER message.

**One Shopify feature task and one WooCommerce feature task:** Consolidated SHOPIFY-001 delivers recovery-detail reads, saved basket, transcript, authenticated Take Over/Resume AI, durable human commands and composer together after DATABASE-001 and BACKGROUND-002. The separately owned Woo API-002/003/004 tasks may progress in parallel with Background. Consolidated WOOCOMMERCE-001 delivers WordPress REST proxy and its full merchant interface together after its Woo API, Background and ARCH-035 prerequisites. Neither platform depends on the other's code or certification. Both platform task acceptance criteria describe feature implementation; **developer validation follows separately and is not a platform implementation-task acceptance criterion**.

**Development boundary:** normal fresh-database Prisma migration validation is required, but no compatibility/backfill/upgrade rehearsal is required for this pre-production feature. Preserve unrelated schema/table behaviour, existing recovery generations and provider records.

## Proposed architecture

**Shopify and WooCommerce have distinct authenticated application boundaries, but share the same database and Background runtime.**

- **Shopify:** The existing `moda-interact` application authenticates the shop through its current Shopify admin session and extends **`/app/recoveries/:recoveryId`** and its existing Recovery Detail server-side loader for saved basket and existing transcript; takeover/send actions and composer are included in the same consolidated SHOPIFY-001 feature task. It never calls `moda-interact-api` for ARCH-040 and needs no signed shop assertion, new staff identity or Gateway secrets.
- **WooCommerce:** The existing `Recoveries > Recovery Detail` plugin screen receives saved basket/transcript and human control/send in one combined implementation task; no new inbox/menu. The WordPress plugin authenticates its local WP-admin operator with its existing `manage_woocommerce` capability and nonce. PHP proxies to the existing hosted `moda-interact-api` using the existing Woo installation ID and Bearer installation credential; the API verifies active shop/installation and authorizes Prisma data by effective shop. The WordPress browser and merchant-hosted PHP never connect directly to Moda PostgreSQL or Redis.
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

## Platform-controlled abuse protection (2026-10-17)

**Decision:** Moda platform administration may suspend **HUMAN messaging only** for an abusive merchant. Do not reuse the broad `Shop.status=SUSPENDED`, merchant-editable `ShopFeaturePreference`, or the existing inbound customer abuse admission as the enforcement authority. Restriction is shop-scoped, persisted in PostgreSQL, admin-audited, and is not a per-staff role/identity. An absent restriction row means ACTIVE. Only a privileged Moda Admin can suspend or restore; each transition needs an internal reason and a monotonic revision.

| Merchant capability | ACTIVE | SUSPENDED |
|---|---|---|
| View existing recoveries / basket / conversation | Yes | Yes |
| Take Over into HUMAN | Yes | No |
| Submit HUMAN text or one eligible template follow-up | Subject to existing rules | No |
| Resume AI from HUMAN | Yes | Yes |
| CommerceAgent / automated recovery / inbound customer messages | Existing policy | Unchanged |

The Shopify app and Woo hosted API check restrictions during **server-side** HUMAN takeover/send acceptance; React/WordPress disabled controls are informative only. Background must enforce again at final provider admission for **all** queued HUMAN commands, even commands accepted before suspension. The Admin and Background implementations need a real ordering/fencing mechanism: a DB read at queue-claim time cannot by itself guarantee that a concurrent suspension beats provider send. Irreversibly submitted requests cannot be recalled. Rejected commands show a safe `human_messaging_suspended` reason, have no extra provider send/credit, and do not auto-resend when access is restored.

An independent Background stage checks HUMAN-only send rates, repeated unsolicited recipient messages and malformed/oversized content, with deterministic rules, bounded per-shop/recipient counters, idempotency-safe retry treatment, typed outcomes and structured review signals. A content classifier/provider is **not** silently introduced; semantic harassment/threat detection requires an approved future policy/service decision. Heuristic signals must not automatically suspend a merchant without an approved high-confidence policy. A platform admin retains suspension authority.

### Moda Admin ASCII acceptance layout

```text
Moda Admin > Merchant > Human Messaging
+---------------------------------------------------------+
| Human messaging: ACTIVE / SUSPENDED      Revision: 4     |
| [Suspend Human Messaging] / [Restore Access]            |
| Reason [Spam v]  Internal note [....................]    |
| [Confirm] [Cancel]                                      |
+---------------------------------------------------------+
| Change history: Time / Action / Reason / Admin           |
+---------------------------------------------------------+
```

### Recovery Detail suspended state (Shopify and WooCommerce)

```text
+-------------------------------------------------------------------+
| Customer / Recovery    [HUMAN]                     [Resume AI]    |
| Conversation transcript               Checkout basket/context    |
+-------------------------------------------------------------------+
| HUMAN MESSAGING UNAVAILABLE                                       |
| Human replies are currently disabled for this store.             |
| [Reply composer disabled]                                         |
+-------------------------------------------------------------------+
```

Restrictions do not add a new UI route, independent conversation, separate billing allowance, new merchant roles, or a Shopify/Woo dependency.


## Data model

- `Conversation`: persisted `AI`/`HUMAN` mode, monotonically increasing control revision, change timestamps and immutable mode-transition history (without individual staff identifiers). Do not create a new conversation because of handover or follow-up.
- `CheckoutRecovery`: reuse `lineItems Json?` and existing `totalPrice`/`currency` as the saved checkout basket/value snapshot, with optional real variant/quantity/image/price metadata only when present and validated. No new basket schema or live-cart assumption.
- `ConversationMessage`: preserves existing sender types; `HUMAN` is sufficient human authorship attribution, without new human staff identity columns. Relate to the admitted send command/attempt if required. Never confuse author with the recovery credit identity.
- `RecoveryOutreachAttempt`: continue sequence 1 (initial) and sequence 2 (only follow-up); record whether HUMAN, AGENT or AUTOMATION initiated sequence 2, together with delivery/credit identity and safe retry state; do not persist a staff principal. Keep unique `(checkoutRecoveryId, sequence)` and validated message-to-conversation association.
- Durable merchant command/outbox (or equivalently correct existing primitive): unique idempotency key scoped to shop, immutable conversation ID and expected control revision; persisted acceptance/result and bounded dispatch/retry state. No correct-only-in-Redis state.
- Pre-production development: use normal Prisma migrations to create a fresh schema. Historical-data migration, backfill, old-queue compatibility and rollback rehearsals are not required for this initiative.

## Contract ownership decision (2026-10-14, revised)

`moda-interact-database`/Prisma owns persisted conversation, messages, control, outreach attempts, and durable merchant send-command model. No new ARCH-040-specific `moda-interact-shared` schemas or publication gate. `SHARED-001/002` remain superseded.

For **WooCommerce only**, `moda-interact-api` enriches the **existing ARCH-035 Recovery Detail read endpoints** with basket and conversation control (API-002), and owns command HTTP validation, responses and errors (API-003/004) using `WooInstallationAuthenticator`. There is no new generic conversations inbox/list GET endpoint. `ARCH-040-API-001`, previously planned to add Shopify assertion verification, is **superseded**. `ARCH-040-API-002/003/004` are independently testable Woo read, handover and send-admission tasks. `moda-interact-woocommerce` owns the authenticated WordPress REST facade and native Woo UI; WOOCOMMERCE-001 owns both the WordPress recovery read projection and authenticated command proxies as one complete feature.

For **Shopify**, `moda-interact` owns the server-side loaders/actions and shop scoping via the existing Shopify admin session and direct Prisma database access. It does not call the hosted merchant API. `SHOPIFY-001` owns the complete existing Recovery Detail feature: scoped reader, basket/transcript layout, authenticated takeover/send server actions and human composer; SHOPIFY-002 and SHOPIFY-003 are superseded historical task records. There is no new Conversations navigation item or standalone inbox.

`moda-interact-background` consumes durable Prisma send commands from either platform, using the same queue/WhatsApp provider transport; Background does not depend on completion of the Woo HTTP API to implement the relay. Already-published Shared logging and unrelated packages remain in use. `ARCH-040-GATEWAY-001` is **superseded** because there is no new Shopify assertion/secret/route to deploy; a future observed routing gap would require a specific new architectural decision.

There are **26 task records: 12 active, 14 superseded** (DATABASE-002/003/004, BACKGROUND-003/004/005, SHARED-001/002, API-001, GATEWAY-001, WOOCOMMERCE-002/003, SHOPIFY-002/003). No new sign-in flow, Shopify API assertion or API package publication is required.

## Abuse-protection ordering and failure modes

- `DATABASE-001` owns persistent shop restriction and immutable admin audit; `ADMIN-001` owns privileged suspend/restore UI and CAS mutations; `BACKGROUND-001` owns tested suspension, final-send admission/fencing, and HUMAN-only deterministic screening services; `BACKGROUND-002` owns live worker/provider integration. No new Shared publication.
- A human conversation already in HUMAN mode stays there on suspension; it is not automatically returned to AI. A previously accepted command must not bypass later platform suspension. A customer-initiated message still enters the existing conversation normally.
- A worker-declined command must be identifiable by safe failure code and must not be sent/billed. Distinguish terminal restriction/content failures from retryable moderation infrastructure failures. Resuming access does not resurrect terminal commands or refresh idempotency keys automatically.
- Platform-admin internal notes never reach merchant APIs, the Shopify storefront, the WordPress browser or shared telemetry. Surface only public status and generic reasons.


## Concurrency and consistency

- Takeover/Resume is an authorised monotonic compare-and-set transaction with audit history. Releasing AI must not resurrect stale agent responses from earlier mode revisions.
- At final send admission, AI generation must verify current mode/revision; protect the provider handoff against takeover in the defined ordering boundary. An already submitted Meta request cannot be cancelled.
- Human message requests carry stable idempotency identity. A duplicate request returns the original operation; a conflicting payload for the same key fails. Never send during API request/database transaction.
- Human and AI follow-up claim must use the same `RecoveryOutreachAttempt` sequence 2 and shared credit source key. Concurrent claim wins one record; loser returns an explicit already-used/conflict result.
- Most-recent verified inbound controls customer-service-window eligibility. Server clock and bounded provider timestamp skew must be considered. Do not infer service-window opening from an outbound template.
- Disconnected Woo installations, invalid WordPress nonce/capability, invalid Shopify app sessions, cross-shop conversation IDs and stale control revisions fail closed.

## Platform-neutral execution and scheduling — approved Attempt 15

**Boundary:** Shopify and WooCommerce/hosted API own only their respective merchant authentication, shop/recovery lookup, read projections, HTTP actions and durable command acceptance. After a merchant command commits, all command discovery, admission, send policy, AI handover, follow-up arbitration, provider dispatch, receipt processing, billing, abuse screening and restriction enforcement are **platform-agnostic**, keyed by trusted `shopId`, `conversationId`, `checkoutRecoveryId` and `commandId`. `shopId` identifies a tenant, **not** a reason to branch on its commerce platform. Do not persist an `actorPlatform`, select a scheduler by `SHOPIFY`/`WOOCOMMERCE`, import either merchant application into Background, or create parallel platform-specific delivery pipelines. Existing provider/shop adapters may resolve credentials from canonical shop configuration, without changing business policy by platform.

**Exactly three existing/new delivery triggers:**

```text
SHOPIFY authenticated server action --+
                                     +--> same PostgreSQL MerchantConversationSendCommand
WOO WordPress -> hosted Woo API -----+                 |
                                                      | one platform-neutral dispatcher
                                                bounded DB polling + atomic lease
                                                      |
                                        BG001 policy and final provider fence
                                                      |
                                           existing WhatsApp transport/receipts

Verified customer inbound --> existing whatsapp BullMQ --> existing agent turn
Recovery follow-up timer --> existing recovery BullMQ --> existing follow-up processor
                      Both existing paths call the same BG001 ownership/follow-up fence.
```

- **No per-platform BullMQ scheduling for human messages.** The server-side Shopify action and Woo hosted API commit an identical command with a stable shop-scoped idempotency key in one PostgreSQL transaction; neither publishes a BullMQ job, calls Meta or waits for a worker. BG002 registers **one** polling dispatcher in existing messaging worker entrypoints; it reads the shared command table independent of producer origin.
- Keep the current BullMQ `whatsapp-events`/conversation-turn path for customer inbound and the existing delayed recovery-follow-up queue/job for no-response outreach. Neither changes into a polling job. A merchant-initiated eligible post-window template is an immediately accepted *database command*, not another scheduled follow-up. All routes use the same sequence-2 claim and credit identity.
- DB polling uses bounded indexed due-command scans, per-command CAS/lease token, short PostgreSQL transactions and safe multi-replica reclamation. Initial tunable defaults are 3 seconds, at most 25 claims/poll, at most four in-flight; these are **unmeasured design defaults**, not guarantees. Polling failure must not lose a committed command or bypass restrictions. `UNKNOWN`/provider-dispatch-admitted work must be reconciled without blind re-send. No Redis producer after commit, no new queue, new Render deployment or second scheduler is required for v1.
- Merchant UI command-status polling is a **different concern**: each platform may refresh the selected command/read model for display; it neither schedules nor delivers messages. Stop browser polling when the page/selection is inactive.

**Provider-send linearisation and unavoidable external race.** Admission is a short, durable PostgreSQL decision, with serialized checks of `(conversation mode, revision, shop HUMAN restriction, recipient/window/attempt)` and a unique provider-dispatch identity. A takeover or suspension committed before this admission must block the stale outbound; if admission commits first, the provider handoff may still complete *after* takeover. Neither platform should promise recall or claim that a provider HTTP call and a database transaction are atomic. `CLAIMED` is only a worker lease, never permission to call Meta. Provider-ambiguous results remain `UNKNOWN` until reconciled; the system does not promise exactly-once delivery under an unknowable provider outcome.

**Resumed AI history and inbound ordering.** BG001 specifies a sender-aware view of messages, preserving `HUMAN` as merchant-authored context instead of treating all OUTBOUND messages as the AI's own replies. BG002 integrates it into the actual agent history loader/processor. Inbound `lastInboundAt` must advance monotonically to the latest verified customer event (including audio); delayed/out-of-order webhooks cannot shorten the 24-hour service window or regress `lastMessageAt`.

**Follow-up and terminal policy.** Existing delayed no-response jobs retain engaged-customer suppression. An eligible deliberate human post-window template may atomically claim the existing unclaimed sequence-2 attempt, if the recovery is actionable; it does not make a new scheduled job or spend a second credit. An already claimed sequence-2 attempt (or unresolved provider submission) cannot be replaced by either actor. The original approved recovery template/recipient snapshots and existing billing/recipient policies remain authoritative. Terminal recoveries remain readable, while sends require existing eligibility rather than being silently enabled by takeover.

**Entitlement boundary:** `RECOVERY_HISTORY` allows viewing only. Shopify's server action and Woo API must use an explicitly resolved existing human-send/feature entitlement, consistent with Background; neither may infer send access from the read-only grant. If the existing billing catalogue has no appropriate entitlement, return a concrete policy gap to the architect rather than inventing a new plan feature inside a platform UI task.

**Retention and privacy:** v1 must not prune shop-scoped command idempotency identities while any original command, provider disposition or credit can still be reconciled. Default to retaining deduplication records until an explicit retention policy is approved; no fabricated replay TTL or resend after deleting an idempotency key. Use structured IDs and reason codes rather than customer texts/recipient numbers in logs.


## Semantic moderation extension — approved Attempt 16 (2026-10-18)

**Status of existing work at definition:** DATABASE-001 and BACKGROUND-001 were complete in the supplied 2026-10-18 snapshot. Developer reports BACKGROUND-002 underway; its source/task is unchanged here even though this snapshot still marks it `ready`. Newly defined DATABASE-005 is independent and ready; BACKGROUND-006 depends on **accepted** DATABASE-005 + BACKGROUND-002. No accepted task is reopened. This change adds **two** new task records, taking active tasks from 12 to 14, with 14 previously superseded historical records.

**Purpose.** Apply OpenAI `omni-moderation-latest` via the existing server-side Background worker to (1) verified inbound CUSTOMER text and completed audio transcription, (2) HUMAN merchant command content and (3) generated AGENT/dynamic AUTOMATION effective outbound content. A CUSTOMER WhatsApp message is already received before classification; we retain the original tenant-scoped transcript but prevent flagged text from reaching normal CommerceAgent prompt/tool processing. A flagged or unreviewed HUMAN/AGENT outbound is not submitted to Meta. Semantic moderation complements—not replaces—existing human spam/rate limits, administrative suspension, AI/HUMAN handover fencing, WhatsApp recipient/24-hour policy and recovery billing.

**Durable authority.** New `whatsapp.ConversationModerationAssessment` from DATABASE-005 references **one** existing message or send command, has shop/conversation binding and a SHA-256 digest of the exact effective text, model/policy version, categorical outcome and bounded audit data. No duplicate text, conversation, message ledger or per-platform moderation record. Only a current ALLOW for the exact subject/digest/policy authorises proceeding to the **separate** existing provider send fence; it is not provider-dispatch authorisation by itself. Fail closed on moderation dependency failures; use existing BullMQ turn retries for inbound/AI and existing PostgreSQL command due polling for HUMAN. No new platform queue or deployable.

**Decision rules (v1).** For complete valid moderation result, `flagged=false` yields ALLOW. `flagged=true` yields blocked outbound and a flagged inbound withheld from normal AI processing, but it is **not proof that the sender is abusive**. Self-harm help-seeking, legitimate complaints and ambiguous context require careful handling; no automatic shop suspension, customer ban or repeated AI regeneration. `REVIEW_REQUIRED` and dependency errors never fail open. The initial implementation is text/transcription-only. Images/audio blobs and prohibited child-safety material must not be submitted blindly to this endpoint; unsupported content is not marked ALLOW by default. Retain bounded category/score metadata for privileged review, with versioning because model internals may change. Approval is invalid if content, digest, model/policy version or subject changes.

**Source and platform separation.** Shopify uses its existing server-side loader/action. WooCommerce continues through WordPress REST and `moda-interact-api`. Both commit/retrieve identical persisted commands and outcomes; *neither* calls OpenAI from a merchant browser or WordPress. DATABASE-005 + BG006 implement one platform-neutral moderation state machine. Shopify/Woo/Moda Admin pending task specs receive only projection/UI changes; no new Shopify-to-WooCommerce dependencies. BG002 remains untouched while in progress.

**External API reference:** https://developers.openai.com/api/docs/guides/moderation?api-mode=responses and https://developers.openai.com/api/reference/resources/moderations/methods/create . These links describe the vendor endpoint, not a new Moda shared contract.

### Moderation flow

```text
Verified CUSTOMER WhatsApp -> existing BullMQ ingress -> persist original message
      -> persisted moderation assessment -> ALLOW: normal eligible agent turn
                                         -> FLAG/REVIEW/ERROR: no normal AI context
Shopify HUMAN action -----------+
                                +--> same durable merchant send command
Woo/API HUMAN action -----------+             |
                                             v
                             existing BG002 PostgreSQL dispatcher
                                    -> BG006 moderation check
                                    -> BG001 final dispatch fence
                                    -> existing WhatsApp transport
CommerceAgent prepared outbound -> BG006 moderation -> BG001 final fence -> Meta
```

**Rollout/dependencies.** DATABASE-005 may execute now without re-opening DATABASE-001. BG006 starts only after BG002 is complete and DATABASE-005 is accepted. Pending API-002/004, Shopify-001, WooCommerce-001 and Admin-001 use safe assessment projections; the platform implementation and final system tests require BG006 where applicable. Terminal SYSTEM-TEST-001/002/003 add moderation scenarios, with no non-test task depending on a system-test task. Developer final validation is a separate checkpoint, not an implementation-task acceptance criterion.

## Repository responsibilities and execution plan

### Independently executable streams (2026-10-17)

ARCH-040 has **three independent implementation streams after their applicable database prerequisites**. There is **no dependency in either direction** between `ARCH-040-SHOPIFY-*` and `ARCH-040-WOOCOMMERCE-*`, and Shopify does **not** depend on any `ARCH-040-API-*` task. Only the WooCommerce stream consumes the hosted Woo API.

```text
                               DATABASE
                                  |
           +----------------------+--------------------+
           |               |             |            |
           v               v             v            v
        BACKGROUND       SHOPIFY     API (Woo-only)  ADMIN
           |               |             |            |
           |               |             v            |
           |               |         WOOCOMMERCE      |
           |               |             |            |
           +---------------+-------------+------------+
                                  |
                                  v
                         SYSTEM TESTS
                   (independent terminal gates)
```

Dependency edges are **prerequisites, not a mandate to run the branches sequentially**:

- **Database -> Background:** `DATABASE-001` -> `BACKGROUND-001` (testable domain policies/services) -> `BACKGROUND-002` (all production call-site and worker integration). Neither Background task depends on Woo API or Shopify implementations.
- **Database/Background -> Shopify:** One consolidated `SHOPIFY-001` depends on `DATABASE-001` and `BACKGROUND-002` for the full recovery-detail feature; the formerly separate SHOPIFY-002 and SHOPIFY-003 tasks are superseded. No WooCommerce or hosted Woo API prerequisites. Developer validation is a subsequent activity, not an implementation acceptance criterion.
- **Database -> Woo API -> WooCommerce:** Woo-only API-002/003/004 depend on consolidated `DATABASE-001` as relevant, alongside `ARCH-035-API-013` where required. One consolidated `WOOCOMMERCE-001` depends on all three Woo API tasks, `BACKGROUND-002` and both ARCH-035 recovery-detail prerequisites. No Shopify prerequisite.
- **Platform Admin:** `ADMIN-001` depends solely on consolidated `DATABASE-001` and is independent of Shopify, WooCommerce and the hosted API. Its acceptance is a prerequisite of shared-runtime safety certification.
- **Independent terminal certification:** `SYSTEM-TEST-001` checks the **database/Background runtime and platform-admin restriction**, using producer-neutral persisted commands without requiring either merchant app. `SYSTEM-TEST-002` checks Shopify after consolidated `SHOPIFY-001` and `BACKGROUND-002`. `SYSTEM-TEST-003` checks WooCommerce after `WOOCOMMERCE-001` and `BACKGROUND-002`. The two platform tests do not depend on `SYSTEM-TEST-001`, each other, or the other platform's implementation. Architectural completion reviews all three accepted results together.

Do not introduce an indirect cross-platform gate by making a shared-runtime test depend on both platform producers, or by making one platform system test depend on a test that requires the other platform.

| ID | Owner | Bounded outcome | Dependencies |
|---|---|---|---|
| ARCH-040-DATABASE-001 | moda_database | **Combined**: control, follow-up, durable send, HUMAN restriction and audit | — |
| ARCH-040-DATABASE-002 | moda_database | **SUPERSEDED** — consolidated into DATABASE-001 | — |
| ARCH-040-DATABASE-003 | moda_database | **SUPERSEDED** — consolidated into DATABASE-001 | — |
| ARCH-040-DATABASE-004 | moda_database | **SUPERSEDED** — consolidated into DATABASE-001 | — |
| ARCH-040-DATABASE-005 | moda_database | NEW moderation assessment persistence and idempotency | — |
| ARCH-040-ADMIN-001 | moda_admin | Privileged suspend/restore plus redacted incident review | DATABASE-001, DATABASE-005 |
| ARCH-040-SHARED-001 | moda_shared | **SUPERSEDED** redundant contract | — |
| ARCH-040-SHARED-002 | moda_shared | **SUPERSEDED** publication gate | — |
| ARCH-040-API-001 | moda_api | **SUPERSEDED** Shopify assertion | — |
| ARCH-040-API-002 | moda_api | Enrich Woo recovery detail with basket/control/moderation state | DATABASE-001, DATABASE-005, ARCH-035-API-013 |
| ARCH-040-API-003 | moda_api | Woo-only control CAS Take Over/Resume | DATABASE-001 |
| ARCH-040-API-004 | moda_api | Woo-only send acceptance + moderation status reads | API-003, DATABASE-001, DATABASE-005 |
| ARCH-040-BACKGROUND-001 | moda_background | Implement modular recovery conversation services: AI fencing, HUMAN command/send, follow-up/credit, suspension, screening and admission policy | DATABASE-001 |
| ARCH-040-BACKGROUND-002 | moda_background | Wire accepted services into AI turns, HUMAN command consumer, recovery follow-up, final provider and receipt paths | DATABASE-001, BACKGROUND-001 |
| ARCH-040-BACKGROUND-003 | moda_background | **SUPERSEDED** — follow-up policy moved to BACKGROUND-001/002 | — |
| ARCH-040-BACKGROUND-004 | moda_background | **SUPERSEDED** — suspension/fencing moved to BACKGROUND-001/002 | — |
| ARCH-040-BACKGROUND-005 | moda_background | **SUPERSEDED** — screening moved to BACKGROUND-001/002 | — |
| ARCH-040-BACKGROUND-006 | moda_background | NEW model moderation of CUSTOMER/HUMAN/AGENT plus runtime gating | DATABASE-005, BACKGROUND-002 |
| ARCH-040-GATEWAY-001 | moda_gateway | **SUPERSEDED** Shopify assertion secret/wiring | — |
| ARCH-040-SHOPIFY-001 | moda_app | **Combined** Recovery Detail, HUMAN controls and moderation feedback | DATABASE-001, DATABASE-005, BACKGROUND-002, BACKGROUND-006 |
| ARCH-040-SHOPIFY-002 | moda_app | **SUPERSEDED** — basket/layout moved to SHOPIFY-001 | — |
| ARCH-040-SHOPIFY-003 | moda_app | **SUPERSEDED** — takeover/composer moved to SHOPIFY-001 | — |
| ARCH-040-WOOCOMMERCE-001 | moda_woocommerce | **Combined** Woo Recovery Detail/HUMAN and moderation feedback | API-002/003/004, DATABASE-005, BACKGROUND-002, BACKGROUND-006, ARCH-035-API-013, ARCH-035-WOOCOMMERCE-013 |
| ARCH-040-WOOCOMMERCE-002 | moda_woocommerce | **SUPERSEDED** — basket and transcript moved to WOOCOMMERCE-001 | — |
| ARCH-040-WOOCOMMERCE-003 | moda_woocommerce | **SUPERSEDED** — human reply/composer and command proxies moved to WOOCOMMERCE-001 | — |
| ARCH-040-SYSTEM-TEST-001 | moda_system_test | Shared runtime plus moderation and credit safety | DATABASE-001/005, ADMIN-001, BACKGROUND-001/002/006 |
| ARCH-040-SYSTEM-TEST-002 | moda_system_test | Independent Shopify Recovery Detail and moderation E2E | SHOPIFY-001, BACKGROUND-002/006 |
| ARCH-040-SYSTEM-TEST-003 | moda_system_test | Independent Woo Recovery Detail and moderation E2E | WOOCOMMERCE-001, BACKGROUND-002/006 |

All tasks remain **portable definitions** rather than Git task branches. `ARCH-035-API-013` and `ARCH-035-WOOCOMMERCE-013` are unchanged external prerequisites; neither is assumed complete. **API-002 explicitly depends on ARCH-035-API-013** before enriching its read DTO.

### WooCommerce consolidation and developer validation decision (2026-10-17)

The WooCommerce implementation is **one complete, independently reviewable feature** under `ARCH-040-WOOCOMMERCE-001`. Old `WOOCOMMERCE-002` and `WOOCOMMERCE-003` are superseded and retained for history. All of their ASCII desktop/narrow-screen/AI/HUMAN/closed-window/suspended states are included in WOOCOMMERCE-001. Unlike Shopify's staged read-only path, Woo's UI, PHP REST command proxy and composer ship as one implementation task.

**Developer-owned validation is not an acceptance criterion or completion gate for WOOCOMMERCE-001.** Its Acceptance Criteria cover implemented behaviour; the developer performs manual/automated validation separately after delivery, and records any failures for correction. Independent `SYSTEM-TEST-003` remains a terminal architecture certification task, not a prerequisite for WOOCOMMERCE-001 review/acceptance. No cross-dependency on Shopify is introduced.

## Gateway and deployment

Reuse existing hosted Woo API ingress, Shopify app ingress, Background, PostgreSQL, Redis/BullMQ and Meta transport. **No Gateway task, new signing secret, new public API route for Shopify, separate chat deployment, database or WebSocket is required.** If future implementation establishes a concrete Woo API routing gap, document and route it to `moda_architect` rather than reviving the superseded Shopify assertion Gateway task.

Development delivery order: accept combined DATABASE-001 first. Woo hosted read DTO API-002 and the Background services may advance in parallel; the **combined Shopify SHOPIFY-001** delivers reads, basket, transcript and human controls in one task after its DATABASE-001 and BACKGROUND-002 dependencies. The combined WooCommerce implementation task WOOCOMMERCE-001 begins only once its complete Woo API-002/003/004, BACKGROUND-002 and ARCH-035 prerequisites are accepted. The Shopify and WooCommerce complete interactive features both require accepted `BACKGROUND-002`; this is a **shared runtime gate**, not a Shopify/WooCommerce cross-dependency. After manual verification, run the three **independent terminal** system-test tasks as their respective prerequisites become Complete; no platform waits for the other platform’s system test. No historical data backfill, compatibility adapters or legacy migration rehearsals for this pre-production initiative; do not delete durable runtime data inadvertently.

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

The composer is delivered by consolidated SHOPIFY-001 and consolidated WOOCOMMERCE-001, each with its own complete Recovery Detail layout and authenticated command boundary. Neither feature relies on inert read-only placeholder controls. Template-based closed-window follow-up is only available in HUMAN mode when the recovery's shared sequence-2 allowance is still eligible. Customer reply opens a new WhatsApp 24-hour service window but **does not** automatically return HUMAN ownership to AI.

Read API adjustment: Woo API-002 **extends** `GET /v1/merchant/recoveries/:recoveryId` with basket/control fields after ARCH-035-API-013 and reuses original `/messages` and `/related` endpoints; API-003/004 continue using conversation-ID scoped **commands only**. Shopify directly extends `/app/recoveries/:recoveryId`. No new generic inbox read endpoints are required.

## Non-goals

No separate Conversations page/list/API, no duplicated recovery transcript, no separate human chat database, no new Conversation per follow-up, no duplication of Meta webhook ingress, no new customer-facing channel, no agent-aided draft mode, no human media/voice attachments, no arbitrary multi-step campaigns, no new billing counter for individual active-window replies, no automatic AI ownership resumption on inbound customer response, and no changes to the Moda platform-support inbox.

## Open considerations before implementation

- **Resolved for v1:** scheduled `NO_RESPONSE_FOLLOW_UP` remains limited to customers who have not responded; a merchant may deliberately use the one remaining sequence-2 follow-up after the window closes even after prior engagement, only while the recovery remains actionable and the attempt is still unclaimed. The existing recovery eligibility, approved template and billing rules apply; no additional follow-up or campaign is introduced.
- First release uses the existing approved recovery follow-up template catalogue/selector, not arbitrary browser-selected template names.
- Inspect final ARCH-035 Woo detail prerequisites and existing Woo API route patterns before materialisation. Pending ARCH-035 tasks are not assumed accepted.
- Clarify CommerceAgent automatic escalation policy in a later extension; merchant-initiated takeover and manual release are mandatory for v1.

## Change history

2026-10-14: Drafted from provided workspace snapshot and user agreement. Explicitly preserved one Conversation per recovery generation while recognising initial/follow-up as separate billable outreach attempts, not new threads. No indexes reconciled pending user confirmation of architecture session completion.

2026-10-14: Superseded ARCH-040-SHARED-001/002; Prisma remains the durable model, Woo hosted API owns Woo HTTP contracts, Background consumes persisted commands; Shared logging remains.

2026-10-14: Corrected app boundaries: Shopify uses authenticated app server and direct Prisma; Woo alone uses hosted API and existing installation credentials. Superseded API-001/GATEWAY-001, detailed Woo API-002/003/004, and removed Background dependence on Woo API implementation.

2026-10-15: UI decision changed to extend the existing Shopify/Woo Recoveries Detail with saved checkout basket, conversation and human handover; removed separate inbox/read-route requirement. Added canonical desktop/mobile ASCII and linked Woo API-002 to ARCH-035-API-013.

2026-10-15: Clarified independent task streams: Database -> Background, Database -> Shopify, and Database -> Woo API -> WooCommerce. Removed API/Shopify implementation gates from the shared-runtime system test and removed SYSTEM-TEST-001 as a prerequisite of the independent Shopify and WooCommerce system tests; corrected obsolete API-001 reference in API-003 task body.

2026-10-16: Proposed HUMAN-only merchant abuse protection: shop-level audited platform suspension, Admin controls, final-dispatch race fencing and HUMAN-specific deterministic screening. Added DATABASE-004, ADMIN-001, BACKGROUND-004/005; updated producer and independent system-test requirements. No Shared/Gateway tasks, separate Conversations page, or Shopify↔Woo dependencies.
2026-10-17: Simplified v1 to recovery-linked human messaging; reused existing attempt/provider/billing paths; separated read-only Shopify/Woo detail work from authenticated write command work without cross-platform dependencies.

2026-10-17: Consolidated ARCH-040-DATABASE-001/002/003/004 into one executable DATABASE-001 with one fresh-database migration and integrated persistence tests. DATABASE-002/003/004 remain superseded historical records; all active consumers now depend only on DATABASE-001 for database schema acceptance. This intentionally makes read-only UI work wait for the full database task, but preserves separate Shopify, Woo API and Background execution streams.

2026-10-17: Consolidated BACKGROUND-001/002/003/004/005 into BACKGROUND-001 (testable recovery conversation policy/services) and BACKGROUND-002 (production call-site/worker wiring); BACKGROUND-003/004/005 are superseded historical tasks. Preserved one transcript, sequence-2 credit identity, HUMAN-only abuse restriction and independent Shopify/WooCommerce streams; terminal system-test gates now depend only on the active integrated runtime.

## 2026-10-19 follow-up reservation and localisation reconciliation

**Verified gap (2026-10-18 snapshot + SHOPIFY-001 Attempt 1 candidate):** a HUMAN approved-template command can reserve the one recovery sequence-two `RecoveryOutreachAttempt` during merchant-side acceptance, *before* the existing Background dispatcher performs asynchronous moderation. A terminal moderation `BLOCK`/`REVIEW_REQUIRED`, shop suspension or stale-control refusal cancels the command before Meta admission but does not release the reserved attempt. The original claim remains non-null. A later eligible HUMAN or scheduled follow-up is then suppressed despite no provider submission or settled recovery credit. Transient moderation failures still require safe retry of the same reserved command.

**Database integrity gate:** the existing migration `20261017120000_arch040_recovery_human_handover` enforces immutable non-null attempt claim fields; `MerchantConversationSendCommand.recoveryOutreachAttemptId` is both `@unique` and immutable with a restrictive FK. Clearing the attempt claim without a migration or deleting the historical cancelled command is not acceptable. New `ARCH-040-DATABASE-006` owns a narrowly guarded pre-provider release protocol and historical command linking; new `ARCH-040-BACKGROUND-007` depends on its accepted release contract and implements lease-fenced terminal cancellation, bounded crash recovery, safe billing no-charge handling and provider/credit invariant proofs. The one sequence-two attempt, normal follow-up eligibility and source identity `recovery-outreach:<attemptId>` remain intact. There is **no** reset after a provider permit, `UNKNOWN`, confirmed send, or other irreversible provider outcome. No new gateway/queue/service is needed.

**Merchant presentation:** the SHOPIFY-001 candidate includes sixteen `recoveryDetail.*` informational/status strings unchanged in English across nineteen non-English locale catalogues. `ARCH-040-SHOPIFY-004` is a separate `moda_app` translation-parity task dependent on accepted SHOPIFY-001. Do not fold localisation into Background/database work.

**Execution and rollout:** DATABASE-006 -> BACKGROUND-007 -> terminal SYSTEM-TEST-001/002/003. Independently, SHOPIFY-001 -> SHOPIFY-004 -> terminal SYSTEM-TEST-002. Shopify/Woo provider follow-up delivery should not be production-enabled until the safe release lifecycle and relevant terminal certification pass. A system-test task must never be a dependency of any non-test task. Existing complete tasks are not reopened. This reconciliation makes no claim that task branches or worktrees have been materialised; the developer must use the canonical launcher.

| New task | Owner | Status at definition | Dependencies |
|---|---|---|---|
| ARCH-040-DATABASE-006 | moda_database | Ready | DATABASE-001 (Complete) |
| ARCH-040-BACKGROUND-007 | moda_background | Pending | DATABASE-006, BACKGROUND-002/006 |
| ARCH-040-SHOPIFY-004 | moda_app | Pending | SHOPIFY-001 |

The task-definition patch also gates each independent SYSTEM-TEST-001/002/003 on BG007 and SYSTEM-TEST-002 on SHOPIFY004. This adds bounded repair and verification requirements to the earlier ARCH-040 architecture; the earlier 2026-10-17/-18 task-count inventory is historical rather than a current count. Domain `_index.md` files remain untouched until the developer closes the architecture session.
