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
updated: 2026-10-04
---

# Roll WooCommerce local recovery entitlement periods every 30 days

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

**Superseded before implementation.**

Do not implement an independent local 30-day Woo BillingPeriod scheduler.

Woo v1 now follows verified provider lifecycle:

```text
initial activated -> open first paid period
updated -> same period / same usage
renewed -> next uninterrupted paid period
paused -> FROZEN; no new period
canceled -> FROZEN; preserve current period/usage
replacement activated before periodEnd -> resume same period
replacement activated at/after periodEnd -> new full-allowance period
prepaid_term_ended -> Free only if old canceled contract is still current
```

`ARCH-027-BACKGROUND-002` owns those transitions.

## Context

Woo documents `renewed` as successful recurring renewal and `paused` as failed renewal while retries occur. Provider-owned `next_payment_date` may move during plan switches.

Provider reference verified 4 October 2026:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

The previous local `periodEnd + 30 days` scheduler could grant included credits without a successful provider renewal.

## Scope

This file remains only as a durable supersession record. No implementation is authorised.

## Out of Scope

- Local 30-day Woo rollover.
- Catch-up creation of skipped paid periods.
- Recovery-capacity resume from a local Woo timer.

## Requirements

### R1 — Superseded tasks are not executable

Keep `status=superseded`, `attempt=0`, `executor=null`, `claimed_at=null`.

### R2 — New Woo included periods require verified provider renewal

No Woo paid period may be opened solely because wall clock crossed a prior period end.

### R3 — Downstream chain bypasses this task

BACKGROUND-004 depends directly on BACKGROUND-002.

## Work Items

- [x] Mark superseded.
- [x] Clear dependencies/enables.
- [x] Record provider-renewal replacement.
- [x] Remove from terminal system-test dependencies.

## Interfaces / Contracts

None.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No implementation worktree/branch is created.
- [x] No downstream task depends on this task.
- [x] BACKGROUND-002 owns Woo paid period renewal.

## Validation

The architect reconciliation patch must pass `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, and `git diff --check`.

## Stop Condition

STOP. Do not execute this task.

## Implementation Notes

`EVERY_30_DAYS` remains a catalogue compatibility value, not a local Woo renewal timer.

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

- BACKGROUND-002 is reconciled to provider-driven Woo periods.

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

Superseded by provider-driven period semantics.

### Follow-up

`ARCH-027-BACKGROUND-002`.
