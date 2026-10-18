---
id: ARCH-043-ADMIN-004
architecture_id: ARCH-043
title: Use database Shopify Partner credentials in Admin subscription reads
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-ADMIN-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-18'
---

# Use database Shopify Partner credentials in Admin subscription reads

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_admin` (`moda-interact-admin`).
- **Defined but not materialised**: no branch, worktree or claim is asserted.

## Objective

Replace the current Admin Shopify Partner subscription inspection environment reads with the approved purpose-scoped `shopify.partner` configuration. Do not change the Admin login system.

## Context

The canonical ARCH-043 inventory defines this as a newly scoped consumer task; do not revive identically numbered superseded proposal files or their retired dependencies. The generic database models and ARCH-039 published cryptography remain unchanged.

## Scope

- Read the validated partner tuple `{accessToken,organizationId,appId,apiVersion?}` from PostgreSQL for each Partner API operation, using the existing Admin service and ARCH-039 unseal mechanism.
- Preserve current environment alias compatibility only until the explicit cutover; never mix org/token/app ID from different sources.
- Keep request authentication, SUPER_ADMIN authorisation, error redaction and Partner API response handling unchanged.

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

- [ ] Read the validated partner tuple `{accessToken,organizationId,appId,apiVersion?}` from PostgreSQL for each Partner API operation, using the existing Admin service and ARCH-039 unseal mechanism.
- [ ] Preserve current environment alias compatibility only until the explicit cutover; never mix org/token/app ID from different sources.
- [ ] Keep request authentication, SUPER_ADMIN authorisation, error redaction and Partner API response handling unchanged.
- [ ] Add positive and negative unit/integration tests; record actual validation and isolated-worktree evidence.

## Interfaces / Contracts

- Configuration keys and decrypted field names: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October reconciliation).
- Writer and sealed key lifecycle: `ARCH-043-ADMIN-002`; schema: `ARCH-043-DATABASE-001`.
- Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (existing published exports).

## Dependencies

- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Valid partner lookup and revision refresh
- [ ] Alias compatibility in transition only; missing/revoked/invalid/wrong-environment rejects
- [ ] No secrets in logs/browser, typecheck and focused Partner API tests
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
