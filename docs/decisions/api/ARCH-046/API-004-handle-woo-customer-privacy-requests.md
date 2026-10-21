---
id: ARCH-046-API-004
architecture_id: ARCH-046
title: Handle authenticated WooCommerce consent privacy export and erasure
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-046-WOOCOMMERCE-006
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: '2026-10-21'
---
# Handle authenticated WooCommerce consent privacy export and erasure

## Architecture

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Provide a hosted installation-authenticated privacy export/erase operation for verified Woo account or guest identity, with safe audit-evidence retention and no late consent resurrection.

## Context

Woo consent evidence lives in Moda PostgreSQL, not the merchant's WordPress database. WordPress privacy requests therefore need an authorised hosted API boundary.

## Scope

- Accept tightly bounded signed/server-authenticated Woo privacy request carrying verified installation/shop/customer or guest checkout identity, request kind and idempotency key; reject client-supplied shopId and phone-only guest requests.
- For export, return a protected bounded customer data result for the authenticated requester without exposing other tenants. For erasure, transactionally apply DATABASE-002 privacy-erasure fence and anonymise/delete CustomerPhone, Woo evidence and identity-link personal fields according to approved lawful retention.
- Prevent delayed pre-submit consent and Action Scheduler retries from recreating privacy-erased state or treating stale evidence as granted; return explicit actual success/failure outcome rather than acknowledgement-only.

## Out of Scope

- No WordPress user-facing erasure UI or Shopify webhook route, no generic new privacy microservice, no automatic recovery job.

## Requirements

- [ ] Verified Woo privacy request handles current consent and evidence safely, without phone-only identity binding, cross-tenant leakage or rehydration.
- [ ] Erasure/redaction exceptions to immutable ordinary audit facts are explicitly documented and provably applied.

## Work Items

- [ ] Accept tightly bounded signed/server-authenticated Woo privacy request carrying verified installation/shop/customer or guest checkout identity, request kind and idempotency key; reject client-supplied shopId and phone-only guest requests.
- [ ] For export, return a protected bounded customer data result for the authenticated requester without exposing other tenants. For erasure, transactionally apply DATABASE-002 privacy-erasure fence and anonymise/delete CustomerPhone, Woo evidence and identity-link personal fields according to approved lawful retention.
- [ ] Prevent delayed pre-submit consent and Action Scheduler retries from recreating privacy-erased state or treating stale evidence as granted; return explicit actual success/failure outcome rather than acknowledgement-only.

## Interfaces / Contracts

Owner: `moda-interact-api` (`moda_api`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-046-WOOCOMMERCE-006`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Verified Woo privacy request handles current consent and evidence safely, without phone-only identity binding, cross-tenant leakage or rehydration.
- [ ] Erasure/redaction exceptions to immutable ordinary audit facts are explicitly documented and provably applied.

## Validation

- [ ] API auth/tenant/guest, export and erase with disposable PostgreSQL, late retry race, i18n-safe messages and `git diff --check`.

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
