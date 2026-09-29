---
id: ARCH-021-SHARED-002
architecture_id: ARCH-021
title: Publish simplified Feature capability contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 89
executor: copilot
claimed_at: 2026-09-29T14:01:46Z
attempt: 1
depends_on:
  - ARCH-021-SHARED-001
enables:
  - ARCH-021-COMMERCE-089
  - ARCH-021-BACKGROUND-002
created: 2026-09-29
updated: 2026-09-29
---

# Publish simplified Feature capability contracts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Publish the architect-accepted ARCH-021-SHARED-001 Commerce contract implementation as the next consumable `@modainteract/moda-interact-shared` package version.

## Context

Commerce and Background are pinned to published Shared package versions. Consumer tasks must use one canonical published contract rather than copying the new Feature/Capability/Tool types locally.

This is a release gate only. SHARED-001 already owns implementation validation.

## Scope

- Apply the approved package/release version required by the repository publication process.
- Publish the exact architect-accepted SHARED-001 implementation.
- Verify the expected package version is visible at the intended registry.
- Record the exact published version in the Completion Report.

## Out of Scope

- Source refactoring or contract changes.
- Unit/integration test reruns.
- Typecheck/build reruns solely to revalidate SHARED-001.
- Commerce or Background dependency updates.
- Consumer integration.

## Requirements

### R1 — publish only accepted SHARED-001 source

SHARED-001 must be Complete and architect-accepted before publication begins.

### R2 — no implementation changes

Only release-specific metadata required by the approved publication process may change. If source changes are required, stop and return to `moda_architect`.

### R3 — record exact publication identity

Record the exact package version and registry evidence consumed by later tasks.

## Work Items

- [ ] Verify ARCH-021-SHARED-001 is Complete/Accepted.
- [ ] Apply the approved next package version/release metadata.
- [ ] Run the approved publication command.
- [ ] Verify the exact published package version is available.
- [ ] Record publication evidence and confirm no unauthorised source changes.

## Interfaces / Contracts

Publishes:

`@modainteract/moda-interact-shared`

containing the accepted simplified Feature capability contracts from ARCH-021-SHARED-001.

## Dependencies

- ARCH-021-SHARED-001

## Enables

- ARCH-021-COMMERCE-089
- ARCH-021-BACKGROUND-002

## Acceptance Criteria

- [ ] SHARED-001 was Complete/Accepted before publication.
- [ ] The intended package version was published successfully.
- [ ] The exact version is visible at the target registry.
- [ ] No implementation source changed beyond authorised release metadata.
- [ ] The published version is recorded for consumers.

## Validation

- [ ] prerequisite SHARED-001 acceptance confirmed
- [ ] approved version/release identifier applied
- [ ] publication command succeeded
- [ ] exact expected package version visible at target registry
- [ ] no unauthorised implementation source changes

## Stop Condition

After publication validation is complete, set the task to `review`, complete the Completion Report and STOP. Do not update Commerce or Background.

## Implementation Notes

Do not rerun SHARED-001 implementation validation in this publication task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
