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
status: in_progress
priority: 80
executor: copilot
claimed_at: 2026-10-10T20:38:28Z
attempt: 3
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

- [x] Inspect the **actual Shopify Billing source** in sibling `moda-interact/` (read-only), trace merchant journey and component/controller/state ownership, and record inspected file paths and an explicit Shopify-to-Woo flow mapping in the next Completion Report.
- [x] Reorganise the **existing** Woo Billing summary/top-up/plan presentation to follow Shopify's merchant journey: integrated current plan and recovery-capacity hierarchy, discoverable Add top-up / Change plan actions, contextual offer/plan cards and clear status/empty states. Keep WordPress-native navigation and accepted modular controller/component boundaries.
- [x] Produce a manual-review-ready Woo UI build/package when needed, record installation/refresh steps for LocalWP/wp-env and the expected review scenarios, then STOP **without running automated tests** or claiming visual parity.
- [x] Extend the accepted PHP billing controller/client with the one exact top-up command proxy route.
- [x] Reuse WOO-001 actionId validation/idempotency forwarding.
- [x] Reuse WOO-001 strict response/confirmation-URL validation.
- [x] Add predefined bundle cards to the existing Billing surface using WOOCOMMERCE-004 modular presentation and Shopify-aligned tokens.
- [ ] Verify top-up cards/credit summary/action states visually against the Shopify reference at desktop and narrow viewport widths, without copying Shopify provider mechanics.
- [x] Format API-provided USD minor amount for display without price recomputation.
- [x] Add exactly one Buy action per bundle and no quantity controls.
- [x] Gate actions on global + per-offer API-002 eligibility.
- [x] Render per-bundle unresolved state without globally blocking other eligible bundles.
- [x] Add bounded INITIATING/AWAITING_CONFIRMATION/OUTCOME_UNKNOWN/CONFIRMED status messages.
- [x] Add top-up command single-flight handling.
- [x] Redirect successful command to Woo through the existing top-level navigation helper.
- [x] Reuse the existing Billing return-marker/one-refresh/manual-refresh behavior.
- [x] Ensure purchased balance changes only from refreshed API-002 state.
- [x] Add bounded command error mapping with no automatic ambiguous-provider retry.
- [x] Add stale-response/connection-generation protections.
- [ ] Extract all new gettext strings, translate in 19 locale catalogues, compile PHP+JS assets and validate plugin ZIP inclusion.
- [x] Add WordPress admin-UI-locale money/quantity formatting, keyboard/accessibility and translated-copy expansion coverage.
- [x] Prove no browser persistence/provider credentials/provider contract IDs/Shopify handles.
- [x] Add focused PHP/React tests.

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

- [x] Top-up purchasing exists only inside the accepted Billing surface.
- [x] Exactly one privileged local top-up command route is added.
- [x] Browser sends only event ID + actionId to local WordPress REST.
- [x] PHP sends only event ID to hosted JSON and actionId as Idempotency-Key.
- [x] No quantity/credits/price/currency/shop/provider/return URL is browser-authoritative.
- [x] Successful hosted response is strictly schema-validated.
- [x] WOO-001 confirmation URL validation/navigation is reused.
- [x] Configured current-plan bundle cards display label, credits and API-provided price.
- [x] No quantity control exists.
- [x] Global API eligibility disables all Buy actions when false.
- [x] Same-bundle unresolved purchase disables only that bundle.
- [x] A different eligible bundle remains actionable after a different bundle is pending.
- [x] OUTCOME_UNKNOWN presents no automatic Retry.
- [x] CONFIRMED-but-REQUESTED presents activation-pending rather than ACTIVE.
- [x] Successful command redirects to Woo and does not locally grant credits.
- [x] Woo return reuses the Billing refresh flow and does not activate purchase from query/browser state.
- [x] Purchased balance changes only after refreshed API-002 durable state changes.
- [x] Failed initiation allows a later explicit new click/new actionId.
- [x] Command/read state is single-flight and stale responses cannot redirect/overwrite newer connection state.
- [x] No top-up business data/action IDs are persisted in browser/WordPress storage.
- [ ] Every new merchant-visible string has reviewed translations in all 19 non-English PO files; POT, placeholders, compiled `.mo`/JS JSON and ZIP checks pass.
- [x] WordPress administrator-locale formatting (not browser/store locale) is consistent for amounts/credits/dates.
- [ ] Shopify-equivalent top-up hierarchy, cards, CTAs, notices, responsiveness and focus/disabled states are demonstrated without Shopify-specific provider controls.
- [x] All visible strings are localized/accessibly rendered.
- [x] No purchase-history/provider-refund-navigation control is added.
- [x] No Woo vendor credential/provider contract ID/Shopify handle reaches React.
- [x] `docs/architecture/_index.md` is unchanged.

## Validation

**Architect-approved staged validation override for the next implementation attempt (2026-10-10):** The developer has requested **implementation first, manual UI inspection second, automated validation only after explicit approval**. During this stage the implementing agent MUST NOT run JavaScript/PHP tests, integration suites, lint, typecheck, automated accessibility tests, automated browser smoke, translation verification suites, or automated browser/accessibility verification. `git status` and `git diff --check` are permitted solely for change/whitespace hygiene; they do not count as feature validation. A build and/or ZIP packaging command is permitted **only if necessary to make the changed UI available for LocalWP/wp-env manual inspection**; report exactly what actually ran, without claiming it proves functionality. Previous completed validations remain historical evidence, not validation of new edits. Keep new/remaining validation and browser-parity checkboxes unchecked. The normal required Validation contract resumes only after the developer explicitly authorizes testing following manual inspection.

Inspect accepted `moda-interact-woocommerce` scripts/repository instructions before selecting exact commands.

Required validation categories:

- [x] repository-required Woo bootstrap/preparation;
- [ ] JavaScript unit tests;
- [x] PHP unit tests;
- [ ] changed-file JS lint;
- [ ] CSS lint when styles change;
- [x] PHP lint/code standards;
- [ ] production build;
- [ ] `npm run test:i18n`, `npm run i18n:verify:20` with updated POT and all 19 PO files;
- [ ] `npm run plugin-zip` and verify compiled PHP `.mo` / JS JSON assets are packaged;
- [x] locale-formatting tests with administrator locale different from browser/store locale;
- [ ] Shopify reference desktop/mobile parity and long-translation layout tests/smoke;
- [x] plugin ZIP/safety validation when repository policy requires it;
- [x] local top-up REST permission/nonce test;
- [x] PHP exact remote mapping/body/header test;
- [x] actionId -> Idempotency-Key test;
- [x] strict command response test;
- [x] confirmation URL allowlist regression tests;
- [x] configured/unconfigured top-up section tests;
- [x] exact bundle-card label/credits/price test;
- [x] no quantity control test;
- [x] global purchaseEligible false test;
- [x] same-bundle pending-only disable test;
- [x] different-bundle remains enabled test;
- [x] INITIATING/AWAITING_CONFIRMATION status tests;
- [x] OUTCOME_UNKNOWN no-retry test;
- [x] CONFIRMED purchase activation-pending test;
- [x] command single-flight test;
- [x] successful top-level Woo redirect test;
- [x] return-marker one-refresh/no-local-credit-grant test;
- [x] purchased balance durable-read-only test;
- [x] top_up_purchase_pending refresh test;
- [x] provider-outcome-unknown refresh/no-retry test;
- [x] failed-initiation explicit-new-attempt/new-actionId test;
- [x] stale command/read after disconnect test;
- [x] no browser persistence test;
- [x] no direct hosted browser call/credential/provider-ID leakage test;
- [x] no purchase/refund placeholder control test;
- [ ] current/minimum supported WordPress/WooCommerce browser/DOM smoke when required by repository policy;
- [x] `git diff --check`;
- [x] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

**Attempt 3 interim manual-review stop (architect-authorized):** After inspecting Shopify source and implementing only the bounded Woo visual/flow correction, commit/push implementation edits and a truthful progress/hand-off report, then return control to the developer **before any automated testing**. Leave the task `in_progress` with its valid Attempt 3 claim (not `review` or `complete`) until the developer manually validates the UI and instructs the next step. Do not clear an active claim simply to appear review-ready. Preserve the latest Architect Review and do not begin a dependent task. The normal `review` transition below applies only after the later authorized validation has been completed.

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

### Attempt 3 Interim Manual-Review Handoff (2026-10-10)

#### Status

Implementation handoff for developer manual UI inspection. The task remains `in_progress`, `attempt: 3`, `executor: copilot`, with the valid claim timestamp `2026-10-10T20:38:28Z`. It has not been moved to `review` or `complete`; the active claim has not been cleared. Automated validation is intentionally paused pending the developer's manual inspection and explicit authorization.

#### Launcher and Worktree Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-WOOCOMMERCE-002`, branch `task/ARCH-027-WOOCOMMERCE-002`.
- Woo implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-002`, branch `task/ARCH-027-WOOCOMMERCE-002`.
- Prepared heads: parent `23d5ee254f3cf3e4a01ca9da057d26fb7f3799a1`; implementation `e9cb40ecf16560b3b8c5dfa787b071f994f54bd3`.
- Parent and implementation task-branch fast-forward: `not-needed`; both `origin/main` incorporations: `already-current`.
- Recursive `git submodule sync` and `git submodule update --init --recursive` passed; packet recorded no submodule entries/commits.
- Attempt 3 claim commit `ed7a17bf69dad3137f925292c56d70cf17abed47` was pushed. Parent task metadata records `ready -> in_progress` and `attempt: 2 -> 3`.
- The Shopify source repository at `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact` was inspected read-only and left clean on `main`; its database submodule pointer was not changed.

#### Shopify Source Study and Flow Mapping

Read-only Shopify source paths inspected:

- `moda-interact/app/routes/app/billing/options/route.tsx`
- `moda-interact/app/components/dashboard/BillingPurchaseHub.jsx`
- `moda-interact/app/components/dashboard/TopUpPurchasePanel.jsx`
- `moda-interact/app/components/dashboard/SubscriptionChangePanel.jsx`
- `moda-interact/app/routes/app/billing/callback/route.tsx`
- `moda-interact/app/routes/app/billing/recovery-credit-purchases/route.tsx`
- `moda-interact/app/services/billing/recovery-credit-purchase-request.service.ts`
- `moda-interact/app/components/dashboard/BillingPurchaseHub.css`

The options route owns Shopify merchant access, commercial-state/capacity reads, and offer availability. `BillingPurchaseHub` presents the current-plan/capacity context with direct top-up and plan actions, then renders the selected `TopUpPurchasePanel` or `SubscriptionChangePanel`. The top-up panel uses provider-defined labels/prices and per-offer pending/eligibility state. The subscription panel shows current/pending/cancellation state. The callback returns to refreshed Shopify Billing state; the separate purchase-history route is outside WOOCOMMERCE-002.

Woo mapping: Shopify's current-plan/capacity hub maps to the existing Woo `BillingHero` and `BillingSummary`; the hub actions map to new `Add top-up` and `Change plan` view tabs; the offer panel maps to existing `TopUpSection`; and the plan panel maps to existing `PlansView`/`PlanCard`. Woo keeps `BillingController` as view/command owner, API-sourced offer eligibility and prices, the opaque usage-event ID plus actionId command, WordPress administrator-locale formatting, Woo confirmation redirect, and durable read-model refresh. Shopify provider forms, Shopify purchase IDs/event handles, provider authentication, and Shopify billing state are not copied. Purchase history/refunds remain excluded for WOOCOMMERCE-003.

#### Attempt 3 Changes

- Added `TOP_UPS` to the existing `BillingController` view state; no new controller or transport path was introduced.
- Updated the existing Billing navigation to expose `Summary`, `Add top-up`, and `Change plan`. The Summary now focuses on current plan and recovery capacity; the dedicated top-up view contains the API-defined bundle cards and existing Woo confirmation guidance. When the API has no configured offers, the view displays an accessible status instead of disappearing. Plans retain their existing catalogue component and load behavior.
- Added the two action labels to `languages/moda-interact.pot` and all 19 non-English PO catalogs, reusing corresponding existing Shopify locale wording. The catalogs are source edits only at this checkpoint: no gettext extraction, translation compilation/verification, or ZIP audit has been run for Attempt 3.
- Source files changed: `src/billing-controller.js`, `src/billing-screen.js`, `src/billing/hero.js`, `src/billing/summary.js`, `src/billing/top-up-section.js`; POT and all 19 PO catalogs.

#### Build and Manual Review Instructions

The WordPress admin enqueues `build/index.js`. The manual-review asset was built with the underlying build command, bypassing `npm run build` because that script runs the currently prohibited strict translation verification:

```text
cd /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-002
npm exec wp-scripts -- build
```

The command completed successfully (webpack emitted `build/index.js` and CSS). This is a build only, not a behavior check. No plugin ZIP was produced. For wp-env, the checked-in `.wp-env.json` mounts the current implementation directory as the plugin; start the repository environment with `npm run env:start`, sign in to its WordPress admin, and refresh the Moda Interact page. For LocalWP, install/update this implementation directory as `wp-content/plugins/moda-interact/`, activate the plugin if needed, and hard-refresh the WordPress admin page so it loads the rebuilt asset.

Manual walkthrough: use a connected **staging** merchant with a current plan and API-provided offers; open Moda Interact > Billing; inspect the current-plan and capacity hierarchy in Summary; select Add top-up and inspect offer labels, API prices, disabled/pending states, keyboard focus and the no-offer state; select Change plan and inspect current-plan markers and plan actions. Repeat at desktop and a narrow viewport (about 390px), and keyboard through all tabs/cards. Do not submit a purchase or plan change unless the connected environment is explicitly safe for a real Woo confirmation. No manual UI inspection has yet been performed by the developer, and no visual-parity claim is made.

#### Attempt 3 Validation Boundary

- Executed: `npm exec wp-scripts -- build` (manual-review asset build); `git diff --check` (patch hygiene only).
- Not executed: JavaScript/PHP tests, integration tests, lint, typecheck, automated browser/accessibility checks, `npm run i18n:makepot`, `npm run i18n:verify:20`, `npm run test:i18n`, translation compilation, `npm run build`, `npm run plugin-zip`, or package lifecycle checks.
- The build was rerun successfully after the final action-label/catalog edits and refreshed the manual-review bundle. It remains only a build, not behavioral validation. All behavioral, translation-asset, package, and desktop/mobile acceptance remains pending developer inspection and later authorization.

### Historical Attempt 1 Submission (superseded)

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

### Attempt 2 (2026-10-10)

#### Work Completed

- Resolved A1-R1 with transient `feedbackContext` in the shared billing controller. Plan changes, cancellations, and top-up commands now retain distinct error attribution; refresh, view/connection changes, command starts, deactivation, disconnect, and successful redirect clear stale attribution. The top-up section renders feedback only for top-up commands, and the general billing screen suppresses recurring-plan copy for top-up failures. No hosted contract or durable billing state changed.
- Added controller and screen regressions for plan/cancellation errors while eligible offers remain visible, top-up failures without recurring-plan notices, distinct command context, and stale feedback cleanup.
- Synchronized current `origin/main` at implementation commit `455ffde` (`Merge main into WOO-002 task branch`). Preserved both WOO-002 and main's read-access feature; included main's RecoverySummary fixture correction. Full PHP tests are green.

#### Validation Results

- Prescribed WooCommerce bootstrap passed. `npm run test:js` passed: 26 unit-test files / 165 tests and 37 integration/i18n checks.
- `npm run test:php` passed: 77 tests / 433 assertions. `npm run lint:php` passed across plugin and test PHP files.
- Task-scoped JavaScript lint passed using `npm exec wp-scripts -- lint-js --ignore-pattern=src/page.js --ignore-pattern=src/page/use-moda-page-state.js --ignore-pattern='src/read-access/**' --ignore-pattern=tests/js/page-controller-session.test.js --ignore-pattern='tests/js/read-access-*.test.js'`. Unfiltered `wp-scripts lint-js` still reports seven existing diagnostics in incoming main read-access files (missing JSDoc parameter types, `no-alert`, and `eqeqeq`); those unrelated files were not changed to hide the baseline. A formatter initially touched incoming-main files; only those formatter diffs were reversed, leaving their branch content intact.
- `npm run lint:css` exited 1 on two unrelated repository diagnostics: `src/index.scss` at-rule spacing and `src/styles/_read-access.scss` line length. No style files were changed for A1-R1.
- `npm run i18n:makepot` passed against wp-env. `npm run i18n:verify:20` passed with 195 source messages, 19/19 translation packs, and 38 compiled assets; `npm run test:i18n` passed 28/28. `makepot` refreshed POT extraction ordering/references; source and catalog checks passed afterward.
- `WP_ENV_PORT=8894 npm run test:integration:wordpress` passed the WOO-014 installed locale/state, WOO-008 category, WOO-007 store-context, and WOO-003 REST/HTTPS integration checks. An initial attempt on 8893 could not start because that port was occupied; retry on 8894 passed.
- `npm run build` passed. `npm run plugin-zip` passed after final sources and rebuilt assets. Final `moda-interact.zip` SHA-256: `73e823e7a19f45277ba5e5e2865f6b8961a707df2f3b6f5c792a5c802b15297f`; `unzip -t` reported no compressed-data errors. The package lifecycle was rerun after the final build and passed on WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1, including fresh install/upgrade and installed locale rendering.
- Minimum wp-env admin smoke used WordPress 7.0.6 / WooCommerce 11.0.1 / PHP 8.1.34. The native Billing route loaded and the first keyboard Tab reached “Skip to main content.” The test store was disconnected, so bundle/offer interactions and translated long-copy layout could not be inspected. At a 390px viewport the general admin body measured 402px scroll width; with no connected top-up offers this is not evidence of top-up layout behavior. The visual parity and current/minimum offer-card browser/DOM checklist items remain unchecked.
- Final implementation `git diff --check` passed. Parent task metadata is set to `status: review`, `executor: null`, `claimed_at: null`, `attempt: 2`; launcher evidence is recorded above and in the original worktree notes. Implementation/report task branches are submitted for Architect review.

#### Remaining Validation Limits

- Desktop/narrow top-up-card visual parity, translated-copy expansion, and connected-offer keyboard/disabled-state smoke remain unverified because neither local wp-env store had a connected merchant/API offer fixture. The corresponding visual and current/minimum browser/DOM checklist items remain unchecked for review.
- CSS lint remains blocked by the two unrelated diagnostics listed above; the repository-wide JavaScript lint baseline has seven unrelated incoming-main read-access diagnostics. Task-scoped JavaScript lint is clean.

## Architect Review

### Review Status

Changes Requested — Attempt 2 (2026-10-10). A1-R1 and A1-R3 are resolved. Required connected-offer browser visual/interaction evidence remains unverified; Attempt 2 launcher-preparation evidence needs explicit reconciliation. Task returned to `ready`, with `attempt: 2` retained and execution claim cleared.

Historical Attempt 1 Review Status (preserved): Changes Requested — Attempt 1 (2026-10-10). Task returned to `ready` for Attempt 2; `executor` and `claimed_at` cleared; accepted attempt history and original Completion Report preserved.

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

### Attempt 2 Architect Review (2026-10-10)

#### Decision

**Changes Requested.** A1-R1 is fixed and the plan/cancellation versus top-up message regressions are present. A1-R3 is closed by the synchronized main Recovery Summary fixture and the reported full PHP result (77 tests/433 assertions). The A1-R2 release/i18n/package work is substantially closed: reported JavaScript 165 passing unit tests plus 37 integration/i18n checks, passing PHP lint, `i18n:makepot`, 20-locale verification (195 source messages, 19 PO packs, 38 compiled locale assets), WordPress integration and fresh/upgrade package lifecycle on WordPress 7.1.2/WooCommerce 11.1.2; final artifact ZIP SHA-256 `73e823e7a19f45277ba5e5e2865f6b8961a707df2f3b6f5c792a5c802b15297f`. Independently verified the uploaded artifact checksum, 103 ZIP entries, archive integrity and its 19 PHP `.mo` and 19 JavaScript JSON translations. The changed controller, Billing screen and top-up section, their tests, and the task report match the pushed mirrored task-branch Git blobs (`e9cb40ecf16560b3b8c5dfa787b071f994f54bd3` and `51ad3cccb60b920fc105b1281411a663f20b5f0f`). Runtime test outcomes are implementer-reported; this review environment has no installed Woo Node dependencies or WordPress/Docker environment to rerun them.

**A2-R1 — Complete the required *connected-offer* browser/visual acceptance evidence (validation and/or test-only fixture correction).** The minimum-version wp-env browser smoke loaded the native Billing route but the store was disconnected and rendered no bundle offers. The task's Shopify-aligned top-up card/CTA hierarchy, responsiveness, disabled/pending states, real keyboard focus/interaction, and expanded translated-copy layout remain explicitly unchecked in Work Items, Acceptance Criteria and Validation. Static source, styles and unit render tests cannot prove these required DOM/visual behaviours. Use either a connected developer test store or a deterministic **test-only** connected installation/API-002 read fixture in the existing WordPress wp-env/Playwright harness (a live Woo one-time charge is *not* required). Exercise at least a two-offer view, one disabled/pending bundle with another independently eligible, the global disabled state, pending/unknown/confirmed status copy, long translated content, keyboard focus/disabled actions, and desktop and narrow (e.g. 390px) layouts. Capture concrete browser assertions/DOM outcomes and screenshots or equivalent inspectable evidence for the current and minimum supported WordPress/WooCommerce configurations. Record viewport sizes, locale, fixture state, test commands and exit results. Show there is no top-up-attributable horizontal overflow, rather than treating the disconnected admin body's previously observed 402px width at a 390px viewport as proof either way. The Shopify design reference should be compared as required by the task. Do **not** create a new production-only mock, bypass permissions, change any merchant billing state, or issue provider charges to obtain this evidence. If the evidence can be collected with existing fixtures and no source edits, prefer validation/report-only rework.

**A2-R2 — Record Attempt 2-specific launcher preparation and synchronization evidence (report-only).** The Completion Report includes canonical parent/implementation worktree paths and initial-launch synchronization, and states it merged `origin/main` at `455ffde`, but does not explicitly give the launcher-prepared Attempt 2 parent/implementation heads, task-branch fast-forward results, `origin/main` incorporation at Attempt 2 start, recursive submodule status and durable Attempt 2 claim commit. Recover those actual values from the launcher packet/commits without inventing them. A clean task branch, old Attempt 1 launcher packet or general 'recorded above' wording is insufficient to prove start-of-attempt synchronization. Do not churn implementation source purely to repair the report.

**Non-blocking validation disposition:** `src/index.scss` and `src/styles/_read-access.scss` are byte-for-byte identical to the current `main` branch according to their Git blob IDs; the two reported repository-wide CSS lint diagnostics are not WOO-002 source regressions. The seven unfiltered JS lint diagnostics are reported in incoming-main read-access files; the task-scoped JS lint passed. No unrelated CSS/read-access source changes are requested. Preserve these actual command failures and their scope in the Completion Report; do not check an overall failing CSS lint command as passed. The optional focused style lint on the changed Billing styles may be reported if it can be run.

#### Reviewed Source and Evidence

- `src/billing-controller.js`, `src/billing-screen.js`, `src/billing/top-up-section.js` and focused `tests/js/billing-controller.test.js` / `tests/js/billing-screen.test.js`.
- `src/styles/_billing.scss`, `src/index.scss`, `src/styles/_read-access.scss`, `includes/Rest/BillingController.php`, the packaged plugin ZIP and compiled localisation assets.
- Parent ARCH-027 Woo top-up architecture, WOO-002 task and both Completion Report attempts, mirrored Git commits, and dependency status of WOOCOMMERCE-003.

#### Validation Reviewed

The submitted report asserts passing JS/PHP/i18n/build/WordPress/package lifecycle checks as detailed above. Independently checked published source/report blob identities, the exact candidate package SHA-256, 103-entry ZIP integrity and 38 compiled assets; confirmed the two unrelated CSS-error files exactly match `main`. No connected-offer browser fixture, screenshots, or test run proving the required visible offer interaction and layout has been supplied. Therefore the visual/current/minimum browser acceptance items remain unchecked. Attempt 2 synchronization packet details are incomplete in the durable report.

#### Architecture Conformance and Follow-up

The core single-bundle command, tenant/credential boundary, provider confirmation redirect, read-only credit activation and cross-command feedback attribution conform to ARCH-027 on the reviewed source. The remaining issue is **evidence**, not a demonstrated new runtime defect. Return the **same** task to a reclaimable `ready` state, retain `attempt: 2`, and clear `executor`/`claimed_at`. The next launcher claim may start Attempt 3, or the developer may supply the missing browser evidence for architect review following the authorized workflow. Resubmit only after A2-R1 browser validation and A2-R2 report reconciliation are complete; do not mark unexecuted criteria as passed. Do not start WOOCOMMERCE-003, which remains pending on WOOCOMMERCE-002 and API-006. Do not create or edit any `docs/decisions/**/_index.md` files until the user requests final reconciliation.

### Architect implementation clarification — Shopify-source UX walkthrough and manual-first checkpoint (2026-10-10)

**This is the latest authoritative instruction for Attempt 3.** It **supplements** the historical Attempt 1 and Attempt 2 reviews above and **supersedes the immediate execution sequence** in Attempt 2 A2-R1: complete the Shopify-referenced Woo presentation implementation first, hand it to the developer for **manual** visual/functional inspection, and run automated browser/unit/integration/i18n validation **only after explicit developer authorization**. The A2-R1 final visual parity requirement is retained, not marked passed or waived. A2-R2 launcher/worktree evidence remains required in the progress report.

#### 1. Mandatory source study before editing WooCommerce

- Inspect the actual Shopify application repository `moda-interact/` **read-only** from the launcher-prepared development workspace. It is a sibling Git submodule, not part of the Woo plugin. If that source is not materialized/available, report the blocker and STOP rather than inventing how Shopify works or relying only on screenshots. Do not modify the Shopify source or its gitlink.
- Find and read the Shopify merchant Billing landing/summary, recovery-capacity presentation, **Add top-up** and **Change plan** navigation, prepaid-bundle selection, current-plan and cancellation presentation, Woo-excluded purchased-credit-history entry point, and the controllers/hooks/actions managing each journey. Inspect the real source files, not merely visible labels or a static screenshot.
- Trace loading, selection, eligibility, global/per-offer pending/disabled state, confirmation hand-off and return/refresh, provider-outcome-unknown/no-auto-retry feedback, manual refresh, stale responses and connection/disconnect behavior. Identify related design tokens, responsive layout, keyboard/focus handling and locale/translation presentation.
- Record the *actual* Shopify file paths inspected and a concise **Shopify flow -> existing Woo component/controller -> planned Woo change / intentional difference** mapping. Do not claim source paths or behavior that were not inspected.

#### 2. Apply that merchant journey to the existing Woo Billing UI

Developer visual evidence shows Woo currently separates **Summary** (Current plan + Recovery capacity cards) from **Plans** and has a compact Billing header, whereas Shopify's merchant journey promotes **Billing & recovery capacity**, the current plan, **Add top-up**, **Change plan**, contextual cards and guidance. Use that functional hierarchy as the guide; preserve WordPress/WooCommerce's native left navigation and context. Do not copy an unhealthy Shopify billing-configuration warning as the normal Woo state.

- Make the existing plan/available-capacity information discoverable in one coherent Billing landing experience; place direct **Add top-up** and **Change plan** navigation/actions where Shopify guides merchants to them. Preserve a compact, responsive design rather than copying Shopify page structure indiscriminately.
- **Add top-up** should reveal API-defined predefined offers with label, recovery credits, *stored API price*, one Buy action per bundle, global eligibility, independent per-bundle pending/disabled state and bounded provider feedback; when there are no offers, keep an accurate empty state. Never invent offers, balances, prices, availability or billing state for production rendering.
- **Change plan** should reveal the existing eligible catalogue, current-plan marker, plan selection/change controls and accepted Woo confirmation/return behaviour. Preserve cancellation semantics and the corrected explicit command-context attribution; a top-up failure must never display a plan-change notice (or vice versa).
- Keep current plan, lifetime Free, promotional, purchased and paid-included capacity aligned with authoritative API-002 data, and show purchased **balance** without inventing purchase-history/refund routes or placeholder buttons. Full history/refunds and provider navigation remain **WOOCOMMERCE-003**, outside this task.
- Follow Shopify's hierarchy/interaction choices where transferable, but retain Woo's actual WordPress REST cookie/nonce boundary, hosted Moda API, Woo provider redirects, immutable actionId/idempotency, single-flight protections, durable-read-only activation, administrator-locale precedence, and WordPress-native localisation. **Do not copy Shopify APIs, authentication, provider billing implementation or cross-repository state.**
- Reuse/reorganise the existing modular Woo controllers, hooks, components and design tokens; keep state/controllers separate from presentation and do not create a monolithic `billing-screen.js`. Respect existing established ARCH-027-WOOCOMMERCE-004 design foundations.
- Preserve desktop and narrow viewport behaviour, readable long translated text, keyboard/visible focus, disabled states and announced status. Reuse translated strings when possible; any newly visible strings must be properly localised across the approved 20 locales before release. Do not mark unverified translation/visual checks passed in this phase.

#### 3. Explicit no-tests instruction and interim stop

- **Do not run automated tests or validation** during this implementation pass: no JS/PHP/unit/integration/i18n/browser/accessibility suites, no lint or typecheck. `git diff --check` may be run only for patch hygiene, not as a test. This temporary developer instruction is higher priority than the task's usual Validation/Stop Condition for this phase. **Only build and/or package if genuinely needed to load the revised plugin for manual LocalWP/wp-env inspection**; state precisely which commands were executed, and do not report them as tests.
- Do not perform live provider charges, use a production connection, bypass authentication or persist invented purchase state to show the UI. A connected demonstration may be exercised manually by the developer later using an approved test fixture/store; do not automate it now.
- Commit and push the **bounded WooCommerce source changes** on the canonical `task/ARCH-027-WOOCOMMERCE-002` implementation branch and update the same canonical parent task Completion Report/progress evidence without altering this Architect Review. Recover exact Attempt 2/3 launcher heads, synchronization, recursive submodule preparation and claim evidence; do not invent it.
- Report changed files, Shopify inspected paths and flow mapping, UI changes, intentional platform differences, build/package command output if any, and **copy-paste LocalWP/wp-env instructions** to load the new plugin. Describe a short developer manual walkthrough covering Billing landing, Add top-up, Change plan, connected/unconnected offers, desktop/390px layout, pending/unknown states, keyboard focus and translations.
- Leave unexecuted validation/visual acceptance boxes **unchecked**. Keep the task `in_progress` under its valid Attempt 3 claim and return to the developer for the manual checkpoint. Do **not** set `review`/`complete`, promote dependencies, begin WOOCOMMERCE-003, or touch any `docs/decisions/**/_index.md` until authorized. After the developer manually approves the UI, obtain explicit instructions for further changes versus automated tests and normal architect review.
