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
status: complete
priority: 20
executor: null
claimed_at: null
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

Definition revision: 2. Materialised on the canonical parent task branch. Attempt 1 was prepared by the launcher after rechecking the `ARCH-054-BACKGROUND-001` dependency; the durable parent claim is `85f053e04d1913dd35489e12e8fd4a851586c984`. Implementation was submitted for review at `a918c85` on the mirrored Background task branch and accepted by moda_architect below. No merge has occurred.

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

- [x] Reorder the existing helper call in the named transaction without changing its semantics or boundary.
- [x] Update focused unit expectations and the existing rollback fixture.
- [x] Add deterministic real-service concurrency and duplicate/error rollback tests using the named test-only helpers.
- [x] Verify preserved control/audio/pending behavior and original-error propagation.
- [x] Verify the actual installed Shared logger emits the original safe message and accurate failure stage; use its real capture sink, not only a mocked logger method.
- [x] Correct the existing worker failure/error projections and prove that their emitted records retain the safe original message without reintroducing removed sensitive text.
- [x] Record the lock schedule and row outcomes, successful-path call comparison and increased rolled-back duplicate work.

## Interfaces / Contracts

No signature, public queue payload, Shared package or database schema change. Preserve the existing helper result `{version:number, scheduleAi:boolean}` and receive result. The existing versioned queue identity and normal caller routing remain unchanged.

The selected order is an architectural correction. Do not replace it with `FOR NO KEY UPDATE`, a new initial parent probe or a queue-wide serialization mechanism. If another current writer makes this exact order unsafe, capture its lock graph and stop for architectural review rather than selecting a different mechanism silently.

## Dependencies

- `ARCH-054-BACKGROUND-001` — Complete and accepted locked pending-turn capture.

No dependency on ARCH-056 billing/outbound/recovery tasks: their production files are separate.

## Enables

- `ARCH-056-SYSTEM-TEST-001`, once the other implementation prerequisites are Complete.

## Acceptance Criteria

- [x] Two distinct same-conversation messages both commit once, with sequential version increments and one frozen pending anchor.
- [x] The second receive blocks before its child INSERT while the first holds the parent lock.
- [x] A raced duplicate leaves one message and one committed version/pending update; every losing helper mutation rolls back.
- [x] Injected failure after helper mutation and before/during INSERT leaves no message or partial pending/version/clock state.
- [x] Old-turn completion, HUMAN transition and audio/text overlap preserve the accepted current-state/version/deadline rules.
- [x] Existing duplicate ownership validation and post-commit engagement/queue retry remain correct.
- [x] No provider/Redis operation or additional production locking mechanism is introduced.
- [x] Real PostgreSQL evidence, original error assertions and cleanup are recorded; a unit mock or unforced Promise.all is not the concurrency proof.
- [x] Actual emitted error JSON retains the harmless injected original message, Conversation/stage and supplied Prisma code; redaction and a throwing log sink preserve the original business exception and rollback/post-commit semantics.

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

- [x] Execute the commands and retain actual results; missing infrastructure or skipped required tests leave validation incomplete.
- [x] Record transaction/session/barrier evidence, affected rows and state before/after rollback, with secret/SQL-parameter redaction.
- [x] Record test container identities and complete cleanup, plus prepared worktree/branch/submodule provenance.

## Implementation Notes

Keep new test modules below 300 lines by separating fixture/barrier logic. Existing larger test files need only the named focused edits; no test-framework rewrite. The standalone SQL mechanism experiment from the review can support diagnosis, but it does not replace exercising `ConversationService.receiveMessage` with real migrations. Follow the parent architecture's common logging, execution and evidence contract.

### Stop Condition

If the named transaction has materially changed, a dependency is not accepted, or a fix would require a lock-mode/schema/queue change, stop and return the concrete evidence. After scoped work and required validation pass, complete the report, publish the normal task evidence, set `status: review`, return to `moda_architect` and stop. Do not start another task or broaden into language/receipt work.

## Completion Report

Implementation submission by `moda_background` (`copilot`), Attempt 1. This report is owned by the implementing repository agent; the Architect Review section below remains architect-owned and unchanged.

### Status

Complete. Implementation branch commit `a918c85` is pushed to `origin/task/ARCH-056-BACKGROUND-001`. Architect acceptance is recorded below; no merge has occurred.

### Files Changed

Implementation repository files (nine task-owned paths):

- `src/services/conversation.service.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/conversation.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/integration/conversation-turn-scheduling.integration.test.ts`
- `tests/integration/arch056-inbound-lock-order.integration.test.ts` (created, 215 lines)
- `tests/integration/arch056-inbound-rollback.integration.test.ts` (created, 198 lines)
- `tests/integration/helpers/arch056-inbound-fixtures.ts` (created, 82 lines)
- `tests/integration/helpers/arch056-inbound-barriers.ts` (created, 134 lines)

### Work Completed

- Moved the existing `recordProcessableInbound` call to precede inbound `ConversationMessage.create` within the same Prisma transaction. Message creation, language persistence and monotonic clocks remain in that transaction; engagement remains post-commit. No production schema, queue, retry or lock-mode change was made.
- Added a local bounded stage (`atomic-receive` / `post-commit-engagement`) and safe original-error projection in `ConversationService`. Service logs retain safe source name/message, Conversation/provider identity where available, and actual Prisma code/client version; the original thrown object is preserved.
- Corrected the worker failed/error callback projections so raw outer errors cannot overwrite redacted fields. Existing event names, job context, routing and retry behavior remain unchanged. Unit tests capture JSON records from the installed Shared logger and cover source wording, supplied metadata, sensitive spans, and throwing sinks.
- Added real PostgreSQL barriers and observed `pg_stat_activity` lock waits. Two distinct receives serialize before the second child insert and commit versions 1/2 with one deadline. A raced duplicate with both early reads forced to miss leaves one message/version; the losing helper mutation rolls back on P2002 and the retry returns the committed duplicate. An injected post-helper failure leaves no message, version, pending snapshot or clock update and emits the same original error.
- Added forced old-turn completion after the receive pre-read, both HUMAN transition lock-winner orders with the required audit event, and real audio-completion/text-receive overlap. Assertions cover the current locked state, HUMAN clearing/watermark behavior, blocked child insert, sequential versions and frozen deadline. Existing mid-turn settings coverage confirms a later setting change does not alter the first committed deadline/revision.
- Successful distinct-message call-site comparison: no database operation was added; the existing locked helper work was reordered before the child insert. On the raced duplicate/error path, the losing transaction now performs the helper update (and applicable pending-setting read) before the unique insert failure; those writes are transactionally rolled back. This path-specific increase is expected and verified rather than presented as a universal zero-delta claim.
- Test-only transaction interception delegates to real Prisma. Waits are bounded and barriers release in `finally`; the test wrapper uses a 30-second interactive-transaction ceiling and individual barriers/lock observations are bounded at 10 seconds. New integration modules comply with the 300-line limit.

### Validation Results

- `npx --no-install vitest run tests/unit/services/conversation.service.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/conversation-ai-delay/pending-turn-repository.test.ts tests/unit/services/inbound-whatsapp-audio.service.test.ts` — passed, 4 files / 80 tests.
- `node scripts/test-integration.mjs tests/integration/conversation-turn-scheduling.integration.test.ts tests/integration/arch056-inbound-lock-order.integration.test.ts tests/integration/arch056-inbound-rollback.integration.test.ts` — passed, 3 files / 10 tests against the disposable PostgreSQL 17 + pgvector and Redis runner using canonical migrations. The final instrumented run passed; a prior run had one transient failure in the existing quiet-window coalescing assertion (`[1, 3]` observed instead of `[3]`), which passed in isolation and in subsequent full runs. No test was skipped in the integration runner.
- `npm run build` — passed; Prisma Client 6.19.3 generated from `database/prisma/schema.prisma`, then TypeScript compilation completed successfully.
- `npx --no-install eslint src/services/conversation.service.ts src/workers/whatsapp.worker.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/conversation.service.test.ts tests/integration/conversation-turn-scheduling.integration.test.ts tests/integration/arch056-inbound-lock-order.integration.test.ts tests/integration/arch056-inbound-rollback.integration.test.ts tests/integration/helpers/arch056-inbound-fixtures.ts tests/integration/helpers/arch056-inbound-barriers.ts` — passed.
- `git diff --check` — passed. New integration module line counts: 215, 198, 82 and 134.
- PostgreSQL evidence: distinct receive B was observed waiting on a PostgreSQL lock while A held the Conversation parent; B had not reached its child insert. After release both rows committed once at versions 1 and 2, sharing one frozen pending anchor. Duplicate race: both early reads missed; one insert committed, the other failed P2002 after helper work; one row/version remained and retry returned duplicate. Injected failure: zero message rows and all pending/version/clock fields remained at their pre-transaction values. Old completion, HUMAN-first/receive-first and audio-first/text-first schedules all passed with bounded barriers and final row/state assertions.
- Disposable infrastructure identities observed via Docker events during the final passing integration run: PostgreSQL `pgvector/pgvector:pg17`, container `moda-test-postgres-994ad8bf9c4e40a8aa7bccbc8397db77` (ID `4972b1b31f14680937076d278d0eff1e725c57fd714c5b68735070bef6ff4f96`) and Redis `redis:7.4.2-alpine`, container `moda-test-redis-59026bf51bc94e02b61c0e80396faa55` (ID `b22028eae97e1fa0b18f4ed4051fae5c9b1b1fb294964efd9f39f276810243c`); PostgreSQL `moda-test-postgres-5124b2fdda9344169669999c91afb5c0` (ID `8fc6887a9715fd168fcaf8841a9a1e8574d1096582dea613f9118578c79a6614`) and Redis `moda-test-redis-d15c2899d25440639910a5fc464c5333` (ID `ee732c126250c6fcd8724e411be948362a0da9bf3e647b9f64e4768d7858df08`). The disposable runner emitted kill/die/destroy events for all four; a subsequent `docker ps -a` showed no test containers. Pre-existing unrelated MariaDB and Portainer containers remained untouched.
- Runtime provenance: macOS, Node.js 24.21.0, lockfile-pinned npm dependencies, Prisma 6.19.3, Vitest 4.1.11. `npm ci` emitted an existing audit summary of 40 advisories (27 moderate, 13 high); dependency remediation was outside scope and no manifest/lockfile was changed.
- Prepared execution provenance: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-056-BACKGROUND-001`, branch `task/ARCH-056-BACKGROUND-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-056-BACKGROUND-001`, same branch. Launcher claim commit `85f053e04d1913dd35489e12e8fd4a851586c984` was pushed before implementation. Recursive `database` submodule was initialized at the recorded commit `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Shared workspace/default implementation checkouts were not switched for task work; no other task worktree was reused.
- Implementation commit `a918c85` was pushed explicitly to `origin/task/ARCH-056-BACKGROUND-001`. The local branch initially tracked `origin/main`; the default GitKraken push refused the mismatched upstream and no main ref was updated. The task branch was pushed by explicit same-name refspec.

### Deviations

No production-scope or contract deviation. The real PostgreSQL HUMAN transition coverage and old-turn race were added to the existing scheduling integration module to keep each newly created integration module under 300 lines. The test-only transaction wrapper gives barrier-driven schedules a bounded 30-second interactive transaction timeout; production transaction configuration is unchanged. The one transient quiet-window test failure is disclosed above and passed on isolation and repeated full runs.

### Assumptions

The launcher rechecked task identity and the completed `ARCH-054-BACKGROUND-001` dependency before claiming Attempt 1. Canonical migration and Prisma schema were used by the disposable integration runner. No provider or Redis I/O was introduced inside the inbound message transaction.

### Unresolved Issues

No known implementation blocker. The existing quiet-window coalescing integration showed one transient timing-sensitive failure before passing in isolation and on subsequent full runs; architect review may decide whether that test’s timing assumption merits separate follow-up. Existing npm audit advisories were not remediated because dependency upgrades are out of scope.

### Architectural Concerns

None identified. The existing helper and lock mode are reused; transaction ownership, public interfaces, schema and queue behavior are unchanged. Awaiting `moda_architect` review; this report does not self-accept the task.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Accepted — Attempt 1 (2026-11-04). The stale executor claim is cleared; task status is Complete.

### Review Notes

- The implementation moves the existing locked pending-turn helper before the child message insert while preserving one transaction for pending state, message, language and clocks. Post-commit engagement remains outside the transaction.
- The real PostgreSQL barrier evidence demonstrates that the second receive waits on the parent before its child insert; duplicate and injected-failure evidence verifies losing mutations roll back.
- The changed error projections preserve the original thrown object and safe source message while recording the failure stage and supplied Prisma metadata. The worker callback no longer reintroduces raw errors after redaction.
- The disclosed transient quiet-window coalescing failure passed in isolation and subsequent full runs. It does not block acceptance; no new blocker was found in the reviewed scope.

### Reviewed Files

- `src/services/conversation.service.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/conversation.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/integration/conversation-turn-scheduling.integration.test.ts`
- `tests/integration/arch056-inbound-lock-order.integration.test.ts`
- `tests/integration/arch056-inbound-rollback.integration.test.ts`
- `tests/integration/helpers/arch056-inbound-fixtures.ts`
- `tests/integration/helpers/arch056-inbound-barriers.ts`

### Validation Reviewed

Reviewed the implementation report's results: focused unit suite (80 tests), PostgreSQL/Redis integration suite (10 tests, no skips), build, changed-file ESLint and `git diff --check` all passed. These commands were not rerun during review. The report records the transient earlier quiet-window failure and later passing reruns.

### Architecture Conformance

Conforms to ARCH-056 revision 2, the task allowlist and the existing conversation persistence contract. No schema, queue, lock-mode or public-interface change was introduced. The original exception identity and truthful atomic/post-commit stage are preserved.

### Follow-up

`ARCH-056-SYSTEM-TEST-001` remains Pending because its other implementation prerequisites are not complete. This acceptance does not authorize a merge to `main` or start another task.
