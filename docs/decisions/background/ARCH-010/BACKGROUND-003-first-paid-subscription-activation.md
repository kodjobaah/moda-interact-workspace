---
id: ARCH-010-BACKGROUND-003
architecture_id: ARCH-010
title: Reconcile first paid activation and create the first paid period
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
executor: null
claimed_at: null
priority: 43
attempt: 5
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-BACKGROUND-001
- ARCH-010-BACKGROUND-007
- ARCH-010-SHARED-008
- ARCH-007-BACKGROUND-008
enables:
- ARCH-010-BACKGROUND-006
- ARCH-010-BACKGROUND-010
- ARCH-010-SHOPIFY-003
created: 2026-09-11
updated: 2026-09-13
---

# ARCH-010-BACKGROUND-003: Reconcile first paid activation and create the first paid period

## Objective

Extend the ARCH-010 subscription-reconciliation path so `NO_CONTRACT + pending paid plan` can become a fully usable first paid subscription only after Shopify confirms the paid plan as current **and** supplies an exact current billing cycle.

Reuse the queue/consumer/runtime created by `ARCH-010-BACKGROUND-001`; do not create another queue or Render worker.

## Inspect before editing

```text
src/entrypoints/billing.ts
src/entrypoints/billing-resources.ts
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/runtime/billing-scheduler.ts
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
package.json
```

Read the implemented ARCH-010-BACKGROUND-001 code before editing. Its exact service/file decomposition is authoritative if names differ from the portable task definition.

## Applicable source state only

This task handles initial paid activation when durable state indicates:

```text
Shop.status = ACTIVE
ShopSettings.onboardingCompleted = false
Subscription is NO_CONTRACT initial activation state
pendingPlanId/pendingShopifyPlanHandle identify an active local PAID_METERED BillingPlan
nextReconcileAt matches the queued job
```

Do not use this path for an already-active Free/Paid subscription changing plan. Upgrade/downgrade is a later ARCH-010 transition.

## Provider verification

Call the existing Partner provider. Activation succeeds only when all are true:

```text
provider current plan handle == pendingShopifyPlanHandle
local pending plan id maps to that same active BillingPlan
BillingPlan.kind == PAID_METERED
provider contains the exact configured normal recovery usage meter
provider currentPeriodStart/currentPeriodEnd are both non-null
currentPeriodStart < currentPeriodEnd
BillingPlan.includedRecoveryConversationAllowance is a non-negative safe integer
```

Provider `null` and transport failure retain the bounded initial-activation retry policy owned by `ARCH-010-BACKGROUND-001` / `ARCH-010-SHOPIFY-002`.

## Unsupported paid trials

Shopify Partner API documents `currentBillingCycle = null` while the subscription is in trial. ARCH-010 does not support a synthetic trial billing period.

If provider truth identifies the requested paid plan as current but `trialEndsAt` is future and current cycle is null:

- do not set onboarding complete;
- do not create a BillingPeriod/counter;
- do not grant paid recovery entitlement;
- record a bounded configuration/synchronization error code such as `UNSUPPORTED_PAID_TRIAL` using the repository's established error-code style;
- do not run the ordinary 1-minute "Shopify has not activated yet" propagation retry loop for the entire trial;
- log an operationally actionable structured event without secrets.

Do not invent trial credits. If the product later wants paid trials, return to architecture.

## First paid period transaction

Once provider verification is valid, perform one transaction that:

1. reloads Subscription/ShopSettings/pending BillingPlan and confirms this is still initial activation;
2. upserts/reuses the exact BillingPeriod keyed by existing canonical `(shopId, periodStart, periodEnd)` identity;
3. require BillingPeriod status OPEN; do not reopen a CLOSED historical period;
4. populate/verify DATABASE-004 period ownership/snapshots: `subscriptionId`, `planId`, Shopify handle/name/kind snapshots and `includedRecoveryCreditsGranted`;
5. upserts/reuses the unique `BillingPeriodEntitlementCounter` for `INCLUDED_RECOVERY_CREDITS`;
6. on create, set `grantedQuantity = BillingPlan.includedRecoveryConversationAllowance`, other quantities zero;
7. on replay, never reset committed/reserved/forfeited quantities;
8. if an existing period snapshot or counter grant disagrees with the expected current plan/grant, fail closed rather than rewriting it;
9. ensure `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` exists; create it only when absent with `grantedQuantity = PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`, otherwise preserve its grant/usage exactly;
9. update Subscription current plan, observed handle, ACTIVE status, exact cycle, provider fields, and current billing period pointer;
10. clear pending initial-selection fields;
11. set `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)` for canonical rollover scheduling;
12. clear transient sync-error metadata on success;
13. set `ShopSettings.onboardingCompleted = true` last within the same transaction.

If any step fails, the transaction rolls back and the merchant remains unavailable for paid recovery.

## Billing-period end scheduling

Persist exact `currentPeriodEnd` as provider truth. After the successful activation transaction, schedule the already-defined canonical rollover lifecycle:

```text
nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)
```

Commit this durable timestamp with activation, then best-effort enqueue the existing deterministic reconciliation job after commit. BACKGROUND-007 owns what the pre-close/boundary job does; this task must not duplicate close/open logic.

Do not alter the current rotating reconciliation cadence solely to simulate rollover.

## Existing rotating reconciliation compatibility

The existing `reconcileOnce()` path may observe this same provider state. Refactor so applying a valid first paid subscription uses the same idempotent transaction/helper as the BullMQ job rather than creating a period without its required included counter.

After this task, no Background code path may produce:

```text
ACTIVE PAID_METERED subscription
+ current BillingPeriod
+ missing INCLUDED_RECOVERY_CREDITS counter
```

for a newly applied ARCH-010 paid subscription.

Do not duplicate Shopify calls inside the transaction. Provider observation occurs before the DB transaction; the transaction revalidates local state and applies that immutable observation.

## Required tests

Prove at least:

1. due pending paid target + matching current provider plan/cycle activates successfully;
2. exact BillingPeriod is created once;
3. included counter is created with configured grant and zero consumption;
4. onboarding becomes true only in the successful transaction;
5. replay reuses period/counter and does not reset usage;
6. provider null retains existing pending retry policy;
7. Partner transport failure retains existing pending retry policy and local state;
8. wrong current plan does not activate requested paid plan;
9. unknown/inactive plan mapping fails closed;
10. missing configured normal usage meter fails closed;
11. provider missing required meter fails closed;
12. missing currentBillingCycle does not create period;
13. paid TRIALING/no-cycle does not grant access and emits the explicit unsupported-trial error;
14. invalid cycle start >= end fails closed;
15. null/negative/non-integer included allowance fails closed;
15a. direct-to-Paid first activation creates the lifetime Free grant exactly once;
16. existing period counter with conflicting grant is not rewritten;
17. stale BullMQ job remains no-op;
18. uninstalled shop remains no-op;
19. Free activation behavior from BACKGROUND-001 remains passing;
20. no new queue/service/runtime process is created.
21. created first period contains DATABASE-004 subscription/plan snapshot fields;
22. successful activation sets nextReconcileAt to periodEnd minus the Shared drain window and best-effort enqueues the deterministic job;
23. queue-add failure does not roll back activation and reconstruction can recreate the scheduled job.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run build
git diff --check
```

Run relevant existing integration tests through `npm run test:integration` when required dependencies are available.

## Non-goals

Do not implement paid recovery reservation routing (BACKGROUND-002 owns it), merchant callback/UI, period rollover implementation (BACKGROUND-007 owns it), upgrade/downgrade, cancellation, top-up refund changes, promotional credits, or Admin UI.

## Stop conditions

STOP if:

- the integrated ARCH-010-BACKGROUND-001 consumer cannot be extended without changing the Shared payload;
- the database client lacks BillingPeriodEntitlementCounter;
- current BillingPeriod identity has changed since the inspected workspace;
- correct activation would require inventing a billing cycle during a trial.

## Completion Report

### Status
Implementation complete; Attempt 5 evidence correction is complete and the task is returned to architect review. Downstream tasks remain blocked pending architect review.

### Files Changed
- `moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`
- `moda-interact-background/src/services/billing-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `moda-interact-background/tests/unit/services/billing-reconciliation.service.test.ts`

### Work Completed
- Added a queued-path `PENDING_PLAN_HANDLE_MISMATCH` guard for same-local-plan Shopify handle drift before `applyOtherCurrentPlan`, preserving the pending target and bounded retry.
- Added a rotating-path fail-closed guard for the same drift, preventing legacy BillingPeriod projection and preserving durable pending intent.
- Added permanent evidence for the real queued drift state, rotating drift, CLOSED exact periods, incompatible period snapshots, conflicting included-credit grants, and successful Paid activation queue failure followed by `reconstruct()` repair.
- Strengthened `does not activate when the provider handle differs from the durable pending handle` with a realistic `paid-new` provider lookup and explicit no-transaction, no-activation, pending-state, and bounded-retry assertions.
- Preserved all Attempt 1-3 production corrections: transactional plan revalidation, nullable unsupported-trial recovery, canonical rotating activation, exact cycle/meter/allowance validation, and replay usage preservation.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- Focused reconciliation suites: passed, 2 files / 91 tests, including the strengthened Attempt 5 queued drift evidence.
- `npm run test:integration`: passed, 2 files / 3 tests.
- `git diff --check`: passed.
- `npm run test:unit`: 53 files passed, 2 failed; 709 tests passed, 10 failed. All failures are the documented unrelated baseline in recovery-credit purchase and observability-startup tests.
- `npm run build`: blocked by 15 existing generated-client/type errors in `purchased-recovery-reservation.service.ts` and `recovery-credit-purchase.service.ts`; no errors were reported in the touched billing services.
- Focused lint was unavailable because this repository does not declare/install ESLint; npm opened an install prompt, which was stopped without changing dependencies.
- Database submodule verified at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.

### Attempt 4 Evidence Map

- Same-local-plan queued handle drift: `does not activate when the provider handle differs from the durable pending handle`.
- Same-local-plan rotating handle drift: `leaves a same-local-plan handle drift pending during rotation`.
- Rotating canonical activation: `uses canonical paid activation for a pending initial target during rotation`.
- Unsupported trial with null schedule: `re-observes an unsupported paid trial with a null schedule and later activates its exact cycle`.
- CLOSED period: `fails closed for a closed exact paid billing period`.
- Incompatible period: `fails closed for an incompatible paid period %s` table covering subscription, plan, handle, name, kind, and grant snapshots.
- Conflicting included counter: `fails closed for a conflicting included-credit counter grant`.
- Paid enqueue failure plus reconstruction: `repairs a missing Paid activation job after post-commit queue failure`.

### Attempt 5 Evidence Map

- Realistic queued same-local-plan handle drift: `does not activate when the provider handle differs from the durable pending handle` maps both the provider handle and provider-handle lookup result to `paid-new`, records `PENDING_PLAN_HANDLE_MISMATCH`, proves no transaction or activation mutation, preserves pending fields, and publishes the exact bounded retry timestamp.
- Production source unchanged from Attempt 4; this attempt is test/evidence only as required by the latest Architect Review.

### Workflow Evidence

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-003`.
- Parent branch: `task/ARCH-010-BACKGROUND-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-003`.
- Implementation branch: `task/ARCH-010-BACKGROUND-003`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

Start-of-attempt synchronization:

- Parent remote task branch fast-forwarded: not-needed.
- Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed.
- Implementation `origin/main` incorporated: already-current.

Recursive implementation submodules:

- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Database gitlink expected and HEAD: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Database initialized: yes.
- Database gitlink staged/changed: no.

Task history:

- Attempt-1 claim `f536ff84f726654d6520ceac93aae1d5038edfc3`: ancestor of parent HEAD, yes.
- Attempt-1 implementation `c6d5c0a66de67cded04d8f60c2d268644286bb13`: ancestor of implementation HEAD, yes.
- Attempt-1 report `082d6de3a1b35c735571a4c7a0238fb0e104eb42`: ancestor of parent HEAD, yes.
- Attempt-2 claim `396d651734470326c6c5048af198d911281c7684`: ancestor of parent HEAD, yes.
- Attempt-2 implementation `3172334ae2400bf8de95422d7e5630320bba0d55`: ancestor of implementation HEAD, yes.
- Attempt-2 report `16ca4212344ab01a3552a341c3d54edbc59252cf`: ancestor of parent HEAD, yes.
- Attempt-3 claim `f9a393135cf701091750784588b0d34394765b2a`: ancestor of parent HEAD, yes.
- Attempt-3 evidence `110b6f5f4a92d2f6d01c206182da0444d912af8a`: ancestor of implementation HEAD, yes.
- Attempt-3 report `87c5064f8cc62ac73b79d85cb33e5c6e2526429c`: ancestor of parent HEAD, yes.
- Attempt-4 claim `c1d7ead3941dab01a27c636d9969822f0d849655`: pushed by launcher.
- Attempt-4 implementation `fbd24668b0a32ee085f8d02c219fd7d505a68a1e`: ancestor of implementation HEAD, yes; pushed.
- Attempt-5 claim `b5f3f9d90e9598b8f4ff32463bdd2dc9ed43a256`: ancestor of parent HEAD, yes.
- Attempt-5 implementation/evidence `0fe699ced684a1c2ffde09cc3510eea2d98524e1`: pushed on the implementation task branch, yes.

Handoff:

- Parent worktree clean before report commit: yes.
- Implementation worktree clean after implementation commit: yes.

### Git / VCS
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-003`.
- Implementation branch: `task/ARCH-010-BACKGROUND-003`.
- Implementation commits: `c6d5c0a66de67cded04d8f60c2d268644286bb13` (`feat(background): activate first paid subscriptions`), `3172334` (`fix(background): harden paid activation revalidation`), `110b6f5` (`test(ARCH-010-BACKGROUND-003): prove rotating paid activation recovery`), and `fbd24668b0a32ee085f8d02c219fd7d505a68a1e` (`fix(ARCH-010-BACKGROUND-003): guard paid activation handle drift`), pushed.
- Attempt 5 implementation/evidence: `0fe699ced684a1c2ffde09cc3510eea2d98524e1` (`test(ARCH-010-BACKGROUND-003): prove realistic paid handle drift guard`), pushed.
- Parent task-report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-003`.
- Database gitlink remains `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`; no database commit or schema change was made.
- Attempt 5 claim is cleared in this report; parent report commit/push follows. No merge to `main` performed.

### Architect Review
Requested. Focused task behavior and integration validation pass; unrelated full-suite and build baseline blockers are documented above. Attempt 5 awaits architect review.

## Architect Review — Attempt 1

### Changes Requested

Attempt 1 is **not accepted**. Return this same task to `ready` for Attempt 2.

Do not start any task listed under `enables`.

Published Attempt-1 history to preserve:

```text
claim:
  f536ff84f726654d6520ceac93aae1d5038edfc3

implementation:
  c6d5c0a66de67cded04d8f60c2d268644286bb13

parent report:
  082d6de3a1b35c735571a4c7a0238fb0e104eb42
```

Attempt 2 is the next claim. Increment `attempt` exactly once.

### Attempt-1 implementation accepted in substance — preserve it

The following behavior is directionally correct and must not regress:

```text
- the existing BACKGROUND-001 BullMQ payload/queue/runtime is reused;
- provider observation happens before the database transaction;
- a successful first Paid activation creates/reuses the canonical
  (shopId, periodStart, periodEnd) BillingPeriod;
- the first Paid BillingPeriod contains subscription/plan snapshots and
  includedRecoveryCreditsGranted;
- INCLUDED_RECOVERY_CREDITS is a BillingPeriodEntitlementCounter;
- a newly created included counter starts with:
    granted = plan allowance
    committed = 0
    reserved = 0
    forfeited = 0;
- existing included counters are replayed with update: {} so usage quantities are
  not reset;
- a CLOSED historical BillingPeriod is not reopened;
- incompatible existing period/counter evidence fails closed;
- LIFETIME_FREE_RECOVERY_CREDITS is created only when absent and otherwise
  preserved;
- subscription activation, pending-field clearing, current-period pointer and
  onboarding completion are transaction-owned;
- nextReconcileAt uses:
    max(now, periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS);
- next reconciliation is published after the activation transaction;
- future Paid trial with no cycle records UNSUPPORTED_PAID_TRIAL and does not
  synthesize credits or a BillingPeriod;
- missing cycle/meter/invalid allowance does not activate;
- rotating reconciliation was changed to call the same paid-activation service
  rather than creating a legacy period directly;
- no schema, Shared payload, second queue, second worker or Render process was
  introduced.
```

### Finding 1 — provider current handle is not required to equal the durable pending handle

Task contract:

```text
provider current plan handle == pendingShopifyPlanHandle
local pending plan id maps to that same active BillingPlan
```

Current BullMQ flow looks up the local BillingPlan by `provider.planHandle`, then
checks only:

```text
plan.id === row.subscription.pendingPlanId
```

That is insufficient.

If the same BillingPlan row has had its Shopify handle changed since the merchant's
pending selection was recorded, this state is possible:

```text
pendingPlanId              = plan-paid
pendingShopifyPlanHandle   = paid-old
provider.planHandle        = paid-new
BillingPlan.id             = plan-paid
BillingPlan.shopifyHandle  = paid-new
```

The current code can activate even though Shopify is **not** reporting the durable
requested handle.

#### Required correction

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

Before entering first-Paid activation, require all of:

```text
provider.planHandle === expected.pendingShopifyPlanHandle
plan.id === expected.pendingPlanId
plan.shopifyPlanHandle === expected.pendingShopifyPlanHandle
plan.active === true
plan.kind === PAID_METERED
```

Do not reinterpret "same local plan id" as equivalent to "same requested Shopify
handle".

A mismatched current provider handle must not activate the requested Paid target.

The existing `applyOtherCurrentPlan(...)` ownership for genuinely different provider
truth may remain; do not redesign it in this task.

### Finding 2 — the transaction does not re-read/revalidate the pending BillingPlan

The task explicitly requires the successful transaction to:

```text
reload Subscription / ShopSettings / pending BillingPlan
and confirm this is still initial activation
```

Attempt 1 locks/reloads ShopSettings and Subscription, but it continues to use the
BillingPlan object read **before** the Partner call/transaction.

This leaves a race where the plan can be changed between observation and commit:

```text
active -> inactive
PAID_METERED -> other kind
shopifyPlanHandle changed
shopifyUsageEventHandle changed
includedRecoveryConversationAllowance changed
plan name changed
```

The transaction can then persist stale plan snapshots or a stale included grant.

#### Required correction

Inside the successful activation transaction, after locking/rereading the source
activation state, re-read the plan by the current/pending plan id using the
transaction client.

Select at least:

```text
id
active
name
kind
shopifyPlanHandle
shopifyUsageEventHandle
includedRecoveryConversationAllowance
```

Fail closed unless the transactional plan satisfies:

```text
id === current.pendingPlanId
id === expected.pendingPlanId
active === true
kind === PAID_METERED
shopifyPlanHandle === current.pendingShopifyPlanHandle
shopifyPlanHandle === expected.pendingShopifyPlanHandle
shopifyPlanHandle === provider.planHandle
shopifyUsageEventHandle is non-null
provider.usageEventHandles contains shopifyUsageEventHandle
includedRecoveryConversationAllowance is a non-negative safe integer
```

The period snapshot, `planId`, plan name, configured handle and included grant used
for the commit must come from this **transactionally re-read plan**, not a stale
pre-transaction plan object.

Do not perform another Shopify/Partner call inside the transaction. The provider
observation remains immutable input; only local durable configuration is revalidated.

If the local plan changed during verification, throw/fail closed. Do not activate
and do not set onboarding complete.

### Finding 3 — rotating reconciliation is unsafe after UNSUPPORTED_PAID_TRIAL

Attempt 1 intentionally records an unsupported Paid trial with:

```text
nextReconcileAt = null
```

That avoids a one-minute retry loop across the entire trial.

However `BillingReconciliationService` currently enters the initial-Paid branch
without requiring `existing.nextReconcileAt` and passes:

```ts
nextReconcileAt: existing.nextReconcileAt!
```

The paid activation helper currently types `nextReconcileAt` as non-null and later
calls:

```ts
expected.nextReconcileAt.toISOString()
```

Therefore a merchant previously placed into `UNSUPPORTED_PAID_TRIAL` can be seen by
rotating reconciliation with a null durable schedule and cause a runtime exception
instead of being safely re-observed after the trial.

#### Required correction

Files:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

The shared first-Paid helper must safely support the exact durable state observed by
rotating reconciliation after unsupported trial.

Preferred deterministic contract:

```ts
type InitialActivationExpected = {
  subscriptionId: string;
  pendingPlanId: string;
  pendingShopifyPlanHandle: string;
  pendingEffectiveAt: Date;
  nextReconcileAt: Date | null;
};
```

The BullMQ initial-activation path still requires a non-null schedule before
constructing/executing its queued job.

The rotating path may pass the exact current nullable schedule.

Use null-safe exact comparison, for example:

```text
both null -> equal
one null -> different
both Date -> equal timestamps
```

Do not use a non-null assertion followed by `.toISOString()`.

Required behavior:

```text
future unsupported Paid trial, no cycle:
  no activation
  no synthetic period
  no one-minute loop across the trial
  no rotating crash

later rotating observation after Shopify supplies an exact Paid cycle:
  same durable pending intent may activate through the canonical helper
  even when the prior nextReconcileAt is null
```

Do not invent a synthetic trial period or trial credits.

### Finding 4 — rotating reconciliation needs permanent same-helper evidence

Attempt 1 changes the rotating production path but adds no direct behavioral test in:

```text
tests/unit/services/billing-reconciliation.service.test.ts
```

Add a focused test proving:

```text
ShopSettings.onboardingCompleted = false
Subscription = NO_CONTRACT
planId = null
pending Paid plan/handle identify provider current plan
provider exact cycle is present
```

Then assert:

```text
Partner is called once by rotating reconciliation;
canonical first-Paid activation helper/path is used;
legacy generic BillingPeriod upsert path is not used to create a first Paid period;
the resulting activation path owns creation/verification of the included counter.
```

Also add the unsupported-trial recovery case:

```text
pending Paid intent remains
nextReconcileAt = null
provider later reports exact Paid current cycle
rotating reconciliation does not throw
canonical Paid activation is allowed to commit.
```

Do not add a second queue or duplicated activation implementation to make the test
pass.

### Finding 5 — required Paid activation evidence is incomplete

Attempt 1 adds seven focused tests, but the task requires more exact Paid-specific
evidence.

Add permanent tests for all of the following.

#### 5.1 Exact provider/pending handle mismatch

Construct:

```text
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
provider.planHandle = paid-new
local provider-handle lookup returns id = plan-paid
```

Expected:

```text
requested Paid target is not activated;
no Paid BillingPeriod/counter is created for the requested activation;
onboardingCompleted is not set true by the Paid activation path.
```

#### 5.2 Transactional plan revalidation

Pre-transaction plan read is valid.

Transaction re-read changes one required authority fact.

At minimum test:

```text
active = false
shopifyPlanHandle differs
shopifyUsageEventHandle differs/missing
includedRecoveryConversationAllowance differs or becomes invalid
```

Each must fail closed before:

```text
BillingPeriod create
included-counter create/upsert
Subscription ACTIVE update
ShopSettings.onboardingCompleted = true
```

A table-driven test is acceptable.

#### 5.3 Allowance validation

The task explicitly requires:

```text
null
negative
non-integer
```

to fail closed.

Attempt 1 currently proves only one invalid numeric example.

Add exact cases for:

```text
null
-1
1.5
```

You may also retain an unsafe integer case.

#### 5.4 Conflicting existing included counter

Create an existing exact BillingPeriod and an existing
`INCLUDED_RECOVERY_CREDITS` counter whose grant differs from the current plan grant.

Expected:

```text
fail closed;
counter is not rewritten/reset;
Subscription does not become ACTIVE through this transaction;
onboardingCompleted remains false.
```

#### 5.5 Existing period conflict / CLOSED history

Permanently prove at least:

```text
exact historical period status CLOSED -> not reopened;
existing period snapshot with wrong plan/subscription/handle/grant -> not rewritten.
```

#### 5.6 Successful Paid enqueue failure + reconstruction repair

This must exercise the **successful Paid activation path**, not the existing generic
null-provider retry test.

Required sequence:

```text
1. Paid activation transaction commits successfully;
2. post-commit queue.add throws;
3. activation remains durable:
     ACTIVE
     billingPeriodId set
     currentPeriodStart/end set
     nextReconcileAt set
     onboardingCompleted true;
4. later reconstruct() sees the durable Paid schedule;
5. reconstruct publishes the missing deterministic job.
```

No database rollback is expected after queue publication failure.

### Finding 6 — replay evidence should assert no usage reset through actual mutation calls

Keep the current replay test, but strengthen it so it proves:

```text
existing BillingPeriod is reused;
billingPeriod.create is not called;
included counter upsert uses update: {};
existing committed/reserved/forfeited values are not supplied in any update payload;
existing lifetime counter causes:
  no PlatformBillingPolicy dependency
  no lifetime counter create/update/reset.
```

The existing in-memory object remaining unchanged is supplementary evidence; the
mutation-call assertions are authoritative.

### Attempt 2 allowed production scope

Expected production files:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

Expected test files:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
```

No other production file is expected.

Do not modify:

```text
database/**
Shared contracts/package versions
Shopify app
Admin
Messaging
Gateway
BACKGROUND-002 paid recovery reservation routing
BACKGROUND-007 rollover implementation
upgrade/downgrade/cancellation/refund/promotion logic
queue/worker topology
```

If a required correction needs schema or Shared payload changes, STOP and return to
`moda_architect`.

### Attempt 2 validation

Run:

```bash
git submodule sync -- database
git submodule update --init --recursive database

npm run prisma:validate
npm run prisma:generate

npx vitest run \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts

npm run test:unit
npm run build
git diff --check
```

Run `npm run test:integration` when the repository's required PostgreSQL/Redis
dependencies are available. If unavailable, record that fact; do not fabricate a
result.

Acceptance requires:

```text
- exact provider current handle == durable pending handle is enforced;
- pending BillingPlan is re-read/revalidated inside the activation transaction;
- period snapshots/grant use the transactionally current plan facts;
- unsupported Paid trial cannot crash rotating reconciliation;
- rotating reconciliation can later activate the same durable pending Paid intent
  when an exact provider cycle appears;
- null/negative/non-integer allowances all fail closed;
- closed/incompatible period evidence is not rewritten;
- conflicting counter grant is not rewritten;
- Paid replay does not reset usage/lifetime state;
- successful Paid activation survives queue-add failure and reconstruction repairs
  the missing job;
- rotating reconciliation has direct same-helper evidence;
- Free activation and BACKGROUND-007 rollover preservation suites remain green;
- no schema/Shared/queue/runtime topology change;
- documented unrelated baseline remains unchanged;
- git diff --check passes.
```

### Attempt 2 workflow evidence

The Completion Report must record actual observed values.

At minimum:

```text
Physical worktree isolation:
  canonical workspace root:
    /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree:
    /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-003
  parent branch:
    task/ARCH-010-BACKGROUND-003
  implementation worktree:
    /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-003
  implementation branch:
    task/ARCH-010-BACKGROUND-003
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Database submodule:
  database submodule initialized: yes
  database gitlink expected:
    <full SHA>
  database submodule HEAD:
    <full SHA>
  database gitlink staged/changed: no

Task history:
  Attempt-1 claim
    f536ff84f726654d6520ceac93aae1d5038edfc3
    ancestor of parent HEAD: yes
  Attempt-1 implementation
    c6d5c0a66de67cded04d8f60c2d268644286bb13
    ancestor of implementation HEAD: yes
  Attempt-1 report
    082d6de3a1b35c735571a4c7a0238fb0e104eb42
    ancestor of parent HEAD: yes

Handoff:
  parent worktree clean: yes
  implementation worktree clean: yes
```

Record observed values only.

When complete:

```text
set this same task to review;
publish implementation commit(s);
publish the Completion Report;
STOP for moda_architect review.
```

## Architect Review — Attempt 2

### Changes Requested

Attempt 2 is **not accepted yet**. Return this same task to `ready` for Attempt 3.

Attempt 2 fixed the three primary Attempt-1 race conditions in production:

```text
- exact provider handle == durable pending handle is now checked before the
  canonical Paid activation branch;
- the pending BillingPlan is re-read inside the activation transaction;
- nullable nextReconcileAt comparison no longer dereferences null after an
  unsupported Paid trial.
```

Those corrections are accepted in substance and must be preserved.

Published Attempt-2 history to preserve:

```text
Attempt-2 claim:
  396d651734470326c6c5048af198d911281c7684

Attempt-2 implementation:
  3172334ae2400bf8de95422d7e5630320bba0d55

Attempt-2 parent report:
  16ca4212344ab01a3552a341c3d54edbc59252cf
```

Attempt 3 is the next claim. Increment `attempt` exactly once.

### Attempt-2 production corrections accepted in substance

Preserve:

```text
- InitialActivationExpected.nextReconcileAt is Date | null;
- sameDate(...) exact nullable comparison;
- BullMQ Paid canonical branch requires:
    plan.id == pendingPlanId
    plan.shopifyPlanHandle == pendingShopifyPlanHandle
    provider.planHandle == pendingShopifyPlanHandle
    active PAID_METERED plan;
- successful Paid transaction re-reads BillingPlan by durable pending plan id;
- transactional plan must still be active PAID_METERED with exact handle/meter;
- provider must still contain the transactionally current configured normal meter;
- transactionally current included allowance must be a non-negative safe integer;
- period snapshot/name/plan/grant now use transactionally re-read plan facts;
- changed allowance/handle/meter/active state fails closed;
- null/negative/non-integer allowance evidence exists;
- replay counter upsert remains update: {} and now asserts no committed/reserved/
  forfeited mutation;
- rotating activation may pass a nullable durable schedule into the canonical helper.
```

Do not revert those changes.

### Finding 1 — same-local-plan handle drift still falls into the legacy other-plan path

This is a remaining production defect.

Current queued flow correctly declines the canonical Paid branch when:

```text
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
provider.planHandle = paid-new
BillingPlan.id = plan-paid
BillingPlan.shopifyPlanHandle = paid-new
```

However it then falls through to:

```text
applyOtherCurrentPlan(...)
```

That helper can project the provider plan as current and create a BillingPeriod
without creating/verifying the required `INCLUDED_RECOVERY_CREDITS` counter.

The Attempt-2 test:

```text
does not activate when the provider handle differs from the durable pending handle
```

does not expose this because its transaction mock still contains the harness default:

```text
pendingPlanId = plan-free
pendingShopifyPlanHandle = free-2026
```

so the transaction exits as stale before the legacy fallthrough can mutate anything.

#### Required production correction

Files:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

Define this case explicitly:

```text
same-local-plan handle drift =
  initial activation state
  AND provider handle resolves to a local PAID_METERED BillingPlan
  AND resolved BillingPlan.id == durable pendingPlanId
  AND (
    provider.planHandle != durable pendingShopifyPlanHandle
    OR resolved BillingPlan.shopifyPlanHandle != durable pendingShopifyPlanHandle
  )
```

For this case:

```text
- do NOT call completeVerifiedPaid;
- do NOT call applyOtherCurrentPlan;
- do NOT create/upsert a BillingPeriod;
- do NOT create/upsert an included counter;
- do NOT set Subscription ACTIVE/TRIALING;
- do NOT clear the durable pending target;
- do NOT set onboardingCompleted true.
```

For the queued path, record a bounded retry using a specific sync code:

```text
PENDING_PLAN_HANDLE_MISMATCH
```

Extend the existing paid-activation failure helper's allowed error-code union rather
than creating another queue/retry mechanism.

For rotating reconciliation, leave the durable pending activation unresolved and
return without the legacy period projection. Rotation itself is the recovery loop;
do not manufacture a one-minute queue loop when the durable schedule is null.

This guard applies only when the provider handle resolves back to the **same durable
pending local plan id**. A genuinely different provider plan id remains owned by the
existing other-current-plan logic; do not redesign that flow here.

#### Required test correction

Replace/strengthen the current handle-mismatch test so the transaction reread is:

```text
status = NO_CONTRACT
planId = null
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
pendingEffectiveAt = expected
nextReconcileAt = expected
```

and the provider/local mapping is:

```text
provider.planHandle = paid-new
resolved BillingPlan.id = plan-paid
resolved BillingPlan.shopifyPlanHandle = paid-new
kind = PAID_METERED
```

Assert:

```text
no transaction BillingPeriod create/upsert;
no included counter create/upsert;
no Subscription ACTIVE update;
no ShopSettings onboarding=true;
durable pending fields are not cleared;
queued path records PENDING_PLAN_HANDLE_MISMATCH through the bounded pending CAS.
```

Add the equivalent rotating test and prove it does not use the legacy period upsert.

### Finding 2 — required rotating canonical-helper evidence is still missing

Attempt 1 explicitly required direct tests in:

```text
tests/unit/services/billing-reconciliation.service.test.ts
```

Attempt 2 did not modify that file.

Add two permanent tests.

#### 2.1 Rotating first Paid activation uses canonical activation path

State:

```text
Shop ACTIVE
ShopSettings.onboardingCompleted = false
Subscription NO_CONTRACT
planId = null
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-2026
pendingEffectiveAt != null
nextReconcileAt != null
provider current handle = paid-2026
provider exact cycle present
active local PAID_METERED plan with normal meter + allowance
```

Use a spy on:

```text
BillingSubscriptionReconciliationService.prototype.activateInitialPaid
```

or a more direct durable harness if preferred.

Assert:

```text
Partner called once;
activateInitialPaid called once with the observed provider and exact durable pending
state;
legacy database.billingPeriod.upsert in BillingReconciliationService is not used
for this initial Paid activation.
```

Do not mock the canonical helper in a way that causes a second Partner call.

#### 2.2 Unsupported-trial recovery with null schedule

State:

```text
same pending Paid intent
nextReconcileAt = null
provider now supplies exact Paid current cycle
```

Assert:

```text
reconcileOnce does not throw;
activateInitialPaid receives nextReconcileAt: null;
legacy period upsert is not used.
```

This is the permanent regression for Attempt-1 Finding 3.

### Finding 3 — existing-period and existing-counter conflict evidence is still absent

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Add exact behavioral tests through `reconcileJob(...)`.

#### 3.1 CLOSED exact historical period

Existing exact `(shopId, periodStart, periodEnd)` BillingPeriod:

```text
status = CLOSED
```

Expected:

```text
rejects with the existing closed-period error;
billingPeriod.create not called;
included counter upsert not called;
Subscription not activated;
onboardingCompleted not set true.
```

#### 3.2 Incompatible existing period snapshot

At minimum use one table-driven set covering:

```text
wrong subscriptionId
wrong planId
wrong Shopify handle snapshot
wrong planNameSnapshot
wrong planKindSnapshot
wrong includedRecoveryCreditsGranted
```

Expected for every case:

```text
fail closed;
existing period not rewritten;
included counter not created/reset;
Subscription not activated;
onboarding remains false.
```

#### 3.3 Conflicting included counter grant

Existing exact OPEN period is compatible.

Existing `INCLUDED_RECOVERY_CREDITS` counter:

```text
grantedQuantity != current transactionally validated plan allowance
```

Expected:

```text
fail closed with incompatible included-credit counter;
counter upsert not called;
Subscription not activated;
onboarding remains false.
```

Also keep the existing compatible replay test.

### Finding 4 — required successful Paid enqueue-failure + reconstruction evidence is missing

The current test:

```text
does not roll back durable state when queue publication fails
```

is the existing null-provider retry path.

The current:

```text
repairs a missing delayed job after a committed rollover enqueue failure
```

is BACKGROUND-007 rollover evidence.

Neither proves task scenario 23 for **first Paid activation**.

Add a dedicated test:

```text
successful first Paid activation transaction commits;
queue.add rejects after commit;
activation remains durable;
later reconstruct() returns the durable Paid ACTIVE row and republishes the exact
nextReconcileAt job.
```

Required assertions before reconstruction:

```text
Subscription update contains:
  status ACTIVE
  planId plan-paid
  billingPeriodId period-paid
  exact currentPeriodStart/end
  exact nextReconcileAt

ShopSettings update contains:
  onboardingCompleted true
```

Then configure:

```text
database.shop.findMany -> one ACTIVE Paid row with that durable nextReconcileAt
queue.add -> succeeds
```

and assert:

```text
reconstruct() == 1;
deterministic job uses the exact durable nextReconcileAt;
no activation transaction is rerun by reconstruct().
```

A queue error after commit may be logged/propagated according to the existing
publish helper contract; the test must prove it does not roll back durable activation.

### Finding 5 — report overstates rotating coverage

Attempt-2 Completion Report says:

```text
Added focused coverage ... and rotating reconciliation compatibility.
```

but the implementation diff from Attempt 1 to Attempt 2 changes only:

```text
src/services/billing-reconciliation.service.ts
src/services/billing-subscription-reconciliation.service.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

It adds no `billing-reconciliation.service.test.ts` evidence.

Attempt 3 report must list exact new test titles by scenario and must not count an
unchanged adjacent suite as newly added rotating evidence.

### Finding 6 — required workflow evidence is still missing

Attempt-2 Completion Report does not contain the mandatory:

```text
Physical worktree isolation
Start-of-attempt synchronization
Task history
Handoff
```

blocks requested in Attempt 1.

Attempt 3 must record actual observed values.

At minimum:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-003
  parent branch: task/ARCH-010-BACKGROUND-003
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-003
  implementation branch: task/ARCH-010-BACKGROUND-003
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Database submodule:
  database submodule initialized: yes
  database gitlink expected: 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
  database submodule HEAD: <actual full SHA>
  database gitlink staged/changed: no

Task history:
  Attempt-1 claim f536ff84f726654d6520ceac93aae1d5038edfc3
    ancestor of parent HEAD: yes
  Attempt-1 implementation c6d5c0a66de67cded04d8f60c2d268644286bb13
    ancestor of implementation HEAD: yes
  Attempt-1 report 082d6de3a1b35c735571a4c7a0238fb0e104eb42
    ancestor of parent HEAD: yes
  Attempt-2 claim 396d651734470326c6c5048af198d911281c7684
    ancestor of parent HEAD: yes
  Attempt-2 implementation 3172334ae2400bf8de95422d7e5630320bba0d55
    ancestor of implementation HEAD: yes
  Attempt-2 report 16ca4212344ab01a3552a341c3d54edbc59252cf
    ancestor of parent HEAD: yes

Handoff:
  parent worktree clean: yes
  implementation worktree clean: yes
```

Record observed values only.

### Attempt 3 allowed scope

Expected production files:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

Expected tests:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
```

No schema/Shared/other-repository change is authorized.

Do not modify:

```text
database/**
Shared contracts/package versions
BACKGROUND-002 recovery admission
BACKGROUND-007 rollover behavior
Shopify/Admin/Messaging/Gateway repositories
upgrade/downgrade/cancellation/refund/promotion flows
queue/worker topology
```

If correcting same-local-plan handle drift requires a schema or Shared payload
change, STOP and return to `moda_architect`.

### Required Attempt 3 validation

Run:

```bash
git submodule sync -- database
git submodule update --init --recursive database

npm run prisma:validate
npm run prisma:generate

npx vitest run \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts

npm run test:unit
npm run build
git diff --check
```

Run `npm run test:integration` only when the repository's required services are
available; otherwise record the exact unavailable dependency.

Acceptance requires:

```text
- same-local-plan handle drift cannot fall through to legacy active-period projection;
- queued handle drift preserves pending state and uses bounded mismatch retry;
- rotating handle drift preserves pending state and does not create a legacy period;
- rotating exact Paid activation has direct canonical-helper evidence;
- rotating null-schedule recovery has direct evidence;
- CLOSED/incompatible existing period is permanently proven fail-closed;
- conflicting included-counter grant is permanently proven fail-closed;
- successful first Paid activation queue failure + reconstruction repair is proven;
- compatible replay still does not reset period/lifetime usage;
- Attempt-2 handle/transaction/allowance/null-schedule corrections remain green;
- Free activation and BACKGROUND-007 rollover adjacent suites remain green;
- documented unrelated full-suite/build baseline remains unchanged;
- workflow/history evidence is complete;
- git diff --check passes.
```

When complete:

```text
set this same task to review;
publish implementation/evidence commit(s);
publish Completion Report with exact test titles/results/workflow evidence;
STOP for moda_architect.
```

## Architect Review — Attempt 3

### Changes Requested

Attempt 3 is **not accepted**. Return this same task to `ready` for Attempt 4.

Do not start any task listed under `enables`.

Published Attempt-3 history to preserve:

```text
Attempt-3 claim:
  f9a393135cf701091750784588b0d34394765b2a

Attempt-3 evidence:
  110b6f5f4a92d2f6d01c206182da0444d912af8a

Attempt-3 parent report:
  87c5064f8cc62ac73b79d85cb33e5c6e2526429c
```

Attempt 4 is the next claim. Increment `attempt` exactly once.

### Attempt-3 evidence accepted in substance

Preserve these new tests:

```text
tests/unit/services/billing-reconciliation.service.test.ts

- "uses canonical paid activation for a pending initial target during rotation"
- "re-observes an unsupported paid trial with a null schedule and later activates
   its exact cycle"

tests/unit/services/billing-subscription-reconciliation.service.test.ts

- "ignores a queued job when unsupported-trial recovery cleared the durable schedule"
```

They close the direct rotating-path/null-schedule evidence gap from Attempt 2.

Attempt 3 also reports:

```text
focused reconciliation: 81/81 passed
integration: 3/3 passed
Prisma validate/generate: passed
git diff --check: passed
```

The unrelated repository baseline remains documented.

### Why Attempt 3 cannot be accepted

GitHub verifies that:

```text
110b6f5f4a92d2f6d01c206182da0444d912af8a
```

is test-only and changes exactly:

```text
tests/unit/services/billing-reconciliation.service.test.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

It makes **no production change**.

Therefore the required Attempt-2 production correction for same-local-plan Shopify
handle drift was never implemented.

The uploaded source still does:

```ts
if (
  plan?.active
  && plan.id === row.subscription.pendingPlanId
  && plan.shopifyPlanHandle === row.subscription.pendingShopifyPlanHandle
  && provider.planHandle === row.subscription.pendingShopifyPlanHandle
  && plan.kind === BillingPlanKind.PAID_METERED
) {
  await this.completeVerifiedPaid(...);
  return;
}

await this.applyOtherCurrentPlan(...);
```

So this exact state still falls through:

```text
durable pendingPlanId = plan-paid
durable pendingShopifyPlanHandle = paid-old
provider.planHandle = paid-new
provider handle lookup returns BillingPlan.id = plan-paid
BillingPlan.shopifyPlanHandle = paid-new
BillingPlan.kind = PAID_METERED
```

That fallthrough is unsafe because `applyOtherCurrentPlan(...)` may project
`Subscription.status = ACTIVE/TRIALING` and create/reuse a BillingPeriod without
creating/verifying the canonical Paid `INCLUDED_RECOVERY_CREDITS` counter.

The existing unit test named:

```text
"does not activate when the provider handle differs from the durable pending handle"
```

still does **not** prove this case. Its transaction mock retains the harness default:

```text
pendingPlanId = plan-free
pendingShopifyPlanHandle = free-2026
```

so `applyOtherCurrentPlan(...)` exits on stale durable state before any unsafe
fallthrough can occur.

### Correction 1 — implement the same-local-plan handle-drift guard

File:

```text
src/services/billing-subscription-reconciliation.service.ts
```

After provider handle -> local BillingPlan lookup, but **before**
`applyOtherCurrentPlan(...)`, detect:

```ts
const samePendingPlanHandleDrift =
  plan?.active === true
  && plan.kind === BillingPlanKind.PAID_METERED
  && plan.id === row.subscription.pendingPlanId
  && (
    provider.planHandle !== row.subscription.pendingShopifyPlanHandle
    || plan.shopifyPlanHandle !== row.subscription.pendingShopifyPlanHandle
  );
```

Equivalent code is allowed, but the predicate must preserve these semantics.

When true:

```text
- never call completeVerifiedPaid;
- never call applyOtherCurrentPlan;
- never create/upsert a BillingPeriod;
- never create/upsert an included counter;
- never set Subscription ACTIVE/TRIALING;
- never clear pendingPlanId/pendingShopifyPlanHandle/pendingEffectiveAt;
- never set onboardingCompleted true.
```

For the queued path, call the existing bounded pending-failure mechanism with:

```text
PENDING_PLAN_HANDLE_MISMATCH
```

Extend the exact error-code union of `recordPaidActivationFailure(...)` to include:

```text
"PENDING_PLAN_HANDLE_MISMATCH"
```

Do not create another retry helper/queue.

The existing `nextSubscriptionReconcileAt(...)` retry cadence remains authoritative.

### Correction 2 — make the queued drift test exercise the real unsafe branch

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Replace or strengthen:

```text
"does not activate when the provider handle differs from the durable pending handle"
```

Use:

```text
row.subscription.pendingPlanId = plan-paid
row.subscription.pendingShopifyPlanHandle = paid-old
provider.planHandle = paid-new
plan.id = plan-paid
plan.shopifyPlanHandle = paid-new
plan.kind = PAID_METERED
```

Critically, also make the **transactional reread** match the same durable state:

```text
status = NO_CONTRACT
planId = null
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
pendingEffectiveAt = expected
nextReconcileAt = expected
```

Then assert:

```text
database.subscription.updateMany called once with:
  lastSyncErrorCode = PENDING_PLAN_HANDLE_MISMATCH
  nextReconcileAt = bounded retry time

transaction billingPeriod.findUnique/create/upsert not called
transaction billingPeriodEntitlementCounter findUnique/upsert not called
transaction subscription.update not called
transaction shopSettings.update not called
pending fields are not cleared
queue publishes at most the bounded retry job from recordPaidActivationFailure
```

Do not accept "no mutation" caused by stale transaction state as evidence.

### Correction 3 — guard the rotating path against the same drift

File:

```text
src/services/billing-reconciliation.service.ts
```

Current rotating initial-activation branch is entered only when:

```text
existing.pendingShopifyPlanHandle === provider.planHandle
```

Preserve that direct canonical-activation condition.

Add an explicit fail-closed branch for:

```text
initial activation state
AND plan resolves from provider.planHandle
AND plan.id === existing.pendingPlanId
AND plan.kind === PAID_METERED
AND provider.planHandle !== existing.pendingShopifyPlanHandle
```

Expected rotating behavior:

```text
- do not invoke activateInitialPaid;
- do not use legacy database.billingPeriod.upsert;
- do not update Subscription to ACTIVE/TRIALING;
- do not clear durable pending intent;
- return bounded/no-op rotating result and allow future rotation to re-observe.
```

Do not create a one-minute queued retry when the durable schedule is null.
Rotation is already the recovery loop.

Add direct evidence in:

```text
tests/unit/services/billing-reconciliation.service.test.ts
```

for this exact same-local-plan handle drift.

### Correction 4 — add the missing existing-period conflict evidence

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

These tests required by Attempt 2 are still absent.

#### 4.1 CLOSED historical exact period

Arrange a canonical first-Paid activation with transactionally valid plan and an
existing exact BillingPeriod whose:

```text
status = CLOSED
```

Assert:

```text
rejects with the production closed-period error;
billingPeriod.create not called;
included counter find/create/upsert not called;
subscription.update not called;
shopSettings.update not called.
```

#### 4.2 Incompatible existing period

Use a table-driven test covering at least:

```text
subscriptionId mismatch
planId mismatch
shopifyPlanHandleSnapshot mismatch
planNameSnapshot mismatch
planKindSnapshot mismatch
includedRecoveryCreditsGranted mismatch
```

For every row:

```text
throws "Initial paid activation found an incompatible billing period";
existing period not rewritten;
included counter not created/reset;
subscription not activated;
onboarding remains false.
```

### Correction 5 — add the missing conflicting included-counter evidence

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Arrange:

```text
existing exact OPEN BillingPeriod is fully compatible;
existing INCLUDED_RECOVERY_CREDITS counter exists;
counter.grantedQuantity != transactionally validated current plan allowance.
```

Assert:

```text
throws "Initial paid activation found an incompatible included-credit counter";
billingPeriodEntitlementCounter.upsert not called;
subscription.update not called;
shopSettings.update not called;
existing committed/reserved/forfeited values are untouched.
```

Keep the existing compatible replay test.

### Correction 6 — add the missing successful Paid activation queue-failure repair evidence

The task still lacks a test for:

```text
successful first Paid activation commits
-> publishNext queue.add fails
-> durable activation remains committed
-> reconstruct() repairs the missing delayed job.
```

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Add a dedicated test, not a renamed existing rollover/null-provider test.

Suggested deterministic harness:

```text
1. Arrange canonical valid Paid activation.
2. transaction callback records successful:
     Subscription ACTIVE update
     BillingPeriod create/reuse
     INCLUDED counter create/upsert
     ShopSettings onboardingCompleted=true
3. queue.add rejects on the post-commit publish.
4. reconcileJob rejects/logs according to current publishNext behavior.
5. Assert all durable transaction calls above already occurred.
6. Reset queue.add to succeed.
7. database.shop.findMany returns one ACTIVE/onboarded Paid row with:
     subscription.id
     exact durable nextReconcileAt
8. call reconstruct().
9. assert reconstruct() == 1 and queue.add uses that exact durable schedule.
```

Also assert reconstruction does not invoke Partner or rerun activation.

### Correction 7 — Completion Report must list exact Attempt-4 evidence

Attempt 3 still reports aggregate counts but does not list the exact new test titles
by requirement as instructed.

Attempt 4 report must include a compact mapping:

```text
same-local-plan queued handle drift:
  <exact test title>

same-local-plan rotating handle drift:
  <exact test title>

rotating canonical activation:
  uses canonical paid activation for a pending initial target during rotation

unsupported trial null schedule:
  re-observes an unsupported paid trial with a null schedule and later activates
  its exact cycle

CLOSED period:
  <exact test title>

incompatible period:
  <exact test title>

conflicting included counter:
  <exact test title>

Paid enqueue failure + reconstruct:
  <exact test title>
```

Do not describe unrelated integration tests as proof of these unit-level invariants.

### Correction 8 — mandatory workflow evidence must be recorded in the current report

The required text currently exists only inside prior Architect Review instructions.
It is not present in the current Attempt-3 Completion Report.

Attempt 4 must record actual observed values:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-003
  parent branch: task/ARCH-010-BACKGROUND-003
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-003
  implementation branch: task/ARCH-010-BACKGROUND-003
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Database submodule:
  database submodule initialized: yes
  database gitlink expected: 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
  database submodule HEAD: <actual full SHA>
  database gitlink staged/changed: no

Task history:
  Attempt-1 claim f536ff84f726654d6520ceac93aae1d5038edfc3
    ancestor of parent HEAD: yes
  Attempt-1 implementation c6d5c0a66de67cded04d8f60c2d268644286bb13
    ancestor of implementation HEAD: yes
  Attempt-1 report 082d6de3a1b35c735571a4c7a0238fb0e104eb42
    ancestor of parent HEAD: yes

  Attempt-2 claim 396d651734470326c6c5048af198d911281c7684
    ancestor of parent HEAD: yes
  Attempt-2 implementation 3172334ae2400bf8de95422d7e5630320bba0d55
    ancestor of implementation HEAD: yes
  Attempt-2 report 16ca4212344ab01a3552a341c3d54edbc59252cf
    ancestor of parent HEAD: yes

  Attempt-3 claim f9a393135cf701091750784588b0d34394765b2a
    ancestor of parent HEAD: yes
  Attempt-3 evidence 110b6f5f4a92d2f6d01c206182da0444d912af8a
    ancestor of implementation HEAD: yes
  Attempt-3 report 87c5064f8cc62ac73b79d85cb33e5c6e2526429c
    ancestor of parent HEAD: yes

Handoff:
  parent worktree clean: yes
  implementation worktree clean: yes
```

Record actual values only.

### Attempt 4 allowed scope

Production:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

Tests:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/services/billing-reconciliation.service.test.ts
```

Parent task document/report.

Do not modify:

```text
database/**
Shared contracts/package versions
other repositories
BACKGROUND-002 recovery admission
BACKGROUND-007 rollover implementation
queue/worker topology
upgrade/downgrade/cancellation/refund/promotion behavior
```

If the required handle-drift guard needs a schema/Shared change, STOP and return to
`moda_architect`.

### Required Attempt 4 validation

Run:

```bash
git submodule sync -- database
git submodule update --init --recursive database

npm run prisma:validate
npm run prisma:generate

npx vitest run \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts

npm run test:integration
npm run test:unit
npm run build
git diff --check
```

Acceptance requires:

```text
- queued same-local-plan handle drift cannot reach applyOtherCurrentPlan;
- queued drift preserves pending target and records PENDING_PLAN_HANDLE_MISMATCH;
- rotating same-local-plan handle drift cannot use legacy BillingPeriod projection;
- canonical rotating activation/null-schedule tests from Attempt 3 remain green;
- CLOSED exact historical period fails closed;
- incompatible existing period snapshots fail closed;
- conflicting included counter grant fails closed;
- successful first Paid activation survives queue publish failure and reconstruct
  repairs the missing job;
- compatible replay continues not to reset usage/lifetime state;
- Attempt-2 transactional plan/allowance/handle validation remains green;
- focused and available integration suites remain green;
- unrelated full-unit/build baseline is unchanged;
- workflow/history evidence is present in the current report;
- database gitlink unchanged;
- git diff --check passes.
```

When complete:

```text
set this same task to review;
publish implementation/evidence commit(s);
publish Completion Report;
STOP for moda_architect.
```



## Architect Review — Attempt 4

### Changes Requested

Attempt 4 is **not accepted**. Return this same task to `ready` for Attempt 5.

Do not start any task listed under `enables`.

Published Attempt-4 history to preserve:

```text
Attempt-4 claim:
  c1d7ead3941dab01a27c636d9969822f0d849655

Attempt-4 implementation:
  fbd24668b0a32ee085f8d02c219fd7d505a68a1e

Attempt-4 parent report:
  9787eb3318d7f0ce4d39e2f563d0d63f6b342b53
```

Attempt 5 is the next claim. Preserve `attempt: 4` in this review patch; the normal
launcher claim must increment it **exactly once** to `attempt: 5`.

### Attempt-4 production correction accepted in substance — preserve it

The production changes in `fbd24668b0a32ee085f8d02c219fd7d505a68a1e` implement the
requested same-local-plan handle-drift guard in both reconciliation paths:

```text
queued reconciliation:
  same active PAID_METERED BillingPlan id
  + provider/local Shopify handle differs from durable pending handle
  -> record PENDING_PLAN_HANDLE_MISMATCH
  -> bounded retry
  -> return before applyOtherCurrentPlan

rotating reconciliation:
  same active PAID_METERED BillingPlan id
  + provider/local Shopify handle differs from durable pending handle
  -> return fail-closed
  -> do not use legacy BillingPeriod projection
```

Preserve these production changes. **Do not modify production source merely to
manufacture an Attempt-5 implementation commit.**

The following Attempt-4 evidence is also accepted and must remain green:

```text
- rotating same-local-plan handle drift;
- rotating canonical first-Paid activation;
- unsupported-trial null-schedule recovery;
- CLOSED exact period rejection;
- incompatible existing-period snapshot rejection;
- conflicting INCLUDED_RECOVERY_CREDITS grant rejection;
- Paid post-commit enqueue failure followed by reconstruct() repair;
- compatible replay preserving committed/reserved/forfeited and lifetime state.
```

### Finding — queued same-local-plan drift test still does not model the real lookup state

File:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

Attempt 3 required the queued regression to model this exact real state:

```text
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
provider.planHandle = paid-new
BillingPlan.id = plan-paid
BillingPlan.shopifyPlanHandle = paid-new
BillingPlan.kind = PAID_METERED
```

Attempt 4 still arranges:

```ts
providerResult: paidProvider, // provider.planHandle == "paid-2026"
plan: { ...paidPlan, shopifyPlanHandle: "paid-new" }
```

Production resolves the local plan with:

```ts
billingPlan.findUnique({
  where: { shopifyPlanHandle: provider.planHandle },
})
```

Therefore the current mock says, in effect:

```text
lookup key:       paid-2026
returned row key: paid-new
```

That cannot represent a real result from the unique `shopifyPlanHandle` lookup and
does not prove the previously unsafe branch. The production guard appears correct,
but acceptance requires permanent evidence against the actual state that caused the
Attempt-3 Changes Requested decision.

### Required correction — test/evidence only

Modify only:

```text
tests/unit/services/billing-subscription-reconciliation.service.test.ts
```

unless the corrected realistic test exposes a genuine production defect.

Strengthen the existing test:

```text
"does not activate when the provider handle differs from the durable pending handle"
```

Use this deterministic arrangement:

```ts
row.subscription.pendingPlanId = "plan-paid";
row.subscription.pendingShopifyPlanHandle = "paid-old";

provider.planHandle = "paid-new";

plan.id = "plan-paid";
plan.active = true;
plan.kind = PAID_METERED;
plan.shopifyPlanHandle = "paid-new";
plan.shopifyUsageEventHandle = "recovery-meter";
plan.includedRecoveryConversationAllowance = 100;
```

The transaction-state fixture, if retained, must describe the same durable pending
intent:

```text
status = NO_CONTRACT
planId = null
pendingPlanId = plan-paid
pendingShopifyPlanHandle = paid-old
pendingEffectiveAt = expected
nextReconcileAt = expected queued schedule
```

Add/assert all of the following:

```text
1. Partner is called exactly once.

2. billingPlan.findUnique is called with:
     where.shopifyPlanHandle = paid-new
   and the returned BillingPlan also has:
     shopifyPlanHandle = paid-new

3. subscription.updateMany records:
     lastSyncErrorCode = PENDING_PLAN_HANDLE_MISMATCH
     nextReconcileAt = the existing bounded retry result

4. database.$transaction is NOT called.
   This proves the guard returned before applyOtherCurrentPlan and before the
   first-Paid transaction helper.

5. No BillingPeriod or BillingPeriodEntitlementCounter mutation occurs.

6. No Subscription activation/update occurs.

7. ShopSettings.onboardingCompleted is not changed.

8. The durable pending target is not cleared by this path.

9. queue.add is called at most once for the bounded retry and uses the exact
   durable retry timestamp produced by nextSubscriptionReconcileAt(...).
```

Do not weaken the rotating drift test. Its Attempt-4 arrangement already uses the
real state `provider.planHandle = paid-new` and `plan.shopifyPlanHandle = paid-new`.

### Production-source rule for Attempt 5

Expected result: **no production source change**.

Do not edit:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
```

if the realistic queued regression passes against `fbd24668...`.

If and only if the corrected realistic test fails because the guard can still reach
`applyOtherCurrentPlan(...)`, make the smallest correction inside the existing
same-local-plan drift guard and report the exact reason. Do not redesign activation,
retry, queue, period, entitlement, trial, rollover, upgrade/downgrade or provider
semantics.

Do not modify:

```text
database/**
Shared contracts/package versions
other repositories
BACKGROUND-002 recovery admission
BACKGROUND-007 rollover implementation
queue/worker topology
upgrade/downgrade/cancellation/refund/promotion behavior
```

### Attempt-5 validation

Because Attempt 4 already completed Prisma, integration, full-unit and build/baseline
validation and this correction is expected to be test-only, run exactly:

```bash
npx vitest run \
  tests/unit/services/billing-subscription-reconciliation.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts

git diff --check
```

Expected focused result is the same two suites with the corrected queued-drift case
green. Record the exact observed test count; do not hard-code `91/91` if the count
changes because the test was split or strengthened.

If production source is changed because the realistic test exposed a defect, also
rerun the full task validation from the task's `## Validation` section before
returning to review.

### Attempt-5 Completion Report evidence

Record explicitly:

```text
queued same-local-plan drift arrangement:
  pending handle = paid-old
  provider handle = paid-new
  returned BillingPlan handle = paid-new
  returned BillingPlan id = plan-paid

lookup evidence:
  billingPlan.findUnique where.shopifyPlanHandle = paid-new

fallback evidence:
  database.$transaction call count = 0

failure evidence:
  lastSyncErrorCode = PENDING_PLAN_HANDLE_MISMATCH
  bounded retry timestamp = <actual ISO timestamp>

production source changed in Attempt 5: yes|no
```

If `production source changed in Attempt 5: no`, an implementation-source commit is
**not required**. Commit/push the corrected permanent test on the existing
implementation task branch, update the parent Completion Report, set this same task
to `review`, clear the claim and STOP for `moda_architect`.
