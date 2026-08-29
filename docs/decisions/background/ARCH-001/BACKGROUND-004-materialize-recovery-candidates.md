---
id: ARCH-001-BACKGROUND-004
architecture_id: ARCH-001
title: Materialize matured recovery candidates
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 40
executor: codex
claimed_at: 2026-08-28T21:07:12Z
attempt: 1
depends_on: ["ARCH-001-BACKGROUND-002", "ARCH-001-BACKGROUND-003"]
enables: ["ARCH-001-BACKGROUND-005"]
created: 2026-08-28
updated: 2026-08-28
---

# Materialize Matured Recovery Candidates

## Architecture

Architecture ID:

ARCH-001

Architecture document:

docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md

Coordinator:

moda_architect

## Objective

When a delayed pending candidate matures, retrieve the current checkout from Shopify and create the durable `CheckoutRecovery` only if it is still recoverable.

## Context

This task is the transition from transient Redis/BullMQ state into durable Moda recovery state. It replaces the current behaviour where the delayed webhook payload itself is used to populate `CheckoutRecovery`.

## Scope

- Consume the internal matured-candidate job.
- Call the Shopify lookup owned by ARCH-001-BACKGROUND-003.
- If checkout is not found/no longer recoverable, discard and clean up candidate state.
- If recoverable, create/upsert `CheckoutRecovery` using current Shopify data.
- Resolve/create the customer from the current Shopify result.
- Populate current line items, totals, currency and recovery URL.
- Preserve unique `shopId + checkoutToken` idempotency.
- Continue the existing recovery conversation/message workflow after durable recovery creation.
- Ensure legacy v1 delayed checkout jobs entering this path ignore embedded basket/customer data.
- Add tests for idempotency and recoverability decisions.

## Out of Scope

- Pending candidate scheduling.
- Order cancellation/completion.
- Checkout-update refresh.
- New repeat-abandonment policy.
- Checkout deletion.
- Database schema changes unless separately approved.

## Requirements

Webhook payload basket data must not populate `CheckoutRecovery`.

The Shopify lookup result is the source used to populate recovery state.

If Shopify reports the checkout completed/not recoverable, no recovery record or recovery message is created.

Duplicate candidate execution must not send duplicate recovery messages.

Existing terminal `CheckoutRecovery` records must not be reopened.

Any database/schema limitation discovered must be returned to `moda_architect`.

## Work Items

- [x] Add matured-candidate handler.
- [x] Call current Shopify checkout lookup.
- [x] Discard not-found/non-recoverable candidates.
- [x] Map current Shopify result into existing recovery fields.
- [x] Adapt customer resolution to use Shopify lookup data rather than old webhook event type.
- [x] Create/upsert recovery idempotently.
- [x] Continue existing recovery messaging only for eligible DETECTED recovery.
- [x] Ensure duplicate execution cannot duplicate message/recovery.
- [x] Add unit/integration tests.

## Interfaces / Contracts

Consumes:

- internal pending candidate from ARCH-001-BACKGROUND-002;
- Shopify lookup from ARCH-001-BACKGROUND-003.

Writes:

- existing PostgreSQL `CheckoutRecovery`;
- existing `Customer`/phone state as required by current recovery workflow.

## Dependencies

- ARCH-001-BACKGROUND-002
- ARCH-001-BACKGROUND-003

## Enables

- ARCH-001-BACKGROUND-005

## Acceptance Criteria

- [x] A candidate does not create recovery data from its stored webhook payload.
- [x] Current Shopify data populates the recovery.
- [x] Completed/non-recoverable checkout creates no recovery/message.
- [x] Same candidate executed twice produces at most one recovery and one recovery-send workflow.
- [x] Existing terminal recovery is not reopened.
- [x] Current recovery message flow remains functional for a newly materialized recovery.

## Validation

- [x] `npm test`
- [x] `npm run test:integration`
- [x] `npm run build`
- [x] `npm run prisma:validate`

## Implementation Notes

Do not redesign message copy or downstream CommerceAgent behaviour.

Keep the transition from 'candidate' to 'recovery' explicit in code so the order-race task can protect it.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/workers/pending-recovery-candidate.worker.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-004-materialize-recovery-candidates.md`

### Work Completed

Implemented the transition from transient pending candidate state into durable
`CheckoutRecovery` for ARCH-001-BACKGROUND-004.

- Added `CheckoutRecoveryService.materializeMaturedCandidate(candidate)`:
  - resolves the shop domain from the candidate's `shopId`;
  - calls the bounded Shopify lookup owned by ARCH-001-BACKGROUND-003;
  - treats `provider-error` as retryable (throws for BullMQ retry, never as a
    not-recoverable decision);
  - discards (no recovery, no message) on `not-found`, `ambiguous`,
    `bounded-limit-exceeded`, and checkout already completed
    (`checkout.completedAt != null`);
  - guards idempotency: an existing recovery is never re-materialized
    (`no-op-existing`) and an existing terminal recovery is never reopened
    (`discarded-terminal`);
  - for a found, recoverable checkout, maps only the current Shopify result
    (plus candidate correlation identifiers shopId/checkoutToken/cartToken)
    into the existing `RecoveryCheckoutSeed` shape and delegates to the existing
    `handleCheckoutCreated` recovery-message workflow (upsert + customer
    resolution + WhatsApp send).
- Wired the matured-candidate worker (`pending-recovery-candidate.worker.ts`) so
  `EVALUATE_PENDING_RECOVERY_JOB` invokes materialization, then cleans up the
  O(1) candidate lookup indexes in a `finally` block regardless of outcome.
- Webhook payload basket/customer data is not used to populate recovery state;
  the candidate carries only correlation identifiers, so the seed is built from
  the Shopify lookup result.
- No database schema changes, no new cross-service contract, no change to
  recovery message copy or downstream CommerceAgent behaviour.

### Validation Results

- `npm test`: `1 failed | 30 passed | 2 skipped`. The sole failure is the
  pre-existing unrelated `tests/unit/services/recovery-routing.service.test.ts`
  (`prisma.customerPhone.findMany` called on undefined mock); not caused by this
  task.
- `npm run test:integration`: `1 passed | 2 skipped`.
- `npm run build` (prisma:generate + tsc): pass.
- `npm run prisma:validate`: pass (schema valid).
- Targeted materialization tests:
  `tests/unit/services/matured-candidate.materialization.test.ts` 10/10 pass.

### Deviations

None.

### Assumptions

- The candidate's `checkoutToken`/`cartToken`/`shopId` are the correlation
  identity; `checkoutCreatedAt`/`abandonedCheckoutUrl` support the bounded lookup.
- Any non-`found` lookup outcome (not-found, ambiguous, bound-exceeded) is
  treated as a safe discard (no recovery, no message) rather than a retryable
  error, matching the task requirement that a non-recoverable/discarded checkout
  creates no recovery.

### Unresolved Issues

- Repository-wide `npm test` remains red solely due to the pre-existing unrelated
  failure in `tests/unit/services/recovery-routing.service.test.ts`.

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
