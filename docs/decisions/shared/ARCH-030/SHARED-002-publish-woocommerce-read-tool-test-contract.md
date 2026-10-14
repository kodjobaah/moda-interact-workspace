---
id: ARCH-030-SHARED-002
architecture_id: ARCH-030
title: Publish accepted WooCommerce read-tool test contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-030-SHARED-001
enables:
  - ARCH-030-API-001
  - ARCH-030-COMMERCE-001
created: 2026-10-14
updated: 2026-10-14
---

# Publish accepted WooCommerce read-tool test contract

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Publish the architect-accepted Shared package version containing the canonical Woo read descriptors and test execution schemas.

## Context

API and Commerce should consume the same released contract; publishing source before acceptance would permit drift.

## Scope

- Confirm SHARED-001 is architect-accepted Complete.
- Version/publish the accepted Shared package and record immutable registry/version evidence.

## Out of Scope

- No runtime edits, refactoring, tests, lint, typecheck or production build reruns; no API/Commerce consumer modifications.

## Requirements

- Publication work changes release metadata only, where required.
- Verify exact intended version exists at the actual package destination.

## Work Items

- [ ] Record release version and registry verification.
- [ ] Confirm no implementation source changes.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared` operation/test contract exports established by SHARED-001.

## Dependencies

- `ARCH-030-SHARED-001`

## Enables

- `ARCH-030-API-001`
- `ARCH-030-COMMERCE-001`

## Acceptance Criteria

- [ ] Accepted SHARED-001 prerequisite recorded.
- [ ] Correct package version is retrievable at intended destination.
- [ ] No unauthorized runtime source edits.

## Validation

- [ ] Run publication command and verify exact published version.
- [ ] Inspect release-only diff and git diff --check.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Do not rerun implementation verification: the publication task is a release gate.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed: portable task definition only.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

Await dependency-gated, launcher-materialised execution and independent review.
