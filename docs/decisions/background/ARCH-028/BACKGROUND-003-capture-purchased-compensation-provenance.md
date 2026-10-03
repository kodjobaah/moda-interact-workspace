---
id: ARCH-028-BACKGROUND-003
architecture_id: ARCH-028
title: Capture purchased recovery compensation provenance at commit
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-DATABASE-002
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Capture purchased recovery compensation provenance at commit

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Populate the compensation provenance introduced by `ARCH-028-DATABASE-002` whenever a **purchased recovery-credit reservation** transitions from `RESERVED` to `COMMITTED`, so a later delivery-failure compensation task can restore the exact purchased-credit/refund lifecycle without guessing from current state.

This task does **not** compensate any recovery and does not change the existing purchase/refund policy. It records the facts that the existing commit transaction already observes or causes.

## Context

`ARCH-028-DATABASE-002` adds nullable provenance needed for exact post-delivery compensation:

```text
UsageReservation.purchasedCreditPurchaseStatusAtCommit?
UsageReservationRefundCancellation(
  usageReservationId,
  refundId,
  previousStatus
)
```

The current `PurchasedRecoveryReservationService.commit(...)` already supports a valid lifecycle where:

```text
purchase ACTIVE
  -> recovery reserves one purchased credit
  -> merchant/refund workflow moves purchase to WITHDRAWN
  -> recovery provider send succeeds
  -> reservation commits
  -> purchase may move WITHDRAWN -> COMPLETED
  -> live refund request(s) may be cancelled as NO_CREDITS_REMAINING
```

Before DATABASE-002 there was no durable relation proving whether the purchase was `ACTIVE` or `WITHDRAWN` at commit time or exactly which live refund rows the commit cancelled. A later compensation task must not infer those facts from timestamps or present-day row state.

The canonical owner remains:

```text
src/services/purchased-recovery-reservation.service.ts
```

Do not create a second purchased-credit commit path in `RecoveryBillingService` or a new generic billing framework.

The task executes only after the prepared Background worktree uses the architect-accepted DATABASE-002 database submodule/schema. If the prepared nested `database/` dependency does not contain the accepted DATABASE-002 fields/models, stop and report the dependency mismatch rather than locally editing database schema from this task.

## Scope

Repository-owned changes in `moda-interact-background`:

- extend the existing purchased-credit reservation commit transaction to persist the purchase status it actually observed at commit;
- when the existing final-credit commit cancels live refund requests, persist one normalized `UsageReservationRefundCancellation` row for each refund that this exact transaction actually cancels;
- preserve the exact refund status observed immediately before cancellation (`REQUESTED` or `PROVIDER_ACTION_REQUIRED`);
- make refund cancellation/provenance capture concurrency-safe inside the existing Serializable transaction/retry boundary;
- preserve existing replay behaviour for reservations that are already terminal/non-RESERVED;
- add focused unit and PostgreSQL integration coverage for ACTIVE/WITHDRAWN commit provenance and refund-cancellation provenance.

Expected implementation/test surface:

```text
moda-interact-background/src/services/purchased-recovery-reservation.service.ts
moda-interact-background/tests/unit/services/purchased-recovery-reservation.service.test.ts
moda-interact-background/tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts
```

A small repository-local helper may be introduced only if it is inseparable from the purchased commit transaction and does not duplicate the canonical reservation service.

## Out of Scope

- Performing any recovery compensation.
- Creating a negative correction `UsageEvent`.
- Populating `compensationUsageEventId`, `compensationReason` or `compensatedAt`.
- Restoring purchased-credit `currentAmount` or counters after a delivery failure.
- Reopening/reinstating cancelled refunds.
- Changing refund eligibility, refund request policy or provider-refund behaviour.
- Changing `UsageReservationStatus` or adding a `COMPENSATED` status.
- Changing lifetime-free, paid-included or promotional reservation commit paths.
- Changing recovery admission order or capacity-source selection.
- Recipient reachability/suppression policy.
- Merchant notification.
- Shared/Messaging changes.
- Any database schema/migration edit in `moda-interact-background`; the schema is owned by DATABASE-002.
- `docs/architecture/_index.md` updates.

## Requirements

### R1 — Persist the purchase status actually observed by the commit transaction

When a purchased reservation transitions from `RESERVED` to `COMMITTED`, persist:

```text
UsageReservation.purchasedCreditPurchaseStatusAtCommit = lot.status
```

using the same purchase row already read/validated by the commit transaction.

The only accepted values are the two statuses the current commit path already permits:

```text
ACTIVE
WITHDRAWN
```

Do not derive the status after changing the lot to `COMPLETED`, and do not reconstruct it from current state on replay.

### R2 — Preserve exact replay semantics

The current service returns replay outcomes when the reservation is no longer `RESERVED`.

For an already-`COMMITTED`, `RELEASED` or `AMBIGUOUS` reservation:

- preserve the existing replay result;
- do not populate missing `purchasedCreditPurchaseStatusAtCommit` retrospectively;
- do not create refund-cancellation provenance retrospectively;
- do not mutate current purchase/refund state.

Legacy committed rows with null provenance remain legacy/unknown. A later compensation task must handle that explicitly rather than this task inventing history.

### R3 — Record only refund rows actually cancelled by this commit

The current commit cancels live refunds only when both are true:

```text
purchase was WITHDRAWN at commit
AND
this reservation consumes the final current/reserved purchased credit
```

Preserve that policy exactly.

When that branch executes, capture each refund row that the transaction actually transitions from:

```text
REQUESTED
or
PROVIDER_ACTION_REQUIRED
```

to:

```text
CANCELLED
reason = NO_CREDITS_REMAINING
```

For each successfully cancelled row create exactly one:

```text
UsageReservationRefundCancellation(
  usageReservationId = reservation.id,
  refundId = refund.id,
  previousStatus = exact pre-cancellation status
)
```

Do not create provenance for refunds that were already `CANCELLED`, `COMPLETED`, failed, or otherwise not transitioned by this commit.

### R4 — Cancellation provenance and refund transition are one transaction

Refund-state changes and their provenance rows must commit or roll back together with the existing purchased reservation commit transaction.

Do not persist provenance before/after the Serializable transaction as a best-effort side effect.

If a refund changes concurrently between the transaction's read and guarded cancellation, the transaction must fail/retry through the existing purchased-reservation concurrency policy rather than record stale `previousStatus` or silently skip an expected cancellation.

The exact local implementation may use guarded per-row updates or an equivalent deterministic mechanism, but it must prove that every provenance row corresponds to a refund row this transaction actually cancelled.

### R5 — Preserve current purchased-credit arithmetic and lifecycle

Do not change the current semantics of:

- `RecoveryCreditPurchase.currentAmount` decrement;
- `RecoveryCreditPurchase.reservedAmount` decrement;
- `ACTIVE`/`WITHDRAWN` acceptance by commit;
- final-credit transition to `COMPLETED`;
- `ShopEntitlementCounter.reservedQuantity` decrement;
- `ShopEntitlementCounter.committedQuantity` increment;
- `refundingQuantity` behaviour;
- positive recovery `UsageEvent` creation;
- `UsageReservation.status = COMMITTED`;
- `committedUsageEventId` assignment;
- transaction isolation/retry behaviour;
- purchase/refund provider-context semantics.

This task records provenance around that lifecycle; it does not redesign it.

### R6 — Do not broaden refund cancellation policy

Keep the current cancellation trigger limited to the final-credit commit of a purchase that was `WITHDRAWN` when commit began.

Do not cancel refunds merely because:

- the lot was ACTIVE;
- the commit did not consume the final credit;
- another purchase lot is exhausted;
- the refund is unrelated to this reservation's purchase.

### R7 — Preserve idempotency under transaction retry

A serialization/concurrency retry must not create duplicate provenance rows or duplicate refund transitions.

The existing reservation state/source key remains the primary commit idempotency boundary. DATABASE-002's normalized provenance uniqueness constraints remain authoritative and must not be bypassed with best-effort `skipDuplicates` behaviour that could hide an inconsistent replay.

### R8 — No new logging of billing/customer payloads

No new log payload is required for normal operation.

If a bounded diagnostic is genuinely necessary, use the existing Shared structured logger and only identifiers/status outcomes such as reservation ID, purchase ID, refund ID and previous status. Do not log customer/message content, provider payloads, credentials or monetary provider response bodies.

## Work Items

- [ ] Update the prepared Background database dependency to the accepted DATABASE-002 schema/generated client through the normal task preparation/dependency mechanism; do not edit schema locally.
- [ ] Persist `purchasedCreditPurchaseStatusAtCommit` from the exact purchase status observed by the commit transaction.
- [ ] Replace/augment the current bulk final-credit refund cancellation with deterministic cancellation/provenance capture that records exact prior status for each row actually cancelled.
- [ ] Keep refund cancellation and provenance capture inside the existing Serializable purchased commit transaction.
- [ ] Preserve replay behaviour without backfilling legacy terminal reservations.
- [ ] Add unit coverage for ACTIVE and WITHDRAWN commit provenance.
- [ ] Add unit coverage for REQUESTED and PROVIDER_ACTION_REQUIRED refund-cancellation provenance and unrelated refund exclusion.
- [ ] Extend PostgreSQL concurrency/integration coverage for withdrawn final-credit commit + refund provenance.
- [ ] Add a concurrency case proving a changing refund cannot produce stale provenance and is retried/fails safely.
- [ ] Confirm no compensation, capacity restoration, reachability or merchant-notification behaviour was introduced.

## Interfaces / Contracts

### Database contract owner

`ARCH-028-DATABASE-002`

Consumes:

```text
UsageReservation.purchasedCreditPurchaseStatusAtCommit?
UsageReservation.refundCancellations
UsageReservationRefundCancellation(
  usageReservationId,
  refundId,
  previousStatus
)
```

### Canonical application owner

`PurchasedRecoveryReservationService.commit(...)`

remains the only Background owner of purchased reservation commit arithmetic and the only place this task captures commit-time purchased/refund provenance.

### Provenance semantics

```text
purchasedCreditPurchaseStatusAtCommit
    = purchase status BEFORE this commit mutates the lot

UsageReservationRefundCancellation.previousStatus
    = refund status immediately BEFORE this exact commit changes it to CANCELLED / NO_CREDITS_REMAINING
```

The next compensation task may rely on this provenance only for reservations committed after BACKGROUND-003 adoption. Null/empty provenance on historical rows remains a legacy condition, not permission to infer history.

## Dependencies

- `ARCH-028-DATABASE-002`

DATABASE-002 must be Complete and architect-accepted so the prepared Background worktree has the accepted schema, migration and generated Prisma surface before this task modifies the purchased commit path.

No dependency on `ARCH-028-BACKGROUND-002` is required. Failure convergence and purchased commit-provenance capture touch independent Background owners and may be implemented/reviewed independently once their own prerequisites are Complete.

## Enables

None yet.

The later recovery compensation/capacity-restoration task will depend on both the terminal-failure convergence and this purchased provenance capture task.

## Acceptance Criteria

- [ ] A newly committed purchased reservation stores exactly the purchase status (`ACTIVE` or `WITHDRAWN`) observed before lot mutation.
- [ ] An already-terminal reservation replay does not backfill or mutate provenance.
- [ ] Final-credit commit from an ACTIVE lot preserves existing behaviour and creates no refund-cancellation provenance solely because the lot completes.
- [ ] Final-credit commit from a WITHDRAWN lot records every REQUESTED/PROVIDER_ACTION_REQUIRED refund this transaction actually cancels, with exact previous status.
- [ ] Refund rows not transitioned by the commit produce no provenance rows.
- [ ] Cancellation provenance and refund status transition are atomic with lot/counter/usage/reservation commit.
- [ ] Concurrent refund mutation cannot leave stale/incorrect provenance committed.
- [ ] Existing purchase/current/reserved/refunding and shop-counter arithmetic is unchanged.
- [ ] Existing positive recovery UsageEvent/idempotency/provider-reporting semantics are unchanged.
- [ ] No compensation UsageEvent, reachability mutation or merchant notification is introduced.

## Validation

Required validation categories:

- [ ] inspect current `package.json` and use repository-declared commands;
- [ ] `npm run prisma:generate` against the accepted DATABASE-002 nested schema;
- [ ] `npm run prisma:validate`;
- [ ] focused unit: `tests/unit/services/purchased-recovery-reservation.service.test.ts`;
- [ ] focused PostgreSQL integration: `tests/integration/purchased-recovery-reservation.concurrency.integration.test.ts` through the repository's current integration harness/environment;
- [ ] `npm run test:unit`;
- [ ] `npm test`;
- [ ] `npm run build` (includes TypeScript compilation in the current repository);
- [ ] `git diff --check`;
- [ ] changed-file inspection proving no local database schema/migration, compensation or unrelated billing semantics changed.

If PostgreSQL integration cannot run because the task environment lacks the repository-required database runtime, leave that validation item unchecked and record the exact blocker. Do not replace it with mocked evidence while claiming integration passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and **STOP**.

Do not begin recovery compensation, reachability suppression, merchant notification or any enabled/follow-on task.

## Implementation Notes

This task intentionally records provenance in the **existing purchased commit transaction** rather than in a later asynchronous compensator. That is the only point at which the code authoritatively knows both the pre-commit purchase status and which refund rows it is about to cancel because the final reserved credit is being consumed.

Do not optimize the refund-provenance relation into JSON and do not derive it later from timestamps.

The current purchased reservation service already uses Serializable transactions plus bounded retries. Preserve that concurrency model rather than introducing a second lock/transaction mechanism.

## Completion Report

### Status

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- DATABASE-002 is Complete and the prepared task worktree contains its accepted schema/generated client.
- Existing purchased commit arithmetic/policy remains canonical and unchanged except for additive provenance capture.

### Unresolved Issues

None at definition time.

### Architectural Concerns

If implementation shows DATABASE-002 provenance cannot represent the exact current purchased commit/refund lifecycle without another schema change, stop and return the issue to `moda_architect`. Do not add database fields or reinterpret refund policy from this Background task.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending implementation.

### Validation Reviewed

Pending implementation.

### Architecture Conformance

Pending implementation.

### Follow-up

Pending implementation.
