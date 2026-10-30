---
id: ARCH-052-SHARED-010
architecture_id: ARCH-052
title: Publish accepted discount discovery contract version
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-10-30T12:46:33Z
attempt: 1
depends_on:
- ARCH-052-SHARED-009
enables:
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-006
- ARCH-052-BACKGROUND-011
created: '2026-10-30'
updated: 2026-10-30
---

# ARCH-052-SHARED-010: Publish the accepted discount-discovery and product identity contract update

## Architecture

ARCH-052: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Publication-only gate; **portable, not materialised**.

## Objective

Publish the architect-accepted SHARED-009 update to the existing `@modainteract/moda-interact-shared/commerce` package entrypoint, then record the exact consumable version. Do not implement or retest the accepted schemas.

## Context

The snapshot's Shared package version is `2.6.0`; SHARED-003 has already published that baseline and remains Complete. SHARED-009 is a coordinated pre-production breaking contract update to discount pagination and nullable product variants. A subsequent version is required before independent MCP, Commerce, Background and Admin tasks consume it.

## Scope

- Use the existing Shared release process to publish **`2.7.0`** if the actual accepted source/release registry baseline remains `2.6.0`. If already published or a different version baseline is encountered, stop for architect reconciliation rather than inventing a version.
- Modify only permitted version/release metadata required by the existing release procedure. Validate that the exact package version and named exports are visible at the intended registry.
- Record source commit, package version, publication output and registry verification in Completion Report. No consumer upgrades in this task.

## Out of Scope

No schema code, tests, lint, build revalidation, MCP/Background consumers, production deployment, Commerce Studio tool publication or historical backfill.

## Requirements

The SHARED-009 task file must have `status:complete` and architect review `Accepted`. Version bump must not silently rewrite the already published 2.6.0 artefact. No secrets in logs.

## Work Items

- [ ] Confirm SHARED-009 is Complete and architect-accepted.
- [ ] Apply the approved 2.7.0 release metadata using repository release tooling.
- [ ] Publish the intended version and inspect registry entry and exported declarations.
- [ ] Record release and worktree evidence; stop.

## Interfaces / Contracts

Published entrypoint: `@modainteract/moda-interact-shared/commerce`. Required new exports: `CommerceDiscountConditionFactsSchema`, `CommerceDiscountConditionFacts`, `CommerceDiscountDetailsSchema`, `CommerceDiscountDetails`, and updated members of `CommerceToolInputs`, `CommerceToolOutputs`, `CommerceProductSchema`. No new subpath or result envelope.

## Dependencies

- ARCH-052-SHARED-009

## Enables

- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-006
- ARCH-052-BACKGROUND-011

## Acceptance Criteria

- [ ] Exact approved version available on registry with expected export declarations.
- [ ] No implementation source or unrelated files changed outside release metadata.
- [ ] Publication receipt and version recorded.

## Validation

- [ ] Verify prerequisite architect acceptance, package version, publication command result and registry availability. Do not rerun implementation tests.

## Stop Condition

Set task to review, provide publication receipt, return to architect and STOP; do not begin consumers.

## Implementation Notes

Use the exact repository release procedure, and preserve the developer's explicit publication authority. The normal publication workflow is independent from Commerce Studio's COMMERCE-007 environment sync.

## Completion Report

### Status

Not Started — portable definition.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Approved baseline package 2.6.0.

### Unresolved Issues

None yet.

### Architectural Concerns

Report unexpected registry/version state to architect before publishing.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending publication review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
