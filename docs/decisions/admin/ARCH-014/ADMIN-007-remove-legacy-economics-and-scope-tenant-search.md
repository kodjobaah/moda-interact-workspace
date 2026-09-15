---
id: ARCH-014-ADMIN-007
architecture_id: ARCH-014
title: Remove superseded BillingPlan economics controls and scope tenant search to tenant directory
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 57
executor: copilot
claimed_at: 2026-09-15T20:05:46Z
attempt: 1
depends_on:
- ARCH-014-ADMIN-005
enables: []
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-007

## Objective

Perform two narrow Admin cleanups confirmed after the MerchantPricing refactor:

1. Remove the **obsolete manual BillingPlan economics controls** (`Upgrade ladder` and `Verified Shopify App Pricing economics`). ARCH-014 `MerchantPricingPlan.cataloguePosition` and full-portfolio economics have replaced those Admin configuration surfaces.
2. Stop rendering the **tenant-directory search bar globally**. `Search tenants by brand name or domain...` belongs only on the tenant directory (`/`). Billing, Promotions, Merchant Support, Observability and Queues must not display it or an empty header spacer.

This task is application-code cleanup only. It MUST NOT modify/drop any database table, migration or Prisma model.

## Binding GPT-5.6 Luna rule

The decisions are already made. Implement the exact deletions/preservations below. Do not infer a broader billing cleanup and do not redesign Admin navigation.

## Part A — remove superseded economics controls

### Required removal

After first confirming zero live consumers outside this legacy cluster, delete these files completely:

```text
src/app/actions/billing-economics.ts
src/lib/admin/billing-economics.ts
src/lib/admin/billing-economics-validation.ts
src/lib/admin/billing-plan-guardrail.ts
```

In `src/components/admin/billing-controls.tsx`:

- remove imports of `mutateUpgradeEdgeAction` and `recordEconomicsSnapshotAction`;
- delete the entire exported `BillingEconomicsControls` component;
- preserve `PlatformBillingControls`, `TenantBillingControls`, `OverrideSelect`, and the shared input/date helpers still used by those retained components.

In both:

```text
src/app/(protected)/billing/page.tsx
src/app/(protected)/billing/controls/page.tsx
```

remove:

```text
getBillingEconomicsControls
BillingEconomicsControls
```

and remove the corresponding data load/render. The Controls view/page must continue to render the retained platform policy controls; do not leave an empty `Upgrade ladder` or snapshot placeholder.

### Required preservation

Do **not** delete or weaken:

```text
src/lib/admin/upgrade-economics-guardrail.ts
src/lib/admin/merchant-pricing-economics.ts
src/lib/admin/billing-control-validation.ts
src/app/actions/billing-controls.ts
PlatformBillingControls
TenantBillingControls
PlatformBillingPolicy.minimumUpgradePremiumBps
```

`upgrade-economics-guardrail.ts` remains live because MerchantPricing economics imports `validateSinglePackShopifyEconomics` and its types. Preserve its unit tests.

Do not touch existing Prisma models/tables:

```text
BillingPlan
BillingUpgradeEconomicsEdge
BillingEconomicsSnapshot
PlatformBillingPolicy
```

This task removes dead Admin application surfaces only.

### Security-test correction

Update `tests/security/admin-billing-economics.test.mjs` deterministically:

- remove file reads/assertions for the deleted action/validation/legacy controls;
- retain the test proving `minimumUpgradePremiumBps` is bounded and persisted through `billing-control-validation.ts` + `billing-controls.ts` action/UI;
- add negative source assertions that the Controls UI no longer contains `Upgrade ladder`, `Verified Shopify App Pricing economics`, `mutateUpgradeEdgeAction` or `recordEconomicsSnapshotAction`.

Do not delete policy safety coverage merely because the legacy economics forms were removed.

## Part B — tenant search belongs only on tenant directory

Current cause: `src/components/admin/admin-shell.tsx` unconditionally renders `SearchInput`, while `SearchInput` is specifically a tenant search whose form action is `/`.

Implement this exact shell contract:

```ts
export async function AdminShell({
  active,
  header,
  children,
}: {
  active: ...existing active union...;
  header?: ReactNode;
  children: ReactNode;
})
```

Remove the `search?: string` prop from `AdminShell`.
Remove the unconditional `SearchInput` import/render from `AdminShell`.
Render the `<header ...>` element **only when `header` is non-null**. When no header is supplied there must be no 64px empty strip/divider.

Update only the tenant directory page:

```text
src/app/(protected)/page.tsx
```

to import `SearchInput` and pass:

```tsx
<AdminShell
  active="tenants"
  header={
    <div className="w-full max-w-2xl">
      <SearchInput defaultValue={search} />
    </div>
  }
>
```

Equivalent formatting is allowed; the semantic contract is not.

Do **not** pass a tenant-search header from:

```text
billing
billing/controls
promotions
promotions/[campaignId]
merchant-support
observability
observability/queues
```

Preserve `src/components/admin/search-input.tsx` itself and its existing `/` GET/query behavior.

## Mandatory tests

Add/update focused tests proving:

1. Tenant directory contains the tenant search placeholder and submits to `/`.
2. Billing page source does not render/import tenant `SearchInput`.
3. Promotions page source does not render/import tenant `SearchInput`.
4. Merchant Support does not render tenant search.
5. Observability and Queues do not render tenant search.
6. `AdminShell` renders its header only when a `header` prop is supplied and has no unconditional search/header markup.
7. `Upgrade ladder` is absent from retained Controls UI.
8. `Verified Shopify App Pricing economics` is absent from retained Controls UI.
9. Deleted legacy actions/read-models have zero source references.
10. `minimumUpgradePremiumBps` remains editable/persisted through the retained platform policy control.
11. MerchantPricing economics unit tests still use/pass the retained generic guardrail.
12. No Prisma/schema/migration file changes.

## Required validation

Run from `moda-interact-admin`:

```bash
npm run test:unit
npm test
npx tsc --noEmit
npm run build
npm run format:check
git diff --check
```

Run:

```bash
rg -n 'mutateUpgradeEdgeAction|recordEconomicsSnapshotAction|getBillingEconomicsControls|BillingEconomicsControls|Verified Shopify App Pricing economics|Upgrade ladder' src tests
rg -n 'SearchInput|search.tenantsPlaceholder' src/app src/components/admin
rg -n 'minimumUpgradePremiumBps|validateSinglePackShopifyEconomics' src tests
```

Expected outcome: first scan has no production references to deleted legacy economics surface; tenant SearchInput appears only in its component and tenant-directory wiring/tests; retained policy/generic economics symbols remain.

## Stop conditions

STOP and return to `moda_architect` if removal would require changing a Prisma/database object, if any deleted-candidate function has a live non-legacy production consumer, or if MerchantPricing economics depends on a candidate legacy module rather than the explicitly preserved generic guardrail. Do not broaden scope.
