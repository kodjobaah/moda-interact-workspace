---
id: ARCH-052-SHARED-007
architecture_id: ARCH-052
title: Add outreach entrypoint to the existing Commerce runner
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-007: Add outreach entrypoint to the existing Commerce runner

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. Portable canonical definition: **defined but not materialised**; no developer worktree, branch, commit or push has occurred.

## Objective

**Superseded without implementation.** BACKGROUND-010 owns one focused InitialOutreachOfferAgent using CommerceModelInvoker; shared conversation runner remains unchanged.

## Context

`runCommerceTurn` in `src/commerce/runner/index.ts` currently requires `CommerceTurnIdentity`, `CommerceConversationGrant`, a conversation-specific `finalResponse`, and a live inbound processing lease enforced by Background host. Passing a fake inbound version would violate that invariant. Reuse shared tool-loop/model-step/runtime/authorization rather than copying it into Background.

Source evidence: `moda-interact-workspace(20261029-080732).zip`. This task changes documentation in the parent only until materialised by the developer.

## Scope

No implementation. Do not claim, materialise, modify repository code or attempt publication under this task.

## Out of Scope

- No new database tables/columns, duplicate recovery-offer engine, unrelated UI, provider writes, or changes outside this repository and its own task report.

## Requirements

The replacement tasks and parent architecture are authoritative. Historical wording in this superseded task is retained solely for audit; it must not govern an implementation.

## Work Items

- [x] Marked superseded in the architecture plan. No code executed.

## Interfaces / Contracts

None — see replacement tasks.

## Dependencies

None — task is superseded.

## Enables

None — task is superseded.

## Acceptance Criteria

- [x] Superseded without implementation. The replacement tasks are explicitly identified.

## Validation

Not applicable; no implementation permitted.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, fill the Completion Report, change the task status to `review`, return the parent task report and implementation branch to `moda_architect` and **STOP**. Do not start dependent tasks, merge, push `main`, or alter architecture/domain indexes.

## Implementation Notes

No implementation. Replacement: BACKGROUND-010 owns one focused InitialOutreachOfferAgent using CommerceModelInvoker; shared conversation runner remains unchanged.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Implementation must confirm package versions and the current task worktree baseline.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes for this task reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
