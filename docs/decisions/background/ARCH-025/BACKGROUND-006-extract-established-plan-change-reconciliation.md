---
id: ARCH-025-BACKGROUND-006
architecture_id: ARCH-025
title: Extract established plan-change reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-005
enables:
  - ARCH-025-BACKGROUND-007
created: 2026-10-02
updated: 2026-10-03
---

# Extract established plan-change reconciliation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract established active/trialing/retryable-SYNC_ERROR plan-change convergence into one handler while preserving its exact CAS predicates, validation/failure policy and canonical `ShopifyPlanChangeTransitionService` delegation.

## Context

After cycle/reinstall/activation extraction, established plan changes are the last substantial lifecycle engine still owned by the coordinator. Isolating them leaves `reconcileJob()` ready to become a bounded parse/context/provider/delegate coordinator.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts
```

Earlier ARCH-025 Background collaborators are consumable dependencies.

## Out of Scope

- modifying `ShopifyPlanChangeTransitionService`.
- changing provider snapshot acquisition.
- cycle/reinstall/activation behaviour.
- retry interval/error-code changes.
- edits to the frozen regression file.

## Requirements

### Common ARCH-025 Background invariants

- This is a **move-only structural refactor**. Do not change billing semantics, provider protocol, queue contract, queue/job identity, retry intervals, error codes, authorization, durable lifecycle state or external worker behaviour.
- Preserve the exact public compatibility surface from `src/services/billing-subscription-reconciliation.service.ts`: `BillingSubscriptionReconciliationService`, `billingSubscriptionReconciliationService`, `activateInitialPaid`, `enqueue`, `reconstruct`, `reconcileJob`, `InitialActivationPlan`, `FREE_CYCLE_DISCOVERY_RETRY_MS`, `ROLLOVER_RETRY_MS`, `nextSubscriptionReconcileAt`, `createSubscriptionReconcilePayload` and the `APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS` compatibility re-export.
- Preserve the positional constructor `(database, partner, queue, logger, now, runtimeConfig, discountQueue)`. Do not modify `src/entrypoints/billing.ts` or `src/services/billing-reconciliation.service.ts` to accommodate extraction.
- Extracted modules MUST NOT import `billing-subscription-reconciliation.service.ts`; dependency direction is coordinator -> collaborator. Symbols moved out of the coordinator file that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during construction.
- Preserve parse-before-runtime-config ordering: only after `parseBillingSubscriptionReconcileJob(...)` succeeds, call `runtimeConfig.current()` exactly once and pass that immutable snapshot downstream. Malformed input must still fail during parsing before runtime-config, database or provider work.
- Normal accepted queued reconciliation performs at most the current single `getSubscriptionReconciliationSnapshot(...)` provider call and reuses `activeSubscription` plus `latestLifecycleEvent`. Do not multiply provider calls while splitting handlers.
- Reinstall reconciliation remains on its distinct `partner.getActiveSubscription(...)` path; do not replace it with the normal reconciliation snapshot helper.
- Preserve all provider/network versus Prisma transaction boundaries, `SELECT ... FOR UPDATE` targets/order, `updateMany` CAS predicates, durable rereads and post-commit side-effect ordering exactly. Preserve existing clock-read points/order too: do not coalesce, hoist or reorder repeated `now()` reads where doing so could move drain-window, period-boundary, retry or queue-delay decisions. Do not impose one global lock order across lifecycles where the current code uses different transaction shapes.
- Continue delegating canonical work to `SamePlanBillingPeriodRolloverService`, `ShopifyPlanChangeTransitionService`, `ShopifySubscriptionLifecycleReconciliationService`, `ensureCurrentBillingPeriodProjection`, `shopifyUsageEventPublisherService`, `shopifyDiscountCatalogueService` and `recoveryCapacityResumeService`; do not duplicate those implementations.
- Preserve existing `billing.subscription_reconciliation.*` structured log event names, levels, bounded field sets and emission boundaries/order relative to the I/O they describe; use the canonical Shared logger and do not log whole provider/customer payloads.
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts` is frozen: do not edit it. SHA-256 must remain `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, and all 146 tests must pass after every task.
- Add separate focused tests for the extracted owner. Do not move assertions out of the frozen regression file, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- `tests/unit/runtime/entrypoint-isolation.test.ts` must continue passing so the billing-worker construction/startup contract remains unchanged.
- Full `npm test` must pass. If execution reveals a pre-existing baseline condition, stop and report it to `moda_architect` unless it is already durably documented in `docs/development-baseline.md`; do not silently redefine the baseline inside this task.

### R1 — move the complete established plan-change cluster

Create `established-plan-change-reconciliation.service.ts` and move:

```text
reconcileEstablishedPlanChange
establishedPlanChangeWhere
nextPlanReconcileAt
recordEstablishedPlanChangeFailure
recordEstablishedPlanChangeRetry
schedulePlanChangeCapacityResume
```

Keep the existing BillingPlan lookup for `provider.planHandle` in the coordinator/final provider-plan dispatch through BACKGROUND-007 and pass its result into this handler as `targetPlan`. Do not duplicate, remove or conditionally skip that lookup on branches where the source currently performs it. The handler retains the separate provider-`pendingPlanHandle` lookup inside the `providerIsCurrent` branch exactly as today.

### R2 — reuse shared retryable-status definition

Consume BACKGROUND-001's single retryable established-plan-change SYNC_ERROR set in both classification and `establishedPlanChangeWhere(...)`. Do not maintain a second local copy.

### R3 — provider/current/pending decision semantics

Preserve all current branches:

- provider remains on current plan -> refresh/clear pending provider projection and schedule pending effective/pre-close as today;
- provider is pending target on same cycle -> fail closed with `UNEXPECTED_IMMEDIATE_PLAN_CHANGE`;
- target appears before effective time -> reschedule exact pending effective time;
- target at/after effective time -> validate cycle/allowance/meters and delegate to `ShopifyPlanChangeTransitionService`;
- unmapped provider handle -> current UNMAPPED terminal behaviour;
- other unexpected provider plan -> current SYNC_ERROR retry behaviour.

### R4 — failure/retry policy remains lifecycle-owned

Preserve 60-second `ROLLOVER_RETRY_MS` behaviour for retryable failures, fail-closed status transitions, observed-handle updates and `PROVIDER_STATE_UNRESOLVED` / `PARTNER_API_ERROR` distinctions. The queue collaborator only publishes the chosen next time.

### R5 — canonical transition/capacity side effect

Durable plan transition remains owned by `ShopifyPlanChangeTransitionService`. On a successful transition, preserve exact next-job publication and best-effort `recoveryCapacityResumeService.schedule({ trigger: "plan-change" })`; enqueue failure remains warning-only after the committed transition.

### R6 — no provider fetch inside handler

The handler consumes the one provider snapshot already acquired by the coordinator and performs no Partner API call.

## Work Items

- [x] Add the established plan-change reconciliation service and move the full method cluster.
- [x] Consume the coordinator-provided provider-handle plan lookup result and preserve the separate pending-handle lookup on the provider-current branch without adding/removing reads.
- [x] Reuse the BACKGROUND-001 retryable error set and BACKGROUND-003 timing/BACKGROUND-002 queue collaborators.
- [x] Continue delegating durable transitions to `ShopifyPlanChangeTransitionService`.
- [x] Add focused tests for provider-current refresh/withdrawal, exact drain/effective scheduling, same-cycle immediate change, missing cycle/meter/allowance, provider null/error retry, unmapped/unexpected plan and capacity-resume failure isolation.
- [x] Prove handler performs zero provider API calls.
- [x] Prove the frozen 146-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Internal handler receives expected durable plan-change snapshot, current plan, provider evidence, queue/timing/logger/clock dependencies and database. It does not fetch Shopify provider state.

## Dependencies

- `ARCH-025-BACKGROUND-005`

## Enables

- `ARCH-025-BACKGROUND-007`

## Acceptance Criteria

- [x] Established plan-change implementation has one dedicated owner and no duplicate retryable-error set.
- [x] Provider-current, early target, valid transition, unmapped and fail-closed/retry branches are behaviourally unchanged.
- [x] `ShopifyPlanChangeTransitionService` remains the durable transition owner.
- [x] Capacity resume remains post-transition/best-effort.
- [x] The exact source BillingPlan lookup sequence is preserved: current-plan-by-id upstream, one provider-handle lookup in the final coordinator dispatch, and the existing pending-handle lookup only when `providerIsCurrent` requires it.
- [x] Frozen regression suite remains byte-identical and all 146 tests pass.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)` prints the expected SHA-256
- [x] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes all 146 frozen regression tests
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts` passes (12 tests)
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes (10 tests)
- [ ] `npm test` passes with no regression (full run retains documented baseline failures; see Completion Report)
- [x] `npm run build` succeeds
- [x] `git diff --check` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Architect Review; the full suite remains nonzero for documented baseline identities and two transient observability timeouts that passed when rerun in isolation.

### Files Changed

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts`
- `tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts`
- This task report only in the parent workspace.

### Work Completed

- Moved established plan-change convergence, CAS/retry/failure helpers, timing, and best-effort capacity resume into `EstablishedPlanChangeReconciliationService`; the coordinator now delegates at its existing dispatch, provider error, and provider-null branches.
- Preserved coordinator current-plan-by-ID and provider-handle plan lookup positions, plus the pending-handle lookup only in the provider-is-current branch. The handler receives the existing provider snapshot and has no Partner API dependency.
- Reused the shared retryable error list, `ROLLOVER_RETRY_MS`, reconciliation queue, and canonical `ShopifyPlanChangeTransitionService` without changing the coordinator constructor or compatibility exports.
- Added 12 focused tests covering current-plan refresh/withdrawal, drain/effective scheduling, same-cycle fail-closed behavior, missing prerequisites, transition delegation, unmapped and unexpected plans, provider retry recording, and warning-only capacity-resume failure.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-006`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-006`; both use `task/ARCH-025-BACKGROUND-006`. Both worktrees were newly created, no task-branch fast-forward was needed, and `origin/main` was current. Shared workspace/implementation checkouts were not switched or mutated; no other task worktree was reused. Recursive submodule sync/update passed; database submodule was at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

- `npm run prisma:generate`: passed.
- Frozen regression SHA-256 matched `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; frozen-file diff was empty; all 146 tests passed.
- Focused established-plan-change suite: 12/12 passed.
- Entrypoint isolation: 10/10 passed. Combined affected slice: 167/167 passed.
- `npm run build`: passed; `git diff --check`: passed.
- Full `npm test`: 1,507 passed, 38 skipped, 10 failed, plus one failed suite load. Eight failures and the missing fixture suite match `ARCH025-BACKGROUND-TEST-001`. Two `observability-startup` tests timed out under full-suite load; rerunning that file alone passed 10/10. No B006 test failed.

### Deviations

- The full test suite did not return exit code 0 because of the recorded baseline failures and fixture-loading failure, plus two observability timeouts under full-suite load. The observability file passed when rerun alone; no baseline was changed and no unrelated failures were modified.

### Assumptions

The task's documented `ARCH025-BACKGROUND-TEST-001` remains the source of truth for the eight stable pre-task failing test identities and the ARCH-020 fixture-loading failure. Full-suite-only observability timeouts are treated as transient because all 10 tests passed in an isolated rerun.

### Unresolved Issues

Full `npm test` remains non-green for the conditions recorded above; this is presented for Architect Review, not treated as a full-suite pass.

### Architectural Concerns

None identified within the assigned extraction scope. Architect acceptance is pending.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

- Reviewed implementation `dbbb9a0664c12887b5245f5839d5e07bd4bdaeb4` against launcher base `fa3e5d910cd31941ada9c1e5dfd1feac7dce3e00` and parent report `32cd45fe484571c5c01a34af473f93edd4c3bd3c`. The implementation is one bounded commit and changes only the three authorised implementation/test files.
- The established plan-change cluster is a move-only extraction. The coordinator still performs the current-plan-by-id read, captures one provider reconciliation snapshot, preserves lifecycle replay, performs the existing provider-handle BillingPlan lookup once in final dispatch, and then delegates the already-resolved provider/current/target inputs. The extracted service has no Partner API dependency.
- Provider-current refresh/withdrawal, the separate pending-handle lookup, effective-time scheduling, same-cycle `UNEXPECTED_IMMEDIATE_PLAN_CHANGE`, target validation, canonical `ShopifyPlanChangeTransitionService` delegation, unmapped/fail-closed handling, 60-second retries, observed-handle projection and post-transition capacity resume are preserved. `establishedPlanChangeWhere(...)` continues to consume the BACKGROUND-001 `RETRYABLE_PLAN_CHANGE_SYNC_ERRORS` set.
- Method-by-method comparison found no durable-state, CAS, clock, queue, logging or transition semantic drift. The small syntactic simplification from nested `updated.count > 0` / `if (next)` to a combined condition is behaviorally equivalent. Constructor shape and compatibility exports remain unchanged.
- Full `npm test` is nonzero only for the eight durable `ARCH025-BACKGROUND-TEST-001` identities, the documented ARCH-020 fixture-loading condition and two full-suite-only observability startup timeouts. The observability file passes 10/10 in isolation, so those timeouts are not added to the durable baseline and do not block this bounded extraction.

### Reviewed Files

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.ts`
- `tests/unit/services/billing-subscription-reconciliation/established-plan-change-reconciliation.service.test.ts`
- `docs/decisions/background/ARCH-025/BACKGROUND-006-extract-established-plan-change-reconciliation.md`

### Validation Reviewed

- Prisma generation passed.
- Frozen reconciliation asset SHA-256 remains `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, its diff is empty, and the frozen suite passes 146/146.
- Focused established-plan-change suite passes 12/12.
- Entrypoint isolation passes 10/10; the positional billing-worker constructor remains unchanged.
- `npm run build` and `git diff --check` pass.
- Full suite: 1,507 passed / 38 skipped / 10 failed plus the known fixture-loading failure. Eight persistent failures and the fixture condition match `ARCH025-BACKGROUND-TEST-001`; the two additional observability timeouts pass 10/10 on isolated rerun.
- Launcher evidence records dedicated parent/implementation worktrees, clean remote-aligned task branches and successful recursive submodule synchronization.

### Architecture Conformance

Accepted. BACKGROUND-006 satisfies the ARCH-025 move-only boundary: established plan-change convergence has one dedicated owner while provider snapshot acquisition, final provider-handle plan lookup and final dispatch remain coordinator-owned through BACKGROUND-007. No new provider call, retry policy, durable transition owner or worker/constructor surface was introduced.

### Follow-up

`ARCH-025-BACKGROUND-007` is promoted to Ready. The full-suite-only observability timeouts remain outside the durable Background baseline unless separately proven by same-environment differential evidence.
