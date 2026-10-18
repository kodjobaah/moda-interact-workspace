---
id: ARCH-043-GATEWAY-001
architecture_id: ARCH-043
title: Remove superseded non-secret Render environment declarations
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-ADMIN-001", "ARCH-043-ADMIN-002", "ARCH-043-ADMIN-003", "ARCH-043-ADMIN-004", "ARCH-043-ADMIN-005", "ARCH-043-ADMIN-006", "ARCH-043-BACKGROUND-001", "ARCH-043-BACKGROUND-002", "ARCH-043-BACKGROUND-003", "ARCH-043-BACKGROUND-004", "ARCH-043-API-001", "ARCH-043-SHOPIFY-001", "ARCH-043-COMMERCE-001"]
enables: ["ARCH-043-SYSTEM-TEST-001"]
created: 2026-10-17
updated: 2026-10-17
---

# Remove superseded non-secret Render environment declarations

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-gateway` / `moda_gateway`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Remove configuration keys from test and production Render Blueprints only after their database-backed consumers and Admin editors are accepted.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Inspect render.test.yaml, render.production.yaml, tests/validate-render-blueprints.sh and related deployment docs.
- Remove only migrated Woo coupon, Knowledge policy/location, translation provider/model, transcription provider/model, preview budget and Grafana navigation keys actually present.
- Retain external database/cache/OAuth/security/telemetry/bootstrap and Shopify R2 credentials.
- Document deployment sequence, rollback plan and environment isolation.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Do not remove required external secret groups or infrastructure keys.
- Render production/test Blueprint differences are reviewed explicitly.
- No code or application repo edits from Gateway task.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Inspect render.test.yaml, render.production.yaml, tests/validate-render-blueprints.sh and related deployment docs.
- [ ] Remove only migrated Woo coupon, Knowledge policy/location, translation provider/model, transcription provider/model, preview budget and Grafana navigation keys actually present.
- [ ] Retain external database/cache/OAuth/security/telemetry/bootstrap and Shopify R2 credentials.
- [ ] Document deployment sequence, rollback plan and environment isolation.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-ADMIN-001` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-002` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-003` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-004` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-005` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-006` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-001` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-002` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-003` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-004` (must be architect-accepted **Complete**)
- `ARCH-043-API-001` (must be architect-accepted **Complete**)
- `ARCH-043-SHOPIFY-001` (must be architect-accepted **Complete**)
- `ARCH-043-COMMERCE-001` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both Blueprint variants validate and no migrated non-secret key is still referenced as runtime authority.
- [ ] Removing keys does not block startup on a canonical deployment.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Render Blueprint validators including negative suites
- [ ] Deployment dry-run/static lint
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
