---
id: ARCH-052-API-001
architecture_id: ARCH-052
title: Align existing Woo multi-select API with canonical Shared validator
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-001: Align existing Woo multi-select API with canonical Shared validator

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** WooCommerce already persists up to 50 merchant-selected coupons transactionally using existing isAvailable flags; its only proposed new work was adoption of the now-removed Shared selected-ID validator. Replacement: Keep existing Woo API behaviour unchanged and assert it in SYSTEM-TEST-002.

## Context

Woo `merchant/discount-offers/service.ts` already writes `isAvailable` transactionally, with 50 selected IDs and a deterministic FIXED anchor; there is no reason to move these rows to a join table.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

None. This task is withdrawn; no files may be edited under this task.

## Out of Scope

- No new selection table or data backfill, new endpoint, plugin UI change or Woo native coupon evaluator.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

No execution, claim, code changes, package publication or test work. Historical task retained for traceability.

## Work Items

None — superseded.

## Interfaces / Contracts

No new interface. Keep existing Woo API behaviour unchanged and assert it in SYSTEM-TEST-002.

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

Task intentionally withdrawn during ARCH-052 Attempt 6 review. WooCommerce already persists up to 50 merchant-selected coupons transactionally using existing isAvailable flags; its only proposed new work was adoption of the now-removed Shared selected-ID validator.

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
