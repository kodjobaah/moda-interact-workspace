---
id: ARCH-001-SHOPIFY-002
architecture_id: ARCH-001
title: Publish recovery webhook events immediately
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-001-SHOPIFY-001"]
enables: []
created: 2026-08-28
updated: 2026-08-28
---

# Publish Recovery Webhook Events Immediately

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Replace ingress-side checkout coalescing/delay with immediate durable BullMQ publication of the canonical checkout-create, checkout-update and order events.

## Context

The current publisher uses the checkout queue itself as mutable delayed checkout state. ARCH-001 moves pending-recovery candidate creation and delay handling into `moda-interact-background`, leaving `moda-interact` as a thin authenticated event producer.

## Scope

- Publish checkout-create events immediately.
- Publish checkout-update events immediately using their own job name.
- Publish order-completed events immediately.
- Use shared deterministic/delivery identifiers appropriate to each event.
- Remove checkout payload merge/update logic and `changeDelay()` behaviour from ingress.
- Remove recovery-delay calculation from queue publication.
- Keep queue publication as the durable acceptance point.
- Add bounded retry/backoff job options and retain failed jobs for operational inspection.
- Preserve duplicate-delivery idempotency.
- Update queue and ingress tests.

## Out of Scope

- Creating the delayed pending-recovery candidate.
- Reading `ShopSettings.recoveryDelayMinutes`.
- Cancelling a candidate on order.
- Recovery GraphQL queries.
- Recovery/database updates.

## Requirements

No state-dependent recovery decision may occur before Shopify acknowledgement.

A successful enqueue remains the durable acceptance point.

A queue publication failure must continue to produce a retryable Shopify HTTP response.

Checkout-update publication must not locate, merge or mutate a delayed checkout-create job.

Failed jobs must not be immediately deleted after their final failed attempt.

Retry policy must be bounded and documented in the Completion Report.

## Work Items

- [ ] Remove checkout job lookup/merge/coalescing code.
- [ ] Remove ingress-side checkout delay/changeDelay behaviour.
- [ ] Add immediate checkout-created publication.
- [ ] Add immediate checkout-updated publication.
- [ ] Keep order publication immediate.
- [ ] Use shared job-name constants and deterministic IDs.
- [ ] Configure bounded retries/backoff.
- [ ] Retain failed jobs for inspection.
- [ ] Update queue publisher tests.
- [ ] Update ingress outcome tests where coalescing outcomes no longer apply.

## Interfaces / Contracts

Consumes:

ARCH-001-SHARED-001

Produces to:

- shared checkout-events queue;
- shared order-events queue.

The delayed internal recovery-candidate queue is not owned by this repository.

## Dependencies

- ARCH-001-SHOPIFY-001

## Enables

None

## Acceptance Criteria

- [ ] No checkout event is delayed in the Shopify HTTP ingress layer.
- [ ] No checkout basket state is merged in Redis by `moda-interact`.
- [ ] Checkout create/update use distinct shared job names.
- [ ] Duplicate Shopify delivery does not create duplicate immediate work.
- [ ] Queue failure still returns HTTP 503 through existing ingress handling.
- [ ] Job retry/backoff is bounded.
- [ ] Failed jobs remain inspectable.
- [ ] Queue/ingress tests pass.

## Validation

- [ ] `npm test -- --run`
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`

## Implementation Notes

Do not create a new Redis client or pending-candidate index in `moda-interact`.

Recovery delay is business processing and belongs in `moda-interact-background`.

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
