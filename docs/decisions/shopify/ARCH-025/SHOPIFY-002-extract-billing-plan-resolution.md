---
id: ARCH-025-SHOPIFY-002
architecture_id: ARCH-025
title: Extract operational BillingPlan resolution and catalogue reads
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-001
enables:
  - ARCH-025-SHOPIFY-003
created: 2026-10-01
updated: 2026-10-01
---

# Extract operational BillingPlan resolution and catalogue reads

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the operational BillingPlan materialisation/resolution and MerchantPricingPlan billing-catalogue reads into one bounded service consumed by the compatibility façade and later billing workflows.

## Context

`BillingService` currently owns `resolveOrMaterializeBillingPlan`, `readRecoveryCreditTopUpConfiguration` and `readMerchantPricingPlan`. These all interpret the platform-managed `MerchantPricingPlan` catalogue for Shopify billing. They are shared dependencies of activation, merchant reads, purchase initiation and synchronization and should have one owner before those workflows are extracted.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/billing-plan-resolution.service.ts              # new
tests/unit/services/billing/billing-plan-resolution.service.test.ts  # new
```

No route or merchant-pricing module changes are authorised.

## Out of Scope

- Changing MerchantPricingPlan/BillingPlan schema or validation rules.
- Changing Merchant Knowledge configuration semantics.
- Changing recovery-credit offer resolution.
- Extracting activation/read/purchase/sync workflows themselves.
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

### R1 — one operational plan owner

Create `BillingPlanResolutionService` (name may be exact) receiving the existing Prisma dependency and owning the logic equivalent to:

```text
resolveOrMaterializeBillingPlan(planHandle)
readRecoveryCreditTopUpConfiguration(planHandle)
readMerchantPricingPlan(planHandle)
```

`BillingService` constructs/reuses this collaborator from its existing `database` dependency.

### R2 — preserve materialisation transaction

`resolveOrMaterializeBillingPlan` must preserve the current transaction boundary, unique-handle race recovery and `materializedAt` update semantics.

Preserve result kinds exactly:

```text
READY
UNKNOWN_CATALOGUE_PLAN
INACTIVE_OPERATIONAL_PLAN
INVALID_CATALOGUE_PLAN
```

and the current invalid-reason strings.

### R3 — preserve catalogue validation

Keep current checkout-recovery feature, plan kind, usage-meter, included-credit and Merchant Knowledge configuration/compatibility validation unchanged. Do not duplicate that validation into later services.

### R4 — preserve provider-facing catalogue fallback

`readMerchantPricingPlan` must retain the current database-first behaviour and fallback to `readMerchantPricingPlanForProvider` when the Prisma model is unavailable in the injected test/runtime shape.

### R5 — no public façade change

No new public route-facing API is introduced. Existing BillingService methods continue behaving identically and call the extracted owner where they currently use these helpers.

## Work Items

- [ ] Create `BillingPlanResolutionService` with injected Prisma dependency.
- [ ] Move the three catalogue/resolution responsibilities without semantic changes.
- [ ] Wire `BillingService` to one collaborator instance; do not duplicate validation.
- [ ] Add focused tests for reuse, materialisation, invalid catalogue, Merchant Knowledge validation, unique race, top-up configuration and provider-read fallback.
- [ ] Prove frozen façade regression suite remains byte-identical and green.

## Interfaces / Contracts

Repository-internal service contract. No Shared export.

The service returns the same operational resolution union and merchant-pricing/top-up read shapes currently consumed inside `BillingService`. These internal types may move with the service but must not alter public BillingService method return shapes.

## Dependencies

- `ARCH-025-SHOPIFY-001`

## Enables

- `ARCH-025-SHOPIFY-003`

## Acceptance Criteria

- [ ] Operational BillingPlan materialisation/catalogue validation has one owner.
- [ ] Merchant Knowledge compatibility validation exists in one resolution path, not duplicated.
- [ ] Unique BillingPlan race recovery and `materializedAt` behaviour are unchanged.
- [ ] No additional provider/database calls occur for equivalent branches.
- [ ] Frozen 127-test façade suite passes unchanged.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `sha256sum tests/unit/services/billing.service.test.ts` returns exactly `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests
- [ ] `npm test -- tests/unit/services/billing/billing-plan-resolution.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/billing-plan-resolution.service.ts tests/unit/services/billing/billing-plan-resolution.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Implementation Notes

Do not create a repository-wide catalogue abstraction. This service is Shopify billing-specific. A small local Prisma unique-constraint predicate may live with the service; do not create a generic utility package solely for that check.

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
