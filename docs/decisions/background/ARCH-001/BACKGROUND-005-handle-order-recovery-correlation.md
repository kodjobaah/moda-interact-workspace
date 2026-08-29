---
id: ARCH-001-BACKGROUND-005
architecture_id: ARCH-001
title: Handle order recovery correlation and cancellation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 50
executor: codex
claimed_at: 2026-08-28T22:05:00Z
attempt: 1
depends_on: ["ARCH-001-BACKGROUND-004"]
enables: []
created: 2026-08-28
updated: 2026-08-28
---

# Handle Order Recovery Correlation and Cancellation

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Process `orders/create` only for recovery purposes: cancel a matching pending candidate, or complete/attribute a matching existing `CheckoutRecovery`, otherwise discard the order.

## Context

Moda does not persist or process normal orders. The order webhook exists in ARCH-001 solely to stop a pending recovery or mark an existing recovery as completed.

## Scope

- Consume the shared v2 order event.
- Resolve a pending candidate by checkout token, with cart-token fallback only through the indexed transient correlation from BACKGROUND-002.
- If a pending candidate exists, cancel/remove it and its aliases, then end processing.
- If no pending candidate exists, lookup an existing `CheckoutRecovery`.
- Complete/attribute an eligible recovery using the existing status/history model.
- Use the event completion timestamp where appropriate.
- Discard unrelated orders without creating durable order/business records.
- Make candidate maturation versus order completion concurrency-safe.
- Keep processing idempotent under duplicate order delivery.
- Add tests for all three outcomes and the race.

## Out of Scope

- General order persistence.
- Order analytics.
- Customer-only correlation.
- Repeat abandonment.
- Checkout deletion.
- Changing recovery statuses outside the existing lifecycle without architect approval.

## Requirements

Lookup order:
1. pending candidate;
2. existing `CheckoutRecovery`;
3. discard.

No queue scan is permitted.

Customer ID alone must not associate an order with recovery.

An unrelated order must not create a PostgreSQL order record or retained business-event record.

The order/candidate race must ensure that an order completing the checkout before recovery action is committed cannot result in an inappropriate recovery message.

The exact narrow locking/tombstone/transition mechanism may be selected by the repository agent, but it must remain scoped to the checkout and must be objectively tested.

## Work Items

- [x] Use v2 order contract including cart token.
- [x] Resolve/cancel pending candidate by indexed correlation.
- [x] Clean up candidate aliases.
- [x] Lookup existing recovery only when no candidate was cancelled.
- [x] Complete eligible recovery transactionally/idempotently.
- [x] Preserve status-history attribution with order ID.
- [x] Discard unrelated order.
- [x] Implement checkout-scoped race protection between candidate materialization and order processing.
- [x] Add duplicate-order test.
- [x] Add candidate/order race test.

## Interfaces / Contracts

Consumes:

- v2 order-completed contract from ARCH-001-SHARED-001;
- pending candidate/index from ARCH-001-BACKGROUND-002;
- materialization transition from ARCH-001-BACKGROUND-004.

Writes:

Existing `CheckoutRecovery` and status history only when a recovery already exists.

## Dependencies

- ARCH-001-BACKGROUND-004

## Enables

None

## Acceptance Criteria

- [x] Order matching a pending candidate prevents that candidate from entering recovery.
- [x] Order matching an existing recovery transitions it once to the appropriate completed state.
- [x] Unrelated order is discarded without durable order persistence.
- [x] Cart-token fallback does not scan BullMQ.
- [x] Duplicate order is idempotent.
- [x] Candidate/order concurrency test demonstrates no false recovery message for the protected race.
- [x] Terminal recovery statuses are not reopened or re-completed incorrectly.

## Validation

- [x] `npm test`
- [x] `npm run test:integration`
- [x] `npm run build`
- [x] `npm run prisma:validate`

## Implementation Notes

Prefer the narrowest checkout-scoped concurrency mechanism.

If the race cannot be made correct without changing the architecture or durable schema, return the task Blocked to `moda_architect`.

## Completion Report

### Status

Ready for Review
### Files Changed

- `moda-interact-background/src/domain/pending-recovery-candidate.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/order-recovery-correlation.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-005-handle-order-recovery-correlation.md`
### Work Completed

- Wired the shared v2 order-completed contract (including cart token) through the existing `handleOrderCompletedContract`/`handleOrderCompleted` boundary.
- Added O(1) `resolveCandidate` (checkout index first, indexed cart alias fallback) and `cancelCandidate` (removes the delayed BullMQ job plus both checkout and cart correlation indexes) to the pending-candidate service. No BullMQ queue scan is performed.
- Reworked `handleOrderCompleted` to follow the mandated lookup order: (1) cancel a matching pending candidate and its aliases; (2) transactionally complete and attribute an eligible existing `CheckoutRecovery` (with order ID in status-history metadata); (3) discard an unrelated order without creating any durable order/business record. Customer identity alone is rejected as a correlation.
- Completed existing recoveries once using the event completion timestamp (`completedAt`) and guarded against re-opening terminal statuses (`COMPLETED`/`EXPIRED`/`CANCELLED`).
- Implemented checkout-scoped race protection: a transient Redis mutex (`pending-recovery:lock:{shopId}:{checkoutToken}`) serialises the order path and the candidate materialization path for a single checkout, and an order-completion tombstone (`pending-recovery:order-completed:...`) recorded by the order path is checked by `materializeMaturedCandidate` before creating a recovery or sending a recovery message. Both the lock and tombstone are bounded by TTL.
- Added an order-recovery correlation test suite covering candidate cancellation, eligible recovery completion/attribution, event completion timestamp, terminal/no-reopen, unrelated-order discard, missing-correlation rejection, duplicate-order idempotency, and the tombstone race guard. Extended the materialization suite with a `discarded-order-completed` test and the pending-candidate suite with cart-fallback/alias-cleanup/tombstone tests.
### Validation Results

- `npm test`: 42 unit tests pass; only the pre-existing, unrelated `tests/unit/services/recovery-routing.service.test.ts` failure remains (`prisma.customerPhone.findMany` undefined in its mock path). Touched suites: `order-recovery-correlation` (8), `matured-candidate.materialization` (11), `pending-recovery-candidate` (8), `abandoned-checkout-lookup` (8) all green.
- `npm run test:integration`: 1 passed, 2 skipped (Shopify integration guarded by unset `SHOPIFY_TEST_SHOP`/`SHOPIFY_TEST_PRODUCT_QUERY`).
- `npm run build`: pass (Prisma generate + tsc).
- `npm run prisma:validate`: pass.
### Deviations

None.

### Assumptions

- The order path and materialization path both key the checkout mutex/tombstone on `shopId + checkoutToken`. For rare cart-only orders, the candidate is resolved via the indexed cart alias first to obtain the checkout token for the lock scope.
- The order-completion tombstone TTL (1 hour) covers the candidate delay window plus the `RECOVERY_CANDIDATE_TTL_BUFFER_MS`, so an in-flight materialization remains suppressed for a checkout already processed by an order.
- The pre-existing `recovery-routing.service.test.ts` failure is unrelated to BACKGROUND-005.
### Unresolved Issues

- Repository-wide `npm test` remains red solely due to the pre-existing `tests/unit/services/recovery-routing.service.test.ts` failure.
### Architectural Concerns

None. The concurrency mechanism is checkout-scoped, transient (Redis), requires no durable schema change, and no cross-repository contract was introduced.
## Architect Review

### Review Status

Complete

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending review.

### Follow-up

None


