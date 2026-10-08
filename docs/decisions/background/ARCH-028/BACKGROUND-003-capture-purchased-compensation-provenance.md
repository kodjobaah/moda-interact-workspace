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
updated: 2026-10-07
---

# Capture purchased recovery compensation provenance at commit

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

**Superseded before implementation.**

The original proposal captured purchased/refund state at recovery commit so later WhatsApp compensation could reconstruct monetary-refund history. ARCH-027 now owns provider refund state and ARCH-028 must not reconstruct it.

## Context

The final design uses generic DATABASE-001 compensation lineage (consolidated from superseded DATABASE-002). Generic non-purchased compensation is implemented by BACKGROUND-004. Committed purchased-credit compensation is isolated in BACKGROUND-009 and consumes the then-current authoritative ARCH-027 purchase/refund model.

## Scope

None. Historical record only.

## Out of Scope

All implementation.

## Requirements

None.

## Work Items

None.

## Interfaces / Contracts

None.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

None.

## Validation

None.

## Stop Condition

Do not execute this task.

## Implementation Notes

Replacement responsibilities: `ARCH-028-DATABASE-001` (consolidated provenance), `ARCH-028-BACKGROUND-004`, `ARCH-028-BACKGROUND-009`.

## Completion Report

### Status

Superseded before implementation.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not applicable.

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

Superseded

### Review Notes

Superseded by the final ARCH-027 refund boundary and the ARCH-028 generic/purchased compensation split.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not applicable.

### Follow-up

Use BACKGROUND-004 and BACKGROUND-009.
