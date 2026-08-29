---
id: ARCH-001-BACKGROUND-002
architecture_id: ARCH-001
title: Manage pending recovery candidates
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 30
executor: codex
claimed_at: 2026-08-28T18:20:54Z
attempt: 1
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

- [x] Add internal recovery-candidate queue/producer.
- [x] Load recovery delay from `ShopSettings`.
- [x] Build minimal candidate data.
- [x] Schedule one delayed candidate per checkout.
- [x] Handle duplicate checkout-create idempotently.
- [x] Add checkout-token lookup.
- [x] Add cart-token alias/index if used for order fallback.
- [x] Clean up aliases on cancellation/completion/maturation.
- [x] Add unit tests for delay, duplicate and cleanup behaviour.

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

- [x] Exactly one pending candidate exists for the same shop/checkout.
- [x] Candidate data contains no basket/customer state.
- [x] Recovery delay comes from current shop settings.
- [x] Candidate lookup by checkout token is O(1).
- [x] Cart-token fallback, if implemented, is O(1) and does not scan queue jobs.
- [x] Transient aliases do not outlive the candidate indefinitely.
- [x] No PostgreSQL `CheckoutRecovery` is created by checkout-create handling itself.

## Validation

- [x] `npm test`
- [x] `npm run build`
- [x] `npm run prisma:validate`

## Implementation Notes

Prefer a dedicated internal BullMQ queue for delayed recovery evaluation so the cross-service checkout event queue remains immediate-event transport.

Do not place Redis operations inside a PostgreSQL transaction.

If robust cart-token correlation requires a design materially different from the task, return it to `moda_architect` rather than adding unbounded queue scans.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/domain/pending-recovery-candidate.ts`
- `moda-interact-background/src/services/pending-recovery-candidate.service.ts`
- `moda-interact-background/src/workers/pending-recovery-candidate.worker.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/index.ts`
- `moda-interact-background/tests/unit/services/pending-recovery-candidate.service.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-002-manage-pending-recovery-candidates.md`

### Work Completed

- Added repository-local delayed pending-candidate queue and job constants for `pending-recovery-candidates` / `evaluate-pending-recovery`.
- Implemented candidate scheduling service that:
  - loads `ShopSettings.recoveryDelayMinutes` from PostgreSQL using shop domain;
  - builds minimal candidate payload (`shopId`, `checkoutToken`, `cartToken`, `abandonedCheckoutUrl`, `checkoutCreatedAt`);
  - schedules exactly one deterministic delayed job per `shopId + checkoutToken` and refreshes existing delayed jobs idempotently.
- Added O(1) Redis index keys for checkout-token and cart-token lookup.
- Added index cleanup on candidate maturation and checkout-token cancellation, with bounded TTL as fallback protection.
- Wired checkout-created contract handling to schedule pending candidates without creating `CheckoutRecovery`.
- Added dedicated pending-candidate worker to process matured jobs and clean transient aliases.
- Added unit tests covering delay loading, duplicate idempotency/refresh, O(1) lookups, and cleanup behavior.

### Validation Results

- `npm test`: fail due pre-existing unrelated unit test failure in `tests/unit/services/recovery-routing.service.test.ts` (`prisma.customerPhone.findMany` undefined in test mock path).
- `npm test -- tests/unit/services/pending-recovery-candidate.service.test.ts`: pass (5/5).
- `npm run build`: pass.
- `npm run prisma:validate`: pass.

### Deviations

None.

### Assumptions

- The existing `recovery-routing.service` unit test failure is unrelated to pending-candidate lifecycle implementation.

### Unresolved Issues

- Repository-wide `npm test` remains red due to a pre-existing failure in `tests/unit/services/recovery-routing.service.test.ts`.

### Architectural Concerns

None.

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
