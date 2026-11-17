---
id: ARCH-077-SHOPIFY-003
architecture_id: ARCH-077
title: Render and activate Shopify cart-page WhatsApp consent App Block
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Render and activate Shopify cart-page WhatsApp consent App Block

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Definition reconciled; task remains `pending`.** Implement only after S001 identity and S002 temporary Redis choice/returning-customer PostgreSQL read contracts have been accepted. No permanent Redis customer preference or click-time PostgreSQL consent write is part of S003.

## Objective

Expose Moda's optional WhatsApp checkout-recovery consent control on the merchant's **existing Shopify cart page** using a merchant-enabled **Theme App Extension App Block**, not a replacement theme, manually edited theme files, checkout injection, global App Embed, cart-drawer injection or WooCommerce code. Provide a safe, merchant-friendly path from Moda's settings into Shopify's theme editor; the merchant chooses placement and saves the theme. All consent capture is delegated to the Shopify-owned S002 backend. **If the Moda Shopify backend/S002 consent endpoint is unavailable, the integration fails silently and the merchant cart remains fully usable.**

**Exact customer-facing disclosure (English):** `Send me WhatsApp shopping updates, reminders and offers.` No wording change, additional marketing permission copy, second mobile-number field, or Shopify Messaging dependency is authorised.

## Repository ownership and touchpoints

**Implementation-owned by S003:**

- Create `extensions/moda-whatsapp-consent/shopify.extension.toml` using the supported Shopify CLI theme-extension manifest (`type = "theme"`). Use the extension directory and block handle below consistently in the manifest, tests and activation-link builder; do not accidentally create a second extension of the same purpose.
- Create `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid` with schema `target: "section"` and `enabled_on.templates: ["cart"]`. Its block handle for links is `cart-consent`.
- Add only necessary packaged JavaScript/CSS under `extensions/moda-whatsapp-consent/assets/`; use Shopify's extension asset loading and storefront locale files under `extensions/moda-whatsapp-consent/locales/` as required by the approved 20-locale presentation contract. S005 owns the full translation/recovery-settings catalogue reconciliation.
- Create `app/services/shopify-consent/theme-activation-url.server.ts` for trusted cart-editor URL construction, and `app/services/shopify-consent/theme-activation-status.client.ts` for the embedded-admin Shopify App API `app.extensions()` read. Keep the latter on the client: it is not a server-side Admin GraphQL query. Add focused unit tests under `tests/unit/shopify-consent/`.

**Existing dependencies, not S003 write targets:**

- `shopify.app.moda-interact.toml` identifies the installed Shopify application and its app/client ID. Any app-proxy registration or storefront authentication change belongs to S001/S002, not ad-hoc S003 changes.
- `app/services/shopify-consent/` (S002) owns cart/session authentication, returning-customer SQL reads, cart-scoped Redis choice writes, conflict handling and acknowledgement.
- `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx` belongs to S005 for integrating the merchant-facing **Enable WhatsApp consent checkbox** action and activation status. S003 must deliver the link/status contract and prove it works; S005 consumes it. Do not modify S005 task or UI in this patch.
- Background checkout lifecycle, Redis candidate-index keys and worker queues are out of S003's write scope.

## Merchant installation and activation contract

1. **Install:** Installing Moda publishes the Theme App Extension with the application but **must not claim the checkbox is already visible**. An App Block requires merchant placement/activation in a compatible published theme.
2. **Activation entry point:** Provide a shop-validated, documented theme-editor deep link. For the published theme and cart template, construct the supported route shape:

   `https://{verifiedShopDomain}/admin/themes/current/editor?template=cart&addAppBlockId={shopifyAppApiKey}/cart-consent&target=newAppsSection`

   Derive `{verifiedShopDomain}` from the authenticated Shopify shop and `{shopifyAppApiKey}` from the installed application's trusted configuration, never an arbitrary browser-supplied domain/client ID. URL-encode appropriate parameter values. The `target=newAppsSection` path is an editor **add/preview flow**, not proof that the block has been saved or positioned directly above the checkout button.
3. **Merchant action:** The merchant opens the cart template in Shopify's theme editor, previews/adds Moda's block in a compatible Apps section, positions it where supported, and explicitly clicks **Save**. Do not modify theme assets programmatically or insert ScriptTag/global DOM interception as a fallback.
4. **Activation verification:** In the embedded Shopify Admin, use Shopify's supported `app.extensions()` App API (subject to the installed framework/API capability) to inspect the published theme's App Block activation. Match the actual `cart-consent` block handle and published theme. Do not equate extension *availability* with block *activation*, or an arbitrary non-cart placement with verified cart-page rendering. If the API does not expose enough evidence for the cart template specifically, report **placement unverified** rather than `enabled`; a bounded storefront/cart rendering check or explicitly approved theme inspection can be evaluated in S005. Do not add `read_themes` scope as a speculative dependency.
5. **Unsupported theme:** If the active theme/cart template cannot host an App Block, explain this condition in the Shopify merchant experience and offer theme-editor/manual supported placement guidance. Do not silently inject code or claim that all themes/cart drawers support this block.
6. **Repeat activation:** If already correctly activated, present a **Manage in theme editor** route that does not intentionally add duplicate blocks; use an officially supported route when available, otherwise open the cart template editor without `addAppBlockId`. Never invent a link that promises to focus an existing block instance without verified platform support.
7. **Ownership:** S003 exports the activation deep-link/status reader for S005; S005 wires the action and its translated merchant-facing status into recovery settings. Shopify installation, extension enablement and customer consent are separate statuses.

## Customer-facing App Block behaviour

- [ ] Render **one** optional WhatsApp consent checkbox on the cart page, accessible by keyboard and screen readers, using the exact approved wording. Use the merchant theme's presentation sensibly; do not alter Checkout, Add to Cart, Shop Pay or express-payment controls.
- [ ] Obtain current non-empty cart token via locale-aware Ajax `cart.js`; send it only as an untrusted cart locator to S002 through the signed-shop App Proxy. The backend validates `{shopId,cartDigest,marker,revision}` and stores a temporary action; **B002** verifies guest checkout token equality or the explicitly verified signed-logged-in customer ID before materialising. Do not claim the client or App Proxy independently authenticated the guest. Do not assume `carts/create` arrived first, rely on Liquid `cart.token` or log raw tokens.
- [ ] For an authenticated returning Shopify customer with a **new** cart, initialise the checkbox using S002's verified PostgreSQL `Customer`/`CustomerPhone` consent read scoped to shop + Shopify customer ID. An existing verified grant displays checked; `UNKNOWN`, `REVOKED`, missing or ambiguous consent does not display a verified grant. A guest with a new cart starts unchecked unless there is a verified choice for that exact current cart.
- [ ] For the **current** cart, an accepted temporary Redis choice from S002 overrides the previously materialised PostgreSQL display state. Reload/re-entry reads the authoritative backend state, not a cached browser Boolean.
- [ ] Only a **deliberate** check sends `GRANT` and only a deliberate uncheck sends `REVOKE` to S002. No action is generated by initial rendering, refresh, Shopify cart events, returning-customer status reads or merely displaying a previously checked consent box. Every choice is acknowledged only after S002 accepts the temporary Redis write; S003 never updates PostgreSQL directly.
- [ ] Handle browser response reordering, two tabs and cart replacement with S002's revision/identity rules; a stale response must not roll back a newer displayed selection or write to the wrong cart. No Redux dependency is prescribed.
- [ ] **Silent degradation (mandatory):** If the Shopify-owned Moda consent endpoint cannot be contacted, times out, returns an error, rejects an App Proxy request, or Redis is unavailable, never show a customer-facing error, warning, retry prompt, toast, modal, spinner that blocks checkout, or technical diagnostic. Do not intercept or delay cart/checkout/payment navigation. This includes first render, returning-customer status reads, and explicit GRANT/REVOKE writes.
- [ ] **Truthful UI under failure:** If initial verified consent status cannot be obtained, omit/hide **only the Moda checkbox** rather than display a guessed checked/unchecked state. If a write fails after the shopper changes the checkbox, never show or retain the unacknowledged choice as saved: quietly restore the last acknowledged displayed state, or hide the Moda control until status is available. Do not change a previously saved PostgreSQL decision or claim that a Redis change succeeded. Normal cart content and controls must remain unchanged. No automatic retry may manufacture an explicit customer action.
- [ ] **Diagnostics:** The Shopify server logs a structured, redacted failure category plus the actual underlying provider/transport error message and safe response details. Do not expose raw cart tokens, personal data, access tokens or stack traces to shoppers. Do not introduce unbounded request retries or repeated status polling when the service is unavailable.
- [ ] Use the approved customer-facing locale catalogue with identical translated meaning across Shopify locales. The actual displayed text/version/locale must be supplied to S002; the application does not reuse WooCommerce PHP or translation files.
- [ ] Do not add a separate telephone field, marketing popup, forced cart interception, cart-drawer renderer or Shopify native WhatsApp consent controls. Customers bypassing the cart via express checkout are not covered by S003; Plus checkout support belongs to S004.
- [ ] Do **not** delete Redis choice keys on unload, navigation to checkout, theme-editor preview or browser close. BACKGROUND-001 owns lifecycle cleanup according to recovery eligibility and retries.

## Required cart-marker injection and validation

- [ ] On Shopify cart App Block initialisation, fetch the current cart using locale-aware `/cart.js`. Call S002's authenticated app-proxy `cart/prepare` once per current verified shop/cart (not on each render or checkbox re-render); the app returns the existing server-issued `m1_` marker on retry. Derive the actual merchant proxy prefix from supported configuration, not a hard-coded storefront path that merchants can customise.
- [ ] Before displaying an actionable Moda checkbox, write **only** `attributes: { moda_cart_correlation_v1: marker }` to the locale-aware `cart/update.js` endpoint. Verify the returned cart's attribute equals the issued marker; if the response omits attributes, re-fetch the current `/cart.js` and verify. Do not overwrite unrelated cart attributes, change cart contents or trigger a consent action from this write.
- [ ] If the existing current-cart attribute already equals the S002-issued marker, do not rewrite it. A different/unknown marker or changed cart token must be revalidated against S002, rewritten only for the new verified cart, and verified before re-enabling actions. Do not silently reuse a stale marker or transfer a GRANT/REVOKE between carts.
- [ ] Failed App Proxy authentication, S002/Redis prepare, marker write, Ajax read-back, malformed cart or lost browser session: hide only Moda's consent control without showing any technical error, blocking navigation or claiming that a new consent action succeeded. **No synchronous checkout interception or redirect delay** is permitted; express checkout bypasses this path and cannot fabricate a grant.
- [ ] Only once the marker binding has been acknowledged and the cart read-back has succeeded may a deliberate checkbox action be submitted to S002 `cart/choice`; S002 independently re-verifies shop, cart-action ownership and marker binding. Unchecked default, status display, marker creation, cart mutation and cart webhook never grant or revoke consent.
- [ ] Test with actual Shopify cart/checkout: both checkout-create and checkout-update carry the same marker as `note_attributes`; cart-webhook marker fields may be absent. Validate duplicate page renders, two tabs, locale-specific routes, cart regeneration, missing proxy, failed marker writes and shopper-controlled marker tampering without changing normal checkout.

## Consent action has no cross-recovery effect

- [ ] A deliberate check/uncheck after verified marker read-back submits the S002 temporary choice only. Do not call STOP, any SQL update, an outreach-admission route or a cache-based proactive suppression endpoint. For a returning customer with SQL GRANTED, the newly unchecked **display** is temporary for the current cart; unrelated recoveries retain their already persisted admission state until this cart becomes independently recoverable. A paid cart discards the temporary selection.
- [ ] Keep exact English checkbox text `Send me WhatsApp shopping updates, reminders and offers.` and translated meaning; do not add explanatory wording or silently modify checkbox labels/defaults for deferred-consent semantics.

## Tests, evidence and acceptance

- [ ] Shopify CLI validates/packages the extension; test the `cart` template restriction, block schema, asset loading and all relevant storefront locale resources.
- [ ] In a real standard-plan Shopify development store with a compatible JSON cart template: app installation exposes the block in **Apps**; the documented deep link opens the cart editor with the correct block staged; merchant can add, reposition and **Save**; the published cart subsequently renders exactly one Moda checkbox.
- [ ] Verify the fallback when the cart section is incompatible, a section is full, the block is already added, the merchant does not save, or a theme is replaced/unpublished. Do not claim successful activation until the published theme supports that conclusion.
- [ ] Exercise `app.extensions()` activation reporting on the **published theme**. Confirm `available` vs `active` vs `unavailable` are not conflated; absent/ambiguous cart placement is reported `unverified` rather than guessed. No new `read_themes` scope without a separate decision.
- [ ] New guest cart: unchecked, no grant on render. New logged-in customer cart: retrieve SQL state via S002, not a persistent Redis customer key. Verified returning GRANTED: checked, no new GRANT event merely from display. REVOKED/UNKNOWN: unchecked.
- [ ] Explicit check/uncheck writes only temporary S002 Redis choice, with unchanged PostgreSQL consent until recovery maturity. Refresh shows latest accepted choice; stale browser responses and cart changes cannot restore an older choice.
- [ ] Cart token missing, Moda endpoint outage/timeout/5xx, Redis outage, App Proxy rejection, failed status read, failed GRANT/REVOKE write, navigation away and express checkout do not block checkout or create permission. Assert **no customer-facing technical error, notification, prompt, or blocking UI**, and verify initial unknown state hides only the Moda control while a failed write does not appear acknowledged. Test keyboard accessibility and mobile cart layout.
- [ ] Verify that the Shopify server still records a redacted original underlying failure when available, without exposing personal data or raw Shopify tokens in storefront output or logs.
- [ ] Tests verify **zero changes** to Background candidate indexes, BullMQ payloads, queue TTLs and checkout locks from S003 UI operations; no Redis cleanup or recovery admission is triggered by render alone.
- [ ] Capture repository commit SHA, Shopify plan/theme name, deployed app/extension identifiers, published-theme activation evidence, exact test commands and redacted browser/network traces. Distinguish mocked unit tests from actual theme-editor/storefront tests.

**Stop conditions:** If reliable current-cart association, storefront action verification, supported App Block placement or merchant-controlled activation cannot be demonstrated, do not work around the problem with manual theme edits, arbitrary DOM injection, an app-wide checked preference, a second phone field or unverified consent writes. Return the precise limitation for architect review. Do not change any other ARCH-077 decision document, shared database schema, WooCommerce application, Woo API or Background worker as part of S003.
