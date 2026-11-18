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
status: review
priority: 50
executor: copilot
claimed_at: 2026-11-18T02:01:40Z
attempt: 3
depends_on: [ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Render and activate Shopify cart-page WhatsApp consent App Block

**Architect Changes Requested (18 November 2026); returning for Attempt 2.** The S002 stateless issuer is accepted. This task must correct verified current-cart display before acceptance. Follow the [ARCH-077 checkout-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This task **does not** request Redis marker preparation, Redis GRANT/REVOKE writes, or checkout correlation. Non-Plus merchants get this cart checkbox, Plus merchants get **only S004** checkout checkbox.

## Owning source touchpoints

- Create `extensions/moda-whatsapp-consent/shopify.extension.toml` (theme extension), `blocks/cart-consent.liquid` (`target: section`, `enabled_on.templates: [cart]`) and only needed assets/locales under `extensions/moda-whatsapp-consent/`. Use supported Shopify CLI scaffold, no injected theme scripts or extra phone fields.
- Create/maintain Shopify cart activation link/status helpers under `app/services/shopify-consent/theme-activation-url.server.ts` and `theme-activation-status.client.ts`; S005 consumes their verified merchant activation state.
- Use the authenticated App Proxy `GET cart/status` + `POST cart/receipt` owned by S002. **Architect-authorised narrow S003 exception:** extend the existing Shopify-owned S002 App Proxy route with read-only `POST cart/verify`, exactly as frozen below and in the ARCH-077 v1 contract; do not change issuer semantics. No new app, queue or storage. Never call obsolete `cart/prepare` or `cart/choice` endpoints or write any Redis consent key.

## Deterministic shopper flow

1. Check that the merchant's selected plan/placement is non-Plus and published cart App Block is active. Do not display both S003/S004 on any one merchant. Load `/cart.js` using Shopify locale-aware routes; require a real current cart and normalize the private `?` suffix for binding as S002 defines.
2. On first render, ask S002 for verified returning-customer SQL status; inspect **only the current cart** `attributes.moda_wa_consent_v1`, and if a nonempty attribute exists, require authenticated server verification before showing the checkbox. Verification is **not optional**: after an accepted GRANT, display checked on reload; after an accepted REVOKE, display unchecked. Do not substitute an unchecked default for an unverified existing receipt. When an existing receipt cannot be verified (including tampering, stale/cart/customer mismatch or backend failure), hide the Moda control silently and leave checkout usable. When no current-cart attribute exists, use the verified returning-customer SQL status. Do not assume browser attribute text alone is a verified grant; unchecked default/render is neutral. Display exact English copy `Send me WhatsApp shopping updates, reminders and offers.` and Shopify locale equivalent.
3. On **explicit check/uncheck only**, call S002 `POST cart/receipt` with `GRANT`/`REVOKE`, verified current cart locator and shopper locale; S002 issues one signed receipt. Write **only** `attributes:{moda_wa_consent_v1:receipt}` to locale-aware `/cart/update.js`, and confirm via Shopify response or a single re-fetch of `/cart.js` that the exact receipt is current. Do not overwrite unrelated attributes or change cart contents. Receipt on an unsubmitted checkout is merely temporary Shopify attribute state; no SQL or proactive suppression occurs.
4. If request, issuer, cart update or readback fails, silently restore last confirmed state or hide *only* Moda control, never display an unacknowledged choice as saved and never interrupt checkout/payment. No repeated automatic action, global retries or leaking raw receipt/cart token into logs.
5. A visitor changing carts must read the new cart and never copy a valid prior checkout's receipt to it. Express/accelerated routes bypassing the cart do not create consent. A non-Plus guest whose `cart_token` differs from the signed cart receipt at Background evaluation fails closed; do not add marker fallback, user matching or product/time heuristics.

## Frozen read-only verification interface (S003 owns this integration)

- Shopify app server adds one action path **`POST /shopify/consent/cart/verify`**, exposed via the *existing* signed App Proxy URL **`/apps/moda-consent/cart/verify`**. Follow S002's installed `authenticate.public.appProxy` signature/shop/signed-customer verification, `write_app_proxy` scope, timestamp freshness, configured safe proxy-prefix handling, origin validation and bounded JSON parser. Do **not** add a second authentication scheme or persist the receipt.
- Request exactly `{ "cartToken": string, "receipt": string }`; do not accept client-supplied shop ID, customer ID, decision or provenance. Obtain shop and optional Shopify customer from authenticated proxy context. Invoke existing `verifyConsentReceipt(receipt, {shopId,kind:"c",token:cartToken,customerId:shopifyCustomerId})`, preserving original Shared keyring/AAD and existing accepted same-cart replay limitation. No new cryptography or Redis.
- Successful response exactly `{ "source": "verified_receipt", "decision": "GRANT" | "REVOKE" }` (map signed `G`/`R`); `Cache-Control: no-store`. Rejected receipts return a bounded non-2xx response with no plaintext, raw receipt, decrypted claims or token in logs. Server preserves redacted original error diagnostics using existing logging.
- The browser reads `/cart.js` first and sends only the receipt that is currently present on **that cart**. On valid verification, set checked for GRANT and unchecked for REVOKE; do **not** issue or overwrite a receipt on initial render. A missing attribute falls back to SQL status. If a present attribute fails verification, **do not** fall back to a potentially contradictory old SQL GRANTED state; hide only this App Block and allow ordinary shopping/checkout.
- If the theme editor rerenders/replaces the cart App Block after initial `DOMContentLoaded`, initialise the new element on Shopify's section-load event without duplicate handlers on an existing root; no repeated grant from render.

## Tests and stop

- Theme App Block schema/cart-template limitation, published-theme save, unavailable/incompatible theme and no false activation claims.
- New cart unchecked with **zero receipt issued**; returning verified SQL GRANTED checked but no new receipt until deliberate change; real browser choice -> signed attribute -> `CHECKOUTS_CREATE/UPDATE` and `AbandonedCheckout.customAttributes`, preserving one exact receipt.
- Verified existing GRANT renders checked after reload and verified existing REVOKE renders unchecked after reload, **without creating any receipt**; modified/cross-cart/cross-customer receipt, verification endpoint error or lost network hides the control without blocking checkout. Test signed App Proxy checks on the new read-only endpoint, including guest and authenticated customer, custom storefront origin and timestamp freshness. Test dynamic theme editor section-load reinitialisation without duplicate writes.
- GRANT then REVOKE same cart replaces key; reading last valid receipt returns REVOKE; copied signed receipt to another cart denied by binding at B002. Missing/broken issuer/readback, cart replacement, two tabs, custom domain, locale and express checkout fail silently, no checkout block.
- Do not modify S002 receipt issuance logic beyond the narrowly authorised `cart/verify` read-only action, or change Background, Shared, Woo/API, existing BullMQ or `_index.md` from S003. Stop if the receipt cannot be written/read or the approved app-proxy path cannot be deployed; report exact blocker.

## Completion Report

### Attempt 1 report (preserved)

- Implemented the cart-only `target: section` Theme App Block, 20 storefront locales, explicit-only receipt issuance, locale-aware Ajax cart requests, exact receipt/cart-token confirmation, and fail-closed theme activation helpers.
- The block is gated by the boolean app-data metafield `moda_interact.cart_consent_enabled`; S005 must set it only for non-Plus plan placement and keep it false for Plus. The block remains unavailable until that plan gate is configured.
- The current S002 route does not expose `verifyConsentReceipt`. A nonempty receipt already on the cart is therefore treated as unverified and displayed neutrally (unchecked); raw cart attribute text is never trusted as a grant.
- Validation passed: 12 focused Vitest cases, targeted ESLint, all 20 locale JSON labels, `shopify app build --config moda-interact` including Theme Check, and `npm run build`.
- `npm run typecheck` still reports five implicit-`any` errors in the unchanged `app/routes/webhooks/root/route.jsx`. No live dev-store operation was run; published-theme activation and Shopify cart-to-checkout receipt propagation remain unverified and require a separately confirmed remote validation.

### Attempt 2 report

**Status: Ready for Review.** The Attempt 1 implementation commit and report are retained in history.

#### Architect Review correction disposition

1. **Verified current-cart display — implemented.** The block now reads the receipt only from the current locale-aware `/cart.js` response, POSTs that receipt and cart token to the verification endpoint, maps verified `G`/`R` to checked/unchecked, and issues no receipt on render. A present receipt that cannot be verified hides the block without falling back to SQL status. Tests cover verified GRANT and REVOKE reloads, tampered/failed verification, no render-time issuance, and explicit same-cart GRANT then REVOKE replacement.
2. **Authenticated read-only App Proxy verification — implemented.** Added the narrowly scoped `POST /shopify/consent/cart/verify` action to the existing route. It accepts exactly `cartToken` and `receipt`, uses the existing authenticated shop/customer context and `verifyConsentReceipt`, returns only the frozen response with `Cache-Control: no-store`, and preserves redacted service error logging. Route tests cover guest and customer contexts, custom HTTPS Origin, timestamp/prefix checks, rejected extra identities, and bounded failure responses. Shopify SDK signature authentication is mocked in unit tests; no live signed-proxy call is claimed.
3. **Theme-editor section lifecycle — implemented.** Added `shopify:section:load` initialization with the existing per-root WeakSet guard. A focused test confirms a new section initializes and repeated section-load events do not duplicate initialization.

#### Changed implementation files

- `app/routes/shopify/consent/route.ts`
- `app/services/shopify-consent/consent-receipt.server.ts`
- `extensions/moda-whatsapp-consent/assets/cart-consent.js`
- `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid`
- `tests/unit/extensions/moda-whatsapp-consent.test.js`
- `tests/unit/routes/shopify-consent-route.test.ts`

Receipt issuance semantics, Shared AEAD implementation, Redis/queue behavior, other repositories, and `_index.md` files were not changed.

#### Validation

- `npm test -- tests/unit/extensions/moda-whatsapp-consent.test.js tests/unit/routes/shopify-consent-route.test.ts tests/unit/services/shopify-consent-receipt.service.test.ts` — passed, 36 tests across 3 files.
- Targeted ESLint on all changed JavaScript/TypeScript source and test files — passed.
- `shopify app build --config moda-interact` — passed, including Theme Check for the Theme App Extension.
- `npm run build` — passed.
- `git diff --check` — passed.
- `npm run typecheck` — still reports five TS7006 implicit-`any` errors in unchanged `app/routes/webhooks/root/route.jsx` (parameters `topic`, `payload`, `token` twice, and `attributes`); these match the Attempt 1 finding and are not in files changed by this attempt.

#### Git and execution evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-SHOPIFY-003`, branch `task/ARCH-077-SHOPIFY-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-SHOPIFY-003`, branch `task/ARCH-077-SHOPIFY-003`.
- Implementation commit pushed to `origin/task/ARCH-077-SHOPIFY-003`: `370f54828b856e7f5055579e154c55b7331b7dbf`.
- Launcher evidence: both worktrees reused at their canonical paths; remote task-branch fast-forward was not needed; `origin/main` was already incorporated; no shared checkout mutation or other-task worktree reuse; recursive submodule sync/update passed; database submodule remained at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`.

#### Remaining validation gates

No live dev-store, published-theme activation, Shopify SDK signed App Proxy request, or cart-to-checkout `AbandonedCheckout.customAttributes` propagation was run. Those remain S005 / terminal SYSTEM-TEST-001 integration gates; the cart block still depends on S005 configuring `moda_interact.cart_consent_enabled` exclusively for non-Plus placement. No live Shopify behavior is claimed by mocked tests.

### Attempt 3 report

**Status: Ready for Review.** Attempt 3 implements the remaining storefront App Proxy configuration correction from the latest Architect Review, preserves the earlier verified-receipt and lifecycle fixes, and prevents saving a newly issued receipt after a cart replacement.

#### Rework correction disposition

1. **Verified current-cart display — implemented.** The block reads the receipt from the current locale-aware `/cart.js` response, verifies it against that cart, maps verified GRANT/REVOKE to checked/unchecked, and does not issue a receipt on render. Present-but-unverifiable receipts still hide only the Moda control without SQL fallback. Covered by `tests/unit/extensions/moda-whatsapp-consent.test.js`.
2. **Authenticated read-only App Proxy verification — implemented.** `app/routes/shopify/consent/route.ts` exposes the exact two-field `cart/verify` request through Shopify's authenticated App Proxy context, calls the existing receipt verifier, returns the bounded frozen response with `Cache-Control: no-store`, and preserves redacted error diagnostics. Route cases remain covered by `tests/unit/routes/shopify-consent-route.test.ts`.
3. **Theme-editor section lifecycle — implemented.** New roots are initialized on `shopify:section:load` without duplicate initialization or duplicate handlers. Covered by `tests/unit/extensions/moda-whatsapp-consent.test.js`.
4. **Merchant-configurable App Proxy root — implemented.** The block exposes exactly one text setting (`app_proxy_root`, label `Moda app proxy path`, default `/apps/moda-consent`) and derives the three escaped endpoint attributes from it. Before any request, the browser validates one supported prefix and one 1–30 character subpath, rejects reserved names and malformed paths, then constructs same-origin endpoint URLs. Empty configuration uses the default. Tests cover the default plus `/tools/custom-consent`, `/a/custom-consent`, and `/community/custom-consent`, and prove invalid paths hide the block without a request.
5. **Cart changes while receipt issuance is pending — implemented.** Before writing, `cart-consent.js` rereads the locale-aware cart and compares its normalized token with the token used for issuance; a changed cart aborts the write and restores the last confirmed checkbox state. A focused regression test proves no update request is sent to the replacement cart.

#### Changed implementation files in Attempt 3

- `extensions/moda-whatsapp-consent/assets/cart-consent.js`
- `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid`
- `tests/unit/extensions/moda-whatsapp-consent.test.js`

No receipt-issuance semantics, App Proxy server routing/authentication, Redis/queue behavior, Shared cryptography, other repositories, or `_index.md` files were changed.

#### Validation

- `npm test -- tests/unit/extensions/moda-whatsapp-consent.test.js tests/unit/routes/shopify-consent-route.test.ts tests/unit/services/shopify-consent-receipt.service.test.ts` — passed, 57 tests across 3 files.
- Targeted ESLint on the changed JavaScript source and test — passed.
- `shopify app build --config moda-interact` — passed, including Theme Check and extension bundling; `cart-consent.js` is 9,855 bytes, below the configured 10,000-byte limit.
- Shopify Liquid app-block validation (`--context app`) — passed.
- `git diff --check` — passed.
- `npm run build` — passed.
- `npm run typecheck` — reports exactly five TS7006 implicit-`any` errors in unchanged `app/routes/webhooks/root/route.jsx` (`topic`, `payload`, `token` twice, `attributes`); these match the already documented baseline, and no new typecheck error was observed.
- Existing shopper locale files were not changed; all 20 locale JSON files were validated.

#### Git and execution evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-SHOPIFY-003`, branch `task/ARCH-077-SHOPIFY-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-SHOPIFY-003`, branch `task/ARCH-077-SHOPIFY-003`.
- Implementation commits pushed to `origin/task/ARCH-077-SHOPIFY-003`: `fe1dbf9` (`fix(shopify): verify cart before saving consent receipt`) and `e774fa7` (`fix(shopify): support merchant app proxy paths`).
- Launcher evidence: both canonical worktrees were reused; task-branch fast-forwards were not needed; `origin/main` was already incorporated in both; shared workspace and implementation checkouts were not switched or mutated; no other task worktree was reused; recursive submodule sync/update passed; the database submodule remained at `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`.

#### Remaining validation gates and documentation note

- No live dev-store, published-theme activation, live signed App Proxy request, or cart-to-checkout `AbandonedCheckout.customAttributes` propagation was run. These remain S005 / SYSTEM-TEST-001 integration gates; no live Shopify behavior is claimed.
- No live dev-store, published-theme activation, live signed App Proxy request, or cart-to-checkout `AbandonedCheckout.customAttributes` propagation was run. These remain S005 / SYSTEM-TEST-001 integration gates; no live Shopify behavior is claimed.
- S005 activation guidance must tell merchants to keep the App Block's `Moda app proxy path` setting aligned with Shopify's configured App Proxy URL when they customize that URL.
- The task's linked `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md` path is absent from the workspace. The implementation followed the complete frozen interface embedded in this task; no implementation blocker remains from the unavailable duplicate reference.

## Architect Review — Attempt 1 (18 November 2026)

### Review Status

**Changes Requested.** Reclaimable task: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1` preserved. Agent claims Attempt 2 via the normal launcher. The existing implementation commits and Completion Report must remain in history.

### Review Notes / Verified deficiencies

1. **Blocking display correctness:** `extensions/moda-whatsapp-consent/assets/cart-consent.js` currently sets `initialChecked = false` for *every* nonempty pre-existing `moda_wa_consent_v1` value, without invoking the existing S002 `verifyConsentReceipt`. This displays a previously GRANTED selection as unchecked after reload, and treats a tampered receipt as an ordinary unchecked selection. The user's last confirmed explicit choice must be shown accurately, not falsely interpreted as a new default.
2. **Missing integration surface:** `app/routes/shopify/consent/route.ts` has `GET cart/status` and `POST cart/receipt`, but no authenticated receipt-read endpoint. The existing task text forbids changing S002's route. This review resolves that conflict by authorising **only** the read-only `POST cart/verify` action above under this same Shopify S003 task. Use the existing S002 verifier and authenticated proxy contract; no new key-management, SQL write, queue or marker logic.
3. **Theme editor lifecycle:** the JS initialiser runs at DOMContentLoaded and relies on a WeakSet for existing roots but does not register Shopify's section-load event, so dynamically replaced cart blocks cannot be assumed initialised. Add bounded section-load reinitialisation tests. No additional global theme script or framework.

### Reviewed Files

- `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid`, `assets/cart-consent.js`, `assets/cart-consent.css`, `shopify.extension.toml`, 20 extension locale JSONs
- `app/services/shopify-consent/theme-activation-url.server.ts`, `theme-activation-status.client.ts`, `app/routes/shopify/consent/route.ts`, `app/services/shopify-consent/consent-receipt.server.ts`
- `tests/unit/extensions/moda-whatsapp-consent.test.js`, `tests/unit/services/shopify-consent-theme-activation.test.ts`, current S003 Completion Report

### Positive Findings / Validation Reviewed

- Bounded cart-only App Block with `target: section`/cart-template scope, locale-aware Ajax calls, server-issued AEAD receipts on explicit actions, readback confirmation and silent failure; uses the existing merchant app-data metafield placement gate.
- Existing SQL status is read for a cart without a receipt. The browser does not try to decrypt Shared ciphertext or write click-time SQL/Redis state.
- Agent reports 12 focused tests, targeted ESLint, 20 valid locale labels, Shopify CLI/theme check and production build passing; **these were not independently executed from the ZIP**. Architect independently ran `node --check` on `cart-consent.js` and parsed all 20 locale JSONs successfully. `npm run typecheck` retains five reported pre-existing errors in unchanged `app/routes/webhooks/root/route.jsx`; distinguish these from any newly introduced errors.
- No live dev-store/published-theme signed-receipt transport was demonstrated. Keep this a **S005 / terminal SYSTEM-TEST-001 integration gate**, not a requirement to invent merchant metafield activation in S003 before S005 is implemented.

### Architecture Conformance

**Partial.** Attribute transport, explicit-only issuance, plan-specific placement, no Redis consent and Shared cryptography reuse conform. Current-cart verified display does **not** conform to the accepted S003 task and v1 receipt-read semantics.

### Required Resubmission / Stop

- Correct only the specified UI/display, read-only Shopify App Proxy verification integration, theme-editor reinit and their focused tests. Keep receipt issuance and Shared AEAD untouched; do not modify other repositories or `docs/decisions/**/_index.md`.
- Provide exact modified paths, current task worktree/branch SHA and implementation commit, `git diff --check`, focused App Proxy/cart reload tests, targeted lint, relevant Shopify build/Theme Check, `npm run build`, and `npm run typecheck` with baseline-vs-new error classification. Report real test results without calling mocked tests live Shopify proof.
- On success, agent sets SHOPIFY-003 back to `review`, completes its report and stops. Architect independently re-reviews before marking `complete` or promoting SHOPIFY-005. Retain downstream gates until then.


## Architect Review — Attempt 2 (18 November 2026)

### Review Status

**Changes Requested — one remaining storefront integration defect.** Return this SAME task to `ready`, clear `executor` and `claimed_at`, retain `attempt: 2`; the launcher alone claims Attempt 3. Preserve all previous implementation commits, tests, Completion Reports and Architect Review history. S005 remains `pending` because S004 is also incomplete. Do not mark S003 `complete` or merge yet.

### Reviewed implementation and positive findings

- Reviewed `moda-interact/app/routes/shopify/consent/route.ts`, `app/services/shopify-consent/consent-receipt.server.ts`, `extensions/moda-whatsapp-consent/assets/cart-consent.js`, `blocks/cart-consent.liquid`, the extension manifest, `tests/unit/extensions/moda-whatsapp-consent.test.js`, `tests/unit/routes/shopify-consent-route.test.ts`, and the preserved Attempt 2 report in the supplied task-worktree ZIP. Agent-reported implementation commit `370f54828b856e7f5055579e154c55b7331b7dbf` and parent-report commit `b988b9d8febb08c7b4e7e69f1d56f12210479202` are not independently verified against Git remotes.
- **Attempt 1 corrections satisfied in inspected source:** current-cart GRANT renders checked and REVOKE unchecked after authenticated `POST cart/verify`, without a render-time receipt write; invalid/unverifiable receipt hides only the Moda control without SQL-status fallback; Shopify `shopify:section:load` reinitialises replaced blocks and WeakSet prevents duplicate handlers. The read-only verification route reuses S002 authentication and Shared-AEAD receipt verification without new storage or cryptography. Keep these changes.
- Agent reports **36 focused tests**, targeted ESLint, Theme Check/Shopify build, production build and Git whitespace validation passed; these were not independently run. Five TypeScript implicit-any errors are reported in unchanged `app/routes/webhooks/root/route.jsx`; preserve baseline attribution and do not edit that unrelated route here. Live signed App Proxy and checkout-to-GraphQL propagation were **not** tested; these remain S005/terminal SYSTEM-TEST-001 gates, not grounds for inventing new S003 infrastructure.

### One verified defect — hard-coded storefront App Proxy root

`extensions/moda-whatsapp-consent/blocks/cart-consent.liquid` hard-codes `/apps/moda-consent` in `data-status-url`, `data-receipt-url` and `data-verify-url`. Shopify allows each merchant to change the proxy `prefix` and `subpath` after installation, while the approved S002 route already accepts signed safe custom prefixes. A merchant with e.g. `/tools/moda-consent` cannot use the current cart checkbox: all three frontend calls would target the obsolete path and hide the control. The fixed default is insufficient for the supported multi-merchant integration.

### Required correction — exact bounded implementation contract

1. **One App Block setting, not three URLs:** add precisely one `type: text` setting with `id: app_proxy_root`, merchant-visible label `Moda app proxy path`, and `default: /apps/moda-consent` to `extensions/moda-whatsapp-consent/blocks/cart-consent.liquid` schema. Use this value (escaped for HTML) to derive the three existing `data-*-url` attributes with suffixes `/cart/status`, `/cart/receipt` and `/cart/verify`. Keep their same backend route mapping; do **not** create new app endpoints, proxy services or store-wide preferences. An empty setting falls back to the default. Do not permit a query, fragment, absolute URL or path outside Shopify's supported proxy prefixes.
2. **Bounded storefront validation:** before any request, validate the configured proxy root as exactly `/(a|apps|community|tools)/<subpath>` with a single nonempty Shopify-valid subpath of at most 30 characters (`[A-Za-z0-9_-]`), no trailing slash, dot segments, backslashes, whitespace, query or fragment. Reject reserved subpaths `admin`, `services`, `password`, `login`. Build three same-origin paths from the validated root; retain existing `sameOriginUrl` protection. Any invalid/unreachable configuration hides only Moda's checkbox, never sends a consent receipt to another origin, never auto-GRANTs and never blocks checkout. Do not attempt to discover Shopify's custom proxy path via unverified assumptions or a new API.
3. **Agent tests:** assert all three URLs are derived from default `/apps/moda-consent` and custom `/tools/custom-consent`, `/a/custom-consent` (and optionally `/community/...`); reject malicious/full-URL/invalid/empty-reserved path input except empty setting's documented default. Verify that current-cart receipt verification, GRANT/REVOKE reloads, explicit-only issuance, silent failures, section-load reinitialisation and all 20 shopper locales remain unchanged. Do not duplicate receipt verification or alter S002 encryption/App Proxy routing.
4. **S005 handoff:** update the merchant-facing activation guidance in **S005 later**, explaining that a merchant who changes Shopify's proxy URL must set the same path in this existing App Block setting. S003 only supplies the validated setting; do not implement S005 settings or live store activation.

### Required re-submission and ownership

Return the same SHOPIFY-003 task to its `moda_app` agent. Reuse the current implementation worktree and branch; do not reset implementation history. The agent must read this newest Architect Review, claim Attempt 3 through `/moda-task`, implement the bounded source/test correction and report exact paths, SHAs, tests, `git diff --check`, targeted lint, Shopify Theme Check/build, app build and baseline-separated typecheck errors. The agent then sets status to `review`, reports and **stops**. Dependants remain gated until architect acceptance. No `docs/decisions/**/_index.md` changes.
