---
id: ARCH-075-SHARED-015
architecture_id: ARCH-075
title: Publish accepted common layout structural reader
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T14:16:56Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-014
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Publish accepted common layout structural reader

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Publish accepted common layout structural reader.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Release-only accepted source as proposed6.0.1; confirm semver before metadata. Produce immutable exact archive and public diff, no implementation changes. Public npm publication requires ROOT relay of explicit user approval for that exact archive; existing6.0.0 approval does not apply. Do not publish before concrete Admin/BG candidate validation. Verify registry downloaded bytes/SRI/latest and report.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Release-only accepted source as proposed6.0.1; confirm semver before metadata. Produce immutable exact archive and public diff, no implementation changes. Public npm publication requires ROOT relay of explicit user approval for that exact archive; existing6.0.0 approval does not apply. Do not publish before concrete Admin/BG candidate validation. Verify registry downloaded bytes/SRI/latest and report.

## Work Items

- [ ] Implement only defined owning capability.
- [ ] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. Publication prerequisite ARCH-075-SHARED-014.

## Dependencies

ARCH-075-SHARED-014

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Publication mechanics only; no repeat tests/lint/build/typecheck. Verify accepted prerequisite, metadata-only diff, exact archive, actual approved publish and registry identity.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Publication authorization gate

Source014 accepted/integrated Sharedmain20aa60f0e9feb4c14ca909b7d7a68771e2b37bcf; parentmain d6d2f0078e05bddad7feb4f37157e6533e532255. Prepare exact6.0.1 metadata/archive from accepted bits without repeating implementation tests/build. Compare nonmetadata archive members against accepted6618d7 candidate. Send archive version/hash/size/SRI and source metadata checkpoint; do NOT publish until root explicitly relays new user approval for that exact archive after concrete consumer tests. Existing6approval is insufficient. Remain In Progress at held release gate.

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
