---
id: ARCH-001-SHARED-001
architecture_id: ARCH-001
title: Define recovery-focused Shopify webhook contracts
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add v2 schema-version constant(s) without redefining v1 semantics.
- [ ] Add strict `checkout.created` schema and TypeScript type.
- [ ] Add strict `checkout.updated` schema and TypeScript type.
- [ ] Add strict v2 `order.completed` schema including `cartToken`.
- [ ] Add/update discriminated-union parser(s) and type guards.
- [ ] Add `checkout-updated` cross-service job contract.
- [ ] Add deterministic pending-candidate job ID helper.
- [ ] Add/update correlation/ordering helper(s).
- [ ] Export all new contracts from `@modainteract/moda-interact-shared/shopify`.
- [ ] Add contract tests covering valid and rejected payloads.
- [ ] Confirm v1 contracts remain importable/parseable for transition.

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

- [ ] v2 checkout-create payload contains no customer, line-item, total or address fields.
- [ ] v2 checkout-update payload contains only the recovery correlation data required by ARCH-001.
- [ ] v2 order payload includes both `checkoutToken` and `cartToken` as nullable correlation identifiers.
- [ ] Producer and consumer can import the same runtime schemas/types from the shared package.
- [ ] Candidate identity is deterministic for the same `shopId + checkoutToken`.
- [ ] v1 contract semantics are not silently changed.
- [ ] Shared contract tests pass.

## Validation

- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`

## Implementation Notes

Do not design checkout deletion in this task.

Use explicit v2 naming/versioning where necessary so a rolling deployment does not reinterpret an already-queued v1 payload as a different shape.

Do not add repository-local implementation behaviour to the shared package.

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
