---
id: ARCH-046-WOOCOMMERCE-007
architecture_id: ARCH-046
title: Manage merchant Woo customer recovery selection
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-API-005
  - ARCH-046-WOOCOMMERCE-004
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: '2026-10-21'
---
# Manage merchant Woo customer recovery selection

## Architecture

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Let the existing WooCommerce merchant admin select/deselect which consented customers are eligible for recovery and record off-channel customer STOP, without treating merchant selection as customer consent.

## Context

Merchant-operated Support/Recovery UI exists; a request received outside WhatsApp must be recorded and enforced through hosted CustomerPhone instead of temporary reachability suppression.

## Scope

- Extend existing privileged Woo Support/Recovery surface with enable/disable recovery controls and a customer STOP action on one merchant-scoped unambiguous CustomerPhone; re-use WP capability checks, REST nonce and current installation auth.
- Proxy only to authenticated API-005, with double-click prevention, safe error state and clear result; use canonical phone lookup under the authenticated installation/shop, refuse ambiguous matches and never treat selecting a phone as a grant.
- Make the action available only to authorised Woo merchant administrators; retain existing localisation and no-new-role policy.

## Out of Scope

- No external customer consent grants, new staff assignment model or standalone inbox.

## Requirements

- [ ] Merchant can deselect a customer to suppress recovery, reselect only a currently consented customer to remove the merchant suppression, and record an outside-channel customer STOP, with correct tenant/capability enforcement.
- [ ] Action cannot create or schedule recovery, grant consent, clear customer STOP or modify another tenant.

## Work Items

- [ ] Extend existing privileged Woo Support/Recovery surface with enable/disable recovery controls and a customer STOP action on one merchant-scoped unambiguous CustomerPhone; re-use WP capability checks, REST nonce and current installation auth.
- [ ] Proxy only to authenticated API-005, with double-click prevention, safe error state and clear result; use canonical phone lookup under the authenticated installation/shop, refuse ambiguous matches and never treat selecting a phone as a grant.
- [ ] Make the action available only to authorised Woo merchant administrators; retain existing localisation and no-new-role policy.

## Interfaces / Contracts

Owner: `moda-interact-woocommerce` (`moda_woocommerce`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-046-API-005`
- `ARCH-046-WOOCOMMERCE-004`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Merchant can deselect a customer to suppress recovery, reselect only a currently consented customer to remove the merchant suppression, and record an outside-channel customer STOP, with correct tenant/capability enforcement.
- [ ] Action cannot create or schedule recovery, grant consent, clear customer STOP or modify another tenant.

## Validation

- [ ] WP admin REST nonce/capability, shop-scoped phone lookup, deselect/reselect, disabled selection without GRANTED consent, STOP precedence, duplicate command and hosted API failure tests.

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
