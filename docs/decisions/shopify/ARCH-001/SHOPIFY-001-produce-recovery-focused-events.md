---
id: ARCH-001-SHOPIFY-001
architecture_id: ARCH-001
title: Produce recovery-focused Shopify webhook events
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: review
priority: 20
executor: codex
claimed_at: 2026-08-28T17:42:16Z
attempt: 1
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

- [x] Import the shared v2 contract.
- [x] Split checkout-create and checkout-update topic plans.
- [x] Replace the current large checkout normalizer with recovery-focused normalizers.
- [x] Preserve `abandoned_checkout_url` on checkout creation.
- [x] Preserve `cart_token` on order creation.
- [x] Update event-envelope typing/parsing.
- [x] Update ordering/correlation key construction.
- [x] Remove unused normalization helpers for customer/line-item/price data from this ingress path.
- [x] Update normalization tests.
- [x] Update ingress-service tests.

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

- [x] `checkouts/create` and `checkouts/update` produce distinct shared event types.
- [x] Checkout-create event contains no customer, line-item, total or address payload.
- [x] Checkout-update event contains no basket snapshot.
- [x] Order event contains `cartToken` when supplied by Shopify.
- [x] Webhook HMAC/authentication flow is unchanged.
- [x] Unsupported/cart-topic behaviour is unchanged by this task.
- [x] Unit tests prove the new normalized shapes.

## Validation

- [x] `npm test -- --run`
- [x] `npm run typecheck`
- [x] `npm run lint`

## Implementation Notes

Do not add state-dependent filtering to the HTTP ingress.

Do not change Shopify subscriptions for checkout deletion or cart topics in this task.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/app/services/webhooks/checkout-normalization.ts`
- `moda-interact/app/services/webhooks/order-normalization.ts`
- `moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts`
- `moda-interact/app/services/webhooks/shopify-webhook-queue.server.ts`
- `moda-interact/tests/unit/webhooks/shopify-normalization.test.js`
- `moda-interact/tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `moda-interact/tests/unit/webhooks/shopify-webhook-queue.server.test.js`
- `docs/decisions/shopify/ARCH-001/SHOPIFY-001-produce-recovery-focused-events.md`

### Work Completed

- Replaced legacy checkout-observed normalization with v2 recovery-focused normalizers:
	- checkout create now emits only `checkoutToken`, `cartToken`, `abandonedCheckoutUrl`, and `checkoutCreatedAt`.
	- checkout update now emits only `checkoutToken`.
- Updated order normalization to v2 shape with `orderId`, `checkoutToken`, `cartToken`, and `completedAt`.
- Updated ingress topic classification so `checkouts/create` and `checkouts/update` map to distinct event types and publication paths.
- Updated envelope construction to v2 schema and parsing via shared v2 runtime parser.
- Updated ordering key construction to shared v2 helpers for checkout and order correlation.
- Added distinct checkout-updated publication path and job contract usage in queue publisher.
- Removed pre-recovery customer/line-item/total transport from this ingress path.
- Updated normalization, ingress, and queue tests to validate new minimal v2 payloads and topic classification.

### Validation Results

- `npm test -- --run`: pass (5 files, 24 tests).
- `npm run typecheck`: fail with pre-existing repository errors unrelated to this task (example: `app/db.server.js` cannot find `process`, plus additional existing errors across billing/routes).
- `npm run lint`: fail with pre-existing repository lint issues unrelated to this task (example: missing `prop-types` in onboarding component, existing `process` and unused-import issues in billing/routes).

### Deviations

None.

### Assumptions

- Existing repository-level typecheck/lint failures are pre-existing and out of scope for this task.

### Unresolved Issues

- Repository-level `npm run typecheck` and `npm run lint` are currently red due to pre-existing issues outside webhook-ingress scope.

### Architectural Concerns

None.

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
