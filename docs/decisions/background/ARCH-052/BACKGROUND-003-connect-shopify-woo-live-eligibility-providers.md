---
id: ARCH-052-BACKGROUND-003
architecture_id: ARCH-052
title: Wire independent Shopify and Woo checkout-specific eligibility adapters
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-003: Wire independent Shopify and Woo checkout-specific eligibility adapters

## Architecture

`ARCH-052` — `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordination: `moda_architect`.

## Objective

**DO NOT IMPLEMENT.** This planning-only task was superseded before claim or source execution.

## Context

The original Attempt 2 proposed an independent Background discount subsystem. The revised architecture reuses existing published MCP discount tools, the shared Commerce runner and existing provider proof. See `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-SHARED-006`, `ARCH-052-SHARED-007` and the single Background bridge `ARCH-052-BACKGROUND-010`.

## Scope

None. Superseded documentation is retained only to explain why no separate Background subsystem may be implemented.

## Out of Scope

**All implementation** under this task ID. In particular no standalone Background candidate crawler, eligibility adapter, or bespoke AI model recommender.

## Requirements

No execution, claim, branch or source edits under this ID.

## Work Items

None — superseded.

## Interfaces / Contracts

Use the published Shared/MCP contracts owned by the replacement tasks instead.

## Dependencies

None — task is superseded and ineligible regardless of dependency state.

## Enables

None — all dependants have been rewired to the replacement tasks.

## Acceptance Criteria

None — the task may not become review or complete.

## Validation

None — no implementation.

## Stop Condition

Do not run `/moda-task ARCH-052-BACKGROUND-003`.

## Implementation Notes

No file edits or architecture deviations authorised.

## Completion Report

### Status

Not Started — Superseded.

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

Replaced by the published MCP integration.

## Architect Review

### Review Status

Superseded.

### Review Notes

Superseded before implementation due to existing CommerceAgent/MCP capabilities; no accepted implementation lost.

### Reviewed Files

Attempt 2 task definition and Attempt 3 replacement tasks.

### Validation Reviewed

Task graph only.

### Architecture Conformance

Superseded; no implementation to review.

### Follow-up

Execute only the dependency-eligible replacement task IDs.
