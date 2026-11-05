---
id: ARCH-059-SYSTEM-TEST-001
architecture_id: ARCH-059
title: Verify discount publication lifecycle
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-059-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-059-MCP-001", "ARCH-059-BACKGROUND-001"]
enables: []
created: 2026-11-05
updated: 2026-11-05
---
# Verify discount publication lifecycle

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Verify discount publication lifecycle through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-system-test source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] After optional user manual exercise, run disposable fixtures through setup twice; verify dry-run no writes, stable IDs/release pointers and preserved unrelated members.
- [ ] Trace Feature/capability/revision to immutable release to MCP list/call to outreach, with each tool name once.
- [ ] Verify active Free/paid plan and Shopify/WooCommerce permission parity, checkout_recovery outreach admission, NONE/FIXED/AI_BEST_APPLICABLE and provider facts.
- [ ] Deactivate/unpublish/revoke permission and forge stale/cross-tenant identities; prove fail-closed behavior and no asserted saving from incomplete facts.
- [ ] Exercise in-flight session draining and paired application/release rollback without rewriting historical releases or grants.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-059-COMMERCE-001
- ARCH-059-MCP-001
- ARCH-059-BACKGROUND-001

## Enables
None

## Acceptance Criteria
- [ ] After optional user manual exercise, run disposable fixtures through setup twice; verify dry-run no writes, stable IDs/release pointers and preserved unrelated members.
- [ ] Trace Feature/capability/revision to immutable release to MCP list/call to outreach, with each tool name once.
- [ ] Verify active Free/paid plan and Shopify/WooCommerce permission parity, checkout_recovery outreach admission, NONE/FIXED/AI_BEST_APPLICABLE and provider facts.
- [ ] Deactivate/unpublish/revoke permission and forge stale/cross-tenant identities; prove fail-closed behavior and no asserted saving from incomplete facts.
- [ ] Exercise in-flight session draining and paired application/release rollback without rewriting historical releases or grants.
- [ ] Existing authorization/provider evaluation and unrelated published members remain intact.

## Validation
- [ ] Run the repository declared integrated harness on disposable multi-tenant fixtures for all Work Items; record setup, exact commands, assertions and cleanup.
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
