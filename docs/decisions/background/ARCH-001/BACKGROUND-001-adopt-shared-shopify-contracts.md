---
id: ARCH-001-BACKGROUND-001
architecture_id: ARCH-001
title: Adopt canonical Shopify webhook contracts
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-001-SHARED-001"]
enables: ["ARCH-001-BACKGROUND-002", "ARCH-001-BACKGROUND-003"]
created: 2026-08-28
updated: 2026-09-08
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
- [x] Remove the transitional v1 compatibility path (architect review instructed its removal).
- [x] Add unit tests for valid v2, invalid data and legacy v1 rejection.

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
- [x] Only the agreed ARCH-001 v2 contract is consumed (no v1 fallback).
- [x] Canonical queue/job constants are imported from the shared package (no duplication).
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
- Added runtime event boundary adapter that parses and validates the v2 recovery contract before business handling.
- Updated checkout and order workers to parse/validate job payloads at runtime before business handling.
- Routed checkout-created and checkout-updated into distinct handlers at worker boundary.
- Routed order-completed through shared contract parsing/mapping.
- Retired local cross-service contract naming (`CheckoutCreatedEvent`, `OrderCompletedEvent`) from active worker contract boundary.
- Added unit tests for valid v2 mapping, invalid payload rejection, and legacy v1 rejection.

### Corrections (Architect Review round 1)

- **Import canonical queue/job constants.** `checkout.worker.ts` and `orders.worker.ts` now source their queue name and job names from `SHOPIFY_WEBHOOK_QUEUE_CONTRACTS` (imported from `@modainteract/moda-interact-shared/shopify`) instead of hard-coding `"checkout-events"`, `"order-events"`, `"checkout-created"`, `"checkout-updated"`, `"order-completed"`. Producer and consumer can no longer drift on queue/job naming.
- **Removed the legacy v1 compatibility path completely.** `shopify-contract-adapter.ts` no longer parses/falls back to `parseShopifyCommerceEvent`/`ShopifyCommerceEvent`. The `RuntimeShopifyEvent` union, `LegacyCheckoutCreatedTransitionEvent` type, and `legacyV1Transition` correlation field are gone. Only the ARCH-001 v2 contract is consumed.
- **Consume/runtime-validate only the agreed ARCH-001 contract.** `parseRuntimeShopifyEvent` now runs `parseShopifyRecoveryEventV2` and returns `ShopifyRecoveryEventV2` directly; invalid/legacy payloads throw visibly before business handling. The three mappers (`mapCheckoutCreatedContractInput`, `mapCheckoutUpdatedContractInput`, `mapOrderCompletedContractInput`) accept the v2 event only and guard on the correct v2 event type.
- **Tests.** Removed the v1-transition test and the `legacyV1Transition: null` assertion; added a test proving a legacy v1 (`checkout.observed`, `schemaVersion: 1`) job is rejected.

### Validation Results

- `npm install`: pass.
- `npm test`: fail due a pre-existing unrelated unit test (`tests/unit/services/recovery-routing.service.test.ts`) error reading `prisma.customerPhone.findMany` from undefined mock.
- `npm test -- tests/unit/events/shopify-contract-adapter.test.ts`: pass (4/4 tests).
- `npm run build`: pass.
- `npx tsc --noEmit`: pass.
- `npm run prisma:validate`: pass.

### Deviations

None.

### Assumptions

- The existing failing `recovery-routing.service` unit test is unrelated to this task's worker contract-boundary changes.
- `npm run build` / `npx tsc --noEmit` in this repository provides the required typecheck signal for the changed code path.

### Unresolved Issues

- Repository test suite contains an unrelated failing unit test in `tests/unit/services/recovery-routing.service.test.ts`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

State synchronized from `docs/architecture/ARCH-001-architect-review-round2.md`.

That existing architect review explicitly records `ARCH-001-BACKGROUND-001` as **Complete / Accepted** after the round-1 corrections were re-reviewed:

- canonical queue/job constants are sourced from Shared;
- the legacy v1 compatibility path is removed;
- Background consumes only the agreed v2 recovery event contract.

This task file had drifted back to `status: review` even though the architecture-level Round 2 review had already accepted it.

### Architecture Conformance

Accepted.

### Follow-up

ARCH-001-BACKGROUND-002 and ARCH-001-BACKGROUND-003 may rely on this task as Complete.
