---
id: ARCH-046-API-005
architecture_id: ARCH-046
title: Manage merchant recovery suppression for Woo customers
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 33
executor: developer
claimed_at: 2026-10-22T18:08:50Z
attempt: 1
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-046-WOOCOMMERCE-007
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: 2026-10-22
---
# Manage merchant recovery suppression for Woo customers

## Architecture

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-046-API-005`, taking execution and completion authority from the prior agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_api` remains the logical repository owner. The canonical launcher will claim Attempt 1 after this ownership amendment is published.

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Provide an installation-authenticated merchant command to **disable or re-enable recovery for an existing CustomerPhone**, and record a customer-reported off-channel opt-out, without turning merchant selection into WhatsApp consent.

## Context

A merchant may choose not to recover a customer or receive a customer opt-out by phone/email. Both suppress recovery; neither permits the merchant to grant opt-in. Only an existing GRANTED customer preference can be eligible when merchant suppression is cleared.

## Scope

- Accept only authenticated active installation and privileged WP admin-proxied request for the one unambiguous existing Woo Customer/active canonical phone within the authenticated merchant and explicit opt-out evidence reference; shop is always inferred from installation.
- Atomically set/increment the durable CustomerPhone local no-contact override, idempotently handling request replay and installation/phone changes; allow clearing only a merchant-owned recovery suppression after checking current GRANTED consent; never grant consent or clear CUSTOMER_STOP.
- Provide bounded read-only opt-out status to the admin caller with minimal PII. No checkout reconciliation or recovery job on either command.

## Out of Scope

- No new WP user role, generic consent-provider adapter or background recovery search.

## Requirements

- [ ] Merchant suppression/recorded opt-out is immediately authoritative for matching CustomerPhone; re-enabling requires current GRANTED consent, must not clear CUSTOMER_STOP, and cannot be overwritten by stale grant.
- [ ] Another merchant or browser without WP admin authorization cannot forge opt-out or grant.

## Work Items

- [ ] Accept only authenticated active installation and privileged WP admin-proxied request for the one unambiguous existing Woo Customer/active canonical phone within the authenticated merchant and explicit opt-out evidence reference; shop is always inferred from installation.
- [ ] Atomically set/increment the durable CustomerPhone local no-contact override, idempotently handling request replay and installation/phone changes; allow clearing only a merchant-owned recovery suppression after checking current GRANTED consent; never grant consent or clear CUSTOMER_STOP.
- [ ] Provide bounded read-only opt-out status to the admin caller with minimal PII. No checkout reconciliation or recovery job on either command.

## Interfaces / Contracts

Owner: `moda-interact-api` (`moda_api`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-046-WOOCOMMERCE-007`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Merchant suppression/recorded opt-out is immediately authoritative for matching CustomerPhone; re-enabling requires current GRANTED consent, must not clear CUSTOMER_STOP, and cannot be overwritten by stale grant.
- [ ] Another merchant or browser without WP admin authorization cannot forge opt-out or grant.

## Validation

- [ ] Installation auth, shop-scoped canonical-phone lookup, duplicate/ambiguous customers, disable/re-enable, no-consent re-enable, customer STOP precedence, replay and cross-shop tests.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-22T18:08:50Z. Attempt 0 review history is preserved below.

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
