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
status: review
priority: 30
executor: copilot
claimed_at: 2026-10-31T22:53:09Z
attempt: 1
depends_on:
  - ARCH-054-DATABASE-001
enables:
  - ARCH-054-BACKGROUND-002
created: 2026-10-31
updated: 2026-11-02
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

- [x] Implement exact pure deadline computation and transaction helper (one owner, reusable for text/audio).
- [x] Modify first-text and audio completion paths; update `ConversationTurnState` projection with pending triple and original `controlMode`/`controlRevision`.
- [x] Add tests for 0,1,7,30, duplicate/out-of-order, concurrent first texts, mixed text/audio, settings changed mid-turn, HUMAN-mode inbound, tenant ownership and actual DB rollback.


## Interfaces / Contracts

Internal pure `computePendingAiNotBeforeAt({pendingStartedAt:Date,delayMinutes:0..30}):Date` with no new public Shared type. Database writes use prisma transaction and contract from DATABASE-001. The observed job remains `{ conversationId, observedVersion }` using existing `conversation-turn__<id>__<version>` jobId.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [x] Only one deadline and captured revision per pending turn; simultaneous first inbound races do not create two anchors.
- [x] No AI deadline for HUMAN inbound, failed audio or unrelated nonrecovery; normal inbound persistence and moderation remain intact.
- [x] No duplicate Meta send or extra credit caused by inbound retry; real DB transaction validates atomicity.


## Validation

- [x] `npx vitest run tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts tests/unit/services/conversation.service.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts` — 43 tests passed.
- [x] `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts` — passed, 1 file / 4 tests (successful run from the canonical implementation task worktree after Colima became available; user-confirmed on 2026-11-02).
- [x] `npm run build` — passed, including Prisma Client generation and TypeScript build.
- [x] Changed-file ESLint — passed.
- [x] `git diff --check` — passed.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Do not perform a network call while a DB transaction is open. Source original cause and provider diagnostic must be logged/redacted, never rewritten as a guessed message. Existing inbound audio service presently sets pendingTurnStartedAt to transcription-completion now: extend it, do not create a second audio dispatcher.


## Completion Report

### Status

Ready for Review: implementation, acceptance criteria and required validation are complete. The PostgreSQL integration suite passed in the user-confirmed run; follow-up agent reruns were interrupted during disposable database migration startup before Vitest began.

### Files Changed

- `src/services/conversation-ai-delay/pending-turn-deadline.ts`
- `src/services/conversation-ai-delay/pending-turn-repository.ts`
- `src/services/conversation.service.ts`
- `src/services/inbound-whatsapp-audio.service.ts`
- `src/services/whatsapp-inbound-processing.service.ts`
- `tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts`
- `tests/unit/services/conversation.service.test.ts`
- `tests/unit/services/inbound-whatsapp-audio.service.test.ts`
- `tests/integration/conversation-turn-scheduling.integration.test.ts`

### Work Completed

- Added pure, range-checked deadline computation and a shared row-locked transaction helper used by text receipt and successful audio transcription completion.
- Captured merchant delay and current recovery control revision only when opening a pending AI recovery turn, using `CheckoutRecovery.shopId`; missing settings default to zero and corrupt persisted values fail without coercion.
- Preserved the original pending timestamp/deadline/revision for later fragments. HUMAN inbound advances the processed watermark and clears pending/processing state; post-commit routing does not enqueue HUMAN-owned turns.
- Added Shared-logger persistence failure handling that propagates the original exception; preserved standalone conversation timing and existing versioned queue identity.
- Added focused unit coverage and PostgreSQL integration cases for concurrent first text, settings changes during a turn, and transaction rollback.
- Corrected the recovery-conversation integration fixture with `controlChangedAt` alongside `controlRevision`, satisfying the persisted control-state database constraint.

### Validation Results

- `npx vitest run tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts tests/unit/services/conversation.service.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts` — passed, 3 files / 43 tests, rerun on 2026-11-02 after mainline synchronization.
- `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts` — passed, 1 file / 4 tests in the user-confirmed run from the canonical implementation task worktree on 2026-11-02.
- `npm run build` — passed after mainline synchronization; Prisma Client generation and TypeScript build completed.
- `npx eslint tests/integration/conversation-turn-scheduling.integration.test.ts` — passed.
- `git diff --check` — passed.
- Two subsequent agent reruns exited before Vitest: the `prisma migrate deploy` child received `SIGTERM` while applying migrations to disposable PostgreSQL databases. No integration assertions ran in those attempts. The active Docker context was `colima`; `docker info` succeeded and reported server 29.5.2. These interrupted reruns did not report test assertion failures.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

- The successful four-test PostgreSQL run is user-confirmed. This agent could not reproduce it because two retries were terminated during Prisma migration deployment before Vitest started; the disposable-database migration startup interruption is recorded for review.

### Worktree and Git Evidence

- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-BACKGROUND-001`
  - parent branch: `task/ARCH-054-BACKGROUND-001`
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-BACKGROUND-001`
  - implementation branch: `task/ARCH-054-BACKGROUND-001`
  - shared workspace checkout switched/mutated for task work: no
  - shared implementation checkout switched/mutated for task work: no
  - another task worktree reused: no
- Start-of-attempt synchronization from launcher packet:
  - parent remote task branch fast-forwarded: not-needed
  - parent `origin/main` incorporated: yes, merge commit `89c9890ba95d757f49c5c5e5e52a5077f10d825a`
  - implementation remote task branch fast-forwarded: not-needed; it matched the remote task ref before the new commit
  - implementation `origin/main` incorporated: yes, merge commit `b0ea947ee392b2741bf8de3683e458208a83fa25`
  - parent pre-claim head: `61a62c5e89eb8b749384de5024f60942aca3a34d`
  - implementation initial head: `b7aa719240bf7e0d793db23dd956c4437c904ded`
  - parent claim commit: `2bae65630708686cffe5bc77be8789506d8f54c4` (pushed)
- Recursive implementation submodules:
  - `git submodule sync --recursive`: passed
  - `git submodule update --init --recursive`: passed
  - recorded database submodule commit: `7c377282aa5819b3008b7d7f3018f44f4161523e`
- Implementation baseline commit: `7bb69d7bb959f96bc0b96ed6e381ac77ecfaf121` (already published before this continuation).
- Fixture correction commit: `588cf39c856c2a9d6e1faf157d2dc1642f9aa1bf`.
- Current implementation task branch head, including the origin/main merge: `b0ea947ee392b2741bf8de3683e458208a83fa25`; pushed to `origin/task/ARCH-054-BACKGROUND-001` and verified equal to the remote ref.
- Parent task branch synchronization head: `89c9890ba95d757f49c5c5e5e52a5077f10d825a`; parent report commit and publication result will be recorded after push.


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
