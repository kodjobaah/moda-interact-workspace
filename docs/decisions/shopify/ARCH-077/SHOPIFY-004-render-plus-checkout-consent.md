---
id: ARCH-077-SHOPIFY-004
architecture_id: ARCH-077
title: Render Shopify Plus checkout WhatsApp consent checkbox
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
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHOPIFY-002]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Render Shopify Plus checkout WhatsApp consent checkbox

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending architectural review. Do not implement before S001's Plus checkout token/session proof and S002's temporary Redis/PostgreSQL-read contract are accepted.** Where earlier architecture/task drafts describe permanent customer preference in Redis, follow accepted S002: **Redis stores only temporary cart/checkout choices; returning-customer state is read from existing PostgreSQL records.** This amendment is S004-specific except for the explicitly requested S003 silent-failure companion amendment.

## Objective

For supported **Shopify Plus** stores, display Moda's optional consent control **inside the Shopify-hosted checkout**, immediately following the contact section. Record deliberate consent changes against the existing, verified checkout token using S002's Shopify backend/temporary Redis service. Do not create a second phone input, depend on Shopify Messaging/native WhatsApp marketing consent, or write the checkbox choice to PostgreSQL at click time. Consent is applied to existing customer records **only if Background determines the checkout is recoverable**, as agreed in S002.

**Exact customer-facing disclosure (English):** `Send me WhatsApp shopping updates, reminders and offers.` Use the independently maintained Shopify locale/version contract; do not edit or import WooCommerce locale files.

## Repository ownership and touchpoints

**S004 implementation-owned:**

- Create a **separate** Shopify Checkout UI Extension at `extensions/moda-whatsapp-checkout-consent/` using the supported Shopify CLI checkout-extension scaffold, with its `shopify.extension.toml`, supported entrypoint/assets, and checkout extension tests. Do not reuse the S003 theme-extension directory (`extensions/moda-whatsapp-consent/`) as a checkout extension.
- Declare the supported checkout static target `purchase.checkout.contact.render-after` and the network-access capability required to call the authenticated Moda Shopify backend, if required by the selected Checkout UI API version. Use the supported checkout extension UI APIs/components for that version; do not use unsupported theme Liquid, script tags, DOM scraping or Shopify's built-in SMS marketing consent checkbox.
- Add the narrow Shopify-only checkout consent client adapter under `app/services/shopify-consent/` only where S002's published contract requires it; reuse S002's existing authenticated consent endpoint/read and Redis writer. Do not implement a second independent permission service or duplicate consent validation in the browser.
- Add focused tests under `tests/unit/shopify-consent/` and extension-owned test files, following the repository's test conventions.

**Dependencies/reference-only:**

- S001 owns verification of the checkout identity, session-token claim and signed-token request proof; no acceptance of an arbitrary browser-supplied checkout token.
- S002 owns PostgreSQL read for verified returning customers, temporary Redis action storage, idempotency/revisions and server error logging. S004 never writes `CustomerPhone` or `Customer` on checkbox interaction.
- S003's theme App Block may be active on the same Plus store. BACKGROUND-001 associates prior cart choices with the checkout; BACKGROUND-002 alone owns recovery maturity, contact-number selection, final consent admission and cleanup.
- S005 owns merchant-facing checkout-extension activation guidance and translated status in `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx`. S004 supplies extension identity/target and verified activation prerequisites; do not change S005's task in this patch.

## Rendering and checkout identity

1. **Supported placement:** Use the supported `purchase.checkout.contact.render-after` checkout target for Shopify Plus. The control appears below the buyer contact section and is optional. Do not assert this target can be mounted on non-Plus information/shipping/payment checkout steps. Confirm target/API support on a real eligible Plus development store before claiming completion.
2. **Verified checkout:** Obtain the current checkout token through the supported Checkout UI Extension API and the session token through Shopify's extension session-token API; the Shopify backend validates the signed request context, shop and checkout association according to S001. If either identity is missing/unverifiable, no GRANT/REVOKE is recorded and only the Moda control is omitted. An extension session token alone must not authorise changes to an unrelated checkout ID.
3. **Recipient:** Do not add a WhatsApp phone field, fetch Shopify's `defaultPhoneNumber.whatsAppMarketingConsent`, or infer recipient ownership from a checkout address. BACKGROUND-002 chooses an eligible recipient at maturity under the frozen customer phone → billing phone → shipping phone rule.
4. **Payment independence:** No mandatory consent control, Checkout Blocking API validation, forced Continue/Pay interception, storefront theme alteration, or additional required checkout input. Shop Pay/accelerated routes that do not render the target remain uncovered by S004; do not invent fallback injection.

## Initial state, cart compatibility and explicit actions

1. **Display precedence for the same verified checkout:**
   - The latest *accepted* explicit checkout choice in S002 Redis.
   - Otherwise, the latest accepted cart choice authoritatively associated with this checkout by BACKGROUND-001.
   - Otherwise, the existing materialised consent decision read from PostgreSQL by S002 for a **verified returning Shopify customer**, scoped to that merchant and customer identity.
   - Otherwise, an unchecked checkbox.
   These are display precedence rules, not automatic permission writes. An unchecked default or checkbox render is neutral.
2. **Both extensions present:** A Plus merchant may activate S003 on the cart and S004 during checkout. S004 displays the verified prior cart selection if the checkout has no later explicit choice; an explicit checkout selection supersedes the cart selection for that checkout. Do not create another cart record merely because checkout starts. Re-rendering the already checked state must never emit GRANT again.
3. **Returning customer with a new cart:** Use S002's authenticated Shopify customer identity and PostgreSQL `Customer`/`CustomerPhone` current consent read, **not a long-lived Redis customer preference key**. GRANTED displays checked where verified; UNKNOWN, REVOKED, ambiguous and absent do not claim current permission. An existing current-checkout/cart choice has precedence for that checkout.
4. **Guest checkout:** A guest may check/uncheck only for the current verified checkout and may later return to that checkout. Do not restore another guest's prior grant from matching phone/email/address or a different cart.
5. **Deliberate changes only:** An explicit check calls S002 `GRANT`, an explicit uncheck calls S002 `REVOKE` for the verified checkout, with S002's idempotent action identity/revision handling. No write on render, reload, buyer data change, failed status read or checkout-created webhook. **Neither action updates PostgreSQL immediately.** S002 stores changes temporarily in Redis, and Background applies the most recent applicable decision only at eligible recovery maturity. An ordinary completed checkout generates no consent materialisation.
6. **Reload and identity changes:** A reload displays the latest accepted state. New checkout token, changed verified shopper identity, cart association change, stale response or two open checkout tabs must not transfer an unverified consent choice or roll back a newer accepted revision. A read failure must never be interpreted as a verified GRANT or REVOKE.

## Silent failure and checkout availability — mandatory

- **Fail silently:** If the Moda **Shopify-owned** consent endpoint cannot be contacted, times out, returns an HTTP error, rejects session authentication, or Redis/PostgreSQL consent reads are unavailable, show **no customer-facing error, toast, banner, modal, blocking spinner, retry prompt or diagnostic text**. This does not mean the request succeeded. Checkout navigation, address entry, shipping selection and payment must continue normally. Do not invoke the separate WooCommerce-facing `moda-interact-api` service.
- **Initial read failure:** Omit/hide **only the Moda extension control** instead of guessing a checked/unchecked state. Other checkout UI must be unaffected. Do not auto-check on an unavailable response.
- **Write failure:** A changed checkbox is committed only after S002 confirms its temporary Redis write. If the write fails, quietly restore the last acknowledged displayed state or hide the Moda control until a verified status can be obtained. Do not leave the attempted selection displayed as saved, silently create an action on retry, or update SQL permission.
- **Bounded requests:** Use a bounded timeout and no unbounded retries/polling. Browser output must not expose internal errors, raw cart/checkout tokens, recipient numbers, customer IDs or credentials. The **Shopify server** must log redacted structured failures while retaining the original underlying SDK/transport message and safe response details for diagnosis.

## Merchant activation boundary

- [ ] Shopify merchants must enable this **Checkout UI Extension** in Shopify's checkout editor and save/publish as the platform requires. It is **not** activated by placing S003's Theme App Block in Online Store → Themes.
- [ ] S004 identifies its actual extension handle and declared target and supplies documented setup/activation evidence for S005. S005 provides merchant-facing activation instructions/status; no speculative theme-editor App Block deep link may be reused for the Plus checkout editor.
- [ ] Report unavailable/unsupported placement accurately rather than claiming the extension runs on every Shopify plan or accelerated checkout path.

## Tests and acceptance

- [ ] Shopify CLI validates/packages the checkout extension and its selected API target/capability; confirm the static contact target in a **real Plus** checkout, including published checkout activation.
- [ ] New guest: unchecked, no write on render. Verified returning customer: read current SQL decision via S002; GRANTED checked, REVOKED/UNKNOWN unchecked; do not persist a new decision from display.
- [ ] Both S003 and S004 activated: accepted cart GRANT displays checked in checkout; later explicit checkout REVOKE displays unchecked and supersedes cart choice. Cart REVOKE followed by explicit checkout GRANT becomes the latest accepted choice. Duplicate/late webhook does not restore a stale choice.
- [ ] Checkout identity/session-token validation, token temporarily undefined, token refresh, changed authenticated identity, same-checkout reload, anonymous checkout, stale responses/two tabs and express/Shop Pay bypass cases are covered.
- [ ] Check/uncheck writes only to temporary S002 Redis records; verify **zero SQL consent writes** before recovery maturity and unchanged Redis candidate indexes, BullMQ jobs, queue TTLs, checkout locks and order tombstones.
- [ ] Moda backend unreachable/timeout/5xx, signed-session rejection, Redis unavailable and PostgreSQL status read failure: assert no shopper-visible error or blocking checkout UI; read failure hides only Moda control; failed write is not shown as acknowledged. Original safe server-side failure details remain diagnosable.
- [ ] Verify keyboard/screen-reader accessibility, applicable Shopify locale presentation and exact English wording. Do not add an extra phone field, WooCommerce API call, Shopify-native consent call or DOM/script fallback.
- [ ] Record repository SHA, extension ID/handle, API version, test Shopify shop/plan, checkout editor activation evidence, redacted checkout/session test evidence, commands and outcomes. Distinguish mocks from real checkout tests.

**Stop conditions:** If the supported Plus checkout target, authenticated checkout identity or S002's server association cannot be verified, do not accept consent for that checkout. Do not fall back to a hidden field, browser-supplied identity, Shopify Messaging, theme injection, a guessed database grant or a customer-visible error flow. Return the precise limitation for architect review. **No changes to S001/S002/S005, Background workers, PostgreSQL schema, WooCommerce or `moda-interact-api` are authorised by S004.**
