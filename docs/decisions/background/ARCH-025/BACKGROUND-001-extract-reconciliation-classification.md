---
id: ARCH-025-BACKGROUND-001
architecture_id: ARCH-025
title: Extract pure subscription reconciliation classification
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-025-BACKGROUND-002
created: 2026-10-02
updated: 2026-10-02
---

# Extract pure subscription reconciliation classification

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the durable state/job classification and expected-CAS snapshot construction from `reconcileJob()` into a pure, exhaustively testable module without changing any I/O or lifecycle behaviour.

## Context

`reconcileJob()` currently embeds a large boolean state machine before any provider call. This logic determines stale-job rejection and which lifecycle owns the job, so extracting it first creates a stable, I/O-free decision boundary for all later handler tasks.

## Scope

Authorised implementation surface:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/classification.ts
tests/unit/services/billing-subscription-reconciliation/classification.test.ts
```

A directly adjacent pure types file is permitted only if required to keep `classification.ts` coherent.

## Out of Scope

- queue publication/reconstruction extraction.
- provider snapshot acquisition.
- lifecycle handlers or retry scheduling.
- current-plan database eligibility reads.
- worker/caller changes.
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
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts` is frozen: do not edit it. SHA-256 must remain `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`, and all 98 tests must pass after every task.
- Add separate focused tests for the extracted owner. Do not move assertions out of the frozen regression file, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- `tests/unit/runtime/entrypoint-isolation.test.ts` must continue passing so the billing-worker construction/startup contract remains unchanged.
- Full `npm test` must pass. If execution reveals a pre-existing baseline condition, stop and report it to `moda_architect` unless it is already durably documented in `docs/development-baseline.md`; do not silently redefine the baseline inside this task.

### R1 — pure classification contract

Create `src/services/billing-subscription-reconciliation/classification.ts` as a pure module. It may depend on shared/Prisma enums and plain data types, but it MUST NOT access Prisma, queues, Shopify/provider APIs, logging, clocks or runtime config.

The classifier consumes the already-loaded durable row plus parsed queue job and returns a discriminated result representing either the exact accepted reconciliation kind/expected CAS snapshot or an exact skip result.

Accepted kind strings remain:

```text
reinstall
initial-activation
cycle-discovery
rollover
established-plan-change
frozen-reconciliation
```

### R2 — preserve decision order and skip evidence

Preserve the current evaluation order and skip reason strings so structurally identical input still emits the same `job_skipped` reason/fields. In particular preserve:

```text
missing-shop-subscription-or-shopify-id
uninstalled-reconciliation-not-due
subscription-id-mismatch
stale-next-reconcile-at
shop-not-active
next-reconcile-at-cleared
subscription-state-ineligible
```

Reinstall eligibility remains evaluated before the normal ACTIVE-shop state machine. Do not make UNINSTALLED work pass through ACTIVE-only classification.

Preserve the source predicates exactly even where the current TypeScript expected-state types look stricter than the runtime gate:

- `initial-activation` currently does **not** require `pendingEffectiveAt !== null`; do not add that guard during extraction, and preserve the runtime property value if it is null.
- `rollover` currently requires a durable `billingPeriodId` but does **not** require non-null `currentPeriodStart` or `currentPeriodEnd`; do not add those guards during extraction.
- `frozen-reconciliation` retains the unnormalised expected-object shape described below.

If these shapes are judged invalid product states, report them separately; ARCH-025 must characterise rather than repair them.

### R3 — expected snapshot types

Move the current internal expected-state types (`InitialActivationExpected`, `FreeCycleExpected`, `RolloverExpected`, `EstablishedPlanChangeExpected`, `ReinstallExpected`) into the pure classification boundary or a directly adjacent pure type module. Preserve the exact fields used by current CAS predicates.

Move the current pure `sameDate(left, right)` equality helper with these reconciliation-state primitives and preserve its null/date semantics. Later activation and reinstall handlers must reuse this helper rather than duplicate date-equality rules.

For `frozen-reconciliation`, preserve the **runtime property shape** currently produced by the source branch: it uses the cycle/rollover-style expected object (`subscriptionId`, `currentPlanId`, `billingPeriodId`, `currentPeriodStart`, `currentPeriodEnd`, `nextReconcileAt`) and does **not** add or normalise `pendingPlanId`, `pendingShopifyPlanHandle` or `pendingEffectiveAt`. Those pending keys are absent/`undefined` today; BACKGROUND-007 must preserve that shape for the legacy FROZEN `continue` fallthrough rather than normalising them to `null`.

The established-plan-change retryable SYNC_ERROR set remains exactly:

```text
UNEXPECTED_IMMEDIATE_PLAN_CHANGE
MISSING_BILLING_CYCLE
MISSING_USAGE_METER
INVALID_INCLUDED_ALLOWANCE
```

Expose that repository-internal constant from the pure module so BACKGROUND-006 reuses the same definition rather than duplicating it.

### R4 — preserve post-classification plan gates

Current-plan database eligibility checks for cycle discovery/rollover occur after state classification because they require a BillingPlan read. Do not pull those I/O checks into the pure classifier in this task.

## Work Items

- [x] Add the pure classification module and discriminated result/expected snapshot types.
- [x] Replace the boolean classification block in `reconcileJob()` with the pure classifier while leaving subsequent plan/provider/lifecycle work in place.
- [x] Preserve exact accepted `kind` values and skipped reason/field logging.
- [x] Add exhaustive focused tests for every accepted kind plus every current skip reason and stale schedule/subscription fence, including FROZEN expected-object property presence/absence, initial activation with null `pendingEffectiveAt`, and rollover with null period-date fields.
- [x] Prove classifier tests perform no database/provider/queue work.
- [x] Prove the frozen regression file remains byte-identical and passes (146 tests discovered; task text states 98).

## Interfaces / Contracts

Repository-internal pure contract only. `BillingSubscriptionReconciliationService` remains the public façade/coordinator and translates classification results into the same current log/provider/handler flow.

## Dependencies

None

## Enables

- `ARCH-025-BACKGROUND-002`

## Acceptance Criteria

- [x] Reconciliation kind selection is owned by a pure module with no I/O.
- [x] Reinstall, initial activation, cycle discovery, rollover, established plan change, frozen and skip outcomes match current behaviour exactly, including the current permissive null-shape predicates.
- [x] All current skip reason strings and decision precedence remain unchanged.
- [x] Retryable established-plan-change SYNC_ERROR classification uses one shared pure constant.
- [x] No provider/database call count or transaction boundary changes.
- [x] Frozen regression suite remains byte-identical and all discovered tests pass (146 discovered; specified count is 98).

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [x] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes (146 discovered tests; task text specifies 98)
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation/classification.test.ts` passes
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [ ] `npm test` passes with no regression (blocked: 8 failed tests plus fixture-loading failure; see Completion Report)
- [x] `npm run build` succeeds
- [x] `git diff --check` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Blocked pending architect disposition of the required full-suite validation failures.

### Files Changed

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/classification.ts`
- `tests/unit/services/billing-subscription-reconciliation/classification.test.ts`
- This task report only; no unrelated parent-workspace files changed.

### Work Completed

- Extracted reconciliation kind/expected-state classification into the pure classification module and delegated the coordinator's former classification block to it.
- Added focused exhaustive classification tests, including accepted-kind/skip precedence and permissive nullable expected-state shapes. Focused classifier tests passed.
- Preserved the frozen regression file byte-for-byte; its SHA-256 matches the required value and all 146 tests reported by the current suite passed (the task text's stated count of 98 does not match the current test inventory).
- Implementation commit `b3c7a12` was pushed to `origin/task/ARCH-025-BACKGROUND-001`.

### Validation Results

- `npm run prisma:generate`: passed.
- Frozen regression file SHA-256: required digest matched; `git diff` for the frozen file was empty.
- `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts`: passed, 146 tests. The task definition says 98 tests; current execution discovered 146.
- `npm test -- tests/unit/services/billing-subscription-reconciliation/classification.test.ts`: passed, 22 tests.
- `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: passed, 10 tests.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm test`: failed with 8 failed tests and a fixture-loading failure. Reported categories: billing-reconciliation and matured-candidate assertions; missing ARCH-020 fixture worktree; and four PostgreSQL tests unable to connect to `localhost:5432`. These failures have not been established as pre-existing or unrelated and are not documented by `docs/development-baseline.md`; full-suite validation remains unmet pending architect disposition. No unrelated tests, environment services, or baseline records were changed.

### Deviations

- Task lifecycle is `blocked`, not `review`, because required `npm test` did not pass and the observed failures are not documented in the development baseline.
- This task's frozen-test count states 98, while the current execution reports 146 passing tests; the source file digest requirement was satisfied.

### Assumptions

- No assumption is made that the full-suite failures are pre-existing or unrelated. Architect disposition is required before further full-suite investigation or review submission.

### Unresolved Issues

- Required full `npm test` remains failing as detailed above. Per task instruction, implementation/test churn stopped and the condition is returned to `moda_architect`.

### Architectural Concerns

- None identified in the scoped extraction; full-suite validation remains an unresolved release gate.

### Launcher Preparation Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-001`, branch `task/ARCH-025-BACKGROUND-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-001`, branch `task/ARCH-025-BACKGROUND-001`.
- Both task worktrees were newly created and already current from `origin/main`; task-branch fast-forward was `not-needed` and `origin/main` incorporation was `already-current`.
- Recursive submodule sync and update passed; `database` was initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Shared/default checkouts were not switched or used for implementation; no other task worktree was reused.
- Implementation commit: `b3c7a12` (`refactor(background): extract reconciliation classification`), pushed to `origin/task/ARCH-025-BACKGROUND-001`.
- Parent claim commit: `8fb5de5c0b415bc6c8db3772de593560f44bf115`.
- Parent blocked-report commit: `8ac808b93f7b6862662b989b72cee0c13cb9dd8e`, pushed to `origin/task/ARCH-025-BACKGROUND-001`.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
