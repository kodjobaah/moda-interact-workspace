---
id: ARCH-018
title: Promotion selection lock and expiry reconciliation
status: Agreed
coordinator: moda_architect
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-018: Promotion selection lock and expiry reconciliation

## Status

Agreed.

## Problem

The current ARCH-010 promotion implementation conflates two different concepts:

1. whether a selected promotional-credit grant is currently **spendable**; and
2. whether the merchant is still **locked to the promotion they selected**.

Current `moda-interact/app/services/promotions/promotion.service.ts` permits a merchant to replace the current promotion when the selected grant becomes unusable because it is exhausted, the campaign is closed, or the merchant is no longer target-eligible. That is not the required merchant contract.

The required product rule is:

> Once a merchant selects a promotion, that promotion occupies the merchant's single promotion-selection slot until `PromotionCampaign.expiresAt`. Exhausting the promotional credits early, manually closing the campaign, or losing target eligibility may stop the credits from being spendable, but none of those conditions releases the selection lock. Only expiry releases the lock.

The merchant UI must make this explicit and must suppress accidental duplicate submissions.

Expired `MerchantPromotionSelection` pointers should also be cleaned up automatically. The cleanup belongs to the existing dynamically controlled `BILLING_RECONCILIATION` cycle so the Admin reconciliation interval controls cleanup latency. The timer is not the business correctness boundary: a merchant must be able to select a new promotion immediately after `expiresAt`, even if cleanup has not yet run.

## Supersession

ARCH-018 supersedes only the ARCH-010 rule that allowed a new promotion to replace a current selection because the current promotion was exhausted, closed, or no longer target-eligible.

Historical ARCH-010 task/document history remains immutable. The new authoritative rule is:

```text
selection lock release = PromotionCampaign.expiresAt <= now
```

The following remain spendability rules only:

```text
PromotionalCreditGrant exhausted / remaining credits = 0
PromotionCampaign.status != ACTIVE
PromotionCampaign.startsAt > now
merchant no longer target-eligible
shop/subscription execution gate
```

## Goals

- keep exactly one current promotion-selection slot per Shop;
- release that slot only when the selected campaign expires;
- prevent exhaustion, closure, or target ineligibility from releasing the slot early;
- preserve existing promotional-credit spendability rules;
- make expiry authoritative at request time so background lag cannot block selection;
- clean stale selection pointers from Background using the existing billing reconciliation cadence and distributed lease;
- preserve `PromotionalCreditGrant`, reservation and history rows when cleanup releases the pointer;
- prevent cleanup from deleting a newer replacement selection during a race;
- make the merchant UI clearly state that another promotion becomes selectable only after expiry;
- prevent rapid/double UI submission and retain server-side authority;
- clarify the existing Admin reconciliation interval description without adding a new timer or runtime-config field.

## Non-goals

- no new Prisma model, field, enum, index or migration;
- no new reconciliation lease/timer;
- no new BullMQ queue;
- no change to campaign targeting, campaign create/edit/reopen rules or promotional-credit quantity allocation;
- no replenishment when a previously claimed campaign is selected again after it becomes eligible again;
- no change to promotional-credit reservation priority/spendability in Background;
- no change to Shopify subscription/proration architecture;
- no automatic deletion of `PromotionalCreditGrant` or campaign/history evidence;
- no Admin control for a separate promotion reconciliation interval.

## Current architecture

### Merchant selection

`moda-interact/app/services/promotions/promotion.service.ts` currently blocks a switch only when the old selected grant is still usable, the old campaign is ACTIVE/running, and the merchant is still target-eligible. This means exhaustion, closure or target loss can release the selection early.

### Merchant presentation

`moda-interact/app/routes/app/promotions/route.tsx` currently renders a selectable/reselectable action for every eligible offer and does not project the selected campaign independently of the eligible-offer query. A selected campaign that becomes CLOSED or target-ineligible may disappear from the offer catalogue even though it must continue to lock selection until expiry.

### Background cadence

`moda-interact-background/src/entrypoints/billing.ts` already runs one `BILLING_RECONCILIATION` dynamically leased cycle using the single `BackgroundRuntimeConfigSnapshot` captured for that run. It uses:

```text
billingReconciliationIntervalSeconds
billingReconciliationShopBatchSize
```

The same cycle currently performs billing reconciliation, refund correction and subscription-reconciliation reconstruction.

### Admin controls

`moda-interact-admin/src/lib/admin/background-runtime-control-validation.ts` already exposes:

```text
Reconciliation interval
billingReconciliationIntervalSeconds
```

with copy that currently describes only Shopify billing checks.

## Agreed architecture

### 1. Selection lock and spendability are separate

For a persisted `MerchantPromotionSelection`, resolve the selected campaign through:

```text
MerchantPromotionSelection
  -> PromotionalCreditGrant
  -> PromotionCampaign
```

The selection lock is exactly:

```ts
const locked = campaign.expiresAt > now;
```

No other field participates in lock release.

A selected promotion may therefore be:

```text
locked=true, spendable=true
locked=true, spendable=false because exhausted
locked=true, spendable=false because CLOSED
locked=true, spendable=false because target-ineligible
locked=false after expiry
```

### 2. Selection action is authoritative at request time

`selectPromotionOffer()` must reject every selection mutation while the current selected campaign has `expiresAt > now`, including a repeated request for the same campaign.

After the selected campaign expires, a stale selection pointer must not block selection of another currently eligible campaign. The request transaction may immediately replace the pointer before Background cleanup runs.

The requested new campaign keeps the existing eligibility requirements:

```text
status = ACTIVE
startsAt <= now
expiresAt > now
target eligible for the current shop/plan
merchant contract executable
```

### 3. Grant quantity/reuse semantics do not change

`PromotionalCreditGrant` remains unique by `(campaignId, shopId)`.

Selecting a campaign whose grant already exists reuses that grant and never replenishes:

```text
quantity
reservedQuantity
committedQuantity
exhaustedAt
```

After expiry cleanup removes the current selection pointer, a later reopened/extended eligible campaign with the same campaign ID may reuse the original remaining grant only. An exhausted grant remains exhausted.

### 4. Merchant read model projects current selection independently

Add a dedicated current-selection projection rather than inferring lock state from `getEligiblePromotionOffers()`.

The projection must expose only merchant-safe fields needed for presentation:

```ts
{
  campaignId: string;
  merchantTitle: string | null;
  expiresAt: Date;
  remainingQuantity: number;
  exhausted: boolean;
  campaignStatus: string;
  targetEligible: boolean;
  spendable: boolean;
  locked: boolean;
}
```

The UI uses `locked`, not `spendable`, to enable or disable promotion selection.

### 5. Merchant UI contract

While `promotionSelection.locked === true`:

- show a visible selection-lock notice above the offers;
- show the selected campaign title where available;
- show its expiry date;
- explain that the merchant can choose another promotion only after expiry and that using all credits early does not unlock another promotion;
- disable **all** promotion selection/reselection buttons;
- the currently selected card, when present in the eligible catalogue, shows Selected and a disabled action;
- exhausted selected promotions remain visibly locked until expiry;
- CLOSED/target-ineligible selected promotions may be absent from eligible offers but remain visible in the lock notice.

After `expiresAt <= now`, buttons are enabled according to normal requested-campaign eligibility even if the stale pointer has not been cleaned up yet.

### 6. Double-submit protection

Client-side prevention is an ergonomics layer only. Use both:

```text
synchronous useRef submission lock
React Router navigation state / disabled controls
```

All offer buttons are disabled while a promotion-selection request is in flight. The ref blocks two events occurring before React renders the disabled state.

Server authority remains `selectPromotionOffer()` under SERIALIZABLE isolation. The first successful request creates/updates the current selection; a duplicate/replay before expiry is rejected by the selection-lock rule and cannot increment selection history twice.

### 7. Background expiry reconciliation

Add a dedicated service in `moda-interact-background`:

```text
PromotionSelectionExpiryReconciliationService
```

It runs inside the existing `BILLING_RECONCILIATION` leased cycle and receives the same `BackgroundRuntimeConfigSnapshot` instance as the other cycle stages.

It selects at most:

```text
runtimeConfig.billingReconciliationShopBatchSize
```

expired selection pointers per cycle and deletes only `MerchantPromotionSelection` rows.

It must never mutate/delete:

```text
PromotionCampaign
PromotionalCreditGrant
UsageReservation
selection/grant history fields
```

### 8. Cleanup race safety

Candidate discovery alone is not authority to delete.

For every candidate, the final `deleteMany` predicate must include:

```text
selection id
shop id
promotionalCreditGrantId observed during candidate discovery
current related campaign expiresAt <= the cycle cutoff
```

If the merchant has concurrently moved the pointer to a new grant, or Admin has extended the campaign expiry beyond the cutoff, the delete affects zero rows.

This prevents stale cleanup from deleting a newer valid selection.

### 9. Same timer, no new Admin setting

The promotion cleanup stage reuses:

```text
BILLING_RECONCILIATION lease
billingReconciliationIntervalSeconds
billingReconciliationShopBatchSize
```

No new lease enum, runtime-config column, migration or scheduler is permitted.

The approved Admin copy is exactly:

> **Reconciliation interval**
>
> How often Moda performs periodic billing and entitlement reconciliation, including Shopify billing checks and expired promotion cleanup.

The timer controls eventual cleanup latency only. `PromotionCampaign.expiresAt` controls merchant selection correctness.

## Request flow

```text
merchant selects campaign A
  -> SERIALIZABLE selectPromotionOffer
  -> grant A created/reused
  -> MerchantPromotionSelection -> grant A

while A.expiresAt > now
  -> A credits may be spendable or not
  -> every selection mutation is blocked

A.expiresAt <= now
  -> request-time selection lock is false immediately
  -> merchant may select currently eligible campaign B
  -> stale A pointer may be replaced directly

existing BILLING_RECONCILIATION cycle
  -> PromotionSelectionExpiryReconciliationService
  -> delete only pointers whose current related campaign is still expired
  -> preserve all grant/history evidence
```

## Repository responsibilities

### moda-interact / moda_app

- server selection-lock semantics;
- current-selection merchant read model;
- UI lock notice and disabled states;
- double-submit protection;
- merchant-focused tests/localized copy.

### moda-interact-background / moda_background

- expired pointer cleanup service;
- same-cycle integration under existing lease/timer/config snapshot;
- race-safe compare/delete predicate;
- focused reconciliation tests.

### moda-interact-admin / moda_admin

- clarify existing runtime-control descriptions only;
- no runtime-config/schema/action change.

### moda_system_test

- terminal integrated expiry/lock/race/runtime-control verification after manual checkpoint.

## Database assessment

No database implementation task is required.

The existing schema already provides all authority required:

```text
PromotionCampaign.expiresAt
PromotionalCreditGrant.campaignId
MerchantPromotionSelection.promotionalCreditGrantId
MerchantPromotionSelection.shopId
```

The existing uniqueness constraints preserve one current selection per Shop and one grant per campaign/shop.

## Infrastructure assessment

No gateway/Render topology change is required. Promotion cleanup runs in the existing billing worker.

## Observability assessment

No new telemetry framework is required. The billing entrypoint should emit bounded structured log events for promotion-expiry cleanup result/failure using the existing shared logger. Do not add duplicate generic scheduler metrics.

## Task graph

```text
ARCH-018-SHOPIFY-001      Complete
ARCH-018-BACKGROUND-001   Ready
ARCH-018-ADMIN-001        Ready
          \                 |                 /
           \________________|________________/
                            v
ARCH-018-SYSTEM-TEST-001   Pending / manual-gated
```

No implementation task depends on the system-test task.

## Manual checkpoint

After SHOPIFY-001, BACKGROUND-001 and ADMIN-001 are accepted and integrated, the developer manually verifies the promotions page and background cleanup before explicitly starting SYSTEM-TEST-001.
