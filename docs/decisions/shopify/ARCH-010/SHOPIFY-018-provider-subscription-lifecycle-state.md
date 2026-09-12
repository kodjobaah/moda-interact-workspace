---
id: ARCH-010-SHOPIFY-018
architecture_id: ARCH-010
title: Expose Shopify-authoritative subscription lifecycle state including freeze
  and unfreeze
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 59
executor: copilot
claimed_at: '2026-09-12T23:41:20Z'
attempt: 1
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-013
- ARCH-010-SHOPIFY-023
enables:
- ARCH-010-SHOPIFY-012
- ARCH-010-SHOPIFY-014
- ARCH-010-SHOPIFY-015
- ARCH-010-SHOPIFY-016
- ARCH-010-SHOPIFY-021
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-018: Expose Shopify-authoritative subscription lifecycle state including freeze and unfreeze

## Objective

Extend the merchant-app Shopify billing provider/service read model so billing-management UI can distinguish ACTIVE, FROZEN, cancellation and unresolved provider states without treating local BillingPlan rows as commercial truth.

This task is read-only provider/service work. It does not mutate Subscription or activate/unfreeze anything.

## Inspect before editing

```text
app/services/billing/providers/shopify-billing.provider.ts
app/services/billing/billing.types.ts
app/services/billing/billing.service.ts
SHOPIFY-013 accepted/provider commercial read model
billing provider/service tests
```

## Provider snapshot

Add a read method equivalent to BACKGROUND-015's canonical semantics:

```text
activeSubscription(appId, shopId)
+
latest relevant root events SubscriptionStatus event
```

Prefer one Partner GraphQL HTTP request for the billing-management read.

Filter lifecycle events exactly to:

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_UPDATED
SUBSCRIPTION_CANCELLATION_SCHEDULED
SUBSCRIPTION_CANCELED
SUBSCRIPTION_FROZEN
SUBSCRIPTION_UNFROZEN
```

Scope by both Shopify app ID and shop ID. Bound history to at most 365 days.

Do not use Admin Billing API subscription status, legacy billing webhooks or local Subscription status as Shopify commercial truth.

## Merchant provider lifecycle read model

Expose a typed result equivalent to:

```ts
type MerchantShopifyLifecycleState =
  | { state: "ACTIVE"; subscription: MerchantShopifySubscriptionState; latestEvent: ... }
  | { state: "FROZEN"; subscription: MerchantShopifySubscriptionState | null; latestEvent: FrozenEvent }
  | { state: "CANCELED"; subscription: null; latestEvent: CanceledEvent }
  | { state: "UNRESOLVED"; subscription: MerchantShopifySubscriptionState | null; latestEvent: ... | null }
  | { state: "NO_ACTIVE_SUBSCRIPTION"; subscription: null; latestEvent: null };
```

Use actual repository types/naming. Preserve these semantics:

- latest effective FROZEN event => `FROZEN`;
- live active subscription + no effective freeze => `ACTIVE`;
- null live subscription + latest CANCELED => `CANCELED`;
- null live subscription + UNFROZEN/CREATED/UPDATED/CANCELLATION_SCHEDULED for an established merchant => `UNRESOLVED`, not canceled;
- truly new/no-contract merchant with no relevant lifecycle evidence may be `NO_ACTIVE_SUBSCRIPTION`;
- provider failure throws/returns verification failure; never substitute local plan data.

## Frozen commercial presentation data

If activeSubscription is null but the latest FROZEN historical event contains provider plan data, preserve the provider plan handle/billing period from that event for display/mapping purposes. Do not fabricate price data that the historical event did not provide.

A local `BillingPlan` lookup may map the Shopify handle to a Moda plan label/features, but mapping is not proof that the Shopify contract is active.

## Important distinction

Do not interpret App Events `ACCOUNT_FROZEN` as merchant subscription freeze. This task uses only Partner subscription lifecycle state `FROZEN`/`SUBSCRIPTION_FROZEN`.

## Required tests

At minimum prove:

1. active live subscription + no freeze returns ACTIVE;
2. latest FROZEN returns FROZEN even when activeSubscription is temporarily non-null;
3. null live subscription + FROZEN returns FROZEN;
4. null + CANCELED returns CANCELED;
5. null + UNFROZEN returns UNRESOLVED for an established merchant;
6. null + no provider history may return NO_ACTIVE_SUBSCRIPTION for fresh/no-contract context;
7. provider plan handle from frozen event is preserved without invented price;
8. mapped/unmapped local plan status remains separate from provider lifecycle state;
9. Partner failure never falls back to local commercial truth;
10. query is scoped to app+shop and bounded to 365 days;
11. existing SHOPIFY-013 active commercial fields remain unchanged for ACTIVE state;
12. no Prisma subscription mutation occurs.

## Non-goals

No dashboard/banner UI, no top-up action, no plan-change action, no Background reconciliation, no Admin and no lifecycle persistence.

## Stop conditions

STOP if root Historical Events subscription status is unavailable in the configured Partner API version. Report the exact provider gap to `moda_architect`; do not use legacy `APP_SUBSCRIPTIONS_UPDATE` or Admin Billing API as a substitute.

## Completion Report

### Status
In Progress.
