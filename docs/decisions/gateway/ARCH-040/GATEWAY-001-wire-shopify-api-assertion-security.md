---
id: ARCH-040-GATEWAY-001
architecture_id: ARCH-040
title: Wire Shopify API assertion security
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
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

# ARCH-040-GATEWAY-001 — Wire Shopify API assertion security

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

**Superseded — do not execute.** No Shopify-to-hosted-API assertion route or new secret is needed for ARCH-040.

## Context

The merchant hosted API is accessed only by WooCommerce using the existing installation credential. Shopify authenticates in its own app server and accesses Prisma directly. Existing Render Gateway/API routes already serve Woo installation requests; no ARCH-040-specific Gateway implementation is currently justified.

## Scope

Historical task record only. Do not claim, implement or materialise.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

None. If actual future implementation discovers a missing Woo API route or environment capability, report it to `moda_architect` with evidence; do not revive signed Shopify assertions.

## Work Items

- [x] Superseded before implementation due to removed Shopify assertion boundary.

## Interfaces / Contracts

No new API authentication route, secret or published Shared package is required by this initiative.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

None; superseded.

## Validation

None; superseded.

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

Historical record. The canonical Render Blueprint remains owned by moda_gateway for independently justified infrastructure changes.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
