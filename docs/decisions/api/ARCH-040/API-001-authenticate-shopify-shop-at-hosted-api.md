---
id: ARCH-040-API-001
architecture_id: ARCH-040
title: Authenticate Shopify shop assertions at hosted API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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
  - ARCH-040-API-003
  - ARCH-040-GATEWAY-001
  - ARCH-040-SHOPIFY-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-API-001 — Authenticate Shopify shop assertions at hosted API

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add an authenticated server-to-server Shopify merchant-shop assertion boundary for hosted conversation endpoints.

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
- Require the Shopify app server to authenticate access through its existing app session before assertion issuance; hosted API verifies the bound `shopId` and tenant ownership. Do not mandate online staff identity or add Moda-specific capabilities.
- Preserve existing separate Woo installation authenticator; no direct browser call with server credentials.

## Work Items

- [ ] Validate short-lived signed assertion, audience, expiry, nonce/replay resistance and shop binding.
- [ ] Require the Shopify app server to authenticate access through its existing app session before assertion issuance; hosted API verifies the bound `shopId` and tenant ownership. Do not mandate online staff identity or add Moda-specific capabilities.
- [ ] Preserve existing separate Woo installation authenticator; no direct browser call with server credentials.

## Interfaces / Contracts

Canonical persisted state and enums are owned by `moda-interact-database` (Prisma `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand`), not by a new ARCH-040 Shared package. The hosted API owns input validation, HTTP request/response DTOs, status/error semantics and documented endpoint compatibility. Authenticate/resolve shop scope server-side. Shopify/Woo clients consume the hosted endpoint; they do not read Moda PostgreSQL directly.

Specify the shop assertion signing format and claims (shop identifier, issuer, audience, expiry and nonce/replay identity) as part of API-001, using a suitable established standard/approved library. `SHOPIFY-001` implements the matching server-side issuer. Test the cross-service bytes/signatures, tampering and rotation/expiry behaviour without introducing a duplicate custom cryptographic utility. If genuinely missing reusable crypto is identified, return the exact gap to `moda_architect`.

## Dependencies

None.

## Enables

- ARCH-040-API-003
- ARCH-040-GATEWAY-001
- ARCH-040-SHOPIFY-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Cross-shop, tampered, expired and replayed assertions are rejected.
- [ ] Authenticated shop identity is available to all hosted commands without trusting arbitrary browser-provided shop IDs or staff identifiers.

## Validation

- [ ] Authenticator unit/security cases
- [ ] Tenant isolation integration tests
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
