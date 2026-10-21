---
id: ARCH-045-BACKGROUND-005
architecture_id: ARCH-045
title: Record inbound WhatsApp opt-outs and enforce no-contact precedence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-004
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
  - ARCH-046-SYSTEM-TEST-001
created: '2026-10-21'
updated: '2026-10-21'
---
# Record inbound WhatsApp opt-outs and enforce no-contact precedence

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Record explicit WhatsApp customer STOP/unsubscribe requests on the correct shop-owned `CustomerPhone`, using existing authenticated inbound correlation **before ordinary routing can ignore the message**; deny subsequent proactive recovery messages without creating a new consent table or modifying delivery reachability.

## Context

`whatsapp.worker.ts` may route/ignore a message before a consent opt-out is interpreted. The normalised inbound message is not guaranteed to carry `shopId`; the same phone can occur at multiple merchants. Current `CustomerPhone` provides durable customer no-contact state, while the existing `WhatsAppRecipientReachability` concerns provider delivery failures, not consent.

## Scope

- Detect deterministic STOP/UNSUBSCRIBE intent using the authenticated inbound message and existing moderation/abuse admission, **before** ignored/guidance/AI/human conversation routing discards the request. Do not substitute LLM classification for explicit commands.
- Resolve shop and customer using trustworthy existing sender/business-number, conversation/recovery and merchant-scoped customer associations. Canonical-phone equality alone is not sufficient to infer a unique shop or select one customer when multiple matches exist.
- Where exactly one active shop-owned CustomerPhone is established, idempotently store customer STOP/no-contact, the receipt's bounded provider-message identity/reference, source/time and monotonic local revision. Later Shopify `SUBSCRIBED` sync and Woo merchant re-enable must not clear a customer STOP; any re-authorisation requires a separate verified customer affirmative decision.
- If the sender/shop cannot be resolved uniquely, do **not** update another CustomerPhone or invent a second recipient-wide consent store. Record a bounded non-PII operational ambiguity for investigation; fail closed for any future candidate for which that ambiguous identity is encountered. **Do not claim guaranteed durable suppression for an unmatched sender without an attributable CustomerPhone.**
- Preserve existing ARCH-040 handover/moderation and normal customer-initiated service-window replies; only business-initiated proactive recovery is blocked by this consent override.

## Out of Scope

- No new customer/session/erasure table, recipient-reachability consent columns, consent-specific queue or global WhatsApp policy rewrite. No merchant opt-out UI/API (separately owned by Shopify app and Woo API/plugin).

## Requirements

- [ ] A resolvable STOP request is processed before any route that would otherwise ignore it, and its customer-phone no-contact revision blocks further proactive sends regardless of older positive consent.
- [ ] Ambiguous shop/customer/phone association never mutates a different merchant's CustomerPhone; unresolved cases are explicitly observable and do not get falsely reported as successfully suppressed.
- [ ] Moderation, human handover and legitimate in-window service replies retain their distinct established rules.

## Work Items

- [ ] Implement a small deterministic opt-out detector at the existing authenticated inbound worker boundary, respecting moderation ordering.
- [ ] Reuse existing shop/conversation routing evidence to resolve an exact active CustomerPhone and idempotently persist STOP before ignored/guidance routing.
- [ ] Add duplicate/wrong-shop/shared-number/ambiguous STOP and provider-status tests; confirm subsequent proactive denial and unchanged service-window behaviour.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone local no-contact fields, existing Meta-normalised inbound provider message/conversation mapping and the reusable consent policy read by ARCH-045-BACKGROUND-001/004 and ARCH-046-BACKGROUND-001/004. No new cross-service event schema or recipient-reachability consent table. Missing reliable shop attribution is an architectural issue to report, not permission to guess identity.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Authenticated identifiable STOP records one effective customer no-contact decision despite duplicate inbound deliveries; no delayed grant, merchant toggle or sender-side retry silently clears it.
- [ ] Unmatched/multi-tenant/multiple-customer STOP creates no unsafe customer mutation or false success; reports a bounded ambiguity while consent-sensitive future matching remains fail-closed.
- [ ] STOP is not lost to ignored/guidance route and does not suppress otherwise legitimate in-window customer-service replies.

## Validation

- [ ] Focused inbound `whatsapp.worker` tests for STOP before ignored/guidance, duplicate provider IDs, multi-merchant same phone, no-shop attribution, local STOP vs Shopify later SUBSCRIBED and merchant re-enable; no PII in logs.
- [ ] ARCH-040 moderation/human-control regression tests, Background send policy denial after STOP and `git diff --check`.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status
Not Started — definition only.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run; no implementation branch.

### Deviations
None.

### Assumptions
Use latest developer implementation branch at claim; supplied snapshot is a reference.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending — no implementation reviewed.

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
None.
