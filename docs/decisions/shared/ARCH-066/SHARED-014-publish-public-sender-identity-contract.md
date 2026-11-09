---
id: ARCH-066-SHARED-014
architecture_id: ARCH-066
title: Publish public configured sender identity contract
task_kind: publication
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
depends_on: ['ARCH-066-SHARED-012', 'ARCH-066-SHARED-013']
enables: []
created: 2026-11-09
updated: 2026-11-09
---
# Publish public configured sender identity contract

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md. Coordinator moda_architect.

## Objective
Publish public configured sender identity contract.

## Context
COMMERCE002 initial outreach cannot validate the configured WABA without a public identity projection. Current messaging.sender seals the entire accessToken/phoneNumberId/businessAccountId object. Reading a saved template assignment is not proof of current configured identity.

## Scope
Release only the exact accepted complete composition containing SHARED013 plus the accepted5.9.0 capabilities. Select the first unused higher5.x minor patch0, record before publication, never overwrite an immutable version. Reuse prerequisite validated build artifact; required packaging lifecycle is allowed only when provenance proves no runtime changes. If a distributable cannot be produced without new code or repeat validation, return to architect. Use approved npm publication mechanism; verify exact downloadable archive integrity and public schema export. Do not implement consumers.

## Out of Scope
Commerce or Background implementation, credential grants to Commerce, live providers, deployments/activation, schema changes, main merges, standalone outreach resurrection and follow-on execution. Implementation changes and repeated code validation.

## Requirements
Fail closed; preserve tenant/environment authorization and the source-version fence. The public identity must never carry secret material. Existing shopBrand.publicMedia is a separate public policy, not sender identity.

## Work Items
- [ ] Implement the bounded scope above.
- [ ] Record exact artifacts, evidence and limitations.

## Interfaces / Contracts
Shared owns messaging/sender-identity. Admin produces messaging.senderIdentity; Commerce consumes the published schema and read-only row metadata. PlatformConfiguration environment/key uniqueness binds the projection; sourceVersion fences its authority.

## Dependencies
- ARCH-066-SHARED-012
- ARCH-066-SHARED-013

## Enables
- ARCH-066-ADMIN-001

## Acceptance Criteria
- [ ] Entire scoped contract is implemented without crossing repository ownership.
- [ ] No token/ciphertext/phone ID exposure or inferred configured WABA.
- [ ] Required focused validation passes with precise evidence.

## Validation
- [ ] Verify Complete/Accepted prerequisites, version/archive provenance, successful approved publication, exact registry downloadable integrity/public-export smoke, and no unauthorized runtime changes. Do not rerun unit/integration tests, lint, typecheck or production builds for revalidation.

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
