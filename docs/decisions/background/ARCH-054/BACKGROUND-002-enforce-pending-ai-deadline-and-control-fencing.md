---
id: ARCH-054-BACKGROUND-002
architecture_id: ARCH-054
title: Gate AI execution by frozen deadline and original control revision
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
attempt: 1
depends_on:
  - ARCH-054-BACKGROUND-001
  - ARCH-054-API-002
  - ARCH-054-SHOPIFY-002
enables:
  - ARCH-054-BACKGROUND-003
created: 2026-10-31
updated: 2026-11-02
---


# ARCH-054-BACKGROUND-002: Gate AI execution by frozen deadline and original control revision


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task materialised on the parent task branch. Its implementation worktree will be prepared when the task is claimed through the normal execution workflow.


## Objective

Extend the existing BullMQ conversation-turn processor to wait without holding a worker, then admit exactly one current AI reply after due-time and control fencing.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Modify `src/services/conversation-turn-processor.service.ts`, `src/services/conversation.service.ts`, `src/services/recovery-conversation/ai-turn-ownership.service.ts`, `src/workers/whatsapp.worker.ts` only as required; add pure deadline helper at `src/services/conversation-ai-delay/eligibility.ts` and focused unit/Redis/PostgreSQL tests. Reuse `whatsapp-events`, version-specific job IDs and `DelayedError`; no new customer queue or worker.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- For recovery AI turns, `eligibleAt = max(pendingAiNotBeforeAt, min(lastInboundAt+conversationQuietWindowMs, pendingTurnStartedAt+conversationMaxSettleWindowMs))`; delay = max(0, eligibleAt-now). For delay=0 this exactly matches existing quiet/settle logic. Never reload/replace the delay with current merchant setting for an already started turn.
- Use DB CAS/row isolation for the initial cheap `claimTurn` (pending inbound version, current AI mode and original control revision). Permit existing moderation, abuse/routing checks and `loadTurn` to classify an AUTOMATION/guidance turn *before* applying the extra delay. After this classification, and **only if an AGENT model reply is needed**, require `now >= eligibleAt` before reserve or LLM invocation; otherwise `releaseTurn`, schedule a BullMQ delayed job for remaining time and return without holding a worker. An old pre-due job must never reserve an AGENT outbound. Inactive HUMAN or obsolete revision/versions must be acknowledged/suppressed without AI execution. Continue to use versioned deterministic job IDs; old observed versions are stale.
- Capture the frozen expected revision from pending state, not from fresh `AiTurnOwnershipService.readTurnOwnership()` after the delay. Check original revision before agent, after every async boundary and in the existing final provider send fence. A HUMAN->AI cycle cannot reauthorise old turns. New inbound during running AI causes stale output to fail prepared and latest version to be re-enqueued with the ORIGINAL pending deadline.
- Only gate `AGENT` model execution. `AUTOMATION` routing guidance, STOP/consent, moderation decisions, outreach templates, template status, merchant HUMAN commands and WhatsApp receipts remain unrestricted by this delay. Existing moderation, abuse, language, credit/idempotency and Meta final dispatch checks still run.
- `completeTurn` clears all pending-AI fields along with pendingTurnStartedAt, processing lease and updates lastProcessedVersion atomically if original revision and version still match; release must not clear another worker's claim. Scheduling exceptions are logged with original Error/cause and propagated; zero swallowed exceptions.


## Work Items

- [x] Add deterministic `eligibleAtMs` helper and apply preclaim delay scheduling and CAS.
- [x] Preserve original revision through all AI operations and final provider admission; add stale-version/replay protections.
- [x] Add unit/integration tests covering 0/1/7/30, burst coalescing, changed merchant setting, job duplicate/out-of-order, HUMAN->AI cycles, newer inbound during LLM await, and provider dispatch winning/losing races.


## Interfaces / Contracts

`ConversationTurnJob` remains `{conversationId:string, observedVersion:number}`; job ID remains `conversation-turn__${conversationId}__${observedVersion}`. Public Shared API contract remains unaffected. Internal `resolveEligibleAt({pendingAiNotBeforeAt,lastInboundAt,pendingTurnStartedAt,quietMs,maxMs})` returns UTC epoch ms.


## Dependencies

- ARCH-054-BACKGROUND-001
- ARCH-054-API-002
- ARCH-054-SHOPIFY-002


## Enables

- ARCH-054-BACKGROUND-003


## Acceptance Criteria

- [x] No AGENT invocation before persisted eligibleAt; routing guidance and safety checks do not wait for the merchant delay, and only one current turn is claimed across workers.
- [x] Human commands are never delayed by AI setting; no ghost reply after successful pre-dispatch takeover or H->AI resume.
- [x] 0 minutes preserves existing quiet window; any delay does not consume a BullMQ worker while waiting; no provider call inside DB transaction.


## Validation

- [x] `npx vitest run tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/recovery-conversation/recovery-conversation-services.test.ts`; `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts`; focused Redis/Meta mock concurrency tests, lint/typecheck/build per declared scripts; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Explicit test: at t=12:00 first inbound and delay=5, second at t=12:02, eligible no earlier than 12:05 (plus settling, not 12:07). If takeover at 12:03 and resume at 12:04, old 12:05 job must still be stale. If a provider request was irreversibly dispatched before takeover commit, do not promise recall.


## Completion Report

### Status

Attempt 1 submitted implementation; architect review requests corrections below. Task is Ready for the next attempt; Attempt 1 evidence is preserved.

### Files Changed

- `src/services/conversation-turn-processor.service.ts`
- `src/services/conversation.service.ts`
- `src/services/conversation-ai-delay/eligibility.ts`
- `tests/integration/conversation-turn-scheduling.integration.test.ts`
- Focused processor, conversation-service, and deadline-helper unit tests.

### Work Completed

- Added deterministic `resolveEligibleAt` calculation and kept merchant delay enforcement after moderation, abuse admission, and routing classification; only AGENT execution waits, with the turn released before delayed BullMQ rescheduling.
- Fenced initial claim, completion, suppression, model execution, and provider admission against the original pending control revision. Newer inbound versions are re-enqueued; stale prepared output is failed without provider send.
- Cleared the frozen deadline/revision fields atomically on successful completion or stale suppression and preserved version/lease ownership on release.
- Added helper, processor-race, service-CAS, and PostgreSQL transaction/snapshot coverage.

### Validation Results

- PASS: task-required processor and recovery-conversation unit suites, 77 tests.
- PASS: focused processor, conversation-service, and deadline-helper unit suites, 82 tests.
- PASS: `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts`, 4 tests.
- PASS: `npm run build` (Prisma Client generation and TypeScript compilation).
- PASS: `npm run lint` and `git diff --check`.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

No scope or contract deviation. ARCH-040 control-transition triggers reject synthetic direct mode/revision updates, so HUMAN-to-AI stale-revision fencing is covered by processor ownership/CAS unit tests rather than bypassing the required audit-event path in PostgreSQL fixtures.

### Worktree and Git Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-BACKGROUND-002`
  parent branch: `task/ARCH-054-BACKGROUND-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-BACKGROUND-002`
  implementation branch: `task/ARCH-054-BACKGROUND-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commit: `database` at `7c377282aa5819b3008b7d7f3018f44f4161523e`

Git:
  implementation commit: `35772c5` (`feat(background): enforce frozen AI deadline and control fence`), pushed to `origin/task/ARCH-054-BACKGROUND-002`
  parent claim commit: `799bd7815c92dd7abf6dd5b7c287366525aefe75`
  implementation starting HEAD: `ea04a633370be407af4090c18abcffae1145e62f`


## Architect Review — Attempt 1

### Review Status

**Changes Requested — 2 November 2026.** Implementation `35772c5b3232c5fe7a7afbc523e2762e28068177`; submitted report `cf40bfc86`. Return to Ready, preserve Attempt 1, clear executor/claimed_at. No architect acceptance or completion is recorded.

### Review Notes

1. **P1 — current inbound version is not fenced at final send admission.** `conversation-turn-processor.service.ts:614` checks `hasChanged`, but the subsequent `sendPreparedText` closure awaits `checkControl` at line 327 and forwards only `expectedControlRevision` at lines 332–334. New ingress can commit during that await, or during delivery preparation/moderation, without changing control revision. `outbound-message-delivery.service.ts` and `outbound-send-fence.service.ts` accept/check no original inbound version, so the outdated prepared reply can still acquire a provider permit. A temporary processor regression that advances version 3 to 4 during the before-provider ownership await failed: send admission was called once with revision 2 and no inbound-version fence. This is an unclosed task/architecture guarantee, not evidence that the existing control-revision fence is broken. Carry the original observed version to the short, locked final dispatch-admission transaction; reject and fail the stale prepared output and ensure the latest pending version remains scheduled with its original deadline. Preserve the existing rule that an already admitted/dispatched provider request cannot be recalled.
2. **P2 — feature-specific database/queue integration evidence is missing.** The four passing cases in `conversation-turn-scheduling.integration.test.ts` cover two BG001 snapshot transactions and two older standalone scheduling scenarios. The processor fixture sets `checkoutRecoveryId: null`, has no real ownership service and mocks send admission; the only integration-file change in this attempt adds an unused fixture method. None exercises the BG002 nonzero recovery deadline, original-revision claim/completion CAS, successful audited takeover/resume, or final provider winning/losing races. Add bounded disposable PostgreSQL/Redis coverage using real recovery state and legal control-transition/audit paths; do not bypass the database trigger. Mock the external model/Meta call, not the durable ownership/final-permit logic under review.

### Reviewed Files

- All 11 changed implementation/test files at `35772c5`.
- Existing `src/services/recovery-conversation/ai-turn-ownership.service.ts`.
- Existing `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` and `src/services/recovery-conversation/outbound-send-fence.service.ts`.
- Parent architecture, task definition, Completion Report, and dedicated worktree/branch evidence.

### Validation Reviewed

- Independent focused run: **4 suites / 100 tests passed** (processor, recovery-conversation services, conversation service, eligibility helper), Node 24.19.0.
- Temporary adversarial regression: **1 test failed**, reproducing the final ownership-await stale-send boundary. The temporary test was removed; implementation worktree remains clean. Reproduction and output are retained in [review evidence](evidence/BACKGROUND-002-attempt-1-review.md).
- Submitted 77-test and 82-test runs overlap; the independent 100-test run is the combined selected suite, not their sum.
- Submitted four integration passes, build and lint are recorded as executor evidence; architect did not rerun those commands. The four integration cases do not establish the missing BG002 scenarios.
- Implementation local HEAD equals its published task ref; no implementation source or branch was changed by this review.

### Architecture Conformance

Frozen deadline calculation, AGENT-only gate placement, persisted original control revision, BullMQ delay reuse and short database operations follow the design. Final current-inbound-version admission and required feature integration proof remain incomplete. No schema/Shared/public contract change is needed for the correction.

### Follow-up

Reclaim the same task through the normal launcher for Attempt 2. Fix P1 and cover it both at the processor boundary and in the locked final permit; include new ingress during outbound preparation/moderation. Add P2 recovery integration covering pre-due release/reschedule with no reservation/model call, due execution, original frozen deadline across newer ingress, duplicate/out-of-order jobs and valid takeover/resume/final-admission races. Preserve all existing moderation, billing, consent, idempotency and HUMAN behavior. BACKGROUND-003 stays Pending; no downstream task is promoted or executed.

## Review correction scope — 2 November 2026

The permitted Background-only correction scope also includes the existing internal admission/delivery ports, `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`, `src/services/recovery-conversation/outbound-send-fence.service.ts`, and its existing SQL projection/helper if needed to compare the original inbound version inside the final permit. Do not invent a new provider queue, call a provider inside a transaction, change public Shared contracts, or weaken non-turn HUMAN/AUTOMATION/initial-outreach behavior. Add targeted tests alongside the existing processor/fence/integration suites.

- [ ] Original observed inbound version is checked atomically with final dispatch admission; stale prepared output cannot pass after newer ingress wins the lock.
- [ ] Real recovery PostgreSQL/Redis execution proves the frozen deadline and original control-revision behavior, including audited control transitions and both final-admission outcomes.

## Definition reconciliation — 2026-11-02

Historical pre-implementation snapshot (superseded by Attempt 1 and its review above): Background main 10e72d7 used conversation-turn-processor.service.ts control ownership checks and has no pendingAiNotBeforeAt/pendingAiControlRevision enforcement in runtime source. Frozen-deadline scheduling, original control-revision fencing and final-admission behavior remain unimplemented; BACKGROUND-001 validation is still a prerequisite.
