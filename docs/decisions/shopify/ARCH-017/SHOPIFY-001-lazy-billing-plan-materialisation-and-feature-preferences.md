---
id: ARCH-017-SHOPIFY-001
architecture_id: ARCH-017
title: Lazily materialise BillingPlan on Shopify lifecycle and add merchant feature preferences
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 20
executor: copilot
claimed_at: 2026-09-18T20:42:21Z
attempt: 1
depends_on:
- ARCH-017-DATABASE-001
enables: []
created: 2026-09-18
updated: 2026-09-18
---

# ARCH-017-SHOPIFY-001

## Objective

Fix the first-subscription failure by resolving or lazily materialising `BillingPlan` from the active `MerchantPricingPlan` identified by the same Shopify handle, and add merchant-facing opt-in management for dynamic optional features.

The implementation must preserve existing non-prorated ARCH-010 BillingPeriod/subscription behavior. ARCH-011 is explicitly out of scope.

## Dependency gate

Do not begin until `ARCH-017-DATABASE-001` is architect-accepted and the accepted database submodule revision is materialised in this task worktree.

Immediately regenerate Prisma client using the repository-declared command before TypeScript/test work.

## Read before editing

```text
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
app/services/billing/billing.server.ts or current BillingService construction module
app/services/shop/shop.service.ts
app/services/merchant-route-access-policy.ts (or current route policy file)
app/routes/app/** navigation/layout files
tests/unit/services/billing.service.test.ts
tests/unit/routes/billing-callback.test.ts
tests/unit/merchant-route-access-policy.test.ts
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
docs/architecture/ARCH-014-admin-managed-merchant-pricing-catalogue.md
```

Search for all places that resolve BillingPlan by `shopifyPlanHandle`. Do not fix only one callback branch while leaving generic subscription sync able to produce a false `UNMAPPED` for a known catalogue plan.

## Authorized implementation surface

```text
app/services/billing/billing.service.ts
app/routes/app/billing/callback/route.tsx
app/services/billing/* small helper file only if it makes the resolver testable
app/routes/app/features/route.tsx              # new preferred route
app/components/features/*                      # new small merchant UI components if needed
merchant route-access/navigation policy files
focused unit/security/route tests
package.json/package-lock.json only if required by existing test wiring
```

Do not edit the database submodule. Do not implement Admin catalogue editing.

## Part A — deterministic BillingPlan resolver/materialiser

### 1. Add structured resolution result

In the BillingService module add a private/internal result type conceptually equivalent to:

```ts
type OperationalBillingPlanResolution =
  | { kind: "READY"; plan: BillingPlan; materialized: boolean }
  | { kind: "UNKNOWN_CATALOGUE_PLAN" }
  | { kind: "INACTIVE_OPERATIONAL_PLAN"; planId: string }
  | { kind: "INVALID_CATALOGUE_PLAN"; reason: string };
```

Use the generated Prisma BillingPlan type/import style already present in the service. Do not export the type unless tests require it.

### 2. Add `resolveOrMaterializeBillingPlan(planHandle)`

Implement one service method and reuse it everywhere the app needs to turn a Shopify plan handle into operational BillingPlan state.

Normalize only by the existing handle conventions. Do not lowercase/rename handles unless existing MerchantPricingPlan creation already does so.

Algorithm MUST be exactly:

```text
BEGIN transaction

1. find BillingPlan by shopifyPlanHandle

2. if found:
     if active=false:
       return INACTIVE_OPERATIONAL_PLAN
     if a MerchantPricingPlan with same handle exists and materializedAt is null:
       set materializedAt = now (do not change isActive)
     return READY(existing, materialized=false)

3. find MerchantPricingPlan by same shopifyPlanHandle including:
     features -> feature

4. if no MPP OR MPP.isActive=false:
     return UNKNOWN_CATALOGUE_PLAN

5. validate catalogue materialisation invariants:
     - planKind FREE or PAID_METERED
     - contains system-required checkout_recovery mapping
     - all mapped Feature rows exist
     - FREE => shopifyRecoveryUsageEventHandle is null
     - PAID_METERED => shopifyRecoveryUsageEventHandle.trim() is nonempty
     - includedRecoveryCredits is valid under existing MerchantPricingPlan schema/rules
   if any fails:
     return INVALID_CATALOGUE_PLAN with stable bounded reason code/message

6. create BillingPlan using unique handle:
     shopifyPlanHandle = MPP.shopifyPlanHandle
     name = MPP.displayName
     kind = MPP.planKind
     active = true
     shopifyUsageEventHandle =
       FREE ? null : MPP.shopifyRecoveryUsageEventHandle.trim()
     includedRecoveryConversationAllowance =
       FREE ? null : MPP.includedRecoveryCredits
     recoveryCreditPackEnabled = false
     recoveryCreditsPerPack = null
     shopifyRecoveryCreditPackEventHandle = null
     features = every MPP feature mapping with enabled=true

7. set MPP.materializedAt = now only when currently null

8. commit and return READY(created, materialized=true)
```

### 3. Concurrency handling

Do not implement `find -> create` without unique-race recovery.

Preferred implementation is a transaction using unique-handle `upsert` or create-with-P2002 recovery. Whichever repository convention is used, the observable rule is:

- two concurrent callers for the same active MPP must both return the same final BillingPlan identity;
- only one BillingPlan row exists;
- MPP ends with non-null materializedAt;
- no callback fails merely because another callback won the unique insert race.

If using `upsert`, do not update an existing inactive BillingPlan back to active. An existing row must be inspected before the create/upsert branch.

### 4. Do not synchronize catalogue activation into runtime activation

Never execute:

```ts
BillingPlan.active = MerchantPricingPlan.isActive
```

An already-existing active BillingPlan remains usable for an existing subscription even if its catalogue MerchantPricingPlan has later been deactivated for new selection.

The MPP `isActive` check applies only when no BillingPlan exists and a new operational plan would have to be created.

## Part B — wire materialisation into current activation/sync

### 5. `prepareFreeActivation`

Current code does:

```ts
const plan = await this.database.billingPlan.findUnique(...);
if (!plan?.active || plan.kind !== BillingPlanKind.FREE) return null;
```

Replace the direct lookup with `resolveOrMaterializeBillingPlan(planHandle)`.

Rules:

- READY + kind FREE -> continue existing logic unchanged;
- READY + wrong kind -> return null/fail existing invalid-plan path;
- UNKNOWN_CATALOGUE_PLAN -> return null so generic sync can project genuine UNMAPPED if provider reports it;
- INACTIVE_OPERATIONAL_PLAN -> do not reactivate; return null / surface fail-closed sync state;
- INVALID_CATALOGUE_PLAN -> do not create Subscription pending token; surface fail-closed error and stable log/error code.

Do not change the current initial-vs-replay token semantics except where required to use the resolved plan.

### 6. `preparePaidActivation`

Apply the same replacement. READY must be `BillingPlanKind.PAID_METERED`.

Do not add prorated logic.

### 7. Generic `syncSubscription`

Current code independently does a `billingPlan.findUnique` around the observed provider plan handle and emits `UNMAPPED_PLAN_HANDLE` if no usable plan exists.

Replace that lookup with the same resolver so direct sync/replay/reinstall cannot still misclassify a known active MerchantPricingPlan.

Projection rules:

```text
READY
  -> existing ACTIVE/TRIALING mapping logic

UNKNOWN_CATALOGUE_PLAN
  -> SubscriptionProjectionStatus.UNMAPPED
  -> lastSyncErrorCode = UNMAPPED_PLAN_HANDLE (preserve existing code)

INACTIVE_OPERATIONAL_PLAN
  -> SubscriptionProjectionStatus.SYNC_ERROR
  -> lastSyncErrorCode = BILLING_PLAN_INACTIVE

INVALID_CATALOGUE_PLAN
  -> SubscriptionProjectionStatus.SYNC_ERROR
  -> lastSyncErrorCode = INVALID_MERCHANT_PRICING_PLAN
```

Use existing bounded error metadata conventions. Do not place arbitrary database/provider payloads in `lastSyncErrorCode`.

### 8. Onboarding completion is a Shopify managed-pricing milestone

`ShopSettings.onboardingCompleted` does NOT mean that Moda successfully resolved, materialised or reconciled a BillingPlan. It means that the merchant has completed the Shopify managed-pricing selection step and therefore has selected/subscribed to a plan in Shopify.

The callback MUST set `onboardingCompleted=true` as soon as the authenticated Shopify callback/provider state establishes that the merchant selected a managed-pricing option. This write is independent of Moda's internal BillingPlan result.

Implement this as an idempotent, separately committed write BEFORE calling `resolveOrMaterializeBillingPlan(...)` or performing Subscription/BillingPeriod projection. Do NOT include this write in a later transaction whose rollback could revert the onboarding milestone.

Preferred repository-equivalent operation:

```ts
await database.shopSettings.updateMany({
  where: {
    shopId,
    onboardingCompleted: false,
  },
  data: {
    onboardingCompleted: true,
  },
});
```

Use the repository's existing ShopSettings access helper if one already exists; do not create a duplicate abstraction merely to match this snippet.

After Shopify managed-pricing selection has been established, ALL of these subsequent Moda outcomes MUST leave onboarding true:

```text
READY / successful BillingPlan reuse
READY / newly materialised BillingPlan
UNKNOWN_CATALOGUE_PLAN -> UNMAPPED
INACTIVE_OPERATIONAL_PLAN -> SYNC_ERROR
INVALID_CATALOGUE_PLAN -> SYNC_ERROR
later Subscription/BillingPeriod projection failure
```

Do not require BillingPlan materialisation, plan mapping, BillingPeriod creation or successful Moda reconciliation before setting onboarding true.

Do not add any path that sets `onboardingCompleted=false`.

Do not set onboarding true merely because an unauthenticated/arbitrary browser request supplies a `plan_handle`. The milestone must be reached only after the existing authenticated Shopify callback/provider flow establishes that managed-pricing selection occurred.

Tests must distinguish:

```text
fresh install before Shopify pricing selection -> onboarding remains false
Shopify managed-pricing selection observed + known plan -> onboarding true
Shopify managed-pricing selection observed + unknown catalogue plan -> onboarding true + UNMAPPED
Shopify managed-pricing selection observed + invalid/inactive local plan -> onboarding true + SYNC_ERROR
```

## Part C — merchant optional-feature preferences

### 9. Add `/app/features`

Add a merchant route at:

```text
/app/features
```

Integrate it with the current app-shell navigation and route access policy using existing conventions.

Access rule:

- ACTIVE/TRIALING mapped subscription: page available;
- first-install onboarding / NO_CONTRACT / UNMAPPED / SYNC_ERROR / FROZEN: follow the existing capability/access-policy behavior for merchant configuration pages; do not bypass the central route guard;
- do not expose cross-shop data.

If the route policy uses a typed surface enum/union, add a `FEATURES` surface and update exhaustive tests.

### 10. Loader query

Resolve the current shop using existing authenticated Shopify admin/session path.

Load:

```text
current Subscription
  -> current BillingPlan
     -> enabled BillingPlanFeature
        -> Feature

ShopFeaturePreference for current shop
```

Also load existing preferences for features no longer supported only if needed to display a dormant indicator. Do not delete them.

Return a view model containing at minimum:

```ts
{
  key: string;
  displayName: string;
  description: string | null;
  activationMode: "ALWAYS_ENABLED" | "MERCHANT_OPT_IN";
  supportedByCurrentPlan: boolean;
  preferenceEnabled: boolean;
  effectiveEnabled: boolean;
}
```

Effective calculation must match ARCH-017:

```text
ALWAYS_ENABLED:
  feature.active && plan mapping enabled

MERCHANT_OPT_IN:
  feature.active && plan mapping enabled && preference.enabled
```

### 11. Action

Accept only:

```text
intent = set-feature-preference
featureKey
value = true | false
```

Re-resolve authenticated shop server-side. Never accept shopId from the browser.

Inside one transaction/rechecked read:

1. find Feature by key;
2. require `active=true`;
3. require `activationMode=MERCHANT_OPT_IN`;
4. require current Subscription has a current BillingPlan;
5. require an enabled BillingPlanFeature for that plan + feature;
6. upsert `ShopFeaturePreference(shopId, featureId)` with requested `enabled`.

Reject attempts to toggle:

- ALWAYS_ENABLED features;
- unsupported features;
- inactive features;
- another shop's preference.

Do not delete preference rows when set false; persist `enabled=false` for deterministic audit/state semantics unless an existing repository convention requires delete. If using delete would conflict with this contract, do not use delete.

### 12. UI behavior

Render:

- ALWAYS_ENABLED feature: enabled/read-only with copy such as `Included with this plan`;
- MERCHANT_OPT_IN supported feature: toggle;
- optional dormant preference may be shown as unavailable if the existing page design can do so without a new cross-plan catalogue query; it must never be silently deleted;
- feature key is internal identity; display `Feature.displayName` and optional description to merchant.

No plan name conditionals such as `if Growth` are permitted.

## Required tests

### Billing materialisation service tests

Add/update tests for:

1. existing active BillingPlan -> reused; no MPP creation path;
2. no BillingPlan + active valid FREE MPP -> BillingPlan created with FREE kind, null usage meter, null included operational allowance, checkout feature projection, materializedAt set;
3. no BillingPlan + active valid PAID MPP -> BillingPlan created with paid allowance and dedicated `shopifyRecoveryUsageEventHandle`;
4. top-up `MerchantPricingUsageEvent.eventHandle` is never chosen as `BillingPlan.shopifyUsageEventHandle`;
5. optional MPP features are projected by featureId with enabled=true;
6. missing MPP -> genuine UNMAPPED behavior;
7. inactive MPP and absent BillingPlan -> no materialisation;
8. existing inactive BillingPlan -> not reactivated, SYNC_ERROR path;
9. invalid paid MPP missing recovery usage meter -> no BillingPlan creation and SYNC_ERROR path;
10. concurrent/duplicate unique create race resolves to one BillingPlan and returns winner;
11. materialisation alone is not the onboarding trigger; Shopify managed-pricing selection is;
12. Shopify managed-pricing selection sets onboarding true before local BillingPlan resolution;
13. unknown catalogue plan still produces UNMAPPED while onboarding remains true;
14. inactive/invalid local plan still produces SYNC_ERROR while onboarding remains true;
15. later callback against durable existing plan uses existing BillingPlan.

### Callback tests

Update `tests/unit/routes/billing-callback.test.ts` so first subscription succeeds when only MerchantPricingPlan exists before callback.

Explicit regression test:

```text
Given:
  ShopSettings.onboardingCompleted=false
  Subscription=NO_CONTRACT
  active MerchantPricingPlan(handle=growth)
  no BillingPlan(handle=growth)
When:
  authenticated Shopify managed-pricing callback establishes selection of growth
Then:
  BillingPlan(growth) exists
  MerchantPricingPlan.materializedAt != null
  Subscription.planId == BillingPlan.id
  Subscription is not UNMAPPED
  onboardingCompleted=true
```

### Feature preferences

Tests for:

- loader never exposes another shop's preference;
- ALWAYS_ENABLED cannot be toggled;
- supported MERCHANT_OPT_IN can be enabled/disabled;
- unsupported feature toggle rejected;
- inactive feature rejected;
- preference survives simulated plan change and becomes dormant when unsupported;
- returning to supporting plan makes saved preference effective again without recreating preference.

### Route access/navigation

Update route policy/navigation tests for `/app/features` using existing status matrix conventions.

## Validation

Inspect current `package.json`, then run declared scripts. Expected current set:

```text
npm run prisma:generate
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Run focused billing/callback/feature tests separately before the aggregate suite and record both.

## Stop conditions

STOP and return to moda_architect if:

- the accepted database schema lacks `shopifyRecoveryUsageEventHandle` or dynamic Feature tables;
- automatic materialisation would need to guess a normal usage meter from top-up events;
- an implementation would reactivate an inactive BillingPlan automatically;
- plan change logic appears to require copying/deleting ShopFeaturePreference;
- ARCH-011 proration is required;
- implementation requires Admin or Background source edits.

## Non-goals

- editing MerchantPricingPlan catalogue;
- global Feature catalogue administration;
- downstream synchronization of durable MPP edits (Admin owns it);
- changing top-up pricing semantics;
- proration.

## Acceptance criteria

- first known MerchantPricingPlan subscription no longer becomes falsely UNMAPPED solely because BillingPlan was absent;
- genuine unknown handle remains UNMAPPED;
- inactive/invalid operational configuration fails closed as SYNC_ERROR rather than being silently repaired;
- BillingPlan materialisation is idempotent/concurrency-safe;
- MPP becomes durable once operational plan exists;
- onboarding flips true when the authenticated Shopify managed-pricing callback/provider state establishes that the merchant selected a pricing option, before Moda BillingPlan resolution;
- merchant optional feature preferences are tenant-safe, plan-gated and persistent across plan changes;
- all validation passes or only architect-approved unrelated baseline failures remain.

## Completion protocol

Set task to `review`. Completion Report must include implementation commit, parent report commit, exact test commands/results, physical worktree evidence and accepted DATABASE-001 dependency revision.

## Completion Report

Status: Blocked. No implementation commit was created because the accepted DATABASE-001 schema contract is not materialised in the authoritative implementation worktree.

Dependency evidence:

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-SHOPIFY-001`
- Database submodule revision: `e246c70284bbe6889b494f30c1442894319f3de8`
- The checked-out schema still contains `BillingPlanFeatureIdentifier` and lacks `MerchantPricingPlan.materializedAt`, `MerchantPricingPlan.shopifyRecoveryUsageEventHandle`, `Feature`, `MerchantPricingPlanFeature`, and `ShopFeaturePreference`.
- The dependency task is marked complete, but its required schema is absent from the submodule revision available to this task.

Validation:

- `npm ci`: passed in the implementation worktree.
- `npm run prisma:generate`: passed after dependency installation.
- The required schema fields/models were checked directly with `rg`; the dependency contract is absent.
- No TypeScript, focused tests, aggregate tests, lint, or build were run because the task stop condition prohibits implementing against the legacy schema.

Required handoff: materialise the accepted DATABASE-001 revision in this worktree, then rerun the prepared task. No Architect Review section was edited.
