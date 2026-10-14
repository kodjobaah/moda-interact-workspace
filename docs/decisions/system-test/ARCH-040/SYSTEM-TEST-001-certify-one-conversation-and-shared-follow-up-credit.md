---
id: ARCH-040-SYSTEM-TEST-001
architecture_id: ARCH-040
title: Certify one conversation and shared follow-up credit
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
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
  - ARCH-040-API-001
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-040-BACKGROUND-001
  - ARCH-040-BACKGROUND-002
  - ARCH-040-BACKGROUND-003
  - ARCH-040-GATEWAY-001
enables:
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-SYSTEM-TEST-001 — Certify one conversation and shared follow-up credit

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Independently certify atomic handover, WhatsApp message history, one post-window follow-up and billing under adversarial concurrency.

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

- Use black-box disposable PostgreSQL/Redis harness with real service boundaries; no all-in-one test file.
- Test customer inbound resets window, queued text crossing 24-hour expiry, takeover vs in-flight AI, human/AI follow-up race, retries, already used and failed provider sends.
- Assert same Conversation ID before/after every operation and one sequence-2 attempt/credit.

## Work Items

- [ ] Use black-box disposable PostgreSQL/Redis harness with real service boundaries; no all-in-one test file.
- [ ] Test customer inbound resets window, queued text crossing 24-hour expiry, takeover vs in-flight AI, human/AI follow-up race, retries, already used and failed provider sends.
- [ ] Assert same Conversation ID before/after every operation and one sequence-2 attempt/credit.

## Interfaces / Contracts

Verify the actual Prisma persistence contract, API-owned HTTP payload/error validation and existing authenticated Shopify/Woo server facades against running services. No new ARCH-040 Shared publication contract is required. Confirm the same `Conversation.id` is used for all author types and sequence-2 follow-up, with idempotent recovery credits and tenant isolation.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-DATABASE-002
- ARCH-040-DATABASE-003
- ARCH-040-API-001
- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-040-BACKGROUND-001
- ARCH-040-BACKGROUND-002
- ARCH-040-BACKGROUND-003
- ARCH-040-GATEWAY-001

## Enables

- ARCH-040-SYSTEM-TEST-002
- ARCH-040-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Single-conversation invariant passes through all branches.
- [ ] Human and AI concurrency produce at most one follow-up credit and provider action.
- [ ] Tenant and authentication bypasses are rejected.

## Validation

- [ ] Black-box database/queue/provider matrix
- [ ] Evidence bundle and deterministic repro scripts
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
