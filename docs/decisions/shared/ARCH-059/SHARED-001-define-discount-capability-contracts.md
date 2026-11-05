---
id: ARCH-059-SHARED-001
architecture_id: ARCH-059
title: Define discount capability contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-059-SHARED-002"]
created: 2026-11-05
updated: 2026-11-05
---
# Define discount capability contracts

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Define discount capability contracts through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-shared source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Define canonical policy operation descriptors for commerce_get_discount_options and commerce_get_discount_details using existing input/output validators and timestamp syntax.
- [ ] Reuse existing published capability/revision/grant identity and version necessary extensions; preserve exact payload semantics and reject duplicate names.
- [ ] Add compatibility vectors for old/new discount facts, permission boundaries, stale revisions and unsupported grants.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
None

## Enables
- ARCH-059-SHARED-002

## Acceptance Criteria
- [ ] Define canonical policy operation descriptors for commerce_get_discount_options and commerce_get_discount_details using existing input/output validators and timestamp syntax.
- [ ] Reuse existing published capability/revision/grant identity and version necessary extensions; preserve exact payload semantics and reject duplicate names.
- [ ] Add compatibility vectors for old/new discount facts, permission boundaries, stale revisions and unsupported grants.
- [ ] Existing authorization/provider evaluation and unrelated published members remain intact.

## Validation
- [ ] Inspect package.json and run declared focused tests for every Work Item, plus declared typecheck/build when deployable TypeScript changes; record exact commands/results. Do not invent missing scripts.
- [ ] Reports contain no secrets and demonstrate task scope only.

## Stop Condition
After Work Items, Acceptance Criteria and Validation complete, submit Completion Report for review and STOP. Explicit developer completion via /moda_developer_update is required. Do not start enabled work. System Test is manually invoked after prerequisites complete.

## Implementation Notes
Use launcher-resolved isolated matching task worktrees/branches and record synchronization evidence. No execution started by this definition. Reuse existing policy/lifecycle services. Return missing schema/contract capability or permission-parity conflicts to architect.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run; definition only.
### Deviations
None
### Assumptions
Existing lifecycle persistence supports canonical capabilities.
### Unresolved Issues
None identified during definition.
### Architectural Concerns
Return newly discovered cross-service or policy gaps before proceeding.

## Architect Review
### Review Status
Pending
### Review Notes
Definition only.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending implementation.
### Follow-up
None
