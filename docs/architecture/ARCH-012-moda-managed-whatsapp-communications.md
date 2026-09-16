---
id: ARCH-012
title: Moda-managed WhatsApp communications
status: agreed
coordinator: moda_architect
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012: Moda-managed WhatsApp communications

## Status

**Agreed for implementation.**

ARCH-012 establishes the canonical bidirectional WhatsApp communications subsystem for Moda Interact. It is intentionally narrower than the Shopify checkout-recovery lifecycle.

ARCH-012 answers exactly these two questions:

```text
Background has decided to send a WhatsApp communication.
How does it reliably reach the customer?

A WhatsApp customer has sent a communication.
How does it reliably reach Background?
```

ARCH-012 does **not** decide when a Shopify recovery is created, when a reminder is due, whether a basket is still abandoned, when a recovery expires, or how a recovery consumes merchant entitlement.

## Product invariant

Moda Interact provides WhatsApp as managed infrastructure for Shopify merchants.

A merchant must **not** need to create, connect or administer:

```text
Meta Business Portfolio
WhatsApp Business Account (WABA)
Meta application
WhatsApp phone number
Meta access token
Meta webhook
WhatsApp template catalogue
```

The merchant consumes a Moda checkout/conversational capability. Moda owns the Meta/WhatsApp provider relationship and sender infrastructure.

ARCH-012 v1 uses **one Moda-owned WhatsApp sender**. The implementation must distinguish provider account identity from sender phone-number identity so a future architecture may introduce additional Moda senders without changing every business caller. ARCH-012 itself does not implement sender pooling, assignment, balancing or merchant-specific senders.

## Problem

The snapshot contains useful WhatsApp capabilities from ARCH-005 and ARCH-007, but the inbound communication boundary is not yet safe as one canonical cross-repository contract.

Current defects/gaps include:

1. `moda-interact-messaging` and `moda-interact-background` define incompatible repository-local inbound event shapes.
2. Messaging publishes `customerAddress` while Background expects `customerPhone`.
3. Messaging currently drops Meta `message.context.id`, even though Background routing is designed to use reply context to locate the exact prior outbound message/conversation.
4. Messaging recognizes `audio` as a type but currently drops the provider audio media identity; Background can therefore receive non-text as empty content.
5. `ConversationMessage.content` alone cannot truthfully represent an asynchronously transcribed audio message lifecycle.
6. Background outbound configuration currently risks conflating `WHATSAPP_PHONE_NUMBER_ID` with provider-account/WABA identity.
7. There is no integrated acceptance proof for realistic Meta webhook -> Messaging -> BullMQ -> Background text/voice transport plus outbound text/template/link/media transport.

## Goals

ARCH-012 must:

- preserve the existing service boundary: Meta ingress in `moda-interact-messaging`, asynchronous conversation work in `moda-interact-background`;
- define one strict versioned Shared contract for normalized inbound customer messages;
- support inbound text messages;
- support inbound WhatsApp voice notes up to and including 120 seconds;
- preserve explicit native WhatsApp reply context (`message.context.id`) when present;
- support ordinary contextless messages without requiring the customer to use WhatsApp's Reply gesture;
- prevent customer phone number from becoming a tenant identity;
- represent unsupported inbound media explicitly rather than converting it to empty text;
- download/transcribe voice media only in Background, after routing/admission succeeds;
- make transcription provider-neutral while using Groq speech-to-text as the initial adapter;
- preserve the spoken language; do not translate speech to English before CommerceAgent processing;
- keep raw audio transient by default;
- preserve exactly-once logical message/turn behaviour under webhook/job/provider retries;
- distinguish Meta WABA/account identity from sender phone-number identity;
- support outbound plain text with HTTPS hyperlinks/link preview;
- support approved template body parameters, image header parameters and dynamic URL-button parameters;
- retain existing provider status lifecycle handling;
- keep webhook acknowledgement lightweight and independent of DB/Shopify/LLM/transcription work;
- provide deterministic integrated system tests for text/reply and voice paths.

## Non-goals

ARCH-012 does **not** implement or redefine:

- Shopify abandoned-checkout detection;
- Shopify checkout reconciliation;
- delayed 48-hour follow-up scheduling or any other reminder policy;
- deciding whether/when another recovery message is sent;
- recovery expiry;
- order/completion detection;
- billing, entitlements, recovery credits or Meta cost accounting;
- merchant-owned WhatsApp/WABA onboarding or Meta Embedded Signup;
- a sender-pool database, automatic sender assignment or load balancing;
- human-agent handoff/live-chat escalation;
- outbound generated speech/TTS;
- image/document/video understanding by CommerceAgent;
- storing raw voice recordings in PostgreSQL/object storage;
- redesign of ARCH-007 abuse admission, turn coalescing or CommerceAgent semantics.

A Shopify/recovery workflow may consume the outbound transport created by ARCH-012, but its decision to send remains outside this initiative.

## Current repository boundaries

### `moda-interact-messaging`

Owner: `moda_messaging`.

Current public Meta ingress lives in:

```text
moda-interact-messaging/app/routes/whatsapp.tsx
```

Messaging owns:

```text
webhook verification/signature boundary
provider payload parsing
provider -> Moda normalization
provider-status normalization
BullMQ publication
fast HTTP acknowledgement after durable queue acceptance
```

Messaging must not own tenant resolution, Shopify recovery logic, media download, transcription or CommerceAgent work.

### `moda-interact-background`

Owner: `moda_background`.

Relevant existing implementation includes:

```text
src/workers/whatsapp.worker.ts
src/integration/whatsapp/types.ts
src/services/recovery-routing.service.ts
src/services/conversation.service.ts
src/services/conversation.message.service.ts
src/services/conversation-turn-processor.service.ts
src/services/inbound-whatsapp-abuse-admission.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/whatsapp-provider-status.service.ts
src/services/whatsapp-template-selector.service.ts
src/services/whatsapp.service.ts
src/providers/groq.provider.ts
```

Background owns:

```text
conversation/tenant resolution
durable message state
abuse admission
turn coalescing/ordering
voice media retrieval and transcription
CommerceAgent invocation
outbound admission
WhatsApp Cloud API transport
provider-status durable projection
```

### `moda-interact-shared`

Owner: `moda_shared`.

Shared owns the canonical cross-service inbound event schema/types. It must not contain tenant/recovery decisions.

### `moda-interact-database`

Owner: `moda_database`.

Database owns durable `whatsapp.ConversationMessage` media/transcription lifecycle fields and integrity.

### `moda-interact-gateway`

Owner: `moda_gateway`.

Gateway owns Render/IaC environment wiring. ARCH-012 requires no new service or public route; it only requires correct WABA identity wiring to the existing messaging worker deployables.

### `moda-interact-system-test`

Owner: `moda_system_test`.

The existing WhatsApp Cloud API emulator is extended; ARCH-012 must not create a competing emulator.

## Target runtime architecture

```text
INBOUND

Customer WhatsApp
      |
      v
Meta Cloud API webhook
      |
      v
moda-interact-messaging
  verify -> normalize -> validate Shared contract -> enqueue -> ACK
      |
      v
BullMQ whatsapp-events / message-received
      |
      v
moda-interact-background
  raw admission
  -> route conversation
  -> persist/dedupe
  -> text: existing turn path
  -> audio: media download -> <=120s -> STT -> existing turn path
      |
      v
existing ordered CommerceAgent conversation processing


OUTBOUND

Background business workflow
      |
      v
existing outbound admission
      |
      v
Moda WhatsApp transport
      |
      +-- plain text + optional link preview
      +-- approved template + body parameters
      +-- approved template + image header
      +-- approved template + dynamic URL button
      |
      v
Meta Cloud API /{providerPhoneNumberId}/messages
      |
      v
Customer WhatsApp

PROVIDER STATUS

Meta status webhook
      -> Messaging existing provider-status normalization
      -> Shared provider-status v2
      -> Background durable status projection
```

## Canonical inbound message contract

`ARCH-012-SHARED-001` owns implementation **and publication** of one strict Shared v1 event under:

```text
@modainteract/moda-interact-shared/whatsapp
```

The exact required shape is:

```ts
{
  schemaVersion: 1;
  provider: "whatsapp";
  providerAccountId: string;       // Meta WABA identity / webhook entry.id
  providerPhoneNumberId: string;   // Meta metadata.phone_number_id
  providerMessageId: string;       // Meta inbound message.id
  customerPhone: string;           // Meta inbound message.from
  contextMessageId: string | null; // Meta message.context.id when present
  occurredAt: string;              // offset-aware ISO timestamp
  content:
    | { type: "text"; text: string }
    | {
        type: "audio";
        mediaId: string;
        mimeType: string | null;
        sha256: string | null;
        voice: boolean | null;
      }
    | {
        type: "unsupported";
        providerType: string;
      };
}
```

The Shared contract deliberately contains **no** `shopId`, `conversationId`, `checkoutRecoveryId`, merchant identity or business decision.

## Inbound reply modes

ARCH-012 supports both normal WhatsApp customer behaviours.

### Mode A — explicit native reply

The customer uses WhatsApp Reply against a specific Moda outbound message.

```text
Meta message.context.id
      -> Shared contextMessageId
      -> Background looks up local outbound ConversationMessage.providerMessageId
      -> exact durable Conversation ownership
```

If that exact provider message exists, its conversation route is authoritative. A newer unrelated conversation must not steal the reply.

If the referenced provider message is unknown, Background falls through safely to the existing contextless resolution rules; it must not fabricate ownership.

### Mode B — ordinary contextless message

The customer simply sends another WhatsApp message without using the Reply gesture.

Messaging publishes:

```text
contextMessageId = null
```

Messaging performs no tenant inference.

Background resolves through durable conversation/recovery state using existing routing principles. `customerPhone` identifies a communications endpoint, **not a tenant**.

Required safety:

```text
one unambiguous eligible conversation -> route
same-owner multiple recovery candidates -> existing clarification behaviour
cross-tenant ambiguity -> unresolved / no CommerceAgent
no recovery conversation -> existing standalone/product ownership resolution may apply
```

ARCH-012 does not authorize a universal "choose the most recent merchant" fallback.

Once an active conversation has been established, subsequent plain messages may continue through that conversation without requiring every message to carry native reply context.

## Inbound text

For normalized `content.type == "text"`:

```text
route/admit
 -> persist idempotently as TEXT / NOT_REQUIRED
 -> preserve contextMessageId when present
 -> increment/coalesce conversation turn exactly once
 -> existing conversation-turn processor
```

Existing ARCH-007 abuse admission, ordering and coalescing are retained.

## Inbound voice notes

Voice is an input modality, not a second conversation architecture.

Binding product policy:

```text
maximum accepted voice-note duration = 120 seconds
exactly 120 seconds                = accepted
>120 seconds                       = rejected before paid transcription
outbound generated voice           = out of scope
translation to English             = prohibited
raw durable audio retention         = prohibited by default
```

Flow:

```text
Meta audio webhook
 -> Messaging publishes media identity only
 -> BullMQ
 -> Background raw admission
 -> resolve conversation FIRST
 -> reserve providerMessageId as AUDIO/PENDING
 -> Meta media metadata/download
 -> bounded MIME/size validation
 -> duration inspection
 -> >120s: REJECTED; no STT; no CommerceAgent
 -> <=120s: SpeechTranscriptionService
 -> nonblank transcript: COMPLETED
 -> content becomes transcript
 -> increment inboundVersion exactly once
 -> existing ordered turn processor
```

Background must not pay for transcription before it can safely route the message to a conversation/tenant.

### Initial transcription adapter

Business code depends on a provider-neutral `SpeechTranscriptionService`.

Initial adapter:

```text
provider: Groq speech-to-text
credential boundary: existing GROQ_API_KEY
model default: whisper-large-v3-turbo
optional config: GROQ_TRANSCRIPTION_MODEL
```

If the optional model configuration is absent, use the exact default. Provider-specific API code remains inside the adapter.

The transcript must preserve the spoken language and pass that transcript unchanged into the existing language/conversation pipeline. ARCH-012 does not insert an English translation stage.

## Unsupported inbound content

Images, video, documents, stickers, locations and other unsupported Meta message types must not disappear or become empty text.

Messaging maps them to:

```text
{ type: "unsupported", providerType: <bounded original Meta type> }
```

Background persists/observes the message idempotently as `UNSUPPORTED`, does not invoke CommerceAgent, and uses only the bounded customer-facing behaviour explicitly authorized by the Background task. ARCH-012 v1 does not introduce multimodal understanding.

## Durable media/transcription state

`ARCH-012-DATABASE-001` extends `whatsapp.ConversationMessage` with exact content/transcription state.

Enums:

```text
MessageContentType
  TEXT
  AUDIO
  UNSUPPORTED

MessageTranscriptionStatus
  NOT_REQUIRED
  PENDING
  COMPLETED
  REJECTED
  FAILED
```

Fields:

```text
contentType
providerMediaId
providerMediaMimeType
providerMediaSha256
mediaDurationMs
transcriptionStatus
transcriptionProvider
transcriptionModel
transcriptionFailureCode
transcriptionCompletedAt
```

`content` remains the canonical text consumed by the existing conversation history/CommerceAgent after a successful transcription.

Prohibited persistence:

```text
raw audio bytes
signed/transient provider download URL
unbounded provider exception prose
access token/authorization header
```

Existing unique `providerMessageId` remains the primary inbound provider deduplication boundary.

## Voice two-phase idempotency

Audio processing must separate reservation from turn completion.

```text
reserveInboundAudio
  -> unique providerMessageId
  -> AUDIO / PENDING
  -> no inboundVersion increment

completeInboundAudio
  -> guarded transaction
  -> transcript/content + COMPLETED
  -> inboundVersion/turn timestamps exactly once
  -> replay returns established completion, no second turn

terminal reject/fail
  -> REJECTED or FAILED
  -> bounded code
  -> no inboundVersion increment
  -> no CommerceAgent
```

Retryable provider/STT failures may remain `PENDING` for the existing BullMQ retry mechanism. Terminal invalid/overlong/blank outcomes must not retry indefinitely.

## Moda sender identity

ARCH-012 makes these identities explicitly distinct:

```text
WHATSAPP_BUSINESS_ACCOUNT_ID  = Meta WABA/provider account identity
WHATSAPP_PHONE_NUMBER_ID      = Meta sending phone-number resource identity
WHATSAPP_ACCESS_TOKEN         = provider credential
```

v1 has one Moda-owned configured sender. No merchant supplies any of these values.

Template selection/account ownership uses WABA/account identity where required. Sending uses the configured phone-number ID endpoint.

Do not build:

```text
merchant -> WABA mapping
sender pool table
sender balancing
sender failover allocation
merchant-specific access tokens
```

inside ARCH-012.

## Outbound transport capabilities

`ARCH-012-BACKGROUND-003` must preserve existing outbound admission and add/normalize transport capabilities sufficient for:

```text
plain text message
plain text containing HTTPS hyperlink
optional WhatsApp link preview flag
approved template body parameters
approved template image header parameter
approved template dynamic URL-button parameter
```

The transport returns/preserves provider message identity for existing durable status tracking.

ARCH-012 does not decide which recovery template to send or when to send it. It only serializes an already-authorized outbound request.

## Webhook durable acceptance

Messaging keeps the existing normal path:

```text
receive
 -> verify
 -> normalize
 -> validate canonical Shared event
 -> deterministic job identity
 -> durable BullMQ acceptance
 -> acknowledge Meta
```

Forbidden inside the inbound HTTP lifecycle:

```text
database lookup
Shopify API request
Meta media download
speech transcription
CommerceAgent/LLM call
recovery decision
```

## Retry and ordering invariants

Inbound:

```text
same providerMessageId delivered repeatedly
 -> one logical durable inbound message
```

Audio:

```text
webhook/job retry after completed transcription
 -> no second paid transcription when durable completion already proves success
 -> no second logical turn
```

Outbound:

```text
provider retry/failure
 -> existing bounded outbound semantics
 -> never fabricate success
```

Provider status:

```text
repeated status webhook
 -> idempotent durable lifecycle projection
```

Conversation ordering/coalescing remains the accepted ARCH-007 implementation. ARCH-012 does not globally serialize WhatsApp processing.

## Security and data safety

- Meta webhook verification/signature enforcement remains mandatory.
- Shared schema is strict and bounded.
- No raw webhook/customer media payload is added to logs.
- No Meta access token, authorization header, signed media URL or raw audio is logged.
- Audio download is bounded by accepted MIME/type and byte ceiling.
- Raw voice audio is transient and discarded after processing.
- Transcript text is customer message content and must not be added to generic operational logs/traces.
- Telemetry failure must never become a communications correctness dependency.

## Observability

Reuse the approved Shared structured logger and existing framework/OpenTelemetry signals. Do not create duplicate generic HTTP/BullMQ telemetry.

ARCH-012-specific semantic evidence may include bounded outcomes such as:

```text
normalized inbound content type
explicit-context present/absent
conversation resolution outcome (without customer content)
audio reserved/completed/rejected/failed
voice duration rejection
transcription provider/model + bounded outcome
Meta send accepted/failed
```

Never place customer transcript, audio bytes, access token or transient media URL in logs/traces.

## Infrastructure

No new Render service, public endpoint, Redis resource or PostgreSQL resource is required.

Gateway work is limited to architecture-required configuration of:

```text
WHATSAPP_BUSINESS_ACCOUNT_ID
```

on the existing test/production messaging worker deployables while preserving least privilege and all existing WhatsApp/Groq/Redis/Postgres/Shopify/OTEL configuration.

## Shared package publication ordering

The 2026-09-16 implementation review established that the live Shared baseline was `0.11.2` and ARCH-012-SHARED-001 published the additive WhatsApp contract as the next minor `0.12.0`.

A coordination error had manually marked `ARCH-011-SHARED-002` Complete before its prerequisite `ARCH-011-SHARED-001` was implemented. Because `0.12.0` is already correctly published and consumable, the architect does not churn the WhatsApp implementation. The release line is reconciled as:

```text
ARCH-012-SHARED-001 accepted Complete (`0.12.0`)
        -> ARCH-011-SHARED-001
        -> ARCH-011-SHARED-002 publication (`0.13.0`)
```

ARCH-011 Shared implementation must preserve the accepted `./whatsapp` entrypoint and all `0.12.0` public capability when it advances the package to `0.13.0`.

There is no executable ARCH-012 publication-only task. `ARCH-012-SHARED-002` is retained only as Superseded history.

## Task graph

```text
ARCH-012-SHARED-001 (accepted + published `0.12.0`)
            -> ARCH-012-MESSAGING-001
            -> ARCH-012-BACKGROUND-001

ARCH-012-SHARED-001 -> ARCH-011-SHARED-001 -> ARCH-011-SHARED-002 (`0.13.0`)

ARCH-012-DATABASE-001
        -> ARCH-012-BACKGROUND-001

ARCH-012-BACKGROUND-003
        -> ARCH-012-BACKGROUND-001
        -> ARCH-012-GATEWAY-001

MESSAGING-001 + BACKGROUND-001 + BACKGROUND-003 + GATEWAY-001
        -> SYSTEM-TEST-001
        -> SYSTEM-TEST-002
```

`ARCH-012-SHARED-002` and `ARCH-012-BACKGROUND-002` are Superseded and must never be prepared/executed.

Current execution frontier after this consolidation:

```text
ARCH-012-DATABASE-001      Complete — architect accepted Attempt 2; implementation `655ff35`
ARCH-012-SHARED-001        Complete — architect accepted Attempt 1; published `0.12.0`
ARCH-012-MESSAGING-001     Ready — promoted by accepted SHARED-001 review
ARCH-012-BACKGROUND-003    Complete — architect accepted Attempt 1; implementation `bb01a66`
ARCH-012-BACKGROUND-001    Ready — Attempt 1 changes requested; canonical ingress, explicit-context direction and audio retry semantics require correction
ARCH-012-GATEWAY-001       Ready — BACKGROUND-003 is accepted Complete
```

Do not downgrade tasks from stale snapshot state. `ARCH-012-BACKGROUND-001` is Ready for Attempt 2 rework after architect Changes Requested on Attempt 1. Its dependencies remain Complete, but it is not Complete and therefore continues to gate both system-test tasks. `ARCH-012-GATEWAY-001` remains independently Ready.

System tests are terminal integrated validation tasks. No implementation task depends on a system-test task.

## Repository responsibilities

| Repository | ARCH-012 responsibility |
|---|---|
| `moda-interact-shared` | canonical strict inbound customer-message contract + publication |
| `moda-interact-database` | durable content/media/transcription lifecycle |
| `moda-interact-messaging` | verified Meta -> canonical event normalization/publication |
| `moda-interact-background` | reply routing, durable message handling, voice STT, outbound sender/transport |
| `moda-interact-gateway` | WABA identity deployment wiring only |
| `moda-interact-system-test` | deterministic integrated text/reply/link/template + voice acceptance |

No `moda-interact` Shopify application implementation task is required by this communication architecture.

## Integrated acceptance

ARCH-012 is not Implemented until the accepted implementation proves, at minimum:

1. explicit text reply preserves `context.id` end to end and routes to the exact prior conversation;
2. ordinary contextless text can continue an unambiguous existing conversation without inventing reply context;
3. cross-tenant contextless ambiguity fails closed and does not invoke CommerceAgent;
4. duplicate inbound provider message creates one logical inbound message/turn;
5. unsupported media does not become empty text;
6. outbound text preserves a supplied Shopify HTTPS hyperlink and optional link-preview request;
7. approved template transport correctly serializes body, image-header and dynamic URL-button parameters;
8. WABA/account identity and phone-number sender identity remain distinct;
9. voice routes before media/STT cost;
10. exactly 120-second voice is accepted and >120-second voice is rejected before STT;
11. successful non-English transcript reaches the existing conversation pipeline without an English translation stage;
12. duplicate/retry voice processing does not create a second logical turn or unnecessary second completed transcription;
13. raw audio/transient provider media URL is not durably persisted/logged;
14. provider status handling remains idempotent;
15. normal webhook acknowledgement is not blocked on DB/Shopify/Meta-media/STT/LLM operations.

## Implementation governance

Individual task files under `docs/decisions/*/ARCH-012/` are the executable contracts and are authoritative for exact files, symbols, dependencies, tests, validation and stop conditions.

Implementation agents may run on GPT-5.6 Luna. They must not infer missing architecture. If a task's named surface/symbol/prerequisite does not match the prepared implementation workspace, the agent must stop and return evidence to `moda_architect` rather than redesigning the task.
