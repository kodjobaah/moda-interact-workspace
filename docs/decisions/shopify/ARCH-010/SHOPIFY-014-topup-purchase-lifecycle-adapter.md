---
id: ARCH-010-SHOPIFY-014
architecture_id: ARCH-010
title: Expose real recovery top-up purchase lifecycle for billing options
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 54
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-013
  - ARCH-010-SHOPIFY-007
  - ARCH-007-SHOPIFY-004
  - ARCH-010-SHOPIFY-018
enables:
  - ARCH-010-SHOPIFY-010
  - ARCH-010-SHOPIFY-012
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHOPIFY-014: Expose real recovery top-up purchase lifecycle for billing options

## Objective

Create a narrow server-side read/action adapter for the real recovery-credit-pack lifecycle used by `/app/billing/options`.

The merchant experiences a top-up as a one-off purchase of lifetime recovery capacity, but Moda is on **Shopify App Pricing**. Therefore this task MUST reuse the existing App Events usage-meter flow and MUST NOT introduce Shopify Billing API one-time charges.

## Hard Shopify billing mechanism

The implementation MUST preserve the accepted ARCH-007 mechanism:

```text
merchant clicks Buy pack
  -> Moda creates RecoveryCreditPurchase(status=PENDING_BILLING)
  -> Moda creates UsageEvent(metric=RECOVERY_CREDIT_PACK_PURCHASE, quantity=1, PENDING)
  -> Background publishes App Event to current Shopify pack meter
  -> Shopify Partner activeSubscription usage quantity is later reconciled
  -> only provider-confirmed purchase becomes ACTIVE
  -> PURCHASED_RECOVERY_CREDITS.grantedQuantity increases exactly once
```

Do NOT call or add:

```text
appPurchaseOneTimeCreate
appSubscriptionCreate
billing.request
appUsageRecordCreate
```

Do not grant credits in the merchant request transaction.

## Inspect before editing

Read these exact current files and accepted task reports before changing code:

```text
app/services/billing/billing.service.ts
app/services/billing/billing.types.ts
app/routes/app/billing/route.tsx
app/routes/app/billing/options/route.tsx
app/components/dashboard/TopUpPurchasePanel.jsx
app/components/dashboard/BillingPurchaseHub.jsx
tests/unit/services/billing.service.test.ts
tests/unit/billing-ui.test.ts
```

Also read the accepted ARCH-007 pack tasks:

```text
docs/decisions/shopify/ARCH-007/SHOPIFY-004-request-repeatable-recovery-credit-pack.md
docs/decisions/background/ARCH-007/BACKGROUND-009-activate-consume-recovery-credit-packs.md
```

Read implemented SHOPIFY-013 before finalising provider field names.

## Required server read model

Add a service method or small adapter owned by the billing service that returns a merchant-safe top-up state equivalent to:

```ts
{
  configured: boolean;
  purchaseEligible: boolean;
  unavailableReason:
    | "NO_ACTIVE_SUBSCRIPTION"
    | "UNMAPPED_PLAN"
    | "PACK_DISABLED"
    | "PACK_METER_UNVERIFIED"
    | "BILLING_CYCLE_UNVERIFIED"
    | "DRAINING"
    | "RECONCILING"
    | "SHOPIFY_VERIFICATION_UNAVAILABLE"
    | null;

  creditsPerPack: number | null;
  purchasedCreditsAvailable: number;

  shopifyPackMeter: {
    handle: string;
    description: string | null;
    currency: string | null;
    price: /* accepted SHOPIFY-013 provider price shape */;
    currentQuantity: number | null;
    currentCostAmount: string | null;
    currentCostCurrency: string | null;
  } | null;

  latestPurchase: {
    id: string;
    status:
      | "PENDING_BILLING"
      | "ACTIVE"
      | "NEEDS_ATTENTION"
      | "CANCELLED"
      | "REFUNDED";
    creditsGranted: number;
    createdAt: string;
    activatedAt: string | null;
    usageReportState: string;
  } | null;
}
```

Use actual integrated enum/type names. Do not introduce a parallel billing-status vocabulary if Prisma already provides the status.

## Authority rules

### Shopify authority

For the top-up meter, Shopify `activeSubscription` is authoritative for:

- whether the current Shopify contract exists;
- whether the configured pack meter handle is an active current subscription item;
- current billing cycle;
- provider usage quantity/cost;
- provider pricing representation for the meter.

### Moda authority

PostgreSQL is authoritative for:

- `recoveryCreditsPerPack` (what one provider meter unit grants inside Moda);
- purchased-credit granted/committed/reserved/refunding balances;
- durable RecoveryCreditPurchase status;
- durable UsageEvent report state;
- whether the current local billing phase is ACTIVE/DRAINING/RECONCILING.

Do not treat local `BillingPlan` monetary values as Shopify price authority.

## Free-plan top-up eligibility — binding ARCH-010 rule

A mapped active Free merchant is eligible to buy the same Moda recovery top-up when **all** of these are true at mutation time:

```text
Shop.status = ACTIVE
Subscription.status = ACTIVE/TRIALING as otherwise supported
provider current plan handle == mapped Free BillingPlan.shopifyPlanHandle
BillingPlan.recoveryCreditPackEnabled = true
BillingPlan.recoveryCreditsPerPack > 0
configured shopifyRecoveryCreditPackEventHandle is present in provider active usage items
provider currentBillingCycle has exact start/end
Subscription.billingPeriodId points to the exact OPEN Free BillingPeriod for that same provider cycle
local phase = ACTIVE (not DRAINING / RECONCILING)
```

For Free, do **not** require `shopifyUsageEventHandle`; that is the normal Paid recovery meter and is irrelevant to Free lifetime recovery admission.

The Free BillingPeriod is commercial/App-Event cycle state only. Buying/rolling a Free top-up MUST NOT:

- reset or grant the five `FREE_RECOVERY_LIFETIME` conversations;
- create `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)`;
- convert Free entitlement into a monthly allowance.

If the exact Free provider/local billing cycle or pack meter cannot be verified, return top-up unavailable and create no purchase/UsageEvent. Do not fall back to `Subscription.planId` alone.

## Pack price presentation rule

This task exposes Shopify's provider price representation to UI; it MUST NOT invent or persist a local monetary top-up price.

Do not implement a browser-side pricing algorithm.

If the provider price representation cannot be reduced safely to one exact merchant-facing amount with the existing accepted Shopify contract, return the raw/provider-safe presentation fields and leave `displayPrice` null. The UI must then say Shopify bills the pack according to the current App Pricing meter rather than fabricate a number.

## Purchase action adapter

Expose/reuse one action method that calls the existing:

```text
billingService.requestRecoveryCreditPack(shopId, "BUY_RECOVERY_CREDIT_PACK", purchaseId)
```

The adapter MUST:

1. authenticate/resolve the current shop through the existing route policy;
2. accept only the server-defined intent and opaque `purchaseId`;
3. ignore client-supplied plan, meter, pack size, price, currency and credit quantity;
4. rely on `requestRecoveryCreditPack` to re-query Shopify and verify the exact current contract/meter/cycle at mutation time;
5. return a typed merchant-safe result containing purchase ID/status only;
6. never report credits as available when the returned purchase is still `PENDING_BILLING`.

## UI lifecycle semantics to support

The read model must support these exact states:

```text
READY
  -> Buy CTA may be shown

PENDING_BILLING
  -> Shopify confirmation is still pending
  -> credits not yet available
  -> do not show success

ACTIVE
  -> credits are in purchased balance
  -> normal capacity projection shows them

NEEDS_ATTENTION
  -> no credits granted
  -> merchant sees support/retry guidance

CANCELLED / REFUNDED
  -> historical state only
  -> do not count as available capacity
```

A Shopify App Events HTTP `202` is NOT `ACTIVE`. It means only that Shopify received the event; billing validation is asynchronous.

## Revalidation behaviour

Do not add a new browser websocket/SSE mechanism.

After a purchase request:

- route action returns the durable pending purchase;
- React Router revalidation may refresh loader state;
- while latest purchase is `PENDING_BILLING`, the UI may expose a normal refresh/reload affordance;
- do not use a tight client polling loop in this task.

Background/provider reconciliation remains responsible for activation.

## Existing purchase concurrency/idempotency

Preserve existing permanent request idempotency by `purchaseId`.

Do not add a one-pack-lifetime restriction.

Do not redesign database concurrency in this task. If the current integrated implementation allows multiple different purchase IDs concurrently, UI may disable a second CTA while its latest request is unresolved, but this task must not invent a cross-purchase uniqueness constraint.

## Required tests

At minimum prove:

1. provider current pack meter is found only by exact configured handle;
2. local BillingPlan monetary data is never used as Shopify top-up price truth;
3. local `creditsPerPack` is returned separately from provider price/cost;
4. purchased available balance comes from durable counters;
5. `PENDING_BILLING` returns zero newly activated credits;
6. `ACTIVE` purchase is reflected through the durable purchased balance;
7. `NEEDS_ATTENTION` grants zero and produces a merchant-safe attention state;
8. `activeSubscription=null` is not treated as purchase-eligible;
9. unmapped current Shopify plan is not purchase-eligible;
10. pack meter missing from current provider items is not purchase-eligible;
11. provider verification failure does not fall back to local commercial truth;
12. DRAINING/RECONCILING blocks the purchase action;
13. action ignores client-supplied price/plan/meter/credits;
14. action delegates to existing requestRecoveryCreditPack exactly once;
15. replaying the same purchaseId returns the same purchase rather than creating a second UsageEvent;
16. action result `PENDING_BILLING` never renders as activated credits;
17. no direct App Events network request occurs in the merchant HTTP transaction;
18. no Billing API one-time-charge mutation exists in task diff;
19. mapped active Free with exact provider/local cycle and exact pack meter is purchase-eligible;
20. Free does not require the normal Paid recovery meter to buy a pack;
21. Free missing exact cycle is not purchase-eligible;
22. Free missing exact pack meter is not purchase-eligible;
23. Free top-up request references the exact current Free BillingPeriod and never creates/resets a Free included allowance;
24. i18n parity is preserved for any new merchant-visible state labels.

## Non-goals

Do not implement Background App Event publication, provider-confirmation reconciliation, refunds, plan changes, cancellation, promotional credits or Admin UI.

## Validation

Run focused service/route tests, declared repository tests, typecheck, build and `git diff --check` using scripts that actually exist in `package.json`.

## Stop conditions

STOP if the integrated code no longer uses Shopify App Pricing/App Events for pack billing.

STOP if satisfying this task would require introducing `appPurchaseOneTimeCreate` or another legacy Manual Pricing charge.

STOP if SHOPIFY-013 does not expose the current configured pack meter item safely; return the provider-contract gap to `moda_architect`.

## Completion Report

### Status
Not started.


## Final frozen purchase guard

Before creating a top-up purchase/UsageEvent, require SHOPIFY-018 lifecycle state to be executable and durable local Subscription not FROZEN. Provider FROZEN or local FROZEN/restoration-pending MUST return a typed non-purchasable result and create no RecoveryCreditPurchase/UsageEvent. Pending purchases created before freeze remain governed by Background reconciliation and must not be re-created.
