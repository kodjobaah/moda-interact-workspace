# ARCH-010 — Opt-in promotional recovery campaigns

> **Status:** Current ARCH-010 promotional-credit contract.
>
> This document supersedes the earlier ARCH-010 assumption that Moda promotional credits are pushed directly onto shops as non-expiring discretionary grants. `ARCH-010-DATABASE-009` remains the completed persistence foundation for the promotional entitlement bucket/provenance ledger; all **new** first-release promotions use the campaign + merchant opt-in model defined here and in `ARCH-010-DATABASE-010/011`.

## 1. Product rule

A promotion is an **optional merchant offer**, not an automatic credit grant.

```text
Admin creates PromotionCampaign
        ↓
GLOBAL | PLAN | SHOP targeting
        ↓
merchant sees currently-running eligible offers
        ↓
merchant chooses one offer
        ↓
one current selected promotion per Shop
        ↓
create/reuse one campaign+shop PromotionalCreditGrant
        ↓
selected promotional credits are highest-priority recovery capacity
```

Multiple promotions may run platform-wide at the same time. The exclusivity rule is **per merchant**: a Shop may have at most one currently selected promotion for new recovery admission.

## 2. Targeting scopes

Every campaign has exactly one target scope:

```text
GLOBAL
  -> available to every otherwise eligible merchant

PLAN
  -> available only while the merchant's current effective mapped BillingPlan.id
     equals targetPlanId

SHOP
  -> available only to targetShopId
```

A campaign never combines scopes. `PLAN` stores the durable `BillingPlan.id`; do not hard-code names such as `Growth` as authority.

## 3. Campaign lifecycle

Canonical durable campaign status:

```text
DRAFT
ACTIVE
CLOSED
```

A campaign is **currently running** only when:

```text
status = ACTIVE
AND startsAt <= now
AND now < expiresAt
```

Expiry is time-derived; correctness does not depend on an expiry queue firing exactly at the boundary.

After a campaign has ever been activated, its identity-defining commercial terms are immutable:

- target scope;
- target plan/shop;
- promotional-credit quantity.

Admin may close it or reopen the **same campaign ID** by supplying a new future `expiresAt`. Reopen does not clone the campaign and does not replenish a merchant who already claimed it. Every lifecycle change is appended to `PromotionCampaignEvent` so old expiry/current expiry and the acting administrator remain auditable.

## 4. Merchant selection and claim semantics

A merchant sees all currently-running campaigns for which the shop is currently eligible.

Selecting a campaign is transactional:

1. resolve current Shop/subscription/plan state;
2. prove the campaign is running and targeted to this merchant;
3. prove there is no different still-usable selected promotion;
4. create or reuse exactly one `PromotionalCreditGrant` for `(campaignId, shopId)`;
5. create/replace the shop's single `MerchantPromotionSelection` pointer;
6. never add another quantity when the same merchant reselects a reopened campaign.

`UNIQUE(campaignId, shopId)` is the exactly-once campaign claim boundary.

A merchant may select another promotion only when the current selection is no longer usable because it is:

- exhausted;
- expired;
- manually closed;
- no longer target-eligible (for example a PLAN promo after changing plan).

A previously-selected partially-used campaign may be selected again if it is later reopened and the merchant is still eligible. Only its original unused quantity becomes spendable again; reopening never grants a second allocation.

## 5. Consumption priority

A selected, running, eligible promotional grant supersedes **every other recovery-credit source**.

```text
PAID
  selected promotional
  -> current-period monthly included
  -> purchased lifetime top-ups
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

FREE
  selected promotional
  -> purchased lifetime top-ups
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

`BLOCK NEW RECOVERY ADMISSION` is only the recovery-capacity exhaustion result; it is not a dashboard/application shutdown.

Promotional-funded recoveries do not create Shopify normal-recovery meter App Events and never participate in purchased-credit refunds.

## 6. Expiry and reservation rule

A promotional grant can fund a **new** reservation only while its campaign is running and the shop remains target-eligible.

A recovery reserved before expiry/close/loss of eligibility remains protected and may commit afterward because it was already admitted. If that reservation is later released after the campaign is no longer usable, the released quantity does not become spendable until the campaign is again running and eligible.

No scheduler is required for correctness. Capacity/admission queries must evaluate campaign time/status/eligibility transactionally.

## 7. PLAN-target eligibility

PLAN-target promotions are continuously eligibility-checked for **new** recovery admission.

If the merchant changes away from the target plan:

- the historical grant remains durable;
- its unused amount is not deleted;
- it cannot fund a new recovery while the merchant is on another plan;
- the merchant may select another currently eligible promotion;
- if the merchant returns to the target plan before the campaign expires/reopens, the original remaining amount may be selected again.

## 8. History

Moda preserves two histories:

### Campaign history

All campaigns ever created remain queryable with:

- scope/target;
- quantity;
- original/current timing;
- status;
- creator;
- lifecycle events including close/reopen/expiry changes.

### Merchant promotion history

`PromotionalCreditGrant` records one merchant's one-time allocation for a campaign, including:

- quantity granted;
- reserved/committed usage;
- first/last selection;
- first/last use;
- exhaustion state.

This lets Moda answer which promotions a merchant selected/used without using aggregate entitlement counters as historical truth.

## 9. Existing DATABASE-009 compatibility

Existing `PromotionalCreditGrant` rows created under the DATABASE-009 foundation may have no campaign link. They remain historical compatibility data and must not be silently converted into a campaign or automatically selected.

After DATABASE-010/011, **new** promotional capacity is created only through a `PromotionCampaign` selected by the merchant. Admin must not use `BillingAllowanceAdjustment(FREE_RECOVERY_LIFETIME)` or a new direct lifetime promotional grant as a substitute.

## 10. Merchant lifecycle gates

Campaign ownership/selection does not bypass ARCH-010 execution gates.

`FROZEN`, `NO_CONTRACT`, inactive/uninstalled and reinstall-pending merchants may retain campaign/grant history, but cannot spend promotional capacity while business execution is disabled. Billing/dashboard surfaces may show history and preserved values according to their existing lifecycle rules.

## 11. First-release non-goals

Do not add in this feature:

- automatic merchant opt-in;
- stacking two selected promotions;
- continuous automatic enrolment of future merchants into a campaign;
- coupon codes;
- Shopify discounts;
- email/WhatsApp marketing delivery;
- campaign cloning on reopen;
- replenishing a previously-claimed campaign on reopen;
- automatic purchased-credit refunds from promo expiry;
- promo-specific Redis scheduler as a source of correctness.
