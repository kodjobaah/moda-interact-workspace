---
id: ARCH-040-SHOPIFY-003
architecture_id: ARCH-040
title: Add Shopify takeover and human reply controls
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHOPIFY-002
  - ARCH-040-BACKGROUND-003
enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-SHOPIFY-003 — Add Shopify takeover and human reply controls

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Enable Shopify merchants to Take Over, Resume AI, and send eligible human text/template replies from the inbox.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded shopify capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Expose mode CAS conflicts, delivery pending/failure, current service-window eligibility and follow-up already-used state.
- Prevent double-submission, stale response and rapid ownership-toggle races.
- Warn when provider submission predated takeover and cannot be recalled; do not imply new conversation creation.

## Work Items

- [ ] Expose mode CAS conflicts, delivery pending/failure, current service-window eligibility and follow-up already-used state.
- [ ] Prevent double-submission, stale response and rapid ownership-toggle races.
- [ ] Warn when provider submission predated takeover and cannot be recalled; do not imply new conversation creation.

## Interfaces / Contracts

The hosted API owns validated HTTP payloads, response shapes and errors; the Shopify server bridge consumes those endpoints after authenticating the existing Shopify shop session. Use the API-001-defined server-to-server assertion format and interoperability tests. No new ARCH-040 Shared conversation package or direct browser-to-PostgreSQL access.

## Dependencies

- ARCH-040-SHOPIFY-002
- ARCH-040-BACKGROUND-003

## Enables

- ARCH-040-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Merchant takeover pauses subsequent AI sends.
- [ ] Follow-up from Shopify consumes the same recovery credit as AI.
- [ ] Closed-window arbitrary free text is disabled in favour of approved template.

## Validation

- [ ] Shopify actions/component tests
- [ ] Manual read/compose/ownership flow
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
