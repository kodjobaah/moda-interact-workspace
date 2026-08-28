---
id: ARCH-001-BACKGROUND-006
architecture_id: ARCH-001
title: Refresh existing recovery on checkout update
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add checkout-updated handler.
- [ ] Lookup recovery by shop/checkout token.
- [ ] Discard when no recovery exists.
- [ ] Skip/reject refresh for terminal recovery as appropriate.
- [ ] Call Shopify abandoned-checkout lookup for current data.
- [ ] Update recovery basket/content fields.
- [ ] Preserve recovery lifecycle status.
- [ ] Add tests for no-recovery, active-recovery, terminal-recovery and provider failure.

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

- [ ] Checkout update with no recovery is discarded without Shopify API call.
- [ ] Existing active recovery is refreshed from current Shopify data.
- [ ] Webhook basket data is not used as recovery state.
- [ ] Recovery status/timer is not restarted by this task.
- [ ] Terminal recovery is not reopened.
- [ ] Transient Shopify failure remains retryable.
- [ ] Tests pass.

## Validation

- [ ] `npm test`
- [ ] `npm run test:integration`
- [ ] `npm run build`
- [ ] `npm run prisma:validate`

## Implementation Notes

This task deliberately stops after refreshing existing recovery data.

Do not implement the later 'customer modifies basket then abandons again' behaviour.

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
