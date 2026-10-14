---
id: ARCH-040-WOOCOMMERCE-001
architecture_id: ARCH-040
title: Proxy conversation API through trusted WordPress REST
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-035-API-013
enables:
  - ARCH-040-WOOCOMMERCE-002
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-WOOCOMMERCE-001 — Proxy conversation API through trusted WordPress REST

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Expose secure WordPress-side customer inbox/hand-over/reply facade to the hosted API without direct browser access.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded woocommerce capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Verify manage_woocommerce, WordPress nonce, current installation credential and disconnected/rotated state before each call.
- Resolve shop exclusively server-side; forward conversation cursor, control revision and idempotency safely. Do not forward/store WordPress user IDs or a staff principal.
- Keep existing two-stage WordPress menu registrations and separate merchant support inbox.

## Work Items

- [ ] Verify manage_woocommerce, WordPress nonce, current installation credential and disconnected/rotated state before each call.
- [ ] Resolve shop exclusively server-side; forward conversation cursor, control revision and idempotency safely. Do not forward/store WordPress user IDs or a staff principal.
- [ ] Keep existing two-stage WordPress menu registrations and separate merchant support inbox.

## Interfaces / Contracts

The hosted API owns validated HTTP payloads, response shapes and errors. WordPress REST authenticates the existing Woo admin session, then its server-side proxy uses connected installation credentials to call the hosted API. Never connect merchant-hosted PHP or browsers to Moda PostgreSQL; no ARCH-040 Shared conversation package.

## Dependencies

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-035-API-013

## Enables

- ARCH-040-WOOCOMMERCE-002

## Acceptance Criteria

- [ ] Tampered nonce/capability/cross-shop and disconnected installation cannot send.
- [ ] Browser sees only WordPress REST nonce, never Moda installation bearer.
- [ ] Hosted API detail reads are reused, not replaced with fake Woo records.

## Validation

- [ ] WordPress REST/PHPUnit security tests
- [ ] Hosted integration contract tests
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
