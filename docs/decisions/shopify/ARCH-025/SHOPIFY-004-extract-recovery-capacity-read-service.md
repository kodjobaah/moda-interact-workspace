---
id: ARCH-025-SHOPIFY-004
architecture_id: ARCH-025
title: Extract merchant recovery-capacity read service
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-003
enables:
  - ARCH-025-SHOPIFY-005
created: 2026-10-01
updated: 2026-10-01
---

# Extract merchant recovery-capacity read service

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract `getMerchantRecoveryCapacityState` into a dedicated local recovery-capacity read service while preserving the exact capacity-source precedence and admission semantics.

## Context

`getMerchantRecoveryCapacityState` is approximately 200 lines and is an independently meaningful read model. It combines local Subscription/BillingPeriod state, lifetime/purchased/promotional counters and current plan top-up configuration. It should not share ownership with the separate merchant billing-page read model.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/merchant-recovery-capacity-read.service.ts              # new
tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts  # new
```

Consume `BillingPlanResolutionService` from SHOPIFY-002 rather than duplicating top-up configuration reads.

## Out of Scope

- Merchant billing-page offer/provider verification.
- recovery admission mutation/reservation.
- recovery-credit purchase initiation.
- changing promotion or entitlement models.
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
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — exact precedence

Preserve current capacity selection order:

```text
PROMOTIONAL
  -> PAID_INCLUDED
  -> PURCHASED
  -> FREE_LIFETIME
  -> EXHAUSTED
```

### R2 — exact blocking states

Preserve `CONTRACT_REQUIRED`, `CONTRACT_FROZEN`, `CONFIGURATION_UNAVAILABLE`, `AVAILABLE` and `EXHAUSTED` decisions and the current `canStartRecovery` semantics.

### R3 — exact arithmetic/validation

Preserve all current non-negative arithmetic, promotion targeting/window rules, refund-hold subtraction and strict paid BillingPeriod/counter integrity checks.

### R4 — catalogue reuse

Use the SHOPIFY-002 collaborator for `readRecoveryCreditTopUpConfiguration`; do not recreate MerchantPricingPlan queries in this service.

### R5 — read only

No new writes or provider calls are permitted.

## Work Items

- [ ] Create `MerchantRecoveryCapacityReadService` with Prisma + narrow billing-plan-resolution dependency.
- [ ] Move exact capacity read logic and leave façade delegate.
- [ ] Add focused tests covering all capacity sources, precedence, promotional validity, refund holds, FROZEN/NO_CONTRACT and invalid paid-period state.
- [ ] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Consumes `MerchantRecoveryCapacityState` from existing `billing.types.ts` and the internal top-up configuration read from SHOPIFY-002. No public contract changes.

## Dependencies

- `ARCH-025-SHOPIFY-003`

## Enables

- `ARCH-025-SHOPIFY-005`

## Acceptance Criteria

- [ ] Capacity read responsibility is removed from the façade implementation.
- [ ] Capacity precedence and all current availability states are unchanged.
- [ ] No database write or Shopify provider call is introduced.
- [ ] Top-up configuration has one catalogue owner.
- [ ] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [ ] `npm test -- tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-recovery-capacity-read.service.ts tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not combine this with `MerchantBillingReadService`; recovery admission/capacity is a distinct business read model with different failure semantics.


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
