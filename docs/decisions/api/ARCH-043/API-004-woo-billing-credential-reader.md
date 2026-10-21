---
id: ARCH-043-API-004
architecture_id: ARCH-043
title: Use database Woo billing credential pair
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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
- ARCH-043-DATABASE-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Use database Woo billing credential pair

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_api` (`moda-interact-api`).
- **Defined but not materialised**: no branch, worktree or claim is asserted.

## Objective

Migrate hosted API WooCommerce billing provider key and secret to `woocommerce.billing`, separate from `woocommerce.auth` and merchant REST grants.

## Context

The canonical ARCH-043 inventory defines this as a newly scoped consumer task; do not revive identically numbered superseded proposal files or their retired dependencies. The generic database models and ARCH-039 published cryptography remain unchanged.

## Scope

- Resolve and decrypt `{apiKey,apiSecret}` together for each billing command without caching across operations.
- Continue to select `sandbox` versus `production` exclusively using deployment `WOO_BILLING_ENVIRONMENT`.
- Preserve billing idempotency, provider receipts and retry semantics. Do not expose credentials to WooCommerce plugin or browser.

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

- [ ] Resolve and decrypt `{apiKey,apiSecret}` together for each billing command without caching across operations.
- [ ] Continue to select `sandbox` versus `production` exclusively using deployment `WOO_BILLING_ENVIRONMENT`.
- [ ] Preserve billing idempotency, provider receipts and retry semantics. Do not expose credentials to WooCommerce plugin or browser.
- [ ] Add positive and negative unit/integration tests; record actual validation and isolated-worktree evidence.

## Interfaces / Contracts

- Configuration keys and decrypted field names: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October reconciliation).
- Writer and sealed key lifecycle: `ARCH-043-ADMIN-002`; schema: `ARCH-043-DATABASE-001`.
- Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (existing published exports).

## Dependencies

- `ARCH-043-ADMIN-002`
- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Sandbox/production isolation and missing pair rejection
- [ ] Provider billing lifecycle, receipt and retry regression
- [ ] CAS rotation, revoked/wrong environment/decrypt failure, typecheck
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
