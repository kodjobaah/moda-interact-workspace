---
id: ARCH-006-BACKGROUND-004
architecture_id: ARCH-006
title: Assemble pending translations into durable logical batches
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 35
executor: copilot
claimed_at: 2026-09-06T14:48:37Z
attempt: 2
depends_on:
  - ARCH-006-BACKGROUND-001
  - ARCH-006-SHARED-004
enables:
  - ARCH-006-BACKGROUND-005
created: 2026-09-05
updated: 2026-09-06T16:05:00Z
---

# ARCH-006-BACKGROUND-004: Assemble pending translations into durable logical batches

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed translation reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Consume translation-dispatch work and atomically assign eligible PENDING translations to one durable READY TranslationBatch, preserving historical membership and preventing concurrent double-claim.

## Context

This task is intentionally separated from provider submission. Its only runtime outcome is: durable PENDING translations become members of exactly one current READY logical batch, then a deterministic submit job is requested best-effort.

## Scope

`translation-dispatch` BullMQ consumer/service and DB transaction(s) for bounded batch assembly in `moda-interact-background`.

## Out of Scope

- OpenAI Batch create.
- Polling/results.
- Reconciliation scans/runtime entrypoint.
- UI/server message creation.
- Provider webhook.

## Requirements

Process strict shared dispatch payloads. Load authoritative translation/message from PostgreSQL; never trust text in Redis.

Only eligible `PENDING` translations with no `currentBatchId` may be claimed. The claim must be a short PostgreSQL transaction that selects a bounded stable-order page with row locks using `FOR UPDATE SKIP LOCKED` (or the repository's proven equivalent with the same semantics). Prisma raw SQL is permitted only when required to express this lock and must be parameterized. Do not first lock only the dispatch payload's translation and then collect more rows; claim the whole bounded candidate set in one locking query so concurrent assemblers select disjoint rows.

Within that same transaction, create one logical `MerchantTranslationBatch` in `READY`, create historical Batch items and set each selected translation's `currentBatchId`. Each new historical Batch item must receive a provider custom ID unique to that Batch item/attempt; retrying a translation in a later logical Batch must not reuse the earlier Batch item custom ID. Commit all membership/pointers together. If any DB step fails, the transaction rolls back and PostgreSQL releases the row locks, leaving the translations eligible for another worker. **Do not perform Redis or OpenAI network calls while these row locks are held.**

Batch aggregation must be bounded and configurable, using values such as `TRANSLATION_BATCH_MAX_REQUESTS` and an optional short collection policy; do not exceed provider limits. Cost discount comes from Batch API, so correctness must not depend on filling a batch. With 20+ workers, concurrent assemblers may create separate batches, but no translation may belong to two current batches.

After commit, ensure/enqueue deterministic `translation-batch-submit` best-effort. DB commit must not be rolled back because Redis enqueue fails.

## Work Items

- [ ] Add dispatch processor using published shared schemas/job IDs.
- [ ] Implement bounded stable-order eligible selection with PostgreSQL `FOR UPDATE SKIP LOCKED` (or proven equivalent) inside one short transaction.
- [ ] Persist logical READY Batch + BatchItem history + currentBatchId pointers atomically.
- [ ] Ensure duplicate dispatch jobs return idempotently when translation is already assigned/terminal.
- [ ] Enqueue deterministic submit work only after commit; isolate Redis failure.
- [ ] Add concurrency tests proving two dispatchers cannot current-assign the same translation twice.

## Interfaces / Contracts

Input: `translation-dispatch {schemaVersion, translationId}`.

Output durable state:

```text
PENDING translation(s), currentBatchId=null
    -> READY TranslationBatch + historical BatchItems + currentBatchId
```

Output execution hint: deterministic `translation-batch-submit` job. Missing submit job is recoverable later from the READY DB state.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-BACKGROUND-005`

## Acceptance Criteria

- [ ] Duplicate dispatch delivery is idempotent.
- [ ] Concurrent dispatch cannot put one translation in two current batches, and blocked rows are skipped rather than serializing the worker fleet.
- [ ] Provider/Redis network calls never occur while translation claim row locks are held.
- [ ] Batch assembly is bounded/configurable.
- [ ] Message body is loaded from DB, never queue payload.
- [ ] Redis enqueue failure after DB commit leaves recoverable READY work.
- [ ] No provider submission occurs in this task.

## Validation

Focused unit/integration/concurrency tests plus repository-declared validation and `git diff --check`.

## Implementation Notes

Luna stop condition: once READY-batch assembly and its deterministic submit hint are correct, stop. Do not “finish the pipeline” in the same task.


### Repository-agent workflow hard stop

SHARED-004 is now architect-accepted Complete and `@modainteract/moda-interact-shared@0.7.1` has been registry/clean-consumer verified. `moda_architect` has returned BACKGROUND-004 to **Ready for Attempt 2**. Execute **only this task**, return it to `review`, and STOP. Do not mark it Complete, do not edit/promote `BACKGROUND-005`, do not update index/architecture readiness, and do not claim another task in the same invocation.

## Architect Correction Requirements

Acceptance is blocked. Attempt 2 is now authorised and is limited to the following corrections:

1. Pin the corrected published shared release recorded by SHARED-004 (`0.7.1`) and remove `src/types/shared-merchant-communications.d.ts`; do not keep a local declaration/runtime substitute for a shared package export.
2. Fix the focused test database double so it exposes `$queryRaw` and `$executeRaw` exactly like the service contract. The current test passes `queryRaw`/`executeRaw` without `$`, so it would fail once the package import blocker is removed.
3. Do not instantiate a dedicated BullMQ `Worker` for only `translation-dispatch` on the shared `merchant-communications` queue. A BullMQ Worker competes for all jobs on its queue; separate per-job-name Workers would steal and fail `translation-batch-submit`, poll, results or reconcile jobs. BACKGROUND-004 must expose a dispatch processor/handler only. BACKGROUND-007 owns the process-level queue Worker/router that dispatches by `job.name`.
4. Add real PostgreSQL concurrency/integration validation for the `FOR UPDATE ... SKIP LOCKED` claim. Unit mocks are not sufficient. The evidence must run two or more concurrent assembly transactions and prove disjoint current assignment with no duplicate BatchItem/currentBatch ownership. The test may be environment-gated, but architect acceptance requires evidence of at least one passing run against a disposable/test PostgreSQL database containing the DATABASE-002 schema.
5. Preserve the existing short-transaction rule: no Redis/OpenAI call while row locks are held; enqueue remains post-commit best effort.

Do not implement BACKGROUND-005/006/007 while correcting this task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/domain/translation-batch.ts` - shared merchant-communications queue and dispatch contract surface.
- `moda-interact-background/src/services/translation-batch-assembly.service.ts` - bounded transactional assembly and post-commit submit enqueue.
- `moda-interact-background/src/types/shared-merchant-communications.d.ts` - local type declaration for the malformed published shared node export.
- `moda-interact-background/src/workers/translation-dispatch.worker.ts` - strict dispatch BullMQ consumer.
- `moda-interact-background/tests/unit/services/translation-batch-assembly.service.test.ts` - focused transaction ordering, enqueue failure and idempotency tests.
- This task document - claim, implementation report and review status.

### Work Completed

- Added a bounded, stable-order PostgreSQL claim using parameterized raw SQL with `FOR UPDATE OF t SKIP LOCKED`.
- Added atomic READY Batch creation, historical BatchItem creation, and `currentBatchId` updates within one transaction.
- Loads source text through the authoritative support-message join rather than trusting dispatch payload text.
- Generates a new provider custom ID per historical Batch item using the new logical Batch ID.
- Requests deterministic submit work only after the transaction callback resolves; enqueue errors are isolated from committed state.
- Added strict published dispatch payload parsing and a worker that rejects job names owned by later processors.
- Added injectable database/queue boundaries for focused tests.

### Validation Results

- `npm exec tsc -- --noEmit` - passed after adding a narrow declaration shim for the malformed shared node export.
- `npm exec vitest run tests/unit/services/translation-batch-assembly.service.test.ts` - blocked at module loading: `@modainteract/moda-interact-shared@0.7.0` exports `./merchant-communications/node` to `./dist/merchant-communications.node.js`, but the published package contains the runtime file at `./dist/merchant-communications/node.js`. The test cannot load the required shared deterministic job-ID helper.

### Deviations

The database submodule remains pinned to the DATABASE-001 revision, so the service uses parameterized SQL rather than unavailable generated DATABASE-002 Prisma delegates. The DATABASE-002 schema/migration exists in the separate database repository working tree but is not committed/published into the background submodule.

### Assumptions

The architect will coordinate a corrected shared `0.7.0` package export (or successor release) and the DATABASE-002 submodule handoff before acceptance.

### Unresolved Issues

The published shared package's `merchant-communications/node` export is not runtime-resolvable. Implementing a local copy of the deterministic helper would violate the shared-contract ownership rule, so focused runtime validation and acceptance are blocked until the shared release is corrected.

### Architectural Concerns

The implementation is intentionally returned for architect review rather than marked complete because the required shared job-ID helper cannot currently be loaded from the published dependency.

## Architect Review

### Review Status

Blocked — architect review 2026-09-06.

### Decision

Not accepted yet. No downstream task is promoted. `ARCH-006-BACKGROUND-005` remains Pending.

### Findings

- The repository agent correctly obeyed the hard-stop workflow: it returned this task to `review`, did not self-complete it, did not promote BACKGROUND-005, and left the architect decision Pending.
- The core SQL uses a bounded stable-order `FOR UPDATE OF t SKIP LOCKED` claim and keeps queue enqueue outside the transaction, which is directionally correct.
- `@modainteract/moda-interact-shared@0.7.0` has a broken runtime/type export for `merchant-communications/node`; the local `.d.ts` shim cannot repair runtime resolution and must not become permanent.
- The focused tests were not runnable because of that package defect. In addition, their transaction double currently exposes `queryRaw`/`executeRaw` rather than `$queryRaw`/`$executeRaw`, so the test harness itself needs correction.
- The task requires concurrency validation proving `SKIP LOCKED` semantics; only mock-based unit tests were added, so that acceptance criterion is still unmet.
- The dedicated `translationDispatchWorker = new Worker(...)` is architecturally unsafe on a queue shared by multiple job names. BACKGROUND-007 owns one process-level `merchant-communications` Worker/router; BACKGROUND-004/005/006 own handlers, not competing per-job Workers.

### Blocking Dependency

`ARCH-006-SHARED-003 -> ARCH-006-SHARED-004` must produce and publish the corrected shared package before BACKGROUND-004 Attempt 2 can be claimed.


### Architect Re-entry Decision — 2026-09-06

SHARED-004 is accepted Complete and the corrected registry artifact `@modainteract/moda-interact-shared@0.7.1` has passed isolated consumer import/execution verification. BACKGROUND-004 is therefore returned from Blocked to Ready for **Attempt 2**. The previous Architect Review remains the historical Attempt 1 decision. The repository agent must claim this task normally (incrementing attempt from 1 to 2), perform only the bounded correction contract, return to `review`, and STOP.

## Attempt 2 Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json` - pinned `@modainteract/moda-interact-shared` to the published `0.7.1` release.
- `moda-interact-background/package-lock.json` - synchronized the `0.7.1` registry tarball and integrity.
- `moda-interact-background/src/types/shared-merchant-communications.d.ts` - removed the local declaration shim now that the published export resolves.
- `moda-interact-background/src/workers/translation-dispatch.worker.ts` - replaced the competing queue-wide Worker with an exported dispatch handler for BACKGROUND-007 routing.
- `moda-interact-background/tests/unit/services/translation-batch-assembly.service.test.ts` - corrected the transaction double to expose `$queryRaw` and `$executeRaw` and supplied the required test model.
- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts` - updated the exact shared release assertion to `0.7.1`.
- `moda-interact-background/tests/integration/translation-batch-assembly.concurrency.integration.test.ts` - added environment-gated real PostgreSQL concurrent assembly validation using two transactions and `SKIP LOCKED`.

### Work Completed

- Installed and pinned the corrected published shared package `@modainteract/moda-interact-shared@0.7.1`; no local runtime or declaration substitute remains.
- Preserved the existing short transaction boundary and post-commit best-effort submit enqueue.
- Exposed `handleTranslationDispatch` without creating a dedicated Worker that could compete for other merchant-communications job names.
- Added a real PostgreSQL integration test that creates isolated support records, runs two concurrent assemblers, and verifies distinct current batches and one historical BatchItem per translation when `TEST_DATABASE_URL` is configured.
- Did not implement BACKGROUND-005/006/007 or modify any downstream task state.

### Validation Results

- `npm exec tsc -- --noEmit` - passed.
- `npm exec vitest run tests/unit/services/translation-batch-assembly.service.test.ts` - passed; 3 tests.
- `npm exec vitest run tests/unit/runtime/observability-startup.test.ts` - passed; 8 tests.
- `npm exec vitest run tests/integration/translation-batch-assembly.concurrency.integration.test.ts` - skipped because `TEST_DATABASE_URL` is not configured.
- `npm test` - 175 passed, 6 skipped, 3 unrelated failures in recovery-routing and pending-recovery-candidate tests.
- `git diff --check` - passed for the workspace and background repository.

### Deviations

The required disposable PostgreSQL concurrency evidence could not run in this environment because `TEST_DATABASE_URL` is not configured. The test is present and environment-gated for architect-requested execution.

### Unresolved Issues

- Architect acceptance still requires at least one passing run of the new concurrency test against a disposable/test PostgreSQL database containing the DATABASE-002 schema.
- The full repository suite retains three unrelated recovery test failures; no files in those failing slices were changed by Attempt 2.

### Architectural Concerns

None introduced by Attempt 2. The task remains in `review` for architect evaluation and database-backed concurrency evidence.


## Architect Acceptance — 2026-09-06

### Review Status

Accepted — Complete.

### Decision

`ARCH-006-BACKGROUND-004` Attempt 2 is architect-accepted Complete. `ARCH-006-BACKGROUND-005` is released to Ready.

### Independent Validation Evidence

The developer supplied the previously missing real PostgreSQL environment and completed the required database-backed validation against a dedicated `moda_interact_test` PostgreSQL database. The authoritative `moda-interact-database` migration chain reported all 20 migrations applied and the DATABASE-002 `support` tables were present.

The real integration run passed:

```text
✓ tests/integration/translation-batch-assembly.concurrency.integration.test.ts
  ✓ assigns concurrent candidates to disjoint current batches with SKIP LOCKED

Test Files  1 passed (1)
Tests       1 passed (1)
```

Final focused validation also passed:

```text
TypeScript no-emit typecheck                              PASS
translation-batch-assembly.service unit tests            3/3 PASS
PostgreSQL batch-assembly concurrency integration test    1/1 PASS
git diff --check                                          PASS
```

The unit-test stderr message `Redis unavailable` is intentional fault injection for the accepted invariant that a committed READY batch remains durable when post-commit enqueue fails; the test itself passed.

### Findings

- The corrected shared package is pinned at `@modainteract/moda-interact-shared@0.7.1`; the local declaration shim is removed.
- Batch assembly performs a bounded stable-order `FOR UPDATE OF t SKIP LOCKED` claim in PostgreSQL and does not call Redis/OpenAI while row locks are held.
- The real PostgreSQL run demonstrated two concurrent assembly calls receiving disjoint current batches with one historical BatchItem per translation.
- Raw-SQL validation exposed and corrected the Prisma-client-default boundaries for `MerchantTranslationBatch.updatedAt` and `MerchantTranslationBatchItem.id`; the database schema/migrations remain unchanged.
- `translation-dispatch` is now exposed as a handler rather than a competing queue-wide BullMQ Worker. BACKGROUND-007 remains owner of the single process-level merchant-communications Worker/router.
- Post-commit submit enqueue remains best-effort; Redis failure does not roll back durable READY work.
- No BACKGROUND-005/006/007 provider-submission, polling or reconciliation capability was implemented in this task.

### Follow-on

A separate, non-gating integration-test-infrastructure chain (`SHARED-005 -> SHARED-006 -> BACKGROUND-008`) standardises disposable PostgreSQL/Redis setup and automatic application of the authoritative Prisma migration chain. It does not block `BACKGROUND-005` or any other unfinished implementation task.
