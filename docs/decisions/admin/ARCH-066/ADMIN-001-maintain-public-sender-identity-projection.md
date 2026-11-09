---
id: ARCH-066-ADMIN-001
architecture_id: ARCH-066
title: Atomically maintain public configured sender identity projection
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ['ARCH-066-SHARED-014']
enables: ['ARCH-066-COMMERCE-002']
created: 2026-11-09
updated: 2026-11-09
---
# Atomically maintain public configured sender identity projection

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md. Coordinator moda_architect.

## Objective
Atomically maintain public configured sender identity projection.

## Context
COMMERCE002 initial outreach cannot validate the configured WABA without a public identity projection. Current messaging.sender seals the entire accessToken/phoneNumberId/businessAccountId object. Reading a saved template assignment is not proof of current configured identity.

## Scope
Consume the exact published Shared sender identity schema/key. In src/lib/admin/platform-configuration/secret-service.ts mutateSecretWithDependencies, derive public.PlatformConfiguration messaging.senderIdentity from the validated messaging.sender payload inside the same serializable transaction and version/CAS boundary as the secret mutation. Persist only businessAccountId/schemaVersion/sourceKey/sourceVersion, same environment. No schema migration is needed: use existing environment/key/value/version rows. Revoke/delete/disable must atomically remove or disable the projection so consumers fail closed. Preserve ciphertext/AAD/keyrotation, auditing, authorization and rollback semantics. Derived namespace is reserved, not freely editable through generic public-policy mutation. Provide a bounded SUPER_ADMIN-authorized explicit rebuild path for preexisting sender configuration using the Admin-owned secret reader if needed; no automatic hosted backfill during execution. Define/document a read-only source metadata predicate allowing Commerce to compare current active source version without selecting/decrypting secret value; use Prisma/JSON predicates plus version-only select. Never grant Commerce secret decryption. Missing projection, disabled source or stale version is unavailable, never inferred from approved template assignment.

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
- ARCH-066-SHARED-014

## Enables
- ARCH-066-COMMERCE-002

## Acceptance Criteria
- [ ] Entire scoped contract is implemented without crossing repository ownership.
- [ ] No token/ciphertext/phone ID exposure or inferred configured WABA.
- [ ] Required focused validation passes with precise evidence.

## Validation
- [ ] Focused existing writer integration tests cover atomic success and rollback, source/projection version equality, CAS/concurrent updates, revoke/disable, reserved namespace rejection, authorized rebuild, absent/stale metadata behavior and no secret fields in projection/logs. Run repository-declared compiler/lint checks appropriate to changed code; use isolated test database, no live Meta or hosted mutation.

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
