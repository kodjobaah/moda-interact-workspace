---
id: ARCH-010-BASELINE
title: ARCH-010 first-production baseline and migration boundary
status: agreed
coordinator: moda_architect
created: 2026-09-12
updated: 2026-09-12
---

# ARCH-010 — First-production baseline and migration boundary

## Decision

ARCH-010 is the **first-production baseline** for Moda Interact billing, merchant lifecycle, recovery capacity, purchased credits and promotional campaigns.

Rollout classification:

```text
PRE-PRODUCTION / BREAKING ROLLOUT
```

The affected billing/lifecycle model has not entered production. There is no production merchant billing state, production queue traffic or deployed production consumer that requires backwards compatibility with the intermediate ARCH-007/008/009/010 development models.

Therefore first production MUST ship the final ARCH-010 model directly. Development-era migrations, aliases, compatibility reads, transitional state machines and historical backfills are not part of the production contract.

## Accepted-task history is immutable

Completed task files remain durable implementation/review evidence.

For ARCH-010 consolidation:

```text
Complete task
  -> do not reopen
  -> do not rewrite its accepted Completion Report
  -> if its accepted implementation is no longer the final first-release model,
     create/amend later correction work that removes the obsolete behaviour
```

This architecture deliberately chooses that stricter rule even though the generic developer workflow permits an explicit developer reopen.

`ARCH-010-DATABASE-001` through `ARCH-010-DATABASE-011` therefore remain Complete historical records. They are not the production migration chain.

`ARCH-010-DATABASE-012` was not completed and is superseded. Its still-valid upgrade-economics requirements are absorbed into `ARCH-010-DATABASE-013`.

## Canonical database boundary

`ARCH-010-DATABASE-013` owns one clean database baseline.

It starts from the fully integrated accepted schema through DATABASE-011, incorporates the still-valid DATABASE-012 economics requirements, removes development-only compatibility, and regenerates the migration history as a single empty-database baseline migration.

Conceptually:

```text
accepted development task history
DATABASE-001 ... DATABASE-011
             +
valid DATABASE-012 target requirements
             +
ARCH-010 final-state cleanup
             ↓
ARCH-010-DATABASE-013
             ↓
canonical Prisma schema
single first-production baseline migration
canonical seed + validators + ERD
             ↓
FIRST PRODUCTION DATABASE BASELINE
```

After DATABASE-013 is accepted, future architectures MUST use ordinary forward migrations from that baseline. ARCH-011 and later must not edit or re-squash the accepted ARCH-010 baseline merely because a later schema changes.

## Canonical first-release billing schema rules

### Lifetime Free recovery entitlement

Canonical counter name:

```text
LIFETIME_FREE_RECOVERY_CREDITS
```

It is a shop-lifetime entitlement, not a Free-plan allowance.

```text
first verified subscription activation (Free OR Paid)
  -> read PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
  -> create ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS) once
  -> snapshot grantedQuantity
  -> never reset/regrant on renewal, plan change, cancellation, uninstall,
     reinstall, freeze or unfreeze
```

First production has **no**:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_ALLOWANCE_ADJUSTED
FREE_RECOVERY_LIFETIME alias
legacy signed-adjustment read
compatibility fallback
BILLING_FREE_ALLOWANCE_EXHAUSTED historical-row compatibility
```

### Paid period entitlement

`BillingPeriod` and `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` remain first-release durable state.

`BillingPeriodCloseReason` contains real product lifecycle reasons only. `MIGRATION_RECONCILED` is development-migration history and is absent from the baseline.

### Purchased recovery credits and partial refunds

Purchased-credit lot accounting remains first-release behaviour.

A new ARCH-010 partial refund:

```text
RecoveryCreditPurchase remains ACTIVE
purchase.refundedQuantity records removed quantity
RecoveryCreditRefund records request/approval/provider evidence/completion
human Shopify Partner Dashboard REFUND or CREDIT
no negative/fractional App Event correction
```

First production has no legacy `RecoveryCreditPurchaseStatus.REFUNDED` compatibility state and no automatic negative-App-Event refund processor.

`RecoveryCreditRefund` does not need the old automatic-settlement state/fields. The canonical human workflow uses:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
COMPLETED
REJECTED
WITHDRAWN
NEEDS_ATTENTION
```

Provider evidence remains durable through the explicit REFUND/CREDIT action, provider reference, amount, currency, confirming admin and confirmation time.

### Subscription cancellation

Shopify App Pricing is cancellation authority.

Moda observes/reconciles provider state. First production has no local cancellation request/approval/execution state machine and no `appSubscriptionCancel` execution path.

Remove first-release schema/contracts/runtime based on:

```text
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
local cancellation approval/executor queues
```

### Promotional campaigns

First-release promotional capacity is **campaign-linked and merchant-selected only**.

```text
PromotionCampaign
  -> merchant selection
  -> exactly one PromotionalCreditGrant for (campaignId, shopId)
  -> MerchantPromotionSelection points to one current grant
  -> UsageReservation points to the exact promotional grant
```

There is no campaign-less direct grant compatibility in the first-production baseline. `PromotionalCreditGrant.campaignId` is required.

The exact campaign grant lot is capacity authority. The development-era aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` is removed; no runtime path may use an aggregate promo counter as fallback or compatibility accounting.

First-release promotion capacity order is:

```text
PAID
  selected usable promotion
  -> current-period included
  -> purchased FIFO lot
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

FREE
  selected usable promotion
  -> purchased FIFO lot
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

### Upgrade economics

DATABASE-013 also incorporates the valid target of superseded DATABASE-012:

- `PlatformBillingPolicy.minimumUpgradePremiumBps` default 2000;
- explicit non-branching `BillingUpgradeEconomicsEdge` plan ladder;
- append-only verified `BillingEconomicsSnapshot` evidence;
- `UPGRADE_ECONOMICS_EVALUATED` audit action;
- no local BillingPlan monetary authority.

Lifetime Free, promotions, purchased balances, refunds and current merchant usage are never recurring monthly capacity for upgrade economics.

## State that remains first-release durable history

The baseline cleanup does **not** remove genuine product history merely because the platform is pre-production.

Keep:

```text
BillingPeriod lifecycle history
Subscription current/pending projection and latest provider lifecycle evidence
purchase-lot and partial-refund audit history
PromotionCampaign lifecycle events
merchant campaign grant/selection/use history
Shopify lifecycle evidence
credit preservation across freeze/uninstall/cancellation
PostgreSQL state required to reconstruct BullMQ jobs after Redis loss
merchant support/refund source-message evidence
```

The distinction is:

```text
remove development compatibility
keep intentional first-release product history
```

## Runtime correction strategy

Do not reopen completed runtime tasks merely because they implemented against an earlier development schema.

Instead:

- amend still-Pending/Ready ARCH-010 tasks so they implement only the baseline contract;
- treat `ARCH-010-SHOPIFY-002` as completed per the 2026-09-12 developer status correction; preserve its implementation/review provenance and use the dependent baseline-conformance task after it;
- use new correction tasks where already-Complete runtime work still references removed baseline concepts;
- publish one clean Shared follow-up release containing the retained first-release contracts and removing obsolete pre-production cancellation exports.

## Database reset and data policy

DATABASE-013 is allowed to replace the development migration chain because there is no production billing state to preserve.

The task MUST NOT attempt to preserve or backfill development-only billing rows into the production baseline.

After integration, local/development/test databases that were created from the old migration chain are recreated/reset against the new baseline. Never run a destructive reset against a database unless its environment is explicitly confirmed as local/development/test.

## Rollout order

The first-production consolidation order is:

```text
1. DATABASE-013   canonical database baseline                         COMPLETE
2. BACKGROUND-020 + SHOPIFY-024
                  remove live first-party consumers                   COMPLETE
3. SHARED-007     remove obsolete Shared compatibility contracts     COMPLETE
4. SHARED-008     publish clean Shared first-production contract      COMPLETE
5. repository baseline-conformance work                              CURRENT FRONTIER
6. remaining ARCH-010 feature tasks
7. developer manual integrated verification
8. terminal/manual-gated ARCH-010 system tests
```

This order is a sequencing correction discovered by SHARED-007 Attempt 1. The earlier
direct `SHARED-007 -> SHARED-008 -> consumer cleanup` order was circular because live
Background/Shopify consumers still imported contracts SHARED-007 must delete.

DATABASE-013 is already independent of this Shared consumer-cleanup chain.

## Non-goals

This baseline decision does not:

- redesign unrelated commerce, messaging, translation or observability schema;
- erase accepted task/review history;
- preserve development data merely for compatibility;
- add production backwards-compatibility adapters before production exists;
- change Shopify App Pricing authority;
- turn system-test tasks into prerequisites for implementation.

## Future migration rule

After first production begins, the default changes from breaking rebaseline to normal production-compatible migration analysis.

Future architecture work must explicitly assess production data, queued work, producer/consumer deployment order, rollback and compatibility before removing or renaming persisted contracts.
