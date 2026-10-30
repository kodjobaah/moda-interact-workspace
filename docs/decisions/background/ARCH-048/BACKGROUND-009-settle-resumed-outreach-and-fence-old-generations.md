---
id: ARCH-048-BACKGROUND-009
architecture_id: ARCH-048
title: Settle unsent Woo outreach and fence retired generations
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 38
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-048-BACKGROUND-007
enables:
  - ARCH-048-BACKGROUND-011
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-048-BACKGROUND-009 — Settle unsent Woo outreach and fence retired generations

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.

Coordinator: `moda_architect`. The task is materialised and was prepared through the dedicated `/moda-task` worktrees after BG007 was Complete.

## Objective

When a Woo abandonment generation is closed by `CHECKOUT_RESUMED`, safely cancel and release its **not-yet-provider-admitted** outreach without undoing a real send, while allowing the next generation its own independent initial outreach.

## Context

BG007 atomically closes the old recovery and returns its ID; it deliberately does not release billing reservations or force-cancel a possibly admitted WhatsApp request. The current `WooRecoveryOutreachService.enqueueInitial()`/`processInitial()` and ARCH-046 `WooInitialSendFenceService` already inspect durable recovery status, but an outstanding old initial job/attempt or provisional credit needs explicit post-closure reconciliation. `RecoveryOutreachAttempt` is unique `(checkoutRecoveryId,sequence)` and `UsageReservation` is uniquely keyed by source; never reuse these across generations.

## Scope

**Permitted Background implementation files:**

- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`, `woo-recovery-outreach.adapters.ts` — implement BG007 `WooRecoveryOutreachDispatcher.settleResumed(recoveryId)` and the existing enqueue/dispatch guards.
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` and `woo-guarded-initial-sender.service.ts` — **only** bounded regression fixes needed to preserve the final SQL terminal/consent/STOP fence; do not replace ARCH-046 implementation.
- `src/services/woocommerce-recovery/woo-initial-dispatch.queue.ts` — generation-safe old-job handling only if necessary; job still identifies the committed recovery/attempt IDs.
- Add a **Woo-specific reservation settlement adapter** in `src/services/woocommerce-recovery/` if required. It may *consume* existing `freeRecoveryReservationService`, `paidIncludedRecoveryReservationService`, `purchasedRecoveryReservationService`, `promotionalRecoveryReservationService` release APIs and `UsageReservation` rows, but must not change their general ledger semantics.
- Tests in `tests/unit/services/woocommerce-recovery/`, `tests/integration/arch048-woo-initial-outreach.integration.test.ts`, `woo-initial-send-fence-races.integration.test.ts`, `woo-initial-send-redis-fault.integration.test.ts` and appropriate focused billing fixtures.

BG007-owned `contracts.ts` is **read-only**. Do not edit checkout/activity/admission, order policy, inbound routing, composition/worker files, WordPress/API/Shared, DB schema or unrelated billing services.

## Out of Scope

- No resumption-event parsing, candidate update, new recovery row INSERT, order webhook reader, WhatsApp inbound routing or orchestrator wiring.
- No extra provider send path, duplicate generic logger, invented credit pool, global reentry cap/cooldown, Woo follow-up activation or production send activation.

## Requirements

1. **Port and call semantics.** Implement exactly `WooRecoveryOutreachDispatcher.settleResumed(previousRecoveryId): Promise<void>` as defined by BG007. BG011 will call it after every `resumed` outcome (including replay). Resolve the persisted Woo recovery by **ID and shop platform**; verify it is `CANCELLED` with durable `CHECKOUT_RESUMED` status history. A missing/other-platform/not-resumed recovery is never permission to cancel another shop's attempt.
2. **Source of truth for provider admission:** lock by `(shopId, checkoutToken)` through BG002's existing coordinator. Look up sequence-one and any pending eligible unsent attempts by `checkoutRecoveryId` only. For each attempt, check durable outbound `ConversationMessage` and `providerDispatchKey`/`providerDispatchAdmittedAt` using the deterministic `recovery-outreach:<attemptId>` idempotency identity (and recorded message ownership). `sentAt: null` or `outboundMessageId: null` **does not prove no provider permit**. Never delete a provider-admitted message, revoke a permit, create a second provider request or refund a confirmed send.
3. **No permit / definitively unsent:** for a genuinely pre-permit pending attempt, conditionally transition to `CANCELLED` with `closedAt` and preserve `sequence`, ownership and historical content. Repeated settlement is idempotent. Suppress its delayed/queued dispatch through the existing final SQL recovery-status fence; removal of BullMQ job is an optional optimisation, not the correctness boundary. Future retries of this attempt must return `suppressed` rather than re-enqueue.
4. **Reserved credit settlement (exact ledger):** find any `UsageReservation` by the existing `createRecoveryIdempotencyKey(shopId, 'recovery-outreach:' + attemptId)` **after proving the attempt/recovery belongs to that shop**. Release `RESERVED` pre-permit credit using the **existing owner-specific release** API for the exact persisted reservation bucket (`counterId` -> free/lifetime-free, `billingPeriodEntitlementCounterId` -> paid-included, `purchasedCreditPurchaseId` -> purchased, `promotionalCreditGrantId` -> promotional). Validate exactly one recognised owner, quantity 1 and source/shop identity. Use the relevant existing service's `release({shopId,sourceKey,quantity:1})` (promotional may use its optional plan ID only if authoritatively available). Never call `admit()` merely to discover a source (it may create a new reservation), edit ledger counters directly, or release `COMMITTED`, `AMBIGUOUS`, already `RELEASED` or unknown-owner reservations. A failure must be logged and retried so a `CANCELLED` attempt with still-`RESERVED` credit can be repaired on replay.
5. **Provider permit already recorded / result uncertain:** do **not** mark an admitted/in-flight attempt `CANCELLED` or release its reservation. Keep its durable provider idempotency key, reconcile a confirmed SENT/DELIVERED/READ through the **existing** finalization/charge path even if recovery became `CANCELLED`, or use existing definitive-failure compensation for a provider-confirmed FAILED message. PENDING/unknown provider result is an explicit retryable reconciliation condition, not an unsent pretext or a second send. Never convert a genuinely delivered message to `CANCELLED` for bookkeeping.
6. **Final send guards and race ordering:** verify `enqueueInitial()` and `processInitial()` both refuse a **new** provider permit for `CANCELLED`/other terminal status, and ARCH-046's final SQL permit still locks the recovery row and rejects status other than `DETECTED`. If closure commits first, no new old-generation permit is possible. If provider permit commits first, do not claim it can be unsent; settle its actual eventual outcome. A closure/permit concurrency test must establish this ordering, including Redis lease expiry/retries.
7. **Generation independence:** every new recovery ID permits its own sequence-one attempt, deterministic job ID, reservation source and initial provider idempotency, without consulting previous generation's successful send count. Preserve current per-recovery limits, merchant eligibility, consent/STOP, verified MARKETING template and no-contact policy. **Do not add any cross-generation initial-message cooldown/cap**. Woo initial outbound remains default-off except explicit test-only injection; Woo follow-ups remain disabled.
8. **Failure handling and telemetry:** use Shared logger `@modainteract/moda-interact-shared/logging` with shop/recovery/attempt/generation/stage/outcome/reason, no sensitive payload. Never swallow release/provider/finalization exceptions; log and rethrow for bounded retry. A terminal retry exhaustion must remain visible in failed-job/structured diagnostics.

## Work Items

- [x] Implement `settleResumed` and provider-permit-aware classification for each attempt.
- [x] Reuse existing persisted billing reservation owner and release API; make the cancelled-attempt/release replay path idempotent.
- [x] Preserve confirmed or uncertain provider admissions and exact-identity finalization without a second send/refund.
- [x] Prove old queued initial dispatch and final SQL permit cannot send after closure.
- [x] Prove generation 2 can independently obtain its first attempt/send/credit under test-only outbound eligibility.
- [x] Add focused concurrency, credit-bucket, retry/failure and regression tests.

## Interfaces / Contracts

- **Consumes unchanged:** `WooRecoveryOutreachDispatcher.settleResumed(previousRecoveryId)` from BG007 `contracts.ts`, `WooCheckoutCoordinator`, `WooGuardedInitialSender`/ARCH-046 final send fence, `RecoveryBillingService`/reservation service release methods.
- **Existing durable identity:** `(checkoutRecoveryId, sequence)` for attempts; `recovery-outreach:<attemptId>` for provider admission; `createRecoveryIdempotencyKey(shopId, 'recovery-outreach:' + attemptId)` for credit reservation. Each generation has a different recoveryId/attemptId.
- **Output:** method returns only when all definitely pre-permit settlement is durable or no action is necessary. An uncertain provider outcome or failed release throws and is retryable; do not invent success states.
- **No new Shared event, API endpoint or Prisma model.**

## Dependencies

- `ARCH-048-BACKGROUND-007` (Complete required).
- Consume already accepted `ARCH-048-BACKGROUND-004`, `ARCH-046-BACKGROUND-004` and ARCH-028 credit/compensation infrastructure; **do not reopen** them.

## Enables

- `ARCH-048-BACKGROUND-011` — orchestrator invokes the new settlement seam.

## Acceptance Criteria

- [x] Checkout resumption cancels **only** unsent/no-permit attempts belonging to the retired recovery; old recovery remains frozen and closed.
- [x] Any RESERVED pre-permit credit is released **once** from the correct free, paid, purchased or promotional ledger; replay is idempotent and failed releases retry.
- [x] A provider-admitted, confirmed old message remains recorded and charged; an uncertain permit is retried as an explicit failure, not cancelled or resent.
- [x] Final SQL permit and old queue retries cannot newly send an old-generation message after closure, including close/permit concurrency and Redis lease renewal/retry.
- [x] New generation can send its own initial when otherwise eligible even if old generation used its initial; no cross-generation cap/cooldown.
- [x] Consent, STOP, template validation, merchant/billing policy, per-recovery duplicate prevention and production default-off remain enforced.
- [x] Errors are safely serialized, logged and propagated; no Shopify source or contract changed.

## Validation

- [x] Focused `npx vitest run tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`: 46 tests passed.
- [x] Required PostgreSQL/Redis integration command — 3 files, 21 tests passed.
- [x] Deterministic real-PostgreSQL settlement covers all four reservation owners, replay, close/permit race, confirmed-send recovery and ambiguous attempt-level send evidence; Redis lease renewal beyond its original TTL is exercised.
- [x] `npm run build` and `git diff --check` passed. Full `npm run lint` reports one unrelated existing error; changed-file lint passed. No baseline ID in `docs/development-baseline.md` matches that single failure.

## Stop Condition

After the settlement and final-fence capability is complete, fill the Completion Report, set `status: review` and **STOP**. Do not wire the orchestrator or start BG010/BG011.

## Implementation Notes

Use dedicated task worktrees/launcher preparation and record both branch revisions, physical isolation, sync and recursive-submodule evidence. This task is deliberately allowed a narrow Woo-specific adapter for already-existing ledger release; it is **not** permission to rewrite `RecoveryBillingService` or its other callers. If a necessary release capability is actually missing, stop and report an exact dependency gap rather than substitute direct counters, undocumented refunds or a fabricated billing admission. Log technical failures via the published Shared logger; follow existing test-only outbound injection.

## Completion Report

### Status

Ready for Review — implementation and focused validation are complete. This agent returns the task to `moda_architect`; no acceptance decision is recorded here.

### Files Changed

- `src/services/woocommerce-recovery/woo-resumed-outreach-settlement.adapter.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`
- `tests/integration/arch048-woo-initial-outreach.integration.test.ts`
- `tests/integration/woo-initial-send-fence-races.integration.test.ts`
- `tests/integration/fixtures/arch048-woo-outreach.fixture.ts`

### Work Completed

- Added `settleResumed(previousRecoveryId)` to verify Woo ownership, durable resumption history and the checkout lock before reconciling sequence-one attempts.
- Added a Woo-only Prisma settlement adapter that uses durable attempt, message/provider-permit and reservation identities. It conditionally cancels only no-permit attempts and releases RESERVED credit through the exact existing owner service. Release failures are logged and propagated; replay retries release without allocating a new reservation.
- Provider-admitted SENT/DELIVERED/READ messages use existing billing and finalization; confirmed provider failures use existing compensation. Attempt-level `sentAt`, admitted-but-unresolved messages, and unknown provider results remain retryable and are never classified as unsent.
- Preserved final SQL terminal-status fencing. Added regression coverage that sanitizes persistence exceptions through the Shared logger as `PERSISTENCE_FAILURE` without emitting the raw database error message.
- Added tests for all four credit owners, successful release replay, release-failure replay, confirmed-send crash recovery, ambiguous attempt evidence, close-before-permit, old queue retry suppression, generation-two independent send, and real Redis lease renewal.
- No database schema, Shared contract, other implementation repository, or orchestrator wiring changed.

### Validation Results

- `npx vitest run tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts` — 46 passed.
- `node scripts/test-integration.mjs tests/integration/arch048-woo-initial-outreach.integration.test.ts tests/integration/woo-initial-send-fence-races.integration.test.ts tests/integration/woo-initial-send-redis-fault.integration.test.ts` — 3 test files, 21 passed.
- Real PostgreSQL reservation tests cover lifetime-free, paid-included, purchased (including its supporting purchased counter), and promotional reservations. The Redis lease test held the lease beyond 10 seconds and confirmed settlement remained serialized while renewal was active.
- `npm run build` — passed (Prisma Client generation and TypeScript build).
- `npx eslint` on all changed files — passed.
- `npm run lint` — one error in untouched `src/services/translation-reconciliation.service.ts:218` (`preserve-caught-error`); no matching baseline ID in `docs/development-baseline.md`.
- `git diff --check` — passed.

### Deviations

The final fence race regression was a narrow task-permitted change: the event now carries a sanitized shared-logger `PERSISTENCE_FAILURE` Error instead of raw exception text, while the original error is still propagated unchanged.

### Assumptions

Integration uses disposable PostgreSQL and Redis and a persisted test-only provider sender. It does not prove deployed worker or Meta traffic.

### Unresolved Issues

Full-repository lint remains blocked by the unrelated untouched-file error above.

### Architectural Concerns

A provider permit committed before checkout closure is irreversible. This implementation reconciles its durable result and leaves uncertainty retryable; it does not treat it as unsent.

### Worktree and Synchronization Evidence

- Parent workspace task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-009`, branch `task/ARCH-048-BACKGROUND-009`; launcher-synchronized starting revision `423ffdf9ffb201dadd025c137ddeaac3f507070b`; Attempt 1 claim pushed as `d6826e0ceaa9d64b4d452ff4cc3d584d8d0ffe7f`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-009`, branch `task/ARCH-048-BACKGROUND-009`; launcher-synchronized starting revision `ddd13338247f26c2ed5e7146489709de9f5e3f7a`; recursive database submodule was ready at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Dedicated physical parent and implementation worktrees were used. The prepared launcher synchronized both task branches from their respective `origin/main` before claim and reported dependency gate passed, recursive submodules ready, and the parent claim pushed. Implementation completion is committed and pushed on the mirrored task branch as `48845d3` (`feat(ARCH-048-BACKGROUND-009): settle resumed Woo outreach`); the parent report remains on the same task branch as claim `d6826e0` and is committed/pushed with this review update.
- The requested Changes Requested task-file update is committed locally on `task/ARCH-048-BACKGROUND-009` but not pushed. The attempt to publish it to `https://github.com/kodjobaah/moda-interact-workspace.git` was rejected by automatic review: “This would publish the private BG009 task report to its configured GitHub remote, but the trusted user messages authorize review—not publication of this task or destination.” No retry or workaround was attempted; explicit user authorization to publish this BG009 parent task branch is required.

## Architect Review

### Review Status

Changes Requested.

### Review Notes

1. `settleResumed` routes failures to `failed()`, which logs the raw `error`. Change this path to log only bounded error class/code and stage fields; do not log the Error object, message, or stack. Rethrow the original error. Add a focused test proving sensitive/raw error data is absent from the log and the same error is rethrown.
2. `cancelIfPrePermit` can return `cancelled` and release the reservation when `updateMany` changes zero rows, including when `followUpDueAt` is non-null. Fail closed on follow-up state. Return `cancelled` only after confirming an eligible transition or rereading and validating an already-`CANCELLED` replay for the same attempt/recovery with no follow-up state. Do not release the reservation after an unconfirmed transition. Add focused tests for zero-row transition with `followUpDueAt` (no cancellation result or release), a validated already-cancelled replay, and successful eligible transition.

### Reviewed Files

- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts`
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`
- `src/services/woocommerce-recovery/woo-initial-dispatch.queue.ts`
- task-scoped Woo recovery unit and integration tests

### Validation Reviewed

Review identified the two corrections above. Changes Requested rework requires implementation and focused tests; no validation is credited for the corrections until they are implemented and reported.

### Architecture Conformance

The task remains within its assigned Background scope. The requested fixes preserve bounded diagnostics, exception retry semantics, and reservation safety.

### Follow-up

Apply both corrections on the same mirrored task branches. This review update does not claim or increment Attempt 2; the launcher will claim it when the task is started again.
