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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
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

Coordinator: `moda_architect`. Task materialised on matching parent and implementation task branches; Attempt 2 accepted and Complete; Attempt 1 review history retained below.


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

Complete — Architect Accepted, Attempt 2, 2 November 2026. Automatic completion applied after independent review; claim cleared and attempt preserved.

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
- Attempt 2 P2 correction: look up the deterministic job ID before enqueue. Existing waiting/delayed/active jobs are left untouched; a retained failed job is retried only when its frozen eligibility is due, using BullMQ's atomic `Job.retry("failed")` with exhausted-attempt counters reset. If another replica wins the state transition, the losing retry rereads job state and records a skip unless it remains failed; active jobs are never removed or replaced. A successful new `queue.add` is counted as requeued without a follow-up lookup that could misclassify that new job as a duplicate.
- Added a real disposable Redis regression that fails a one-attempt versioned job, runs two repair instances concurrently, and proves exactly one retry proceeds without new inbound data while the pending deadline and ownership revision remain unchanged. The successful retried worker claims and completes the same version once.
- Attempt 2 implementation commit: `8d120af` (`fix(background): retry retained failed turn jobs`), pushed to `task/ARCH-054-BACKGROUND-003`.

### Validation Results

- `node_modules/.bin/vitest run tests/unit/services/conversation-ai-delay/pending-turn-repair.test.ts tests/unit/services/conversation-ai-delay/start-pending-turn-repair.test.ts tests/unit/runtime/arch047-meta-messaging-startup.test.ts` — passed, 3 files / 5 tests.
- Attempt 2 focused unit command for scanner/poller/startup — passed, 3 files / 7 tests.
- `node scripts/test-integration.mjs tests/integration/arch054-pending-turn-repair.integration.test.ts` — passed, 1 file / 4 tests using disposable PostgreSQL and Redis; includes retained failed-job retry with concurrent repair.
- `node scripts/test-integration.mjs tests/integration/arch047-meta-messaging-startup.integration.test.ts` — passed, 1 file / 1 test using disposable PostgreSQL and Redis.
- Attempt 2 `npm run lint` — passed.
- Attempt 2 `npm run build` — passed; Prisma Client generation and TypeScript compilation completed.
- Attempt 2 `git diff --check` — passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

- The Redis-outage recovery path is tested by injecting the original enqueue error at the queue boundary, verifying PostgreSQL pending state is unchanged, and retrying through the same repair service. Real Redis-backed integration cases verify concurrent replica and restart deduplication through BullMQ deterministic IDs.
- The retained-failed-job P2 is addressed in Attempt 2; validation confirms the existing failed record becomes executable without replacing active jobs or changing the frozen deadline. Independently verified and accepted at Attempt 2.
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
Attempt 2 claim commit: `4ff20cdeef93ea4fb72bd5ae98efb613cd00c737` (pushed).
Attempt 2 implementation commit: `8d120af` (pushed to the explicit task branch ref).
No implementation submodule gitlink was changed.


## Architect Review

### Current decision — Accepted, Attempt 2

Accepted implementation `8d120afa51337d408296c7b0f9bc746499ecd530`, independently verified against the remote task ref. The retained-failed-job P2 is resolved. No new blocking findings. Under `completion_mode: automatic`, set Complete, clear executor/claimed_at, and preserve Attempt 2.

The repair looks up the deterministic job and retries only failed jobs whose persisted eligibility is due. Existing waiting/delayed/active jobs are skipped. BullMQ's failed-state retry provides the atomic transition; a losing replica rechecks state and reports skipped after a competing transition. Genuine retry errors that leave the job failed still propagate with correlation. Repair does not mutate frozen database deadlines or pending ownership state; existing execution-time fences remain authoritative.

Independent validation (Node 24.19.0):

- Focused scanner/poller/messaging-startup suites: **3 files / 7 tests passed**.
- Repair and messaging-startup disposable PostgreSQL/Redis suites: **2 files / 5 tests passed**, including the real retained-failed-job concurrent retry. The regression confirms one recovery enqueue and one replica skip, unchanged persisted deadline/ownership before execution, and successful subsequent execution without new inbound. Its worker models the processing gate; it is not full provider-send certification.
- `git diff --check` passed. Executor-reported typecheck/lint/build results retained as supplied evidence; not independently repeated for this review.
- Both canonical worktrees inspected, implementation clean and published; no source changes or merges to main made by the reviewer. Parent submission `e8fc9c34` precedes this acceptance commit.

Dependency frontier: all explicit implementation/release prerequisites of ARCH-054-SYSTEM-TEST-001 are Complete. It becomes Ready, Attempt 0, unclaimed, with manual launch still required. SYSTEM-TEST-002 remains Pending on SYSTEM-TEST-001; its BACKGROUND-003 prerequisite is now satisfied. No system certification is claimed.

### Historical Attempt 1 review


### Review Status

**Changes Requested — Attempt 1, 2 November 2026.** Return to Ready, clear executor/claimed_at, preserve Attempt 1. The next launcher claim increments the attempt; do not create a replacement branch. No architect acceptance.

### Finding — P2: retained failed jobs prevent durable repair

At `src/services/conversation-ai-delay/pending-turn-repair.ts:101–119`, repair calls `queue.add` using the deterministic versioned ID and unconditionally increments `requeued`. The existing queue retains failed jobs (no removeOnFail policy), and ordinary conversation processing can throw after releasing the processing lease while preserving the pending deadline/version. BullMQ treats an add with the retained failed job's ID as a duplicate: it does not move that job back to waiting. Every later pass reports a successful repair while the same pending turn remains stuck until external intervention or newer inbound.

Independently reproduced with the installed BullMQ and isolated Redis: enqueue the exact job name/data/options used by repair, execute it once with a Worker that throws a transient processor error, close that worker, then repeat the identical queue.add. Result:

```text
before repair: failed
after repair queue.add: failed
counts: {"waiting":0,"delayed":0,"failed":1}
```

The temporary Redis container was removed; no implementation files changed. Source inspection confirms `ConversationTurnProcessor` releases the lease and rethrows, `ConversationService.releaseTurn` only clears processing fields, and the production queue supplies neither automatic failed-job removal nor a failed-state retry in the new repair path.

### Required correction

Handle retained terminal failed jobs explicitly using a bounded, race-safe retry/reconciliation path. Preserve deterministic deduplication and frozen deadlines; never remove or replace active jobs. A failed job must become executable when the persisted turn is still pending, and repeated/concurrent repair passes must remain safe. Do not count a retained terminal failed job as successfully requeued. Add a real Redis regression that fails a versioned job, runs repair, and proves execution resumes without requiring another inbound message; include concurrent repair and unchanged deadline/ownership gates. Reuse the existing execution-time control/version fences.

### Validation Reviewed

- Independently ran focused scanner/poller/messaging-startup unit suites: **3 files / 5 tests passed**.
- Independently ran the submitted repair and messaging-startup integration suites together through `scripts/test-integration.mjs`: **2 files / 4 tests passed**, disposable PostgreSQL/Redis, successful runner exit.
- Independent retained-failed-job probe reproduced the finding above. Submitted integration tests cover waiting/delayed duplicates, not a retained failed job.
- `git diff --check` passed. Executor-reported lint/build remain recorded as supplied results; not rerun in this review.
- `ed5b8037018fcae54fe1b10f89ddcda6de48f138` matches the remote implementation task ref. Canonical physical worktrees and task branches verified; no implementation changes or main merge performed.

### Positive findings and dependency frontier

Cross-pass cursor progression, bounded pages/pass counts, narrow SQL projection, ownership/lease filtering, original enqueue error propagation, injected cadence and nonoverlapping shutdown wiring conform to the intended design. The blocking issue is retained failed-job liveness. ARCH-054-SYSTEM-TEST-001 remains Pending because BACKGROUND-003 is not accepted Complete; no downstream promotion or test execution is authorized by this review.

### Follow-up

Correct the retained-failed-job path and publish the regression evidence on the same mirrored task branches. Historical submission evidence above remains preserved; it does not imply acceptance.

## Definition reconciliation — 2026-11-02

Background main 10e72d7 has no implemented overdue frozen-AI-turn repair path. Keep this task Pending behind BACKGROUND-002; existing generic conversation processing/reconciliation does not prove delayed-turn durable repair or 10k-turn capacity.


## Dependency readiness — 2 November 2026

ARCH-054-BACKGROUND-002 is architect-accepted Complete at Attempt 2 (`64d1be0`). Its sole dependency is satisfied; this task is Ready, Attempt 0, unclaimed. Prepare through the normal launcher; this promotion does not execute repair work.
