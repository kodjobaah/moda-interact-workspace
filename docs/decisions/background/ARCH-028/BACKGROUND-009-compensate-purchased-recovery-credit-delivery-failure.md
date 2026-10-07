---
id: ARCH-028-BACKGROUND-009
architecture_id: ARCH-028
title: Compensate committed purchased recovery credit after terminal delivery failure
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-008
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-07
---

# Compensate committed purchased recovery credit after terminal delivery failure

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Extend the accepted generic ARCH-028 compensation orchestrator to correct a COMMITTED purchased recovery-credit source using the final authoritative ARCH-027 purchase/refund state, then continue the same suppression/notification pipeline.

## Context

Generic compensation is intentionally not gated by ARCH-027-BACKGROUND-005. Only committed purchased-credit cases need final provider-refund semantics. RESERVED purchased sources were already releasable by BACKGROUND-004.

## Scope

For the exact purchased lot linked by the original reservation:

- if ACTIVE/COMPLETED and not held/refunded, decrement committed and restore exact lot/currentAmount; completed lot may become ACTIVE; disposition `RESTORED_SPENDABLE`;
- if held by one live ARCH-027 refund, correct usage while keeping restored quantity unavailable in the existing refund hold; disposition `HELD_FOR_REFUND`;
- if already provider-refunded/terminal, perform historical aggregate correction only without reopening lot/refund; disposition `HISTORICAL_ONLY`;
- incoherent purchase/refund states fail closed for operator attention;
- never create/reopen a provider monetary refund because delivery failed;
- after successful correction, reuse BACKGROUND-005 reachability and BACKGROUND-008 notification owners.

## Out of Scope

- Generic lifetime-Free/paid/promotional compensation.
- New refund attempt/provider API call.
- New make-good bucket.

## Requirements

- [ ] Consume accepted ARCH-027 purchase/refund state rather than reconstructing old state.
- [ ] One durable compensation correction/disposition per reservation.
- [ ] Live refund hold remains held; provider-refunded source remains closed.
- [ ] No second provider refund attempt is created.
- [ ] Reachability/notification only follow successful correction.

## Work Items

- [ ] Extend compensation orchestrator for committed purchased source.
- [ ] Add active/completed, live-refund, refunded and incoherent-state tests.
- [ ] Reuse suppression/notification pipeline.
- [ ] Add provider-status replay/idempotency tests.

## Interfaces / Contracts

Consumes DATABASE-002 provenance, BACKGROUND-004 orchestrator, BACKGROUND-005/008 post-correction capabilities and final `ARCH-027-BACKGROUND-005` purchase/refund semantics.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-008`
- `ARCH-027-BACKGROUND-005`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Committed purchased terminal delivery failure is corrected exactly once.
- [ ] Existing refund hold/provider-refunded state remains authoritative.
- [ ] No provider monetary refund is created/reopened.
- [ ] Corrected purchased case reaches the same suppression/merchant-notification ordering as generic cases.

## Validation

Focused purchased/refund PostgreSQL integration across all accepted ARCH-027 states, replay tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This task exists solely because its dependency differs from generic compensation. Do not move unrelated generic correction policy here.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
