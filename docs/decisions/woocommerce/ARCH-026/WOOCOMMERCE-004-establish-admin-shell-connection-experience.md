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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-003
enables:
  - ARCH-026-WOOCOMMERCE-005
created: 2026-10-02
updated: 2026-10-02
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

### Accessibility and localisation

All merchant-visible strings must use the existing WordPress/WooCommerce i18n tooling.

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
- API-003 merchant business read/write capability.
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

### R10 — Accessible/localizable presentation

All merchant-visible text and actions use the repository's WordPress/WooCommerce i18n and accessibility conventions.

## Work Items

- [ ] Replace the WOO-001 placeholder React page with a bounded Moda Interact Admin application shell.
- [ ] Preserve the canonical `/moda-interact` Woo Admin page registration and Woo navigation placement.
- [ ] Add a typed/discriminated browser connection-state model covering all accepted WOO-003 states plus local loading/failure state.
- [ ] Add a bounded browser client for WOO-003 local GET/POST connection routes using WordPress REST nonce/cookie semantics.
- [ ] Implement initial connection-state loading with stale-response protection.
- [ ] Implement `DISCONNECTED` connection presentation and single-flight Connect action.
- [ ] Implement `RECONNECT_REQUIRED` presentation and explicit single-flight Reconnect action.
- [ ] Implement `CONNECTED` summary without inferring onboarding/billing/feature state.
- [ ] Implement `REMOTE_UNAVAILABLE` presentation with status retry only.
- [ ] Implement non-automatic `SITE_URL_CHANGED` blocked/support presentation.
- [ ] Implement bounded `API_NOT_CONFIGURED`, `LOCAL_STATE_INVALID` and browser-load failure presentation.
- [ ] Add reusable notice/loading/action-state primitives only where they directly support this shell.
- [ ] Ensure unavailable future pages are not exposed as active navigation destinations.
- [ ] Add focused React/controller/client tests for all states, action admission and request races.
- [ ] Verify browser bundles/state/logs contain no WOO-003 secret material.
- [ ] Document the shell/page-extension boundary for later WOO-005 work.

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

- [ ] `/moda-interact` renders the production-shaped Moda Interact React shell through the existing WooCommerce Admin page mechanism.
- [ ] No branded top-level WordPress menu is added.
- [ ] The shell makes no browser-direct call to the hosted Moda API.
- [ ] Browser-side requests target only the accepted WOO-003 local WordPress REST routes.
- [ ] All seven WOO-003 connection states have explicit presentation/behavior.
- [ ] Unknown/malformed local API status cannot be interpreted as `CONNECTED` or `DISCONNECTED`.
- [ ] `DISCONNECTED` offers one explicit single-flight Connect action.
- [ ] `RECONNECT_REQUIRED` offers one explicit single-flight Reconnect action.
- [ ] Repeated clicks cannot create overlapping POST connection requests.
- [ ] A stale GET response cannot overwrite a newer successful connection/reconnect result.
- [ ] `CONNECTED` does not imply or display onboarding/billing/entitlement completion.
- [ ] `REMOTE_UNAVAILABLE` does not display the installation as disconnected and retry does not automatically rotate credentials.
- [ ] `SITE_URL_CHANGED` never automatically reconnects or creates a new tenant from the browser.
- [ ] `API_NOT_CONFIGURED` and `LOCAL_STATE_INVALID` are shown as bounded configuration/recovery states rather than raw PHP/API errors.
- [ ] Browser-visible state, bundles, console/log captures and local/session storage contain no bootstrap secret, installation credential, Authorization header or credential digest.
- [ ] Future unimplemented merchant pages are not navigable.
- [ ] All merchant-visible strings are localizable through existing WordPress/WooCommerce tooling.
- [ ] All connection actions/statuses have accessible text semantics and keyboard-operable controls.
- [ ] No billing, recovery, Merchant Knowledge, promotions, product/discount, event-ingress or Background functionality is introduced.

## Validation

Run the Woo repository's declared validation commands and record exact commands/results.

Required validation categories:

- [ ] `scripts/bootstrap-woocommerce.sh` succeeds before repository validation;
- [ ] clean npm/Composer dependency installation from accepted lockfiles where required by the repository;
- [ ] production asset build;
- [ ] JavaScript/TypeScript typecheck where provided;
- [ ] JavaScript lint;
- [ ] PHP lint/tests only where Admin registration/bootstrap PHP is touched;
- [ ] focused browser/client tests for strict local response parsing and all accepted connection statuses;
- [ ] single-flight Connect test;
- [ ] single-flight Reconnect test;
- [ ] stale GET versus newer POST race test;
- [ ] stale/unmounted action completion test;
- [ ] `REMOTE_UNAVAILABLE` refresh-without-reconnect test;
- [ ] `SITE_URL_CHANGED` no-POST/no-auto-reconnect test;
- [ ] unknown/malformed response fail-closed test;
- [ ] browser artifact/state/log negative test for bootstrap/install credential material;
- [ ] WordPress/WooCommerce runtime smoke showing `/moda-interact` shell renders under the accepted supported matrix;
- [ ] runtime smoke with a controlled WOO-003 local REST fixture for DISCONNECTED -> CONNECTED;
- [ ] runtime smoke for REMOTE_UNAVAILABLE and RECONNECT_REQUIRED presentation;
- [ ] accessibility-focused assertions for action names/status text/busy state;
- [ ] production plugin ZIP still builds after shell changes;
- [ ] `git diff --check`;
- [ ] clean repository/worktree evidence required by the task protocol.

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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- WOO-003 provides the accepted local connection GET/POST REST contract and all server-side credential handling.
- WOO-001/WOO-002 provide the accepted Woo Admin page/runtime foundation.
- Merchant business screens will be added only after their hosted API contracts exist.

### Unresolved Issues

None within this bounded connection/setup UI task.

### Architectural Concerns

None.

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
