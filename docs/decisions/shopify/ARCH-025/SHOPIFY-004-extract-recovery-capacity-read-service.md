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
status: review
priority: 40
executor: copilot
claimed_at: 2026-10-01T22:07:10Z
attempt: 1
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

- [x] Create `MerchantRecoveryCapacityReadService` with Prisma + narrow billing-plan-resolution dependency.
- [x] Move exact capacity read logic and leave façade delegate.
- [x] Add focused tests covering all capacity sources, precedence, promotional validity, refund holds, FROZEN/NO_CONTRACT and invalid paid-period state.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Consumes `MerchantRecoveryCapacityState` from existing `billing.types.ts` and the internal top-up configuration read from SHOPIFY-002. No public contract changes.

## Dependencies

- `ARCH-025-SHOPIFY-003`

## Enables

- `ARCH-025-SHOPIFY-005`

## Acceptance Criteria

- [x] Capacity read responsibility is removed from the façade implementation.
- [x] Capacity precedence and all current availability states are unchanged.
- [x] No database write or Shopify provider call is introduced.
- [x] Top-up configuration has one catalogue owner.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [x] `npm test -- tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts` passes the new focused capability tests
- [x] `npm test` introduces no new failures
- [x] `npm run typecheck`
- [x] `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-recovery-capacity-read.service.ts tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts`
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not combine this with `MerchantBillingReadService`; recovery admission/capacity is a distinct business read model with different failure semantics.


## Completion Report

### Status

Ready for Review

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/services/billing/merchant-recovery-capacity-read.service.ts` (new)
- `tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts` (new)

### Work Completed

- Extracted the recovery-capacity read model into `MerchantRecoveryCapacityReadService`; `BillingService` constructs it with the existing database and `BillingPlanResolutionService`, then delegates without changing its public signature.
- Preserved the four parallel reads, counter arithmetic, promotion target/window checks, paid BillingPeriod integrity checks, top-up configuration reuse, blocker ordering, and capacity precedence.
- Added 9 focused tests covering source precedence/fallbacks, promotion eligibility and rejection cases, refund holds, NO_CONTRACT/FROZEN behavior, invalid paid-period projections, query shape, collaborator reuse, and absence of writes.

### Validation Results

- `npm run prisma:generate`: passed; generated Prisma Client 6.19.3.
- Frozen test SHA-256: `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` was empty.
- `npm test -- tests/unit/services/billing.service.test.ts`: 195 passed, 18 failed; all 18 failing identifiers are the documented `ARCH025-TEST-001` date-sensitive baseline.
- `npm test -- tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts`: passed, 9/9.
- `npm test`: 971 passed, 24 failed, 33 skipped across 90 test files; all 24 failing identifiers match `ARCH025-TEST-001` (18 frozen-suite failures and its six documented unrelated failures); no task-only failing identifier.
- `npm run typecheck`: passed.
- `npx eslint app/services/billing/billing.service.ts app/services/billing/merchant-recovery-capacity-read.service.ts tests/unit/services/billing/merchant-recovery-capacity-read.service.test.ts`: passed; ESLint emitted the repository's existing TypeScript 5.9.3 parser-support warning.
- `npm run build`: passed; existing Vite dependency/chunk warnings were emitted.
- `git diff --check`: passed.
- Editor diagnostics for all three changed files: no errors.

### Deviations

None. Existing test failures were compared with and found unchanged from `ARCH025-TEST-001` in `docs/development-baseline.md`.

### Assumptions

The SHOPIFY-004 attempt was claimed with both task worktrees synchronized. Parent `origin/main` advanced during validation; its new commit was merged into the parent task branch before report submission.

### Unresolved Issues

The 18 frozen-suite and six unrelated full-suite failures documented by `ARCH025-TEST-001` remain; none is introduced by this task.

### Architectural Concerns

None identified.

### Git / VCS

Task branch: `task/ARCH-025-SHOPIFY-004`

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-004`
- Parent branch: `task/ARCH-025-SHOPIFY-004`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-004`
- Implementation branch: `task/ARCH-025-SHOPIFY-004`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization:
- Parent remote task branch fast-forwarded: not needed; launcher found it synchronized at claim.
- Parent `origin/main` incorporated: already current at claim; later commit `99f8c59e` arrived during validation and was merged into the task branch before report submission.
- Implementation remote task branch fast-forwarded: not needed; no remote task ref existed when the prepared implementation worktree was established.
- Implementation `origin/main` incorporated: yes, already current at `1630c0e10b9c88e6bbb568d597b3b19c8a36d2ec`.

Implementation repository:
- Repository: `moda-interact`
- Commit: `350dedbf61290a01bf3edba642de64cc8482c811`
- Remote branch: `origin/task/ARCH-025-SHOPIFY-004`
- Pushed: yes

Parent workspace:
- Task file: `docs/decisions/shopify/ARCH-025/SHOPIFY-004-extract-recovery-capacity-read-service.md`
- Report commit: `5091aa4bf646a86f721f0bdf798bf2a9047868be`
- Remote branch: `origin/task/ARCH-025-SHOPIFY-004`
- Pushed: yes
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
