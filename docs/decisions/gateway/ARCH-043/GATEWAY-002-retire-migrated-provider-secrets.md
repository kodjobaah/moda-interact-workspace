---
id: ARCH-043-GATEWAY-002
architecture_id: ARCH-043
title: Retire superseded provider secret wiring after database cutover
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-ADMIN-007", "ARCH-043-ADMIN-008", "ARCH-043-ADMIN-009", "ARCH-043-ADMIN-010", "ARCH-043-BACKGROUND-005", "ARCH-043-BACKGROUND-006", "ARCH-043-BACKGROUND-007", "ARCH-043-API-002", "ARCH-043-API-003"]
enables: ["ARCH-043-SYSTEM-TEST-002"]
created: 2026-10-17
updated: 2026-10-17
---

# Retire superseded provider secret wiring after database cutover

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-gateway` / `moda_gateway`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Remove redundant R2, speech, outbound WhatsApp and Woo billing secret assignments only for accepted database-backed hosted readers.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Audit both Render Blueprints/secret groups against actual service readers and ARCH-039 least-privilege matrix.
- Remove obsolete secrets for API/Background where all operations use encrypted DB, retain Shopify R2 signing secrets.
- Ensure ARCH-039 root keyring remains externally injected only into authorised decryptors/writers.
- Document staged credential cutover, recovery, token rotation and rollback.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Do not remove ingress bootstrap META_APP_SECRET or WHATSAPP_VERIFY_TOKEN, COMMERCE_CONNECTION_KEYS_JSON, ACTIVE_KEY_ID, COMMAND_HMAC_KEY or WOO_BILLING_ENVIRONMENT.
- Never inject hosted keyring into Shopify merchant app, browser or WordPress plugin.
- No secret plaintext in Render YAML or committed docs.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Audit both Render Blueprints/secret groups against actual service readers and ARCH-039 least-privilege matrix.
- [ ] Remove obsolete secrets for API/Background where all operations use encrypted DB, retain Shopify R2 signing secrets.
- [ ] Ensure ARCH-039 root keyring remains externally injected only into authorised decryptors/writers.
- [ ] Document staged credential cutover, recovery, token rotation and rollback.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-ADMIN-007` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-008` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-009` (must be architect-accepted **Complete**)
- `ARCH-043-ADMIN-010` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-005` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-006` (must be architect-accepted **Complete**)
- `ARCH-043-BACKGROUND-007` (must be architect-accepted **Complete**)
- `ARCH-043-API-002` (must be architect-accepted **Complete**)
- `ARCH-043-API-003` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Service-to-secret distribution follows approved reader/writer matrix.
- [ ] All supported credential operations work after redundant vars are removed and fail if database cred revoked.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Blueprint positive and negative validation
- [ ] Secret-reference least-privilege matrix tests
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
