---
id: ARCH-040-SHARED-001
architecture_id: ARCH-040
title: Define merchant conversation and handover contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
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
updated: 2026-10-14
---

# ARCH-040-SHARED-001 — Define merchant conversation and handover contracts

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. **Superseded task definition only; do not materialise or execute.**

## Objective

Superseded — no implementation is authorised by this task.

## Context

The persisted conversation and send-command model is already defined by the Prisma database schema. HTTP request/response validation belongs to moda_api, and Background consumes the canonical database records. No duplicate Shared conversation package is warranted.

## Scope

None. This record documents an abandoned ARCH-040 implementation proposal.

## Out of Scope

- Do not publish or implement new ARCH-040 conversation schemas in `moda-interact-shared`.
- Do not change existing published Shared logging or unrelated contracts.
- Do not introduce an implementation or publication gate for the active ARCH-040 tasks.

## Requirements

None — task superseded by the 2026-10-14 architecture decision.

## Work Items

None.

## Interfaces / Contracts

`moda-interact-database` owns the canonical persistent Prisma models; `moda-interact-api` owns validated HTTP payloads and authentication assertions; `moda-interact-background` consumes durable commands. See active task definitions. No new ARCH-040 Shared package exports are required.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

None — do not execute.

## Validation

None — do not execute.

## Stop Condition

This task is superseded. No task worktree, implementation, publication or review is to be launched.

## Implementation Notes

Retain this file for historical coordination only. Existing Shared logging remains independently available.

## Completion Report

### Status
Not Started — superseded.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
No active dependency must reference this superseded task.

## Architect Review

### Review Status
Pending — superseded without implementation.

### Review Notes
Superseded by approved ARCH-040 contract-ownership simplification (2026-10-14). No acceptance of implementation is implied.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Inactive task; does not gate ARCH-040.

### Follow-up
None.
