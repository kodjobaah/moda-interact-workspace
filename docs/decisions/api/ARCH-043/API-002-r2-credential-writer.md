---
id: ARCH-043-API-002
architecture_id: ARCH-043
title: Use encrypted database R2 write credentials in hosted API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-DATABASE-007", "ARCH-043-SHARED-004", "ARCH-043-API-001"]
enables: ["ARCH-043-GATEWAY-002"]
created: 2026-10-17
updated: 2026-10-17
---

# Use encrypted database R2 write credentials in hosted API

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-api` / `moda_api`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Replace hosted API R2 signing credentials with environment-scoped, write-purpose encrypted record lookup.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Use accepted Shared AAD/keyring to resolve upload-signing credentials server-side.
- Cache bounded revision and sign only approved object key/operation, preserving API-017 upload security.
- Retire API R2 access/secret environment reads after controlled cutover.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Only API server is authorised reader; WordPress/browser never receive raw keys.
- Fail closed on revocation, wrong environment, key mismatch and malformed credential.
- Do not grant write-purpose credentials to Background read-only service.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Use accepted Shared AAD/keyring to resolve upload-signing credentials server-side.
- [ ] Cache bounded revision and sign only approved object key/operation, preserving API-017 upload security.
- [ ] Retire API R2 access/secret environment reads after controlled cutover.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-DATABASE-007` (must be architect-accepted **Complete**)
- `ARCH-043-SHARED-004` (must be architect-accepted **Complete**)
- `ARCH-043-API-001` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-GATEWAY-002`

## Acceptance Criteria

- [ ] Woo signed upload and finalisation still valid across rotation.
- [ ] Read-purpose credentials cannot sign writes and tenant isolation holds.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] API-017 presigned-upload unit/integration tests
- [ ] Cross-service AAD compatibility tests
- [ ] Typecheck/lint/build
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
