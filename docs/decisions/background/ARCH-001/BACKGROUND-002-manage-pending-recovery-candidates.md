---
id: ARCH-001-BACKGROUND-002
architecture_id: ARCH-001
title: Manage pending recovery candidates
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-001-BACKGROUND-001"]
enables: ["ARCH-001-BACKGROUND-004"]
created: 2026-08-28
updated: 2026-08-28
---

# Manage Pending Recovery Candidates

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

Create and manage the delayed Redis/BullMQ `PendingRecoveryCandidate` lifecycle inside `moda-interact-background` when a checkout-create event is received.

## Context

ARCH-001 defines pending recovery as transient business state, not an ingress concern. The background service already owns asynchronous recovery workflows and can load the merchant recovery delay from PostgreSQL before scheduling the candidate.

## Scope

- On checkout-created, load the shop recovery delay.
- Create one delayed internal recovery-candidate job per `shopId + checkoutToken`.
- Candidate data must contain only:
  - shopId;
  - checkoutToken;
  - cartToken;
  - abandonedCheckoutUrl;
  - checkoutCreatedAt.
- Do not carry customer/basket/pricing data into the candidate.
- Maintain O(1) lookup needed to find a candidate by checkout token.
- If cart-token cancellation is supported, maintain an O(1) transient cart-token alias/index; do not scan BullMQ queues.
- Clean up transient correlation aliases when a candidate is removed or matures.
- Define internal queue/job constants locally because this queue does not cross a repository boundary.
- Add candidate lifecycle tests.

## Out of Scope

- Shopify GraphQL lookup.
- CheckoutRecovery creation.
- Sending WhatsApp.
- Order completion of an existing recovery.
- Checkout update refresh.
- Database schema changes.

## Requirements

`ShopSettings.recoveryDelayMinutes` is loaded in background processing, not passed from Shopify ingress.

Candidate identity must be deterministic and idempotent.

Candidate creation must not create multiple delayed recovery evaluations for the same `shopId + checkoutToken`.

The internal candidate representation must not contain customer, line-item, total, currency or address state.

Any secondary cart-token correlation must use an indexed Redis key/structure with bounded lifetime; queue scanning is prohibited.

## Work Items

- [ ] Add internal recovery-candidate queue/producer.
- [ ] Load recovery delay from `ShopSettings`.
- [ ] Build minimal candidate data.
- [ ] Schedule one delayed candidate per checkout.
- [ ] Handle duplicate checkout-create idempotently.
- [ ] Add checkout-token lookup.
- [ ] Add cart-token alias/index if used for order fallback.
- [ ] Clean up aliases on cancellation/completion/maturation.
- [ ] Add unit tests for delay, duplicate and cleanup behaviour.

## Interfaces / Contracts

Consumes:

- v2 checkout-created event from ARCH-001-SHARED-001.

Produces:

- repository-local delayed `PendingRecoveryCandidate` job.

Durable business state:

None.

## Dependencies

- ARCH-001-BACKGROUND-001

## Enables

- ARCH-001-BACKGROUND-004

## Acceptance Criteria

- [ ] Exactly one pending candidate exists for the same shop/checkout.
- [ ] Candidate data contains no basket/customer state.
- [ ] Recovery delay comes from current shop settings.
- [ ] Candidate lookup by checkout token is O(1).
- [ ] Cart-token fallback, if implemented, is O(1) and does not scan queue jobs.
- [ ] Transient aliases do not outlive the candidate indefinitely.
- [ ] No PostgreSQL `CheckoutRecovery` is created by checkout-create handling itself.

## Validation

- [ ] `npm test`
- [ ] `npm run build`
- [ ] `npm run prisma:validate`

## Implementation Notes

Prefer a dedicated internal BullMQ queue for delayed recovery evaluation so the cross-service checkout event queue remains immediate-event transport.

Do not place Redis operations inside a PostgreSQL transaction.

If robust cart-token correlation requires a design materially different from the task, return it to `moda_architect` rather than adding unbounded queue scans.

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
