---
id: ARCH-070-BACKGROUND-002
architecture_id: ARCH-070
title: Respect terminal failures for the same inbound version
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Respect terminal failures for the same inbound version

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Respect terminal failures for the same inbound version without relaxing existing production security or lifecycle guarantees.

## Context

A nonretryable INVALID_FINAL failure was repeatedly requeued by the 30-second pending-turn repair, repeating model/tool work for the same inbound version.

## Scope

src/services/conversation-turn-processor.service.ts; src/services/conversation-ai-delay/pending-turn-repair.ts; directly related lifecycle unit/integration tests. No edits to commerce/host.ts.

## Out of Scope

Other task's owned modules, Shared/MCP implementation, schema changes, provider/model switching, credentials, infrastructure, old-message replay, unrelated refactors and unsolicited customer sends.

## Requirements

Persist or derive a durable version-scoped terminal condition using existing state contracts; repair must not requeue the same terminal inbound version. A genuinely newer inbound remains processable. Retryable/transient failures retain bounded recovery; crashes and in-flight claims remain recoverable. Preserve locking, idempotency, delivery and user-facing failure behavior. Do not add a blanket skip or process-local suppression. Return schema needs to architect rather than modifying database ownership.

## Work Items

- [x] Establish exact source/fixture cause and preserve a failing regression.
- [x] Implement only the owned correction.
- [x] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None. The two ARCH-070 tasks are independently executable on disjoint modules; final developer integration must preserve both changes.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [x] Requirements demonstrated with deterministic positive and negative regression tests.
- [x] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [x] No duplicate delivery, live test send, secret logging or unrelated changes.
- [x] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [x] Deterministic repeated repair cycles after nonretryable failure cause no new model/tool/send; newer inbound progresses; retryable failure and crash recovery regressions; relevant PostgreSQL lifecycle tests if durable state is changed, typecheck, lint and required repository CI.
- [x] Diff hygiene and exact changed-file scope review.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/conversation-turn-processor.service.ts`
- `tests/unit/services/conversation-turn-processor.service.test.ts`
- `tests/unit/services/conversation-turn-processor/terminal-failure.cases.ts`
- `tests/integration/arch054-pending-turn-repair.integration.test.ts`

### Work Completed

- Confirmed the catch path always released the lease and threw without consuming a nonretryable Commerce host failure; pending repair therefore reselected the same durable inbound version.
- Confirmed the production admission helper already calls reservation cleanup before rethrowing agent failures. Added a separate successful-cleanup flag rather than treating an attempted cleanup as success.
- Only typed `CommerceHostError` failures with `retryable === false`, no provider-send attempt, and confirmed reservation cleanup consume the owned version using existing `completeOwnedTurn()` CAS semantics.
- Newer inbound versions remain pending and are enqueued; control-revision changes suppress only the old owned turn. Cleanup/completion failures, untyped/unknown errors, transient errors and uncertain provider delivery still release and throw for existing recovery.
- Reused existing durable conversation fields; no repair SQL, queue, database schema, Shared dependency, provider, credential or customer-send change.

### Validation Results

- Regression proof against original processor: five new terminal/CAS cases failed, 69 passed. Restoring the fix made all cases green.
- Focused unit command: `npx vitest run tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/conversation-ai-delay/pending-turn-repair.test.ts tests/unit/services/conversation.service.test.ts tests/unit/workers/whatsapp.worker.test.ts` — 130 passed.
- `npx tsc --noEmit` and focused ESLint on all four changed files — passed. `git diff --check` — passed.
- Disposable PostgreSQL/Redis: `node scripts/test-integration.mjs tests/integration/arch054-pending-turn-repair.integration.test.ts --reporter=verbose` — five passed, 22.98s. The new actual-processor/real-admission-helper proof completed in 1013ms: terminal version 9 clears pending state, two later repair passes scan/requeue zero, no provider send occurs, and a new durable inbound version 10 is processed. Existing 10,000-row/stale-lease, concurrent replica/restart, retained transient failure and enqueue-failure/deadline recovery proofs also passed. Disposable infrastructure was removed by the runner.
- Full repository CI at `451709030abdc92b32b5c1c40fd17aec2f067972`: 3,951 tests / 367 files passed in both push and PR checks: https://github.com/kodjobaah/moda-interact-background/actions/runs/43222332413/job/131196697503 and https://github.com/kodjobaah/moda-interact-background/actions/runs/43222491125/job/131197242757.

### Deviations

- The initial combined disposable run including the broader existing `conversation-turn-scheduling.integration.test.ts` stalled in that file's fixtures without reporting a result. Its known Vitest child was terminated, and its wrapper cleaned up the disposable infrastructure. The required repair suite then passed in isolation; no claim is made that the broader scheduling run passed.
- Initial disposable command lacked Docker on its process PATH. The already-installed `/usr/local/bin/docker` was verified and made available only in the validation process; no software or machine configuration was changed.

### Assumptions

The typed Commerce host retryability contract is authoritative only before any provider-send attempt; arbitrary error properties do not terminally consume a turn.

### Unresolved Issues

No runtime issue remains in this task's scope. The broader scheduling run described above has no result; the terminal repair suite and repository CI passed. Production verification and final merge remain developer-owned.

### Architectural Concerns

No new contract or schema dependency was required. Recommendation verification remains the separately owned BACKGROUND-001 task.

### Git / VCS

- Task branch in both repositories: `task/ARCH-070-BACKGROUND-002`.
- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-002`.
- Prepared packet: `/tmp/moda-arch070-bg002-prepare.json`; attempt 1, executor codex, durable parent claim `2eab9a419d8b1969a9c01a3cc80323775cd099af` pushed by the launcher.
- Parent worktree reused; implementation worktree created. Both remote task fast-forwards were not needed; both origin/main histories were already current. Recursive submodule sync/init/update passed, database at `5329d5390d346042895219663f3a040ea54ae168`.
- Shared/default workspace and implementation checkouts were not switched or mutated; no other task worktree reused.
- Implementation commit `451709030abdc92b32b5c1c40fd17aec2f067972` pushed to origin/task/ARCH-070-BACKGROUND-002; PR https://github.com/kodjobaah/moda-interact-background/pull/200.
- Parent publication: this task file only on the mirrored branch. No submodule gitlink staged. No implementation or workspace main merge performed by this agent.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

Reviewed actual implementation451709030abdc92b32b5c1c40fd17aec2f067972, all four changed files and durable report9879bb4bb. Only typed CommerceHostError nonretryable failures before provider attempt can consume the observed turn, and only after confirmed admission cleanup. Existing completeOwnedTurn version/control-revision CAS preserves newer input; uncertain provider, cleanup, completion, unknown and retryable errors remain repairable. No repair SQL or schema change. Prepared mirrored physical isolation/synchronization/recursive database evidence verified.

### Reviewed Files

conversation-turn-processor.service.ts; terminal-failure.cases.ts and facade registration; arch054-pending-turn-repair.integration.test.ts.

### Validation Reviewed

Original-code five-case regression failure, 130 focused unit passes, typecheck/lint/diff hygiene, both full CI3,951 tests/367 files. Disposable PostgreSQL/Redis suite5 passed, including actual processor/admission helper terminal completion, two zero-requeue repair passes and fresh inbound progression. Broader scheduling fixture run produced no result and is not claimed passed; focused durable proof plus unchanged relevant existing repair scenarios satisfy this bounded contract.

### Architecture Conformance

Conforms to durable inbound-version scoped terminal policy without weakening tenant, delivery, controls or crash/transient recovery. Existing shared structured logger used for bounded semantic terminal outcome. Independently shippable before recommendation and footer tasks. Production remains developer-verification owned.

### Follow-up

Developer may merge PR200 and deploy this independent correction to stop terminal retry amplification. Observe subsequent repair passes in production without resetting/replaying processed inbound versions. Recommendation and footer remain separately gated.
