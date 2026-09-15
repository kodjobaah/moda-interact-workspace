---
id: ARCH-013-SHOPIFY-002
architecture_id: ARCH-013
title: Close residual billing-options navigation and validation gaps
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 90
attempt: 1
depends_on:
- ARCH-013-SHOPIFY-001
enables: []
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-013-SHOPIFY-002: Close residual billing-options navigation and validation gaps

## Objective

Correct exactly two residual defects found after architect acceptance of `ARCH-013-SHOPIFY-001`:

1. `/app/billing/options` currently advertises `/app/billing/recovery-credit-purchases` during `ONBOARDING`, although the accepted ARCH-013 route policy allows `BILLING_OPTIONS` and denies `BILLING_PURCHASE_HISTORY` for `ONBOARDING`.
2. `tests/unit/billing-ui.test.ts` contains two concatenated top-level import blocks with duplicate bindings and must be made into one valid test module before its validation evidence can be trusted.

This is a correction-only task. `ARCH-013-SHOPIFY-001` remains Complete / Attempt 2 Accepted. Do not reopen its accepted architecture.

## Binding accepted baseline

The following SHOPIFY-001 behaviour is already accepted and is READ-ONLY for this task:

```text
canonical route graph in app/routes.ts
8 MerchantExperienceState values
exact MerchantSurface matrix
state-derived App navigation
/app/billing/options nested under the App shell
/app/billing/select standalone
/app/billing/callback standalone
/app/reinstalling standalone
/app/pending-recoveries standalone
/app/billing removed with no compatibility alias
/app/additional removed
stale billing/recovery-credits module removed
NO_CONTRACT/FROZEN historical reads
ACTIVE-only Promotions
FROZEN plan-selection denial
pending-recovery gating in home + standalone resource
lifecycle-aware support-message CTAs
declarative breadcrumbs
purchase-history breadcrumb parent = /app/billing/options
callback destination semantics
```

Do not change any item in this list.

## Canonical rule this task must preserve

The accepted surface matrix remains:

```text
ONBOARDING
  BILLING_OPTIONS          = allowed
  BILLING_PURCHASE_HISTORY = denied

ACTIVE
  BILLING_OPTIONS          = allowed
  BILLING_PURCHASE_HISTORY = allowed

NO_CONTRACT
  BILLING_OPTIONS          = allowed
  BILLING_PURCHASE_HISTORY = allowed

FROZEN
  BILLING_OPTIONS          = allowed
  BILLING_PURCHASE_HISTORY = allowed

BILLING_ATTENTION
  BILLING_OPTIONS          = allowed
  BILLING_PURCHASE_HISTORY = allowed
```

Therefore the correction is **presentation suppression**, not authorization expansion.

MUST NOT make `BILLING_PURCHASE_HISTORY` available to `ONBOARDING`.

## Read before editing

Read these files before the first code change:

```text
docs/architecture/ARCH-013-merchant-application-routing-navigation.md
docs/decisions/shopify/ARCH-013/SHOPIFY-001-coherent-merchant-routing-navigation.md
app/services/shop/merchant-route-access-policy.ts
app/routes/app/billing/options/route.tsx
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/components/dashboard/BillingPurchaseHub.jsx
tests/unit/merchant-route-access-policy.test.ts
tests/unit/billing-purchase-hub.test.tsx
tests/unit/billing-ui.test.ts
app/routes.ts
```

`app/services/shop/merchant-route-access-policy.ts`, `app/routes/app/billing/recovery-credit-purchases/route.tsx` and `app/routes.ts` are READ-ONLY inspection dependencies for this task.

## Exact authorized implementation files

The implementation repository may modify exactly these four files:

```text
app/routes/app/billing/options/route.tsx
app/components/dashboard/BillingPurchaseHub.jsx
tests/unit/billing-purchase-hub.test.tsx
tests/unit/billing-ui.test.ts
```

Do not modify another `moda-interact` file. If a required correction cannot be completed within these four files, STOP and return the exact blocking evidence to `moda_architect`.

Normal task metadata / Completion Report updates in the parent workspace task file are permitted by the task workflow and are not application implementation scope.

## Step 1 — derive purchased-credit-history presentation from the canonical policy

File:

```text
app/routes/app/billing/options/route.tsx
```

The loader already computes:

```ts
const merchantExperienceState = resolveMerchantExperienceState({
  shop,
  settings,
  subscription,
});
```

and already verifies `BILLING_OPTIONS` with `canAccessMerchantSurface`.

Immediately after the existing `BILLING_OPTIONS` access check, add exactly one derived presentation capability:

```ts
const purchaseHistoryAvailable = canAccessMerchantSurface(
  merchantExperienceState,
  "BILLING_PURCHASE_HISTORY",
);
```

Rules:

- derive this boolean only from `merchantExperienceState` + `canAccessMerchantSurface`;
- DO NOT derive it from provider `lifecycleState`;
- DO NOT derive it from Shopify verification state;
- DO NOT derive it from whether the merchant currently owns purchases;
- DO NOT change the surface matrix;
- DO NOT add a provider call.

Return `purchaseHistoryAvailable` from **both** loader result branches:

1. the normal `try` result;
2. the bounded `catch` fallback result.

The boolean is known before provider/commercial reads and must not disappear when provider verification fails.

In `BillingOptionsPage`, pass exactly that loader boolean to `BillingPurchaseHub`:

```tsx
purchaseHistoryAvailable={data.purchaseHistoryAvailable}
```

Do not pass `merchantExperienceState` into `BillingPurchaseHub` for it to reinterpret.

## Step 2 — suppress only the denied purchase-history link

File:

```text
app/components/dashboard/BillingPurchaseHub.jsx
```

Add a required boolean prop:

```text
purchaseHistoryAvailable
```

Update all three places that describe component props:

```text
JSDoc prop shape
function destructuring
BillingPurchaseHub.propTypes
```

`PropTypes` requirement:

```js
purchaseHistoryAvailable: PropTypes.bool.isRequired
```

Replace the unconditional purchased-credit-history paragraph/link with conditional rendering equivalent to:

```jsx
{purchaseHistoryAvailable ? (
  <p>
    <a href="/app/billing/recovery-credit-purchases">
      {i18n.t("billingPurchases.manageLink")}
    </a>
  </p>
) : null}
```

Do not change:

```text
top-up visibility
plan-management visibility
capacity rendering
current/pending plan rendering
billing copy
CSS
route URL
```

Expected UI result:

| Merchant experience | `/app/billing/options` | Manage purchased credits link |
|---|---:|---:|
| ONBOARDING | allowed | hidden |
| ACTIVE | allowed | shown |
| NO_CONTRACT | allowed | shown |
| FROZEN | allowed | shown |
| BILLING_ATTENTION | allowed | shown |

The direct `/app/billing/recovery-credit-purchases` route remains independently guarded by the existing `BILLING_PURCHASE_HISTORY` policy. Do not weaken or modify that route.

## Step 3 — add focused component regression coverage

File:

```text
tests/unit/billing-purchase-hub.test.tsx
```

In the existing `render(...)` helper, pass:

```tsx
purchaseHistoryAvailable
```

as the default so existing tests continue to represent an allowed state.

Add tests proving both sides of the rendering contract:

### Allowed

With `purchaseHistoryAvailable={true}`:

```text
markup contains href="/app/billing/recovery-credit-purchases"
markup contains the translated Manage purchased credits label
```

### Denied

With `purchaseHistoryAvailable={false}`:

```text
markup does NOT contain href="/app/billing/recovery-credit-purchases"
markup does NOT contain the Manage purchased credits label
```

Do not remove or weaken any existing `BillingPurchaseHub` tests.

## Step 4 — repair `billing-ui.test.ts` as one valid module

File:

```text
tests/unit/billing-ui.test.ts
```

The current accepted baseline contains two concatenated import sections. It begins with imports equivalent to:

```ts
import { access, readFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
```

and later imports `readFile`, `describe`, `expect` and `it` again.

This is invalid module structure and must be repaired without deleting either existing test suite.

Use one top-level import block containing the union of required imports:

```ts
import { createElement, type ReactNode } from "react";
import { access, readFile } from "node:fs/promises";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useLoaderData } from "react-router";
```

Requirements:

- delete the later duplicate import block;
- keep the existing `canonical merchant billing UI` describe suite;
- keep the existing `merchant billing UI` describe suite;
- keep all existing assertions unless they must be minimally adjusted for the new required component prop;
- MUST NOT split the file into a new file in this task;
- MUST NOT delete tests merely to make parsing succeed.

## Step 5 — prove loader capability mapping uses the canonical policy

Still in:

```text
tests/unit/billing-ui.test.ts
```

Extend the existing billing-options route import so the test has access to the loader as well as the component/action. Use the existing mocks; do not create a new test harness file.

Add focused loader tests with these exact local states:

```text
ONBOARDING
  settings.onboardingCompleted = false
  subscription.status = NO_CONTRACT
  expected purchaseHistoryAvailable = false

ACTIVE
  settings.onboardingCompleted = true
  subscription.status = ACTIVE
  expected purchaseHistoryAvailable = true

NO_CONTRACT
  settings.onboardingCompleted = true
  subscription.status = NO_CONTRACT
  expected purchaseHistoryAvailable = true

FROZEN
  settings.onboardingCompleted = true
  subscription.status = FROZEN
  expected purchaseHistoryAvailable = true

BILLING_ATTENTION
  settings.onboardingCompleted = true
  subscription.status = UNMAPPED
  expected purchaseHistoryAvailable = true
```

For every case:

- `resolveShopifyShop` remains an `ACTIVE` shop;
- call the real billing-options loader with a request to `/app/billing/options`;
- assert the returned loader data has exactly the expected `purchaseHistoryAvailable` boolean;
- do not infer the expected value from mocked provider lifecycle/commercial state.

Also retain/read the purchase-history route source and assert it still checks the canonical surface name:

```text
BILLING_PURCHASE_HISTORY
```

This source assertion is a regression guard only. Do not edit the purchase-history route.

The existing `tests/unit/merchant-route-access-policy.test.ts` remains the authoritative matrix test and must also be run in validation.

## Step 6 — preserve all accepted ARCH-013 routing behaviour

Before returning to review, verify no implementation diff exists in:

```text
app/routes.ts
app/services/shop/merchant-route-access-policy.ts
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/routes/app/home/route.jsx
app/routes/app/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/routes/app/promotions/route.tsx
app/services/merchant-support/system-message-actions.ts
app/components/dashboard/Breadcrumbs.jsx
```

Do not make cleanup edits in those files.

## Acceptance Criteria

All criteria are mandatory:

- [ ] `ARCH-013-SHOPIFY-001` remains Complete / Attempt 2 Accepted and is not reopened.
- [ ] `merchant-route-access-policy.ts` is unchanged.
- [ ] `app/routes.ts` is unchanged.
- [ ] `ONBOARDING` still allows `BILLING_OPTIONS` and denies `BILLING_PURCHASE_HISTORY`.
- [ ] billing-options loader derives `purchaseHistoryAvailable` through `canAccessMerchantSurface(merchantExperienceState, "BILLING_PURCHASE_HISTORY")`.
- [ ] both billing-options loader result branches return `purchaseHistoryAvailable`.
- [ ] `BillingPurchaseHub` receives a required boolean `purchaseHistoryAvailable` prop.
- [ ] ONBOARDING billing options do not render the purchased-credit-history link.
- [ ] ACTIVE billing options render the purchased-credit-history link.
- [ ] NO_CONTRACT billing options render the purchased-credit-history link.
- [ ] FROZEN billing options render the purchased-credit-history link.
- [ ] BILLING_ATTENTION billing options render the purchased-credit-history link.
- [ ] direct purchase-history route authorization remains unchanged and still uses `BILLING_PURCHASE_HISTORY`.
- [ ] `tests/unit/billing-ui.test.ts` has one import section with no duplicate top-level bindings.
- [ ] both pre-existing describe suites in `tests/unit/billing-ui.test.ts` remain present.
- [ ] existing BillingPurchaseHub tests remain present and new allowed/denied link tests are added.
- [ ] no billing v1.1 behaviour is implemented.
- [ ] no Prisma/database/shared/background/messaging/gateway/admin code changes occur.
- [ ] implementation repository changes are limited to the four authorized files.
- [ ] focused tests pass.
- [ ] full `npm test` passes.
- [ ] production build passes.
- [ ] `git diff --check` passes.

## Validation

From the `moda-interact` implementation task worktree, first inspect `package.json` and use the declared scripts. Then run exactly:

```bash
npx vitest run \
  tests/unit/merchant-route-access-policy.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/routes/explicit-route-config.test.ts

npm test
npm run typecheck
npm run build

npx eslint \
  app/routes/app/billing/options/route.tsx \
  app/components/dashboard/BillingPurchaseHub.jsx \
  tests/unit/billing-purchase-hub.test.tsx \
  tests/unit/billing-ui.test.ts

git diff --check
```

Expected outcomes:

```text
focused Vitest: exit 0
full npm test: exit 0
npm run build: exit 0
focused ESLint: exit 0
git diff --check: exit 0
```

For `npm run typecheck`:

- if it passes, record PASS;
- if it reports only a repository baseline condition already documented in `docs/development-baseline.md`, verify none of the diagnostics originate from the four changed files, record the applicable baseline ID, and continue;
- any new diagnostic in a changed file is task failure and must be corrected before review;
- do not expand this task into unrelated baseline cleanup.

## Completion Report requirements

The Completion Report must record:

```text
implementation commit SHA
parent Completion Report commit SHA
all four changed implementation files
confirmation that no unauthorized implementation file changed
focused Vitest command + result
full npm test result
typecheck result / baseline ID if applicable
build result
focused ESLint result
git diff --check result
confirmation that ONBOARDING options hides purchase history
confirmation that ACTIVE/NO_CONTRACT/FROZEN/BILLING_ATTENTION keep purchase history visible
confirmation that billing-ui.test.ts retains both original describe suites with one valid import section
```

Do not claim a validation result that was not actually run.

## Stop conditions

STOP and return to `moda_architect` without broadening scope if any of the following occurs:

```text
the correction appears to require changing the MerchantSurface matrix
the correction appears to require editing merchant-route-access-policy.ts
the correction appears to require editing app/routes.ts
the correction appears to require changing purchase-history route authorization
the correction appears to require billing/provider/refund business behaviour changes
the correction appears to require Prisma/schema/shared/background/messaging/gateway/admin changes
a required fix cannot be completed within the four authorized implementation files
```

When the implementation and validation are complete:

```text
set task status to review
complete the Completion Report
return control to moda_architect
STOP
```

Do not start billing v1.1, ARCH-011, or another task automatically.

## Work Items

- [ ] Derive `purchaseHistoryAvailable` from canonical ARCH-013 route policy in billing-options loader.
- [ ] Return the capability from both loader branches and pass it to `BillingPurchaseHub`.
- [ ] Conditionally render the purchased-credit-history link.
- [ ] Add allowed/denied BillingPurchaseHub tests.
- [ ] Consolidate `billing-ui.test.ts` imports without deleting either existing suite.
- [ ] Add loader-state tests for ONBOARDING, ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION.
- [ ] Preserve direct purchase-history authorization evidence.
- [ ] Run all required validation.
- [ ] Complete the Completion Report and return to architect review.

## Completion Report

Status: Complete; returned to Architect Review.

### Implementation

- Implementation commit: `20a6034` (`fix billing purchase history route coherence`), pushed to `task/ARCH-013-SHOPIFY-002`.
- Changed implementation files:
  - `app/routes/app/billing/options/route.tsx`
  - `app/components/dashboard/BillingPurchaseHub.jsx`
  - `tests/unit/billing-purchase-hub.test.tsx`
  - `tests/unit/billing-ui.test.ts`
- No unauthorized implementation file changed. Read-only policy, route-graph, and direct purchase-history route files were unchanged.
- `purchaseHistoryAvailable` is derived from the canonical merchant surface policy and returned from both loader branches.
- ONBOARDING keeps billing options available while hiding purchase history; ACTIVE, NO_CONTRACT, FROZEN, and BILLING_ATTENTION keep purchase history visible.
- `billing-ui.test.ts` retains both original describe suites in one valid import section.

### Validation

- Focused Vitest: PASS, 4 files and 67 tests passed.
  - `npx vitest run tests/unit/merchant-route-access-policy.test.ts tests/unit/billing-ui.test.ts tests/unit/billing-purchase-hub.test.tsx tests/unit/routes/explicit-route-config.test.ts`
- Full `npm test`: PASS, 44 files passed, 2 skipped; 555 tests passed, 3 skipped.
- `npm run typecheck`: non-zero due documented `TYPECHECK-001` repository baseline debt; no diagnostics originated in the four changed files.
- `npm run build`: PASS.
- Focused ESLint: PASS for all four changed files. The command emitted only the repository's existing unsupported-TypeScript-version warning.
- `git diff --check`: PASS.
- Locked dependencies were installed with `npm ci`; the generated build and full test run completed successfully.

### Deviations

The first full test invocation raced Prisma client generation during parallel validation and reported unrelated initialization failures; after the build generated the client, the required full `npm test` rerun passed. No implementation scope was broadened.

### Architect Review

Ready for `moda_architect` review. Parent Completion Report commit SHA will be recorded by the report commit.
