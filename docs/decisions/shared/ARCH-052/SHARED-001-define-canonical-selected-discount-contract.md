---
id: ARCH-052-SHARED-001
architecture_id: ARCH-052
title: Freeze discount authorization and delivered promotional offer in existing attempt JSON
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-001: Freeze discount authorization and delivered promotional offer in existing attempt JSON

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** Current merchant settings remain authoritative; no frozen discount-policy copy and no duplicate sent-offer JSON in RecoveryOutreachAttempt. Replacement: Existing Shopify/Woo selected flags, BACKGROUND-010 context, and BACKGROUND-008 persisted outbound template record.

## Context

Both providers store discount rows in shopify.ShopifyDiscount. Woo already writes isAvailable as the merchant checkbox. Shopify writes isAvailable as provider health; ARCH-052-BACKGROUND-009 corrects that. Existing Shared EffectiveRecoveryPolicySchema still requires one fixedShopifyDiscountId when mode=FIXED, so the first sorted selected ID remains a non-authoritative single-ID projection.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

None. This task is withdrawn; no files may be edited under this task.

## Out of Scope

- No new database tables, columns, Prisma migrations, backfill or legacy snapshot parser. No merchant settings, provider API, template or send implementation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

No execution, claim, code changes, package publication or test work. Historical task retained for traceability.

## Work Items

None — superseded.

## Interfaces / Contracts

No new interface. Existing Shopify/Woo selected flags, BACKGROUND-010 context, and BACKGROUND-008 persisted outbound template record.

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

Task intentionally withdrawn during ARCH-052 Attempt 6 review. Current merchant settings remain authoritative; no frozen discount-policy copy and no duplicate sent-offer JSON in RecoveryOutreachAttempt.

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
