---
id: ARCH-027-BACKGROUND-003
architecture_id: ARCH-027
title: Roll WooCommerce local recovery entitlement periods every 30 days
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-03
updated: 2026-10-06
---

# Roll WooCommerce local recovery entitlement periods every 30 days

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

**Superseded before implementation.**

This task records a rejected earlier scheduler contract and MUST NOT be reactivated. Its later provider-driven replacement was also superseded by the 6 October ARCH-027 reconciliation.

The active architecture now separates:

```text
BACKGROUND-002
    provider financial/lifecycle/coverage reconciliation

BACKGROUND-006
    exact-30-day Moda entitlement-boundary reconciliation
    gated by verified provider coverage
```

## Context

Earlier ARCH-027 drafts alternated between an unconditional local rollover and a provider-renewal-owned allowance period. Both were rejected.

The accepted design retains exact `EVERY_30_DAYS` Moda allowance windows but prevents the local timer from granting credits without durable verified provider coverage. `renewed` updates financial coverage and does not directly reset allowance.

## Scope

This file remains only as a durable supersession record. No implementation is authorised.

## Out of Scope

- Any executable scheduler implementation.
- Provider-driven `renewed -> allowance reset`.
- Catch-up credit accumulation for uncovered/FROZEN windows.

## Requirements

### R1 — Superseded tasks are not executable

Keep `status=superseded`, `attempt=0`, `executor=null`, `claimed_at=null`.

### R2 — The active replacement is BACKGROUND-006

Do not add dependencies/enables to this task. `ARCH-027-BACKGROUND-006` is a separate new task depending on `ARCH-027-BACKGROUND-002`.

## Work Items

- [x] Keep task superseded.
- [x] Clear dependencies/enables.
- [x] Record the active replacement without reusing this task identity.

## Interfaces / Contracts

None.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No implementation worktree/branch is created for this task.
- [x] No downstream task depends on this task.
- [x] Active cadence work is defined separately as `ARCH-027-BACKGROUND-006`.

## Validation

The architect reconciliation patch must pass `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, and `git diff --check`.

## Stop Condition

STOP. Do not execute this task.

## Implementation Notes

Historical task identity is preserved so the architecture change history remains auditable.

## Completion Report

### Status

Not Started — superseded before execution

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; no implementation exists.

### Deviations

None.

### Assumptions

- BACKGROUND-003 remains historical only; BACKGROUND-006 owns the accepted coverage-gated exact-30-day cadence.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Superseded

### Review Notes

Do not implement.

### Reviewed Files

None.

### Validation Reviewed

Architecture reconciliation only.

### Architecture Conformance

Superseded historical design; active replacement is coverage-gated BACKGROUND-006.

### Follow-up

`ARCH-027-BACKGROUND-006`.
