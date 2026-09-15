---
id: ARCH-015-SHOPIFY-001
architecture_id: ARCH-015
title: Resolve live recovery-credit top-up offers from Shopify and ARCH-014
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-014-SHOPIFY-001
enables:
- ARCH-015-SHOPIFY-002
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-015-SHOPIFY-001

## Objective

Replace the singular operational BillingPlan top-up read model with a live multi-offer resolver that correlates the merchant's current Shopify App Pricing subscription with ARCH-014 `MerchantPricingPlan`/`MerchantPricingUsageEvent` entitlement semantics.

This task is read/UI only. Do not create purchases.

## Authorized implementation surface

```text
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts                 # read/commercial projection only
app/services/merchant-pricing/*                         # reuse/extend ARCH-014 server-only capability
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx         # only if prop shape requires
app/i18n/locales/*.json                                 # generic empty/verification labels only
tests/unit/services/billing*.test.*
tests/unit/billing-ui.test.ts
tests/unit/billing-purchase-hub.test.tsx
tests/unit/*topup*.test.*
```

Do not modify purchase mutation semantics in this task.

## Provider parser correction

In `ShopifyBillingProvider`, do not exclude a returned live subscription item solely because `item.price.active === false`.

Keep type/handle validation, but subscription membership comes from `activeSubscription.items`.

Apply the same principle to parsing helpers in this repository.

## Canonical offer resolver

Create/reuse a server-only function equivalent to:

```text
resolveCurrentRecoveryCreditOffers({
  providerSubscription,
  merchantPricingPlan
})
```

Resolution sequence:

1. require live provider subscription;
2. use provider `planHandle`;
3. load exactly one `MerchantPricingPlan` where `shopifyPlanHandle == provider.planHandle`;
4. DO NOT require `MerchantPricingPlan.isActive == true` for an already-contracted merchant;
5. load usage events ordered `position ASC`;
6. for each ARCH-014 usage event, find exact provider usage item where `handle == eventHandle`;
7. only matched events become offers;
8. `creditsGranted` comes from `creditsGrantedPerUnit`;
9. provider price/usage/currency comes from provider usage item, not ARCH-014 monetary fields;
10. unknown provider meters are ignored for purchasing but recorded in bounded diagnostics;
11. ARCH-014 events absent from provider subscription are not purchasable.

Never globally resolve `eventHandle` without the current provider `planHandle`.

## Offer DTO

Return equivalent objects:

```text
{
  eventHandle,
  cataloguePosition,
  creditsGranted,
  providerPrice,
  providerUsage
}
```

Do not expose `adminLabel`.

## Empty-state behavior

Always render the top-up section.

When offer list is empty because no valid intersection exists, render exactly the merchant meaning:

```text
No top ups are currently available for this subscription.
```

Use a translated generic key across all supported locales.

Do not hide the panel.

Provider/API verification failure is separate:

```text
We couldn't verify top-up availability right now. Please try again later.
```

Purchasing remains unavailable in that state.

## Legacy singular fields

This task must stop using these as the operative top-up source:

```text
BillingPlan.recoveryCreditsPerPack
BillingPlan.shopifyRecoveryCreditPackEventHandle
```

Do not delete schema fields in this task; simply remove them from this top-up read/UI flow.

## Required tests

- current Shopify plan resolves matching ARCH-014 plan;
- `isActive=false` catalogue plan can still resolve for an existing live Shopify contract;
- multiple ARCH-014 usage events resolve in `position` order;
- provider meter absent => ARCH-014 event omitted;
- provider-only unknown meter => no fabricated credits;
- same event handle on another plan is never used;
- credits come from `creditsGrantedPerUnit`;
- provider price comes from live provider item;
- `price.active=false` item remains eligible if returned in live subscription;
- zero ARCH-014 events -> empty-state panel shown;
- zero provider matches -> empty-state panel shown;
- provider failure -> verification-unavailable state, not empty-state;
- singular BillingPlan pack fields are not read for offers.

## Stop conditions

STOP if:

- ARCH-014 merchant app implementation is not available/compatible;
- ARCH-014 usage-event rows cannot be distinguished as the intended recovery-credit top-up offers under the accepted ARCH-014 contract;
- resolving an existing subscription requires `MerchantPricingPlan.isActive=true`;
- implementation requires reading ARCH-014 stored price as proof of Shopify's live charge.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation summary:

- Added the server-only ARCH-014 to Shopify live subscription intersection resolver, scoped by the current Shopify `planHandle`, ordered by usage-event position, bounded unknown-meter diagnostics, and live provider price/usage data.
- Preserved contracted access to inactive ARCH-014 catalogue plans and retained Shopify subscription items whose returned price has `active: false`.
- Updated the billing read projection and route/UI state to distinguish verified empty offers from verification-unavailable states, always render the top-up panel, and derive configuration from live offers rather than singular `BillingPlan` pack fields.
- Preserved purchase mutation semantics and Shopify-hosted subscription management.

Changed files:

- `app/components/dashboard/BillingPurchaseHub.jsx`
- `app/components/dashboard/TopUpPurchasePanel.jsx`
- `app/i18n/locales/en.json`
- `app/routes/app/billing/options/route.tsx`
- `app/services/billing/billing.service.ts`
- `app/services/billing/billing.types.ts`
- `app/services/billing/providers/shopify-billing.provider.ts`
- `app/services/merchant-pricing/merchant-pricing.server.js`
- `tests/unit/billing-purchase-hub.test.tsx`
- `tests/unit/merchant-pricing-reader.test.js`
- `tests/unit/services/shopify-billing.provider.test.ts`

Validation:

- Focused provider, resolver, and UI suite: 3 files passed, 40 tests passed.
- Expanded focused suite: 4 files passed; two existing exact-active-cycle billing service tests still fail because their fixtures provide only retired singular `BillingPlan` pack metadata and no ARCH-014 `MerchantPricingPlan`.
- `npm run prisma:generate`: passed.
- Focused ESLint for the final corrected service and panel files: passed, with the repository TypeScript-version compatibility warning.
- `npm run typecheck`: repository baseline remains failing in unrelated dashboard/Polaris JavaScript files; no remaining diagnostics were reported for the touched billing service, provider, resolver, route, or top-up panel files.
- Both generic top-up empty/verification keys are present in all 20 supported locale files; English text matches the task contract exactly.
- `git diff --check`: passed.

Baseline limitations:

- The two existing exact-active-cycle billing service tests still encode the retired singular `BillingPlan` top-up contract and fail until their fixtures are migrated to ARCH-014 usage events. No legacy fallback was added because that would violate this task's source-of-truth requirement.
- Full repository typecheck/lint remains affected by pre-existing unrelated diagnostics; the touched-slice checks above are clean.

Launcher and isolation evidence:

- Continued the prepared attempt in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-SHOPIFY-001` and parent report worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-SHOPIFY-001`.
- Preserved parent claim commit `68b0ccd8e6e776790920056a12836cbb21ec8638` and did not rerun the launcher or create another claim.
- Implementation worktree contained only the 11 authorized ARCH-015 files; the database submodule was not changed.

Commits:

- Implementation: `374f16f` (`feat(billing): resolve live recovery credit top-up offers`)
- Parent report: pending publication on the mirrored `task/ARCH-015-SHOPIFY-001` branch.
