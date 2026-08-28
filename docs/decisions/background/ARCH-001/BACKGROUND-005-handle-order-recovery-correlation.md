---
id: ARCH-001-BACKGROUND-005
architecture_id: ARCH-001
title: Handle order recovery correlation and cancellation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
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

- [ ] Use v2 order contract including cart token.
- [ ] Resolve/cancel pending candidate by indexed correlation.
- [ ] Clean up candidate aliases.
- [ ] Lookup existing recovery only when no candidate was cancelled.
- [ ] Complete eligible recovery transactionally/idempotently.
- [ ] Preserve status-history attribution with order ID.
- [ ] Discard unrelated order.
- [ ] Implement checkout-scoped race protection between candidate materialization and order processing.
- [ ] Add duplicate-order test.
- [ ] Add candidate/order race test.

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

- [ ] Order matching a pending candidate prevents that candidate from entering recovery.
- [ ] Order matching an existing recovery transitions it once to the appropriate completed state.
- [ ] Unrelated order is discarded without durable order persistence.
- [ ] Cart-token fallback does not scan BullMQ.
- [ ] Duplicate order is idempotent.
- [ ] Candidate/order concurrency test demonstrates no false recovery message for the protected race.
- [ ] Terminal recovery statuses are not reopened or re-completed incorrectly.

## Validation

- [ ] `npm test`
- [ ] `npm run test:integration`
- [ ] `npm run build`
- [ ] `npm run prisma:validate`

## Implementation Notes

Prefer the narrowest checkout-scoped concurrency mechanism.

If the race cannot be made correct without changing the architecture or durable schema, return the task Blocked to `moda_architect`.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

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
