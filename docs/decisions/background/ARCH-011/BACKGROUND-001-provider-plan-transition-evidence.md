---
id: ARCH-011-BACKGROUND-001
architecture_id: ARCH-011
title: Expose exact Shopify plan-transition evidence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 14
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-BACKGROUND-015
enables:
- ARCH-011-BACKGROUND-002
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-011-BACKGROUND-001

## Authorized implementation surface
```text
src/providers/shopify-partner-billing.provider.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
```
Do not edit reconciliation/database services in this task.

## Exact provider changes
In `PartnerSubscriptionLifecycleEvent` add exact fields:

```text
providerAppId: string
providerShopId: string
```

In `PartnerSubscriptionReconciliationSnapshot` add:

```text
providerAppId: string
providerShopId: string
recentPlanLifecycleEvents: PartnerSubscriptionLifecycleEvent[]
```

Keep `activeSubscription` and `latestLifecycleEvent` unchanged for ARCH-010 compatibility.

Change `SUBSCRIPTION_RECONCILIATION_SNAPSHOT_QUERY` from `events(first: 1)` to `events(first: 25)`. Keep the existing event types so `latestLifecycleEvent` semantics are preserved. Parse **all** returned edges with the existing identity validation in `parseLifecycleEvent`; any malformed edge makes the entire snapshot fail closed with `ShopifyPartnerBillingError(code="malformed-response", retryable=true)`.

Return:

```text
latestLifecycleEvent = parsedEvents[0] ?? null
recentPlanLifecycleEvents = parsedEvents.filter(type CREATED or UPDATED)
providerAppId = configured appId
providerShopId = requested shopifyShopId
```

Do not require `legacySubscriptionId`; leave existing `providerSubscriptionId` field unchanged only for ARCH-010 compatibility.

Add exported pure helper in the same file:

```text
selectSameCyclePlanLifecycleEvent({events, providerAppId, providerShopId, targetPlanHandle, cycleStart, cycleEnd})
```

Rules: candidates must match app, shop, CREATED/UPDATED, exact target handle, and `cycleStart < occurredAt < cycleEnd`; deduplicate exact event ID; sort by occurredAt descending then ID ascending; return newest candidate or null. Never use requested target or worker time.

## Tests
Append tests proving first=25 query, all-edge validation, identity mismatch rejection, null legacy ID success, exact handle matching, strict cycle boundaries, newest deterministic candidate, no-match null, and latestLifecycleEvent compatibility.

## Validation
```text
npm run prisma:validate
npm run prisma:generate
npx vitest run tests/unit/providers/shopify-partner-billing.provider.test.ts
npm test
npm run build
git diff --check
```

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
