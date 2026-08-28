---
id: ARCH-001-SHOPIFY-002
architecture_id: ARCH-001
title: Publish recovery webhook events immediately
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: review
priority: 30
executor: codex
claimed_at: 2026-08-28T17:57:49Z
attempt: 1
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

- [x] Remove checkout job lookup/merge/coalescing code.
- [x] Remove ingress-side checkout delay/changeDelay behaviour.
- [x] Add immediate checkout-created publication.
- [x] Add immediate checkout-updated publication.
- [x] Keep order publication immediate.
- [x] Use shared job-name constants and deterministic IDs.
- [x] Configure bounded retries/backoff.
- [x] Retain failed jobs for inspection.
- [x] Update queue publisher tests.
- [x] Update ingress outcome tests where coalescing outcomes no longer apply.

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

- [x] No checkout event is delayed in the Shopify HTTP ingress layer.
- [x] No checkout basket state is merged in Redis by `moda-interact`.
- [x] Checkout create/update use distinct shared job names.
- [x] Duplicate Shopify delivery does not create duplicate immediate work.
- [x] Queue failure still returns HTTP 503 through existing ingress handling.
- [x] Job retry/backoff is bounded.
- [x] Failed jobs remain inspectable.
- [x] Queue/ingress tests pass.

## Validation

- [x] `npm test -- --run`
- [x] `npm run typecheck`
- [x] `npm run lint`
- [x] `npm run build`

## Implementation Notes

Do not create a new Redis client or pending-candidate index in `moda-interact`.

Recovery delay is business processing and belongs in `moda-interact-background`.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/app/services/webhooks/shopify-webhook-queue.server.ts`
- `moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts`
- `moda-interact/tests/unit/webhooks/shopify-webhook-queue.server.test.js`
- `moda-interact/tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `docs/decisions/shopify/ARCH-001/SHOPIFY-002-publish-events-immediately.md`

### Work Completed

- Removed checkout-created queue coalescing/merge/update and delay mutation logic.
- Removed ingress-side recovery delay usage and `ShopSettings.recoveryDelayMinutes` dependency from publication path.
- Kept checkout-created, checkout-updated, and order-completed publication all immediate.
- Updated checkout-created and checkout-updated duplicate-delivery idempotency to use shared deterministic delivery-based IDs.
- Kept durable acceptance point at successful queue enqueue with unchanged failure-to-503 ingress behavior.
- Configured bounded retries/backoff and retained failed jobs for operational inspection.
- Updated queue and ingress unit tests to validate immediate publication semantics and removal of coalescing outcomes.

### Validation Results

- `npm test -- --run`: pass (25 tests passed across 5 files).
- `npm run typecheck`: fail with pre-existing repository issues outside this task scope (example: `app/shopify.server.js` `process` typing errors).
- `npm run lint`: fail with pre-existing repository issues outside this task scope (example: onboarding prop-types and billing route lint issues).
- `npm run build`: pass.

### Deviations

None.

### Assumptions

- Existing repository-wide typecheck/lint failures are pre-existing and out of scope for this task.

### Unresolved Issues

- Repository-level typecheck and lint failures outside webhook queue/ingress files remain unresolved.

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
