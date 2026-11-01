---
id: ARCH-043-SYSTEM-TEST-002
architecture_id: ARCH-043
title: Certify encrypted provider credential cutover
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-GATEWAY-002"]
enables: []
created: 2026-10-17
updated: 2026-10-17
---

# Certify encrypted provider credential cutover

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-system-test` / `moda_system_test`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Validate encrypted database credential creation, rotation, revocation and strict key distribution across hosted services.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Provision test R2, transcription, WhatsApp outbound and Woo billing credentials via protected Admin flows.
- Exercise authorised API/Background readers, cross-service AAD vectors, rotation, wrong key/env/purpose, revocation and fail-closed operation.
- Assert Shopify/WordPress/browser never receive credential keyring or provider plaintext; verify ingress bootstrap unchanged.
- Check independent observability/log transport on credential failures and safe Render secret retirement.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- System testing is terminal and does not gate any implementation task.
- Use test provider fakes or approved disposable infrastructure; no live paid provider traffic.
- Report artifacts and secret-free output.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Provision test R2, transcription, WhatsApp outbound and Woo billing credentials via protected Admin flows.
- [ ] Exercise authorised API/Background readers, cross-service AAD vectors, rotation, wrong key/env/purpose, revocation and fail-closed operation.
- [ ] Assert Shopify/WordPress/browser never receive credential keyring or provider plaintext; verify ingress bootstrap unchanged.
- [ ] Check independent observability/log transport on credential failures and safe Render secret retirement.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-GATEWAY-002` (must be architect-accepted **Complete**)

## Enables

None

## Acceptance Criteria

- [ ] Valid encrypted creds work end-to-end and tampered/foreign/revoked fail.
- [ ] Legacy environment values cannot silently supersede DB credential after cutover.
- [ ] No root keys or payload secrets leak into HTTP, logs, queues or client.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Disposable Postgres and fake external providers
- [ ] Secret scanning & auth/tenant negative tests
- [ ] Versioned integrated evidence and git diff --check

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
