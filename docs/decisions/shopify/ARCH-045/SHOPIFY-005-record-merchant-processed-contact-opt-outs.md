---
id: ARCH-045-SHOPIFY-005
architecture_id: ARCH-045
title: Record Shopify merchant-processed off-channel WhatsApp opt-outs
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 33
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: '2026-10-21'
updated: '2026-10-21'
---
# Record Shopify merchant-processed off-channel WhatsApp opt-outs

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Provide the existing Shopify merchant admin with a minimal authenticated way to record a customer no-contact request received outside WhatsApp or checkout.

## Context

A customer can request opt-out by telephone or email. There is no identified merchant recording path and no-contact suppression cannot rely on temporary provider reachability.

## Scope

- Add a bounded Shopify merchant-authenticated action in existing recovery/customer UI to record an explicit off-channel WhatsApp marketing opt-out against an independently verified shop/customer/exact active phone, with shop+principal inferred from trusted session; no new staff roles.
- Use CustomerPhone local no-contact state and monotonic revision, record actor/timestamp and minimal evidence reference without leaking phone in logs, block cross-tenant writes and reject phone-only identity selection.
- Expose clear read-only opt-out state. If customer wants to re-enable messaging, require a subsequent separately verified affirmative permission; merchant cannot grant consent on the customer's behalf.

## Out of Scope

- No outbound WhatsApp opt-in solicitation, new merchant user/assignment system, Shopify tracking-banner changes or direct recovery wakeup.

## Requirements

- [ ] Merchant can securely record an outside-channel STOP and it immediately invalidates all proactive sends for that customer/phone.
- [ ] No merchant action can forge customer grant or bypass local opt-out precedence.

## Work Items

- [ ] Add a bounded Shopify merchant-authenticated action in existing recovery/customer UI to record an explicit off-channel WhatsApp marketing opt-out against an independently verified shop/customer/exact active phone, with shop+principal inferred from trusted session; no new staff roles.
- [ ] Use CustomerPhone local no-contact state and monotonic revision, record actor/timestamp and minimal evidence reference without leaking phone in logs, block cross-tenant writes and reject phone-only identity selection.
- [ ] Expose clear read-only opt-out state. If customer wants to re-enable messaging, require a subsequent separately verified affirmative permission; merchant cannot grant consent on the customer's behalf.

## Interfaces / Contracts

Owner: `moda-interact` (`moda_app`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant can securely record an outside-channel STOP and it immediately invalidates all proactive sends for that customer/phone.
- [ ] No merchant action can forge customer grant or bypass local opt-out precedence.

## Validation

- [ ] Shopify merchant auth/tenant/CSRF tests and Background fence integration evidence, `git diff --check`.

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
