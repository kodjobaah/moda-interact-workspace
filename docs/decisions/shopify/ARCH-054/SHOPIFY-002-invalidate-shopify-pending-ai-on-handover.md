---
id: ARCH-054-SHOPIFY-002
architecture_id: ARCH-054
title: Invalidate pending AI inside Shopify take-over/resume action
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-054-DATABASE-001
enables:
  - ARCH-054-BACKGROUND-002
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SHOPIFY-002: Invalidate pending AI inside Shopify take-over/resume action


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Apply the same atomic pending-turn and processing-lease invalidation to authenticated Shopify control changes.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Modify `app/services/recoveries/recovery-human-commands.server.ts` only plus existing Shopify control tests. Keep the existing recovery-detail route/UI and `targetMode` / `expectedControlRevision` interface.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Under the existing authenticated shop/recovery row locks, on successful controlMode change (AI->HUMAN or HUMAN->AI) increment controlRevision, clear `pendingTurnStartedAt`, `pendingAiNotBeforeAt`, `pendingAiControlRevision`, `pendingAiDelayMinutes`, `processingInboundVersion`, `processingStartedAt`, and advance `lastProcessedVersion` to current inboundVersion in the same DB transaction. Write ConversationControlEvent within that transaction.
- Retain all existing entitlement, restriction, terminal-recovery and stale-control checks. Idempotent/no-op transitions and concurrent conflicting requests cannot erase newly started turns or reuse previous AI revision. Human composer and durable command dispatch do not consult aiResponseDelayMinutes.
- The worker final provider admission must still fence on the original revision. Do not claim to recall already submitted Meta traffic.


## Work Items

- [ ] Extend the existing Shopify control service; add transaction-level race tests and rollback assertions.
- [ ] Verify no replay after HUMAN->AI, no pending AI for HUMAN, no human dispatch delay and no regression to existing controls.


## Interfaces / Contracts

Existing ARCH-040 control DTO and `controlRevision` are unchanged; DATABASE-001 owns newly cleared nullable fields.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [ ] Shopify takeover suppresses a waiting or in-flight AI turn whose dispatch has not passed final admission; Resume AI cannot revive an old queued job.
- [ ] Authenticated merchant human send remains immediate subject to normal guards.


## Validation

- [ ] Existing Shopify human-command/control service tests; Prisma transaction integration test; changed-file lint/typecheck/build per package.json; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
