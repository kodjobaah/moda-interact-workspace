---
id: ARCH-011-BACKGROUND-001
architecture_id: ARCH-011
title: Expose exact provider plan-transition effective-time evidence
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
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-BACKGROUND-001: Expose exact provider plan-transition effective-time evidence

## Objective

Extend the accepted Shopify Partner subscription snapshot so Background can prove **when a plan became current** inside one provider app billing cycle.

This task is read-only provider/service work. It must not mutate Subscription, BillingPeriod, transition, segment or entitlement state.

## Inspect before editing

```text
src/providers/shopify-partner-billing.provider.ts
src/integration/shopify/types.ts
src/services/billing-subscription-reconciliation.service.ts
existing provider unit tests
ARCH-010-BACKGROUND-015 accepted implementation
```

Preserve all accepted cancellation/freeze/unfreeze lifecycle semantics.

## Required provider evidence

The accepted ARCH-010 snapshot exposes live `activeSubscription`, current billing cycle and the latest lifecycle event. ARCH-011 additionally needs bounded recent CREATED/UPDATED plan evidence so a newer freeze/cancellation event cannot hide the plan-change event required for proration.

Extend the internal snapshot with a bounded collection equivalent to:

```text
recentPlanLifecycleEvents[]
```

Only include validated app+shop subscription events representing plan creation/change, at minimum the provider equivalents of:

```text
SUBSCRIPTION_CREATED / CREATED
SUBSCRIPTION_UPDATED / UPDATED
```

Do not remove or weaken the existing `latestLifecycleEvent` used by ARCH-010.

## Query constraints

Prefer one Partner GraphQL request containing:

```text
activeSubscription
latest lifecycle event data
bounded recent plan lifecycle events
```

when the configured Partner API supports it.

Bound plan-event history deterministically:

```text
maximum events <= 25
lookback <= existing 365-day lifecycle safety window
```

Do not fetch unbounded history.

Each accepted plan event must preserve validated:

```text
id
occurredAt
eventType/state
plan.handle
plan.billingPeriod where provider supplies it
app identity
shop identity
```

Reject identity-mismatched/malformed events using existing provider validation conventions.

## Exact same-cycle matching contract

Provide/test an internal helper or clearly documented consumer contract that selects the newest exact event satisfying all:

```text
event.plan.handle == activeSubscription.planHandle
providerCycleStart < event.occurredAt < providerCycleEnd
event is valid CREATED or UPDATED plan event
app ID matches
shop ID matches
```

The selected event ID is durable idempotency evidence.

The selected `occurredAt` is the only ARCH-011 same-cycle `providerEffectiveAt`.

Do NOT use:

```text
Date.now()
worker startedAt
queue timestamp
local Subscription.updatedAt
merchant click timestamp
```

as a replacement.

## New-cycle distinction

If the provider current cycle does not equal the local open BillingPeriod, this task only exposes provider evidence. It does not decide whether the downstream path is ARCH-010 boundary activation/rollover or ARCH-011 same-cycle proration.

## Required tests

Prove at minimum:

1. activeSubscription current cycle remains exact and unchanged;
2. multiple plan events are retained newest-first and bounded;
3. a newer freeze/cancel event does not erase an older same-cycle matching plan event;
4. wrong app event rejected;
5. wrong shop event rejected;
6. malformed plan event rejected;
7. current-plan exact event strictly inside cycle selected;
8. handle match outside cycle rejected for same-cycle effective time;
9. no exact event yields explicit no-proof result, not observation time;
10. duplicate event IDs are normalized/rejected deterministically;
11. one Partner HTTP request is retained if supported without weakening validation;
12. existing ARCH-010-BACKGROUND-015 provider tests remain green.

## Validation

Run repository-declared equivalents of:

```text
npm run prisma:validate
npm run prisma:generate
<focused provider tests>
npm test
npm run build
git diff --check
```

Document unrelated baseline failures exactly; do not hide them.

## Non-goals

No DB writes, Shared changes, merchant UI, topology classification, proration or entitlement mutation.

## Stop conditions

STOP and return exact provider/API evidence to `moda_architect` if the configured Partner API cannot provide reliable event identity + `occurredAt` + plan handle required for exact same-cycle effective time.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
