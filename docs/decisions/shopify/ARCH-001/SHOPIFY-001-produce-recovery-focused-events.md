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
attempt: 2
depends_on: ["ARCH-001-SHARED-001"]
enables: ["ARCH-001-SHOPIFY-002"]
created: 2026-08-28
updated: 2026-08-29
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
- `moda-interact/app/services/webhooks/webhook-normalization-utils.ts`
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

### Corrections (Architect Review round 1)

- **Timestamp normalization.** Added a shared repository-local `normalizeTimestamp()` helper (`webhook-normalization-utils.ts`) that parses a provider timestamp and returns canonical UTC ISO (`Date -> toISOString()`), or `null` for absent/unparseable values. `checkoutCreatedAt` (checkout-created) and `completedAt` (order-completed, required; falls back to `updated_at`) are now normalized through it. Valid Shopify offset timestamps such as the fixture `2021-12-31T19:00:00-05:00` normalize to `2022-01-01T00:00:00.000Z`, satisfying the canonical `z.iso.datetime()` contract; invalid timestamps are rejected rather than emitting a malformed event.
- **Shared schema-version constant.** `buildShopifyEventEnvelope()` now sets `schemaVersion` from `SHOPIFY_COMMERCE_EVENT_SCHEMA_VERSION_V2` (imported from `@modainteract/moda-interact-shared/shopify`) instead of the hard-coded literal `2`, so producer versioning cannot drift from the canonical contract.
- **Tests.** Added offset-timestamp coverage using the actual fixture value `2021-12-31T19:00:00-05:00` in both the normalization unit tests and the ingress-service test (proving normalize -> envelope -> shared-schema parse succeeds), plus tests for unparseable/invalid timestamps and `updated_at` fallback.

### Validation Results

- `npm test -- --run`: pass (5 files, 31 tests).
- `npm run typecheck`: fail with pre-existing repository errors in files outside this task's changes (e.g. `app/shopify.server.js` cannot find `process`, `shopify-webhook-queue.server.ts` strict-null queue guards). The files changed by this task produce zero typecheck errors.
- `npm run lint`: fail with pre-existing repository lint issues outside this task's changes (missing `prop-types`, `process`/unused-import errors across onboarding/billing/privacy/routes). The files changed by this task produce zero lint errors.
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

Changes Requested - Corrections Addressed, Re-review Required
### Review Notes

Both round-1 requested corrections have been implemented and validated.

1. **Shopify timestamps normalized to canonical UTC ISO.** Added `webhook-normalization-utils.ts` with `normalizeTimestamp()`; `checkoutCreatedAt` and order `completedAt` (with `updated_at` fallback) now normalize valid provider timestamps via `Date.toISOString()` and reject invalid ones. Tests use the actual supplied fixture offset timestamp `2021-12-31T19:00:00-05:00` and assert the normalized UTC ISO form (`2022-01-01T00:00:00.000Z`) through both the normalizers and the full ingress -> envelope -> shared-schema parse path.

2. **Shared schema-version constant used.** `buildShopifyEventEnvelope()` now sets `schemaVersion` from `SHOPIFY_COMMERCE_EVENT_SCHEMA_VERSION_V2`.

Validation re-run: `npm test -- --run` passes (31 tests). Repository-level typecheck/lint remain red from the same pre-existing, out-of-scope issues noted previously; none of the files changed by this task produce typecheck or lint errors.
### Reviewed Files

- `moda-interact/app/services/webhooks/checkout-normalization.ts`
- `moda-interact/app/services/webhooks/order-normalization.ts`
- `moda-interact/app/services/webhooks/webhook-normalization-utils.ts`
- `moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts`
- relevant webhook normalization/ingress tests
- supplied `shopify-webhook-payloads/checkouts/create.json` and `orders/create.json` timestamp shapes

### Validation Reviewed

Agent re-ran `npm test -- --run` (31 tests pass) and confirmed the offset-timestamp and shared-version-constant corrections compile cleanly within their changed files. Repository-wide typecheck/lint remain red from pre-existing, unrelated issues.
### Architecture Conformance

Pending re-review. The round-1 conformance finding (producer not reliably satisfying the canonical runtime contract for real Shopify offset timestamps) is believed resolved by timestamp normalization; the producer versioning is now bound to the shared schema-version constant.
### Follow-up

Return this same task to `moda_app`. Re-review the two round-1 corrections (timestamp normalization + shared schema-version constant). If accepted, transition to `complete`; otherwise reproduce the remaining finding.

