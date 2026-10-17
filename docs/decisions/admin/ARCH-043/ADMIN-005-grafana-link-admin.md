---
id: ARCH-043-ADMIN-005
architecture_id: ARCH-043
title: Manage Grafana navigation URLs
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-DATABASE-005"]
enables: ["ARCH-043-GATEWAY-001"]
created: 2026-10-17
updated: 2026-10-17
---

# Manage Grafana navigation URLs

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-admin` / `moda_admin`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Replace Admin Grafana environment-link reads with validated database-managed navigation links.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Inspect/reuse src/lib/observability/grafana.ts and Admin links editor rather than adding a parallel Admin config service.
- Implement authenticated admin loader, mutation, audit presentation and focused security/UI regression tests.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Treat as navigation URLs only, not OTLP credentials or authentication.
- Validate HTTPS/host, optional links, CAS and environment separation.
- Do not break System Health observability when optional URL absent.
- Require existing privileged platform-admin authorisation, CSRF protections, tenant/environment isolation where applicable.
- Use version CAS; no double-submit or silent last-write-wins mutation.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Inspect/reuse src/lib/observability/grafana.ts and Admin links editor rather than adding a parallel Admin config service.
- [ ] Implement authenticated admin loader, mutation, audit presentation and focused security/UI regression tests.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-DATABASE-005` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-GATEWAY-001`

## Acceptance Criteria

- [ ] Authorised platform admin can inspect and update its own environment policy.
- [ ] Stale/unauthorised edits rejected with no partial audit and no secret leakage.
- [ ] Config is visible after refresh across Admin replicas.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Focused Admin service/action tests
- [ ] Auth/CAS and UI component regressions
- [ ] Typecheck/lint/build as declared
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
