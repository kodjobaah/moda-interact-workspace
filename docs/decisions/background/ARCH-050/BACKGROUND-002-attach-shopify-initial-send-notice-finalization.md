---
id: ARCH-050-BACKGROUND-002
architecture_id: ARCH-050
title: Wire Shopify automated initial-outreach confirmation to the common Support notice
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-27T12:43:42Z
attempt: 1
depends_on:
  - ARCH-050-BACKGROUND-001
enables:
  - ARCH-050-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-27
---

# Wire Shopify automated initial-outreach confirmation to the common Support notice

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Make Shopify automated first-send finalisation invoke the accepted atomic attempt/notice port without changing billing, provider admission or follow-up rules.

## Context

`src/services/checkout-recovery/recovery-initiation.service.ts` calls `RecoveryOutreachFinalizationService.finalizeConfirmedOutreach` for first admitted sends and duplicate-provider confirmation replay. Existing follow-up scheduling is Shopify-only.

## Scope

**Modify only** `moda-interact-background/src/services/checkout-recovery/recovery-outreach-finalization.service.ts` and its corresponding unit/integration tests (create `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts` if no focused file exists).

**Inspect, but avoid changing except for the smallest required typed plumbing:** `src/services/checkout-recovery/recovery-initiation.service.ts` and `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`. They already both call `RecoveryOutreachFinalizationService.finalizeConfirmedOutreach`; follow-up `sequence=2` must still use the original path.

## Out of Scope

- Modifying Woo dispatch, Meta templates, Shopify UI or policy persistence; charging for Support notices.

## Requirements

- Inject/consume `ConfirmedInitialOutreachFinalizer` from BACKGROUND-001 as an optional constructor dependency with production default instance, keeping existing billing dependency available; do **not** create a second notice writer.
- Keep the existing `commitSuccessfulInitiation({ admission, recoveryId, occurredAt: message.sentAt })` in its current billing position. Preserve its idempotency, error propagation and compensation semantics.
- Compute `followUpDueAt` exactly as the existing policy logic does for sequence 1. For **sequence 1 only**, replace the current `recoveryOutreachAttemptService.markWaitingAfterConfirmedSend()` call with `initialOutreachFinalizer.finalizeConfirmedInitial({ shopId: recovery.shopId, checkoutRecoveryId: recovery.id, outreachAttemptId: attempt.id, outboundMessageId: message.id, sentAt: message.sentAt, followUpDueAt })`.
- Update the typed `recovery` argument in `finalizeConfirmedOutreach()` from `{id,status}` to `{id,shopId,status}`; verify current callers provide `shopId` or minimally propagate it, rather than guessing identity. Confirmed message ownership/status checking remains mandatory.
- Retain current `checkoutRecovery.updateMany({status:"DETECTED" ...})` and `ensureScheduledInitialFollowUp()` **after** the new transactional finaliser succeeds; retries must complete idempotently when notification already committed, without losing scheduled work.
- For sequence 2, continue existing `markWaitingAfterConfirmedSend`, billing, and no-notification semantics; for human-authored send, leave `recovery-conversation/human-command-dispatcher.service.ts` untouched.
- If the notification DB transaction fails, bubble the error so the job retries and uses existing message idempotency. Never send another WhatsApp message solely to retry a Support notification and never swallow the error.
- Use `@modainteract/moda-interact-shared/logging`, not `console.*` or a feature-local logger. Since this finaliser currently has no logger constructor parameter, add an **optional final constructor dependency** `logger: Pick<StructuredLogger,"error">` with a default `createLogger({serviceName:"moda-recovery-worker", environment:resolveDeploymentEnvironmentName()})`, or reuse an existing injected Background process logger if the current canonical code exposes one. Preserve the current billing constructor call pattern.
- For the new automated **sequence-1** path, wrap only its affected finalisation orchestration in an error-reporting boundary: on any caught error, log `recovery.initial_outreach_support_notice.shopify_finalization_failed` at `error` with safe `shopId`, `checkoutRecoveryId`, `outreachAttemptId`, `outboundMessageId` (when known), `stage` (`billing` / `support_notice` / `recovery_status` / `follow_up`) and `{error}`; rethrow **the exact error** so BullMQ's existing retry/failure policy remains authoritative. Do not replace with a `replayed` result, `null` or success, do not suppress and do not send again. Preserve the pre-existing sequence-2 error path and keep new logging outside any transaction.
- Shared BACKGROUND-001 already emits the canonical writer `.failed` event. The platform-specific failure event adds owning orchestration stage, not a second generic serializer. Sink failure cannot mask the original exception. Expected `created`/`disabled`/`replayed` outcomes are not errors.

## Work Items

- [ ] Inject BACKGROUND-001 port into `RecoveryOutreachFinalizationService` and type `shopId` on recovery input.
- [ ] Branch only on `attempt.sequence === 1` to invoke the shared atomic finaliser, preserving sequence-2 existing transition and replay handling.
- [ ] Preserve Shopify status update and follow-up scheduler after a successful (created/disabled/replayed) result.
- [ ] Update and test first-send, duplicate confirmed admission, error propagation, follow-up sequence 2 and merchant HUMAN negative path.
- [ ] Add the Shared structured logger injection/usage and stage-scoped failure logging for any new catch; assert error is rethrown unchanged, including when the injected log sink throws.

## Interfaces / Contracts

- Import `ConfirmedInitialOutreachFinalizer` / `ConfirmedInitialRecoveryOutreachInput` from `./recovery-initial-outreach-support-notice.contracts.js` and use the singleton in `./recovery-initial-outreach-support-notice.service.js`.
- Existing `finalizeConfirmedOutreach({ recovery:{id,shopId,status}, attempt:{id,sequence,followUpDueAt?}, admission, message, policy? })` stays the public Background service method; its only intentional type extension is `recovery.shopId`.
- `sequence=1` sends the specified `{shopId, checkoutRecoveryId, outreachAttemptId, outboundMessageId, sentAt, followUpDueAt}` payload. `sequence=2` never calls the notice port.
- No new HTTP/queue/Shared/public API, no billing contract change.
- Logger import: `import {createLogger, type StructuredLogger} from "@modainteract/moda-interact-shared/logging"` and use the existing `src/runtime/deployment-environment.ts` resolver (when a default logger is needed). Event `recovery.initial_outreach_support_notice.shopify_finalization_failed`, level `error`; its `stage` field identifies the actual failed operation, not a guessed cause. Log only safe identifiers; no provider request/response/body/phone.

## Dependencies

- `ARCH-050-BACKGROUND-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-001` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Confirmed automatic sequence-1 Shopify send: shared port called once, creates notice only when enabled; checkout status/after-send follow-up preserved.
- [ ] Duplicate admission/retry with same sent message leads to `replayed` with zero extra notices and no extra credit.
- [ ] Sequence 2 and HUMAN send produce no ARCH-050 notification and retain existing semantics.
- [ ] Error in shared writer is propagated, with no attempt to initiate a second provider send; tests cover failure then retry.
- [ ] An unexpected billing/notice/status/follow-up exception is recorded through the Shared logger at the owning boundary and rethrown; logging sink failure never masks the original exception.

## Validation

- [ ] Focused Vitest for new Shopify finaliser paths and existing `tests/unit/recovery-outreach-follow-up.test.ts` (adapt to actual test layout).
- [ ] Focused test with injected recording/failing logger verifies `shopify_finalization_failed`, `stage`, safe context and `toBe(originalError)` on rejection; verify no accidental second provider send/credit.
- [ ] Run relevant Background first-outreach integration evidence and `npm run build`, targeted ESLint, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Use an explicit dependency injection rather than embedding a raw SQL Support insert in the Shopify finaliser. BACKGROUND-001 owns the transaction and all message deduplication; this task only selects the appropriate automatic stage and preserves downstream recovery-status/follow-up orchestration. Keep edits bounded to Shopify-specific finalisation. Do not edit Woo adapter, consent service, database schema, or domain indexes.

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

## Architect Dependency Frontier Reconciliation — 27 October 2026

`ARCH-050-BACKGROUND-001` was accepted and completed at Attempt 3. This task's sole declared dependency is now complete, so its status advances from `pending` to `ready`. The task remains unclaimed at Attempt 0 (`executor: null`, `claimed_at: null`); no implementation worktree or attempt was started.
