---
id: ARCH-052-BACKGROUND-001
architecture_id: ARCH-052
title: Freeze effective selected-discount policy at initial attempt creation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-001: Freeze effective selected-discount policy at initial attempt creation

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** Do not freeze merchant discount settings or write an additional offer snapshot at attempt creation. Replacement: BACKGROUND-010 loads current merchant context and MCP-001/002 enforce live shop policy.

## Context

Existing `RecoveryPolicyService.resolve` considers only one fixedShopifyDiscountId and puts provider data into offerSnapshot. Existing `RecoveryOutreachAttempt.offerSnapshot Json?` is already persisted and cloned for follow-ups. No new field or table is needed. The frozen snapshot is read by the outreach-scoped MCP tool adapter; Background does not create a discount candidate evaluator.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

None. This task is withdrawn; no files may be edited under this task.

## Out of Scope

- No separate attempt snapshot field, new Prisma model, data backfill, provider/AI evaluation or meta sends.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

No execution, claim, code changes, package publication or test work. Historical task retained for traceability.

## Work Items

None — superseded.

## Interfaces / Contracts

No new interface. BACKGROUND-010 loads current merchant context and MCP-001/002 enforce live shop policy.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded.

## Validation

None — superseded; do not run task-specific tests.

## Stop Condition

Do not claim or execute this task. The developer must use the active replacement tasks.

## Implementation Notes

Task intentionally withdrawn during ARCH-052 Attempt 6 review. Do not freeze merchant discount settings or write an additional offer snapshot at attempt creation.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
