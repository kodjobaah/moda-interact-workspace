---
id: ARCH-054-API-002
architecture_id: ARCH-054
title: Invalidate pending AI when Woo merchant changes human control
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
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


# ARCH-054-API-002: Invalidate pending AI when Woo merchant changes human control


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Fence pending/delayed AI turns atomically inside the existing authenticated WooCommerce HUMAN/AI control transaction.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Modify `src/merchant/conversations/control/service.ts` only plus its existing focused tests; do not change request/response wire schema `ARCH-040` control command or introduce another control endpoint.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Retain `SELECT ... FOR UPDATE` recovery/shop/installation auth, `expectedControlRevision` CAS, `ConversationControlEvent`, and status/suspension rules. On a *successful* AI->HUMAN or HUMAN->AI transition, in the same SQL transaction as `controlRevision += 1` clear `pendingTurnStartedAt`, `pendingAiNotBeforeAt`, `pendingAiControlRevision`, `pendingAiDelayMinutes`, `processingInboundVersion`, `processingStartedAt`, and set `lastProcessedVersion` to the current `inboundVersion`; do not remove transcript or alter provider send receipts.
- No-op repeated target-mode request must not increment revision, reopen pending AI, or race. Stale expected revision must return existing 409. The old worker must be stopped by original revision fence at final provider admission; cannot recall previously dispatched Meta operation.
- Existing HUMAN send command admission and dispatch must remain immediate (no delay field check). Do not alter Meta window, consent, moderation or human sending entitlements.


## Work Items

- [ ] Add atomic pending invalidation to control transition transaction.
- [ ] Test pending AI=>HUMAN, HUMAN=>AI, duplicate control request, concurrent inbound/claim, stale queued job after control toggles, existing 409, and HUMAN text dispatch independence.


## Interfaces / Contracts

No new public control request field. Existing `controlRevision` and `expectedControlRevision` remain canonical. Internal Prisma fields owned by DATABASE-001.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [ ] One durable control transition atomically invalidates old pending state, across workers; no stale AI reply after final admission fence.
- [ ] Existing Woo tenant auth and human-message behaviour remain unchanged; focused integration tests pass.


## Validation

- [ ] Focused API conversation-control unit/PostgreSQL tests using declared script; changed-file lint/build/typecheck per package.json; `git diff --check`.


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
