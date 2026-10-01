---
id: ARCH-025-SHOPIFY-001
architecture_id: ARCH-025
title: Extract current billing-period projection invariants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
  - ARCH-025-SHOPIFY-002
created: 2026-10-01
updated: 2026-10-01
---

# Extract current billing-period projection invariants

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the current BillingPeriod cycle/projection logic from `billing.service.ts` into one repository-internal billing-period module while preserving the façade export and every current projection/CAS behaviour.

## Context

`billing.service.ts` currently owns `hasDurableBillingPeriod`, `hasMatchingBillingCycle`, `ensureMappedCurrentBillingPeriodProjection` and `deriveBillingPeriodPhase`. These functions form one coherent responsibility: validate/represent the current durable provider billing cycle and safely create/repair the mapped BillingPeriod projection. ARCH-017 already established the exact conflict-preserving semantics; this task moves that accepted logic without redesign.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/billing-period-projection.ts              # new
tests/unit/services/billing/billing-period-projection.test.ts  # new
```

No other production or test file is authorised.

## Out of Scope

- BillingPlan resolution/materialisation.
- activation, hosted callback, merchant read, purchase or sync workflow extraction beyond replacing existing helper calls with imports.
- schema/migration changes.
- edits to the frozen `billing.service.test.ts`.

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

### R1 — exact symbol ownership

Move the current logic equivalent to:

```text
DurableBillingCycle
CurrentBillingPeriodPlan
CurrentBillingPeriodProjectionConflictReason
CurrentBillingPeriodProjectionResult
hasDurableBillingPeriod
hasMatchingBillingCycle
ensureMappedCurrentBillingPeriodProjection
deriveBillingPeriodPhase
isSafeNonNegativeInteger   # repository-internal helper required by projection and SHOPIFY-005
```

into `billing-period-projection.ts`.

### R2 — preserve projection algorithm exactly

The extracted `ensureMappedCurrentBillingPeriodProjection(transaction, input)` must retain the current signature/return semantics and remain transaction-caller-owned. It MUST NOT open its own transaction.

Preserve exactly:

```text
invalid PAID allowance -> CONFLICT / INVALID_INCLUDED_ALLOWANCE
missing exact period -> create complete OPEN mapped period
PAID create -> create INCLUDED_RECOVERY_CREDITS counter
closed/mismatched existing durable facts -> CONFLICT, no overwrite
compatible null mapping -> repair exact existing row in place
compatible existing-period path retains the current BillingPeriod update call; do not optimise it away (the row has `updatedAt @updatedAt`)
FREE + included counter -> conflict
PAID counter arithmetic/grant mismatch -> conflict
missing PAID included counter -> create once
READY returns exact billingPeriodId + repaired flag
```

### R3 — preserve public and repository-internal exports

`deriveBillingPeriodPhase` must remain importable from `app/services/billing/billing.service.ts` through a compatibility re-export. Existing callers/tests must not migrate.

The new projection module must also export `hasDurableBillingPeriod`, `hasMatchingBillingCycle` and `isSafeNonNegativeInteger` as repository-internal helpers for later ARCH-025 tasks. They are **not** new public route contracts and need not be re-exported from the façade unless already public.

### R4 — no I/O expansion

The extracted helper performs exactly the existing Prisma operations for the same branches. No provider call, logger or additional durable read/write is introduced.

## Work Items

- [x] Create `billing-period-projection.ts` and move the bounded projection/cycle logic, including `isSafeNonNegativeInteger`.
- [x] Replace in-file implementations with imports/re-export wiring from `billing.service.ts`.
- [x] Add focused unit tests for READY create, compatible repair, FREE/PAID counter rules, conflict/no-overwrite and phase/cycle helpers.
- [ ] Prove the frozen façade suite is byte-identical and green. Attempt 2 proves its 18 failures are identical on the exact pre-task baseline; the suite is not green on either commit, as documented below.

## Interfaces / Contracts

Internal module contract only. `DurableBillingCycle` moves with the cycle helpers. `ensureMappedCurrentBillingPeriodProjection` continues accepting an existing `Prisma.TransactionClient`; transaction ownership stays with the caller. `hasDurableBillingPeriod`, `hasMatchingBillingCycle` and `isSafeNonNegativeInteger` are stable repository-internal exports for later ARCH-025 collaborators.

Public compatibility contract: `deriveBillingPeriodPhase` continues to be exported by `billing.service.ts`.

## Dependencies

None

## Enables

- `ARCH-025-SHOPIFY-002`

## Acceptance Criteria

- [x] BillingPeriod projection/cycle logic has one owner in `billing-period-projection.ts`.
- [x] No equivalent implementation remains duplicated in `billing.service.ts`.
- [x] Existing conflict reasons, reads/writes (including the compatible-row update), counter semantics and returned results are unchanged.
- [x] `deriveBillingPeriodPhase` remains publicly available from `billing.service.ts`.
- [ ] Frozen 127-test façade suite passes unchanged. The file hash is unchanged; the actual suite contains 213 tests and the same 18 failures on both the pre-task baseline and submitted commit against the 2026-10-01 runtime date.

## Validation

- [x] `npm run prisma:generate` (Prisma Client 6.19.3 generated successfully)
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` passes all 127 tests. Actual suite: 18 failed / 195 passed / 213 total on both pre-task and submitted commits; frozen file hash remains exact.
- [x] `npm test -- tests/unit/services/billing/billing-period-projection.test.ts` passes the new focused capability tests (11 tests)
- [x] `npm test` introduces no new failures. Attempt 2 differential: identical 24 failing test identifiers on pre-task and submitted commits; submitted adds the 11 passing focused projection tests. Exact counts and identifiers are recorded below.
- [x] `npm run typecheck`
- [x] `npx eslint app/services/billing/billing.service.ts app/services/billing/billing-period-projection.ts tests/unit/services/billing/billing-period-projection.test.ts`
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Prefer direct function exports from the internal module rather than a class; this capability has no owned mutable state. Do not create a generic billing utility module. The extracted names may remain unchanged where practical so the diff is mechanically reviewable.


## Completion Report

### Status

Review

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/services/billing/billing-period-projection.ts` (new)
- `tests/unit/services/billing/billing-period-projection.test.ts` (new)

### Work Completed

- Moved `DurableBillingCycle`, projection types, `hasDurableBillingPeriod`, `hasMatchingBillingCycle`, `ensureMappedCurrentBillingPeriodProjection`, `deriveBillingPeriodPhase` and `isSafeNonNegativeInteger` into the repository-internal billing-period module. The projection algorithm, including the compatible existing-period update, counter rules, conflict reasons and transaction-caller ownership, was moved without redesign.
- Rewired existing `BillingService` call sites to the internal module and retained `deriveBillingPeriodPhase` as a compatibility export from `billing.service.ts`.
- Added 11 focused tests covering paid create/counter creation, compatible repair/update, missing paid counter repair, closed-period no-overwrite, FREE and PAID counter conflicts, invalid allowance, cycle matching, phase boundaries and safe integer checks.
- Frozen `tests/unit/services/billing.service.test.ts` was not edited. Its SHA-256 remains `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`.
- Implementation commit: `ed1e4eb` (`Extract billing period projection helpers`), pushed to `task/ARCH-025-SHOPIFY-001`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-001`
  parent branch: `task/ARCH-025-SHOPIFY-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-001`
  implementation branch: `task/ARCH-025-SHOPIFY-001`
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
  preparation claim: Attempt 1, executor `copilot`, claim commit `c2b5751f3f2276ca1eefe149a59c26e63c1ba909`, pushed

### Validation Results

- `npm run prisma:generate`: passed; Prisma Client 6.19.3 generated.
- Focused new suite: passed, 1 file / 11 tests.
- Frozen façade suite: failed, 18 of 213 tests. Several failures use a fixed period end of `2026-10-01T00:00:00.000Z` without freezing the clock, so with the runtime date on 2026-10-01 after midnight, the unchanged phase function returns `RECONCILING` and recovery-credit requests stop at the transition guard. The committed pre-extraction implementation has the same `now = new Date()` phase logic. Frozen source SHA and diff checks pass. No baseline ID for these failures was found.
- Full `npm test`: 5 failed files / 24 failed tests; 74 files passed / 8 skipped; 951 tests passed / 33 skipped. Failures: 18 in the frozen billing façade suite, 1 billing UI test, 1 merchant knowledge read-model test, 1 merchant navigation test, and 3 merchant pricing renderer tests. No matching documented baseline entries were found. The shared-runtime timeout seen on the first full run did not recur on the final run.
- `npm run typecheck`: passed.
- Required three-file ESLint command: passed (repository parser emitted its existing TypeScript 5.9 support-range warning).
- `npm run build`: passed (client and SSR bundles built; existing bundler warnings only).
- Frozen file SHA-256: exact required value; frozen file diff: empty.
- `git diff --check`: passed.

### Attempt 2 — A1-R1 Baseline Differential

Evidence-only rework; no production or test source files were changed.

- Compared exact pre-task commit `b6d1fd6d362f2a6a302a735e0a54abd8ee677782` with submitted implementation commit `ed1e4ebe00f29e16e4acb1d799784a6b60b23531`.
- Both trees used Node `v24.21.0`, npm `11.19.0`, identical `package.json` and `package-lock.json`, the same submitted `node_modules` dependency tree, and database submodule commit `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Frozen test SHA-256 in both trees: `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`.
- Frozen façade suite on each commit: 1 failed file; 18 failed, 195 passed, 213 total. Sorted failing test identifiers were identical:
  - `BillingService subscription projection > schedules the next pre-close reconciliation for a pack-enabled Free cycle`
  - `BillingService recovery credit packs > creates a pending pack request for a mapped FREE plan`
  - `BillingService recovery credit packs > creates a pending pack request for a mapped PAID_METERED plan`
  - `BillingService recovery credit packs > uses Serializable isolation and locks Subscription before single-flight lookup`
  - `BillingService recovery credit packs > returns the existing purchase without creating another usage event`
  - `BillingService recovery credit packs > blocks a second unresolved purchase for the same provider context`
  - `BillingService recovery credit packs > replays an existing purchase without provider availability`
  - `BillingService recovery credit packs > fails closed when the durable configuration changes after provider verification`
  - `BillingService recovery credit packs > fails closed when live provider evidence changes before the transaction`
  - `BillingService recovery credit packs > fails closed when the transaction re-read changes the billing period identity`
  - `BillingService recovery credit packs > fails closed when the transaction re-read changes the billing period boundary`
  - `BillingService recovery credit packs > ignores legacy singular top-up configuration fields`
  - `BillingService recovery credit packs > persists fractional provider-before quantity and derived identity when legacy subscription ID is null`
  - `BillingService recovery credit packs > blocks an unresolved purchase from a previous period or provider identity for the same offer`
  - `BillingService recovery credit packs > allows independent unresolved purchases for different event handles`
  - `BillingService recovery credit packs > ignores client-supplied plan and pricing fields`
  - `BillingService recovery credit packs > recovers a concurrent same-id unique conflict by returning the committed purchase`
  - `BillingService recovery credit packs > verifies Shopify before opening the Prisma write transaction`
- Full suite on the pre-task baseline: 5 failed files, 24 failed / 940 passed / 33 skipped, 997 total tests (86 files).
- Full suite on the submitted commit: 5 failed files, 24 failed / 951 passed / 33 skipped, 1008 total tests (87 files). The 11 additional tests are the passing focused projection tests.
- All 24 full-suite failing test identifiers are identical between the two commits. In addition to the 18 façade tests above, the six other failures are:
  - `tests/unit/billing-ui.test.ts > canonical merchant billing UI > sends onboarding plan CTAs to Shopify plan selection`
  - `tests/unit/merchant-knowledge-read-model.test.ts > limits the catalogue to supported WEB_PAGE pairs and filters source types before the cap`
  - `tests/unit/merchant-navigation-history.test.tsx > merchant navigation and history links > renders localized navigation without stale Messages label for ACTIVE`
  - `tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > renders structured DTO card content and hides raw usage pricing mechanics`
  - `tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > renders a generic unavailable state for an empty catalogue`
  - `tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > omits the Free proof item when the active catalogue has no Free plan`
- Thus no failure is present only in the submitted commit; sorted full failure identifiers were compared directly.
- Submitted-tree reruns: focused projection suite 11/11 passed; `npm run typecheck` passed; required three-file ESLint passed with the existing TypeScript parser support-range warning; `npm run build` passed with existing bundler warnings; `git diff --check` passed.
- Launcher Attempt 2 claim: executor `copilot`, claim commit `08fdbb3db15fcd2970d29c711a5b06ddfbdfcfb7`, pushed. Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-001`; implementation commit unchanged at `ed1e4ebe00f29e16e4acb1d799784a6b60b23531`; recursive submodule status `ready` at the recorded database revision.
- Attempt 2 synchronization: parent task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `yes`; implementation task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.

### Deviations

The task text describes the frozen façade suite as 127 tests, but the current checked-in file executes 213 tests. The frozen suite is byte-identical and was not modified; Attempt 2 proves the same 18 failures occur on the exact pre-task commit, so neither run is green. The full suite likewise has the same 24 failing test identifiers on both commits; see the Attempt 2 differential evidence above.

### Assumptions

The phase-helper failures reflect the current wall-clock date against fixed historical test fixtures; the extracted implementation retains the original function body and default-time behavior.

### Unresolved Issues

- Architect guidance is needed on reconciling the task's 127-test acceptance wording with the checked-in 213-test façade suite and its baseline-identical failures. The task prohibits editing the frozen façade test file.
- The full suite has 6 non-billing test failures in addition to the 18 frozen façade failures; Attempt 2 proves all 24 failing test identifiers are also present at the exact pre-task baseline. They remain outside the authorised source scope.

### Architectural Concerns

None identified in the bounded extraction. No provider calls, transaction ownership, durable operations or production call paths were changed beyond importing the moved helpers.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is source-conformant, but acceptance is blocked on regression-baseline evidence rather than code correction.

Independent review established that implementation commit `ed1e4ebe00f29e16e4acb1d799784a6b60b23531` is exactly one commit ahead of pre-task `moda-interact` baseline `b6d1fd6d362f2a6a302a735e0a54abd8ee677782` and changes only the three authorised files. The extracted billing-period projection/cycle bodies preserve the pre-task Prisma operations, branch ordering, transaction-caller ownership, conflict reasons, counter arithmetic and default-time phase semantics. `billing.service.ts` retains the compatibility export for `deriveBillingPeriodPhase`, and no equivalent helper implementation remains duplicated there.

The frozen `tests/unit/services/billing.service.test.ts` SHA-256 is the required `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`, and the implementation commit does not modify that file. Focused projection tests, typecheck, targeted lint, build and `git diff --check` are reported passing.

However, two required validation gates remain unproven:

1. the frozen façade suite currently reports 18 failures / 213 tests even though the architecture/task text says 127 tests; and
2. the full suite reports 24 failures, including six outside the frozen façade suite.

The Completion Report gives a credible fixed-date explanation for the 18 façade failures, but `docs/development-baseline.md` contains no matching baseline entry and Attempt 1 did not execute the same suites on the exact pre-task commit. The six other full-suite failures likewise have no durable baseline evidence. Under the ARCH-025 no-regression contract, those failures cannot be treated as pre-existing solely from explanation or unchanged-file scope.

No production or test source change is requested at this point. Attempt 2 is an evidence-only differential validation attempt unless it demonstrates a task-introduced regression.

### Reviewed Files

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/billing-period-projection.ts`
- `moda-interact/tests/unit/services/billing/billing-period-projection.test.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- `docs/decisions/shopify/ARCH-025/SHOPIFY-001-extract-billing-period-projection.md`
- `docs/decisions/shopify/ARCH-025/_index.md`
- `docs/development-baseline.md`
- implementation commit `ed1e4ebe00f29e16e4acb1d799784a6b60b23531` and its pre-task merge base `b6d1fd6d362f2a6a302a735e0a54abd8ee677782`

### Validation Reviewed

- GitHub comparison: pre-task `b6d1fd6d362f2a6a302a735e0a54abd8ee677782` -> submitted `ed1e4ebe00f29e16e4acb1d799784a6b60b23531` is one commit with only the three authorised files changed.
- Frozen façade source SHA-256: exact required value; implementation commit does not change the frozen test file.
- Focused extracted-owner suite: reported 11/11 passing.
- `npm run typecheck`: reported passing.
- required targeted ESLint: reported passing.
- `npm run build`: reported passing.
- `git diff --check`: reported passing.
- Frozen façade suite: 18 failures / 213 tests; not yet proven identical on the pre-task baseline.
- Full `npm test`: 24 failures; not yet proven identical on the pre-task baseline.

### Architecture Conformance

The implementation conforms to the ARCH-025 move-only extraction boundary, authorised file scope, façade compatibility, projection/CAS semantics, transaction ownership, I/O-preservation requirement and repository ownership. Acceptance is withheld only because the architecture's regression gate requires proof that the observed failing tests are not task regressions.

### Follow-up

**A1-R1 — Evidence-only baseline differential; no source/test edits requested.**

Reclaim this same task for Attempt 2 through the canonical launcher and keep the existing implementation commit unchanged unless the differential validation identifies a genuine regression.

Using the same Node/dependency state and database submodule revision for both comparisons:

1. preserve the submitted implementation worktree at `ed1e4ebe00f29e16e4acb1d799784a6b60b23531`;
2. create a disposable detached validation checkout/worktree at exact pre-task commit `b6d1fd6d362f2a6a302a735e0a54abd8ee677782` (validation only; it is not a replacement implementation worktree);
3. in both baseline and submitted trees verify the frozen file SHA-256;
4. run `npm test -- tests/unit/services/billing.service.test.ts` in both trees and record the exact failing test names/counts;
5. run full `npm test` in both trees and record the exact failing file/test names/counts;
6. demonstrate that the submitted commit has no failure absent from the pre-task baseline. If failure sets are identical, do not modify production code or the frozen test file;
7. rerun the focused projection suite plus the task-required typecheck, targeted lint, build and `git diff --check` on the submitted implementation tree;
8. update only the Completion Report/execution evidence, return the task to `review`, clear the claim and STOP.

If the submitted commit has any task-only failure, correct it only if it belongs to this task's authorised scope; otherwise return the dependency/scope issue to `moda_architect`. Do not edit the frozen façade test, do not weaken assertions, and do not start `ARCH-025-SHOPIFY-002`.

The architect will reconcile the erroneous `127` test-count wording and create any durable development-baseline entry only after the baseline differential is proven.
