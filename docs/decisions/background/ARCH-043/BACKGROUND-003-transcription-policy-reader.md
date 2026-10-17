---
id: ARCH-043-BACKGROUND-003
architecture_id: ARCH-043
title: Use database speech provider/model selection
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 28
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-043-DATABASE-003"]
enables: ["ARCH-043-BACKGROUND-006", "ARCH-043-GATEWAY-001"]
created: 2026-10-17
updated: 2026-10-17
---

# Use database speech provider/model selection

## Architecture

- Architecture ID: `ARCH-043`
- Architecture document: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`
- Coordinator: `moda_architect`
- Repository / logical owner: `moda-interact-background` / `moda_background`
- Definition lifecycle: **defined but not materialised**; no Git branch, developer worktree or remote commit exists by virtue of this portable definition.

## Objective

Replace WHATSAPP_TRANSCRIPTION_PROVIDER and Groq/OpenAI transcription model environment reads with the typed policy.

## Context

Implements the environment-variable audit of `moda-interact-workspace(20261017-111156).zip` in its owning repository. Follow the accepted ARCH-014 runtime controls, ARCH-039 credential security and current code behavior. Existing task and source implementations are authoritative over assumptions in this definition; return material cross-repository discrepancies to `moda_architect`.

## Scope

- Update speech-transcription.service.ts and provider adapters to read an environment-qualified validated cached policy.
- Use one immutable provider/model selection per job to prevent mid-transcription switch.
- Preserve existing externally supplied provider tokens until ARCH-043-BACKGROUND-006.

## Out of Scope

- Unrelated business workflows, credential root secrets and unrelated environment variables.
- Modifying other repositories or any `docs/decisions/**/_index.md`.
- Implementing enabled follow-on tasks or merging/pushing main.

## Requirements

- No silent Groq/OpenAI provider fallback when selected configuration is bad.
- No DB lookup for every media request and no live reconfiguration during job.
- Failures remain structured and bounded, preserving message/queue retries.
- Use the canonical launcher-resolved dedicated parent and implementation task worktrees; record preparation/isolation evidence in the Completion Report.
- Retain bootstrap dependency-free configuration (`DATABASE_URL`, Redis, deployment identity, auth/webhook roots, OTEL transport, ARCH-039 encryption/HMAC roots) outside the application database.

## Work Items

- [ ] Update speech-transcription.service.ts and provider adapters to read an environment-qualified validated cached policy.
- [ ] Use one immutable provider/model selection per job to prevent mid-transcription switch.
- [ ] Preserve existing externally supplied provider tokens until ARCH-043-BACKGROUND-006.
- [ ] Add focused positive/negative tests and update only task-owned documentation required by the implementation.
- [ ] Record launcher worktree isolation, start-of-attempt synchronization, changed files and validation evidence.

## Interfaces / Contracts

- PostgreSQL/schema contracts owned by `moda_database` and published Shared contracts, where specified in Dependencies.
- Consumer domain validates authorisation/environment/purpose; never infer a new shared protocol locally.

## Dependencies

- `ARCH-043-DATABASE-003` (must be architect-accepted **Complete**)

## Enables

- `ARCH-043-BACKGROUND-006`
- `ARCH-043-GATEWAY-001`

## Acceptance Criteria

- [ ] Config changes converge across Background replicas.
- [ ] Invalid model/provider does not leak tokens or trigger a second provider.
- [ ] All required dependencies were Complete before this task was claimed.
- [ ] No unrelated sources, other agents’ tasks or `_index.md` files modified.

## Validation

- [ ] Focused speech/WhatsApp media tests
- [ ] Config version/refresh tests
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
