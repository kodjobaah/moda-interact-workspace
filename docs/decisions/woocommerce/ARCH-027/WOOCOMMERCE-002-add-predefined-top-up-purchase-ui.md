---
id: ARCH-027-WOOCOMMERCE-002
architecture_id: ARCH-027
title: Add predefined WooCommerce recovery-credit top-up purchasing
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-WOOCOMMERCE-001
  - ARCH-027-API-004
enables:
  - ARCH-027-WOOCOMMERCE-003
created: 2026-10-03
updated: 2026-10-03
---

# Add predefined WooCommerce recovery-credit top-up purchasing

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extend the accepted ARCH-027 Woo Billing surface with the **real predefined recovery-credit top-up purchase flow**.

The merchant experience is:

```text
Billing
  -> purchased-credit balance
  -> predefined bundle cards
  -> Buy one bundle
  -> local WordPress REST
  -> hosted API-004
  -> Woo one-time-charge confirmation
  -> return to Billing
  -> durable top-up state refresh
```

One click always means:

```text
one MerchantPricingUsageEvent
one predefined bundle
one RecoveryCreditPurchase
one Woo ONE_TIME_CHARGE
```

There is deliberately:

```text
no quantity field
no quantity stepper
no tier calculation
no browser price calculation
no "buy N bundles" request
```

If the merchant wants the same bundle again after the previous purchase resolves, that is a new deliberate click, a new idempotency key, a new Woo charge and a new purchase lot.

The browser boundary remains unchanged:

```text
WooCommerce Admin React
        |
        | WordPress REST cookie + nonce
        v
local Moda plugin REST
        |
        | server-side PHP ModaApiClient
        | stored installation credential
        v
POST /v1/billing/recovery-credit-purchases
        |
        v
Woo confirmation URL
```

The plugin/browser never receives Woo vendor credentials or authoritative provider contract identity.

## Context

WOOCOMMERCE-001 establishes the Billing surface and recurring plan-management infrastructure, including:

- the accepted PHP Moda API client;
- privileged local Billing REST routes;
- browser-generated `actionId` -> hosted `Idempotency-Key`;
- strict hosted response validation;
- exact Woo confirmation-host validation;
- top-level redirect to Woo;
- generic Woo return-marker handling;
- one authoritative Billing refresh on return;
- manual Refresh rather than unbounded polling;
- stale-response/single-flight request protections.

WOOCOMMERCE-002 must reuse those pieces rather than creating another billing client/state machine.

### API-002 read contract

The accepted Billing read includes:

```text
capacity.purchased
topUps.configured
topUps.purchaseEligible
topUps.offers
topUps.latestPurchase
topUps.unresolvedPurchases
```

Each current-plan Woo bundle is:

```json
{
  "merchantPricingUsageEventId": "usage_bronze",
  "label": "Bronze",
  "creditsGranted": 10,
  "amountMinor": 1000,
  "currency": "USD",
  "purchaseEligible": true,
  "unavailableReason": null
}
```

One unresolved purchase blocks only the same bundle.

A different eligible bundle may remain purchasable.

### API-004 command contract

Hosted command:

```text
POST /v1/billing/recovery-credit-purchases
Idempotency-Key: <required>

{
  "merchantPricingUsageEventId": "..."
}
```

Successful response:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "operationId": "...",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

The merchant then confirms the charge on WooCommerce.com.

Browser/provider return is not credit activation. BACKGROUND-004 activates the purchase only after verified provider evidence.

## Scope

Modify only `moda-interact-woocommerce` PHP/React/tests required for:

1. one local top-up command proxy route;
2. predefined bundle presentation inside the accepted Billing surface;
3. one-bundle Buy action;
4. Woo confirmation redirect;
5. pending/confirmed/unknown top-up presentation after durable Billing refresh;
6. stale-response/single-flight behavior.

Expected implementation areas conceptually:

```text
includes/
  Api/
    ModaApiClient.php
  Rest/
    BillingController.php

src/
  billing/
    billing-page.tsx
    top-up-section.tsx
    top-up-card.tsx
    top-up-status.tsx
    use-top-up-purchase.ts

tests/
  ... PHP client/REST + React/controller/presentation tests
```

Use the exact accepted WOO-001 structures/names where they differ.

## Out of Scope

- Purchase-history/provider-refund-navigation UI; owned by WOOCOMMERCE-003.
- Refund hold creation; owned by API-006.
- Provider refund workflow.
- Top-up quantity selection.
- Runtime FIXED/GRADUATED/VOLUME pricing.
- `maximumUnitsPerBillingPeriod` purchase limiting.
- Woo tax calculation.
- Provider payment-status polling.
- Direct browser calls to hosted Moda.
- Woo vendor credentials.
- Purchase activation in browser/PHP.
- WordPress persistence of merchant billing state.
- New menu/page/router/state-management framework.
- Database/API schema changes.
- Gateway changes.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Reuse the accepted Billing surface

Add top-up purchasing to the existing WOOCOMMERCE-001:

```text
Billing
```

surface.

Do not register another WordPress page or top-level navigation item.

The top-up area belongs with the Billing summary/capacity experience.

Do not add a separate:

```text
Top-ups
```

top-level merchant destination.

### R2 — Reuse the existing Billing read

Do not add another top-up catalogue GET route.

Use the already-loaded API-002 Billing model from WOOCOMMERCE-001:

```text
capacity.purchased
topUps
```

A manual/return refresh refreshes the same Billing read.

Do not make one GET per top-up offer.

### R3 — Exact local purchase command route

Expose exactly:

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-purchases
```

Require:

```text
manage_woocommerce
valid WordPress REST cookie/nonce
CONNECTED installation
```

Request JSON exactly:

```json
{
  "merchantPricingUsageEventId": "...",
  "actionId": "..."
}
```

Reject unknown fields.

### R4 — `actionId` reuses WOO-001 idempotency semantics

Reuse WOOCOMMERCE-001's accepted browser UUID-v4 action helper and PHP validation.

React creates one `actionId` for one explicit merchant Buy attempt.

PHP maps:

```text
actionId
    -> hosted Idempotency-Key
```

unchanged.

The hosted JSON body contains only:

```json
{
  "merchantPricingUsageEventId": "..."
}
```

Do not persist `actionId`.

Do not create another top-up-specific UUID/idempotency implementation.

### R5 — PHP remote mapping is exact

Local:

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-purchases
```

maps exactly to:

```text
POST /v1/billing/recovery-credit-purchases
Idempotency-Key: actionId
```

with:

```json
{
  "merchantPricingUsageEventId": "..."
}
```

PHP MUST NOT send:

```text
quantity
creditsGranted
amountMinor
currency
shopId
billingPeriodId
providerSubscriptionId
providerContractId
returnUrl
```

### R6 — Strict purchase response validation

Accept successful hosted response only when:

```text
schemaVersion = 1
purchaseId is bounded non-blank string
operationId is bounded non-blank string
state = AWAITING_CONFIRMATION
confirmationUrl passes the accepted WOO-001 Woo URL validator
```

Local browser response is exactly:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "operationId": "...",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

Do not return provider contract ID, raw provider payload, request key/fingerprint or credentials.

### R7 — Reuse confirmation URL validation

Use the exact WOO-001 defense-in-depth helper:

```text
scheme = https
host exactly:
    woocommerce.com
    sandbox.woocommerce.com
no username/password
```

Do not implement a second looser top-up validator.

React also applies the accepted bounded validation before top-level navigation.

### R8 — Render configured predefined bundles only

Render the top-up section when:

```text
topUps.configured = true
topUps.offers.length > 0
```

Preserve the API response order.

Each card displays only:

```text
label
creditsGranted
formatted amountMinor/currency
purchase state/action
```

Do not display:

```text
eventHandle
merchantPricingUsageEventId as merchant-facing label
maximumUnitsPerBillingPeriod
provider contract IDs
```

The opaque event ID may exist only in React data/action state.

### R9 — Price display is presentation only

The authoritative price is API-002's integer:

```text
amountMinor
currency
```

For Woo v1 require/expect:

```text
currency = USD
```

Format the amount with locale-aware browser formatting from the integer minor amount.

The browser MUST NOT:

```text
apply discount
apply Woo markup
calculate tax
evaluate tiers
multiply by quantity
```

Woo calculates provider tax on its confirmation surface.

### R10 — No quantity control

The top-up card has exactly one purchase action equivalent to:

```text
Buy 10 credits
```

for an offer whose `creditsGranted = 10`.

Do not render:

```text
quantity input
plus/minus stepper
dropdown quantity
"Buy x 2"
custom credits field
```

One click submits only the selected event ID.

### R11 — Global top-up eligibility gate

A Buy action is enabled only when:

```text
topUps.purchaseEligible = true
offer.purchaseEligible = true
connection = CONNECTED
no top-up command currently in flight
```

If global `topUps.purchaseEligible = false`, all bundle Buy actions are disabled.

Do not infer global eligibility from:

```text
providerSubscriptionId
current plan kind
browser capacity balance
```

API-002 is authoritative.

### R12 — Individual bundle pending state

API-002 defines:

```text
offer.unavailableReason = PENDING_PURCHASE
```

only when that same offer has an unresolved Woo purchase.

For that bundle:

```text
purchaseEligible = false
```

and render a merchant-readable:

```text
Purchase pending
```

status instead of a Buy action.

A pending Bronze purchase MUST NOT disable an otherwise eligible Silver/Gold card.

### R13 — Exact unresolved-purchase presentation

Use:

```text
topUps.unresolvedPurchases
```

to show bounded status for the affected bundle.

Map:

```text
INITIATING
    -> "Starting purchase"

AWAITING_CONFIRMATION
    -> "Awaiting Woo confirmation"

OUTCOME_UNKNOWN
    -> "Confirmation needs reconciliation. Do not retry this bundle yet."

CONFIRMED
    -> "Payment confirmed. Credits are being activated."
```

Do not expose raw operation/provider IDs.

`OUTCOME_UNKNOWN` MUST NOT present an automatic Retry button.

### R14 — Latest purchase is a summary, not purchase history

`topUps.latestPurchase` may be used for a small recent-status message after refresh/return.

Do not build a history table from it.

Do not add:

```text
Manage purchases
Refund
Reactivate
```

in this task.

WOOCOMMERCE-003 owns the real API-006 history/refund UI.

### R15 — Buy action is single-flight

During one top-up command request:

```text
all top-up Buy controls disabled
```

to prevent accidental duplicate browser submissions before the command response/redirect is authoritative.

This is a transient UI lock only.

After a returned/error state refresh, different eligible bundles may be bought according to API-002.

Do not globally persist a "top-up locked" flag.

### R16 — Successful command redirects top-level to Woo

After strict local command success:

```text
window.top/location equivalent
    -> confirmationUrl
```

using the exact accepted WOO-001 navigation abstraction.

Do not:

- activate credits locally;
- increment purchased balance;
- mark purchase ACTIVE;
- persist purchase status in WordPress;
- show a synthetic completed purchase before redirect.

### R17 — Woo return reuses WOO-001 durable refresh

API-004 uses the same accepted return marker:

```text
moda_billing_return=1
operation=<opaque id>
```

Do not create a second top-up callback page/route.

On return:

1. WOO-001 opens Billing;
2. perform the accepted one authoritative Billing refresh;
3. WOO-002 renders the returned durable `topUps`/capacity state.

Do not use the opaque `operation` query value as billing authority.

### R18 — Return while activation is pending

If the merchant returns before BACKGROUND-004 activates the purchase, show the durable unresolved state from API-002.

Do not:

```text
poll indefinitely
call Woo from browser/PHP
assume browser return means payment succeeded
```

Expose the existing manual:

```text
Refresh
```

action.

A later refresh may show:

```text
purchase ACTIVE
capacity.purchased.available increased
```

after verified provider evidence.

### R19 — Successful activation is reflected only by the read model

The purchased capacity card from WOOCOMMERCE-001 remains authoritative:

```text
capacity.purchased.available
```

WOO-002 MUST NOT locally add:

```text
offer.creditsGranted
```

to that number after browser return.

This prevents double-display and preserves provider-confirmation-before-entitlement.

### R20 — Exact top-up command error behavior

Map bounded hosted/local errors:

#### `top_up_purchase_pending`

Refresh Billing once and present the same-bundle pending state.

Do not generate an automatic new action ID/retry.

#### `billing_provider_outcome_unknown`

Refresh Billing once and present:

```text
Confirmation needs reconciliation. Do not retry this bundle yet.
```

No automatic retry.

#### `billing_operation_in_progress`

Refresh once and show durable state. Do not issue another provider command automatically.

#### `billing_operation_failed`

Show bounded failure:

```text
The purchase could not be started.
```

A later explicit merchant Buy click is a **new deliberate attempt** and generates a new action ID.

#### `top_up_bundle_not_found`

Refresh Billing and show:

```text
This bundle is no longer available.
```

Do not keep a stale card actionable.

#### `top_up_purchase_unavailable`

Refresh Billing and render the current authoritative eligibility state.

#### `idempotency_conflict`

Treat as a bounded client/attempt conflict; do not retry automatically.

Arbitrary remote bodies are never shown.

### R21 — Connection/auth failure rejoins ARCH-026 lifecycle

A hosted installation-authentication failure must use the accepted WOO-001/WOO-005 connection-attention/reconnect behavior.

Do not display it as:

```text
card payment failed
bundle unavailable
```

and do not leave stale merchant billing data visible after connection invalidation.

### R22 — Stale response protection

A late top-up command/read result MUST NOT:

- redirect after connection left CONNECTED;
- overwrite newer Billing state;
- resurrect a stale bundle list after Billing refresh;
- show a command success after a newer connection generation exists.

Reuse the accepted WOO-001 request generation/abort/single-flight machinery.

### R23 — No browser persistence

Do not persist:

```text
topUps
offers
purchaseId
operationId
actionId
confirmationUrl
```

to:

```text
localStorage
sessionStorage
WordPress options
cookies
```

The browser reloads durable Billing state from the local authenticated route.

### R24 — Accessibility and localization

All merchant-visible strings use:

```text
@wordpress/i18n
text domain: moda-interact
```

Bundle cards/actions must be keyboard accessible.

Busy/pending status must be communicated in text, not only color/spinner.

Currency/number formatting uses locale-aware browser primitives.

### R25 — No fake purchase-history controls

After adding Buy actions, continue to omit:

```text
Manage purchases
Refund
Reactivate
```

until WOOCOMMERCE-003.

A recent/latest purchase summary is allowed; a fake history surface is not.

## Work Items

- [ ] Extend the accepted PHP billing controller/client with the one exact top-up command proxy route.
- [ ] Reuse WOO-001 actionId validation/idempotency forwarding.
- [ ] Reuse WOO-001 strict response/confirmation-URL validation.
- [ ] Add predefined bundle cards to the existing Billing surface.
- [ ] Format API-provided USD minor amount for display without price recomputation.
- [ ] Add exactly one Buy action per bundle and no quantity controls.
- [ ] Gate actions on global + per-offer API-002 eligibility.
- [ ] Render per-bundle unresolved state without globally blocking other eligible bundles.
- [ ] Add bounded INITIATING/AWAITING_CONFIRMATION/OUTCOME_UNKNOWN/CONFIRMED status messages.
- [ ] Add top-up command single-flight handling.
- [ ] Redirect successful command to Woo through the existing top-level navigation helper.
- [ ] Reuse the existing Billing return-marker/one-refresh/manual-refresh behavior.
- [ ] Ensure purchased balance changes only from refreshed API-002 state.
- [ ] Add bounded command error mapping with no automatic ambiguous-provider retry.
- [ ] Add stale-response/connection-generation protections.
- [ ] Add WordPress i18n/accessibility coverage.
- [ ] Prove no browser persistence/provider credentials/provider contract IDs/Shopify handles.
- [ ] Add focused PHP/React tests.

## Interfaces / Contracts

### Read

Owner:

`ARCH-027-API-002`

Consumed from:

```text
GET /wp-json/moda-interact/v1/billing
```

Relevant shape:

```text
capacity.purchased
topUps.configured
topUps.purchaseEligible
topUps.offers
topUps.latestPurchase
topUps.unresolvedPurchases
```

### Local top-up command

Owner:

`ARCH-027-WOOCOMMERCE-002`

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-purchases

{
  "merchantPricingUsageEventId": "...",
  "actionId": "<uuid-v4>"
}
```

### Hosted top-up command

Owner:

`ARCH-027-API-004`

```text
POST /v1/billing/recovery-credit-purchases
Idempotency-Key: actionId

{
  "merchantPricingUsageEventId": "..."
}
```

### Provider return

Same accepted Billing return URL as WOO-001.

It remains a refresh signal only.

## Dependencies

- `ARCH-027-WOOCOMMERCE-001`
- `ARCH-027-API-004`

Both must be architect-accepted Complete before WOOCOMMERCE-002 becomes Ready.

WOOCOMMERCE-001 supplies the accepted Billing shell, local credential boundary, action-idempotency helper, confirmation redirect, durable return refresh and state-race protections.

API-004 supplies one-predefined-bundle/one-charge command semantics.

## Enables

- `ARCH-027-WOOCOMMERCE-003`

WOOCOMMERCE-003 will add the API-006 purchase-history/provider-refund-navigation experience to the now-complete Billing + top-up merchant surface.

## Acceptance Criteria

- [ ] Top-up purchasing exists only inside the accepted Billing surface.
- [ ] Exactly one privileged local top-up command route is added.
- [ ] Browser sends only event ID + actionId to local WordPress REST.
- [ ] PHP sends only event ID to hosted JSON and actionId as Idempotency-Key.
- [ ] No quantity/credits/price/currency/shop/provider/return URL is browser-authoritative.
- [ ] Successful hosted response is strictly schema-validated.
- [ ] WOO-001 confirmation URL validation/navigation is reused.
- [ ] Configured current-plan bundle cards display label, credits and API-provided price.
- [ ] No quantity control exists.
- [ ] Global API eligibility disables all Buy actions when false.
- [ ] Same-bundle unresolved purchase disables only that bundle.
- [ ] A different eligible bundle remains actionable after a different bundle is pending.
- [ ] OUTCOME_UNKNOWN presents no automatic Retry.
- [ ] CONFIRMED-but-REQUESTED presents activation-pending rather than ACTIVE.
- [ ] Successful command redirects to Woo and does not locally grant credits.
- [ ] Woo return reuses the Billing refresh flow and does not activate purchase from query/browser state.
- [ ] Purchased balance changes only after refreshed API-002 durable state changes.
- [ ] Failed initiation allows a later explicit new click/new actionId.
- [ ] Command/read state is single-flight and stale responses cannot redirect/overwrite newer connection state.
- [ ] No top-up business data/action IDs are persisted in browser/WordPress storage.
- [ ] All visible strings are localized/accessibly rendered.
- [ ] No purchase-history/provider-refund-navigation control is added.
- [ ] No Woo vendor credential/provider contract ID/Shopify handle reaches React.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect accepted `moda-interact-woocommerce` scripts/repository instructions before selecting exact commands.

Required validation categories:

- [ ] repository-required Woo bootstrap/preparation;
- [ ] JavaScript unit tests;
- [ ] PHP unit tests;
- [ ] changed-file JS lint;
- [ ] CSS lint when styles change;
- [ ] PHP lint/code standards;
- [ ] production build;
- [ ] plugin ZIP/safety validation when repository policy requires it;
- [ ] local top-up REST permission/nonce test;
- [ ] PHP exact remote mapping/body/header test;
- [ ] actionId -> Idempotency-Key test;
- [ ] strict command response test;
- [ ] confirmation URL allowlist regression tests;
- [ ] configured/unconfigured top-up section tests;
- [ ] exact bundle-card label/credits/price test;
- [ ] no quantity control test;
- [ ] global purchaseEligible false test;
- [ ] same-bundle pending-only disable test;
- [ ] different-bundle remains enabled test;
- [ ] INITIATING/AWAITING_CONFIRMATION status tests;
- [ ] OUTCOME_UNKNOWN no-retry test;
- [ ] CONFIRMED purchase activation-pending test;
- [ ] command single-flight test;
- [ ] successful top-level Woo redirect test;
- [ ] return-marker one-refresh/no-local-credit-grant test;
- [ ] purchased balance durable-read-only test;
- [ ] top_up_purchase_pending refresh test;
- [ ] provider-outcome-unknown refresh/no-retry test;
- [ ] failed-initiation explicit-new-attempt/new-actionId test;
- [ ] stale command/read after disconnect test;
- [ ] no browser persistence test;
- [ ] no direct hosted browser call/credential/provider-ID leakage test;
- [ ] no purchase/refund placeholder control test;
- [ ] current/minimum supported WordPress/WooCommerce browser/DOM smoke when required by repository policy;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin purchase-history/provider-refund-navigation UI or Admin support work.

## Implementation Notes

This task should feel like the existing Shopify bundle purchase experience, but the provider mechanic is Woo `/charges`.

The important architecture is:

```text
React displays server-defined bundle
    -> sends opaque bundle ID
    -> PHP forwards authenticated command
    -> hosted API owns commercial validation
    -> Woo owns payment confirmation
    -> Background owns activation
    -> React displays refreshed durable state
```

Do not collapse those boundaries for convenience.

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

- WOOCOMMERCE-001 has accepted reusable confirmation URL, action-idempotency and return-refresh helpers.
- API-002 exposes current-plan predefined top-up bundles and same-bundle unresolved state.
- API-004 returns one validated confirmation URL for one bundle and never activates credits synchronously.
- WOOCOMMERCE-003 remains the owner of purchase history/provider refund navigation.

### Unresolved Issues

None within this top-up UI boundary.

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
