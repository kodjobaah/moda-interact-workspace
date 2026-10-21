---
id: ARCH-046-WOOCOMMERCE-006
architecture_id: ARCH-046
title: Connect WordPress personal data export and erase to Moda hosted consent
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
  - ARCH-046-API-004
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: '2026-10-21'
---
# Connect WordPress personal data export and erase to Moda hosted consent

## Architecture

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Use WordPress/WooCommerce customer privacy exporter/eraser extension hooks to honour verified consent data requests stored in Moda API.

## Context

The merchant owns WordPress privacy processing, while customer phone and consent evidence are stored in hosted Moda PostgreSQL. Both Classic and Blocks guests require safe identity resolution.

## Scope

- Register the appropriate WP privacy exporter/eraser callbacks under the installed Moda Woo plugin with administrative nonce/capability context, including bounded cursor/batching and recognisable customer/guest identity proof.
- Call API-004 server-to-server with installation credentials and idempotency; report accurate pending/complete/errors to WordPress, not a fabricated success when hosted API fails.
- Never expose raw installation secrets in browser or logger; address retries, guest identity unavailable, plugin disconnected, multilingual privacy guidance and HPOS compatibility.

## Out of Scope

- No direct Moda DB access, extra consent table, checkout wakeup or new standalone privacy portal.

## Requirements

- [ ] WP privacy export and erase reach hosted CustomerPhone/evidence with verified ownership; partial or unavailable hosted result does not claim success.
- [ ] Erased guest and account data cannot be rebuilt from a delayed Woo event retry.

## Work Items

- [ ] Register the appropriate WP privacy exporter/eraser callbacks under the installed Moda Woo plugin with administrative nonce/capability context, including bounded cursor/batching and recognisable customer/guest identity proof.
- [ ] Call API-004 server-to-server with installation credentials and idempotency; report accurate pending/complete/errors to WordPress, not a fabricated success when hosted API fails.
- [ ] Never expose raw installation secrets in browser or logger; address retries, guest identity unavailable, plugin disconnected, multilingual privacy guidance and HPOS compatibility.

## Interfaces / Contracts

Owner: `moda-interact-woocommerce` (`moda_woocommerce`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-046-API-004`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] WP privacy export and erase reach hosted CustomerPhone/evidence with verified ownership; partial or unavailable hosted result does not claim success.
- [ ] Erased guest and account data cannot be rebuilt from a delayed Woo event retry.

## Validation

- [ ] WP unit/integration privacy exporter/eraser tests on guest and account sessions, hosted API outage/retry and LocalWP evidence.

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
