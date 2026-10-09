---
id: ARCH-027-API-003
architecture_id: ARCH-027
title: Initiate WooCommerce recurring subscription create, switch and cancellation
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-09T07:58:30Z
attempt: 3
depends_on:
  - ARCH-027-API-002
enables:
  - ARCH-027-API-004
  - ARCH-027-WOOCOMMERCE-001
created: 2026-10-03
updated: 2026-10-09
---

# Initiate WooCommerce recurring subscription create, switch and cancellation

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Add the bounded authenticated Woo Marketplace recurring-billing command boundary for an already-connected Woo merchant:

```text
POST   /v1/billing/subscription
POST   /v1/billing/subscription/switch
DELETE /v1/billing/subscription
```

The task must let a merchant:

```text
Free Moda subscription
    -> choose a paid Moda catalogue plan
    -> create Woo recurring contract intent
    -> receive Woo confirmation URL

Existing paid Woo subscription
    -> choose another paid Moda catalogue plan
    -> initiate Woo plan switch against the same provider contract
    -> receive Woo confirmation URL

Existing paid Woo subscription
    -> cancel future renewal
    -> retain current paid Moda projection until verified provider lifecycle evidence ends the prepaid term
```

This task owns **provider command initiation only**. It MUST NOT activate a paid plan, change the Shop's current `Subscription.planId`, create/rotate a `BillingPeriod`, change included-credit allowance, process Woo webhooks, or transition a paid merchant back to Free.

Provider confirmation remains a later verified-evidence/reconciliation responsibility.

The Free plan remains local Moda state. This task MUST NOT create a zero-value Woo subscription contract for Free.

## Context

ARCH-027 has already established:

- `ARCH-027-API-001`: first successful Woo connection automatically establishes the Shop's one ACTIVE local Free Moda subscription, with `providerSubscriptionId = NULL`, one lifetime Free allocation at most once, and no Woo recurring contract;
- `ARCH-027-API-002`: the authenticated read model exposes Shopify-parity billing presentation using opaque `MerchantPricingPlan.id` values;
- `ARCH-027-DATABASE-001`: `BillingOperation` durably records create/switch/cancel intent before provider network calls and preserves `OUTCOME_UNKNOWN` for ambiguous provider results;
- one Moda `Shop` has at most one Moda `Subscription` because `Subscription.shopId` is unique;
- Woo recurring provider contract IDs are external WooCommerce.com evidence, not additional Moda subscriptions;
- the customer-facing recurring retail amount comes directly from `MerchantPricingPlan.recurringAmountMinor` and is the same catalogue amount used for the equivalent plan on Shopify; ARCH-027 does not add a Woo surcharge or provider-specific recurring-price table.

Woo's official Marketplace SaaS Billing documentation, verified 3 October 2026, establishes the provider mechanics used by this task:

- create a subscription with `POST /subscriptions` and redirect the merchant to the returned `confirmation_url`;
- do not associate the paid plan until the merchant has completed Woo checkout;
- switch an existing contract with `POST /subscriptions/{contractID}` and redirect to the returned `confirmation_url`;
- Woo performs switch proration/renewal-date adjustments itself;
- cancel an existing recurring contract through the provider DELETE endpoint;
- cancellation preserves prepaid entitlement until the provider's prepaid term ends;
- Woo's current SaaS Billing API supports USD only;
- vendor API authentication uses Basic authentication with the Woo-issued application key/secret;
- subscription create/switch responses return the external contract UUID used by Woo returns/webhooks.

Provider reference:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

### Paid `BillingPlan` materialisation boundary

Source review for `ARCH-027-BACKGROUND-002` exposed a durability gap in the earlier wording.

`BillingOperation` snapshots the selected catalogue ID and provider quote, but it does not snapshot every feature/configuration/included-allowance field copied into an operational `BillingPlan`. If paid materialisation waited until the webhook arrived, an Admin catalogue edit between checkout initiation and confirmation could change the operational entitlement/feature projection after the merchant selected the plan.

Therefore paid create/switch MUST reuse/generalise API-001's bounded operational-plan resolver **before provider I/O**:

```text
selected MerchantPricingPlan.id
    -> validate current paid catalogue invariants
    -> resolve/reuse/materialise the single operational BillingPlan
       using current Shopify-equivalent projection semantics
    -> persist BillingOperation intent/quote
    -> commit
    -> call Woo
```

Materialising the operational catalogue snapshot is **not** entitlement activation.

API-003 still MUST NOT update:

```text
Subscription.planId
Subscription.status
Subscription billing/pending fields
BillingPeriod
entitlement counters
```

before verified provider evidence.

BACKGROUND-002 later resolves the already-materialised target through the current schema bridge and updates the Shop's existing unique Subscription only after a trusted webhook receipt.

## Scope

Modify only `moda-interact-api` implementation/tests/OpenAPI/runtime configuration required for these recurring Woo commands, plus the nested `database/` gitlink only when needed to remain on the newest compatible architect-accepted database commit.

Expected implementation areas are conceptually:

```text
src/
  billing/
    commands/
      recurring-subscription-command.service.ts
      recurring-subscription-routes.ts
      recurring-command-schema.ts
      operation-idempotency.ts
      woo-recurring-quote.ts
  woocommerce/
    billing/
      woo-billing-client.ts
      woo-billing-config.ts
      woo-billing-response.ts
openapi/
  woocommerce-billing-commands-v1.yaml
tests/
  ... focused command/provider/idempotency/integration tests
```

Exact repository-local filenames may differ when the accepted API-001/API-002 structure provides clearer existing owners. Do not create duplicate authentication, database, request-parsing or generic HTTP infrastructure.

### Canonical database dependency

Use the accepted `ARCH-027-DATABASE-001` schema already consumed by API-001/API-002.

If the nested API `database/` gitlink is behind the newest compatible architect-accepted database `main`, advance it. Do not move it backwards.

Do not edit Prisma schema/migrations in this task.

### Existing authentication boundary

All three command routes MUST reuse the accepted ARCH-026 `WooInstallationAuthenticator`.

Authoritative tenant identity is only:

```text
X-Moda-Installation-Id + Bearer credential
    -> WooInstallationAuthenticator
    -> principal.shopId
```

The routes MUST NOT accept tenant identity through request body/query/path/domain aliases.

For a normal command, the resolved Shop must satisfy:

```text
Shop.id            = principal.shopId
Shop.platform      = WOOCOMMERCE
Shop.shopifyShopId = NULL
Shop.status        = ACTIVE
Shop.domain        = principal.canonicalSiteUrl
Shop.onboardingCompleted = true
```

Fail closed on impossible principal/Shop mismatches. Do not fall back to a domain lookup.

## Out of Scope

- Local Free activation; owned by `ARCH-027-API-001`.
- Billing/read presentation; owned by `ARCH-027-API-002`.
- Woo one-time top-up charges (`POST /charges`).
- `RecoveryCreditPurchase` creation or activation.
- Refund initiation or settlement.
- Woo billing webhook ingress/signature verification/durable receipt acceptance.
- Background lifecycle reconciliation or entitlement projection.
- Assigning a paid `BillingPlan` to `Subscription` before verified provider evidence.
- Mutating `Subscription.planId`, pending-plan fields, billing periods or entitlement counters from provider command success/browser return.
- Woo Admin/WordPress React/PHP UI implementation.
- Gateway/Render secret wiring.
- Real Woo sandbox certification.
- Free trials in Woo v1.
- Provider-specific retail markups, FX, discounts or price tables.
- Shopify billing implementation changes.
- A generic cross-provider BillingProvider rewrite.
- Changes to `moda-interact-database` schema/migrations other than advancing the nested accepted gitlink when required.

## Requirements

### R1 — Exact public command routes

Implement exactly:

```text
POST   /v1/billing/subscription
POST   /v1/billing/subscription/switch
DELETE /v1/billing/subscription
```

Do not create generic `/provider` command routes in ARCH-027 v1.

All routes return JSON except the external Woo `confirmationUrl`, which is returned as data for the PHP/plugin layer to redirect the browser.

The hosted API MUST NOT issue the merchant browser redirect itself.

### R2 — Required command idempotency header

Every command requires:

```text
Idempotency-Key: <caller-generated key>
```

The key MUST:

- be 1..128 characters after trimming;
- contain only ASCII letters, digits, `.`, `_`, `:`, or `-`;
- be stored unchanged as `BillingOperation.requestKey` after validation;
- be unique per Shop through the accepted database constraint.

Do not synthesize a new key when the header is missing.

Missing/invalid key:

```text
400 invalid_idempotency_key
```

### R3 — Canonical operation fingerprint

Before creating an operation, compute exactly one SHA-256 `requestFingerprint` over a canonical UTF-8 intent string.

Use versioned fields in this exact order:

```text
SUBSCRIPTION_CREATE
arch027-recurring-v1\n
SUBSCRIPTION_CREATE\n
<shopId>\n
<merchantPricingPlanId>\n
<quotedAmountMinor>\n
<quotedCurrency>\n
<quotedBillingPeriod>\n

PLAN_SWITCH
arch027-recurring-v1\n
PLAN_SWITCH\n
<shopId>\n
<providerReference>\n
<merchantPricingPlanId>\n
<quotedAmountMinor>\n
<quotedCurrency>\n
<quotedBillingPeriod>\n

CANCEL
arch027-recurring-v1\n
CANCEL\n
<shopId>\n
<providerReference>\n
```

Values are the validated canonical database values with no locale formatting.

Store the raw 32-byte SHA-256 digest, not hex/base64 text.

The derived provider return URL is not part of the fingerprint because it is deterministic from the operation/Shop and does not define commercial intent.

### R4 — Same-key replay semantics

Within a per-Shop serialized command transaction, first lookup:

```text
BillingOperation
where shopId = locked Shop.id
  and requestKey = Idempotency-Key
```

If found:

1. compare the stored 32-byte fingerprint with the newly calculated fingerprint in constant time where practical;
2. different fingerprint -> `409 idempotency_conflict`;
3. same fingerprint + `AWAITING_CONFIRMATION` -> return the existing operation and existing `confirmationUrl`; MUST NOT call Woo again;
4. same fingerprint + `CONFIRMED` -> return the existing successful command result; MUST NOT call Woo again;
5. same fingerprint + `INITIATING` -> `409 billing_operation_in_progress` with the existing operation ID;
6. same fingerprint + `OUTCOME_UNKNOWN` -> `409 billing_provider_outcome_unknown` with the existing operation ID; MUST NOT retry provider POST/DELETE;
7. same fingerprint + `FAILED` -> `409 billing_operation_failed` with the existing operation ID and bounded safe error code; a deliberate new merchant retry requires a new `Idempotency-Key`.

Never create a second operation for the same `(shopId, requestKey)`. Because the Subscription is unique per Shop, this preserves the same merchant idempotency boundary.

### R5 — Per-Shop recurring-command serialization

Different idempotency keys MUST NOT allow two recurring commands for the same Shop to race past the command gate.

Inside the database transaction, lock in this order:

```text
1. commerce.Shop
2. billing.Subscription
3. read existing Woo recurring operations for the locked `Shop.id`
4. insert the new BillingOperation with required `shopId = Shop.id`
```

Use the repository's accepted bounded row-lock helper or equivalent `SELECT ... FOR UPDATE` implementation.

Do not hold a database transaction open while calling WooCommerce.com.

For a genuinely new command, reject creation when another recurring operation exists for the Shop with:

```text
kind IN (SUBSCRIPTION_CREATE, PLAN_SWITCH, CANCEL)
state IN (INITIATING, AWAITING_CONFIRMATION, OUTCOME_UNKNOWN)
```

with:

```text
409 billing_operation_conflict
```

Additionally, a `CANCEL` operation already `CONFIRMED` blocks conflicting recurring commands until BACKGROUND-002 records verified cancellation durably. Verified `canceled` evidence then leaves the paid Subscription current with `cancelAtPeriodEnd = true`; create/switch remain unavailable until prepaid entitlement actually ends and the current Subscription becomes local Free. A later paid purchase after that terminal transition is the ordinary Free -> paid create flow.

### R6 — Paid target plan validation

For create/switch requests, the only request-body field is:

```json
{
  "merchantPricingPlanId": "..."
}
```

Unknown body fields are rejected.

Load the target by exact `MerchantPricingPlan.id` and require:

```text
isActive = true
planKind = PAID_METERED
allowancePeriod = EVERY_30_DAYS
billingPeriod = EVERY_30_DAYS
recurringAmountMinor is a positive safe integer
currency = USD
includedRecoveryCredits is a non-negative safe integer
```

Do not accept:

```text
shopifyPlanHandle
Woo provider plan handle
browser-supplied price
browser-supplied currency
browser-supplied billing period
browser-supplied provider contract id
```

The command reloads all commercial values from the durable Moda catalogue.

Selecting a `FREE` target through create/switch is rejected with:

```text
409 free_plan_uses_cancellation
```

because Woo Free is local Moda state and a paid merchant reaches Free only after the provider prepaid term actually ends. Selecting Free while paid therefore uses cancellation semantics rather than create/switch.

### R7 — Price parity and exact quote snapshot

For create/switch, quote exactly:

```text
quotedAmountMinor   = MerchantPricingPlan.recurringAmountMinor
quotedCurrency      = MerchantPricingPlan.currency
quotedBillingPeriod = MerchantPricingPlan.billingPeriod
```

No Woo Marketplace surcharge, multiplier, discount, FX conversion or provider-specific price table is allowed in this task.

This is the same Moda retail catalogue amount used for the equivalent Shopify plan.

Woo tax is provider-owned and MUST NOT be predicted or included in `quotedAmountMinor`.

### R8 — Woo billing-period mapping

ARCH-027 v1 supports the current Moda recurring period only:

```text
MerchantPricingBillingPeriod.EVERY_30_DAYS
```

Map it to the Woo provider request as:

```text
billing_period   = "month"
billing_interval = 1
```

The provider financial renewal date is Woo-owned evidence. API-003 MUST NOT mutate allowance synchronously. Woo `month/1` is the financial billing request only; Moda retains an independent exact-30-day entitlement cadence. BACKGROUND-002 reconciles provider lifecycle/financial coverage and BACKGROUND-006 owns due allowance-period rollover. `renewed` never resets included allowance merely because a charge succeeded.

Any future additional Moda billing period requires a separate architecture decision rather than an implicit fallback.

### R9 — Exact provider monetary conversion

`quotedAmountMinor` remains integer minor units in Moda persistence.

For the Woo request, convert USD minor units to a JSON monetary value with exactly cent semantics:

```text
1999 -> 19.99
2000 -> 20.00 commercial value
```

Do not perform percentage calculations, FX or floating multiplication.

Tests must prove representative `.00`, `.01`, `.99` and large safe-integer values do not change the persisted quote.

Provider response monetary fields, when present, are evidence only and do not replace the persisted quote in this task.

### R10 — Provider return URL is server-derived

Do not accept an arbitrary `returnUrl` from WordPress/browser input.

After the operation row exists, derive its Woo `return_url` from the authenticated installation's canonical site URL and the accepted Woo Admin application route:

```text
<canonicalSiteUrl>/wp-admin/admin.php
    ?page=wc-admin
    &path=/moda-interact
    &moda_billing_return=1
    &operation=<BillingOperation.id>
```

Use URL construction/encoding rather than string concatenation for query parameters.

Requirements:

- preserve the canonical site's existing path prefix when WordPress is installed below the origin root;
- production requires HTTPS because ARCH-026 production connection already requires HTTPS;
- never derive the return origin from request headers such as `Host`, `Origin`, or browser input;
- do not include secrets, provider contract ID or raw installation credential in the return URL.

Woo may append its own contract identifier when redirecting the merchant. That browser return is a UX signal only and MUST NOT activate or switch the Moda subscription.

### R11 — Woo provider configuration

Add explicit runtime configuration:

```text
WOO_BILLING_ENVIRONMENT = sandbox | production
WOO_BILLING_API_KEY
WOO_BILLING_API_SECRET
```

Derive the provider base URL from `WOO_BILLING_ENVIRONMENT`; do not accept an arbitrary production base URL from configuration:

```text
sandbox:
https://sandbox.woocommerce.com/wp-json/wccom/billing/1.0/

production:
https://woocommerce.com/wp-json/wccom/billing/1.0/
```

Tests may inject a provider client/mock through repository-local dependency injection; they do not justify a runtime arbitrary-URL escape hatch.

The API key/secret:

- live only in hosted API runtime secret configuration;
- never enter browser/WordPress responses;
- never enter database operation rows;
- never appear in logs/errors/traces;
- never enter committed source/default environment files.

### R12 — Woo provider HTTP client

The provider client MUST:

- use Basic authentication exactly as required by Woo;
- use HTTPS/TLS verification;
- disable redirects;
- use a bounded 10-second request timeout;
- bound response bodies to 64 KiB;
- send/accept JSON only where the provider route does so;
- parse provider errors into bounded internal error codes;
- never log Authorization headers or full provider response bodies;
- make no automatic retry of create, switch or cancel writes.

### R13 — Create command eligibility

`POST /v1/billing/subscription` always means **local Free -> new Woo paid recurring contract**.

Require:

```text
Subscription exists
status = ACTIVE
current plan = FREE
providerSubscriptionId = NULL
billingPeriodId = NULL
```

This includes a Shop that reached Free after an earlier Woo cancellation's prepaid term actually ended. API-003 does not distinguish first-ever paid activation from a later paid purchase after terminal cancellation/end reconciliation.

Persist a new:

```text
BillingOperation
shopId = locked Shop.id
kind = SUBSCRIPTION_CREATE
state = INITIATING
providerReference = NULL
target MerchantPricingPlan + exact quote snapshot
```

and commit before `POST /subscriptions`.

Do not mutate Subscription/BillingPeriod/counters before verified provider activation.

BACKGROUND-002 establishes the paid provider/lifecycle projection after activation and opens the first exact-30-day Moda entitlement period for that new paid term. There is no detached former-period carry-forward or overlapping replacement-contract path.

There is no separate re-subscribe endpoint, request type or scheduled-cancellation replacement-contract state.

### R14 — Switch command eligibility

`POST /v1/billing/subscription/switch` means **existing paid recurring Woo contract -> another paid Moda plan**.

Require:

```text
Subscription exists
status IN (ACTIVE, TRIALING)
current plan resolves to PAID_METERED
providerSubscriptionId is non-null/non-blank
cancelAtPeriodEnd = false
target MerchantPricingPlan.id != current MerchantPricingPlan.id
```

`TRIALING` is accepted only as existing schema compatibility; ARCH-027 v1 does not create Woo trials.

Reject same-plan target:

```text
409 billing_plan_unchanged
```

Create the operation with the current recurring provider contract snapshotted at insertion:

```text
kind = PLAN_SWITCH
state = INITIATING
providerReference = Subscription.providerSubscriptionId
merchantPricingPlanId = target plan id
exact target quote snapshot
```

Resolve/reuse/materialise the target operational `BillingPlan` before provider I/O so the selected plan's feature/allowance projection is frozen consistently with the accepted materialisation boundary.

Do not assign that plan to merchant entitlement state and do not update:

```text
Subscription.planId
Subscription.pendingPlanId
Subscription.pendingShopifyPlanHandle
Subscription.currentPeriodStart/End
BillingPeriod
entitlement counters
```

Then call:

```text
POST /subscriptions/{providerContractId}
```

with the target paid plan details and server-derived return URL.

Woo owns provider financial proration. Moda entitlement changes occur only after verified lifecycle reconciliation.

### R15 — Cancellation eligibility

`DELETE /v1/billing/subscription` accepts no request body and no query parameters.

Cancellation is allowed when the current Shop has a non-null recurring `Subscription.providerSubscriptionId` and the subscription has not already durably recorded `cancelAtPeriodEnd = true`.

The command MUST remain available for a provider-backed subscription in:

```text
ACTIVE
TRIALING
FROZEN
```

so a merchant can cancel a recurring contract even when payment/recovery state prevents a plan switch.

Do not allow cancel on local Free:

```text
409 no_recurring_subscription
```

Create:

```text
kind = CANCEL
state = INITIATING
providerReference = current Subscription.providerSubscriptionId
all plan/quote/purchase fields = NULL
```

Commit before calling Woo.

Then call the provider DELETE subscription endpoint for that exact contract.

A definite successful DELETE confirms the provider command but does not itself mutate Moda state. Verified `canceled` reconciliation in BACKGROUND-002 keeps the current paid plan/provider contract/BillingPeriod active, sets `cancelAtPeriodEnd = true`, and records the signed prepaid end as `providerCoverageEndAt`. Paid -> Free occurs only on terminal prepaid-end reconciliation (or the durable local signed-end-date safety net owned by BACKGROUND-006).

Do not modify:

```text
Subscription.cancelAtPeriodEnd
Subscription.status
Subscription.planId
Subscription.providerSubscriptionId
BillingPeriod
entitlement counters
```

in this task. Verified Woo lifecycle reconciliation later projects cancellation/prepaid-term end.

### R16 — Provider create/switch success handling

A successful Woo create/switch response must contain:

```text
non-blank external contract UUID/reference
non-blank HTTPS confirmation_url
```

Validate the confirmation URL host against the selected environment:

```text
sandbox.woocommerce.com
or
woocommerce.com
```

Do not return an arbitrary provider-controlled redirect host to the plugin.

Before attaching a newly returned provider contract ID to a `SUBSCRIPTION_CREATE`, verify that any existing `BillingOperation` rows using that contract ID resolve through `operation.shopId` to the same Shop. A cross-Shop conflict is an integrity/security failure.

On valid success, update the operation with bounded compare-and-set semantics:

```text
INITIATING
    -> AWAITING_CONFIRMATION
providerReference: NULL -> returned contract ID   # create only
confirmationUrl: null -> validated provider URL
lastErrorCode = null
```

For `PLAN_SWITCH`, `providerReference` was already snapshotted and the returned contract ID, when the provider returns one, must match it. A mismatch is `OUTCOME_UNKNOWN`/integrity failure and MUST NOT redirect the merchant.

Return:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "kind": "SUBSCRIPTION_CREATE",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

Do not return `providerReference`, request fingerprints, credentials or provider raw payloads.

The command response/merchant browser return MUST NOT mark the operation `CONFIRMED` and MUST NOT activate the paid plan.

### R17 — Provider cancellation success handling

On a definite successful provider DELETE:

```text
INITIATING -> CONFIRMED
confirmationUrl remains NULL
lastErrorCode = NULL
```

Return:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "kind": "CANCEL",
  "state": "CONFIRMED",
  "confirmationUrl": null
}
```

`CONFIRMED` here means only that Woo accepted the cancellation command. It does not mean the prepaid term has ended or that Moda has changed plan.

### R18 — Ambiguous provider outcome

If a provider write may have succeeded but Moda cannot prove whether it did, set:

```text
state = OUTCOME_UNKNOWN
lastErrorCode = bounded safe code
```

Examples include:

- request timeout after send;
- connection reset after request body was sent;
- provider 5xx where contract creation/mutation cannot be excluded;
- malformed/truncated successful response after a create/switch may have completed;
- create success response with a suspicious cross-Shop provider-contract collision;
- switch response returning a different recurring contract ID from the snapshotted target.

Do not automatically retry the provider write.

Return:

```text
502 billing_provider_outcome_unknown
```

with operation ID and no raw provider body.

### R19 — Definite provider rejection

When a complete provider response definitively rejects the request before a successful result is established, set:

```text
state = FAILED
lastErrorCode = bounded normalized code
```

Examples may include validated provider 4xx responses such as invalid credentials/request/rate limit.

Do not store the complete provider response body.

Return an appropriate bounded API error without provider secrets or customer/payment data.

A later deliberate retry uses a new idempotency key.

### R20 — Compare-and-set result updates

Provider result updates MUST NOT blindly overwrite a state that a concurrent later provider-evidence path has already advanced.

Update result fields only when the operation is still in the expected source state, normally:

```text
state = INITIATING
```

If zero rows are updated, re-read the operation and return/continue according to the newer durable state rather than overwriting it.

This requirement preserves future webhook/reconciliation race safety.

### R21 — No paid subscription projection before verified evidence

Create/switch command success and browser return are not entitlement proof.

This task MUST NOT write paid activation/change state into:

```text
Subscription.planId
Subscription.pendingPlanId
Subscription.observedShopifyPlanHandle
Subscription.pendingShopifyPlanHandle
Subscription.currentPeriodStart
Subscription.currentPeriodEnd
Subscription.status
BillingPeriod
BillingPeriodEntitlementCounter
ShopEntitlementCounter
```

The unresolved Woo operation is the durable pending intent consumed by API-002's presentation overlay.

A later Background lifecycle task owns verified provider projection.

### R22 — No top-up/refund behaviour

This task MUST NOT implement:

```text
POST /charges
RecoveryCreditPurchase creation
RecoveryCreditRefund initiation/settlement
MerchantPricingUsageEvent purchase validation
maximumUnitsPerBillingPeriod semantics
```

Those belong to separate bounded ARCH-027 tasks.

### R23 — No webhook ingress

This task MUST NOT expose or process Woo billing webhooks.

Do not create `WooCommerceBillingWebhookReceipt` rows here.

Webhook signature verification/durable acceptance remains a separate API task.

### R24 — Structured logging and telemetry

Use the existing shared structured logger if available in the accepted API dependency version; do not create a competing generic logger.

Logs may include bounded identifiers:

```text
shopId
billingOperationId
operationKind
operationState
merchantPricingPlanId
providerEnvironment
safe error code
```

Do not log:

```text
Authorization header
Woo API key/secret
installation bearer credential
provider raw response body
confirmation URL query strings if they may contain provider identifiers
customer/payment information
```

Use existing framework/OpenTelemetry HTTP client/server instrumentation where it already provides equivalent technical telemetry. Do not create duplicate generic HTTP metrics merely for this task.

## Work Items

- [x] Add strict schemas/routes for `POST /v1/billing/subscription`, `POST /v1/billing/subscription/switch`, and `DELETE /v1/billing/subscription`.
- [x] Reuse accepted Woo installation authentication and principal-derived `shopId` only.
- [x] Add strict `Idempotency-Key` validation and per-Shop same-key replay semantics.
- [x] Add exact versioned SHA-256 operation fingerprint construction for create/switch/cancel.
- [x] Add per-Shop recurring-command serialization using Shop -> Subscription lock order and unresolved-operation gating.
- [x] Add server-side paid `MerchantPricingPlan` validation with no client-controlled price/provider identity.
- [x] Snapshot exact same-catalogue recurring price/currency/period into `BillingOperation`.
- [x] Add deterministic `EVERY_30_DAYS -> month/1` Woo financial-period mapping.
- [x] Add exact minor-unit -> Woo USD monetary conversion with focused tests.
- [x] Add server-derived Woo return URL using the accepted canonical site and Woo Admin route.
- [x] Add Woo billing runtime configuration for sandbox/production plus API key/secret.
- [x] Add bounded Woo Billing API client with Basic auth, TLS, no redirects, timeout/body limits and no automatic write retries.
- [x] Implement the single Free -> paid `SUBSCRIPTION_CREATE` intent persisted before `POST /subscriptions`; after a previous cancellation this path is available only once prepaid entitlement has actually ended and the current Subscription is Free.
- [x] Implement paid -> paid `PLAN_SWITCH` intent persisted before `POST /subscriptions/{contractID}`.
- [x] Implement provider-backed cancellation intent persisted before provider DELETE.
- [x] Implement exact success/FAILED/OUTCOME_UNKNOWN operation transitions with compare-and-set updates.
- [x] Ensure create/switch success exposes confirmation URL but does not activate/change the Moda subscription.
- [x] Ensure successful cancel does not end prepaid Moda entitlement synchronously.
- [x] Add cross-Shop provider-contract collision protection for newly returned create contracts.
- [x] Update OpenAPI with exact request/response/error/idempotency contracts, including confirmed replay responses.
- [x] Add focused provider-client, route, database integration, concurrency and failure tests.

## Interfaces / Contracts

### Public hosted API

Authenticated commands:

```text
POST /v1/billing/subscription
body: { merchantPricingPlanId }
header: Idempotency-Key

POST /v1/billing/subscription/switch
body: { merchantPricingPlanId }
header: Idempotency-Key

DELETE /v1/billing/subscription
body: none
query: none
header: Idempotency-Key
```

Successful create/switch response:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "kind": "SUBSCRIPTION_CREATE | PLAN_SWITCH",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

Successful cancel response:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "kind": "CANCEL",
  "state": "CONFIRMED",
  "confirmationUrl": null
}
```

No response exposes Woo vendor credentials or recurring provider contract ID.

### Durable command contract

Owner:

`ARCH-027-DATABASE-001`

Consumed fields:

```text
BillingOperation
MerchantPricingPlan
Subscription
Shop
WooCommerceInstallation
```

This task consumes the database contract; it does not redefine it.

### Woo provider contract

External provider routes used:

```text
POST   /subscriptions
POST   /subscriptions/{contractID}
DELETE /subscriptions/{contractID}
```

Authentication:

```text
Authorization: Basic base64(api_key:api_secret)
```

ARCH-027 v1 provider plan payload is derived from:

```text
name             <- MerchantPricingPlan.displayName
price            <- recurringAmountMinor converted from USD minor units
billing_period   <- "month"
billing_interval <- 1
return_url       <- server-derived canonical Woo Admin return URL
```

No free trial is requested in ARCH-027 v1.

## Dependencies

- `ARCH-027-API-002`

API-002 must be architect-accepted Complete before this task becomes Ready so the command task can reuse the accepted authentication, Shop/catalogue mapping and Shopify-parity presentation semantics rather than independently redefining them.

Through API-002/API-001, this task also requires the accepted ARCH-027 database schema and ARCH-026 installation-authentication foundation.

## Enables

- `ARCH-027-WOOCOMMERCE-001`

The Woo merchant plan-management UI needs both the API-002 presentation state and these recurring provider commands.

Later webhook/background tasks may also consume the operations created here but are not made Ready solely by this task; their verified-evidence contract remains separately architected.

## Acceptance Criteria

- [x] All three exact recurring command routes exist and require the accepted Woo installation principal.
- [x] No route accepts `shopId`, site/domain identity, provider contract ID, price, currency or billing period from merchant input.
- [x] Every command requires a valid `Idempotency-Key` and stores it as the per-Shop operation request key.
- [x] Canonical request fingerprints exactly follow the task's versioned field ordering and are stored as 32-byte SHA-256 values.
- [x] Same key/same fingerprint replays never issue a second provider write, including `CONFIRMED` create/switch replay.
- [x] Same key/different fingerprint returns `409 idempotency_conflict`.
- [x] Concurrent different-key recurring commands for the same Shop serialize and at most one new unresolved recurring operation is created.
- [x] No provider network call occurs while the recurring-command database transaction is open.
- [x] Create is allowed only from a valid ACTIVE local Free subscription with no recurring provider contract.
- [x] Create rejects an existing provider-backed paid subscription.
- [x] Switch is allowed only for an existing ACTIVE/TRIALING paid subscription with a non-blank recurring provider contract and no scheduled cancellation.
- [x] A verified scheduled cancellation (`cancelAtPeriodEnd=true`) keeps the paid subscription current but blocks create/switch until prepaid entitlement actually ends; a historical confirmed cancellation permits create only after terminal local Free projection.
- [x] Switch rejects the same target plan.
- [x] Create/switch reject a Free target and direct merchants to cancellation semantics.
- [x] Cancel is rejected for local Free/no recurring provider contract.
- [x] Cancel remains allowed for provider-backed ACTIVE/TRIALING/FROZEN subscriptions.
- [x] Target paid plan is loaded by `MerchantPricingPlan.id` and satisfies all exact task eligibility rules.
- [x] Woo recurring quote exactly equals the stored Moda catalogue recurring amount/currency; no Woo-specific markup/discount/FX is introduced.
- [x] `EVERY_30_DAYS` maps only to Woo monthly interval 1.
- [x] Provider return URL is derived server-side from the authenticated canonical Woo site and operation ID; arbitrary merchant `returnUrl` input is impossible.
- [x] Sandbox and production Woo Billing base URLs are selected only through the bounded environment enum.
- [x] Woo API key/secret never enter database rows, browser responses, logs or committed files.
- [x] Provider client uses Basic auth, TLS, no redirects, 10-second timeout, 64-KiB response bound and no automatic write retry.
- [x] New create operation is committed in `INITIATING` before `POST /subscriptions`.
- [x] New switch operation is committed in `INITIATING` with the existing recurring contract snapshot before `POST /subscriptions/{contractID}`.
- [x] New cancel operation is committed in `INITIATING` with the existing recurring contract snapshot before provider DELETE.
- [x] Create/switch provider success transitions to `AWAITING_CONFIRMATION`, stores immutable contract/confirmation evidence and returns only the bounded confirmation response.
- [x] Successful provider DELETE transitions only the operation to `CONFIRMED`; later verified `canceled` lifecycle schedules prepaid term end without immediately returning Moda to Free.
- [x] Browser/provider command success does not update `Subscription.planId`, BillingPeriod or entitlement counters.
- [x] Definite provider rejection becomes `FAILED` with bounded safe error evidence.
- [x] Ambiguous provider outcome becomes `OUTCOME_UNKNOWN` and is never automatically retried.
- [x] Malformed successful create/switch response is treated as ambiguous rather than as a definite failed create.
- [x] A newly returned create contract ID already associated with another Shop fails closed and is not returned as a merchant confirmation redirect.
- [x] Plan-switch returned contract identity cannot silently change from the current recurring provider contract.
- [x] Provider result state updates use compare-and-set/re-read semantics and do not overwrite newer durable state.
- [x] This task creates no `RecoveryCreditPurchase`, `RecoveryCreditRefund` or webhook receipt; paid BillingPlan materialisation/reuse is allowed only as the non-entitlement catalogue snapshot required by the accepted materialisation boundary.
- [x] OpenAPI exactly documents the command, idempotency and bounded error contracts, including HTTP 200 confirmed replay and HTTP 202 awaiting confirmation.

## Validation

Inspect the accepted `moda-interact-api/package.json` before execution and run the scripts actually declared there plus focused tests introduced by this task.

Required validation categories:

- [x] focused route schema/authentication tests for all three commands;
- [x] `Idempotency-Key` grammar/bound tests;
- [x] fingerprint golden-vector tests for create/switch/cancel;
- [x] same-key replay and different-fingerprint conflict tests, including confirmed create/switch replay;
- [x] concurrent different-key per-Shop serialization integration test against disposable PostgreSQL;
- [x] Shop/principal tenant-isolation and impossible-mapping failure tests;
- [x] paid catalogue eligibility tests including inactive/Free/non-USD/invalid period/invalid amount rejection;
- [x] exact price-parity/minor-unit conversion tests;
- [x] server-derived return URL tests including WordPress sub-path site URLs and no arbitrary origin injection;
- [x] sandbox/production provider configuration validation tests;
- [x] controlled Woo client tests proving Basic auth, no redirects, timeout/body/media-type/error bounds and secret redaction;
- [x] create success test proving operation committed before provider call and no Subscription mutation;
- [x] switch success test proving same recurring contract is targeted and no Subscription/pending-plan mutation;
- [x] cancel success test proving provider command confirmation alone does not change Moda state; the subsequent BACKGROUND-002 verified-lifecycle projection is validated by its owning task and integrated system tests, not by API-003;
- [x] create/switch definite rejection -> FAILED tests;
- [x] create/switch/cancel timeout/5xx/malformed-success -> OUTCOME_UNKNOWN tests and proof of no automatic retry;
- [x] provider contract cross-Shop collision negative test;
- [x] compare-and-set race test showing provider result cannot overwrite a newer operation state;
- [x] Prisma client generation from the pinned accepted database schema;
- [x] repository `npm test` or declared focused equivalent;
- [x] repository `npm run typecheck` when declared;
- [x] repository `npm run lint` when declared;
- [x] repository `npm run build` when declared;
- [x] `git diff --check`;
- [x] changed-file/repository diagnostics required by `moda_api`;
- [x] clean dedicated parent and implementation task worktree evidence recorded in the Completion Report.

Provider HTTP tests MUST use controlled mock/provider fixtures. Real Woo sandbox certification belongs to the later terminal/sandbox task and is not required to implement this command boundary.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> set task status to review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo UI, top-up, webhook or Background reconciliation work.

## Implementation Notes

Keep the command boundary deliberately asymmetric:

```text
Free
    local Moda state
    no Woo recurring contract

Paid create/switch/cancel
    durable Woo operation
    provider command
    verified provider evidence later changes Moda projection
```

Do not force paid command initiation through the Shopify `BillingProvider` abstraction. ARCH-027 is intentionally adapting Woo around the existing platform rather than rewriting Shopify billing into a generic provider framework.

Resolve/reuse/materialise the selected paid operational `BillingPlan` before opening Woo checkout, using the same current projection validation/mapping semantics as API-001/Shopify. This freezes operational feature/allowance state but MUST NOT assign the plan to the Shop's Subscription until verified provider confirmation.

Woo switch proration changes provider financial dates/charges. It must not synchronously reset Moda recovery usage or included capacity.

A confirmation URL is transient merchant-navigation data backed by the durable operation. It is not entitlement proof.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `moda-interact-api/scripts/test-woocommerce-installation-postgres.mjs`
- `moda-interact-api/src/index.ts`
- `moda-interact-api/src/runtime-config.ts`
- `moda-interact-api/src/runtime-config.test.ts`
- `moda-interact-api/src/billing/commands/recurring-command-primitives.ts`
- `moda-interact-api/src/billing/commands/recurring-command-primitives.test.ts`
- `moda-interact-api/src/billing/commands/recurring-openapi-contract.test.ts`
- `moda-interact-api/src/billing/commands/recurring-subscription-command.service.ts`
- `moda-interact-api/src/billing/commands/recurring-subscription-command.postgres.test.ts`
- `moda-interact-api/src/woocommerce/billing/initial-free-activation.service.ts`
- `moda-interact-api/src/woocommerce/billing/initial-free-activation.service.test.ts`
- `moda-interact-api/src/woocommerce/billing/woo-billing-client.ts`
- `moda-interact-api/src/woocommerce/billing/woo-billing-client.test.ts`
- `moda-interact-api/src/woocommerce/billing/woo-billing-config.ts`
- `moda-interact-api/src/woocommerce/installation/routes.ts`
- `moda-interact-api/src/woocommerce/installation/routes.test.ts`
- `moda-interact-api/openapi/woocommerce-billing-commands-v1.yaml`

### Work Completed

- Added the authenticated create, switch and cancel routes with strict request handling, principal-derived tenancy, required idempotency keys and bounded no-store responses.
- Added per-Shop serialized durable command handling, canonical fingerprints and same-key replay/conflict behavior. Operations and the exact catalogue quote are committed before provider I/O; provider results update only the operation using compare-and-set semantics.
- Added paid catalogue eligibility and operational plan materialization without changing the active Subscription projection, plus Woo sandbox/production configuration and a bounded HTTPS client with Basic auth, manual redirect rejection, timeout/response limits and no automatic write retry.
- Added failure/outcome classification, cross-Shop returned-contract collision protection, and server-derived Woo return URLs. Cancellation confirmation does not end prepaid Moda entitlement.
- Addressed A1-R1: a historical `CANCEL/CONFIRMED` continues to block new recurring commands while the paid Subscription remains current, including verified scheduled cancellation. A new create is allowed only after the locked Subscription is durably ACTIVE Free with no provider contract, no billing period and no scheduled cancellation. PostgreSQL regression coverage proves the paid state blocks create/switch, terminal Free allows exactly one new provider create with a new key, the confirmed cancel remains auditable, and the new intent does not mutate Free entitlement state.
- Addressed A1-R2: create/switch OpenAPI now documents HTTP 202 for `AWAITING_CONFIRMATION` and HTTP 200 for persisted `CONFIRMED` replay. Route/OpenAPI tests and PostgreSQL service tests cover both operation kinds, no second provider write and no entitlement mutation.
- Addressed A1-R3 by reconciling Work Items, Acceptance Criteria and Validation checklists below against implementation and executed evidence. The clarified BACKGROUND-002 projection remains owned by its task and is not treated as an API-003 dependency.
- Added OpenAPI documentation and focused unit, route, provider, contract and PostgreSQL integration coverage. No database schema or migration changes were required; the database submodule gitlink was not changed.
- Prepared execution evidence: dependency gate passed for `ARCH-027-API-002` (Complete). The canonical workspace was `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; the dedicated parent worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-API-003` on `task/ARCH-027-API-003`, and the dedicated implementation worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-API-003` on the same task branch. Both were newly created, not reused; task-branch fast-forward was not needed and `origin/main` was already incorporated in both. The shared workspace and implementation source checkout were not used for task edits.
- Launcher initialized recursive implementation submodules successfully; the `database` gitlink was initialized at `e86b16027595af663eab5ba5fb23745435307372`. Attempt 1 was claimed by `copilot` at `2026-10-09T00:13:54Z`; the parent claim commit `ad5f9f2f4d04c89fc81cf316bb4df6b0b2967fe5` was committed and pushed. Initial parent and implementation heads were `a6853f69f24911b12415d588b32f0491ee43c023` and `eeef9d49e658f55e78e203d3bcbe1c047206e8df`, respectively.
- Attempt 2 launcher evidence: previous attempt 1; claim by `copilot` at `2026-10-09T01:38:51Z`, parent claim commit `8d947adafb703d759c319f993c65ca138c45477e` pushed. The exact dedicated parent and implementation worktrees were reused on `task/ARCH-027-API-003`; task-branch fast-forward was not needed and `origin/main` was already incorporated. The canonical workspace remained `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; prepared parent head `9c81dc3f6ab9a06529bf3dcd68ed7d4e3d6034b0`, implementation head `e8cd6777899c114ff359f3918e51aa58d252a226`. Recursive submodule sync/update passed and the `database` gitlink remained initialized at `e86b16027595af663eab5ba5fb23745435307372`.
- Attempt 2 implementation correction commit `bdf14fb4bbc6aedff2d1baf22ca649dfef2d967d` was pushed to `origin/task/ARCH-027-API-003`; the remote branch was verified at that commit and the implementation worktree was clean.

### Validation Results

- `npm test`: 103 passed, 0 failed, 22 database-only tests skipped in the non-integration run.
- `npm run test:integration`: passed all disposable PostgreSQL suites; API-003 command integration suite 7/7, including A1-R1 terminal-cancellation and A1-R2 confirmed-replay coverage.
- Focused route/OpenAPI tests: 15 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run build`: passed.
- `git diff --check`: passed after implementation edits; the final task-report edit is checked before publication.
- Prisma Client generation from the pinned accepted database schema: passed.
- Changed-file diagnostics: no errors found in all four modified TypeScript source/test files; repository lint/typecheck also passed.
- Provider HTTP behavior was validated with controlled mocks; no live Woo sandbox certification was attempted, as that belongs to the later certification task.

### Deviations

- No schema migration was needed because the accepted `BillingOperation` and catalogue persistence contracts covered the command boundary. The required cancel lifecycle projection by BACKGROUND-002 is intentionally not implemented here; cancellation command success changes only the operation and awaits verified provider lifecycle evidence.
- API-003 does not independently execute BACKGROUND-002's verified lifecycle projection; the task's clarified Validation criterion assigns that evidence to BACKGROUND-002 and its integrated system tests.

### Assumptions

- Woo's published SaaS Billing create/switch/cancel flow and USD-only restriction remain as documented when implementation begins.
- ARCH-027 v1 uses the existing Moda `EVERY_30_DAYS` recurring product period and maps it to Woo's monthly provider financial interval.
- Woo vendor credentials are supplied later through architecture-approved hosted API deployment secret wiring.
- API-002's accepted current-plan/catalogue mapping helpers are available for reuse.

### Unresolved Issues

- Exact live provider payload/response edge cases remain subject to later Woo sandbox certification; the task uses controlled mocks and the published provider contract meanwhile.
- No client idempotency key is documented by Woo for these provider writes, so `OUTCOME_UNKNOWN` remains required for ambiguous response loss.
- `npm ci` reported three high-severity dependency audit advisories. They were not modified as part of this bounded task.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested — Attempt 2 (2026-10-09). A1-R1, A1-R2 and A1-R3 are verified resolved; A2-R1 requires correction.

### Review Notes

#### Attempt 2 review — verification and new A2-R1 finding

Reviewed the exact uploaded `ARCH-027-API-003` Attempt 2 source and report, with Git blob identity matching implementation commit `bdf14fb4bbc6aedff2d1baf22ca649dfef2d967d` and parent report commit `99ec43e42449b3f27a6daa2e2f6ebf1ac5a09959` on their respective task branches. A1-R1 is corrected for terminal local Free -> paid create, A1-R2 is corrected for HTTP 200 confirmed create/switch replay versus HTTP 202 pending confirmation, and A1-R3 is corrected with 21/21 Work Items, 37/37 Acceptance Criteria and 26/26 Validation checkboxes checked and updated launcher evidence. The submitted tests cover those bounded corrections, but stop immediately after the subsequent paid create; they do not test later commands on that new provider contract.

**A2-R1 — Historical confirmed cancellation of provider contract A blocks switch/cancel of later provider contract B (source and real-PostgreSQL regression correction required).**

In `src/billing/commands/recurring-subscription-command.service.ts`, `persistIntent()` reads all recurring operations for the Shop with only `{ kind, state }`, then computes `hasConfirmedCancellation` using any historical `CANCEL/CONFIRMED`. The new `canCreateAfterTerminalCancellation` exception permits a fresh `SUBSCRIPTION_CREATE` after terminal Free, but applies **only** when `kind === SUBSCRIPTION_CREATE` and the Subscription is Free. After provider B's verified activation makes the same Subscription paid and assigns B's provider reference, the old confirmed cancellation for A still unconditionally rejects `PLAN_SWITCH` and `CANCEL` with `409 billing_operation_conflict`, contrary to R5, R14 and R15 and the ARCH-027 contract-identity isolation invariant. The historical cancellation must remain auditable but must not govern a distinct subsequent provider contract.

Correct the confirmed-cancellation fence by distinguishing the provider contract being cancelled from the Shop's **current** provider contract and authoritative local subscription lifecycle. Preserve blocking of competing commands during the current contract's unprojected `CANCEL/CONFIRMED` state and during its verified scheduled cancellation, including `cancelAtPeriodEnd=true`; preserve the terminal-Free eligibility fence, all unresolved-operation gating, Shop lock ordering, idempotency and no external network I/O inside transactions. Historical `CANCEL/CONFIRMED` operations for *earlier, different* provider references must not block commands on a newly activated paid contract. Avoid relying on a global has-ever-cancelled flag or deleting audit history to unblock.

Extend the **disposable PostgreSQL** lifecycle regression through the next term: contract A `CANCEL/CONFIRMED` -> verified scheduled cancellation (new create/switch still blocked) -> terminal Free -> new `SUBSCRIPTION_CREATE` for B -> independently simulate verified B paid activation and completion of B's create operation -> exercise distinct new-key `PLAN_SWITCH` and `CANCEL` against B without interference from A's historical cancellation. Respect the unresolved-operation gate when ordering these actions (separate fixtures or reconcile the intermediate switch). Assert each valid command targets B's contract reference, creates one operation/one provider write, does not synchronously change entitlement or counters, and leaves A's cancellation immutable. Also retain a negative regression that an unprojected/active cancellation for **the current contract** continues to fail closed. Do not alter database schema, WooCommerce UI, or BACKGROUND-002's lifecycle ownership.

#### Changes Requested — Attempt 1 (2026-10-09): historical review preserved

The implementation was reviewed against the ARCH-027 parent architecture, this task's requirements, the submitted snapshot and both pushed task commits: implementation `e8cd6777899c114ff359f3918e51aa58d252a226`, parent report `bdefcc4c5c8902011c669f53c3cc7ac2e37a889f` (following `8ee4a559efe55f2f1c9f68a242acdb459451a51d`). The new hosted API command boundary is largely aligned: authenticated Shop-scoped commands, Shop -> Subscription locking, operation intent before provider I/O, bounded Woo client configuration, CAS updates and no synchronous subscription entitlement changes. The following corrections are required within the same task scope.

**A1-R1 — Historical `CONFIRMED` cancellation permanently prevents legitimate Free -> paid resubscription (source and test correction required).**

`src/billing/commands/recurring-subscription-command.service.ts`, `persistIntent()`: the operation gate rejects whenever *any* historical `CANCEL` is `CONFIRMED`. It does so even after BACKGROUND-002 / the prepaid-end safety net has durably projected the Shop's subscription back to ACTIVE local Free, cleared the provider contract and ended its BillingPeriod. This contradicts R5 and R13 and the parent ARCH-027 terminal-cancellation lifecycle. Distinguish an unprojected/scheduled cancellation that must block competing recurring commands from historical cancellation evidence after an established terminal Free transition. Preserve the existing durable cancellation operation for audit, reject replacement contracts while current paid entitlement remains active, and permit a new `SUBSCRIPTION_CREATE` only after the current subscription satisfies *all* Free-create predicates. Add real-Prisma disposable-PostgreSQL regression coverage: `CANCEL` CONFIRMED -> verified scheduled paid cancellation remains blocked -> final local Free projection permits a new paid create with a new request key, without double provider writes or premature subscription/counter changes. Preserve same-key replay and different-key serialization.

**A1-R2 — Create/switch `CONFIRMED` replay is not represented in OpenAPI (contract and test correction required).**

The task's R4 explicitly permits replay of a `CONFIRMED` operation. `operationResponse()` returns that persisted state, and `routes.ts` sends HTTP 200 for `CONFIRMED`, even when the kind is `SUBSCRIPTION_CREATE` or `PLAN_SWITCH`. `openapi/woocommerce-billing-commands-v1.yaml` documents only HTTP 202 with a `ConfirmationResult.state` fixed at `AWAITING_CONFIRMATION` for both POST routes. Align the public OpenAPI response status/schema with the actual, architecture-authorised successful confirmed replay; preserve 202 for newly awaiting merchant confirmation and 200 for cancellation. Add contract and route/service regressions explicitly covering CONFIRMED create/switch replay with no new provider write and no entitlement mutation. Do not falsify persisted state to fit the current OpenAPI schema.

**A1-R3 — Submitted Work Items, Acceptance Criteria and Validation evidence are unreconciled (task report correction required).**

All 21 Work Items, 37 Acceptance Criteria and 26 Validation checkbox items are unchecked while the Completion Report asserts successful work and tests. Update only supported checkboxes after correcting A1-R1/R2 and rerunning required checks. Record any true exceptions with specific justification rather than checking unexecuted validation. In particular, the API-003-only cancellation test is required, but the later BACKGROUND-002 verified provider projection is *not* an executable API-003 validation dependency; its validation checkbox has been narrowly clarified above to prevent a backward task dependency. Preserve the existing launcher preparation and physical-isolation evidence and accurately record the next attempt.

Three high-severity dependency audit advisories were disclosed by the repository agent; they do not independently block this bounded architectural review and have not been attributed to this task.

### Reviewed Files

Attempt 2: re-inspected the updated command writer and PostgreSQL lifecycle scenarios, OpenAPI 200/202 contract, route/OpenAPI tests, parent ARCH-027 contract-lifecycle requirements, Completion Report and task dependency definitions. Verified the four changed source/test blobs and task report against the pushed task branches.

The Attempt 1 reviewed-file inventory follows unchanged:

- `src/billing/commands/recurring-subscription-command.service.ts`
- `src/billing/commands/recurring-subscription-command.postgres.test.ts`
- `src/billing/commands/recurring-command-primitives.ts`
- `src/billing/commands/recurring-openapi-contract.test.ts`
- `openapi/woocommerce-billing-commands-v1.yaml`
- `src/woocommerce/installation/routes.ts`
- `src/woocommerce/billing/woo-billing-client.ts`
- `src/woocommerce/billing/woo-billing-config.ts`
- `src/woocommerce/billing/initial-free-activation.service.ts`
- `scripts/test-woocommerce-installation-postgres.mjs`
- `package.json`, parent ARCH-027 architecture, task definition and Completion Report.

### Validation Reviewed

Attempt 2 submitted evidence: `npm test` 103 passed/22 database-only skips; disposable `npm run test:integration` including API-003 suite 7/7; focused route/OpenAPI 15/15; typecheck, lint, build and `git diff --check` passed. The regression assertions and command writer were inspected. These reported test executions were **not independently rerun** here: the uploaded source snapshot has no `node_modules` and this environment has Node 22 rather than the repository-declared Node 24 and does not provide Docker/PostgreSQL CLI tools. A2-R1 is a source-established untested new-contract lifecycle case despite the green supplied suites. The completion report's physical-isolation, launcher and submodule evidence is sufficient for this review.

Attempt 1 validation record (historical):

The implementing agent reports: `npm test` 103 passed/22 database-only skips; `npm run test:integration` API-003 PostgreSQL suite 7/7; `npm run typecheck`, `npm run lint`, `npm run build` and `git diff --check` passed. Inspected the submitted test source, harness registration, provider-client tests and report. This review environment does not contain the repository's installed dependencies or PostgreSQL/Docker tooling and has Node 22 rather than the repository-declared Node 24, so those test suites were not independently rerun. The missing terminal-cancellation and confirmed-POST contract cases remain unvalidated. Snapshot code/task file hashes matched the corresponding pushed task-branch blobs.

### Architecture Conformance

Attempt 2: A1-R1/R2/R3 meet the original corrections. The command system remains partially conforming because A2-R1 permits the audit row for a previous cancelled contract to block both switch and cancellation of a newer valid paid contract. This violates the current-contract lifecycle/tenant isolation of ARCH-027 R5/R14/R15. No schema or additional service ownership change is needed. The known three high-severity dependency audit advisories are outside this bounded defect absent evidence of task-introduced regressions.

Attempt 1 conformance record (historical):

Partially conforming. The command/operation/provider boundaries and no-entitlement-before-verification rule are respected. A1-R1 violates the explicitly approved eventual Free -> paid pathway following terminal cancellation; A1-R2 violates public command contract fidelity. Task-state documentation requires reconciliation under A1-R3. No new database migration or new cross-repository contract is requested for these corrections.

### Follow-up

**Attempt 2 decision: Changes Requested.** Return this same task to `ready` with `executor: null`, `claimed_at: null`, preserving `attempt: 2`, so the next authorized launcher claim records Attempt 3. `moda_api` corrects A2-R1 only, adds the real-Prisma cancellation-A -> new paid-B -> switch/cancel-B regressions, reruns focused, required repository and disposable PostgreSQL validation, updates the Completion Report and republishes both mirrored task branches. A1-R1/R2/R3 remain resolved and need no unrelated code churn. `ARCH-027-API-004` and `ARCH-027-WOOCOMMERCE-001` remain Pending/dependency-gated. No domain/architecture `_index.md` reconciliation until the user explicitly requests architecture-session finalization.

Attempt 1 follow-up (historical, preserved):

Return the **same** `ARCH-027-API-003` task to `ready`, clear `executor`/`claimed_at`, and preserve `attempt: 1` so the next launcher claim creates Attempt 2. `moda_api` owns bounded A1-R1/R2 source and regression changes plus A1-R3 task-record reconciliation. Run the focused and repository-required validation, including real disposable PostgreSQL tests, and republish the mirrored implementation and parent task report for review. Do not start API-004 or WooCommerce UI work: `ARCH-027-API-004` and `ARCH-027-WOOCOMMERCE-001` remain dependency-gated until this task is Accepted and Complete. Do not create or modify any `docs/decisions/**/_index.md` files before final architecture-session reconciliation.
