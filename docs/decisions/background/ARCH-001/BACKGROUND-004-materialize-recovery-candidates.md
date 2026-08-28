---
id: ARCH-001-BACKGROUND-004
architecture_id: ARCH-001
title: Materialize matured recovery candidates
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-001-BACKGROUND-002", "ARCH-001-BACKGROUND-003"]
enables: ["ARCH-001-BACKGROUND-005"]
created: 2026-08-28
updated: 2026-08-28
---

# Materialize Matured Recovery Candidates

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

When a delayed pending candidate matures, retrieve the current checkout from Shopify and create the durable `CheckoutRecovery` only if it is still recoverable.

## Context

This task is the transition from transient Redis/BullMQ state into durable Moda recovery state. It replaces the current behaviour where the delayed webhook payload itself is used to populate `CheckoutRecovery`.

## Scope

- Consume the internal matured-candidate job.
- Call the Shopify lookup owned by ARCH-001-BACKGROUND-003.
- If checkout is not found/no longer recoverable, discard and clean up candidate state.
- If recoverable, create/upsert `CheckoutRecovery` using current Shopify data.
- Resolve/create the customer from the current Shopify result.
- Populate current line items, totals, currency and recovery URL.
- Preserve unique `shopId + checkoutToken` idempotency.
- Continue the existing recovery conversation/message workflow after durable recovery creation.
- Ensure legacy v1 delayed checkout jobs entering this path ignore embedded basket/customer data.
- Add tests for idempotency and recoverability decisions.

## Out of Scope

- Pending candidate scheduling.
- Order cancellation/completion.
- Checkout-update refresh.
- New repeat-abandonment policy.
- Checkout deletion.
- Database schema changes unless separately approved.

## Requirements

Webhook payload basket data must not populate `CheckoutRecovery`.

The Shopify lookup result is the source used to populate recovery state.

If Shopify reports the checkout completed/not recoverable, no recovery record or recovery message is created.

Duplicate candidate execution must not send duplicate recovery messages.

Existing terminal `CheckoutRecovery` records must not be reopened.

Any database/schema limitation discovered must be returned to `moda_architect`.

## Work Items

- [ ] Add matured-candidate handler.
- [ ] Call current Shopify checkout lookup.
- [ ] Discard not-found/non-recoverable candidates.
- [ ] Map current Shopify result into existing recovery fields.
- [ ] Adapt customer resolution to use Shopify lookup data rather than old webhook event type.
- [ ] Create/upsert recovery idempotently.
- [ ] Continue existing recovery messaging only for eligible DETECTED recovery.
- [ ] Ensure duplicate execution cannot duplicate message/recovery.
- [ ] Add unit/integration tests.

## Interfaces / Contracts

Consumes:

- internal pending candidate from ARCH-001-BACKGROUND-002;
- Shopify lookup from ARCH-001-BACKGROUND-003.

Writes:

- existing PostgreSQL `CheckoutRecovery`;
- existing `Customer`/phone state as required by current recovery workflow.

## Dependencies

- ARCH-001-BACKGROUND-002
- ARCH-001-BACKGROUND-003

## Enables

- ARCH-001-BACKGROUND-005

## Acceptance Criteria

- [ ] A candidate does not create recovery data from its stored webhook payload.
- [ ] Current Shopify data populates the recovery.
- [ ] Completed/non-recoverable checkout creates no recovery/message.
- [ ] Same candidate executed twice produces at most one recovery and one recovery-send workflow.
- [ ] Existing terminal recovery is not reopened.
- [ ] Current recovery message flow remains functional for a newly materialized recovery.

## Validation

- [ ] `npm test`
- [ ] `npm run test:integration`
- [ ] `npm run build`
- [ ] `npm run prisma:validate`

## Implementation Notes

Do not redesign message copy or downstream CommerceAgent behaviour.

Keep the transition from 'candidate' to 'recovery' explicit in code so the order-race task can protect it.

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
