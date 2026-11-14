---
id: ARCH-075-SHARED-014
architecture_id: ARCH-075
title: Parse common layout structure without application placement policy
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T14:01:20Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Parse common layout structure without application placement policy

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Parse common layout structure without application placement policy.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Keep envelope/prepared/hash verification and exact mechanical single response slot; remove shop.name/site header placement, empty footer, checkout conditional/last-line business checks from readCommonRecoveryLayoutReference. No new website footer placement rule. Preserve exact hash integrity, reject malformed shape/tamper/duplicate response slots, no operational authority. Audit exported callers. Explicit application policy must guard Admin/BG consumer paths before new writes. Add tests for structurally intact alternative section placements accepted and tampered/unsafe frames rejected. No renderer or unrelated contract refactor.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Keep envelope/prepared/hash verification and exact mechanical single response slot; remove shop.name/site header placement, empty footer, checkout conditional/last-line business checks from readCommonRecoveryLayoutReference. No new website footer placement rule. Preserve exact hash integrity, reject malformed shape/tamper/duplicate response slots, no operational authority. Audit exported callers. Explicit application policy must guard Admin/BG consumer paths before new writes. Add tests for structurally intact alternative section placements accepted and tampered/unsafe frames rejected. No renderer or unrelated contract refactor.

## Work Items

- [ ] Implement only defined owning capability.
- [ ] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

None

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Focused common reader/contracts tests, types/build/scopedlint/browser boundary and exact installed pack proof. Produce exact tested provisional pack for consumer validation. No publication in this implementation task.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

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

Pending actual code

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
