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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 2
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

Status: Ready for Review

Attempt: 2 rework completed against the authoritative review corrections.

Implementation commit: `4e215f2` (`fix(shopify): preserve initial activation after onboarding`), pushed to `origin/task/ARCH-017-SHOPIFY-001`.

Accepted DATABASE-001 dependency revision: `3c7179825c3e12af1d6db805b8a2a73c61c2097c`.

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-SHOPIFY-001`; implementation branch: `task/ARCH-017-SHOPIFY-001`.

Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-017-SHOPIFY-001`; parent branch: `task/ARCH-017-SHOPIFY-001`.

Implemented review corrections:

- Removed `onboardingCompleted` from Free/Paid initial activation eligibility and exact-token fencing; durable Subscription pending-selection fields now control initial intent, retries, stale-token rejection, and preservation.
- Kept authenticated callback onboarding persistence separately committed before BillingService resolution; onboarding-complete fresh Free/Paid selections still create initial tokens and exact Paid tokens still synchronize.
- Preserved active different-plan protection, verified replay behavior, accepted BillingPlan materialisation, feature preferences, and no-proration scope.
- Removed the contradictory test that rejected a fresh shop solely because onboarding was already complete and added focused regression coverage.

Validation:

- `npm run prisma:generate`: passed.
- `npm test -- --run tests/unit/services/billing.service.test.ts`: 191 passed.
- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/routes/billing-callback.test.ts`: 220 passed.
- `npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/routes/features-route.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/merchant-route-access-policy.test.ts`: 260 passed across 4 files.

- `npm run typecheck`: failed on existing repository-wide diagnostics, including unrelated JSX, webhook, Redis, and implicit-`any` errors; no new diagnostic was introduced in the edited activation/token lines.
- `npm run lint`: failed with 16 existing errors in unrelated files and 2 existing warnings for duplicate imports in `tests/unit/services/billing.service.test.ts`; changed-file lint had 0 errors.
- `npm run build`: passed, including Prisma generation and production client/SSR bundles.
- `git diff --check`: passed.

Parent report commit: `f368cdeb` (`task(ARCH-017-SHOPIFY-001): return rework for review`), pushed to `origin/task/ARCH-017-SHOPIFY-001`.

No database submodule contents or Architect Review section were edited.

## Architect Review

### Review Status

Changes Requested

### Review Notes

The implementation is close and the lazy BillingPlan materialiser plus merchant feature-preference surface are functionally aligned with ARCH-017. One blocking lifecycle defect remains in the first managed-pricing selection path.

The callback now correctly commits `ShopSettings.onboardingCompleted=true` before local BillingPlan resolution. However, the initial-activation and token-fencing code still treats `onboardingCompleted=false` as a prerequisite:

- `prepareFreeActivation()` requires `settings?.onboardingCompleted !== true` before it will create the initial pending token.
- `preparePaidActivation()` has the same requirement.
- `matchesInitialFreeActivationToken()` requires `settings?.onboardingCompleted === false`.
- `syncSubscription()` additionally requires onboarding to remain false for `initialPaidActivation` and uses onboarding=false when deciding whether to preserve initial pending intent.

Because the callback writes onboarding=true first, a fresh Free or Paid selection can materialise/reuse the BillingPlan and then immediately fail the initial-activation eligibility check. The callback therefore falls out of the intended immediate activation/sync path. The existing callback tests do not expose this because the onboarding write and BillingService state are mocked independently.

This is a functional ARCH-017 issue, not a request for broader test hardening. `onboardingCompleted` is now a historical Shopify managed-pricing milestone and MUST NOT remain a gate for whether a valid initial activation token can be created, matched, synchronized or retried.

### Required Corrections

1. Keep the callback's separately committed onboarding transition exactly before local BillingPlan resolution. Do not move it after activation/sync and do not make it conditional on successful Moda mapping.
2. In `prepareFreeActivation()`, remove `ShopSettings.onboardingCompleted` from initial-activation eligibility. Preserve the existing verified-same-plan replay rule and the protection against overwriting an active/different subscription. A first activation is determined from Subscription state: no Subscription, or `NO_CONTRACT` with `planId=null` and no observed Shopify plan handle.
3. Apply the same change to `preparePaidActivation()`. A callback that has just set onboarding=true must still be able to persist the initial Paid pending-selection token.
4. Change `matchesInitialFreeActivationToken()` so the stale-token fence is based on the exact durable Subscription token fields (`subscriptionId`, pending plan id/handle, pending effective time and reconcile time), not on onboarding state. Remove the `settings` dependency from this helper if no longer needed.
5. Update `syncSubscription()` so an exact current initial token remains valid after onboarding has become true. In particular, remove the onboarding=false requirement from the initial Paid activation branch. Preserve the existing row locks and exact-token stale-write protection.
6. Update initial-intent preservation/retry logic that currently uses `onboardingCompleted !== true` as the discriminator. The new discriminator must be durable pending-selection/token state, not the historical onboarding flag. Do not weaken stale-token protection and do not overwrite an active different-plan subscription.
7. Add/adjust focused tests that execute the new ordering rather than mocking the two sides independently:
   - onboarding already true + fresh `NO_CONTRACT` Free selection -> `prepareFreeActivation()` returns `mode=INITIAL` with a token;
   - onboarding already true + fresh `NO_CONTRACT` Paid selection -> `preparePaidActivation()` returns `mode=INITIAL` with a token;
   - an exact initial token still synchronizes when onboarding is true;
   - current-token retry scheduling still works when onboarding is true;
   - stale tokens remain no-ops;
   - active different-plan protection and verified replay behavior remain unchanged.
8. Replace the contradictory service test that currently asserts a fresh shop must be rejected merely because onboarding is already complete. Under ARCH-017 that expectation is no longer valid.
9. Preserve all accepted materialisation behavior: no proration, no automatic reactivation of inactive BillingPlan rows, no usage-meter inference from top-up events, and no feature-preference deletion/copying on plan changes.
10. On Attempt 2, leave one current `## Completion Report`. Remove/supersede the stale earlier `Status: Blocked` Completion Report and record the actual parent report commit used for the resubmission.

### Reviewed Files

- `app/routes/app/billing/callback/route.tsx`
- `app/services/billing/billing.service.ts`
- `app/routes/app/features/route.tsx`
- `app/services/shop/merchant-route-access-policy.ts`
- `tests/unit/routes/billing-callback.test.ts`
- `tests/unit/services/billing.service.test.ts`
- `tests/unit/routes/features-route.test.ts`
- `database/prisma/schema.prisma`

### Validation Reviewed

The Completion Report records 259 focused tests passing, typecheck/build/changed-file lint/diff checks passing, with 16 unrelated full-lint baseline errors. Those results are accepted as evidence for the areas they exercise. They do not cover the blocking shared-state ordering defect above because the callback test mocks the onboarding persistence separately from BillingService.

### Architecture Conformance

Partial. BillingPlan materialisation, concurrency recovery, dynamic feature preferences, tenant scoping and route-policy integration are consistent with ARCH-017 on inspection. The first managed-pricing selection lifecycle is not yet conformant because historical onboarding state still gates activation-token semantics after the callback deliberately commits that milestone first.

### Follow-up

Return the same task for Attempt 2. No new task is required. Do not start terminal ARCH-017 system testing from this review.

## Architect Review — Attempt 2

### Review Status

Changes Requested

### Functional Review Summary

Attempt 2 correctly removes `ShopSettings.onboardingCompleted` from initial activation eligibility, exact-token matching, retry scheduling and initial-intent preservation. The durable Subscription token now remains authoritative after onboarding becomes true, and the previously accepted BillingPlan materialisation and merchant feature-preference implementation remains functionally intact on inspection.

Two linked callback defects still block acceptance.

#### Blocking finding 1 — provider selection is not established before onboarding/materialisation

`app/routes/app/billing/callback/route.tsx` currently executes, in this order:

```text
resolve authenticated shop
-> set ShopSettings.onboardingCompleted=true
-> prepareFreeActivation()/preparePaidActivation()
-> only afterwards read Shopify provider subscription state
```

This means an authenticated browser request containing an arbitrary `plan_handle` can mark onboarding complete before Shopify provider truth proves that the merchant selected that plan. If the supplied handle names an active MerchantPricingPlan, the same request can also call the BillingPlan materialiser and make that catalogue plan durable even when Shopify has no matching current/pending selection.

ARCH-017 requires the milestone to mean "Shopify managed-pricing selection observed", not merely "authenticated callback route visited with a plan_handle". Provider truth must therefore be established before both the onboarding write and local BillingPlan resolution/materialisation.

#### Blocking finding 2 — fresh unknown/inactive/invalid selections are not projected

When both `prepareFreeActivation()` and `preparePaidActivation()` return `null`, the callback falls into `recordHostedPlanChangeReturn(...)`.

For a fresh shop with no existing Subscription, `recordHostedPlanChangeReturn(...)` returns the provider classification with `subscriptionId=null` and does not call `syncSubscription()`. Therefore a provider-confirmed initial selection whose local result is:

```text
UNKNOWN_CATALOGUE_PLAN
INACTIVE_OPERATIONAL_PLAN
INVALID_CATALOGUE_PLAN
```

can leave the shop with onboarding complete but no durable Subscription projection at all. That violates the required ARCH-017 outcomes:

```text
unknown catalogue -> UNMAPPED / UNMAPPED_PLAN_HANDLE
inactive BillingPlan -> SYNC_ERROR / BILLING_PLAN_INACTIVE
invalid MerchantPricingPlan -> SYNC_ERROR / INVALID_MERCHANT_PRICING_PLAN
```

The generic `syncSubscription()` implementation already produces those bounded outcomes correctly; the callback simply fails to invoke it for this fresh-selection branch.

### Required Attempt 3 Corrections

Implement only the following bounded correction. Do not redesign the billing lifecycle.

#### 1. Reorder provider verification before onboarding and local resolution

File:

```text
app/routes/app/billing/callback/route.tsx
```

In `loader(...)`, after `resolveShopifyShop(...)` and `assertActiveShop(...)`, perform these operations in this exact order:

```text
A. capture verificationFence = billingService.getHostedPlanVerificationFence(shop.id)
B. call billingService.getMerchantShopifySubscriptionState(shop.id)
C. establish whether provider state confirms requestedPlanHandle
D. only if confirmed, commit onboardingCompleted=true
E. only after that commit, call prepareFreeActivation()/preparePaidActivation()
```

Do not call either `prepareFreeActivation()` or `preparePaidActivation()` before step D.

If the provider read in step B throws:

```text
- do not update onboardingCompleted;
- do not call either prepare method;
- call recordHostedPlanVerificationFailure(shop.id, verificationFence);
- preserve the existing guarded reconciliation enqueue;
- redirect with the existing `unverified` result.
```

#### 2. Define provider-confirmed managed-pricing selection deterministically

Treat the requested handle as provider-confirmed only when:

```text
state.status === "ACTIVE_SUBSCRIPTION"
AND
(
  state.subscription.planHandle === requestedPlanHandle
  OR
  state.subscription.pendingUpdate?.planHandle === requestedPlanHandle
)
```

If that condition is false:

```text
- do not update onboardingCompleted;
- do not call either prepare method;
- pass the already-read provider state plus the original verificationFence to recordHostedPlanChangeReturn(...);
- preserve the existing enqueue/redirect behaviour for current/pending/mismatch/no_active.
```

Do not infer selection from the query parameter alone.

#### 3. Preserve the monotonic milestone ordering once provider confirmation exists

When step 2 confirms the requested handle, execute the existing idempotent `shopSettings.updateMany(...)` as its own committed database operation before either prepare method.

Required ordering:

```text
provider confirms requested current/pending handle
-> onboardingCompleted=true committed
-> resolve/materialise BillingPlan
-> Subscription/BillingPeriod projection
```

Do not move onboarding into a later BillingService transaction. Do not make it conditional on successful local mapping.

#### 4. Keep the known-plan activation path unchanged after the reorder

After the onboarding write, call:

```ts
const activation = await billingService.prepareFreeActivation(shop.id, requestedPlanHandle) ??
  await billingService.preparePaidActivation(shop.id, requestedPlanHandle);
```

If `activation` is non-null, preserve the current Attempt 2 token/sync/retry behaviour. Do not reintroduce any `onboardingCompleted` gate into BillingService.

#### 5. Project a fresh provider-confirmed current selection when no activation token can be prepared

Use the captured `verificationFence` to identify a fresh initial projection candidate:

```text
verificationFence === null
OR
(
  verificationFence.status === NO_CONTRACT
  AND verificationFence.planId === null
  AND verificationFence.observedShopifyPlanHandle === null
)
```

When all of the following are true:

```text
activation === null
fresh initial projection candidate
state.status === ACTIVE_SUBSCRIPTION
state.subscription.planHandle === requestedPlanHandle
```

call:

```ts
await billingService.syncSubscription(shop.id)
```

with no fabricated initial token.

This call is required so the existing resolver writes one of the real durable outcomes:

```text
READY                       -> normal ACTIVE/TRIALING projection
UNKNOWN_CATALOGUE_PLAN      -> UNMAPPED + UNMAPPED_PLAN_HANDLE
INACTIVE_OPERATIONAL_PLAN   -> SYNC_ERROR + BILLING_PLAN_INACTIVE
INVALID_CATALOGUE_PLAN      -> SYNC_ERROR + INVALID_MERCHANT_PRICING_PLAN
```

After this fresh-initial fallback sync, return through the existing app/billing-attention UX (redirect to `/app` is acceptable). Do not call `recordHostedPlanChangeReturn(...)` using the pre-sync verification fence after `syncSubscription()` has mutated Subscription state.

Do not run this fallback merely because the requested handle is a provider `pendingUpdate`. Existing non-initial/current-plan-change handling remains owned by the hosted-plan return/reconciliation path.

#### 6. Preserve existing non-initial hosted-plan handling

When the callback is not the fresh-initial-current case from correction 5, continue to use `recordHostedPlanChangeReturn(...)` with the provider state already read in correction 1.

Do not introduce proration, same-cycle downgrade machinery, automatic BillingPlan reactivation, top-up-meter inference, or cross-repository changes.

#### 7. Add focused callback regressions only

File:

```text
tests/unit/routes/billing-callback.test.ts
```

Add/adjust tests proving exactly these cases:

1. **arbitrary authenticated request is not onboarding**
   - `plan_handle=growth` is supplied;
   - provider returns `NO_ACTIVE_SUBSCRIPTION`;
   - `shopSettings.updateMany` is not called;
   - neither prepare method is called;
   - no local materialisation path is entered.

2. **provider verification failure is not onboarding**
   - provider-state read throws;
   - onboarding update is not called;
   - prepare methods are not called;
   - existing verification-failure retry path remains active.

3. **confirmed known initial selection preserves ordering**
   - provider current handle equals requested handle;
   - onboarding update occurs before `prepareFreeActivation`/`preparePaidActivation`;
   - existing successful first-subscription flow remains successful.

4. **confirmed unknown initial selection becomes UNMAPPED**
   - initial verification fence is null or `NO_CONTRACT` with no current plan/observed handle;
   - provider current handle equals requested unknown handle;
   - prepare methods return null;
   - `syncSubscription(shop.id)` is called without an initial token;
   - mocked sync result is `UNMAPPED` with `UNMAPPED_PLAN_HANDLE`;
   - `recordHostedPlanChangeReturn` is not called with the stale pre-sync fence.

5. **confirmed inactive/invalid initial selection becomes SYNC_ERROR**
   - same initial conditions as case 4;
   - prepare methods return null;
   - sync result is `SYNC_ERROR` using `BILLING_PLAN_INACTIVE` or `INVALID_MERCHANT_PRICING_PLAN`;
   - onboarding remains true because provider selection was observed.

6. **existing/pending plan-change behaviour remains unchanged**
   - provider confirms only a pending update or the shop already has a mapped current subscription;
   - do not invoke the fresh-initial fallback sync;
   - preserve `recordHostedPlanChangeReturn(...)`, queueing and redirects.

Do not expand this into exhaustive billing testing. Existing BillingService tests for resolver result codes, stale-token fencing, materialisation concurrency and feature preferences remain valid supporting evidence.

#### 8. Validation

Run from the canonical `moda-interact` Attempt 3 implementation worktree:

```text
npm run prisma:generate
npm test -- --run tests/unit/routes/billing-callback.test.ts
npm test -- --run tests/unit/services/billing.service.test.ts tests/unit/routes/features-route.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/merchant-route-access-policy.test.ts
npm run build
npm run typecheck
npm run lint
git diff --check
```

For repository-wide typecheck/lint failures that exactly match the documented baseline, record them factually. Changed callback/service files must not introduce a new diagnostic.

#### 9. Completion Report evidence

The submitted archive's Completion Report says the parent report commit is `f368cdeb`, while the developer submission identifies `8777b7d6`.

On Attempt 3, record one current Completion Report and state the actual pushed parent report commit unambiguously. Do not retain two competing parent-report commit values for the same submission.

### Accepted From Attempt 2

Do not churn these areas unless correction 1-6 requires a direct call-site adjustment:

- `onboardingCompleted` is no longer an activation-token authority bit;
- exact durable pending token matching is onboarding-independent;
- initial retry preservation is driven by Subscription pending state;
- BillingPlan lazy materialisation/concurrency recovery remains accepted;
- inactive BillingPlan is not auto-reactivated;
- recovery usage meter is not inferred from top-up events;
- `/app/features` remains tenant-scoped, plan-gated and data-driven;
- ShopFeaturePreference rows remain persistent across plan changes;
- ARCH-011 proration remains out of scope.

### Architecture Conformance

Partial. Attempt 2 fixes the previous monotonic-onboarding/token interaction, but the callback still treats route visitation as sufficient evidence of Shopify pricing selection and does not durably classify fresh provider-confirmed non-ready plans. Those are functional ARCH-017 lifecycle defects.

### Follow-up

Return this same task to `ready` at Attempt 2. Attempt 3 begins only when the normal launcher claims it. Do not start terminal ARCH-017 system testing from this review.
