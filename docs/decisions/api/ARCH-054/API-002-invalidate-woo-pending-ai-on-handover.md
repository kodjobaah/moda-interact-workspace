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
status: review
priority: 30
executor: copilot
claimed_at: 2026-10-31T21:55:35Z
attempt: 2
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

- [x] Add atomic pending invalidation to control transition transaction.
- [x] Test pending AI=>HUMAN, HUMAN=>AI, duplicate control request, concurrent inbound/claim, stale queued job after control toggles, existing 409, and HUMAN text dispatch independence.


## Interfaces / Contracts

No new public control request field. Existing `controlRevision` and `expectedControlRevision` remain canonical. Internal Prisma fields owned by DATABASE-001.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [x] One durable control transition atomically invalidates old pending state, across workers; no stale AI reply after final admission fence.
- [x] Existing Woo tenant auth and human-message behaviour remain unchanged; focused integration tests pass.


## Validation

- [x] Focused API conversation-control unit/PostgreSQL tests using declared script; changed-file lint/build/typecheck per package.json; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for Review

### Files Changed

Implementation: `src/merchant/conversations/control/service.ts` and `tests/integration/merchant/conversations/control.service.postgres.test.ts`.
Parent task file: `docs/decisions/api/ARCH-054/API-002-invalidate-woo-pending-ai-on-handover.md`.

### Work Completed

- Confirmed the previous blocker is resolved: the prepared database submodule is at `7c377282aa5819b3008b7d7f3018f44f4161523e`; its Prisma model includes the three pending-AI columns and its migrations contain `20261031170000_arch054_merchant_ai_response_delay`.
- Extended the locked Woo control read to capture the current `inboundVersion`; the successful CAS update now changes control mode/revision and, in that same transaction, clears `pendingTurnStartedAt`, all three pending-AI fields, and both processing-claim fields, while advancing `lastProcessedVersion` to that locked inbound version.
- Same-mode requests remain read-only no-ops, stale expected revisions remain 409 conflicts, and the existing audit event, Woo authentication, suspension checks, and recovery/shop ownership locks are unchanged.
- Extended the disposable PostgreSQL control test for AI→HUMAN and HUMAN→AI invalidation, no-op behavior, stale revision, and takeover waiting for an in-flight inbound/claim transaction before consuming its new version and clearing pending work. The old queued job is fenced because its pending metadata is cleared and its captured control revision is no longer current.
- Existing human-send PostgreSQL coverage passed, confirming HUMAN command admission remains independent of the AI delay fields.

### Validation Results

- `npm run test:arch040-conversation-control:postgres`: passed; fresh migrations including ARCH-054 applied and the PostgreSQL concurrency/control test passed.
- `node --import tsx --test tests/unit/merchant/conversations/control/*.test.ts`: passed, 6/6.
- `npm run test:arch040-human-send:postgres`: passed, 4/4; immediate HUMAN command behavior remains unchanged.
- `npm run build`: passed.
- `npm run typecheck`: passed.
- `npx eslint src/merchant/conversations/control/service.ts tests/integration/merchant/conversations/control.service.postgres.test.ts --max-warnings=0`: passed.
- `npm run lint`: repository-wide lint reports one error in untouched `src/merchant/support/routes.ts:75` (`no-empty`); no task-changed file is implicated.
- `git diff --check`: passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

No architectural deviation. The queued AI job cannot be recalled, but it is no longer authorized after a control transition: the transition clears the pending turn and the existing worker's original control-revision fence rejects stale work before final provider admission. A provider operation already dispatched remains non-recallable as specified by ARCH-054. Repository-wide lint remains blocked only by the unrelated existing `no-empty` diagnostic noted above.

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
  parent prepared head: `08c184a1a9c8356488d90b166c58a0277c1524e9`
  implementation prepared head: `25fb95062355b15cbadc954db1164fd94fc2cfa7`

Recursive implementation submodules (launcher packet):
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded database submodule commit: `7c377282aa5819b3008b7d7f3018f44f4161523e`

Publication:
  implementation task branch commit: `954fd95`
  parent task branch commit: completion report commit
  both task branches pushed: yes


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
