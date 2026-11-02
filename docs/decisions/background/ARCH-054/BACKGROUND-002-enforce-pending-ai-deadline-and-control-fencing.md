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
status: review
priority: 30
executor: copilot
claimed_at: 2026-11-02T13:55:04Z
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

Implementation complete; ready for `moda_architect` review.

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

## Definition reconciliation — 2026-11-02

Background main 10e72d7 still uses conversation-turn-processor.service.ts control ownership checks and has no pendingAiNotBeforeAt/pendingAiControlRevision enforcement in runtime source. Frozen-deadline scheduling, original control-revision fencing and final-admission behavior remain unimplemented; BACKGROUND-001 validation is still a prerequisite.
