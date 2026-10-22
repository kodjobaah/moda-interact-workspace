---
id: ARCH-040-BACKGROUND-009
architecture_id: ARCH-040
title: Correct purchased-lot credit recognition during pre-provider follow-up release
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-BACKGROUND-007
  - ARCH-010-DATABASE-007
  - ARCH-010-DATABASE-014
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-22
updated: 2026-10-22
---

# ARCH-040-BACKGROUND-009 — Correct purchased-lot credit recognition during pre-provider follow-up release

## Architecture

Architecture: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
Owner: `moda_background` / `moda-interact-background`; coordinator: `moda_architect`.
**Portable canonical definition; defined but not materialised** in a task parent/implementation branch or worktree.

## Objective

Make application-owned cancellation and crash repair of an undelivered HUMAN recovery follow-up correctly recognise and safely release the **persisted purchased-credit reservation**, without consuming the single sequence-two claim or trapping a purchased lot indefinitely when Meta was never admitted.

## Context

In `src/services/recovery-conversation/recovery-follow-up-billing.service.ts`, `inspectFollowUpCredit()` queries `billing.UsageReservation` and counts these four nullable columns as if exactly one must be present: `counterId`, `billingPeriodEntitlementCounterId`, `purchasedCreditPurchaseId`, `promotionalCreditGrantId`. The real purchased reservation created in `src/services/purchased-recovery-reservation.service.ts` has **both** `counterId` (the Shop purchased-credit aggregate) and `purchasedCreditPurchaseId` (the exact lot). It is currently classified as `unsafe` before the purchased branch can run. In addition, the `counterId`-first discriminator must not mistake valid purchased reservations for lifetime-free credits.

`tests/unit/services/recovery-conversation/recovery-follow-up-billing.test.ts` currently models purchased capacity using `purchasedCreditPurchaseId` with a null `counterId`, so its passing test does not represent the persisted row shape. Accepted `ARCH-040-BACKGROUND-007` owns `FollowUpClaimCancellationService.cancelClaimed`, `repairCancelledClaims`, the command/attempt lock order and release-before-claim-reset state machine. This task fixes its **billing source interpretation only**, not that state machine.

## Scope

- Correct `inspectFollowUpCredit`'s source classification to use **source-specific allowed FK combinations**: purchased uses `counterId` with counter kind `PURCHASED_RECOVERY_CREDITS` **and** non-null exact `purchasedCreditPurchaseId`; lifetime free uses its actual lifetime counter without purchase FK; paid included uses period counter; promotional uses the grant FK. Reject conflicting/unknown combinations and incorrect counter kinds.
- Verify reservation Shop, exact unique original `sourceKey`, quantity `1`, status, settled/compensated UsageEvent absence and provider-pre-admission evidence using the accepted BG007 fencing protocol. Do not reconstruct a source from current plan policy or reuse a different purchase lot.
- Ensure the existing `RecoveryFollowUpBillingService.releaseBeforePermit` calls `purchasedRecoveryReservationService.release` for the original purchased source key/quantity, then verifies durable release **before** clearing the sequence-two attempt's HUMAN claim. Preserve refund-hold/lot inventory authority in the existing purchase source owner; do not manually decrement counters.
- Fix bounded cancelled-command repair for real purchased reservations when pre-provider cancellation was persisted but credit release or claim reset was interrupted. Preserve idempotency across replay and competing dispatch/cancel workers.
- Add unit tests with **realistic purchased rows containing both FKs**, plus integration coverage at the actual PostgreSQL reservation/command/attempt boundary. Retain free, paid and promotional regression coverage.

## Out of Scope

- Schema/migrations, purchased-credit ordering, credit purchase acquisition, refund economics, new usage ledger or a separate reservation source.
- Changes to merchant Shopify/Woo UI or API; this is platform-neutral Background behaviour.
- Releasing a post-provider-admitted, provider-UNKNOWN, committed, compensated, expired-unsafe or already-sent reservation; no Meta resend/retry policy changes.
- Rewriting `ARCH-040-BACKGROUND-007`'s accepted cancellation/locking model or `ARCH-040-BACKGROUND-008`'s final 24-hour-window policy.
- ARCH-028 uncertain-send commitment policy and broader `FAILED` compensation; those are architect-gated separately.

## Requirements

1. A real `RESERVED` purchased row with `counterId` referencing `PURCHASED_RECOVERY_CREDITS` plus `purchasedCreditPurchaseId` must return `{kind:"reserved", admission:{kind:"persisted", capacity:"purchased", sourceKey:<exact persisted key>, quantity:1}}`, not `unsafe` or `free`.
2. Reject a fabricated purchased row with lot ID but missing/incorrect purchased counter, purchase/counter Shop mismatch, mixed period/promotion IDs, multiple matching source keys, invalid quantities, settled/compensated usage, or unsupported statuses. Never treat `unsafe` as `clear`.
3. For a definitively pre-provider terminal HUMAN template refusal, cancel the immutable command, release only its corresponding provisional purchased lot through the existing service, then conditionally free the same `RecoveryOutreachAttempt(sequence=2)` claim using BG007 locking. A later eligible claimant may use that **same** one attempt/credit identity; do not create sequence 3 or another conversation.
4. If the existing source release is unavailable or not durably confirmed, retain the cancelled command and held claim for bounded `repairCancelledClaims`; never double-release or blindly retry Meta.
5. If `providerDispatchKey`, `providerDispatchAdmittedAt`, outbound linkage, provider acceptance/unknown state or committed/compensated UsageEvent exists, do not release or reset the claim. No negative effect on regular free/paid/promotional reservations or standard successful HUMAN/AI flows.
6. Preserve idempotency, tenant isolation and purchase-specific credit allocation under concurrent cancels and stale leases. Do not change the existing source-key format or introduce a second billing ledger.

## Work Items

- [ ] Confirm the real purchased reservation write/commit/release shapes and accepted BG007 final-permit guard; pin the source-specific FK shape as the canonical read contract.
- [ ] Fix the bounded `inspectFollowUpCredit()` capacity classifier and fail-closed checks, preserving the persisted purchased source key and purchase identity.
- [ ] Update purchased fixture(s) to populate `counterId`, purchased counter kind and `purchasedCreditPurchaseId`; add false-positive mixed-source/settled/unsafe tests.
- [ ] Add real PostgreSQL scenario(s) covering pre-provider HUMAN cancellation, original purchased-lot release, subsequent same-sequence reclaim, repair-after-cancel crash, and competing claim/send attempts.
- [ ] Record validation, worktree and branch evidence in the Completion Report; stop at this correction.

## Interfaces / Contracts

- Database owns `billing.UsageReservation`, `billing.ShopEntitlementCounter`, `billing.RecoveryCreditPurchase`, `billing.UsageEvent`, and `commerce.RecoveryOutreachAttempt`; their schema already supports paired purchased FKs.
- Background owns `RecoveryFollowUpBillingService`, `FollowUpClaimCancellationService` and the existing `PurchasedRecoveryReservationService.release` operation.
- `ARCH-040-BACKGROUND-007` is the accepted cancellation/reconciliation contract; `ARCH-040-BACKGROUND-008` remains a separate final-dispatch policy change. No new API/event/Shared export.

## Dependencies

- `ARCH-040-BACKGROUND-007` — Complete: application-owned pre-provider cancellation/release.
- `ARCH-010-DATABASE-007` — Complete: purchase-lot accounting.
- `ARCH-010-DATABASE-014` — Complete: purchase lifecycle/provenance.

## Enables

- `ARCH-040-SYSTEM-TEST-001` — certify platform-neutral, one-credit follow-up release/reclaim.
- `ARCH-040-SYSTEM-TEST-002` — Shopify workflow certification must not mask purchased-credit leak.
- `ARCH-040-SYSTEM-TEST-003` — Woo workflow certification must not mask purchased-credit leak.

## Acceptance Criteria

- [ ] Valid purchased lot with paired FKs classifies as purchased; invalid pairing fails closed without double-counting or release.
- [ ] For a definitively pre-provider cancelled HUMAN follow-up using purchased credits, the exact lot's reserved balance is restored through its existing release owner and the one sequence-two claim becomes re-claimable **only after durable release**.
- [ ] Cancel/replay/repair and two-worker races release at most once, maintain one claim/credit, and never resend or release provider-admitted or uncertain sends.
- [ ] Free, paid-included and promotional source handling is unchanged; no changes to purchased-credit grant/refund policy or existing positive provider usage.
- [ ] Unit and real PostgreSQL integration tests establish the actual persisted purchased reservation shape; generic mocks alone are insufficient.

## Validation

- [ ] Focused `recovery-follow-up-billing.test.ts` and `follow-up-claim-cancellation.test.ts` unit tests.
- [ ] Real PostgreSQL purchased-lot reservation/cancellation/repair/reclaim integration case, including tenant/counter mismatch and provider-permit race.
- [ ] Existing relevant recovery-conversation and purchased reservation tests; declared Background TypeScript check/build/lint commands selected from `package.json`.
- [ ] `git diff --check`; launcher-resolved isolated parent/implementation worktree and start-of-attempt sync evidence in Completion Report.

## Implementation Notes

The bug is not solved by relaxing `capacityColumns.length` from `1` to `2` globally; define **legal combinations by source kind** and verify the purchased counter enum. Keep `sourceKey` and lot identity from the durable row. The source-specific release service—not this classifier—owns balances, refund holds and transaction semantics. The BG007 cancellation code already protects irreversible dispatch with canonical Shop -> Conversation -> command -> attempt row locks; do not widen transactions with Redis or Meta calls. Reconcile concurrent work with pending BG008 without creating an artificial Shopify/Woo dependency.

## Stop Condition

After the bounded source-discriminator fix and validation, set the task to `review`, provide Completion Report to `moda_architect`, and STOP. Do not start Background-008 or an enabled system test.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The persisted purchased reservation has both counter and purchase FKs; validated by the existing purchased reservation writer and Prisma schema.

### Unresolved Issues

None identified at definition time.

### Architectural Concerns

If the accepted BG007 release state machine cannot reliably prove the exact lot was durably released, stop and report that evidence gap rather than clearing the follow-up claim optimistically.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and real worktree evidence.

### Reviewed Files

Not applicable before implementation.

### Validation Reviewed

Not applicable before implementation.

### Architecture Conformance

Pending implementation.

### Follow-up

None.
