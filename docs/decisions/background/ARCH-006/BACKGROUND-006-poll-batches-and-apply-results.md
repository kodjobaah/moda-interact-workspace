---
id: ARCH-006-BACKGROUND-006
architecture_id: ARCH-006
title: Poll OpenAI batches in minutes and apply translation results idempotently
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 45
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-006-BACKGROUND-005
enables:
  - ARCH-006-BACKGROUND-007
created: 2026-09-05
updated: 2026-09-06T18:50:51Z
---
# ARCH-006-BACKGROUND-006: Poll OpenAI batches in minutes and apply translation results idempotently

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Implement provider completion polling and replay-safe result application, including message availability and pending-response transitions, without relying on webhooks.

## Context

Polling is deliberately minute-scale. Poll jobs may be lost, duplicated or stale; durable `nextPollAt` and `pollSequence` decide whether a job is current. Provider completion and Moda result application are separate durable phases so a crash between them is recoverable.

## Scope

`translation-batch-poll` and `translation-batch-results` processors and their DB transitions.

## Out of Scope

- Batch create.
- Startup/periodic reconciliation scans.
- Admin manual reconciliation request creation.
- UI.
- Provider webhook.

## Requirements

Poll behavior:

- Validate shared payload and load Batch.
- Ignore stale poll job when payload sequence != durable `pollSequence` or Batch is terminal.
- Retrieve provider state through adapter.
- Provider retrieve is read-only: on transient transport/429/5xx failure, leave the provider lifecycle nonterminal, persist bounded poll-failure metadata as available, advance `nextPollAt` using configurable minute backoff, and retry via the next deterministic poll/reconciliation. Do not mark translations FAILED merely because one poll request failed.
- If provider state is still non-terminal, transactionally set `lastPolledAt`, increment sequence, set `nextPollAt = now + configurable minute interval`, then best-effort enqueue the next deterministic delayed poll.
- On provider completed, persist output/error file IDs and `PROVIDER_COMPLETED`, then best-effort enqueue deterministic results work.
- On a known provider Batch terminal failure (`FAILED`/`EXPIRED`/`CANCELLED`) or per-request failure in an otherwise completed Batch, retain the failed Batch/item history. Classify each affected translation failure as retryable or terminal. Retryable translations may be returned to `PENDING`, `currentBatchId=null`, `nextAttemptAt=<minute backoff>` and increment `retryCount` while below configurable `TRANSLATION_MAX_AUTO_RETRIES`; they will be assembled into a **new** logical Batch. When the bound is exhausted or the failure is non-retryable, persist translation `FAILED` and require durable Admin reconciliation for another attempt. Never reuse a known terminal provider Batch and never delete history.

Result behavior:

- Read output through adapter and map each `custom_id` to the unique expected historical Batch item, then to its durable translation. Do not assume provider `custom_id` is stable across retry Batches.
- Validate translation result is non-empty and belongs to the expected Batch item/target.
- Apply each translation idempotently; already AVAILABLE translation is skipped.
- A worker crash halfway through a Batch must be safely replayable.
- For outbound ADMINISTRATIVE/SYSTEM required translation: set message `AVAILABLE` + `availableAt` only when target translation is AVAILABLE.
- For ADMINISTRATIVE availability, update `lastAdministrativeMessageAt` and clear `needsAdminResponse` only if current `merchantMessageVersion == respondsThroughMerchantVersion`; a newer merchant message keeps it true.
- SYSTEM never clears pending support.
- MERCHANT original remains AVAILABLE even if its admin translation fails.
- Mark logical Batch COMPLETED only after every expected item is durably terminal/applied.


### Shared queue worker topology

`merchant-communications` is one BullMQ queue containing multiple job names. This task owns its job-name processor/handler only. **Do not instantiate a dedicated `new Worker(MERCHANT_COMMUNICATIONS_QUEUE_NAME, ...)` for this job name.** Multiple per-job Workers on one queue compete for all queue jobs and can steal/fail work owned by another processor. `ARCH-006-BACKGROUND-007` owns the single process-level Worker/router and registers the accepted handlers by `job.name`. Horizontal scale is achieved by running multiple identical router-worker processes, each capable of every registered merchant-communications job.

## Work Items

- [x] Implement current-sequence poll processor and minute-based reschedule.
- [x] Persist provider completion separately as `PROVIDER_COMPLETED`.
- [x] Implement deterministic result processor with strict custom-id membership validation.
- [x] Apply results transactionally/idempotently per translation.
- [x] Implement outbound message availability and admin response-boundary transition.
- [x] Handle transient poll errors with minute-scale read retry and no false translation failure.
- [x] Handle Batch/per-request terminal outcomes with bounded automatic retry for retryable translations and durable FAILED after exhaustion/non-retryable error.
- [x] Add stale-poll, duplicate-results, partial-crash replay and newer-merchant-message race tests.

## Interfaces / Contracts

Inputs: shared `translation-batch-poll` and `translation-batch-results` jobs.

Minute configuration must be explicit (for example `TRANSLATION_BATCH_POLL_INTERVAL_MINUTES`) and validated as a positive bounded integer. No webhook endpoint is introduced.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-BACKGROUND-007`

## Acceptance Criteria

- [x] Polling uses minutes, not seconds.
- [x] Stale/duplicate poll jobs do not cause duplicate provider work.
- [x] A transient OpenAI poll/read failure reschedules safely in minutes and does not fail the translation.
- [x] Retryable known-terminal Batch/item failures are automatically retried only up to the configured bound; exhausted/non-retryable failures become durable `FAILED`.
- [x] Lost next-poll enqueue remains reconstructible from DB.
- [x] Provider completion survives a crash before result application.
- [x] Partial result processing can replay without duplicate business transitions.
- [x] Admin reply clears pending only through its snapshot boundary and never clears a newer merchant message.
- [x] SYSTEM translation never clears pending support.
- [x] Original message body is never overwritten.

## Validation

Focused polling/result/race tests plus repository-declared validation and `git diff --check`.

## Implementation Notes

Keep polling/result processing together because they form one provider-completion lifecycle and share the same Batch state, but do not add the global recovery scanner here.

## Completion Report

### Status

Ready for Review

### Files Changed

- [moda-interact-background/src/domain/translation-batch.ts](../../../../moda-interact-background/src/domain/translation-batch.ts)
- [moda-interact-background/src/services/translation-batch-poll.service.ts](../../../../moda-interact-background/src/services/translation-batch-poll.service.ts)
- [moda-interact-background/src/services/translation-batch-results.service.ts](../../../../moda-interact-background/src/services/translation-batch-results.service.ts)
- [moda-interact-background/src/workers/translation-batch-poll.worker.ts](../../../../moda-interact-background/src/workers/translation-batch-poll.worker.ts)
- [moda-interact-background/src/workers/translation-batch-results.worker.ts](../../../../moda-interact-background/src/workers/translation-batch-results.worker.ts)
- [moda-interact-background/tests/unit/services/translation-batch-poll.service.test.ts](../../../../moda-interact-background/tests/unit/services/translation-batch-poll.service.test.ts)
- [moda-interact-background/tests/unit/services/translation-batch-results.service.test.ts](../../../../moda-interact-background/tests/unit/services/translation-batch-results.service.test.ts)
- [moda-interact-background/tests/unit/services/translation-batch-lifecycle.test.ts](../../../../moda-interact-background/tests/unit/services/translation-batch-lifecycle.test.ts)

### Work Completed

- Poll handlers validate the shared job contracts, ignore stale/terminal sequences, keep provider reads outside transactions, persist minute-based sequence advancement, and enqueue deterministic follow-up poll/results jobs only after durable state changes.
- Provider completion is recorded as `PROVIDER_COMPLETED` before result application.
- Result processing consumes complementary provider output/error files, resolves exact historical `providerCustomId` membership, applies each translation idempotently, and marks a logical Batch complete only after every item is available or terminal.
- Administrative availability uses the merchant-version snapshot boundary; SYSTEM translations never clear support pending state, merchant originals remain available, and immutable `originalBody` is not changed.
- Known terminal Batch/item failures use bounded automatic retry; exhausted or non-retryable failures become durable `FAILED` while historical Batch rows remain retained.
- Terminal Batch retry mutation is guarded by the `SUBMITTED + pollSequence` compare-and-set; duplicate/stale terminal polls do not mutate translations.
- Result application requires the translation to remain `PENDING` and owned by the historical Batch; replay after retry reassignment or after a committed item outcome is a no-op, while Batch completion checks historical ownership rather than global `PENDING` status.
- Merchant-facing availability is driven only by the required display-language translation; additional translations cannot block or independently trigger availability or the administrative pending-response transition.
- Per-request `http-400/401/403/404/422` failures are terminal while `http-429` and `http-5xx` failures remain retryable.
- Attempt 3 removed the duplicate failed-result SQL predicate, guarded failed-result and terminal-item message transitions by affected-row ownership, and returns a stale result when terminal Batch CAS ownership is lost.

### Validation Results

- `npm exec vitest run tests/unit/services/translation-batch-assembly.service.test.ts tests/unit/services/translation-batch-submit.service.test.ts tests/unit/services/translation-batch-poll.service.test.ts tests/unit/services/translation-batch-results.service.test.ts tests/unit/services/translation-batch-lifecycle.test.ts tests/unit/providers/translation.provider.test.ts` - 6 files, 45 tests passed.
- `npm run test:unit` - 210 passed, 3 pre-existing failures in unrelated recovery-routing/pending-recovery tests.
- `npm run build` - passed.
- `npm run prisma:validate` - passed.
- Touched-file diagnostics - no errors found.
- `git diff --check` - passed.
- Attempt 3 focused correction suite - 3 files, 21 tests passed.
- Attempt 3 complete translation validation slice - 6 files, 47 tests passed.
- Attempt 3 build - passed.
- Attempt 3 Prisma validation - passed.
- Attempt 3 touched-file diagnostics - no errors found.
- Attempt 3 `git diff --check` - passed.

### Deviations

No schema, migration, queue-topology, webhook, or reconciliation-worker changes were made. The central merchant-communications Worker/router remains owned by `ARCH-006-BACKGROUND-007`.

### Assumptions

Provider output and error files are treated as complementary result streams for a completed Batch; their custom IDs are expected to cover the historical Batch items exactly once.

### Unresolved Issues

The repository-wide unit suite retains three unrelated recovery-service failures from the prior validation; they do not involve the polling/results files or translation lifecycle tests. No repository-wide rerun was needed for this bounded correction.

### Architectural Concerns

None. The bounded Attempt 3 correction remained within the five architect-authorized implementation/test files.

## Architect Review

### Attempt 1 Decision — 2026-09-06

Not accepted. Return the same task to `ready` for a bounded Attempt 2 correction.

The polling/result lifecycle is substantially implemented, but independent review found replay and message-availability defects at the exact failure boundaries this task is intended to make deterministic.

#### Blocking findings

1. **Retryable provider-item failure is not replay-safe and can consume the retry budget repeatedly.** `applyResult()` clears `currentBatchId` but leaves the translation `PENDING`; a replay of the same historical Batch still processes that item because it only skips `AVAILABLE`. The retry count can therefore be incremented again on every result-job replay. `completeBatch()` also treats that deliberately re-pended translation as unapplied because it tests global translation status instead of whether the historical Batch item has already been consumed. A single retryable provider failure can consequently cause the results job to fail/replay until the auto-retry budget is exhausted without a new provider Batch ever running.

2. **Old Batch output is not guarded by current Batch ownership.** A historical result update is not constrained by `currentBatchId = <historical batch>`. If a retryable translation has already been claimed into a newer logical Batch, replay of the older result must not mutate it.

3. **Additional translations incorrectly participate in merchant-facing availability.** Admin can request additional target-language translations for an ADMINISTRATIVE or SYSTEM message. The current `NOT EXISTS (... status <> AVAILABLE)` rule requires every translation on the message to be AVAILABLE, so an unrelated additional translation can block the required display-language result. Conversely, an additional translation completion can execute the ADMINISTRATIVE thread response-boundary update even when the merchant-required display translation has not made the message AVAILABLE. The required translation is the one whose `targetLanguageTag` matches the message's persisted `displayLanguageTag`; additional translations must neither gate nor trigger merchant-facing availability.

4. **Terminal Batch poll application is not guarded after the Batch CAS.** `persistTerminalBatch()` mutates translation retries even when the guarded Batch status/sequence update affected zero rows. Two duplicate terminal poll deliveries can therefore increment the same retryable translation more than once. Translation mutation must occur only when this invocation successfully owns the `SUBMITTED + pollSequence` terminal transition.

5. **Per-request HTTP failure classification is incomplete.** Provider output encodes non-2xx request failures as values such as `http-400`, `http-401`, `http-403`, `http-422`, `http-429`, and `http-500`. The current textual regex treats all of those numeric codes as retryable. At minimum, 429/5xx (and other explicitly documented transient cases) may retry, while 400/401/403/404/422 must be terminal/non-retryable.

### Attempt 2 Correction Contract

This is a correction of `ARCH-006-BACKGROUND-006`, not a new capability.

#### Allowed implementation files

- `moda-interact-background/src/services/translation-batch-poll.service.ts`
- `moda-interact-background/src/services/translation-batch-results.service.ts`
- `moda-interact-background/tests/unit/services/translation-batch-poll.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-results.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-lifecycle.test.ts`

`translation-batch.ts`, the poll/results handler files, provider adapter, schema/migrations, queue topology and `BACKGROUND-007` are read-only for this correction. If a correction genuinely requires one of those boundaries to change, stop and return `blocked` rather than expanding scope.

#### Required corrections

- Make the terminal Batch transition a real compare-and-set boundary. If the `SUBMITTED + pollSequence` Batch update did not affect exactly one row, treat the invocation as stale and do **not** mutate any translation/message retry state.
- Tie result application to the historical Batch ownership. An item may mutate a translation only while that translation is still `PENDING` and `currentBatchId` equals the historical Batch being applied. Once that Batch outcome clears/replaces `currentBatchId`, replay of that historical result is a no-op.
- Permit a retryable failed item to be durably returned to `PENDING` for a **new** logical Batch while allowing the old logical Batch to become `COMPLETED` once every historical item outcome has been consumed. Do not use global `PENDING` status alone as evidence that the old Batch is unfinished.
- Preserve partial-crash replay: if item 1 is committed and the worker crashes before item 2/Batch completion, replay must not increment item 1's retry count again and must safely finish the remaining items.
- Protect newer attempts: old Batch result replay must not overwrite or clear `currentBatchId` after the translation has been assigned to another logical Batch.
- For ADMINISTRATIVE/SYSTEM messages, merchant-facing availability must be driven only by the required translation where `translation.targetLanguageTag == message.displayLanguageTag`. Additional translations must not block that transition and must not independently trigger it.
- Update the ADMINISTRATIVE thread response boundary only when the required translation actually transitions the outbound message to `AVAILABLE`. Preserve the `merchantMessageVersion == respondsThroughMerchantVersion` guard. SYSTEM must never alter `needsAdminResponse`.
- Allow a successfully recovered required translation to move an outbound message from `FAILED` back to `AVAILABLE` where appropriate; do not require unrelated additional translations to succeed first.
- Classify per-request `http-*` failures explicitly enough that known client/auth/validation failures (`400`, `401`, `403`, `404`, `422`) are terminal and transient capacity/server failures (`429`, `5xx`; plus any deliberately supported transient codes) are retryable.

#### Required focused regressions

- duplicate/stale terminal poll CAS affects zero rows -> no translation retry mutation;
- retryable per-item failure increments retry count exactly once, clears old `currentBatchId`, and permits the old Batch to complete;
- crash/replay after that item commit does not increment the retry count again;
- replay of an old Batch cannot mutate a translation already assigned to a newer Batch;
- successful required display-language translation makes ADMINISTRATIVE/SYSTEM message AVAILABLE even when an unrelated additional translation remains PENDING/FAILED;
- successful additional translation alone cannot make a PROCESSING outbound message AVAILABLE and cannot clear Admin pending response state;
- ADMINISTRATIVE required result clears pending only through the snapshot boundary; SYSTEM still never clears it;
- `http-429` and `http-5xx` are retryable while `http-400`, `401`, `403`, `404`, and `422` are terminal;
- successful-result replay remains idempotent and `originalBody` remains immutable.

#### Validation

Run the focused translation lifecycle suite, TypeScript/build, Prisma validation, repository diagnostics and `git diff --check`. The three documented unrelated recovery-service failures remain an accepted baseline only if unchanged.

Return only `ARCH-006-BACKGROUND-006` to `review` and STOP. Do not claim or modify `BACKGROUND-007`.


### Attempt 2 Decision — 2026-09-06

Not accepted. Return the same task to `ready` for a bounded Attempt 3 correction.

Attempt 2 fixed the principal replay/availability design, but independent review of the actual SQL found remaining correctness defects that the mock-focused suite did not execute against PostgreSQL.

#### Blocking findings

1. **Per-item failure SQL is syntactically invalid.** The failed-result `UPDATE support."MerchantMessageTranslation"` contains two consecutive `WHERE "id" = ...` clauses. Any provider item failure reaching this branch will fail at PostgreSQL runtime even though the mocked focused tests pass.

2. **A failed-result ownership loss is not respected after the guarded UPDATE.** The failed-result branch does not inspect the affected-row count. If another concurrent worker/retry changes `currentBatchId` after the pre-read, the guarded translation UPDATE can affect zero rows but the code still returns `true`; for terminal ADMINISTRATIVE/SYSTEM failure it can also mark the message `FAILED` even though this historical Batch no longer owns the translation.

3. **Terminal Batch item failure has the same post-guard message-state gap.** `persistTerminalBatch()` correctly guards each translation by `status='PENDING' AND currentBatchId=<batch>`, but it ignores whether that UPDATE affected a row before marking a PROCESSING ADMINISTRATIVE/SYSTEM message `FAILED`. A translation no longer owned by the terminal historical Batch must not drive message state.

4. **CAS loser is not surfaced as stale as required.** The Batch-level terminal CAS now prevents retry mutation when it loses, but `persistTerminalBatch()` returns `void` and `poll()` still reports `{status:'terminal'}`. The Attempt 2 contract explicitly requires a zero-row `SUBMITTED + pollSequence` CAS to be treated as stale. The new regression currently asserts the incorrect terminal result.

The required-display-language availability rule, old-Batch replay ownership check, historical Batch completion rule and HTTP retry classification are otherwise directionally correct and should not be rewritten.

### Attempt 3 Correction Contract

This is a narrow correction of `ARCH-006-BACKGROUND-006`, not a new capability.

#### Allowed files

- `moda-interact-background/src/services/translation-batch-poll.service.ts`
- `moda-interact-background/src/services/translation-batch-results.service.ts`
- `moda-interact-background/tests/unit/services/translation-batch-poll.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-results.service.test.ts`
- `moda-interact-background/tests/unit/services/translation-batch-lifecycle.test.ts` only if an existing lifecycle fixture requires adjustment.

All provider, schema/migration, worker/router, queue-contract and `BACKGROUND-007` files remain read-only.

#### Required corrections

- Remove the duplicate `WHERE` and make the failed-result translation UPDATE valid PostgreSQL.
- Capture the failed-result translation UPDATE affected-row count. If it is not exactly one, return `false` and do not mutate message/thread state.
- In terminal Batch failure handling, mutate outbound message failure state only when the corresponding guarded translation UPDATE affected exactly one row.
- Make the terminal Batch CAS return ownership to `poll()`. A zero-row `SUBMITTED + pollSequence` CAS must return `{status:'stale'}` and must not mutate translations/messages.
- Preserve the accepted Attempt 2 fixes: old historical output cannot mutate newer Batch ownership; retryable historical outcomes can be consumed while the old Batch completes; only the required display-language translation can make outbound messages AVAILABLE; SYSTEM never clears pending support; HTTP 400/401/403/404/422 are terminal and 429/5xx retryable.

#### Required regressions

- failed provider item executes one syntactically valid guarded translation UPDATE;
- failed-result guarded UPDATE returning `0` yields `applied: 0` and performs no outbound message/thread mutation;
- terminal Batch CAS returning `0` returns `stale`, with no translation/message mutation;
- terminal Batch translation UPDATE returning `0` does not mark an outbound message FAILED;
- existing historical replay, required-language availability, retry classification, successful replay and original-body immutability regressions remain passing.

#### Validation

Run the focused translation lifecycle suite, build/TypeScript, Prisma validation, repository diagnostics and `git diff --check`. The three documented unrelated recovery failures remain acceptable only if unchanged.

Return only `ARCH-006-BACKGROUND-006` to `review` and STOP. Do not claim or modify `BACKGROUND-007`.

### Attempt 3 Decision — 2026-09-06

Accepted by `moda_architect`. `ARCH-006-BACKGROUND-006` is Complete.

Independent review confirmed that Attempt 3 satisfies the bounded correction contract:

- the failed provider-item SQL contains one valid guarded `WHERE` predicate;
- failed-result mutation checks the affected-row count before any outbound message/thread transition;
- terminal Batch item handling marks an outbound message FAILED only when the historical Batch still owns and updates that translation;
- a zero-row `SUBMITTED + pollSequence` terminal Batch compare-and-set returns `stale` and performs no translation/message mutation;
- the accepted Attempt 2 protections remain intact: historical replay cannot overwrite a newer Batch, retryable outcomes can be consumed while the old logical Batch completes, merchant-facing availability is driven only by the required display-language translation, SYSTEM never clears pending support, and HTTP 400/401/403/404/422 vs 429/5xx retry classification remains explicit;
- the Attempt 3 diff is confined to the architect-authorized poll/results services and focused tests; `BACKGROUND-007` remained untouched.

Validation evidence recorded by the repository agent: 47 focused translation tests passed, build passed, Prisma validation passed, repository diagnostics reported no issues, and `git diff --check` passed. The three documented unrelated recovery-service failures remain outside this task.

This acceptance releases `ARCH-006-BACKGROUND-007` to Ready.

