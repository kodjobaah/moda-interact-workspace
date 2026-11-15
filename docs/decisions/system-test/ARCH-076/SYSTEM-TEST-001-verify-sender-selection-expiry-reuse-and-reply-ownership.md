---
id: ARCH-076-SYSTEM-TEST-001
architecture_id: ARCH-076
title: Verify shop sender sharing, basket clarification and immediate reuse
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-076-ADMIN-001, ARCH-076-ADMIN-002, ARCH-076-ADMIN-003, ARCH-076-BACKGROUND-004]
enables: []
created: 2026-11-13
updated: 2026-11-15
---

# Deferred integrated sender routing validation

## Architecture

ARCH-076; parent architecture is authoritative.

## Objective

Validate integrated sender routing only after later explicit developer invocation.

## Context

User deferred this task. Do not implement, claim, execute or complete it now.

## Scope

Five-table sender inventory, assignment and unresolved-question flow with provider fixtures and tenant isolation.

## Out of Scope

Allowance implementation, current execution and production activation.

## Requirements

When later invoked, include all R15 role cases: Friday original plus unique running-shoes selection; independent black-shoes question while original remains pending; verified option plus exact new collection clause; ambiguous bare 2 across prompts; ordinary numeric input. Include persisted decision retry and changed template/config/control/assignment races. This adds deferred scenarios only; do not execute now.

Validate multiple shops/baskets, quoted replies, independent pending originals, expiry/reuse, failed initial delivery, STOP and exhausted allowance without selecting by credit.

## Work Items

- [ ] Wait for prerequisite completion and developer invocation.
- [ ] Validate integrated accepted sender paths.

## Interfaces / Contracts

Final accepted parent architecture and prerequisite implementation reports. Explicit Thread/Route generation scope must remain pinned.

## Dependencies

ARCH-076-ADMIN-001, ARCH-076-ADMIN-002, ARCH-076-ADMIN-003, ARCH-076-BACKGROUND-004.

## Enables

Final architectural review only; no implementation depends on this task.

## Acceptance Criteria

- [ ] Integrated ownership survives concurrent delivery/restart without cross-tenant exposure or original-question reassignment.

## Validation

- [ ] Deferred PostgreSQL/Redis/provider-fixture integrated checks after developer invocation. No execution or pass is claimed.

## Stop Condition

Return evidence for architect review and STOP; no deployment.

## Implementation Notes

Repository task unit/component/disposable PostgreSQL checks remain mandatory independently of this deferred task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not executed.

### Deviations

None

### Assumptions

None

### Unresolved Issues

User-deferred.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Definition only, user-deferred.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not claimed.

### Follow-up

Later developer invocation required.
