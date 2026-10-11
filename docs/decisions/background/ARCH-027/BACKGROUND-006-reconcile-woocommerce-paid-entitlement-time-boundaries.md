---
id: ARCH-027-BACKGROUND-006
architecture_id: ARCH-027
title: Reconcile WooCommerce paid-entitlement time boundaries
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-027-BACKGROUND-002
enables: []
created: 2026-10-06
updated: 2026-10-11
---

# Reconcile WooCommerce paid-entitlement time boundaries

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Reconcile **time-driven** Woo paid-entitlement boundaries from Moda's exact `EVERY_30_DAYS` cadence and the durable provider-coverage projection established by BACKGROUND-002, without charging money, calling Woo, accumulating missed grants, or creating another worker deployment.

## Context

ARCH-027 intentionally separates two clocks:

```text
Woo financial clock
    provider charges / proration / next_payment_date / cancellation end

Moda entitlement clock
    exact 30-day included-recovery allowance windows
```

`Subscription.providerCoverageEndAt` is the durable financial-coverage fence. `Subscription.currentPeriodEnd` is the Moda allowance boundary. They may differ substantially.

The existing Background billing runtime already owns leased periodic reconciliation. This task reuses that runtime; no Gateway/Render service/cron is added.

`ARCH-027-BACKGROUND-003` remains superseded and is not the executable owner of this behavior.

## Scope

Modify only `moda-interact-background` implementation/tests required to add bounded due-work reconciliation for Woo paid Subscriptions to the existing leased billing-worker cycle.

The task owns three time-driven outcomes:

1. exact-30-day allowance rollover while verified provider coverage permits it;
2. fail-closed `ACTIVE -> FROZEN` when non-canceled provider coverage expires without newer verified evidence;
3. scheduled-cancellation finalization at the verified provider coverage/end deadline when `prepaid_term_ended` was delayed or lost.

## Out of Scope

- Woo provider network calls.
- Provider webhook parsing/causal reconciliation; BACKGROUND-002 owns it.
- Provider charges/refunds.
- Top-up acquisition/refund lifecycle.
- Shopify billing-period cadence changes.
- A new worker, queue, cron or Gateway deployment.
- Catch-up credit accumulation.
- Domain `_index.md` or architecture-index updates.

## Requirements

### R1 — Reuse the existing leased billing worker

Add the bounded due-work query/reconciliation to the accepted billing worker/scheduler. Do not add an independently deployed worker or scheduler.

### R2 — Candidate selection is provider/tenant bounded

Select only WooCommerce Shops with a current paid recurring Subscription requiring time reconciliation. The exact repository query may be optimized, but must be bounded/index-supported and must not scan/process Shopify as Woo.

Candidate causes include:

```text
currentPeriodEnd <= now
providerCoverageEndAt <= now
```

Use narrow Shop/Subscription locking and re-read the row after lock before deciding.

### R3 — Exact-30-day cadence derives from the established Moda boundary

For a covered ACTIVE paid Woo Subscription whose current entitlement period is due:

```text
next theoretical start = previous currentPeriodEnd
next theoretical end   = previous currentPeriodEnd + exact 30 days
```

Do not derive the allowance boundary from Woo `next_payment_date`, calendar-month arithmetic or worker run time.

### R4 — Open at most the currently applicable covered window

When reconciliation runs after one or more theoretical boundaries:

- do not create historical skipped grants one by one;
- do not accumulate unused missed allowances;
- advance the theoretical 30-day cadence to the single window containing `now`;
- open/grant only that current window when verified provider coverage proves entitlement for it.

Existing prior periods are closed through the accepted close invariants.

### R5 — Provider coverage gates every new paid included grant

A successor allowance may open only when the locked Subscription has durable verified provider coverage for the relevant time.

If:

```text
cancelAtPeriodEnd = false
providerCoverageEndAt <= now
no newer verified evidence has been projected
```

then fail closed:

```text
Subscription.status = FROZEN
no new included allowance
```

Do not invent future coverage. A later valid BACKGROUND-002 renewal may restore ACTIVE/extend coverage; a subsequent run then opens at most the current theoretical window.

### R6 — Scheduled cancellation remains paid until the provider end

If:

```text
cancelAtPeriodEnd = true
now < providerCoverageEndAt
```

then the merchant remains on the paid plan. If an exact-30-day allowance boundary occurs before the prepaid end and coverage proves that window, normal rollover is allowed.

### R7 — Scheduled cancellation deadline is a terminal safety net

If:

```text
cancelAtPeriodEnd = true
providerCoverageEndAt <= now
```

perform the same idempotent terminal paid -> Free projection defined by BACKGROUND-002:

```text
close/truncate current paid BillingPeriod with CONTRACT_ENDED semantics
Subscription.status = ACTIVE
Subscription.planId = existing Free BillingPlan
Subscription.providerSubscriptionId = NULL
Subscription.providerCoverageEndAt = NULL
Subscription.billingPeriodId = NULL
Subscription.currentPeriodStart = NULL
Subscription.currentPeriodEnd = NULL
Subscription.cancelAtPeriodEnd = false
```

Preserve onboarding, lifetime-Free, purchased, promotional and history state. Never recreate/reset lifetime-Free credits.

A later `prepaid_term_ended` receipt is then an idempotent historical/no-op for current state.

### R8 — Plan switches do not reset cadence

Always use the current locked paid plan to set the successor period's `currentAllowanceQuantity`, but preserve the existing cadence established by prior `currentPeriodEnd`. A plan switch never re-anchors the 30-day clock.

### R9 — Recovery resume occurs after durable entitlement commit

When a new paid allowance becomes available or FROZEN is cleared by separately reconciled provider evidence, invoke the accepted recovery-capacity resume path only after the entitlement transaction commits, preserving existing idempotency/ordering behavior.

### R10 — No provider/network correctness dependency

This task consumes only durable Moda/provider projection state. It performs zero Woo network calls and does not parse raw webhook payloads.

### Maintainability — bounded production modules

ARCH-027 must not extend the existing Background monoliths or create another catch-all service. For production source introduced or materially expanded by this task:

- target **<= 200 physical lines per new production file**;
- **300 physical lines is a hard ceiling** for a new production file;
- an existing production file already over 300 lines may receive only thin integration/composition changes required to delegate into focused modules;
- substantive new reconciliation, policy, evidence parsing, persistence/accounting or provider-specific mechanics must live in bounded focused modules with independently testable responsibilities;
- do not evade the rule by moving several unrelated responsibilities into one dense file just below the ceiling;
- cohesive test files are exempt from the production-source line ceiling when keeping the behavioural matrix together is clearer.

## Work Items

- [x] Keep ARCH-027 production implementation modular: new production files target <= 200 lines and never exceed 300; add only thin wiring to existing >300-line production files and extract substantive new behaviour into focused modules.
- [x] Add bounded/index-supported Woo paid-entitlement due-work selection to the existing billing worker.
- [x] Re-read/lock Shop + Subscription before every time-driven transition.
- [x] Implement exact `previousPeriodEnd + 30 days` theoretical cadence.
- [x] Implement single-current-window catch-up with no accumulated skipped grants.
- [x] Gate new allowance on durable `providerCoverageEndAt`.
- [x] Implement expired non-canceled coverage -> FROZEN/no grant.
- [x] Implement scheduled-cancellation rollover before provider end.
- [x] Implement scheduled-cancellation deadline -> idempotent Free/CONTRACT_ENDED transition.
- [x] Preserve plan-switch usage/cadence semantics.
- [x] Wire recovery-capacity resume after durable commit where newly available capacity requires it.
- [x] Add focused boundary/race/idempotency tests.

## Interfaces / Contracts

Consumes the durable projection owned by BACKGROUND-002/DATABASE-001:

```text
Subscription.status
Subscription.planId
Subscription.providerSubscriptionId
Subscription.providerCoverageEndAt
Subscription.cancelAtPeriodEnd
Subscription.billingPeriodId
Subscription.currentPeriodStart
Subscription.currentPeriodEnd
BillingPeriod
BillingPeriodEntitlementCounter
```

No cross-service queue/API contract is introduced.

## Dependencies

- `ARCH-027-BACKGROUND-002`

BACKGROUND-002 must be architect-accepted Complete before this task becomes Ready.

## Enables

None.

This task is an independent implementation branch in the ARCH-027 terminal dependency set. It does not gate BACKGROUND-004/005.

## Acceptance Criteria

- [x] No new ARCH-027 production file exceeds 300 physical lines; new files normally remain <= 200 lines, and any existing >300-line production file changed by this task contains only bounded integration/composition changes rather than substantive new domain logic.
- [x] No new worker/cron/queue/Gateway deployment is introduced.
- [x] Only Woo paid Subscriptions are processed by this reconciliation path.
- [x] Successor entitlement cadence is derived from the previous Moda boundary using exact 30-day durations.
- [x] Woo `next_payment_date` never becomes `currentPeriodEnd`.
- [x] A normal covered boundary opens exactly one currently applicable entitlement window/full current-plan allowance.
- [x] Multiple skipped theoretical windows during FROZEN/uncovered time do not create accumulated grants.
- [x] Expired non-canceled provider coverage fails closed to FROZEN and grants no new paid allowance.
- [x] Later provider coverage restoration opens at most the currently applicable theoretical window, not historical catch-up grants.
- [x] Scheduled cancellation before provider end remains paid and may receive a normal due allowance window when coverage permits it.
- [x] Scheduled cancellation at/after provider end transitions idempotently to existing Free and closes/truncates the paid period with CONTRACT_ENDED semantics.
- [x] Lifetime-Free credits are never recreated/reset during terminal transition.
- [x] Current plan at rollover sets current allowance without resetting cadence/previous usage history incorrectly.
- [x] Recovery resume happens only after durable entitlement commit.
- [x] No Woo network call/raw webhook parsing occurs.
- [x] Repeated/concurrent worker runs are idempotent.

## Validation

Required focused validation categories:

- [x] exact-30-day normal rollover test (focused unit suite);
- [x] provider next-payment date different from allowance boundary test (focused unit suite and disposable PostgreSQL test added);
- [x] plan switch without cadence reset test (focused unit suite);
- [x] expired provider coverage -> FROZEN/no grant test (focused unit suite);
- [x] restored coverage after >1 missed theoretical period -> one current-window grant test (focused unit suite);
- [x] scheduled cancellation with allowance boundary before provider end -> normal rollover test (focused unit suite);
- [x] scheduled cancellation deadline without prepaid_term_ended -> Free/CONTRACT_ENDED test (focused unit suite and disposable PostgreSQL test added);
- [ ] late prepaid_term_ended after local terminal transition -> idempotent no-op integration test where practical (test added; not executed because the approved local `moda_interact` database endpoint is unavailable);
- [x] concurrent/duplicate worker reconciliation idempotency test (serialized unit race; PostgreSQL concurrency test added but not executable in this environment);
- [x] targeted TypeScript typecheck; repository has no package lint script for this package;
- [x] `git diff --check`;
- [x] dedicated parent/implementation worktrees and start-of-attempt synchronization confirmed by the prepared launcher packet; parent claim and implementation task branch pushed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and STOP. Do not begin another ARCH-027 task.

## Implementation Notes

Prefer a thin entitlement-boundary coordinator with separate focused modules for candidate selection, exact-30-day window calculation/coverage policy and transactional period/counter transition. Reuse the existing leased billing worker only as scheduling/composition infrastructure.

Prefer adding one bounded reconciler to the existing leased billing worker composition. Do not recreate provider receipt interpretation here. If implementation discovers that `providerCoverageEndAt` cannot be queried efficiently with the accepted schema/indexes, return the database gap to `moda_architect` rather than adding cross-repository schema changes from this task.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation (`moda-interact-background`):

- `src/entrypoints/billing.ts`
- `src/services/woocommerce-billing/paid-entitlement-time-reconciliation.service.ts`
- `src/services/woocommerce-billing/paid-entitlement-transition.ts`
- `src/services/woocommerce-billing/paid-entitlement-window.ts`
- `src/services/woocommerce-billing/subscription-period-activation.ts`
- `src/services/woocommerce-billing/subscription-period-projection.ts`
- `src/services/woocommerce-billing/subscription-receipt-processor.ts`
- `src/services/woocommerce-billing/subscription-receipt-reconciliation.service.ts`
- `src/services/woocommerce-billing/subscription-transition.service.ts`
- `tests/unit/services/woocommerce-billing/paid-entitlement-time-reconciliation.test.ts`
- `tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts`

Parent task report: this task file's Work Items, Validation, execution metadata and Completion Report. `## Architect Review` was not changed.

### Work Completed

- Added bounded Woo-only time reconciliation to the existing leased billing cycle. Candidate selection uses indexed `nextReconcileAt` and `providerCoverageEndAt` fields, with bounded cursor-based seeding for legacy rows that lack `nextReconcileAt`; it does not query the unindexed `currentPeriodEnd` column.
- Added Shop then Subscription row locks and re-read before deciding each transition.
- Added exact 30-day Moda window arithmetic, single-current-window catch-up, provider-coverage gating, fail-closed expiry freezing, and scheduled-cancellation terminal projection through the existing close/accounting helper.
- Preserved cadence across plan changes and applied the current paid plan allowance to the successor counter.
- Scheduled recovery-capacity resume after committed rollover and after a receipt transaction restores a FROZEN paid Woo projection with future verified coverage.
- Added focused unit behavior coverage and disposable PostgreSQL concurrency/late-receipt scenarios.
- New production modules are 31, 121 and 136 lines respectively; existing billing entrypoint and receipt processor received composition/boundary wiring only.

### Validation Results

- `node_modules/.bin/vitest run tests/unit/services/woocommerce-billing/paid-entitlement-time-reconciliation.test.ts`: 11 tests passed.
- `node_modules/.bin/vitest run tests/unit/services/woocommerce-billing`: 6 files, 40 tests passed.
- `node_modules/.bin/tsc --noEmit --pretty false`: passed.
- Strict direct TypeScript check of the changed unit/integration test files with `--ignoreConfig`: passed.
- `git diff --check`: passed.
- Disposable PostgreSQL run was attempted with `TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact` and `MODA_DISPOSABLE_INTEGRATION=1`. It could not connect to `localhost:5432`; all 8 integration cases stopped during fixture setup before exercising transitions. The running local PostgreSQL containers use databases `postgres` and `moda_test_76f0aee14472`, neither the task-approved `moda_interact` database, so they were not used for destructive fixture tests.
- Workspace doctor reported an unrelated existing `moda-interact-admin` direct-Zod declaration failure; no Admin files were changed.

### Deviations

- Live PostgreSQL concurrency and late-receipt integration scenarios were added but could not be executed because the approved local database endpoint is unavailable. This is recorded as a validation limitation for Architect review.

### Assumptions

- BACKGROUND-002 has already established the accepted evidence-derived provider coverage projection.
- The existing `Subscription.nextReconcileAt` and `Subscription.providerCoverageEndAt` indexes are sufficient for due selection; legacy null scheduler rows are seeded in bounded batches through the indexed coverage field without a schema change.

### Unresolved Issues

- Live PostgreSQL integration evidence remains outstanding until `localhost:5432/moda_interact` is available.

### Architectural Concerns

- None identified. No schema, migration, worker deployment, queue contract, provider call or cross-repository change was introduced.

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

Pending implementation.

### Follow-up

None.
