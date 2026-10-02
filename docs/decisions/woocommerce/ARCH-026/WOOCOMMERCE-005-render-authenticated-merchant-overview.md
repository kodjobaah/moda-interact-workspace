---
id: ARCH-026-WOOCOMMERCE-005
architecture_id: ARCH-026
title: Render the first authenticated Woo merchant overview
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-004
  - ARCH-026-API-003
enables:
  - ARCH-026-WOOCOMMERCE-006
created: 2026-10-02
updated: 2026-10-02
---

# Render the first authenticated Woo merchant overview

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Extend the accepted WooCommerce Admin shell with the first real merchant-data screen backed by Moda PostgreSQL through the authenticated hosted API.

The completed flow is:

```text
WooCommerce Admin React shell
        |
        | WordPress cookie + REST nonce
        v
GET /wp-json/moda-interact/v1/merchant/bootstrap
        |
        v
PHP ModaApiClient + WOO-003 installation credential
        |
        | X-Moda-Installation-Id + Bearer credential
        v
GET /v1/merchant/bootstrap
        |
        v
API-003 authenticated merchant bootstrap read model
        |
        v
commerce.Shop + CommerceShopProfile
        |
        v
browser-safe Overview presentation
```

The overview must present real shared merchant state including the one-time onboarding milestone, bounded Store Category selection state and provider-neutral international context.

This task is read-only with respect to merchant business state. It MUST NOT complete onboarding, select/change Store Category, activate a plan, alter billing, create ShopSettings, or introduce placeholder feature pages.

## Context

WOO-003 owns the PHP/server-side installation credential and the authenticated Moda API client. Browser JavaScript never receives the remote credential.

WOO-004 owns the `/moda-interact` WooCommerce Admin shell and the browser-safe connection lifecycle. It intentionally exposes no fake merchant-data screens before a real backend capability exists.

API-003 owns the accepted hosted read contract:

```text
GET /v1/merchant/bootstrap
```

and returns the bounded logical model:

```text
schemaVersion
shop
    id
    platform = WOOCOMMERCE
    domain
    onboardingCompleted
    installedAt
internationalContext
    storeLocale
    languageTag
    timeZone
    countryCode
storeProfile
    activeCategory
    pendingCategory
    pendingSelectionGeneration
    pendingSelectedAt
```

API-003 is authenticated by API-002 and derives the Shop from the installation principal. It does not accept caller-supplied tenant identity.

ARCH-026 internationalization is first-class. The Woo application MUST accept/preserve provider-native WordPress/WooCommerce locale identity without a fixed Moda Woo locale allowlist. The administrator UI locale used to translate/render the WordPress Admin application is separate from the merchant/store international context returned by API-003.

`shop.onboardingCompleted` is the provider-neutral one-time milestone. A connected Woo installation with `onboardingCompleted = false` is valid and must not be treated as disconnected or billing-invalid.

## Scope

Modify only `moda-interact-woocommerce` files required to:

1. extend the existing WOO-003 PHP client with the accepted API-003 bootstrap read;
2. expose one privileged local WordPress REST read route to browser JavaScript; and
3. render the first real Overview/Setup-state presentation inside the WOO-004 Admin shell.

Expected implementation areas are conceptually:

```text
includes/
  Api/
    ModaApiClient.php
  Rest/
    MerchantBootstrapController.php

src/
  admin/
    api/
      wordpress-client.ts
    overview/
      merchant-bootstrap.ts
      use-merchant-bootstrap.ts
      overview-screen.tsx
      onboarding-status-card.tsx
      store-profile-card.tsx
      international-context-card.tsx

tests/
  php/
  javascript/
```

Exact filenames may follow the accepted WOO-003/WOO-004 repository layout when clearer.

### Connection gate

Merchant bootstrap data may be loaded only when the accepted WOO-004 connection state is:

```text
CONNECTED
```

Do not call the merchant bootstrap route while connection state is:

```text
DISCONNECTED
RECONNECT_REQUIRED
SITE_URL_CHANGED
REMOTE_UNAVAILABLE
API_NOT_CONFIGURED
LOCAL_STATE_INVALID
```

WOO-004 remains the owner of connection presentation/actions.

A successful connection does not imply onboarding completion, plan activation or billing entitlement.

### Remote PHP client call

Extend the accepted WOO-003 `ModaApiClient` (or equivalent) with a bounded read operation for:

```text
GET /v1/merchant/bootstrap
```

The PHP client MUST reuse the stored WOO-003 installation identity and credential and send only the accepted remote authentication:

```text
X-Moda-Installation-Id: <installationId>
Authorization: Bearer <raw installation credential>
```

Do not send locally stored `shopId`, domain, locale or another browser/provider value as tenant authority.

Retain the WOO-003 transport invariants:

- HTTPS-only production API origin;
- TLS verification enabled;
- redirects disabled;
- bounded timeout and response size;
- no cookies;
- strict JSON/media-type/schema validation;
- no credential, Authorization-header or complete-body logging.

Consume API-003's accepted OpenAPI/runtime contract. Do not invent a structurally different merchant bootstrap model in PHP.

### Local browser REST route

Expose exactly one new privileged local route:

```text
GET /wp-json/moda-interact/v1/merchant/bootstrap
```

The route requires:

```text
current_user_can('manage_woocommerce')
```

and normal authenticated WordPress REST cookie/nonce semantics.

The local route must:

1. verify the local WOO-003 connection record is structurally valid;
2. re-run the WOO-003 current-site URL/clone guard before using the credential;
3. call the API-003 remote bootstrap route through the server-side client;
4. validate the remote response strictly; and
5. return only the accepted browser-safe merchant bootstrap fields.

The browser cannot supply:

```text
shopId
installationId
siteUrl
Moda API origin
locale override
platform
```

The route is read-only and MUST perform no local WordPress business mutation.

Use private/no-store response semantics appropriate for authenticated merchant data.

### Local error mapping

Do not relay arbitrary hosted-API response bodies into WordPress REST errors or React.

Map failures to bounded local outcome codes sufficient for the UI, at minimum conceptually:

```text
RECONNECT_REQUIRED
SITE_URL_CHANGED
REMOTE_UNAVAILABLE
REMOTE_RESPONSE_INVALID
MERCHANT_BOOTSTRAP_UNAVAILABLE
```

A remote authentication rejection maps to `RECONNECT_REQUIRED` and should cause the UI to return attention to the WOO-004 connection experience rather than silently retrying with the rejected credential.

A network/provider outage maps to `REMOTE_UNAVAILABLE`; it does not mean the installation has become disconnected.

### Browser bootstrap model

Use an explicit discriminated browser state rather than scattering nullable/raw response handling through components.

At minimum represent:

```text
IDLE
LOADING
READY
RECONNECT_REQUIRED
REMOTE_UNAVAILABLE
LOAD_FAILED
```

`READY` contains the accepted API-003 model only after runtime validation.

Unknown schema versions, malformed categories or malformed international-context values fail closed into a bounded load error and are not silently normalized.

### First real Overview screen

When the connection state is `CONNECTED`, the WOO-004 shell may now expose one real merchant destination/content section:

```text
Overview
```

Do not expose additional future pages merely to reserve navigation labels.

The Overview MUST use real API-003 data and contain three bounded areas.

#### Account setup state

Present the shared:

```text
shop.onboardingCompleted
```

as a merchant-readable setup milestone, for example:

```text
false -> Setup not completed
true  -> Setup completed
```

Do not:

- infer onboarding state from installation connection;
- read/create `shopify.ShopSettings`;
- expose a "Complete onboarding" command in this task;
- create or display a stored `ACCOUNT_PENDING_ACTIVATION` state;
- infer billing/plan state.

The display may explain that setup functionality will become available through later real capabilities, but it MUST NOT present an enabled placeholder action that does nothing.

#### Store profile state

Display only the bounded category identity supplied by API-003:

```text
activeCategory
pendingCategory
pendingSelectionGeneration
pendingSelectedAt
```

When no category exists, display a truthful empty state such as:

```text
Store category: Not selected
```

Do not add a category picker or mutate selection in this task.

Do not expose prompt text, revision IDs, taxonomy mappings or Admin-only metadata.

If both active and pending category state exist, present them distinctly; do not collapse pending selection into active configuration.

#### International context

Present the provider-neutral store context supplied by API-003:

```text
storeLocale
languageTag
timeZone
countryCode
```

Rules:

- `storeLocale` is provider-native identity and must be displayed/preserved as returned;
- `languageTag` is a separate normalized Moda value and may be null;
- null language tag MUST NOT cause the UI to substitute/persist English;
- null international-context fields are valid and should display a truthful unavailable/not-yet-synchronized state;
- do not maintain or consult a fixed Woo locale allowlist;
- do not infer `storeLocale` from `languageTag` or vice versa;
- no valid returned provider locale may be rejected merely because Moda lacks a translation catalogue for it.

Merchant-visible labels follow the current WordPress administrator UI locale through WordPress i18n. They do not switch to `storeLocale` merely because the merchant store uses another locale.

### Locale-aware UI implementation

All new PHP and React merchant-visible strings MUST use the existing WordPress/WooCommerce localization machinery and the `moda-interact` text domain.

React should use the repository's accepted WordPress i18n packages rather than a new locale framework.

Where a date/time is rendered, use the accepted WordPress/Woo date-formatting facilities/current administrator locale rather than a hard-coded US/UK date pattern. Do not parse the returned IANA store timezone as the administrator display timezone unless the UI explicitly labels it as store context.

### Refresh and race safety

Provide a bounded explicit refresh/retry action for the Overview bootstrap read.

Requirements:

- no overlapping bootstrap GETs;
- stale/aborted results cannot overwrite a newer load;
- a late bootstrap result cannot overwrite a newer connection-state transition from WOO-004;
- connection leaving `CONNECTED` invalidates/hides merchant bootstrap presentation;
- no background polling is required.

Refresh is a read-only action; it must not reconnect, rotate credentials or mutate account state.

### Sensitive-data boundary

Browser-visible state may contain the API-003 merchant bootstrap fields only.

It MUST NOT contain:

- raw installation credential;
- Authorization header;
- credential digest;
- bootstrap secret;
- Shopify access/session data;
- billing/subscription rows;
- customer/recovery/conversation payloads;
- prompt content.

Do not place bootstrap response data into `localStorage` or `sessionStorage`. Keep it in bounded in-memory React state and reload it from the authenticated local route when needed.

### No duplicate merchant domain logic

The plugin is a presentation/client boundary.

Do not reproduce Moda lifecycle/business decisions in PHP or React beyond presentation of API-003's accepted fields. In particular, do not implement independent rules for onboarding completion, category activation, normalized locale selection or Shop status.

## Out of Scope

- Completing onboarding.
- A provider-neutral onboarding command/API.
- Creating/storing `ACCOUNT_PENDING_ACTIVATION`.
- Store Category selection/change/activation.
- International-context synchronization/write commands.
- Woo hooks that populate store locale/timezone/country in Moda.
- Billing/subscriptions/pricing-plan selection.
- Recovery list/configuration.
- Usage reporting.
- Merchant Knowledge.
- Promotions.
- Products/coupons/discounts.
- CommerceAgent configuration.
- WhatsApp.
- Cart/checkout/order event ingress.
- Redis/BullMQ/Background.
- Site/domain migration.
- Installation revocation/uninstall workflow.
- Direct browser calls to `moda-interact-api`.
- Additional future merchant pages/navigation placeholders.
- A new frontend router/data-fetching/state-management framework.
- A Woo-specific locale allowlist.

## Requirements

### R1 — Real merchant data only

The Overview is backed by API-003/PostgreSQL state and does not use fabricated/demo merchant values.

### R2 — PHP remains the remote credential boundary

React calls only the local WordPress REST route. The long-lived Moda installation credential never enters browser state.

### R3 — Tenant identity remains server-resolved

Neither React nor PHP sends a caller-selected `shopId` or domain as tenant authority to API-003.

### R4 — Connection gates merchant-data loading

The bootstrap read executes only while WOO-004 has an accepted `CONNECTED` connection state.

### R5 — Shared onboarding milestone is presentation-only here

WOO-005 reads/displays `Shop.onboardingCompleted` but cannot change it or infer it from connection/billing state.

### R6 — Internationalization is open-ended

No Woo locale allowlist is introduced. Provider-native locale identity is accepted/preserved independently from Moda translation coverage and normalized language-tag availability.

### R7 — Administrator UI locale and store locale remain separate

WordPress Admin controls UI translation/formatting; API-003 store international context is displayed as merchant/store data and does not implicitly switch the UI locale.

### R8 — Store profile remains read-only

Active/pending category state is displayed exactly as projected by API-003 and no category mutation is introduced.

### R9 — Remote outage is not account-state mutation

Failure to load bootstrap data cannot change connection, onboarding, category, locale, billing or credential state.

### R10 — Stale reads cannot overwrite newer state

Bootstrap loading/refresh must be single-flight or cancellation-safe and cannot overwrite a newer connection transition.

### R11 — Browser persistence remains secret/data-minimal

Merchant bootstrap state is not copied into browser persistent storage and no credential/provider-secret material is exposed.

### R12 — No placeholder capability expansion

Overview is the only new merchant-data surface. Future capabilities remain absent until implemented by their owning tasks.

## Work Items

- [ ] Extend the WOO-003 PHP Moda API client with the accepted API-003 `GET /v1/merchant/bootstrap` read.
- [ ] Add strict PHP-side validation/mapping for the accepted API-003 response and bounded remote errors.
- [ ] Add privileged `GET /wp-json/moda-interact/v1/merchant/bootstrap` local REST route.
- [ ] Reuse WOO-003 connection-store, site-URL guard and credential handling rather than duplicating authentication code.
- [ ] Add private/no-store response behavior and browser-safe bounded error codes.
- [ ] Add the typed/discriminated React merchant-bootstrap state/client/controller.
- [ ] Gate bootstrap loading on WOO-004 `CONNECTED` state.
- [ ] Implement the first real Overview content in the accepted WOO-004 shell/page composition boundary.
- [ ] Render shared onboarding completion truthfully without adding an onboarding mutation.
- [ ] Render active/pending Store Category identity and truthful empty state without a selector.
- [ ] Render store locale, normalized language tag, time zone and country independently, including nullable values.
- [ ] Use WordPress i18n for all new PHP/React strings and locale-aware date formatting where dates are shown.
- [ ] Add explicit read-only refresh/retry with stale-response/single-flight protection.
- [ ] Ensure leaving `CONNECTED` clears/hides previously loaded merchant bootstrap presentation.
- [ ] Add focused PHP REST/client and React controller/presentation tests.
- [ ] Verify no credential or merchant bootstrap payload is persisted to browser storage/logs.
- [ ] Document the read-only Overview boundary and intentional lack of onboarding/category/international-context mutations.

## Interfaces / Contracts

### Hosted contract owner

`ARCH-026-API-003`

### Hosted API consumed by PHP

```text
GET /v1/merchant/bootstrap
```

Authentication remains owned by API-002/WOO-003:

```text
X-Moda-Installation-Id: <installationId>
Authorization: Bearer <raw installation credential>
```

### Local browser API owner

`ARCH-026-WOOCOMMERCE-005`

### Local browser route

```text
GET /wp-json/moda-interact/v1/merchant/bootstrap
```

Authorization:

```text
WordPress authenticated administrator
+
current_user_can('manage_woocommerce')
+
normal REST nonce/cookie semantics
```

### Browser-safe success model

The local route exposes the accepted API-003 model only:

```text
schemaVersion
shop
internationalContext
storeProfile
```

It does not expose remote authentication material.

### UI host

`ARCH-026-WOOCOMMERCE-004`

Canonical Woo Admin page:

```text
/moda-interact
```

WOO-005 adds `Overview` as the first real merchant-data content within that accepted shell.

## Dependencies

- `ARCH-026-WOOCOMMERCE-004`
- `ARCH-026-API-003`

Both tasks must be architect-accepted `complete` before WOO-005 becomes Ready.

WOO-005 consumes the accepted WOO-004 application-shell/connection state and API-003 remote merchant-bootstrap contract; it must not execute against in-review drafts.

## Enables

None currently.

Later ARCH-026 packaging/deployment/system-test tasks may depend on WOO-005 after those tasks are explicitly defined.

## Acceptance Criteria

- [ ] Merchant bootstrap is requested only while the accepted WOO-004 connection state is `CONNECTED`.
- [ ] Browser JavaScript calls only the local WordPress merchant-bootstrap route, never `moda-interact-api` directly.
- [ ] The local WordPress route requires `manage_woocommerce` and valid WordPress REST authentication/nonce semantics.
- [ ] PHP reuses the WOO-003 stored installation credential/site guard rather than creating another credential store/authenticator.
- [ ] Remote API-003 calls contain no locally asserted `shopId`/domain tenant authority.
- [ ] The local route returns only the accepted API-003 browser-safe bootstrap fields and bounded error codes.
- [ ] The Overview displays real `Shop.onboardingCompleted` state and never infers it from connection/billing state.
- [ ] The Overview cannot complete onboarding or create a stored pending-activation state.
- [ ] Missing Store Category state renders a truthful empty state and performs zero mutation.
- [ ] Active and pending categories are distinguished when both exist.
- [ ] No Store Category picker/mutation is introduced.
- [ ] `storeLocale`, `languageTag`, `timeZone` and `countryCode` are presented independently from API-003 state.
- [ ] A valid provider-native locale is not rejected because it is absent from a Moda translation catalogue/allowlist.
- [ ] Null normalized language tag does not cause the UI/API client to manufacture or persist English.
- [ ] WordPress administrator locale controls UI translations; returned store locale does not implicitly switch the UI language.
- [ ] New PHP/React merchant-visible strings use WordPress/WooCommerce localization with text domain `moda-interact`.
- [ ] Refresh is read-only, non-overlapping and stale-response safe.
- [ ] Leaving `CONNECTED` prevents stale merchant data from remaining presented as current.
- [ ] Remote authentication rejection is surfaced as connection attention/reconnect-required and does not expose arbitrary remote error bodies.
- [ ] Remote outage does not mark the installation disconnected or mutate merchant state.
- [ ] No raw installation credential, Authorization header, credential digest, bootstrap secret, Shopify session/access token or customer/recovery payload reaches React/browser storage/logs.
- [ ] No additional unimplemented merchant page is exposed as navigable UI.
- [ ] No billing, recovery, Merchant Knowledge, promotions, products/discounts, event-ingress or Background functionality is introduced.

## Validation

Run the Woo repository's declared validation commands and record exact commands/results.

Required validation categories:

- [ ] required `scripts/bootstrap-woocommerce.sh` succeeds before repository validation;
- [ ] clean npm/Composer dependency installation from lockfiles as required by the repository foundation;
- [ ] PHP lint/code-standard/static checks;
- [ ] JavaScript lint/typecheck/tests/build according to repository scripts;
- [ ] PHP remote-client fixture test for valid API-003 merchant bootstrap response;
- [ ] PHP test proving API-003 request sends installation authentication but no local `shopId`/domain tenant-selection input;
- [ ] PHP strict-response tests for malformed/unknown schema version/oversized/non-JSON remote bootstrap responses;
- [ ] WordPress REST authorization/nonce test for the local merchant-bootstrap route;
- [ ] site-URL mismatch test proving the stored credential is not used;
- [ ] remote authentication rejection -> bounded `RECONNECT_REQUIRED` mapping test;
- [ ] remote network/provider failure -> bounded `REMOTE_UNAVAILABLE` mapping test;
- [ ] no-store/private-response test;
- [ ] React test proving bootstrap is not requested unless connection state is `CONNECTED`;
- [ ] React/controller stale GET/single-flight/connection-transition race tests;
- [ ] onboarding false/true Overview presentation tests;
- [ ] no-profile, active-category and active+pending-category presentation tests;
- [ ] international-context tests covering WordPress locale identity such as `pt_BR`, normalized tag such as `pt-BR`, nullable language tag, time zone and country;
- [ ] test with a bounded provider-native locale outside any existing Moda fixed translation catalogue proving it renders rather than being rejected;
- [ ] administrator UI locale test proving labels use WordPress i18n rather than store locale switching;
- [ ] browser-state/storage/log capture proving installation credentials and sensitive remote headers never appear;
- [ ] browser/DOM smoke in the accepted local WordPress/WooCommerce environment showing real fixture-backed Overview content through the PHP local route;
- [ ] production asset build/plugin smoke remains successful;
- [ ] `git diff --check`;
- [ ] clean task-worktree/branch evidence required by the task protocol.

Do not satisfy the PHP/UI integration only with direct React fixtures. At least one WordPress REST integration/browser smoke must exercise:

```text
React
  -> local WordPress REST
  -> PHP ModaApiClient
  -> controlled HTTPS API-003 fixture
  -> browser-safe Overview
```

A deployed public Moda API is not required for this repository task; Gateway/system validation owns deployed end-to-end verification.

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

Do not begin packaging, Gateway or system-test work.

## Implementation Notes

Keep the screen small. WOO-005 establishes the first authenticated merchant-data presentation; it is not permission to clone the Shopify merchant application wholesale.

Reuse WOO-003's server-side client/credential store and WOO-004's shell/request-concurrency patterns. Do not introduce a second remote API client or parallel connection state.

Internationalization support is structural, not a fixed translation matrix. A locale may be valid merchant/store identity even when Moda does not yet ship a translation for all of its strings.

Do not implement Store Category mutation locally. API-003 deliberately exposed category state read-only because the existing mutation has non-trivial lifecycle semantics and must be generalized separately rather than duplicated in Woo.

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

- WOO-004 provides the accepted React Admin shell and browser-safe connection state/controller.
- API-003 provides the accepted authenticated, read-only merchant bootstrap contract including shared international context.
- WOO-003 remains the sole owner of the locally stored long-lived installation credential and remote authentication transport.
- No merchant-data mutation beyond already-accepted Connect/Reconnect is required for this first Overview task.

### Unresolved Issues

- Completing onboarding and Store Category mutation remain intentionally undefined follow-on capabilities.

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
