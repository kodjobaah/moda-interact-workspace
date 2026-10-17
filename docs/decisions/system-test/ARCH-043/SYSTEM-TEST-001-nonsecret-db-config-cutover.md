---
id: ARCH-043-SYSTEM-TEST-001
architecture_id: ARCH-043
title: Certify dynamic database runtime configuration
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-GATEWAY-001"]
enables: []
created: 2026-10-17
updated: 2026-10-17
---

# Certify dynamic database runtime configuration

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-system-test` / `moda_system_test`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Prove non-secret settings are database authoritative across Admin, API, Shopify, Commerce and Background in an integrated environment.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Exercise versioned Admin edits and propagation to all affected consumers.
- Prove policy safety, environment separation, crash/restart/refresh, stale replica, corrupted row and DB transient outages.
- Verify no superseded environment variable can override accepted DB configuration, and Render Blueprints deploy without those declarations.
- Preserve evidence for Woo coupon lease correctness and Knowledge upload integrity.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Black-box tests via running services, not merely mock typed policy.
- Do not create implementation changes in the system-test task.
- No nondeterministic remote production operations.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Exercise versioned Admin edits and propagation to all affected consumers.
- [ ] Prove policy safety, environment separation, crash/restart/refresh, stale replica, corrupted row and DB transient outages.
- [ ] Verify no superseded environment variable can override accepted DB configuration, and Render Blueprints deploy without those declarations.
- [ ] Preserve evidence for Woo coupon lease correctness and Knowledge upload integrity.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-GATEWAY-001` (must be architect-accepted **Complete**)

## Enables

None

## Acceptance Criteria

- [ ] All required cross-service changes observable without redeployment.
- [ ] No unbounded fallback, cross-environment access or failure of hard cap.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Disposable Postgres/Redis and signed API upload E2E
- [ ] Black-box Admin/worker/Commerce/Shopify config scenario
- [ ] Evidence paths/repro logs, cleanup and git diff --check

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
