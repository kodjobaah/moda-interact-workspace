---
id: ARCH-052-BACKGROUND-015
architecture_id: ARCH-052
title: Enforce shared-sender contextual recovery replies and accurate text/voice guidance
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 35
executor: codex
claimed_at: 2026-10-31T03:57:30Z
attempt: 1
depends_on:
  - ARCH-012-MESSAGING-001
  - ARCH-040-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-052-BACKGROUND-008
  - ARCH-052-SYSTEM-TEST-003
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-015 — Enforce shared-sender contextual recovery replies and accurate text/voice guidance

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Owner: `moda_background` / `moda-interact-background`; coordinator `moda_architect`. This is a **portable definition, defined but not materialised**. The developer's launcher creates the canonical mirrored task worktrees when implementation starts; no branch/commit/push is asserted here.

## Objective

Guarantee that a WhatsApp customer replying with text **or** a voice note to a recovery message sent from Moda's shared phone is resolved to the correct merchant/recovery, and that an ambiguous or invalid reply receives safe, accurate Reply guidance rather than guessed routing.

## Context

One Meta WABA/phone can send outbound recovery messages for many merchants to the same recipient. Existing `src/services/recovery-routing.service.ts` resolves quoted `contextMessageId` through `ConversationMessage.providerMessageId`, checks outbound confirmation/recipient and returns resolved/guidance/ignored. `src/services/whatsapp-inbound-processing.service.ts` checks STOP before routing, processes text and audio after routing, and persists `inReplyToProviderId`. `src/services/inbound-whatsapp-audio.service.ts` transcribes supported voice notes with a **120,000 ms** maximum. `src/services/routing-guidance.service.ts` presently says only "basket message" and does not tell customers voice notes are supported; it has silent cache-failure handling and an inaccurate unconditional `guidance_sent` event in its caller. Amend these existing services; **do not create another router or service**.

## Scope

- Inspect and extend `src/services/recovery-routing.service.ts`, `whatsapp-inbound-processing.service.ts`, `routing-guidance.service.ts` and existing tests under `tests/unit/services/` and `tests/integration/`. Update `inbound-whatsapp-audio.service.ts` only if a specific quoted-audio regression is proven; preserve its existing 2-minute policy and current transcription/dedup logic.
- Verify quoted text/audio ownership using existing Shared `NormalizedWhatsAppInboundMessage` v1 `contextMessageId` and `content.type`, existing Meta account/phone ID, recipient phone, outbound `ConversationMessage` and recovery/shop identity. No Shared schema, database migration, Meta subscription or queue contract changes.
- Replace ambiguous/invalid-route guidance with a concise shared-sender message that explicitly asks the customer to find the **specific store's recovery message**, use WhatsApp's **Reply** option on it and send a typed question or voice note (max two minutes). Maintain existing approved text/no-contact admission.
- Make provider-guidance outcomes and diagnostic handling observable through the shared structured logger without leaking customer content, contact details, shop lists or credentials.

## Out of Scope

- **Order-confirmation/transactional** notification support is NOT authorised by this recovery task: it has no confirmed durable order-message-to-merchant-conversation mapping in the inspected snapshot. A quoted unknown order-confirmation ID must not be attached to a recovery or fabricated order thread. Any later transactional-order reply feature requires separate architecture and tenant/order linkage.
- No new inbox, standalone Conversation, customer-service billing plan, tenant-wide routing service, media provider, outbound template editing, image/URL logic, post-window proactive send or alteration of STOP suppression rules.
- Do not change `ARCH-049-BACKGROUND-003`, `ARCH-052-MCP-005`, `ARCH-052-SHOPIFY-001`, accepted ARCH-012/040/045 tasks, or their completion histories. No `_index.md` modifications.

## Requirements

### Canonical routing — normative

1. STOP is handled **first**, before raw-abuse checks, routing, guidance, moderation or transcription. Existing rule is unchanged: STOP replying to a verified merchant outbound suppresses only that merchant; unquoted/unattributable STOP suppresses all registered merchants. A transcription of spoken words is **not** silently reclassified into a STOP command by this task.
2. Validate the inbound `providerAccountId` and `providerPhoneNumberId` against the currently configured sender before any shop lookup or customer guidance. Ignore mismatched sender identity; do not leak whether a customer or shop exists.
3. For non-empty `contextMessageId`, use that **exact** outbound `ConversationMessage.providerMessageId`; accept only if `direction=OUTBOUND`, `sentAt` confirms provider send, it is related to a single authoritative `CheckoutRecovery`/`Conversation`, and the stored recipient canonicalises to the inbound `customerPhone`. Verify `recovery.shopId`, conversation ownership, WABA/phone and current shop execution eligibility. The quoted message may be initial outreach, a confirmed follow-up or a later agent/human reply on the same recovery. Do not use a merchant name, order number, phone-only lookup or latest message as substitute proof.
4. If an explicit quote is missing, unknown, not provider-confirmed, cross-recipient, belongs to another sender or points at an outbound without a recovery, return `INVALID_REFERENCE` guidance (or `ignored` for wrong provider sender); **never fall back** to the most recent recovery, another merchant or generic CommerceAgent inference. Quoted historical/superseded Woo generations retain the existing `historical` route and must never enqueue a new active AI turn or resume an obsolete checkout.
5. For context-free input, retain only the existing *exactly-one-eligible-recovery* fallback, subject to the already validated provider/recipient and execution rules. If zero candidates return `NO_RECOVERY`; if two or more (including multiple merchants or multiple generations) return `MULTIPLE_RECOVERIES`. Never resolve ambiguity by ordering messages, naming a merchant, analysing free text or automatically choosing the latest. Preserve Woo generation filtering.
6. A text or audio reply to the same outbound ID resolves to the **same** conversation/recovery before message persistence, media download or transcription. Inbound `providerMessageId` idempotency must pin replay to the original stored conversation even if the replay changes quote ID; a conflicting/foreign persisted owner fails closed. Persist `inReplyToProviderId=contextMessageId` without creating a new Conversation or CheckoutRecovery. Voice must keep the existing 120-second rejection, transcription ordering, moderation and read/turn ownership checks.
7. For `guidance` results, **do not download media, transcribe, enqueue an AI turn, create a recovery, or charge a recovery conversation credit**. Guidance is a single, deduplicated, standalone platform response protected by the existing STOP/no-contact admission and may not reveal tenant/customer/order details.

### Required guidance copy and outcomes

- `MULTIPLE_RECOVERIES`: `This number sends messages for different stores. For help with a basket, find the message from that store and use WhatsApp's Reply option on that message. Then type your question or send a voice note (up to 2 minutes).`
- `NO_RECOVERY` and `INVALID_REFERENCE`: same guidance plus `If you cannot find the message, contact the store directly.` Never describe an unknown order/merchant as an existing recovery.
- `SHOP_UNAVAILABLE`: `Please contact the store directly for help with your basket.` Do not reveal business state.
- Preserve existing provider-sender checks, deduplication keyed to inbound provider message ID and recipient STOP fencing. Add an internal `RoutingGuidanceOutcome` discriminant (`sent`, `suppressed` with bounded reason, or `failed` with bounded reason) from `sendRoutingGuidance`; the caller must log **the actual outcome**, not unconditional `guidance_sent`. This is a Background-local type, not a new Shared wire contract.
- Every catch path (Redis NX/set, DB admission, Meta send) MUST record the actual originating exception (source message and cause where safe), operation and reason using `@modainteract/moda-interact-shared/logging`; distinguish `suppressed` by policy from `failed` by provider/cache/DB. Keep idempotent no-retry policy for guidance after ambiguous provider errors; no silent catches, `console.warn` replacement text, fabricated provider errors, credential/PII logging or new generic logger. Preserve fail-closed behaviour on uncertain guidance admission.

## Work Items

- [ ] Verify quoted outbound record lookup, sender/recipient/shop identity, historical recovery behavior, replay pinning and text/audio parity; implement only corrections evidenced by failing cases in the existing routing pipeline.
- [ ] Update `routingGuidanceText` with the exact copy above, avoiding merchant-name lists; update `sendRoutingGuidance` to return an internal outcome and use shared structured logging for original errors and suppression reasons.
- [ ] Update `whatsapp-inbound-processing.service.ts` so only a confirmed `sent` outcome is logged as guidance sent; ambiguous voice context cannot reach download/transcription/AI.
- [ ] Add targeted existing-service unit/Postgres integration tests covering the normative matrix and STOP, duplicate, provider-identity and redaction cases.

## Interfaces / Contracts

Existing published `@modainteract/moda-interact-shared/whatsapp`:

```typescript
// Already published; do not redefine/extend in this task.
type ContextualInbound = NormalizedWhatsAppInboundMessage;
// Fields used: providerAccountId, providerPhoneNumberId, providerMessageId,
// customerPhone, contextMessageId: string | null,
// content: {type:"text"; text:string} | {type:"audio"; mediaId:string; ...} | ...
```

Existing `RecoveryRoutingService.resolveInboundMessage(event)` and its `RecoveryRoute` (`resolved` with `conversationId`, `checkoutRecoveryId`, `shopId`, `mode: active|historical`; `guidance` with existing `RoutingGuidanceReason`; or `ignored`) stay the primary boundary. The **internal** `sendRoutingGuidance()` result is a tagged type: `{kind:"sent"}` | `{kind:"suppressed"; reason:"DUPLICATE"|"NO_CONTACT"|"INVALID_SENDER"|"UNSUPPORTED"}` | `{kind:"failed"; reason:"CACHE_UNAVAILABLE"|"DB_ADMISSION_FAILED"|"PROVIDER_SEND_FAILED"}`. Source failures must be logged before returning a failed result. Do not export this type through Shared or expose raw error bodies to the model/WhatsApp.

## Dependencies

- `ARCH-012-MESSAGING-001` — Complete; Shared inbound normalization includes reply context and audio type.
- `ARCH-040-BACKGROUND-002` — Complete; recovery conversation/AI turn routing and receipt infrastructure.
- `ARCH-045-BACKGROUND-005` — Complete; STOP precedence and deduplicated merchant/global suppression.

## Enables

- `ARCH-052-BACKGROUND-008` — can advertise text/audio Reply help once the route is accepted.
- `ARCH-052-SYSTEM-TEST-003` — shared-number cross-merchant certification.

## Acceptance Criteria

- [ ] Same customer and same Moda sender can hold independently provider-confirmed outbound recovery messages for two shops; explicitly quoted text and voice each persist/turn **only** in the correct shop/recovery. No session, AI invocation, merchant handover, usage charge or conversation leaks across shops.
- [ ] Wrong `contextMessageId`, wrong recipient, wrong provider account/phone, unsent/unconfirmed quote and a quoted outbound unrelated to recovery never fall back to any other shop, even when one other recovery is eligible. Unknown quoted order-confirmation message does not route to a recovery.
- [ ] Context-free exactly-one eligible recovery retains existing permitted behavior; multiple recoveries yield one deduplicated neutral guidance, including for audio, without media download or transcription. No fabricated tenant/order identity or merchant enumeration.
- [ ] Historical/superseded Woo quotes remain historical and do not schedule active AI, checkout revival or another initial outreach. Duplicate inbound message IDs preserve existing conversation owner.
- [ ] STOP precedence and all-merchant versus quoted-merchant semantics unchanged; guidance no-contact and retry suppression still work. Guidance never creates a new conversation/credit.
- [ ] User-facing copy expressly says to use WhatsApp Reply to the specific store message, supports text/voice (2-minute limit), and cannot be misunderstood as a guarantee that plain chat text will route safely with several merchants.
- [ ] Original provider/cache/DB errors are captured by the shared logger with truthful `sent|suppressed|failed` classification, identifiable redaction/truncation, and no sensitive payloads in logs, guidance or model context. No silent caught exceptions.

## Validation

- [ ] Unit tests: quoted text, quoted audio, second merchant same phone, wrong recipient/provider identity, unsent outbound, mismatched conversation ownership, absent/out-of-scope quote, duplicate inbound replay with changing `contextMessageId`, no-context zero/one/two recovery candidates and latest Woo generation handling.
- [ ] Audio tests: guidance happens before media fetch/transcription, 120-second upper boundary, staleness/retry and moderation preserved; ambiguous voice causes zero AI turns and no additional charges.
- [ ] Guidance tests: exact copy per reason, deduplicated Meta text send, no-contact/STOP priority, cache/DB failure logged and fail-closed, original Meta error wording retained after explicit redaction, outcome event reflects actual delivery.
- [ ] Existing ARCH-012/040/045/046 inbound text/audio/moderation and opt-out suites; declared Background lint/typecheck/build, `git diff --check`, with start-of-attempt worktree and submodule evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are satisfied, complete the task report, set status `review`, return the implementation and parent task branch evidence to `moda_architect`, and STOP. Do not begin enabled work or modify another agent's task or `_index.md`.

## Implementation Notes

Inspect current Background source before editing; use task-dedicated launcher-resolved mirrored worktrees and the shared logger from `@modainteract/moda-interact-shared/logging`. No silent exception handling, generic logger, new source-of-truth table or code outside Background ownership. Record specific failing tests that justify any routing algorithm change; do not rewrite an already-correct route just to satisfy the new task. Preserve the fixed existing recovery 24-hour conversation window and two proactive sends maximum.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Existing Shared inbound schema is already published; Meta's context ID is present when the user actually invokes WhatsApp Reply, including for supported audio inbound.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any missing outbound provider receipt, source contract or non-recovery order mapping must be returned to the architect, not replaced with an inferred owner.

## Architect Review

### Review Status

Pending.

### Review Notes

New scoped recovery guidance task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
