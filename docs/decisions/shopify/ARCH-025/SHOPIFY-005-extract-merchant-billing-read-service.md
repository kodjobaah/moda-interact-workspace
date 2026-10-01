---
id: ARCH-025-SHOPIFY-005
architecture_id: ARCH-025
title: Extract merchant billing-state read service
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-004
enables:
  - ARCH-025-SHOPIFY-006
created: 2026-10-01
updated: 2026-10-01
---

# Extract merchant billing-state read service

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract `getMerchantBillingState` into a dedicated billing-page read service while preserving provider offer verification, local cycle validation, purchase presentation and all returned fields.

## Context

`getMerchantBillingState` is approximately 269 lines and builds the merchant billing UI read model. It is distinct from recovery admission capacity: it combines local counters/usage/purchase history with optional verified Shopify commercial evidence and recovery-credit offers.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/merchant-billing-read.service.ts              # new
tests/unit/services/billing/merchant-billing-read.service.test.ts  # new
```

Consume SHOPIFY-001 billing-period helpers (including `isSafeNonNegativeInteger`) and SHOPIFY-002 catalogue reads; do not duplicate them.

## Out of Scope

- Recovery capacity admission.
- purchase command mutation.
- subscription sync or activation.
- provider protocol changes.
- route/UI changes.
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
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and all 127 tests must pass.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — preserve method contract

`BillingService.getMerchantBillingState(...)` retains its existing arguments and complete return shape and delegates to the extracted service.

### R2 — preserve commercial verification

When `verifiedCommercialState` is supplied, continue reusing it rather than performing another provider read. When absent, preserve current provider lookup behaviour and failure handling.

### R3 — preserve exact-cycle eligibility

Reuse SHOPIFY-001 `hasDurableBillingPeriod`, `hasMatchingBillingCycle`, `deriveBillingPeriodPhase` and repository-internal `isSafeNonNegativeInteger`. Recovery-credit purchase eligibility and paid-period/counter integrity validation must continue requiring the same exact OPEN local/provider cycle, ACTIVE phase and safe-integer arithmetic. Do not recreate a second integer guard in this service.

### R4 — preserve read composition

Keep current usage totals, lifetime/purchased/included counters, refund holds, purchase history, offer diagnostics, verification state, labels, period phase and unavailable reason semantics.

### R5 — catalogue reuse

Use SHOPIFY-002 `readMerchantPricingPlan` rather than adding another MerchantPricingPlan reader.

### R6 — preserve current provider verification I/O

Do not route this method through SHOPIFY-003 `SubscriptionReadService` merely because it can read Shopify commercial state. The current method either consumes the supplied `verifiedCommercialState` or performs its own single `provider.getActiveSubscription(...)` call and does **not** perform the extra BillingPlan mapping reads owned by SHOPIFY-003. Preserve that I/O shape exactly.

## Work Items

- [ ] Create `MerchantBillingReadService` with provider, Prisma and narrow collaborator dependencies.
- [ ] Move merchant billing-state composition and leave façade delegate, importing SHOPIFY-001 cycle/integer helpers and SHOPIFY-002 catalogue reads directly.
- [ ] Add focused tests for Free/Paid presentation, exact-cycle phase, provider snapshot reuse, provider failure, offer diagnostics/purchase eligibility and unresolved purchases.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Repository-internal service. Existing method return shape remains the route-facing contract. Existing provider and merchant-pricing contracts are reused.

## Dependencies

- `ARCH-025-SHOPIFY-004`

## Enables

- `ARCH-025-SHOPIFY-006`

## Acceptance Criteria

- [ ] Merchant billing-page read model has one owner outside the façade.
- [ ] Verified commercial state prevents duplicate provider reads exactly as before; absent state performs the same single provider read without extra SHOPIFY-003 mapping queries.
- [ ] Recovery-credit offer eligibility uses unchanged cycle/phase rules.
- [ ] No returned field or error/fallback meaning changes.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/merchant-billing-read.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-billing-read.service.ts tests/unit/services/billing/merchant-billing-read.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Keep this a read service. Do not absorb the purchase command simply because both concern recovery-credit packs.


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
