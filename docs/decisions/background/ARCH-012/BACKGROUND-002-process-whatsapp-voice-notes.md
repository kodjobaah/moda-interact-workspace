---
id: ARCH-012-BACKGROUND-002
architecture_id: ARCH-012
title: Process inbound WhatsApp voice notes through asynchronous transcription
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-012-BACKGROUND-001
- ARCH-012-BACKGROUND-003
- ARCH-012-DATABASE-001
enables:
- ARCH-012-SYSTEM-TEST-002
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-012-BACKGROUND-002

## Objective
Add production inbound voice-note support without creating a parallel conversation architecture. A WhatsApp voice note is routed exactly like text, asynchronously downloaded/transcribed in Background, and only the completed transcript becomes an ordinary ordered customer turn.

## Binding product rules

```text
maximum supported customer voice-note duration: 120 seconds
outbound generated voice:                         NOT in ARCH-012 v1
translation to English before CommerceAgent:      prohibited
raw voice recording durable retention:            prohibited by default
```

The transcription must preserve the customer's spoken language. Use transcription, not translation.

## Provider architecture
Create a provider-neutral interface, for example:

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

Initial implementation: Groq Speech-to-Text using the already deployed `GROQ_API_KEY` boundary.

Use:

```text
endpoint family: OpenAI-compatible Groq audio transcription API
model default:   whisper-large-v3-turbo
optional env:    GROQ_TRANSCRIPTION_MODEL
```

If the optional env is absent, use the exact default above. Do not reuse the translation endpoint. Do not couple business code directly to Groq outside the adapter.

## Media retrieval boundary
Implement a bounded Meta media client inside Background:

```text
mediaId
  -> authenticated Graph API media metadata lookup
  -> authenticated download URL fetch
  -> bounded in-memory audio buffer
```

Requirements:

- use existing `WHATSAPP_ACCESS_TOKEN` and configurable existing `WHATSAPP_API_BASE_URL` conventions;
- provider media URL is transient and MUST NOT be persisted/logged;
- require an audio MIME/type compatible with supported transcription input;
- cap download size to a conservative value no greater than Meta's supported inbound audio ceiling; abort streaming/download if the cap is exceeded;
- no temp-file retention after request; if a library requires a temporary file, delete it in `finally` and never expose it outside the task process.

## Duration enforcement before transcription
Add a local audio metadata parser capable of OGG/Opus WhatsApp voice notes and the accepted audio MIME variants. `music-metadata` is the preferred bounded dependency unless inspection establishes an already-installed equivalent.

Flow:

```text
route conversation first
  -> reserve/dedupe inbound ConversationMessage as AUDIO/PENDING
  -> retrieve bounded audio
  -> inspect duration
  -> duration > 120s: REJECTED; no STT; no CommerceAgent
  -> duration <= 120s: transcribe
  -> nonblank transcript: COMPLETED; finalize message; increment conversation inboundVersion exactly once
  -> enqueue existing conversation-turn processor
```

Do not pay for transcription before tenant/conversation routing succeeds.

## Two-phase idempotency
Implement explicit Background service methods so a provider retry cannot create duplicate logical turns:

1. `reserveInboundAudio(...)`
   - unique by existing `providerMessageId`;
   - persist provider/context/media metadata;
   - `contentType=AUDIO`, `transcriptionStatus=PENDING`;
   - do **not** increment `Conversation.inboundVersion` yet.

2. `completeInboundAudio(...)`
   - guarded transaction updates transcript/content and `COMPLETED`;
   - increments inbound version / turn timestamps exactly once;
   - replay of an already COMPLETED message is a no-op returning its established conversation version.

3. terminal rejection/failure
   - update `REJECTED` or `FAILED` with bounded failure code;
   - do not increment conversation turn and do not invoke CommerceAgent.

Retryable download/STT failures may leave PENDING until BullMQ retries. Terminal malformed/overlong/blank-speech outcomes must not retry indefinitely.

## Customer-facing overlong/failed voice response
Use the normal admitted outbound text path after terminal voice rejection/failure. v1 exact fallback strings:

```text
VOICE_TOO_LONG:
"Please send a voice note that is 2 minutes or shorter."

VOICE_UNREADABLE:
"I couldn't understand that voice note. Please try again or send your message as text."
```

These messages are deterministic communications fallbacks and MUST NOT invoke CommerceAgent. Do not add a human escalation path.

## Structured observability
Use the existing Shared logger/OpenTelemetry runtime; do not create a competing logger. Record bounded semantic outcomes:

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
At minimum:

- 30s OGG/Opus -> transcript -> one turn;
- exactly 120s -> accepted;
- >120s -> no transcription call, deterministic fallback;
- duplicate webhook/job -> one reservation, at most one completed logical turn;
- retry after successful transcription finalization -> no second transcription/turn;
- retryable download/STT failure -> no premature turn;
- unsupported/corrupt audio -> terminal bounded failure/fallback;
- blank transcript -> terminal fallback, no agent;
- explicit reply voice retains `contextMessageId` ownership;
- contextless voice uses BACKGROUND-001 routing before download;
- cross-tenant ambiguous voice -> no media download/transcription;
- spoken language is not sent to translation endpoint and returned transcript is passed unchanged into the normal conversation turn;
- raw bytes/URL are not persisted/logged.

## Non-goals

- outbound TTS/voice responses;
- streaming live calls;
- self-hosted Whisper/HuBERT/wav2vec;
- Shopify/recovery business decisions;
- audio retention/archive.

## Acceptance Criteria

- [ ] voice is an input modality to the existing ordered conversation pipeline, not a second agent pipeline;
- [ ] 120-second rule is enforced before paid transcription;
- [ ] duplicate/retry behaviour is durable and idempotent;
- [ ] customer language is preserved;
- [ ] raw media is transient.

## Validation
Inspect repository scripts first. Run focused voice/media tests, full declared tests/build/typecheck/Prisma validation, dependency install integrity, and:

```text
git diff --check
```

No live Groq test is mandatory in the normal suite. If an opt-in live-provider test is added, it must skip unless explicit credentials/flag are present and must not export customer audio.

## Stop conditions
STOP if the existing deployment lacks the required `GROQ_API_KEY` for `moda-messaging-worker`, if supporting WhatsApp audio requires another durable media store, or if a new infrastructure secret is required beyond the architecture above.

## Completion protocol
Return BACKGROUND-002 to `review`; STOP.

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
