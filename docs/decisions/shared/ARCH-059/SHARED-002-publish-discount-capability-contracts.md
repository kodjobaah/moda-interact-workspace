---
id: ARCH-059-SHARED-002
architecture_id: ARCH-059
title: Publish discount capability contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-05T17:30:45Z
attempt: 1
depends_on: ["ARCH-059-SHARED-001"]
enables: ["ARCH-059-COMMERCE-001", "ARCH-059-MCP-001", "ARCH-059-BACKGROUND-001", "ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Publish discount capability contracts

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Publish discount capability contracts through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-shared source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Publish only the architect-accepted implementation with the next available approved package version.
- [ ] Record immutable publication receipt, exact version and registry export visibility; no repeat implementation validation.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-001

## Enables
- ARCH-059-COMMERCE-001
- ARCH-059-MCP-001
- ARCH-059-BACKGROUND-001
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Publish only the architect-accepted implementation with the next available approved package version.
- [ ] Record immutable publication receipt, exact version and registry export visibility; no repeat implementation validation.
- [ ] Existing authorization/provider evaluation and unrelated published members remain intact.

## Validation
- [ ] Verify accepted prerequisite and approved version; publication succeeds and exact registry exports exist; no unauthorized source changes. Do not rerun implementation tests, lint, typecheck or build.
- [ ] Reports contain no secrets and demonstrate task scope only.

## Stop Condition
After Work Items, Acceptance Criteria and Validation complete, submit Completion Report for review and STOP. Explicit developer completion via /moda_developer_update is required. Do not start enabled work. System Test is manually invoked after prerequisites complete.


### Verified publication touchpoint
`moda-interact-shared/package.json`: inspect version, exports and declared publication scripts; change release metadata only and use the approved publication command. Registry receipt records exact published version.

### Release acceptance matrix
| Check | Required result |
|---|---|
| Prerequisite review | SHARED-001 Complete/accepted |
| Registry receipt | Exact approved immutable version visible with expected exports |
| Source diff | Release metadata only; no runtime source changes |

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

## Architect Dependency Reconciliation — 5 November 2026

SHARED-001 Attempt 1 is architect-accepted and explicitly developer-completed at implementation `50891ef9062a2da26f2e5fc2cd81eed93ccbdd94`. The sole prerequisite is satisfied. Promoted to Ready, unclaimed, Attempt 0 preserved; execution_mode/completion_mode remain developer. No package publication or automatic execution is authorized by readiness.
