---
id: ARCH-011
title: Pro-rated same-cycle subscription upgrades
status: agreed
coordinator: moda_architect
created: 2026-09-13
updated: 2026-09-13
---

# ARCH-011: Pro-rated same-cycle subscription upgrades

## Status

**Agreed for implementation tasking.** ARCH-011 is a forward extension of the accepted ARCH-010 billing/lifecycle model. It does not reopen completed ARCH-010 task history.

ARCH-011 adds one capability:

> A merchant may move to any strictly higher subscription tier during the current Shopify App Pricing billing cycle. Shopify remains commercial authority for the subscription and monetary proration. Moda changes only the current provider-cycle plan history and the merchant's included-recovery-credit entitlement after the higher plan is provider-confirmed.

## Non-goals / immutable ARCH-010 boundaries

ARCH-011 MUST NOT redesign or reset:

```text
RecoveryCreditPurchase lifecycle or refund valuation
purchased-credit FIFO allocation
promotional-credit allocation
LIFETIME_FREE_RECOVERY_CREDITS
existing admitted conversation reservations
freeze/unfreeze, cancellation or uninstall/reinstall semantics
Shopify as commercial billing authority
ARCH-010 capacity order
```

Accepted capacity order remains:

```text
PAID
  selected promotion
  -> current BillingPeriod INCLUDED_RECOVERY_CREDITS
  -> purchased FIFO
  -> lifetime Free
  -> block

FREE
  selected promotion
  -> purchased FIFO
  -> lifetime Free
  -> block
```

## Provider time authority

The merchant's ordinary Shopify store invoice cycle is not Moda's entitlement clock.

Binding model:

```text
Shopify Partner activeSubscription.currentBillingCycle
    = provider/commercial app billing-cycle authority

Moda BillingPeriod
    = exact local projection of that provider app billing cycle

BillingPlanSegment
    = which Moda plan was effective during part of that BillingPeriod
```

Moda MUST NOT manufacture a billing period from:

```text
merchant click time
local createdAt + 30 days
calendar month
Shopify store invoice dates
worker observation time
```

## Canonical tier topology

ARCH-011 reuses `BillingUpgradeEconomicsEdge` as the explicit adjacent-tier ordering graph.

The graph is an **ordering graph only**. It is not an allowed-transition whitelist.

Canonical example:

```text
Free -> Starter -> Growth -> Scale
```

All transitively higher targets are valid direct upgrades:

```text
Free -> Starter
Free -> Growth
Free -> Scale
Starter -> Growth
Starter -> Scale
Growth -> Scale
```

The merchant never has to move one tier at a time.

Direction MUST NOT be inferred from:

```text
plan name
plan price
allowance size alone
lexicographic order
current discount
```

Direction classification:

```text
same plan
  => SAME

target reachable by following active higher edges from current
  => UPGRADE

current reachable by following active higher edges from target
  => DOWNGRADE

invalid/disconnected/cyclic/ambiguous topology
  => UNRESOLVED and fail closed
```

The persisted active topology itself must be one valid acyclic linear chain across the active Shopify-mapped merchant plan catalogue. Database persistence is the final invariant authority; Shared provides the canonical pure validation/classification implementation used by applications for preflight and deterministic error reporting.

## Upgrade and downgrade rules

### Immediate upgrades

Any transitively higher target is eligible for immediate Shopify-hosted upgrade.

Multiple upgrades in one provider BillingPeriod are allowed without an architectural limit:

```text
Free -> Starter -> Growth -> Scale
```

Skipping is also allowed:

```text
Free -> Scale
Starter -> Scale
```

### Downgrades

A lower plan MUST NOT become effective mid-cycle through ARCH-011.

A lower target remains an ARCH-010 next-provider-cycle change. No current-cycle credit clawback is performed.

### Unverified requested upgrade may be replaced

A requested target is not an effective plan.

Example:

```text
effective Starter
Growth REQUESTED but not provider-confirmed
merchant selects Scale
```

Required result:

```text
fresh provider read proves Growth is not current
old Starter -> Growth request becomes SUPERSEDED
new request is Starter -> Scale
```

The replacement is always classified from the **still-effective** plan, never from the unverified target.

If the fresh provider read proves the old target already became current, supersession is refused and reconciliation must first apply that provider-effective transition.

## One unresolved transition per subscription

At most one transition may be unresolved for a subscription in:

```text
REQUESTED
PROVIDER_CONFIRMED
NEEDS_ATTENTION
```

Terminal states:

```text
APPLIED
SUPERSEDED
FAILED
```

`REQUESTED` may be superseded only after a fresh provider read proves it has not become current.

`PROVIDER_CONFIRMED` and `NEEDS_ATTENTION` block another immediate upgrade until reconciled.

## Provider-confirmed effective time

For a same-cycle upgrade, Moda may apply a prorated entitlement only when it can prove:

1. provider current plan maps to the requested target;
2. provider subscription identity matches the local subscription projection;
3. provider `currentBillingCycle` exactly matches the still-open local `BillingPeriod`;
4. a bounded Shopify Partner subscription CREATED/UPDATED event for the app+shop matches the provider current plan;
5. event `occurredAt` is strictly inside the provider cycle;
6. provider event identity has not already been applied.

For same-cycle proration:

```text
providerEffectiveAt = matching provider lifecycle event occurredAt
```

Moda MUST NOT use worker observation time.

If current provider plan changed but exact same-cycle effective-time evidence cannot be proven, persist `NEEDS_ATTENTION`, do not grant credits, and block conflicting new billing actions.

## New provider cycle versus same-cycle upgrade

This distinction is binding, including Free -> paid.

After provider confirmation:

```text
provider currentBillingCycle != local open BillingPeriod
    => NEW PROVIDER CYCLE / ARCH-010 boundary path
    => no ARCH-011 same-cycle proration
    => opening plan receives the normal full opening allowance

provider currentBillingCycle == local open BillingPeriod
AND providerEffectiveAt is strictly inside that cycle
    => ARCH-011 SAME_CYCLE_PRORATED path
```

Therefore:

- if Free -> Starter creates a newly anchored Shopify app billing cycle, Starter receives the normal full Starter opening allowance;
- if Shopify preserves an existing Free provider cycle and Starter becomes current inside it, Starter participates in same-cycle target-entitlement proration.

Moda never chooses which provider behaviour occurred.

## BillingPlanSegment

One `BillingPeriod` remains one provider cycle even after multiple upgrades.

Example:

```text
BillingPeriod: 1 Sep -> 1 Oct

Free      1 Sep -> 5 Sep
Starter   5 Sep -> 12 Sep
Growth   12 Sep -> 20 Sep
Scale    20 Sep -> 1 Oct
```

`Subscription.planId` remains the current local projection.

`BillingPeriod.plan*Snapshot` remains the **period-opening plan snapshot** and is not rewritten on each upgrade.

`BillingPlanSegment` is the durable plan-effective history inside the provider cycle.

## Included-credit entitlement: binding calculation

ARCH-011 does **not** calculate the grant from how many credits the merchant has already used.

Usage is deliberately excluded from proration.

The following are NOT inputs to the entitlement calculation:

```text
BillingPeriodEntitlementCounter.committedQuantity
BillingPeriodEntitlementCounter.reservedQuantity
purchased-credit balances
promotional-credit balances
lifetime-Free balances
```

For a provider-confirmed same-cycle upgrade, construct the complete **candidate segment timeline for the entire provider cycle** after applying the new target segment.

Example candidate timeline:

```text
cycleStart                                              cycleEnd
   |---------------------------------------------------------|
   Free             Starter              Growth
   |----------------|--------------------|--------------------|
```

Every candidate segment carries the immutable included allowance for that segment's plan:

```text
FREE = 0
PAID_METERED = includedRecoveryConversationAllowance snapshot
```

The candidate segments MUST:

```text
start exactly at providerCycleStart
end exactly at providerCycleEnd
be strictly ordered
be contiguous
have no gaps
have no overlaps
have non-negative integer allowance snapshots
```

Calculate with integer/rational arithmetic only:

```text
totalDurationMs = providerCycleEnd - providerCycleStart

weightedAllowanceTime =
    SUM(segment.includedAllowance * segment.durationMs)

targetEntitlement =
    floor(weightedAllowanceTime / totalDurationMs)
```

Use safe integer / BigInt intermediate arithmetic. Do not use IEEE floating point entitlement arithmetic.

Then:

```text
alreadyGranted =
    current BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS).grantedQuantity
    or 0 when the current Free provider period has no included counter yet

additionalGrant = targetEntitlement - alreadyGranted
```

Required invariants:

```text
targetEntitlement >= alreadyGranted
additionalGrant >= 0
```

If `targetEntitlement < alreadyGranted`, fail closed as inconsistent history/configuration. Do NOT claw back existing current-cycle credits and do NOT clamp to zero.

Apply only:

```text
grantedQuantity += additionalGrant
```

Preserve exactly:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
```

### Why prior usage does not matter

Example:

```text
Starter allowance = 100
Growth allowance  = 300
upgrade halfway through cycle

targetEntitlement = floor((100 * 50%) + (300 * 50%)) = 200
alreadyGranted    = 100
additionalGrant   = 100
```

Whether the merchant previously used 0, 20, 80 or all 100 Starter credits, `additionalGrant` is still 100. Usage changes remaining availability, not the entitlement created by the upgrade.

### Multiple upgrades and rounding

Recalculate the target from the **whole candidate segment history**, not by independently flooring `(newAllowance - oldAllowance) * remainingFraction` for every transition.

This avoids cumulative rounding drift across multiple upgrades.

Example:

```text
Free 0       1 Sep -> 5 Sep
Starter 100  5 Sep -> 12 Sep
Growth 300  12 Sep -> 20 Sep
Scale 1000  20 Sep -> 1 Oct
```

At each provider-confirmed transition:

1. construct candidate full-cycle segments including the new target through `cycleEnd`;
2. calculate one `targetEntitlement` from the complete timeline;
3. subtract the counter's current `grantedQuantity`;
4. persist both `targetEntitlement` and `additionalGrant` as immutable transition evidence;
5. increment `grantedQuantity` exactly once by `additionalGrant`.

## New-cycle opening allowance

ARCH-011 target-entitlement proration is only for a provider-confirmed plan transition inside the **same provider cycle**.

When Shopify reports a new provider cycle, ARCH-010 boundary/activation semantics open the new `BillingPeriod` and grant the full opening-plan allowance. ARCH-011 records/opens the corresponding first plan segment but does not prorate that new cycle.

## Top-up safety during unresolved plan transition

Top-up meter/rate may differ by provider tier.

While a transition is unresolved:

```text
REQUESTED
PROVIDER_CONFIRMED
NEEDS_ATTENTION
```

new `RecoveryCreditPurchase` requests are blocked.

Existing purchases, reservations, refund requests and refund settlement continue under ARCH-010 rules.

After `APPLIED`, new top-ups use the newly current provider plan/meter and retain immutable ARCH-010 purchase provenance.

## Existing purchase/refund provenance remains independent

A top-up purchased under Starter remains a Starter-era purchase even if the merchant later upgrades to Growth/Scale.

ARCH-011 MUST NOT recalculate purchase refund monetary basis from current plan or current top-up rate.

## Concurrency and idempotency

Applying one transition and increasing the current-period included counter must be replay-safe.

The same provider lifecycle event must never grant twice.

Required durable identities include:

```text
merchant request key
subscription ID
provider subscription ID
provider cycle start/end
provider lifecycle event ID
from-plan snapshot
to-plan snapshot
```

Counter mutation uses the accepted architecture convention:

```text
interactive Prisma transaction
isolationLevel Serializable
read counter + version inside transaction
conditional updateMany CAS on id + version
require count == 1
retry whole transaction on CAS/P2034 conflict
```

Do not substitute:

```text
Redis lock
process mutex
advisory lock
raw SELECT FOR UPDATE as a new entitlement-locking strategy
unversioned read/update
```

Conversation reservation and upgrade grant may race. One CAS mutation wins; the loser retries from fresh state.

## Monetary proration

Shopify owns the subscription-fee proration.

Moda MUST NOT:

```text
calculate Shopify's cash charge
infer cash charge from recovery-credit entitlement
use Shopify cash proration to calculate recovery credits
invent a local monetary proration authority
```

## Repository ownership

```text
moda-interact-database
  one consolidated ARCH-011 database task owns plan-segment + transition persistence
  and database-enforced canonical active tier topology

moda-interact-shared
  pure topology validation/direction classifier
  pure target-period-entitlement calculation
  publication

moda-interact-background
  provider-evidence task owns exact provider transition evidence only
  one consolidated lifecycle task owns provider-confirmed transition application,
  target entitlement grant, repeated upgrades, rollover and deferred-downgrade integration

moda-interact
  one consolidated merchant task owns upgrade intent/supersession,
  Shopify-hosted plan management integration, top-up ambiguity gate,
  merchant UI and current-cycle history

moda-interact-admin
  one consolidated Admin task owns topology/economics configuration UI
  and transition/segment operational audit UI; it is never topology authority

moda-interact-system-test
  one terminal/manual-gated integrated lifecycle + concurrency/regression validation task
```

No Gateway or Messaging task is required.
