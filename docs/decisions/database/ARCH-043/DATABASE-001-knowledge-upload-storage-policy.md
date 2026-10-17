---
id: ARCH-043-DATABASE-001
architecture_id: ARCH-043
title: Persist versioned Merchant Knowledge upload and storage policies
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
enables: ["ARCH-043-ADMIN-001", "ARCH-043-BACKGROUND-002", "ARCH-043-API-001", "ARCH-043-SHOPIFY-001"]
created: 2026-10-17
updated: 2026-10-17
---

# Persist versioned Merchant Knowledge upload and storage policies

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-database` / `moda_database`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Create one typed, environment-scoped authority for Merchant Knowledge upload limits and non-secret R2 location.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Inspect existing Merchant Knowledge schema and API, Background and Shopify upload validators before deciding field shapes.
- Add typed configuration for max upload bytes, max XLSX uncompressed bytes, R2 endpoint and bucket, with environment identity, version and audit trail.
- Provide migration/seeding strategy that does not invent actual R2 endpoint or bucket values, including explicit operator cutover.
- Add fresh-install and upgrade PostgreSQL integration tests, constraints, safe bounds and rollback notes.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Hard runtime safety caps stay in consuming code; lower database policy cannot be bypassed by legacy process.env.
- R2 endpoint is validated as HTTPS, without credentials, SSRF-prone locations or unsupported origins; consumers retain independent network restrictions.
- Configuration is environment scoped and fail closed when absent at a protected operation; no implicit test-to-production fallback.
- Optimistic version/CAS mutations with a single audit event committed atomically; no untyped catch-all JSON config.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Inspect existing Merchant Knowledge schema and API, Background and Shopify upload validators before deciding field shapes.
- [ ] Add typed configuration for max upload bytes, max XLSX uncompressed bytes, R2 endpoint and bucket, with environment identity, version and audit trail.
- [ ] Provide migration/seeding strategy that does not invent actual R2 endpoint or bucket values, including explicit operator cutover.
- [ ] Add fresh-install and upgrade PostgreSQL integration tests, constraints, safe bounds and rollback notes.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- Merchant Knowledge policy contract: ARCH-043-SHARED-001
- Existing Merchant Knowledge storage and revision models remain authoritative for source lifecycle.

## Dependencies

None

## Enables

- `ARCH-043-ADMIN-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-API-001`
- `ARCH-043-SHOPIFY-001`

## Acceptance Criteria

- [ ] Environment-specific typed row/columns and migration verified on fresh and upgraded Postgres.
- [ ] Concurrent/stale updates fail without partial audit; safety bounds and missing location rejected.
- [ ] No existing ShopSettings/feature entitlement or knowledge revision semantics changed.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Prisma format and validate
- [ ] Fresh/upgrade disposable PostgreSQL integration
- [ ] Schema constraint, tenant/environment and CAS tests
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
