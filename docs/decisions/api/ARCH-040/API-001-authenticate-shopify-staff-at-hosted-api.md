---
id: ARCH-040-API-001
architecture_id: ARCH-040
title: Authenticate Shopify staff at hosted API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHARED-002
enables:
  - ARCH-040-API-003
  - ARCH-040-SHOPIFY-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-API-001 — Authenticate Shopify staff at hosted API

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add an authenticated server-to-server Shopify merchant-principal assertion boundary for hosted conversation endpoints.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded api capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Validate short-lived signed assertion, audience, expiry, nonce/replay resistance and shop binding.
- Require Shopify app server to verify staff and session before assertion issue; hosted API still enforces shop ID and capabilities.
- Preserve existing separate Woo installation authenticator; no direct browser call with server credentials.

## Work Items

- [ ] Validate short-lived signed assertion, audience, expiry, nonce/replay resistance and shop binding.
- [ ] Require Shopify app server to verify staff and session before assertion issue; hosted API still enforces shop ID and capabilities.
- [ ] Preserve existing separate Woo installation authenticator; no direct browser call with server credentials.

## Interfaces / Contracts

Use the single versioned cross-repository runtime contract owned by `ARCH-040-SHARED-001` and published by `ARCH-040-SHARED-002`; where a task operates before that gate, define schema-compatible fields in its own boundary and do not import unpublished sibling source. Canonical persisted entities: `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt` and the approved durable command/outbox. The provider request stays in Background; Woo browser traffic stays on WordPress REST.

## Dependencies

- ARCH-040-SHARED-002

## Enables

- ARCH-040-API-003
- ARCH-040-SHOPIFY-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Cross-shop, tampered, expired and replayed assertions are rejected.
- [ ] Request actor identity can be audited without trusting arbitrary browser-provided fields.

## Validation

- [ ] Authenticator unit/security cases
- [ ] Tenant isolation integration tests
- [ ] git diff --check; review canonical task-worktree and dependency-sync evidence

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks. Publication tasks validate only publication mechanics.

## Implementation Notes

Use `scripts/start-agent-task.py --prepare` in the actual developer workspace when this definition is materialised; keep matching parent and implementation task branches in separate launcher-resolved worktrees, as documented in workspace policy. Check actual repository scripts before validation. Structured logging must use the published shared logger; no credentials or full customer content in logs. Preserve current production compatibility unless architect specifically establishes a safe pre-production breaking rollout.

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
