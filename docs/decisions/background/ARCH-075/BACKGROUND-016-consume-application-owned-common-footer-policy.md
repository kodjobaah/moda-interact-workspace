---
id: ARCH-075-BACKGROUND-016
architecture_id: ARCH-075
title: Consume application-owned common footer policy
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
depends_on:
  - ARCH-075-SHARED-015
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Consume application-owned common footer policy

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Consume application-owned common footer policy.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Adopt exact published reader and implement Background application policy at every common reference selection/read/frozen/finalpermit/native preparation path. Allow saved website in checkout.available conditional before trusted checkout URL final line, unique trusted name/site/checkout bindings, allowed-variable authority. Remove website-in-header assumptions without dropping rendered boundary/hash/receipt proof. No URL counting/strip heuristics over authored answer; no invented URLs. Existing immutable common refs remain frozen and current-source locks authoritative. Final checkout and STOP/body preservation remain app-owned. No Shared business rules/release or live writes.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Adopt exact published reader and implement Background application policy at every common reference selection/read/frozen/finalpermit/native preparation path. Allow saved website in checkout.available conditional before trusted checkout URL final line, unique trusted name/site/checkout bindings, allowed-variable authority. Remove website-in-header assumptions without dropping rendered boundary/hash/receipt proof. No URL counting/strip heuristics over authored answer; no invented URLs. Existing immutable common refs remain frozen and current-source locks authoritative. Final checkout and STOP/body preservation remain app-owned. No Shared business rules/release or live writes.

## Work Items

- [ ] Implement only defined owning capability.
- [ ] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

ARCH-075-SHARED-015

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Exact reader/app rejection tests including Shared technically accepts alternate frames while host rejects noncanonical application source; website absent from bitmap and once clickable caption, checkout last; tamper/stale/current-source/finalpermit/AI/HUMAN/native checks, types/build/scopedlint/exact CI. Local exact accepted pack tests may precede release; final registry lock/npmci required after actual approved publication.

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
