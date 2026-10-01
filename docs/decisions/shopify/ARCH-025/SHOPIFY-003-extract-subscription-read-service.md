---
id: ARCH-025-SHOPIFY-003
architecture_id: ARCH-025
title: Extract Subscription and Shopify commercial read service
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-002
enables:
  - ARCH-025-SHOPIFY-004
created: 2026-10-01
updated: 2026-10-01
---

# Extract Subscription and Shopify commercial read service

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the read-only local Subscription projection and Shopify commercial/lifecycle mapping methods into one service while retaining identical `BillingService` methods as façade delegates.

## Context

The current façade mixes local subscription reads and provider commercial/lifecycle state mapping with mutation workflows. These four public reads plus `mapMerchantShopifySubscription` form a coherent read owner and can be extracted without touching mutation semantics.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-read.service.ts              # new
tests/unit/services/billing/subscription-read.service.test.ts  # new
```

Existing routes remain unchanged.

## Out of Scope

- Merchant recovery-capacity arithmetic.
- merchant billing-page state.
- hosted callback mutations.
- activation or synchronization.
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

### R1 — move exact public read implementations behind façade

The extracted service owns the logic currently backing:

```text
getSubscription(shopId)
getSubscriptionProjection(shopId)
getMerchantShopifySubscriptionState(shopId)
getMerchantShopifyLifecycleState(shopId)
mapMerchantShopifySubscription(providerSubscription)
```

`BillingService` keeps all four public methods with the same signatures/return shapes and delegates.

### R2 — preserve provider read behaviour

Keep the current Shopify provider methods, call counts, lifecycle precedence, plan mapping and Partner failure propagation. Do not add fallback to local Subscription state when the current code fails/returns unresolved provider state.

### R3 — preserve local eligibility semantics

`getSubscription` must continue returning only ACTIVE/TRIALING local subscriptions and `getSubscriptionProjection` must keep its current include graph.

### R4 — no mutation

The extracted read service must not introduce durable writes.

## Work Items

- [ ] Create `SubscriptionReadService` with injected provider + Prisma dependencies.
- [ ] Move local/provider read logic and mapper.
- [ ] Keep BillingService method signatures as delegating compatibility methods.
- [ ] Add focused tests for active/no-contract local reads, current/pending Shopify mapping, lifecycle precedence and provider failure.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

The service consumes existing repository-local `BillingProvider`, `MerchantShopifySubscriptionState` and `MerchantShopifyLifecycleState` contracts from `billing.types.ts`.

No cross-repository contract is introduced.

## Dependencies

- `ARCH-025-SHOPIFY-002`

## Enables

- `ARCH-025-SHOPIFY-004`

## Acceptance Criteria

- [ ] Read-only subscription/provider responsibilities have one owner.
- [ ] BillingService callers require no changes.
- [ ] Provider invocation count and lifecycle precedence match the pre-refactor implementation.
- [ ] Extracted service performs no writes.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/subscription-read.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-read.service.ts tests/unit/services/billing/subscription-read.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

Keep the mapper close to the read service; do not create a generic Shopify billing mapper package. The façade may delegate directly to one collaborator created in its constructor.

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
