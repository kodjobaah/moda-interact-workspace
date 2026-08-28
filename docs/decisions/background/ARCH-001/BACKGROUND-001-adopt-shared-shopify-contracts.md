---
id: ARCH-001-BACKGROUND-001
architecture_id: ARCH-001
title: Adopt canonical Shopify webhook contracts
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 20
executor: codex
claimed_at: 2026-08-28T18:10:27Z
attempt: 1
depends_on: ["ARCH-001-SHARED-001"]
enables: ["ARCH-001-BACKGROUND-002", "ARCH-001-BACKGROUND-003"]
created: 2026-08-28
updated: 2026-08-28
---

# Adopt Canonical Shopify Webhook Contracts

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Make `moda-interact-background` consume and runtime-validate the canonical shared Shopify contracts instead of repository-local event shapes.

## Context

The current background workers expect old top-level `CheckoutCreatedEvent` and `OrderCompletedEvent` structures, while `moda-interact` publishes the shared envelope. This is the immediate producer/consumer integration defect identified by ARCH-001.

## Scope

- Add `@modainteract/moda-interact-shared` as a background dependency.
- Type workers using shared contracts.
- Runtime-parse job data with shared schemas before business processing.
- Route checkout-created, checkout-updated and order-completed jobs distinctly.
- Remove/retire local duplicate cross-service event interfaces.
- Add a temporary compatibility path for already-queued v1 events during rollout.
- Ensure legacy v1 checkout events ignore their embedded basket snapshot when entering the new recovery flow.
- Add worker contract tests.

## Out of Scope

- Pending candidate creation.
- Shopify GraphQL lookup.
- CheckoutRecovery creation.
- Order cancellation/completion logic.
- Checkout update refresh logic.
- Database schema changes.

## Requirements

Shared runtime validation is mandatory.

Invalid cross-service payloads must fail visibly rather than being treated as valid business events.

Repository-local duplicate definitions of the canonical contract must be removed.

The temporary v1 compatibility path must be explicitly identifiable and must not redefine v1 data as v2.

Legacy v1 checkout jobs may use their identifiers for transition, but their customer/line-item/total payload must not become authoritative recovery data.

## Work Items

- [x] Add shared-package dependency.
- [x] Import shared queue/event schemas and types.
- [x] Parse worker job data at the runtime boundary.
- [x] Route checkout-created and checkout-updated separately.
- [x] Route order-completed using the shared contract.
- [x] Remove old local `CheckoutCreatedEvent` contract usage.
- [x] Remove old local `OrderCompletedEvent` contract usage.
- [x] Add transitional v1 handling for queued jobs.
- [x] Add unit tests for valid v2, invalid data and legacy v1 transition.

## Interfaces / Contracts

Contract owner:

ARCH-001-SHARED-001

Package:

`@modainteract/moda-interact-shared`

Consumer:

`moda-interact-background`

## Dependencies

- ARCH-001-SHARED-001

## Enables

- ARCH-001-BACKGROUND-002
- ARCH-001-BACKGROUND-003

## Acceptance Criteria

- [x] Background no longer maintains a separate structural copy of the v2 checkout/order contract.
- [x] Every cross-service job is runtime validated.
- [x] Checkout create and checkout update reach distinct handlers.
- [x] Invalid payloads fail with clear diagnostics.
- [x] Transitional v1 checkout jobs do not use embedded basket data to populate recovery.
- [x] Background build/typecheck succeeds with the shared dependency.

## Validation

- [x] `npm test`
- [x] `npm run build`
- [x] `npm run prisma:validate`

## Implementation Notes

This task establishes the boundary only. Keep business handlers thin/stubbed where later ARCH-001 tasks own behaviour.

If package/dependency versioning prevents safe rolling deployment, report it as an architectural concern.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/events/shopify-contract-adapter.ts`
- `moda-interact-background/src/events/checkout-events.ts`
- `moda-interact-background/src/workers/checkout.worker.ts`
- `moda-interact-background/src/workers/orders.worker.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/services/customer.service.ts`
- `moda-interact-background/src/services/conversation.message.service.ts`
- `moda-interact-background/tests/unit/events/shopify-contract-adapter.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-001-adopt-shared-shopify-contracts.md`

### Work Completed

- Added shared package dependency `@modainteract/moda-interact-shared` to consume canonical cross-service Shopify contracts.
- Added runtime event boundary adapter to parse v2 contracts first and fall back to explicit v1 transition parsing for already-queued legacy jobs.
- Updated checkout and order workers to parse/validate job payloads at runtime before business handling.
- Routed checkout-created and checkout-updated into distinct handlers at worker boundary.
- Routed order-completed through shared contract parsing/mapping.
- Added explicit transitional v1 mapping path that carries only correlation identifiers and does not treat legacy customer/line-item/total payload as authoritative.
- Retired local cross-service contract naming (`CheckoutCreatedEvent`, `OrderCompletedEvent`) from active worker contract boundary.
- Added unit tests for valid v2 mapping, invalid payload rejection, and legacy v1 transition behaviour.

### Validation Results

- `npm install`: pass.
- `npm test`: fail due a pre-existing unrelated unit test (`tests/unit/services/recovery-routing.service.test.ts`) error reading `prisma.customerPhone.findMany` from undefined mock.
- `npm test -- tests/unit/events/shopify-contract-adapter.test.ts`: pass (4/4 tests).
- `npm run build`: pass.
- `npm run prisma:validate`: pass.

### Deviations

None.

### Assumptions

- The existing failing `recovery-routing.service` unit test is unrelated to this task's worker contract-boundary changes.
- `npm run build` in this repository provides the required typecheck signal for the changed code path.

### Unresolved Issues

- Repository test suite contains an unrelated failing unit test in `tests/unit/services/recovery-routing.service.test.ts`.

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
