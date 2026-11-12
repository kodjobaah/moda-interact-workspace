---
id: ARCH-070-BACKGROUND-002
architecture_id: ARCH-070
title: Respect terminal failures for the same inbound version
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-12T12:40:04Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Respect terminal failures for the same inbound version

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Respect terminal failures for the same inbound version without relaxing existing production security or lifecycle guarantees.

## Context

A nonretryable INVALID_FINAL failure was repeatedly requeued by the 30-second pending-turn repair, repeating model/tool work for the same inbound version.

## Scope

src/services/conversation-turn-processor.service.ts; src/services/conversation-ai-delay/pending-turn-repair.ts; directly related lifecycle unit/integration tests. No edits to commerce/host.ts.

## Out of Scope

Other task's owned modules, Shared/MCP implementation, schema changes, provider/model switching, credentials, infrastructure, old-message replay, unrelated refactors and unsolicited customer sends.

## Requirements

Persist or derive a durable version-scoped terminal condition using existing state contracts; repair must not requeue the same terminal inbound version. A genuinely newer inbound remains processable. Retryable/transient failures retain bounded recovery; crashes and in-flight claims remain recoverable. Preserve locking, idempotency, delivery and user-facing failure behavior. Do not add a blanket skip or process-local suppression. Return schema needs to architect rather than modifying database ownership.

## Work Items

- [ ] Establish exact source/fixture cause and preserve a failing regression.
- [ ] Implement only the owned correction.
- [ ] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None. The two ARCH-070 tasks are independently executable on disjoint modules; final developer integration must preserve both changes.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [ ] Requirements demonstrated with deterministic positive and negative regression tests.
- [ ] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [ ] No duplicate delivery, live test send, secret logging or unrelated changes.
- [ ] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [ ] Deterministic repeated repair cycles after nonretryable failure cause no new model/tool/send; newer inbound progresses; retryable failure and crash recovery regressions; relevant PostgreSQL lifecycle tests if durable state is changed, typecheck, lint and required repository CI.
- [ ] Diff hygiene and exact changed-file scope review.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

Existing runtime evidence needs corroboration in source and fixtures.

### Unresolved Issues

None known beyond investigation.

### Architectural Concerns

Return contract or schema gaps before implementing outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
