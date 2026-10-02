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
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-10-02T20:56:27Z
attempt: 3
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

- [ ] Add the pure classification module and discriminated result/expected snapshot types.
- [ ] Replace the boolean classification block in `reconcileJob()` with the pure classifier while leaving subsequent plan/provider/lifecycle work in place.
- [ ] Preserve exact accepted `kind` values and skipped reason/field logging.
- [ ] Add exhaustive focused tests for every accepted kind plus every current skip reason and stale schedule/subscription fence, including FROZEN expected-object property presence/absence, initial activation with null `pendingEffectiveAt`, and rollover with null period-date fields.
- [ ] Prove classifier tests perform no database/provider/queue work.
- [ ] Prove the frozen 98-test regression file remains byte-identical and passes.

## Interfaces / Contracts

Repository-internal pure contract only. `BillingSubscriptionReconciliationService` remains the public façade/coordinator and translates classification results into the same current log/provider/handler flow.

## Dependencies

None

## Enables

- `ARCH-025-BACKGROUND-002`

## Acceptance Criteria

- [ ] Reconciliation kind selection is owned by a pure module with no I/O.
- [ ] Reinstall, initial activation, cycle discovery, rollover, established plan change, frozen and skip outcomes match current behaviour exactly, including the current permissive null-shape predicates.
- [ ] All current skip reason strings and decision precedence remain unchanged.
- [ ] Retryable established-plan-change SYNC_ERROR classification uses one shared pure constant.
- [ ] No provider/database call count or transaction boundary changes.
- [ ] Frozen regression suite remains byte-identical and all 98 tests pass.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing-subscription-reconciliation.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239'){console.error(h);process.exit(1)};console.log(h)"` prints the expected SHA-256
- [x] `git diff -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation.service.test.ts` passes (146 discovered tests; task text specifies 98)
- [x] `npm test -- tests/unit/services/billing-subscription-reconciliation/classification.test.ts` passes
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes
- [x] `npm test` introduces no new failing test or suite identity relative to durable baseline `ARCH025-BACKGROUND-TEST-001`; Attempt 2 proved the exact same 8 failing tests plus the same fixture-loading failure on the pre-task and submitted commits
- [x] `npm run build` succeeds
- [x] `git diff --check` passes

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 closes A1-R1 and `ARCH-025-BACKGROUND-001` is accepted. The implementation remained unchanged at `b3c7a1264a22baf498b14916a341686a751de869`; Attempt 2 was evidence-only and required no production or test-source correction.

The same-environment differential compared exact pre-task commit `670fbad4d52308c96ef41a6a4d29116f1ad42f1a` with the submitted implementation commit. Both runs used Node `v24.21.0`, identical `package-lock.json` SHA-256 `24b51056b787611cc08f854679c6570ad823c345e03f24101847d7b4829334bc`, and the same dependency tree. Each full-suite run produced the same eight failing test identities plus the same `tests/unit/commerce/evidence.test.ts` fixture-loading failure. The submitted tree differs only by the additional passing focused classifier file/tests. Therefore no full-suite regression was introduced by this extraction.

The scoped implementation remains architecture-conformant: classification is pure and I/O-free, the coordinator retains durable loading and all post-classification plan/provider/lifecycle work, accepted-kind and skip-reason ordering is preserved, the retryable plan-change error set has one pure owner, and the implementation commit changes only the three authorised files.

Architect reconciliation records the proven pre-task full-suite conditions as durable baseline `ARCH025-BACKGROUND-TEST-001` in `docs/development-baseline.md`. This is a no-regression reference, not an instruction to recreate unavailable PostgreSQL or fixture conditions if the development environment is later repaired.

### Reviewed Files

- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/src/services/billing-subscription-reconciliation/classification.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation/classification.test.ts`
- frozen `moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts` identity/evidence
- `docs/decisions/background/ARCH-025/BACKGROUND-001-extract-reconciliation-classification.md`
- `docs/development-baseline.md`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- implementation commit `b3c7a1264a22baf498b14916a341686a751de869`
- pre-task commit `670fbad4d52308c96ef41a6a4d29116f1ad42f1a`
- Attempt 2 report commit `080c4070134b3a2191a893f865815379eea1b7cf`

### Validation Reviewed

- Frozen reconciliation SHA-256 remained `0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239`; file diff was empty.
- Frozen reconciliation suite passed all 146 tests on the submitted tree.
- Focused classifier suite passed 22 tests.
- Billing entrypoint-isolation suite passed 10 tests.
- `npm run prisma:generate`, production build and `git diff --check` passed.
- Full pre-task suite: eight failing tests plus one suite-loading failure; 1,392 passed / 38 skipped.
- Full submitted suite: the same eight failing tests plus the same suite-loading failure; 1,414 passed / 38 skipped. The additional passes are the focused classifier coverage.
- Four translation-enum integration failures reported the same `Can't reach database server at localhost:5432` error on both commits.
- The commerce evidence suite reported the same missing ARCH-020 fixture path on both commits.
- The three billing-reconciliation assertions and one matured-candidate assertion had identical expected/actual differences on both commits.
- Physical worktree, dependency, temporary baseline-worktree cleanup and clean/pushed evidence are recorded in the Attempt 2 Completion Report.

### Architecture Conformance

Conforms to ARCH-025, the authorised Background repository/file boundary, pure-classification extraction contract, public coordinator compatibility and no-regression requirement as reconciled by durable baseline `ARCH025-BACKGROUND-TEST-001`.

### Follow-up

`ARCH-025-BACKGROUND-002` is now Ready. BACKGROUND-003..007 remain Pending behind the sequential reconciliation chain. The independent BACKGROUND-008 and ADMIN-001 frontiers are unchanged. No further BACKGROUND-001 implementation work is required.

## Developer Override - Reopen (2026-10-02)

- Previous accepted attempt: 2.
- Reason: The developer requested reopening after the BACKGROUND-002 launcher reported this dependency as `ready` despite the accepted/completed record on this task branch. Reopen this prerequisite to reconcile its lifecycle state before continuing the dependent sequence; no implementation correction was specified.
- Historical Architect acceptance and Attempt 2 evidence are preserved above. This reopen does not claim the task or increment the attempt.
