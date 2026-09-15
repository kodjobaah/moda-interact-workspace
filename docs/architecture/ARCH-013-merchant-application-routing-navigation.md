---
id: ARCH-013
title: Merchant application routing, navigation and lifecycle coherence
status: implemented
coordinator: moda_architect
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-013: Merchant application routing, navigation and lifecycle coherence

## Status

**Implemented — SHOPIFY-001 Attempt 2 Accepted.**

ARCH-013 is a bounded pre-billing-refactor initiative for `moda-interact` only. It fixes the merchant application's current route graph, access/navigation mismatch, breadcrumb hierarchy and stale route artefacts **before** implementation work begins from `Moda_Recovery_Credits_Shopify_App_Pricing_Design_v1.1`.

ARCH-013 does not implement the v1.1 billing design. It preserves existing billing/provider business behaviour except where route availability or route ownership must be corrected to make the existing merchant journey coherent.

## Problem statement

The current merchant application has four independent sources of navigation truth:

```text
React Router registration
shop-level loader guards
individual lifecycle checks inside route loaders/actions
UI links/navigation/breadcrumbs
```

They are not currently aligned.

Observed defects include:

1. `/app/billing/options` is a full embedded merchant page but is registered outside the `/app` layout, so it does not inherit the normal app shell/navigation.
2. `/app/billing` and `/app/billing/options` are competing billing pages with overlapping responsibilities.
3. `/app/usage` rejects onboarded `NO_CONTRACT` and `FROZEN` merchants even though ARCH-010 preserves read/history access for both states.
4. the App shell always renders Home, Messages and Promotions, including for merchants whose current lifecycle state cannot access Home or Promotions.
5. persistent merchant-support system-message CTAs can point to routes the merchant's current lifecycle state rejects.
6. the Breadcrumbs component hard-codes `/app` as `Usage overview`, even though `/app` can render onboarding, usage overview or billing-period detail.
7. purchased-credit history omits its actual billing parent from the breadcrumb hierarchy.
8. fresh onboarding merchants can directly reach product/billing-history surfaces that ARCH-010 says are unavailable until a mapped active/trialing plan exists.
9. the stock Shopify `/app/additional` route is still registered and reachable.
10. `app/routes/app/billing/recovery-credits/route.ts` contains an obsolete unregistered implementation beside the canonical purchased-credit route.

The server-side guards prevent many actual unauthorized actions, but navigation routinely advertises destinations that immediately redirect or fail. That is a product-flow and authorization-presentation defect even where no security bypass exists.

## Relationship to ARCH-010

ARCH-013 does not replace ARCH-010 lifecycle semantics. It makes the merchant routes obey them consistently.

Where ARCH-010 historical text names `/app/billing`, ARCH-013 changes the route-level representation to:

```text
/app/billing/options
```

because `/app/billing/options` is already the production billing/recovery-capacity surface and `/app/billing` is redundant.

All underlying lifecycle semantics remain:

- fresh install + onboarding incomplete -> onboarding/plan selection only;
- ACTIVE/TRIALING onboarded merchant -> full merchant application;
- previously onboarded `NO_CONTRACT` -> read/history/billing/support plus plan selection, no execution;
- `FROZEN` -> read/history/billing/support, no billing/product mutations or plan change;
- suspended shop -> support only;
- reinstall pending -> restoration flow plus support;
- fully uninstalled/non-restoring -> authentication/login boundary.

## Goals

ARCH-013 must:

- define one explicit merchant experience state model used by route guards and UI navigation;
- keep low-level Shopify shop-status gating fail-closed;
- align direct URL access with the links shown to the merchant;
- preserve historical/read access for onboarded `NO_CONTRACT` and `FROZEN` merchants;
- prevent fresh onboarding merchants from entering product/history/promotions surfaces;
- make `/app/billing/options` the canonical embedded billing/capacity page;
- keep `/app/billing/select` as the standalone Shopify-hosted plan-selection transition;
- keep `/app/billing/callback` as the standalone Shopify plan-selection callback/reconciliation transition;
- remove `/app/billing` as a route and implementation;
- remove stale route modules and their stale tests;
- make breadcrumbs declarative instead of assuming `/app == Usage overview`;
- make persistent support-message CTAs lifecycle-aware;
- keep `/app/pending-recoveries` an execution-only resource available only for onboarded ACTIVE/TRIALING merchants;
- add focused tests proving the full state/route/navigation matrix.

## Non-goals

ARCH-013 MUST NOT:

- implement Recovery Credits / Shopify App Pricing Design v1.1;
- change recovery-credit purchase valuation/reconciliation;
- change refund/correction economics;
- implement ARCH-011 proration behaviour;
- change Shopify Partner API commercial authority;
- change billing entitlements, allowances, consumption order or refund rules;
- add a new merchant Admin surface;
- change database schema;
- change Shared contracts;
- change Background/Messaging/Gateway behaviour;
- introduce a second billing page;
- preserve `/app/billing` as a compatibility alias or redirect route.

If implementation discovers that one of these changes is required, the task stops and returns evidence to `moda_architect`.

## Canonical target route graph

### Embedded merchant UI under `/app` layout

```text
/app
/app/usage
/app/promotions
/app/merchant-support
/app/billing/options
/app/billing/recovery-credit-purchases
```

These routes inherit the embedded App shell. Their child loaders/actions must still perform their own capability checks because parent and child loaders may execute independently/parallel; the parent layout is not the only correctness boundary.

### Standalone transition/restoration/resource routes

```text
/app/reinstalling
/app/billing/select
/app/billing/callback
/app/pending-recoveries
```

Semantics:

```text
/app/reinstalling
  restoration UI; intentionally standalone

/app/billing/select
  transition only; authenticates -> validates merchant lifecycle -> redirects _top to Shopify-hosted App Pricing
  renders no merchant page

/app/billing/callback
  transition/reconciliation only; not a merchant navigation destination

/app/pending-recoveries
  JSON resource; no app-shell UI
```

### Removed routes/modules

The following MUST NOT remain registered or implemented after ARCH-013-SHOPIFY-001:

```text
/app/billing
/app/additional
app/routes/app/billing/route.tsx
app/routes/app/additional/route.jsx
app/routes/app/billing/recovery-credits/route.ts
```

There is no `/app/billing` redirect compatibility alias in ARCH-013. All first-party links/tests must be updated to the canonical route.

## Canonical billing journey

Each surviving billing URL has one responsibility:

```text
/app/billing/options
  canonical embedded Billing & recovery capacity page
  reads current billing/capacity state
  owns current production BillingPurchaseHub UI
  links to plan selection and purchased-credit history when allowed

/app/billing/select
  no UI
  redirects to Shopify-hosted App Pricing when lifecycle permits plan selection

/app/billing/callback
  no navigational UI
  verifies/reconciles provider return
  established merchant return -> /app/billing/options?plan_change=...
  initial activation return -> /app

/app/billing/recovery-credit-purchases
  embedded purchase/refund history/management page
  breadcrumb parent = /app/billing/options
```

All onboarding `Choose plan` CTAs go directly to `/app/billing/select`.

All first-party `View billing`, lifecycle-status and capacity-management links go to `/app/billing/options`.

## Merchant experience state model

`moda-interact` must expose one pure application-level policy with these exact states:

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

Resolution precedence is binding:

```text
1. Shop.status == UNINSTALLED && reinstallPendingAt != null
     -> REINSTALLING

2. Shop.status == SUSPENDED
     -> SUPPORT_ONLY

3. Shop.status != ACTIVE
     -> SIGNED_OUT

4. Shop.status == ACTIVE && onboardingCompleted != true
     -> ONBOARDING

5. Shop.status == ACTIVE && onboardingCompleted == true && Subscription.status in ACTIVE/TRIALING
     -> ACTIVE

6. Shop.status == ACTIVE && onboardingCompleted == true && Subscription.status == NO_CONTRACT
     -> NO_CONTRACT

7. Shop.status == ACTIVE && onboardingCompleted == true && Subscription.status == FROZEN
     -> FROZEN

8. Shop.status == ACTIVE && onboardingCompleted == true && Subscription is missing or status is UNMAPPED/SYNC_ERROR
     -> BILLING_ATTENTION
```

`onboardingCompleted=false` wins over any partially observed subscription state for merchant page routing. A first activation is not complete until the accepted onboarding lifecycle has completed.

## Merchant surface matrix

Legend: `Y` = route/read surface allowed; `N` = denied by route policy.

| Experience state | `/app` | `/app/usage` | `/app/billing/options` | purchase history | promotions | support | `/app/billing/select` | pending recoveries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ONBOARDING | Y | N | Y | N | N | Y | Y | N |
| ACTIVE | Y | Y | Y | Y | Y | Y | Y | Y |
| NO_CONTRACT | Y | Y | Y | Y | N | Y | Y | N |
| FROZEN | Y | Y | Y | Y | N | Y | N | N |
| BILLING_ATTENTION | Y | Y | Y | Y | N | Y | Y | N |
| SUPPORT_ONLY | N | N | N | N | N | Y | N | N |
| REINSTALLING | N | N | N | N | N | Y | N | N |
| SIGNED_OUT | N | N | N | N | N | N | N | N |

`/app?view=detail` is part of the `/app` surface. Therefore it is available for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION once onboarding is complete, and unavailable to ONBOARDING.

The purchase-history route remains readable for onboarded historical states. ARCH-013 does not redefine refund eligibility; existing server/domain rules remain authoritative. FROZEN must continue to reject billing/product mutations according to accepted ARCH-010 behaviour.

## Denied-route destinations

Use these deterministic redirects for merchant UI/resource denial:

```text
REINSTALLING
  -> /app/reinstalling

SUPPORT_ONLY
  -> /app/merchant-support

SIGNED_OUT
  -> /auth/login

ONBOARDING denied product/history route
  -> /app

NO_CONTRACT denied execution-only route
  -> /app

FROZEN denied execution-only route
  -> /app

FROZEN /app/billing/select
  -> /app/billing/options

BILLING_ATTENTION denied execution-only route
  -> /app
```

For `/app/pending-recoveries`, ONBOARDING/NO_CONTRACT/FROZEN/BILLING_ATTENTION may continue returning the existing bounded `available:false` JSON instead of an HTML redirect because it is a resource endpoint. It MUST NOT call `readPendingRecoveries` in those states.

## App navigation contract

The App shell navigation is derived from the merchant experience state. It is never a static unconditional menu.

Exact navigation order:

```text
ONBOARDING
  Home        -> /app
  Billing     -> /app/billing/options
  Messages    -> /app/merchant-support

ACTIVE
  Home        -> /app
  Billing     -> /app/billing/options
  Messages    -> /app/merchant-support
  Promotions  -> /app/promotions

NO_CONTRACT
  Home        -> /app
  Billing     -> /app/billing/options
  Messages    -> /app/merchant-support

FROZEN
  Home        -> /app
  Billing     -> /app/billing/options
  Messages    -> /app/merchant-support

BILLING_ATTENTION
  Home        -> /app
  Billing     -> /app/billing/options
  Messages    -> /app/merchant-support

SUPPORT_ONLY
  Messages    -> /app/merchant-support

REINSTALLING when support page is rendered
  Messages    -> /app/merchant-support
```

The standalone reinstalling page keeps its existing restoration UI and support link; it does not need to render the complete App shell.

No main navigation item may point to a surface that `canAccessMerchantSurface(...)` rejects for the same experience state.

## Breadcrumb contract

Breadcrumbs are declarative. The component MUST NOT infer a root breadcrumb from the current label and MUST NOT hard-code `/app` as `Usage overview`.

Canonical call-site hierarchy:

```text
/app onboarding
  no Breadcrumbs component

/app Usage overview
  Usage overview                         (current only)

/app?view=detail...
  Usage overview -> /app
  <billing-period label>                 (current)

/app/usage...
  Usage overview -> /app
  <billing-period label> -> /app?view=detail&...
  Billable usage                         (current)

/app/billing/options
  Billing & recovery capacity            (current only)

/app/billing/recovery-credit-purchases
  Billing & recovery capacity -> /app/billing/options
  Purchased credit history               (current)
```

A breadcrumb parent must always be a route allowed in every lifecycle state that can render the child page.

## Persistent system-message CTA contract

`getMerchantSystemMessageAction` becomes lifecycle-aware.

Canonical destinations:

```text
BILLING_FREE_ALLOWANCE_WARNING
  -> /app/billing/select only when PLAN_SELECT surface is allowed
  -> otherwise no CTA

BILLING_PLAN_UPGRADED
BILLING_PLAN_DOWNGRADE_SCHEDULED
BILLING_SUBSCRIPTION_ENDED
BILLING_SAFETY_LIMIT_REACHED
  -> /app/billing/options only when BILLING_OPTIONS surface is allowed
  -> otherwise no CTA
```

No system-message action may return `/app/billing`.

For suspended/restoring support-only views, stale billing CTAs are suppressed instead of advertising an inaccessible billing page.

## Fresh onboarding rules

For `ONBOARDING`:

Allowed direct merchant UI:

```text
/app
/app/billing/options
/app/merchant-support
```

Allowed standalone billing transition:

```text
/app/billing/select
/app/billing/callback
```

Unavailable:

```text
/app/usage
/app/promotions
/app/billing/recovery-credit-purchases
/app?view=detail
/app/pending-recoveries business data
```

All onboarding `Choose plan` buttons link directly to `/app/billing/select`. No onboarding CTA uses removed `/app/billing`.

## Read-only lifecycle rules

### Previously onboarded NO_CONTRACT

Must retain:

```text
/app
/app?view=detail
/app/usage
/app/billing/options
/app/billing/recovery-credit-purchases
/app/merchant-support
/app/billing/select
```

Must not expose:

```text
/app/promotions
pending-recovery business data
```

### FROZEN

Must retain:

```text
/app
/app?view=detail
/app/usage
/app/billing/options
/app/billing/recovery-credit-purchases
/app/merchant-support
```

Must not expose:

```text
/app/promotions
/app/billing/select
pending-recovery business data
```

Existing frozen action guards remain fail-closed.

## Route-loader correctness rule

Do not rely solely on the `/app` parent loader for child access because route loaders may execute independently. Every protected child loader/action must guard the exact surface before performing business reads/mutations.

At minimum:

```text
/app/usage
  surface USAGE

/app/promotions loader/action
  surface PROMOTIONS

/app/billing/options loader
  surface BILLING_OPTIONS

/app/billing/options action
  existing billing mutation guards retained; no v1.1 behaviour added

/app/billing/recovery-credit-purchases loader
  surface BILLING_PURCHASE_HISTORY

/app/merchant-support
  surface SUPPORT using existing support-specific shop semantics

/app/billing/select
  surface PLAN_SELECT

/app/pending-recoveries
  surface PENDING_RECOVERIES before reader call
```

## Stale route cleanup

Delete exactly:

```text
moda-interact/app/routes/app/additional/route.jsx
moda-interact/app/routes/app/billing/route.tsx
moda-interact/app/routes/app/billing/recovery-credits/route.ts
moda-interact/tests/unit/routes/additional-route.test.ts
```

Remove corresponding route registrations and all first-party/test references to `/app/billing`.

Do not delete:

```text
app/routes/app/billing/options/route.tsx
app/routes/app/billing/select/route.jsx
app/routes/app/billing/callback/route.tsx
app/routes/app/billing/recovery-credit-purchases/route.tsx
```

## Sequencing boundary with ARCH-011 and billing v1.1

ARCH-013-SHOPIFY-001 is intentionally executed before new billing v1.1 implementation work.

Do not execute an ARCH-011 Shopify task concurrently with ARCH-013-SHOPIFY-001 if it modifies any of:

```text
app/routes.ts
app/routes/app/billing/**
app/components/dashboard/BillingPurchaseHub.*
app/components/dashboard/SubscriptionChangePanel.*
```

After ARCH-013-SHOPIFY-001 is architect-accepted, pending future task definitions that still name `/app/billing` must be reconciled to the canonical route graph before execution.

No task for the supplied billing v1.1 document is created in this initiative yet.

## Architecture acceptance

ARCH-013 routing work is complete only when:

1. the registered route graph equals the canonical target graph;
2. `/app/billing` and `/app/additional` no longer exist;
3. the unregistered `recovery-credits` route module is deleted;
4. billing options inherits the `/app` shell;
5. route policy, navigation and CTAs agree for every experience state;
6. onboarded `NO_CONTRACT` and `FROZEN` usage/history are readable;
7. fresh onboarding cannot enter usage/promotions/purchase-history/product detail;
8. frozen cannot enter plan selection or promotions;
9. suspended/restoring support pages do not show Home/Billing/Promotions links;
10. breadcrumbs contain no inaccessible or semantically false parent link;
11. focused route/access/navigation tests and repository validation pass with no task regression.


## Post-review update — SHOPIFY-001 Attempt 1 Changes Requested

Architect review of the supplied Attempt-1 implementation found one remaining
functional mismatch.

The canonical merchant policy correctly denies `PENDING_RECOVERIES` to
NO_CONTRACT/FROZEN/BILLING_ATTENTION, and the standalone `/app/pending-recoveries`
resource respects that denial. However, the `/app` home loader still invokes the same
pending-recovery reader for every onboarded merchant.

Therefore ARCH-013 remains **In Progress** until the same `ARCH-013-SHOPIFY-001` task
is corrected so:

```text
ACTIVE
  -> /app may read real pending recoveries

NO_CONTRACT / FROZEN / BILLING_ATTENTION
  -> /app retains historical dashboard/usage reads
  -> /app does not call readPendingRecoveries
  -> pending-recovery presentation is bounded unavailable/empty
```

All other Attempt-1 routing/navigation/breadcrumb/CTA behaviour is retained. Billing
v1.1 and ARCH-011 implementation remain gated until SHOPIFY-001 is architect-accepted
Complete.

## Post-review update — SHOPIFY-001 Attempt 2 Accepted

Architect review confirms the Attempt-2 correction closes the final ARCH-013 functional
gap.

The `/app` home loader now uses the canonical merchant surface policy before reading
pending-recovery business data:

```text
ACTIVE
  -> may call readPendingRecoveries
  -> receives real bounded pending-recovery data

NO_CONTRACT / FROZEN / BILLING_ATTENTION
  -> retain historical dashboard / billing-period / usage / recovery reads
  -> do not call readPendingRecoveries
  -> receive the bounded unavailable pending-recovery payload
```

The onboarding early return remains before all dashboard/history reads. The Attempt-2
implementation did not reopen any previously accepted route, navigation, breadcrumb, CTA
or billing-callback behaviour.

`ARCH-013-SHOPIFY-001` is therefore **Complete** and ARCH-013 is **Implemented**.

The ARCH-013 Ready frontier is empty. The sequencing gate on later billing-v1.1 design
and task definition is removed, but no later task is automatically created or promoted by
this acceptance. Any future implementation definition must use `/app/billing/options` and
`/app/billing/select` according to the canonical route responsibilities established here.
