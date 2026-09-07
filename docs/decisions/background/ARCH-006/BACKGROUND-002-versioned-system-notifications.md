---
id: ARCH-006-BACKGROUND-002
architecture_id: ARCH-006
title: Implement versioned merchant system notifications
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: superseded
priority: 999
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-006-BACKGROUND-002: Implement versioned merchant system notifications

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Superseded: SYSTEM message creation now belongs to the repository that owns the authoritative event transition. `ARCH-006-SHOPIFY-002` creates `SUBSCRIPTION_ENDED` directly and the generic translation pipeline handles any required translation; a cross-repository callable background notification service would add an unnecessary runtime boundary.

## Context

This task remains as a durable supersession record so historical ARCH-006 references do not disappear.

## Scope

None

## Out of Scope

All implementation.

## Requirements

None

## Work Items

None

## Interfaces / Contracts

None

## Dependencies

None

## Enables

None

## Acceptance Criteria

None

## Validation

None

## Implementation Notes

Do not claim or execute this task.

## Completion Report

### Status

Superseded before implementation.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

None yet.

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
