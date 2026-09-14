---
id: ARCH-010-SHOPIFY-003
architecture_id: ARCH-010
title: Activate first verified paid plan with exact billing period
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 44
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-002
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-003
- ARCH-008-SHOPIFY-001
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-004
- ARCH-010-SHOPIFY-007
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-003: Activate first verified paid plan with exact billing period

## Objective

Extend the billing callback/fast-path subscription sync so a merchant with no current plan can complete onboarding into a paid plan only after Shopify verifies the exact current paid plan, normal usage meter, and current billing cycle. Atomically create the first period-scoped included-credit counter before paid product access becomes available.

## Inspect before editing

```text
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/routes/app/home/route.jsx
app/routes/app/billing/route.tsx
app/services/shop/shop.service.ts
app/services/shop/shop-access-policy.ts
tests/unit/routes/billing-callback.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/services/shopify-billing.provider.test.ts
package.json
```

Read the implemented ARCH-010-SHOPIFY-002 result before editing; reuse its pending-intent and best-effort reconciliation producer instead of creating another queue path.

## Source-state guard

This task is only for first paid activation:

```text
ShopSettings.onboardingCompleted = false
and no existing current mapped plan is active for Moda entitlement
```

If the shop already has a current active Free/Paid plan, a different requested handle is an upgrade/downgrade transition and MUST NOT be applied immediately by this task.

## Callback intent

A locally mapped active `BillingPlan.kind = PAID_METERED` callback handle may be persisted as pending initial-selection intent using the same ARCH-010-SHOPIFY-002 mechanism:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt = now
nextReconcileAt = now
```

The URL parameter alone never sets current paid entitlement or onboarding complete.

## Fast-path verification

Perform one Partner `activeSubscription` query using the existing provider.

Activation requires all of:

```text
current provider flat-rate plan handle == requested plan_handle
mapped local plan exists and active
plan.kind == PAID_METERED
configured normal recovery meter exists
provider current subscription exposes that exact meter
currentPeriodStart/currentPeriodEnd are both non-null
start < end
includedRecoveryConversationAllowance is a non-negative safe integer
provider is not an unsupported paid trial/no-cycle state
```

Do not calculate a billing cycle locally.

## Successful first paid activation transaction

Refactor `BillingService.syncSubscription()` narrowly so the paid first-activation apply path cannot create an incomplete period.

In one Prisma transaction:

1. reload local Shop/Settings/Subscription/target plan;
2. confirm this remains an initial activation rather than a plan change;
3. upsert/reuse the exact `BillingPeriod` from Shopify `currentBillingCycle`;
4. require period OPEN; do not reopen CLOSED historical periods;
5. populate/verify DATABASE-004 ownership/snapshots: `subscriptionId`, `planId`, Shopify handle/name/kind snapshots and `includedRecoveryCreditsGranted`;
6. create/reuse `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`;
7. new counter grant = `BillingPlan.includedRecoveryConversationAllowance`;
8. replay never resets committed/reserved/forfeited quantities;
9. conflicting existing period snapshot or counter grant fails closed rather than being overwritten;
10. update current Subscription projection/cycle/current period pointer;
11. clear initial pending target;
12. set `nextReconcileAt = max(now, currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)`;
13. clear successful sync error metadata;
14. set `ShopSettings.onboardingCompleted = true` only after all billing state above is valid.

Return/redirect to `/app` only after the transaction succeeds. After commit, best-effort enqueue the existing deterministic subscription-reconciliation job at the new `nextReconcileAt`. Queue failure must not roll back activation; Background queue repair reconstructs it.

## Provider null / transport failure

Reuse the initial-activation verification behaviour from `ARCH-010-SHOPIFY-002` / `ARCH-010-BACKGROUND-001` exactly:

- successful provider null -> stay onboarding/NO_CONTRACT, retain pending target and delayed reconciliation;
- Partner API transport failure -> preserve local state, retain pending target and delayed reconciliation;
- BullMQ enqueue failure -> durable DB intent remains, queue repair recovers it later.

Do not add a second retry implementation.

## Unsupported paid trial

Shopify documents `currentBillingCycle = null` during a trial. ARCH-010 does not support paid trial entitlements.

If the current paid plan is verified but `trialEndsAt` is future/current cycle absent:

- do not create a BillingPeriod;
- do not set onboarding complete;
- do not expose paid recovery services;
- persist/return a safe billing configuration state compatible with BACKGROUND-003's `UNSUPPORTED_PAID_TRIAL` handling;
- do not fabricate an upcoming cycle from trial end.

Do not implement trial entitlement in this task.

## Free/purchased/promotional balance preservation

First paid activation MUST NOT:

- reset or delete an existing `LIFETIME_FREE_RECOVERY_CREDITS` grant/usage;
- reset purchased top-up credits;
- consume purchased credits;
- grant promotional credits;
- skip the one-time shop-lifetime Free grant merely because the first verified plan is Paid;
- copy Free allowance into the paid period.

The new paid period receives only its configured paid `includedRecoveryConversationAllowance` in the period counter.

In the same first-activation transaction, ensure `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` exists. If absent, create it with `grantedQuantity = PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` and zero committed/reserved/refunding quantities. If it exists, never rewrite its grant or usage. This lifetime grant is independent of the paid period counter.

## No incomplete paid subscription state

After this task, the application fast path must never commit:

```text
ACTIVE paid subscription + onboardingCompleted=true
```

unless the exact current BillingPeriod and unique included-credit counter both exist and match the observed Shopify cycle.

## Required tests

At minimum prove:

1. paid callback records pending intent before activation;
2. callback parameter alone does not activate;
3. current matching paid plan + exact cycle + meter activates;
4. first BillingPeriod created with exact Shopify boundaries;
5. first period counter created with configured included grant;
6. onboarding completes only after period/counter transaction;
7. replay does not reset committed/reserved/forfeited values;
8. conflicting existing period grant fails closed;
9. provider null uses existing delayed-reconciliation path;
10. Partner API failure uses existing delayed-reconciliation path;
11. queue failure does not lose durable intent;
12. wrong current handle does not activate requested paid plan;
13. pending-only paid handle does not activate first onboarding;
14. already-current Free/Paid merchant requesting another plan is not handled as first activation;
15. missing provider usage meter fails closed;
16. missing current cycle fails closed;
17. paid trial/no-cycle fails closed without synthetic period;
18. invalid included allowance fails closed;
19. direct-to-Paid first activation creates the one-time lifetime Free grant exactly once; replay does not regrant it;
19. Free lifetime and purchased balances remain unchanged;
20. no merchant route points to `moda-interact-admin`;
21. first BillingPeriod contains DATABASE-004 ownership/snapshot fields;
22. successful activation schedules nextReconcileAt at periodEnd minus the Shared drain window;
23. queue-add failure does not roll back successful activation.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test -- tests/unit/routes/billing-callback.test.ts tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts
npm run typecheck
npm run build
git diff --check
```

If Vitest argument forwarding differs in the integrated package, use the actual declared Vitest invocation without inventing an npm script; document the command used.

## Non-goals

Do not implement paid reservation routing, period rollover execution (BACKGROUND-007 owns it), upgrade/downgrade, cancellation, top-up refunds, promotional-credit grants, Admin UI or a new queue contract.

## Stop conditions

STOP if:

- ARCH-010 period counter is not available in generated Prisma client;
- callback source state cannot distinguish first activation from a plan change;
- the existing billing provider cannot expose exact current cycle/meter identity;
- successful activation would require synthetic trial-period dates.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact/app/routes/app/billing/callback/route.tsx`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/tests/unit/routes/billing-callback.test.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`

### Work Completed
- Preserved the Attempt-1 pending initial Paid intent and existing reconciliation producer.
- Moved verified first-Paid period/counter creation and onboarding completion into the single `syncSubscription` transaction using the immutable single Partner observation.
- Revalidated Shop status, onboarding state, exact pending token and transactionally re-read active Paid plan, normal usage meter, allowance, and exact provider cycle before commit.
- Preserved period/counter usage on replay, failed closed on snapshot/grant conflicts, preserved lifetime and purchased balances, and completed onboarding only after exact period and counter state existed.
- Recorded unsupported Paid trials as `SYNC_ERROR` / `UNSUPPORTED_PAID_TRIAL` with `nextReconcileAt = null`, preserved pending intent, and avoided the one-minute enqueue path.
- Removed the callback's second mutating Paid activation step; successful sync now only schedules the existing best-effort reconciliation job after the committed row proves activation.
- Added regression coverage for the review corrections and retained the exact-period, meter, allowance, replay, balance, provider-null, Partner-failure, and queue-failure cases.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run test -- tests/unit/routes/billing-callback.test.ts tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing-reconciliation.service.test.ts`: passed, 4 files / 120 tests.
- `npm run typecheck`: repository baseline failure, 166 errors across 29 files. The changed-file diagnostics are the pre-existing billing purchase/provider typing diagnostic at `app/services/billing/billing.service.ts:933` and the pre-existing test provider-shape diagnostic at `tests/unit/services/billing.service.test.ts:1153`; the Attempt-2 lines introduce no new diagnostics.
- `npm run build`: passed.
- `git diff --check`: passed.
- `rg -n "moda-interact-admin" app/routes`: passed with no matches.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-003`, branch `task/ARCH-010-SHOPIFY-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-003`, branch `task/ARCH-010-SHOPIFY-003`.
- Implementation Attempt-1 history preserved: `8c3f15beafc659a875caf38d60544a63c90c71ae`.
- Implementation Attempt-2 commit: `53e07302c6be761939268b80cca70959913be73b`, pushed to `origin/task/ARCH-010-SHOPIFY-003`.
- Parent report intermediate commit: `65b38382f86a4ec95c29c232def7755e56dd33ce`, pushed to `origin/task/ARCH-010-SHOPIFY-003`; final parent HEAD is recorded by the follow-up report commit below.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Review Status

**Changes Requested**

Attempt 1 establishes most of the required data-shape work for first Paid activation,
but it does not yet satisfy the architecture's same-observation/transactional
verification contract and it mishandles the unsupported Paid-trial state.

The corrections below are the complete Attempt-2 contract. Do not infer additional
architecture from chat history.

### Accepted Attempt-1 work to preserve

Preserve these behaviours unless an exact correction below requires a local refactor:

- `preparePaidActivation(...)` records pending initial Paid intent instead of
  granting entitlement from the callback parameter;
- Shopify current-plan projection checks the configured normal usage meter;
- first Paid periods use the canonical `(shopId, periodStart, periodEnd)` identity;
- period ownership/snapshot fields and `includedRecoveryCreditsGranted` are written;
- `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` is created only when
  absent and replay does not rewrite committed/reserved/forfeited quantities;
- `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` is created only when
  absent and existing lifetime quantities are preserved;
- CLOSED/incompatible exact periods and incompatible counter grants fail closed;
- successful activation computes
  `max(now, periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)`;
- the existing best-effort billing-reconciliation producer remains the only queue
  path;
- no schema, Shared payload, second queue or Admin dependency was introduced.

### Finding 1 — provider verification and Paid entitlement commit are split across two transactions

The callback currently does:

```text
preparePaidActivation()
  -> syncSubscription()              # provider call + projection transaction
  -> getSubscriptionProjection()
  -> completePaidActivation()        # second transaction
```

The second transaction no longer owns the immutable Partner observation that proved
the current handle/meter/cycle.

It also does not transactionally re-read/require all of:

```text
Shop.status = ACTIVE
pending BillingPlan by pendingPlanId
BillingPlan.active = true
BillingPlan.kind = PAID_METERED
BillingPlan.shopifyPlanHandle = durable pending handle
BillingPlan.shopifyUsageEventHandle still equals a provider-observed usage meter
pendingPlanId = current target plan id
```

Therefore local state can change after Partner verification and before
`completePaidActivation()` commits. Examples include:

```text
Shop ACTIVE -> UNINSTALLED/SUSPENDED
BillingPlan active -> inactive
shopifyPlanHandle changed
shopifyUsageEventHandle changed
includedRecoveryConversationAllowance changed
pending plan id/handle changed
```

This is the same class of race already corrected and architect-accepted in
`ARCH-010-BACKGROUND-003`.

#### Required correction

Files:

```text
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
```

Use **one Partner query only**.

For an initial Paid selection, the provider observation returned by
`this.provider.getActiveSubscription(...)` inside `syncSubscription(...)` must remain
immutable input to the transaction that creates/reuses the first Paid BillingPeriod
and included counter.

Do not perform a second Partner call inside a Prisma transaction.

##### 1.1 Move the successful initial-Paid commit into `syncSubscription(...)`

When all of these are true:

```text
expectedInitialSelection != null
ShopSettings.onboardingCompleted = false
durable Subscription matches the exact initial-selection token
durable current plan is still null / initial activation state
provider current plan handle == expectedInitialSelection.pendingShopifyPlanHandle
```

the `syncSubscription(...)` transaction must:

1. lock the existing initial-activation state using the current lock helper;
2. re-read `Shop` and require `Shop.status === ACTIVE`;
3. re-read `ShopSettings` and require `onboardingCompleted === false`;
4. re-read the current `Subscription` and require the exact token still matches;
5. re-read the pending BillingPlan by `expectedInitialSelection.pendingPlanId`;
6. fail closed unless the transactional plan satisfies exactly:

```text
plan.id === current.pendingPlanId
plan.id === expectedInitialSelection.pendingPlanId
plan.active === true
plan.kind === PAID_METERED
plan.shopifyPlanHandle === current.pendingShopifyPlanHandle
plan.shopifyPlanHandle === expectedInitialSelection.pendingShopifyPlanHandle
plan.shopifyPlanHandle === providerSubscription.planHandle
plan.shopifyUsageEventHandle is non-null/non-blank
providerSubscription.usageEventHandles contains plan.shopifyUsageEventHandle
plan.includedRecoveryConversationAllowance is a non-negative safe integer
```

7. require exact non-null provider cycle:

```text
currentPeriodStart != null
currentPeriodEnd != null
currentPeriodStart < currentPeriodEnd
```

8. create/reuse and validate the exact OPEN BillingPeriod;
9. use only the **transactionally re-read plan** for:
   - `planId`;
   - plan name snapshot;
   - Shopify handle snapshot;
   - kind snapshot;
   - `includedRecoveryCreditsGranted`;
10. create/reuse the unique included-credit counter without resetting any existing
    usage quantities;
11. create the lifetime-Free counter only if absent;
12. preserve purchased-credit and promotional state;
13. update the Subscription current projection, current period pointer and exact
    cycle;
14. clear the initial pending target;
15. clear successful sync-error metadata;
16. set:

```text
nextReconcileAt =
  max(now, provider currentPeriodEnd
           - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)
```

17. set `ShopSettings.onboardingCompleted = true` **last** in the same transaction;
18. return the committed Subscription row.

No intermediate transaction may commit:

```text
onboardingCompleted = true
```

without the exact period and included counter.

##### 1.2 Remove the second mutating Paid activation step from the callback

The Paid callback must not do:

```text
syncSubscription(...)
then
completePaidActivation(...)
```

as two independent mutation transactions.

After the corrected `syncSubscription(...)` returns, treat Paid activation as
successful only if the returned durable row proves:

```text
status === ACTIVE
planId === activation.plan.id
observedShopifyPlanHandle === requestedPlanHandle
billingPeriodId != null
currentPeriodStart != null
currentPeriodEnd != null
pendingShopifyPlanHandle === null
pendingPlanId === null
pendingEffectiveAt === null
nextReconcileAt != null
```

Then:

```text
enqueueBillingSubscriptionReconcileBestEffort(...)
redirect("/app")
```

The Free callback path may continue to use its existing
`completeFreeActivation(...)` logic.

`completePaidActivation(...)` must no longer be a second independently callable
mutation path. Remove it, or reduce it to no mutating role if a compile-time
compatibility reason requires the symbol temporarily. There must be one canonical
Shopify fast-path Paid activation transaction.

### Finding 2 — unsupported Paid trial is not recorded and falls back into the one-minute retry loop

Current `syncSubscription(...)` maps provider `TRIALING` to:

```text
Subscription.status = TRIALING
lastSyncErrorCode = null
```

When the provider supplies the requested Paid plan but has no current billing cycle,
the callback cannot complete activation and then calls
`scheduleInitialFreeReconciliationIfCurrent(...)`, creating the ordinary
one-minute propagation retry.

That directly contradicts ARCH-010 and the accepted BACKGROUND-003 behaviour.

#### Required correction

For an exact pending initial Paid target where provider truth is:

```text
provider plan handle == pending handle
provider status == TRIALING
trialEndsAt is future
currentPeriodStart == null OR currentPeriodEnd == null
```

inside the guarded initial-Paid transaction persist exactly:

```text
Subscription.status = SYNC_ERROR
Subscription.planId = null
Subscription.billingPeriodId = null
Subscription.currentPeriodStart = null
Subscription.currentPeriodEnd = null
Subscription.lastSyncErrorCode = "UNSUPPORTED_PAID_TRIAL"
Subscription.lastSyncErrorAt = now
Subscription.nextReconcileAt = null
pendingPlanId = existing durable pendingPlanId
pendingShopifyPlanHandle = existing durable pendingShopifyPlanHandle
pendingEffectiveAt = existing durable pendingEffectiveAt
ShopSettings.onboardingCompleted = false
```

Do not create:

```text
BillingPeriod
BillingPeriodEntitlementCounter
paid recovery entitlement
synthetic cycle derived from trialEndsAt
```

Do not enqueue a one-minute retry.

The later rotating/background reconciliation path owns re-observation after the trial;
the durable pending intent must remain available for that path.

The callback's generic initial retry scheduler must naturally become a no-op for this
state because the durable `nextReconcileAt` no longer matches the original activation
token.

### Finding 3 — verified configuration failures must not accidentally become a successful Paid activation

The initial Paid fast path must fail closed when provider truth is current but any
required Paid configuration fact is invalid.

At minimum preserve/use these error semantics:

```text
missing configured/provider usage meter -> MISSING_USAGE_METER
unsupported trial/no cycle             -> UNSUPPORTED_PAID_TRIAL
```

For the following states, do not set onboarding complete and do not create a Paid
period/counter:

```text
inactive local pending plan
wrong local pending plan id
durable pending handle != provider current handle
wrong plan kind
missing/blank configured normal meter
provider does not expose configured meter
missing/invalid current cycle
null/negative/non-integer/unsafe included allowance
Shop not ACTIVE
```

When the failure is a durable local/provider configuration incompatibility rather
than provider-null/transport propagation, do not silently convert it into a normal
one-minute initial-propagation retry.

Do not invent new queue contracts.

### Finding 4 — required first-Paid regression evidence is incomplete

Attempt 1's focused count is green, but the task-specific first-Paid matrix is not
fully represented by executable assertions.

Add/strengthen permanent tests with the exact cases below.

#### `tests/unit/services/billing.service.test.ts`

Add tests named/described clearly enough to identify each contract:

1. **transactionally revalidates the pending Paid plan before first activation**

   During the provider observation use a valid plan, but make the transaction re-read
   return one invalid mutation per table row:

```text
active = false
kind != PAID_METERED
shopifyPlanHandle changed
shopifyUsageEventHandle changed/not present in provider usageEventHandles
includedRecoveryConversationAllowance = null
includedRecoveryConversationAllowance = -1
includedRecoveryConversationAllowance = non-integer
includedRecoveryConversationAllowance > Number.MAX_SAFE_INTEGER
```

   Each row must prove:

```text
onboardingCompleted remains false
no BillingPeriod create/update
no included-counter create
no lifetime-counter grant
no successful Subscription activation commit
```

2. **rejects stale pending-plan identity inside the activation transaction**

   Durable:

```text
pendingPlanId = plan-paid-old
```

   Transactional plan/provider resolve another id/handle.

   Prove no activation.

3. **does not activate when Shop becomes inactive before commit**

   Table:

```text
UNINSTALLED
SUSPENDED
```

   Prove no period/counter/onboarding mutation.

4. **creates exact first Paid period and snapshots from the transactionally reread plan**

   Assert exact:

```text
shopId
subscriptionId
planId
shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot = PAID_METERED
includedRecoveryCreditsGranted
periodStart
periodEnd
status = OPEN
```

5. **replay preserves existing included/lifetime quantities**

   Keep the current replay test and additionally assert no update resets:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
lifetime committed/reserved/refunding quantities
```

6. **closed exact historical period fails closed**

   Existing exact period `status = CLOSED`.

   Prove no reopen, no counter mutation, onboarding false.

7. **conflicting exact period snapshot fails closed**

   At minimum table one mismatch for:

```text
subscriptionId
planId
shopifyPlanHandleSnapshot
planKindSnapshot
includedRecoveryCreditsGranted
```

8. **conflicting included counter grant fails closed**

   Existing exact counter has `grantedQuantity != current transactional allowance`.

   Prove no overwrite/reset.

9. **direct-to-Paid creates lifetime Free exactly once and never touches purchases/promotions**

   Add observable mutation spies for:

```text
recoveryCreditPurchase
promotionalCreditGrant
merchantPromotionSelection
```

   Assert no create/update/updateMany/upsert/delete/deleteMany mutation methods are
   called.

10. **unsupported Paid trial records configuration error without one-minute schedule**

    Prove:

```text
status = SYNC_ERROR
lastSyncErrorCode = UNSUPPORTED_PAID_TRIAL
nextReconcileAt = null
pending target preserved
no period
no included counter
no onboarding completion
```

11. **missing provider usage meter cannot activate the initial Paid target**

    This must execute the initial-Paid/token path, not only the generic projection
    test already present.

12. **successful first Paid activation stores the exact drain-window schedule**

    Freeze system time and assert the exact Date:

```text
max(now, periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS)
```

#### `tests/unit/routes/billing-callback.test.ts`

13. **Paid callback uses one canonical Paid activation mutation path**

    Prove the callback:

```text
preparePaidActivation called once
syncSubscription called once with the Paid token
does not call a second Paid activation mutator
enqueues only after the returned Subscription proves complete Paid activation
```

14. **Paid provider-null keeps pending intent and schedules the existing bounded retry**

    Use a Paid token/plan, not the existing Free-only retry evidence.

15. **Paid Partner transport failure keeps pending intent and schedules the existing bounded retry**

    Use a Paid token/plan and assert `partnerErrorAt`.

16. **unsupported Paid trial does not enqueue the one-minute retry**

    Return the persisted `SYNC_ERROR / UNSUPPORTED_PAID_TRIAL / nextReconcileAt=null`
    projection from the service path and prove:

```text
no activation success
no reconcile enqueue from the callback
redirect("/app")
```

17. **successful Paid queue hint failure cannot undo activation**

    Do not make the callback mock violate the best-effort producer contract. Instead,
    keep/use the existing producer test that proves queue `.add()` rejection resolves
    successfully, and add a callback assertion that successful Paid activation is
    considered complete before the best-effort enqueue result is relevant.

#### Static safety check

Run:

```bash
rg -n "moda-interact-admin" app/routes
```

Expected result: no matches.

### Validation required for Attempt 2

From `moda-interact` run:

```bash
npm run prisma:validate
npm run prisma:generate

npm run test -- \
  tests/unit/routes/billing-callback.test.ts \
  tests/unit/services/billing.service.test.ts \
  tests/unit/services/shopify-billing.provider.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts

npm run typecheck
npm run build
git diff --check
```

Report exact test pass/fail/skip counts.

For typecheck:

- record the repository-wide total;
- prove no diagnostic originates from Attempt-2 changed files;
- do not modify unrelated baseline files merely to reduce the 168-error baseline.

### Allowed implementation scope

Attempt 2 may modify only:

```text
moda-interact/app/routes/app/billing/callback/route.tsx
moda-interact/app/services/billing/billing.service.ts
moda-interact/tests/unit/routes/billing-callback.test.ts
moda-interact/tests/unit/services/billing.service.test.ts
```

`tests/unit/services/billing-reconciliation.service.test.ts` may be modified only if
an additional assertion is needed to reuse the existing best-effort queue-failure
evidence.

Do not modify:

```text
database/prisma/**
Shared contracts/package version
Background
Admin
Messaging
Gateway
recovery-credit purchase implementation
promotion implementation
plan-change/upgrade/downgrade flows
rollover implementation
```

If satisfying the corrections requires a schema/shared-contract/background change,
STOP and return the exact dependency gap to `moda_architect`.

### Workflow evidence correction

The current handoff summary reports parent report commit:

```text
6e7f4d4
```

while the uploaded task file records:

```text
911cc2b84dd598b76d51198f4444081a5c2cea66
```

Attempt 2 must record the **actual full parent report/HEAD SHA** and explain if one
value was an intermediate report commit. Do not leave contradictory publication
evidence in the Completion Report.

Also preserve:

```text
implementation Attempt-1 history: 8c3f15beafc659a875caf38d60544a63c90c71ae
```

### Reclaim / stop condition

Return this SAME task through `/moda-task`.

The current attempt remains:

```text
attempt: 1
```

The next authorized claim must increment it to **Attempt 2 exactly once**.

After implementing only the corrections above, run validation, update the Completion
Report, set the task back to `status: review`, clear `executor`/`claimed_at`,
commit/push both mirrored task branches, then STOP and return to `moda_architect`.

Do not start `ARCH-010-SHOPIFY-004`, `ARCH-010-SHOPIFY-007`, or any system-test task.

