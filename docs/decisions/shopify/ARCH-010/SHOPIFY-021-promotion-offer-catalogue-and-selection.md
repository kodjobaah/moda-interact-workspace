---
id: ARCH-010-SHOPIFY-021
architecture_id: ARCH-010
title: Show eligible running promotion offers and let a merchant select one
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 84
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHOPIFY-018
- ARCH-010-ADMIN-004
enables:
- ARCH-010-SHOPIFY-020
- ARCH-010-SHOPIFY-022
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SHOPIFY-021: Show eligible running promotion offers and let a merchant select one

## Objective

Add the merchant-facing promotion offer catalogue and transactional opt-in action. A merchant sees every **currently running campaign available to that Shop** and may select one when no different still-usable promotion is already selected.

## Inspect before editing

```text
app/routes/app/**
app/services/billing/**
app/components/dashboard/**
app/i18n/locales/*.json
database/prisma/schema.prisma
tests/unit/**
```

Use current integrated merchant navigation and server-action conventions; do not expose Admin routes/components.

## 1. Eligible campaign query

For the authenticated Shop, return running campaigns where:

```text
status=ACTIVE
startsAt <= now < expiresAt
AND (
  GLOBAL
  OR SHOP targetShopId == shop.id
  OR PLAN targetPlanId == current effective mapped BillingPlan.id
)
```

Use durable local subscription/plan projection only for targeting eligibility; do not call Shopify solely to enumerate local promotion offers.

Lifecycle execution state remains separate. A FROZEN/NO_CONTRACT/inactive merchant may see preserved/history information according to existing app rules, but selection mutation must fail closed unless the current merchant contract is executable.

## 2. Catalogue presentation

Show merchant-facing campaign fields only, such as:

```text
name
merchantDescription
credit quantity
expiry
scope-appropriate friendly eligibility label when useful
remaining allocation if this campaign was previously claimed by this shop
selection/used/exhausted state
```

Do not expose:

```text
platformAdminId
internal audit/event metadata
internal target ids
requestKey
internal reason/classification
```

Localize static UI labels through the repository i18n system. Admin-authored campaign text is displayed as authored; do not invent an automatic translation pipeline in this task.

## 3. Select campaign transaction

On merchant selection:

1. authenticate exact Shopify Shop;
2. re-read campaign current state/time/target;
3. require executable merchant lifecycle state;
4. inspect current `MerchantPromotionSelection`;
5. if a different current selection is still usable and has remaining credits, return typed `ACTIVE_PROMOTION_ALREADY_SELECTED`;
6. otherwise create or reuse exactly one `(campaignId, shopId)` PromotionalCreditGrant;
7. first claim snapshots exactly `campaign.quantity` into the grant;
8. reselecting the same/reopened campaign **must not add quantity**;
9. upsert the one current MerchantPromotionSelection pointer;
10. update first/last selection timestamps/count exactly once per successful selection action under the accepted replay convention.

Use serializable/version-safe handling so two tabs selecting different promotions cannot both win.

## 4. Reselection rules

A new campaign may replace the current selection only if the old selection is no longer usable because it is:

- exhausted;
- expired;
- CLOSED;
- target-ineligible after plan change.

A partially-used campaign reopened with the same ID may be selected again and exposes only its original remaining allocation.

An exhausted campaign reopened later remains exhausted; it must not grant again.

## Required tests

At minimum prove:

1. GLOBAL/PLAN/SHOP eligible offer query;
2. wrong PLAN/SHOP target hidden/unselectable;
3. running time/status checks;
4. first selection creates one grant of exact campaign quantity;
5. duplicate/retry does not duplicate grant/quantity;
6. two-tab competing selection permits one winner;
7. still-usable selected promo prevents switching;
8. expired/closed/ineligible/exhausted selection permits another;
9. reopened partially-used campaign reuses same grant/remaining;
10. reopened exhausted campaign gets no new quantity;
11. FROZEN/NO_CONTRACT/inactive selection fails closed;
12. internal Admin metadata never serializes to merchant;
13. static copy i18n checks pass.

## Non-goals

Do not implement Background credit consumption, Admin campaign management, merchant history page, automatic enrolment, coupon codes or campaign marketing messages.

## Stop conditions

Stop if DATABASE-011 selection/grant uniqueness is unavailable or SHOPIFY-018/current local projection cannot provide a safe executable lifecycle/plan context.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
