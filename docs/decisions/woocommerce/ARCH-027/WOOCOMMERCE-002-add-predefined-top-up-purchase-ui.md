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
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-027-WOOCOMMERCE-001
  - ARCH-027-API-004
  - ARCH-027-WOOCOMMERCE-004
enables:
  - ARCH-027-WOOCOMMERCE-003
created: 2026-10-03
updated: 2026-10-10
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

The presentation baseline is `ARCH-027-WOOCOMMERCE-004`: modular React Billing components and the Shopify-aligned layout/tokens already established on the native WordPress Billing page. This task is Pending until that foundation is architect-accepted Complete. It must extend the foundation, not recreate an embedded Shopify SPA.

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

Use the accepted WOOCOMMERCE-004 presentation modules and WOO-001 client/controller callbacks where they already exist. Current real composition is `src/page/connected-workspace.js` and `src/page/use-moda-page-state.js`; native menu ownership is `includes/Admin/NativeNavigation.php`. Implement focused bundle/card/status/purchase-action modules under the existing `src/billing/` presentation boundary (or accepted equivalent), not another large `billing-screen.js`/`billing-controller.js` or a new router. Retain `src/billing-client.js` and `includes/Rest/BillingController.php` as the existing transport owners.

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
- Reimplementing the WOOCOMMERCE-004 Billing hero/current-plan/capacity foundation or modifying WOOCOMMERCE-001 recurring semantics.
- Native `Recoveries`, `Promotions`, `Support` or `Recovery settings` navigation changes unrelated to the Billing flow.
- Partial locale support or an English-only new billing UI.
- Editing any `docs/decisions/**/_index.md` while this architecture session is open.
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

### R1A — Shopify-aligned top-up presentation within the existing Woo Billing view

The presentation must use the accepted WOOCOMMERCE-004 Billing hierarchy/design tokens and mirror the equivalent Shopify top-up concepts from `app/components/dashboard/TopUpPurchasePanel.jsx` and `BillingPurchaseHub.css`: purchased/free credit balances, predefined credit bundle grid, readable price/credits, one prominent Buy CTA, informative unavailable/pending notices and responsive card collapse. Align spacing, typography, cards, labels, active/disabled states, focus outlines and status treatments; do not copy Shopify's React Router `<form>`, event handles, pricing units or checkout mechanisms. Long translated copy must wrap without obscuring prices or actions.

Navigation remains the existing native WordPress Billing destination with internal top-up view/state via `ConnectedWorkspace`; do not add a Top-ups submenu. Use the accepted `src/styles/_tokens.scss` variables, and scope new styles to `.moda-interact-page`. Reuse the WOOCOMMERCE-004 admin-UI locale formatter for currency/quantity/date presentation.

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

### R24 — Accessibility and complete WordPress localisation

Every merchant-visible label, button, status, error, aria-label and provider-guidance string uses `@wordpress/i18n` (`__`, `sprintf` as required) with text domain `moda-interact` and statically extractable gettext source. Keep placeholders/number formats safe for translations; do not concatenate English sentence fragments.

After adding strings, regenerate/validate `languages/moda-interact.pot` and the **19 non-English PO catalogues**. All new keys require reviewed translations in every locale, and strict compilation must generate the corresponding PHP `.mo` and JavaScript JSON assets included by `npm run plugin-zip`. Update source-count/locale assertions as required; a POT-only update or wrapping strings in `__()` does not complete localisation. Preserve existing approved terminology and differentiated `pt_BR`/`pt_PT` copy. UI formatting must reuse WOOCOMMERCE-004's explicit WordPress administrator-locale preference, with site fallback, independent of store/customer conversation language.

Bundle cards/actions must be keyboard accessible with clear focus and disabled states. Busy/pending status must be announced in text (e.g. `role=status` where appropriate), not only color/spinner; check translated text expansion, mobile layout and screen-reader action labels.

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
- [ ] Add predefined bundle cards to the existing Billing surface using WOOCOMMERCE-004 modular presentation and Shopify-aligned tokens.
- [ ] Verify top-up cards/credit summary/action states visually against the Shopify reference at desktop and narrow viewport widths, without copying Shopify provider mechanics.
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
- [ ] Extract all new gettext strings, translate in 19 locale catalogues, compile PHP+JS assets and validate plugin ZIP inclusion.
- [ ] Add WordPress admin-UI-locale money/quantity formatting, keyboard/accessibility and translated-copy expansion coverage.
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
- `ARCH-027-WOOCOMMERCE-004`

All three must be architect-accepted Complete before WOOCOMMERCE-002 becomes Ready. This task is now **Pending**, not Ready; the existing accepted WOO-001 code remains intact.

WOOCOMMERCE-001 supplies the accepted Billing shell, local credential boundary, action-idempotency helper, confirmation redirect, durable return refresh and state-race protections.

API-004 supplies one-predefined-bundle/one-charge command semantics. WOOCOMMERCE-004 supplies modular billing UI, design tokens and the administrator-locale formatting helpers.

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
- [ ] Every new merchant-visible string has reviewed translations in all 19 non-English PO files; POT, placeholders, compiled `.mo`/JS JSON and ZIP checks pass.
- [ ] WordPress administrator-locale formatting (not browser/store locale) is consistent for amounts/credits/dates.
- [ ] Shopify-equivalent top-up hierarchy, cards, CTAs, notices, responsiveness and focus/disabled states are demonstrated without Shopify-specific provider controls.
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
- [ ] `npm run test:i18n`, `npm run i18n:verify:20` with updated POT and all 19 PO files;
- [ ] `npm run plugin-zip` and verify compiled PHP `.mo` / JS JSON assets are packaged;
- [ ] locale-formatting tests with administrator locale different from browser/store locale;
- [ ] Shopify reference desktop/mobile parity and long-translation layout tests/smoke;
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

This task should feel like the **same Moda merchant product** as Shopify bundle purchasing, but the provider mechanic is Woo `/charges`. Use the Shopify source components as a design reference, the accepted WOOCOMMERCE-004 modular Billing presentation as the implementation foundation, and WordPress gettext as the translation authority.

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

Review-ready (`review`).

### Files Changed

PHP billing command proxy and strict response validation; browser billing client/controller and connected Billing composition; new `src/billing/top-up-section.js`; billing SCSS; focused PHP/JS tests; POT and all 19 non-English PO catalogs; locale-batch/release fixtures.

### Work Completed

- Added the privileged local recovery-credit purchase route. It forwards only `merchantPricingUsageEventId` in the hosted JSON body and maps the browser `actionId` unchanged to `Idempotency-Key`; hosted response and confirmation URL validation reuse strict existing boundaries.
- Added the predefined bundle purchase interaction to the existing Billing surface: localized bundle labels, credits and server-provided prices, eligibility and same-bundle unresolved gating, single-flight command handling, top-level Woo confirmation redirect, durable refresh after return/unknown outcomes, and stale-connection protection. No quantity control, browser persistence, local credit grant, or history/refund control was added.
- Added responsive, accessible localized presentation and expanded focused PHP/JS coverage for the command mapping, response/error handling, offer/status states, purchase lifecycle, redirect, refresh, and race behavior.
- Updated the POT and all 19 non-English catalogs for 11 new merchant-visible messages, including the reviewed Finnish and Thai entries.

### Validation Results

- WooCommerce bootstrap and locked dependency installation passed.
- JavaScript unit suite passed: 23 files / 147 tests. Integration and i18n suites passed: 37 tests. After the final JSDoc typing/guard edits, the focused Billing screen suite passed (25 tests), `npm run lint:js` passed, and editor diagnostics reported no errors in `src/billing/top-up-section.js`.
- `npm run lint:css`, `npm run lint:php`, `npm run i18n:verify:20`, production build, and `npm run plugin-zip` passed. Strict locale verification covered all 20 locales and produced 38 compiled assets; the production ZIP contained 101 entries. ZIP SHA-256: `86a554c88d61307754a9f580cef50a78456765406201dca00ca8760875568b06`.
- The full PHP suite reported 71/72 passing. The remaining failure is outside this task's billing surface: `RecoverySummaryControllerTest::test_no_browser_shop_id_and_missing_installation` expected 401 but received 200.
- Final `git diff --check` passed for the implementation and task report; focused lint/tests and editor diagnostics passed after the final JS edits.
- Prepared-worktree evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-WOOCOMMERCE-002`, branch `task/ARCH-027-WOOCOMMERCE-002`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-002`, branch `task/ARCH-027-WOOCOMMERCE-002`. Both were created for this task; shared workspace/implementation checkout mutation: no; another task worktree reused: no.
- Start synchronization: parent and implementation remote task-branch fast-forward: `not-needed`; parent and implementation `origin/main` incorporation: `already-current`. Recursive `git submodule sync` and `git submodule update --init --recursive` both passed; packet recorded no submodule entries/commits. The launcher claim was committed and pushed.
- Developer-owned environment validation remains: wp-env-dependent `i18n:makepot`, package-lifecycle validation, and current/minimum WordPress/WooCommerce browser/DOM smoke were not run because wp-env was not initialized. `i18n:makepot` was attempted and stopped at that prerequisite; POT/source consistency and strict locale compilation passed independently.

### Deviations

The generated POT/catalog verification and strict compilation were used instead of completing the wp-env-dependent `i18n:makepot` lifecycle. No task-scope or architecture deviation.

### Assumptions

- WOOCOMMERCE-001 has accepted reusable confirmation URL, action-idempotency and return-refresh helpers.
- API-002 exposes current-plan predefined top-up bundles and same-bundle unresolved state.
- API-004 returns one validated confirmation URL for one bundle and never activates credits synchronously.
- WOOCOMMERCE-003 remains the owner of purchase history/provider refund navigation.

### Unresolved Issues

- One unrelated full-PHP-suite failure remains as recorded above.
- Developer-owned wp-env/package-lifecycle and current/minimum browser smoke remain outstanding before final acceptance.

### Architectural Concerns

None identified; the implementation preserves the hosted API, Woo confirmation, and durable activation ownership boundaries.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-10). Task returned to `ready` for Attempt 2; `executor` and `claimed_at` cleared; accepted attempt history and original Completion Report preserved.

### Review Notes

The principal one-bundle/one-charge boundary conforms: the browser supplies only an opaque event ID plus actionId; the privileged PHP route forwards one event ID as hosted JSON and uses actionId solely as `Idempotency-Key`; the existing Woo confirmation URL validator and redirect are reused. Read-model gating, per-bundle pending states, single-flight handling, and no local credit activation were found in the submitted implementation. The package `moda-interact.zip` has 101 entries, matches the Completion Report SHA-256 `86a554c88d61307754a9f580cef50a78456765406201dca00ca8760875568b06`, and contains 19 `.mo` plus 19 JavaScript catalogue assets.

**A1-R1 — Correct cross-command error/notice attribution (source and focused regression tests required).** `TopUpSection` currently displays `NOTICE_COPY[state.notice ?? ''] ?? NOTICE_COPY[state.error ?? '']` without knowing whether the error came from top-up purchasing or a recurring-plan/cancellation command. When an unrelated subscription or cancellation command fails with `billing_operation_failed`, the top-up section incorrectly says “The purchase could not be started.” Conversely, a failed top-up causes the general `BillingScreen` handler for the same error to say “Your current plan remains unchanged,” which is unrelated to the purchase. Reproduced the former case with the submitted `src/billing/top-up-section.js`. Preserve the shared WOO-001 controller; make the command/error context explicit or otherwise confine top-up feedback to top-up commands and recurring feedback to recurring commands. Reset or retire stale feedback on a subsequent command, refresh, connection change or disposition as appropriate. Add regression cases exercising both directions, including non-top-up plan/cancellation failures when eligible top-up offers are visible and top-up failures without a plan-change notice. Preserve the existing unknown-outcome single-refresh/no-retry, same-bundle and stale-connection guarantees. Do not alter hosted API contracts or billing state.

**A1-R2 — Complete and reconcile validation evidence.** The Completion Report acknowledges outstanding `i18n:makepot`, wp-env package-lifecycle and current/minimum browser/DOM smoke checks. After A1-R1, run or obtain developer-authorized evidence for the required WordPress integration, package lifecycle against the newly generated candidate ZIP, 20-locale generation/verification, responsive/long-copy and keyboard smoke at supported current/minimum environments. Record exact commands, exit codes, candidate SHA-256 and any failures. Rebuild and audit the production ZIP after the *final* source changes, not before. Static ZIP/i18n checks already reported as passing do not substitute for these required runtime proofs. If a command cannot run, retain its unchecked validation item and document the exact blocker for architect review; do not claim it passed.

**A1-R3 — Reconcile the pre-existing PHP-suite failure without unrelated production changes.** `RecoverySummaryControllerTest::test_no_browser_shop_id_and_missing_installation` in the submitted branch expects a missing connection after a helper has saved one. `InstallationStore` reads persistent mock options, so the result can be HTTP 200 rather than the asserted 401. The canonical `main` version of this test already explicitly deletes `InstallationStore::OPTION_NAME` before the missing-installation assertion; the task branch is behind that correction. Re-synchronize through the canonical task launcher/branch workflow, verify the corrected fixture, and rerun the full PHP suite. Do not change Recovery Summary production behavior or copy a conflicting duplicate fix solely to make WOO-002 green. If a different failure remains after sync, include its exact output.

**A1-R4 — Task completion evidence.** Before resubmission, check completed Work Items, Acceptance Criteria and Validation boxes as proven, leave outstanding items unchecked, append Attempt 2 results in the Completion Report, and record launcher-resolved parent/implementation worktree and synchronization evidence. Reclaim via the normal task launcher: increment `attempt` once from 1 to 2; do not reuse a shared/default checkout. Return the task to `review`, clear `executor`/`claimed_at`, and stop. The original Attempt 1 Completion Report is historical evidence and must not be overwritten.

No architecture or implementation dependencies are promoted. `ARCH-027-WOOCOMMERCE-003` remains Pending until this task is architect-accepted Complete and its other prerequisites are satisfied. Do not edit any `docs/decisions/**/_index.md` during this session.

### Reviewed Files

- `src/billing/top-up-section.js`, `src/billing/summary.js`, `src/billing-screen.js`, `src/billing-controller.js`, `src/billing-client.js`, `src/page/connected-workspace.js`.
- `includes/Rest/BillingController.php`, `includes/Api/ModaApiClient.php`, `includes/Api/BillingResponseValidator.php`.
- `tests/js/billing-screen.test.js`, `tests/js/billing-controller.test.js`, `tests/js/billing-client.test.js`, `tests/BillingControllerTest.php`, `tests/RecoverySummaryControllerTest.php`.
- `languages/moda-interact.pot`, the submitted compiled `moda-interact.zip`, task Completion Report, parent architecture and direct dependencies.

### Validation Reviewed

- Reported focused Billing suite: 25 passing; broader JS: 147 passing; integration/i18n: 37 passing; lint/build/locale/ZIP: reported passing. These are Completion Report evidence, not independently rerun suite results.
- Reported PHP: 71/72, with the single failure explained in A1-R3; branch/main fixture mismatch verified in source.
- Independently checked published task-branch Git blobs for the task report and key PHP/JS files against the uploaded snapshot; the reported distribution SHA-256, 101 ZIP entries, ZIP integrity and 19 `.mo`/19 JS locale assets matched. Reproduced wrong top-up notice when an unrelated recurring command supplies `billing_operation_failed`.
- Required wp-env-dependent release/WordPress browser validation remains outstanding. Physical developer worktree cleanliness and runtime suites were not directly reproducible in this review environment; the Completion Report contains launcher/worktree evidence.

### Architecture Conformance

Core API/tenant, deterministic one-bundle purchase, no browser-calculated price or provider identity, provider confirmation and durable-read activation boundaries: conformant. User-visible error attribution and required release validation: incomplete (A1-R1/A1-R2). No production contract/schema change requested.

### Follow-up

Return same task `ARCH-027-WOOCOMMERCE-002` for Attempt 2. Do not create a new feature task or start `WOOCOMMERCE-003` until accepted.
