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
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
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
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — one operational plan owner

Create `BillingPlanResolutionService` (name may be exact) receiving the existing Prisma dependency and owning `OperationalBillingPlanResolution` plus the logic equivalent to:

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

### R6 — preserve frozen-suite private runtime seam

The frozen regression suite intentionally reaches the runtime-private method named `resolveOrMaterializeBillingPlan(...)` by casting `BillingService`. Therefore this task MUST retain a thin private method with that exact name on `BillingService`; it delegates to `BillingPlanResolutionService` and contains no resolution/materialisation implementation. Do not remove or rename this delegate during ARCH-025 while `billing.service.test.ts` remains frozen.

## Work Items

- [x] Create `BillingPlanResolutionService` with injected Prisma dependency.
- [x] Move the three catalogue/resolution responsibilities without semantic changes.
- [x] Wire `BillingService` to one collaborator instance; do not duplicate validation.
- [x] Retain `BillingService.resolveOrMaterializeBillingPlan(...)` as a thin private compatibility delegate for the frozen regression suite.
- [x] Add focused tests for reuse, materialisation, invalid catalogue, Merchant Knowledge validation, unique race, top-up configuration and provider-read fallback.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Repository-internal service contract. No Shared export.

The service returns the same operational resolution union and merchant-pricing/top-up read shapes currently consumed inside `BillingService`. These internal types may move with the service but must not alter public BillingService method return shapes.

## Dependencies

- `ARCH-025-SHOPIFY-001`

## Enables

- `ARCH-025-SHOPIFY-003`

## Acceptance Criteria

- [x] Operational BillingPlan materialisation/catalogue validation has one owner.
- [x] Merchant Knowledge compatibility validation exists in one resolution path, not duplicated.
- [x] Unique BillingPlan race recovery and `materializedAt` behaviour are unchanged.
- [x] No additional provider/database calls occur for equivalent branches.
- [x] The runtime-private `BillingService.resolveOrMaterializeBillingPlan(...)` name remains present as a thin delegate and its two existing frozen-suite calls still pass unchanged.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate` (passed; Prisma Client 6.19.3 generated).
- [x] Frozen test SHA-256 is `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4` and `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- [x] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001` (18 failures / 195 passed / 213 total; all 18 are documented).
- [x] `npm test -- tests/unit/services/billing/billing-plan-resolution.service.test.ts` passes (7 tests).
- [x] `npm test` introduces no new failures (24 failures / 958 passed / 33 skipped / 1015 total; all 24 identifiers are documented by `ARCH025-TEST-001`).
- [x] `npm run typecheck` passed.
- [x] Required three-file ESLint command passed.
- [x] `npm run build` passed.
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not create a repository-wide catalogue abstraction. This service is Shopify billing-specific. A small local Prisma unique-constraint predicate may live with the service; do not create a generic utility package solely for that check. The existing purchase workflow still needs its own P2002 detection until SHOPIFY-008; do not couple that workflow back to the plan-resolution service merely to share this tiny predicate.


## Completion Report

### Status

Review

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/services/billing/billing-plan-resolution.service.ts` (new)
- `tests/unit/services/billing/billing-plan-resolution.service.test.ts` (new)

### Work Completed

- Added `BillingPlanResolutionService`, injected with the existing Prisma client, and moved operational BillingPlan resolution/materialisation, recovery-credit top-up configuration reads, and MerchantPricingPlan catalogue reads into that single owner.
- Preserved the original transaction boundaries, resolution variants/reasons, catalogue validation, Merchant Knowledge active-pair validation, BillingPlan creation fields, unique-handle race recovery, and each `materializedAt` repair/update path without adding provider or database operations.
- Wired one collaborator instance in the `BillingService` constructor without changing its constructor signature. Kept `BillingService.resolveOrMaterializeBillingPlan(...)` as a thin private delegate for the frozen runtime-private test seam; all top-up and merchant-pricing read call sites now use the collaborator.
- Preserved database-first MerchantPricingPlan reads and provider fallback when the injected database shape lacks the model method.
- Added seven focused tests covering operational-plan reuse, catalogue materialisation, unknown/inactive results, Merchant Knowledge compatibility rejection, unique-race recovery, top-up configuration projection, database catalogue projection and provider fallback.
- Did not edit the frozen `tests/unit/services/billing.service.test.ts`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-002`
  parent branch: `task/ARCH-025-SHOPIFY-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-002`
  implementation branch: `task/ARCH-025-SHOPIFY-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent `origin/main` incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation `origin/main` incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commits: `database` at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`
  preparation claim: Attempt 1, executor `copilot`, claim commit `daf233e0de951213489f224a8ddfa58b48a1a898`, pushed

### Validation Results

- `npm run prisma:generate`: passed; Prisma Client 6.19.3 generated.
- Focused new service suite: passed, 1 file / 7 tests.
- Frozen private resolver seam: the two parameterized Merchant Knowledge rejection cases passed unchanged (2 passed, 211 skipped), directly exercising `BillingService.resolveOrMaterializeBillingPlan(...)`.
- Frozen `billing.service.test.ts`: 18 failed / 195 passed / 213 total. Every failing identifier is included in `ARCH025-TEST-001`; the frozen file hash is the exact required SHA-256 and its diff is empty.
- Full `npm test`: 5 failed files / 75 passed / 8 skipped; 24 failed / 958 passed / 33 skipped / 1015 total. All 18 frozen failures and six additional failures match `ARCH025-TEST-001`; a mechanical identifier comparison found zero new failures.
- `npm run typecheck`: passed.
- Required three-file ESLint command: passed.
- `npm run build`: passed (existing bundler warnings only).
- `git diff --check`: passed. Editor diagnostics reported no errors in the three authorized files.

### Deviations

None. The documented baseline failures remain visible in the test results and were not changed or suppressed.

### Assumptions

The existing `ARCH025-TEST-001` failure identifiers remain the accepted pre-task baseline for this ARCH-025 task; the current frozen and full-suite runs introduced no additional failing identifier.

### Unresolved Issues

None within this task's authorized scope.

### Architectural Concerns

None identified. The extracted collaborator is Shopify-billing-specific, has a side-effect-free constructor, and depends on the existing provider catalogue fallback rather than the façade.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted. `BillingPlanResolutionService` is the single owner of operational BillingPlan resolution/materialisation plus the two MerchantPricingPlan catalogue reads defined by this task. The extraction is mechanically faithful to the pre-task façade implementation: the transaction boundary, resolution-kind ordering, validation reason strings, Merchant Knowledge active-pair compatibility check, BillingPlan creation shape, `materializedAt` repair/update behaviour and P2002 winner recovery are unchanged.

`BillingService` constructs one collaborator from its existing Prisma dependency and retains the exact runtime-private `resolveOrMaterializeBillingPlan(...)` name as a thin delegate for the frozen regression seam. The moved top-up and provider-facing catalogue reads now route through the collaborator without adding database/provider operations. The collaborator constructor is side-effect-free and does not import the façade.

The submitted implementation commit `804894cc598d394c7d1f61bc2828c61743d1145f` is one commit ahead of implementation `main` at review time and changes only the three authorised files. The frozen façade file remains byte-identical at SHA-256 `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The reported frozen/full-suite failures contain no identifier outside durable baseline `ARCH025-TEST-001`; focused service tests, the two frozen private-seam cases, Prisma generation, typecheck, targeted ESLint, build and whitespace validation all passed.

No implementation correction or follow-up task is required for SHOPIFY-002.

### Reviewed Files

- `moda-interact/app/services/billing/billing-plan-resolution.service.ts`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/tests/unit/services/billing/billing-plan-resolution.service.test.ts`
- frozen `moda-interact/tests/unit/services/billing.service.test.ts` identity/evidence
- `docs/decisions/shopify/ARCH-025/SHOPIFY-002-extract-billing-plan-resolution.md`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- `docs/development-baseline.md` baseline `ARCH025-TEST-001`
- implementation commit `804894cc598d394c7d1f61bc2828c61743d1145f`
- parent report commit `8e809936f66aae8cc7e9899ea127ac795b131699`

### Validation Reviewed

- Independently confirmed the implementation branch changes only the three authorised files.
- Independently compared the moved resolution/materialisation and catalogue-read logic with the pre-task façade and found the relevant branch order, reads/writes, validation strings and retry semantics unchanged.
- Independently confirmed exactly one `BillingPlanResolutionService` collaborator instance is wired in `BillingService`, the runtime-private delegate is retained, and the extracted collaborator has no reverse import of `billing.service.ts`.
- Independently confirmed frozen `billing.service.test.ts` SHA-256 is the exact required value.
- Submitted focused `billing-plan-resolution.service.test.ts`: 7/7 passed.
- Submitted frozen private resolver seam: 2/2 selected cases passed unchanged.
- Submitted frozen suite: 18 failures / 195 passed / 213 total; all failures match `ARCH025-TEST-001`.
- Submitted full suite: 24 failures / 958 passed / 33 skipped / 1015 total; all failure identifiers match `ARCH025-TEST-001`.
- Submitted `npm run prisma:generate`, `npm run typecheck`, targeted ESLint, production build and `git diff --check`: passed.
- Physical worktree isolation, start-of-attempt synchronization, recursive submodule and clean/pushed evidence are recorded in the Completion Report.

### Architecture Conformance

Conforms to ARCH-025, the authorised Shopify repository/file boundary, move-only semantics, public façade compatibility, one-owner plan-resolution boundary, transaction/I/O preservation requirements and durable no-regression baseline `ARCH025-TEST-001`.

### Follow-up

`ARCH-025-SHOPIFY-003` is now Ready. Later ARCH-025 tasks remain Pending behind the sequential dependency chain. Do not begin SHOPIFY-004 or later work until the immediately preceding task is architect-accepted Complete.
