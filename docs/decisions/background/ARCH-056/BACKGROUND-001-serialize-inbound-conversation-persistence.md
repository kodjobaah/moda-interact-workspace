---
id: ARCH-056-BACKGROUND-001
architecture_id: ARCH-056
title: Serialize inbound persistence before the message foreign-key insert
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-11-04T00:34:05Z
attempt: 1
depends_on:
- ARCH-054-BACKGROUND-001
enables:
- ARCH-056-SYSTEM-TEST-001
created: '2026-11-03'
updated: 2026-11-04
---

# ARCH-056-BACKGROUND-001: Serialize inbound persistence before the message foreign-key insert

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`.

Definition revision: 2. **Defined but not materialised.** Ready is based on the completed prerequisite in the reviewed snapshot; the real launcher rechecks before execution. No implementation or task claim has occurred.

## Objective

Remove the inbound parent/child lock-upgrade cycle while preserving atomic message, version and pending-turn persistence.

## Context

U3 arises because `ConversationService.receiveMessageInternal` inserts the child message before `recordProcessableInbound` requests parent `FOR UPDATE`. Two immediate FK checks may each retain a parent KEY SHARE before either upgrade. The helper's locked current-state decision correctly addresses MSG-01 and must be retained. This is a new correction against that accepted implementation, not reopening or rewriting ARCH-054's historical review.

## Scope

One repository: `moda-interact-background`. Exact paths and operations:

| Path | Operation | Allowed edit |
|---|---|---|
| `src/services/conversation.service.ts` | MODIFY | Move the existing helper invocation before `tx.conversationMessage.create` inside the same transaction; retain its return value and later writes; add the required per-invocation diagnostic stage and safe original-error projection |
| `src/workers/whatsapp.worker.ts` | MODIFY, diagnostics only | Correct existing `failed`/`error` callback projections and `boundedError` so raw outer errors cannot bypass the source log's redaction; retain every job route, retry, telemetry and queue setting |
| `tests/unit/services/conversation.service.test.ts` | MODIFY | Assert transaction call order, rollback propagation and unchanged duplicate ownership behavior; capture actual Shared records for transaction/post-commit failure, redaction and sink isolation |
| `tests/unit/workers/whatsapp.worker.test.ts` | MODIFY | Exercise existing callback records through the installed Shared logger; original safe message, code/context, redaction and sink failure |
| `tests/integration/conversation-turn-scheduling.integration.test.ts` | MODIFY | Keep existing regression coverage; align the manually reconstructed rollback fixture with corrected ordering |
| `tests/integration/arch056-inbound-lock-order.integration.test.ts` | CREATE | Real service/two-connection parent-first serialization and control/audio interleavings |
| `tests/integration/arch056-inbound-rollback.integration.test.ts` | CREATE | Raced duplicate and injected post-helper failure atomicity |
| `tests/integration/helpers/arch056-inbound-fixtures.ts` | CREATE | Minimal owned recovery/standalone fixtures and scoped cleanup using existing Prisma/schema |
| `tests/integration/helpers/arch056-inbound-barriers.ts` | CREATE | Test-only transaction interception and observed lock/barrier coordination; no production hook |

Read-only dependencies include `src/services/conversation-ai-delay/pending-turn-repository.ts`, `src/services/inbound-whatsapp-audio.service.ts`, `src/services/whatsapp-inbound-processing.service.ts`, `src/services/conversation-turn-processor.service.ts`, the accepted Conversation FK/control migrations and `scripts/test-integration.mjs`. No helper lock-mode change or new production file is authorized.

## Out of Scope

No language-policy/read consolidation, markSent/final-send changes, stronger Shop lock, weakened lock mode, FK deferral, new queue/mutex, swallowed unique errors, broad write batching, migration or existing task/index edits. General moderation/reservation replay and receipt locking are other touchpoints. The older unlocked language-resolution race remains explicitly outside this narrow task.

## Requirements

1. Required transaction order: `recordProcessableInbound(tx, conversationId, receivedAt)` -> inbound `ConversationMessage.create` -> existing language write -> existing monotonic Conversation clocks -> commit. Keep the duplicate lookup and initial language resolution outside the transaction, and `markEngagedForConversation` after commit, as in the current contract.
2. Reuse the existing `FOR UPDATE OF c` helper and current locked recovery-to-shop identity. Add no second parent lock, no Shop lock and no weaker mode. The helper remains the only pending-turn calculation.
3. Same transaction persists message and version/deadline/control state. Any error after the helper, including a raced providerMessageId uniqueness violation, must reject the whole transaction. Do not catch the insert failure inside the transaction and return success; do not turn a failed receive into a completed job.
4. Preserve unique provider-message ownership, returned `{conversationId, version, duplicate}`, received/occurred timestamp meaning, frozen first-turn delay/revision, current 0–30 whole-minute delay/default-zero rules, HUMAN processing watermark/clear behavior, standalone behavior, future deadline and existing audio completion semantics.
5. Keep post-commit engagement and enqueue recoverable through the current existing-message shortcut. A post-commit failure is not a rolled-back receive. Preserve original errors through the current Shared logger and rethrow; no message-content/recipient secrets in logs.
6. No provider/Redis I/O while the message transaction is open. Existing bounded queue retry remains; this task does not promise unlimited delivery or prove that the new pending-turn repair can recover a transaction that never committed.
7. Successful distinct-message paths introduce no new database call site and retain their direct-call count. Duplicate/error paths can now execute helper work before the failed INSERT; record this honestly rather than claiming a universal zero delta.
8. Preserve `whatsapp.inbound.persistence_failed` as the failure owner at `ConversationService.receiveMessage`. Its Shared logger event must include the original safe `error.name`/`error.message`, the Conversation identity, actual provider-message identity when safe and already available, and a truthful stage distinguishing the atomic receive from post-commit engagement. Add a bounded local stage value to the same existing service only; it must not change transaction/retry behavior. Include actual Prisma code/clientVersion when present, and no request/message body or raw parameter/meta dump. Do not log a post-commit engagement failure as if the receive rolled back. Preserve the exact thrown error object. Follow the parent's revision-2 logging acceptance contract; no new production logging helper or logger framework is authorised.
9. The WhatsApp worker is the terminal failure logger for inbound and provider-status jobs. Retain `whatsapp.job.failed` and `whatsapp.worker.error`, `jobId` normalization, job name, attempts and existing behavior. Correct only its existing error projection/callback fields: do not spread a safe `boundedError` result and then overwrite it with raw `error.message`/`error`, as the baseline does. Emit a safe bounded direct original name/message, actually supplied Prisma/SDK code when safe, and available job context. Preserve original source diagnostics owned by BG002/BG003 and do not dump payloads or pretend the worker recovered provider fields absent from the exception. Test the real emitted callback record for safe and sensitive error fixtures; no service-only assertion may certify the worker output. This shared file has one writer here; BG002 reads its diagnostic contract but does not edit it or gain a task-order dependency.

## Work Items

- [ ] Reorder the existing helper call in the named transaction without changing its semantics or boundary.
- [ ] Update focused unit expectations and the existing rollback fixture.
- [ ] Add deterministic real-service concurrency and duplicate/error rollback tests using the named test-only helpers.
- [ ] Verify preserved control/audio/pending behavior and original-error propagation.
- [ ] Verify the actual installed Shared logger emits the original safe message and accurate failure stage; use its real capture sink, not only a mocked logger method.
- [ ] Correct the existing worker failure/error projections and prove that their emitted records retain the safe original message without reintroducing removed sensitive text.
- [ ] Record the lock schedule and row outcomes, successful-path call comparison and increased rolled-back duplicate work.

## Interfaces / Contracts

No signature, public queue payload, Shared package or database schema change. Preserve the existing helper result `{version:number, scheduleAi:boolean}` and receive result. The existing versioned queue identity and normal caller routing remain unchanged.

The selected order is an architectural correction. Do not replace it with `FOR NO KEY UPDATE`, a new initial parent probe or a queue-wide serialization mechanism. If another current writer makes this exact order unsafe, capture its lock graph and stop for architectural review rather than selecting a different mechanism silently.

## Dependencies

- `ARCH-054-BACKGROUND-001` — Complete and accepted locked pending-turn capture.

No dependency on ARCH-056 billing/outbound/recovery tasks: their production files are separate.

## Enables

- `ARCH-056-SYSTEM-TEST-001`, once the other implementation prerequisites are Complete.

## Acceptance Criteria

- [ ] Two distinct same-conversation messages both commit once, with sequential version increments and one frozen pending anchor.
- [ ] The second receive blocks before its child INSERT while the first holds the parent lock.
- [ ] A raced duplicate leaves one message and one committed version/pending update; every losing helper mutation rolls back.
- [ ] Injected failure after helper mutation and before/during INSERT leaves no message or partial pending/version/clock state.
- [ ] Old-turn completion, HUMAN transition and audio/text overlap preserve the accepted current-state/version/deadline rules.
- [ ] Existing duplicate ownership validation and post-commit engagement/queue retry remain correct.
- [ ] No provider/Redis operation or additional production locking mechanism is introduced.
- [ ] Real PostgreSQL evidence, original error assertions and cleanup are recorded; a unit mock or unforced Promise.all is not the concurrency proof.
- [ ] Actual emitted error JSON retains the harmless injected original message, Conversation/stage and supplied Prisma code; redaction and a throwing log sink preserve the original business exception and rollback/post-commit semantics.

## Validation

Use actual canonical migrations on disposable PostgreSQL 17 + pgvector and the existing disposable Redis runner. Intercept the real transaction only in test code; delegate each operation to real Prisma so the service boundary, FK and rollback are exercised. Establish independent session IDs and explicit barriers/observed lock waits. Do not use production sleeps. Bound every wait and release all barriers in `finally`.

| Case | Forced boundary | Required observation |
|---|---|---|
| Distinct initial receives | A paused after parent/helper lock; B reaches its parent request | B cannot reach child INSERT; after A commits both messages exist, versions 1 and 2, one deadline |
| Duplicate receive race | Both early duplicate reads miss; A commits; B performs helper then unique INSERT fails | Loser's transaction rolls back; retry returns duplicate; one message/version only |
| Failure before INSERT | Inject original error after real helper update | All helper state rolls back; original exception reaches logger/caller |
| Old completion versus receive | Complete old pending state after pre-read but before new helper lock | New turn opens from current state; MSG-01 does not reappear |
| HUMAN/control transition | Run both parent-lock winner orders | No stale AI pending state/send authorization; current revision preserved |
| Audio completion versus text | Compete on the same parent through real service transactions | First processable input anchors delay; later fragment preserves it |
| Mid-turn setting change | Change delay after first committed fragment | Existing deadline/revision unchanged, including future deadlines |
| Post-commit engagement failure | Inject once after receive commit, then retry | No duplicate message/version; existing-message route can complete subsequent work |

Extend the existing owned `tests/unit/services/conversation.service.test.ts`, `tests/unit/workers/whatsapp.worker.test.ts` and relevant new rollback fixture with real installed Shared `createLogger({serviceName: "moda-messaging-worker", environment: "test", sink})`. Use a distinct harmless message such as `arch056-inbound-fixture-source-failure`; serialize/parse the captured record and assert its original `data.error.message` or the worker's explicit `data.errorMessage`, event, service, stage/available job context, Conversation identity where known and actual injected Prisma code. The caller must receive the same error object. Cover both transaction failure and failure after commit, sink-throws isolation, and a sensitive-text fixture whose credential/PII portions are absent while safe source wording remains. Verify the worker has no second raw Error field that reintroduces the removed text. Do not inject secrets into a real provider or assert that a mock receiving an Error proves its final JSON fields.

Required commands from the Background implementation worktree:

```bash
npx --no-install vitest run tests/unit/services/conversation.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts
node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts tests/integration/arch056-inbound-lock-order.integration.test.ts tests/integration/arch056-inbound-rollback.integration.test.ts
npm run build
npx --no-install eslint src/services/conversation.service.ts src/workers/whatsapp.worker.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/conversation.service.test.ts tests/integration/conversation-turn-scheduling.integration.test.ts tests/integration/arch056-inbound-lock-order.integration.test.ts tests/integration/arch056-inbound-rollback.integration.test.ts tests/integration/helpers/arch056-inbound-fixtures.ts tests/integration/helpers/arch056-inbound-barriers.ts
git diff --check
```

- [ ] Execute the commands and retain actual results; missing infrastructure or skipped required tests leave validation incomplete.
- [ ] Record transaction/session/barrier evidence, affected rows and state before/after rollback, with secret/SQL-parameter redaction.
- [ ] Record test container identities and complete cleanup, plus prepared worktree/branch/submodule provenance.

## Implementation Notes

Keep new test modules below 300 lines by separating fixture/barrier logic. Existing larger test files need only the named focused edits; no test-framework rewrite. The standalone SQL mechanism experiment from the review can support diagnosis, but it does not replace exercising `ConversationService.receiveMessage` with real migrations. Follow the parent architecture's common logging, execution and evidence contract.

### Stop Condition

If the named transaction has materially changed, a dependency is not accepted, or a fix would require a lock-mode/schema/queue change, stop and return the concrete evidence. After scoped work and required validation pass, complete the report, publish the normal task evidence, set `status: review`, return to `moda_architect` and stop. Do not start another task or broaden into language/receipt work.

## Completion Report

This section belongs to the implementing repository agent. No implementation is recorded by this definition.

### Status

Not Started

### Files Changed

Pending implementation.

### Work Completed

Pending implementation.

### Validation Results

Not run. Record exact commands, exit results, failures, warnings, source/build/schema provenance, scenario evidence and cleanup; do not copy planned checks as completed results.

### Deviations

None at definition time. Record actual deviations and their architect disposition before review.

### Assumptions

The reviewed snapshot and accepted prerequisite contracts are the definition baseline. Recheck the real current checkout and task state at launch.

### Unresolved Issues

Pending implementation evidence. Preserve the task's explicit held/deferred and blocked-policy boundaries.

### Architectural Concerns

Return changes to ownership, contracts, schema, transaction boundaries, durable-state semantics, queue behavior, security or another repository to moda_architect before expanding scope.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Pending

### Review Notes

Awaiting an implementation submission and its evidence.

### Reviewed Files

No implementation submitted.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

Pending review against the parent architecture, task allowlist, interface contracts, repository boundaries and failure requirements.

### Follow-up

Pending implementation review; no enabled task may be started by this task's executor.
