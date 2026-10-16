---
id: ARCH-040-API-001
architecture_id: ARCH-040
title: Authenticate Shopify shop assertions at hosted API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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

# ARCH-040-API-001 — Authenticate Shopify shop assertions at hosted API

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

**Superseded — do not execute.** Shopify server routes use existing Shopify app authentication and direct Prisma access; hosted `moda-interact-api` remains exclusively the WooCommerce installation API for ARCH-040.

## Context

2026-10-14 decision: The earlier design added Shopify-to-API signed assertions unnecessarily. There is no Shopify caller of the hosted merchant API for this feature. The existing WooCommerce installation authenticator remains sufficient. No new signing/nonce/issuer/audience infrastructure is required.

## Scope

Historical task record only. Do not claim, implement, or materialise as an active task.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

None. Superseded by the authenticated server-side Shopify routes in `ARCH-040-SHOPIFY-001`; WooCommerce API uses the existing `WooInstallationAuthenticator` in API-002/003/004.

## Work Items

- [x] Architecture decision: superseded before implementation; no code changes.

## Interfaces / Contracts

None. Do not add a Shopify assertion contract. Existing Woo installation credential authentication and tenant-scoped Prisma data form the relevant hosted API boundary.

## Dependencies

None.

## Enables

None; removed from all active dependencies.

## Acceptance Criteria

None; superseded.

## Validation

None; superseded.

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

Historical record. Any future need for a Shopify-to-hosted-API boundary would require a separate architectural decision; do not revive this task implicitly.

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
