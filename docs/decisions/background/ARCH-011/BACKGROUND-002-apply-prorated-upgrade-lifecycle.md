---
id: ARCH-011-BACKGROUND-002
architecture_id: ARCH-011
title: Apply provider-confirmed prorated upgrade lifecycle, repeated upgrades and rollover
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
- ARCH-011-SHARED-002
- ARCH-011-BACKGROUND-001
- ARCH-010-BACKGROUND-010
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-BACKGROUND-002: Apply provider-confirmed prorated upgrade lifecycle, repeated upgrades and rollover

## Objective

Implement the **complete Background-owned ARCH-011 transition state machine in one task**. This task absorbs what would otherwise be separate same-cycle application, repeated-upgrade, rollover and deferred-downgrade tasks.

Extend the accepted ARCH-010 provider-confirmed plan-change/reconciliation path; do not create a competing Background billing engine.

## Inspect before editing

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-reconciliation.service.ts
src/providers/shopify-partner-billing.provider.ts
src/integration/shopify/types.ts
src/workers/billing-subscription-reconciliation.worker.ts
src/services/recovery-billing.service.ts
tests/unit/services/billing-subscription-reconciliation.service.test.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts

ARCH-010-BACKGROUND-010 accepted implementation when dependency becomes Complete
ARCH-011 DATABASE models
published ARCH-011 Shared primitives
```

Preserve ARCH-010 cancellation/freeze/uninstall/reinstall, purchased-credit, promotion, lifetime-Free and capacity-routing behaviour.

## A. Never apply merchant intent directly

`SubscriptionPlanTransition.REQUESTED` is merchant intent only. Do not change effective `Subscription.planId`, segments or included entitlement because a request exists.

Provider confirmation requires a fresh authoritative Shopify snapshot.

## B. Provider-confirmed transition matching

For an unresolved transition, prove all applicable identity conditions:

```text
local subscription/shop identity matches provider
providerSubscriptionId matches/establishes the same subscription projection
provider current plan handle maps to an active BillingPlan
provider current plan is the requested target before marking PROVIDER_CONFIRMED
provider currentBillingCycle start/end are valid
```

For a same-cycle transition, additionally require the exact matching lifecycle event supplied by BACKGROUND-001:

```text
event.plan.handle == provider current plan handle
providerCycleStart < event.occurredAt < providerCycleEnd
app/shop identity valid
event ID has not already been applied
```

Then persist:

```text
providerEffectiveAt = exact matching event.occurredAt
providerLifecycleEventId = exact event ID
```

Never use worker time, queue time, merchant click time or local `updatedAt`.

If provider changed plan but exact same-cycle event evidence cannot be proven, transition => `NEEDS_ATTENTION`; grant nothing and preserve old local effective plan until reconciled according to accepted provider-authority rules.

## C. Classify same-cycle versus new-cycle

Use exact instants, not date-only comparisons.

```text
provider currentBillingCycle == still-open local BillingPeriod periodStart/periodEnd
AND providerEffectiveAt strictly inside it
  => SAME_CYCLE_PRORATED

provider currentBillingCycle differs / provider opened a new cycle
  => NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
```

This includes Free -> paid. Moda never assumes whether Shopify resets/preserves a Free provider cycle.

## D. Same-cycle segment application

Inside one interactive Prisma transaction at `Serializable` isolation:

1. re-read Subscription, unresolved transition, BillingPeriod, current segment(s), target BillingPlan and `INCLUDED_RECOVERY_CREDITS` counter;
2. revalidate exact transition/provider identities and expected version/state;
3. if no segment history exists because this is the first ARCH-011 transition in an existing ARCH-010 period, materialize the period-opening segment from `BillingPeriod.plan*Snapshot` / current effective plan evidence covering `periodStart -> periodEnd`; STOP if the historical opening plan/allowance cannot be proven;
4. require current last segment plan == transition `fromPlanId`;
5. atomically set current segment `effectiveTo = providerEffectiveAt`;
6. create target segment `providerEffectiveAt -> BillingPeriod.periodEnd` with immutable target plan/allowance snapshots;
7. construct the **complete candidate segment timeline from periodStart through periodEnd**;
8. call the published Shared target-entitlement primitive;
9. read `alreadyGranted = counter.grantedQuantity`, or `0` only for an existing provider Free cycle with no included counter before first same-cycle paid grant;
10. call Shared additional-grant primitive;
11. persist `targetEntitlementSnapshot`, `alreadyGrantedSnapshot`, `includedCreditDelta`;
12. apply exactly `grantedQuantity += includedCreditDelta`; preserve committed/reserved/forfeited;
13. update `Subscription.planId` / observed current plan projection to provider-confirmed target according to ARCH-010 semantics;
14. mark transition `APPLIED`, set application mode and timestamps;
15. emit existing bounded plan-upgraded system/audit effects only once where ARCH-010 owns them.

## E. Counter concurrency

Use the accepted entitlement convention exactly:

```text
interactive Prisma transaction
isolationLevel Serializable
read counter + version inside transaction
conditional updateMany WHERE id + version
version += 1 in same mutation
require count == 1
retry whole transaction on CAS/P2034 conflict with bounded retry
```

Do not introduce Redis locks, process mutexes, advisory locks, raw `SELECT FOR UPDATE` or unversioned read/update.

Conversation reservation may race with an upgrade grant. One versioned mutation wins; loser retries from fresh state.

## F. Usage is not a proration input

Do not pass/use:

```text
committedQuantity
reservedQuantity
remaining credits
RecoveryCreditPurchase balances
promotion balances
lifetime Free balances
```

to calculate target/additional grant.

Example binding result:

```text
Starter allowance = 100
Growth allowance  = 300
half-cycle transition

target = 200
alreadyGranted = 100
additionalGrant = 100
```

The additional grant remains `100` whether prior committed usage is `0`, `20`, `80` or `100`.

## G. Multiple same-cycle upgrades

After one transition is APPLIED another higher target may be requested/applied in the same provider BillingPeriod. There is no arbitrary upgrade-count limit.

Required supported history:

```text
Free -> Starter -> Growth -> Scale
```

and direct skipping such as:

```text
Free -> Scale
Starter -> Scale
```

For every new transition, recalculate the target from the **entire candidate segment timeline** and subtract current `grantedQuantity`. Do not independently floor a percentage delta per edge.

Each applied transition uses its own unique provider lifecycle event ID and creates exactly one target segment. Replay grants zero additional credits / returns prior result without a second mutation.

## H. Superseded/failed requests

Background must never treat `SUPERSEDED`/`FAILED` as effective.

If a REQUESTED transition is no longer provider-pending and provider definitively remains on the old plan, it may be marked FAILED only according to the accepted reconciliation evidence contract. Merchant-side supersession is owned by SHOPIFY-001.

## I. New provider cycle / full opening allowance

When provider reports a different/new `currentBillingCycle`:

1. use the accepted ARCH-010 boundary/activation/rollover semantics to close old period and open/project the exact provider cycle;
2. grant the full opening-plan allowance exactly once through the ARCH-010 period-opening path;
3. create/ensure the first ARCH-011 `BillingPlanSegment` spans new period start -> end using the opening effective plan snapshot;
4. if the provider target corresponds to a transition request, record it `APPLIED` with `NEW_PROVIDER_CYCLE_FULL_ALLOWANCE`;
5. leave same-cycle target/already-granted/delta fields null;
6. do not add another ARCH-011 prorated grant.

## J. Deferred downgrades

ARCH-011 never makes a lower plan effective mid-cycle. Existing ARCH-010 next-cycle downgrade semantics remain authoritative.

If a lower target becomes provider-current at the new provider-cycle boundary, the new cycle opens on that lower plan with its full opening allowance. Do not claw back the prior cycle.

## K. Rollover and segment closure

At provider cycle rollover:

```text
old final segment.effectiveTo == old BillingPeriod.periodEnd
old period closes under ARCH-010 rules
new BillingPeriod periodStart/periodEnd exactly provider values
new first segment covers full new period until later provider-confirmed upgrade
```

Delayed worker observation must use provider period/effective timestamps, not observation time.

## L. `target < alreadyGranted`

If Shared reports target entitlement below current granted quantity during an upgrade path:

```text
transition => NEEDS_ATTENTION
no clawback
no clamp-to-zero
no segment/counter partial commit
```

Return bounded evidence identifying provider cycle, segment timeline, target and granted values.

## Required tests

Prove at minimum:

1. same-cycle Starter -> Growth grant;
2. same result with different committed/reserved usage;
3. Free -> paid with preserved provider cycle is prorated;
4. Free -> paid with new provider cycle gets full opening allowance and no prorated delta;
5. direct Free -> Scale;
6. Starter -> Growth -> Scale in one cycle;
7. whole-period rounding across multiple upgrades;
8. duplicate provider event replay grants once;
9. two reconciliation workers race safely;
10. conversation reservation races upgrade CAS safely;
11. missing exact provider event => NEEDS_ATTENTION/no grant;
12. provider-cycle mismatch routes new-cycle path;
13. delayed observation uses provider timestamps;
14. lower-plan change is not applied mid-cycle;
15. deferred downgrade applies at next cycle through ARCH-010;
16. rollover creates/maintains exactly one opening segment;
17. `target < granted` fails closed;
18. purchased/promotional/lifetime-Free balances unchanged;
19. accepted ARCH-010 capacity order unchanged;
20. existing Background billing suites remain green except documented unrelated baseline failures.

## Validation

Run repository-declared equivalents of:

```text
npm run prisma:validate
npm run prisma:generate
<focused provider/reconciliation/concurrency tests>
npm test
npm run build
git diff --check
```

## Non-goals

No merchant UI, Admin UI, Shared implementation/publication, database migration, cash-proration calculation or purchased-credit mutation.

## Stop conditions

STOP if:

- exact provider effective-time evidence is unavailable;
- the accepted ARCH-010 transition/boundary path cannot be extended without replacing it;
- opening historical plan/allowance for an existing period cannot be proven;
- provider and local subscription identities contradict;
- implementation would require a new locking strategy;
- Shopify money proration would have to become an entitlement input.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
