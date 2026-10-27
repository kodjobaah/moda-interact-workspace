---
id: ARCH-050-BACKGROUND-001
architecture_id: ARCH-050
title: Atomically sample preference and create a deduplicated first-outreach Support notice
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-BACKGROUND-002
  - ARCH-050-BACKGROUND-003
created: 2026-10-26
updated: 2026-10-27
---

# Atomically sample preference and create a deduplicated first-outreach Support notice

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Expose one reusable Background-local first-send finalisation primitive that conditionally persists one merchant Support notice in the same transaction as the first confirmed initial-attempt state transition.

## Context

The shared pattern is `src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts`; automated Shopify and Woo finalisers currently use `RecoveryOutreachAttemptService.markWaitingAfterConfirmedSend`. Existing HUMAN and sequence-2 paths also use that method; do not change their semantics.

## Scope

**Create under `moda-interact-background/`:**

- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts` — typed, Background-local finalisation input/result/port; no cross-repo event contract.
- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts` — PostgreSQL transaction, state transition, preference sampling, idempotent Support message writer.
- `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts` — pure guards/port errors with injected collaborators.
- `tests/integration/recovery-initial-outreach-support-notice.integration.test.ts` — real disposable PostgreSQL concurrency, rollback, tenant and preference cases (run with the existing `scripts/test-integration.mjs` harness).

**Inspect for reuse, but do not modify unless a narrow helper extraction is demonstrably necessary:** `src/services/checkout-recovery/recovery-consent-merchant-notice.service.ts` and its `.contracts.ts` / `.formatter.ts`; `src/services/recovery-outreach-attempt.service.ts`. The new notice must follow the **existing** `MerchantSupportThread.createMany(skipDuplicates)` and `MerchantSupportMessage.createMany(skipDuplicates)` pattern, without copying generic infrastructure into a second abstraction.

Do **not** edit Shopify finalisation, Woo adapters, billing or human-send paths in this task. Those belong to BACKGROUND-002/003.

## Out of Scope

- Directly modifying Shopify or Woo workflow adapters (BACKGROUND-002/003); adding a queue, provider call, cost, new external event, or modifying HUMAN/sequence-2 send.

## Requirements

- Use the existing default `prisma` import. Import `createLogger` / `type StructuredLogger` from `@modainteract/moda-interact-shared/logging`, reuse the existing Background environment resolver and `serviceName:"moda-recovery-worker"` pattern from `recovery-consent-merchant-notice.service.ts`. Constructor-inject database, clock and `Pick<StructuredLogger,"info"|"error">` for deterministic unit tests; do not create an alternative local generic logger.
- At entry, validate finite `sentAt`, nonblank IDs, `followUpDueAt` consistency. Inside a **single interactive Prisma transaction**, lock the persisted sequence-1 attempt (`SELECT ... FOR UPDATE` via `Prisma.sql` or an equivalent concurrency-safe CAS), validate durable lineage and guarantee the first transition is the only opportunity to evaluate the preference.
- Read `RecoveryOutreachAttempt`: `id`, `checkoutRecoveryId`, `sequence = 1`, `trigger = INITIAL`, `initiatedBy` must **not** be `HUMAN`, `status`, `sentAt`, `outboundMessageId` and `followUpDueAt`. Read `CheckoutRecovery.shopId` and its `Conversation.id`. Read persisted `ConversationMessage` with `conversationId` equal to the recovery conversation, `direction = OUTBOUND`, `senderType = AUTOMATION`, `status IN (SENT, DELIVERED, READ)` and non-null `sentAt`. `Conversation.shopId` when non-null must match. Never accept a caller's unauthenticated shop/recovery IDs as proof of tenancy.
- On the **first confirmed transition**, require attempt `status IN (PENDING,CAPACITY_BLOCKED)` and `sentAt/outboundMessageId` absent; update status to `WAITING_FOR_RESPONSE`, set `sentAt`, `outboundMessageId` and specified `followUpDueAt` within that transaction. Query `ShopSettings.notifyOnInitialRecoveryOutreach`, treating a missing row as OFF. If OFF, commit transition without Support insertion and return `disabled`.
- If ON, `createMany({ skipDuplicates: true })` a Support thread keyed by authoritative recovery `shopId`, `findUniqueOrThrow({ where: { shopId } })`, insert one `SYSTEM / AVAILABLE` Support message with `checkoutRecoveryId`, `readAt:null`, `availableAt:now()`, `systemCode:"RECOVERY_INITIAL_OUTREACH_SENT"`, `systemVersion:"1"`, `sourceKey:"recovery-initial-outreach:v1:<attempt.id>"`, bounded neutral originalBody, `sourceLanguageTag:"en-GB"`. Existing Support translation handling must not falsely flag it pending. Conditionally advance `thread.lastMessageAt`; never mutate `lastMerchantMessageAt`, `merchantMessageVersion` or `needsAdminResponse`.
- If attempt already finalised with **the same** `outboundMessageId/sentAt`, return `replayed` after verifying lineage, including progressed `WAITING_FOR_RESPONSE/ENGAGED/NO_RESPONSE`; NEVER inspect a newly changed opt-in to backfill. Different message identity, failed/cancelled transition, mismatched recovery/shop, invalid sender or a conflicting sourceKey must throw.
- Any exception before commit rolls back **attempt update + thread + message**. Propagate the error, do not suppress it, and do not call billing, Redis, Meta, an LLM, an API or outbound provider inside this transaction. Do not try to undo a confirmed external send.
- Emit exactly one shared-logger outcome event per `finalizeConfirmedInitial` invocation after the transaction commits or fails: `recovery.initial_outreach_support_notice.created`, `.disabled`, `.replayed` at `info`, or `.failed` at `error`. **Never log inside the interactive database transaction**. Do not mistake default OFF or replay for an exception.
- On failure, catch **outside** `$transaction`, log `.failed` with a bounded category such as `INVALID_INPUT`, `LINEAGE_MISMATCH`, `FINALIZATION_CONFLICT` or `PERSISTENCE_FAILURE`, plus the original `{ error }` when safe, then `throw error` (same object). This must cover validation errors, duplicate/sourceKey integrity failures and Prisma/transaction errors; never use `catch {}`, return a success-shaped result, or silently skip Support persistence after the confirmed transition.
- Use bounded, explicit correlation fields when valid (`shopId`, `checkoutRecoveryId`, `outreachAttemptId`, `outboundMessageId`, `outcome`, `errorCategory`). No phone, customer identity, checkout contents, provider payloads, message bodies, credentials, raw input objects, raw SQL or dynamic event names. Invalid/raw IDs must not be logged before validation.
- Implement one narrow `logSafely(event, fields, level)` helper around the **injected logger call only**; a failing logger/sink must not undo committed writes or replace a pending exception. Catching a logger's own exception is the only intentionally ignored catch and must have a code comment explaining failure isolation. Do not use `console.*` or a new logging sink.

## Work Items

- [ ] Create contracts and implement the explicit `finalizeConfirmedInitial` method with typed discriminated result.
- [ ] Implement row lock/CAS and first-transition-only preference sample, with correct persisted outbound/attempt/recovery/shop checks.
- [ ] Implement atomic Support thread/message insert using existing deduplication conventions, sourceKey and recovery FK; update `lastMessageAt` conditionally.
- [ ] Implement replay protection for same-message finalisation, including a merchant opt-in flip between attempts.
- [ ] Add dedicated unit tests (malformed inputs, status/ownership/type guards, logger failure) and **real PostgreSQL** tests (ON, OFF, OFF then ON replay, ON then OFF, duplicate/concurrent same attempt, cross-shop spoof, failure after transition before message insert, sourceKey collision).
- [ ] Implement and test the shared-logger outcome/failure event contract, including a failing injected sink; demonstrate original exception identity survives a failing logger and the transaction is rolled back before the error log is emitted.

## Interfaces / Contracts

**Create in `recovery-initial-outreach-support-notice.contracts.ts`:**

```ts
export type ConfirmedInitialRecoveryOutreachInput = {
  shopId: string;                    // asserted against persisted recovery
  checkoutRecoveryId: string;
  outreachAttemptId: string;
  outboundMessageId: string;
  sentAt: Date;                      // must agree with persisted provider message
  followUpDueAt: Date | null;       // Shopify policy due date or Woo null
};
export type InitialOutreachNoticeResult =
  | { outcome: "created"; outreachAttemptId: string }
  | { outcome: "disabled"; outreachAttemptId: string }
  | { outcome: "replayed"; outreachAttemptId: string };
export interface ConfirmedInitialOutreachFinalizer {
  finalizeConfirmedInitial(
    input: ConfirmedInitialRecoveryOutreachInput
  ): Promise<InitialOutreachNoticeResult>;
}
```

**Create implementation** `RecoveryInitialOutreachSupportNoticeService implements ConfirmedInitialOutreachFinalizer`, with default exported instance `recoveryInitialOutreachSupportNoticeService`. Dependencies may be injected through constructor `database: Pick<PrismaClient,"$transaction">`, `now:()=>Date`, `logger:Pick<StructuredLogger,"info"|"error">`, matching the existing consent notice service's patterns.

**Stable structured events (owned by this task):**

| Event | Level | Required safe data |
|---|---|---|
| `recovery.initial_outreach_support_notice.created` | `info` | `outcome:"created"`, validated shop/recovery/attempt IDs |
| `recovery.initial_outreach_support_notice.disabled` | `info` | `outcome:"disabled"`, validated shop/recovery/attempt IDs |
| `recovery.initial_outreach_support_notice.replayed` | `info` | `outcome:"replayed"`, validated shop/recovery/attempt IDs |
| `recovery.initial_outreach_support_notice.failed` | `error` | `outcome:"failed"`, `errorCategory`, safe available IDs, `{error}` (bounded Shared serializer) |

No additional Shared contract package is needed; the event names are service-local domain semantics implemented through the Shared logger.

This is an **internal direct TypeScript call**, not a new BullMQ event, cross-service contract, public endpoint or Shared package export. The first-send state transition is moved to this primitive by BACKGROUND-002 and BACKGROUND-003; do not call the primitive after a separately committed `markWaitingAfterConfirmedSend`.

## Dependencies

- `ARCH-050-DATABASE-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-BACKGROUND-002` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-BACKGROUND-003` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] One real-Postgres atomic transition creates **exactly one** SYSTEM Support notification for enabled first send, no second charge/provider send.
- [ ] OFF first transition commits no notice; enabling later and replaying the same attempt still leaves zero notifications.
- [ ] Real concurrent finalisers serialize on the same attempt and produce exactly one Support message and one thread.
- [ ] Invalid persisted `direction`, `senderType`, status, null sentAt, trigger, sequence, wrong shop/ID or mismatched conversation fails closed; HUMAN/sequence-2 are excluded.
- [ ] Injected failure between attempt update and Support insert rolls back both writes; retry can complete without duplicate Support message.
- [ ] Logger errors never roll back already committed notification; result is deterministic and has no PII.
- [ ] Each created/disabled/replayed result and transaction/lineage failure emits its corresponding stable structured event; an exception is logged and rethrown as the same error, not swallowed or mapped to a successful outcome.
- [ ] Failure with injected throwing logger preserves the original business exception; successful commit with throwing logger still returns created/disabled/replayed and never causes a second attempt.

## Validation

- [ ] `npx vitest run tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts`.
- [ ] `node scripts/test-integration.mjs tests/integration/recovery-initial-outreach-support-notice.integration.test.ts` against disposable real PostgreSQL (not mocked Prisma).
- [ ] Unit log-spy assertions verify shared logger event name, level, bounded correlation fields, failure `errorCategory`, no PII and original-error rethrow; integration confirms rollback + retriable job failure on notification persistence error.
- [ ] `npm run build` (defined in Background package.json), targeted ESLint for changed source/tests, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

**Concurrency algorithm:** acquire per-attempt row lock *before* reading first/previous transition state; validate lineage; if already sent, verify same message and return `replayed`; otherwise update pending/capacity-blocked attempt, sample preference, optionally insert Support row, commit. `sourceKey` uniqueness is a secondary dedupe fence, not a substitute for the one-time decision. Use the consent-notice service only as a reusable pattern; it should not acquire responsibility for outreach attempt state.

Do not require `RecoveryOutreachAttempt.initiatedBy === "AUTOMATION"` as the current `getOrCreate()` implementation does not populate that field for ordinary initial sends. Instead reject `HUMAN` and require the persisted outbound message `senderType === "AUTOMATION"` plus the dedicated automatic callsite. Do not rewrite the existing attempt creation in this task.

Canonical task branch and worktree evidence is required at execution. No `_index.md` changes or cross-repo implementations.

## Completion Report

### Status

Attempt 2 implementation and required validation are complete. Submitted for `moda_architect` review. Attempt 1 remains recorded as blocked before source changes while the Background checkout lacked the accepted ARCH-050 database schema.

### Files Changed

- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts`
- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts`
- `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts`
- `tests/integration/recovery-initial-outreach-support-notice.integration.test.ts`
- Background `database` submodule gitlink updated to the accepted schema commit `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.

### Work Completed

- Added the Background-local typed finalizer contract and default service instance.
- Locked the persisted attempt row in one interactive PostgreSQL transaction, validated attempt/recovery/shop/conversation/outbound-message lineage, and guarded the first state transition with a compare-and-set update.
- Sampled `notifyOnInitialRecoveryOutreach` only on the first transition. Missing or disabled settings commit the transition without Support data; replay never resamples the setting.
- Added deduplicated SYSTEM/AVAILABLE Support notices with the recovery foreign key, stable source key, bounded neutral body, and conditional `lastMessageAt` update that preserves merchant-response metadata.
- Added outcome logging through the shared logger after transaction completion, with logger failure isolation and safe error-field handling.
- Added injected-collaborator unit coverage and real disposable PostgreSQL coverage for enabled/disabled/replayed outcomes, opt-in changes, concurrent finalizers, tenant and lineage guards, rollback/retry, and source-key collisions.

### Validation Results

- `npx vitest run tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts` — passed, 8 tests.
- `npm run test:integration -- tests/integration/recovery-initial-outreach-support-notice.integration.test.ts` — passed against disposable PostgreSQL, 8 tests. This invokes the repository's `scripts/test-integration.mjs` harness with local binaries on `PATH`.
- `npm run build` — passed; regenerated Prisma Client from the updated database schema and completed TypeScript compilation.
- Targeted ESLint for the four changed source/test files — passed.
- `git diff --cached --check` — passed before commit.

### Deviations

The direct `node scripts/test-integration.mjs ...` invocation initially could not resolve the local `prisma` executable (`spawn prisma ENOENT`) before tests started. The same harness and test file passed when run through the repository's `test:integration` npm script, which supplies `node_modules/.bin` on `PATH`. No implementation scope changed.

### Assumptions

`followUpDueAt` may be null for WooCommerce and, when present, must be a valid date later than `sentAt`. Replays must match the persisted follow-up due date as well as message identity.

### Unresolved Issues

None.

### Architectural Concerns

None identified.

### Previous Attempt 1 — Blocked

Attempt 1 stopped before source edits because the synchronized Background database submodule was pinned at `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`, which lacked the new preference field and Support recovery relation. The database fix is now consumed from `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`; the database dependency update was committed and pushed as `57d32270ffc586128a3587d269ed714eec0b9b29`.

### Task Branch / Worktree Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-BACKGROUND-001`
  parent branch: `task/ARCH-050-BACKGROUND-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-BACKGROUND-001`
  implementation branch: `task/ARCH-050-BACKGROUND-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded submodule commit: `database` at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`

Implementation repository:
  repository: `moda-interact-background`
  implementation commit: `a4ec3b17da9b6d158243b1b6fb953aa2dd9c173c`
  remote branch: `origin/task/ARCH-050-BACKGROUND-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-050/BACKGROUND-001-finalize-initial-attempt-and-write-deduplicated-support-notice.md`
  claim commit: `62d41b1523d298a49bc061bcb50f8df6d37948e7` (pushed by launcher)
  report commit: `0f4c8ca0ca65510fa6a3096ac762a57a34c71b22`
  remote branch: `origin/task/ARCH-050-BACKGROUND-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.

## Developer Override

### Decision

Reopened on 2026-10-27 by explicit developer request after resolving the database dependency blocker.

### Previous Attempt

Attempt 1 remains preserved as the blocked attempt; it stopped before implementation source changes because the Background database submodule lacked the ARCH-050 schema. This reopen does not increment the attempt.

### Reason

The database fix is available at commit `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`. The Background task worktree now points its `database` submodule at that commit, with gitlink update committed and pushed as `57d3227`. Prisma Client was regenerated successfully from the updated schema. The dependency blocker is resolved, so the task can resume through the normal launcher.

### Reopen Transition

`blocked` to `ready`; `executor` and `claimed_at` cleared; `attempt` remains 1. This override does not claim the task.

## Architect Review — Attempt 2 — Changes Requested — 27 October 2026

### Review Status

Changes Requested.

### Review Notes

The implementation is otherwise aligned with the task contract: the finalizer locks and validates persisted attempt/recovery/conversation/outbound-message lineage; the first transition, preference sample and optional deduplicated Support insert share one PostgreSQL transaction; replay does not resample preference; and the report records the focused PostgreSQL, unit, build, lint and diff-check evidence.

Required corrections before acceptance:

1. **Reconcile task completion markers.** All six Work Items, eight Acceptance Criteria and four Validation entries are still unchecked, although the Attempt 2 Completion Report says they are complete and records passing validation. In the next attempt, check only items supported by the implementation and evidence. Explain any item that cannot be substantiated; do not infer completion from the report alone.
2. **Log unexpected transaction errors safely.** The failed event currently includes `{ error }` only for `FinalizationError`. Include the original unexpected persistence/transaction error as `{ error }` so the Shared logger's bounded Error serializer can process it. Preserve the `PERSISTENCE_FAILURE` category and exact rethrow behavior. Add an assertion that the logger receives the error field for this category and that a throwing logger does not replace the original business exception.

The Background ARCH-050 domain index currently points to a different architecture/task set. This is architect-owned coordination state and will be reconciled during acceptance; it does not authorize implementation changes to the index in this task.

### Reviewed Files

- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.contracts.ts`
- `src/services/checkout-recovery/recovery-initial-outreach-support-notice.service.ts`
- `tests/unit/services/checkout-recovery/recovery-initial-outreach-support-notice.service.test.ts`
- `tests/integration/recovery-initial-outreach-support-notice.integration.test.ts`
- Attempt 2 Completion Report and canonical worktree/publication evidence.

### Validation Reviewed

The recorded 8/8 focused unit tests, 8/8 disposable PostgreSQL integration tests, build, targeted ESLint and diff check are consistent with the reviewed implementation. No validation was rerun as part of this architect review.

### Architecture Conformance

No architecture or interface change is requested. Implement only the safe error serialization correction and task-record reconciliation; keep the transaction and first-transition design intact.

### Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. Attempt 3 requires the canonical task launcher claim. Preserve the current implementation branch and worktrees; no merge to `main` is authorized.
