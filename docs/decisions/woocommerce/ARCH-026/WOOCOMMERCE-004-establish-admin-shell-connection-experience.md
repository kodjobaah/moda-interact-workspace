---
id: ARCH-026-WOOCOMMERCE-004
architecture_id: ARCH-026
title: Establish the WooCommerce Admin shell and connection experience
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: copilot
claimed_at: 2026-10-03T19:30:12Z
attempt: 1
depends_on:
  - ARCH-026-WOOCOMMERCE-003
enables:
  - ARCH-026-WOOCOMMERCE-005
created: 2026-10-02
updated: 2026-10-03
---

# Establish the WooCommerce Admin shell and connection experience

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Replace the WOO-001 placeholder React page with the first production-shaped Moda Interact merchant experience inside WooCommerce Admin.

The task must establish one bounded Woo Admin application shell and use the accepted WOO-003 local WordPress REST boundary to present and operate the real Moda connection lifecycle without exposing any Moda installation credential to browser JavaScript.

The completed browser/runtime flow is:

```text
WooCommerce Admin
      |
      v
Moda Interact React application shell
      |
      | GET /wp-json/moda-interact/v1/connection
      v
browser-safe connection state
      |
      +-- DISCONNECTED --------> explicit Connect action
      |                              |
      |                              | POST local connection route
      |                              v
      |                         PHP WOO-003 boundary
      |                              |
      |                              v
      |                         hosted Moda API
      |
      +-- CONNECTED -----------> connected account summary
      +-- RECONNECT_REQUIRED --> explicit Reconnect action
      +-- REMOTE_UNAVAILABLE --> retain connected state + retry status
      +-- SITE_URL_CHANGED ----> blocked migration/support presentation
      +-- API_NOT_CONFIGURED --> deployment/configuration presentation
      `-- LOCAL_STATE_INVALID --> bounded recovery/support presentation
```

This task creates the real merchant shell and connection/setup experience only. It MUST NOT implement merchant business data such as recoveries, usage, Merchant Knowledge, promotions, billing, products, discounts or CommerceAgent configuration.

## Context

WOO-001 establishes the installable PHP + React extension foundation and one minimal React-powered WooCommerce Admin page at:

```text
/moda-interact
```

WOO-002 establishes the supported WordPress/WooCommerce/PHP runtime and safe plugin lifecycle.

WOO-003 establishes the complete PHP/server-side connection boundary and exposes only browser-safe local WordPress REST routes:

```text
GET  /wp-json/moda-interact/v1/connection
POST /wp-json/moda-interact/v1/connection
```

Both routes require a privileged WooCommerce administrator and normal WordPress REST cookie/nonce authorization. WOO-003 owns the long-lived installation credential, bootstrap secret, remote Moda API client, site-control challenge callback and remote probe. React MUST NOT reimplement any of those responsibilities.

The local GET route exposes one browser-safe connection state from this accepted set:

```text
DISCONNECTED
CONNECTED
RECONNECT_REQUIRED
SITE_URL_CHANGED
REMOTE_UNAVAILABLE
API_NOT_CONFIGURED
LOCAL_STATE_INVALID
```

A successful `CONNECTED` response may include only safe metadata such as:

```text
installationId
shopId
canonicalSiteUrl
credentialVersion
```

No raw installation credential, Authorization header, bootstrap secret or digest may cross into browser state.

WooCommerce's supported React-powered Admin page mechanism is the architecture-approved host for this UI. The existing WOO-001 `/moda-interact` page identity remains stable. Do not replace it with a separate WordPress top-level application menu, iframe or independently hosted frontend.

ARCH-026 is still establishing application foundations. WOO-004 must not create placeholder merchant-data screens that imply unavailable features are implemented.

## Scope

Modify only `moda-interact-woocommerce` files required for the React/Woo Admin application shell, browser-side local REST client, connection/setup presentation and focused tests/documentation.

Expected implementation areas are conceptually:

```text
src/
  admin/
    app.tsx
    app-shell.tsx
    connection/
      connection-card.tsx
      connection-state.ts
      use-connection.ts
    api/
      wordpress-client.ts
    components/
      ... bounded shared presentation primitives
    styles/
      ...

tests/
  javascript/
    ... focused shell/connection tests
```

Exact filenames may follow the accepted WOO-001 repository structure.

### WooCommerce Admin hosting

Retain the canonical Woo Admin page identity:

```text
path: /moda-interact
name: Moda Interact
```

Register/render it through WooCommerce's supported React-powered Admin page mechanism established by WOO-001.

Use the existing WooCommerce navigation structure. Do not create a branded top-level WordPress menu.

Do not introduce the experimental WooCommerce Settings UI as a dependency for this application shell. This is a standalone merchant application surface, not a Woo settings-form migration.

### Application shell

Replace the WOO-001 placeholder with a production-shaped application shell containing only functionality that is real at this stage.

The shell must own:

- page-level loading and fatal-error presentation;
- application heading/identity;
- bounded connection/setup content area;
- reusable notice/status presentation;
- accessible action admission/pending feedback;
- an extension point/page registry suitable for later ARCH-026 screens without making unimplemented screens navigable now.

Do not expose navigation entries for Recoveries, Merchant Knowledge, Billing, Promotions or another future capability until the owning implementation task makes that page real.

### Browser-to-PHP API boundary

React MUST call only the local WOO-003 WordPress REST routes for connection state/actions.

Use the normal WordPress REST client/nonce mechanism available in the accepted extension foundation rather than constructing a browser-side remote Moda client.

The browser MUST NOT know or choose:

```text
Moda API base URL
installation credential
bootstrap secret
Authorization header
credential digest
remote Shop identity authority
```

Do not call `moda-interact-api` directly from browser JavaScript.

### Initial connection-state load

On application load, request:

```text
GET /wp-json/moda-interact/v1/connection
```

and map the accepted WOO-003 response into an explicit discriminated browser state rather than scattering raw status-string branches through components.

At minimum model:

```text
LOADING
DISCONNECTED
CONNECTED
RECONNECT_REQUIRED
SITE_URL_CHANGED
REMOTE_UNAVAILABLE
API_NOT_CONFIGURED
LOCAL_STATE_INVALID
LOAD_FAILED
```

`LOAD_FAILED` is browser/client transport/parsing failure and is distinct from WOO-003's `REMOTE_UNAVAILABLE` state.

Unknown status values or malformed local responses must fail closed into a bounded error state and must not be interpreted as `DISCONNECTED` or `CONNECTED`.

### Connection action

When status is `DISCONNECTED`, expose one explicit merchant action:

```text
Connect Moda Interact
```

The button invokes exactly:

```text
POST /wp-json/moda-interact/v1/connection
```

with no browser-supplied tenant/site/API identity.

Action requirements:

- single-flight: repeated clicks while pending cannot create overlapping POSTs;
- pending state is visually and programmatically exposed;
- controls that would trigger another connect/reconnect are disabled while pending;
- successful completion replaces local UI state from the validated POST response and then may refresh GET state when required by the accepted WOO-003 contract;
- failure produces a bounded actionable message without showing arbitrary remote/PHP response bodies;
- component unmount/navigation must not allow a stale completion to overwrite a newer state.

### Reconnect action

When status is `RECONNECT_REQUIRED`, expose one explicit:

```text
Reconnect Moda Interact
```

using the same WOO-003 POST route.

The UI must explain that local Moda connection credentials need to be re-established without claiming merchant account/business data has been lost.

Do not clear local connection state from React and do not implement credential rotation in JavaScript; WOO-003 owns the reconnect semantics.

### Connected state

When status is `CONNECTED`, present a bounded connection summary using only browser-safe WOO-003 metadata.

At minimum the UI may display:

```text
Connection: Connected
canonical site URL
```

Installation ID, Shop ID and credential version may be shown only where useful for support/diagnostics and must not be presented as editable identity fields.

Do not infer billing/onboarding/feature state from `CONNECTED`. Connection proves only installation authentication.

### Remote unavailable state

`REMOTE_UNAVAILABLE` means a valid local connection may still exist while the hosted API cannot currently be reached.

The UI MUST:

- avoid presenting the merchant as disconnected;
- preserve the distinction between remote availability and credential state;
- offer a bounded `Retry`/refresh action that re-runs the local GET status check;
- not automatically invoke reconnect/credential rotation merely because the remote probe failed.

### Site URL changed state

`SITE_URL_CHANGED` is not recoverable by an automatic browser reconnect in ARCH-026 because API-002 explicitly makes site/domain migration out of scope.

The UI MUST:

- clearly state that the current WordPress site URL differs from the connected Moda installation;
- not call POST connection automatically;
- not expose the stored credential;
- direct the merchant to a bounded support/future migration path rather than silently creating another Moda Shop.

Do not add domain-migration functionality in this task.

### API not configured state

`API_NOT_CONFIGURED` is an installation/deployment configuration problem, not a merchant billing or account state.

The UI should present a bounded administrator-facing message explaining that Moda service connectivity is not configured for this plugin deployment.

Do not expose environment-variable names, credentials or internal network details unnecessarily in merchant-visible content.

### Local state invalid

`LOCAL_STATE_INVALID` means WOO-003 rejected the stored local connection record.

Present a bounded recovery/support state. An explicit reconnect action may be offered only if the accepted WOO-003 response/action contract states reconnect is safe for that condition; do not infer this from the status name alone.

### Refresh / request concurrency

Connection status reads and connect/reconnect commands must be race-safe.

At minimum:

- ignore/cancel stale status loads when a newer request has become authoritative;
- do not allow polling overlap (this task does not require polling at all);
- do not permit a late GET response to overwrite a newer successful POST connection result;
- one explicit retry action may start a new GET after the previous request has settled/cancelled.

### Accessibility and internationalization

Internationalization is a first-class requirement of the Woo Admin shell.

All merchant-visible PHP/JavaScript strings must use the existing WordPress/WooCommerce i18n tooling and the canonical `moda-interact` text domain. React/browser strings should use WordPress i18n primitives rather than a Moda-maintained locale switch. PHP must register script translations through the supported WordPress mechanism when required by the accepted build.

The UI locale is the current WordPress administrator/request locale. It is distinct from the store's business/default locale that later merchant bootstrap/setup APIs expose. WOO-004 MUST NOT persist the current admin user's locale as merchant/store international context.

Do not introduce a fixed Moda-specific Woo locale allowlist. Any locale that WordPress/WooCommerce can legitimately run for the current administrator must be allowed to reach the normal translation/fallback mechanism. Missing Moda translation coverage falls back through WordPress/i18n behavior; it does not make the locale unsupported.

The browser must not rewrite WordPress locale identity into a different merchant/store locale. Locale conversion for shared backend store context belongs to the later provider-owned synchronization path, not this connection shell.

Interactive controls must have accessible names and keyboard behavior.

Connection state must not be communicated by color/icon alone; include text/status semantics.

Pending actions should communicate busy/disabled state to assistive technologies where supported by the selected components.

### UI dependencies

Prefer WordPress/WooCommerce-provided React primitives/packages already supported by the generated extension foundation.

Do not introduce a second full design system, router framework, generic data-fetching framework or state-management library solely for this bounded shell.

If the accepted WOO-001 scaffold already provides React/WordPress packages, reuse them rather than bundling a duplicate React runtime.

## Out of Scope

- Direct browser calls to `moda-interact-api`.
- PHP connection/authentication implementation; owned by WOO-003.
- Remote installation/site-control challenge implementation; owned by API-002/WOO-003.
- New WordPress REST routes.
- Merchant onboarding state or UI.
- Provider-neutral onboarding migration.
- Billing/subscriptions.
- Recovery list/configuration.
- Merchant Knowledge.
- Promotions.
- Products/coupons/discounts.
- CommerceAgent configuration.
- WhatsApp.
- Cart/checkout/order event ingress.
- Redis/BullMQ/Background.
- API-003 merchant business read capability.
- Gateway/Render deployment.
- Site/domain migration.
- Installation revocation/uninstall flow.
- Additional top-level WordPress menu entries.
- iframe-hosted Moda pages.
- Experimental Woo Settings UI migration.
- Placeholder navigation to future/unimplemented screens.
- A generic frontend framework/plugin system.

## Requirements

### R1 — Woo Admin remains the host

Moda Interact remains a React-powered WooCommerce Admin page at `/moda-interact`; no separate merchant frontend runtime or top-level WordPress application menu is introduced.

### R2 — Browser talks only to local WordPress REST

React consumes WOO-003's local connection GET/POST routes and never sends the installation credential or Authorization header itself.

### R3 — Connection state is explicit and exhaustive

All accepted WOO-003 connection statuses are represented deliberately. Unknown/malformed responses fail closed and cannot masquerade as a connected/disconnected state.

### R4 — Connect/reconnect commands are single-flight

A user cannot create overlapping local POST connection commands through repeated UI interaction.

### R5 — Remote outage is not disconnection

`REMOTE_UNAVAILABLE` retains the distinction between locally connected credentials and temporary provider/API reachability.

### R6 — Site migration is not silently invented

`SITE_URL_CHANGED` never triggers automatic reconnect or creation of a second tenant from the browser.

### R7 — Connection does not imply onboarding or billing

The UI must not display a successful installation connection as proof that onboarding, plan activation, billing or entitlements are complete.

### R8 — Credentials never become React state

No bootstrap secret, installation credential, digest or Authorization header is localized, fetched, logged, rendered or stored in browser state/storage.

### R9 — No fake feature pages

Only connection/setup functionality proven by accepted backend/plugin capabilities is navigable in this task.

### R10 — Accessible and open-ended WordPress locale presentation

All merchant-visible text and actions use the repository's WordPress/WooCommerce i18n and accessibility conventions. The shell does not maintain a fixed Woo locale allowlist and does not reject an administrator locale because a Moda translation is missing.

## Work Items

- [x] Replace the WOO-001 placeholder React page with a bounded Moda Interact Admin application shell.
- [x] Preserve the canonical `/moda-interact` Woo Admin page registration and Woo navigation placement.
- [x] Add an explicit browser connection-state model covering accepted WOO-003 statuses plus local loading/failure states.
- [x] Add a bounded browser client for local GET/POST routes using WordPress api-fetch cookie/nonce semantics.
- [x] Implement initial connection loading, stale-response protection, and single-flight status reads.
- [x] Implement `DISCONNECTED` Connect and `RECONNECT_REQUIRED` Reconnect presentations/actions with single-flight POST admission.
- [x] Implement a safe `CONNECTED` summary without inferring onboarding, billing, entitlement, or feature state.
- [x] Implement `REMOTE_UNAVAILABLE` status retry only and blocked `SITE_URL_CHANGED` presentation.
- [x] Implement bounded `API_NOT_CONFIGURED`, `LOCAL_STATE_INVALID`, and browser-load failure presentations.
- [x] Add accessible loading, notice, pending, and action feedback for the connection shell.
- [x] Route merchant-visible React strings through WordPress i18n with the `moda-interact` text domain and register script translations.
- [x] Add static/test guards against a locale allowlist or persisting admin locale/store context.
- [x] Keep future merchant pages out of navigation and add an internal connection-section composition boundary.
- [x] Add focused client/controller/presentation tests for statuses, response parsing, admission, and races.
- [x] Verify the production browser bundle and runtime browser storage contain no WOO-003 secret material.
- [x] Document the shell/page-extension boundary for later WOO-005 work.

## Interfaces / Contracts

### Local API owner

`ARCH-026-WOOCOMMERCE-003`

### Local browser API consumed

```text
GET  /wp-json/moda-interact/v1/connection
POST /wp-json/moda-interact/v1/connection
```

### Connection status values consumed

```text
DISCONNECTED
CONNECTED
RECONNECT_REQUIRED
SITE_URL_CHANGED
REMOTE_UNAVAILABLE
API_NOT_CONFIGURED
LOCAL_STATE_INVALID
```

### Woo Admin page identity

```text
path: /moda-interact
name: Moda Interact
```

### Browser security boundary

React/browser code receives only WOO-003 browser-safe response data. It never consumes the API-002 remote contract directly and never receives the long-lived installation credential.

### Future page-extension boundary

WOO-004 may create one repository-local page/section registry or composition boundary for future real merchant pages.

That registry is an internal frontend composition mechanism, not a cross-service contract. It must not expose unimplemented routes merely to reserve names.

## Dependencies

- `ARCH-026-WOOCOMMERCE-003`

WOO-003 must be architect-accepted `complete` before WOO-004 becomes Ready.

WOO-004 must consume the accepted WOO-003 local browser contract rather than an in-review draft.

## Enables

- `ARCH-026-WOOCOMMERCE-005`

WOO-005 may add the first real merchant business screen only after this shell is accepted and the corresponding hosted API capability is architect-accepted.

## Acceptance Criteria

- [x] `/moda-interact` renders through the existing WooCommerce Admin page mechanism; no top-level WordPress menu was added.
- [x] Browser calls use only WOO-003 local WordPress REST routes; no hosted Moda API client/call was added.
- [x] All seven WOO-003 statuses have explicit behavior and malformed/unknown data fails closed.
- [x] Connect and Reconnect are explicit, state-gated, and single-flight; stale GETs cannot override newer POST results.
- [x] Connected, outage, URL-change, configuration, invalid-local-state, and load-failure messages remain bounded and do not infer business lifecycle state.
- [x] Future pages are not navigable; merchant strings use WordPress i18n and current administrator locale is not stored as merchant context.
- [x] Connection controls expose accessible text, `aria-busy`, and disabled pending behavior.
- [x] No out-of-scope billing, recovery, knowledge, promotion, catalog, event, or Background functionality was introduced.

## Validation

Run the Woo repository's declared validation commands and record exact commands/results.

Required validation categories:

- [x] Bootstrap: `scripts/bootstrap-woocommerce.sh` succeeded before repository commands.
- [x] Locked dependencies: `npm ci`; `composer install --no-interaction`.
- [x] Production assets: `npm run build`; `npm run plugin-zip` succeeded and produced `moda-interact.zip`.
- [x] JavaScript tests: `npm run test:js` passed, 31 tests across 3 files.
- [x] Changed-file JavaScript lint: `npx wp-scripts lint-js src/page.js src/connection-client.js src/connection-controller.js tests/js/page.test.js tests/js/connection-client.test.js tests/js/connection-controller.test.js` passed.
- [x] CSS lint: `npm run lint:css` passed.
- [x] PHP tests/lint: `composer test` passed, 27 tests/116 assertions; `composer lint` passed.
- [x] Client/controller tests cover strict status/metadata parsing, local routes, Connect/Reconnect single-flight, stale GET/POST races, unmounted actions, retry-only outage handling, changed-site blocking, and no overlapping status reads.
- [x] Browser artifact/security checks: built bundle has no bootstrap secret, credential digest, Authorization header, or remote API configuration; browser storage contained no connection data.
- [x] Current runtime smoke: WordPress 7.1.2/WooCommerce 11.1.2 rendered `/moda-interact` and bounded `API_NOT_CONFIGURED` state.
- [x] Minimum runtime smoke: WordPress 7.0.6/WooCommerce 11.0.1 rendered `/moda-interact` and bounded `API_NOT_CONFIGURED` state.
- [x] Controlled local REST browser fixture exercised `DISCONNECTED` -> one `POST` -> `CONNECTED`, `RECONNECT_REQUIRED`, `REMOTE_UNAVAILABLE` retry presentation, and `SITE_URL_CHANGED`; retry was GET-only and changed-site issued no POST.
- [x] Accessibility/i18n assertions covered named controls, disabled/busy state, text status semantics, `moda-interact` domain, and absence of future navigation/locale persistence.
- [x] Non-English smoke: user locale resolved to `fr_FR`; shell rendered its normal WordPress fallback path. Temporary user meta was removed afterward.
- [x] `git diff --check` passed.
- [ ] Full `npm run lint:js` remains blocked by 136 pre-existing Prettier findings in the untouched `tests/integration/run-wordpress.mjs`; all changed JS files pass the scoped configured linter.

The runtime UI tests may use controlled local WordPress REST fixtures/stubs at the PHP boundary; they MUST NOT bypass the local REST contract by injecting remote Moda credentials into JavaScript.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin WOO-005 or API-003.

## Implementation Notes

Use the existing WooCommerce React Admin page registration established by WOO-001 rather than creating a second page system.

WooCommerce's documented React-page mechanism uses `wc_admin_register_page()` on the PHP side and `woocommerce_admin_pages_list` on the JavaScript side. Preserve the accepted repository implementation if WOO-001 uses the equivalent current supported API rather than rewriting it gratuitously.

Keep navigation simple. The architecture deliberately avoids exposing future screens before their backend capability exists.

Prefer WordPress/WooCommerce-supplied React and i18n primitives already in the accepted scaffold. Do not add a general router/data-fetch/state-management framework unless the existing foundation demonstrably requires it.

Connection state is not account lifecycle. `CONNECTED` means the Woo plugin can authenticate to Moda; it does not mean merchant onboarding or billing activation has completed.

## Completion Report

### Status

Review

### Files Changed

`moda-interact-woocommerce`: `README.md`, `package.json`, `package-lock.json`, `src/page.js`, `src/index.scss`, `src/connection-client.js`, `src/connection-controller.js`, `includes/Admin/Setup.php`, `includes/Rest/ConnectionController.php`, `tests/PluginTest.php`, `tests/ConnectionControllerTest.php`, `tests/bootstrap.php`, `tests/js/page.test.js`, `tests/js/connection-client.test.js`, and `tests/js/connection-controller.test.js`.

### Work Completed

Replaced the placeholder with the localized, accessible Woo Admin connection shell; added strict local REST parsing, api-fetch integration, request/action single-flight control and race protection; preserved the existing `/moda-interact` registration; registered script translations and cache-busted built JS; allowed only WordPress api-fetch's `_locale=user` query parameter while retaining WOO-003 rejection of other browser inputs; added focused tests and documented the future section boundary.

### Validation Results

See the checked Validation list above. The existing WOO-003 HTTPS/WordPress integration runner passed at `WP_ENV_PORT=8899`. Full `npm run lint:js` reports 136 formatting findings exclusively in the untouched `tests/integration/run-wordpress.mjs`; the scoped linter passes for every JavaScript file changed by WOO-004.

No separate JavaScript/TypeScript typecheck is provided or applicable; changed files are JavaScript and are covered by JS lint, tests, and build.

### Deviations

The live Woo runtime exposed two integration details requiring bounded compatibility work: WordPress api-fetch appends `_locale=user` to REST requests, and throws recognized non-2xx status payloads such as `API_NOT_CONFIGURED`. The local REST guard now permits only that exact locale query value; the browser client normalizes only recognized WOO-003 status bodies and keeps arbitrary/transport errors in `LOAD_FAILED`. A full-repository JS lint cannot pass until existing formatting debt in the untouched WOO-003 integration runner is addressed.

### Assumptions

- WOO-003 provides the accepted local connection GET/POST REST contract and all server-side credential handling.
- WOO-001/WOO-002 provide the accepted Woo Admin page/runtime foundation.
- Merchant business screens will be added only after their hosted API contracts exist.

### Unresolved Issues

The repository-wide `npm run lint:js` baseline has 136 Prettier findings in the unchanged `tests/integration/run-wordpress.mjs`; changed task files pass the configured scoped lint.

### Architectural Concerns

None identified. The existing WOO-003 contract remains the only browser/server boundary; Architect Review is pending.

### Execution Isolation Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-WOOCOMMERCE-004`, branch `task/ARCH-026-WOOCOMMERCE-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-WOOCOMMERCE-004`, branch `task/ARCH-026-WOOCOMMERCE-004`.
- Shared workspace and implementation checkouts were not switched or used for task edits; no other task worktree was reused.
- Launcher start synchronization: task-branch fast-forward was `not-needed` in both worktrees; both already incorporated/current with `origin/main`.
- Launcher claim commit `b8e9bccbd992abd31845b0068566ea9917063bcc` was pushed; dependency gate passed.
- Recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed; there were no submodule entries.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
