---
id: ARCH-059-COMMERCE-001
architecture_id: ARCH-059
title: Publish canonical discount capabilities
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-059-SHARED-002", "ARCH-058-COMMERCE-001"]
enables: ["ARCH-059-MCP-001", "ARCH-059-BACKGROUND-001", "ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Publish canonical discount capabilities

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Publish canonical discount capabilities through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-commerce source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [ ] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [ ] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and activate with optimistic concurrency.
- [ ] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [ ] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-058-COMMERCE-001

## Enables
- ARCH-059-MCP-001
- ARCH-059-BACKGROUND-001
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [ ] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [ ] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and activate with optimistic concurrency.
- [ ] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [ ] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.
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
