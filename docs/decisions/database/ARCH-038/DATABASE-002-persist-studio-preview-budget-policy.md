---
id: ARCH-038-DATABASE-002
architecture_id: ARCH-038
title: Persist isolated Studio Preview budget policies
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-13
updated: 2026-10-13
superseded_by: ARCH-038-DATABASE-001
---
# Persist isolated Studio Preview budget policies

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_database`
- Repository: `moda-interact-database`

## Objective

Superseded — the separately persisted PREVIEW policy is now part of **ARCH-038-DATABASE-001**, using a single generic `CommerceModelPolicy` table with a mandatory `context=PREVIEW` discriminator and versioned JSONB budget.

## Context

The architect and developer agreed to consolidate LIVE and PREVIEW storage into one table, retaining strict logical isolation by context and scope. The former DATABASE-002 is kept for task-history traceability only; it is not an executable implementation task.

## Scope

None — superseded by `ARCH-038-DATABASE-001`.

## Out of Scope

Do not implement a separate PREVIEW table, migration or partial duplicate of DATABASE-001.

## Requirements

All previously required PREVIEW Platform defaults, Shop overrides, tenant isolation, optimistic concurrency and audit requirements now belong to DATABASE-001 under `context=PREVIEW`.

## Work Items

None — task superseded. No implementation claim should be opened.

## Interfaces / Contracts

See `ARCH-038-DATABASE-001`: `CommerceModelPolicy` with `context=PREVIEW`, `scope=PLATFORM|SHOP`, and versioned sparse JSONB `budget`.

## Dependencies

None — superseded.

## Enables

None — `ARCH-038-COMMERCE-001`, `ARCH-038-COMMERCE-002` and `ARCH-038-SYSTEM-TEST-002` now depend on DATABASE-001.

## Acceptance Criteria

Not applicable — superseded.

## Validation

Not applicable — superseded.

## Stop Condition

No execution. Do not claim, materialise an implementation worktree, migrate or push this superseded task. `ARCH-038-DATABASE-001` owns the complete database implementation.

## Implementation Notes

The architect superseded this portable, not-materialised task before execution. Preserve the record for traceability and do not create a dedicated DATABASE-002 branch/worktree. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Superseded by accepted architecture revision: DATABASE-001 now persists both LIVE and PREVIEW policies in `CommerceModelPolicy`. No code execution or review is required for DATABASE-002.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Superseded — design ownership moved to DATABASE-001.

### Follow-up

None

### Supersession Record

Superseded before execution by the agreed ARCH-038 consolidation: DATABASE-001 persists both LIVE and PREVIEW contexts in one `CommerceModelPolicy` model. Do not claim or execute this historical definition; downstream Preview task dependencies now reference DATABASE-001.
