---
id: ARCH-052-SYSTEM-TEST-003
architecture_id: ARCH-052
title: Certify exact quoted-message text and voice routing across merchants on one sender
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-052-BACKGROUND-015
  - ARCH-052-BACKGROUND-008
  - ARCH-052-ADMIN-003
  - ARCH-012-MESSAGING-001
  - ARCH-040-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables: []
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-SYSTEM-TEST-003 — Certify exact quoted-message text and voice routing across merchants on one sender

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Owner: `moda_system_test` / `moda-interact-system-test`. This is a portable terminal validation definition, **not materialised**. Run only after all implementation dependencies are Complete and architect-accepted; developer manual testing may precede system tests.

## Objective

Prove that Meta contextual replies (typed and voice) are routed to the correct recovery across Shopify and WooCommerce merchants sharing a WhatsApp sender, and that ambiguous/invalid inbound content fails safely without cross-tenant leakage or extra recovery credits.

## Context

Background-008 sends approved merchant-identified initial templates with durable Meta outbound IDs. Background-015 verifies quote-based recovery routing and safe guidance. Existing ARCH-012 normalisation already carries `contextMessageId` for both text and audio. This certification tests the **composition** of these independently owned components; it is not permission to implement routing inside System Test.

## Scope

- Build a disposable two-provider fixture with one Meta `providerAccountId` and `providerPhoneNumberId`, one canonical customer phone, at least one Shopify shop (A) and one WooCommerce shop (B), and three distinct provider-confirmed recovery messages: A1, B1 and A2. Record shop/recovery/conversation/attempt IDs, `ConversationMessage.providerMessageId` and confirmed sent timestamps for each.
- Exercise the real normalized inbound processing via existing message queue/worker, with mocked Meta/media/transcription only at external boundaries and disposable PostgreSQL/Redis. Assert durable conversation ownership, provider receipts, moderation, billing and guidance messages.
- Verify approved immutable template BODY and actual resolved `shop.name` for each sender message; the shared phone profile must not be the sole merchant identity. Test text and audio WhatsApp Reply to each provider outbound ID.
- Include invalid, absent and forged quote/source identities, historical Woo generation, duplicate inbound delivery, same-customer multiple merchants, ambiguous context-free text/audio, and STOP precedence.

## Out of Scope

- No checkout-link creation, restoring coupons on a customer click, new WhatsApp sender number, speech-recognition model implementation, order-confirmation conversation routing, data migration, tenant-wide inbox or implementation changes to Background source.
- Do not modify existing ARCH-052-ADMIN-003/BACKGROUND-008/BACKGROUND-015 implementations during validation. Defects return to owning agent via architect review.

## Requirements

### Deterministic fixture and routing matrix

| Case | Input | Expected durable and outbound result |
|---|---|---|
| A1 text quote | `contextMessageId=wamid.A1`, inbound `type=text` | A1 recovery Conversation only; B untouched; one AI turn when active |
| B1 audio quote | `contextMessageId=wamid.B1`, inbound `type=audio` | B1 recovery Conversation only, media retrieved/transcribed only after successful routing; A untouched |
| A2 voice quote | `contextMessageId=wamid.A2`, valid 120-second-or-shorter audio | A2 exact recovery, not A1 or B1; no duplicate conversation |
| Same phone, no quote | Context null with multiple candidates, text | One neutral guidance, no AI, no credit, no shop disclosure |
| Same phone, no quote | Context null with multiple candidates, audio | One neutral guidance, no media fetch or transcription, no AI or credit |
| Invalid quote | Unknown/unsent/cross-recipient provider ID | INVALID_REFERENCE guidance only; **no** fallback to latest merchant |
| Wrong sender | Wrong WABA/phone number ID | Ignored, no shop lookup or guidance |
| Historical quote | Valid B1 but Woo newer recovery generation exists | Persist historical inbound in B1 only; no active AI, new session or revive |
| Replay | Same inbound `providerMessageId` with a different quote ID | Durable original owner retained; no second inbound turn/send/credit |
| STOP reply to A1 | Exact verified quote | Only merchant A suppressed, none of B changed |
| Standalone STOP | No quoted context | All registered merchants for sender suppressed, no ordinary guidance |
| Unknown order quote | Message ID not linked to a verified recovery | No guessed recovery/merchant; neutral guidance or ignore |

- All 20 supported locales retain merchant identity and direct WhatsApp Reply/text/voice semantics in approved template revisions, with frozen parameter indices and Meta approval; the system test can inspect locale fixture/canonical registration snapshots without emitting 20 live sends.
- Verify a missing/compliant-unapproved template produces typed no-send; zero provider send, zero accepted initial attempt or newly charged credit. A live confirmed send must have provider ID/sent timestamp and exact outbound-message/attempt link.
- Capture the provider-origin error from injected Meta guidance/send failure and Redis/DB fault through Shared logger; compare literal provider message (after declared redaction) with logged value. Internal reason codes and delivery outcome must not replace source error, and `guidance_sent` may appear only for an actual successful send.
- Preserve existing moderation, human handover, two-proactive-message limit and 24-hour customer service window; do not charge an extra recovery-conversation credit merely for an inbound text/audio or neutral platform guidance.

## Work Items

- [ ] Seed disposable two-merchant/three-recovery/one-sender fixture with stable provider IDs and exact shop binding evidence.
- [ ] Drive queued text/audio/STOP inbound messages through canonical normalized event processing, compare durable routing, actual sent guidance and all absence-of-side-effect invariants.
- [ ] Exercise template locale approval and missing/unapproved fallback cases; verify shop-specific names, exact user Reply instructions and 120-second voice limit.
- [ ] Capture shared structured logs and record source-preserving provider errors plus redaction/tenant-isolation tests. Produce reproducible evidence and clean up Postgres/Redis/fixture artifacts.

## Interfaces / Contracts

Use published `@modainteract/moda-interact-shared/whatsapp` `NormalizedWhatsAppInboundMessageSchema` v1 with `contextMessageId`; existing `ConversationMessage.providerMessageId`, `inReplyToProviderId`, `Conversation.checkoutRecoveryId`, `RecoveryOutreachAttempt.outboundMessageId`; approved ARCH-052 `shop.name` template binding and Background-local `RecoveryRoute`. No new Shared interface.

## Dependencies

- `ARCH-052-BACKGROUND-015` — accepted contextual recovery routing and guidance.
- `ARCH-052-BACKGROUND-008` — accepted confirmed outbound receipt and approved text.
- `ARCH-052-ADMIN-003` — accepted immutable merchant/Reply templates.
- `ARCH-012-MESSAGING-001`, `ARCH-040-BACKGROUND-002`, `ARCH-045-BACKGROUND-005` — previously accepted ingress/conversation/STOP boundaries.

## Enables

None. System tests are terminal; no implementation or publication task may depend on this test.

## Acceptance Criteria

- [ ] Every valid quoted inbound text/audio is assigned to the *exact* original recovery/merchant, with no duplicate conversation/charge or cross-tenant data exposure; wrong/unknown quotes and sender identity fail closed.
- [ ] Shared sender and customer with two+ merchants never resolves ambiguous context-free messages to the newest merchant; guidance asks for Reply to the specific message and supports text/voice, no unnecessary media download.
- [ ] SHOPIFY and WOOCOMMERCE approved templates each display the authenticated merchant identity and 20-locale-safe instruction; unapproved revisions do not send a misleading instruction.
- [ ] STOP merchant-specific quoted and all-merchant standalone suppression, historical recovery handling, voice duration limit, no-contact admission, moderation, credit and conversation invariants hold.
- [ ] Original external failure evidence remains logged with separate bounded internal reason and redaction; no successes are logged for suppressed/failed guidance sends.

## Validation

- [ ] Run system-test runner with disposable PostgreSQL, Redis/BullMQ, Meta emulator and speech/media mocks; record commands and environment/branch/submodule evidence in Completion Report.
- [ ] Execute all 12 routing matrix cases plus approved/unapproved template and injected provider/sensitive-message failures; check no-duplication, credit count and isolation assertions.
- [ ] `git diff --check` and relevant declared system-test lint/build as required by the actual repository scripts. Record any external Meta/locale acceptance checks not executable in the harness as unverified, never as passed.

## Stop Condition

When all required Work Items/Validation and Acceptance Criteria pass, complete the report, mark task `review`, return full reproducible fixture and evidence to `moda_architect`, and STOP. Do not implement source fixes or self-accept.

## Implementation Notes

Build small modular executors/fixtures/assertions/helpers with bounded source files; no 300-line test monolith. Use Shared structured logging and fail-closed real routing, not a second test-only resolver. All tests are black-box against the existing Background ingress. No changes to `_index.md` or accepted source tasks.

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

Test harness can inject provider-confirmed outbound receipts, text, audio and STOP; if external simulator cannot reproduce provider message context, adapt fixture at the documented normalized boundary and record limitation.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any architectural inability to associate a provider-confirmed outbound message with a single tenant conversation must be returned to architect review.

## Architect Review

### Review Status

Pending.

### Review Notes

New terminal cross-merchant certification; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
