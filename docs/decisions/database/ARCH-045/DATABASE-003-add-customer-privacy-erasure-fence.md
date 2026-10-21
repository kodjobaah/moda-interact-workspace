---
id: ARCH-045-DATABASE-003
architecture_id: ARCH-045
title: Add durable customer privacy erasure fence and safe phone erasure
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-045-DATABASE-002
enables:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SHOPIFY-003
  - ARCH-045-SHOPIFY-004
  - ARCH-046-DATABASE-001
  - ARCH-046-API-004
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: '2026-10-21'
---
# Add durable customer privacy erasure fence and safe phone erasure

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Define the smallest durable tenant/customer privacy fence that prevents late Shopify or Woo consent activity from rehydrating erased phone/consent data.

## Context

The Shopify redaction handler currently retains historical CustomerPhone.phone values and may fail to find a GID-keyed customer. Consent sync and Woo retries must be unable to recreate erased data.

## Scope

- Add/extend schema necessary to store an effective erasure barrier for shop + verified platform principal, with privacy-minimised lookup identity and monotonic cutoff. Prove that redaction of Customer and every active/historical CustomerPhone row removes phone/contact/consent PII while retaining lawful billing/recovery integrity; do not leave ended rows with raw numbers.
- A privacy-erasure marker must be usable by both Shopify sync and authenticated Woo writes and read under the same SQL transaction; choose reuse of existing schema where valid, adding a minimal tombstone entity only if required for safety. Never persist raw session tokens in the marker.
- Define which Woo immutable evidence fields are retained, deleted or pseudonymised under verified requests and which non-identifying integrity fields may remain, with documented retention/legal-basis decision. Immutable ordinary facts are not an excuse to refuse privacy erasure.
- Cover old/redacted principal retries, race with new projection, deletion followed by new legitimate verified customer lifecycle, shop deletion, cross-tenant isolation, indexes and incremental migration.

## Out of Scope

- No new current-consent table, consent scheduler, remote Shopify provider IO, Woo API route or automatic data export UI.

## Requirements

- [ ] Completed redaction cannot leave active or historical raw CustomerPhone.phone values and delayed sync/retry cannot revive erased principal data.
- [ ] The erasure fence is bounded, indexed, shop/platform scoped and cannot be bypassed by concurrency or an incorrectly converted numeric Shopify webhook ID.
- [ ] Privacy retention policy and migration/rollback impact are documented; no speculative consent expiry or second current-consent table.

## Work Items

- [ ] Add/extend schema necessary to store an effective erasure barrier for shop + verified platform principal, with privacy-minimised lookup identity and monotonic cutoff. Prove that redaction of Customer and every active/historical CustomerPhone row removes phone/contact/consent PII while retaining lawful billing/recovery integrity; do not leave ended rows with raw numbers.
- [ ] A privacy-erasure marker must be usable by both Shopify sync and authenticated Woo writes and read under the same SQL transaction; choose reuse of existing schema where valid, adding a minimal tombstone entity only if required for safety. Never persist raw session tokens in the marker.
- [ ] Define which Woo immutable evidence fields are retained, deleted or pseudonymised under verified requests and which non-identifying integrity fields may remain, with documented retention/legal-basis decision. Immutable ordinary facts are not an excuse to refuse privacy erasure.
- [ ] Cover old/redacted principal retries, race with new projection, deletion followed by new legitimate verified customer lifecycle, shop deletion, cross-tenant isolation, indexes and incremental migration.

## Interfaces / Contracts

Owner: `moda-interact-database` (`moda_database`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SHOPIFY-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-046-DATABASE-001`
- `ARCH-046-API-004`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Completed redaction cannot leave active or historical raw CustomerPhone.phone values and delayed sync/retry cannot revive erased principal data.
- [ ] The erasure fence is bounded, indexed, shop/platform scoped and cannot be bypassed by concurrency or an incorrectly converted numeric Shopify webhook ID.
- [ ] Privacy retention policy and migration/rollback impact are documented; no speculative consent expiry or second current-consent table.

## Validation

- [ ] Prisma validate, PostgreSQL fresh/upgrade redaction/rehydration concurrency tests, evidence anonymisation tests and `git diff --check`.

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
