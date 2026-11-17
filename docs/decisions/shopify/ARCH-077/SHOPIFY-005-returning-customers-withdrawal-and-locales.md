---
id: ARCH-077-SHOPIFY-005
architecture_id: ARCH-077
title: Returning-customer consent display, merchant activation and locales
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-002, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Returning-customer consent display, merchant activation and locales

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending architectural review.** Follow the accepted S002 recovery-only persistence decision and the S003/S004 silent-failure and extension activation contracts. S001 and downstream Background task descriptions containing older Redis-resident customer preference/immediate-withdrawal assumptions require separate architect reconciliation. Do not modify those documents in this task.

## Objective

Complete the **Shopify application** merchant experience and verify returning-customer presentation for Moda's independent WhatsApp checkout-recovery consent. Use S002/S003/S004, not a second consent backend. The merchant enables Moda's cart App Block or Plus checkout extension; the customer sees the same approved checkbox wording as WooCommerce. **Only Background, when an eligible checkout becomes recoverable, materialises a customer's selected GRANT or REVOKE to PostgreSQL.** All other checkouts retain no new SQL consent decision.

## Touchpoints and ownership

- **S005 implementation:** `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx`, its existing recovery-settings integration, and existing `app/i18n/locales/*.json` Shopify application catalogues. Add focused tests under `tests/unit/shopify-consent/` and existing recovery-settings test locations following repository conventions.
- **S003 provides:** cart Theme App Block identifier/activation deep-link builder and trusted activation status reader; consume those interfaces rather than recreate them. The merchant's published theme and cart-template placement are distinct from installed extension availability.
- **S004 provides:** Shopify Plus checkout extension identifier, supported target and verified checkout editor activation guidance. Do **not** reuse the theme App Block deep link for checkout configuration.
- **S002 provides:** authenticated returning-customer SQL consent status and temporary cart/checkout Redis choice reads/writes. Do not add new API routes, Redis key types or customer-preference caches in S005.
- **Reference only:** `shopify.app.moda-interact.toml`, Redis/BullMQ worker keys, Background recovery admission and current `commerce.Customer`/`commerce.CustomerPhone` schema.
- No writes to `moda-interact-api`, `moda-interact-woocommerce`, database schema/migrations or `docs/decisions/**/_index.md`.

## 1. Returning customer: display, never materialise on click

- [ ] S003 (cart) and S004 (Plus checkout) receive the **current verified** consent state only through S002's authenticated Shopify backend. For a logged-in returning buyer, the verified **shop + Shopify customer ID** identifies which existing PostgreSQL `Customer`/active `CustomerPhone` consent records to read. A new cart token does not identify the returning customer.
- [ ] A verified, unambiguous current PostgreSQL `GRANTED` decision may initialise the checkbox as checked, subject to the existing STOP/no-contact checks in the approved S002 read contract. `REVOKED`, `UNKNOWN`, absent or ambiguous permission must not be labelled granted. Guests with new carts do not inherit prior consent by phone, email, basket similarity or timestamp.
- [ ] For the **current verified cart/checkout**, show its latest accepted explicit S002 Redis choice ahead of the older SQL display state, including on reload. A verified Plus checkout choice takes priority over an earlier cart choice for the same correlated checkout, as specified in S004. Rendering, status reads and auto-population **never** emit consent writes.
- [ ] A customer checking or unchecking the control causes only S002's temporary `GRANT` or `REVOKE` write against the **current** cart/checkout. **Neither a returning-customer withdrawal nor regrant writes PostgreSQL immediately.** Do not add a background consent job or a second state machine.
- [ ] At recoverability, Background reads the applicable temporary choice and applies it to existing customer consent under the separately accepted Background policy. If the checkout completes or otherwise becomes ineligible, the temporary selection is cleaned up by Background's lifecycle and **does not update SQL**. A new cart then reads the still-current SQL decision again. This is the explicitly approved ARCH-077 lifecycle; S005 must not add an immediate-withdrawal exception.
- [ ] Keep merchant/customer identity and disclosure evidence out of browser-visible status responses except the minimum non-sensitive verified checkbox state. A status read must not alter STOP, create a recovery or reserve billing credits.

## 2. Merchant configuration, placement and truthful status

- [ ] Replace the existing Shopify-native WhatsApp marketing setup instructions in `WhatsAppCustomerConsent.tsx` with **Moda-owned consent extension setup**. Do not instruct merchants to install Shopify Messaging, modify Shopify's native WhatsApp consent, or configure a separate Shopify WhatsApp business account.
- [ ] Provide a clear **Enable WhatsApp consent checkbox** path for the S003 cart App Block. Open Shopify's cart template in the theme editor using S003's validated shop-specific deep link; the merchant previews, positions and explicitly **saves** the block. Installation or opening a preview is not proof that the block is enabled.
- [ ] For an already verified cart placement, provide a **Manage in theme editor** link without intentionally proposing a duplicate App Block. Handle unsupported themes and missing cart sections through truthful merchant guidance; **do not** inject scripts or change the merchant's theme code as a fallback.
- [ ] For Shopify Plus, provide separate guidance for enabling S004's Checkout UI Extension at its supported checkout contact-information target. State accurately when the plan or target is unsupported; do not offer a cart theme-editor link as a substitute.
- [ ] Consume the S003/S004 documented activation-status readers where available. Distinguish **extension installed/available**, **merchant activated**, **verified in intended cart/checkout placement**, **unsupported**, and **status unavailable**. If the available platform API cannot prove actual placement on the published configuration, show **placement unverified**, not **enabled**. Do not request speculative Shopify scopes or claim that a block in an unrelated template covers the cart.
- [ ] Keep activation controls in Moda's merchant recovery settings. Do not introduce a new merchant consent opt-in/out policy switch or duplicate feature configuration unless required by the accepted extension contract.

## 3. Same customer-facing text; Shopify-owned translations

- [ ] English checkbox disclosure must be exactly: `Send me WhatsApp shopping updates, reminders and offers.` Do not add explanatory marketing copy, change punctuation or present a separate meaning for Plus.
- [ ] Use the existing **20 Shopify application locales**, plus the Shopify theme/checkout extension locale facilities defined by S003/S004. Translate merchant setup/status guidance and preserve the approved customer disclosure meaning. Do not import, refactor or edit WooCommerce translation files; only the English wording is shared.
- [ ] Pass the **actual customer-visible** disclosure text, Shopify-specific immutable disclosure version and storefront/checkout display locale to S002 with the deliberate action. Do not substitute the merchant administrator's interface locale for the shopper's locale. S005 must not invent a new evidence store or extend the schema.
- [ ] Preserve keyboard/screen-reader labelling; no locale-dependent implicit selection or action on render.

## 4. Silent shopper failure; operational diagnostics

- [ ] Apply the same S003/S004 failure contract to both placements: if the Shopify-owned Moda consent endpoint cannot be reached, times out, returns a non-success response, rejects authentication, or a Redis/SQL read fails, **do not show shopper-facing errors, warning banners, retry prompts, modal dialogs, blocking spinners or technical diagnostics**. Never interfere with cart navigation, address entry, accelerated checkout or payment.
- [ ] When verified status cannot be read, hide **only the Moda checkbox**; do not guess a grant/withdrawal. When a deliberate write fails, quietly restore the last acknowledged state or hide the Moda control; never present an unacknowledged change as saved. A failed write is not automatically retried as a new customer action.
- [ ] Merchant settings may show a neutral **Status unavailable** or **Placement unverified** state rather than a false green/enabled claim. Do not display raw provider errors or sensitive identities in merchant or customer UI.
- [ ] Keep bounded requests. The **server** logs the original Shopify/Redis/provider/SDK error message and relevant safe response details for debugging, with credentials, cart/checkout tokens, contact details, customer identifiers and proofs redacted. Do not swallow server exceptions without diagnostics; do not expose them to shoppers.

## 5. Tests, evidence, acceptance and stop

**Required tests:**

- [ ] Verified returning customer + new Cart B: read PostgreSQL via S002, show checked only when current consent is verified `GRANTED`; otherwise unchecked. New Cart B must not read a prior cart's temporary Redis selection. Status read and render create **zero** consent writes.
- [ ] Customer unchecks previously checked Cart B: S002 records a temporary `REVOKE`, UI reflects it after acknowledgement and PostgreSQL remains unchanged. A cart completing without becoming recoverable cleans up temporary Redis without SQL change; on later Cart C the display again reflects existing SQL state. The same test applies to a fresh `GRANT`.
- [ ] An abandoned eligible checkout delegates materialisation to Background; S005 itself performs zero SQL grant/revocation writes. Same-cart reload and Plus cart-to-checkout precedence use S002/S004 only.
- [ ] Guest with new cart, customer switching, ambiguous active phone, cross-merchant identity, STOP/no-contact and missing provider proof do not expose or generate grants.
- [ ] Merchant installs extension without enabling it: display **not enabled**. Theme editor deep link opens correct published cart template; actual merchant save/placement is verified separately. Unsupported/non-cart placements do not display an inaccurate **enabled** claim. Plus checkout activation uses its own configuration path.
- [ ] Test all 20 Shopify locale catalogues for required keys and exact English disclosure; verify displayed locale/version/text delivered to S002 for explicit actions and never on rendering alone.
- [ ] S003/S004 failure cases (network down, timeout, authentication failure, Redis loss, PostgreSQL status failure) show no customer-facing errors and do not block checkout; failed writes do not appear saved. Check safe original server diagnostics.
- [ ] Existing Background BullMQ jobs, pending-recovery indexes, locks, tombstones and TTLs are unchanged; no new permanent Redis customer-preference keys or worker jobs. WooCommerce and `moda-interact-api` regression scope is unchanged.

**Evidence:** List changed files, repository commit SHA, Shopify plan and theme/checkout configuration used, extension identifiers, activation checks, test commands/results, mock-versus-real-test distinction, and any unsupported placement. Report blockers with actual underlying diagnostic evidence, redacted appropriately.

**Stop conditions:** If S002's returning-customer SQL identity/status contract is unavailable or ambiguous, S003/S004 activation verification is unsupported, a Shopify theme/checkout target cannot be verified, or silent shopper failure cannot be guaranteed, report the exact blocker. Never invent an identity fallback, native WhatsApp consent dependency, customer-preference Redis mirror, direct SQL update on checkbox action, new schema or WooCommerce-side change.
