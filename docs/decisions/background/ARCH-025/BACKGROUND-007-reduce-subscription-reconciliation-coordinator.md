---
id: ARCH-025-BACKGROUND-007
architecture_id: ARCH-025
title: Reduce billing subscription reconciliation to a coordinator
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-006
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Reduce billing subscription reconciliation to a coordinator

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Complete the refactor by extracting bounded durable context loading and reducing `reconcileJob()` to parse, capture one runtime snapshot, load/classify, acquire one provider snapshot, replay existing lifecycle evidence and delegate to accepted lifecycle handlers.

## Context

After BACKGROUND-001 through BACKGROUND-006, all substantial business lifecycle engines have dedicated owners. This final task removes remaining orchestration density without changing the worker/caller façade or correcting unrelated behaviour.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reconciliation-context.ts
tests/unit/services/billing-subscription-reconciliation/reconciliation-context.test.ts
tests/unit/services/billing-subscription-reconciliation/coordinator.test.ts
```

Previously accepted ARCH-025 Background collaborator files may be wired/imported. Do not behaviourally revise an accepted earlier collaborator inside this task; if its interface proves insufficient, stop and return to `moda_architect`.

## Out of Scope

- new lifecycle behaviour or defect fixes.
- modifying existing canonical lifecycle/rollover/plan-change/projection services.
- caller/entrypoint migration.
- queue/Shared/schema/provider protocol changes.
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

### R1 — bounded context loader

Create `reconciliation-context.ts` owning the exact durable context read currently at the start of `reconcileJob()` and the current-plan-by-id read used by cycle/rollover/plan-change/FROZEN work. Preserve selected fields and query count; do not broaden to whole-row/domain-object loading.

The pure BACKGROUND-001 classifier still owns state classification/skip results. Context loading does not perform lifecycle decisions. After loading the current plan, preserve the **only two** pre-provider plan eligibility gates from the source: cycle discovery skips with `cycle-discovery-plan-ineligible` unless the plan is active, Free and pack-enabled; rollover skips with `rollover-plan-ineligible` unless the plan is active and, when Free, pack-enabled. Do **not** add the same gate to established-plan-change or FROZEN kinds.

### R2 — final coordinator flow and ordering

Refactor `reconcileJob()` into a dispatcher with this exact high-level order:

```text
parse Shared job
capture runtimeConfig.current() exactly once **after successful parse**
load bounded durable context
classify / log exact skip or accepted result
if reinstall -> delegate reinstall handler and return
load current plan when required; apply only the source cycle-discovery/rollover eligibility gates
request one getSubscriptionReconciliationSnapshot(...) and reuse it
on provider-fetch failure -> delegate lifecycle-specific failure handler
for non-initial work, run existing ShopifySubscriptionLifecycleReconciliationService when lifecycle evidence exists or kind is FROZEN
if lifecycle handled/restored -> republish committed durable schedule and return
delegate cycle/pre-close/rollover where applicable (preserving pre-close-before-provider-null ordering)
resolve provider-null outcomes through the owning handler
perform the source provider-handle BillingPlan lookup once
if established-plan-change with currentPlan -> delegate established plan-change handler
otherwise preserve the exact final Free/Paid/mismatch/applyOtherCurrentPlan predicate sequence, including legacy FROZEN `continue` fallthrough
```

No lifecycle transaction implementation should remain in `reconcileJob()`.

### R3 — one normal provider snapshot

For every accepted non-reinstall job requiring provider evidence, call `getSubscriptionReconciliationSnapshot(this.partner, shopifyShopId)` exactly once. Reuse both `snapshot.activeSubscription` and `snapshot.latestLifecycleEvent`. Preserve `provider_snapshot_requested` / `provider_snapshot_received` logging fields and timing around that call.

### R4 — lifecycle replay remains existing-service owned

Continue using `ShopifySubscriptionLifecycleReconciliationService` with the one captured runtime config. Preserve its current dependency source as well as its behaviour: the source constructs it with the façade database and captured runtime config while leaving its existing default resume-service/logger dependencies in place. Do not silently replace those defaults with different collaborators during this structural refactor. Do not move its durable lifecycle logic into the coordinator or create a competing lifecycle service.

When it returns `handled` or `restored`, read the committed `nextReconcileAt` and publish it through the BACKGROUND-002 queue collaborator exactly as today.

### R5 — frozen provider failure stays exact

The existing `recordFrozenProviderFailure(...)` FROZEN snapshot-fetch failure path may remain as one small coordinator-private failure helper or move to a tightly scoped adjacent helper, but preserve its exact CAS (`status: FROZEN`, plan id, consumed schedule), `PARTNER_API_ERROR`, captured `billingFrozenRecheckSeconds`, logging and next-job publication. Do not create a generic retry switch.

### R6 — preserve current fallthrough behaviour; do not opportunistically fix it

If an edge path appears questionable during extraction, preserve the source behaviour and frozen tests. In particular, when a FROZEN reconciliation reaches lifecycle result `continue`, do **not** add a new early return or a `kind === initial-activation` guard.

- When `snapshot.activeSubscription` is present, continue through the same provider-handle plan lookup and final Free/Paid/mismatch/`applyOtherCurrentPlan` predicates as the source, using BACKGROUND-001's unnormalised FROZEN expected-object shape and BACKGROUND-003's independently invocable `applyOtherCurrentPlan` operation.
- When `snapshot.activeSubscription` is null after a lifecycle `continue`, preserve the source provider-null dispatch to BACKGROUND-003 `recordMissingSubscription(...)` with that same FROZEN-shaped expected object. For a genuine FROZEN durable row its `NO_CONTRACT` CAS does not match, so the path remains a non-throwing no-op with no newly scheduled job. Do not substitute `recordFrozenProviderFailure`, `PROVIDER_STATE_UNRESOLVED`, or another newly invented retry.

Report either edge as a suspected product defect if appropriate, but do not change it inside ARCH-025.

### R7 — final façade/entrypoint compatibility

The final `BillingSubscriptionReconciliationService` retains the same constructor, public methods/exports and singleton. `src/entrypoints/billing.ts` must still instantiate it with the existing positional expression asserted by `entrypoint-isolation.test.ts`, and `billing-reconciliation.service.ts` continues calling `activateInitialPaid(...)` without migration.

## Work Items

- [x] Add bounded reconciliation context loading with the exact current select/query shape.
- [x] Reduce `reconcileJob()` to parse -> one runtime snapshot -> load -> classify -> one provider snapshot -> lifecycle replay -> handler delegation.
- [x] Remove obsolete lock wrappers from the coordinator; accepted lifecycle and activation workflows remain delegated to their existing owners.
- [x] Preserve exact skip/accepted/provider-snapshot structured log event names, levels, fields and emission order; explicitly cover `cycle-discovery-plan-ineligible` and `rollover-plan-ineligible`.
- [x] Prove stale/ineligible jobs remain provider-free and accepted normal jobs perform at most one snapshot provider call.
- [x] Add focused coordinator/context tests for invalid-input parse-before-runtime-config behaviour, dispatch, exact current-plan eligibility gates, provider-call count, runtime-config-single-read after parse, lifecycle handled/restored schedule publication, both FROZEN `continue` legacy fallthroughs (provider present and provider null), provider-error routing and no caller migration.
- [x] Prove `src/entrypoints/billing.ts` and `src/services/billing-reconciliation.service.ts` require no changes.
- [x] Prove the frozen 146-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Final public boundary remains `BillingSubscriptionReconciliationService`. `reconcileJob()` consumes Shared job parsing, pure classification, bounded context, queue service and lifecycle handlers. No new cross-repository contract is produced.

## Dependencies

- `ARCH-025-BACKGROUND-006`

## Enables

None

## Acceptance Criteria

- [x] `reconcileJob()` is a bounded coordinator and contains no complete activation, reinstall, cycle/rollover or established plan-change transaction workflow.
- [x] One runtime-config snapshot and one normal provider reconciliation snapshot are reused per accepted job exactly as required.
- [x] Reinstall retains its separate provider path.
- [x] Existing lifecycle reconciliation service remains canonical and committed lifecycle schedules are republished exactly as today.
- [x] Public constructor/methods/exports, billing worker entrypoint and `billing-reconciliation.service.ts` caller remain unchanged.
- [x] No provider/database/queue work is added to stale/ineligible hot paths; malformed input still fails before runtime-config/database/provider work, and established/FROZEN kinds do not gain cycle/rollover plan-eligibility gates.
- [ ] Frozen regression suite remains byte-identical and all 146 tests pass; full repository test/build pass.

## Validation

- [x] `npm run prisma:generate` (passed via `npm run build`)
- [x] Frozen-file SHA-256 is exact: `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`.
- [x] Frozen-file diff is empty.
- [x] Frozen regression suite passes all 146 tests.
- [x] Coordinator and context focused suites pass: 11/11 and 2/2 (13/13 combined).
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- [ ] Full `npm test` passes with no regression; run completed, results and blocker are recorded below.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-context.ts`
- `tests/unit/services/billing-subscription-reconciliation/coordinator.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-context.test.ts`

### Work Completed

- Added `ReconciliationContextService` for the exact bounded shop/subscription query and current-plan-by-id query; kept their existing selected fields and query count.
- Reduced `reconcileJob()` to parse, capture one runtime configuration snapshot, log receipt, load bounded context, classify, and dispatch accepted work to a private coordinator method.
- Preserved cycle-discovery and rollover-only plan eligibility gates, skip log fields, accepted/provider snapshot log event names and order, one provider snapshot call, current plan provider lookup, captured runtime config, and lifecycle handler defaults.
- Kept reinstall on its existing handler path and normal accepted work on a single `getSubscriptionReconciliationSnapshot(...)` call. Preserved pre-close behavior by delegating the same provider evidence to the billing-cycle handler.
- Preserved both FROZEN `continue` fallthroughs, including the legacy provider-present `applyOtherCurrentPlan(...)` dispatch and provider-null `recordMissingSubscription(...)` dispatch with the unnormalised FROZEN expected shape.
- Removed unused coordinator lock wrappers; existing lifecycle/activation transaction owners remain unchanged.
- Added focused tests covering exact context selects, parse-before-config behavior, dispatch/log/provider ordering, plan gates, lifecycle schedule republication, FROZEN fallthroughs, provider error routing, and reinstall delegation.
- Confirmed `src/entrypoints/billing.ts` and `src/services/billing-reconciliation.service.ts` are unchanged.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-007` on `task/ARCH-025-BACKGROUND-007`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-007` on the same task branch. Both worktrees were newly created; no shared checkout was switched and no other task worktree was reused. Parent and implementation task branches required no fast-forward and already incorporated `origin/main`. Recursive submodule sync/update passed; `database` was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- Frozen reconciliation suite: 146/146 passed; the SHA-256 remains `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239` and its diff is empty.
- New coordinator/context suites: 13/13 passed.
- Frozen + new reconciliation suites: 159/159 passed.
- Entrypoint isolation: 10/10 passed.
- `git diff --check`: passed.
- Full `npm test`: 1,536 passed, 38 skipped, 9 failed, plus one suite-loading failure. Eight test failures and the missing ARCH-020 fixture match durable baseline `ARCH025-BACKGROUND-TEST-001`. The additional failure is `tests/unit/runtime/observability-startup.test.ts > keeps hosted export disableable for 'moda-shopify-event-worker'`, which timed out at 5 seconds. This failure is not listed in `docs/development-baseline.md`; per B007 requirements it is reported unresolved and no further investigation or baseline change was made.

### Deviations

The required full-suite pass gate is not met because of the additional non-baselined observability startup timeout. This is outside the authorized B007 file scope and is returned to `moda_architect` for disposition.

### Assumptions

None

### Unresolved Issues

The full-suite observability startup timeout for `moda-shopify-event-worker` is not present in the durable development baseline. B007 implementation did not change observability files; the task-specific policy requires architect disposition before treating this as a baseline condition.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

- Accepted implementation `f501dda913c5d9618524a83f5da6d58c7bdc6c45` and submitted report `71acec42cd1fa4a636d8d8d986a0ac97f374a29e`.
- The implementation changes exactly the four authorised B007 files. `src/entrypoints/billing.ts`, `src/services/billing-reconciliation.service.ts`, the frozen regression file and previously accepted lifecycle collaborators are unchanged.
- `ReconciliationContextService` owns only the pre-existing bounded Shop/subscription read and current-plan-by-id read. The selected fields and query count are unchanged, and its constructor performs no I/O.
- `reconcileJob()` now performs only Shared parsing, one runtime-config capture after successful parse, bounded context loading, pure classification/skip handling and accepted-job dispatch. No activation, reinstall, cycle/rollover or established-plan-change transaction workflow remains in `reconcileJob()`.
- Accepted normal work retains the exact current-plan lookup conditions, the two source-only cycle/rollover eligibility gates, one `getSubscriptionReconciliationSnapshot(...)` call, provider snapshot requested/received log boundaries and reuse of both active-subscription and lifecycle evidence. Reinstall remains on its separate `getActiveSubscription(...)` path.
- Lifecycle replay remains owned by `ShopifySubscriptionLifecycleReconciliationService` constructed with the façade database and captured runtime config while preserving its existing default collaborators. `handled`/`restored` results still republish the committed durable schedule through the BACKGROUND-002 queue owner.
- Provider-null dispatch, final provider-handle BillingPlan lookup and the source Free/Paid/mismatch/`applyOtherCurrentPlan` predicate sequence are preserved. Both legacy FROZEN `continue` fallthroughs remain unchanged: provider-present continues through the final predicates and provider-null still reaches BACKGROUND-003 `recordMissingSubscription(...)`, whose `NO_CONTRACT` CAS harmlessly does not match a genuine FROZEN row.
- `recordFrozenProviderFailure(...)` retains its exact FROZEN/plan/schedule CAS, captured `billingFrozenRecheckSeconds`, `PARTNER_API_ERROR`, logging and next-job publication. Public constructor order, methods, singleton and compatibility exports remain intact.
- The additional `moda-shopify-event-worker` observability timeout is not a B007 regression. The failing `keeps hosted export disableable` probe spawns Node with only `./observability/shopify-event.mjs` and the Shared observability runtime; it does not execute the Shopify event entrypoint or any billing-reconciliation/B007 module. B007 changes no observability preload, Shared runtime, package or Docker input. The timeout remains separate runtime/observability follow-up and is not added to `ARCH025-BACKGROUND-TEST-001`.

### Reviewed Files

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-context.ts`
- `tests/unit/services/billing-subscription-reconciliation/coordinator.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-context.test.ts`
- `docs/decisions/background/ARCH-025/BACKGROUND-007-reduce-subscription-reconciliation-coordinator.md`

### Validation Reviewed

- Frozen reconciliation suite: 146/146 passed and SHA-256 remains `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; frozen diff is empty.
- Coordinator/context focused suites: 13/13 passed.
- Entrypoint isolation: 10/10 passed.
- `npm run build` passed, including Prisma generation and TypeScript compilation.
- `git diff --check` passed.
- Full `npm test`: 1,536 passed, 38 skipped, eight durable `ARCH025-BACKGROUND-TEST-001` failures plus the documented ARCH-020 fixture-loading failure, and one separate observability preload/runtime timeout outside the B007 execution path. No B007-owned or newly changed test failed.

### Architecture Conformance

Accepted. B007 completes the move-only billing-subscription reconciliation refactor: the public façade and worker/caller contracts remain stable while durable context loading, classification, queue publication and lifecycle workflows have bounded owners. The billing-reconciliation Background chain is complete.

### Follow-up

Keep the observability preload/runtime timeout outside `ARCH025-BACKGROUND-TEST-001` unless same-environment pre-task differential evidence establishes a durable baseline. No B007 implementation follow-up is required.
