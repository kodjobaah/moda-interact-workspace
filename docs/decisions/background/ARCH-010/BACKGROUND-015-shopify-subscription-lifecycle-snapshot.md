---
id: ARCH-010-BACKGROUND-015
architecture_id: ARCH-010
title: Read Shopify live subscription plus latest lifecycle event for reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 57
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-010-BACKGROUND-012
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-015: Read Shopify live subscription plus latest lifecycle event for reconciliation

## Objective

Extend the existing Shopify Partner provider so reconciliation can distinguish a frozen subscription from cancellation instead of treating `activeSubscription=null` as sufficient cancellation evidence.

This task owns provider I/O and typed provider results only. It does not mutate Prisma state.

## Inspect before editing

```text
src/providers/shopify-partner-billing.provider.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
src/services/billing-reconciliation.service.ts   # inspect consumers only
SHOPIFY Partner API environment configuration already used by the provider
```

Read the ARCH-010 cancellation/freeze architecture before editing.

## Provider query

Add one reconciliation-snapshot method, using the repository's naming conventions, equivalent to:

```ts
getSubscriptionReconciliationSnapshot(shopifyShopId: string): Promise<{
  activeSubscription: PartnerSubscription | null;
  latestLifecycleEvent: PartnerSubscriptionLifecycleEvent | null;
}>;
```

Do not delete or change the externally observable contract of
getActiveSubscription().

Before changing this service, search the repository for every existing call site
of getActiveSubscription().

Existing code that currently calls getActiveSubscription() MUST continue to:

- compile;
- receive the same return shape;
- preserve the same null/error semantics;
- preserve the same Shopify-provider interpretation.

BG15 may refactor getActiveSubscription() internally so that it delegates to the
new shared Partner GraphQL parsing/snapshot implementation, but existing call
sites MUST NOT be forced to migrate as part of this task unless this task
explicitly names those call sites.

Do not add merchant/customer backwards-compatibility behaviour. This requirement
is only about repository API compatibility for existing source-code callers.

```text
activeSubscription(appId, shopId)
events(filter: { subjectId: appId, shopId, eventTypes: [...] }, first: 1, orderBy: OCCURRED_AT_DESC)
```

Filter lifecycle history to exactly:

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_UPDATED
SUBSCRIPTION_CANCELLATION_SCHEDULED
SUBSCRIPTION_CANCELED
SUBSCRIPTION_FROZEN
SUBSCRIPTION_UNFROZEN
```

Use `occurredAtMin = now - 365 days` and `occurredAtMax = now`, which is Shopify's maximum documented Historical Events range. Do not issue an unbounded history query.

## Lifecycle result

Return a typed event equivalent to:

```ts
type PartnerSubscriptionLifecycleEvent = {
  id: string;
  eventType:
    | "SUBSCRIPTION_CREATED"
    | "SUBSCRIPTION_UPDATED"
    | "SUBSCRIPTION_CANCELLATION_SCHEDULED"
    | "SUBSCRIPTION_CANCELED"
    | "SUBSCRIPTION_FROZEN"
    | "SUBSCRIPTION_UNFROZEN";
  state:
    | "CREATED"
    | "UPDATED"
    | "CANCELLATION_SCHEDULED"
    | "CANCELED"
    | "FROZEN"
    | "UNFROZEN";
  occurredAt: Date;
  cancelEffectiveOn: string | null;
  planHandle: string | null;
  billingPeriod: string | null;
};
```

Use exact generated/provider naming where necessary. Preserve semantics.

Do not infer a lifecycle state from `activeSubscription` fields. Historical `SubscriptionStatus.state` is provider evidence.

## Parsing rules

1. Partner non-2xx -> throw existing provider request error.
2. Any GraphQL error that makes either requested root result unreliable -> throw; do not return partial success.
3. `activeSubscription=null` is a valid live result.
4. zero lifecycle events in the 365-day range -> `latestLifecycleEvent=null`.
5. require the returned event to be a `SubscriptionStatus` event for the requested shop/app; malformed shapes are provider errors.
6. parse `occurredAt` as a valid Date; invalid timestamps fail the provider call.
7. preserve existing active-subscription parsing/invariants exactly, including one active flat-rate item and usage snapshots.

## Important terminology

Do NOT interpret the App Events billing error `ACCOUNT_FROZEN` as merchant subscription freeze. Shopify documents `ACCOUNT_FROZEN` as a partner-account billing-event error. This task deals only with `SUBSCRIPTION_FROZEN` / `SubscriptionStatusState.FROZEN` for the merchant subscription.

## Required tests

At minimum prove:

1. active subscription + latest CREATED parses both results;
2. active subscription + latest FROZEN exposes `FROZEN` lifecycle evidence;
3. `activeSubscription=null` + latest FROZEN remains distinguishable from cancellation;
4. `activeSubscription=null` + latest CANCELED exposes CANCELED;
5. latest UNFROZEN parses correctly;
6. latest CANCELLATION_SCHEDULED parses `cancelEffectiveOn`;
7. zero events returns null lifecycle evidence;
8. provider HTTP failure throws;
9. GraphQL errors do not become provider null;
10. malformed lifecycle timestamp/state fails closed;
11. the query scopes history by both app/subject and shop;
12. the query uses the six explicit event types and bounded 365-day window;
13. existing `getActiveSubscription()` behaviour/tests remain valid;
14. no Prisma write occurs in this provider.

## Non-goals

No Subscription update, no FROZEN transition, no BullMQ scheduling, no execution gate, no UI and no historical-event persistence.

## Validation

Run focused provider tests, repository-declared typecheck/build/unit suite and `git diff --check`.

## Stop conditions

STOP if the configured Partner API version does not expose root `events`, `EventFilterInput`, `SubscriptionStatus.state` and the required lifecycle event types. Return the exact schema mismatch to `moda_architect`; do not fall back to legacy Admin Billing API/webhooks.

## Completion Report

### Status
Not started.
