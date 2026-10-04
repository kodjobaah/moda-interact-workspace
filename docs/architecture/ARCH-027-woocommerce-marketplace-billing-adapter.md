---
id: ARCH-027
title: WooCommerce Marketplace billing adapter
status: proposed
coordinator: moda_architect
created: 2026-10-03
updated: 2026-10-03
---

# ARCH-027: WooCommerce Marketplace billing adapter

## Status

Proposed.

This is the **living design document** for ARCH-027. It is intentionally being
refined as the billing tasks are discussed and materialised. Confirmed decisions
belong here; task-local implementation details belong in the corresponding
`docs/decisions/<domain>/ARCH-027/` task files.

Tasks currently defined are:

- `ARCH-027-DATABASE-001` — Add minimal WooCommerce billing persistence (`pending`).
- `ARCH-027-SHARED-001` — Extract deterministic merchant usage-price evaluator (`superseded` before implementation).
- `ARCH-027-API-001` — Automatically activate WooCommerce installs on the Moda Free plan (`pending`).
- `ARCH-027-API-002` — Expose Shopify-parity Woo billing presentation state (`pending`).
- `ARCH-027-API-003` — Initiate Woo recurring subscription create, switch and cancellation (`pending`).
- `ARCH-027-API-004` — Initiate Woo predefined recovery-credit charges (`pending`).
- `ARCH-027-API-005` — Accept and durably persist signed Woo billing webhooks (`pending`).
- `ARCH-027-BACKGROUND-001` — Make paid included recovery accounting WooCommerce-safe (`pending`).
- `ARCH-027-BACKGROUND-002` — Reconcile Woo recurring subscription webhook receipts (`pending`).
- `ARCH-027-BACKGROUND-003` — Roll Woo local recovery entitlement periods every 30 days (`pending`).
- `ARCH-027-BACKGROUND-004` — Reconcile Woo one-time-charge acquisition receipts (`pending`).
- `ARCH-027-BACKGROUND-005` — Prepare and reconcile Woo one-time-charge refunds (`pending`).
- `ARCH-027-API-006` — Expose Shopify-parity Woo purchase history and refund actions (`pending`).
- `ARCH-027-WOOCOMMERCE-001` — Add Woo billing hub and recurring plan management (`pending`).
- `ARCH-027-WOOCOMMERCE-002` — Add predefined recovery-credit top-up purchasing (`pending`).
- `ARCH-027-WOOCOMMERCE-003` — Add purchase history, refund request and reactivation UI (`pending`).
- `ARCH-027-ADMIN-001` — Make refund support WooCommerce-aware (`pending`).
- `ARCH-027-ADMIN-002` — Recover deterministic exceptional Woo refunds (`pending`).
- `ARCH-027-GATEWAY-001` — Wire Woo Marketplace billing runtime and webhook ingress (`pending`).
- `ARCH-027-SHOPIFY-001` — Preserve Shopify billing provider compatibility (`pending`).
- `ARCH-027-SYSTEM-TEST-001` — Validate Shopify regression and Woo billing lifecycle with local integration (`pending`, manual terminal gate).

Follow-on Background, Shopify, Admin, WooCommerce, Gateway and System-Test tasks will be added only after their exact contracts and repository boundaries have been agreed.

## Problem

Moda Interact already has a mature Shopify billing domain built around:

- `MerchantPricingPlan` and `MerchantPricingUsageEvent` commercial catalogue
  records;
- operational `BillingPlan`, `Subscription` and `BillingPeriod` projection;
- included-recovery entitlement counters and reservations;
- purchased recovery-credit lots;
- refund lifecycle and provider reconciliation.

ARCH-026 establishes the WooCommerce application, tenant/install identity,
authenticated PHP-to-Moda API boundary, shared onboarding state and shared
international context, but intentionally excludes WooCommerce Marketplace SaaS
billing and recovery-credit purchases.

ARCH-027 must add WooCommerce Marketplace billing **without replacing the current
Shopify billing architecture with a new generic billing platform** and without
creating a second Woo-specific Moda pricing catalogue.

The architectural problem is therefore to adapt a second provider edge onto the
existing Moda commercial catalogue and operational billing domain while keeping
provider-specific financial evidence at the edge.

## Goals

- Support WooCommerce Marketplace SaaS paid subscriptions using the existing
  Moda pricing catalogue.
- Preserve current Shopify hosted-pricing, usage-meter, reconciliation and
  refund behaviour unless a later explicit task changes it.
- Use the existing `MerchantPricingPlan` as the recurring-price source for both
  Shopify and WooCommerce v1.
- Use the existing `MerchantPricingUsageEvent` catalogue as the Woo top-up bundle source without creating Woo-specific pricing rows.
- Treat one Woo v1 top-up selection as one predefined, directly priced `FIXED` bundle; repeated purchases create separate purchase lots.
- Reuse the existing operational `BillingPlan` and the existing one-subscription-
  per-Shop model.
- Automatically activate a newly connected Woo Shop on the Moda Free plan before
  returning a usable installation credential.
- Grant the shop-lifetime Free recovery allocation at most once per durable Shop,
  so uninstall/reinstall or reconnect cannot mint a second Free allocation.
- Support a Woo Free Moda subscription without fabricating a zero-value Woo
  recurring contract.
- Allow a Woo Shop on the Free plan to buy configured recovery-credit top-ups
  through independent Woo one-time charges.
- Persist only the Woo workflow/provider evidence required for correctness,
  idempotency, reconciliation and recovery after process failure.
- Keep Woo vendor billing credentials inside hosted Moda infrastructure; never
  expose them to the WordPress plugin or browser.
- Accept signed Woo billing webhooks durably before applying asynchronous Moda
  business transitions.
- Reuse existing purchase-lot/refund business semantics rather than inventing a
  Woo-specific credit ledger.
- Keep the change small enough that Shopify remains recognisably the existing
  implementation rather than being rewritten around a speculative generic
  provider framework.

## Non-Goals

ARCH-027 does not introduce:

- `WooCommerceBillingOffer`;
- `MerchantPricingProviderOffer` for v1;
- a second Woo-specific `MerchantPricingPlan` catalogue;
- separate Shopify and Woo `BillingPlan` rows for the same Moda product;
- multiple Moda `Subscription` rows for one Shop;
- a new generic `BillingProvider` framework merely to make the code look
  provider-neutral;
- a replacement for `BillingPeriod`;
- a replacement for `RecoveryCreditPurchase`, `RecoveryCreditRefund`,
  `UsageEvent` or `UsageReservation`;
- billing state inside `WooCommerceInstallation`;
- Woo vendor credentials in the plugin/browser;
- automatic blind retry of ambiguous provider create requests;
- automatic proportional Woo top-up refunds until the required Woo sandbox
  capability has been proven;
- a rewrite of existing Shopify ARCH-011 plan-change behaviour as a prerequisite
  for Woo billing.

## Current Architecture

### ARCH-026 foundation

ARCH-026 establishes one shared Moda `Shop` tenant with a platform discriminator,
provider-neutral onboarding milestone, shared international context and an optional
Woo-specific installation/authentication record:

```text
commerce.Shop
    platform = SHOPIFY | WOOCOMMERCE
    onboardingCompleted
    international context
    |
    `-- 0..1 woocommerce.WooCommerceInstallation
            installation/authentication identity only
```

`WooCommerceInstallation` answers **which WordPress/Woo installation is allowed to
act for the Shop**. It is not the Shop's billing subscription and must not become a
billing-state container.

ARCH-026 also establishes the hosted `moda-interact-api` boundary and the
installation credential used by the PHP plugin to authenticate requests. ARCH-027
must reuse that authenticated principal to resolve `shopId`; billing endpoints must
not accept a browser/plugin-selected tenant ID as authority.

### Existing Shopify billing activation

The existing Shopify flow establishes the reference mapping pattern:

```text
Shopify callback intent
    -> verify active provider subscription
    -> verified plan_handle
    -> MerchantPricingPlan.shopifyPlanHandle
    -> resolve/materialise BillingPlan
    -> update the Shop's Subscription/BillingPeriod projection
```

Provider verification, not the browser return alone, is the entitlement authority.

### Existing commercial catalogue

The existing catalogue already owns the product economics required by Woo:

```text
MerchantPricingPlan
    recurringAmountMinor
    currency
    billingPeriod
    includedRecoveryCredits
    features
    shopifyPlanHandle

MerchantPricingUsageEvent
    creditsGrantedPerUnit
    pricingMode = FIXED | GRADUATED | VOLUME
    currency
    fixedUnitAmountMinor / tiers
    maximumUnitsPerBillingPeriod
```

The catalogue supports richer Admin economics, but ARCH-027 Woo v1 deliberately consumes only predefined, directly priced bundles: `pricingMode = FIXED` with non-null `fixedUnitAmountMinor`. `creditsGrantedPerUnit` is the bundle credit grant and `fixedUnitAmountMinor` / `currency` are the authoritative retail price. Woo does not reevaluate `GRADUATED` / `VOLUME` schedules at purchase time.

### Existing subscription cardinality

The current schema enforces:

```text
Shop 1 -> 0..1 Subscription
```

through unique `Subscription.shopId`.

ARCH-027 preserves that cardinality. Woo provider contracts are external financial
identities associated with operations and the current subscription projection; they
are not additional Moda subscriptions.

## Proposed Architecture

ARCH-027 adds a **thin Woo billing provider edge** over the existing Moda catalogue
and operational billing domain.

```text
                         MODA COMMERCIAL CATALOGUE

                      MerchantPricingPlan
                     /                   \
                    /                     \
     Shopify verified handle        Woo trusted plan id
              |                            |
              v                            v
      Shopify billing edge          Woo billing adapter
              |                            |
              +-------------+--------------+
                            |
                            v
                 existing/materialised
                       BillingPlan
                            |
                            v
                       Subscription
                            |
                            v
                 existing entitlement /
                 purchase/refund domain
```

Provider-specific payment mechanics remain at the edges:

```text
Shopify
    hosted App Pricing
    Partner API subscription evidence
    App Events / usage meter

WooCommerce
    SaaS Billing /subscriptions
    SaaS Billing /charges
    Woo contract UUIDs
    signed lifecycle webhooks
```

Both edges converge on the existing Moda business records only after trusted
provider evidence has been established.

## Core Decisions

### 1. One Moda commercial catalogue

`MerchantPricingPlan` remains the recurring commercial definition.

`MerchantPricingUsageEvent` remains the Woo top-up bundle definition. `MerchantPricingUsageTier` remains part of the existing catalogue/Admin economics model but is not interpreted by Woo v1.

Woo v1 does not get a second price table. A Woo plan selection therefore carries a trusted opaque `MerchantPricingPlan.id`; a top-up selection carries one trusted opaque `MerchantPricingUsageEvent.id`. One selected event means one predefined bundle purchase.

The hosted API must reload and validate these rows server-side. For a Woo-v1 top-up it must require `pricingMode = FIXED`, read the persisted `fixedUnitAmountMinor` and `currency`, and snapshot that exact stored amount before the provider request. Browser/plugin price values are display data only and are never authoritative provider charge inputs. `GRADUATED` / `VOLUME` price schedules are not runtime Woo charge inputs.

### 2. Provider-specific plan mapping, shared BillingPlan materialisation

Shopify retains:

```text
verified shopifyPlanHandle
    -> MerchantPricingPlan
    -> BillingPlan
```

Woo uses:

```text
verified Woo operation/provider evidence
    -> captured merchantPricingPlanId
    -> MerchantPricingPlan
    -> same BillingPlan materialisation semantics
```

Whether Shopify or Woo causes a plan to be materialised first must not create two
operational `BillingPlan` rows for the same Moda commercial plan.

Source review for BACKGROUND-002 exposed one additional durability requirement.

`WooCommerceBillingOperation` freezes provider pricing but not every feature/allowance field that becomes part of the operational BillingPlan snapshot. API-003 must therefore reuse/generalise API-001's bounded BillingPlan resolver and resolve/reuse/materialise the selected paid operational BillingPlan **before provider I/O**.

This does not activate merchant entitlement. API-003 still leaves Subscription/BillingPeriod/counters untouched until verified provider evidence.

After a trusted `activated` / `updated` receipt, BACKGROUND-002 resolves:

```text
operation.merchantPricingPlanId
    -> MerchantPricingPlan.shopifyPlanHandle
    -> already-materialised BillingPlan.shopifyPlanHandle
```

and only then updates the Shop's existing unique Subscription.

Whether Shopify or Woo materialises a plan first still converges on one operational BillingPlan through the existing unique current-schema bridge.

### 3. One Moda subscription per Shop

Woo does not introduce another subscription model.

```text
Shop
    `-- 0..1 Subscription
```

A Shop may accumulate many historical Woo billing operations and provider contract
references while still having only one current Moda `Subscription` row.

`WooCommerceBillingOperation` therefore does not contain a `subscriptionId`
foreign key. Subscription-affecting operations are scoped by `shopId` and later
software resolves the Shop's unique current `Subscription`.

### 4. Woo contract identity is provider-owned evidence

`providerContractId` is a WooCommerce.com external billing-contract UUID/reference.
It is not:

```text
Shop.id
WooCommerceInstallation.id
Subscription.id
MerchantPricingPlan.id
merchant/customer identity
```

Its meaning depends on the operation:

```text
SUBSCRIPTION_CREATE
    newly created Woo recurring subscription contract

PLAN_SWITCH
    existing Woo recurring subscription contract being changed

CANCEL
    existing Woo recurring subscription contract being cancelled

ONE_TIME_CHARGE
    Woo one-time charge contract
```

After verified recurring activation/reconciliation, the current recurring Woo
contract may be projected to `Subscription.providerSubscriptionId`.

A one-time charge contract must never be copied to
`Subscription.providerSubscriptionId`; it belongs to the billing operation and
corresponding `RecoveryCreditPurchase` provider evidence.

### 5. Woo installation automatically activates the local Free subscription once

A successful first Woo installation connection does not stop at installation/authentication state. After ARCH-026 site-control proof succeeds, ARCH-027 extends the same connection transaction so the merchant enters Moda already on the Free plan.

The first committed Woo connection establishes:

```text
Shop
    platform = WOOCOMMERCE
    onboardingCompleted = true

Subscription
    plan = Free BillingPlan
    status = ACTIVE
    providerSubscriptionId = NULL
    billingPeriodId = NULL

ShopEntitlementCounter
    counter = LIFETIME_FREE_RECOVERY_CREDITS
    granted once for the lifetime of this Shop
```

Free activation is local Moda state and must not manufacture a zero-value Woo
`SUBSCRIPTION_CREATE` operation or provider contract.

Lifetime Free credits belong to the durable `Shop`, not to a plugin installation instance. The accepted ARCH-026 reconnect path reuses the same Shop for the same canonical Woo site. Therefore:

```text
first install/connect
    -> one lifetime Free allocation

uninstall / revoke installation
reinstall / reconnect same Shop
    -> preserve existing Subscription
    -> preserve granted/committed/reserved/refunding quantities exactly
    -> no second Free allocation
```

`Shop.onboardingCompleted=true` is a monotonic replay guard, and the unique lifetime Free entitlement counter is the durable grant record. Reconnect of an already-onboarded Free or paid merchant is a billing/entitlement no-op; it must never force the merchant back to Free.

The absence of a Woo recurring contract does **not** prevent recovery-credit
purchases. A Free merchant may buy any top-up configured for the current Free plan:

```text
Free Moda Subscription
    providerSubscriptionId = NULL
        |
        v
MerchantPricingUsageEvent belonging to Free
        |
        v
WooCommerceBillingOperation(kind = ONE_TIME_CHARGE)
        |
        v
Woo /charges
        |
        v
Woo charge contract UUID
        |
        v
RecoveryCreditPurchase provider evidence
```

The Shop remains on one Free Moda subscription throughout that flow unless a
separate verified plan change occurs.

### 6. Paid Woo activation requires provider verification

Creating a Woo subscription and receiving a confirmation URL is intent/provider
workflow state, not entitlement proof.

```text
merchant chooses paid Moda plan
    -> API validates MerchantPricingPlan and Woo compatibility
    -> persist WooCommerceBillingOperation(INITIATING)
    -> POST Woo /subscriptions
    -> store returned recurring contract UUID + confirmation URL
    -> merchant confirms on WooCommerce.com
    -> verified signed provider evidence
    -> resolve/materialise BillingPlan
    -> activate/update the Shop's one Subscription
    -> complete onboarding when applicable
```

A browser `return_url` may improve UX but must not independently activate paid
entitlements.

### 7. Woo plan switch changes the existing subscription

A Woo plan switch acts on the current recurring Woo contract and changes the
Shop's existing Moda subscription projection after verification:

```text
existing Subscription(plan = Starter)
    providerSubscriptionId = woo-recurring-123
        |
        v
PLAN_SWITCH operation
    shopId
    providerContractId = woo-recurring-123
    merchantPricingPlanId = Growth
        |
        v
verified provider switch
        |
        v
same Subscription row
    plan = Growth BillingPlan
    providerSubscriptionId = woo-recurring-123
```

No second Moda subscription is created.

### 8. Current-period usage does not reset for Woo plan switches

ARCH-027 adds a nullable mutable allowance ceiling to the existing entitlement
counter:

```text
currentAllowanceQuantity ?? grantedQuantity
```

Availability becomes conceptually:

```text
available = max(
    currentAllowanceQuantity
      - committedQuantity
      - reservedQuantity,
    0
)
```

for rows with an explicit current allowance, while legacy/current Shopify rows may
continue to use `grantedQuantity` when the override is null.

For Woo:

```text
upgrade
    current allowance increases
    committed unchanged
    reserved unchanged
    BillingPeriod unchanged

downgrade
    current allowance may decrease below already-consumed usage
    committed unchanged
    reserved unchanged
    no clawback
    available floors at zero
```

`grantedQuantity` remains cumulative/audit grant evidence; the mutable allowance
ceiling has a different job and must not invalidate historical usage.

### 8A. Paid included usage must be provider-aware before Woo paid activation

The current Background paid included-recovery path is Shopify-shaped: it requires a Shopify normal-usage event handle and creates `UsageEvent` rows in `PENDING` Shopify report state.

ARCH-027 must correct that **before** a Woo paid subscription can safely become active.

`ARCH-027-BACKGROUND-001` keeps one shared Moda counter/reservation path and dispatches only the external reporting evidence:

```text
SHOPIFY Shop
    -> provider = SHOPIFY
    -> shopifyReportState = PENDING
    -> existing App Event publisher unchanged

WOOCOMMERCE Shop
    -> provider = WOOCOMMERCE
    -> shopifyReportState = NOT_APPLICABLE
    -> no Shopify event handle/idempotency key
    -> local usage accounting only
```

The same task makes new-reservation admission consume:

```text
currentAllowanceQuantity ?? grantedQuantity
```

while preserving `grantedQuantity` as the non-decreasing high-water/audit grant. Existing reservations survive a downgrade and may still commit/release; the lower current allowance gates only new reservation admission.

This capacity/accounting task deliberately precedes the Woo subscription receipt task so provider verification cannot activate a paid Woo merchant into a Shopify-only usage-reporting path.

### 8B. Woo recurring receipts project provider lifecycle but do not drive local allowance cadence

`ARCH-027-BACKGROUND-002` consumes provider-shaped `subscription` receipts from PostgreSQL and correlates `providerContractId` only through trusted Moda operations/current Subscription state.

Its recurring projection is:

```text
activated          Free -> paid; confirm create; open first local 30-day period
updated            confirm one pending switch; same period; change current allowance only
renewed            active/unfreeze evidence; NO local period reset
paused             FROZEN; preserve plan/period/credits
canceled           cancelAtPeriodEnd=true; preserve prepaid access
refunded           scheduled-cancellation evidence only
prepaid_term_ended close paid period; same Subscription -> existing local Free
```

The first paid local period is anchored at the durable activated receipt time for exactly 30 days.

Woo `next_payment_date` and proration-adjusted provider dates do not reset Moda recovery allowance. A separate Background task owns periodic local `EVERY_30_DAYS` rollover.

### 8C. Woo local recovery periods roll from durable Moda boundaries, not provider dates

`ARCH-027-BACKGROUND-003` owns the time-driven local cadence.

Eligible state is an ACTIVE Woo paid Subscription whose current local `BillingPeriod.periodEnd <= now`. It runs from the existing leased billing cycle **after** BACKGROUND-002 provider receipt reconciliation.

Each successor is derived only from the previous durable period:

```text
successorStart = current periodEnd
successorEnd   = successorStart + exactly 30 days
```

A Woo `renewed` webhook never defines these boundaries.

Closing an expired period reuses the existing Moda high-water close invariant:

```text
release RESERVED/AMBIGUOUS
forfeit grant - committed - forfeited
close against grantedQuantity
```

The lower mutable `currentAllowanceQuantity` is not used to rewrite historical grant evidence.

A mid-period Woo plan switch means the expiring period may retain an old opening-plan snapshot while `Subscription.planId` points to the new plan. The successor always snapshots the **current** Subscription plan and its configured allowance.

Worker downtime/FROZEN intervals use bounded catch-up:

```text
max 12 period transitions per Subscription per transaction
```

Skipped full periods are durably represented and fully forfeit unused included allowance. If 12 transitions are insufficient, the newest current period may remain expired and `EXPIRED_RECONCILING`; no recovery-capacity resume occurs until a later cycle reaches a live period.

FROZEN does not roll or grant periods. Once verified renewal makes the Subscription ACTIVE, catch-up resumes from the original cadence. `cancelAtPeriodEnd=true` does not stop local cadence while prepaid access remains ACTIVE; `prepaid_term_ended` is processed first in the same leased cycle and prevents a successor from being created.

### 9. Woo top-ups reuse the existing purchase-lot model

A Woo top-up does not require a recurring Woo subscription contract.

For ARCH-027 Woo v1, one merchant selection is one predefined credit bundle. The hosted API must:

1. authenticate the Woo installation and resolve `shopId`;
2. load the Shop's current Moda `Subscription`/plan;
3. load the selected `MerchantPricingUsageEvent`;
4. prove that event belongs to the current plan;
5. require `pricingMode = FIXED` and a non-null positive `fixedUnitAmountMinor`;
6. enforce plan/event currency consistency and the Woo v1 provider-currency restriction;
7. use `fixedUnitAmountMinor` / `currency` as the authoritative stored retail price;
8. create `RecoveryCreditPurchase(REQUESTED)` for `creditsGrantedPerUnit`;
9. persist `WooCommerceBillingOperation(kind = ONE_TIME_CHARGE)` with the selected event and exact stored quote before calling Woo;
10. create one Woo `/charges` contract;
11. activate that purchase lot only after verified provider evidence.

There is no requested purchase quantity and no runtime FIXED/GRADUATED/VOLUME evaluator in the Woo adapter. If a merchant buys the same bundle again, that is a new request key, a new Woo charge operation/contract and a new `RecoveryCreditPurchase` lot.

### 9A. Verified Woo charge activation converges on the existing purchase-lot ledger

`ARCH-027-BACKGROUND-004` consumes only charge acquisition lifecycle receipts:

```text
activated
canceled
prepaid_term_ended
```

`refunded` remains a later refund-specific task.

A verified `activated` charge resolves exactly one `ONE_TIME_CHARGE` operation and linked REQUESTED purchase, then atomically:

```text
purchase -> ACTIVE
currentAmount = creditsGranted
providerReference = Woo charge contract
providerPurchaseAmount = observed provider transaction amount
providerPurchaseCurrency = USD
providerPriceSnapshot = frozen quote + provider transaction evidence

PURCHASED_RECOVERY_CREDITS.grantedQuantity += creditsGranted

operation -> CONFIRMED
receipt -> processed
```

No purchase-acquisition UsageEvent is created.

Woo may add tax on top of Moda's original price. `quotedAmountMinor` remains the immutable pre-tax Moda price sent to Woo; the signed transaction total is stored separately as provider settlement evidence and is not required to equal the quote.

For an unconfirmed charge, `canceled` / `prepaid_term_ended` makes the operation terminal FAILED and leaves the zero-value REQUESTED purchase as historical intent so bundle checkout no longer remains blocked.

For an already ACTIVE purchase, canceled/prepaid-term-ended is a no-op: credits are not revoked without a later `refunded` receipt and the separate refund business workflow.


Once activated, purchased credits enter the existing reservation/consumption path. Woo must not create a fake Shopify purchase-acquisition `UsageEvent` merely to satisfy old Shopify evidence requirements.

### 10. No new Shared billing runtime contract for Woo v1

`ARCH-027-SHARED-001` was defined before the predefined-bundle purchase semantics were clarified. It is superseded before implementation.

Admin retains its existing portfolio-economics arithmetic, including FIXED/GRADUATED/VOLUME calculations where that Admin workflow needs them. Woo v1 does not share or duplicate that arithmetic because it consumes the already persisted price of a predefined FIXED bundle.

ARCH-027 also does not introduce a separately versioned Shared Woo lifecycle event for webhook processing. The accepted cross-repository handoff is the provider-specific durable `WooCommerceBillingWebhookReceipt` in PostgreSQL: API authenticates and stores the signed Woo provider payload; Background later claims that receipt and applies Woo-specific semantics to the existing Moda billing domain.

### 11. Woo operation state is durable before provider POST

Woo create/charge calls may produce an ambiguous result if the provider accepted
an operation but Moda lost the response.

ARCH-027 therefore persists `WooCommerceBillingOperation` before sending a create
request.

The operation state model includes:

```text
INITIATING
AWAITING_CONFIRMATION
CONFIRMED
OUTCOME_UNKNOWN
FAILED
```

A network timeout after send is not interpreted as proof that Woo did not create
the contract. The operation moves to `OUTCOME_UNKNOWN`; the system must reconcile
or require explicit operational investigation rather than blindly creating a
second provider contract.

### 12. Request identity and contract identity are immutable workflow evidence

Each Woo billing command has an application-owned request key and deterministic
request fingerprint. The request key supports same-command idempotency; the
fingerprint proves that reuse of the same key refers to the same canonical intent.

The fingerprint itself is not globally unique because two legitimate top-ups may
have identical plan/event/price intent under different request keys.

Once a provider contract ID becomes known for an operation, it is write-once
provider evidence. A switch/cancel operation snapshots the recurring contract it
acts on and cannot later be redirected to another provider contract.

### 13. Signed webhook receipt is a durable acceptance boundary

Woo lifecycle webhooks are accepted by `moda-interact-api`:

```text
raw HTTP body
    -> 256 KiB / JSON transport bounds
    -> verify Base64 HMAC-SHA256 over exact raw body using WOO_BILLING_API_SECRET
    -> validate the exact supported Woo SaaS Billing topic allowlist
    -> require one provider `subscription` or `charge` contract wrapper
    -> persist provider-shaped WooCommerceBillingWebhookReceipt
    -> acknowledge provider with 204 only after commit
```

Business reconciliation occurs after durable receipt acceptance.

Receipt deduplication must not depend on nullable `providerContractId`. The current
DATABASE-001 contract deduplicates exact deliveries by:

```text
(topic, payloadSha256)
```

Background reconciliation must remain idempotent even when semantically equivalent
but byte-distinct provider deliveries produce distinct receipts.

ARCH-027-API-005 does not resolve a Shop or mutate billing state on the webhook request path. Woo webhooks intentionally omit merchant identity; `providerContractId` is stored as external provider evidence and tenant/business correlation is deferred to Background. The receipt JSON remains Woo provider-shaped rather than being mapped to a new Shared lifecycle enum.

The ARCH-027 v1 API -> Background transport is PostgreSQL itself. Background will later claim unprocessed receipts (`processedAt IS NULL`) using bounded row-locking/claim semantics consistent with the existing reconciliation patterns; API-005 does not publish BullMQ/Redis/outbox work.

### 14. Refund business semantics remain purchase-lot based

The existing business rule is retained:

```text
refundableCredits = currentAmount - reservedAmount
```

A refund concerns one exact `RecoveryCreditPurchase` lot. Consumed credits are not
restored and reserved credits cannot be refunded until they settle/release.

Shopify keeps its existing provider-correction mechanics. Woo stores Woo-specific
provider settlement/reference evidence while reusing the generic
`RecoveryCreditRefund` lifecycle.

Automatic arbitrary partial Woo one-time-charge refund initiation remains an
external sandbox capability gate. If the provider cannot safely execute the exact
proportional refund, Moda must not fabricate provider settlement; the existing
manual/provider-action-required style of workflow remains the safe fallback.


`ARCH-027-BACKGROUND-005` now fixes that provider-action-required flow:

```text
local Woo refund hold
    -> wait until reserved credits settle/release
    -> freeze finalCreditQuantity
    -> expectedProviderAmount =
         providerPurchaseAmountSnapshot
         * finalCreditQuantity / purchaseCreditsGranted
    -> PROVIDER_ACTION_REQUIRED
    -> vendor/admin performs refund in Woo SaaS Pending Refunds dashboard
    -> signed `refunded` charge receipt
```

Exact provider amount match completes the existing refund business state:

```text
purchase -> REFUNDED
purchased granted/refunding quantities reduced
refund -> COMPLETED
```

Provider amount mismatch is not coerced into a different credit quantity. The actual provider evidence is frozen and the refund moves to `NEEDS_ATTENTION` for operator resolution.

A provider refund with no existing local Moda refund hold is intentionally not converted into an invented refund row. The receipt remains unprocessed until a future Admin/support recovery path explicitly reconciles that exceptional external action.

For Woo Free top-ups, `RecoveryCreditRefund.billingPeriodIdSnapshot` may be null; Shopify refund provenance remains non-null.


`ARCH-027-ADMIN-001` establishes the support boundary before any exceptional recovery mutation exists:

```text
normal Woo PROVIDER_ACTION_REQUIRED
    -> show expected refund evidence
    -> tell operator to use Woo SaaS Pending Refunds
    -> NO generic Admin manual-settlement form
    -> signed webhook remains authoritative

Woo NEEDS_ATTENTION
    -> show expected vs observed provider evidence
    -> keep credits held
    -> NO speculative completion

unmatched refunded receipt
    -> show bounded WOO_REFUND receipt evidence
    -> correlate operation/purchase when unique
    -> NO invented RecoveryCreditRefund
    -> NO credit/counter mutation
```

The current Shopify manual provider-evidence action is explicitly guarded as `provider=SHOPIFY` server-side. This prevents a crafted Admin action from bypassing the Woo webhook settlement path.

`ARCH-027-ADMIN-002` proves the exact safe accounting transitions for the two recoverable exception classes above.

BACKGROUND-005 also treats Woo `amount_refunded` as cumulative transaction evidence. A NEEDS_ATTENTION under-refund may progress monotonically: a later exact cumulative amount completes normally; a later still-mismatched increase refreshes evidence; a decrease conflicts; an over-refund remains attention state for explicit ADMIN-002 acceptance.

### 15. Shopify is the reference merchant billing experience

The WooCommerce application must reproduce the existing Shopify merchant billing experience rather than invent a separate Woo product UX. Provider mechanics differ, but the merchant-facing product concepts remain the same.

The current Shopify reference surfaces include:

```text
current plan summary
recovery-capacity balances
Add top-up / Change plan navigation
predefined top-up bundle cards
pending purchase state
current and pending plan presentation
scheduled cancellation presentation
usage-history availability
purchase-history availability
```

The hosted Woo API exposes provider-neutral presentation state using opaque Moda catalogue identifiers:

```text
MerchantPricingPlan.id
MerchantPricingUsageEvent.id
```

It must not expose Shopify plan/event handles merely because the current operational BillingPlan materialisation still uses them internally.

Woo read paths are based on durable Moda state and must not call WooCommerce.com synchronously to render merchant billing pages. Provider verification enters the durable projection through the later signed webhook/reconciliation path.

Woo initial acquisition differs deliberately from Shopify: successful first Woo connection automatically activates the local Free plan. From that point onward, current plan, capacity, top-up, plan-change and billing-history experiences should match Shopify's product semantics.

`ARCH-027-API-002` owns the first read-only HTTP projection of this parity contract. It exposes the billing hub plus selectable plan catalogue without implementing any billing command.


`ARCH-027-API-006` owns the purchase-history/refund-management portion of the same Shopify-parity contract:

```text
GET  /v1/billing/recovery-credit-purchases
POST /v1/billing/recovery-credit-refunds
POST /v1/billing/recovery-credit-refunds/reactivate
```

It preserves the Shopify merchant experience:

```text
ACTIVE | WITHDRAWN | COMPLETED | REFUNDED | ALL
5 / 10 / 20 page sizes
batch refund selection up to 20
independent per-purchase outcomes
reactivation only before provider action begins
```

but uses Woo purchase-local provider evidence rather than Shopify current-meter context. Historical Woo one-time-charge lots may remain refundable after plan/cycle changes when they still have unused/unreserved credits and valid provider purchase evidence.

The local refund request ends after the durable hold commits. BACKGROUND-005 later freezes provider economics and reconciles the Woo vendor-dashboard refund asynchronously.


`ARCH-027-WOOCOMMERCE-001` materialises the first Woo billing UI slice against API-002/API-003. It adds a real Billing destination to the accepted ARCH-026 Woo Admin shell and implements current plan/capacity, plan catalogue, create/switch/cancel, provider confirmation redirect and return-state refresh.

To make cancellation status durable across a browser reload, API-002 also exposes a bounded `pendingCancellation` projection. A provider-accepted API-003 cancel may be `CONFIRMED` before BACKGROUND-002 records `Subscription.cancelAtPeriodEnd`; the UI must show that lag rather than briefly presenting cancellation as absent.


`ARCH-027-WOOCOMMERCE-002` adds predefined top-up purchase controls to that same Billing surface. It consumes API-002's current-plan bundles and API-004's one-bundle/one-charge command through the existing browser -> WordPress REST -> PHP Moda client boundary.

The UI has no quantity control. One Buy click sends only the opaque `merchantPricingUsageEventId`; the hosted API remains authoritative for bundle ownership, credits and stored USD price. Successful command initiation redirects the top-level browser to Woo. On return, the existing Billing refresh shows durable pending/activated state; browser return never grants credits.

Per-offer pending state is deterministic: an unresolved purchase disables only its matching bundle with `unavailableReason=PENDING_PURCHASE`. Global billing-state/cancellation restrictions use `topUps.purchaseEligible=false`; they do not invent additional per-offer reason codes.


`ARCH-027-WOOCOMMERCE-003` completes the purchased-credit management UI inside the same Billing surface. It adds a real Purchased credits internal view using API-006 for versioned history, current-page selection, bounded batch refund holds and strictly pre-provider reactivation.

The UI does not calculate refund quantities or provider money. It renders API-computed `refundEligible`, `refundUnavailableReason`, `reactivationAvailable` and `providerActionStarted` fields. A refund request produces only the local `RecoveryCreditRefund(REQUESTED)` hold; BACKGROUND-005 owns preparation/provider settlement.

Selection intentionally mirrors the current Shopify manager: only eligible purchases on the current visible page are selectable, `Select all` is page-local, and the 20-row maximum page size naturally bounds one batch to API-006's 20-purchase limit.

Provider-action and attention states are presentation-only in the plugin:

```text
REQUESTED               -> reactivation may still be available
PROVIDER_ACTION_REQUIRED -> provider processing; no reactivation
NEEDS_ATTENTION         -> support review; no reactivation
COMPLETED               -> completed history
```

No provider/internal identifiers are exposed to React.

### 16. Recurring Woo commands persist intent before provider writes

`ARCH-027-API-003` owns exactly three authenticated recurring-provider commands:

```text
POST   /v1/billing/subscription
POST   /v1/billing/subscription/switch
DELETE /v1/billing/subscription
```

Create is only local Free -> paid. Switch is only existing paid recurring contract -> another paid Moda catalogue plan. A paid merchant selecting Free uses cancellation semantics; the current paid plan remains effective until verified provider lifecycle evidence reaches the prepaid-term end.

Every provider write requires a per-Shop `Idempotency-Key`, persists `WooCommerceBillingOperation(INITIATING)` before network I/O, and snapshots the exact catalogue quote. The Woo retail amount is the stored Moda recurring amount with no provider-specific markup, discount or FX conversion.

The current Moda `EVERY_30_DAYS` recurring product maps to Woo financial billing as `billing_period=month`, `billing_interval=1`. Woo owns provider financial proration and renewal-date movement; those provider dates do not synchronously reset Moda recovery allowance or usage.

Create/switch return a validated Woo `confirmationUrl` and leave the operation `AWAITING_CONFIRMATION`. Browser return is UX only. Paid activation/change occurs only after verified lifecycle evidence. Cancellation may be acknowledged as a provider command without immediately ending prepaid Moda entitlement.

Provider return URLs are derived server-side from the authenticated canonical Woo site and the accepted Woo Admin route; the WordPress/browser caller cannot supply an arbitrary return origin.

### 17. Woo predefined top-up command creates one durable purchase lot per charge

`ARCH-027-API-004` owns exactly one authenticated one-time-charge command:

```text
POST /v1/billing/recovery-credit-purchases
```

The request contains one opaque `MerchantPricingUsageEvent.id` and no quantity. The selected event must belong to the Shop's current Moda catalogue plan and be a directly priced `FIXED` bundle.

The API snapshots:

```text
creditsGranted      = creditsGrantedPerUnit
quotedAmountMinor   = fixedUnitAmountMinor
quotedCurrency      = event currency
```

and atomically persists one REQUESTED `RecoveryCreditPurchase` plus one INITIATING `ONE_TIME_CHARGE` operation before calling Woo `/charges`.

A Woo Free merchant remains eligible without a recurring provider contract or BillingPeriod:

```text
Subscription.plan = Free
Subscription.providerSubscriptionId = NULL
Subscription.billingPeriodId = NULL

RecoveryCreditPurchase.billingPeriodId = NULL
```

For paid Woo acquisition, the purchase snapshots the current OPEN Moda BillingPeriod.

`maximumUnitsPerBillingPeriod` is not enforced as a Woo-only runtime gate in ARCH-027 v1 because the current Shopify purchase command does not enforce it. A future runtime cap must be cross-platform.

Definite provider rejection may leave a REQUESTED purchase linked to a `FAILED` operation as historical command intent; that row is not treated as an unresolved checkout and does not block a deliberate new attempt with a new idempotency key. `OUTCOME_UNKNOWN` remains blocking because an external charge may exist.

## Request / Event Flows

### Woo installation / automatic Free activation

```text
plugin install
    -> ARCH-026 connection handshake
    -> hosted API proves control of canonical Woo site
    -> begin connection transaction
    -> create/reconnect the durable Shop + WooCommerceInstallation
    -> if Shop.onboardingCompleted = false and Subscription is absent/empty
         -> resolve exactly one active Free MerchantPricingPlan
         -> reuse/materialise the operational Free BillingPlan
         -> establish the Shop's one ACTIVE Free Subscription
         -> providerSubscriptionId = NULL
         -> no BillingPeriod
         -> create lifetime Free counter only if it does not already exist
         -> set Shop.onboardingCompleted = true
    -> if Shop.onboardingCompleted = true
         -> preserve all billing/entitlement state unchanged
    -> commit
    -> return installation credential
```

If initial Free activation fails, the first connection transaction rolls back and no usable new installation credential is returned. No Woo recurring billing operation is created.

Uninstall/reinstall or credential reconnection for the same durable Shop cannot recreate or reset lifetime Free credits.

### Woo paid subscription activation

```text
Woo Admin UI
    -> PHP plugin
    -> authenticated Moda API
    -> validate active paid MerchantPricingPlan by opaque Moda id
    -> resolve/reuse/materialise target operational BillingPlan (no Subscription mutation)
    -> require exact stored USD recurring quote / EVERY_30_DAYS
    -> persist SUBSCRIPTION_CREATE operation + idempotency fingerprint + exact quote
    -> commit operation before provider network call
    -> Woo POST /subscriptions (month, interval 1)
    -> persist recurring contract UUID + validated confirmation URL
    -> merchant confirms on WooCommerce.com
    -> signed webhook / verified provider evidence
    -> durable receipt
    -> BACKGROUND-002 recurring receipt reconciliation
    -> operation target -> already-materialised BillingPlan
    -> activate the Shop's one Subscription
    -> open first local 30-day BillingPeriod
```

### Woo plan switch

```text
current paid Shop Subscription
    -> target paid MerchantPricingPlan.id
    -> resolve/reuse/materialise target operational BillingPlan (no Subscription mutation)
    -> persist PLAN_SWITCH operation + exact target quote against current recurring Woo contract
    -> commit before provider network call
    -> Woo POST /subscriptions/{contractID}
    -> merchant confirms switch / provider proration on WooCommerce.com
    -> verified provider evidence
    -> same Subscription row receives target BillingPlan
    -> current allowance ceiling changes
    -> committed/reserved usage remains unchanged
```

### Woo top-up purchase

```text
current Free or Paid Moda Subscription
    -> selected predefined MerchantPricingUsageEvent.id
    -> validate current-plan ownership
    -> require FIXED + stored fixedUnitAmountMinor/currency
    -> Free: purchase billingPeriodId = NULL
       Paid: purchase billingPeriodId = current OPEN BillingPeriod
    -> atomically persist RecoveryCreditPurchase(REQUESTED)
       + ONE_TIME_CHARGE(INITIATING)
    -> commit before provider I/O
    -> Woo POST /charges with no quantity parameter
    -> persist returned charge contract + confirmation URL
    -> merchant confirmation
    -> signed provider evidence
    -> later Background activates purchase

repeat the same resolved bundle
    -> new request / new charge / new RecoveryCreditPurchase lot
```

One unresolved purchase blocks only that selected bundle. A different eligible bundle may remain purchasable. A `FAILED` initiation is terminal and is not treated as unresolved; `OUTCOME_UNKNOWN` remains blocking until reconciled.

### Woo cancellation

```text
current provider-backed paid Subscription
    -> persist CANCEL operation against current recurring Woo contract
    -> commit before provider network call
    -> Woo DELETE subscription contract
    -> provider command accepted without immediate Moda plan change
    -> verified lifecycle evidence
    -> preserve paid access until provider effective/prepaid end where applicable
    -> eventual existing Free fallback
    -> never reset onboarding
```

## Repository Responsibilities

### `moda-interact-database` / `moda_database`

Owns schema/migrations and database-level integrity for the minimal Woo billing
persistence delta.

`ARCH-027-DATABASE-001` creates:

```text
woocommerce.WooCommerceBillingOperation
woocommerce.WooCommerceBillingWebhookReceipt
```

and minimally extends:

```text
BillingPeriodEntitlementCounter
Subscription lookup/indexing where required
RecoveryCreditPurchase
RecoveryCreditRefund
```

It must not create a second commercial catalogue or put billing state into
`WooCommerceInstallation`.

### `moda-interact-shared` / `moda_shared`

No new ARCH-027 runtime billing contract is currently required in Shared.

`ARCH-027-SHARED-001` (usage-price evaluator) is superseded and must not be implemented. API-005 persists the signed Woo provider payload into the provider-specific database receipt and Background consumes that durable provider contract directly. Existing Shared logging/observability utilities continue to be reused.

### `moda-interact-api` / `moda_api`

Will own:

- authenticated Woo billing read models/commands;
- provider-currency compatibility checks;
- Woo vendor billing client and secrets;
- recurring subscription create/switch/cancel requests through `ARCH-027-API-003` with durable idempotent operation intent before provider writes;
- server-derived Woo return URLs and bounded Woo sandbox/production provider client configuration;
- one-time predefined-bundle top-up charge requests through `ARCH-027-API-004`, using the persisted FIXED price and no quantity parameter;
- exact stored-price quote snapshot creation;
- signed Woo billing webhook ingress and durable receipt acceptance through `ARCH-027-API-005`;
- exact raw-body Base64 HMAC-SHA256 verification and seven-topic provider allowlisting;
- Shopify-parity purchase-history/refund-hold/reactivation APIs through `ARCH-027-API-006`;
- API-specific request/idempotency validation.

The API does not own asynchronous durable subscription/entitlement business
reconciliation.

### `moda-interact-background` / `moda_background`

Will own asynchronous application of verified Woo provider evidence to the existing
Moda billing domain, including:

- subscription activation/lifecycle projection;
- plan switch application;
- current allowance updates;
- Woo top-up purchase activation;
- Woo refund settlement/reconciliation;
- retry/idempotency of durable receipt processing;
- provider-aware paid included recovery accounting;
- `currentAllowanceQuantity` admission semantics;
- local Woo `UsageEvent(provider=WOOCOMMERCE, shopifyReportState=NOT_APPLICABLE)` creation without Shopify App Event publication.

ARCH-025 has already decomposed the existing billing reconciliation code into
smaller services. ARCH-027 should add bounded Woo collaborators around those
existing components rather than rebuilding another monolithic reconciliation
service.

`ARCH-027-BACKGROUND-001` is intentionally a safety prerequisite rather than the receipt consumer itself. Source inspection showed that activating Woo paid subscriptions before this correction would either retain Shopify meter requirements or create Shopify-reportable included-usage events for Woo.

`ARCH-027-BACKGROUND-004` is the charge-acquisition receipt consumer. It does not reuse Shopify meter reconciliation; Woo `/charges` provides different provider evidence. Both paths converge on the same `RecoveryCreditPurchase` / purchased-credit counter state.


### `moda-interact` / `moda_app`

Retains the existing Shopify billing edge.

`ARCH-027-SHOPIFY-001` is the bounded compatibility task required by the provider-aware persistence delta. It does not genericize the Shopify billing provider.

It makes Shopify ownership explicit:

```text
RecoveryCreditPurchase.provider = SHOPIFY
RecoveryCreditRefund.provider   = SHOPIFY
UsageEvent.provider             = SHOPIFY
```

and scopes Shopify purchase/history/refund reads accordingly so Woo rows cannot be interpreted through Shopify snapshot/meter semantics.

Although ARCH-027 makes Shopify acquisition/refund fields physically nullable for Woo, valid Shopify rows retain all existing non-null historical evidence. Shopify services must narrow/fail closed rather than fabricate missing handles/period/provider context.

Shopify paid included-period writers leave:

```text
currentAllowanceQuantity = NULL
```

and existing Shopify capacity semantics continue to use the pre-ARCH-027 grant behavior. A non-null mutable current allowance is a Woo lifecycle semantic and must not silently alter Shopify behavior.

`BillingPlanResolutionService` remains keyed by `shopifyPlanHandle` and keeps existing Shopify usage-meter validation. It must deterministically reuse an already-materialised operational plan with the same handle so Shopify and Woo never create provider-specific duplicates.

Existing hosted pricing, App Event usage, subscription projection/reconciliation, top-up meter flow and merchant refund behavior remain unchanged.

### `moda-interact-admin` / `moda_admin`

Continues to own portfolio economics and support/operator presentation. ARCH-027 does not move Admin's FIXED/GRADUATED/VOLUME economics arithmetic into Shared.

`ARCH-027-ADMIN-001` extends the existing recovery-credit refund support queue rather than creating a Woo console. It makes refund provenance/provider presentation explicit, keeps Shopify manual fallback intact, blocks the generic manual settlement path for Woo, explains Woo vendor-dashboard `PROVIDER_ACTION_REQUIRED` handling, and surfaces bounded read-only attention for unprocessed `WOO_REFUND_*` provider receipts.

`ARCH-027-ADMIN-002` owns only two deterministic exceptional mutations:

```text
1. Existing local refund + provider over-refund
   -> SUPER_ADMIN explicitly accepts the provider overage
   -> remove the already-frozen full remaining credit quantity
   -> preserve expected vs actual provider evidence

2. Unmatched provider refund
   -> one exact charge operation/purchase/transaction
   -> purchase ACTIVE, reservedAmount=0
   -> provider refunded at least the amount required for ALL currently unused credits
   -> SUPER_ADMIN creates one audited ADMIN COMPLETED refund
   -> remove all currently unused credits
   -> mark that provider receipt processed
```

Provider under-refund is intentionally not converted into a smaller credit quantity. The provider settlement must first increase sufficiently. Ambiguous identity, reserved credits, no remaining credits or inconsistent counters remain non-mutating support exceptions.

### `moda-interact-woocommerce` / `moda_woocommerce`

Owns Woo merchant-facing billing UX inside the existing ARCH-026 Woo Admin shell:

- `ARCH-027-WOOCOMMERCE-001`: plan/status/capacity presentation, plan selection/switch/cancel commands, Woo confirmation redirect and return/status presentation;
- `ARCH-027-WOOCOMMERCE-002`: predefined top-up purchase UX inside the accepted Billing surface;
- `ARCH-027-WOOCOMMERCE-003`: purchase-history/refund/reactivation UX inside the accepted Billing surface.

The browser calls local WordPress REST; PHP calls the authenticated hosted Moda API.
The plugin never receives Woo vendor billing credentials and never calculates the
authoritative provider charge.

### `moda-interact-gateway` / `moda_gateway`

`ARCH-027-GATEWAY-001` owns the minimum additive infrastructure needed by Woo billing.

ARCH-026 already owns:

```text
api-test.modainteract.com / api.modainteract.com
    -> public Gateway
    -> private moda-interact-api
```

ARCH-027 therefore does not create a second billing host/service/backend.

Gateway adds environment-isolated:

```text
moda-interact-test-woo-billing-config
moda-interact-production-woo-billing-config
```

containing the bounded `WOO_BILLING_ENVIRONMENT` plus Render-managed API key/secret placeholders, attached only to the private API service.

It also proves that the existing API-host route transports:

```text
X-WC-Webhook-Topic
X-WC-Webhook-Signature
exact raw request bytes
```

unchanged to API-005 at:

```text
/v1/billing/webhooks/woocommerce
```

Gateway does not authenticate the Woo webhook, parse provider billing payloads, own billing business logic or expose the vendor secret to any other service.

### `moda-interact-system-test` / `moda_system_test`

Owns terminal validation only after all required implementation and infrastructure tasks are Complete.

`ARCH-027-SYSTEM-TEST-001` is the local/mock integration gate. It runs the accepted database/API/Background lifecycle against disposable pgvector PostgreSQL, injects provider evidence only at architecture-approved boundaries, reuses accepted Woo plugin/Gateway/Shopify regression evidence, and generates one redacted cross-repository result artifact.

It MUST NOT add a test-only Woo provider base URL merely to fake API-003/API-004 outbound traffic. Real Woo command/provider behavior, tax/proration and provider refund capability are reserved for a separate sandbox-certification task.

No implementation task depends on a system-test task.

## Data Model

### WooCommerceBillingOperation

Durable provider workflow/intent evidence. It is Shop-scoped, not Subscription-row
scoped.

Required concepts include:

```text
shopId
kind
state
requestKey
requestFingerprint
merchantPricingPlanId?
merchantPricingUsageEventId?
quotedAmountMinor?
quotedCurrency?
quotedBillingPeriod?
recoveryCreditPurchaseId?
providerContractId?
confirmationUrl?
lastErrorCode?
createdAt / updatedAt
```

The exact field types, allowed operation shapes, write-once fields and PostgreSQL
constraints are owned by `ARCH-027-DATABASE-001`.

### WooCommerceBillingWebhookReceipt

Durable accepted provider delivery:

```text
topic
providerContractId?
payloadSha256
normalizedPayload
receivedAt
processedAt?
processingError?
```

The exact dedupe/immutability contract is owned by `ARCH-027-DATABASE-001`.

`ARCH-027-API-005` fixes `normalizedPayload` as the signed Woo provider-shaped JSON wrapper (`subscription` or `charge`) after HMAC/minimum-envelope validation. It is not a provider-neutral Shared lifecycle event and it is never used for signature verification; `payloadSha256` remains the identity of the exact raw bytes.

### BillingPeriodEntitlementCounter

Adds a nullable current allowance/spend ceiling while retaining the existing audit
and usage quantities.

Existing rows keep null and therefore retain existing behaviour until a provider
path explicitly establishes the current allowance override.

### Subscription

Remains one row per Shop. The current Woo recurring provider contract, when one
exists, is represented by `providerSubscriptionId` after trusted reconciliation.

A Woo Free subscription legitimately has:

```text
providerSubscriptionId = NULL
```

and may still own Woo top-up purchases.

### RecoveryCreditPurchase / RecoveryCreditRefund

Remain the provider-neutral business ownership/lifecycle rows. Mandatory Shopify
acquisition/correction evidence must become conditional where Woo uses different
provider evidence, but valid existing Shopify evidence requirements must be
preserved.

`RecoveryCreditPurchase.billingPeriodId` becomes nullable because the accepted Woo Free subscription has no BillingPeriod but may still buy one-time top-ups. Shopify purchases continue to require a billing period; a paid Woo purchase snapshots the current OPEN period.

## Contracts

### Existing database/catalogue contract

Owner: `moda-interact-database`.

Producer/consumer code uses the existing Prisma models. ARCH-027 does not create a
new cross-service pricing catalogue contract.

### Superseded Shared usage-price task

`ARCH-027-SHARED-001` is superseded before implementation. Woo v1 reads the directly stored price of a predefined FIXED `MerchantPricingUsageEvent`; it does not require a cross-repository pricing evaluator.

## Consistency and Transactions

- PostgreSQL remains the durable source of truth.
- Billing operations are persisted before provider create/charge requests.
- External Woo network calls must not occur inside a PostgreSQL transaction merely
  to approximate atomicity.
- Provider response loss is represented explicitly as `OUTCOME_UNKNOWN`.
- Same request-key reuse must not create a second provider operation when the
  canonical intent is unchanged.
- Same request key with a conflicting canonical fingerprint must fail closed.
- Receipt acceptance is durable before success acknowledgement.
- Receipt processing is retryable and idempotent.
- Provider contract identity becomes immutable once known for an operation.
- Subscription projection follows verified provider evidence rather than browser
  return state.
- New paid included reservations use `currentAllowanceQuantity ?? grantedQuantity`; a lower Woo current allowance does not claw back already committed/reserved usage.
- Included recovery commits remain one Moda `UsageEvent` business metric, but provider reporting evidence is selected from durable Shop platform: Shopify remains reportable; Woo is local `NOT_APPLICABLE` usage.

## Ordering

No global billing serialization is required.

Operations affecting the same Shop/current recurring contract must be applied with
sufficient optimistic/transactional protection to avoid two contradictory current
subscription transitions. Exact locking/CAS semantics belong in the owning
API/Background tasks after inspection of the current service mechanisms.

Top-up purchases remain separate purchase lots and may exist multiple times for the
same Shop. Equal event/price does not make two separately requested bundle purchases duplicates. Each accepted purchase has its own request identity and purchase lot.

Woo provider events may be duplicated, delayed or delivered out of order. Background
reconciliation must derive current Moda state idempotently and must not assume
exactly-once or strict webhook ordering.

## Failure Handling

### Provider POST ambiguity

If `/subscriptions` or `/charges` may have succeeded but the response is lost:

```text
operation -> OUTCOME_UNKNOWN
```

Do not blindly issue another create request.

### Webhook failure

If receipt persistence fails, do not acknowledge successful durable acceptance. API-005 returns non-2xx so Woo's provider retry policy can redeliver.

After receipt persistence, downstream processing failure must not require Woo to
re-send the exact same HTTP delivery for correctness; Background retries the durable
receipt from PostgreSQL. Exact duplicate provider deliveries are acknowledged idempotently without creating a second receipt.

### Invalid provider evidence

HMAC failure, malformed/unsupported payloads, mismatched contract identity or
cross-tenant evidence must fail closed and must not change Moda subscription or
credit state.

### Refund capability uncertainty

Automatic partial Woo refund initiation remains disabled until provider capability
is proven. Unsupported/unsafe cases remain explicit provider-action/manual workflows
rather than fabricating successful settlement.

## Scalability

Woo billing traffic is a different workload from high-volume Shopify checkout/order
webhook ingress. ARCH-027 does not assume raw Shopify event rates apply to SaaS
billing operations.

The relevant workload is expected to be merchant billing commands and Woo billing
lifecycle webhooks. The architecture therefore favours correctness, bounded request
work, durable acceptance and idempotent reconciliation over introducing new
infrastructure for throughput that has not been demonstrated.

The API and Background services remain horizontally deployable. No new Kafka,
database or queue technology is introduced by ARCH-027.

## Security

- Woo vendor API credentials live only in hosted Moda API deployment secrets.
- WordPress/PHP installation credentials are the ARCH-026 authentication mechanism;
  they are not Woo vendor billing credentials.
- Browser JavaScript must never receive either credential class.
- Every billing command resolves tenant authority from the authenticated installation
  principal, not from a caller-supplied `shopId`.
- Webhook HMAC verification uses the exact raw body before trusting JSON semantics.
- Provider contract IDs are identifiers, not tenant authorization tokens.
- Provider evidence must be checked against the resolved Shop/operation before
  changing business state.
- Logs/traces must not contain Authorization headers, vendor secrets, installation
  secrets, raw signatures or unnecessary payment/customer payloads.

## Observability

ARCH-027 reuses the platform Shared structured logger/OpenTelemetry conventions and
must not create another generic provider logger.

Useful bounded correlation identifiers include:

```text
shopId
billingOperationId
providerContractId
webhookReceiptId
recoveryCreditPurchaseId / refundId when relevant
request/correlation id
```

Operational evidence should distinguish:

- provider command initiated/accepted/unknown/failed;
- durable webhook receipt accepted/rejected;
- reconciliation completed/retried/failed;
- operation/receipt age when reconciliation is delayed.

Before creating custom metrics, the owning task must verify whether equivalent HTTP,
queue or database telemetry already exists through the approved framework/runtime.
Telemetry failure must not become a billing correctness dependency.

## Infrastructure / Deployment

ARCH-026 already establishes the public API host and private `moda-interact-api`
service topology. ARCH-027 therefore does not require a new public service.

`ARCH-027-GATEWAY-001` fixes the remaining infrastructure boundary:

```text
test API:
    WOO_BILLING_ENVIRONMENT=sandbox
    WOO_BILLING_API_KEY=<Render-managed secret>
    WOO_BILLING_API_SECRET=<Render-managed secret>

production API:
    WOO_BILLING_ENVIRONMENT=production
    WOO_BILLING_API_KEY=<Render-managed secret>
    WOO_BILLING_API_SECRET=<Render-managed secret>
```

These are attached only to the private API service.

Public provider webhook URLs reuse the ARCH-026 API host:

```text
https://api-test.modainteract.com/v1/billing/webhooks/woocommerce
https://api.modainteract.com/v1/billing/webhooks/woocommerce
```

Gateway adds no webhook-specific backend/path rewrite and no smaller Woo-specific body limit. API-005 remains responsible for HMAC/topic/payload validation and its 256 KiB route limit.

No secret value may be committed to Render Blueprint/repository configuration.

## Rollout / Migration

Classification: **pre-production / breaking Woo rollout with Shopify compatibility
preservation**.

There is no existing production Woo billing state to migrate. Existing Shopify
development/billing state must continue to migrate and operate correctly.

Expected implementation order is broadly:

```text
ARCH-026 database foundation complete
    -> ARCH-027 DATABASE-001
    -> API provider-edge tasks including API-005 durable webhook acceptance
    -> BACKGROUND-001 provider-aware paid-capacity safety
    -> BACKGROUND-002 Woo recurring subscription receipt reconciliation
    -> BACKGROUND-003 Woo local 30-day entitlement rollover
    -> BACKGROUND-004 Woo one-time-charge acquisition reconciliation
    -> BACKGROUND-005 Woo one-time-charge refund preparation/reconciliation
    -> API-006 Woo purchase-history/refund actions
    -> WOOCOMMERCE-001 billing hub + recurring plan management
    -> WOOCOMMERCE-002 top-up UI
    -> WOOCOMMERCE-003 purchase/refund UI
    -> ADMIN-001 provider-aware refund support/receipt attention
    -> ADMIN-002 deterministic exceptional refund recovery
    -> GATEWAY-001 Woo billing secrets/webhook transport wiring
    -> SHOPIFY-001 provider-aware persistence compatibility/regression
    -> developer manual validation / implementation acceptance
    -> SYSTEM-TEST-001 terminal local/mock integrated validation
    -> Woo sandbox capability certification (separate terminal task)
```

The precise dependency graph is updated as each task is authored. A system-test task
must never be made a prerequisite for unfinished implementation work.

## Decisions / Tasks

### Defined task

| Task | Owner | Status | Depends On |
|---|---|---|---|
| `ARCH-027-DATABASE-001` | `moda_database` | Pending | `ARCH-026-DATABASE-002` |
| `ARCH-027-SHARED-001` | `moda_shared` | Superseded | - |
| `ARCH-027-API-001` | `moda_api` | Pending | `ARCH-026-API-002`, `ARCH-027-DATABASE-001` |
| `ARCH-027-API-002` | `moda_api` | Pending | `ARCH-027-API-001` |
| `ARCH-027-API-003` | `moda_api` | Pending | `ARCH-027-API-002` |
| `ARCH-027-API-004` | `moda_api` | Pending | `ARCH-027-API-003` |
| `ARCH-027-API-005` | `moda_api` | Pending | `ARCH-027-API-004` |
| `ARCH-027-BACKGROUND-001` | `moda_background` | Pending | `ARCH-027-DATABASE-001` |
| `ARCH-027-BACKGROUND-002` | `moda_background` | Pending | `ARCH-027-API-005`, `ARCH-027-BACKGROUND-001` |
| `ARCH-027-BACKGROUND-003` | `moda_background` | Pending | `ARCH-027-BACKGROUND-002` |
| `ARCH-027-BACKGROUND-004` | `moda_background` | Pending | `ARCH-027-BACKGROUND-003` |
| `ARCH-027-BACKGROUND-005` | `moda_background` | Pending | `ARCH-027-BACKGROUND-004` |
| `ARCH-027-API-006` | `moda_api` | Pending | `ARCH-027-BACKGROUND-005` |
| `ARCH-027-WOOCOMMERCE-001` | `moda_woocommerce` | Pending | `ARCH-026-WOOCOMMERCE-005`, `ARCH-027-API-002`, `ARCH-027-API-003` |
| `ARCH-027-WOOCOMMERCE-002` | `moda_woocommerce` | Pending | `ARCH-027-WOOCOMMERCE-001`, `ARCH-027-API-004` |
| `ARCH-027-WOOCOMMERCE-003` | `moda_woocommerce` | Pending | `ARCH-027-WOOCOMMERCE-002`, `ARCH-027-API-006` |
| `ARCH-027-ADMIN-001` | `moda_admin` | Pending | `ARCH-027-BACKGROUND-005` |
| `ARCH-027-ADMIN-002` | `moda_admin` | Pending | `ARCH-027-ADMIN-001` |
| `ARCH-027-GATEWAY-001` | `moda_gateway` | Pending | `ARCH-026-GATEWAY-001`, `ARCH-027-API-005` |
| `ARCH-027-SHOPIFY-001` | `moda_app` | Pending | `ARCH-026-SHOPIFY-002`, `ARCH-027-DATABASE-001` |
| `ARCH-027-SYSTEM-TEST-001` | `moda_system_test` | Pending / Manual | all ARCH-027 implementation tasks through SHOPIFY-001 |

### Planned task areas — not yet materialised

The following are architectural work areas, not yet authoritative task files. IDs,
scope and dependencies may be refined as we discuss each one:

| Area | Expected owner | Intended outcome |
|---|---|---|
| Woo sandbox certification | `moda_system_test` | Real provider subscriptions/charges/webhooks/refund capability |

## Open Questions

The following are intentionally unresolved and must be settled before the owning task
is authored:

1. **Resolved — API -> Background handoff transport.** PostgreSQL `WooCommerceBillingWebhookReceipt` is the ARCH-027 v1 durable handoff. API-005 authenticates/persists; Background later claims unprocessed receipts directly with bounded PostgreSQL row-locking semantics. No BullMQ/outbox/Shared lifecycle event is introduced for this path.

2. **Woo sandbox partial refund capability.** Exact provider-side arbitrary partial
   one-time-charge refund support remains an external capability gate.

3. **Woo create response-loss recovery.** `OUTCOME_UNKNOWN` is fixed. The provider
   reconciliation/manual recovery mechanism will be finalized once the real Woo
   capability can be tested.

4. **Resolved — supported Woo webhook ingress contract.** API-005 accepts exactly the seven currently documented `saas_billing_contract.*` topics, verifies Base64 HMAC-SHA256 over the exact raw body with the Woo API secret, requires one signed `subscription` or `charge` wrapper, stores exact raw-body SHA-256 plus a bounded provider-shaped JSON snapshot, and performs no Moda lifecycle transition in the HTTP request.

5. **Resolved — `maximumUnitsPerBillingPeriod` remains catalogue/economics metadata in ARCH-027 v1.** The current Shopify purchase command does not enforce it as a runtime admission cap. To preserve Shopify/Woo parity, API-004 does not introduce a Woo-only limit. Any future enforced cap must be a separate cross-platform product/architecture change.

## Change History

### 2026-10-03 — Initial living design

- Created ARCH-027 as the follow-on to ARCH-026 Woo application foundation.
- Adopted the minimal-change architecture: one existing Moda commercial catalogue,
  two provider billing edges.
- Removed `WooCommerceBillingOffer` and `MerchantPricingProviderOffer` from v1.
- Preserved the existing one-Subscription-per-Shop invariant.
- Defined Woo contract IDs as provider-owned financial evidence rather than merchant
  or Moda subscription identities.
- Removed any need for `WooCommerceBillingOperation.subscriptionId`.
- Confirmed that Woo Free is a normal Moda subscription with no recurring Woo
  contract and may still purchase configured top-up credits through independent Woo
  one-time charges.
- Kept Woo plan-switch current-period usage intact by introducing a separate mutable
  allowance ceiling rather than resetting usage.
- Kept existing purchase-lot/refund semantics and made Woo partial automatic refund
  initiation an external sandbox capability gate.
- Defined `ARCH-027-DATABASE-001` as the first task and left later task boundaries
  deliberately iterative.
- Clarified Woo v1 top-ups as predefined, directly priced FIXED bundles: one selected `MerchantPricingUsageEvent` equals one purchase lot and one Woo charge; repeated purchases create separate lots.
- Removed `requestedQuantity` from the Woo billing-operation design.
- Superseded `ARCH-027-SHARED-001`; Woo no longer requires a Shared FIXED/GRADUATED/VOLUME price evaluator. Admin retains its existing economics implementation.
- Confirmed that successful first Woo connection automatically activates the local Moda Free subscription; merchants do not choose a plan during initial Woo install.
- Confirmed uninstall/reinstall anti-abuse semantics: lifetime Free credits are keyed to the durable Shop/counter and may be granted at most once; reconnect preserves the exact existing entitlement quantities and never forces an onboarded paid merchant back to Free.
- Defined `ARCH-027-API-001` to extend the accepted ARCH-026 connection transaction with atomic, idempotent initial Free activation and rollback on configuration failure.
- Confirmed Shopify as the reference merchant billing UX after Woo's automatic-Free entry point; Woo must reproduce the same current-plan, capacity, top-up and plan-management product semantics while keeping provider mechanics at the edge.
- Defined `ARCH-027-API-002` as the read-only authenticated Woo billing presentation contract: `GET /v1/billing` and `GET /v1/billing/plans`, using opaque Moda catalogue IDs and no live Woo provider calls.
- Resolved the paid `BillingPlan` materialisation boundary: recurring create/switch commands persist `MerchantPricingPlan` intent only; paid operational plan materialisation happens later from verified provider lifecycle evidence in Background.
- Defined `ARCH-027-API-003` as the recurring Woo command boundary for Free -> paid create, paid -> paid switch and provider-backed cancellation, with per-Shop idempotency, operation persistence before provider writes, no synchronous entitlement mutation, price parity and server-derived Woo return URLs.
- Identified and corrected the Free-top-up acquisition-context gap: `RecoveryCreditPurchase.billingPeriodId` must be nullable for Woo because automatic Free has no BillingPeriod; Shopify purchase-period requirements remain intact.
- Resolved `maximumUnitsPerBillingPeriod` for ARCH-027 v1 as non-enforced catalogue/economics metadata, matching the current Shopify runtime purchase behavior instead of adding a Woo-only cap.
- Defined `ARCH-027-API-004` as the one-predefined-bundle/one-Woo-charge command: atomic REQUESTED purchase + INITIATING operation before `/charges`, no quantity, Free top-ups without recurring contract/period, and provider confirmation deferred to later reconciliation.
- Rejected a separate Shared normalized Woo lifecycle contract for ARCH-027 v1. PostgreSQL `WooCommerceBillingWebhookReceipt` is the durable API -> Background boundary; the receipt retains provider-shaped Woo JSON and Background owns semantic interpretation.
- Resolved the webhook handoff transport as direct PostgreSQL receipt claiming rather than BullMQ/outbox publication.
- Defined `ARCH-027-API-005` as the public provider ingress: exact raw-body HMAC verification, seven-topic allowlist, provider-shaped durable receipt, exact-delivery dedupe and 204 acknowledgement only after commit.
- Source review identified a prerequisite before Woo paid activation: the current Background paid included-recovery path still requires Shopify meter semantics and reports committed usage as Shopify PENDING events.
- Defined `ARCH-027-BACKGROUND-001` to make included recovery accounting Woo-safe: consume mutable current allowance for new admission, preserve high-water grant/history, retain existing reservations across downgrade, and record Woo included usage locally with `provider=WOOCOMMERCE` / Shopify reporting `NOT_APPLICABLE`.
- BACKGROUND-002 source review moved paid BillingPlan materialisation to API-003 command initiation: materialise/reuse the operational plan before provider I/O to freeze feature/allowance state, while still deferring Subscription entitlement activation until verified Woo evidence.
- Defined `ARCH-027-BACKGROUND-002` as the Woo recurring receipt consumer: bounded PostgreSQL claim/retry, trusted contract correlation, Free -> paid activation, same-period plan switch allowance change, pause/renew recovery, cancellation/prepaid-end handling and atomic receipt completion.
- Kept local Woo recovery-period rollover separate from provider renewal: initial activation opens a 30-day local period; `renewed` never resets it; a later scheduled Background task owns EVERY_30_DAYS rollover.
- Defined `ARCH-027-BACKGROUND-003` as that local cadence owner: derive every successor from the previous Moda period end, preserve Shopify close invariants, use the current Subscription plan for the successor, bound multi-period catch-up to 12 transitions, do not grant while FROZEN, and run after recurring provider receipt reconciliation.
- Defined `ARCH-027-BACKGROUND-004` as Woo one-time-charge acquisition reconciliation: verified activated charge -> existing purchase lot ACTIVE + purchased counter grant + operation confirmation; canceled/unconfirmed charge -> terminal failed checkout; no Shopify purchase-meter evidence.
- Recorded Woo tax separation for top-ups: `quotedAmountMinor` is the immutable pre-tax Moda price sent to Woo; provider transaction amount is separate signed settlement evidence and may be higher because Woo adds tax.
- Kept one-time-charge `refunded` receipts out of BACKGROUND-004 so refund hold/unused-credit/provider-settlement semantics remain a separate bounded task.
- Defined `ARCH-027-BACKGROUND-005` to preserve ARCH-015 purchase-lot refund semantics for Woo: prepare local holds only after reservations settle, freeze proportional expected provider amount from provider purchase value, require vendor-dashboard provider action, then complete only from signed `refunded` evidence.
- Woo refund amount mismatch now has an explicit safe outcome: record actual provider evidence and move the local refund to `NEEDS_ATTENTION`; never change the credit quantity merely to match provider money.
- Corrected DATABASE-001 so `RecoveryCreditRefund.billingPeriodIdSnapshot` may be null for a Woo Free top-up refund while Shopify refund provenance remains non-null.
- Explicitly left provider refunds with no local Moda refund hold unmatched/unprocessed for a later Admin/support recovery path rather than fabricating a refund ledger row after money moved.
- Defined `ARCH-027-API-006` from the inspected Shopify purchase manager: exact ACTIVE/WITHDRAWN/COMPLETED/REFUNDED/ALL history filters, 5/10/20 pagination, bounded 20-lot batch refund requests, independent outcomes, and pre-provider reactivation.
- Woo refund eligibility is deliberately purchase-local rather than current-provider-context-bound: unlike Shopify meter corrections, an independent Woo one-time charge may remain refundable after recurring plan/cycle changes when unused/unreserved credits and acquisition evidence remain valid.
- API-006 produces only the local provider=WOOCOMMERCE REQUESTED refund hold; it makes no Woo/provider call and leaves proportional provider preparation/settlement to BACKGROUND-005.
- Defined `ARCH-027-WOOCOMMERCE-001` as the first Woo billing UI slice rather than cloning the Shopify application wholesale: current plan/capacity, plan catalogue, create/switch/cancel, provider redirect and return-state refresh through the existing PHP credential boundary.
- Split later Woo UI work deliberately: WOOCOMMERCE-002 will add top-up purchase controls; WOOCOMMERCE-003 will add purchase-history/refund/reactivation. WOOCOMMERCE-001 exposes no non-functional placeholders.
- Defined `ARCH-027-WOOCOMMERCE-002` as the top-up UI slice: one server-defined bundle per Buy click, no quantity/tier logic in WordPress, API-004 command through the existing PHP credential boundary, Woo confirmation redirect, and durable Billing refresh after return.
- Tightened API-002 per-offer top-up presentation: only same-bundle unresolved purchase uses `unavailableReason=PENDING_PURCHASE`; global billing/cancellation restrictions remain on `topUps.purchaseEligible` so one pending Bronze bundle does not disable Silver/Gold.
- Defined `ARCH-027-WOOCOMMERCE-003` as the Shopify-parity Purchased credits UI: exact filters/pagination, current-page batch selection, API-006 refund holds, merchant-safe refund status and pre-provider reactivation inside the existing Woo Billing surface.
- Kept all refund arithmetic/provider interpretation outside WordPress: React renders API-computed eligibility/state and BACKGROUND-005 remains the only provider refund preparation/settlement owner.
- Clarified API-006 response contracts for plugin safety: purchase history is `schemaVersion=1`, and both reactivation success outcomes use the same bounded versioned response shape.
- Source review of the existing Admin refund queue found a critical provider-boundary issue: its generic PROVIDER_ACTION_REQUIRED manual evidence form/action would also match normal Woo refunds unless explicitly provider-gated.
- Defined `ARCH-027-ADMIN-001` as a surgical provider-aware extension of the existing Admin refund support surface: Shopify manual settlement remains intact; Woo normal settlement is webhook-only; Woo PROVIDER_ACTION_REQUIRED/NEEDS_ATTENTION and unprocessed WOO_REFUND receipt evidence are triaged read-only.
- Deferred unmatched-provider-refund/NEEDS_ATTENTION mutation to `ARCH-027-ADMIN-002` rather than guessing credit/counter corrections after provider money has moved.
- Defined `ARCH-027-ADMIN-002` with a deliberately narrow recovery policy: accept only provider over-refund against an existing frozen Woo refund, or create an audited recovery refund for an unmatched provider refund when one active/unreserved purchase and all remaining credits map deterministically to the provider amount.
- Explicitly rejected provider-under-refund -> smaller-credit inference; ARCH-027 keeps the existing all-remaining-purchase-lot refund product rule.
- Corrected BACKGROUND-005 to treat Woo `amount_refunded` as monotonic cumulative evidence: later under-refund remediation can reach the frozen expected amount and complete normally; over-refund remains NEEDS_ATTENTION; decreasing evidence conflicts.
- Defined `ARCH-027-GATEWAY-001` as a small additive infrastructure task over the accepted ARCH-026 API topology: environment-isolated Woo billing key/secret groups attached only to private API, existing API host reused for the webhook, and explicit raw-body/signature-header preservation tests through Gateway.
- Fixed the public Woo webhook URLs to the existing API hosts; ARCH-027 creates no second billing/webhook hostname or service.
- Defined `ARCH-027-SHOPIFY-001` as a conservative compatibility task over `moda-interact`: explicitly scope purchase/refund/usage evidence to SHOPIFY, preserve non-null Shopify provenance despite shared schema nullability, keep mutable current allowance out of Shopify plan semantics, and prove existing BillingPlan materialisation/top-up/refund/hosted-pricing behavior remains unchanged.
- Defined `ARCH-027-SYSTEM-TEST-001` as the manual terminal local/mock integration gate spanning fresh/upgrade database rehearsal, Woo Free/paid/switch/pause/cancel/rollover/top-up/refund/exception lifecycles, API read consistency, duplicate/security/tenant-isolation behavior, and collected Woo plugin/Gateway/Shopify regression evidence.
- Kept real Woo provider commands, tax/proration, response-loss recovery and partial-refund capability out of SYSTEM-TEST-001; those remain the separate sandbox-certification gate.
- Corrected API-002 with durable `pendingCancellation` presentation so API-003 DELETE success cannot disappear from the UI during the provider-command-to-webhook projection window.
