---
id: ARCH-040-DATABASE-001
architecture_id: ARCH-040
title: Persist conversation mode, revision and human attribution
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
  - ARCH-040-SHARED-001
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-BACKGROUND-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-DATABASE-001 — Persist conversation mode, revision and human attribution

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add durable AI/HUMAN ownership and audit provenance to the existing Conversation/ConversationMessage schema without changing conversation identity.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded database capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Preserve @@unique([checkoutRecoveryId]) and existing ConversationMessage.senderType.
- Add a monotonic control revision that does not reset when mode is toggled; audited human actor and takeover timestamp.
- Provide the indexes needed for tenant-scoped inbox mode queries; safe additive migration and rollback.

## Work Items

- [ ] Preserve @@unique([checkoutRecoveryId]) and existing ConversationMessage.senderType.
- [ ] Add a monotonic control revision that does not reset when mode is toggled; audited human actor and takeover timestamp.
- [ ] Provide the indexes needed for tenant-scoped inbox mode queries; safe additive migration and rollback.

## Interfaces / Contracts

Use the single versioned cross-repository runtime contract owned by `ARCH-040-SHARED-001` and published by `ARCH-040-SHARED-002`; where a task operates before that gate, define schema-compatible fields in its own boundary and do not import unpublished sibling source. Canonical persisted entities: `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt` and the approved durable command/outbox. The provider request stays in Background; Woo browser traffic stays on WordPress REST.

## Dependencies

None.

## Enables

- ARCH-040-DATABASE-002
- ARCH-040-DATABASE-003
- ARCH-040-SHARED-001
- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-BACKGROUND-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Existing recovery has exactly one conversation before and after human/AI control toggles.
- [ ] Human provenance is immutable and can be tied to authenticated merchant principal.
- [ ] Repeated takeovers cannot reset revision or lose control history.

## Validation

- [ ] Prisma validate/generate
- [ ] Fresh+upgrade disposable PostgreSQL migrations
- [ ] Schema/uniqueness/CAS focused integration tests
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
