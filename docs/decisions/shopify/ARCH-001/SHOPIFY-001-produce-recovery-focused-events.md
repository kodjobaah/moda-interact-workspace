---
id: ARCH-001-SHOPIFY-001
architecture_id: ARCH-001
title: Produce recovery-focused Shopify webhook events
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-001-SHARED-001"]
enables: ["ARCH-001-SHOPIFY-002"]
created: 2026-08-28
updated: 2026-08-28
---

# Produce Recovery-Focused Shopify Webhook Events

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Update Shopify webhook classification and normalization so `moda-interact` produces the canonical minimal ARCH-001 events.

## Context

The current producer normalizes checkout create/update into one large `checkout.observed` payload containing basket/customer state. ARCH-001 intentionally avoids carrying that state before recovery and gives create/update distinct meanings.

## Scope

- Adopt the shared ARCH-001 v2 event schemas.
- Classify `checkouts/create` and `checkouts/update` separately.
- Normalize `checkouts/create` to the agreed minimal candidate fields.
- Normalize `checkouts/update` to the agreed recovery-correlation fields.
- Normalize `orders/create` to the new order payload including `cartToken`.
- Build the canonical shared envelope and correlation/ordering key.
- Remove producer dependence on basket/customer fields that are no longer in the contract.
- Update unit tests for normalization and ingress classification.

## Out of Scope

- BullMQ delay/candidate lifecycle.
- Recovery-state lookups.
- Shopify GraphQL.
- Background business processing.
- Checkout deletion.
- Cart webhook architecture.

## Requirements

Webhook authentication must remain unchanged.

The producer must not fetch Shopify GraphQL data.

The producer must not query `CheckoutRecovery` to decide whether an update matters.

The event emitted for `checkouts/create` must include only:
- checkout token;
- cart token if available;
- abandoned checkout URL if available;
- checkout creation timestamp if available.

The event emitted for `checkouts/update` must not transport the basket.

The order event must preserve `cart_token` in addition to `checkout_token`.

Invalid required identifiers must follow the existing rejected-payload behaviour rather than emitting malformed events.

## Work Items

- [ ] Import the shared v2 contract.
- [ ] Split checkout-create and checkout-update topic plans.
- [ ] Replace the current large checkout normalizer with recovery-focused normalizers.
- [ ] Preserve `abandoned_checkout_url` on checkout creation.
- [ ] Preserve `cart_token` on order creation.
- [ ] Update event-envelope typing/parsing.
- [ ] Update ordering/correlation key construction.
- [ ] Remove unused normalization helpers for customer/line-item/price data from this ingress path.
- [ ] Update normalization tests.
- [ ] Update ingress-service tests.

## Interfaces / Contracts

Consumes:

ARCH-001-SHARED-001

Canonical package:

`@modainteract/moda-interact-shared`

Produces:

- v2 checkout-created event;
- v2 checkout-updated event;
- v2 order-completed event.

## Dependencies

- ARCH-001-SHARED-001

## Enables

- ARCH-001-SHOPIFY-002

## Acceptance Criteria

- [ ] `checkouts/create` and `checkouts/update` produce distinct shared event types.
- [ ] Checkout-create event contains no customer, line-item, total or address payload.
- [ ] Checkout-update event contains no basket snapshot.
- [ ] Order event contains `cartToken` when supplied by Shopify.
- [ ] Webhook HMAC/authentication flow is unchanged.
- [ ] Unsupported/cart-topic behaviour is unchanged by this task.
- [ ] Unit tests prove the new normalized shapes.

## Validation

- [ ] `npm test -- --run`
- [ ] `npm run typecheck`
- [ ] `npm run lint`

## Implementation Notes

Do not add state-dependent filtering to the HTTP ingress.

Do not change Shopify subscriptions for checkout deletion or cart topics in this task.

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
