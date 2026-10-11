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
attempt: 2
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
- [x] late prepaid_term_ended after local terminal transition -> idempotent no-op (disposable PostgreSQL integration suite passed 8/8 on 2026-10-11);
- [x] concurrent/duplicate worker reconciliation idempotency test (serialized unit race and disposable PostgreSQL concurrency suite passed 8/8 on 2026-10-11);
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

Ready for Review — Attempt 2. Developer-executed validation on 2026-10-11 resolved the earlier test-environment blocker: A1-R1 focused failure-isolation tests passed 4/4, A1-R2 disposable PostgreSQL integration tests passed 8/8, and A1-R3 worktree preparation evidence is recorded below. No further production source changes were required after the Attempt 2 correction.

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
- `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts` (Attempt 2)

Parent task report: this task file's Work Items, Validation, execution metadata and Completion Report. `## Architect Review` was not changed.

### Work Completed

- Added bounded Woo-only time reconciliation to the existing leased billing cycle. Candidate selection uses indexed `nextReconcileAt` and `providerCoverageEndAt` fields, with bounded cursor-based seeding for legacy rows that lack `nextReconcileAt`; it does not query the unindexed `currentPeriodEnd` column.
- Added Shop then Subscription row locks and re-read before deciding each transition.
- Added exact 30-day Moda window arithmetic, single-current-window catch-up, provider-coverage gating, fail-closed expiry freezing, and scheduled-cancellation terminal projection through the existing close/accounting helper.
- Preserved cadence across plan changes and applied the current paid plan allowance to the successor counter.
- Scheduled recovery-capacity resume after committed rollover and after a receipt transaction restores a FROZEN paid Woo projection with future verified coverage.
- Added focused unit behavior coverage and disposable PostgreSQL concurrency/late-receipt scenarios.
- Attempt 2 added an isolated failure boundary around the Woo paid-entitlement batch. Batch failure emits a structured bounded error with lease generation and config version, does not emit a success event, and does not prevent the existing global-scan reporting, promotion expiry, refund correction, reconstruction or cycle-completed phases from running. Successful reconciliation retains its completion event.
- Added focused success/failure coordinator coverage in `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts`.
- New production modules are 31, 121 and 136 lines respectively; existing billing entrypoint and receipt processor received composition/boundary wiring only.

### Validation Results

- `node_modules/.bin/vitest run tests/unit/services/woocommerce-billing/paid-entitlement-time-reconciliation.test.ts`: 11 tests passed.
- `node_modules/.bin/vitest run tests/unit/services/woocommerce-billing`: 6 files, 40 tests passed.
- `node_modules/.bin/tsc --noEmit --pretty false`: passed.
- Strict direct TypeScript check of the changed unit/integration test files with `--ignoreConfig`: passed.
- `git diff --check`: passed.
- Attempt 1 PostgreSQL run attempted the approved `localhost:5432/moda_interact` endpoint and stopped during fixture setup; this historical blocker was resolved by the later Attempt 2 disposable-harness run recorded below. No unrelated existing database was used.
- Workspace doctor reported an unrelated existing `moda-interact-admin` direct-Zod declaration failure; no Admin files were changed.
- Attempt 2 editor diagnostics: no errors reported for `src/entrypoints/billing.ts` or `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts`.
- Attempt 2 `git diff --check`: passed.
- Attempt 2 focused validation: `npm test -- tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts` passed **4/4** with Vitest 4.1.11, exit code **0** (developer output, 2026-10-11). Includes Woo receipt success/failure isolation and Woo paid-entitlement success/failure isolation; a rejected entitlement scan logs a failure and subsequent billing phases still execute.
- The earlier agent-shell Node-bootstrap failure was not reproduced in the developer's terminal. Developer checks on 2026-10-11 confirmed the primary workspace and parent task worktree `.nvmrc` both specify **24.19.0**; Node **v24.21.0** and `/usr/bin/tr` are available in the parent and implementation task worktrees. Local Prisma **6.19.3** is installed. No `.nvmrc` changes or global Prisma installation were needed. The version difference is recorded, not presented as a test failure.
- Attempt 2 integration validation: `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` passed **8/8**, 1 test file, with Vitest 4.1.11 (developer output, 2026-10-11). The repository wrapper `scripts/test-integration.mjs` invokes the approved disposable PostgreSQL 17 infrastructure (`pgvector/pgvector:pg17`), uses `database/prisma/schema.prisma` for migration deployment, and runs Vitest with `MODA_DISPOSABLE_INTEGRATION=1`. Successful completion was reported; an explicit numeric exit code and generated database URL were not included in the pasted output. An earlier direct `node scripts/test-integration.mjs` failed before tests with `spawn prisma ENOENT`; invoking the declared npm script resolved executable lookup without source changes.

### Deviations

- Attempt 1 required-PostgreSQL-endpoint validation was blocked by local environment configuration; Attempt 2 instead ran the repository-approved disposable PostgreSQL harness successfully (8/8). No unrelated existing database was repurposed.
- An initial direct Node invocation could not resolve the local Prisma executable; executing via npm fixed PATH resolution. The agent's original missing-Node/`tr`/empty-`.nvmrc` report did not describe the later verified developer terminal environment. Both outstanding runtime validations have now passed.

### Assumptions

- BACKGROUND-002 has already established the accepted evidence-derived provider coverage projection.
- The existing `Subscription.nextReconcileAt` and `Subscription.providerCoverageEndAt` indexes are sufficient for due selection; legacy null scheduler rows are seeded in bounded batches through the indexed coverage field without a schema change.

### Unresolved Issues

- No outstanding A1-R1/A1-R2 test failures are reported. Both developer test runs passed. The pasted integration output does not separately print a numeric process exit code or the generated disposable database URL; source-verified harness configuration and complete passing Vitest output are recorded above.

### Architectural Concerns

- None identified. No schema, migration, worker deployment, queue contract, provider call or cross-repository change was introduced.

### Attempt 2 Architect Correction Disposition

- **A1-R1 — implemented and validated (4/4 PASS).** Changed `src/entrypoints/billing.ts` and `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts`. Entitlement batch errors emit `billing.woocommerce.paid_entitlement.reconciliation_failed` through `@modainteract/moda-interact-shared/logging` with bounded error metadata, lease generation and config version; later billing phases continue. The focused test passed with exit code 0 and checks success-only completion reporting.
- **A1-R2 — validated (8/8 PASS).** Ran the approved PostgreSQL integration through `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` from the implementation task worktree. The wrapper supplies isolated PostgreSQL 17, Prisma migrations and `MODA_DISPOSABLE_INTEGRATION=1`. All eight cases passed, including concurrency, time boundaries, cancellation, later renewal and historical/contradictory evidence handling. No shared database was retargeted. The explicit process exit code and generated database URL are not present in the provided terminal excerpt.
- **A1-R3 — implemented from the Attempt 2 launcher packet.** Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace` (not derived from a previous task worktree). Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-BACKGROUND-006`, branch `task/ARCH-027-BACKGROUND-006`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-BACKGROUND-006`, branch `task/ARCH-027-BACKGROUND-006`. Both were reused as the exact task worktrees; neither was a foreign task worktree. No source edits were made in the shared/default checkout. Parent synchronization: remote task fast-forward `not-needed`; `origin/main` incorporation `already-current`; packet head `4615fb4c1f69ca74cb474167852770d3bfadfc0b`. Implementation synchronization: remote task fast-forward `not-needed`; `origin/main` incorporation `already-current`; packet head `9377839ec1a0b4b538709d05ce5347efa07ad16c`. Recursive submodule sync and update both passed; `database` was initialized at the branch-recorded gitlink `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`. Before the successful claim, the nested checkout was aligned from the old clean commit `7e0dcebd6216a886d29e226ba1d9c63da204053e` to that already-recorded gitlink; no database source or gitlink change was made. Attempt 2 claim commit `9b42ba6a2da6851c66487528ee74f6978149c054` was committed and pushed. Source changes remain confined to the implementation task worktree; the parent task report is confined to the parent task worktree.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-11)

### Review Notes

The implementation follows the approved high-level Woo entitlement-time design: one bounded leased billing-worker path, Woo-only paid-subscription selection, Shop-then-Subscription locking, exact 30-day window arithmetic, nonaccumulating catch-up, durable provider coverage gating, scheduled-cancellation termination via the accepted paid-period close helper, and post-commit recovery resume. No new deployable worker, schema change, provider call or queue contract was introduced.

Implementation commit `7b8582445f19cfa293f84f1203ab94c8cdc013aa` and parent report commit `0a4959ae8a81b5378853951053940454d8c26199` were verified as the published task-branch heads. Selected source, test and task-document Git blob hashes in the submitted snapshot match those branches. Local worktree cleanliness/physical execution could not be independently observed from this review environment.

**A1-R1 — Billing-cycle failure isolation (source/test correction required).** `src/entrypoints/billing.ts` awaits `wooPaidEntitlementTimeReconciliationService.reconcileOnce(...)` outside a failure boundary. A rejected due-candidate database query or other batch-level failure escapes `runBillingCycle` before the existing global-scan completion log, promotion selection expiry, refund correction, subscription queue reconstruction and cycle completion. This creates an avoidable shared-worker operational dependency. The pre-existing Woo receipt path already isolates an equivalent Woo-specific scan failure.

Correction contract:

- Isolate exceptions from the Woo entitlement batch within the existing billing-cycle orchestration, using the shared structured logger with bounded error metadata and the lease/config identifiers.
- Preserve success reporting, the existing candidate-level per-shop failure handling, leased scheduling, and business semantics. Do not mask a failed Woo scan as a successful Woo completion.
- Allow subsequent, otherwise-independent billing-cycle phases to execute even when the Woo entitlement candidate selection rejects. Do not add a new worker or move business logic into the entrypoint.
- Add a focused regression proving rejected Woo entitlement scan -> failure log -> later promotion-expiry/refund/reconstruction phases still execute; retain the successful-path test.

**A1-R2 — PostgreSQL acceptance evidence (validation correction required; no code change if it passes).** Eight submitted `woocommerce-subscription-reconciliation.concurrency.integration.test.ts` cases were blocked during database setup; no PostgreSQL transaction/race/late-receipt execution was observed. Execute the required suite against a disposable, task-approved database whose URL, schema, migrations and isolation are recorded. Specifically prove concurrent same-window rollover, exact boundary independent of Woo payment date, scheduled-cancellation terminal projection, late prepaid-term receipt idempotency, and no duplicate credit grant. Do not retarget unrelated or shared existing databases. Record command, pass/failure counts, exit status and any failures in the Completion Report. A continuing environment blocker must be reported explicitly; it cannot be counted as a passing test.

**A1-R3 — Worktree evidence completion (report correction required; no code change if execution was conformant).** The submitted Completion Report summarizes a prepared launcher packet but omits the exact mandatory physical paths and explicit per-repository synchronization fields. Record the launcher-resolved canonical workspace root, parent and implementation task worktree paths/branch names, no shared/default checkout mutation, no reused foreign task worktree, each parent and implementation fast-forward/main incorporation result, and recursive implementation-submodule preparation. Reuse the actual prepared packet; do not manufacture evidence. If source execution took place outside the canonical task worktrees, restore the task worktree, rerun required validation and document the correction under `docs/agent-worktree-isolation-policy.md`; source-code churn is not required merely for a new commit.

### Reviewed Files

- `src/entrypoints/billing.ts`
- `src/services/woocommerce-billing/paid-entitlement-time-reconciliation.service.ts`
- `src/services/woocommerce-billing/paid-entitlement-transition.ts`
- `src/services/woocommerce-billing/paid-entitlement-window.ts`
- `src/services/woocommerce-billing/subscription-period-activation.ts`
- `src/services/woocommerce-billing/subscription-period-projection.ts`
- `src/services/woocommerce-billing/subscription-transition.service.ts`
- `src/services/woocommerce-billing/subscription-receipt-processor.ts`
- `src/services/billing-period-transition/{close-billing-period,successor-billing-period}.ts`
- `src/services/billing-reconciliation.service.ts`
- `tests/unit/services/woocommerce-billing/paid-entitlement-time-reconciliation.test.ts`
- `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts`
- `tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts`
- `database/prisma/schema.prisma` (read-only contract inspection)
- `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`
- `docs/agent-worktree-isolation-policy.md`

### Validation Reviewed

- Developer report: Woo billing unit suite 40/40; production typecheck, strict changed-test typecheck and `git diff --check` passed. These were not independently rerun because the uploaded source lacks installed Node/Vitest/Prisma dependencies.
- Developer report: eight PostgreSQL integration cases could not connect to the approved local `moda_interact` test database; not accepted as passing validation.
- Independently inspected due-query, row-lock, period-close, and exception propagation control flow. The batch-level Woo-scan failure-isolation deficiency is directly visible in the changed billing entrypoint.
- Verified six representative uploaded file Git blob hashes against the pushed task branches, including the parent report and integration tests.
- Physical task-worktree isolation and start-of-attempt sync evidence remains incomplete in the submitted Completion Report.

### Architecture Conformance

Partial. The core entitlement-transition design and repository ownership conform to ARCH-027. Billing-cycle fault isolation, PostgreSQL concurrency proof and the mandatory worktree evidence are required before acceptance. No downstream readiness promotion is authorized.

### Follow-up

Return the **same task** to `status: ready`, retain `attempt: 1`, and clear `executor` and `claimed_at`. The next authorized claim becomes Attempt 2. Implement only A1-R1, complete A1-R2/A1-R3, resubmit with the exact validation/launcher evidence, and STOP. No changes to `docs/decisions/**/_index.md` until explicitly requested by the developer.
