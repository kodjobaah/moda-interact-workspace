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
status: blocked
priority: 30
executor: copilot
claimed_at: 2026-10-31T21:08:15Z
attempt: 1
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

Blocked

### Files Changed

Parent task file only: `docs/decisions/api/ARCH-054/API-002-invalidate-woo-pending-ai-on-handover.md`.
No API source or test files changed because the required database contract is absent from the pinned submodule.

### Work Completed

- Read the complete task and ARCH-054 architecture contract; the task's Architect Review is Pending and contains no requested changes.
- Verified the implementation worktree's `database` submodule is at `b87e460e86de2044477f8c96b5c1c42e722de8f0`.
- Confirmed `database/prisma/schema.prisma` in that commit has `pendingTurnStartedAt`, `processingInboundVersion`, and `processingStartedAt`, but lacks `pendingAiNotBeforeAt`, `pendingAiControlRevision`, and `pendingAiDelayMinutes`.
- Confirmed the pinned `database/prisma/migrations` tree does not contain `20261031170000_arch054_merchant_ai_response_delay`.
- The required API PostgreSQL script migrates from this pinned submodule, so it cannot validate atomic invalidation of the ARCH-054 fields. Updating the schema, migration, or database gitlink is outside this API task's authority.

### Validation Results

Not run: no implementation was made because the required DATABASE-001 schema/migration contract is missing from the task's pinned submodule. The declared focused command is `npm run test:arch040-conversation-control:postgres`; it provisions a fresh database from that submodule and therefore cannot exercise the required pending-AI fields. `git diff --check` on the task report passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Blocked pending `moda_architect` resolution: ARCH-054-DATABASE-001 is reported complete, but the API task's database submodule pin does not contain the three pending-AI columns or the ARCH-054 migration. Please coordinate the correct database revision/submodule update or provide an approved API contract and PostgreSQL validation fixture. Do not work around this by locally duplicating database schema ownership or relying on unvalidated raw SQL. Acceptance criteria and Work Items remain incomplete.

### Worktree and Git Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-API-002`
  parent branch: `task/ARCH-054-API-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-API-002`
  implementation branch: `task/ARCH-054-API-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization (launcher packet):
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current
  parent claim/sync head: `12450c44ed20b8c30150117e706b7bd495e0308c`
  implementation initial head: `e59aba1939531e250b7cefc3c1c3e21b13cda3af`

Recursive implementation submodules (launcher packet):
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded database submodule commit: `b87e460e86de2044477f8c96b5c1c42e722de8f0`


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
