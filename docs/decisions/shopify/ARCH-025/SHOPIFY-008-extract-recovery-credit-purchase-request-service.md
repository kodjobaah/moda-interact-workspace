---
id: ARCH-025-SHOPIFY-008
architecture_id: ARCH-025
title: Extract recovery-credit purchase request workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-007
enables:
  - ARCH-025-SHOPIFY-009
created: 2026-10-01
updated: 2026-10-01
---

# Extract recovery-credit purchase request workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract `requestRecoveryCreditPack` and its provider-evidence/idempotency helpers into a dedicated purchase-request service without moving it into the already-large purchase-management/refund service.

## Context

Purchase initiation is a command workflow with provider-before/provider-after verification, Serializable transaction semantics and single-flight/idempotency rules. `recovery-credit-purchase-management.service.ts` already owns history/refunds and is approximately 867 lines; absorbing initiation there would recreate the maintainability problem.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/recovery-credit-purchase-request.service.ts              # new
tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts  # new
```

Existing `recovery-credit-purchase-management.service.ts` is read-only/out-of-scope for this task.

## Out of Scope

- refund/history management.
- purchase activation/reconciliation owned elsewhere.
- changing Shopify usage event format or idempotency key.
- billing-page read logic.
- edits to frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and all 127 tests must pass.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact command

Move implementation ownership of `requestRecoveryCreditPack(shopId, intent, purchaseId, eventHandle)` and directly associated helpers:

```text
purchase ID validation
provider-before evidence validation
executable provider subscription selection
provider evidence equality
unresolved purchase message
same-id unique-race handling
```

### R2 — preserve provider/transaction boundary

Shopify/provider verification that currently occurs before the Prisma write transaction MUST remain before it. No provider/network call may move into the transaction.

### R3 — preserve transaction and locking

Keep Serializable isolation, Subscription locking order, single-flight lookup, current BillingPeriod/cycle validation and exact durable revalidation after provider verification.

### R4 — preserve provider evidence fencing

The provider snapshot used for admission must still be revalidated against live/durable state as today. A changed lifecycle/configuration/cycle/meter must fail closed without creating a usage event.

### R5 — reuse catalogue owner

Use SHOPIFY-002 merchant-pricing/catalogue reads; do not recreate them.

### R6 — preserve idempotency

Keep client purchase ID validation, existing-purchase replay, unresolved offer/provider-context blocking, deterministic Shopify usage idempotency key and P2002 same-ID recovery semantics.

## Work Items

- [ ] Create `RecoveryCreditPurchaseRequestService` with provider, Prisma and catalogue collaborator dependencies.
- [ ] Move request command/helpers and leave façade delegate.
- [ ] Do not edit purchase-management/refund service.
- [ ] Add focused tests for provider-before ordering, Serializable/lock order, exact cycle, duplicate replay, unresolved blocking, changed provider/config evidence, invalid IDs and unique-race recovery.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Consumes existing `BillingProvider`, Shared `createShopifyUsageIdempotencyKey`/provider-context identity and existing Prisma purchase/usage-event models. No new queue/provider contract.

## Dependencies

- `ARCH-025-SHOPIFY-007`

## Enables

- `ARCH-025-SHOPIFY-009`

## Acceptance Criteria

- [ ] Purchase initiation is owned by a dedicated request service.
- [ ] Existing purchase-management/refund service is not enlarged by this refactor.
- [ ] Provider-before/provider-after evidence and transaction ordering are unchanged.
- [ ] Idempotency/single-flight behaviour is unchanged.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/recovery-credit-purchase-request.service.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

Do not generalise this into a command bus. Keep current error messages because billing routes/tests may display/assert them.

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
