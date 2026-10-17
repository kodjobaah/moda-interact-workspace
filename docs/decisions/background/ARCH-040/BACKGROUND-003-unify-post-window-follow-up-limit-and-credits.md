---
id: ARCH-040-BACKGROUND-003
architecture_id: ARCH-040
title: Unify post-window follow-up limit and credits
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
  - ARCH-040-DATABASE-002
  - ARCH-040-BACKGROUND-002
enables:
  - ARCH-040-SHOPIFY-003
  - ARCH-040-WOOCOMMERCE-003
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
  - ARCH-040-BACKGROUND-005
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-003 — Unify post-window follow-up limit and credits

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Route scheduled AI/automation and merchant-initiated post-window follow-ups through the same recovery attempt and credit lifecycle.

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

- Reuse `recovery-outreach-follow-up-processor.service.ts`, its checkout/recovery lock and `RecoveryBillingService` credit identity `recovery-outreach:<attempt.id>`; do not add a second scheduler, follow-up record, provider receipt or usage ledger. Any failed/unknown receipt must reconcile through existing provider-status semantics before another attempt.

- Reconcile ARCH-016 configurable scheduling with customer lastInboundAt 24-hour window and one sequence-2 attempt.
- **Keep scheduled follow-ups no-response-only**: preserve the existing suppress-if-customer-responded branch. A merchant explicitly initiating an eligible post-window template after previous customer engagement may claim the **same** sequence-2 attempt (if unclaimed and recovery still actionable); do not add a scheduled re-engagement campaign. Document re-engagement eligibility and test both cases.
- Require approved Meta template; reserve/commit/release the existing recovery-conversation credit identically for HUMAN and AI.
- Lock by recovery/attempt; suppress scheduled automation while the thread is in HUMAN mode; compensate definitive failure without granting a second successful follow-up.

### Abuse and recovery-credit isolation

- Shop-level suspension and message screening apply only to HUMAN follow-up sends. A blocked/rejected HUMAN command does not create a second follow-up or consume an extra recovery conversation credit.
- Admin suspension does not change CommerceAgent/automation policy. Coordinate with BACKGROUND-004/005 at final provider admission; do not bypass those guards for `RECOVERY_FOLLOW_UP_TEMPLATE`.


## Work Items

- [ ] Reconcile ARCH-016 configurable scheduling with customer lastInboundAt 24-hour window and one sequence-2 attempt.
- [ ] Generalise existing no-response follow-up where necessary for a merchant-initiated closed-window follow-up after prior customer engagement, while keeping scheduled no-response policy conservative.
- [ ] Require approved Meta template; reserve/commit/release the existing recovery-conversation credit identically for HUMAN and AI.
- [ ] Lock by recovery/attempt; suppress scheduled automation while the thread is in HUMAN mode; compensate definitive failure without granting a second successful follow-up.

## Interfaces / Contracts

Canonical persisted state and enums are owned by `moda-interact-database` (Prisma `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand`), not by a new ARCH-040 Shared package. Background consumes Prisma-generated models and durable commands from PostgreSQL. Queue publication may carry a minimal stable command ID using existing queue infrastructure; do not invent a new Shared conversation schema solely for this. Preserve current provider transport, delivery receipts and ordering semantics.

## Dependencies

- ARCH-040-DATABASE-002
- ARCH-040-BACKGROUND-002

## Enables

- ARCH-040-SHOPIFY-003
- ARCH-040-WOOCOMMERCE-003
- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SYSTEM-TEST-002
- ARCH-040-SYSTEM-TEST-003
- ARCH-040-BACKGROUND-005

## Acceptance Criteria

- [ ] No new Conversation created by any follow-up route.
- [ ] At most one confirmed sequence-2 send and one follow-up credit per recovery.
- [ ] Window crossing, simultaneous human and AI, transient provider failure and recovery terminalization have deterministic outcomes.

## Validation

- [ ] Follow-up window matrix and billing unit tests
- [ ] PostgreSQL contention tests
- [ ] End-to-end provider/credit compensation checks
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
