---
id: ARCH-001-SHARED-001
architecture_id: ARCH-001
title: Define recovery-focused Shopify webhook contracts
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 10
executor: codex
claimed_at: 2026-08-28T17:02:29Z
attempt: 1
depends_on: []
enables: ["ARCH-001-SHOPIFY-001", "ARCH-001-BACKGROUND-001"]
created: 2026-08-28
updated: 2026-08-28
---

# Define Recovery-Focused Shopify Webhook Contracts

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Define the canonical versioned cross-service contracts for checkout creation, checkout update and order completion used by ARCH-001.

## Context

The current shared contract uses one `checkout.observed` event containing customer, totals and line items. ARCH-001 no longer transports pre-recovery basket state. Checkout creation, checkout update and order completion also have different business meanings and need distinct event contracts.

This task is the contract owner for all producer and consumer work in ARCH-001.

## Scope

- Introduce a new recovery-focused Shopify commerce contract version rather than mutating the existing v1 contract in place.
- Define distinct events for:
  - checkout created;
  - checkout updated;
  - order completed.
- Define minimal strict payload schemas.
- Add `cartToken` to the order contract.
- Define queue/job-name constants needed across `moda-interact` and `moda-interact-background`.
- Define deterministic identifiers/correlation helpers used across repositories.
- Export runtime parsers/type guards for the new version.
- Preserve existing v1 exports/parsing long enough to support rolling deployment and already-queued jobs.

## Out of Scope

- Shopify webhook HTTP implementation.
- BullMQ producer implementation.
- Background recovery logic.
- Shopify GraphQL queries.
- Database schema changes.
- Checkout deletion events.

## Requirements

The v2 logical payloads must represent:

`checkout.created`
- `checkoutToken`
- `cartToken` nullable
- `abandonedCheckoutUrl` nullable
- `checkoutCreatedAt` nullable

`checkout.updated`
- `checkoutToken`

`order.completed`
- `orderId`
- `checkoutToken` nullable
- `cartToken` nullable
- `completedAt`

The common envelope continues to carry tenant identity, provider topic, delivery/event identifiers, timestamps and tracing metadata.

Pre-recovery checkout contracts must not carry customer, line-item, pricing or address data.

The order correlation helper must prefer deterministic checkout correlation when available and must not rely on customer identity.

The shared package must provide a deterministic pending-recovery candidate identifier based on shop and checkout identity.

## Work Items

- [x] Add v2 schema-version constant(s) without redefining v1 semantics.
- [x] Add strict `checkout.created` schema and TypeScript type.
- [x] Add strict `checkout.updated` schema and TypeScript type.
- [x] Add strict v2 `order.completed` schema including `cartToken`.
- [x] Add/update discriminated-union parser(s) and type guards.
- [x] Add `checkout-updated` cross-service job contract.
- [x] Add deterministic pending-candidate job ID helper.
- [x] Add/update correlation/ordering helper(s).
- [x] Export all new contracts from `@modainteract/moda-interact-shared/shopify`.
- [x] Add contract tests covering valid and rejected payloads.
- [x] Confirm v1 contracts remain importable/parseable for transition.

## Interfaces / Contracts

Contract owner:

ARCH-001-SHARED-001

Package:

`@modainteract/moda-interact-shared`

Producers:

- `moda-interact`

Consumers:

- `moda-interact-background`

Runtime validation:

Shared Zod schemas exported by this task.

## Dependencies

None

## Enables

- ARCH-001-SHOPIFY-001
- ARCH-001-BACKGROUND-001

## Acceptance Criteria

- [x] v2 checkout-create payload contains no customer, line-item, total or address fields.
- [x] v2 checkout-update payload contains only the recovery correlation data required by ARCH-001.
- [x] v2 order payload includes both `checkoutToken` and `cartToken` as nullable correlation identifiers.
- [x] Producer and consumer can import the same runtime schemas/types from the shared package.
- [x] Candidate identity is deterministic for the same `shopId + checkoutToken`.
- [x] v1 contract semantics are not silently changed.
- [x] Shared contract tests pass.

## Validation

- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`

## Implementation Notes

Do not design checkout deletion in this task.

Use explicit v2 naming/versioning where necessary so a rolling deployment does not reinterpret an already-queued v1 payload as a different shape.

Do not add repository-local implementation behaviour to the shared package.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/src/shopify/constants.ts`
- `moda-interact-shared/src/shopify/queue-contracts.ts`
- `moda-interact-shared/src/shopify/node.ts`
- `moda-interact-shared/src/shopify/node.test.ts`
- `moda-interact-shared/src/shopify/index.ts`
- `moda-interact-shared/src/shopify/v1/checkout-observed.schema.ts`
- `moda-interact-shared/src/shopify/v1/order-completed.schema.ts`
- `moda-interact-shared/src/shopify/v1/commerce-event.schema.ts`
- `moda-interact-shared/src/shopify/v1/commerce-event.test.ts`
- `moda-interact-shared/src/shopify/v2/checkout-created.schema.ts`
- `moda-interact-shared/src/shopify/v2/checkout-updated.schema.ts`
- `moda-interact-shared/src/shopify/v2/order-completed.schema.ts`
- `moda-interact-shared/src/shopify/v2/recovery-event.schema.ts`
- `moda-interact-shared/src/shopify/v2/recovery-event.test.ts`
- `docs/decisions/shared/ARCH-001/SHARED-001-define-recovery-webhook-contracts.md`

### Work Completed

- Added explicit v2 schema version constant and v2 event type constants while preserving v1 constants and semantics.
- Added strict recovery-focused v2 payload schemas for `checkout.created`, `checkout.updated`, and `order.completed`.
- Added v2 discriminated-union event schema, runtime parser/safe parser, and event type guards.
- Added `checkout-updated` queue/job contract under shared queue constants.
- Added deterministic pending-recovery candidate identifier helper in Node-only exports.
- Added v2 ordering/correlation helpers with checkout-token preference for order correlation.
- Exported all new v2 contracts and helpers from `@modainteract/moda-interact-shared/shopify`.
- Added tests for valid/rejected v2 payloads and explicit v1 parser compatibility.
- Reorganized contract sources into explicit `v1/` and `v2/` folders while preserving the package export surface.

### Validation Results

- `npm test` (pass): 7 tests passed.
- `npm run typecheck` (pass).
- `npm run build` (pass).

### Deviations

- None.

### Assumptions

- `checkout-updated` uses the existing `checkout-events` queue with a distinct job name for cross-service routing.

### Unresolved Issues

- None.

### Architectural Concerns

- None.

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
