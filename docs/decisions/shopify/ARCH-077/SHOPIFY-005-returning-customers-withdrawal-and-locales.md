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
status: in_progress
priority: 55
executor: copilot
claimed_at: 2026-11-18T17:00:52Z
attempt: 2
depends_on: [ARCH-077-SHOPIFY-002, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004]
enables: [ARCH-077-SHOPIFY-006, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Returning-customer consent display, merchant activation and locales

**Architect revision — 18 November 2026; interrupted Attempt 1; READY for Attempt 2.** The developer stopped the agent to replace instruction-heavy merchant setup with an automated activation flow. This revision supersedes the older manual-onboarding requirements; preserve the unfinished implementation. S002, S003, and S004 remain accepted. Follow [the signed attribute contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This task owns merchant-facing plan detection, guided activation, published-placement verification, returning-customer display and locale integration, **not** receipt issuance, recovery materialisation or a second consent store.

## Architect-approved outcome: guided activation, minimal merchant work

The normal merchant experience is: **(1)** Moda reads the merchant's Shopify plan and existing published-extension evidence; **(2)** Moda prepares the appropriate extension and its own availability setting; **(3)** merchant chooses **Activate WhatsApp Consent**, is taken directly to the supported Shopify editor, and clicks Shopify **Save**; **(4)** Moda refreshes and reports verified published placement. A merchant should not have to manually enter extension IDs, locate Shopify settings, configure keys, or configure the standard App Proxy path. Shopify retains the final editor Save/Publish action. Never mark `active` on click, redirect, deployment or configuration mutation alone.

### Preserve and reconcile the stopped Attempt 1 implementation

The uploaded paused snapshot contains unfinished runtime edits and locale files. Preserve them, including changes under:

- `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx`, `RecoverySettingsView.tsx`, `route.tsx`;
- `app/services/shopify-consent/consent-activation.server.ts`, `theme-activation-url.server.ts`, `theme-activation-status.client.ts`;
- `app/i18n/locales/*.json` (20 admin locales) and `tests/unit/services/shopify-consent-activation.test.ts`, `tests/unit/services/shopify-consent-theme-activation.test.ts`, `tests/unit/whatsapp-customer-consent.test.tsx`.

In the uploaded snapshot `consent-activation.server.ts` already queries `shop.plan.shopifyPlus`, loads the published cart JSON and constructs a cart-editor URL; the settings panel renders both plan-specific status cards. **Keep useful implementation, simplify the UI and complete the missing actions.** The snapshot does **not** establish a clean Git worktree or successful tests; before restarting, the developer/agent must preserve all staged, unstaged and untracked changes in the actual implementation worktree and restore/reconcile them without reset/clean. Do not edit `docs/decisions/**/_index.md`.

### S005-A — Plan-exclusive selection, no new state

- Continue using `resolveConsentPlacement()` in `app/services/shopify-consent/consent-activation.server.ts` from the authenticated Shopify Admin GraphQL `shop { plan { shopifyPlus } }`. `true => plus_checkout`, `false => non_plus_cart`, missing/error => `unknown`. Do not infer Plus from Moda's billing plan or the existence of an extension.
- Present exactly **one** primary action. Non-Plus => **Activate cart consent**; Plus => **Activate checkout consent**. Unknown => **Status unavailable**, no activation action. Display the currently verified state, not a switch that pretends to activate an extension by updating a Moda setting.
- Changing Shopify plan must not silently make both customer-facing placements authoritative. Plan-derived UI is exclusive. Existing published placement conflicts are shown clearly for merchant correction; the app must not assert it removed a merchant-owned published layout. The S003/S004 runtime's plan/capability checks remain in force.
- Use the existing `ConsentActivation` DTO and Recovery Settings loader; add only the fields necessary for editor URL, availability-gate state and published verification evidence. No new tables, Redis records, queue, webhook or shared protocol.

### S005-B — Automatically reconcile the **existing** cart App Block visibility gate

`extensions/moda-whatsapp-consent/blocks/cart-consent.liquid` already declares `available_if: "{{ app.metafields.moda_interact.cart_consent_enabled }}"` (Shopify app-data boolean). The stopped implementation defines `CART_CONSENT_APP_DATA_METAFIELD` but has **no actual writer**. Without this gate, a fresh merchant may be sent to an editor where the App Block is unavailable.

- On the **authenticated merchant activation action**, query `currentAppInstallation { id metafield(namespace:"moda_interact",key:"cart_consent_enabled") { value type } }`, then perform an idempotent Admin GraphQL `metafieldsSet` only when needed, ownerId = returned `AppInstallation.id`, namespace `moda_interact`, key `cart_consent_enabled`, type `boolean`, value `"true"` for non-Plus and `"false"` for Plus. Verify GraphQL `errors`, `userErrors` and returned value; do not silently report success if the write failed. Use the merchant's existing authenticated Admin client and existing server diagnostic logger with original provider error details. No second configuration service or SQL field.
- Never write this app-data gate merely to render a GET/loader or read shopper consent. For Plus, perform the false gate write as part of activation/plan reconciliation before continuing, so an existing non-Plus cart block becomes ineligible; warn if the old published block requires merchant cleanup. For non-Plus, only open the Shopify editor once `true` has been verified. If unavailable, show **Setup unavailable** and do not claim installation.
- The gate controls **availability**, not placement and not customer consent. It does not automatically add an App Block to a theme, mutate Shopify checkout attributes or write `CustomerPhone`.

### S005-C — Non-Plus one-action theme editor flow

- Reuse `buildCartConsentThemeActivationUrl` from `app/services/shopify-consent/theme-activation-url.server.ts` using trusted `shop.domain` and `apiKey`; the supported URL is `https://{shop}.myshopify.com/admin/themes/current/editor?template=cart&addAppBlockId={apiKey}/cart-consent&target=newAppsSection` (subject to S003 `enabled_on` and theme support). Do not invent another target, edit theme files, or request restricted `write_themes` access.
- If already published/active, show **Manage** or **Open editor**, not **Add again** (duplicate blocks); use only documented editor URL forms, not an undocumented deep link pretending to focus the existing block. If the cart template lacks compatible app-block support, show unsupported, never active.
- On merchant's return/refresh after Shopify Save, use the existing published-theme GraphQL read and `deriveCartTemplateEvidence` (or Shopify App Bridge `shopify.app.extensions()`) to confirm the **Moda app's** exact `cart-consent` block in the **published** cart template, enabled and not under a disabled section. Do not classify a different app's `cart-consent` block as ours, or treat a draft theme as published. An enabled template reference is evidence of **placement**, not proof of the configured App Proxy working.
- Do **not** force merchants to configure `/apps/moda-consent` by default; S003 already supplies it. If the merchant changed Shopify's App Proxy prefix/subpath, Shopify exposes no per-installation getter. Provide an **exception-only** advanced instruction to align the S003 `app_proxy_root` block setting with their actual full path and retest; keep `unverified` when endpoint operation cannot be verified. Do not create a new guessed proxy introspection API or duplicate the S003 path validator.

### S005-D — Shopify Plus editor and **actual** published activation status

- In `WhatsAppCustomerConsent.tsx`, provide **Open Shopify checkout editor** for verified Plus. Use supported Shopify Admin checkout navigation (`https://{shop}.myshopify.com/admin/settings/checkout` as safe fallback), with concise instruction to choose Customize, Add app block `moda-whatsapp-checkout-consent` on the contact step and **Save**. Do not invent a deep link that silently installs or targets this specific Checkout UI Extension; there is no general supported API that publishes it on the merchant's behalf.
- The stopped `consent-activation.server.ts` always sets `extensionVerified:null`, leaving Plus perpetually `unverified`. **Fix this** using the already-embedded Shopify App Bridge **read-only** `shopify.app.extensions()` API client-side: match `type === "ui_extension"`, exact handle `moda-whatsapp-checkout-consent` and a published activation whose `target === "purchase.checkout.contact.render-after"`. Match all three, not any arbitrary UI extension. Re-check after the merchant comes back to Moda or clicks **Refresh status**. Successfully queried and absent => `inactive`; matching target => `active`; API unavailable/error/unsupported => `unverified`/`unavailable` with original server-side errors wherever applicable. Do not create a new Admin GraphQL checkout-profile read or persist a fake `active` bit.
- Recognise that `app.extensions()` provides **published placement evidence**, not a successful end-customer session JWT or attribute mutation. S004's accepted issuer/readback semantics remain unchanged. Preview/draft placements must not be shown as published.

### S005-E — Returning customer, locale, copy and deployment

- Keep the exact English shopper wording **`Send me WhatsApp shopping updates, reminders and offers.`**; S003/S004 remain the sole checkbox owners and use **shopper** locale. The 20 `app/i18n/locales/*.json` additions belong to the **merchant** setup and status interface; use existing i18n helpers, no new translation subsystem.
- Reuse S002 returning-customer signed shop/customer SQL status read. Verified returning `GRANTED` can display checked without issuing a new signed receipt or writing SQL. Valid signed choice for the **current** cart/checkout overrides SQL for **that display only**; `REVOKE` is not materialised until a separately recoverable checkout. Never reuse a guest's phone/email as proof of SQL consent. STOP/no-contact still suppress outbound independently.
- Remove stale Shopify-native WhatsApp marketing opt-in/Shopify Forms guidance. The existing `tests/unit/arch045-whatsapp-consent-guidance.test.tsx` still expects the old one-argument component and native-guide links: **update its assertions** to the new Moda-owned activation contract rather than deleting/skipping the suite.
- S004's `MODA_CHECKOUT_RECEIPT_ORIGIN` is a **build/deployment** setting, not a merchant input. Do not add a merchant-facing secret field or backend proxy service. In the deployment/certification acceptance report, verify the production Checkout UI Extension bundle uses `https://app.modainteract.com` (or the actual approved production origin) and **not** the `https://app-test.modainteract.com` fallback. Stop production release if this cannot be verified; do not silently change a tested dev default in unrelated code.
- Invalid app sessions, unavailable S002, unverifiable status, unsupported checkout attribute writes or Shopify API failures must hide only Moda shopper controls as already implemented; do not block the cart or payment. Merchant-facing status is unavailable/unverified, with original Shopify/SDK error and stage logged using the existing structured logger (no credentials/keys).

## Acceptance tests and evidence

1. Non-Plus/Plus/unknown plan fixtures select exactly one action; verified plan comes from Shopify, not merchant-supplied data.
2. `metafieldsSet` gate tests for missing/false/true app-data boolean, idempotence, denied GraphQL mutation, first-time non-Plus activation and Plus upgrade disablement. No write during ordinary GET/status reads. Verify the gate is not represented as published placement or SQL consent.
3. Cart editor deep link tests for real shop/API-key, correct template/handle/target, unsupported template and already-active manage path; published `cart.json` (including disabled ancestor and foreign-app same-name block) versus draft/unverified evidence. No unsupported theme-file modification.
4. Client App Bridge `app.extensions()` tests: published correct S004 handle/target active; absent inactive; wrong target/handle, API error and unavailable API unverified. Include returning from Shopify Editor / Refresh status. Plus never renders the S003 activation path.
5. Happy paths: merchant click -> gate verified -> Shopify editor -> manual Save -> published confirmation. Status changes only after positive published evidence. Plan transition does not claim automatic removal of merchant-authored placements.
6. 20 merchant locales, no Shopify-native consent guidance, exact shopper copy, S002 returning-customer status/read-only display, no receipt on render, no auto-GRANT, no cross-guest inheritance, STOP and revocation boundaries unchanged. Include a non-default custom App Proxy mismatch exceptional path.
7. Run targeted Vitest suites, **the pre-existing `arch045-whatsapp-consent-guidance.test.tsx`**, targeted ESLint, Shopify build, general `npm run build`, `npm run typecheck` with precise baseline-vs-new diagnosis and `git diff --check`. Report any pre-existing failures; do not claim they passed.

## Stop conditions and delivery

- Stop on an unsupported documented Shopify SDK contract, missing permission/grant preventing supported activation, or inability to distinguish published checkout extension from an unverified one. Report exact original errors and smallest corrective options; do not invent an Admin API to force merchant Save/Publish.
- Do not add SQL migrations, Redis, new queues, another receipt mechanism, new `docs/decisions/**/_index.md` edits, direct theme-file mutation or changes to other repositories. Do not change existing S002, S003 or S004 receipt semantics.
- The stopped Attempt 1 is **interrupted, not accepted or rejected as completed work**. Preserve its partial implementation and write the normal Attempt 2 Completion Report after implementation. Return `ready -> in_progress -> review`; architect will decide acceptance from actual source, tests and live evidence.
