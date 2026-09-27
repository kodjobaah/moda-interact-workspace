---
id: ARCH-023-SHARED-004
architecture_id: ARCH-023
title: Publish ARCH-023 Shared contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHARED-001
  - ARCH-023-SHARED-002
  - ARCH-023-SHARED-003
enables:
  - ARCH-023-ADMIN-001
  - ARCH-023-ADMIN-002
  - ARCH-023-ADMIN-003
  - ARCH-023-ADMIN-004
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
  - ARCH-023-SHOPIFY-003
  - ARCH-023-BACKGROUND-001
  - ARCH-023-BACKGROUND-002
  - ARCH-023-BACKGROUND-003
  - ARCH-023-COMMERCE-001
  - ARCH-023-COMMERCE-002
created: 2026-09-27
updated: 2026-09-27
---

# Publish ARCH-023 Shared contracts

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Publish one approved `@modainteract/moda-interact-shared` version containing the accepted ARCH-023 configuration, Merchant Knowledge and runner-contract changes.

## Context

Consumer repositories must import the same published contracts rather than copy local schemas/helpers.

## Scope

- Apply the approved package version/release metadata.
- Publish the exact accepted Shared implementation.
- Verify the published version is available from the intended registry/destination.

## Out of Scope

- Implementation changes.
- Consumer dependency updates.
- Rerunning accepted unit/integration/lint/typecheck/build validation.

## Requirements

- All three prerequisite implementation tasks are Complete and architect-accepted before publication.
- Only release-specific metadata may change.
- Published package contains all three accepted ARCH-023 contract surfaces.

## Work Items

- [ ] Verify prerequisite accepted SHAs.
- [ ] Perform approved package publication.
- [ ] Record published version and registry evidence.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared` for all ARCH-023 consumer tasks.

## Dependencies

- ARCH-023-SHARED-001
- ARCH-023-SHARED-002
- ARCH-023-SHARED-003

## Enables

- ARCH-023-ADMIN-001
- ARCH-023-ADMIN-002
- ARCH-023-ADMIN-003
- ARCH-023-ADMIN-004
- ARCH-023-SHOPIFY-001
- ARCH-023-SHOPIFY-002
- ARCH-023-SHOPIFY-003
- ARCH-023-BACKGROUND-001
- ARCH-023-BACKGROUND-002
- ARCH-023-BACKGROUND-003
- ARCH-023-COMMERCE-001
- ARCH-023-COMMERCE-002

## Acceptance Criteria

- [ ] Exact approved version is visible at target destination.
- [ ] No implementation source changed during publication.

## Validation

- [ ] Prerequisite tasks verified Complete/Accepted.
- [ ] Publication command succeeds.
- [ ] Exact version/release visible.
- [ ] No unauthorised implementation-source changes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

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

Pending.

### Follow-up

None
