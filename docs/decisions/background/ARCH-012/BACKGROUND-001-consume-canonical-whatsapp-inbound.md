---
id: ARCH-012-BACKGROUND-001
architecture_id: ARCH-012
title: Consume canonical WhatsApp events and process text, unsupported and voice input
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 21
executor: copilot
claimed_at: 2026-09-16T12:04:20Z
attempt: 1
depends_on:
- ARCH-012-SHARED-001
- ARCH-012-DATABASE-001
- ARCH-012-BACKGROUND-003
- ARCH-007-BACKGROUND-010
- ARCH-007-BACKGROUND-011
- ARCH-010-BACKGROUND-013
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
enables:
- ARCH-012-SYSTEM-TEST-001
- ARCH-012-SYSTEM-TEST-002
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-BACKGROUND-001

## Objective
Implement the complete Background-owned inbound WhatsApp pipeline in **one task**:

```text
canonical Shared event
  -> abuse admission
  -> conversation/tenant routing
  -> durable inbound reservation/persistence
  -> text / unsupported / audio branch
  -> for audio: Meta media retrieval -> <=120s validation -> transcription
  -> exactly-once completed customer turn
  -> existing ordered/coalesced CommerceAgent pipeline
```

This task replaces the former split between BACKGROUND-001 routing and BACKGROUND-002 voice processing. Voice is an inbound content branch of the same worker/persistence/routing pipeline, not a separate architecture.

## Binding boundaries
Preserve both customer reply modes:

```text
A. explicit native WhatsApp reply
   contextMessageId -> exact prior outbound ConversationMessage -> Conversation

B. ordinary contextless message
   contextMessageId = null -> durable Background conversation resolution
```

Do not make `customerPhone` a tenant identity. Do not move routing, DB, media download, STT, Shopify or CommerceAgent work into Messaging.

## Required dependencies

- consume the exact published `@modainteract/moda-interact-shared/whatsapp` release recorded by completed `ARCH-012-SHARED-001`; do not duplicate the schema locally;
- consume the live/accepted `ARCH-012-DATABASE-001` schema/commit exactly as implemented; **do not modify its task definition or database schema in this task**;
- require `ARCH-012-BACKGROUND-003` so deterministic voice-failure/overlong responses use the accepted outbound transport/admission path.

If DATABASE-001 is still in progress, this task remains Pending. Do not copy provisional database changes into Background to bypass the dependency.

## Authorized implementation surface
Expected Background-owned files include:

```text
package.json
package-lock.json
src/workers/whatsapp.worker.ts
src/integration/whatsapp/types.ts
src/services/recovery-routing.service.ts
src/services/conversation.service.ts
src/services/*whatsapp*media*.ts             # bounded new media client/service if required
src/services/*speech*transcription*.ts       # provider-neutral interface + Groq adapter
src/services/*inbound*audio*.ts              # bounded reservation/completion service if useful
focused unit/integration tests
```

Database submodule pointer may move only to the accepted/live DATABASE-001 commit under normal submodule workflow. Do not edit `database/prisma/**` here.

`src/entrypoints/messaging.ts`, runtime-config services and queue-concurrency controller are not authorized redesign surfaces; preserve their accepted behaviour.

## 2026-09-16 runtime controls that must survive
The current Background baseline includes accepted controls that post-date the original ARCH-012 overlay:

- `backgroundRuntimeConfigService` starts before the WhatsApp worker;
- `createWhatsappWorker()` remains the worker factory;
- dynamic fleet-wide concurrency remains bound through `bindWorkerConcurrency(..., "whatsappQueueGlobalConcurrency")`;
- raw/settled WhatsApp abuse limits remain ARCH-014 runtime-configured;
- ARCH-010 shop execution eligibility remains authoritative, including distinct `contract-required` and `subscription-frozen` outcomes.

Do not restore static abuse/concurrency constants, bypass `shopExecutionEligibilityService`, or replace `createWhatsappWorker()` with a direct worker construction.

## Exact routing behaviour

### Explicit reply
When `contextMessageId` is non-null:

1. find the local/outbound `ConversationMessage.providerMessageId == contextMessageId`;
2. if found, route to that durable Conversation exactly;
3. preserve `inReplyToProviderId = contextMessageId` on the inbound message;
4. do not override exact context because another conversation is newer.

If referenced provider message is unknown, fall through to normal contextless resolution; do not fabricate ownership.

### Contextless message
When `contextMessageId == null`:

- one actionable recovery conversation for the phone -> resolve it;
- multiple actionable recoveries under one unambiguous shop/customer ownership -> use existing clarification behaviour rather than choosing by recency alone;
- candidates across different tenant ownership -> `ambiguous-tenant`, no CommerceAgent;
- no recovery conversation -> existing product-only/standalone ownership resolution may apply;
- shop execution eligibility remains authoritative.

Cross-tenant ambiguity must be resolved **before audio download/transcription** so Moda does not pay to transcribe a message it cannot safely attach to a tenant/conversation.

## Content branches

### Text
For `content.type == "text"`:

- persist `contentType=TEXT`, `transcriptionStatus=NOT_REQUIRED`;
- persist actual text and provider/context IDs;
- increment/coalesce the conversation turn exactly as accepted ARCH-007 behaviour currently does;
- duplicate `providerMessageId` must not create a second logical turn.

### Unsupported
For `content.type == "unsupported"`:

- persist idempotently with `contentType=UNSUPPORTED` and bounded descriptor content;
- `transcriptionStatus=NOT_REQUIRED`;
- do not invoke CommerceAgent;
- do not convert it into an empty text turn;
- emit bounded structured operational evidence using Shared logging;
- do not implement image/document/video understanding.

### Audio / voice
A WhatsApp voice note is routed exactly like text first, but its media/transcription lifecycle is two-phase so retries cannot create duplicate turns.

Binding product rules:

```text
maximum supported voice-note duration: 120 seconds
exactly 120 seconds:                    accepted
>120 seconds:                           reject before STT
outbound generated voice:               out of scope
translation to English:                 prohibited
raw audio durable retention:            prohibited
```

## Provider-neutral speech transcription
Create a provider-neutral service equivalent to:

```ts
interface SpeechTranscriptionService {
  transcribe(input: {
    bytes: Uint8Array;
    mimeType: string;
  }): Promise<{
    text: string;
    provider: string;
    model: string;
  }>;
}
```

Initial adapter: Groq Speech-to-Text using the already-deployed `GROQ_API_KEY` boundary.

```text
API family: OpenAI-compatible Groq audio transcription
model default: whisper-large-v3-turbo
optional env: GROQ_TRANSCRIPTION_MODEL
```

If the optional env is absent, use exactly `whisper-large-v3-turbo`. Do not use a translation endpoint. Do not couple conversation/business code directly to Groq outside the adapter.

## Meta media retrieval
Implement a bounded Background media client:

```text
mediaId
  -> authenticated Graph API media metadata lookup
  -> authenticated download URL fetch
  -> bounded in-memory audio buffer
```

Requirements:

- use existing `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_API_BASE_URL` conventions;
- never persist/log signed provider media URLs;
- require supported audio MIME/type;
- cap download bytes conservatively and abort if cap exceeded;
- no durable raw audio;
- if a temporary file is unavoidable, delete it in `finally`.

## Duration enforcement
Inspect audio duration **before paid transcription**. Support WhatsApp OGG/Opus and accepted audio MIME variants. Prefer an already-installed metadata parser; otherwise `music-metadata` is the approved bounded dependency.

```text
route conversation
  -> reserve AUDIO/PENDING
  -> download bounded media
  -> inspect duration
  -> >120s: terminal REJECTED, no STT, no agent
  -> <=120s: transcribe
  -> nonblank transcript: COMPLETED exactly once
  -> increment inboundVersion/turn exactly once
  -> existing conversation-turn processor
```

## Two-phase audio idempotency
Implement explicit service methods/transactions equivalent to:

### `reserveInboundAudio(...)`

- unique on existing `providerMessageId`;
- persist provider/context/media metadata;
- `contentType=AUDIO`, `transcriptionStatus=PENDING`;
- do **not** increment `Conversation.inboundVersion` yet.

### `completeInboundAudio(...)`

- guarded transaction writes transcript/content and `COMPLETED`;
- increments inbound version/timestamps exactly once;
- replay after COMPLETED is a no-op returning the established conversation version.

### Terminal rejection/failure

- set `REJECTED` or `FAILED` with bounded failure code;
- no turn increment;
- no CommerceAgent.

Retryable download/STT failures may leave PENDING for BullMQ retry. Terminal malformed/overlong/blank-speech outcomes must not retry forever.

## Deterministic customer fallbacks
After terminal rejection/failure use the normal admitted outbound text path from BACKGROUND-003. Do not invoke CommerceAgent.

```text
VOICE_TOO_LONG:
"Please send a voice note that is 2 minutes or shorter."

VOICE_UNREADABLE:
"I couldn't understand that voice note. Please try again or send your message as text."
```

No human escalation is added.

## Structured observability
Use existing Shared logger/OpenTelemetry runtime. Record bounded semantic outcomes:

```text
accepted
rejected-too-long
rejected-media
transcription-completed
transcription-retryable-failure
transcription-terminal-failure
```

Never log raw audio, transcript text, signed media URL, access token or full webhook payload.

## Required tests
At minimum prove:

### Routing/text/unsupported
1. contextual text resolves exact original conversation and persists reply ID;
2. contextless text with one active conversation resolves normally;
3. same-owner multiple recoveries use clarification flow;
4. cross-tenant candidates remain unresolved and never call CommerceAgent;
5. unknown explicit context falls through safely;
6. duplicate text providerMessageId is idempotent;
7. unsupported content is not converted to empty text/agent turn;
8. existing raw/settled abuse admission and ordering/coalescing remain intact.

### Audio
9. 30s OGG/Opus -> transcript -> one logical turn;
10. exactly 120s -> accepted;
11. >120s -> no transcription call and deterministic fallback;
12. duplicate webhook/job -> one reservation and at most one completed turn;
13. retry after COMPLETED -> no second STT or turn;
14. retryable media/STT failure -> no premature turn;
15. corrupt/unsupported media -> terminal bounded failure/fallback;
16. blank transcript -> fallback, no agent;
17. explicit reply voice retains `contextMessageId` ownership;
18. contextless voice resolves tenant/conversation before media download;
19. cross-tenant ambiguous voice -> no media download/STT;
20. returned transcript is passed unchanged into normal conversation processing; no translation endpoint;
21. raw bytes/URL are not persisted/logged.

### Compatibility
22. `createWhatsappWorker()` remains intact;
23. dynamic `whatsappQueueGlobalConcurrency` binding remains intact;
24. ARCH-014 runtime-configured abuse limits remain intact;
25. ARCH-010 `contract-required` / `subscription-frozen` execution gates remain effective.

## Non-goals

- outbound TTS/voice responses;
- streaming calls;
- self-hosted Whisper/HuBERT/wav2vec;
- Shopify/recovery timing or reconciliation;
- audio archive/storage;
- human escalation;
- merchant WhatsApp onboarding.

## Acceptance Criteria

- [ ] no authoritative local inbound WhatsApp schema remains;
- [ ] explicit and contextless reply modes are deterministic/tested;
- [ ] unsupported input never becomes empty agent text;
- [ ] voice is a branch of the existing ordered inbound pipeline, not a second agent architecture;
- [ ] 120-second limit is enforced before STT;
- [ ] duplicate/retry behaviour is durable and exactly-once at logical-turn level;
- [ ] spoken language is preserved;
- [ ] raw provider media is transient;
- [ ] accepted ARCH-007/010/014 runtime controls remain intact.

## Validation
Inspect actual `package.json` scripts first. Run focused inbound/routing/audio tests plus repository-declared full validation. Minimum where declared:

```text
npm test
npm run build
npm run typecheck
npx prisma validate --schema database/prisma/schema.prisma
git diff --check
```

No live Groq test is required in the normal suite. Any opt-in live test must require explicit credentials/flag and must never export retained customer audio.

## Stop conditions
STOP if:

- DATABASE-001 requires additional schema fields beyond its live accepted scope;
- supporting audio requires a durable media store;
- a new infrastructure secret is required beyond the documented Meta/Groq boundaries;
- existing routing semantics require a new recovery/product decision;
- implementing this task would require changing Shopify recovery timing/business logic.

## Completion protocol
Return `ARCH-012-BACKGROUND-001` to `review` and STOP. Do not create or execute BACKGROUND-002; it is superseded by this task.

## Completion Report

### Status
Not started.

### Files Changed
TBD.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
