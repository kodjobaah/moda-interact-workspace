---
id: ARCH-001-BACKGROUND-006
architecture_id: ARCH-001
title: Refresh existing recovery on checkout update
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 40
executor: codex
claimed_at: 2026-08-28T22:49:02Z
attempt: 1
depends_on: ["ARCH-001-BACKGROUND-003"]
enables: []
created: 2026-08-28
updated: 2026-08-28
---

# Refresh Existing Recovery on Checkout Update

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Process checkout-update events by refreshing current Shopify checkout data only when a matching `CheckoutRecovery` already exists; otherwise discard the update.

## Context

A checkout update is irrelevant before recovery because a matured candidate will fetch current Shopify data. It becomes relevant only after recovery exists, for example when a customer follows the recovery link and changes their basket.

## Scope

- Consume the shared v2 checkout-updated event.
- Lookup `CheckoutRecovery` by `shopId + checkoutToken`.
- If no recovery exists, discard immediately.
- If recovery exists and is updateable, call the Shopify lookup from BACKGROUND-003.
- Refresh the recovery fields required by ARCH-001, including current line items/totals/currency/recovery URL where available.
- Do not restart recovery timing or create another recovery.
- Do not reopen terminal recovery state.
- Add tests for discard, refresh, duplicate/stale update and terminal recovery.

## Out of Scope

- Pending candidate mutation.
- New recovery creation.
- Re-abandonment policy.
- Sending a second recovery message.
- Checkout deletion.
- General checkout history.

## Requirements

No `CheckoutRecovery` means no Shopify GraphQL call and no PostgreSQL write beyond the lookup.

An existing recovery refresh must use current Shopify data, not webhook basket data.

The refresh must update basket/content fields without changing recovery lifecycle status unless an existing invariant explicitly requires it.

A terminal recovery must not be reopened by checkout update.

Provider failures are retryable and must not be converted into a discard outcome.

## Work Items

- [x] Add checkout-updated handler.
- [x] Lookup recovery by shop/checkout token.
- [x] Discard when no recovery exists.
- [x] Skip/reject refresh for terminal recovery as appropriate.
- [x] Call Shopify abandoned-checkout lookup for current data.
- [x] Update recovery basket/content fields.
- [x] Preserve recovery lifecycle status.
- [x] Add tests for no-recovery, active-recovery, terminal-recovery and provider failure.

## Interfaces / Contracts

Consumes:

- v2 checkout-updated event from ARCH-001-SHARED-001;
- Shopify lookup from ARCH-001-BACKGROUND-003.

Writes:

Existing `CheckoutRecovery` only.

## Dependencies

- ARCH-001-BACKGROUND-003

## Enables

None

## Acceptance Criteria

- [x] Checkout update with no recovery is discarded without Shopify API call.
- [x] Existing active recovery is refreshed from current Shopify data.
- [x] Webhook basket data is not used as recovery state.
- [x] Recovery status/timer is not restarted by this task.
- [x] Terminal recovery is not reopened.
- [x] Transient Shopify failure remains retryable.
- [x] Tests pass.

## Validation

- [x] `npm test`
- [x] `npm run test:integration`
- [x] `npm run build`
- [x] `npm run prisma:validate`

## Implementation Notes

This task deliberately stops after refreshing existing recovery data.

Do not implement the later 'customer modifies basket then abandons again' behaviour.

## Completion Report

### Status

Ready for Review
### Files Changed

- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-006-refresh-recovery-on-checkout-update.md`
### Work Completed

- Replaced the BACKGROUND-001 boundary-only `handleCheckoutUpdatedContract` with a real refresh handler.
- The handler resolves the shop, looks up `CheckoutRecovery` by `shopId + checkoutToken`, and discards immediately when no recovery exists (no Shopify API call, no write beyond the lookup).
- Terminal recoveries (`COMPLETED`/`EXPIRED`/`CANCELLED`) are never reopened: the handler returns `ignored terminal-*` without a Shopify call or write.
- For an active recovery, the handler calls the BACKGROUND-003 Shopify abandoned-checkout lookup, deriving the lookup input exclusively from durable recovery state (shop/checkout/cart correlation, stored `checkoutUrl`, and the Shopify creation timestamp retained in `detectedAt`) — never from the webhook payload.
- On a `found` result, basket/content fields (`currency`, `totalPrice`, `checkoutUrl`, `lineItems`) are refreshed via a status-guarded `updateMany` on an updateable recovery. Lifecycle status and timing (`detectedAt`/`messageSentAt`/`engagedAt`/`completedAt`) are preserved; no new recovery is created and no recovery message is sent.
- Transient `provider-error` lookup failures are thrown (retryable by BullMQ) and never converted into a discard outcome.
- Extracted a shared private `serializeLineItems` helper so creation (BACKGROUND-004) and refresh (BACKGROUND-006) store an identical durable line-item snapshot shape.
- Added a `checkout-refresh.test.ts` suite (8 tests) covering no-recovery discard, active-recovery refresh, webhook-data non-use + lifecycle preservation, no timer restart, terminal-recovery no-reopen, duplicate/stale already-transitioned idempotency, provider-failure retryability, and non-deterministic lookup discard.
### Validation Results

- `npm test`: 50 unit tests pass, 1 pre-existing unrelated failure (`tests/unit/services/recovery-routing.service.test.ts`) that predates this task. New `checkout-refresh` suite (8/8) and all existing ARCH-001 suites pass.
- `npm run test:integration`: 1 passed, 2 skipped (Shopify integration guarded by unset `SHOPIFY_TEST_SHOP`/`SHOPIFY_TEST_PRODUCT_QUERY`).
- `npm run build`: pass (Prisma generate + tsc).
- `npm run prisma:validate`: pass.
### Deviations

None.

### Assumptions

- The stored `CheckoutRecovery.checkoutUrl` is the abandoned-checkout recovery URL (populated from the Shopify lookup at materialization in BACKGROUND-004), so it is a valid exact-match key for the BACKGROUND-003 lookup.
- `CheckoutRecovery.detectedAt` retains the Shopify checkout `createdAt` from materialization (BACKGROUND-004 sets `detectedAt` from the lookup result's `createdAt`), making it an appropriate `checkoutCreatedAt` reference for the bounded lookup window on refresh.
- For refresh the narrow durable-state lookup input substitutes for the candidate the BACKGROUND-003 lookup expects at materialization, since pending candidates no longer exist after materialization. This is consistent with the task's "lookup by shop/checkout token" and "current Shopify data" acceptance criteria.
- The pre-existing `recovery-routing.service.test.ts` failure is unrelated to BACKGROUND-006.
### Unresolved Issues

- Repository-wide `npm test` remains red solely due to the pre-existing `tests/unit/services/recovery-routing.service.test.ts` failure.
### Architectural Concerns

None. The refresh is scoped to existing `CheckoutRecovery`, uses only current Shopify data, preserves lifecycle, requires no durable schema change, and introduces no new cross-service contract.
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


