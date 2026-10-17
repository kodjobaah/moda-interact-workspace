---
id: ARCH-040-BACKGROUND-005
architecture_id: ARCH-040
title: Screen human outbound messages and detect merchant abuse
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-BACKGROUND-004
  - ARCH-040-BACKGROUND-003
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
  - ARCH-040-SHOPIFY-003
  - ARCH-040-WOOCOMMERCE-003
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-005 — Screen human outbound messages and detect merchant abuse

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Portable task definition; no branch, worktree, commit, push or implementation is claimed.

## Objective

Screen merchant-originated WhatsApp messages for deterministic spam/rate abuse, persist decision outcomes, and surface repeat abuse for platform-admin review without silently suspending stores.

## Context

Existing `inbound-whatsapp-abuse-admission.service.ts` limits incoming customer traffic. It is not an outbound human-message moderation service. Reuse its patterns where applicable but keep separate policy, identities and failure semantics.

## Scope

- Add a HUMAN-only outbound screening stage to the command dispatcher before provider admission; use shop, recipient and stable command identity as moderation keys.
- Implement deterministic bounded guards for malformed/oversized payloads, excessive send rate and repeated equivalent unsolicited messages; choose documented, configurable thresholds supported by measured tests rather than arbitrary hardcoded bans.
- Persist or produce durable per-command outcomes and bounded abuse signals visible to Admin; do not auto-suspend on a single uncertain heuristic.

## Out of Scope

- No semantic harassment classifier, LLM moderation request, new external content-moderation service, arbitrary keyword blocklist or merchant automatic suspension in v1. Platform Admin restriction and transparent deterministic rate/repeat screening are sufficient for this bounded feature.

- Do not change existing AI/automation entitlement or full-shop `Shop.status` rules; this is a platform-controlled HUMAN-only restriction.
- No merchant-facing toggle to restore a suspension, no per-employee permission system, no new Conversation or duplicated follow-up credit.
- Do not add new ARCH-040 Shared package publication, Shopify-to-Woo/API dependencies or `docs/decisions/**/_index.md` files.
- No speculative new service, queue platform or third-party AI moderation provider.

## Requirements

### Deterministic screening policy

- Apply only to `HUMAN_TEXT` and merchant-originated permitted templates. Preserve legitimate single-recovery follow-up rules and CommerceAgent outbound behaviour.
- Validate length/control characters, normalized repetitive bodies to the same recipient, and excessive shop-wide/recipient-directed send attempts across a rolling interval. Identify commands by `(shopId, commandId)` so queue retries or identical idempotent replays are not counted as new abusive attempts.
- Prefer Redis atomic rolling counters/expirations where already supported, with measured resource bounds; retained durable `MerchantConversationSendCommand` and provider receipts remain source of truth for send outcomes. If screening infrastructure is unavailable, adopt a documented conservative fail-closed HUMAN-send decision with explicit temporary failure and bounded retry; never silently bypass restrictions or charge without send.
- Avoid unreviewed keyword blocklists or blanket bans on normal shopping text/URLs. Threats/harassment semantic moderation may require a separate approved provider/policy; do not invent an external moderation API or claim full content detection in this task. Provide a hook for later policy review if needed.
- Machine outcomes: `human_rate_limited`, `human_repeated_spam`, `human_content_invalid`, `human_screening_unavailable`. Define terminal versus retryable behaviours; no provider call or consumed recovery credit for definitively rejected commands, and explain provider-uncertain outcomes accurately.
- Emit bounded structured violation events/counters, with shopId, commandId, category, threshold/rule version and timestamp, **not raw body/customer data**. Repeated violations are escalated to operator review; only ADMIN-001 changes shop-wide SUSPENDED state.
- Revalidate both the platform restriction and the shared recovery follow-up/window policy at final send admission; screening is additive, never a bypass for B004 or B003.

## Work Items

- [ ] Add a modular, testable HUMAN-only abuse screening policy with repeat/rate limits, request guards and explicit outcomes.
- [ ] Wire screening into Background command dispatch without introducing an AI or WooCommerce-only path.
- [ ] Make retries/idempotency non-amplifying; emit operator-reviewable bounded signals without message payload leakage.
- [ ] Test legitimate rapid responses, repeated spam, tenant separation, Redis failure, and concurrent sends across workers.

## Interfaces / Contracts

Consumes existing durable merchant commands, restriction outcome from B004 and the same provider dispatch from BACKGROUND-002. No Shared model, new browser content moderation library, independent credits, or new Meta endpoint. Any Admin incident presentation beyond existing logging/tenant detail is a follow-on decision unless required to make the review signal accessible.

## Dependencies

- ARCH-040-BACKGROUND-004
- ARCH-040-BACKGROUND-003

## Enables

- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SYSTEM-TEST-002
- ARCH-040-SYSTEM-TEST-003
- ARCH-040-SHOPIFY-003
- ARCH-040-WOOCOMMERCE-003

## Acceptance Criteria

- [ ] Repeated/rapid abusive HUMAN sends are blocked while legitimate responses remain possible under declared thresholds.
- [ ] Duplicate command retries are counted once; no extra provider requests or billing.
- [ ] Screening failures and rate limits are explicit, bounded and auditable; uncertain heuristics do not automatically suspend the merchant.
- [ ] AI/automated conversation messages are unaffected, and shop restrictions remain enforced.

## Validation

- [ ] Focused unit tests for normalized-body/rate/size policy
- [ ] Disposable Redis concurrency/TTL/failure tests
- [ ] Provider mock, idempotency and recovery-credit tests
- [ ] git diff --check and worktree evidence

## Stop Condition

After defined work, acceptance criteria and required validation are complete, record Completion Report, set task to review, return control to moda_architect and STOP. Do not begin another task.

## Implementation Notes

Do not add heavy synchronous LLM classification to the hot send path. Prefer verified bounded protections now and return broader content-moderation policy decisions to moda_architect. Use the canonical task preparation/worktree protocol. Check actual repository scripts before running tests; use the published shared logger for structured telemetry without message contents or credentials. No `_index.md` updates until the user explicitly confirms architectural-session completion.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The initiative is proposed; work has not begun.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
