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

Follow-on API, Background, Shopify, Admin, WooCommerce, Gateway and System-Test tasks, plus any genuinely required Shared lifecycle/receipt contract, will be added only after their exact contracts and repository boundaries have been agreed.

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

The exact repository-local extraction/reuse boundary for the materialiser will be
frozen before the relevant implementation task is authored. ARCH-027 does not
require a database redesign solely to make that reuse possible.

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

Once activated, purchased credits enter the existing reservation/consumption path. Woo must not create a fake Shopify purchase-acquisition `UsageEvent` merely to satisfy old Shopify evidence requirements.

### 10. No Shared usage-price evaluator for Woo v1

`ARCH-027-SHARED-001` was defined before the predefined-bundle purchase semantics were clarified. It is superseded before implementation.

Admin retains its existing portfolio-economics arithmetic, including FIXED/GRADUATED/VOLUME calculations where that Admin workflow needs them. Woo v1 does not share or duplicate that arithmetic because it consumes the already persisted price of a predefined FIXED bundle.

A future Shared billing task may still be justified for a genuine API -> Background lifecycle/receipt runtime contract, but no Shared price-evaluator task is required by ARCH-027.

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
    -> bounded request checks
    -> verify Woo HMAC over exact raw body
    -> validate/normalise supported payload
    -> persist WooCommerceBillingWebhookReceipt
    -> acknowledge provider
```

Business reconciliation occurs after durable receipt acceptance.

Receipt deduplication must not depend on nullable `providerContractId`. The current
DATABASE-001 contract deduplicates exact deliveries by:

```text
(topic, payloadSha256)
```

Background reconciliation must remain idempotent even when semantically equivalent
but byte-distinct provider deliveries produce distinct receipts.

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
    -> validate MerchantPricingPlan
    -> persist SUBSCRIPTION_CREATE operation + exact quote
    -> Woo /subscriptions
    -> persist recurring contract UUID + confirmation URL
    -> merchant confirms on WooCommerce.com
    -> signed webhook / verified provider evidence
    -> durable receipt
    -> asynchronous reconciliation
    -> MerchantPricingPlan -> BillingPlan
    -> activate the Shop's one Subscription
```

### Woo plan switch

```text
current Shop Subscription
    -> target MerchantPricingPlan.id
    -> persist PLAN_SWITCH operation against current recurring Woo contract
    -> provider switch request
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
    -> RecoveryCreditPurchase(REQUESTED) for creditsGrantedPerUnit
    -> persist ONE_TIME_CHARGE operation + exact stored quote
    -> Woo /charges
    -> merchant confirmation
    -> signed provider evidence
    -> purchase becomes ACTIVE

repeat the same bundle
    -> new request / new charge / new RecoveryCreditPurchase lot
```

### Woo cancellation

```text
current paid Subscription
    -> persist CANCEL operation against current recurring Woo contract
    -> provider cancellation request
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

Planned owner only of genuinely cross-repository billing contracts that are demonstrated to cross runtime boundaries, such as a normalized API -> Background lifecycle/receipt contract if one is required.

`ARCH-027-SHARED-001` (usage-price evaluator) is superseded and must not be implemented. The exact lifecycle Shared exports/schema version, if needed, will be frozen before that task definition is authored.

### `moda-interact-api` / `moda_api`

Will own:

- authenticated Woo billing read models/commands;
- provider-currency compatibility checks;
- Woo vendor billing client and secrets;
- recurring subscription create/switch/cancel requests;
- one-time predefined-bundle top-up charge requests using the persisted FIXED price;
- exact stored-price quote snapshot creation;
- signed Woo billing webhook ingress and durable receipt acceptance;
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
- retry/idempotency of durable receipt processing.

ARCH-025 has already decomposed the existing billing reconciliation code into
smaller services. ARCH-027 should add bounded Woo collaborators around those
existing components rather than rebuilding another monolithic reconciliation
service.

### `moda-interact` / `moda_app`

Retains the existing Shopify billing edge. Any ARCH-027 Shopify task is limited to
compatibility with the bounded provider-aware schema/shared primitives and reuse of
BillingPlan materialisation where required. Existing hosted pricing, App Event usage
and Shopify reconciliation semantics are not rewritten merely to make Woo possible.

### `moda-interact-admin` / `moda_admin`

Will continue to own portfolio economics and support/operator presentation. ARCH-027 does not move Admin's FIXED/GRADUATED/VOLUME economics arithmetic into Shared. Optional Woo operation/receipt/refund support views consume evidence but do not become a second pricing editor.

### `moda-interact-woocommerce` / `moda_woocommerce`

Owns Woo merchant-facing billing UX inside the existing ARCH-026 Woo Admin shell:

- plan/status presentation;
- plan selection/switch/cancel commands;
- top-up purchase UX;
- redirect to Woo confirmation URLs;
- return/status presentation.

The browser calls local WordPress REST; PHP calls the authenticated hosted Moda API.
The plugin never receives Woo vendor billing credentials and never calculates the
authoritative provider charge.

### `moda-interact-gateway` / `moda_gateway`

Will own any required deployment/environment wiring for Woo vendor billing secrets
and public routing to the existing hosted API. ARCH-026 already owns the API host and
private API topology; ARCH-027 should not create a second billing gateway or embed
business logic in Gateway.

### `moda-interact-system-test` / `moda_system_test`

Will own terminal integrated validation after all required implementation,
publication and infrastructure tasks are Complete. Mock/local integration should be
separated from real Woo sandbox capability certification where external access is
required.

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

## Contracts

### Existing database/catalogue contract

Owner: `moda-interact-database`.

Producer/consumer code uses the existing Prisma models. ARCH-027 does not create a
new cross-service pricing catalogue contract.

### Superseded Shared usage-price task

`ARCH-027-SHARED-001` is superseded before implementation. Woo v1 reads the directly stored price of a predefined FIXED `MerchantPricingUsageEvent`; it does not require a cross-repository pricing evaluator.

### Planned normalized Woo lifecycle contract

If API accepted receipts are handed to Background through an explicit cross-service
runtime contract, the canonical schema must be owned by `moda-interact-shared` and
imported by both producer and consumer. The precise event set, schema version,
deterministic identity and transport are intentionally not frozen until that task is
discussed.

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

If receipt persistence fails, do not acknowledge successful durable acceptance.

After receipt persistence, downstream processing failure must not require Woo to
re-send the exact same HTTP delivery for correctness; Background retries the durable
receipt according to the eventual task contract.

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

A bounded Gateway/infrastructure task is expected only for architecture-required
Woo billing environment/secret wiring and any route/config additions not already
covered by the existing API host.

No secret value may be committed to `render.yaml` or repository configuration.

## Rollout / Migration

Classification: **pre-production / breaking Woo rollout with Shopify compatibility
preservation**.

There is no existing production Woo billing state to migrate. Existing Shopify
development/billing state must continue to migrate and operate correctly.

Expected implementation order is broadly:

```text
ARCH-026 database foundation complete
    -> ARCH-027 DATABASE-001
    -> required Shared lifecycle contract/publication only if the API -> Background handoff needs one
    -> provider-edge + Background + Shopify/Admin compatibility tasks
    -> Woo plugin billing UI
    -> infrastructure wiring
    -> developer manual validation
    -> terminal system/mock validation
    -> Woo sandbox capability certification
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

### Planned task areas — not yet materialised

The following are architectural work areas, not yet authoritative task files. IDs,
scope and dependencies may be refined as we discuss each one:

| Area | Expected owner | Intended outcome |
|---|---|---|
| Shared lifecycle/receipt contract | `moda_shared` | Canonical cross-service validation only if API/Background runtime handoff requires it |
| Shared lifecycle publication gate | `moda_shared` | Publish an accepted lifecycle/receipt contract only if such a Shared contract is materialised |
| Shopify compatibility/materialisation | `moda_app` | Preserve Shopify behaviour while reusing any accepted billing-plan materialisation boundary |
| Admin Woo evidence/support | `moda_admin` | Bounded support/audit views without a second pricing editor |
| Woo recurring billing commands | `moda_api` | Paid create, switch and cancel provider adapter; Free is already local/automatic |
| Woo top-up charge command | `moda_api` | Validate one predefined FIXED bundle, snapshot its stored price and create one-time charge |
| Woo purchase-history/refund API | `moda_api` | Paginated purchased-credit history plus refund/reactivation commands matching the Shopify management experience |
| Woo billing webhook ingress | `moda_api` | Raw-body verification + durable receipt acceptance |
| Current allowance semantics | `moda_background` | Apply mutable Woo current-period allowance without usage reset |
| Woo subscription lifecycle reconciliation | `moda_background` | Verified Woo contract -> existing BillingPlan/Subscription projection |
| Woo top-up/refund reconciliation | `moda_background` | Provider evidence -> existing purchase/refund lifecycle |
| Woo receipt processing coordinator | `moda_background` | Idempotent retryable durable receipt processing |
| Woo billing UI | `moda_woocommerce` | Plans/status/switch/cancel in existing Woo Admin shell |
| Woo top-up UI | `moda_woocommerce` | Purchase/confirmation through existing PHP -> Moda API boundary |
| Woo billing infrastructure wiring | `moda_gateway` | Vendor secrets/configuration on existing hosted API topology |
| Integrated mock validation | `moda_system_test` | Cross-service Shopify regression + Woo mock/local flows |
| Woo sandbox certification | `moda_system_test` | Real provider subscriptions/charges/webhooks/refund capability |

## Open Questions

The following are intentionally unresolved and must be settled before the owning task
is authored:

1. **Paid BillingPlan materialiser boundary.** API-001 freezes the automatic Free-plan materialisation semantics required inside the Woo connection transaction. Paid Woo activation must still converge on the same operational BillingPlan as Shopify; the smallest safe repository-level reuse/extraction mechanism for the paid path will be frozen before that task is authored.

2. **API -> Background handoff transport.** Durable Woo webhook receipt persistence is
   fixed. Whether Background consumes receipts by polling/claiming PostgreSQL state or
   through a versioned asynchronous event/outbox must be chosen from the existing
   runtime capabilities; no new transport should be invented without need.

3. **Woo sandbox partial refund capability.** Exact provider-side arbitrary partial
   one-time-charge refund support remains an external capability gate.

4. **Woo create response-loss recovery.** `OUTCOME_UNKNOWN` is fixed. The provider
   reconciliation/manual recovery mechanism will be finalized once the real Woo
   capability can be tested.

5. **Exact supported Woo webhook topic/payload set.** The security/durable acceptance
   boundary is fixed, but precise topic normalization and lifecycle observation fields
   will be frozen from provider evidence when the Shared/API tasks are authored.

6. **Woo `maximumUnitsPerBillingPeriod` semantics for automatic-Free merchants.** Woo v1 top-ups are one predefined bundle per charge, but a Free Woo subscription has no recurring provider BillingPeriod. API-002 therefore does not invent a Free billing-period interpretation for this catalogue limit. The top-up charge-command task must freeze the authoritative limit/cadence rule before provider POST.

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
