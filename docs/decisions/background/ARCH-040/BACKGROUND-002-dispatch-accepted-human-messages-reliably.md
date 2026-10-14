---
id: ARCH-040-BACKGROUND-002
architecture_id: ARCH-040
title: Dispatch accepted human messages reliably
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
  - ARCH-040-DATABASE-003
  - ARCH-040-BACKGROUND-001
enables:
  - ARCH-040-BACKGROUND-003
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-BACKGROUND-002 — Dispatch accepted human messages reliably

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Consume the merchant command/outbox and send human WhatsApp messages into the existing ConversationMessage history.

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

- Build durable relay/consumer with retry and idempotent provider dispatch; retain `ConversationMessage.senderType=HUMAN` without staff provenance.
- Share existing approved WhatsApp delivery/receipts and recipient suppression, but do not bypass existing AGENT/AUTOMATION caps with a cast.
- Recheck control revision, conversation/recipient eligibility and the last-customer-inbound 24-hour window at final handoff; if an accepted text command expires while queued, fail it safely, never send free text or silently convert it to a template.

## Work Items

- [ ] Build durable relay/consumer with retry and idempotent provider dispatch; retain `ConversationMessage.senderType=HUMAN` without staff provenance.
- [ ] Share existing approved WhatsApp delivery/receipts and recipient suppression, but do not bypass existing AGENT/AUTOMATION caps with a cast.
- [ ] Recheck control revision, conversation/recipient eligibility and the last-customer-inbound 24-hour window at final handoff; if an accepted text command expires while queued, fail it safely, never send free text or silently convert it to a template.

## Interfaces / Contracts

Canonical `MerchantConversationSendCommand` in PostgreSQL is the producer/consumer boundary, regardless of whether it was created by authenticated Shopify app actions or the WooCommerce hosted API. Background polls/leases `ACCEPTED` commands and uses existing outbound transport/receipt mechanisms. A job may carry only the stable command ID through existing BullMQ infrastructure; no new Shared contract or HTTP endpoint is required. Producer acceptance and worker dispatch can be implemented independently, and both must be tested against the same database schema.

## Dependencies

- ARCH-040-DATABASE-003
- ARCH-040-BACKGROUND-001

## Enables

- ARCH-040-BACKGROUND-003
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] One human outbound message exists in the original conversation.
- [ ] Duplicate queue delivery or API retry does not send twice.
- [ ] Definitive provider failures and timeouts reconcile accurately.

## Validation

- [ ] Outbound integration tests
- [ ] BullMQ duplicate/crash/retry tests
- [ ] Provider failure/receipt tests
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
