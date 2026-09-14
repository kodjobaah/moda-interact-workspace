---
id: ARCH-012-SYSTEM-TEST-002
architecture_id: ARCH-012
title: Validate WhatsApp voice-note transport and transcription lifecycle
task_kind: system_test
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 41
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-012-MESSAGING-001
- ARCH-012-BACKGROUND-002
- ARCH-012-BACKGROUND-003
- ARCH-012-GATEWAY-001
enables: []
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-012-SYSTEM-TEST-002

## Objective
Prove that a WhatsApp customer can reply by voice and that the communication reaches the existing ordered Background conversation path without raw-audio retention, duplicate transcription or cross-tenant misrouting.

## Test infrastructure
Extend existing test infrastructure with deterministic fakes/emulators rather than calling live Meta/Groq in the normal suite:

- WhatsApp emulator must provide Meta-style inbound `audio` webhook payloads and media lookup/download endpoints;
- provide fixture OGG/Opus audio with known durations/content properties sufficient to validate <=120s and >120s policy;
- provide a deterministic transcription fake at the same adapter boundary used by BACKGROUND-002, returning controlled multilingual transcripts/failures;
- if BACKGROUND-002 exposes an optional provider base URL for testability, use that; do not patch production code from system tests.

## Required scenarios

1. 30-second voice note, explicit reply context -> exact conversation -> transcript -> one ordered CommerceAgent turn;
2. contextless voice note with one active conversation -> correct route before media download -> transcript -> one turn;
3. contextless cross-tenant ambiguous voice -> no media download and no transcription call;
4. exactly 120 seconds -> accepted;
5. >120 seconds -> no transcription call, `REJECTED`, deterministic "2 minutes or shorter" outbound text;
6. corrupt/unsupported audio -> terminal voice failure and deterministic retry/text fallback;
7. blank transcription -> no CommerceAgent invocation;
8. duplicate inbound webhook/job -> one durable audio message and one completed logical turn;
9. worker retry after completed transcription -> no second logical turn and no second transcription;
10. retryable transcription failure -> remains resumable without creating an empty turn;
11. French/non-English fake transcript is passed unchanged as transcript content; no translation-to-English stage occurs;
12. database contains media ID/MIME/hash/duration/transcription metadata but no raw audio bytes or signed provider URL;
13. logs/traces do not contain audio bytes, transcript text, signed URL or token.

## Out of scope

- benchmarking live Groq/OpenAI accuracy;
- outbound generated speech;
- long-form audio >120 seconds;
- image understanding;
- Shopify recovery scheduling/business logic.

## Acceptance Criteria

- [ ] voice is a first-class inbound modality through Messaging -> Background;
- [ ] duration policy is enforced before paid STT;
- [ ] route safety occurs before media/STT cost;
- [ ] exactly-once logical turn semantics hold under duplicate/retry scenarios;
- [ ] raw media remains transient;
- [ ] existing text path is not regressed.

## Validation
Run focused ARCH-012 voice system scenarios, the full declared system-test suite, and:

```text
git diff --check
```

If deployed Render validation is part of the accepted test environment, prove `WHATSAPP_BUSINESS_ACCOUNT_ID`, WhatsApp credentials and Groq credential presence only by configuration/readiness evidence; never print secret values.

## Stop conditions
STOP if a live external provider is required for the normal deterministic acceptance suite or if raw customer audio must be retained to make the test pass.

## Completion protocol
Return SYSTEM-TEST-002 to `review`; STOP.

## Completion Report

### Status
Not started.

### Validation Results
TBD.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
