---
id: ARCH-054-SHOPIFY-002
architecture_id: ARCH-054
title: Invalidate pending AI inside Shopify take-over/resume action
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-31T22:36:03Z
attempt: 2
depends_on:
  - ARCH-054-DATABASE-001
enables:
  - ARCH-054-BACKGROUND-002
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SHOPIFY-002: Invalidate pending AI inside Shopify take-over/resume action


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Apply the same atomic pending-turn and processing-lease invalidation to authenticated Shopify control changes.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Modify `app/services/recoveries/recovery-human-commands.server.ts` only plus existing Shopify control tests. Keep the existing recovery-detail route/UI and `targetMode` / `expectedControlRevision` interface.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Under the existing authenticated shop/recovery row locks, on successful controlMode change (AI->HUMAN or HUMAN->AI) increment controlRevision, clear `pendingTurnStartedAt`, `pendingAiNotBeforeAt`, `pendingAiControlRevision`, `pendingAiDelayMinutes`, `processingInboundVersion`, `processingStartedAt`, and advance `lastProcessedVersion` to current inboundVersion in the same DB transaction. Write ConversationControlEvent within that transaction.
- Retain all existing entitlement, restriction, terminal-recovery and stale-control checks. Idempotent/no-op transitions and concurrent conflicting requests cannot erase newly started turns or reuse previous AI revision. Human composer and durable command dispatch do not consult aiResponseDelayMinutes.
- The worker final provider admission must still fence on the original revision. Do not claim to recall already submitted Meta traffic.


## Work Items

- [x] Extend the existing Shopify control service; add transaction-level race tests and rollback assertions.
- [x] Verify no replay after HUMAN->AI, no pending AI for HUMAN, no human dispatch delay and no regression to existing controls.


## Interfaces / Contracts

Existing ARCH-040 control DTO and `controlRevision` are unchanged; DATABASE-001 owns newly cleared nullable fields.


## Dependencies

- ARCH-054-DATABASE-001


## Enables

- ARCH-054-BACKGROUND-002


## Acceptance Criteria

- [x] Shopify takeover suppresses a waiting or in-flight AI turn whose dispatch has not passed final admission; Resume AI cannot revive an old queued job.
- [x] Authenticated merchant human send remains immediate subject to normal guards.


## Validation

- [x] Existing Shopify human-command/control service tests: `npm test -- tests/unit/arch040-shopify-command.test.ts` — 36 tests passed.
- [ ] Prisma transaction integration test: added and attempted with `MODA_DISPOSABLE_INTEGRATION=1`; Testcontainers could not start because this machine has no working container runtime (`Could not find a working container runtime strategy`).
- [x] Changed-file lint: ESLint passed for the service and both test files.
- [x] Typecheck: `npm run typecheck` passed.
- [x] Build: `npm run build` passed. It emitted the existing Zod annotation and large-chunk warnings; there were no build errors.
- [x] `git diff --check` passed.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Ready for Review

### Files Changed

- `app/services/recoveries/recovery-human-commands.server.ts`
- `tests/unit/arch040-shopify-command.test.ts`
- `tests/integration/shopify-recovery-control-invalidation.postgres.integration.test.ts`

### Work Completed

- Shopify HUMAN takeover and Resume AI now increment `controlRevision`, clear the pending-turn deadline/revision/delay and processing lease, and advance `lastProcessedVersion` to the locked conversation's current `inboundVersion` in the same transaction as the control event.
- The conditional write also matches the locked `inboundVersion`, so a failed compare-and-set cannot clear a newer turn. Idempotent transitions still exit before writing.
- Added unit coverage for both transitions, lost compare-and-set, and no-op requests. Added a disposable PostgreSQL test for concurrent takeovers, event-write rollback, and stale-revision preservation of a newly opened AI turn.
- The existing durable HUMAN command path remains unchanged and does not consult `aiResponseDelayMinutes`.

### Validation Results

- Focused Shopify command/control suite: 36 passed.
- Changed-file ESLint: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed (existing Zod annotation and large chunk warnings only).
- `git diff --check`: passed.
- PostgreSQL integration: test added and attempted, but unverified because Testcontainers reported no working container runtime. The three integration cases were therefore not executed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

- PostgreSQL transaction behavior still needs execution in an environment with a working Docker/container runtime.
- The first `npm ci` attempt could not complete because the disk ran out of space (`ENOSPC`). The task worktree had no installed dependencies, so validation temporarily reused the exact-lockfile dependency tree from the preceding ARCH-054 Shopify worktree; its temporary `node_modules` symlink has been removed. No dependency manifest or lockfile changed.
- The build completed with Rollup warnings for dependency annotations and a chunk larger than 500 kB; these are not build failures.

### Worktree and Git Evidence

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-SHOPIFY-002
  parent branch: task/ARCH-054-SHOPIFY-002
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-SHOPIFY-002
  implementation branch: task/ARCH-054-SHOPIFY-002
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no (the exact-lockfile dependency tree was temporarily linked for validation only)

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current
  parent branch start SHA: 196bacc54c1b657657b35d54b4e66b207b44cfe8
  implementation branch start SHA: db845bf5e67d0b1a6c853768f1abeb047402b3bd
  durable claim commit: ac60a4c0a6711a297d62372dc2724654020ed23f (pushed)

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  database submodule commit: 7c377282aa5819b3008b7d7f3018f44f4161523e

Implementation publication:
  implementation commit: 0101f1bfb33e67e42c5d72a55c31022e3696901b (pushed to origin/task/ARCH-054-SHOPIFY-002)
  parent task report: committed and pushed on task/ARCH-054-SHOPIFY-002


## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

Code inspection found the control change clears pending AI scheduling and
processing state atomically with the control revision and event write. The
conditional write includes the locked `inboundVersion`, and the no-op path
returns before mutation. No source-code correction is identified.

The required PostgreSQL integration test did not execute because Testcontainers
could not find a working container runtime. This leaves the core database
behavior unverified: concurrent takeover serialization, rollback when event
creation fails, and preservation of a fresh pending turn after a stale request.
The unit tests use Prisma mocks and do not replace those checks.

Keep Attempt 1 and the implementation branch unchanged. Return the task to
`ready`; the next canonical task claim increments the attempt. Run the existing
disposable PostgreSQL test in an environment with a working container runtime:
`MODA_DISPOSABLE_INTEGRATION=1 npx vitest run tests/integration/shopify-recovery-control-invalidation.postgres.integration.test.ts`.
Record the result, including all three cases, before resubmitting. The task is
not accepted or complete.

### Reviewed Files

- `app/services/recoveries/recovery-human-commands.server.ts`
- `tests/unit/arch040-shopify-command.test.ts`
- `tests/integration/shopify-recovery-control-invalidation.postgres.integration.test.ts`

### Validation Reviewed

The Completion Report records the 36-test focused unit run, changed-file lint,
typecheck, build and `git diff --check` as passing. The PostgreSQL test was
attempted but did not start because no working Testcontainers runtime was
available. Tests were not rerun for this review.

### Architecture Conformance

The implementation follows the existing control transaction and retains the
Shop/conversation locks, control revision, and event transaction. Acceptance is
withheld until the required PostgreSQL transaction evidence is available.

### Follow-up

Rerun and report the existing PostgreSQL integration test; no implementation
change is currently requested. Do not promote `ARCH-054-BACKGROUND-002` until
this task is accepted.
