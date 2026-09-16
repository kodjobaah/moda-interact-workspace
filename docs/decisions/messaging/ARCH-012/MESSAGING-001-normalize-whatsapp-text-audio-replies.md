---
id: ARCH-012-MESSAGING-001
architecture_id: ARCH-012
title: Normalize inbound WhatsApp text, voice and reply context to the Shared contract
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-012-SHARED-001
- ARCH-007-MESSAGING-001
enables:
- ARCH-012-SYSTEM-TEST-001
- ARCH-012-SYSTEM-TEST-002
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-MESSAGING-001

## Objective
Make `moda-interact-messaging` a strict provider-normalization boundary for customer messages. It must preserve enough Meta evidence for Background to resolve either an explicit reply to a specific Moda message or an ordinary contextless WhatsApp message, and it must preserve voice media identity without downloading/transcribing media in the webhook request.

## Required dependency
Adopt the **exact architect-accepted package version published by ARCH-012-SHARED-001**. SHARED-001 now owns implementation and publication in one task. Read the exact published version from its Completion Report and install that exact version; do not guess, use a range, or derive a newer version.

## Authorized implementation surface
Expected files:

```text
package.json
package-lock.json
app/routes/whatsapp.tsx
app/lib/types/whatsapp.ts                 # remove/supersede local inbound event type
app/lib/queues/whatsapp.queue.ts          # only if queue typing requires
tests/whatsapp-queue-telemetry.test.mjs
tests/whatsapp-ingress-telemetry.test.mjs
new focused inbound-normalization test file if clearer
```

Do not add database access, Meta media download, transcription or tenant routing to Messaging.

## Exact normalization
For each verified Meta inbound `messages[]` object, construct and Shared-validate one `NormalizedWhatsAppInboundMessage`:

```text
providerAccountId      = entry.id
providerPhoneNumberId  = change.value.metadata.phone_number_id
providerMessageId      = message.id
customerPhone          = message.from
contextMessageId       = message.context?.id ?? null
occurredAt             = provider timestamp converted to offset-aware ISO
```

Content mapping:

```text
message.type == text
  -> {type:"text", text: message.text.body}

message.type == audio
  -> {
       type:"audio",
       mediaId: message.audio.id,
       mimeType: message.audio.mime_type ?? null,
       sha256: message.audio.sha256 ?? null,
       voice: typeof message.audio.voice === "boolean" ? message.audio.voice : null
     }

all other inbound message types
  -> {type:"unsupported", providerType: bounded original message.type or "unknown"}
```

Do not turn non-text messages into `text: null` or empty strings.

## Reply modes that must be preserved

1. **Explicit WhatsApp reply**: `message.context.id` is present -> publish it unchanged as `contextMessageId`.
2. **Ordinary message as reply**: no context object -> publish `contextMessageId: null`; do not infer the conversation in Messaging.

Background owns both resolution paths.

## Durable acceptance / queue behaviour

- preserve existing verified-signature boundary;
- validate via Shared before enqueue;
- publish to existing `whatsapp-events` queue / `message-received` job;
- preserve deterministic `providerMessageId`-derived job identity;
- preserve existing bounded retry/backoff;
- acknowledge Meta only after existing durable queue acceptance succeeds;
- no Meta media GET, speech API, Shopify API, DB or CommerceAgent operation in request lifecycle.

## Required tests
Use realistic Meta-shaped fixtures and prove:

- explicit text reply preserves `context.id`;
- contextless text produces null context;
- audio voice note preserves media ID/MIME/SHA/voice flag;
- context can also be present on audio and is preserved;
- unsupported image/document/video/sticker/location is explicit `unsupported`, not dropped/empty text;
- `entry.id` and `metadata.phone_number_id` remain separate provider identities;
- old `customerAddress` producer shape is no longer emitted;
- malformed provider identities or malformed content fail validation and are not queued;
- duplicate provider message receives the same deterministic job ID;
- no raw webhook body or audio payload is logged.

## Non-goals

- conversation resolution;
- media retrieval/transcription;
- outbound sending;
- recovery timing;
- merchant-owned WABA onboarding.

## Acceptance Criteria

- [ ] repository-local inbound event interface is removed or no longer authoritative;
- [ ] producer output is exactly Shared v1;
- [ ] both reply modes are faithfully represented;
- [ ] webhook acknowledgement path remains lightweight;
- [ ] voice payload is transported by media identity only.

## Validation
Inspect `package.json`, then run repository-declared commands:

```text
npm test
npm run typecheck
npm run build
git diff --check
```

Also run the focused normalization/queue tests explicitly.

## Stop conditions
STOP if the implementation needs tenant/shop lookup, transcription, raw media download, or a new queue solely for ARCH-012. Return the architectural gap instead.

## Completion protocol
Set to `review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Status
Implemented, validated, and published on the implementation task branch. Awaiting `moda_architect` review.

### Files Changed
- `app/routes/whatsapp.tsx`
- `app/lib/observability/whatsapp-ingress-telemetry.ts`
- `app/lib/types/whatsapp.ts` (removed)
- `package.json`
- `package-lock.json`
- `tests/whatsapp-inbound-normalization.test.mjs`
- `tests/whatsapp-queue-telemetry.test.mjs`
- `tests/whatsapp-ingress-telemetry.test.mjs`
- `tests/startup-contract.test.mjs`

### Validation Results
- Implementation commits: `2267f26`, `424e09d`, pushed to `task/ARCH-012-MESSAGING-001`.
- Exact dependency installed: `@modainteract/moda-interact-shared@0.12.0`, the ARCH-012-SHARED-001 accepted publication.
- Correction mapping: producer now uses `@modainteract/moda-interact-shared/whatsapp`, constructs strict Shared v1 events, preserves `entry.id` separately from `metadata.phone_number_id`, preserves explicit/contextless replies, transports audio media identity only, maps unsupported content explicitly, and rejects malformed payloads before queueing.
- Correction mapping: existing `whatsapp-events` / `message-received` queue, deterministic `providerMessageId` job ID, three attempts, exponential backoff, signature verification, and acknowledgement-after-queue-acceptance ordering remain intact.
- Correction mapping: removed the repository-local `WhatsAppInboundEvent` producer type; no database, media download, transcription, Shopify, tenant routing, or AI work was added.
- Focused normalization tests: 13 passed, 0 failed, covering text, audio, context, unsupported image/document/video/sticker/location, provider identity separation, malformed validation, deterministic job IDs, and no raw-body/audio logging.
- `npm test`: 34 passed, 1 skipped, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed. Build emitted existing Vite warnings about browser externalization of Node/Redis modules; no build failure.
- `git diff --check`: passed.
- Implementation worktree is clean after push.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
