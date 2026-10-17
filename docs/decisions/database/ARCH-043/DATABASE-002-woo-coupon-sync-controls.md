---
id: ARCH-043-DATABASE-002
architecture_id: ARCH-043
title: Extend BackgroundRuntimeConfig for Woo coupon sync
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-043-ADMIN-002", "ARCH-043-BACKGROUND-001"]
created: 2026-10-17
updated: 2026-10-17
---

# Extend BackgroundRuntimeConfig for Woo coupon sync

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-database` / `moda_database`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Make Woo coupon sync operational limits versioned and Admin-auditable in existing BackgroundRuntimeConfig.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Extend the existing singleton with the ten ARCH-036 coupon sync knobs, including worker process concurrency.
- Reuse BackgroundRuntimeConfig.version, audit events, admin sections, constraints and defaults that match documented ARCH-036 operating bounds.
- Add migration tests for unchanged existing rows and fresh singleton initialisation.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Do not add a competing Woo-specific key/value table or runtime environment override.
- Preserve database-leased WOO_COUPON_SYNC_DISPATCH cadence, shop claim ownership and existing bounds.
- Correctness-internal absolute caps stay code-owned.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Extend the existing singleton with the ten ARCH-036 coupon sync knobs, including worker process concurrency.
- [ ] Reuse BackgroundRuntimeConfig.version, audit events, admin sections, constraints and defaults that match documented ARCH-036 operating bounds.
- [ ] Add migration tests for unchanged existing rows and fresh singleton initialisation.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

None

## Enables

- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-001`

## Acceptance Criteria

- [ ] Exact ten values and bounds are queryable from the existing versioned singleton.
- [ ] Existing runtime configuration fields and audit records remain valid after migration.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Prisma validate
- [ ] Disposable PostgreSQL fresh/upgrade tests
- [ ] Schema constraint and audit tests
- [ ] git diff --check

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, record the Completion Report, set this task to `review`, clear the active implementation claim under normal workflow and **STOP**. Do not start enabled tasks; architectural acceptance is reserved to `moda_architect`.

## Implementation Notes

- Do not repeat configuration parsing or encryption across services when a matching published Shared primitive exists.
- Preserve snapshot/refresh and failure semantics without synchronous configuration reads on throughput-critical paths.
- If the original snapshot differs from the developer task worktree, rebase against the actual target, never force-apply or overwrite concurrent task changes.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Worktree and Branch Evidence

Not yet materialised or claimed. Record prepared launcher packet, parent/implementation worktree paths, Git common-dir identity, submodules and start-of-attempt synchronisation when executed.

### Deviations

None

### Assumptions

Source snapshot dated 2026-10-17; revalidate actual runtime behavior when claimed.

### Unresolved Issues

None identified at definition time.

### Architectural Concerns

None identified at definition time.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and independent architect review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
