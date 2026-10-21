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

Translate authenticated WhatsApp recipient opt-outs into a durable exact-customer/recipient no-contact override before conversation routing and proactive admission.

## Context

Existing inbound WhatsApp processing routes or ignores messages before any STOP policy and reachability suppression is temporary, not withdrawal of marketing permission.

## Scope

- Inspect existing Messaging normalized WhatsApp text/provider-status payloads and Background `whatsapp.worker.ts` to classify clear STOP/UNSUBSCRIBE or provider no-contact outcomes **before** an ignored/guidance/recovery conversation route can discard them; require shop/sender identity from authenticated ingress, not phone-only customer merging.
- For a verified shop/customer/active phone, idempotently record the CustomerPhone durable local no-contact revision, opt-out time/source and inbound providerMessageId reference. If matching is ambiguous, refuse to mutate an unrelated CustomerPhone, do not authorise proactive outreach, and record an operational ambiguity for resolution. Do not turn the delivery-focused recipient reachability model into consent state.
- Reuse the same reusable Background policy for first-send, initial retry and follow-up eligibility. Shopify native SUBSCRIBED must not overwrite local STOP. Require a subsequent genuinely verified affirmative choice after opt-out to reinstate permission; non-marketing 24-hour service replies are governed separately.
- Keep handling compatible with ARCH-040 HUMAN/AI handover and moderation, no AI model classification needed for deterministic opt-out keywords.

## Out of Scope

- No new WhatsApp ingress queue, blanket blocking of customer-initiated service replies, consent-triggered recovery creation or merchant-admin UI (Shopify APP/Woo API own those).

## Requirements

- [ ] STOP is captured before routing/AI and records at most one effective opt-out per provider message; proactive sends are denied even if Shopify still reports old SUBSCRIBED.
- [ ] Ambiguous sender cannot revoke another shop/customer but also cannot create an unauthorised proactive send, and regular service-window inbound replies are not silently suppressed.

- For an unmatched or ambiguous sender, do not assume another customer's identity or consent. Record a bounded operational ambiguity and fail closed on consent-sensitive outbound matching. There is **no** new permanent consent field on WhatsAppRecipientReachability in DATABASE-002; its existing temporary delivery suppression is independent.

## Work Items

- [ ] Inspect existing Messaging normalized WhatsApp text/provider-status payloads and Background `whatsapp.worker.ts` to classify clear STOP/UNSUBSCRIBE or provider no-contact outcomes **before** an ignored/guidance/recovery conversation route can discard them; require shop/sender identity from authenticated ingress, not phone-only customer merging.
- [ ] For a verified shop/customer/active phone, idempotently record the CustomerPhone durable local no-contact revision, opt-out time/source and inbound providerMessageId reference. If matching is ambiguous, refuse to mutate an unrelated CustomerPhone, do not authorise proactive outreach, and record an operational ambiguity for resolution. Do not turn the delivery-focused recipient reachability model into consent state.
- [ ] Reuse the same reusable Background policy for first-send, initial retry and follow-up eligibility. Shopify native SUBSCRIBED must not overwrite local STOP. Require a subsequent genuinely verified affirmative choice after opt-out to reinstate permission; non-marketing 24-hour service replies are governed separately.
- [ ] Keep handling compatible with ARCH-040 HUMAN/AI handover and moderation, no AI model classification needed for deterministic opt-out keywords.

- [ ] Verify identifiable CustomerPhone STOP is durable; unmatched/ambiguous STOP never revokes another customer and does not rely on newly added reachability consent columns.

## Interfaces / Contracts

Owner: `moda-interact-background` (`moda_background`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

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

- [ ] STOP is captured before routing/AI and records at most one effective opt-out per provider message; proactive sends are denied even if Shopify still reports old SUBSCRIBED.
- [ ] Ambiguous sender cannot revoke another shop/customer but also cannot create an unauthorised proactive send, and regular service-window inbound replies are not silently suppressed.

- [ ] Identifiable CustomerPhone STOP is persisted; unmatched/ambiguous STOP does not mutate another customer or imply positive consent; no cross-shop opt-out corruption.

## Validation

- [ ] Inbound WhatsApp worker tests: STOP before ignored/guidance, duplicate ID, shared mobile, wrong merchant, moderation, opt-out vs native sync and no-sends/billing.

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
