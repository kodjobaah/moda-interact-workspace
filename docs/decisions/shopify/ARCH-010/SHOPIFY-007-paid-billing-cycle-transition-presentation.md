---
id: ARCH-010-SHOPIFY-007
architecture_id: ARCH-010
title: Present App Pricing billing-cycle transition and guard late-cycle top-up purchase
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-007
  - ARCH-010-DATABASE-004
  - ARCH-010-SHARED-002
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-004
enables:
  - ARCH-010-SHOPIFY-012
  - ARCH-010-SHOPIFY-014
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-007: Present App Pricing billing-cycle transition and guard late-cycle top-up purchase

## Objective

Make merchant billing UI and server-side top-up creation respect the exact Shopify App Pricing billing-cycle phase for **both Free and Paid** subscriptions.

The cycle phase controls actions that create App Events. It does not redefine recovery entitlement:

```text
Paid included recovery -> period-scoped, creates normal recovery App Event
Free lifetime recovery -> lifetime, creates no normal recovery App Event
Top-up purchase (Free or Paid) -> creates recovery-credit-pack App Event
```

Merchants never access `moda-interact-admin`.

## Inspect before editing

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
app/routes/app/usage/route.jsx
app/routes/app/home/route.jsx
app/routes/app/pending-recoveries/route.*
app/components/dashboard/**
app/i18n/locales/*.json
tests/unit/services/billing.service.test.ts
tests/unit/routes/**billing**
package.json
```

Read integrated SHOPIFY-003/004, BACKGROUND-007 and published Shared billing exports first.

## Shared constant

Import:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

from `@modainteract/moda-interact-shared/billing`.

Do not copy a literal five-minute duration into app business logic.

## Derived cycle phase

For a mapped Free or Paid subscription with an exact current local BillingPeriod:

```text
ACTIVE
  now < periodEnd - drainWindow

DRAINING
  periodEnd - drainWindow <= now < periodEnd

RECONCILING
  now >= periodEnd and Subscription still points at that expired period
```

This is derived state only. Do not add another persisted Subscription status.

## Presentation rules

### Paid

ACTIVE uses SHOPIFY-004 normal current-period presentation.

DRAINING displays a localized message that new App-Event-backed Paid activity is briefly paused while Shopify's cycle changes.

RECONCILING displays a bounded verification state and must not present expired included allowance as spendable current capacity.

### Free

Always display Free recovery entitlement from the lifetime Free counter, never from BillingPeriod.

A Free BillingPeriod is shown only as Shopify billing/top-up cycle context where useful. It must never be labelled as a monthly Free recovery allowance.

During DRAINING/RECONCILING, explain only that **new top-up purchase** is temporarily unavailable while Shopify's billing cycle is being confirmed. Do not tell the merchant that their remaining lifetime Free recoveries have expired or paused.

## Merchant routes

Keep merchant-owned routes available during DRAINING/RECONCILING:

```text
/app
/app/usage
/app/billing
/app/billing/options
/app/billing/select
/app/merchant-support
```

Read-only pending/recovery/history surfaces remain available according to existing access policy.

No merchant route/link exposes Admin.

## Top-up purchase server guard

`BillingService.requestRecoveryCreditPack(...)` must apply the same new-purchase guard to Free and Paid:

```text
exact current local BillingPeriod exists
provider current plan == mapped current plan
provider current cycle == local exact cycle
configured recovery-credit-pack meter exists in provider active usage items
now < currentPeriodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

If DRAINING/RECONCILING or exact cycle/meter verification fails:

- create no `RecoveryCreditPurchase`;
- create no pack `UsageEvent`;
- perform no App Events request;
- return the canonical merchant-safe unavailable reason;
- preserve replay/idempotency of an already-existing purchase ID.

### Free-specific guard

For Free:

- do not require `BillingPlan.shopifyUsageEventHandle` (Paid normal recovery meter);
- require the configured `shopifyRecoveryCreditPackEventHandle` only;
- require `Subscription.billingPeriodId` to point to the exact OPEN Free provider BillingPeriod;
- do not create/reset any Free included entitlement while validating or creating a pack request.

## Behaviour matrix

| State | Paid new included recovery | Free lifetime recovery | Purchased-credit recovery | New top-up purchase |
|---|---|---|---|---|
| ACTIVE | allowed if capacity | allowed if lifetime capacity | allowed if purchased capacity | allowed if exact meter/cycle |
| DRAINING | blocked | allowed | allowed | blocked |
| RECONCILING | blocked | allowed if verified Free subscription/lifetime state remains current under ARCH-010 policy | allowed if no new billing event is required | blocked |

The Background entitlement layer remains final recovery-admission authority; this task must not add UI-only bypasses.

## No app-side rollover

The app never closes/opens BillingPeriods or grants credits. BACKGROUND-007 owns same-plan cycle rollover.

Do not add browser polling against Partner API. Billing-management loader may perform explicit Shopify verification through SHOPIFY-013/014 where required, but ordinary dashboard rendering must not become a Partner polling loop.

## Required tests

1. Paid ACTIVE derives ACTIVE;
2. Free ACTIVE derives ACTIVE from exact provider/local period;
3. exact drain start derives DRAINING;
4. exact period end derives RECONCILING;
5. Paid DRAINING/RECONCILING hides/disables included-cycle actions truthfully;
6. Free DRAINING/RECONCILING keeps lifetime-Free capacity presentation unchanged;
7. new pack purchase in ACTIVE may proceed only after exact provider/local cycle + exact pack meter verification;
8. new pack purchase in DRAINING creates no purchase/event;
9. new pack purchase in RECONCILING creates no purchase/event;
10. existing purchase replay remains idempotent;
11. Free does not require Paid normal recovery meter for pack purchase;
12. Free missing exact BillingPeriod is pack-ineligible;
13. Free missing pack meter is pack-ineligible;
14. Free DRAINING still allows remaining lifetime-Free recovery admission in the shared policy/Background path;
15. Free RECONCILING does not claim lifetime entitlement reset;
16. successor Free BillingPeriod restores pack purchase eligibility without changing lifetime Free quantities;
17. plan selection/support/navigation remain available;
18. no merchant link exposes Admin;
19. i18n parity for added states/messages.

## Non-goals

Do not implement:

- period close/open transaction;
- BullMQ worker;
- different-plan transition;
- cancellation;
- refund workflow;
- promotional credits;
- Admin UI.

## Validation

Inspect `package.json`; run focused billing service/route/component tests, declared typecheck/build tests and `git diff --check`. Do not invent scripts.

## Stop conditions

STOP if:

- exact local/provider billing-cycle comparison is unavailable;
- new purchase creation cannot be distinguished from replay;
- implementation would require turning Free lifetime entitlement into a monthly period counter;
- task would require recurring Partner polling from ordinary merchant dashboard loaders.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
