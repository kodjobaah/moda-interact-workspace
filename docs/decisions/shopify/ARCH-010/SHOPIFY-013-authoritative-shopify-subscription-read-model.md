---
id: ARCH-010-SHOPIFY-013
architecture_id: ARCH-010
title: Expose authoritative Shopify commercial subscription read model
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 52
executor: copilot
claimed_at: 2026-09-11T22:09:08Z
attempt: 1
depends_on:
  - ARCH-008-SHOPIFY-001
enables:
  - ARCH-010-SHOPIFY-011
  - ARCH-010-SHOPIFY-012
  - ARCH-010-SHOPIFY-014
  - ARCH-010-SHOPIFY-015
  - ARCH-010-SHOPIFY-016
  - ARCH-010-SHOPIFY-018
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-013: Expose authoritative Shopify commercial subscription read model

## Objective

Expose the live Shopify App Pricing subscription facts that merchant billing-management UI requires, without treating local `BillingPlan` rows as the commercial plan catalogue.

Shopify Partner `activeSubscription(appId:, shopId:)` is authoritative for:

- whether an active App Pricing contract exists;
- the current Shopify plan handle;
- the current flat-rate subscription price/currency;
- billing interval;
- current billing cycle;
- trial end;
- `cancelAtEndOfCycle`;
- pending plan handle/price/effective cycle.

Moda PostgreSQL remains authoritative only for Moda-owned entitlement mapping, features and credit accounting.

This task is service/provider-contract only. It does not change UI.

## Inspect before editing

```text
app/services/billing/billing.types.ts
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.service.ts
tests/unit/services/shopify-billing.provider.test.ts
tests/unit/services/billing.service.test.ts
```

Also inspect every current consumer of `ProviderSubscription` before changing its shape.

## Current implementation fact

`ShopifyBillingProvider.getActiveSubscription()` already queries Shopify fields including:

```text
billingPeriod
cancelAtEndOfCycle
trialEndsAt
currentBillingCycle
items.handle
items.description
items.price
pendingUpdate.billingPeriod
pendingUpdate.items.handle
pendingUpdate.items.price
```

but the returned `ProviderSubscription` currently discards the active flat-rate plan's description/price/currency and billing interval.

Do not add a second Partner query to retrieve information already present in this response.

## Required provider contract extension

Extend the existing provider result **backwards-compatibly**. Preserve current fields such as `planHandle`, `pendingPlanHandle`, `usageEventHandles`, current period dates and provider usage snapshots because existing reconciliation/purchase logic consumes them.

Add explicit commercial fields equivalent to:

```ts
type ProviderFlatRatePlan = {
  handle: string;
  description: string | null;
  price: {
    amount: string;
    currency: string | null;
  };
};

type ProviderPendingFlatRatePlan = {
  handle: string;
  price: {
    amount: string;
    currency: string | null;
  };
  effectiveAt: Date | null;
};

interface ProviderSubscription {
  // existing fields remain
  billingPeriod: "EVERY_30_DAYS" | "ANNUAL" | string;
  currentFlatRatePlan: ProviderFlatRatePlan;
  pendingFlatRatePlan: ProviderPendingFlatRatePlan | null;
}
```

Use the repository's actual typing conventions, but preserve the semantics exactly.

The current provider invariant remains:

```text
exactly one active flat-rate item is required
```

Do not infer the current plan from local `BillingPlan` rows.

## Required service read model

Add one provider-backed method with an explicit name such as:

```ts
getMerchantShopifySubscriptionState(shopId: string)
```

The method must:

1. load the durable Shop and require `shopifyShopId`;
2. call `provider.getActiveSubscription()` exactly once;
3. if Shopify returns `null`, return an explicit `NO_ACTIVE_SUBSCRIPTION` result;
4. if Shopify returns a subscription, preserve the provider's current/pending commercial state exactly;
5. look up the current Shopify plan handle in local `BillingPlan` only to determine whether Moda has an entitlement mapping;
6. look up the pending Shopify plan handle separately when present;
7. never replace/override the Shopify handle/price/cycle with local data.

Return a typed result equivalent to:

```ts
type MerchantShopifySubscriptionState =
  | {
      status: "NO_ACTIVE_SUBSCRIPTION";
      subscription: null;
    }
  | {
      status: "ACTIVE_SUBSCRIPTION";
      subscription: {
        planHandle: string;
        description: string | null;
        price: { amount: string; currency: string | null };
        billingPeriod: string;
        currentPeriodStart: string | null;
        currentPeriodEnd: string | null;
        trialEndsAt: string | null;
        cancelAtEndOfCycle: boolean;
        pendingUpdate: {
          planHandle: string;
          price: { amount: string; currency: string | null };
          effectiveAt: string | null;
        } | null;
      };
      modaMapping: {
        id: string;
        name: string;
        kind: "FREE" | "PAID_METERED";
      } | null;
      mappingStatus: "MAPPED" | "UNMAPPED";
      pendingModaMapping: {
        id: string;
        name: string;
        kind: "FREE" | "PAID_METERED";
      } | null;
    };
```

Exact names may follow repository conventions. Semantics must not change.

## Unmapped Shopify plan — required behaviour

This case must be first-class:

```text
Shopify activeSubscription planHandle = premium_2026
BillingPlan(shopifyPlanHandle = premium_2026) does not exist
```

Required result:

```text
Shopify contract exists = true
Shopify plan handle/price/cycle preserved = true
mappingStatus = UNMAPPED
modaMapping = null
```

Do NOT convert this to `NO_ACTIVE_SUBSCRIPTION`.
Do NOT pretend that the Shopify plan does not exist.
Do NOT create a `BillingPlan` automatically.

## Partner/API failure

If the Partner request fails/timeouts/throttles, throw/return the repository's existing verification failure path. Do not fall back to local `Subscription.plan` and present it as live Shopify commercial truth.

UI handling of this failure belongs to SHOPIFY-012.

## Full Shopify plan catalogue — explicit non-goal

`activeSubscription` returns the merchant's live current/pending contract, not an enumerable catalogue of every plan configured in Partner Dashboard.

This task MUST NOT:

- treat `BillingPlan.findMany()` as the Shopify plan catalogue;
- invent an API for all available Shopify plans;
- scrape the hosted pricing page;
- add Admin plan-creation behaviour.

Plan discovery/selection remains Shopify-hosted through `/app/billing/select`.


## Free + usage-meter subscription is first-class

Do not assume that `BillingPlan.kind = FREE` means there is no Shopify billing cycle or no usage item. A Moda Free plan that permits recovery top-ups is configured in Shopify App Pricing as a zero-recurring/usage-enabled plan and can carry the recovery-credit-pack meter.

For an active Free provider subscription, preserve exactly the same provider facts as for Paid:

```text
current flat-rate Free plan handle / £0 price
currentBillingCycle start/end
active usage items including recovery-credit-pack meter
pendingUpdate when present
```

The service must not discard `currentBillingCycle` or usage items because the mapped Moda plan kind is Free. It also must not reinterpret the provider billing cycle as a monthly Free recovery allowance.

## Usage-item exposure for top-up billing

In addition to current/pending flat-rate commercial state, preserve the provider `TieredPrice` item information required to identify the current recovery-credit-pack meter without another Partner API request.

Expose current active usage items equivalent to:

```ts
{
  handle: string;
  description: string | null;
  price: {
    kind: "TIERED";
    active: boolean;
    currency: string | null;
    tiersMode: string;
    tiers: Array<{
      upTo: number | null;
      amountPerUnit: string;
      amount: string;
    }>;
  };
  usage: {
    quantity: number | null;
    costAmount: string | null;
    costCurrency: string | null;
  } | null;
}
```

Use actual provider type names. Do not infer which item is the pack meter inside the generic provider; SHOPIFY-014 matches the exact locally configured pack handle to this provider list.

Do not convert provider tier pricing into local `BillingPlan` monetary fields.

## Required tests

At minimum prove:

0. active mapped Free subscription preserves exact currentBillingCycle, £0/current flat-rate commercial data and active usage items;
0a. active Free recovery-credit-pack usage item is exposed identically to a Paid pack usage item and is not filtered out because the plan is Free;

1. current flat-rate amount/currency/description are preserved from the provider response;
2. billing period is preserved;
3. current billing-cycle dates are preserved;
4. `cancelAtEndOfCycle` is preserved;
5. pending flat-rate handle/price/effective date are preserved;
6. usage-meter handles/snapshots remain unchanged for existing consumers;
7. exactly-one-active-flat-rate-item validation remains enforced;
8. `activeSubscription = null` returns `NO_ACTIVE_SUBSCRIPTION`;
9. mapped Shopify handle returns `mappingStatus=MAPPED`;
10. unmapped Shopify handle returns `mappingStatus=UNMAPPED` while preserving Shopify commercial facts;
11. pending Shopify handle may be unmapped independently of the current handle;
12. Partner failure is not replaced with local commercial state;
13. the service calls `provider.getActiveSubscription()` once per read;
14. no local plan catalogue is fabricated.

## Non-goals

No UI, no top-up purchase mutation, no plan activation mutation, no Admin changes, no all-plans catalogue and no Background change.

## Validation

Run focused Shopify billing-provider/service tests, repository-declared typecheck/build/full tests and `git diff --check`.

## Stop conditions

STOP if the installed Partner API schema/version does not expose the flat-rate fields already queried by the current provider. Report the exact mismatch.

STOP if implementation would require local `BillingPlan` rows to substitute for unavailable Shopify commercial data.

## Completion Report

### Status
Ready for Review

### Files Changed

- `app/services/billing/billing.types.ts`
- `app/services/billing/providers/shopify-billing.provider.ts`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/shopify-billing.provider.test.ts`
- `tests/unit/services/billing.service.test.ts`

### Work Completed

- Extended `ProviderSubscription` backwards-compatibly with billing period, current/pending flat-rate commercial facts, and active tiered usage items while preserving existing usage handles, snapshots, dates and reconciliation fields.
- Preserved the existing exactly-one-active-flat-rate invariant and existing Partner failure path.
- Added `BillingService.getMerchantShopifySubscriptionState(shopId)` with durable Shop/Shopify ID validation, exactly one provider read, explicit `NO_ACTIVE_SUBSCRIPTION`, Shopify-authoritative current/pending commercial data, independent current/pending local mapping lookups, and first-class unmapped results.
- Preserved Free-plan billing cycles and usage items without converting provider data into local monetary fields or a fabricated catalogue.
- Added focused regression coverage for commercial fields, billing cycles, cancellation, pending mappings, Free usage meters, unmapped handles, provider failures, no active subscription, and one-call behavior.

### Validation Results

- `npm run prisma:generate`: passed after initializing the pinned existing `database` submodule for validation; no database files or schema changes made.
- `npm test -- --run tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing.service.test.ts`: passed, 2 files and 43 tests.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm test`: 27 files passed, 1 skipped, 3 failures out of 220 tests. The failures are the pre-existing missing `billingCommerce.actions.manageCapacity` i18n catalogue key in `tests/unit/merchant-i18n.test.ts` and `tests/unit/billing-i18n.test.ts`; unrelated to this task.
- `npm run typecheck`: exits 2 on existing repository-wide diagnostics in unrelated JSX/routes/services/tests. A current direct `npx tsc --noEmit --pretty false` check reports no diagnostics in the five task-touched files.
- Targeted ESLint reports two existing test-fixture unused-variable errors at `tests/unit/services/billing.service.test.ts` lines 68 and 409; no production-file lint errors.

### Deviations

None.

### Assumptions

- An existing `BillingPlan` row is the Moda mapping signal; Shopify remains authoritative for live handle, price, billing period, cycle dates, cancellation and pending commercial state.
- Active tiered provider items are exposed unchanged for downstream exact pack-meter matching.

### Unresolved Issues

- Repository baseline failures remain as recorded under Validation Results; they are outside this task's bounded provider/service scope.

### Architectural Concerns

None.

### Git / VCS

Task branch: `task/ARCH-010-SHOPIFY-013`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-013`
  parent branch: `task/ARCH-010-SHOPIFY-013`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-013`
  implementation branch: `task/ARCH-010-SHOPIFY-013`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact`
  commit: `8ef0786`
  remote branch: `origin/task/ARCH-010-SHOPIFY-013`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/shopify/ARCH-010/SHOPIFY-013-authoritative-shopify-subscription-read-model.md`
  claim commit: `49c36ed`
  review submission commit: pending until this report is committed
  remote branch: `origin/task/ARCH-010-SHOPIFY-013`
  pushed: yes for claim; review submission follows this commit
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no
