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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-18
---

# Render Shopify Plus checkout WhatsApp consent checkbox

**Architect accepted — Attempt 2, 18 November 2026.** Plus uses **only this checkout checkbox**, while non-Plus uses S003 cart checkbox. Do not run both, and do not implement old S003 cart-selection precedence. The shared temporary choice is one signed `moda_wa_consent_v1` **Shopify checkout attribute**; see [receipt contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md).

## Source, extension and authentication

- Create separate Checkout UI Extension at `extensions/moda-whatsapp-checkout-consent/` with supported Shopify CLI manifest, supported `purchase.checkout.contact.render-after` target and `network_access` capability, Shopify-owned 20 locales and tests. Never use theme script injection, Shopify native marketing checkbox or a second phone field.
- Use Shopify checkout extension's **signed session token** obtained from `shopify.sessionToken.get()` to call S002 `POST checkout/receipt`; verify by SDK `authenticate.public.checkout` or installed equivalent on server. The extension's `checkoutToken` is a stable checkout locator and may be undefined: do not offer an actionable Moda checkbox if unavailable or if app verification fails. Do not invent verified JWT claims or use unauthenticated checkoutToken alone as authority.
- Only after verifying `instructions.attributes.canUpdateAttributes`, supported plan/target and signed server response, call `shopify.applyAttributeChange({type:'updateAttribute',key:'moda_wa_consent_v1',value:receipt})`. Confirm `type:'success'` and read the current checkout attribute. Accelerated checkouts or unavailable attribute mutations hide Moda control and do not block payment.

## Explicit action and status

- Show exact English wording `Send me WhatsApp shopping updates, reminders and offers.` with Shopify locale meaning. On verified returning customer, S002 reads current PostgreSQL consent for display; for current checkout read/verify current signed receipt and show its decision. No auto-GRANT on render/default, no write without explicit check/uncheck.
- Each deliberate GRANT/REVOKE obtains a fresh `kind=x` receipt bound to current checkout token and replaces the **same attribute key**; no Redis, cart marker or SQL consent write at click time. A failed issuer or Shopify mutation does not show saved state; hide or restore control silently.
- A Plus merchant's cart App Block is disabled by the merchant installation/plan configuration in S005; no precedence between cart and checkout choices exists for Plus. Unsupported express routes are uncovered, not auto-granted.

## Tests/stop

- Real eligible Plus development-store test: verified session JWT/shop/customer, actual checkoutToken, attribute write, authoritative `AbandonedCheckout.customAttributes` retrieved later, malformed/copy/replay scenarios, GRANT->REVOKE replacement, Plus-only placement, readback, 20 locales, accessibility and silent failure.
- SDK mocks are not proof of a working Plus checkout extension. If supported checkout token cannot be established/verified, attribute mutation denied, or extension unavailable under merchant plan, stop with evidence. Never substitute a cart checkbox on Plus or add a new Redis/SQL consent store.

## Completion Report

Task: `ARCH-077-SHOPIFY-004`
Status: Review — Attempt 2 completed the previously blocked live Plus checkout verification.

### Attempt 1 summary (preserved)

Attempt 1 (executor copilot) implemented the Checkout UI Extension at
`extensions/moda-whatsapp-checkout-consent/` (`purchase.checkout.contact.render-after`,
API `2026-10`, `network_access`, 20 Shopify locales), extended
`POST shopify/checkout/receipt` for verified current-checkout display and
read-only returning-customer SQL status, added route/extension-helper tests, and
passed focused Vitest/ESLint/`npm run build`/`shopify app build`. It blocked on
live verification pending an approved Plus development store and preview
invocation. Sealed `shopify.oauth` PlatformConfiguration records for
`development`/`test` were created in the local `moda_interact` database.

### Attempt 2 scope

Developer approved Plus development store `eugenes-plus-store.myshopify.com`,
the `shopify app dev --config moda-interact` preview invocation against the
local database/keyring, and resetting the task to Ready (parent commit
`c522396`). Attempt 2 performed the outstanding live verification and the
minimal code corrections it surfaced.

### Implementation changes (implementation branch `task/ARCH-077-SHOPIFY-004`)

- `3d13eb2` fix(shopify): restore valid app handle `moda-interact` in
  `shopify.app.moda-interact.toml` (attempt-1 local fix, committed).
- `907339c` feat(shopify):
  - `extensions/moda-whatsapp-checkout-consent/src/consent.js`: the receipt
    endpoint origin is now build-time configurable through
    `MODA_CHECKOUT_RECEIPT_ORIGIN` (Shopify CLI `.env` define) with the
    existing `https://app-test.modainteract.com` default unchanged. Without
    this, the extension hardcodes app-test and can never be verified against a
    locally previewed app.
  - `tests/unit/moda-whatsapp-checkout-consent-locales.test.js`: expected
    Chinese locale filenames aligned to the CLI-accepted `zh-CN.json` /
    `zh-TW.json` actually shipped (stale attempt-1 expectation).
  - `tests/unit/routes/shopify-consent-route.test.ts`: removed duplicate
    object property (tsc TS1117) in a mock literal.

### Live Plus checkout verification (eugenes-plus-store.myshopify.com)

Environment: `shopify app dev --config moda-interact --store
eugenes-plus-store.myshopify.com --checkout-cart-url "/cart/51656792441049:1"`,
local `DATABASE_URL` (Docker `moda-postgres`, database `moda_interact`), keyring
env from the developer-held `platform.env`, cloudflare tunnel, development-store
password supplied via `SHOPIFY_FLAG_STORE_PASSWORD`. The embedded app was opened
in Shopify admin, completing token exchange against the local app: offline
`shopify."Session"` row stored and `commerce."Shop"` row created with status
`ACTIVE` (shopId `cmwlnm2hx0000pomhrco0r59e`). Live checkout interaction was
performed by the developer in their authenticated browser on the dev-preview
checkout; all server-side evidence was captured from the locally running app
logs, the local database and the Admin API (CLI GraphiQL).

Verified live:

- Verified signed session JWT: server log shows `Authenticating checkout
  request` → `Validating session token` → `Session token is valid - validated`
  for every status/decision call (e.g. 09:13:14Z, 09:14:08Z, 11:15:25Z), via
  `authenticate.public.checkout`, with shop gate `commerce.Shop` = ACTIVE.
- Actual checkoutToken: extension rendered only on a real checkout with a
  checkout token; the receipt bound to that token verified on reload and on
  the same checkout session at 11:15:25Z.
- Exact English wording displayed: `Send me WhatsApp shopping updates,
  reminders and offers.`
- No auto-GRANT on render: fresh checkout rendered unchecked with no write.
- GRANT: explicit check issued a fresh `kind=x` receipt, wrote only the
  `moda_wa_consent_v1` checkout attribute, confirmed Shopify `type:'success'`
  and attribute readback before showing checked (instrumented run showed the
  full pipeline `ok`).
- GRANT -> REVOKE replacement: explicit uncheck issued a fresh REVOKE receipt
  replacing the same attribute key; state persisted unchecked. One earlier
  REVOKE attempt during concurrent contact-email entry reverted silently to
  the last verified state — the specified silent-restore behaviour on a
  transient mutation failure; subsequent cycles replaced correctly.
- Persistence/readback: reload re-verified the current signed receipt
  server-side and displayed its decision (checked after GRANT).
- AbandonedCheckout propagation: Admin API `abandonedCheckouts` returned
  `gid://shopify/AbandonedCheckout/47325222568153` whose
  `customAttributes` contained `moda_wa_consent_v1` with the real signed
  receipt (`v1.dev-1....`, 199 chars), having replaced an earlier forged
  value on the same key — authoritative later retrieval confirmed.
- Malformed/copied receipt: a cart-permalink-injected forged
  `moda_wa_consent_v1` value produced server `receipt_verification` failures
  with `INVALID_RECEIPT` (09:40:29Z, 09:40:54Z), HTTP 400, and the extension
  hid the control silently; checkout remained fully usable.
- Replay binding: the copied real receipt presented on the same checkout
  token verified (expected — same binding, 11:15:25Z, no failure); cross-token
  replay rejection is enforced by `verifyConsentReceipt` binding checks
  covered by `tests/unit/services/shopify-consent-receipt.service.test.ts`
  (different token/shop/customer each throw). A cross-session incognito
  attempt showed the control hidden, but the dev-preview extension does not
  load in that fresh session, so that specific run is recorded as
  inconclusive rather than as cryptographic evidence.
- Silent failure: a transient local Postgres connection failure
  (`shop_resolution` 10:30:53Z → 503) and the earlier unknown-shop phase both
  resulted in the control being hidden with checkout unaffected — observed
  live twice.
- Accessibility: checkbox reachable via Tab with visible focus and toggles
  with Space (developer-verified live).
- Plus placement: rendering occurred on the Plus development store checkout
  contact step; the checkout-step surface is Plus-gated by Shopify, and
  non-Plus/cart-checkbox substitution was never introduced (S005 owns the
  merchant plan configuration).
- Locales: live render verified in `en` (the store's only published locale —
  `shopLocales` returns only `en`); the 20-locale catalogue is enforced by
  the locale unit test and the Shopify CLI build, and the dev manifest
  served all 20 translations.

Not live-verified, with reason:

- Returning-customer PostgreSQL display path (`receipt: null` with a verified
  customer `sub` claim): requires a logged-in customer account in checkout;
  covered by route unit tests (`shopify-consent-route.test.ts`).
- Cross-checkout replay rejection live (see above): service-test covered;
  live forged/copied-value rejection was demonstrated.

### Validation

- PASS — focused Vitest: `tests/unit/moda-whatsapp-checkout-consent.test.js`,
  `tests/unit/moda-whatsapp-checkout-consent-locales.test.js`,
  `tests/unit/routes/shopify-consent-route.test.ts`,
  `tests/unit/services/shopify-consent-receipt.service.test.ts` — 4 files,
  37 tests.
- PASS — focused ESLint on the three changed files.
- PASS — `shopify app build --config moda-interact`.
- FAIL (unrelated baseline, unchanged) — `npm run typecheck` reports errors
  only in untouched `app/routes/auth/login/route.jsx` and
  `app/routes/webhooks/root/route.jsx`. The previously unreported TS1117 in
  the task-owned route test was fixed in this attempt.

### Observations for `moda_architect`

- The extension's default receipt origin remains
  `https://app-test.modainteract.com`. If this extension version is intended
  for production deployment, the production origin (or a deploy-time
  `MODA_CHECKOUT_RECEIPT_ORIGIN`) must be provided at `shopify app deploy`
  build time; left as an architecture/deployment decision.
- Webhook subscriptions observed during dev pointed at the per-run tunnel URL;
  CHECKOUTS_UPDATE deliveries stopped after a tunnel rotation until restart —
  dev-only behaviour, no code change.
- Dev-preview checkout extension loading is bound to the merchant/admin
  browser session; automated (non-admin) browser sessions do not load draft
  extensions. Live UI steps were therefore developer-executed with
  server-side evidence captured locally.

### Physical worktree isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-SHOPIFY-004`
- Parent branch: `task/ARCH-077-SHOPIFY-004`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-SHOPIFY-004`
- Implementation branch: `task/ARCH-077-SHOPIFY-004`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

### Start-of-attempt synchronization (launcher packet, attempt 2)

- Parent remote task branch fast-forwarded: not-needed
- Parent `origin/main` incorporated: already-current
- Implementation remote task branch fast-forwarded: not-needed
- Implementation `origin/main` incorporated: already-current
- Claim: attempt 2, executor copilot, claimed 2026-11-18T02:24:07Z, commit
  `6efa43d`, pushed.

### Recursive implementation submodules (launcher packet)

- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- Recorded submodule commit: `database` at
  `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`


## Architect Review — 18 November 2026 — ACCEPTED (Attempt 2)

**Decision: Accepted; task `complete`.** Review of the exact uploaded Attempt 2 Shopify implementation and report, cross-checked with pushed implementation commits `3d13eb2` and `907339c` on `task/ARCH-077-SHOPIFY-004`. No additional implementation attempt is required.

**Accepted source and live evidence:** The separate `moda-whatsapp-checkout-consent` Checkout UI Extension targets `purchase.checkout.contact.render-after`, uses `shopify.sessionToken.get()` with authenticated `POST /shopify/checkout/receipt`, requires current checkout token and attribute-mutation capability, and writes only the single `moda_wa_consent_v1` attribute after explicit customer interaction. Issuer uses the accepted Shared AEAD receipt contract. Live Plus dev-store report records successful GRANT, REVOKE replacement, readback/persistent verified display, `AbandonedCheckout.customAttributes` signed-receipt propagation, tampered receipt refusal, silent failure without checkout blockage, and keyboard accessibility. Exactly 20 locale JSON files and unchanged required English wording were inspected.

**Validation evidence:** Agent reports 37 focused Vitest tests, targeted ESLint and Shopify app build passed; TypeScript baseline errors remain in untouched `app/routes/auth/login/route.jsx` and `app/routes/webhooks/root/route.jsx`, while the task-owned TS1117 test error was corrected. The architect inspected uploaded source and reviewed pushed commits; the live browser/shop/GraphQL session and tests were not independently re-executed by the architect.

**Remaining gates, not S004 defects:** Live cross-checkout replay denial was inconclusive; signed receipt binding is exercised by the Shared receipt-service tests and must receive end-to-end certification in ARCH-077-SYSTEM-TEST-001. The verified returning-customer PostgreSQL initial display has route-test coverage but was not exercised live with a logged-in Plus customer; S005 owns merchant activation and returning-customer demonstration. Only English was exercised in the single-locale dev store; the other 19 locale files have test/build evidence, with live coverage in downstream certification as feasible.

**Required deployment handoff to S005:** `MODA_CHECKOUT_RECEIPT_ORIGIN` is resolved at extension build time and defaults to `https://app-test.modainteract.com`. Before a production extension build/deploy, set it to the actual published app origin and validate the emitted bundle uses that host. The default test host must not be silently deployed into production. This is a deployment configuration/certification gate, not permission to create another endpoint or receipt scheme. Non-Plus S003 and Plus S004 remain mutually exclusive; S005 must verify placement against the merchant's plan.

**No new consent database/Redis state:** S004 makes no click-time SQL consent write, does not create a Redis consent ledger/queue, and does not override BACKGROUND-002's recoverability-only materialisation contract.
