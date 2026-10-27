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
status: complete
priority: 30
executor: null
claimed_at: null
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

- [x] Inject BACKGROUND-001 port into `RecoveryOutreachFinalizationService` and type `shopId` on recovery input.
- [x] Branch only on `attempt.sequence === 1` to invoke the shared atomic finaliser, preserving sequence-2 existing transition and replay handling.
- [x] Preserve Shopify status update and follow-up scheduler after a successful (created/disabled/replayed) result.
- [x] Update and test first-send, duplicate confirmed admission, error propagation, follow-up sequence 2 and merchant HUMAN negative path.
- [x] Add the Shared structured logger injection/usage and stage-scoped failure logging for any new catch; assert error is rethrown unchanged, including when the injected log sink throws.

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

- [x] Confirmed automatic sequence-1 Shopify send: shared port called once, creates notice only when enabled; checkout status/after-send follow-up preserved.
- [x] Duplicate admission/retry with same sent message leads to `replayed` with zero extra notices and no extra credit.
- [x] Sequence 2 and HUMAN send produce no ARCH-050 notification and retain existing semantics.
- [x] Error in shared writer is propagated, with no attempt to initiate a second provider send; tests cover failure then retry.
- [x] An unexpected billing/notice/status/follow-up exception is recorded through the Shared logger at the owning boundary and rethrown; logging sink failure never masks the original exception.

## Validation

- [x] Focused Vitest for new Shopify finaliser paths and existing `tests/unit/recovery-outreach-follow-up.test.ts` (adapt to actual test layout).
- [x] Focused test with injected recording/failing logger verifies `shopify_finalization_failed`, `stage`, safe context and `toBe(originalError)` on rejection; verify no accidental second provider send/credit.
- [x] Run relevant Background first-outreach integration evidence and `npm run build`, targeted ESLint, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Use an explicit dependency injection rather than embedding a raw SQL Support insert in the Shopify finaliser. BACKGROUND-001 owns the transaction and all message deduplication; this task only selects the appropriate automatic stage and preserves downstream recovery-status/follow-up orchestration. Keep edits bounded to Shopify-specific finalisation. Do not edit Woo adapter, consent service, database schema, or domain indexes.

## Completion Report

### Status

Complete — Attempt 1 was accepted by `moda_architect` on 2026-10-27. The sequence-1 integration delegates to BACKGROUND-001's atomic finalizer, retains Shopify billing/status/follow-up behavior, and preserves the existing sequence-2 path.

### Files Changed

- `src/services/checkout-recovery/recovery-outreach-finalization.service.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`

### Work Completed

- Added the BACKGROUND-001 finalizer and Shared logger as injectable dependencies while preserving the existing billing constructor argument.
- Sequence 1 now sends persisted recovery/shop/attempt/message identity and the existing policy-derived follow-up due time to the shared atomic finalizer. Billing remains first; recovery status and scheduled follow-up work remain after its success, including `replayed` outcomes.
- Sequence 2 keeps its original billing and `markWaitingAfterConfirmedSend` path. The HUMAN command dispatcher was not changed.
- Added stage-scoped Shared logger events for billing, Support notice, recovery status and follow-up failures. The original exception is rethrown unchanged, and a failing logger sink cannot mask it.
- Added finalizer orchestration tests for the sequence-1 port payload/order, all four failure stages, throwing logger, and sequence-2 behavior. Updated Shopify initiation coverage to verify first sends, duplicate replay and retry after a Support persistence failure through the same durable admission key.

### Validation Results

- `npx vitest run tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts tests/unit/services/recovery-conversation/background-wiring.test.ts` — passed, 77 tests across four files.
- `npx vitest run tests/unit/recovery-outreach-follow-up.test.ts` — passed, 6 tests.
- `npx vitest run tests/unit/services/recovery-billing.service.test.ts` — passed, 7 tests, including idempotent paid recovery usage reservation/commit behavior.
- `npm run test:integration -- tests/integration/recovery-initial-outreach-support-notice.integration.test.ts` — passed against disposable PostgreSQL, 8 tests.
- `npm run build` — passed; generated Prisma Client from the pinned database schema and completed TypeScript compilation.
- Targeted ESLint for the changed finalizer and unit tests — passed.
- `git diff --check` — passed.
- `scripts/workspace-doctor.sh --quick` from the canonical workspace passed Background checks but reported the documented, unrelated `DEP-ZOD-001` failure for `moda-interact-admin` (missing direct runtime Zod declaration). No admin-owned files were changed.

### Deviations

The new implementation worktree initially had no installed `node_modules`; after the focused test command surfaced missing `dotenv/config` and `vitest/config`, installed exact locked dependencies with `npm ci` and reran validation successfully. The quick doctor also reports the existing unrelated admin `DEP-ZOD-001` issue documented above.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

The quick workspace doctor reports that `moda-interact-admin` lacks a direct runtime Zod declaration (`DEP-ZOD-001`). This task owns Background and did not modify admin; the finding is recorded for architect coordination.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-BACKGROUND-002`
  parent branch: `task/ARCH-050-BACKGROUND-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-BACKGROUND-002`
  implementation branch: `task/ARCH-050-BACKGROUND-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commit: `database` at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`

Launcher claim commit: `9cf7a1d56f2c0a5ee50bde8145efd35f41da6b97` (pushed).
Implementation commit: `3b5dc7d06205a69e4a814a3005048731c3368b1b` (pushed to `origin/task/ARCH-050-BACKGROUND-002`).
Parent task report commit is this review-ready task-file update, pushed to `origin/task/ARCH-050-BACKGROUND-002`.

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

## Architect Review — Attempt 1 — Accepted — 27 October 2026

### Review Status

Accepted.

### Review Notes

The implementation replaces only the sequence-1 transition with the accepted BACKGROUND-001 finalizer, providing the persisted `shopId`, recovery/attempt/message identities and policy-derived follow-up due time. Billing remains before the shared finalizer; recovery status and follow-up scheduling remain after success, including replay. Sequence 2 retains its established billing and attempt transition path. The new Shopify boundary logs the specified stage-scoped failure event and rethrows the exact error, with a sink failure isolated from the original exception.

### Reviewed Files

- `moda-interact-background/src/services/checkout-recovery/recovery-outreach-finalization.service.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- Attempt 1 Completion Report and canonical worktree/publication evidence.

### Validation Reviewed

- Focused finalizer/initiation/follow-up/wiring tests: 77 tests passed across four files.
- Existing follow-up regression tests: 6 passed; recovery billing tests: 7 passed.
- BACKGROUND-001 disposable PostgreSQL integration suite: 8 tests passed.
- `npm run build`, targeted ESLint and `git diff --check` passed.
- Implementation branch `task/ARCH-050-BACKGROUND-002` is clean and published at `3b5dc7d06205a69e4a814a3005048731c3368b1b`; the recorded Database submodule is `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.

### Architecture Conformance

Conforms to the ARCH-050 ownership and ordering boundaries. Changes are limited to the Shopify-specific Background finalizer and its focused tests; no Woo, human-send, billing-contract, provider-admission or database behavior was changed.

### Dependency Frontier

This task uses `completion_mode: automatic`; architect acceptance transitions Attempt 1 to Complete. `ARCH-050-SYSTEM-TEST-001` remains pending because its other declared dependencies `ARCH-050-SHOPIFY-001` and `ARCH-050-SHOPIFY-002` are ready but not complete. No downstream status promotion is applicable. The ARCH-050 architecture defers domain `_index.md` changes until the architecture session closes.

### Lifecycle

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. Neither task branch was merged to `main`.
