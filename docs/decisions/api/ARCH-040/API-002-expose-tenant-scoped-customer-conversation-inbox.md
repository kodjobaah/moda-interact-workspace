---
id: ARCH-040-API-002
architecture_id: ARCH-040
title: Expose tenant-scoped customer conversation inbox
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
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-SHOPIFY-001
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-API-002 — Expose tenant-scoped customer conversation inbox

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Expose bounded, authenticated merchant inbox/list and paginated messages on the existing Conversation models.

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

- Read only conversations belonging to authenticated shop and allowed recovery scope.
- Return mode, message `senderType` (including HUMAN), current revision, last inbound/last message, eligibility; preserve independent cursor pagination.
- Reuse ARCH-035 Woo detail read contracts wherever applicable rather than invent second recovery-detail payloads; redact unnecessary PII.

## Work Items

- [ ] Read only conversations belonging to authenticated shop and allowed recovery scope.
- [ ] Return mode, message `senderType` (including HUMAN), current revision, last inbound/last message, eligibility; preserve independent cursor pagination.
- [ ] Reuse ARCH-035 Woo detail read contracts wherever applicable rather than invent second recovery-detail payloads; redact unnecessary PII.

## Interfaces / Contracts

Canonical persisted state and enums are owned by `moda-interact-database` (Prisma `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand`), not by a new ARCH-040 Shared package. The hosted API owns input validation, HTTP request/response DTOs, status/error semantics and documented endpoint compatibility. Authenticate/resolve shop scope server-side. Shopify/Woo clients consume the hosted endpoint; they do not read Moda PostgreSQL directly.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-SHOPIFY-001
- ARCH-040-WOOCOMMERCE-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Initial and follow-up messages appear in one transcript with one conversation ID.
- [ ] Mixed human/AI authors render distinguishably.
- [ ] Foreign shop, invalid cursors and disabled merchant accesses fail closed.

## Validation

- [ ] API contract tests
- [ ] Pagination and cross-tenant PostgreSQL integration
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
