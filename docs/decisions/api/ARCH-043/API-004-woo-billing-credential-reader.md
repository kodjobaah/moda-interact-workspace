---
id: ARCH-043-API-004
architecture_id: ARCH-043
title: Use database Woo billing credential pair
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 55
executor: developer
claimed_at: 2026-10-21T13:04:14Z
attempt: 1
depends_on:
- ARCH-043-ADMIN-002
- ARCH-043-DATABASE-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-21'
---

# Use database Woo billing credential pair

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_api` (`moda-interact-api`).
- **Materialised and claimed — developer Attempt 1, 2026-10-21.** The canonical parent and API implementation task worktrees were created from current `origin/main`; developer execution and completion authority were explicitly assumed while preserving `assigned_agent: moda_api`.

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

In Progress — developer Attempt 1 claimed on 2026-10-21. Both explicit dependencies resolved `complete` before claim. Implementation has not started; this invocation prepares the task and hands control back to the developer.

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

## Developer Execution Ownership Amendment

On 2026-10-21, the developer invoked `/moda_developer_create ARCH-043-API-004`, explicitly taking over this ready agent-owned task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria, and validation requirements are unchanged.

## Developer Claim — Attempt 1

**Claimed — 2026-10-21T13:04:14Z.** The task transitioned from `ready`, Attempt 0, null executor to `in_progress`, Attempt 1, `executor: developer`.

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-API-004`, branch `task/ARCH-043-API-004`, created from current parent `origin/main` at `d3f61398`. The task-specific branch was not present locally/remotely before preparation; publication follows this claim commit.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-API-004`, branch `task/ARCH-043-API-004`, created from current API `origin/main` at `0d97176`. The task-specific branch was not present locally/remotely before preparation; implementation work remains unstarted.
- Start synchronization: both worktrees were created from fetched current `origin/main`; no task-branch fast-forward or mainline merge was needed. Both worktrees are clean. Shared workspace and API source checkouts were not switched or modified for task execution; their pre-existing unrelated/generated changes were left untouched.
- Dependency readiness was verified through the canonical launcher before claim: `ARCH-043-ADMIN-002` and `ARCH-043-DATABASE-001` both resolve `complete`.
- Required implementation validation remains: task-focused positive/negative unit and integration tests; typecheck; applicable lint/build; and `git diff --check`. No implementation or test changes were made as part of this claim operation.
