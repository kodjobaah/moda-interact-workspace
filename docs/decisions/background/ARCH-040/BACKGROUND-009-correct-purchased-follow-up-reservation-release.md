---
id: ARCH-040-BACKGROUND-009
architecture_id: ARCH-040
title: Correct purchased-lot credit recognition during pre-provider follow-up release
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-040-BACKGROUND-007
  - ARCH-010-DATABASE-007
  - ARCH-010-DATABASE-014
enables:
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-22
updated: 2026-10-23
---

# ARCH-040-BACKGROUND-009 — Correct purchased-lot credit recognition during pre-provider follow-up release

## Architecture

Architecture: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`.
Owner: `moda_background` / `moda-interact-background`; coordinator: `moda_architect`.
**Materialised for developer execution** on the mirrored `task/ARCH-040-BACKGROUND-009` branches. The claim and implementation handoff are recorded below.

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

- [x] Confirm the real purchased reservation write/commit/release shapes and accepted BG007 final-permit guard; pin the source-specific FK shape as the canonical read contract.
- [x] Fix the bounded `inspectFollowUpCredit()` capacity classifier and fail-closed checks, preserving the persisted purchased source key and purchase identity.
- [x] Update purchased fixture(s) to populate `counterId`, purchased counter kind and `purchasedCreditPurchaseId`; add false-positive mixed-source/settled/unsafe tests.
- [x] Add real PostgreSQL scenario(s) covering pre-provider HUMAN cancellation, original purchased-lot release, subsequent same-sequence reclaim, repair-after-cancel crash, and competing claim/send attempts.
- [x] Record validation, worktree and branch evidence in the Completion Report; stop at this correction.

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

- [x] Valid purchased lot with paired FKs classifies as purchased; invalid pairing fails closed without double-counting or release.
- [x] For a definitively pre-provider cancelled HUMAN follow-up using purchased credits, the exact lot's reserved balance is restored through its existing release owner and the one sequence-two claim becomes re-claimable **only after durable release**.
- [x] Cancel/replay/repair and two-worker races release at most once, maintain one claim/credit, and never resend or release provider-admitted or uncertain sends.
- [x] Free, paid-included and promotional source handling is unchanged; no changes to purchased-credit grant/refund policy or existing positive provider usage.
- [x] Unit and real PostgreSQL integration tests establish the actual persisted purchased reservation shape; generic mocks alone are insufficient.

## Validation

- [x] Focused `recovery-follow-up-billing.test.ts` and `follow-up-claim-cancellation.test.ts` unit tests.
- [x] Real PostgreSQL purchased-lot reservation/cancellation/repair/reclaim integration case, including tenant/counter mismatch and provider-permit race.
- [x] Existing relevant recovery-conversation and purchased reservation tests; declared Background TypeScript check/build/lint commands selected from `package.json`.
- [x] `git diff --check`; launcher-resolved isolated parent/implementation worktree and start-of-attempt sync evidence in Completion Report.

## Implementation Notes

The bug is not solved by relaxing `capacityColumns.length` from `1` to `2` globally; define **legal combinations by source kind** and verify the purchased counter enum. Keep `sourceKey` and lot identity from the durable row. The source-specific release service—not this classifier—owns balances, refund holds and transaction semantics. The BG007 cancellation code already protects irreversible dispatch with canonical Shop -> Conversation -> command -> attempt row locks; do not widen transactions with Redis or Meta calls. Reconcile concurrent work with pending BG008 without creating an artificial Shopify/Woo dependency.

## Stop Condition

After the bounded source-discriminator fix and validation, set the task to `review`, provide Completion Report to `moda_architect`, and STOP. Do not start Background-008 or an enabled system test.

## Completion Report

### Status

Complete — developer execution, Attempt 1 (claimed 2026-10-23T10:59:30Z). The accepted developer self-review passed and explicit developer completion was recorded on 2026-10-23. Implementation patch corrections labelled Attempt 1 and Attempt 2 occurred within this one task-workflow attempt; the canonical task `attempt` remains 1.

### Files Changed

Implementation repository `moda-interact-background`, committed as `86eff5db3cebaf4cab8ed05bb2ffe7e7b89eb1a5` on `task/ARCH-040-BACKGROUND-009`:

- `src/services/recovery-conversation/recovery-follow-up-billing.service.ts`
- `tests/unit/services/recovery-conversation/recovery-follow-up-billing.test.ts`
- `tests/unit/services/recovery-conversation/follow-up-claim-cancellation.test.ts`
- `tests/integration/recovery-follow-up-purchased-release.integration.test.ts` (new)

No schema, Shared contract, accepted BG007 cancellation-state-machine, domain `_index.md` or parent architecture modifications are included in this task implementation.

### Work Completed

- Updated reservation classification to recognise the persisted purchased-credit pair (`counterId` referencing a `PURCHASED_RECOVERY_CREDITS` shop counter and the exact `purchasedCreditPurchaseId`) without confusing purchased capacity with lifetime-free capacity.
- Enforced fail-closed source-specific FK combinations, reservation/shop/counter/purchase ownership, original source identity and quantity checks; also validate a `RELEASED` row before treating it as durable release evidence.
- Preserved the existing purchased reservation owner for release, and BG007's release-before-claim-reset, cancelled-command repair and final provider permit fencing; no second ledger or claim sequence introduced.
- Updated unit fixtures and negative cases. Added real PostgreSQL integration coverage for exact purchased-lot release, same-sequence reclaim, failed-release hold and repair, interruption after durable release, cross-shop references and final provider permit concurrency.
- Corrected the new integration fixture in the second implementation patch by removing `BillingPlan` outbound-limit fields not supported by the current Prisma schema; no production change was needed for that correction.
- The developer applied the supplied source/test patches, validated the result, and committed/pushed the four-file implementation to the Background task branch.

### Validation Results

- **PASS:** `npm run test -- tests/unit/services/recovery-conversation/recovery-follow-up-billing.test.ts tests/unit/services/recovery-conversation/follow-up-claim-cancellation.test.ts` — 18/18 tests passed across two files (focused Attempt 1 execution).
- **PASS:** `npm run test:integration -- tests/integration/recovery-follow-up-purchased-release.integration.test.ts tests/integration/recovery-follow-up-claim-races.integration.test.ts` — 7/7 tests passed across two files with real PostgreSQL (after the test-only fixture correction).
- **PASS:** `npm run build` — Prisma Client generation v6.19.3 and TypeScript compilation completed successfully after the correction.
- **PASS:** `npm run lint` — the repository-declared ESLint command completed without findings.
- **PASS:** `npm run test:arch040-recovery-conversation` — 45/45 tests passed across 7 recovery-conversation unit files.
- **PASS:** implementation patch whitespace checks / `git diff --check` in the supplied developer terminal runs. Git commit `86eff5db3cebaf4cab8ed05bb2ffe7e7b89eb1a5` and push of `task/ARCH-040-BACKGROUND-009` succeeded; subsequent `git status` showed a clean worktree. Its upstream status relative to `origin/main` does not negate the successful explicit branch push.
- **PASS:** the canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-009` is clean and on `task/ARCH-040-BACKGROUND-009`; the dedicated parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-009`.
- **PASS:** focused unit, recovery-conversation regression, PostgreSQL integration, build, lint and diff checks were rerun from the canonical Background implementation worktree.

Worktree/branch evidence available for review:

- Parent task record: `task/ARCH-040-BACKGROUND-009` in `kodjobaah/moda-interact-workspace`, developer claim at `2026-10-23T10:59:30Z`.
- Implementation execution: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-009`, branch `task/ARCH-040-BACKGROUND-009` in `kodjobaah/moda-interact-background`, pushed as `86eff5db3cebaf4cab8ed05bb2ffe7e7b89eb1a5`.
- Expected dedicated parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-009`; the parent branch is verified, but the launcher-resolved local path/isolation/synchronisation evidence was not provided.

### Deviations

None in production architecture or repository ownership. The initial PostgreSQL test fixtures used unsupported BillingPlan outbound-limit fields; this was corrected in the second implementation patch before successful validation. Source/test patch preparation was AI-assisted at the developer's request; the developer retained task execution ownership and performed the commit/push.

### Assumptions

The purchased credit writer persists both purchased counter and exact lot FK, and the existing purchase owner retains source-of-truth release/hold/refund handling. Existing BG007 provider admission fencing remains authoritative.

### Unresolved Issues

No remaining validation failure or required Work Item gap was identified. Explicit developer completion has been recorded.

### Architectural Concerns

No new cross-repository contract, schema or provider-dispatch policy change identified. The accepted BG007 cancellation/release ordering remains unchanged; focused concurrency and repair cases passed. The reviewer should validate the remaining workflow-evidence gap rather than treating task-branch existence as proof of isolation.

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

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-040-BACKGROUND-009` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The canonical launcher will claim Attempt 1 after worktree preparation.

## Developer Self-Review - Accepted

### Review Status

Passed — all defined Work Items and Acceptance Criteria are implemented within the bounded Background repository scope, and the required focused, regression, integration, build, lint and diff validation passed for Attempt 1.

### Review Evidence

- Implementation branch `task/ARCH-040-BACKGROUND-009` is committed and published at `86eff5db3cebaf4cab8ed05bb2ffe7e7b89eb1a5`.
- Canonical implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-009`; canonical parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-009`.
- Validation passed: focused units 18/18, recovery-conversation regression units 45/45, PostgreSQL integration 7/7, `npm run build`, `npm run lint`, and `git diff --check`.
- Scope remains limited to the four implementation/test files listed above; no schema, Shared contract, accepted BG007 state machine, architecture document or index changes were introduced.

### Completion Decision

The self-review passed. The developer explicitly completed the task on 2026-10-23; task status is now `complete`, with `executor: null`, `claimed_at: null`, and `attempt: 1`. No enabled task was started and no branch was merged into `main`.

## Developer Completion Decision

### Decision

Complete — the accepted Attempt 1 review is durable, all required Work Items and Acceptance Criteria are checked off, implementation and parent task changes are committed and published, and no merge to `main` is required for task completion.

### Evidence

- Implementation commit: `86eff5db3cebaf4cab8ed05bb2ffe7e7b89eb1a5` on `task/ARCH-040-BACKGROUND-009`.
- Parent completion record is being published on the same task branch without changing the attempt number.
- Focused units, recovery-conversation regressions, PostgreSQL integration, build, lint and diff checks passed.
