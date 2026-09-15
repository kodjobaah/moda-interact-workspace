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
status: complete
priority: 57
executor:
claimed_at:
attempt: 2
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

## Completion Report

Status: Ready for Review

Audit outcome: the implementation at `95e8b5e` satisfied the requested cleanup. The corrective audit added a recursive source-reference assertion and published implementation commit `559b555` (`test(admin): prove legacy economics refs are absent`) to `origin/task/ARCH-014-ADMIN-007`.

Confirmed fixes and preservation:

- Deleted only the four obsolete economics modules after source inspection showed no live consumers; removed the legacy controls and page loads while retaining `PlatformBillingControls`, `TenantBillingControls`, `OverrideSelect`, shared helpers, `billing-control-validation.ts`, `billing-controls.ts`, `upgrade-economics-guardrail.ts`, `merchant-pricing-economics.ts`, and `minimumUpgradePremiumBps` editing/persistence.
- Preserved the generic guardrail and its unit tests; MerchantPricing still uses `validateSinglePackShopifyEconomics`.
- `AdminShell` has the exact `{active, header?, children}` contract, no `search` prop or unconditional `SearchInput`, and renders no header strip when `header` is absent. Only the tenant directory imports/wires `SearchInput`; its `/` GET form and `q` query behavior remain intact. Billing, controls, promotions, merchant support, observability, and queues do not wire tenant search.
- Added a deterministic recursive `src` assertion proving deleted legacy action/read-model/control symbols have zero source references. Negative assertions also prove the retained Controls UI lacks `Upgrade ladder`, `Verified Shopify App Pricing economics`, `mutateUpgradeEdgeAction`, and `recordEconomicsSnapshotAction`.
- No Prisma models/tables, schema, migrations, or database files changed. The implementation commit diff contains only the named Admin source/test changes and the two obsolete economics unit-test deletions.

Changed files in implementation commits:

- Modified: `src/app/(protected)/billing/controls/page.tsx`, `src/app/(protected)/billing/page.tsx`, `src/app/(protected)/page.tsx`, `src/components/admin/admin-shell.tsx`, `src/components/admin/billing-controls.tsx`, `tests/security/admin-billing-economics.test.mjs`.
- Deleted: `src/app/actions/billing-economics.ts`, `src/lib/admin/billing-economics-validation.ts`, `src/lib/admin/billing-economics.ts`, `src/lib/admin/billing-plan-guardrail.ts`, `tests/unit/billing-economics-behavior.test.ts`, `tests/unit/billing-economics-validation.test.ts`.

Scans and focused validation:

- Required legacy scan: no production matches; only intentional negative assertions remain in `tests/security/admin-billing-economics.test.mjs`.
- Required tenant-search scan: `SearchInput` appears only in `src/components/admin/search-input.tsx` and tenant-directory wiring.
- Required retained-symbol scan: `minimumUpgradePremiumBps` and `validateSinglePackShopifyEconomics` remain live.
- `node --test tests/security/admin-billing-economics.test.mjs`: passed, 8/8.
- `npm run test:unit`: passed, 42/42.
- Combined focused security plus guardrail tests: passed, 49/49.
- Changed-file Prettier check and `git diff --check`: passed.

Required repository validation:

- `npm test`: 176 total, 171 passed, 2 failed, with 3 skipped observability tests. The two failures are unrelated baseline assertions expecting `@modainteract/moda-interact-shared` `^0.7.3` while the repository declares `^0.11.2`: `Admin validates and consumes the published Shared ICU runtime` and `consumes the published shared release without a local declaration shim`. No ADMIN-007 focused test failed.
- `npx tsc --noEmit`: failed on the unrelated existing `src/components/admin/merchant-pricing-translation-import.tsx:56` type mismatch (`string` versus the translation issue-code union).
- `npm run build`: production compilation succeeded, then failed on the same existing translation-import type error. It emitted existing optional BullMQ/Valkey warnings for `@valkey/valkey-glide` and dynamic BullMQ dependencies.
- `npm run format:check`: failed on 106 existing files; every ADMIN-007-touched file passes the focused Prettier check.
- The requested `rg` scans were executed with recursive `grep` because `rg` is unavailable in the prepared environment; results are recorded above.

Isolation and publication evidence: continued the prepared attempt without rerunning the launcher, creating a claim, inferring worktrees, or repeating startup synchronization. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-ADMIN-007`. Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-ADMIN-007`. Implementation commits pushed: `95e8b5e`, `559b555`. Parent claim commit: `aed9994add4def479bbd0bf530888d9340f920e7`.

Limitations: repository-wide typecheck, build completion, full test pass, and format check remain limited by the unrelated baseline failures documented above. No out-of-scope database or dependency remediation was attempted.

## Stop conditions

STOP and return to `moda_architect` if removal would require changing a Prisma/database object, if any deleted-candidate function has a live non-legacy production consumer, or if MerchantPricing economics depends on a candidate legacy module rather than the explicitly preserved generic guardrail. Do not broaden scope.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted Attempt 2. Functional review confirms implementation commit `559b555` completes the narrow Admin cleanup without broadening scope.

The four obsolete BillingPlan economics application modules are absent and the retained Controls surfaces no longer load or render `BillingEconomicsControls`, `Upgrade ladder`, `Verified Shopify App Pricing economics`, `mutateUpgradeEdgeAction`, or `recordEconomicsSnapshotAction`. The retained `PlatformBillingControls`, `TenantBillingControls`, `billing-control-validation.ts`, `billing-controls.ts`, `upgrade-economics-guardrail.ts`, `merchant-pricing-economics.ts`, and `PlatformBillingPolicy.minimumUpgradePremiumBps` remain live. MerchantPricing continues to use `validateSinglePackShopifyEconomics`.

`AdminShell` now has the required `{ active, header?, children }` contract, contains no tenant-specific search wiring, and renders no empty header strip when `header` is absent. Only the tenant directory imports and supplies `SearchInput`; billing, billing controls, promotions, merchant support, observability, and queues do not wire the tenant search.

The Attempt 2 correction adds a genuinely recursive scan of `src` proving the deleted economics symbols have zero production references. Independent architect validation reproduced the focused evidence available in the uploaded snapshot: `admin-billing-economics.test.mjs` passed 8/8 and the retained MerchantPricing/upgrade-economics unit suites passed 69/69. The reported repository-wide shared-package, translation-import type/build, and formatting baselines are unrelated to this cleanup and do not constitute an ADMIN-007 functional regression.

No Prisma schema, migration, database object, Shopify merchant-app behavior, or operational billing model is changed. `ARCH-014-ADMIN-007` has no downstream dependency edge, so acceptance does not promote another task. No further ADMIN-007 implementation attempt is required.
