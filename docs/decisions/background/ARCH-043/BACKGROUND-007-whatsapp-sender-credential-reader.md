---
id: ARCH-043-BACKGROUND-007
architecture_id: ARCH-043
title: Decrypt database WhatsApp outbound sender credential
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-DATABASE-009", "ARCH-043-SHARED-004"]
enables: ["ARCH-043-GATEWAY-002"]
created: 2026-10-17
updated: 2026-10-17
---

# Decrypt database WhatsApp outbound sender credential

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-background` / `moda_background`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Replace Background WHATSAPP_ACCESS_TOKEN / PHONE_NUMBER_ID / BUSINESS_ACCOUNT_ID outbound reads with the database sender config.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Update outbound WhatsApp send and media-read adapters to resolve active sender identity/token safely.
- Use approved encrypted credential reader, revisioned bounded cache and consistent per-send account snapshot.
- Preserve webhook ingress META_APP_SECRET and WHATSAPP_VERIFY_TOKEN untouched.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- No token lookup for every media chunk; no cross-tenant/provider account confusion.
- Fail closed on disabled sender/invalid token without duplicate sending or charging.
- WhatsApp provider status/cancellation semantics remain ARCH-028 compliant.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Update outbound WhatsApp send and media-read adapters to resolve active sender identity/token safely.
- [ ] Use approved encrypted credential reader, revisioned bounded cache and consistent per-send account snapshot.
- [ ] Preserve webhook ingress META_APP_SECRET and WHATSAPP_VERIFY_TOKEN untouched.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-DATABASE-009` (must be architect-accepted **Complete**)
- `ARCH-043-SHARED-004` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-GATEWAY-002`

## Acceptance Criteria

- [ ] Outbound send/media read use same authorised account snapshot.
- [ ] Rotation, retry, missing token and wrong environment negative tests pass.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Focused outbound/Meta provider regressions
- [ ] Credential lifecycle Postgres tests
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
