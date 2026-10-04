---
id: ARCH-027-API-002
architecture_id: ARCH-027
title: Expose Shopify-parity Woo billing presentation state
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-API-001
enables:
  - ARCH-027-API-003
  - ARCH-027-WOOCOMMERCE-001
created: 2026-10-03
updated: 2026-10-04
---

# Expose Shopify-parity Woo billing presentation state

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Expose a strict, authenticated, read-only Woo billing presentation contract that gives the WooCommerce plugin the **same merchant-facing billing information and state distinctions that the current Shopify application uses**, while keeping provider-specific Woo credentials, contract identifiers and Shopify implementation fields out of the browser-facing contract.

The task owns exactly two authenticated read endpoints:

```text
GET /v1/billing
GET /v1/billing/plans
```

Together they provide the bounded state required for the Woo Admin application to reproduce the existing Shopify billing experience:

```text
Current plan
Recovery-capacity balances
Predefined top-up bundles
Pending/awaiting billing state
Plan-management availability
Top-up purchase availability
Plan catalogue for Change Plan
```

The task is read-only. It MUST NOT:

```text
create/switch/cancel subscriptions
create Woo contracts
create top-up charges
create/refund RecoveryCreditPurchase rows
process Woo webhooks
mutate entitlement counters
call WooCommerce.com
```

Shopify is the reference merchant billing UX, but **not** the public API shape. The hosted API must expose provider-neutral Moda presentation state using opaque Moda catalogue identifiers, not Shopify handles.

## Context

The current Shopify application already has a mature merchant billing experience implemented primarily by:

```text
moda-interact/app/routes/app/billing/options/route.tsx
moda-interact/app/components/dashboard/BillingPurchaseHub.jsx
moda-interact/app/components/dashboard/TopUpPurchasePanel.jsx
moda-interact/app/components/dashboard/SubscriptionChangePanel.jsx
moda-interact/app/services/billing/merchant-billing-read.service.ts
moda-interact/app/services/billing/merchant-recovery-capacity-read.service.ts
moda-interact/app/services/merchant-pricing/merchant-pricing.server.js
```

That experience presents:

```text
billing hero / current plan
included credits
lifetime Free credits
promotional credits
purchased credits
Add top-up / Change plan switch
predefined credit-pack cards
pending purchase state
current plan card
pending plan card
scheduled cancellation notice
purchase-history availability
usage-history availability
```

ARCH-027 intentionally keeps that merchant experience as the reference. Woo provider mechanics differ, but the merchant should not see a different Moda product model.

`ARCH-027-API-001` establishes the Woo-specific initial condition:

```text
successful first connection
    -> one ACTIVE local Free Subscription
    -> providerSubscriptionId = NULL
    -> lifetime Free credits granted at most once
    -> Shop.onboardingCompleted = true
```

Therefore API-002 can assume an architect-accepted API-001 implementation exists before execution. Reinstall/reconnect must continue to preserve the same durable Shop, Subscription and entitlement state rather than creating another billing identity.

`ARCH-027-DATABASE-001`, consumed transitively through API-001, adds the Woo operation/receipt and provider-neutral purchase/refund evidence required by later command/reconciliation tasks. API-002 may read those accepted fields where necessary to present pending Woo operations, but MUST NOT mutate them.

Woo v1 top-ups are now defined as **predefined directly priced bundles**:

```text
MerchantPricingUsageEvent
    pricingMode = FIXED
    creditsGrantedPerUnit = credits in one bundle
    fixedUnitAmountMinor = authoritative retail price of one bundle
    currency = authoritative bundle currency
```

One click purchases one bundle. API-002 MUST NOT expose arbitrary quantity pricing or run FIXED/GRADUATED/VOLUME economics calculations.

The current Shopify application uses Shopify provider handles internally. The Woo presentation contract must instead expose:

```text
MerchantPricingPlan.id
MerchantPricingUsageEvent.id
```

as opaque Moda catalogue identifiers for later command requests.

## Scope

Modify only `moda-interact-api` implementation/test/documentation files required to provide the authenticated Woo billing presentation read model plus the nested `database/` gitlink required to consume the architect-accepted ARCH-027 database schema.

Expected implementation areas are conceptually:

```text
src/
  billing/
    presentation/
      billing-read-service.ts
      plan-catalogue-read-service.ts
      experience-state.ts
      locale.ts
      schemas.ts
      routes.ts
openapi/
  woocommerce-billing-presentation-v1.yaml
tests/
  ... focused billing presentation tests
```

The exact repository-local filenames may differ if an equally bounded structure is clearer.

### Canonical database dependency

Before implementation, update/preserve the API repository's nested:

```text
database/
```

gitlink at the newest architect-accepted `moda-interact-database` `main` commit that includes `ARCH-027-DATABASE-001`.

Do not move the gitlink backwards if API-001 has already advanced it to a newer compatible accepted database commit.

Generate Prisma from that pinned schema.

Do not copy/redeclare database models locally and do not modify Prisma schema/migrations in this task.

### Existing authentication boundary

Both routes MUST reuse the accepted ARCH-026 API-002 `WooInstallationAuthenticator`.

Authenticated identity is exclusively:

```text
X-Moda-Installation-Id + Bearer credential
    -> WooInstallationAuthenticator
    -> principal.shopId
```

Neither endpoint may accept tenant identity through:

```text
query shopId
path shopId
request body shopId
custom merchant/site-id header
browser-supplied domain
```

`principal.shopId` is the only tenant key.

### Shop integrity

For normal successful reads, the authenticated Shop must satisfy:

```text
Shop.id            = principal.shopId
Shop.platform      = WOOCOMMERCE
Shop.shopifyShopId = NULL
Shop.status        = ACTIVE
Shop.domain        = principal.canonicalSiteUrl
```

API-002 MUST fail closed on an impossible principal/Shop mismatch. It MUST NOT fall back to domain lookup.

### No live Woo provider dependency

These read endpoints MUST NOT call WooCommerce.com.

Woo billing presentation is derived from durable Moda state:

```text
Shop
Subscription
BillingPlan
BillingPeriod / entitlement counter
ShopEntitlementCounter
promotion selection/grant
MerchantPricingPlan / translations / highlights
MerchantPricingUsageEvent
RecoveryCreditPurchase
WooCommerceBillingOperation
```

Provider confirmation enters the durable projection through later provider-ingress/reconciliation tasks. The merchant read path does not turn Woo availability into a synchronous correctness dependency.

### Route 1 — billing hub state

Expose exactly:

```text
GET /v1/billing
```

No request body is permitted.

Unknown query parameters MUST be rejected. This route has no query parameters in v1.

Return a strict versioned logical response shaped as follows:

```json
{
  "schemaVersion": 1,
  "experienceState": "ACTIVE",
  "surfaces": {
    "usageHistoryAllowed": true,
    "purchaseHistoryAllowed": true,
    "managePlansAllowed": true
  },
  "currentPlan": {
    "merchantPricingPlanId": "mp_free",
    "displayName": "Free",
    "planKind": "FREE",
    "recurringAmountMinor": 0,
    "currency": "USD",
    "billingPeriod": "EVERY_30_DAYS",
    "currentPeriodEnd": null,
    "cancelAtPeriodEnd": false
  },
  "pendingPlan": null,
  "pendingCancellation": null,
  "capacity": {
    "paidIncluded": null,
    "freeLifetime": {
      "granted": 2,
      "committed": 0,
      "reserved": 0,
      "remaining": 2
    },
    "promotional": {
      "granted": 0,
      "committed": 0,
      "reserved": 0,
      "remaining": 0
    },
    "purchased": {
      "granted": 0,
      "committed": 0,
      "reserved": 0,
      "refunding": 0,
      "available": 0
    }
  },
  "topUps": {
    "configured": true,
    "purchaseEligible": true,
    "offers": [
      {
        "merchantPricingUsageEventId": "usage_bronze",
        "label": "Bronze",
        "creditsGranted": 10,
        "amountMinor": 1000,
        "currency": "USD",
        "purchaseEligible": true,
        "unavailableReason": null
      }
    ],
    "latestPurchase": null,
    "unresolvedPurchases": []
  }
}
```

All fields above are part of the v1 contract unless explicitly defined as nullable.

Do not return an absent key merely because a value is unavailable; use the defined nullable/empty representation.

### Experience state

The read model must use the same merchant-facing business state vocabulary as the Shopify application where applicable:

```text
ACTIVE
NO_CONTRACT
FROZEN
BILLING_ATTENTION
```

API-001 should normally make a newly connected Woo shop `ACTIVE` on Free immediately.

If the authenticated Shop is active but `Shop.onboardingCompleted != true`, API-002 MUST fail with bounded error:

```text
409 billing_not_initialized
```

rather than recreating onboarding/subscription state inside this read task.

Map Subscription state deterministically:

```text
Subscription ACTIVE/TRIALING -> ACTIVE
Subscription NO_CONTRACT      -> NO_CONTRACT
Subscription FROZEN           -> FROZEN
missing/other invalid state   -> BILLING_ATTENTION
```

Do not create Woo-specific UI states such as `WOO_PAUSED` or `WOO_PAYMENT_FAILED`.

### Surface availability

Derive the same logical billing navigation permissions used by the current Shopify merchant surface matrix:

```text
ACTIVE:
    usageHistoryAllowed      = true
    purchaseHistoryAllowed   = true
    managePlansAllowed       = true

NO_CONTRACT:
    usageHistoryAllowed      = true
    purchaseHistoryAllowed   = true
    managePlansAllowed       = true

FROZEN:
    usageHistoryAllowed      = true
    purchaseHistoryAllowed   = true
    managePlansAllowed       = false

BILLING_ATTENTION:
    usageHistoryAllowed      = true
    purchaseHistoryAllowed   = true
    managePlansAllowed       = true
```

These booleans are business-surface permissions. They do not imply that every corresponding Woo UI/page task has already been implemented.

### Current plan mapping

`Subscription.planId` points to the existing operational `BillingPlan`.

The current source does not yet have a direct `BillingPlan -> MerchantPricingPlan` FK. Until a later accepted architecture changes that, API-002 may resolve the catalogue row internally using the existing compatibility mapping:

```text
Subscription.plan.shopifyPlanHandle
    -> MerchantPricingPlan.shopifyPlanHandle
```

This is an internal compatibility lookup only.

The response MUST expose:

```text
MerchantPricingPlan.id
```

and MUST NOT expose:

```text
shopifyPlanHandle
observedShopifyPlanHandle
pendingShopifyPlanHandle
Shopify usage-event handles
```

If the current `BillingPlan` cannot resolve to exactly one catalogue row, return bounded integrity error:

```text
409 billing_catalogue_mapping_invalid
```

Do not fall back to a guessed plan.

Current-plan commercial presentation values come from `MerchantPricingPlan`, not from browser input and not from Woo:

```text
displayName
planKind
recurringAmountMinor
currency
billingPeriod
```

For Free:

```text
providerSubscriptionId = NULL
currentPeriodEnd = NULL
```

is valid and MUST NOT make the plan unavailable.

For paid Woo, `currentPeriodEnd` is provider-derived:
- activated/renewed -> signed `next_payment_date`;
- updated -> signed proration-adjusted `next_payment_date`;
- canceled -> accepted signed prepaid `end_date`.

It is not a locally synthesized `periodStart + 30 days` date.

### Pending recurring billing presentation

Read current Woo recurring-operation evidence for the Shop.

First consider unresolved operations where:

```text
kind IN (SUBSCRIPTION_CREATE, PLAN_SWITCH, CANCEL)
state IN (INITIATING, AWAITING_CONFIRMATION, OUTCOME_UNKNOWN)
```

Rules:

1. zero unresolved create/switch operations -> `pendingPlan = null` unless the current durable Subscription already has a valid `pendingPlanId`;
2. one unresolved `SUBSCRIPTION_CREATE` or `PLAN_SWITCH` with `merchantPricingPlanId` -> present that target as `pendingPlan`;
3. more than one unresolved recurring operation for the same Shop is an integrity/command-serialization conflict and MUST return:
   ```text
   409 billing_operation_conflict
   ```

A pending plan response is:

```json
{
  "merchantPricingPlanId": "mp_growth",
  "displayName": "Growth",
  "recurringAmountMinor": 4900,
  "currency": "USD",
  "billingPeriod": "EVERY_30_DAYS",
  "state": "AWAITING_CONFIRMATION"
}
```

Do not expose:

```text
providerContractId
confirmationUrl
requestFingerprint
requestKey
lastErrorCode
```

through this read model.

If both `Subscription.pendingPlanId` and one unresolved recurring operation exist, they must resolve to the same target catalogue plan when both represent a plan change. A mismatch fails closed with `409 billing_operation_conflict`.

#### Pending cancellation

The Woo merchant UI needs a durable cancellation-pending signal across browser reloads.

Return:

```text
pendingCancellation
```

as either `null` or:

```json
{
  "state": "CONFIRMED"
}
```

Allowed states are:

```text
INITIATING
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
CONFIRMED
```

Set `pendingCancellation` from exactly one current `CANCEL` operation when either:

```text
state IN (INITIATING, AWAITING_CONFIRMATION, OUTCOME_UNKNOWN)
```

or:

```text
state = CONFIRMED

and
Subscription.providerSubscriptionId is non-null

and
operation.providerContractId
    = Subscription.providerSubscriptionId

and
Subscription.plan.kind = PAID_METERED

and
Subscription.cancelAtPeriodEnd = false
```

The `CONFIRMED` case means Woo accepted the provider DELETE but the durable Subscription projection has not yet recorded the canceled/prepaid lifecycle event.

Once:

```text
Subscription.cancelAtPeriodEnd = true
```

return:

```text
pendingCancellation = null
```

because scheduled cancellation is now represented by `currentPlan.cancelAtPeriodEnd`.

For local Free / null current provider contract, ignore stale historical CONFIRMED CANCEL operations.

If operation evidence produces more than one current recurring command, or a cancellation overlaps an unresolved create/switch in a way API-003 serialization should have prevented, fail closed with:

```text
409 billing_operation_conflict
```

Never expose the provider contract ID through `pendingCancellation`.

### Capacity projection

Return the same merchant-facing capacity categories as Shopify:

```text
paidIncluded
freeLifetime
promotional
purchased
```

#### Free lifetime

Read the Shop-scoped `LIFETIME_FREE_RECOVERY_CREDITS` entitlement counter.

Return:

```text
granted
committed
reserved
remaining = max(granted - committed - reserved, 0)
```

A missing Free counter after API-001 on an active Free Shop is a bounded integrity failure; do not silently grant credits in this read task.

#### Purchased

Read the existing Shop-scoped `PURCHASED_RECOVERY_CREDITS` counter.

Return:

```text
granted
committed
reserved
refunding
available = max(granted - committed - reserved - refunding, 0)
```

#### Promotional

Use the existing selected active promotion semantics already used by Shopify:

```text
campaign ACTIVE
current time inside campaign interval
scope matches GLOBAL / current plan / current shop
quantities valid
```

Return zero quantities when no valid selected promotion is active.

#### Paid included

For a valid current paid BillingPeriod, read the `INCLUDED_RECOVERY_CREDITS` period counter.

ARCH-027 changes availability semantics to:

```text
effectiveAllowance = currentAllowanceQuantity ?? grantedQuantity
remaining = max(
    effectiveAllowance
    - committedQuantity
    - reservedQuantity
    - forfeitedQuantity,
    0
)
```

Return:

```json
{
  "granted": 10,
  "currentAllowance": 5,
  "committed": 6,
  "reserved": 0,
  "forfeited": 0,
  "remaining": 0
}
```

`granted` is historical/current-period grant evidence. `currentAllowance` is the current spend ceiling. They are intentionally distinct.

A Woo downgrade may legitimately have:

```text
committed + reserved > currentAllowance
```

without making the counter invalid.

Do not apply the old Shopify-only assumption that committed/reserved/forfeited must be <= `currentAllowance`.

Existing rows with `currentAllowanceQuantity = NULL` remain valid through the fallback to `grantedQuantity`.

For Woo when `experienceState = FROZEN`, or when the current provider-backed paid period has passed its accepted provider end while lifecycle evidence is still converging:

```text
paidIncluded.remaining = 0
```

for spendable merchant presentation.

Preserve the historical grant/currentAllowance/committed/reserved/forfeited values.

Do not zero promotional, purchased or lifetime-Free balances merely because recurring Woo billing is FROZEN.

### Top-up offer projection

Top-up offers belong to the Shop's current catalogue plan.

Resolve them from the current `MerchantPricingPlan.usageEvents` only.

A Woo-v1 offer is eligible for presentation as a purchasable bundle only when all are true:

```text
pricingMode = FIXED
fixedUnitAmountMinor is a positive safe integer
creditsGrantedPerUnit is a positive safe integer
currency is exactly the owning MerchantPricingPlan.currency
currency = USD for Woo v1
```

Do not expose `GRADUATED` or `VOLUME` events as Woo-v1 purchasable bundles.

Do not evaluate tiers.

Do not expose `eventHandle`.

Each offer response is exactly one predefined bundle:

```json
{
  "merchantPricingUsageEventId": "...",
  "label": "Bronze",
  "creditsGranted": 10,
  "amountMinor": 1000,
  "currency": "USD",
  "purchaseEligible": true,
  "unavailableReason": null
}
```

`label` is the bounded trimmed catalogue `adminLabel`; fall back to a stable non-secret display label only if the accepted catalogue contract permits it. Do not return the Shopify event handle as fallback text.

`maximumUnitsPerBillingPeriod` remains existing catalogue/economics metadata and is **not** a Woo-v1 runtime purchase-admission gate. The current Shopify recovery-credit purchase command does not enforce it at runtime; ARCH-027 preserves that merchant behavior rather than creating a stricter Woo-only limit. API-002 therefore does not use `maximumUnitsPerBillingPeriod` to calculate `purchaseEligible`. Any future enforced purchase cap must be designed as a cross-platform Shopify/Woo product change.

The read endpoint MUST NOT rely on browser-supplied counters to determine eligibility.

### Top-up purchase eligibility

A Free Woo merchant with:

```text
Subscription.plan = Free
Subscription.status = ACTIVE
Subscription.providerSubscriptionId = NULL
```

MAY have `topUps.purchaseEligible = true`.

A recurring Woo contract is not required.

Global top-up purchase eligibility is true only if:

```text
experienceState = ACTIVE
Subscription.cancelAtPeriodEnd = false
at least one offer is individually purchaseEligible
```

For `FROZEN`, `NO_CONTRACT` or `BILLING_ATTENTION`, set:

```text
topUps.purchaseEligible = false
```

Do not remove historical balances/offers merely because purchasing is temporarily blocked.

### Latest and unresolved purchase presentation

Return at most one latest purchase and a bounded unresolved list sufficient to reproduce Shopify's pending-purchase UX.

`latestPurchase` is the most recently created `RecoveryCreditPurchase` for the Shop, or null.

For Woo purchases, resolve bundle identity through the associated `WooCommerceBillingOperation.merchantPricingUsageEventId`, not through Shopify `usageEventId` or event-handle snapshots.

Return only:

```text
id
status
merchantPricingUsageEventId
label
creditsGranted
currentAmount
reservedAmount
createdAt
activatedAt
operationState
```

Do not expose provider contract IDs, Woo transaction identifiers, request keys or raw provider evidence.

`unresolvedPurchases` includes bounded Woo purchases where:

```text
RecoveryCreditPurchase.status = REQUESTED

and the exactly linked ONE_TIME_CHARGE operation has state in:
    INITIATING
    AWAITING_CONFIRMATION
    OUTCOME_UNKNOWN
    CONFIRMED
```

A REQUESTED Woo purchase whose exactly linked operation is `FAILED` is historical failed command intent, not an unresolved checkout. It MUST NOT disable that bundle for a deliberate new request using a new idempotency key.

The unresolved list is ordered deterministically by:

```text
createdAt ASC, id ASC
```

Each unresolved Woo purchase must resolve to exactly one Woo `ONE_TIME_CHARGE` operation. Missing/ambiguous operation linkage is a bounded integrity failure rather than a guessed bundle identity. A linked `FAILED` operation is excluded from unresolved/pending presentation but may remain visible through later purchase-history/support surfaces.

Per-offer unavailability is intentionally narrow and deterministic:

```text
if an unresolved purchase exists for this exact
merchantPricingUsageEventId:
    offer.purchaseEligible = false
    offer.unavailableReason = "PENDING_PURCHASE"

otherwise:
    offer.purchaseEligible = true
    offer.unavailableReason = null
```

Global business-state restrictions such as `FROZEN`, `NO_CONTRACT`, `BILLING_ATTENTION` or `cancelAtPeriodEnd` are represented by:

```text
topUps.purchaseEligible = false
```

and do not invent additional per-offer `unavailableReason` values.

The read model must preserve Shopify-parity behavior:

```text
an unresolved Bronze purchase disables Bronze
another eligible bundle may remain purchasable
```

Do not globally block every bundle solely because one different bundle has an unresolved purchase.

### Route 2 — plan catalogue

Expose exactly:

```text
GET /v1/billing/plans
```

This route accepts at most one optional query parameter:

```text
locale=<BCP-47 presentation locale>
```

Unknown query parameters MUST be rejected.

`locale` is presentation-only. It is not tenant identity and MUST NOT be persisted as Shop international context.

Bounds:

```text
locale <= 64 UTF-8 bytes
must parse as a valid Intl/BCP-47 locale after trimming
```

If absent, use `Shop.defaultLanguageTag` as the first presentation fallback when valid; do not write it.

Return:

```json
{
  "schemaVersion": 1,
  "resolvedLocale": "en",
  "plans": [
    {
      "merchantPricingPlanId": "mp_growth",
      "displayName": "Growth",
      "planKind": "PAID_METERED",
      "cataloguePosition": 2,
      "featured": true,
      "localizedDescription": "...",
      "includedRecoveryCredits": 10,
      "allowancePeriod": "EVERY_30_DAYS",
      "billingPeriod": "EVERY_30_DAYS",
      "recurringAmountMinor": 4900,
      "currency": "USD",
      "highlights": [
        {
          "contentKey": "...",
          "position": 0,
          "title": "...",
          "description": "..."
        }
      ]
    }
  ]
}
```

The response MUST NOT expose `shopifyPlanHandle`.

### Plan catalogue eligibility

Return active Woo-v1-selectable plans only.

For Free:

```text
planKind = FREE
recurringAmountMinor = 0
```

For paid:

```text
planKind = PAID_METERED
recurringAmountMinor > 0
currency = USD
billingPeriod = EVERY_30_DAYS
```

ARCH-027 does not add Woo-specific prices. `recurringAmountMinor` and `currency` are the same authoritative Moda catalogue price used by Shopify.

Do not apply a Woo marketplace surcharge or pricing multiplier.

If an active catalogue plan is not Woo-v1-compatible because of provider currency restrictions, it MUST NOT be presented as a selectable Woo plan. Log only a bounded diagnostic code/plan ID; do not expose internal diagnostics to the merchant response.

The current Shop's plan remains displayable through `GET /v1/billing` even if later catalogue edits make that row inactive or no longer selectable. Never hide the merchant's current durable plan merely because it cannot be newly selected.

### Catalogue ordering and integrity

Sort plans by:

```text
cataloguePosition ASC
```

Require strictly increasing positions among returned plans.

Require one active Free plan to remain available for Woo. Zero or multiple active Free plans is a catalogue-integrity failure:

```text
409 billing_catalogue_invalid
```

Plan ID, usage-event ID and highlight identity are opaque Moda IDs. The API must not manufacture IDs from display labels or Shopify handles.

### Catalogue translation resolution

Do not add a fixed Woo locale allowlist.

Resolve one catalogue translation locale for the entire response using this ordered candidate strategy:

```text
1. requested locale exact normalized tag, when supplied
2. requested locale base language
3. Shop.defaultLanguageTag exact normalized tag, when valid
4. Shop.defaultLanguageTag base language
5. en
```

Deduplicate candidates while preserving order.

Choose the first candidate for which every returned plan has exactly one `MerchantPricingPlanTranslation` and every returned highlight has exactly one `MerchantPricingPlanHighlightTranslation`.

Do not mix different translation locales between cards in one response.

If none of the candidates yields a complete catalogue translation, return:

```text
409 billing_catalogue_translation_unavailable
```

The selected locale is returned as `resolvedLocale`.

Presentation-locale resolution MUST NOT mutate:

```text
Shop.storeLocale
Shop.defaultLanguageTag
Shop.defaultTimeZone
Shop.defaultCountryCode
```

### Read consistency

A single endpoint response must not combine obviously conflicting billing snapshots.

Use one bounded database read/transaction strategy appropriate to the repository so that:

```text
current Subscription
current plan mapping
capacity counters
unresolved operations/purchases
```

are read consistently enough to avoid presenting mutually impossible state created solely by interleaved application reads.

Do not hold a transaction while making external network calls; this task makes no provider calls.

The exact repository-local Prisma transaction/read-isolation mechanism is implementation detail, but the response must fail closed if required relations disagree.

### Response privacy

Both routes MUST use private/no-store response behavior appropriate to authenticated server-to-server PHP consumption.

Do not configure permissive browser CORS.

Do not return or log:

```text
installation credential/digest
Woo vendor credentials
providerContractId
confirmationUrl
requestKey
requestFingerprint
raw webhook payload/evidence
shopifyShopId
shopifyPlanHandle
Shopify usage-event handles
provider subscription/charge transaction IDs
customer/recovery message payloads
```

### Structured logging

Use the existing Shared structured logger.

Log only bounded operational fields such as:

```text
shopId
route
experienceState
planKind
planId
returnedPlanCount
returnedTopUpCount
outcome/errorCode
```

Do not log complete billing/catalogue responses.

## Out of Scope

- Creating or modifying Prisma schema/migrations.
- Creating a second Woo pricing catalogue.
- `WooCommerceBillingOffer` or `MerchantPricingProviderOffer`.
- A Woo marketplace price surcharge or multiplier.
- Runtime `FIXED` / `GRADUATED` / `VOLUME` price evaluation.
- Paid subscription create/switch/cancel commands.
- Woo `/subscriptions` calls.
- Woo `/charges` calls.
- Free-plan activation; owned by `ARCH-027-API-001`.
- Recovery-credit purchase command execution.
- Purchase refund initiation/reactivation.
- Full paginated purchase-history endpoint.
- Woo webhook HMAC verification or receipt persistence.
- Background subscription/charge/refund reconciliation.
- Admin support/audit UI.
- Woo Admin React implementation.
- WordPress local REST proxy implementation.
- Gateway/Render configuration.
- System tests or Woo sandbox certification.
- Changing Shopify UI/components/services.
- Changing Shopify plan-change behavior.
- Removing/renaming Shopify-specific database fields.
- Introducing a generic cross-provider BillingProvider framework.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Shopify is the reference merchant billing experience

The contract must contain the business presentation state required to reproduce Shopify's current billing hero, current-plan summary, capacity cards, top-up bundle cards, pending purchase presentation, current/pending plan presentation and durable pending-cancellation presentation.

Provider-specific mechanics may differ; Moda product semantics must not.

### R2 — Authenticated Shop identity is authoritative

Both endpoints use the API-002 authenticated principal `shopId` exclusively and fail closed on Shop/principal mismatch.

### R3 — Reads are provider-network independent

Neither endpoint calls WooCommerce.com. Durable Moda projection is the read authority.

### R4 — Current plan is represented by Moda catalogue identity

The response exposes `MerchantPricingPlan.id` and commercial presentation fields, never Shopify handles.

### R5 — Free is a normal active subscription without a Woo recurring contract

An ACTIVE Free subscription with `providerSubscriptionId = NULL` is valid and fully readable.

### R6 — Capacity uses ARCH-027 current allowance semantics

Paid included availability uses:

```text
currentAllowanceQuantity ?? grantedQuantity
```

without resetting/rewriting committed or reserved usage.

### R7 — Top-ups are predefined FIXED bundles

Woo-v1 top-up offers expose one stored bundle amount/credit grant per `MerchantPricingUsageEvent.id`. No arbitrary quantity or tier evaluator is introduced.

### R8 — Free merchants may buy top-ups

Top-up eligibility must not require a recurring Woo contract. Active Free merchants may buy eligible predefined bundles.

### R9 — One unresolved bundle does not globally block other bundles

Pending purchase state is scoped to the selected `MerchantPricingUsageEvent` so other eligible bundles can remain available.

### R10 — Catalogue pricing preserves platform parity

Equivalent Shopify/Woo plans and bundles use the same persisted Moda catalogue price. API-002 performs no marketplace gross-up.

### R11 — Woo plan catalogue uses opaque Moda IDs

The plan endpoint returns `MerchantPricingPlan.id`; no Shopify plan handle is exposed or accepted.

### R12 — Presentation locale is open-ended and non-durable

The optional locale is presentation-only, has no fixed Woo allowlist and cannot mutate shared Shop international context.

### R13 — Translation resolution is deterministic

One complete translation locale is selected for the whole returned catalogue using the defined candidate order; missing/partial translations fail closed rather than mixing languages silently.

### R14 — Billing operation conflicts fail closed

Multiple unresolved recurring Woo operations or disagreement between durable pending-plan projection and operation intent return a bounded conflict error.

### R15 — Read endpoints have no side effects

Both routes perform zero database writes, provider calls, queue publication, entitlement grants or operation creation.

### R16 — Public contract is PHP-consumable and versioned

A version-controlled OpenAPI 3.1 document defines both routes, response schemas and bounded error schemas.

### R17 — Sensitive/provider evidence is excluded

The external read contract never returns provider credentials, contract UUIDs, operation fingerprints, Shopify handles or raw provider evidence.

## Work Items

- [ ] Verify the API repository consumes the newest architect-accepted database gitlink containing ARCH-027-DATABASE-001.
- [ ] Add the provider-neutral billing presentation response/runtime schemas.
- [ ] Add the plan-catalogue response/runtime schemas.
- [ ] Implement one authenticated Shop-scoped billing read service with no Woo provider calls.
- [ ] Reproduce the Shopify merchant experience-state vocabulary needed for billing presentation.
- [ ] Resolve the current `BillingPlan` to `MerchantPricingPlan` through the current compatibility mapping without exposing Shopify handles.
- [ ] Project Free, paid-included, promotional and purchased recovery capacity.
- [ ] Use `currentAllowanceQuantity ?? grantedQuantity` for paid included availability.
- [ ] Project unresolved recurring Woo billing operations into bounded pending-plan state.
- [ ] Project current CANCEL operation evidence into bounded `pendingCancellation` state, including the provider-accepted/durable-projection lag after API-003 DELETE success.
- [ ] Detect conflicting unresolved recurring operations and fail closed.
- [ ] Project Woo-v1 eligible predefined top-up bundles from the current `MerchantPricingPlan`.
- [ ] Exclude GRADUATED/VOLUME usage events from Woo-v1 purchasable bundle output.
- [ ] Preserve Free-plan top-up eligibility without a recurring Woo contract.
- [ ] Add per-bundle purchase-eligibility/pending behavior so one unresolved bundle does not block unrelated bundles.
- [ ] Project latest and bounded unresolved purchase state without provider identifiers.
- [ ] Implement `GET /v1/billing` using the reusable API-002 authenticator.
- [ ] Implement deterministic locale resolution for plan catalogue presentation.
- [ ] Project active Woo-v1-selectable plans and localized highlights using opaque `MerchantPricingPlan.id`.
- [ ] Implement `GET /v1/billing/plans` using the reusable API-002 authenticator.
- [ ] Reject unknown query parameters and invalid presentation locale.
- [ ] Add `openapi/woocommerce-billing-presentation-v1.yaml` matching runtime validation exactly.
- [ ] Add private/no-store and no-permissive-CORS behavior.
- [ ] Add bounded structured logging without complete response/provider evidence.
- [ ] Add focused unit/integration/security tests covering Free, paid, frozen, pending, top-up and catalogue cases.
- [ ] Document that purchase-history pagination and all write commands remain separate follow-on tasks.

## Interfaces / Contracts

### Contract owner

`ARCH-027-API-002`

### Public API owner

`moda-interact-api`

### Authentication owner

`ARCH-026-API-002`

### Upstream lifecycle owner

Initial Woo Free activation:

`ARCH-027-API-001`

### Consumer

Planned:

`ARCH-027-WOOCOMMERCE-001`

through PHP/server-side WordPress code. Browser JavaScript must continue to use the local WordPress REST boundary rather than calling the hosted API directly with installation credentials.

### Routes

```text
GET /v1/billing
GET /v1/billing/plans?locale=<optional BCP-47 presentation locale>
```

### Authentication

```text
X-Moda-Installation-Id: <installationId>
Authorization: Bearer <raw installation credential>
```

The route layer receives the resolved API-002 principal. It must not implement a second authentication mechanism.

### Portable contract

```text
openapi/woocommerce-billing-presentation-v1.yaml
```

### Database contracts consumed

```text
commerce.Shop
billing.Subscription
billing.BillingPlan
billing.BillingPeriod
billing.BillingPeriodEntitlementCounter
billing.ShopEntitlementCounter
billing.MerchantPromotionSelection
billing.PromotionalCreditGrant
billing.PromotionCampaign
billing.MerchantPricingPlan
billing.MerchantPricingPlanTranslation
billing.MerchantPricingPlanHighlight
billing.MerchantPricingPlanHighlightTranslation
billing.MerchantPricingUsageEvent
billing.RecoveryCreditPurchase
woocommerce.WooCommerceBillingOperation
```

Schema owner for ARCH-027 additions:

`ARCH-027-DATABASE-001`

API-002 reads these models only.

### Public identifier contract

Woo browser/server presentation uses:

```text
MerchantPricingPlan.id
MerchantPricingUsageEvent.id
RecoveryCreditPurchase.id
```

as opaque Moda identifiers.

It does not use Shopify handles as public contract identifiers.

## Dependencies

- `ARCH-027-API-001`

API-001 must be architect-accepted `complete` before API-002 becomes Ready.

This dependency also guarantees the accepted ARCH-027 database schema and ARCH-026 installation authenticator required by API-002 are already on the API implementation frontier.

Do not implement API-002 against an in-review API-001 branch or an unaccepted database task branch.

## Enables

- `ARCH-027-WOOCOMMERCE-001`

The first Woo billing presentation/UI task may consume this read contract only after API-002 is architect-accepted Complete.

Paid commands, top-up charge commands and provider webhook reconciliation do not need to be artificially serialized behind this read-model task unless their own final task definitions consume API-002 implementation directly.

## Acceptance Criteria

- [ ] `GET /v1/billing` exists and requires API-002 installation authentication.
- [ ] `GET /v1/billing/plans` exists and requires API-002 installation authentication.
- [ ] Neither endpoint accepts `shopId`, site URL or another tenant selector from the caller.
- [ ] An authenticated principal/Shop mismatch fails closed without fallback lookup.
- [ ] An active Free Woo Shop returns one normal current Moda plan with `providerSubscriptionId` semantics hidden from the public response.
- [ ] Free presentation does not require a Woo recurring contract.
- [ ] Current plan exposes `MerchantPricingPlan.id`, display name and stored commercial price, not Shopify handles.
- [ ] Current operational `BillingPlan` to catalogue mapping failure returns `billing_catalogue_mapping_invalid`.
- [ ] `ACTIVE`, `NO_CONTRACT`, `FROZEN` and `BILLING_ATTENTION` are projected deterministically from durable Moda state.
- [ ] `Shop.onboardingCompleted != true` returns `409 billing_not_initialized` and performs no repair/write.
- [ ] Free-lifetime capacity is returned from the existing lifetime counter without mutation.
- [ ] Purchased capacity includes `refunding` in availability calculation.
- [ ] Promotional capacity matches the current Shopify selection/campaign validity semantics.
- [ ] Paid included capacity uses `currentAllowanceQuantity ?? grantedQuantity` as the current ceiling.
- [ ] A downgrade state with historical committed usage greater than current allowance returns remaining `0` rather than an integrity error solely for that reason.
- [ ] Existing rows with null `currentAllowanceQuantity` use `grantedQuantity` fallback.
- [ ] Woo top-up offers are limited to current-plan FIXED events with positive stored price/credit grant and USD currency.
- [ ] GRADUATED/VOLUME events are not exposed as Woo-v1 purchasable bundles.
- [ ] Top-up response exposes `MerchantPricingUsageEvent.id` and stored price; it never exposes Shopify event handles.
- [ ] An ACTIVE Free Shop with no recurring contract may have top-up purchasing enabled.
- [ ] An unresolved purchase disables its own bundle while an unrelated eligible bundle may remain enabled.
- [ ] The matching unresolved bundle uses `unavailableReason=PENDING_PURCHASE`; an unrelated eligible bundle keeps `unavailableReason=null`.
- [ ] Global billing-state/cancellation restrictions set `topUps.purchaseEligible=false` without inventing additional per-offer unavailable reason codes.
- [ ] `FROZEN`, `NO_CONTRACT` and `BILLING_ATTENTION` disable new top-up purchase eligibility without removing historical balances.
- [ ] `latestPurchase` and unresolved purchase entries contain no provider contract/reference identifiers.
- [ ] Zero unresolved recurring operations yield no operation-derived pending plan.
- [ ] One unresolved create/switch operation projects one bounded pending plan using the target `MerchantPricingPlan.id`.
- [ ] Current INITIATING/AWAITING_CONFIRMATION/OUTCOME_UNKNOWN cancellation projects `pendingCancellation` without provider identifiers.
- [ ] A CONFIRMED CANCEL against the current provider contract projects `pendingCancellation=CONFIRMED` until durable `cancelAtPeriodEnd=true` is observed.
- [ ] Once durable scheduled cancellation is present, `pendingCancellation` is null and currentPlan.cancelAtPeriodEnd is authoritative.
- [ ] Historical CONFIRMED CANCEL evidence cannot make a local Free subscription appear cancellation-pending.
- [ ] Multiple unresolved recurring operations return `409 billing_operation_conflict`.
- [ ] Durable pending-plan and unresolved-operation target mismatch returns `409 billing_operation_conflict`.
- [ ] Plan catalogue returns only active Woo-v1-selectable plans sorted by catalogue position.
- [ ] Paid Woo-v1-selectable plans are USD, positive priced and `EVERY_30_DAYS`.
- [ ] Exactly one active Free plan is required; zero/multiple returns `409 billing_catalogue_invalid`.
- [ ] Catalogue response exposes no Shopify plan handles.
- [ ] The same persisted `recurringAmountMinor`/currency is returned for Woo; no marketplace surcharge is applied.
- [ ] Locale query is presentation-only, bounded and validated.
- [ ] Catalogue translation selection follows the defined exact/base/store/default candidate ordering.
- [ ] One response uses one complete translation locale; incomplete candidates are skipped rather than mixed across plan cards.
- [ ] Missing complete translation returns `409 billing_catalogue_translation_unavailable`.
- [ ] Presentation locale processing performs no Shop international-context write.
- [ ] Both endpoints perform zero writes, zero queue publication and zero WooCommerce.com calls.
- [ ] Responses use private/no-store behavior and do not enable permissive browser CORS.
- [ ] OpenAPI 3.1 and runtime request/response/error validators agree exactly.
- [ ] Structured logs contain bounded identifiers/outcomes and no complete billing response or provider evidence.

## Validation

Inspect `package.json` first and run the repository's actual scripts rather than assuming uniform workspace commands.

Required validation:

- [ ] clean dependency installation from the repository lockfile;
- [ ] Prisma generation from the architect-accepted nested database gitlink;
- [ ] typecheck;
- [ ] repository lint for changed API files;
- [ ] focused runtime-schema/OpenAPI agreement tests;
- [ ] authentication tests proving missing/invalid installation credential is rejected;
- [ ] tenant-isolation tests proving caller-supplied shop/domain values cannot change tenant selection;
- [ ] Free-plan read-model test with `providerSubscriptionId = NULL`;
- [ ] Free lifetime anti-mutation test proving the read does not change/regrant counters;
- [ ] paid included `currentAllowanceQuantity` downgrade test;
- [ ] null-current-allowance fallback test;
- [ ] promotional-capacity validity tests;
- [ ] purchased-capacity/refunding test;
- [ ] predefined FIXED top-up projection test;
- [ ] GRADUATED/VOLUME exclusion tests;
- [ ] Free/no-recurring-contract top-up eligibility test;
- [ ] per-bundle unresolved-purchase isolation test;
- [ ] frozen/no-contract/billing-attention purchase-denial tests;
- [ ] pending recurring operation presentation test;
- [ ] multiple recurring-operation conflict test;
- [ ] durable-pending/operation mismatch conflict test;
- [ ] plan catalogue ordering/filtering test;
- [ ] zero/multiple-Free catalogue integrity tests;
- [ ] price-parity test proving no Woo multiplier is applied;
- [ ] locale exact/base/store/default translation-resolution tests;
- [ ] incomplete/mixed translation rejection test;
- [ ] static/response audit proving no Shopify handles or provider contract/reference fields escape;
- [ ] test proving no endpoint invokes Woo provider client code;
- [ ] private/no-store and no-permissive-CORS test;
- [ ] bounded structured-log redaction test;
- [ ] full API repository test suite required by repository policy;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] changed-file/worktree evidence required by `moda_api`.

Where integration tests require PostgreSQL, use disposable test infrastructure only. Do not target durable development/staging/production databases.

If a required validation capability is absent from the repository, record the exact gap in the Completion Report rather than inventing an unrelated validation contract.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    ->
set task status to review
    ->
return to moda_architect
    ->
STOP
```

Do not begin paid command, top-up charge, purchase-history, Woo UI, webhook or Background reconciliation work.

## Implementation Notes

This task should be implemented as a bounded read model rather than by copying Shopify route code into the API.

Use the current Shopify merchant experience as behavioural evidence, especially:

```text
BillingPurchaseHub
TopUpPurchasePanel
SubscriptionChangePanel
MerchantBillingReadService
MerchantRecoveryCapacityReadService
MerchantPricingCatalogue
```

but remove Shopify-provider assumptions from the public Woo contract.

Do not extract a broad generic billing framework merely to avoid small repository-local read-model code.

Do not make Woo provider availability part of read correctness. Later signed webhook/reconciliation tasks own provider evidence ingestion.

Prefer explicit Prisma `select`/bounded includes so future schema growth cannot silently expand the public response.

The current `BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle` lookup is tolerated as a compatibility implementation detail because ARCH-027 deliberately avoids a large provider-neutral catalogue rewrite. It must remain internal and must not leak into the HTTP contract.

The plan catalogue locale is a UI presentation concern only. WordPress/Woo Admin remains responsible for its own static string translation through the `moda-interact` text domain; this API returns translated dynamic catalogue content only.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- API-001 will have established an ACTIVE local Free Subscription for newly connected Woo shops before API-002 executes.
- Current active MerchantPricingPlan data remains the single commercial catalogue shared by Shopify and Woo.
- Woo v1 supports only USD paid subscriptions/one-time charges; this provider restriction remains adapter/read-eligibility logic rather than a database-global rule.
- The current one-Subscription-per-Shop invariant remains unchanged.
- Full purchase-history/refund-management reads will be defined as a separate bounded task.

### Unresolved Issues

None within this task's read-only presentation boundary.

### Architectural Concerns

If implementation discovers that current operational BillingPlan -> MerchantPricingPlan mapping cannot be resolved safely without changing schema or another repository's contract, STOP and return that fact to `moda_architect`. Do not introduce an unplanned mapping table or provider-offer model inside this API task.

If reproducing the Shopify merchant UX requires a write-side or provider-live capability not represented by this read contract, record the missing capability for a follow-on task rather than expanding API-002.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
