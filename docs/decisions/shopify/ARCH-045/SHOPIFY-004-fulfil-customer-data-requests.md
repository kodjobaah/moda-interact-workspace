---
id: ARCH-045-SHOPIFY-004
architecture_id: ARCH-045
title: Fulfil Shopify customer data requests for consent records
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-045-DATABASE-002
- ARCH-045-DATABASE-003
- ARCH-045-SHARED-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: '2026-10-21'
updated: '2026-10-21'
---
# Fulfil Shopify customer data requests for consent records

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Replace the acknowledgement-only Shopify customer data-request path with a verifiable, tenant-scoped privacy export process covering current phone consent and retained relevant customer records.

## Context

Current customers/data_request route authenticates and records success without producing an export. New CustomerPhone consent fields must be covered by verified data-access requests.

## Scope

- Validate Shopify privacy webhook shop/customer identity using the canonical published helper and current Shopify request contract; do not treat an authenticated ACK as completion.
- Collect only the requested customer's authorised customer/phone consent, recovery and applicable retained history in bounded pages using existing privacy-safe storage/delivery workflow, or define a bounded auditable manual fulfilment path if fully automatic transmission is not yet supported.
- Record actual request lifecycle and customer/shop isolation, retry/duplicate status and evidence of fulfilment without exposing protected records in request logs or unprotected browser URLs.
- Explicitly document any unresolved compliance operations/retention dependencies to architect rather than claim implementation based solely on HTTP 200.

## Out of Scope

- No Woo WordPress privacy export, tracking-cookie UI, new merchant analytics or recovery scheduling.

## Requirements

- [ ] A verified request has a traceable actual fulfilment or explicit actionable failure; customer data is not leaked across shops or into logs.
- [ ] Current and historical customer-phone consent and erasure markers are handled according to approved privacy-retention scope.

## Work Items

- [ ] Validate Shopify privacy webhook shop/customer identity using the canonical published helper and current Shopify request contract; do not treat an authenticated ACK as completion.
- [ ] Collect only the requested customer's authorised customer/phone consent, recovery and applicable retained history in bounded pages using existing privacy-safe storage/delivery workflow, or define a bounded auditable manual fulfilment path if fully automatic transmission is not yet supported.
- [ ] Record actual request lifecycle and customer/shop isolation, retry/duplicate status and evidence of fulfilment without exposing protected records in request logs or unprotected browser URLs.
- [ ] Explicitly document any unresolved compliance operations/retention dependencies to architect rather than claim implementation based solely on HTTP 200.

## Interfaces / Contracts

Owner: `moda-interact` (`moda_app`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-DATABASE-003`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] A verified request has a traceable actual fulfilment or explicit actionable failure; customer data is not leaked across shops or into logs.
- [ ] Current and historical customer-phone consent and erasure markers are handled according to approved privacy-retention scope.

## Validation

- [ ] Data-request webhook replay/tenant/auth tests, export/operational fulfilment evidence and `git diff --check`.

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
