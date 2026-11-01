---
id: ARCH-054-BACKGROUND-001
architecture_id: ARCH-054
title: Atomically freeze AI delay when inbound text or voice opens a turn
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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


# ARCH-054-BACKGROUND-001: Atomically freeze AI delay when inbound text or voice opens a turn


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Capture one source-backed deadline and control revision for the first processable customer inbound of each AI-controlled recovery turn.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `src/services/conversation-ai-delay/pending-turn-deadline.ts` (pure clock/boundary helper) and `src/services/conversation-ai-delay/pending-turn-repository.ts` (database transaction helper). Modify `src/services/conversation.service.ts` and `src/services/inbound-whatsapp-audio.service.ts`; update typed turn state projections and focused unit/PostgreSQL integration tests. No standalone worker/queue or UI changes.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Read current shop from `Conversation.checkoutRecoveryId -> CheckoutRecovery.shopId` inside the existing short transaction; do not use nullable `Conversation.shopId` or sender phone as authority. Read `ShopSettings.aiResponseDelayMinutes` only for first AI pending opening; a valid shop with no settings row has effective value 0. Reject corrupt/out-of-range persisted settings, do not silently coerce.
- When first processable text commits with `controlMode=AI` and no pending turn: set `pendingTurnStartedAt=receivedAt`, `pendingAiNotBeforeAt=receivedAt+60_000*minutes`, `pendingAiDelayMinutes=minutes`, `pendingAiControlRevision=current controlRevision`; atomically persist inbound message and version. Use row lock/CAS to serialize two first messages; a loser must join the winner, not overwrite.
- Audio is processable on successful `transcriptionCompletedAt`, NOT on raw audio receipt. In its existing transcription-completion transaction, use that `now` for pending-start and deadline, and the same helper. Duplicated/stale/failed transcriptions must not open/restart a turn.
- Additional text or completed voice fragments increment inboundVersion without changing the original three pending-AI fields or `pendingTurnStartedAt` regardless of settings updates. On HUMAN mode, persist inbound transcript and advance processed watermark without creating a pending AI deadline or scheduling AI; no old human messages are replayed after Resume AI.
- For non-recovery/standalone conversations, retain current non-merchant delay behaviour. No network or queue publish inside the transaction; enqueue only after commit and use existing versioned job identity. Preserve 3s/10s settle config untouched.
- If duplicate webhook or retries occur, preserve the first deadline. On DB/persistence error, log original exception through Shared and propagate; no unobserved catch-and-continue.


## Work Items

- [ ] Implement exact pure deadline computation and transaction helper (one owner, reusable for text/audio).
- [ ] Modify first-text and audio completion paths; update `ConversationTurnState` projection with pending triple and original `controlMode`/`controlRevision`.
- [ ] Add tests for 0,1,7,30, duplicate/out-of-order, concurrent first texts, mixed text/audio, settings changed mid-turn, HUMAN-mode inbound, tenant ownership and actual DB rollback.


## Interfaces / Contracts

Internal pure `computePendingAiNotBeforeAt({pendingStartedAt:Date,delayMinutes:0..30}):Date` with no new public Shared type. Database writes use prisma transaction and contract from DATABASE-001. The observed job remains `{ conversationId, observedVersion }` using existing `conversation-turn__<id>__<version>` jobId.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [ ] Only one deadline and captured revision per pending turn; simultaneous first inbound races do not create two anchors.
- [ ] No AI deadline for HUMAN inbound, failed audio or unrelated nonrecovery; normal inbound persistence and moderation remain intact.
- [ ] No duplicate Meta send or extra credit caused by inbound retry; real DB transaction validates atomicity.


## Validation

- [ ] `npx vitest run tests/unit/services/conversation.service.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts`; `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts`; changed-file lint/typecheck/build per available scripts; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Do not perform a network call while a DB transaction is open. Source original cause and provider diagnostic must be logged/redacted, never rewritten as a guessed message. Existing inbound audio service presently sets pendingTurnStartedAt to transcription-completion now: extend it, do not create a second audio dispatcher.


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
