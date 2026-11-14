---
id: ARCH-075-BACKGROUND-015
architecture_id: ARCH-075
title: Bound AI product-list composition to branded caption budget
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Bound AI product-list composition to branded caption budget

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Bound AI product-list composition to branded caption budget.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Investigate then implement deterministic app-owned bounded product selection/composition for long AI lists, preserving exact verified IDs/facts/discount provenance and rendered mandatory STOP/checkout footer. Budget full caption<=1024 after actual canonical footer; no arbitrary model prose truncation, no human text truncation, no automatic invented selection or weakening model/receipt/permit guards. If no evidence-safe compact form fits, retain fullTEXT fallback. Shared6 renderer unchanged; root owns actual model/customer/live operations. Source profile/saved template remains authority. This task becomes Ready only after concrete composition strategy is documented by architect.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Investigate then implement deterministic app-owned bounded product selection/composition for long AI lists, preserving exact verified IDs/facts/discount provenance and rendered mandatory STOP/checkout footer. Budget full caption<=1024 after actual canonical footer; no arbitrary model prose truncation, no human text truncation, no automatic invented selection or weakening model/receipt/permit guards. If no evidence-safe compact form fits, retain fullTEXT fallback. Shared6 renderer unchanged; root owns actual model/customer/live operations. Source profile/saved template remains authority. This task becomes Ready only after concrete composition strategy is documented by architect.

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

Focused exact provenance/selection/budget/Unicode/mandatory footer/discount/no-fit/referral/HUMAN preservation tests, actual one provider send/billing root integration, types/build/scopedlint/exact CI. No unrelated broad repeats.

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
