---
id: ARCH-027-WOOCOMMERCE-003
architecture_id: ARCH-027
title: Add WooCommerce purchase history and provider refund navigation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 85
executor: null
claimed_at: null
attempt: 5
depends_on:
  - ARCH-027-WOOCOMMERCE-002
  - ARCH-027-API-006
enables: []
created: 2026-10-03
updated: 2026-10-11
---

# Add WooCommerce purchase history and provider refund navigation

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Complete the Woo **Purchased credits** merchant experience with Shopify-aligned purchase-history cards, filters, pagination, refund status and a **provider-owned external WooCommerce.com refund-request link**, inside the existing Billing surface.

The Woo plugin does **not** create, cancel, reactivate or settle a refund. Its accepted flow is:

```text
Billing > Purchased credits
    -> view purchase/refund history from hosted API-006
    -> eligible merchant clicks Request refund on WooCommerce.com
    -> external https://woocommerce.com/my-account/orders/
    -> merchant/provider/vendor refund workflow outside Moda
    -> later refresh of durable Moda purchase/refund status
```

## Context

WOOCOMMERCE-001 (Complete) supplies the accepted native WordPress Billing screen, authenticated browser -> WordPress REST -> PHP client -> hosted API pipeline, return handling and connection/stale-response protections.

WOOCOMMERCE-004 supplies modular Billing composition, Shopify-aligned layout and explicit administrator-locale display formatting. WOOCOMMERCE-002 adds top-up bundle purchases inside that same Billing experience. This task builds on those **accepted** modules rather than introducing a second page/router/controller or expanding the old `billing-screen.js` into a monolith.

API-006 owns the read-only `/v1/billing/recovery-credit-purchases` history and provider refund navigation projection; it remains Pending until BACKGROUND-005. The refund workflow intentionally differs from Shopify's local refund-hold and merchant reactivation UI. Reuse Shopify's **visual** purchase-history reference (`app/routes/app/billing/recovery-credit-purchases/route.tsx` and associated styles), but do not reproduce Shopify's checkbox batch refund submit, local refund dialog or reactivation actions.

The Woo plugin's WordPress gettext pipeline requires all **19 non-English** PO catalogues, strict compiled PHP/JS translation assets and `plugin-zip` validation for every new visible history label/status/action.

The existing filename mentions reactivation for historical reasons; **reactivation is expressly prohibited** in this task. Retain the filename so existing task discoverability/references are not broken.

## Scope

Only `moda-interact-woocommerce`:

1. Add the `Purchased credits` internal Billing view using current native navigation/connected-workspace composition.
2. Extend the accepted PHP `ModaApiClient` / privileged Billing REST controller with one **GET-only** local history proxy to API-006.
3. Add modular history data/controller state and separate filter, card/status, pagination, refund-guidance and external-link components under the accepted `src/billing/` boundary.
4. Display the exact API-006 filters, page sizes, bounded purchase/refund summaries and safe WooCommerce Orders refund navigation.
5. Deliver Shopify-aligned history presentation using Woo's existing scoped design tokens and complete WordPress administrator localisation.
6. Validate permissions, provider-only refund link, no mutation, pagination, stale response/disconnect, responsive/accessibility and packaged locales.

## Out of Scope

- Woo merchant refund POST, allowance hold, batch selection/submit, refund confirmation dialog or local refund reactivation/cancel operation.
- Provider monetary calculation, Woo vendor operations, settlement, Admin vendor approval/rejection and Background webhook reconciliation.
- Provider contract/transaction IDs, internal billing-period IDs, raw webhook evidence or Shopify handles in browser responses.
- New top-level WordPress page, Purchased credits submenu, frontend router or state-management framework.
- Direct hosted Moda API call from browser, browser storage of customer/billing history, Woo vendor secrets.
- Changing WOOCOMMERCE-001 recurring billing or WOOCOMMERCE-002 top-up command behaviour.
- Database/API/Gateway changes; editing `docs/decisions/**/_index.md` or `docs/architecture/_index.md` until session finalisation.

## Requirements

### R1 — Existing Billing internal view and Shopify visual parity

Expose `Purchased credits` **inside** the current native WordPress `Billing` submenu / `ConnectedWorkspace` Billing screen. Provide an obvious, accessible in-Billing switch/back-navigation using existing Woo presentation/navigation patterns.

Match Shopify's relevant card hierarchy, filters, status badges, date/credit metrics, empty/error/loading states and pagination affordances using the accepted WOOCOMMERCE-004 design tokens. Do **not** copy Shopify's multi-select toolbar, local refund dialog, refund POST or reactivation action. Cards must adapt to narrow WordPress admin layouts and longer translated copy.

### R2 — Exact local history proxy (GET only)

Local authenticated route:

```text
GET /wp-json/moda-interact/v1/billing/recovery-credit-purchases
    ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
    &page=<positive integer>
    &pageSize=5|10|20
```

Forward only validated filter/page/pageSize to API-006's `GET /v1/billing/recovery-credit-purchases` through the server-side `ModaApiClient` using the stored installation credential. Enforce `manage_woocommerce`, WordPress REST cookie/nonce checks and established `_locale=user` compatibility at the local boundary. Do not accept a client-supplied `shopId`/provider or forward unexpected arguments.

### R3 — Filters/pagination

Use exact `ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL`, page sizes `5|10|20`; defaults `ACTIVE`, `1`, `5`. Reuse API-006's bounded pagination metadata and page clamp (last available page; empty uses page 1). Reset page when changing filter/page size and ignore responses from superseded requests/disconnected sessions. No unbounded fetch/polling.

### R4 — Merchant-safe purchase and refund cards

For each API-006 purchase row, render only relevant merchant-facing fields:

```text
status, createdAt, activatedAt, bundleLabel, planName
creditsGranted, currentAmount, reservedAmount, availableAmount, heldForRefundAmount
refundEligible, refundUnavailableReason, refundAttempted
latestRefund, completedRefund
originalProviderPurchase amount/currency when supplied
```

Use API-provided values only, with the WOOCOMMERCE-004 WordPress administrator UI locale formatter for dates, amounts and quantities. Never infer/refund-price math locally. Do not display raw provider evidence or contract/transaction IDs; a bounded opaque purchase `id` may be used internally for stable row identity, not merchant disclosure.

### R5 — Provider-owned refund navigation only

Render `Request refund on WooCommerce.com` **only when** the purchase says `refundEligible=true`, `refundAttempted=false` and the API-006 top-level `refundRequest.method=WOOCOMMERCE_ORDERS` with its approved HTTPS Orders URL is present.

Use the exact API-provided URL through the accepted safe external-link/navigation helper. Treat navigation as **link only**. It MUST NOT call a Moda mutation route, create a local hold, optimistically change purchase state or construct a provider URL from untrusted identifiers. Prevent unsafe redirect/URL schemes and test the known `https://woocommerce.com/my-account/orders/` contract.

### R6 — Merchant guidance

Provide accurately translated guidance equivalent to:

> Open your WooCommerce.com orders, find the Moda Interact purchase and request a refund using Woo's process. Moda updates credits and status after the provider/vendor decision is verified.

Do not depend on transient provider dashboard labels or imply the click itself requests the refund from Moda. Explicitly identify the external site to assist screen-reader users.

### R7 — One-attempt presentation

If `refundAttempted=true`, **never** show the refund request link for that purchase, including after `latestRefund.status=REJECTED` or `CANCELLED` and restored allowance. Display a bounded explanation such as “This purchase already has a refund request.” Do not offer another attempt.

### R8 — No merchant undo or batch refund

No `Reactivate credits`, `Cancel refund`, refund selection checkboxes, batch actions, refund confirmation dialog or local refund mutation route. A Woo vendor/provider outcome is outside this plugin's write authority.

### R9 — Status presentation

Map and translate all applicable purchase states:

```text
ACTIVE                   Active
WITHDRAWN                Refund under review / credits held
COMPLETED                Used
REFUNDED                 Refunded
```

And the relevant refund history states:

```text
REQUESTED                Refund request being prepared
PROVIDER_ACTION_REQUIRED Awaiting vendor decision in Woo
REJECTED                 Refund rejected; eligible allowance restored if applicable
COMPLETED                Refund completed
NEEDS_ATTENTION          Refund needs review
```

Distinguish purchase COMPLETED from refund COMPLETED. Status information must remain textually meaningful without color or icon alone.

### R10 — Connection/stale-response safety

Reuse WOOCOMMERCE-001/002 controller session generation, AbortController/stale-response and authenticated error handling. On disconnect/credential rotation, immediately clear any purchase/refund state and prevent late data from rendering. Refresh from durable API state after provider workflow; do not infer completion from a Woo browser redirect or polling.

### R11 — No browser persistence/internal identifiers

Do not persist purchase/refund data or commands in `localStorage`, `sessionStorage`, WordPress options or cookies. Do not display provider contract IDs, transaction/request keys or raw provider evidence. React makes no direct hosted API or provider calls.

### R12 — Complete WordPress internationalisation and accessibility

Use `@wordpress/i18n` and `moda-interact` domain for all filter names, counts/ranges, statuses, pagination, empty/error states, merchant guidance, external-link labels and aria/live-region copy; use statically extractable gettext messages and correct placeholders. Translate additions across the POT and all 19 non-English PO files, compile PHP `.mo`/JS JSON assets and verify ZIP packaging. Respect WordPress admin UI locale (site fallback) for formatting, not browser/store locale.

All filter controls, pagination and links must be keyboard-usable, with active/disabled/current state exposed accessibly and tested at mobile sizes and long translation lengths.

## Work Items

- [ ] Reuse WOOCOMMERCE-004 modular Billing shell and add internal Purchased credits view without new native menu.
- [ ] Add GET-only privileged PHP history proxy, exact query forwarding, strict/merchant-safe response checks.
- [ ] Add isolated history controller/state with filter/page/pageSize, abort and disconnect protections.
- [ ] Add Shopify-aligned but Woo-safe card/filter/status/pagination components and external refund guidance.
- [ ] Ensure prior refund attempt always suppresses provider refund link; no batch/refund/reactivation command exists.
- [ ] Format amounts/dates/counts via WordPress administrator locale helper.
- [ ] Extract/translate all new strings in all 19 PO catalogues, compile and package assets.
- [ ] Add focused PHP/JS/locale/keyboard/responsive tests and plugin package evidence.

## Interfaces / Contracts

### Read model

Owner: `ARCH-027-API-006`.

```text
GET /v1/billing/recovery-credit-purchases
  ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
  &page=...
  &pageSize=5|10|20
```

Versioned response: `schemaVersion=1`; bounded purchase rows and pagination; top-level `refundRequest={method:'WOOCOMMERCE_ORDERS',url:'https://woocommerce.com/my-account/orders/'}`.

### Local provider proxy

Owner: `ARCH-027-WOOCOMMERCE-003`. GET-only local WordPress REST route using existing PHP credential/client and nonce/capability checks. No local or hosted refund mutation route is added.

### Presentation

Owner: `moda_woocommerce`. Reuse accepted WOOCOMMERCE-004 components/formatters/design tokens and WordPress gettext 20-locale pipeline. API-006 is the source of merchant purchase/refund state; the browser never computes refund/allowance authority.

## Dependencies

- `ARCH-027-WOOCOMMERCE-002` — accepted Complete after WOOCOMMERCE-004 foundation.
- `ARCH-027-API-006` — accepted Complete and available with provider-safe history contract.

Both are required. This task remains Pending until they are Complete.

## Enables

None. This is a Woo implementation prerequisite for the terminal ARCH-027 integrated/system-test certification, not a provider workflow owner.

## Acceptance Criteria

- [ ] Purchased credits view stays inside native Billing page with Shopify-aligned responsive history/filter/status presentation but no Shopify-specific refund batch/local actions.
- [ ] Exactly one authenticated local **GET-only** history route forwards validated filter/page/pageSize; no merchant refund/reactivation POST endpoint exists.
- [ ] History filters/page sizes/defaults and API page clamp work with stale-response protection.
- [ ] Purchase/refund cards render only API-006's merchant-safe fields, with admin-locale formatting and accessible statuses.
- [ ] Eligible purchase displays only the approved WooCommerce.com external refund link; following it causes **zero Moda mutations**.
- [ ] `refundAttempted=true` permanently suppresses provider link even after refund rejection/restored credits.
- [ ] Distinct purchase/refund status states (including NEEDS_ATTENTION) and useful provider guidance are translated/accessibly rendered.
- [ ] Reconnect/disconnect clears history and rejects stale responses; no browser storage or hidden identifiers leak.
- [ ] Every new string has reviewed translation in all 19 non-English PO files, valid placeholders and compiled PHP/JS language assets in `plugin-zip`.
- [ ] Mobile/long-translation layout, focus order, disabled controls and external-link context are tested.
- [ ] No `_index.md` or unrelated application/provider/database code changed.

## Validation

Inspect `package.json`/Composer and run applicable declared checks, including:

- [ ] PHP `BillingController` GET-route permissions/nonce/validation/provider forwarding tests, proof no refund POST;
- [ ] JS Billing view/filter/pagination/controller and stale-response/disconnect tests;
- [ ] `refundAttempted` no-link test (including REJECTED and restored credit states);
- [ ] HTTPS Orders URL/safe external navigation and zero Moda mutation test;
- [ ] all purchase/refund status/empty/error, accessible text/keyboard and long-label responsive tests;
- [ ] WordPress administrator vs browser/store locale format assertions;
- [ ] `npm run test:i18n`, `npm run i18n:verify:20`, POT+19 PO/placeholder coverage;
- [ ] `npm run test:js`, `npm run test:php`, `npm run lint:js`, `npm run lint:css` and PHP lint as applicable;
- [ ] `npm run plugin-zip` with compiled `.mo`/JavaScript JSON asset verification;
- [ ] repository-required LocalWP/WordPress/package-lifecycle integration smoke where available;
- [ ] `git diff --check`, bounded diff and canonical task worktree / sync / Completion Report evidence.

## Stop Condition

Complete Work Items, Acceptance Criteria and Validation; populate Completion Report, set status to `review`, return to `moda_architect`, and **STOP**. Do not implement another provider/refund task.

## Implementation Notes

The task's filename is retained for stable workflow references; its actual accepted architecture prohibits Reactivate/Cancel refund controls. Shopify is a visual reference only. Use small focused modules and keep existing plugin/REST/security boundaries.

## Completion Report

### Status

Implemented through developer-applied Attempts 1–5 and **accepted for Woo plugin
implementation closure on 2026-10-11**. The accepted boundary is the
purchased-credit history and provider-owned Orders navigation UI, **not** real
WooCommerce.com payment/refund certification. No implementation commit, task
worktree or push is asserted by this architect documentation-only overlay.

### Files Changed

Developer-applied WooCommerce implementation and focused tests include:

- PHP boundary: `includes/Rest/BillingController.php`,
  `includes/Api/ModaApiClient.php`,
  `includes/Api/BillingPurchaseHistoryResponseValidator.php`, and the Composer
  class map;
- UI/controller: `src/billing/connected-billing-screen.js`,
  `src/billing/purchase-history-{client,contract,controller,screen,filters,
  card,pagination,guidance}.js`, `src/billing/use-purchase-history.js`,
  `src/billing/purchased-credit-history-card.js`, and thin Billing shell wiring;
- scoped billing-history styles, POT/PO and compiled translations, JS/PHP and
  i18n tests.

This acceptance patch itself modifies only this parent task record. No
production code, `_index.md` or architecture index is changed.

### Work Completed

- Enabled **Manage purchased credits** inside the existing native WordPress
  Billing destination; added Back to billing, Shopify-aligned cards, accessible
  empty/loading/error states, filters and 5/10/20 pagination.
- Added one privileged, authenticated **GET-only** history proxy to API-006,
  with validated query arguments, bounded response checks and server-held
  installation credentials; no new merchant refund mutation route.
- Implemented provider-reported purchase/refund statuses, API-owned refund
  eligibility and a validated `https://woocommerce.com/my-account/orders/`
  external navigation link only for qualifying purchases without a prior
  refund attempt.
- Kept refund initiation, vendor decision, money and credit-hold settlement
  outside the Woo plugin; no batch refund, cancellation or local reactivation.
- Kept controller and presentation modules separate and completed the
  administrator-locale WordPress gettext pipeline for all 20 supported locales.
- Corrected obsolete UI assertions, formatting/JSDoc/translation comments and
  lint issues through Attempts 2–5; Attempt 5 is the accepted local source
  validation baseline.

### Validation Results

- **Developer-reported local checks: PASS.** After Attempt 5, the developer
  confirmed JavaScript and CSS lint, JavaScript tests, PHP tests, and plugin
  build/packaging all pass. No raw terminal output for the final PHP or plugin
  ZIP runs was independently captured in this architect review.
- Prior developer-provided logs showed **176/176 JavaScript tests passing**
  and **37/37 integration/i18n tests passing**; the earlier CSS lint pass and
  history screenshot were reviewed. These are earlier logs, not claims of an
  independent architect rerun after Attempt 5.
- Earlier i18n verification covered **243 source messages**, all 19
  non-English locale packs, and **28/28 focused i18n checks**; subsequent
  patches introduced no new translation strings.
- **Manual visual evidence:** the merchant's LocalWP screenshot showed the
  Purchased credit history view, filter tabs, `0–0 of 0` empty state,
  pagination and Back to billing affordance after resetting the test database.
  A real confirmed purchase/refund row was not exercised in that screenshot.
- Previous incremental source patches were checked for Git whitespace and ZIP
  integrity against their stated upload baselines. The acceptance overlay was
  verified independently against the exact 2026-10-11 17:07 workspace archive.

### Deviations

The developer explicitly used a manual patch/apply/validate flow, instead of
an agent-created dedicated task worktree and agent Completion Report. This is
recorded as a task-workflow deviation; no launcher isolation, Git commit or
remote merge evidence is claimed for WOOCOMMERCE-003.

### Assumptions

The user's final all-green confirmation refers to the implemented Attempt 5
checkout and the previously reported PHPUnit dependency restoration, with
`npm run plugin-zip` completing after developer dependencies were available.
The 17:07 archive predates the small Attempt 5 formatting correction, which
was separately delivered and developer-validated.

### Unresolved Issues

1. WooCommerce.com Marketplace SaaS Billing **sandbox API key/secret have not
   been issued**. Real hosted charge initiation, checkout/confirmation and
   provider tax/settlement behaviour remain unverified.
2. The local WordPress HTTP origin does not satisfy the hosted API's current
   HTTPS return-URL requirement; real provider testing needs a valid HTTPS
   return origin.
3. No real Woo one-time purchase/refund or signed provider webhook settlement
   has been certified; provider money, vendor decisions and Moda allowance
   changes remain separate release/integration gates.
4. In the uploaded parent record `ARCH-027-API-006` still has `status: ready`,
   despite the developer-applied and locally passing API implementation.
   Formally reconcile and architect-accept API-006 before claiming the full
   ARCH-027 dependency/release chain is closed. `BACKGROUND-005` was Complete
   in the same snapshot.

### Architectural Concerns

The plugin correctly does not turn a link click into a Moda refund request or
infer refund completion from a browser return. Keep financial certification,
provider reconciliation and the API-006 task-metadata dependency visible.

## Architect Review

### Review Status

Accepted — **WooCommerce purchase-history UI implementation** (Attempt 5).
External provider billing/refund certification is expressly **not accepted**.

### Review Notes

Accepted the developer-applied implementation scope after source-level review,
manual LocalWP history-view evidence, reported green local validation and
repeated bounded lint-correction patches. The implementation intentionally
mirrors Shopify's history *presentation* but uses provider-owned external
WooCommerce.com Orders refund initiation. No local Woo merchant refund POST or
merchant reactivation flow is authorized by this acceptance.

### Reviewed Files

The 2026-10-11 workspace snapshot's Woo Billing controller/client and
`src/billing/purchase-history-*` modules, `use-purchase-history.js`,
`includes/Rest/BillingController.php`, `includes/Api/ModaApiClient.php`,
`includes/Api/BillingPurchaseHistoryResponseValidator.php`, purchase-history
JS/PHP tests, localisation assets and related incremental correction patches.

### Validation Reviewed

Developer-reported Attempt 5 local all-green result; earlier JS 176/176,
integration/i18n 37/37, i18n 28/28, CSS lint, and manual screenshot evidence.
Latest PHP suite/build/plugin ZIP success is developer-reported, not
independently reproduced by the architect. No real WooCommerce.com sandbox
transaction, provider refund approval or signed webhook certification ran.

### Architecture Conformance

Conforms for the scoped WordPress merchant UI: provider/tenant data remains
behind the authenticated PHP boundary; history is read-only; server-owned
eligibility gates the approved external Orders link; no browser-created
provider evidence, financial refund mutation or local reactivation is added.
The task's dependent API-006 record still needs formal status reconciliation,
and ARCH-027 production certification remains open.

### Follow-up

- Reconcile/architect-accept `ARCH-027-API-006` task metadata on its already
  developer-tested implementation; do not infer acceptance from its current
  `ready` state.
- Complete `ARCH-027-ADMIN-001` vendor-side refund support and associated
  trusted `BACKGROUND-005` integration/system-test evidence.
- Obtain Woo SaaS sandbox credentials and HTTPS return infrastructure; certify
  real top-up charge activation, purchase-history/refund status updates and
  signed provider settlement before production release.
- Leave all `docs/decisions/**/_index.md` and architecture indexes unchanged
  until the user authorizes the final architecture reconciliation.
