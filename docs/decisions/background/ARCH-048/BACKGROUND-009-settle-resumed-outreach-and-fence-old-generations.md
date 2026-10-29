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
status: pending
priority: 38
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-BACKGROUND-007
enables:
  - ARCH-048-BACKGROUND-011
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-048-BACKGROUND-009 — Settle unsent Woo outreach and fence retired generations

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.

Coordinator: `moda_architect`. **Defined but not materialised**. Only execute through dedicated `/moda-task` worktrees after BG007 is accepted Complete.

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

- [ ] Implement `settleResumed` and provider-permit-aware classification for each attempt.
- [ ] Reuse existing persisted billing reservation owner and release API; make the cancelled-attempt/release replay path idempotent.
- [ ] Preserve confirmed or uncertain provider admissions and exact-identity finalization without a second send/refund.
- [ ] Prove old queued initial dispatch and final SQL permit cannot send after closure.
- [ ] Prove generation 2 can independently obtain its first attempt/send/credit under test-only outbound eligibility.
- [ ] Add focused concurrency, credit-bucket, retry/failure and regression tests.

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

- [ ] Checkout resumption cancels **only** unsent/no-permit attempts belonging to the retired recovery; old recovery remains frozen and closed.
- [ ] Any RESERVED pre-permit credit is released **once** from the correct free, paid, purchased or promotional ledger; replay after release failure repairs without double release or allocation.
- [ ] A provider-admitted, actually delivered old message remains recorded and charged; an uncertain permit is reconciled, not cancelled or resent.
- [ ] Final SQL permit and queue retries cannot newly send an old-generation message after closure, including close/permit concurrency.
- [ ] New generation can send its own initial when otherwise eligible even if old generation used its initial; no cross-generation cap/cooldown.
- [ ] Consent, STOP, template validation, merchant/billing policy, per-recovery duplicate prevention and production default-off remain enforced.
- [ ] Errors are redacted, logged and propagated; Shopify existing outreach/billing tests remain unchanged.

## Validation

- [ ] Focused `npx vitest run` of Woo outreach and settlement unit tests.
- [ ] `node scripts/test-integration.mjs tests/integration/arch048-woo-initial-outreach.integration.test.ts tests/integration/woo-initial-send-fence-races.integration.test.ts tests/integration/woo-initial-send-redis-fault.integration.test.ts` (run separately if the current integration runner requires it).
- [ ] New deterministic real-PostgreSQL reservation-bucket settlement tests, including crash/replay, close/permit race, confirmed send and ambiguous admission.
- [ ] `npm run build`, `npm run lint` as environment permits, and `git diff --check`; report exact results and baseline IDs.

## Stop Condition

After the settlement and final-fence capability is complete, fill the Completion Report, set `status: review` and **STOP**. Do not wire the orchestrator or start BG010/BG011.

## Implementation Notes

Use dedicated task worktrees/launcher preparation and record both branch revisions, physical isolation, sync and recursive-submodule evidence. This task is deliberately allowed a narrow Woo-specific adapter for already-existing ledger release; it is **not** permission to rewrite `RecoveryBillingService` or its other callers. If a necessary release capability is actually missing, stop and report an exact dependency gap rather than substitute direct counters, undocumented refunds or a fabricated billing admission. Log technical failures via the published Shared logger; follow existing test-only outbound injection.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Source snapshot dated 2026-10-29, not proof of deployed worker/Meta traffic.

### Unresolved Issues

None at definition time.

### Architectural Concerns

A provider permit already committed before checkout closure is irreversible; provider-outcome uncertainty must be reconciled, not called unsent.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
