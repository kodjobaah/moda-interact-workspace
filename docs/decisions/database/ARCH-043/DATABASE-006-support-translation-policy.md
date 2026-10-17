---
id: ARCH-043-DATABASE-006
architecture_id: ARCH-043
title: Persist support-message translation routing policy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-043-ADMIN-006", "ARCH-043-BACKGROUND-004"]
created: 2026-10-17
updated: 2026-10-17
---

# Persist support-message translation routing policy

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-database` / `moda_database`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Create an explicit database authority only for the Background support-message translation workflow rather than reusing unrelated Commerce translation model rows.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Inventory the actual provider/model reads in Background translation-batch-assembly.service.ts and providers/translation.provider.ts and map their distinct workload.
- Add narrowly scoped, versioned support-translation provider/model configuration only where existing CommerceTranslationModelConfiguration cannot represent the workflow safely.
- Record provider/model validation, revision history and data migration while retaining existing translation operational cadence in BackgroundRuntimeConfig.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- Do not silently change Commerce product/pricing translation semantics.
- If existing published model/credential records already provide exact same scope, reuse them and document proof rather than adding a duplicate.
- Provider credentials are separate and may remain external until a separately accepted security migration.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Inventory the actual provider/model reads in Background translation-batch-assembly.service.ts and providers/translation.provider.ts and map their distinct workload.
- [ ] Add narrowly scoped, versioned support-translation provider/model configuration only where existing CommerceTranslationModelConfiguration cannot represent the workflow safely.
- [ ] Record provider/model validation, revision history and data migration while retaining existing translation operational cadence in BackgroundRuntimeConfig.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

None

## Enables

- `ARCH-043-ADMIN-006`
- `ARCH-043-BACKGROUND-004`

## Acceptance Criteria

- [ ] One durable authority for support-message provider/model, with no parallel env override after cutover.
- [ ] Existing translation retries and batching untouched.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Prisma validate (if schema changed)
- [ ] Postgres version/selection tests
- [ ] Background contract regression evidence
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
