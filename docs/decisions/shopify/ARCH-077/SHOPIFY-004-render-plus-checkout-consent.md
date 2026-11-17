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
status: blocked
priority: 50
executor: copilot
claimed_at: 2026-11-17T20:15:17Z
attempt: 1
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-SHOPIFY-005, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Render Shopify Plus checkout WhatsApp consent checkbox

**Pending; depends on accepted S002.** Plus uses **only this checkout checkbox**, while non-Plus uses S003 cart checkbox. Do not run both, and do not implement old S003 cart-selection precedence. The shared temporary choice is one signed `moda_wa_consent_v1` **Shopify checkout attribute**; see [receipt contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md).

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
Status: Blocked — live Plus checkout verification remains outstanding.

Implemented in `moda-interact` commits `028086d` and `85ce24f`:

- Added the CLI-scaffolded Checkout UI Extension at
  `extensions/moda-whatsapp-checkout-consent/`, targeting
  `purchase.checkout.contact.render-after` on API `2026-10` with
  `network_access`.
- Added the localized consent checkbox in the 20 supported Shopify locales.
  Chinese translations use the CLI-accepted regional locale filenames
  `zh-CN.json` and `zh-TW.json`.
  The extension hides the control unless the correct target, checkout token,
  attribute mutation instruction and authenticated server status are available.
  It issues a receipt only after an explicit choice, writes only
  `moda_wa_consent_v1`, and confirms Shopify attribute readback before reflecting
  the new state.
- Extended `POST shopify/checkout/receipt` to return a verified current-checkout
  receipt decision or read-only returning-customer SQL status for display.
- Added route and extension-helper tests.

Validation:

- PASS — focused Vitest: 3 files, 22 tests.
- PASS — focused ESLint for changed application, extension and test files.
- PASS — `npm run build`.
- PASS — `shopify app build --config moda-interact`.
- PASS — Shopify Checkout UI validator for
  `purchase.checkout.contact.render-after`, API `2026-10`.
- PASS — after correcting the Chinese locale filenames, `shopify app build
  --config moda-interact` succeeded.
- PASS — after `read_brand` was removed from the local app config and its handle
  was restored to a valid value, `shopify app dev` reached its ready state on
  the Plus development store and built the extension through a temporary local
  tunnel.
- BLOCKED — the preview page failed during Shopify OAuth bootstrap with
  `shopify.oauth: DATABASE_UNAVAILABLE`. A local pgvector-enabled PostgreSQL
  container is running and all 83 existing migrations were applied to the
  local `moda_interact` database, but that fresh database has no
  `PlatformConfiguration` records, including no development `shopify.oauth`
  record. A local test-only OAuth configuration and matching unseal keyring
  must be provisioned before the app can start. No managed database URL or
  production credentials were used.
  Therefore this task has not verified a real signed checkout session, actual
  checkout token, Shopify attribute write/readback and subsequent
  `AbandonedCheckout.customAttributes` propagation, copied/malformed/replay
  cases, GRANT-to-REVOKE replacement, plan-specific placement, accessibility or
  live silent-failure behavior. CLI build and SDK mocks are not evidence of
  those live behaviors.
- FAIL (unrelated errors) — `npm run typecheck` reports errors only in untouched
  `app/routes/auth/login/route.jsx` and `app/routes/webhooks/root/route.jsx`;
  no changed task file is named in the diagnostics.

Unresolved blocker: provision non-production Shopify OAuth configuration in
the local development database, then run the required end-to-end checkout
propagation scenarios before unblocking this task. No cart checkbox or
alternate consent store was substituted.

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-077-SHOPIFY-004`
- Parent branch: `task/ARCH-077-SHOPIFY-004`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-077-SHOPIFY-004`
- Implementation branch: `task/ARCH-077-SHOPIFY-004`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization from the launcher packet:

- Parent remote task branch fast-forwarded: not needed
- Parent `origin/main` incorporated: already current
- Implementation remote task branch fast-forwarded: not needed
- Implementation `origin/main` incorporated: already current

Recursive implementation submodules:

- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- Recorded submodule commit: `database` at
  `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`
