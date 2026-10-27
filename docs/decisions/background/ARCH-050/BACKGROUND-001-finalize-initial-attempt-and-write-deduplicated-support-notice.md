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
attempt: 0
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

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

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
