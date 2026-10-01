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
status: review
priority: 50
executor: copilot
claimed_at: 2026-10-01T22:31:04Z
attempt: 1
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
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
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

- [x] Create `MerchantBillingReadService` with provider, Prisma and narrow collaborator dependencies.
- [x] Move merchant billing-state composition and leave façade delegate, importing SHOPIFY-001 cycle/integer helpers and SHOPIFY-002 catalogue reads directly.
- [x] Add focused tests for Free/Paid presentation, exact-cycle phase, provider snapshot reuse, provider failure, offer diagnostics/purchase eligibility and unresolved purchases.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Repository-internal service. Existing method return shape remains the route-facing contract. Existing provider and merchant-pricing contracts are reused.

## Dependencies

- `ARCH-025-SHOPIFY-004`

## Enables

- `ARCH-025-SHOPIFY-006`

## Acceptance Criteria

- [x] Merchant billing-page read model has one owner outside the façade.
- [x] Verified commercial state prevents duplicate provider reads exactly as before; absent state performs the same single provider read without extra SHOPIFY-003 mapping queries.
- [x] Recovery-credit offer eligibility uses unchanged cycle/phase rules.
- [x] No returned field or error/fallback meaning changes.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [x] `npm test -- tests/unit/services/billing/merchant-billing-read.service.test.ts` passes the new focused capability tests
- [x] `npm test` introduces no new failures
- [x] `npm run typecheck`
- [x] `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-billing-read.service.ts tests/unit/services/billing/merchant-billing-read.service.test.ts`
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Keep this a read service. Do not absorb the purchase command simply because both concern recovery-credit packs.


## Completion Report

### Status

Ready for Review

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/services/billing/merchant-billing-read.service.ts` (new)
- `tests/unit/services/billing/merchant-billing-read.service.test.ts` (new)

### Work Completed

- Extracted `getMerchantBillingState` into `MerchantBillingReadService` and left the `BillingService` public method as a delegate with the same parameters and inferred result contract.
- Preserved local reads, return fields, counters/refund holds, purchase history and labels, offer diagnostics, unavailable reasons, exact-cycle phase/integrity checks, verified commercial snapshot reuse, and provider failure handling.
- Reused the SHOPIFY-001 cycle/integer helpers and SHOPIFY-002 `readMerchantPricingPlan` collaborator. The extracted service does not use SHOPIFY-003 `SubscriptionReadService` or perform plan-mapping reads.
- Added 6 focused tests covering Free/Paid balances, invalid Paid counters, exact-cycle eligibility, supplied snapshot reuse, the single provider lookup path, provider failures, diagnostics and unresolved purchase presentation.

### Validation Results

- `npm run prisma:generate`: passed; Prisma Client 6.19.3 generated.
- Frozen test SHA-256: `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` was empty.
- `npm test -- tests/unit/services/billing.service.test.ts`: 195 passed, 18 failed; all 18 identifiers match `ARCH025-TEST-001`.
- `npm test -- tests/unit/services/billing/merchant-billing-read.service.test.ts`: passed, 6/6.
- `npm test`: 977 passed, 24 failed, 33 skipped across 91 test files; all 24 identifiers match `ARCH025-TEST-001` (18 frozen BillingService failures and 6 documented unrelated failures), with no task-only failing identifier.
- `npm run typecheck`: passed.
- `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-billing-read.service.ts tests/unit/services/billing/merchant-billing-read.service.test.ts`: passed; emitted the existing TypeScript 5.9.3 parser-support warning.
- `npm run build`: passed; existing dependency annotation, empty-route chunk and large-chunk warnings were emitted.
- `git diff --check`: passed.
- Editor diagnostics for all three changed files: no errors.

### Deviations

None. Existing failures match `ARCH025-TEST-001` in `docs/development-baseline.md`.

### Assumptions

The prepared launcher packet is authoritative for worktree, branch synchronization, dependency gate and recursive submodule readiness evidence.

### Unresolved Issues

The 18 frozen BillingService and six unrelated full-suite failures documented by `ARCH025-TEST-001` remain; no new failing identifier was introduced.

### Architectural Concerns

None identified.

### Git / VCS

Task branch: `task/ARCH-025-SHOPIFY-005`

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-005`
- Parent branch: `task/ARCH-025-SHOPIFY-005`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-005`
- Implementation branch: `task/ARCH-025-SHOPIFY-005`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization:
- Parent remote task branch fast-forwarded: not-needed.
- Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed.
- Implementation `origin/main` incorporated: already-current.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; database initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

Implementation repository:
- Repository: `moda-interact`
- Commit: `28b7cc065035d8bc0fe81a30208c33d770930b08`
- Remote branch: `origin/task/ARCH-025-SHOPIFY-005`
- Pushed: yes

Parent workspace:
- Task file: `docs/decisions/shopify/ARCH-025/SHOPIFY-005-extract-merchant-billing-read-service.md`
- Report commit: to be recorded after task-file commit.
- Remote branch: `origin/task/ARCH-025-SHOPIFY-005`
- Pushed: pending
- Submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

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
