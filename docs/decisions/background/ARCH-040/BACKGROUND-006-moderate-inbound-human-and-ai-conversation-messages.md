---
id: ARCH-040-BACKGROUND-006
architecture_id: ARCH-040
title: Moderate customer, merchant and CommerceAgent conversation content
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-005
  - ARCH-040-BACKGROUND-002
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SHOPIFY-001
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-18
updated: 2026-10-18
---

# ARCH-040-BACKGROUND-006 — Moderate customer, merchant and CommerceAgent conversation content

## Architecture

ARCH-040 parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. **Defined but not materialised**. DATABASE-001 and BACKGROUND-001 are already complete and must not be reopened; BACKGROUND-002 is reported in progress by the developer, although the supplied archive still says `ready`. **Do not claim BG006 until BACKGROUND-002 and DATABASE-005 are architect-accepted Complete.**

## Objective

Implement and wire **one platform-agnostic OpenAI moderation capability** into (a) verified customer inbound WhatsApp content before ordinary CommerceAgent processing, (b) HUMAN merchant outbound before irreversible Meta dispatch, and (c) dynamic AGENT/AUTOMATION outbound before Meta dispatch. Persist auditable decisions and ensure no content is sent or given to normal AI context under an absent, stale, blocked or review-required decision.

## Context

The October 18 snapshot has inbound WhatsApp BullMQ (`src/workers/whatsapp.worker.ts`), `ConversationService.receiveMessage()`, `ConversationTurnProcessor`, `OutboundMessageDeliveryService`, and existing HUMAN policy/dispatch modules under `src/services/recovery-conversation/`. `BACKGROUND-001` already implements deterministic HUMAN spam/rate/suspension and final-send fences. `BACKGROUND-002` owns wiring these into production and is actively being worked on. `DATABASE-005` will add assessments against existing `ConversationMessage` or `MerchantConversationSendCommand`. Do not build a new sender, another inbox, new scheduler or separate commerce-platform processing.

Official API: `POST /v1/moderations`, SDK `openai.moderations.create({ model: "omni-moderation-latest", input: text })`; classify results using the returned `flagged`, `categories`, `category_scores`, `category_applied_input_types`. `omni-moderation-latest` supports text and certain image classifications, but v1 explicitly handles **text and existing completed audio transcription only**, not raw audio or image media. The vendor may update model internals, so do not treat scores as immutable guarantees.

## Scope

- One injectable OpenAI moderation client and policy adapter in `moda-interact-background` (the repo already depends on `openai`). No separate moderation API server or Shared schema publication.
- Durable assessment reservation/digest matching, provider retries and safe outcome mapping using `DATABASE-005`.
- Integration into the existing inbound BullMQ path, HUMAN PostgreSQL command dispatcher, CommerceAgent reply path and relevant dynamic automated outbound content.
- Expose minimal stable reason/status projection to existing Shopify and Woo server readers; no UI changes here.
- Focused unit tests with fake OpenAI responses and integration tests with disposable Postgres and existing worker harness; no real customer text, production secrets or network calls in automated tests.

## Out of Scope

- Do not edit the completed DATABASE-001 or BACKGROUND-001 tasks/code merely to relocate their responsibilities; reuse their accepted services through compositional seams. Do not change BG002's scope/branch while it is in progress.
- No new BullMQ queue or shop/platform-specific queue, new webhook request-time network call, Redis publication, worker deployment, separate conversation, customer block list or additional follow-up credit.
- No global automatic shop suspension based solely on a model flag, no global content deletion, no direct moderation logic in Shopify or WooCommerce, and no unsupported promises of perfect abuse detection.
- No image moderation, raw-audio moderation, file scanning or prohibited child-safety material uploads. Such media must follow an explicit restricted path and separate approved safety procedure; do not send raw unknown media to the moderation endpoint.
- No new LLM-based appeals, reviewer portal, policy authoring UI or unlimited retry scheduler.

## Requirements

### 1. New small modules — concrete responsibilities and signatures

Create modules under `src/services/conversation-moderation/` (equivalent existing conventions allowed; **no 300+ line all-in-one service**):

```ts
// moderation-client.ts
export type ModerateText = (input: { text: string; model: string; timeoutMs: number }) =>
  Promise<{ flagged: boolean; categories: Record<string, boolean>;
    categoryScores: Record<string, number>; appliedInputTypes?: Record<string, string[]>;
    returnedModel: string; requestId?: string }>;

// moderation-assessment.service.ts
export type ModerationSubject =
  | { kind: 'CUSTOMER_MESSAGE' | 'AGENT_MESSAGE' | 'AUTOMATION_MESSAGE'; messageId: string }
  | { kind: 'HUMAN_COMMAND'; commandId: string };
export type ModerationResult =
  | { kind: 'allow'; assessmentId: string; digest: string; policyVersion: string }
  | { kind: 'block'; assessmentId: string; reasonCode: string }
  | { kind: 'review_required'; assessmentId: string; reasonCode: string }
  | { kind: 'retry'; assessmentId: string; retryAt: Date };
export interface ModerationAssessmentService {
  assessText(input: { subject: ModerationSubject; shopId: string;
    conversationId: string; effectiveText: string; inputKind: 'TEXT' | 'TRANSCRIPT' | 'TEMPLATE_PARAMETERS';
    policyVersion: string; now: Date }): Promise<ModerationResult>;
  requireCurrentAllowance(input: { subject: ModerationSubject; effectiveText: string;
    policyVersion: string }): Promise<boolean>;
}
```

The caller's `shopId` is a tenant-scoping assertion that MUST be independently verified against the real recovery/conversation in PostgreSQL. Caller-provided text must be matched to the canonical persisted message/command payload and its SHA-256; never accept a UI-provided approval or digest as authority. For an AGENT candidate, use the pre-existing reserved/prepared `ConversationMessage.id` and the **final effective text** (including any terminal/fallback substitution) before provider admission.

- `moderation-policy.ts`: pure classifier policy receiving vendor response + actor, returning `ALLOW`, `BLOCK` or `REVIEW_REQUIRED` and a bounded reason. Initial version `arch040-moderation-v1`: `flagged === false` -> ALLOW; `flagged === true` -> BLOCK outbound / suppress ordinary AI processing inbound, with category-specific `reasonCode`, subject to explicit safe-handling exceptions noted below. Invalid/incomplete/missing model result -> RETRYABLE_ERROR, **never ALLOW**. Empty input/unsupported media -> REVIEW_REQUIRED, never a fabricated safe approval. Do not use an arbitrary uniform score threshold; record scores for calibration only. Version any future policy change and invalidate cached approval for new content or new policy version.
- `moderation-client.ts`: reuse installed `openai` SDK, `OPENAI_API_KEY` secret from Background runtime, `omni-moderation-latest` default; inject client/clock for tests. No browser/API key. Set an explicit bounded timeout (suggested 8s), SDK retries disabled and bounded policy retries for transient 429/5xx/timeouts (example 10s, 30s, 120s; configurable), circuit/backpressure where needed. Bad credentials/config or invalid model response fail closed and expose a bounded operational error; do not silently substitute a different provider/model.
- `moderation-assessment.service.ts`: read-or-create durable assessment by subject/content digest/model/policy, claim via lease/CAS, call OpenAI **outside** a DB transaction, validate complete result shape, persist result atomically. Reuse allowed assessments for identical digest/policy; never re-call OpenAI on mere UI polling or replay of same command. Persist category-name flags/scores bounded and a returned model ID, not a second copy of content; redact PII/secrets in structured logs.
- `moderation-decision-adapter.ts`: translate `BLOCK`/`REVIEW_REQUIRED`/`RETRYABLE_ERROR` into existing command/AI/turn control paths. `BLOCK` human command terminates with `failureCode=HUMAN_CONTENT_MODERATION_BLOCKED` and no Meta send/credit; `REVIEW_REQUIRED` uses `HUMAN_MODERATION_REVIEW_REQUIRED` and no send; transient errors leave pre-dispatch command safely retryable at the same ID; never change an already `DISPATCH_ADMITTED`/`UNKNOWN` provider call to unsent or automatically resubmit it.

### 2. Explicit integration call-site matrix

| Existing source | Integration change | Critical invariant |
|---|---|---|
| `src/workers/whatsapp.worker.ts` (`processInboundMessage`) | After verified route and persist/dedupe, obtain text assessment before enqueue/normal turn eligibility. Audio uses completed transcript after existing `inbound-whatsapp-audio.service.ts`; unsupported media is not auto-allowed. | Inbound webhook/queue acknowledgement does not wait on OpenAI HTTP; subsequent Background work owns classification. Persist all inbound text even when flagged. |
| `src/services/conversation-turn-processor.service.ts` and `src/services/conversation.service.ts` | Gate real AI turn on the moderation state of all candidate inbound messages, then filter blocked/review-required content from agent history/context. Include sender-aware HUMAN context already specified by BG002. Moderate the final agent response before prepared delivery. | A queued turn must not race ahead of moderation; no blocked text, summaries or tool inputs leak into normal AI context; no stale AI send after takeover. |
| `src/services/recovery-conversation/merchant-send-command.service.ts` or BG002's dispatcher | Assess leased HUMAN command's canonical payload before BG001 `OutboundSendFenceService.admitFinalSend`. If blocked, close same command with stable reason; transient moderation failure defers same command. | Same command/attempt/credit identity; no new queue, shop-specific scheduling or re-send of provider-unknown work. |
| `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` | At the common final text/template delivery boundary require current ALLOW for **the actual outgoing content and sender**; apply to AGENT and dynamic AUTOMATION too, including safe fallback/terminal paths. | Moderation before dispatch permit; ownership/recipient/window/billing fence still enforced independently; `ALLOW` does not skip other gates. |
| `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` (if dynamic content) | Moderate dynamic/customer-specific template parameters or a canonical rendering if available. Approved static template alone remains governed by existing approval/recipient eligibility. | Do not claim that unseen Meta-rendered text was semantically moderated; do not silently permit unmoderated arbitrary dynamic parameters. |
| Existing `src/entrypoints/messaging.ts` and local `src/index.ts` | Configure and inject one service, wired through the existing worker lifecycle. | No new queue/worker deployment; clean startup/shutdown; no separate Shopify/Woo code path. |

**Ordering clarification:** current `processInboundMessage()` runs inside an existing BullMQ worker. Never introduce synchronous OpenAI calls in Meta webhook ingress. The BullMQ job can await bounded moderation or requeue/defer under its existing retry contracts; ensure inbound acknowledgement and durable message persistence first. For HUMAN commands reuse BG002's single Postgres polling dispatcher and `nextAttemptAt`. For AI failures use existing delayed/retryable turn machinery, not another queue. Consider all turn phases, including audio transcript completion, repeated/out-of-order webhooks, stale inboundVersion and stale controlRevision.

### 2.1 Provider bypass inventory (explicit review obligation)

Before wiring only the named services, search the accepted BG002 tree for all calls to `sendWhatsAppText`, `sendWhatsAppTemplate` and direct provider adapters, including routing-guidance, audio fallback, recovery template and terminal/fallback delivery. For each callsite record whether its effective text is (a) recovery/customer-facing dynamic text requiring BG006 moderation, (b) an approved static/operational template whose dynamic parameters must be assessed, or (c) a non-conversation flow excluded with documented justification. Do not leave an alternative direct provider path that can send unmoderated recovery-linked HUMAN/AGENT/dynamic AUTOMATION content. Do not globally moderate unrelated platform/system traffic without architectural approval.

### 3. Precise safety policy and exception handling

- **CUSTOMER:** A verified inbound may be recorded regardless of classification. If flagged, do not feed that text/transcript or a summary derived from it to CommerceAgent's normal prompt, retrieval, tool calls or automatic reply generation. Mark review-required/blocked reason in the read model, keep the original message in the existing tenant-scoped transcript for appropriate review. Do **not** treat user anger, legitimate complaints or self-harm discussion as proof the customer is malicious; no automatic punitive block or merchant suspension from one flag. Where a separately approved safe-support flow exists, use it; otherwise suppress normal AI response and surface a safe, neutral state to the merchant. Normal 24-hour window accounting still follows verified inbound WhatsApp receipt.
- **HUMAN:** An outbound flagged message or review-required result cannot reach Meta. The merchant can revise/re-submit as a **new content digest and new idempotent command**; do not silently mutate the original frozen command. Existing deterministic shop/recipient rate/suspension checks remain in force. Do not consume a recovery follow-up or billable credit for definitively blocked/unsubmitted content; release pre-dispatch reservation through existing accepted billing semantics.
- **AGENT:** Moderate final generated text before any provider dispatch identity is granted. Flagged candidate is suppressed, recorded with bounded failure reason and no automatic retry that sends identical blocked text. For v1 do not automatically regenerate repeatedly, risking repeated harmful output or infinite retry; use explicitly approved safe fallback only if that fallback itself passes moderation and normal send eligibility.
- **AUTOMATION/TEMPLATES:** For plain dynamic outbound text moderate effective text. For approved static Meta templates, do not pretend to inspect unrendered provider content; moderate user/merchant-supplied dynamic parameters deterministically (or full canonical rendering if available) before dispatch, and keep existing template approval checks.
- **Unsupported media:** v1 only supports text and completed audio transcriptions. Image/attachment moderation may be a later architecture; no raw audio/image forwarding to moderation. Messages with no safe text must not get an ALLOW through an empty-string shortcut. Known/suspected child-safety material requires its own appropriate escalation and must not be uploaded to this endpoint.
- **Moderation unavailable:** no fail-open. Transient faults return retryable state with bounded backoff without acknowledging a send as successful. Permanent misconfiguration remains a visible operational block; do not infinite-loop or corrupt inbound version/worker progress. Repeated flagged customer messages are observable without flooding review events or expanding prompt context.
- **False positives/review:** persist audit scores and categories for privileged inspection. An Admin review can annotate the assessment or use existing `ShopHumanMessagingRestriction`, but cannot silently turn a previous BLOCK into an unrestricted send. No automatic shop suspension/customer ban from a single model decision.

### 4. State machine and idempotency proofs

```text
Inbound CUSTOMER:  verified, persisted -> PENDING/CHECKING -> ALLOW -> normal eligible turn
                                          -> BLOCK/REVIEW_REQUIRED -> retain transcript; exclude from AI
                                          -> RETRYABLE_ERROR -> delay same turn / reassess; never normal AI

Outbound HUMAN:    ACCEPTED/CLAIMED -> moderate identical frozen command payload
                                ALLOW -> BG001 final dispatch permit -> existing Meta transport/receipts
                                BLOCK/REVIEW_REQUIRED -> terminal no-send outcome, no recovery debit
                                RETRYABLE_ERROR -> nextAttemptAt same command ID, no Redis publication

Outbound AGENT:    reserved message -> moderate final effective content
                                ALLOW -> existing final permit and Meta
                                BLOCK/REVIEW_REQUIRED -> fail/suppress prepared message, no Meta
                                RETRYABLE_ERROR -> safe existing retry/suppression, no Meta
```

A cached `ALLOW` must be rejected if any of: subject ID, effective text SHA-256, policy version, message direction, conversation/shop binding or expected provider-admission content differ. Moderation *cannot* revoke an already irreversible Meta send. All final submission race rules from BG001/BG002 remain authoritative.

### 5. Observability/configuration/cost guardrails

- Configuration: `MODA_CONVERSATION_MODERATION_MODEL` default `omni-moderation-latest`, `MODA_CONVERSATION_MODERATION_POLICY_VERSION` default `arch040-moderation-v1`, bounded timeout/backoff/concurrency settings. `OPENAI_API_KEY` is injected server-side only. Unsupported or malformed configuration blocks protected processing with bounded diagnostic codes rather than disabling checks.
- Structured events via `@modainteract/moda-interact-shared/logging`, e.g. `conversation.moderation.started`, `.allowed`, `.blocked`, `.review_required`, `.retry`, `.dependency_unavailable`; record shopId, conversationId, assessmentId, actor, category names, latency bucket and reason code. **Never** log message text, transcript, media URLs, phone, OpenAI key or raw private notes.
- Avoid unbounded OpenAI calls on duplicate events: assessment digest deduplication, in-flight lease/claim and bounded concurrency per worker; apply reasonable per-shop fairness and global backpressure. Distinguish provider rate limiting from malicious merchant/customer traffic.
- OpenAI moderation classifications are signals, not infallible proof of abuse. Establish an offline multilingual fixture set including legitimate support complaints and self-harm help-seeking content. Do not invent claims of equal quality in every supported language or of zero false positives.

### 6. Required tests (code-level examples, not developer certification)

1. Client parsing: `flagged:false`, `flagged:true`, multiple categories, missing results, malformed scores, 429, 5xx, timeout, missing secret; fully mocked network.
2. Persistence: one assessment for duplicate inbound and same merchant command, separate for changed content digest or policy version; concurrent workers/lease expiry; no double classification or stranded checking state.
3. Inbound: verified customer text persisted; flagged content does not reach LLM history/retrieval/tool calls; legitimate unflagged message continues; audio transcript same; unsupported image never auto-allowed; one blocked message must not poison later allowed messages.
4. AI: final generated text moderation uses actual send bytes; blocked candidate fails without Meta; false-positive/review state visible; HUMAN takeover still fences old AI admission.
5. HUMAN: flagged command rejected with original command ID, no WhatsApp, no credit, no double abuse counters; transient moderation failure reuses command and safely retries; unknown provider state never resent.
6. Template: static template/dynamic parameter paths don't bypass policy; one recovery sequence-2 follow-up cannot be claimed twice by HUMAN and automation.
7. Administrative: flagged merchant incidents queryable without exposing message bodies in logs; shop-wide suspension remains separately controlled; no automatic account suspension after one flagged message.
8. Mixed tenancy: two shops, identical customer text, separate moderation identities, no cross-tenant access; Shopify/Woo send commands share exact same Background code path.
9. Worker integration: real `whatsapp.worker.ts`, `ConversationTurnProcessor`, dispatcher, final send and receipt paths call moderation once per stable subject/digest; no duplicate scheduling, no platform-conditional branch.

## Work Items

- [ ] Add injectable OpenAI SDK moderation client, strict response decoder and per-actor policy with versioned decisions.
- [ ] Add durable assessment creation, lease/retry/reconciliation and content SHA-256 matching through DATABASE-005.
- [ ] Integrate inbound CUSTOMER text and completed audio transcription before any ordinary AI consumption; exclude flagged material from context.
- [ ] Integrate HUMAN command pre-send, AI effective-reply moderation and dynamic AUTOMATION/template checks into existing BG002 execution paths.
- [ ] Preserve existing AI/HUMAN ownership fence, recovery follow-up, billing, provider uncertainty and shop suspension logic.
- [ ] Add focused unit/integration tests plus startup/shutdown/negative-race proofs without external API calls.
- [ ] Record exact touched files, test commands, outstanding gaps and dependency versions in Completion Report.

## Interfaces / Contracts

Consumes published/generated Prisma types for `ConversationModerationAssessment` from DATABASE-005, existing `MerchantConversationSendCommand`, `ConversationMessage`, and BG001/BG002 runtime methods. OpenAI `moderations.create` is an **external vendor API**, not a new Moda Shared runtime contract. Exposes only stable status/reason read projections to Shopify/Woo/Moda Admin consumers; no raw `categoryScores` or OpenAI request metadata in public responses.

## Dependencies

- ARCH-040-DATABASE-005
- ARCH-040-BACKGROUND-002

**Do not claim while BG002 remains `in_progress` or `ready`.** The user reports ongoing BG002 work; reconcile its canonical branch/status before launch, and require accepted completion before starting this task.

## Enables

- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SHOPIFY-001
- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [ ] All supported CUSTOMER, HUMAN, AGENT and dynamic AUTOMATION text paths require a current persistent moderation decision before normal AI processing or new Meta provider admission.
- [ ] Flagged/review-required customer content is persisted but excluded from ordinary agent context; flagged merchant/AI outbound is never submitted to Meta.
- [ ] For exact subject/digest/policy matches, duplicate events/retries reuse assessments and do not double-send, double-charge or double-count abuse incidents.
- [ ] Moderation failures do not silently bypass safety; blocking and retry states are visible without leaking sensitive content.
- [ ] Existing one-conversation, recovery follow-up, AI/HUMAN mode, shop suspension, tenant isolation and platform-neutral scheduling guarantees are preserved.

## Validation

**Developer validation is performed separately and is NOT an acceptance criterion for this implementation task.** The implementing agent must record any focused checks actually run, but developer-owned environment/integration certification follows review. Do not mark external Live Moderation, LocalWP, Shopify browser testing or full system tests as prerequisites of this task's functional acceptance.

Suggested developer checks: `npm run test:unit`, targeted Vitest moderation/worker tests, `npm run build`, PostgreSQL harness, fake moderation transport integration, `git diff --check` and final SYSTEM-TEST-001/002/003 with the respective platform stream.

## Stop Condition

When implementation and functional acceptance conditions are met, record Completion Report and move this newly defined task to review through the assigned developer/agent workflow; stop. Do not implement API, Shopify, Woo or Admin task changes in BG006.

## Implementation Notes

- Before coding, inspect the **completed BG002 implementation**; filenames listed above are confirmed in the 2026-10-18 snapshot, but may change by the time BG006 becomes Ready. Reuse actual accepted extension points.
- Do not install another `openai` dependency blindly; `moda-interact-background/package.json` already includes `openai` version `^7.10.0` in the supplied snapshot.
- Preserve 20-locale and merchant screen behaviour through existing platform tasks; moderation decision messages should be stable reason codes translated by the existing UI.
- Do not add production secrets to Git or log external moderation input.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; developer validation is separate.

### Deviations

None.

### Assumptions

Text and completed audio transcription in v1; no image moderation.

### Unresolved Issues

None at task definition.

### Architectural Concerns

None at task definition.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
