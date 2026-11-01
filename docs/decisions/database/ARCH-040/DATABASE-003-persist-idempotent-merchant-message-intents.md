---
id: ARCH-040-DATABASE-003
architecture_id: ARCH-040
title: Persist idempotent merchant message intents
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-14
updated: '2026-10-17'
---

# ARCH-040-DATABASE-003 — Superseded by ARCH-040-DATABASE-001

## Architecture

`ARCH-040` — `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.

## Objective

**Superseded — do not implement.** Its original outcome (recovery-only durable human message command, payload integrity and worker leases) is fully incorporated in `ARCH-040-DATABASE-001`.

## Context

The user opted for one consolidated database implementation task and one fresh-development database migration. Keeping this file records the previous task ID without creating an executable dependency.

## Scope

None. Implementation is owned entirely by `ARCH-040-DATABASE-001`.

## Out of Scope

All repository changes under this historical task ID.

## Requirements

Refer to the corresponding work package in `ARCH-040-DATABASE-001`. No independent schema, SQL migration, tests or review required.

## Work Items

None — superseded.

## Interfaces / Contracts

`ARCH-040-DATABASE-001` is the canonical persistence contract.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

Not applicable — superseded.

## Validation

Not applicable — superseded.

## Stop Condition

Do not claim or execute this historical task.

## Implementation Notes

The original detailed persistence requirements are consolidated verbatim in substance into `ARCH-040-DATABASE-001` including enums/models, constraints, concurrency rules and tests. Consult the authoritative combined task rather than this historical record.

## Completion Report

### Status
Not Started — superseded.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run — superseded.

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
Superseded by architectural decision, no acceptance of implementation claimed.

### Review Notes
Requirements transferred to ARCH-040-DATABASE-001; this task must never become Ready.

### Reviewed Files
Task definition only.

### Validation Reviewed
None.

### Architecture Conformance
Superseded.

### Follow-up
ARCH-040-DATABASE-001.
