---
id: ARCH-045-SHOPIFY-003
architecture_id: ARCH-045
title: Complete Shopify customer redaction and stale-event protection
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-045-DATABASE-003
- ARCH-045-SHARED-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: '2026-10-21'
updated: '2026-10-21'
---
# Complete Shopify customer redaction and stale-event protection

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Make authenticated Shopify customer redaction reliably locate the canonical customer, erase all retained contact/consent PII and establish a race-safe no-rehydration guard.

## Context

Existing customers/redact route stringifies numeric webhook IDs but Background persists Shopify GIDs; only active phone intervals are closed, while historical phone strings remain.

## Scope

- Use the published Shared numeric-ID/GID helper after verified webhook authentication, tenant resolution and HMAC; resolve only the specific Shopify Customer in that shop.
- Transactionally establish DATABASE-003 erasure fence, anonymise Customer fields, erase historical and active CustomerPhone raw number/current consent, and reconcile linked retained recovery/usage data under approved privacy and financial retention policy. Do not cascade-delete unrelated merchants or historical financial obligations.
- Make duplicate/redelivered redact idempotent; ensure Background consent sync cannot rehydrate after deletion, even when old webhook is processed after redact or provider still returns subscribed.
- Emit bounded PII-free operation outcomes, and preserve authenticated ingress ACK semantics without pretending unknown customer is a processed erasure.

- If a valid redaction webhook arrives before a matching Customer row exists, still establish the shop+provider-principal erasure fence and record `fenced_no_current_customer` or equivalent truthful outcome. Later event ingestion cannot populate customer/contact PII solely because a row did not exist when redact arrived.

## Out of Scope

- No consent-triggered checkout work, no Woo erasure endpoint, no full generic DSGP tool, no unauthorised new Shopify scopes.

## Requirements

- [ ] Numeric webhook customer ID resolves the same identity as GraphQL GID; all historical phone PII is erased and replayed old sync cannot restore it.
- [ ] Idempotent cross-tenant-safe redact and correct privacy/legal retention outcome are verified.

## Work Items

- [ ] Use the published Shared numeric-ID/GID helper after verified webhook authentication, tenant resolution and HMAC; resolve only the specific Shopify Customer in that shop.
- [ ] Transactionally establish DATABASE-003 erasure fence, anonymise Customer fields, erase historical and active CustomerPhone raw number/current consent, and reconcile linked retained recovery/usage data under approved privacy and financial retention policy. Do not cascade-delete unrelated merchants or historical financial obligations.
- [ ] Make duplicate/redelivered redact idempotent; ensure Background consent sync cannot rehydrate after deletion, even when old webhook is processed after redact or provider still returns subscribed.
- [ ] Emit bounded PII-free operation outcomes, and preserve authenticated ingress ACK semantics without pretending unknown customer is a processed erasure.

## Interfaces / Contracts

Owner: `moda-interact` (`moda_app`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-003`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Numeric webhook customer ID resolves the same identity as GraphQL GID; all historical phone PII is erased and replayed old sync cannot restore it.
- [ ] Idempotent cross-tenant-safe redact and correct privacy/legal retention outcome are verified.

## Validation

- [ ] Authenticated Shopify webhook route tests with disposable PostgreSQL, old GID/numeric fixtures, grant-vs-redact races, tenant protection and `git diff --check`.

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
