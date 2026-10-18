---
id: ARCH-043-SHOPIFY-003
architecture_id: ARCH-043
title: Consume encrypted Shopify Partner billing credentials
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-ADMIN-002
- ARCH-043-SHOPIFY-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Consume encrypted Shopify Partner billing credentials

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_app` (`moda-interact`).
- **Defined but not materialised**: no branch, worktree or claim is asserted.

## Objective

Replace Shopify billing provider Partner API environment reads with purpose-bound `shopify.partner` DB configuration; leave store OAuth intact.

## Context

The canonical ARCH-043 inventory defines this as a newly scoped consumer task; do not revive identically numbered superseded proposal files or their retired dependencies. The generic database models and ARCH-039 published cryptography remain unchanged.

## Scope

- Resolve the complete Partner tuple at each Partner billing operation using the Shopify server-only configuration service.
- Retain Shopify billing idempotency, provider responses, app identity and API version behaviour.
- Never expose Partner tokens to merchant browser or share with shop-scoped OAuth.

## Out of Scope

- No new Prisma model, root cryptography, Shared package, gateway or cross-repository implementation.
- No `_index.md` changes, unrelated refactors or premature environment removal.

## Requirements

- Use the environment-scoped `PlatformConfiguration` sealed envelope with immutable AAD bytes and published ARCH-039 Node-only decryption.
- A configured, disabled, corrupt, undecryptable or unavailable database credential fails closed. Transitional env use requires an explicit gated cutover and must never mix credential bundle sources.
- Read once per relevant bounded operation; do not add a per-event hot-path query, a global indefinite cache or a network operation inside a transaction.
- Secrets never leave the trusted server or enter logs, audits, errors or browser output.
- Respect existing service ownership, launcher task-isolation, developer review and task-state claims.

## Work Items

- [ ] Resolve the complete Partner tuple at each Partner billing operation using the Shopify server-only configuration service.
- [ ] Retain Shopify billing idempotency, provider responses, app identity and API version behaviour.
- [ ] Never expose Partner tokens to merchant browser or share with shop-scoped OAuth.
- [ ] Add positive and negative unit/integration tests; record actual validation and isolated-worktree evidence.

## Interfaces / Contracts

- Configuration keys and decrypted field names: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October reconciliation).
- Writer and sealed key lifecycle: `ARCH-043-ADMIN-002`; schema: `ARCH-043-DATABASE-001`.
- Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (existing published exports).

## Dependencies

- `ARCH-043-ADMIN-002`
- `ARCH-043-SHOPIFY-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Partner billing provider and webhook billing regressions
- [ ] Version changes/revoke/unavailable database and secret non-disclosure
- [ ] Shopify server-only boundary proof and build
- [ ] No cross-environment secret leakage, duplicate provider credentials or stale revision reuse.
- [ ] All prerequisite tasks were Complete before the implementation claim.

## Validation

- [ ] Task-focused unit and integration tests using existing repository commands.
- [ ] Typecheck, applicable lint/build, `git diff --check`.
- [ ] Recorded launcher-resolved parent/implementation task worktree isolation and sync.

## Stop Condition

After required work and validation, record the Completion Report, mark Review and STOP. Architect alone accepts this agent-owned task. Do not start enabled tasks.

## Implementation Notes

Inspect the actual target worktree before coding; this portable task is grounded in an earlier snapshot and is not a claim that a current deployed reader has changed.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not evaluated.

### Follow-up

None
