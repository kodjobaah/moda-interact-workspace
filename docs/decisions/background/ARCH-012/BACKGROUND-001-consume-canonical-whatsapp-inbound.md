---
id: ARCH-012-BACKGROUND-001
architecture_id: ARCH-012
title: Consume canonical inbound WhatsApp events and preserve both reply modes
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-012-SHARED-002
- ARCH-012-DATABASE-001
- ARCH-007-BACKGROUND-010
- ARCH-007-BACKGROUND-011
- ARCH-010-BACKGROUND-013
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
enables:
- ARCH-012-BACKGROUND-002
- ARCH-012-SYSTEM-TEST-001
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-BACKGROUND-001

## Objective
Replace Background's incompatible local inbound WhatsApp event type with the canonical Shared contract and make the existing routing/persistence path explicitly correct for both customer reply modes:

```text
A. explicit native WhatsApp reply -> contextMessageId -> exact original outbound ConversationMessage -> Conversation
B. ordinary contextless message   -> active-conversation resolution using durable state
```

This task is primarily a contract/routing correction. Do not redesign accepted ARCH-007 coalescing, abuse admission or CommerceAgent semantics.

## Required dependency
Adopt the **exact architect-accepted Shared release recorded by SHARED-002**. Do not duplicate the schema locally and do not infer a package version from npm `latest`.

## Authorized implementation surface
Expected files only:

```text
package.json
package-lock.json
src/workers/whatsapp.worker.ts
src/integration/whatsapp/types.ts          # delete/supersede inbound type; outbound types may remain
src/services/recovery-routing.service.ts
src/services/conversation.service.ts
focused unit/integration tests for worker/routing/conversation persistence
```

Database submodule pointer may be updated only to the accepted DATABASE-001 commit according to normal submodule workflow. Do not edit database schema here.

## Current runtime controls that must survive this task
The 2026-09-16 Background baseline has accepted controls that post-date the original ARCH-012 overlay:

- `src/entrypoints/messaging.ts` starts `backgroundRuntimeConfigService` before creating the WhatsApp worker;
- `src/workers/whatsapp.worker.ts` exposes `createWhatsappWorker()` and binds dynamic concurrency through `bindWorkerConcurrency(worker, backgroundRuntimeConfigService, "whatsappQueueGlobalConcurrency")`;
- raw/settled abuse admission reads ARCH-014 runtime-configured limits rather than static constants;
- shop execution eligibility from ARCH-010 remains authoritative.

Do not revert, bypass, statically replace or duplicate those controls while changing inbound event typing/routing. `src/entrypoints/messaging.ts`, runtime-config services and queue-concurrency controller are **not** authorized implementation surfaces for this task.

## Exact routing behaviour

### Explicit reply
If `contextMessageId` is non-null:

1. find the outbound/local `ConversationMessage.providerMessageId == contextMessageId`;
2. if found, use its durable Conversation ownership exactly;
3. preserve `inReplyToProviderId = contextMessageId` on the inbound message;
4. do not override that exact route merely because another more-recent conversation exists.

If the referenced provider message is unknown, fall through to the normal contextless resolution; do not fabricate ownership.

### Contextless message
When `contextMessageId == null`, preserve current durable resolution principles:

- exactly one actionable recovery conversation for the phone -> resolve it;
- multiple actionable recoveries under one unambiguous shop/customer ownership -> use existing clarification flow rather than choosing a recovery by recency alone;
- actionable conversations across different tenant ownership -> `ambiguous-tenant`, no CommerceAgent invocation;
- no recovery conversation -> existing product-only/standalone ownership resolution may apply;
- shop execution eligibility remains authoritative.

Do not make `customerPhone` itself a tenant identity.

## Text and unsupported content

### Text
For `content.type == "text"`:

- persist `contentType=TEXT`, `transcriptionStatus=NOT_REQUIRED`;
- persist actual text;
- preserve provider/context IDs;
- increment/coalesce the conversation turn exactly as accepted ARCH-007 behaviour currently does.

### Unsupported
For `content.type == "unsupported"`:

- persist the provider message idempotently with `contentType=UNSUPPORTED` and bounded descriptor content;
- `transcriptionStatus=NOT_REQUIRED`;
- do not invoke CommerceAgent and do not turn it into an empty text turn;
- emit bounded structured operational evidence using Shared logging conventions;
- do not implement image/document/video understanding in this task.

Audio is reserved for BACKGROUND-002. BACKGROUND-001 must recognize the union and delegate/return without creating an empty-string conversation turn.

## Required tests

1. Shared contextual text event resolves exact original conversation and persists reply ID;
2. Shared contextless text event with one active conversation resolves normally;
3. contextless same-owner multiple recoveries enters existing clarification path;
4. contextless cross-tenant candidates remain unresolved and never call CommerceAgent;
5. unknown explicit context falls through safely without tenant fabrication;
6. text duplicate providerMessageId is idempotent;
7. unsupported event is persisted/observed but does not increment a CommerceAgent turn as empty content;
8. audio event is not processed as empty text and is handed to the voice path contract expected by BACKGROUND-002;
9. existing ARCH-007 raw and settled abuse admission remains in place;
10. existing turn coalescing/order semantics remain unchanged for text;
11. `createWhatsappWorker()` plus dynamic `whatsappQueueGlobalConcurrency` binding remain intact;
12. ARCH-014 runtime-configured abuse limits remain intact (no restored static limits);
13. ARCH-010 `contract-required` / `subscription-frozen` shop execution gates remain effective.

## Non-goals

- audio download/transcription;
- outbound transport redesign;
- recovery scheduling/Shopify reconciliation;
- human escalation;
- merchant WhatsApp onboarding.

## Acceptance Criteria

- [ ] no authoritative local `WhatsAppInboundEvent` remains;
- [ ] explicit reply and plain-message reply modes are both deterministic and tested;
- [ ] non-text is never converted to `""` and passed to CommerceAgent;
- [ ] existing routing/coalescing safety is retained rather than rewritten.

## Validation
Inspect `package.json` and run actual repository scripts plus focused tests. Minimum expected where declared:

```text
npm test
npm run build
npm run typecheck            # only if declared
npx prisma validate --schema database/prisma/schema.prisma
git diff --check
```

Use the documented baseline IDs for unchanged known failures; do not excuse a regression in changed files.

## Stop conditions
STOP if accepted routing semantics require a new product decision about recovery lifecycle or if database fields beyond DATABASE-001 are necessary.

## Completion protocol
Return BACKGROUND-001 to `review` and STOP.

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
