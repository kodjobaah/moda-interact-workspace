---
id: ARCH-045-SHARED-003
architecture_id: ARCH-045
title: Publish-ready canonical recipient and Shopify customer identity helpers
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-045-SHARED-002
  - ARCH-045-SYSTEM-TEST-001
created: '2026-10-21'
updated: '2026-10-21'
---
# Publish-ready canonical recipient and Shopify customer identity helpers

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Implement a reusable, runtime-safe cross-service identity codec for exact international WhatsApp recipients and Shopify numeric/GID customer identifiers, with golden fixtures that PHP Woo adapters can independently verify.

## Context

The snapshot trims CustomerPhone phones and separately strips nondigits for WhatsApp; Shopify privacy webhooks provide numeric IDs while Background uses GraphQL GIDs. Two services must not invent conflicting security/identity mappings.

## Scope

- Add a new browser-safe/Node-safe explicit published Shared subpath (or extend the existing approved Shared Shopify/WhatsApp exports) for canonical E.164-equivalent phone identity, requiring an explicit verified country context when input is national-format and rejecting ambiguous/unparseable numbers; do not infer consent.
- Provide canonical validated `gid://shopify/Customer/<numeric>` conversion and equality, rejecting wrong Shopify resource kind, malformed/zero/overflow inputs, arbitrary strings and cross-shop identity (shop scoping stays in services).
- Provide compatibility fixtures for UK national/international variants, country ambiguity, extension characters, changed/reused numbers, numeric webhook and GraphQL GID; PHP implementations must pass the same fixtures rather than attempting to import Node source.
- Keep provider `wa_id`/digits-only destination conversion at the service boundary; do not silently change existing Meta sender semantics outside assigned consumer tasks.

## Out of Scope

- No database migration, Shopify API calls, consent policy, new runtime queue contract, phone-based customer merge or publishing an unaccepted package.

## Requirements

- [ ] One verified canonical phone identity or typed rejection per input, with deterministic, portable fixtures covering national/international equivalence and ambiguity.
- [ ] One Shopify customer ID conversion reused by webhook, Background and privacy handlers; published contract contains no secrets, PII logs or service-specific shop lookups.

## Work Items

- [ ] Add a new browser-safe/Node-safe explicit published Shared subpath (or extend the existing approved Shared Shopify/WhatsApp exports) for canonical E.164-equivalent phone identity, requiring an explicit verified country context when input is national-format and rejecting ambiguous/unparseable numbers; do not infer consent.
- [ ] Provide canonical validated `gid://shopify/Customer/<numeric>` conversion and equality, rejecting wrong Shopify resource kind, malformed/zero/overflow inputs, arbitrary strings and cross-shop identity (shop scoping stays in services).
- [ ] Provide compatibility fixtures for UK national/international variants, country ambiguity, extension characters, changed/reused numbers, numeric webhook and GraphQL GID; PHP implementations must pass the same fixtures rather than attempting to import Node source.
- [ ] Keep provider `wa_id`/digits-only destination conversion at the service boundary; do not silently change existing Meta sender semantics outside assigned consumer tasks.

## Interfaces / Contracts

Owner: `moda-interact-shared` (`moda_shared`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] One verified canonical phone identity or typed rejection per input, with deterministic, portable fixtures covering national/international equivalence and ambiguity.
- [ ] One Shopify customer ID conversion reused by webhook, Background and privacy handlers; published contract contains no secrets, PII logs or service-specific shop lookups.

## Validation

- [ ] Repository-declared focused unit/fixture tests, typecheck/build and `git diff --check`.

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
