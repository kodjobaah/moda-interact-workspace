---
id: ARCH-040-BACKGROUND-001
architecture_id: ARCH-040
title: Fence CommerceAgent against human takeover
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-BACKGROUND-002
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-001 — Fence CommerceAgent against human takeover

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Prevent CommerceAgent from starting or committing new automated messages after an authoritative human takeover.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded background capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Gate ARCH-040 handover in existing **recovery-linked** conversation execution; leave non-recovery conversation processing unaffected. Reuse the existing turn scheduler and final outbound-admission path rather than adding a second CommerceAgent runner. Scheduled recovery follow-ups must also respect HUMAN mode under BACKGROUND-003.

- Recheck mode/revision before AI execution, after tool/LLM await and at final provider-send admission.
- Use narrow conversation ordering, not a global worker mutex; stale generation and queued retry cannot bypass mode change.
- Make irreversible Meta send precedence explicit; never claim to retract provider requests already dispatched.

## Work Items

- [ ] Recheck mode/revision before AI execution, after tool/LLM await and at final provider-send admission.
- [ ] Use narrow conversation ordering, not a global worker mutex; stale generation and queued retry cannot bypass mode change.
- [ ] Make irreversible Meta send precedence explicit; never claim to retract provider requests already dispatched.

## Interfaces / Contracts

Canonical persisted state and enums are owned by `moda-interact-database` (Prisma `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand`), not by a new ARCH-040 Shared package. Background consumes Prisma-generated models and durable commands from PostgreSQL. Queue publication may carry a minimal stable command ID using existing queue infrastructure; do not invent a new Shared conversation schema solely for this. Preserve current provider transport, delivery receipts and ordering semantics.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-BACKGROUND-002
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Human takeover wins when persisted before send admission.
- [ ] AI does not resume stale turns after return to AI mode.
- [ ] Incoming customer messages remain durably recorded during Human mode.

## Validation

- [ ] Race-oriented unit tests
- [ ] Integration with concurrent outbound admission
- [ ] No duplicate provider-send tests
- [ ] git diff --check; review canonical task-worktree and dependency-sync evidence

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

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
