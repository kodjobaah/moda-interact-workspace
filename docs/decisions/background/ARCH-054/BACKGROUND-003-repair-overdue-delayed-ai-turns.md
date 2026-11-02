---
id: ARCH-054-BACKGROUND-003
architecture_id: ARCH-054
title: Repair missed or overdue delayed AI turn jobs
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
claimed_at: 2026-11-02T18:28:25Z
attempt: 1
depends_on:
  - ARCH-054-BACKGROUND-002
enables:
  - ARCH-054-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-11-02
---


# ARCH-054-BACKGROUND-003: Repair missed or overdue delayed AI turn jobs


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Ensure PostgreSQL pending deadlines survive Redis loss, worker restart or enqueue failure using bounded, idempotent repair in the existing messaging process.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `src/services/conversation-ai-delay/pending-turn-repair.ts` and `src/services/conversation-ai-delay/start-pending-turn-repair.ts`; wire start/stop in `src/entrypoints/messaging.ts` (with close handler) and existing whatsapp queue interface. Add `tests/integration/arch054-pending-turn-repair.integration.test.ts` and focused unit tests.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- At an explicit 30-second cadence (test-clock injectable), scan PostgreSQL for `controlMode=AI`, nonnull pending AI deadline, `inboundVersion > lastProcessedVersion`, no active nonexpired processing lease, and `pendingAiControlRevision=controlRevision`. Read in keyset pages ordered by `(pendingAiNotBeforeAt,id)` using index from DATABASE-001; `LIMIT 100` per page and maximum 1000 per pass; do not load customer content, full shop list, or use offset pagination.
- Maintain an in-process keyset cursor *across repair passes*, wrapping only after scanning through the final page; never restart from the first page on every 30-second pass (which can starve later records). For each candidate, enqueue the LATEST inboundVersion with existing deterministic BullMQ jobId and `delay=max(0,eligibleAt-now)` computed from persisted fields. Parallel instances may discover same record; deduplicate by jobId and rely on claim CAS, not an unbounded global mutex. Do not delete/replace active jobs or restart deadlines. Recheck eligible state when job executes. Failure to enqueue preserves DB pending state for next pass; propagate/log original exception with correlation.
- No tight-loop retry, no new Render deployable, no new Redis topology or arbitrary timeout extension. Provide shutdown cleanup. Expose counts `scanned`, `requeued`, `skipped`, `failed`, oldest due lag as bounded domain logs; reuse BullMQ queue telemetry (no duplicate HTTP metrics).
- Include test for continuous flood of oldest conversations proving the cross-pass keyset cursor advances fairly and no starvation from 1000 maximum; wrap the cursor only after reaching end-of-range. Validate clock drift and overdue handling.


## Work Items

  - [x] Implement bounded SQL scanner and existing queue enqueue adapter; wire startup and graceful shutdown.
  - [x] Test Redis outage then repair, multiple replicas, stale HUMAN/control-revision candidate, duplicate jobs, fair keyset pagination, crash/restart and a missed versioned enqueue.


## Interfaces / Contracts

No new public queue schema; same `process-conversation-turn` job as BACKGROUND-002. Existing original provider errors retained through Shared logging. SQL reads use `CheckoutRecovery.shopId` only as needed for consistency.


## Dependencies

- ARCH-054-BACKGROUND-002


## Enables

- ARCH-054-SYSTEM-TEST-001


## Acceptance Criteria

  - [x] Lost Redis job recovers automatically without second AI send or reset deadline; queue repair never sends from an obsolete control revision.
  - [x] Repair stays bounded under 10,000 waiting conversations and leaves HUMAN commands unaffected.


## Validation

  - [x] Focused unit tests; `node scripts/test-integration.mjs tests/integration/arch054-pending-turn-repair.integration.test.ts`; existing messaging worker startup/shutdown test; lint/typecheck/build per package.json; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for architect review

### Files Changed

- `src/services/conversation-ai-delay/pending-turn-repair.ts`
- `src/services/conversation-ai-delay/start-pending-turn-repair.ts`
- `src/entrypoints/messaging.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/conversation-ai-delay/pending-turn-repair.test.ts`
- `tests/unit/services/conversation-ai-delay/start-pending-turn-repair.test.ts`
- `tests/unit/runtime/arch047-meta-messaging-startup.test.ts`
- `tests/integration/arch054-pending-turn-repair.integration.test.ts`
- `tests/integration/arch047-meta-messaging-startup.integration.test.ts`

### Work Completed

- Added a PostgreSQL keyset scanner using `(pendingAiNotBeforeAt, id)`, pages of 100, a 1,000-row pass ceiling, and an in-process cursor that wraps only after reaching the final page. It selects only AI-controlled pending conversations with matching control revisions and no active processing lease; it reads no customer content.
- Repairs enqueue the latest persisted inbound version onto the existing `whatsapp-events` queue with the established deterministic job ID and computed nonnegative eligibility delay. Pending database state and frozen deadlines are not modified; original enqueue errors are logged with conversation/version/job correlation and rethrown for the next scheduled pass.
- Added the 30-second periodic repair lifecycle with one in-flight pass, retry on the next cadence after failure, and graceful timer cancellation/active-pass shutdown. Messaging startup passes the existing queue after readiness and registers the closer.
- Added focused unit and disposable PostgreSQL/Redis coverage for fairness under an older-row flood, cursor wrap, bounded 10,000-row scans, HUMAN/control-revision/lease exclusions, latest-version repair, simulated Redis enqueue outage and recovery, concurrent replicas, deterministic duplicate suppression, restart recovery, overdue/future delay calculation, and startup/shutdown wiring.
- Implementation commit: `ed5b803` (`feat(background): repair pending delayed AI turns`), pushed to `task/ARCH-054-BACKGROUND-003`.

### Validation Results

- `node_modules/.bin/vitest run tests/unit/services/conversation-ai-delay/pending-turn-repair.test.ts tests/unit/services/conversation-ai-delay/start-pending-turn-repair.test.ts tests/unit/runtime/arch047-meta-messaging-startup.test.ts` — passed, 3 files / 5 tests.
- `node scripts/test-integration.mjs tests/integration/arch054-pending-turn-repair.integration.test.ts` — passed, 1 file / 3 tests using disposable PostgreSQL and Redis.
- `node scripts/test-integration.mjs tests/integration/arch047-meta-messaging-startup.integration.test.ts` — passed, 1 file / 1 test using disposable PostgreSQL and Redis.
- `npm run lint` — passed.
- `npm run build` — passed; Prisma Client generation and TypeScript compilation completed.
- `git diff --check` — passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

- The Redis-outage recovery path is tested by injecting the original enqueue error at the queue boundary, verifying PostgreSQL pending state is unchanged, and retrying through the same repair service. Real Redis-backed integration cases verify concurrent replica and restart deduplication through BullMQ deterministic IDs.
- `npm ci` reported 40 dependency audit findings (27 moderate, 13 high); dependency remediation was outside this task and no dependency manifests or lockfiles were changed.

### Worktree and Git Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-BACKGROUND-003`
  parent branch: `task/ARCH-054-BACKGROUND-003`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-BACKGROUND-003`
  implementation branch: `task/ARCH-054-BACKGROUND-003`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization (launcher packet):
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules (launcher packet):
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commit: `database` at `7c377282aa5819b3008b7d7f3018f44f4161523e`

Task claim commit: `60f3ae0dbeac672fcfe302f356423b8f674c7913` (pushed).
Implementation commit: `ed5b803` (pushed to the explicit task branch ref).
No implementation submodule gitlink was changed.


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

Background main 10e72d7 has no implemented overdue frozen-AI-turn repair path. Keep this task Pending behind BACKGROUND-002; existing generic conversation processing/reconciliation does not prove delayed-turn durable repair or 10k-turn capacity.


## Dependency readiness — 2 November 2026

ARCH-054-BACKGROUND-002 is architect-accepted Complete at Attempt 2 (`64d1be0`). Its sole dependency is satisfied; this task is Ready, Attempt 0, unclaimed. Prepare through the normal launcher; this promotion does not execute repair work.
