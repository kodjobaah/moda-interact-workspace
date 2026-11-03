---
id: ARCH-050-BACKGROUND-003
architecture_id: ARCH-050
title: Wire WooCommerce confirmed initial outreach to the common Support notice
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
  - ARCH-048-BACKGROUND-005
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-27
---

# Wire WooCommerce confirmed initial outreach to the common Support notice

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Attach deduplicated merchant Support notifications to the existing guarded WooCommerce first-send finalisation without opening its production outbound gate or scheduling a follow-up.

## Context

`src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` owns the `finalize.confirmed` adapter; `woo-recovery-outreach.service.ts` currently enables outbound exclusively under test mode. ARCH-048-BACKGROUND-005 owns its existing composition.

## Scope

**Modify only:** `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` and a focused test (e.g. `tests/unit/services/woocommerce-recovery/woo-initial-outreach-notice.test.ts`). Touch `tests/integration/woo-recovery-composed-services.integration.test.ts` and existing Woo first-send tests only when wiring assertions require it.

**Inspect without changing:** `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`, `src/services/woocommerce-recovery/contracts.ts`, `src/services/checkout-recovery/recovery-initial-outreach-support-notice.*`. No WordPress/plugin/API files belong to this task.

## Out of Scope

- Enabling live Woo outbound; changing ARCH-048 worker routing, order/checkout capture, ARCH-046 final SQL consent fence, human handover or merchant UI.

## Requirements

- Within `createWooRecoveryOutreachService(...).finalize.confirmed`, keep current guards requiring sequence 1, `followUpDueAt === null`, conversation ownership and the existing billing `commitSuccessfulInitiation` call.
- Replace the adapter's local `markWaitingAfterConfirmedSend(attempt.id,...)` and independent replay-validation branch with `recoveryInitialOutreachSupportNoticeService.finalizeConfirmedInitial({ shopId: recovery.shopId, checkoutRecoveryId: recovery.id, outreachAttemptId: attempt.id, outboundMessageId: message.id, sentAt: message.sentAt, followUpDueAt: null })`.
- Accept `created`, `disabled`, `replayed` outcomes and keep `checkoutRecovery.updateMany({id,shopId,status:"DETECTED" ...})` after successful finaliser completion.
- Never schedule Shopify's `ensureScheduledInitialFollowUp`, never add Woo sequence 2, and never invoke the notice primitive for `HUMAN` messages.
- Preserve `WooRecoveryOutreachService.enabled()` test-only outbound gate (`NODE_ENV==="test"` with injected `enableTestOutbound`), guarded provider sender and ARCH-046 final-send STOP/consent security. No setting is allowed to bypass these.
- Preserve existing error propagation/compensation boundary: a confirmed external send + Support persistence failure is retried using the existing durable provider admission, not resent/charged again.
- Reuse **the already required** `input.logger: StructuredLogger` of `createWooRecoveryOutreachService`; it uses the canonical `@modainteract/moda-interact-shared/logging` contract. Do **not** instantiate a new logger, use `console.*` or implement a Woo-specific serializer.
- If the adapter's `finalize.confirmed` callback catches an operational exception from billing, shared notification writer or recovery-status update, call `input.logger.error("recovery.initial_outreach_support_notice.woocommerce_finalization_failed", {shopId:recovery.shopId, checkoutRecoveryId:recovery.id, outreachAttemptId:attempt.id, outboundMessageId:message.id, stage, error})` with a bounded stage (`billing` / `support_notice` / `recovery_status`) and **rethrow the identical original error**. Log after the DB transaction has ended; a failed sink must not mask the original error. Do not turn any failure into `disabled`, `replayed`, or a successful result.
- The shared service also logs its own `.failed` event; this Woo-specific event is for finalisation-stage correlation, not duplicate notice persistence. Preserve existing worker compensation/retry/error logging and avoid logging customer data, credentials, message/template text, or full provider payloads. `created`, `disabled`, `replayed` are normal outcomes.

## Work Items

- [x] Import/consume BACKGROUND-001 finalisation interface and singleton inside Woo adapter's `finalize.confirmed` callback.
- [x] Remove only the now-redundant adapter-local attempt transition and replay check; leave Woo guard, billing and recovery status update unchanged.
- [x] Add tests for enabled/disabled, duplicate, exception after confirmed provider state, no Shopify follow-up, HUMAN exclusion and default test-only outbound gate. Adapter outcomes, composed integration replay, shared HUMAN-lineage unit coverage, and existing Woo durable-admission retry/test-gate coverage are included in the evidence below.
- [x] Add stage-labelled Shared-logger error reporting through the existing Woo adapter logger, with tests for recorded error, unchanged rethrow and throwing log sink.

## Interfaces / Contracts

- Same `ConfirmedInitialOutreachFinalizer.finalizeConfirmedInitial(ConfirmedInitialRecoveryOutreachInput)` port owned by BACKGROUND-001; Woo always passes `followUpDueAt: null`.
- The existing `WooOutreachDependencies["finalize"]["confirmed"]` signature and Woo checkout/coordinator inputs remain unchanged; adapter consumes port internally.
- No new API endpoint, BullMQ event, WordPress call or production sender enablement.
- Structured logging: keep `logger:StructuredLogger` in the existing adapter factory input; call its `error` method with event `recovery.initial_outreach_support_notice.woocommerce_finalization_failed` only for caught failures. No extra logger constructor, no generic logging helper and no platform-secret payload.

## Dependencies

- `ARCH-050-BACKGROUND-001` must be `complete` in canonical task metadata before claim.
- `ARCH-048-BACKGROUND-005` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [x] Same verified initial automated Woo send causes one Support notice iff merchant opted in, and initial recovery status updates exactly as before.
- [x] Retries/duplicate confirmed provider results do not create duplicate alerts, extra credits or new outbound messages.
- [x] Woo test-only gate and final-send consent/STOP protections remain enforced, follow-up scheduling stays absent.
- [x] Integration can run with existing Woo test fixtures and injected guarded sender; no production Meta send required.
- [x] Failure in billing/notice/status logs a sanitised Woo finalisation-stage event and propagates to the existing retry path; simulated sink failure cannot suppress or replace the original error.

## Validation

- [x] Focused Woo adapter/Woo retry/shared finalizer unit tests passed: 54 tests across 3 files. `scripts/test-integration.mjs tests/integration/woo-recovery-composed-services.integration.test.ts` passed (1 test); existing initial-send fence and race integration files passed via the same declared harness (9 tests).
- [x] Adapter logger tests cover billing, notice and recovery-status stages, exact event/context/error object, identical rethrow, and a throwing logger sink. Existing Woo service retry tests verify a confirmed send is finalized again without another provider send or refund; shared finalizer unit tests cover bounded `PERSISTENCE_FAILURE` logging and HUMAN lineage rejection.
- [x] Targeted ESLint and `git diff --check` passed. Build was attempted (Prisma Client generation succeeded; TypeScript compilation was blocked by missing `sharp` in the available dependency installation, causing unrelated errors in `src/services/shop-brand-media/image-transformer.ts` and `metadata-verifier.ts`). Test-only outbound evidence: the composed integration uses `NODE_ENV=test` with `enableTestOutbound: () => true`; the existing unit suite verifies outbound remains disabled without the test injection and outside test mode.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

BACKGROUND-001 owns the transaction and code/version contract. BACKGROUND-003 only integrates the Woo `finalize.confirmed` path; this separation deliberately avoids merge conflicts with BACKGROUND-002. Existing `ARCH-048-BACKGROUND-005` must be `complete` in canonical task YAML before claim (it is complete in the inspected 2026-10-26 snapshot); do not reopen it merely for this notification.

## Completion Report

### Status

Accepted by architect at Attempt 1; task completed automatically.

### Files Changed

- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` — consumes the shared finalizer, preserves guards/billing/status transition, and records bounded stage failures through the injected Shared logger.
- `tests/unit/services/woocommerce-recovery/woo-initial-outreach-notice.test.ts` — covers normal finalizer outcomes, call contract, stage-labelled logging, original-error propagation under sink failure, and guards.
- `tests/integration/woo-recovery-composed-services.integration.test.ts` — verifies one opted-in notice on first send and no duplicate on replay.

### Work Completed

Replaced the Woo adapter's local attempt finalization/replay branch with BACKGROUND-001's atomic `finalizeConfirmedInitial` service. Billing remains before notice finalization and the existing tenant/status-scoped recovery update remains after it succeeds. No follow-up scheduling, sequence 2, production outbound gate, or sender changes were introduced. Operational failures in billing, notice persistence, and recovery status now emit `recovery.initial_outreach_support_notice.woocommerce_finalization_failed` with a bounded stage and the same error object, then rethrow. Logging-sink failure cannot replace the original failure.

### Validation Results

- Passed: focused unit suites for the Woo adapter, Woo outreach retry/test gate, and shared initial notice finalizer (54 tests, 3 files).
- Passed: composed Woo + BullMQ + PostgreSQL disposable integration (1 test); confirmed exactly one notice on first send and no duplicate after replay, with one provider request and no sequence 2.
- Passed: existing Woo initial-send fence and race disposable integration suites (9 tests).
- Passed: targeted ESLint on all three changed files; `git diff --check`.
- Build attempted: Prisma Client generation succeeded. TypeScript compilation did not complete because `sharp` is absent from the available Background dependency installation; reported errors are in the unrelated shop-brand-media image transformer and metadata verifier.
- Outbound integration configuration remained test-only: the fixture injected `enableTestOutbound: () => true` under `NODE_ENV=test`; existing tests verified default-off and non-test behavior.

### Deviations

The full build could not pass in this environment because the Background dependency installation lacks `sharp`; no dependency installation or unrelated source change was made to work around it.

### Assumptions

The Woo guarded sender produces only automated confirmed initial messages; the shared finalizer independently verifies attempt initiator and rejects HUMAN lineage before creating a notice.

### Unresolved Issues

The missing `sharp` package prevents a clean package-wide TypeScript build in this worktree. Architect review may decide whether dependency restoration is needed before acceptance.

### Architectural Concerns

None discovered. No cross-repository contract or schema changes were required.

### Task Branch / Worktree Evidence

Canonical launcher prepared Attempt 1 after confirming both dependencies complete. Parent task branch/worktree: `task/ARCH-050-BACKGROUND-003`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-BACKGROUND-003`; implementation branch/worktree: `task/ARCH-050-BACKGROUND-003`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-BACKGROUND-003`. Parent branch incorporated `origin/main`; implementation branch was already current with `origin/main` at preparation. Implementation commit `4654fb9` is pushed to `origin/task/ARCH-050-BACKGROUND-003`. Parent review record commit `998a3cc8` is pushed to `origin/task/ARCH-050-BACKGROUND-003`. No task branch was merged to `main`.

## Architect Review — Attempt 1 — Accepted — 27 October 2026

### Review Status

Accepted.

### Review Notes

The Woo `finalize.confirmed` adapter retains the sequence-1/no-follow-up and conversation-ownership guards, commits billing before calling BACKGROUND-001's shared finalizer, and updates the tenant- and status-scoped recovery row only after successful finalization. The shared call carries the Woo shop, recovery, attempt, outbound message and send-time identities with `followUpDueAt: null`; all three normal outcomes are handled by continuing the existing recovery update. The adapter no longer performs its own attempt transition or replay validation. The surrounding Woo service retains the test-only outbound gate and durable-admission replay path, and the finalizer is not called for a non-confirmed or mismatched message.

Failures in billing, Support notice persistence, or recovery status update are reported through the injected Shared logger with the required bounded stage and correlation identifiers, then the identical original error is rethrown. The logger sink is isolated so its own failure cannot mask the operational error. No Shopify follow-up, sequence 2, production sender enablement, database/API contract, or WooCommerce plugin change was introduced.

### Reviewed Files

- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-initial-outreach-notice.test.ts`
- `moda-interact-background/tests/integration/woo-recovery-composed-services.integration.test.ts`
- Attempt 1 Completion Report and canonical worktree/publication evidence.

### Validation Reviewed

- Focused Woo adapter, retry/test-gate, and shared finalizer unit suites: 54 tests passed across three files.
- Composed Woo/BullMQ/PostgreSQL integration: 1 test passed; recorded evidence verifies a single notice on initial send and no duplicate after replay, with one provider request and no sequence 2.
- Existing Woo initial-send fence/race integration suites: 9 tests passed.
- Targeted ESLint and `git diff --check` passed.
- Package build was attempted; Prisma generation succeeded, while TypeScript compilation was blocked by missing `sharp` in the available dependency installation, with errors confined to unrelated image-transformer and metadata-verifier files. This does not block acceptance because the required focused validation passed and no task-owned failure was reported.
- Implementation branch `task/ARCH-050-BACKGROUND-003` is clean and published at `4654fb9`; parent task branch is current with its remote. Neither task branch was merged to `main`.

### Architecture Conformance

Conforms to ARCH-050 and the task's ownership boundaries. The adapter delegates initial-outreach notice finalization to BACKGROUND-001 while retaining Woo billing, guards, recovery status transition, compensation/retry behavior, and the existing test-only outbound gate. Changes stay within the authorized Background adapter and focused tests.

### Dependency Frontier

This task uses `completion_mode: automatic`; architect acceptance completes Attempt 1. `ARCH-050-SYSTEM-TEST-002` remains `pending`: although this task is now complete, its other declared prerequisites `ARCH-050-API-001`, `ARCH-050-API-002`, `ARCH-050-WOOCOMMERCE-001`, and `ARCH-050-WOOCOMMERCE-002` are not complete. `ARCH-048-WOOCOMMERCE-002` and `ARCH-048-WOOCOMMERCE-003` are complete. No dependent task is eligible for promotion from this completion. The ARCH-050 architecture defers domain `_index.md` updates until the architecture session closes.

### Lifecycle

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. Neither task branch was merged to `main`.

## Architect Dependency Frontier Reconciliation — 27 October 2026

`ARCH-050-BACKGROUND-001` was accepted and completed at Attempt 3, and the other declared dependency `ARCH-048-BACKGROUND-005` is complete. This task's dependencies are therefore satisfied, so its status advances from `pending` to `ready`. The task remains unclaimed at Attempt 0 (`executor: null`, `claimed_at: null`); no implementation worktree or attempt was started.
