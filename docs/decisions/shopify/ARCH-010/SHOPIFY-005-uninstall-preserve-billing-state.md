---
id: ARCH-010-SHOPIFY-005
architecture_id: ARCH-010
title: Make uninstall an execution gate without resetting billing state
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 47
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-004
  - ARCH-010-BACKGROUND-005
enables: []
created: 2026-09-11
updated: 2026-09-11
superseded_by: ARCH-010-SHOPIFY-006
---

# ARCH-010-SHOPIFY-005: Make uninstall an execution gate without resetting billing state

> **Superseded by ARCH-010-SHOPIFY-006. Do not implement this task.**
> Iteration 5 established that uninstall preservation and safe reinstall entry must ship as one app-owned change; otherwise the existing `markInstalled()` path can expose stale preserved entitlement between deployments. The original reviewed definition is retained below as architecture history.

## Architecture hold before execution

This task is intentionally `pending` even after its Background dependencies complete until `moda_architect` has agreed the next ARCH-010 reinstall transition.

Reason: the supplied code's current `markInstalled()` turns an `UNINSTALLED` Shop directly back to `ACTIVE`. Once uninstall stops overwriting Subscription status with `NO_CONTRACT`, executing this task without the reinstall correction could expose stale pre-uninstall entitlement on reinstall.

Do not claim/implement this task until the architect removes that hold or amends dependencies after the reinstall iteration.

## Objective

Change the Shopify `app/uninstalled` persistence semantics so uninstall records installation availability only:

```text
Shop.status = UNINSTALLED
Shop.uninstalledAt = uninstall event time
```

and removes the Shopify session, while preserving subscription, billing-period and credit state exactly as it stood immediately before uninstall.

## Inspect before editing

```text
app/routes/webhooks/app/uninstalled/route.jsx
app/services/shop/shop.service.ts
app/services/shop/shop-access-policy.ts
app/routes/auth/catchall/route.jsx
app/services/billing/billing.service.ts
tests/unit/services/shop.service.test.ts
tests/unit/shop-access-policy.test.ts
tests/unit/routes/explicit-route-config.test.ts
package.json
```

Also inspect the integrated ARCH-010 reinstall task before implementation; that implementation is authoritative for how a preserved uninstall state later becomes executable again.

## Current supplied-code behaviour to remove

`ShopService.markUninstalled()` currently performs:

```text
Shop.status = UNINSTALLED
Shop.uninstalledAt = eventTime
Subscription.status = NO_CONTRACT
```

The final line is no longer allowed under ARCH-010.

## Required uninstall transaction

For an existing resolved Shop:

1. mark Shop status `UNINSTALLED`;
2. record `uninstalledAt` using the webhook's validated event time according to existing idempotent semantics;
3. do **not** update Subscription;
4. do **not** mutate BillingPeriod;
5. do **not** mutate period/free/purchased/promotional entitlement counters;
6. do **not** mutate RecoveryCreditPurchase/Refund state;
7. do **not** reset `ShopSettings.onboardingCompleted`;
8. preserve all merchant/history records.

The webhook route continues deleting matching Shopify Session rows after the durable Shop transition, exactly as its existing duplicate-safe flow permits.

If the shop cannot be resolved using the existing identity mechanism, preserve the current no-op/not-found behaviour. Do not invent a new identity heuristic.

## Explicit preserved state

Uninstall must preserve all of the following when present:

```text
Subscription.planId
Subscription.status
Subscription.observedShopifyPlanHandle
Subscription current cycle/current BillingPeriod pointer
Subscription pending plan fields
Subscription provider identifiers
BillingPeriod rows/status/history
BillingPeriod included-credit counters
FREE_RECOVERY_LIFETIME state
purchased top-up balance/lots
promotional lifetime top-up balance
refund workflow state
ShopSettings.onboardingCompleted
```

Later Shopify reconciliation may legitimately change subscription projection after reinstall. Uninstall itself may not.

## No BullMQ publication from uninstall

Do not add queue-wide purge or per-shop cancellation publication from this webhook.

ARCH-010 relies on durable `Shop.status` execution gates in Background. Existing queued jobs independently no-op when they execute after uninstall.

This keeps the uninstall request bounded and avoids coupling Shopify webhook acknowledgement to Redis availability.

## Access behaviour

The current app session deletion remains. A merchant who has uninstalled has no merchant app session/surface.

Do not expose `moda-interact-admin` to the merchant.

## Shop identity non-goal

ARCH-010 explicitly accepts the current non-deterministic/limited shop-identification model for this lifecycle iteration.

Do not modify:

- Shopify identity resolution strategy;
- Meta/WhatsApp tenant identity;
- customer-phone tenant correlation;
- shared event contracts;

merely to implement uninstall.

## Required tests

Update/add tests proving at least:

1. uninstall marks an ACTIVE shop UNINSTALLED;
2. uninstall records `uninstalledAt`;
3. duplicate uninstall remains idempotent under the existing event-time semantics;
4. uninstall of unknown shop remains safe/no-op;
5. Subscription status is **not** changed;
6. Subscription current plan/provider/cycle fields are not changed;
7. pending plan fields are not changed;
8. BillingPeriod rows/pointer are not changed;
9. Free lifetime entitlement is not reset;
10. purchased top-up state is not reset;
11. promotional top-up state is not reset when that schema is present;
12. `ShopSettings.onboardingCompleted` is not reset;
13. Shopify sessions are still removed by the webhook route when a session is supplied;
14. route remains safe when Shopify supplies no session on a duplicate uninstall webhook.

Use narrow mocks/spies or fixture state to prove absence of Subscription updates; do not merely assert final Shop status.

## Non-goals

Do not:

- implement reinstall behaviour in this task;
- query Partner `activeSubscription` during uninstall;
- cancel/refund a subscription;
- refund top-ups;
- delete merchant data;
- purge BullMQ queues;
- solve shop identification;
- modify Background code.

## Validation

Run the affected shop/uninstall route unit tests, then the repository's declared validation scripts applicable to the changed code and:

```text
git diff --check
```

## Stop conditions

Stop and return to `moda_architect` if:

- the integrated reinstall implementation has not been defined/accepted when this task is claimed;
- preserving Subscription state makes any merchant business path executable while Shop remains UNINSTALLED;
- implementation would require a new shop-identity strategy;
- another ARCH-010 task has changed Shop lifecycle semantics since this task definition.
