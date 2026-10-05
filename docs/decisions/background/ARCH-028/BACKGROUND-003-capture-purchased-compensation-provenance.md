---
id: ARCH-028-BACKGROUND-003
architecture_id: ARCH-028
title: Capture purchased recovery compensation provenance at commit
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
created: 2026-10-04
updated: 2026-10-05
---

# Capture purchased recovery compensation provenance at commit

## Objective

**Superseded before implementation.**

The original task captured pre-commit purchase status plus exact refund rows cancelled by a final purchased-credit commit so a later WhatsApp compensation could reconstruct the old refund lifecycle.

That is no longer the ARCH-028 boundary.

ARCH-027 now owns one-attempt purchase refunds and provider monetary outcomes. ARCH-028 compensation uses the current authoritative purchase/refund state and never reopens/reconstructs monetary-refund history.

## Replacement

`ARCH-028-DATABASE-002` now persists only generic compensation lineage/disposition.

`ARCH-028-BACKGROUND-004` performs the actual source-specific compensation using existing reservation source links plus current ARCH-027 purchase/refund state.

## Requirements

- Keep `status=superseded`, no claim/executor/attempt.
- Do not add `purchasedCreditPurchaseStatusAtCommit`.
- Do not add/create `UsageReservationRefundCancellation` rows.
- Do not modify the purchased commit path for ARCH-028 provenance.

## Work Items

- [x] Supersede old purchased/refund provenance capture.
- [x] Remove as compensation dependency.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No implementation worktree is created for this task.
- [x] ARCH-028 compensation does not reconstruct provider monetary-refund history.

## Stop Condition

STOP. Do not execute.

## Architect Review

### Review Status

Superseded
