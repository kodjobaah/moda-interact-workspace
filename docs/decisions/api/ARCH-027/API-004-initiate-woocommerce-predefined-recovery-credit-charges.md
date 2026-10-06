---
id: ARCH-027-API-004
architecture_id: ARCH-027
title: Initiate WooCommerce predefined recovery-credit charges
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-API-003
enables:
  - ARCH-027-API-005
  - ARCH-027-WOOCOMMERCE-002
created: 2026-10-03
updated: 2026-10-06
---

# Initiate WooCommerce predefined recovery-credit charges

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Add the bounded authenticated Woo Marketplace one-time-charge command for the existing Moda recovery-credit purchase-lot model:

```text
POST /v1/billing/recovery-credit-purchases
```

One successful command initiation represents **exactly one predefined recovery-credit bundle**:

```text
authenticated Woo Shop
    -> choose one MerchantPricingUsageEvent.id
    -> validate that event belongs to the Shop's current Moda plan
    -> read its stored FIXED bundle price and credit grant
    -> atomically persist one REQUESTED RecoveryCreditPurchase
       plus one INITIATING WooCommerceBillingOperation
    -> commit
    -> POST Woo /charges
    -> persist returned charge-contract UUID + confirmation URL
    -> return confirmation URL to the plugin
```

The merchant does **not** submit quantity, price, credits, currency, Shop identity, provider contract identity or billing-period identity.

The task owns provider charge **initiation only**. It MUST NOT activate credits, mark a purchase `ACTIVE`, create a purchase-acquisition `UsageEvent`, mutate recovery-capacity counters, process Woo billing webhooks, reconcile provider transaction evidence or complete/refund a purchase.

Verified Woo provider evidence remains a later Background reconciliation responsibility.

A Woo merchant on the local Moda Free plan is explicitly eligible to buy a predefined top-up bundle even though:

```text
Subscription.providerSubscriptionId = NULL
Subscription.billingPeriodId = NULL
```

No recurring Woo contract is required for `/charges`.

## Context

ARCH-027 has already fixed these foundations:

- `ARCH-027-API-001` automatically activates a first connected Woo Shop on the local Moda Free plan, grants lifetime Free recovery capacity at most once per durable Shop and creates no Woo recurring contract;
- `ARCH-027-API-002` exposes Shopify-parity current-plan/capacity/top-up presentation and uses opaque `MerchantPricingUsageEvent.id` values for Woo bundle selection;
- `ARCH-027-API-003` establishes the Woo Billing API runtime configuration/client, exact `Idempotency-Key` handling, server-derived return URLs, exact minor-unit conversion, provider write ambiguity rules and durable operation-before-provider-write pattern for recurring billing;
- `ARCH-027-DATABASE-001` defines `WooCommerceBillingOperation(kind = ONE_TIME_CHARGE)`, provider-neutral Woo `RecoveryCreditPurchase` evidence and one-operation/one-purchase linkage;
- one Woo v1 top-up selection is one predefined directly priced bundle, not an arbitrary quantity.

The current Shopify merchant experience is the UX reference:

```text
Bronze bundle -> Buy
Silver bundle -> Buy
Gold bundle -> Buy
```

One unresolved purchase for Bronze blocks another Bronze purchase while Silver/Gold can remain available. Re-buying Bronze after the previous purchase resolves creates a new purchase lot.

### Current-source purchase facts

The `moda-interact-workspace(20261003-123430).zip` baseline shows:

- `MerchantPricingUsageEvent` stores `creditsGrantedPerUnit`, `pricingMode`, `currency`, `fixedUnitAmountMinor`, `maximumUnitsPerBillingPeriod` and optional tiers;
- the realistic/manual Admin catalogue seeds current top-up offers as `FIXED` with `maximumUnitsPerBillingPeriod = NULL`;
- the current Shopify `RecoveryCreditPurchaseRequestService` creates one purchase lot per merchant purchase request and uses `quantity = 1` for the Shopify purchase usage event;
- the current Shopify runtime purchase path does not enforce `maximumUnitsPerBillingPeriod` as an admission limit;
- `RecoveryCreditPurchase.billingPeriodId` is currently mandatory in the pre-ARCH-027 schema, while API-001 intentionally gives local Free a `Subscription.billingPeriodId = NULL`.

That last point requires the small DATABASE-001 definition correction recorded by this task handoff: `RecoveryCreditPurchase.billingPeriodId` / relation become nullable, with existing Shopify purchase rows still requiring a billing period and Woo Free purchases allowed to snapshot no period.

### Woo provider facts

Woo's official Marketplace SaaS Billing documentation, verified 3 October 2026, states:

- one-time charges are intended for non-renewable purchases such as credit packs;
- initiate one with `POST /charges`;
- the response contains a `confirmation_url`;
- after merchant confirmation Woo appends the charge contract ID to the return URL and sends a `saas_billing_contract.activated` webhook containing the charge object;
- the current Billing API does not support a quantity parameter;
- only USD is currently supported;
- Woo calculates tax itself on top of the supplied original price.

Provider reference:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

These provider facts align directly with ARCH-027's one-predefined-bundle-per-charge decision.

## Scope

Modify only `moda-interact-api` implementation/tests/OpenAPI/runtime code required for the one-time recovery-credit charge command, plus the nested `database/` gitlink only when needed to consume the newest compatible architect-accepted database commit.

Expected implementation areas are conceptually:

```text
src/
  billing/
    commands/
      recovery-credit-purchase-command.service.ts
      recovery-credit-purchase-route.ts
      recovery-credit-purchase-schema.ts
      ... reuse accepted operation-idempotency / quote helpers ...
  woocommerce/
    billing/
      ... reuse accepted woo-billing-client.ts ...
      ... reuse accepted woo-billing-config.ts ...
openapi/
  woocommerce-billing-commands-v1.yaml
tests/
  ... focused top-up/idempotency/provider/concurrency tests
```

Exact repository-local filenames may differ when the accepted API-003 structure provides clearer owners. Reuse accepted authentication, Woo client/configuration, return-URL construction, exact monetary conversion, generic HTTP bounds and structured logging. Do not create parallel implementations.

### Canonical database dependency

Use the architect-accepted `ARCH-027-DATABASE-001` schema including the Free-top-up correction:

```text
RecoveryCreditPurchase.billingPeriodId String?
RecoveryCreditPurchase.billingPeriod   BillingPeriod?
```

Provider-specific invariant:

```text
SHOPIFY purchase
    billingPeriodId MUST remain non-null

WOOCOMMERCE purchase
    billingPeriodId MAY be null
```

The API task owns the stronger runtime rule:

```text
Woo current plan = FREE
    -> purchase.billingPeriodId = NULL

Woo current plan = PAID_METERED
    -> require current OPEN BillingPeriod
    -> purchase.billingPeriodId = Subscription.billingPeriodId
```

Before implementation, update the API repository's nested `database/` gitlink to the newest compatible architect-accepted `moda-interact-database` main commit containing this contract. Do not edit Prisma schema/migrations in API-004.

### Authentication boundary

The route MUST reuse the accepted ARCH-026 `WooInstallationAuthenticator`.

Authoritative tenant identity is only:

```text
X-Moda-Installation-Id + Bearer credential
    -> WooInstallationAuthenticator
    -> principal.shopId
```

The request MUST NOT contain a `shopId`, site URL/domain, recurring provider contract ID or Woo charge-contract ID.

For normal execution, the resolved Shop must satisfy:

```text
Shop.id                  = principal.shopId
Shop.platform            = WOOCOMMERCE
Shop.shopifyShopId       = NULL
Shop.status              = ACTIVE
Shop.domain              = principal.canonicalSiteUrl
Shop.onboardingCompleted = true
```

Fail closed on impossible principal/Shop mismatches. Do not fall back to domain-only authorization.

## Out of Scope

- Automatic Free activation; owned by `ARCH-027-API-001`.
- Billing/read presentation; owned by `ARCH-027-API-002`.
- Recurring create/switch/cancel; owned by `ARCH-027-API-003`.
- Arbitrary top-up quantity input.
- Runtime FIXED/GRADUATED/VOLUME price evaluation.
- Woo-specific price uplift, FX, discount or provider pricing table.
- Enforcing `maximumUnitsPerBillingPeriod` as a Woo-only runtime purchase cap.
- Purchase activation or credit grant after provider checkout.
- Woo billing webhook ingress/signature verification/durable receipt acceptance.
- Background charge reconciliation.
- Purchase-history pagination.
- Refund request/reactivation/provider settlement.
- Creating a Shopify purchase `UsageEvent` for Woo.
- Updating `Subscription.providerSubscriptionId` from a one-time charge.
- Woo Admin/WordPress UI implementation.
- Gateway/Render secret wiring.
- Woo sandbox certification.
- Changes to Shopify purchase code.
- Changes to `moda-interact-database` schema/migrations other than advancing the nested accepted gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Exact public command route

Implement exactly:

```text
POST /v1/billing/recovery-credit-purchases
```

Required header:

```text
Idempotency-Key: <caller-generated key>
```

Request JSON is exactly:

```json
{
  "merchantPricingUsageEventId": "..."
}
```

Reject unknown body fields.

The command accepts no query parameters.

Do not accept:

```text
shopId
merchantPricingPlanId
quantity
creditsGranted
amountMinor
currency
billingPeriodId
providerSubscriptionId
providerContractId
returnUrl
eventHandle
```

from the caller.

### R2 — Reuse exact API-003 idempotency-key grammar

Reuse API-003's accepted `Idempotency-Key` validation exactly:

```text
1..128 characters after trimming

allowed:
ASCII letters
digits
.
_
:
-
```

Store the validated value unchanged as:

```text
WooCommerceBillingOperation.requestKey
```

Do not synthesize a key when absent.

Missing/invalid key:

```text
400 invalid_idempotency_key
```

### R3 — Canonical top-up operation fingerprint

Compute SHA-256 over this exact UTF-8 canonical intent:

```text
arch027-topup-v1\n
ONE_TIME_CHARGE\n
<shopId>\n
<merchantPricingUsageEventId>\n
<quotedAmountMinor>\n
<quotedCurrency>\n
```

Where:

- `shopId` is the authenticated principal Shop ID;
- the event ID is the exact validated database ID;
- `quotedAmountMinor` is the exact stored `fixedUnitAmountMinor`;
- `quotedCurrency` is the exact validated uppercase catalogue currency.

Store the raw 32-byte digest in `requestFingerprint`.

Do not include server-generated `purchaseId`, operation ID, confirmation URL or provider charge-contract ID in the fingerprint.

### R4 — Same-key replay semantics

Inside the per-Shop serialized command transaction, first lookup:

```text
WooCommerceBillingOperation
where shopId = principal.shopId
  and requestKey = Idempotency-Key
```

If found:

1. compare stored/new fingerprint;
2. different fingerprint -> `409 idempotency_conflict`;
3. same fingerprint + `AWAITING_CONFIRMATION` -> return the existing `purchaseId`, operation ID and confirmation URL; MUST NOT call Woo again;
4. same fingerprint + `CONFIRMED` -> return the existing successful command result; MUST NOT call Woo again;
5. same fingerprint + `INITIATING` -> `409 billing_operation_in_progress`;
6. same fingerprint + `OUTCOME_UNKNOWN` -> `409 billing_provider_outcome_unknown`; MUST NOT retry `POST /charges`;
7. same fingerprint + `FAILED` -> `409 billing_operation_failed` with bounded safe error code; a deliberate new merchant attempt requires a new idempotency key.

Never create a second operation/purchase for the same `(shopId, requestKey)`.

### R5 — Command serialization and same-bundle unresolved gating

Use the same durable lock order as API-003:

```text
1. commerce.Shop
2. billing.Subscription
3. read current BillingPlan / acquisition BillingPeriod
4. read current-plan catalogue + selected bundle
5. read unresolved Woo ONE_TIME_CHARGE state for the selected bundle
6. create RecoveryCreditPurchase
7. create WooCommerceBillingOperation
```

Use the repository's accepted bounded row-lock helper or equivalent `SELECT ... FOR UPDATE`.

Do not hold a transaction open while calling WooCommerce.com.

A **different bundle** is not globally blocked because another bundle is unresolved.

For the selected `MerchantPricingUsageEvent.id`, reject a new different-key purchase when there is an existing linked Woo purchase with:

```text
RecoveryCreditPurchase.status = REQUESTED

and operation.kind = ONE_TIME_CHARGE

and operation.state IN (
  INITIATING,
  AWAITING_CONFIRMATION,
  OUTCOME_UNKNOWN,
  CONFIRMED
)
```

Return:

```text
409 top_up_purchase_pending
```

`operation.state = FAILED` is terminal for command admission and MUST NOT block a deliberate new request with a new idempotency key.

This implements Shopify-parity behavior:

```text
pending Bronze -> Bronze blocked
pending Bronze -> Silver may remain purchasable
```

### R6 — Current subscription eligibility

Require one current Moda Subscription for the authenticated Shop:

```text
Subscription exists
Subscription.status = ACTIVE
Subscription.planId is non-null
Subscription.plan exists
Subscription.plan.active = true
```

`cancelAtPeriodEnd = true` is still eligible while the Subscription remains `ACTIVE`: the merchant has prepaid paid-plan entitlement until the provider term end, and purchased top-ups survive recurring-plan termination.

Do not require a non-null recurring provider contract merely to buy a top-up.

Therefore this is valid:

```text
Free BillingPlan
Subscription.status = ACTIVE
Subscription.providerSubscriptionId = NULL
Subscription.billingPeriodId = NULL
```

Reject:

```text
NO_CONTRACT
UNMAPPED
SYNC_ERROR
FROZEN
```

and any corrupted/missing current plan projection with:

```text
409 top_up_purchase_unavailable
```

ARCH-027 v1 creates no Woo trial subscriptions; `TRIALING` is not admitted by this top-up command merely because the enum exists.

### R7 — Resolve current Moda catalogue plan through the accepted bridge

The current schema has no direct `BillingPlan -> MerchantPricingPlan` FK.

Resolve the current catalogue plan using the same current-schema bridge already accepted by ARCH-027:

```text
Subscription.plan.shopifyPlanHandle
    -> MerchantPricingPlan.shopifyPlanHandle
```

This is internal current-schema mapping only. Do not expose or accept the Shopify handle through the Woo API.

Require exactly one current `MerchantPricingPlan` and:

```text
MerchantPricingPlan.isActive = true
```

Its `planKind` must correspond to the current operational `BillingPlan.kind`:

```text
FREE         <-> FREE
PAID_METERED <-> PAID_METERED
```

Mismatch is a billing-integrity conflict and fails closed.

### R8 — Bundle ownership and Woo-v1 bundle eligibility

Load the requested event by exact:

```text
MerchantPricingUsageEvent.id
```

and require:

```text
merchantPricingUsageEvent.merchantPricingPlanId
    = current MerchantPricingPlan.id
```

A bundle from another plan is not purchasable by this Shop and returns:

```text
404 top_up_bundle_not_found
```

Do not reveal whether an ID belongs to another plan.

Woo-v1 eligibility is exactly:

```text
pricingMode = FIXED
fixedUnitAmountMinor is a positive safe integer
creditsGrantedPerUnit is a positive safe integer
event.currency is exactly the current plan currency
event.currency = USD
adminLabel is non-blank after trimming
```

Do not read/evaluate pricing tiers for Woo.

Do not calculate a quantity.

One request always means:

```text
creditsGranted = creditsGrantedPerUnit
quotedAmountMinor = fixedUnitAmountMinor
quotedCurrency = currency
```

### R9 — `maximumUnitsPerBillingPeriod` is not a Woo-only runtime gate

Resolve the API-002 open question as follows:

`maximumUnitsPerBillingPeriod` remains existing catalogue/economics metadata in ARCH-027 v1.

The current Shopify purchase-command implementation does not enforce it as an admission gate. To preserve the requested Shopify-parity merchant behavior, API-004 MUST NOT introduce a stricter Woo-only runtime cap.

Therefore:

```text
maximumUnitsPerBillingPeriod
    -> may be read as catalogue metadata
    -> is NOT used to reject/allow POST /v1/billing/recovery-credit-purchases
```

If Moda later decides this field must become an enforced purchase cap, that must be a separate cross-platform product/architecture change covering Shopify and Woo together.

### R10 — Acquisition BillingPeriod semantics

The purchase lot records the acquisition context without inventing a period for Free.

For current Free:

```text
current BillingPlan.kind = FREE
Subscription.billingPeriodId = NULL
purchase.billingPeriodId = NULL
purchase.providerSubscriptionIdSnapshot = NULL
```

Do not create a `BillingPeriod` merely to buy a top-up.

For current paid:

```text
current BillingPlan.kind = PAID_METERED
Subscription.providerSubscriptionId is non-null/non-blank
Subscription.billingPeriodId is non-null
Subscription.billingPeriod exists
Subscription.billingPeriod.status = OPEN
purchase.billingPeriodId = Subscription.billingPeriodId
purchase.providerSubscriptionIdSnapshot = Subscription.providerSubscriptionId
```

If the paid local period is missing/closed, fail closed with:

```text
409 top_up_purchase_unavailable
```

The purchase lot survives later plan/cycle changes regardless of its acquisition-period snapshot.

### R11 — Atomic REQUESTED purchase + INITIATING operation

For a genuinely new command, generate one UUID purchase ID server-side.

In one database transaction, create the purchase first:

```text
RecoveryCreditPurchase
    id = generated UUID
    shopId = principal.shopId
    planId = current BillingPlan.id
    billingPeriodId = R10 acquisition value
    provider = WOOCOMMERCE
    providerReference = NULL
    providerSubscriptionIdSnapshot = R10 acquisition value
    all Shopify plan/event/usage-before/usage-after snapshots = NULL
    providerPurchaseAmount = NULL
    providerPurchaseCurrency = NULL
    providerValuationConfirmedAt = NULL
    providerPriceSnapshot = NULL
    creditsGranted = MerchantPricingUsageEvent.creditsGrantedPerUnit
    currentAmount = 0
    reservedAmount = 0
    status = REQUESTED
    usageEventId = NULL
```

Then create exactly one operation referencing it:

```text
WooCommerceBillingOperation
    shopId = principal.shopId
    kind = ONE_TIME_CHARGE
    state = INITIATING
    requestKey = Idempotency-Key
    requestFingerprint = canonical digest
    merchantPricingPlanId = NULL
    merchantPricingUsageEventId = selected event ID
    quotedAmountMinor = fixedUnitAmountMinor
    quotedCurrency = USD
    quotedBillingPeriod = NULL
    recoveryCreditPurchaseId = generated purchase ID
    providerContractId = NULL
    confirmationUrl = NULL
    lastErrorCode = NULL
```

Commit both before provider network I/O.

Do not create a Woo purchase-acquisition `UsageEvent`.

### R12 — Exact stored retail price and price parity

The authoritative customer-facing amount is the stored bundle price:

```text
quotedAmountMinor = MerchantPricingUsageEvent.fixedUnitAmountMinor
quotedCurrency    = MerchantPricingUsageEvent.currency
```

No:

```text
Woo markup
marketplace multiplier
FX conversion
tier calculation
quantity multiplication
discount
```

is performed.

Equivalent Shopify/Woo bundle pricing therefore comes from the same Moda catalogue value.

Woo tax is provider-owned and is not predicted or added to `quotedAmountMinor`.

### R13 — Reuse API-003 provider configuration/client

Reuse the accepted API-003 Woo provider configuration:

```text
WOO_BILLING_ENVIRONMENT
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
```

and its bounded Billing API HTTP client behavior:

```text
Basic auth
TLS
no redirects
bounded timeout
bounded response body
no automatic write retries
safe error normalization
no Authorization/raw-body logging
```

Extend that client with the provider one-time-charge operation rather than creating another Woo client.

External provider route:

```text
POST /charges
```

The provider request is derived server-side from:

```text
name       <- selected MerchantPricingUsageEvent.adminLabel
price      <- fixedUnitAmountMinor converted using API-003 exact USD minor-unit conversion
return_url <- server-derived canonical Woo Admin billing return URL
```

Do not send a quantity parameter.

Do not send merchant personal information.

### R14 — Reuse the server-derived Woo return URL

Reuse API-003's accepted return-URL builder.

The return URL is derived only from:

```text
authenticated WooInstallation canonicalSiteUrl
+
WooCommerceBillingOperation.id
```

Conceptually:

```text
<canonicalSiteUrl>/wp-admin/admin.php
    ?page=wc-admin
    &path=/moda-interact
    &moda_billing_return=1
    &operation=<operationId>
```

Do not include:

```text
providerContractId
purchase amount
installation secret
Woo vendor credential
```

in the return URL.

The browser return is navigation evidence only and MUST NOT activate the purchase.

### R15 — Exact provider monetary conversion

Reuse API-003's exact USD minor-unit conversion helper.

Examples:

```text
1    -> 0.01
100  -> 1.00 commercial value
1999 -> 19.99
```

Do not use percentage calculations or floating multiplication.

The persisted integer quote remains authoritative.

### R16 — Provider charge-create success handling

A successful `POST /charges` response must provide:

```text
non-blank external charge-contract UUID/reference
non-blank HTTPS confirmation_url
```

Validate the confirmation URL host using the same environment allowlist as API-003:

```text
sandbox -> sandbox.woocommerce.com
production -> woocommerce.com
```

Before attaching a newly returned charge-contract ID, ensure any existing Woo billing operation using that provider contract belongs to the same Shop. A cross-Shop collision is an integrity/security failure.

On valid success, compare-and-set:

```text
operation.state:
    INITIATING -> AWAITING_CONFIRMATION

providerContractId:
    NULL -> returned charge contract ID

confirmationUrl:
    NULL -> validated provider URL

lastErrorCode = NULL
```

The linked `RecoveryCreditPurchase` remains:

```text
status = REQUESTED
currentAmount = 0
reservedAmount = 0
```

Return exactly:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "operationId": "...",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

Do not return provider contract ID, request key/fingerprint or raw provider payload.

### R17 — Provider/browser success is not credit activation

Neither:

```text
successful POST /charges
browser return to WordPress
```

is sufficient to grant credits.

This task MUST NOT set:

```text
RecoveryCreditPurchase.status = ACTIVE
RecoveryCreditPurchase.currentAmount > 0
RecoveryCreditPurchase.providerReference
RecoveryCreditPurchase.providerPurchaseAmount
RecoveryCreditPurchase.providerPurchaseCurrency
RecoveryCreditPurchase.providerValuationConfirmedAt
RecoveryCreditPurchase.providerPriceSnapshot
```

and MUST NOT mutate:

```text
ShopEntitlementCounter
BillingPeriodEntitlementCounter
UsageReservation
UsageEvent
```

Verified `saas_billing_contract.activated` provider evidence is reconciled later by Background.

A one-time charge contract ID MUST NEVER be copied into:

```text
Subscription.providerSubscriptionId
```

### R18 — Definite provider rejection

When a complete provider response definitively rejects the charge before a successful result is established, compare-and-set:

```text
operation.state = FAILED
operation.lastErrorCode = bounded normalized safe code
```

Keep the linked purchase as durable historical intent:

```text
RecoveryCreditPurchase.status = REQUESTED
```

because the current purchase status enum has no FAILED acquisition state and DATABASE-001 intentionally does not add one.

A `FAILED` operation is terminal for command admission:

- it does not block a later new attempt for the same bundle using a new idempotency key;
- API-002's unresolved-purchase presentation must not treat a REQUESTED purchase linked only to a FAILED operation as pending checkout.

Do not delete the purchase merely to hide the failed attempt, and do not store the complete provider response body.

### R19 — Ambiguous provider outcome

If Woo may have created the charge but Moda cannot prove the result, compare-and-set:

```text
operation.state = OUTCOME_UNKNOWN
operation.lastErrorCode = bounded safe code
purchase remains REQUESTED
```

Examples:

- timeout after request send;
- connection reset after request body send;
- provider 5xx where charge creation cannot be excluded;
- malformed/truncated apparent success response;
- suspicious cross-Shop provider-contract collision.

Do not automatically retry `POST /charges`.

Return:

```text
502 billing_provider_outcome_unknown
```

with bounded operation/purchase IDs and no raw provider payload.

Because duplicate external charging is possible, an `OUTCOME_UNKNOWN` purchase continues to block another purchase of the same bundle until reconciliation/manual recovery resolves it.

### R20 — Compare-and-set provider-result updates

Provider result updates MUST modify the operation only when its current state is the expected source state:

```text
INITIATING
```

If zero rows update, re-read the operation and honor the newer durable state. Do not overwrite a state that future webhook/reconciliation has already advanced.

### R21 — No recurring-contract prerequisite for Free

The command MUST prove this flow works:

```text
ACTIVE local Free Subscription
providerSubscriptionId = NULL
billingPeriodId = NULL
    +
eligible Free-plan predefined bundle
    ->
REQUESTED Woo RecoveryCreditPurchase with billingPeriodId = NULL
    +
INITIATING ONE_TIME_CHARGE operation
    ->
POST /charges
```

Do not call `/subscriptions` and do not manufacture any recurring provider contract.

### R22 — Structured logging and telemetry

Use the existing Shared structured logger and existing framework/OpenTelemetry instrumentation.

Allowed bounded identifiers include:

```text
shopId
purchaseId
billingOperationId
merchantPricingUsageEventId
operationState
providerEnvironment
safe error code
```

Do not log:

```text
Woo API key/secret
Authorization header
installation bearer credential
provider raw response body
full confirmation URL when it may include provider identifiers
customer/payment data
```

Do not create duplicate generic HTTP metrics when approved framework telemetry already provides them.

## Work Items

- [ ] Reuse the accepted API-003 Woo billing client/configuration/idempotency/return-URL/monetary helpers rather than creating parallel infrastructure.
- [ ] Add exactly `POST /v1/billing/recovery-credit-purchases`.
- [ ] Accept exactly `merchantPricingUsageEventId` in the JSON body and reject unknown fields.
- [ ] Require the accepted `Idempotency-Key`; do not accept quantity or caller-controlled commercial/provider fields.
- [ ] Add exact `arch027-topup-v1` SHA-256 fingerprint construction.
- [ ] Add exact same-key replay behavior for all five operation states.
- [ ] Serialize command creation with Shop -> Subscription lock order and no provider call inside the transaction.
- [ ] Resolve the current operational BillingPlan to the current MerchantPricingPlan through the existing internal `shopifyPlanHandle` bridge only.
- [ ] Prove the selected MerchantPricingUsageEvent belongs to that current plan.
- [ ] Enforce Woo-v1 predefined FIXED bundle eligibility and USD parity without tier calculation.
- [ ] Do not enforce `maximumUnitsPerBillingPeriod` as a Woo-only runtime gate.
- [ ] Add same-bundle unresolved purchase gating while allowing a different bundle to proceed.
- [ ] Add Free acquisition semantics with null recurring contract and null purchase billing period.
- [ ] Add paid acquisition semantics requiring the current OPEN BillingPeriod and snapshotting the current recurring contract.
- [ ] Atomically create one REQUESTED Woo RecoveryCreditPurchase plus one INITIATING ONE_TIME_CHARGE operation.
- [ ] Ensure Woo purchase creation writes no Shopify snapshots or purchase-acquisition UsageEvent.
- [ ] Extend the accepted Woo client with `POST /charges`.
- [ ] Send no quantity parameter.
- [ ] Reuse exact server-derived return URL and minor-unit conversion.
- [ ] Implement provider success -> `AWAITING_CONFIRMATION` while leaving the purchase REQUESTED.
- [ ] Implement definite provider rejection -> operation `FAILED` without credit activation.
- [ ] Implement ambiguous provider outcome -> `OUTCOME_UNKNOWN` with no automatic retry.
- [ ] Add provider contract cross-Shop collision checks.
- [ ] Ensure one-time charge contract IDs never populate `Subscription.providerSubscriptionId`.
- [ ] Update API-002 presentation behavior so FAILED purchase intents do not count as unresolved bundle checkouts.
- [ ] Update OpenAPI with exact request/response/error/idempotency contracts.
- [ ] Add focused route, catalogue, database, concurrency, replay, provider client and failure tests.

## Interfaces / Contracts

### Public hosted API

Authenticated command:

```text
POST /v1/billing/recovery-credit-purchases

header:
    Idempotency-Key: <required>

body:
{
  "merchantPricingUsageEventId": "..."
}
```

Successful initiation response:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "operationId": "...",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

No response exposes Woo charge-contract ID or credentials.

### Durable operation contract

Owner:

`ARCH-027-DATABASE-001`

Created shape:

```text
WooCommerceBillingOperation
    kind = ONE_TIME_CHARGE
    state = INITIATING
    merchantPricingUsageEventId = selected bundle ID
    quotedAmountMinor = stored fixedUnitAmountMinor
    quotedCurrency = stored currency
    recoveryCreditPurchaseId = new purchase ID
```

### Durable purchase contract

Owner:

`ARCH-027-DATABASE-001`

Created shape:

```text
RecoveryCreditPurchase
    provider = WOOCOMMERCE
    status = REQUESTED
    creditsGranted = selected creditsGrantedPerUnit
    currentAmount = 0
    reservedAmount = 0
    usageEventId = NULL
```

Acquisition-period shape:

```text
Free -> billingPeriodId = NULL
Paid -> billingPeriodId = current OPEN BillingPeriod
```

### Woo provider contract

Provider route:

```text
POST /charges
```

Authentication/configuration are owned by accepted API-003 infrastructure.

ARCH-027 v1 sends one charge for one predefined bundle. Woo's current Billing API has no quantity parameter.

Provider confirmation/activation is not consumed as entitlement proof in this task.

## Dependencies

- `ARCH-027-API-003`

API-003 must be architect-accepted Complete before API-004 becomes Ready because API-004 deliberately reuses its accepted:

- Woo Billing API environment/credential configuration;
- provider HTTP client and security bounds;
- exact idempotency-key parser;
- exact monetary conversion;
- server-derived Woo Admin return URL builder;
- provider result/error normalization;
- operation compare-and-set conventions.

Through API-003/API-002/API-001, this task also depends on the accepted ARCH-027 database schema and ARCH-026 installation-authentication boundary.

## Enables

- `ARCH-027-WOOCOMMERCE-002`

The later Woo top-up UI task consumes API-002's bundle presentation plus this command to reproduce the Shopify top-up purchase experience.

Webhook/background reconciliation tasks consume the durable operation/purchase created here but remain separately architected because provider-evidence normalization/handoff is not owned by API-004.

## Acceptance Criteria

- [ ] Exactly `POST /v1/billing/recovery-credit-purchases` is added for Woo top-up initiation.
- [ ] The request accepts only `merchantPricingUsageEventId`; no quantity, Shop, price, credits, currency, period or provider identity can be caller-controlled.
- [ ] The route uses the accepted Woo installation principal `shopId` exclusively.
- [ ] The route requires API-003's exact `Idempotency-Key` grammar.
- [ ] The raw 32-byte `arch027-topup-v1` request fingerprint follows the exact field ordering in R3.
- [ ] Same key/same fingerprint replay never creates another purchase/operation or another Woo charge.
- [ ] Same key/different fingerprint returns `409 idempotency_conflict`.
- [ ] Same-key `OUTCOME_UNKNOWN` never retries `POST /charges`.
- [ ] Current Subscription must be ACTIVE with a valid active current plan; scheduled cancellation alone does not block an otherwise valid top-up purchase.
- [ ] Free with null recurring provider contract is eligible.
- [ ] FROZEN/NO_CONTRACT/UNMAPPED/SYNC_ERROR are rejected.
- [ ] Current BillingPlan resolves deterministically to current MerchantPricingPlan through the accepted internal bridge.
- [ ] A selected bundle from another plan returns bounded not-found and is not purchasable.
- [ ] Woo-v1 bundle must be FIXED, positive stored amount, positive credits, same plan/event currency and USD.
- [ ] No tiers are evaluated.
- [ ] No quantity parameter is sent to Woo.
- [ ] `maximumUnitsPerBillingPeriod` is not introduced as a Woo-only runtime gate.
- [ ] Pending purchase gating is per selected bundle; a pending different bundle does not globally block purchasing.
- [ ] A FAILED prior operation does not block a deliberate new attempt with a new idempotency key.
- [ ] Free purchase creation permits `RecoveryCreditPurchase.billingPeriodId = NULL`.
- [ ] Paid purchase creation requires and snapshots the current OPEN BillingPeriod.
- [ ] The REQUESTED purchase and INITIATING operation are committed atomically before provider I/O.
- [ ] Woo REQUESTED purchase contains no Shopify snapshots and no purchase-acquisition UsageEvent.
- [ ] Quote exactly equals the stored fixed bundle price/currency with no Woo surcharge/FX/tier calculation.
- [ ] Provider request uses the accepted Woo client, Basic authentication, bounded I/O and no automatic write retries.
- [ ] Provider request contains no quantity or merchant PII.
- [ ] Valid provider success attaches the charge contract exactly once, stores validated confirmation URL and moves operation to AWAITING_CONFIRMATION.
- [ ] Provider success does not activate credits.
- [ ] Browser return does not activate credits.
- [ ] One-time charge contract ID is never written to `Subscription.providerSubscriptionId`.
- [ ] Definite provider rejection sets operation FAILED with bounded error evidence and does not grant credits.
- [ ] Ambiguous provider result sets OUTCOME_UNKNOWN and is not retried automatically.
- [ ] Cross-Shop returned provider-contract collision fails closed.
- [ ] Compare-and-set result updates cannot overwrite later durable state.
- [ ] API-002 unresolved-purchase presentation excludes REQUESTED purchases whose only linked operation is FAILED.
- [ ] OpenAPI documents exact request/response/error contracts.
- [ ] No Prisma schema/migration is edited by API-004.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect `moda-interact-api/package.json` and the accepted API-003 task before choosing exact commands. Do not assume scripts.

Required validation categories:

- [ ] clean dependency install from the repository lockfile when required by repository instructions;
- [ ] accepted repository typecheck;
- [ ] accepted repository lint/changed-file lint;
- [ ] accepted repository production build when declared/required;
- [ ] focused authenticated route/schema tests;
- [ ] exact idempotency-key grammar/replay/conflict tests;
- [ ] exact fingerprint byte-order tests;
- [ ] Free top-up integration test with null `Subscription.providerSubscriptionId` and null purchase `billingPeriodId`;
- [ ] paid top-up integration test with current OPEN BillingPeriod snapshot;
- [ ] current-plan/event membership negative test;
- [ ] FIXED positive bundle test;
- [ ] GRADUATED/VOLUME rejection tests;
- [ ] non-USD/currency-mismatch rejection tests;
- [ ] zero/null fixed-price rejection tests;
- [ ] test proving no quantity field is accepted or sent to Woo;
- [ ] test proving `maximumUnitsPerBillingPeriod` does not change Woo command admission;
- [ ] same-bundle unresolved concurrency test;
- [ ] different-bundle parallel eligibility test;
- [ ] FAILED prior attempt does not block new-key retry test;
- [ ] atomic purchase+operation creation/rollback test;
- [ ] provider request exact-price/minor-unit conversion tests;
- [ ] server-derived return URL tests;
- [ ] provider success -> AWAITING_CONFIRMATION while purchase remains REQUESTED;
- [ ] browser-return/no-webhook cannot activate purchase test;
- [ ] one-time contract never mutates Subscription provider identity test;
- [ ] provider deterministic rejection -> FAILED test;
- [ ] provider timeout/reset/ambiguous 5xx -> OUTCOME_UNKNOWN test;
- [ ] no automatic provider retry test;
- [ ] cross-Shop provider-contract collision test;
- [ ] compare-and-set race test;
- [ ] secret/raw-provider-payload logging negative test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, synchronization, branch and push evidence in the Completion Report.

Real Woo sandbox execution is not required for this implementation task; sandbox certification remains a terminal external/system-test gate.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> set task status to review
    -> clear execution claim according to repository protocol
    -> return to moda_architect
    -> STOP
```

Do not begin Woo UI, webhook ingress, Background reconciliation or refund tasks.

## Implementation Notes

This task should be implemented as a **small extension of API-003's provider-edge command infrastructure**, not as another billing subsystem.

Keep these boundaries visible:

```text
catalogue bundle identity/price
    -> MerchantPricingUsageEvent

purchase ownership/lifecycle
    -> RecoveryCreditPurchase

external provider command workflow
    -> WooCommerceBillingOperation

provider payment confirmation
    -> later verified webhook/reconciliation
```

Do not copy Shopify's App Event/meter machinery into Woo. Woo `/charges` is a different provider mechanism over the same Moda purchase-lot business concept.

The `shopifyPlanHandle` bridge remains an internal limitation of the current operational BillingPlan schema. API-004 may use it to resolve the current catalogue row but must not expose it to the Woo plugin.

The intentionally nullable Woo Free purchase `billingPeriodId` is acquisition-context absence, not loss of purchase ownership. The purchase lot remains Shop/plan-owned and survives later plan/cycle changes.

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

- `ARCH-027-API-003` provides an accepted reusable Woo Billing API client/configuration, return-URL builder, idempotency parser and monetary conversion helper.
- ARCH-027 Woo v1 purchases one predefined FIXED bundle per one-time charge.
- The current Shopify runtime does not enforce `maximumUnitsPerBillingPeriod` as a purchase admission limit; ARCH-027 preserves that behavior rather than creating a Woo-only restriction.
- The accepted DATABASE-001 correction permits Woo Free purchases to have null `billingPeriodId` while preserving non-null Shopify acquisition periods.

### Unresolved Issues

- Real Woo `/charges` sandbox request/response behavior remains to be certified later.
- Provider-side response-loss reconciliation for `OUTCOME_UNKNOWN` remains an external capability/system-test concern.
- Refund initiation behavior is outside this task.

### Architectural Concerns

None.

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
