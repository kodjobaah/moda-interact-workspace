---
id: ARCH-066-SHARED-013
architecture_id: ARCH-066
title: Define public configured sender identity projection
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: blocked
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-066-SHARED-012']
enables: []
created: 2026-11-09
updated: 2026-11-09
---
# Define public configured sender identity projection

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md. Coordinator moda_architect.

## Objective
Define public configured sender identity projection.

## Context
COMMERCE002 initial outreach cannot validate the configured WABA without a public identity projection. Current messaging.sender seals the entire accessToken/phoneNumberId/businessAccountId object. Reading a saved template assignment is not proof of current configured identity.

## Scope
Implement one strict browser-safe published contract at @modainteract/moda-interact-shared/messaging/sender-identity: SenderIdentityProjectionSchema/type and SENDER_IDENTITY_CONFIGURATION_KEY = messaging.senderIdentity. Payload contains only schemaVersion literal1, businessAccountId validated compatibly with the existing messaging.sender businessAccountId contract, sourceKey literal messaging.sender and positive safe-integer sourceVersion. Reject unknown fields and malformed IDs; inspect the existing sender validator before choosing exact bounds. Environment is bound by the PlatformConfiguration row and server-selected environment, never request input. No accessToken, phoneNumberId, ciphertext or credentials. Document read-time requirement: projection sourceVersion equals currently active source metadata version; missing/disabled/mismatched source fails closed. This schema is the canonical cross-service contract, not a local Commerce copy. Preserve the complete accepted5.9.0 composition (source b65e04f7b702e4bae7f9cb354d55a23681b677cc), including prior product-detail and outreach-brand changes; carry exact accepted prerequisites when main lacks them, without unrelated source changes.

## Out of Scope
Commerce or Background implementation, credential grants to Commerce, live providers, deployments/activation, schema changes, main merges, standalone outreach resurrection and follow-on execution. Publication is separate.

## Requirements
Fail closed; preserve tenant/environment authorization and the source-version fence. The public identity must never carry secret material. Existing shopBrand.publicMedia is a separate public policy, not sender identity.

## Work Items
- [ ] Implement the bounded scope above.
- [ ] Record exact artifacts, evidence and limitations.

## Interfaces / Contracts
Shared owns messaging/sender-identity. Admin produces messaging.senderIdentity; Commerce consumes the published schema and read-only row metadata. PlatformConfiguration environment/key uniqueness binds the projection; sourceVersion fences its authority.

## Dependencies
- ARCH-066-SHARED-012

## Enables
- ARCH-066-SHARED-014

## Acceptance Criteria
- [ ] Entire scoped contract is implemented without crossing repository ownership.
- [ ] No token/ciphertext/phone ID exposure or inferred configured WABA.
- [ ] Required focused validation passes with precise evidence.

## Validation
- [ ] Focused schema tests cover valid payload, unknown/secret fields, malformed IDs/version, and browser-safe public export; run repository-declared required typecheck/build for the new contract and record exact distributable provenance for publication.

## Stop Condition
After required scope and validation, set review, return Completion Report and STOP. Do not execute enabled tasks. Developer completion remains explicit after Accepted review.

## Implementation Notes
Defined from actual Commerce task boundary findings on2026-11-09. No infrastructure change/new generic telemetry is required; existing config transport and failure-isolated semantic diagnostics suffice. Missing external capability must be reported, never replaced by insecure defaults.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review
### Review Status
Pending
### Review Notes
Definition only; implementation not started.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None

## User-directed withdrawal — 2026-11-09

WITHDRAWN. The user explicitly removed template/WABA validation from Studio initial-outreach preview. A configured-sender identity projection is therefore outside the requested scope. Do not claim, implement, publish a package, or execute follow-on work under this task. Historical definition/publication evidence above is retained, not accepted or completed. Lifecycle status is blocked to prevent launcher execution using existing supported statuses; this is a scope withdrawal, not a technical blocker awaiting repair. Attempt0 and null claim remain unchanged. Reopening requires explicit user instruction and a new architectural disposition.

SHARED-013, SHARED-014 and ADMIN-001 are removed from the Studio dependency path. Replacement preview-only renderer/adoption definitions are SHARED-015 → SHARED-016 → COMMERCE-003. Existing Background production send checks remain unchanged. No source changes, release, deployment or live configuration mutation follows from this withdrawal.
