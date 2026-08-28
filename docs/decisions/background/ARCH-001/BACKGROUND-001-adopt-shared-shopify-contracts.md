---
id: ARCH-001-BACKGROUND-001
architecture_id: ARCH-001
title: Adopt canonical Shopify webhook contracts
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add shared-package dependency.
- [ ] Import shared queue/event schemas and types.
- [ ] Parse worker job data at the runtime boundary.
- [ ] Route checkout-created and checkout-updated separately.
- [ ] Route order-completed using the shared contract.
- [ ] Remove old local `CheckoutCreatedEvent` contract usage.
- [ ] Remove old local `OrderCompletedEvent` contract usage.
- [ ] Add transitional v1 handling for queued jobs.
- [ ] Add unit tests for valid v2, invalid data and legacy v1 transition.

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

- [ ] Background no longer maintains a separate structural copy of the v2 checkout/order contract.
- [ ] Every cross-service job is runtime validated.
- [ ] Checkout create and checkout update reach distinct handlers.
- [ ] Invalid payloads fail with clear diagnostics.
- [ ] Transitional v1 checkout jobs do not use embedded basket data to populate recovery.
- [ ] Background build/typecheck succeeds with the shared dependency.

## Validation

- [ ] `npm test`
- [ ] `npm run build`
- [ ] `npm run prisma:validate`

## Implementation Notes

This task establishes the boundary only. Keep business handlers thin/stubbed where later ARCH-001 tasks own behaviour.

If package/dependency versioning prevents safe rolling deployment, report it as an architectural concern.

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
