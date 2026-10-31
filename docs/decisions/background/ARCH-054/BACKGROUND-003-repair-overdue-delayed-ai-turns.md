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
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-054-BACKGROUND-002
enables:
  - ARCH-054-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
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

- [ ] Implement bounded SQL scanner and existing queue enqueue adapter; wire startup and graceful shutdown.
- [ ] Test Redis outage then repair, multiple replicas, stale HUMAN/control-revision candidate, duplicate jobs, fair keyset pagination, crash/restart and a missed versioned enqueue.


## Interfaces / Contracts

No new public queue schema; same `process-conversation-turn` job as BACKGROUND-002. Existing original provider errors retained through Shared logging. SQL reads use `CheckoutRecovery.shopId` only as needed for consistency.


## Dependencies

- ARCH-054-BACKGROUND-002


## Enables

- ARCH-054-SYSTEM-TEST-001


## Acceptance Criteria

- [ ] Lost Redis job recovers automatically without second AI send or reset deadline; queue repair never sends from an obsolete control revision.
- [ ] Repair stays bounded under 10,000 waiting conversations and leaves HUMAN commands unaffected.


## Validation

- [ ] Focused unit tests; `node scripts/test-integration.mjs tests/integration/arch054-pending-turn-repair.integration.test.ts`; existing messaging worker startup/shutdown test; lint/typecheck/build per package.json; `git diff --check`.


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
