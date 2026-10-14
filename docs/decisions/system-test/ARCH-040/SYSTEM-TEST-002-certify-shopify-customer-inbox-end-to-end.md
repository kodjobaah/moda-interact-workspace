---
id: ARCH-040-SYSTEM-TEST-002
architecture_id: ARCH-040
title: Certify Shopify customer inbox end-to-end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHOPIFY-003
  - ARCH-040-SYSTEM-TEST-001
enables: []
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-SYSTEM-TEST-002 — Certify Shopify customer inbox end-to-end

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Validate Shopify merchant sessions, inbox pagination, author labels, takeover and human replies against deployed integration.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded system-test capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Exercise valid and invalid Shopify app sessions and cross-shop access (without assuming online staff identity), duplicate clicks, closed-window templates, retry/failure and stale poll responses.
- Verify UI and provider transcript refer to same Conversation row and activity is credited once.

## Work Items

- [ ] Exercise valid and invalid Shopify app sessions and cross-shop access (without assuming online staff identity), duplicate clicks, closed-window templates, retry/failure and stale poll responses.
- [ ] Verify UI and provider transcript refer to same Conversation row and activity is credited once.

## Interfaces / Contracts

Use the single versioned cross-repository runtime contract owned by `ARCH-040-SHARED-001` and published by `ARCH-040-SHARED-002`; where a task operates before that gate, define schema-compatible fields in its own boundary and do not import unpublished sibling source. Canonical persisted entities: `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt` and the approved durable command/outbox. The provider request stays in Background; Woo browser traffic stays on WordPress REST.

## Dependencies

- ARCH-040-SHOPIFY-003
- ARCH-040-SYSTEM-TEST-001

## Enables

None.

## Acceptance Criteria

- [ ] Shopify interface fully exercises the shared runtime without a new thread.
- [ ] Mode, audit and billing evidence agree.

## Validation

- [ ] Shopify black-box browser/system test suite
- [ ] Evidence paths and release checklist
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
