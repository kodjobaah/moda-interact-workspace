---
id: ARCH-059-BACKGROUND-001
architecture_id: ARCH-059
title: Pin outreach published discount tools
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-059-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-059-MCP-001", "ARCH-058-BACKGROUND-001"]
enables: ["ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Pin outreach published discount tools

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Pin outreach published discount tools through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-background source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Consume canonical published MCP identities in outreach and conversation; remove fabricated built-in grant/descriptor registration.
- [ ] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; preserve four-tool outreach allowlist, budgets and deadline.
- [ ] Pin release/capability/revision within attempt; missing/stale/mismatched tools follow existing unavailable/no-verified-offer behavior, never permissive fallback.
- [ ] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [ ] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-059-COMMERCE-001
- ARCH-059-MCP-001
- ARCH-058-BACKGROUND-001

## Enables
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Consume canonical published MCP identities in outreach and conversation; remove fabricated built-in grant/descriptor registration.
- [ ] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; preserve four-tool outreach allowlist, budgets and deadline.
- [ ] Pin release/capability/revision within attempt; missing/stale/mismatched tools follow existing unavailable/no-verified-offer behavior, never permissive fallback.
- [ ] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [ ] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.
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
