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
status: review
priority: 10
executor: null
claimed_at: null
attempt: 3
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
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

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
- [x] Background test/build/lint according to package.json, git diff --check; repository-wide failures were compared with the pre-task revision and all are identical.

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

Ready for Review — Attempt 3 reconciled repository-wide test and lint results against the pre-task revision. No implementation service changes were needed.

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

### Attempt 3 Completion Report

#### Prepared Execution and Synchronization Evidence

- The parent task branch contains the Attempt 3 claim commit a12157db2e581cef75a04974edfae7ac4d5264ef, pushed to origin/task/ARCH-052-BACKGROUND-009. Its parent/start commit is 59bccbdf4, which incorporated the resolved origin/main index merge. The task's remote branch was already synchronized at that start state.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-009, branch task/ARCH-052-BACKGROUND-009. Parent origin/main was incorporated at the start state.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-009, branch task/ARCH-052-BACKGROUND-009, start head a5be659 (Fix Shopify selection integration timestamp assertion). Its local task branch matched origin/task/ARCH-052-BACKGROUND-009; origin/main at f80d916 was already an ancestor.
- The launcher returned TASK_NOT_READY because the task was already in_progress for codex; it did not emit a prepared packet on this invocation. The above history and branch state are recorded directly from the two canonical task worktrees. Recursive submodule status remains at the recorded database gitlink f16d5fc955b1fa1215177cc89fb6fd326bfa65c8; Attempt 2's prepared packet recorded recursive submodule sync/update as passed.
- Shared workspace and implementation checkouts were not switched for task work. No other task worktree was reused.

#### Validation Results

- npm test on the submitted task branch: 20 test files failed, 282 passed; 64 tests failed, 3,079 passed (3,143 total).
- Compared with the pre-task Background revision f80d916 in an isolated source snapshot, using Node v24.19.0, npm 11.17.0, the same installed node_modules, the same package-lock.json SHA-256 (e3880239dde01b5979419c9db42232d6c8568df5d1985beacd9d51683bf85ac7), the same database gitlink (f16d5fc955b1fa1215177cc89fb6fd326bfa65c8), and DATABASE_URL=postgresql://localhost/test, REDIS_URL=redis://localhost: the baseline also had 20 failing files, 282 passing files, 64 failing tests and 3,079 passing tests. A sorted comparison of all 64 failure identities produced no differences. The earlier Attempt 1 count of 22 failing files was from before Prisma Client generation; this equivalent post-build comparison supersedes it.
- Exact failing test identities present on both pre-task and submitted revisions:

~~~text
tests/unit/commerce/model-bridge-diagnostics.test.ts > ARCH-029 model bridge diagnostics > identifies the exact production_model_invoke phase without logging the raw exception
tests/unit/commerce/model-bridge-diagnostics.test.ts > ARCH-029 model bridge diagnostics > identifies the exact response_postprocess phase without logging the raw exception
tests/unit/commerce/model-bridge-diagnostics.test.ts > ARCH-029 model bridge diagnostics > identifies the exact turn_state_check phase without logging the raw exception
tests/unit/runtime/entrypoint-isolation.test.ts > production worker entrypoints > wires bounded Shared logging for scheduled billing failures
tests/unit/services/billing-reconciliation/reconciliation-scheduler.service.test.ts > BillingReconciliationSchedulerService > keeps periodic reconciliation successful when queue publication fails
tests/unit/services/billing-reconciliation/same-plan-period-progression.service.test.ts > SamePlanPeriodProgressionService > isolates recovery-capacity resume failure after a committed paid rollover
tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts > EstablishedPlanChangeReconciliationService > keeps a successful plan transition when capacity resume enqueue fails
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > does not execute an unrelated SYNC_ERROR as an established plan change
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: enabled Free pack meter null
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: enabled Paid pack meter null
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: invalid cycle
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: missing cycle
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: missing normal Paid meter config
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: negative Paid allowance
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: non-integer Paid allowance
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: null Paid allowance
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: provider omits Free pack meter
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: provider omits Paid pack meter
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: provider omits normal Paid meter
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > fails established queued plan change closed for invalid target prerequisite: unsafe Paid allowance
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > retries established plan changes from retryable SYNC_ERROR: INVALID_INCLUDED_ALLOWANCE
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > retries established plan changes from retryable SYNC_ERROR: MISSING_BILLING_CYCLE
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > retries established plan changes from retryable SYNC_ERROR: MISSING_USAGE_METER
tests/unit/services/billing-subscription-reconciliation/facade-established-plan-transition.test.ts > BillingSubscriptionReconciliationService > retries established plan changes from retryable SYNC_ERROR: UNEXPECTED_IMMEDIATE_PLAN_CHANGE
tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts > RecoveryCapacityResumeProcessorService > requeues an early targeted wake-up while the original suppression block write is pending
tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts > RecoveryOutreachFinalizationService initial Support notice wiring > logs the billing stage and rethrows the exact error
tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts > RecoveryOutreachFinalizationService initial Support notice wiring > logs the follow-up stage and rethrows the exact error
tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts > RecoveryOutreachFinalizationService initial Support notice wiring > logs the notice stage and rethrows the exact error
tests/unit/services/checkout-recovery/recovery-outreach-finalization-notice.test.ts > RecoveryOutreachFinalizationService initial Support notice wiring > logs the recovery status stage and rethrows the exact error
tests/unit/services/conversation-wrappers/service.test.ts > ARCH-047 BG005 selection and facade > logs exceptions through shared-logger interface and rethrows, never swallows
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > admits the fifth Free recovery and blocks the next distinct recovery before send
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > allows paid recovery beyond included units and does not repeat a duplicate send
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > allows provider-check-required templates to reach the provider
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > creates a recovery from current Shopify data when the lookup is found and recoverable
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > materializes a token-only candidate after stale activity fills its lookup hints
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > never uses the candidate's embedded webhook basket data for recovery fields
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > persists a truthful descriptor for a selected non-English template
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > uses current CustomerPhone when the checkout snapshot has no phone
tests/unit/services/matured-candidate.materialization.test.ts > CheckoutRecoveryService.materializeMaturedCandidate > uses merchant defaults only when current and event context are absent
tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts > OutboundMessageDeliveryService > converges synchronous 131026 through compensation and reachability owners
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > activates a native App Pricing purchase only for its derived context identity
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > activates a zero-cost purchase when quantity proof is exact
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > activates distinct event-handle candidates independently
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > activates one equivalent provider-confirmed unit deterministically
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > activates sequential purchases with the same event handle from successive baselines
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > does not alter an activated purchase when a later plan handle is observed
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > does not derive the stored purchase amount from a plan price
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > does not grant twice when the provider quantity is replayed
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > proves a candidate from its exact snapshot handle and supports fractional baselines
tests/unit/services/recovery-credit-purchase.service.test.ts > RecoveryCreditPurchaseService > runs activation at Serializable isolation with the aggregate grant in the same transaction
tests/unit/services/recovery-offers/recovery-offer-ai.test.ts > ARCH-047-BACKGROUND-004 AI-only and read-only behaviour > logs and propagates unexpected AI exceptions instead of silently swallowing them
tests/unit/services/recovery-offers/recovery-offer-resolver.test.ts > ARCH-047-BACKGROUND-004 FIXED/NONE recovery offers > logs unexpected database/provider exceptions without sensitive error messages and rethrows
tests/unit/services/recovery-template-preparation/recovery-template-preparer.test.ts > ARCH-047 BACKGROUND-001: reusable, read-only recovery template preparation > logs every handled binding exception and rethrows unexpected provider/database errors
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts > ShopifySubscriptionLifecycleReconciliationService > does not add a second Paid grant after BACKGROUND-007 restoration
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts > ShopifySubscriptionLifecycleReconciliationService > restores an unfrozen subscription only from live same-cycle evidence
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts > ShopifySubscriptionLifecycleReconciliationService > restores changed mapped plan through BACKGROUND-010 exactly once
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts > ShopifySubscriptionLifecycleReconciliationService > restores later same-plan Free cycle without resetting lifetime Free
tests/unit/services/shopify-subscription-lifecycle-reconciliation.service.test.ts > ShopifySubscriptionLifecycleReconciliationService > restores later same-plan Paid cycle through BACKGROUND-007 exactly once
tests/unit/services/translation-batch-assembly.service.test.ts > TranslationBatchAssemblyService > commits the durable batch before requesting submit work
tests/unit/services/translation-batch-assembly.service.test.ts > TranslationBatchAssemblyService > keeps the committed batch durable when submit enqueue fails
tests/unit/services/translation-batch-assembly.service.test.ts > TranslationBatchAssemblyService > returns idempotently when no eligible translation is available
tests/unit/services/translation-reconciliation.service.test.ts > ARCH-043 support translation credential revocation > fails before provider construction when Commerce credentials are revoked despite a valid legacy OPENAI_API_KEY
tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts > ARCH-048-BACKGROUND-004 WooRecoveryOutreachService > keeps an unknown provider timeout visible and never blindly retries
tests/unit/workers/shopify-discount-sync.worker.test.ts > Shopify discount sync worker logging > logs bounded worker-level errors
~~~

- npm run lint on the submitted branch and at f80d916 each reported exactly one error: src/services/translation-reconciliation.service.ts:218, rule preserve-caught-error. The file is byte-identical to the pre-task revision and is outside the task diff.
- Targeted ESLint on all four changed TypeScript source/test files passed. git diff --check f80d916..HEAD passed.
- npm run build passed during Attempt 1; no production source changed in Attempts 2 or 3. Attempt 2's PostgreSQL lifecycle integration also passed (2 tests), and the focused unit coverage remains 10 passing tests.

#### Validation Disposition

The repository-wide failures and lint diagnostic are identical on the pre-task and submitted revisions under equivalent conditions. No task-caused failure or worsening was found. The Validation checkbox is marked complete to record that required validation was executed and reconciled; the baseline failures remain visible above rather than being represented as passing.

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
