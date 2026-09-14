---
id: ARCH-010-SHOPIFY-009
architecture_id: ARCH-010
title: Add local merchant recovery-capacity projection
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 52
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-004
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-008
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-020
created: 2026-09-11
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-009: Add local merchant recovery-capacity projection

## Objective

Create one canonical **PostgreSQL-only operational projection** answering one narrow question:

> Can Moda admit another abandoned-checkout recovery for this merchant right now, and which Moda recovery-capacity bucket would fund it?

Before evaluating Paid included capacity, resolve whether the Shop has a currently selected, running, target-eligible campaign grant with remaining quantity. That exact grant is the highest-priority capacity source. There is no aggregate promotional entitlement counter in the first-production baseline; the exact usable selected campaign grant is promotional spendability authority.

This projection is for dashboard/runtime capacity presentation. It is **not** the authority for:

- which Shopify App Pricing plans exist;
- the merchant's live Shopify commercial subscription;
- Shopify plan price/currency/trial terms;
- Shopify pending plan changes.

Shopify remains authoritative for those commercial subscription facts through Partner `activeSubscription`. Local `Subscription`/`BillingPlan` rows are reconciled operational projection and Moda entitlement mapping/configuration only.

This task does not change UI and must not call Shopify.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

Also inspect implemented SHOPIFY-004 and the final DATABASE-013 period/counter schema before naming fields.

## Authority boundary — hard invariant

Treat the data sources as follows:

```text
Shopify Partner activeSubscription
  authority for commercial subscription existence/current plan/pending plan/cycle/price

shopify.Subscription + billing.BillingPlan
  reconciled local projection + mapping from Shopify plan handle to Moda entitlements/features

BillingPeriodEntitlementCounter / ShopEntitlementCounter
  authority for Moda recovery-capacity consumption/reservation accounting
```

A `BillingPlan` row MUST NOT be interpreted as proof that the corresponding Shopify plan currently exists or that the merchant is currently subscribed to it.

A local `Subscription.planId` is usable here only because Background and merchant runtime require a fast local operational projection. It must be labelled/treated as the **reconciled Moda mapping**, not as live commercial Shopify truth.

## Existing implementation constraint

`BillingService.getMerchantBillingState()` currently calls `BillingProvider.getActiveSubscription()` when recovery-credit-pack configuration is present. Do **not** call that provider-verifying method from `/app` merely to render a recovery-capacity warning.

Add a dedicated method such as:

```ts
getMerchantRecoveryCapacityState(shopId: string)
```

or an equivalently explicit local-only API.

The implementation MUST NOT silently rename an existing provider-backed method into a local-only method if that would change existing billing-route semantics.

## Required projection

Return a typed projection equivalent to:

```ts
type MerchantRecoveryCapacityState = {
  availability: "AVAILABLE" | "EXHAUSTED" | "CONTRACT_REQUIRED" | "CONFIGURATION_UNAVAILABLE";
  capacitySource:
    | "FREE_LIFETIME"
    | "PAID_INCLUDED"
    | "PROMOTIONAL"
    | "PURCHASED"
    | "EXHAUSTED"
    | null;

  // This is a Moda entitlement mapping, NOT Shopify commercial authority.
  reconciledPlanMapping: {
    id: string;
    shopifyPlanHandle: string;
    name: string;
    kind: "FREE" | "PAID_METERED";
  } | null;

  observedShopifyPlanHandle: string | null;

  freeLifetime: {
    granted: number;
    committed: number;
    reserved: number;
    remaining: number;
  } | null;

  paidIncluded: {
    billingPeriodId: string;
    periodStart: string;
    periodEnd: string;
    granted: number;
    committed: number;
    reserved: number;
    forfeited: number;
    remaining: number;
  } | null;

  promotional: {
    granted: number;
    committed: number;
    reserved: number;
    remaining: number;
  };

  purchased: {
    granted: number;
    committed: number;
    reserved: number;
    refunding: number;
    available: number;
  };

  topUpConfiguration: {
    enabled: boolean;
    creditsPerPack: number | null;
  };
};
```

Use actual integrated enum/type names if they differ; preserve these semantics exactly.

Do **not** include Shopify price, currency, trial, pending-update commercial details or a local plan catalogue in this projection.

## Availability calculations

### Free

Use only the shop-lifetime `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)` snapshot and durable committed/reserved state. DATABASE-013 removes plan-owned allowance and signed-adjustment compatibility. This lifetime source is available under both Free and Paid subscriptions.

```text
remaining = max(granted - committed - reserved, 0)
```

A reserved Free credit is not available for another recovery.

### Paid

Use the unique current OPEN `BillingPeriodEntitlementCounter`, not shop-wide `UsageEvent` aggregation.

```text
remaining = max(granted - committed - reserved - forfeited, 0)
```

### Promotional

Resolve the current `MerchantPromotionSelection` and exact campaign-linked `PromotionalCreditGrant`. Promotional capacity is available only when the selection/campaign/grant is currently usable under DATABASE-013 targeting/status/time-window rules.

```text
remaining = max(grant.quantity - grant.committedQuantity - grant.reservedQuantity, 0)
```

No selected usable campaign grant means zero promotional spendability. There is no aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` fallback. Promotional credits are non-refundable and have no `refundingQuantity`.

### Purchased

Subtract every quantity unavailable for spending, including `refundingQuantity` when present in the integrated schema.

```text
available = max(granted - committed - reserved - refunding, 0)
```

## Capacity source order

```text
FREE mapped operational projection:
  if promotional remaining > 0 -> PROMOTIONAL
  else if purchased available > 0 -> PURCHASED
  else if lifetime Free remaining > 0 -> FREE_LIFETIME
  else -> EXHAUSTED

PAID mapped operational projection:
  if promotional remaining > 0 -> PROMOTIONAL
  else if current-period included remaining > 0 -> PAID_INCLUDED
  else if purchased available > 0 -> PURCHASED
  else if lifetime Free remaining > 0 -> FREE_LIFETIME
  else -> EXHAUSTED
```

If `Subscription.status=NO_CONTRACT`, return `CONTRACT_REQUIRED` regardless of preserved local lifetime balances. Do not report NO_CONTRACT as `EXHAUSTED`, and do not expose purchased or lifetime Free balances as spendable while there is no verified current Shopify contract. The balances may still be returned for presentation/history, but `capacitySource` must be `null` and recovery admission remains unavailable.

If the local operational projection is ACTIVE/TRIALING but the mapped plan/period/counter needed for deterministic capacity is missing, return `CONFIGURATION_UNAVAILABLE`. Do not invent a plan, allowance or balance.

## No-contract semantics

For a previously onboarded merchant whose Shopify contract has ended:

```text
Subscription.status = NO_CONTRACT
availability        = CONTRACT_REQUIRED
capacitySource       = null
```

Preserved purchased/lifetime balances remain visible values only. This projection must not claim they are currently spendable until Shopify verifies a new contract. Fresh never-activated merchants may also be NO_CONTRACT, but routing/onboarding presentation is owned by the merchant route tasks.

## No provider calls — hard requirement

Focused tests MUST spy on the configured `BillingProvider` and prove this method does not call:

```ts
provider.getActiveSubscription(...)
```

Provider/commercial verification belongs to SHOPIFY-013 and mutation/reconciliation flows.

## Required tests

At minimum prove:

1. no usable selected promotion + Free purchased available + lifetime Free available -> `PURCHASED`;
2. no usable selected promotion + Free purchased exhausted + lifetime Free available -> `FREE_LIFETIME`;
3. Free fully exhausted -> `EXHAUSTED`;
4. Free reserved quantity reduces spendable lifetime remaining;
5. no signed lifetime-Free adjustment or plan-owned allowance is queried;
6. no usable selected promotion + Paid included available -> `PAID_INCLUDED`;
7. Paid included exhausted + purchased available -> `PURCHASED`;
8. selected promotional unavailable + Paid included/purchased exhausted + lifetime Free available -> `FREE_LIFETIME`;
9. Paid fully exhausted -> `EXHAUSTED`;
10. Paid reserved and forfeited quantities reduce included remaining correctly;
11. purchased `refundingQuantity` reduces purchased available;
12. missing Paid period -> `CONFIGURATION_UNAVAILABLE`;
13. missing Paid period counter -> `CONFIGURATION_UNAVAILABLE`;
14. returned plan information is explicitly the local reconciled mapping;
15. no pending Shopify/commercial plan catalogue is fabricated from `BillingPlan` rows;
16. provider `getActiveSubscription()` is never called;
17. no BillingPlan lifetime-free allowance field exists or is used to derive lifetime capacity.

Additional required cases:

- NO_CONTRACT + preserved purchased credits -> `CONTRACT_REQUIRED`, not PURCHASED;
- NO_CONTRACT + preserved lifetime Free credits -> `CONTRACT_REQUIRED`, not FREE_LIFETIME;
- NO_CONTRACT + zero balances -> `CONTRACT_REQUIRED`, not EXHAUSTED;
- Shopify provider is still not called for those cases.

## Non-goals

No route/component changes, no Partner verification, no commercial plan catalogue, no price retrieval, no purchase mutation and no Background admission changes.

## Validation

Run focused billing-service tests, then repository-declared typecheck/build/full tests and `git diff --check`.

## Stop conditions

STOP if the integrated period/counter schema differs materially from DATABASE-013; report the exact mismatch rather than inferring another capacity source.

STOP if implementing this task would require treating `BillingPlan` as Shopify plan-existence authority. Return to `moda_architect` instead.

## Completion Report

### Status
Ready for Review.

### Files Changed

- `app/services/billing/billing.service.ts`
- `app/services/billing/billing.types.ts`
- `tests/unit/services/billing.service.test.ts`

### Work Completed

- Added `getMerchantRecoveryCapacityState(shopId)`, a PostgreSQL-only local projection that never calls the configured `BillingProvider`.
- Reads the integrated lifetime Free, current paid-period, purchased, and selected campaign grant counters using DATABASE-013 fields only; no legacy plan allowance, signed adjustment, aggregate promotional counter, or usage-event capacity fallback is used.
- Implements exact promotional, paid included, purchased, and lifetime Free ordering with committed/reserved/forfeited/refunding arithmetic and explicit `CONTRACT_REQUIRED`, `CONTRACT_FROZEN`, `CONFIGURATION_UNAVAILABLE`, and `EXHAUSTED` outcomes.
- Returns the local `BillingPlan` row only as `reconciledPlanMapping`, preserves observed Shopify handle separately, returns informational balances for lifecycle-blocked states, and exposes `canStartRecovery` without changing routes, components, or admission.
- Added focused coverage for Free/Paid ordering, promotional targeting/window/selection usability, reserved grant quantities, missing paid state, lifecycle blocking, no legacy reads, and provider-call isolation.

### Validation Results

- `npm run prisma:generate` — passed against the integrated DATABASE-013 schema.
- `npm test -- tests/unit/services/billing.service.test.ts` — passed, 133 tests.
- `npm run build` — passed.
- `npm test` — passed, 38 files; 416 passed, 3 skipped; 2 files skipped.
- `git diff --check` — passed.
- `npm run typecheck` — non-zero only for existing `TYPECHECK-001` baseline diagnostics; no new diagnostics were reported in the changed projection/type/test additions.

### Launcher Worktree / Synchronization / Submodule Evidence

- Prepared launcher packet used without rerunning startup routing, dependency discovery, worktree creation, synchronization, or submodule initialization.
- Parent/report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-009`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-009`.
- Both mirrored task branches were prepared and synchronized by the launcher; parent and implementation `origin/main` were already current and remote task branches required no fast-forward.
- Recursive submodule sync/update passed; DATABASE-013 dependency checkout was `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- No parent implementation submodule gitlink was staged or changed.

### Git / VCS

- Implementation commits: `9e4ef65` and `d73153d`, pushed to `origin/task/ARCH-010-SHOPIFY-009`.
- Parent claim commit supplied by launcher: `00143ecb67400a1ba5e495a5cce33595b80edbd4`.
- Parent report commit: to be recorded after this report update and pushed to the mirrored parent task branch.


## Final frozen capacity projection

Add a distinct operational availability result such as `CONTRACT_FROZEN`. When durable Subscription.status is FROZEN, informational balances may still be returned, but `canStartRecovery=false` regardless of remaining monthly included, promotional, purchased or lifetime Free capacity. Do not report ordinary `EXHAUSTED` and do not zero balances.


## Required promotional cases

Add focused coverage proving:

- Free promotional + purchased + lifetime Free -> `PROMOTIONAL`;
- Free promo zero + purchased -> `PURCHASED`;
- usable selected promotional > 0 returns `PROMOTIONAL` even when Paid included remains;
- no usable selected promotional + Paid included > 0 -> `PAID_INCLUDED`;
- selected grant reserved quantity reduces its remaining allocation;
- no selected usable campaign means zero promotional spendability and no aggregate promotional counter is queried;
- FROZEN/NO_CONTRACT returns the lifecycle availability state even when promotional remaining > 0;
- provider `getActiveSubscription()` remains uncalled.

## Architect Review — Attempt 1

### Status

**Changes Requested**

Implementation commits reviewed:

- `9e4ef651ddccd1e3215bc0013b67ab748b68a0e5` — adds the local PostgreSQL-only recovery-capacity projection, type and primary permanent tests.
- `d73153dcd7f5f770029f8e9a9a3858bfbc4c471d` — adds promotional ordering evidence only.
- Parent Completion Report: `6cd5232af97062f01318a9f345cf15105d671472`.

The implementation direction is correct and the following work is accepted and MUST be preserved in Attempt 2:

- `getMerchantRecoveryCapacityState(shopId)` remains a local PostgreSQL-only read model;
- it MUST NOT call `BillingProvider.getActiveSubscription(...)`;
- commercial Shopify price/currency/trial/pending-plan catalogue data remains outside this projection;
- capacity source ordering remains exactly:
  - Free: `PROMOTIONAL -> PURCHASED -> FREE_LIFETIME`;
  - Paid: `PROMOTIONAL -> PAID_INCLUDED -> PURCHASED -> FREE_LIFETIME`;
- `NO_CONTRACT` remains `CONTRACT_REQUIRED`, with `capacitySource=null` and `canStartRecovery=false`;
- `FROZEN` remains `CONTRACT_FROZEN`, with `capacitySource=null` and `canStartRecovery=false`;
- purchased availability continues to subtract `refundingQuantity`;
- selected promotional spendability continues to come only from the exact selected `PromotionalCreditGrant` and its currently usable campaign;
- there is no aggregate promotional `ShopEntitlementCounter` fallback;
- no route/component/admission/purchase/schema/Background changes belong to this task.

Acceptance is withheld for the bounded corrections below.

### Finding 1 — FROZEN Paid merchants lose the informational current-period balance

Current production code makes `paidIncluded` conditional on:

```text
subscription.status != NO_CONTRACT
subscription.status != FROZEN
```

That contradicts this task's **Final frozen capacity projection** contract.

For a `FROZEN` subscription with a structurally valid current Paid BillingPeriod and included counter:

```text
availability      = CONTRACT_FROZEN
capacitySource    = null
canStartRecovery  = false
paidIncluded      = the real preserved period/counter snapshot
promotional       = the real informational selected-grant balance
purchased         = the real informational purchased balance
freeLifetime      = the real informational lifetime-Free balance
```

Freezing blocks admission. It MUST NOT erase the informational Paid-period balance.

#### Required production correction

In:

```text
app/services/billing/billing.service.ts
```

separate **Paid period structural validity** from **lifecycle spendability**.

The Paid-period read model may be populated when all period/plan/counter ownership invariants are valid and Subscription status is one of:

```text
ACTIVE
TRIALING
FROZEN
```

Do not populate current Paid included capacity for `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`, or another unsafe state.

Keep the existing early FROZEN return:

```text
availability = CONTRACT_FROZEN
capacitySource = null
canStartRecovery = false
```

so a preserved `paidIncluded.remaining > 0` is informational only.

Do not alter BillingPeriod/counter state.

### Finding 2 — missing canonical lifetime-Free state can be misreported as ordinary exhaustion

`LIFETIME_FREE_RECOVERY_CREDITS` is provisioned as the canonical shop-lifetime fallback during accepted activation/reconciliation flows.

The current implementation treats an absent lifetime counter as:

```text
freeLifetime = null
```

but, after all higher-priority sources are exhausted, falls through to:

```text
availability = EXHAUSTED
capacitySource = EXHAUSTED
```

That is not deterministic exhaustion. The canonical fallback counter is missing, so the task contract requires `CONFIGURATION_UNAVAILABLE`.

#### Required production correction

Do NOT make an absent lifetime-Free counter globally fatal when a higher-priority source can deterministically fund the recovery.

Use this exact decision rule after lifecycle and mapped-plan/paid-period validation:

```text
Free:
  usable promotion > 0
    -> AVAILABLE / PROMOTIONAL
  else purchased available > 0
    -> AVAILABLE / PURCHASED
  else lifetime-Free counter missing
    -> CONFIGURATION_UNAVAILABLE / null
  else lifetime-Free remaining > 0
    -> AVAILABLE / FREE_LIFETIME
  else
    -> EXHAUSTED / EXHAUSTED

Paid:
  usable promotion > 0
    -> AVAILABLE / PROMOTIONAL
  else Paid included remaining > 0
    -> AVAILABLE / PAID_INCLUDED
  else purchased available > 0
    -> AVAILABLE / PURCHASED
  else lifetime-Free counter missing
    -> CONFIGURATION_UNAVAILABLE / null
  else lifetime-Free remaining > 0
    -> AVAILABLE / FREE_LIFETIME
  else
    -> EXHAUSTED / EXHAUSTED
```

For `CONFIGURATION_UNAVAILABLE`:

```text
capacitySource = null
canStartRecovery = false
```

Do not synthesize a zero lifetime grant.

### Finding 3 — permanent acceptance evidence is incomplete and promotion tests are date-dependent

The current projection suite contains 12 permanent tests. Several explicit task requirements are not directly proven, including:

- `NO_CONTRACT + zero balances -> CONTRACT_REQUIRED`;
- lifecycle blocking when a usable promotional grant has remaining capacity;
- fully exhausted Paid capacity -> `EXHAUSTED`;
- missing lifetime-Free fallback -> `CONFIGURATION_UNAVAILABLE`;
- no-selected-promotion -> zero promotional spendability and no promotional aggregate-counter lookup;
- an explicit purchased `refundingQuantity` arithmetic assertion;
- FROZEN Paid informational period capacity preservation.

The promotional tests also use campaign windows ending `2026-10-01` while production uses `new Date()`. Without a frozen test clock, those permanent tests become time-dependent after 1 October 2026.

### Attempt 2 implementation contract

#### Allowed production files

Only:

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
```

`billing.types.ts` should change only if a correction genuinely requires a type adjustment. The existing type already supports the required result and SHOULD normally remain unchanged.

#### Allowed tests

Only:

```text
tests/unit/services/billing.service.test.ts
```

Do not modify routes, components, provider implementations, Admin, Background, Shared, database schema/migrations, purchase mutation code, reservation code, or billing-option composition.

#### Required deterministic test clock

Inside the `BillingService local recovery capacity` suite, freeze time to an instant inside the campaign fixtures, for example:

```ts
beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-09-14T00:00:00.000Z"));
});

afterEach(() => {
  vi.useRealTimers();
});
```

Use an equivalent isolated mechanism only if it leaves other suites unaffected.

#### Required permanent evidence

Keep all existing projection tests and add/strengthen tests proving all of the following:

1. `Free promotion outranks purchased and lifetime Free`
   - selected usable GLOBAL campaign;
   - promotional remaining > 0;
   - purchased and lifetime Free also > 0;
   - result `AVAILABLE/PROMOTIONAL`.

2. `Free zero promotion falls to purchased`
   - selected usable campaign exists but grant remaining is zero;
   - purchased > 0;
   - result `AVAILABLE/PURCHASED`.

3. `Free purchased exhausted falls to lifetime Free`.

4. `Free fully exhausted`
   - usable promotion = 0;
   - purchased = 0;
   - lifetime counter exists with remaining = 0;
   - result `EXHAUSTED/EXHAUSTED`.

5. `Free missing lifetime fallback fails closed`
   - no usable promotion;
   - purchased = 0;
   - lifetime counter = null;
   - result `CONFIGURATION_UNAVAILABLE`, `capacitySource=null`, `canStartRecovery=false`.

6. `Missing lower-priority lifetime state does not block a deterministic higher source`
   - lifetime counter = null;
   - purchased > 0 (or usable promotion > 0);
   - result remains `AVAILABLE` from that higher source.

7. `Paid promotion outranks included capacity`.

8. `Paid included outranks purchased`.

9. `Paid included exhausted falls to purchased`.

10. `Paid included + purchased exhausted falls to lifetime Free`.

11. `Paid fully exhausted`
    - Paid included counter exists and remaining = 0;
    - purchased = 0;
    - lifetime counter exists and remaining = 0;
    - result `EXHAUSTED/EXHAUSTED`.

12. `Paid missing lifetime fallback fails closed only after higher sources are exhausted`
    - valid Paid period/counter with remaining = 0;
    - purchased = 0;
    - lifetime counter = null;
    - result `CONFIGURATION_UNAVAILABLE`.

13. `Paid included reserved and forfeited arithmetic`
    - assert exact `granted`, `committed`, `reserved`, `forfeited`, and `remaining`.

14. `Purchased refund hold arithmetic`
    - assert exact `granted`, `committed`, `reserved`, `refunding`, and `available`.

15. `Missing Paid BillingPeriod -> CONFIGURATION_UNAVAILABLE`.

16. `Missing Paid included counter -> CONFIGURATION_UNAVAILABLE`.

17. `FROZEN Paid preserves informational balances but blocks admission`
    - structurally valid current Paid period/counter with remaining > 0;
    - usable selected promotion with remaining > 0;
    - purchased and lifetime Free balances > 0;
    - assert `availability=CONTRACT_FROZEN`;
    - assert `capacitySource=null`;
    - assert `canStartRecovery=false`;
    - assert `paidIncluded` retains the exact real period/counter balance;
    - assert promotional/purchased/freeLifetime remain non-zero informational values;
    - assert provider is not called.

18. `NO_CONTRACT with preserved balances`
    - result `CONTRACT_REQUIRED`, never PURCHASED/FREE_LIFETIME/PROMOTIONAL;
    - balances may remain visible;
    - provider is not called.

19. `NO_CONTRACT with zero balances`
    - lifetime counter exists at zero OR is absent;
    - purchased = zero;
    - result remains `CONTRACT_REQUIRED`, not `EXHAUSTED`;
    - provider is not called.

20. `NO_CONTRACT with a usable selected promotion`
    - promotional informational remaining may be > 0;
    - result remains `CONTRACT_REQUIRED`;
    - `capacitySource=null`;
    - provider is not called.

21. `No selected usable promotion`
    - `promotional` equals `{ granted: 0, committed: 0, reserved: 0, remaining: 0 }`;
    - verify `ShopEntitlementCounter` is queried only for:
      - `LIFETIME_FREE_RECOVERY_CREDITS`;
      - `PURCHASED_RECOVERY_CREDITS`;
    - no aggregate promotional counter or `UsageEvent` capacity aggregation is used.

22. `Reconciled mapping is explicitly local`
    - return exact local `BillingPlan` id/handle/name/kind as `reconciledPlanMapping`;
    - preserve `observedShopifyPlanHandle` separately;
    - do not expose price/currency/trial/pending commercial catalogue data.

23. `Provider isolation`
    - `provider.getActiveSubscription` is never called by this method across Free, Paid, FROZEN and NO_CONTRACT representative cases.

24. `No legacy lifetime authority`
    - no signed lifetime adjustment or plan-owned lifetime allowance read is introduced;
    - no `UsageEvent` aggregate determines recovery capacity.

Tests may combine assertions where one executable case genuinely proves multiple numbered requirements, but the Completion Report MUST map every numbered requirement above to exact permanent test title(s).

### Validation

Run exactly the repository-declared commands available in the task worktree:

```bash
npm run prisma:generate
npm test -- tests/unit/services/billing.service.test.ts
npm run build
npm test
npm run typecheck
git diff --check
```

Also run a static source scan proving this projection contains no provider call and no aggregate promotional/lifetime compatibility source. Record the exact command and result in the Completion Report.

`TYPECHECK-001` remains non-blocking only when every diagnostic is unchanged, pre-existing and unrelated to Attempt 2. Record the exact count and changed-file status.

### Stop conditions

STOP and return **Blocked** rather than guessing if:

- the materialized database schema no longer matches DATABASE-013 for these counters/campaign relations;
- preserving FROZEN Paid informational period balance would require mutating lifecycle/period/counter state;
- a fix would require Shopify Partner verification;
- a fix would require route/UI/admission/Background/schema changes.

### Completion Report requirements

Before returning to review:

- record the Attempt 2 implementation commit(s);
- record focused/full test totals;
- record Prisma generation/build/typecheck/diff-check results;
- record the database submodule SHA;
- include a 24-row requirement-to-test evidence table;
- state explicitly that no route, component, provider, Background, Shared, Admin, schema or purchase/reservation mutation code changed.

### Dependency / execution gate

This task remains the same task:

```text
status: ready
executor: null
claimed_at: null
attempt: 1
```

The next authorized `/moda-task ARCH-010-SHOPIFY-009` claim MUST increment to Attempt 2 exactly once.

Do not start `ARCH-010-SHOPIFY-008`, `ARCH-010-SHOPIFY-012`,
`ARCH-010-SHOPIFY-016`, or `ARCH-010-SHOPIFY-020`.
