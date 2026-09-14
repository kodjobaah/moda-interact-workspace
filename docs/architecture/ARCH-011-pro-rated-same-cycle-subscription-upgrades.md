---
id: ARCH-011
title: Pro-rated same-cycle subscription upgrades
status: agreed
coordinator: moda_architect
created: 2026-09-13
updated: 2026-09-14
---

# ARCH-011: Pro-rated same-cycle subscription upgrades

## Status

**Agreed for revised implementation tasking.** ARCH-011 is a forward extension of the frozen ARCH-010 behaviour. It does not reopen or amend ARCH-010 task history.

Database-specific baseline:

```text
ARCH-010-DATABASE-013
```

ARCH-011 database work MUST be additive from DATABASE-013. It MUST NOT depend on DATABASE-014 or copy DATABASE-014 as a schema prerequisite.

Other ARCH-010 capabilities referenced by ARCH-011 are treated as immutable external baseline contracts. If an implementation workspace does not yet contain one of those assumed runtime capabilities, the ARCH-011 repository agent must STOP and report the baseline gap; it must not implement or rewrite the missing ARCH-010 task inside ARCH-011.

ARCH-011 adds exactly one product capability:

> A merchant may move to any strictly higher Moda subscription tier during the current Shopify App Pricing billing cycle. Shopify remains commercial authority for the actual subscription and monetary treatment. Moda grants only the additional included-recovery-credit entitlement justified by the provider-confirmed higher plan and its exact effective time.

## Native Shopify App Pricing only

Moda Interact is still in development and has no production merchants or legacy Billing API subscriptions.

ARCH-011 therefore supports **native Shopify App Pricing only**.

Binding consequences:

```text
legacySubscriptionId is NOT an ARCH-011 identity requirement
no Billing API migration branch
no legacy AppSubscription migration compatibility
no providerSubscriptionIdSnapshot requirement in SubscriptionPlanTransition
```

An ARCH-010 field that already stores legacy/provider subscription identity may remain untouched for baseline compatibility, but ARCH-011 MUST NOT use that field as a prerequisite for provider confirmation, proration or idempotency.

ARCH-011 provider identity/evidence is based on:

```text
configured Shopify app identity
Shop.shopifyShopId / validated provider shop identity
activeSubscription current state
activeSubscription.currentBillingCycle
Partner Historical Events event identity
Partner Historical Events occurredAt
```

## Immutable ARCH-010 boundaries

ARCH-011 MUST NOT redesign or reset:

```text
RecoveryCreditPurchase lifecycle/refund valuation when that baseline capability exists
purchased-credit FIFO allocation
promotional-credit allocation
LIFETIME_FREE_RECOVERY_CREDITS
existing admitted conversation reservation semantics
freeze/unfreeze/cancellation/uninstall/reinstall semantics
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

```text
Shopify Partner activeSubscription.currentBillingCycle
    = provider/commercial app billing-cycle authority

Moda BillingPeriod
    = exact local projection of that provider app billing cycle

BillingPlanSegment
    = which Moda plan was effective during part of that BillingPeriod
```

Moda MUST NOT manufacture a provider cycle from:

```text
merchant click time
local createdAt + 30 days
calendar month
store invoice dates
worker observation time
```

If `activeSubscription.currentBillingCycle` is null, ARCH-011 same-cycle proration is not eligible. Preserve the accepted trial/fail-closed behaviour; do not invent a billing cycle.

## Canonical tier topology

`BillingUpgradeEconomicsEdge` remains the adjacent ordering graph.

Example:

```text
Free -> Starter -> Growth -> Scale
```

The graph defines order, not allowed merchant steps. All transitively higher direct targets are upgrades:

```text
Free -> Starter
Free -> Growth
Free -> Scale
Starter -> Growth
Starter -> Scale
Growth -> Scale
```

Direction MUST NOT be inferred from plan name, price, allowance size, display order or lexicographic order.

```text
same plan => SAME
provider/target later in validated chain => UPGRADE
provider/target earlier in validated chain => DOWNGRADE
invalid/missing/ambiguous topology => UNRESOLVED
```

Database persistence is final topology authority. Shared provides the canonical deterministic validator/classifier for application preflight and bounded errors.

## Product transition rule: upgrade now, downgrade next cycle

### Same-cycle upgrades

A strictly higher provider-confirmed target may become effective inside the current provider cycle and is eligible for ARCH-011 included-credit proration.

Multiple upgrades in one cycle are allowed. Direct tier skipping is allowed.

### Downgrades

**Downgrades are never prorated by Moda.**

A lower plan may be selected/requested at any time, but Moda MUST NOT make it locally effective inside the current provider cycle.

Binding rule:

```text
UPGRADE
  provider makes higher plan current inside same cycle
  => ARCH-011 SAME_CYCLE_PRORATED

DOWNGRADE
  provider exposes lower plan as pending for next cycle
  => preserve current effective plan/counter/meter until boundary
  => ARCH-010 boundary path applies lower plan at new cycle
  => no current-cycle clawback
  => no current-cycle refund/entitlement reduction calculation in Moda
```

Paid -> Free is expected to follow Shopify App Pricing's deferred cancellation/downgrade behaviour.

For paid -> lower-paid, Moda's release-1 product policy is also deferred. Because Shopify's hosted pricing page is provider-owned, production validation MUST prove that a lower paid selection remains current-plan + `pendingUpdate` until the next cycle. If Shopify makes a lower paid plan current inside the same provider cycle, ARCH-011 MUST fail closed and the production system-test gate MUST fail. Do not invent downgrade proration to accommodate that provider behaviour.

## Merchant-selected target is intent, not provider authority

Moda redirects to Shopify's hosted pricing-plan selector. Therefore the target clicked in Moda is **merchant intent only**. Shopify may ultimately confirm a different plan.

Example:

```text
local effective plan: Starter
Moda requested target: Scale
Shopify actual selected/current plan: Growth
```

Required result:

```text
requested target remains historical intent = Scale
provider-confirmed target = Growth
Growth is the only target eligible for local application/proration
```

ARCH-011 MUST NOT require:

```text
provider current plan == requested target
```

Instead, provider reconciliation classifies the actual provider-current plan from the still-effective local source plan.

If provider current plan is a valid UPGRADE, that provider target is authoritative even when it differs from the original requested target.

If no merchant `REQUESTED` row exists and Shopify is already on a valid higher plan, Background creates a provider-observed transition and reconciles it. Browser callback delivery is therefore an accelerator, not a correctness dependency.

## Transition origin and lifecycle

`SubscriptionPlanTransition` is an **upgrade transition** record. Downgrades remain on the existing Subscription pending-plan / boundary mechanism.

Origins:

```text
MERCHANT_REQUEST
  created before redirect; requested target is captured as intent.

PROVIDER_OBSERVED
  no usable merchant request exists; provider is already on a valid higher plan.
```

States:

```text
REQUESTED
  merchant intent exists; provider has not yet proven a higher current plan.

PROVIDER_CONFIRMED
  actual higher provider-current plan/cycle/effective-time evidence is durably captured;
  local segment/counter application is not yet complete.

APPLIED
  transition applied exactly once.

SUPERSEDED
  merchant intent was replaced/cancelled before a provider-current higher plan was established,
  or Shopify instead scheduled a lower next-cycle plan.

FAILED
  terminally could not be confirmed/applied under the bounded reconciliation contract.

NEEDS_ATTENTION
  provider changed but exact/consistent evidence required for safe application is unavailable.
```

Terminal:

```text
APPLIED
SUPERSEDED
FAILED
```

At most one unresolved transition per subscription exists in:

```text
REQUESTED
PROVIDER_CONFIRMED
NEEDS_ATTENTION
```

## Hosted-selector request and callback rule

For an immediate higher-plan request:

```text
server validates topology
-> persist REQUESTED intent
-> schedule/reuse subscription reconciliation
-> redirect to Shopify hosted pricing page
```

The callback `plan_handle` is a hint/evidence trigger only. It MUST NOT directly mutate current entitlement or make the requested plan effective.

Callback flow:

```text
callback received
-> fresh Partner API read/reconciliation
-> actual provider current/pending state wins
```

Lost callback flow:

```text
callback absent
-> already-scheduled reconciliation still observes provider state
-> provider-current higher plan can still become PROVIDER_CONFIRMED/APPLIED
```

The existing bounded subscription-reconciliation retry/backoff contract is reused. Do not create a second scheduler.

When the existing request observation/retry window is exhausted and a fresh provider read still proves:

```text
provider current == local source
AND no conflicting provider pending update
```

then a MERCHANT_REQUEST transition may become:

```text
FAILED
failureCode = REQUEST_NOT_CONFIRMED
```

A later out-of-band provider upgrade is still recoverable by creating a new `PROVIDER_OBSERVED` transition.

## Provider-confirmed effective time

For same-cycle proration, Background must prove:

1. provider app/shop identity is valid;
2. provider current plan maps to an active BillingPlan;
3. Shared classifies local effective -> provider current as UPGRADE;
4. provider currentBillingCycle exactly matches the still-open local BillingPeriod;
5. bounded CREATED/UPDATED Partner event matches provider current plan and app/shop;
6. `providerCycleStart < event.occurredAt < providerCycleEnd`;
7. event ID has not already been applied.

Then:

```text
providerEffectiveAt = matching provider lifecycle event occurredAt
provider-confirmed target = provider current plan
```

Never substitute worker time, request time, callback time or local `updatedAt`.

If provider is already on a different higher plan but exact same-cycle event evidence is not yet provable:

```text
transition => NEEDS_ATTENTION
no grant
no partial segment mutation
reconciliation remains scheduled
```

If the exact event becomes available later in the same cycle, NEEDS_ATTENTION may recover to PROVIDER_CONFIRMED/APPLIED.

If the cycle rolls over before exact old-cycle effective time can be proven, the ambiguous old transition becomes FAILED with a bounded failure code and the new provider cycle is projected through the normal full-opening boundary path. Moda never invents the missing old-cycle timestamp.

## Same-cycle versus new-cycle

```text
provider cycle != local open BillingPeriod
  => NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
  => existing ARCH-010 boundary/opening semantics
  => no ARCH-011 prorated delta

provider cycle == local open BillingPeriod
AND exact provider event is strictly inside the cycle
AND direction == UPGRADE
  => SAME_CYCLE_PRORATED
```

An event exactly at the new provider-cycle start is not a same-cycle interior transition; it belongs to the new-cycle/full-opening path.

## Downgrade provider-state decision table

When local current remains Growth and provider reports:

```text
active current = Growth
pendingUpdate = Starter or Free
```

required behaviour:

```text
Growth remains locally effective
no BillingPlanSegment split
no proration
no included-credit reduction
Subscription pending plan/effective boundary remains the existing downgrade projection
at next provider cycle: ARCH-010 boundary transition applies lower plan
```

If a MERCHANT_REQUEST upgrade row exists but Shopify instead exposes a lower `pendingUpdate`, that upgrade request becomes SUPERSEDED; no ARCH-011 downgrade transition is created.

If provider unexpectedly reports a lower plan as **current** while the same local provider cycle is still open:

```text
NEEDS_ATTENTION / fail closed
no downgrade proration
no credit clawback
no stale-plan billable operations
```

This condition is a release blocker if reproduced as normal Shopify App Pricing lower-paid behaviour.

## BillingPlanSegment

One BillingPeriod remains one exact provider cycle even across repeated upgrades.

Example:

```text
BillingPeriod: 1 Sep -> 1 Oct

Free      1 Sep -> 5 Sep
Starter   5 Sep -> 12 Sep
Growth   12 Sep -> 20 Sep
Scale    20 Sep -> 1 Oct
```

`BillingPeriod.plan*Snapshot` remains the period-opening plan snapshot.

`BillingPlanSegment` records actual provider-effective plan history. It MUST NOT fabricate intermediate tiers for a direct skip.

## Included-credit target entitlement

Usage is not an input to proration.

Candidate segments cover the exact whole provider cycle, are contiguous/non-overlapping, and carry immutable included-allowance snapshots.

```text
targetEntitlement = floor(
  SUM(segmentAllowance * segmentDurationMs)
  / totalProviderCycleDurationMs
)
```

Use integer/BigInt intermediate arithmetic.

Then:

```text
alreadyGranted = current period INCLUDED_RECOVERY_CREDITS.grantedQuantity
                 or 0 for an existing Free provider cycle with no included counter

additionalGrant = targetEntitlement - alreadyGranted
```

Require:

```text
targetEntitlement >= alreadyGranted
additionalGrant >= 0
```

If false:

```text
NEEDS_ATTENTION
no clawback
no clamp-to-zero
no partial mutation
```

Mutate only:

```text
grantedQuantity += additionalGrant
```

Preserve committed/reserved/forfeited exactly.

The following are not proration inputs:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
remaining credits
purchased credits
promotional credits
lifetime Free credits
Shopify monetary proration
```

## Multiple upgrades and rounding

For every provider-confirmed higher transition, recalculate the target from the complete candidate segment history through cycle end, then subtract current `grantedQuantity`.

Do not independently floor a percentage grant per adjacent edge.

## Billing/meter safety during provider/local mismatch

ARCH-010's stale-meter safety rule remains binding.

When provider current is known to differ from local effective plan and the higher transition is not yet APPLIED (`PROVIDER_CONFIRMED` or `NEEDS_ATTENTION`):

```text
block new billable recovery operations that would require a plan-specific Shopify recovery meter
block new top-up initiation
preserve existing durable reservations/purchases/refund state
```

Do not block normal recovery merely because a REQUESTED intent exists while provider is still proven on the local effective plan.

If the existing implementation reveals that unresolved old-plan reportable UsageEvents can remain when Shopify has already changed current plan and there is no architecture-safe handling consistent with ARCH-010's "do not send old-plan meter events after provider current plan changed" rule, STOP and return exact evidence to moda_architect. Do not rewrite UsageEvent provenance or silently retarget an old event to a new meter.

## Monetary proration

Shopify owns cash proration/charging. Moda MUST NOT calculate, reproduce or use Shopify monetary proration as an included-credit input.

## Repository ownership

```text
moda-interact-database
  BillingPlanSegment + SubscriptionPlanTransition persistence
  provider-confirmed target evidence
  DB-enforced canonical tier topology

moda-interact-shared
  pure topology validation/direction classification
  pure whole-period target/additional-grant arithmetic
  publication

moda-interact-background
  exact Partner plan-event evidence
  provider-authoritative upgrade observation/reconciliation/application
  same-cycle/new-cycle decision
  NEEDS_ATTENTION recovery
  downgrade deferral integration
  provider/local billing safety fence

moda-interact
  merchant intent + Shopify hosted redirect/callback trigger
  request supersession
  downgrade request presentation
  top-up gate
  merchant billing UI/history

moda-interact-admin
  topology/economics management preflight
  read-only transition/segment/proration audit

moda-interact-system-test
  terminal manual-gated provider/lifecycle/concurrency/regression proof
```

No Gateway or Messaging task is required.


## Deterministic implementation decomposition (Luna binding)

The implementation is deliberately split so no Luna task owns multiple independently useful mechanisms.

```text
DATABASE-001   transition/segment persistence only
DATABASE-002   database-final canonical topology enforcement only
SHARED-001     pure topology/proration contract
SHARED-002     publication only
BACKGROUND-001 provider evidence only
BACKGROUND-002 provider-authoritative upgrade reconciliation/application only
BACKGROUND-003 paid-recovery stale-meter admission/commit fence only
SHOPIFY-001    server plan-change intent/redirect/callback/downgrade projection/top-up gate only
SHOPIFY-002    merchant billing presentation only
ADMIN-001      topology configuration mutation only
ADMIN-002      read-only upgrade/downgrade audit presentation only
SYSTEM-TEST-001 terminal integrated validation only
```

A task MUST edit only the files explicitly listed in its **Authorized implementation surface** unless a listed file imports a directly inseparable local type/test helper. If another repository capability is required, STOP and return to `moda_architect`; do not broaden scope.
