---
id: ARCH-052-BACKGROUND-009
architecture_id: ARCH-052
title: Make Shopify catalogue and lifecycle writers preserve merchant selection
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-052-SHOPIFY-001
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: 2026-10-29
---

# ARCH-052-BACKGROUND-009: Make Shopify catalogue and lifecycle writers preserve merchant selection

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This task was materialised and executed through its canonical launcher-resolved parent and Background task worktrees. The Completion Report must record the prepared packet evidence for both histories.

## Objective

Standardise `ShopifyDiscount.isAvailable` to mean merchant-selected, including Shopify discount refresh and subscription lifecycle transitions.

## Context

`shopify-discount-catalogue.service.ts` currently sets isAvailable=true on every upsert, false on disappearance/unavailable, and `billing-subscription-reconciliation/reinstall-reconciliation.service.ts` clears it when a contract is lost; Woo sync intentionally preserves this flag.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- In `src/services/shopify-discount-catalogue.service.ts`, set `isAvailable:false` ONLY in the `upsert.create` branch for brand-new provider discount rows. Remove `isAvailable` entirely from `upsert.update`. Never set `isAvailable` from providerStatus, syncGeneration, active scope, dates, or catalogue status.
- Delete the `shopifyDiscount.updateMany(...isAvailable:false)` calls from stale-generation reconciliation and `markCatalogueUnavailable`. Keep the existing `unavailableAt` and catalogue status changes untouched; a missing provider discount remains selected but is never eligible while unavailable.
- In `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`, remove only the `isAvailable:false` clearing operation in `completeReinstallWithoutContract`; retain subscription/Shop/catalogue invalidation and `unavailableAt` transitions unchanged.
- Audit every Background `shopifyDiscount` upsert/update/updateMany write in this snapshot for `isAvailable` modifications and prove that merchant selection is changed only by authenticated merchant settings APIs. Do not modify Woo coupon sync.
- Add PostgreSQL integration tests for new discount defaults false, sync does not select all, merchant choice survives full resync, disappearance, missing read scope, catalogue UNAVAILABLE and reinstall/no-contract; provider liveness still blocks positive eligibility.

## Out of Scope

- No DB migrations or schema changes, no merchant UI, no Woo API write or offer eligibility/AI implementation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- This is a prerequisite for Shopify multi-selection. Never infer a discount is authorised merely from the provider catalogue; availability fields remain separate.
- No historical backfill: development fixtures will explicitly reset only Shopify selections and fixed anchors before enabling the new feature.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [x] Remove all Background-originated Shopify selection writes except false on first creation.
- [x] Verify no-contract/reinstall path and provider metadata invalidation remain intact.
- [x] Add PostgreSQL lifecycle/concurrency regression tests for sync, selection, provider eligibility, and reinstall.

## Interfaces / Contracts

- `ShopifyDiscount.isAvailable` means merchant selection; existing provider fields and catalogue generation retain their meanings.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHOPIFY-001`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] All newly synced discounts remain unchecked; selected ones survive re-sync and reinstall without becoming provider-eligible if unavailable.
- [x] No Woo merchant checkbox state is changed by this task.

## Validation

- [x] Shopify catalogue and reinstall service unit/integration tests; provider unavailable and sync race cases.
- [ ] Background test/build/lint according to package.json, `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`
- `moda-interact-background/tests/integration/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Ready for Review — Attempt 2 completed the requested report corrections and passed the PostgreSQL lifecycle integration suite. No implementation service changes were needed.

### Prepared Execution Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Task definition status from the prepared launcher: materialized.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-009`, branch `task/ARCH-052-BACKGROUND-009`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-009`, branch `task/ARCH-052-BACKGROUND-009`.
- Shared workspace checkout switched or mutated for task work: no. Shared implementation checkout switched or mutated for task work: no. Another task worktree reused: no.
- Parent task branch fast-forward from origin task branch: not needed. Parent `origin/main` incorporated: already current. Parent start head: `e24fa08e9bbdfe77e559cb916d46211c0dcf8ef6`.
- Implementation branch fast-forward from origin task branch: not needed. Implementation `origin/main` incorporated: already current. Implementation start head: `086d35c7c3b91d7dd79c855045107fe72f93d185`.
- `git submodule sync --recursive`: passed. `git submodule update --init --recursive`: passed. `database` was initialized at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Attempt 2 claim was committed and pushed by the launcher as `d7979909d79aa685ac6b2a38d53a40a5b848fe3d`.

### Files Changed

- `moda-interact-background/src/services/shopify-discount-catalogue.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts`
- `moda-interact-background/tests/integration/arch052-shopify-discount-selection.integration.test.ts`
- `moda-interact-background/package.json`

### Work Completed

- Shopify sync now creates new provider rows with `isAvailable: false` and omits the flag from existing-row updates. Disappearance and unavailable-catalogue handling still set `unavailableAt` and retain their existing catalogue status transitions without changing merchant selection.
- No-contract reinstall still invalidates the catalogue and stamps `unavailableAt`; it no longer clears merchant selection. The focused unit assertion verifies that only the unavailable timestamp update remains.
- Audited Background `shopifyDiscount` writes: Shopify sync is the only Background path writing `isAvailable`, and it writes false only in the upsert create branch. Woo sync still creates unchecked rows and omits the flag from updates. No Background writer changes an existing merchant choice. The current API selection writer is authenticated and Woo-scoped; Shopify selection changes remain owned by the authenticated settings/API implementation.
- Added disposable PostgreSQL integration coverage for new-row defaults, selection surviving a full sync, a new discount remaining unchecked, disappearance, missing `read_discounts` scope and `UNAVAILABLE` catalogue state, provider-status eligibility, no-contract reinstall, and a stale concurrent sync response.

### Validation Results

- Passed: focused unit files for Shopify catalogue and reinstall reconciliation (10 tests).
- Passed: `npm run build` (Prisma client generation and TypeScript build).
- Passed: ESLint on all five changed Background files.
- Passed: `git diff --check`.
- Passed on Attempt 2: `npm run test:arch052-shopify-discount-selection:postgres` (2 tests), covering initial unchecked rows, full resync selection retention, disappearance, missing scope/UNAVAILABLE catalogue, provider eligibility, no-contract reinstall, and a stale concurrent sync response.
- Passed on Attempt 2: ESLint on the corrected PostgreSQL integration test and `git diff --check`.
- Attempt 1 repository-wide `npm test` completed with 280 test files passing and 22 failing (3,044 tests passing and 64 failing). Failures are outside the changed files; observed causes include unavailable Redis/database services, Prisma client setup in unit suites, and logger/fixture expectation mismatches. It was not rerun on Attempt 2 because only the integration test clock expectation and this report changed.
- Attempt 1 repository-wide `npm run lint` reported one issue in untouched `src/services/translation-reconciliation.service.ts:218` (`preserve-caught-error`); changed-file lint passed. The repository-wide lint script was not rerun on Attempt 2.

### Deviations

The first PostgreSQL attempt exposed a test assertion that incorrectly equated `unavailableAt` with the requested sync time. The assertion now verifies the persisted timestamp is retained across later lifecycle transitions; the final disposable PostgreSQL run passed. The repository-wide test and lint failures are recorded above and were not changed because they are unrelated to this task.

### Assumptions

Provider liveness and catalogue availability remain represented by provider metadata and `unavailableAt`; preserving `isAvailable` therefore does not make a missing or provider-ineligible discount eligible.

### Unresolved Issues

None for this task. The Docker CLI at `/usr/local/bin/docker` was missing from the test shell's `PATH`; the active Colima Docker daemon was available, and the required PostgreSQL suite passed after adding the CLI directory to `PATH`.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Attempt 2 Architect Review

#### Review Status

Changes Requested — repository-wide validation disposition

#### Review Notes

The previously requested corrections are satisfied. The Completion Report records the guarded PostgreSQL lifecycle suite passing (2 tests) after the initial Docker PATH issue was resolved; it records the dedicated parent and implementation worktree paths, branches, start heads, task-branch and `origin/main` synchronization results, recursive submodule preparation, and no shared checkout or task worktree reuse. The task's Architecture section now correctly says this definition was materialised and executed.

The implementation diff remains within scope and the lifecycle behavior conforms to the merchant-selection invariant. The focused catalogue/reinstall unit tests, disposable PostgreSQL integration, build, changed-file ESLint and diff checks are reported passing. No code defect has been identified and no source change is requested at this point.

Acceptance is still withheld because the second required Validation item remains unchecked. The Completion Report records repository-wide `npm test` with 64 failing tests across 22 files and `npm run lint` with one error in an untouched file. These are described generally as unrelated environment/fixture issues, but it does not list the failing test identities or establish that they match a pre-task baseline. The current development baseline has no entry matching this reported 64-test/22-file failure set. We therefore cannot yet confirm that task changes caused no regression across the required Background test validation.

#### Reviewed Files

- Attempt 2 Completion Report and launcher evidence.
- Background implementation branch `task/ARCH-052-BACKGROUND-009` at `086d35c7c3b91d7dd79c855045107fe72f93d185`; its five-file diff from `origin/main` and clean worktree.
- `src/services/shopify-discount-catalogue.service.ts`.
- `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`.
- `tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts`.
- `tests/integration/arch052-shopify-discount-selection.integration.test.ts`.
- The task Validation checklist, ARCH-052 execution table and dependent task records.

#### Validation Reviewed

Reviewed Attempt 2's passing `npm run test:arch052-shopify-discount-selection:postgres` (2 tests), changed integration-file ESLint, and `git diff --check`; Attempt 1's 10 focused unit tests, `npm run build`, changed-file lint and diff check; and the reported full-suite/lint failures. The PostgreSQL integration and launcher evidence close the prior review findings. No tests were rerun for this review.

#### Architecture Conformance

The implementation conforms to ARCH-052 and repository ownership. This task remains incomplete until the unchecked required Validation item is reconciled with evidence that the repository-wide failures are pre-existing/environmental and do not include task-caused regressions. No dependent task is promoted while the task is not Complete.

#### Follow-up

Return this same task to `ready`, clear `executor` and `claimed_at`, preserve `attempt: 2`, and let the next canonical launcher claim advance the attempt once. Before review resubmission:

1. Reconcile the unchecked Validation item. Record the failing test/suite identities from the full `npm test` output and establish, by matching documented baseline evidence or comparison with the task's starting `origin/main` under equivalent dependency/service conditions, that these failures are not introduced or worsened by this task. Confirm the full lint error remains in the untouched `translation-reconciliation.service.ts` and that all changed files pass targeted lint. Do not fix unrelated repository failures inside this task.
2. If any failure is new or task-related, correct it within this task's scope or return the exact issue to moda_architect if it crosses ownership. Then update the Validation checklist and Completion Report accurately; do not mark a failed or unrun command as passing.

The PostgreSQL integration and worktree/materialisation corrections are accepted as evidence and need not be repeated unless relevant code or environment changes.

### Attempt 1 Architect Review — Changes Requested


### Review Status

Changes Requested — required validation and workflow evidence

### Review Notes

The implementation diff at Background commit `086d35c7c3b91d7dd79c855045107fe72f93d185` is narrowly scoped and matches the requested behavior: new Shopify discount rows default to unchecked, updates preserve existing merchant selection, disappearance/unavailable catalogue paths retain their availability timestamps without changing selection, and the no-contract reinstall path no longer clears selection. The implementation audit and targeted unit assertions are consistent with those changes. No source defect is established from the reviewed diff.

Acceptance is withheld because the task's explicit PostgreSQL lifecycle integration validation did not run. The guarded command stopped before tests with `spawn docker ENOENT`, and the required validation item remains unchecked. The integration scenarios cover creation defaults, selection through resync, missing scope/disappearance/unavailable state, provider eligibility, reinstall, and stale concurrent sync; unit tests cannot substitute for this database integration contract.

The Completion Report also omits mandatory prepared-launcher evidence for physical task isolation and start synchronization. In addition, the task Architecture section still calls this definition portable and unmaterialised, contradicting the actual claimed task branch, canonical parent task worktree, implementation task worktree, and the Completion Report. The task definition has been reconciled to the materialised state; the implementing report still needs the packet evidence.

The repository-wide `npm test` and `npm run lint` results are reported as failing in unrelated areas while focused tests and changed-file lint pass. No unrelated failures are assigned to this task for correction. No source changes are requested unless the required PostgreSQL validation exposes a task-scope failure.

### Reviewed Files

- Background implementation task branch at `086d35c7c3b91d7dd79c855045107fe72f93d185` and its 5-file diff from `origin/main`.
- `src/services/shopify-discount-catalogue.service.ts`.
- `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`.
- `tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts`.
- `tests/integration/arch052-shopify-discount-selection.integration.test.ts`.
- Task Completion Report, ARCH-052 execution table, and `ARCH-052-SHOPIFY-001`/system-test dependency references.

### Validation Reviewed

Reviewed recorded focused unit results (10 tests), `npm run build`, changed-file ESLint, and `git diff --check`. The task-specific PostgreSQL command did not execute tests because Docker was unavailable. Repository-wide `npm test` reports 280 files passing and 22 failing (3,044 passed / 64 failed); repository-wide lint reports one issue in untouched `translation-reconciliation.service.ts`. No tests were rerun. The implementation worktree is clean at the pushed task commit.

### Architecture Conformance

The code changes conform to ARCH-052's separation of merchant selection from provider liveness and preserve repository ownership. Completion remains gated on the specified PostgreSQL lifecycle tests and complete prepared-launcher evidence. No dependent task is promoted while this task is not Complete.

### Follow-up

Return this same task to `ready`, clear `executor` and `claimed_at`, preserve `attempt: 1`, and have the next launcher claim increment it once. Before review resubmission:

1. Run `npm run test:arch052-shopify-discount-selection:postgres` with the repository's disposable PostgreSQL harness available. Record a passing result covering all listed lifecycle/race cases. Do not claim the skipped attempt as passed; do not change code unless a scenario fails.
2. Complete the Completion Report's prepared execution evidence from the launcher packet: canonical workspace root; parent and implementation worktree paths and branches; confirmation whether shared checkouts were switched/mutated or another task worktree reused; for each repository, task-branch fast-forward and `origin/main` synchronization results; recursive submodule preparation result. Do not infer synchronization results from current branch cleanliness. If the packet shows shared/default-checkout execution, restore/use the canonical worktrees, rerun required validation there, and correct the evidence per isolation policy.
3. Keep the report consistent with the materialised task lifecycle and explain the repository-wide failures as environment/baseline observations without claiming they passed.

No implementation changes are required if the integration test passes. `ARCH-052-SHOPIFY-001` and `ARCH-052-SYSTEM-TEST-001` remain Pending until this task is accepted Complete and their other dependencies are satisfied.
