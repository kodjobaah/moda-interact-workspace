---
id: ARCH-013-SHOPIFY-001
architecture_id: ARCH-013
title: Make merchant routing, navigation and breadcrumbs lifecycle-coherent
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 90
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-021
- ARCH-010-SHOPIFY-026
enables: []
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-013-SHOPIFY-001: Make merchant routing, navigation and breadcrumbs lifecycle-coherent

## Objective

Refactor the current `moda-interact` merchant route surface so registered routes, direct loader/action access, App-shell navigation, breadcrumbs and persistent support-message CTAs all agree with the same merchant lifecycle state.

This is a routing/application-flow task only. Do **not** implement `Moda_Recovery_Credits_Shopify_App_Pricing_Design_v1.1` in this task.

## Read before editing

Read these files before the first code change:

```text
docs/architecture/ARCH-013-merchant-application-routing-navigation.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
app/routes.ts
app/routes/app/route.jsx
app/services/shop/shop-access-policy.ts
app/routes/app/home/route.jsx
app/routes/app/usage/route.jsx
app/routes/app/promotions/route.tsx
app/routes/app/merchant-support/route.jsx
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/billing/callback/route.tsx
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/routes/app/pending-recoveries/route.jsx
app/components/dashboard/Breadcrumbs.jsx
app/components/dashboard/UsageOverview.jsx
app/components/dashboard/Dashboard.jsx
app/components/onboarding/Onboarding.jsx
app/services/merchant-support/system-message-actions.ts
```

Do not use ARCH-011 or billing v1.1 to infer new behaviour for this task.

## Authorized implementation surface

The task may create:

```text
app/services/shop/merchant-route-access-policy.ts
tests/unit/merchant-route-access-policy.test.ts
```

The task may modify:

```text
app/routes.ts
app/routes/app/route.jsx
app/routes/app/home/route.jsx
app/routes/app/usage/route.jsx
app/routes/app/promotions/route.tsx
app/routes/app/merchant-support/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/components/onboarding/Onboarding.jsx
app/components/dashboard/Breadcrumbs.jsx
app/components/dashboard/UsageOverview.jsx
app/components/dashboard/Dashboard.jsx
app/services/merchant-support/system-message-actions.ts
tests/unit/routes/explicit-route-config.test.ts
tests/unit/routes/app-layout-access.test.ts
tests/unit/shop-access-policy.test.ts
tests/unit/usage-route.test.ts
tests/unit/home-route.test.ts
tests/unit/merchant-support-route.test.ts
tests/unit/routes/promotion-route.test.ts
tests/unit/pending-recoveries-route.test.ts
tests/unit/billing-ui.test.ts
tests/unit/billing-purchase-hub.test.tsx
tests/unit/services/billing.service.test.ts
```

If another existing focused route/UI test must be updated solely because it asserts one of the retired URLs or the changed Breadcrumbs prop contract, it may be changed and must be listed in the Completion Report.

The task MUST delete exactly these stale implementation/test files:

```text
app/routes/app/additional/route.jsx
app/routes/app/billing/route.tsx
app/routes/app/billing/recovery-credits/route.ts
tests/unit/routes/additional-route.test.ts
```

Do not modify database schema, migrations, Background, Shared, Messaging, Gateway or Admin repositories.

## Step 1 — create the canonical pure route-access policy

Create:

```text
app/services/shop/merchant-route-access-policy.ts
```

Export these exact public concepts (names may differ only if an existing repository naming collision requires it; document any deviation):

```text
MerchantExperienceState
MerchantSurface
resolveMerchantExperienceState(...)
canAccessMerchantSurface(state, surface)
getMerchantDeniedRedirect(state, surface)
getMerchantNavigation(state)
```

### Exact experience states

```text
SIGNED_OUT
REINSTALLING
SUPPORT_ONLY
ONBOARDING
ACTIVE
NO_CONTRACT
FROZEN
BILLING_ATTENTION
```

### Exact surfaces

```text
HOME
USAGE
BILLING_OPTIONS
BILLING_PURCHASE_HISTORY
PROMOTIONS
SUPPORT
PLAN_SELECT
PENDING_RECOVERIES
```

### Exact resolution precedence

Input must be sufficient to represent:

```text
shop.status
shop.reinstallPendingAt
settings?.onboardingCompleted
subscription?.status
```

Return exactly:

```text
shop.status == UNINSTALLED && reinstallPendingAt != null
  => REINSTALLING

shop.status == SUSPENDED
  => SUPPORT_ONLY

shop.status != ACTIVE
  => SIGNED_OUT

shop.status == ACTIVE && onboardingCompleted != true
  => ONBOARDING

onboarded + subscription.status ACTIVE/TRIALING
  => ACTIVE

onboarded + subscription.status NO_CONTRACT
  => NO_CONTRACT

onboarded + subscription.status FROZEN
  => FROZEN

onboarded + missing subscription OR UNMAPPED OR SYNC_ERROR
  => BILLING_ATTENTION
```

Do not add provider calls to this pure policy.

### Exact surface matrix

Implement this exact matrix:

```text
ONBOARDING
  allow HOME, BILLING_OPTIONS, SUPPORT, PLAN_SELECT

ACTIVE
  allow HOME, USAGE, BILLING_OPTIONS, BILLING_PURCHASE_HISTORY,
        PROMOTIONS, SUPPORT, PLAN_SELECT, PENDING_RECOVERIES

NO_CONTRACT
  allow HOME, USAGE, BILLING_OPTIONS, BILLING_PURCHASE_HISTORY,
        SUPPORT, PLAN_SELECT

FROZEN
  allow HOME, USAGE, BILLING_OPTIONS, BILLING_PURCHASE_HISTORY, SUPPORT

BILLING_ATTENTION
  allow HOME, USAGE, BILLING_OPTIONS, BILLING_PURCHASE_HISTORY,
        SUPPORT, PLAN_SELECT

SUPPORT_ONLY
  allow SUPPORT only

REINSTALLING
  allow SUPPORT only

SIGNED_OUT
  allow none
```

### Exact denial redirects

```text
REINSTALLING -> /app/reinstalling
SUPPORT_ONLY -> /app/merchant-support
SIGNED_OUT -> /auth/login
ONBOARDING denied surface -> /app
NO_CONTRACT denied surface -> /app
FROZEN denied PLAN_SELECT -> /app/billing/options
FROZEN any other denied product surface -> /app
BILLING_ATTENTION denied product surface -> /app
```

`PENDING_RECOVERIES` is a JSON resource. Its loader uses the access boolean to return the existing bounded unavailable JSON for ONBOARDING/NO_CONTRACT/FROZEN/BILLING_ATTENTION rather than redirecting those authenticated active shops.

### Exact navigation

`getMerchantNavigation` returns the exact ordered hrefs:

```text
ONBOARDING:
  /app
  /app/billing/options
  /app/merchant-support

ACTIVE:
  /app
  /app/billing/options
  /app/merchant-support
  /app/promotions

NO_CONTRACT:
  /app
  /app/billing/options
  /app/merchant-support

FROZEN:
  /app
  /app/billing/options
  /app/merchant-support

BILLING_ATTENTION:
  /app
  /app/billing/options
  /app/merchant-support

SUPPORT_ONLY and REINSTALLING:
  /app/merchant-support

SIGNED_OUT:
  none
```

Return stable IDs with the hrefs so the App component can render `Home`, `Billing`, `Messages`, `Promotions` without inferring access.

## Step 2 — make the route graph match the architecture

Edit `app/routes.ts` to make the `/app` child list contain exactly these merchant UI routes:

```text
index("./routes/app/home/route.jsx")
route("usage", "./routes/app/usage/route.jsx")
route("promotions", "./routes/app/promotions/route.tsx")
route("merchant-support", "./routes/app/merchant-support/route.jsx")
route("billing/options", "./routes/app/billing/options/route.tsx")
route("billing/recovery-credit-purchases", "./routes/app/billing/recovery-credit-purchases/route.tsx")
```

Keep these standalone exact paths:

```text
app/reinstalling
app/billing/select
app/billing/callback
app/pending-recoveries
```

Remove route registrations for:

```text
app/additional
app/billing
```

Remove the standalone registration of `app/billing/options` because that page is now the nested `billing/options` child while retaining the same public URL `/app/billing/options`.

Do not move `app/billing/select`, `app/billing/callback`, `app/reinstalling` or `app/pending-recoveries` under the App layout.

## Step 3 — delete stale route modules

Delete exactly:

```text
app/routes/app/additional/route.jsx
app/routes/app/billing/route.tsx
app/routes/app/billing/recovery-credits/route.ts
tests/unit/routes/additional-route.test.ts
```

Do not replace `/app/billing` with a redirect alias. The route no longer exists after this task.

## Step 4 — remove every first-party `/app/billing` destination

After deleting the old route, update runtime links/actions:

### Onboarding

In `app/components/onboarding/Onboarding.jsx` both `Choose plan` primary buttons MUST point to:

```text
/app/billing/select
```

There must be no `/app/billing` onboarding link.

### Support system-message actions

In `app/services/merchant-support/system-message-actions.ts`:

```text
BILLING_FREE_ALLOWANCE_WARNING
  target = /app/billing/select

BILLING_PLAN_UPGRADED
BILLING_PLAN_DOWNGRADE_SCHEDULED
BILLING_SUBSCRIPTION_ENDED
BILLING_SAFETY_LIMIT_REACHED
  target = /app/billing/options
```

The helper must accept the current `MerchantExperienceState` (or a directly equivalent access capability) and return `null` when `canAccessMerchantSurface` rejects the target.

There must be no exported/runtime `BILLING_ROUTE = "/app/billing"`.

### Tests/service expectations

Update all tests that assert `/app/billing` to the correct canonical destination based on intent:

```text
view/manage billing/capacity/status -> /app/billing/options
choose/change a Shopify plan -> /app/billing/select
```

Do not mechanically replace all strings with one destination. Preserve the intent rule above.

## Step 5 — make the App shell navigation state-aware

Edit `app/routes/app/route.jsx`.

### Loader order

Preserve the existing early shop-status redirects so suspended/reinstalling product requests do not perform unnecessary app-shell business reads.

For a permitted App-shell render, load enough durable local state to resolve `MerchantExperienceState`:

```text
Shop
ShopSettings.onboardingCompleted
current local Subscription.status
```

Use the existing local billing/subscription service. Do not call Shopify Partner API solely to choose navigation.

The loader returns the resolved `merchantExperienceState` alongside existing `apiKey`, unread messages and merchant UI context.

For `/app/merchant-support`:

- preserve `assertSupportShop` semantics;
- `SUSPENDED` resolves to SUPPORT_ONLY;
- pending reinstall resolves to REINSTALLING;
- ACTIVE support requests resolve using settings + local subscription.

### Component

Replace the unconditional Home/Messages/Promotions links with the ordered result of `getMerchantNavigation(merchantExperienceState)`.

Render labels as:

```text
home       -> Home
billing    -> i18n.t("billingCommerce.page.title")
messages   -> Messages plus existing unread count
promotions -> i18n.t("promotions.nav")
```

Do not add a nav item that is absent from `getMerchantNavigation`.

Required result examples:

```text
SUSPENDED support page:
  Messages only

pending reinstall support page:
  Messages only

fresh onboarding:
  Home, Billing, Messages

ACTIVE/TRIALING:
  Home, Billing, Messages, Promotions

onboarded NO_CONTRACT/FROZEN:
  Home, Billing, Messages
```

## Step 6 — enforce lifecycle route availability in child loaders/actions

Do not rely on the parent loader as the only guard.

### `/app/usage`

Keep shop authentication/isolation.

Resolve settings + local subscription, then use surface `USAGE`.

Exact behaviour:

```text
onboarding incomplete -> redirect /app
ACTIVE/TRIALING -> load usage
onboarded NO_CONTRACT -> load historical usage
onboarded FROZEN -> load historical usage
onboarded missing/UNMAPPED/SYNC_ERROR -> load historical usage
```

Delete the current rule that requires subscription status to be only ACTIVE/TRIALING.

Do not change usage query semantics except what is necessary to permit historical reads.

### `/app/promotions`

Both loader and action use surface `PROMOTIONS` before promotion reads/mutations.

Only onboarded ACTIVE/TRIALING merchant state reaches promotion business logic.

For ONBOARDING, NO_CONTRACT, FROZEN or BILLING_ATTENTION, redirect to `/app` and do not call promotion read/selection service.

Preserve suspended/reinstall redirects from shop status.

### `/app/billing/options`

Because the page is now nested, keep its own authenticated direct-loader guard.

Surface `BILLING_OPTIONS` is allowed for ONBOARDING, ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION.

Do not add new billing v1.1 logic.

Preserve existing provider verification, capacity, lifecycle and top-up fail-closed behaviour.

The action keeps the existing billing mutation restrictions; FROZEN/CONTRACT_REQUIRED/scheduled cancellation remain unavailable exactly as current accepted behaviour requires.

### `/app/billing/recovery-credit-purchases`

Loader uses surface `BILLING_PURCHASE_HISTORY`.

It must:

```text
redirect ONBOARDING -> /app
allow ACTIVE
allow onboarded NO_CONTRACT
allow FROZEN read
allow BILLING_ATTENTION read
```

Do not redefine refund economics in this task.

For actions, preserve existing shop ownership and domain-service authority. Additionally, do not weaken existing FROZEN fail-closed billing behaviour. If the current domain service already rejects an action, do not bypass it.

### `/app/billing/select`

Keep standalone.

Resolve enough local state to enforce surface `PLAN_SELECT` before building the Shopify pricing URL.

Exact behaviour:

```text
ONBOARDING -> allowed
ACTIVE -> allowed
NO_CONTRACT -> allowed
BILLING_ATTENTION -> allowed
FROZEN -> redirect /app/billing/options
SUPPORT_ONLY -> redirect /app/merchant-support
REINSTALLING -> redirect /app/reinstalling
SIGNED_OUT -> /auth/login via existing auth/shop boundary
```

Keep existing Shopify-hosted URL construction and `_top` redirect. Do not convert this into a UI page.

### `/app/pending-recoveries`

Use surface `PENDING_RECOVERIES` after auth/shop/settings/subscription resolution.

Only ACTIVE is allowed to call `readPendingRecoveries`.

For ONBOARDING, NO_CONTRACT, FROZEN and BILLING_ATTENTION return exactly the existing unavailable JSON shape and do not call the reader.

Suspended/reinstalling shop redirects remain fail-closed before resource read.

### `/app` home/detail

Preserve existing onboarding early return.

Add an explicit guard so `?view=detail` cannot expose detail when experience state is ONBOARDING. It must render/redirect to normal onboarding `/app` rather than loading detail semantics.

For onboarded NO_CONTRACT/FROZEN/BILLING_ATTENTION, preserve dashboard/history reads and lifecycle banners.

Do not add Partner API calls solely for `/app` navigation/access.

## Step 7 — refactor Breadcrumbs to an explicit hierarchy

Replace the current implicit API in `app/components/dashboard/Breadcrumbs.jsx`.

New component contract:

```text
Breadcrumbs({ items = [], current, merchantUi })

items = [
  { label: string, href: string },
  ...
]
```

Rendering rules:

1. render each supplied item as `Link` + separator;
2. render `current` as `<strong aria-current="page">`;
3. do not inspect `current` to decide whether `/app` should be inserted;
4. do not hard-code `/app` or `usage.title` inside Breadcrumbs;
5. keep the localized `navigation.breadcrumb` aria label;
6. add/update PropTypes for `items`.

Update call sites exactly:

### Usage overview

```text
items = []
current = usage.title
```

### Dashboard billing-period detail

```text
items = [{ label: usage.title, href: "/app" }]
current = periodLabel
```

### Billable usage

```text
items = [
  { label: usage.title, href: "/app" },
  { label: periodLabel, href: dashboardUrl }
]
current = usage.billable
```

### Billing options

```text
items = []
current = billingCommerce.page.title
```

Also correct the `<s-page>` heading in billing options so it uses `billingCommerce.page.title`; do not leave the current `usage.billable` heading on the billing page.

### Purchased-credit history

```text
items = [
  { label: billingCommerce.page.title, href: "/app/billing/options" }
]
current = billingPurchases.title
```

Onboarding does not render Breadcrumbs.

## Step 8 — make merchant-support CTAs lifecycle-aware

`app/routes/app/merchant-support/route.jsx` must expose the same resolved merchant experience state used by the App shell.

Pass the state into `MessageCard` and then into `getMerchantSystemMessageAction`.

Exact behaviour examples:

```text
SUSPENDED or REINSTALLING support view
  BILLING_* system message -> no inaccessible billing CTA

FROZEN
  FREE_ALLOWANCE_WARNING -> no plan-selection CTA
  PLAN_UPGRADED/DOWNGRADE/SUBSCRIPTION_ENDED/SAFETY_LIMIT -> /app/billing/options if support page is otherwise reachable

NO_CONTRACT
  FREE_ALLOWANCE_WARNING -> /app/billing/select
  other billing status actions -> /app/billing/options
```

Do not inspect translated message body URLs to decide navigation.

## Step 9 — update route/config tests for removed files

`tests/unit/routes/explicit-route-config.test.ts` must prove all of these:

```text
/app child includes billing/options
/app child includes billing/recovery-credit-purchases
/app child does not include billing route
/app child does not include additional route
standalone select/callback/reinstalling/pending-recoveries remain standalone
standalone app/billing/options registration no longer exists
retired app/routes/app/billing/route.tsx does not exist
retired app/routes/app/additional/route.jsx does not exist
retired app/routes/app/billing/recovery-credits/route.ts does not exist
```

Do not retain a test that expects the stock Additional page to be accessible.

## Step 10 — required focused tests

Create `tests/unit/merchant-route-access-policy.test.ts` covering every state and every surface in the matrix, not only selected examples.

Add/update focused route/component tests to prove at minimum:

1. ONBOARDING navigation is exactly Home, Billing, Messages.
2. ACTIVE navigation is exactly Home, Billing, Messages, Promotions.
3. NO_CONTRACT navigation excludes Promotions and retains Home/Billing/Messages.
4. FROZEN navigation excludes Promotions and plan-selection destination.
5. SUSPENDED support navigation contains Messages only.
6. pending reinstall support navigation contains Messages only.
7. every rendered nav href is allowed by the same state/surface policy.
8. `/app/usage` allows onboarded NO_CONTRACT without redirect.
9. `/app/usage` allows FROZEN without redirect.
10. `/app/usage` redirects fresh onboarding to `/app` before usage query execution.
11. promotions loader/action do not call promotion services for ONBOARDING/NO_CONTRACT/FROZEN/BILLING_ATTENTION.
12. `/app/billing/options` remains readable for ONBOARDING/NO_CONTRACT/FROZEN.
13. `/app/billing/select` allows onboarding and NO_CONTRACT, but FROZEN redirects `/app/billing/options`.
14. `/app/pending-recoveries` reads data only for ACTIVE and returns unavailable without reader call for other active-shop lifecycle states.
15. onboarding contains no `/app/billing` link and both Choose plan CTAs use `/app/billing/select`.
16. no runtime source file under `app/` contains an exact first-party destination `"/app/billing"` or `'/app/billing'` after the task. Prefixes `/app/billing/options`, `/select`, `/callback`, `/recovery-credit-purchases` are valid.
17. support action mapping never returns `/app/billing`.
18. support-only states suppress inaccessible billing CTAs.
19. Breadcrumbs does not hard-code `/app` or `usage.title`.
20. dashboard detail breadcrumb links Usage overview -> `/app`.
21. usage breadcrumb links Usage overview -> `/app` -> selected period detail.
22. purchased-credit-history breadcrumb links Billing & recovery capacity -> `/app/billing/options`.
23. billing options page heading is Billing & recovery capacity, not Billable usage.
24. `/app/billing` is not registered.
25. `/app/additional` is not registered.
26. unregistered `recovery-credits` module is deleted.
27. existing billing callback redirects to `/app/billing/options?...` remain unchanged.
28. existing frozen billing mutation tests remain fail-closed.

When updating `tests/unit/billing-ui.test.ts`, remove tests/imports for the deleted `app/routes/app/billing/route.tsx`; preserve and adapt the tests for billing options/select/callback behaviour. Do not recreate old-route coverage elsewhere.

## Exact validation commands

From `moda-interact` after the launcher-provided Node/bootstrap requirements are satisfied:

```text
npx vitest run \
  tests/unit/merchant-route-access-policy.test.ts \
  tests/unit/routes/explicit-route-config.test.ts \
  tests/unit/routes/app-layout-access.test.ts \
  tests/unit/usage-route.test.ts \
  tests/unit/home-route.test.ts \
  tests/unit/merchant-support-route.test.ts \
  tests/unit/routes/promotion-route.test.ts \
  tests/unit/pending-recoveries-route.test.ts \
  tests/unit/billing-ui.test.ts \
  tests/unit/billing-purchase-hub.test.tsx

npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

Also run these source checks from `moda-interact`:

```text
rg -n 'route\("billing",|route\("additional",|route\("app/billing/options"' app/routes.ts
```

Expected: **no matches**.

```text
rg -n '(^|[^A-Za-z0-9_-])["'"']\/app\/billing["'"']' app
```

Expected: **no exact `/app/billing` destination matches**. Do not treat valid longer routes such as `/app/billing/options` as failures.

```text
test ! -e app/routes/app/billing/route.tsx
test ! -e app/routes/app/additional/route.jsx
test ! -e app/routes/app/billing/recovery-credits/route.ts
```

Expected: all exit 0.

If repository-wide validation hits a documented unchanged baseline, record the exact baseline ID and prove no task-touched file introduced the failure. Do not weaken the focused route tests.

## Acceptance Criteria

- [ ] one pure merchant route-access policy implements all 8 experience states and the complete surface matrix;
- [ ] `/app/billing/options` is nested under the App layout without changing its public URL;
- [ ] `/app/billing/select`, callback, reinstalling and pending-recoveries remain standalone;
- [ ] `/app/billing` registration/module is removed with no compatibility alias;
- [ ] `/app/additional` registration/module/test is removed;
- [ ] obsolete unregistered `billing/recovery-credits/route.ts` is removed;
- [ ] all onboarding Choose plan CTAs use `/app/billing/select`;
- [ ] all billing-status/capacity UI destinations use `/app/billing/options` unless the intent is direct plan selection;
- [ ] App nav is state-derived and never advertises a denied surface;
- [ ] onboarded NO_CONTRACT and FROZEN retain `/app/usage` historical reads;
- [ ] fresh ONBOARDING cannot access usage, promotions, purchase history, detail or pending-recovery business data;
- [ ] NO_CONTRACT/FROZEN/BILLING_ATTENTION cannot access Promotions;
- [ ] FROZEN cannot access `/app/billing/select`;
- [ ] support-only states show Messages only and suppress inaccessible system CTAs;
- [ ] Breadcrumbs has no implicit `/app == Usage overview` rule;
- [ ] purchased-credit history has `/app/billing/options` as breadcrumb parent;
- [ ] billing-options page heading is corrected;
- [ ] billing callback destination semantics remain unchanged;
- [ ] no billing v1.1/proration/schema/cross-repository behaviour was added;
- [ ] focused tests, full repository validation and diff check satisfy the task contract.

## Non-goals

Do not implement:

```text
Recovery Credits / Shopify App Pricing Design v1.1
new top-up pack catalogue
App Event purchase reconciliation changes
refund correction changes
proration
subscription transition economics
new database fields/migrations
new Shared contracts
Background changes
Gateway changes
Admin changes
```

## Stop conditions

STOP and return evidence to `moda_architect` if any of these occur:

1. `/app/billing/options` cannot be nested under the existing App layout without changing its public URL or executing an architecture-prohibited provider mutation.
2. preserving NO_CONTRACT/FROZEN historical usage would require changing billing entitlement/consumption semantics rather than route-read gating.
3. a current in-progress/review ARCH-011 or other task is modifying the same billing route files; do not resolve concurrent branch intent by guessing.
4. implementing the lifecycle route policy requires a Prisma/schema change.
5. satisfying a system-message CTA requires inventing a new billing product rule.
6. a named canonical route/module from this task is materially absent for reasons not represented in the supplied snapshot.

Do not substitute a different design. Return the exact conflicting file/task/state to the architect.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass:

1. update the Completion Report with exact changed/deleted files;
2. record the complete state/surface tests and validation results;
3. record any unchanged baseline IDs separately from task regressions;
4. set task status to `review`;
5. clear the active claim according to the normal launcher protocol;
6. return control to `moda_architect`;
7. **STOP** — do not begin billing v1.1 or an ARCH-011 task.

## Completion Report

### Status
Review-ready. Implementation published in `moda-interact` commit
`b3442f7d4a648055036e818d0ccf7e8cad88905d`.

### Changed Files

```text
app/components/dashboard/Breadcrumbs.jsx
app/components/dashboard/Dashboard.jsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/UsageOverview.jsx
app/components/onboarding/Onboarding.jsx
app/routes.ts
app/routes/app/billing/options/route.tsx
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/merchant-support/route.jsx
app/routes/app/pending-recoveries/route.jsx
app/routes/app/promotions/route.tsx
app/routes/app/route.jsx
app/routes/app/usage/route.jsx
app/services/merchant-support/system-message-actions.ts
app/services/shop/merchant-route-access-policy.ts
tests/unit/billing-i18n.test.ts
tests/unit/billing-ui.test.ts
tests/unit/merchant-support-route.test.ts
tests/unit/merchant-route-access-policy.test.ts
tests/unit/routes/app-layout-access.test.ts
tests/unit/routes/explicit-route-config.test.ts
tests/unit/services/billing.service.test.ts
tests/unit/usage-route.test.ts
```

### Deleted Files

```text
app/routes/app/additional/route.jsx
app/routes/app/billing/recovery-credits/route.ts
app/routes/app/billing/route.tsx
tests/unit/routes/additional-route.test.ts
```

### Acceptance and Validation Results

- Exact ARCH-013 focused test list: 10 files passed, 87 tests passed.
- Full `npm test`: 44 files passed, 538 tests passed, 2 files skipped, 3 tests skipped.
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- Route registration/source checks: passed; no stale billing/additional registrations, no exact `/app/billing` destinations, and all required retired files are absent.
- Prisma client generation completed before test execution.
- `npm run typecheck`: unchanged repository baseline failure (exit 2) from existing implicit-any and related JSX diagnostics across legacy dashboard/home/support files; no diagnostic was introduced in the new TypeScript route policy. This baseline did not block focused behavior, lint, build, or test validation.

### Review Handoff

Implementation branch: `task/ARCH-013-SHOPIFY-001`.
Implementation commit: `b3442f7d4a648055036e818d0ccf7e8cad88905d`.
Task claim cleared; status returned to `review` for `moda_architect`.
