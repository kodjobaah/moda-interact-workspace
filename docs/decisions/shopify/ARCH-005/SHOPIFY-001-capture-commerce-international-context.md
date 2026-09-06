---
id: ARCH-005-SHOPIFY-001
architecture_id: ARCH-005
title: Initialise Shopify merchant international defaults
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-005-SHARED-002
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-06
---

# Initialise Shopify merchant international defaults

## Architecture

ARCH-005 separates merchant/shop defaults from buyer/checkout context.

This task owns only the merchant-default lifecycle at the authenticated Shopify
shop-resolution boundary. Buyer-specific checkout/order context is handled by
SHOPIFY-003 after the shared consumer contract is ready.

Current source inspection established:

```text
app/services/shop/shop.service.ts
```

already performs an authenticated Admin GraphQL `shop` query and lazily upserts
the Moda `Shop` on authenticated app access. It does not currently create or
populate `ShopSettings`.

Current application routes subsequently read `ShopSettings`, so a new tenant can
exist with a `Shop` row but no `ShopSettings` row.

This existing authenticated boundary is the approved place to initialise
merchant international defaults. Do not add Shopify API calls to webhook hot
paths for these defaults.

## Objective

Create missing `ShopSettings` idempotently when a Shopify shop is resolved and
initialise standards-based merchant fallback language, timezone and country from
authoritative Shopify store configuration without overwriting later merchant
configuration.

## Context

DATABASE-001 added:

```text
ShopSettings.defaultLanguageTag
ShopSettings.defaultTimeZone
ShopSettings.defaultCountryCode
```

SHARED-002 published canonical validation helpers in:

```text
@modainteract/moda-interact-shared@0.6.1
```

The supplied Shopify repository is currently on an older database submodule
revision and shared dependency. Before implementation, adopt the already
accepted/published revisions rather than copying schema or validation locally.

Development-stage rollout context:

```text
Moda Interact is not yet in production.
```

There is no installed production merchant population requiring compatibility
machinery for the previous OAuth scope set. Development stores may be
re-authorised/reinstalled as needed.

## Scope

Primary files to inspect/change:

```text
moda-interact/shopify.app.moda-interact.toml
moda-interact/app/services/shop/shop.service.ts
moda-interact/package.json
moda-interact/package-lock.json
moda-interact/database                 # submodule pointer only, after DB publication
focused ShopService tests/new test file as appropriate
```

Inspect current configuration selection before changing any other Shopify TOML.
Do not update generated `.shopify/*bundle*` artifacts manually.

## Out of Scope

- Buyer/checkout/order event context emission.
- Changes to shared queue-event schemas.
- Background recovery materialisation.
- Persisting a local copy of all Shopify Markets.
- Per-webhook Admin API lookups.
- Using `Session.locale` as the shop's primary locale.
- Inferring language from shop country/currency.
- Inferring a recovery currency from shop currency.
- Merchant UI translation work; SHOPIFY-002 owns that.

## Requirements

### 1. Required Shopify scopes

Update the active Moda Shopify app configuration to include:

```text
read_locales
read_markets
```

alongside the existing required scopes.

`read_locales` is required because the primary `ShopLocale` is the authoritative
shop/store fallback locale.

`read_markets` establishes the read-only Shopify Markets permission boundary for
ARCH-005 while the app is still pre-production. This task must NOT build or
persist a complete market catalogue merely because the scope exists.

Do not request write-locales or write-markets scopes.

### 2. Shop configuration query

Extend the existing authenticated shop-resolution query to retrieve the minimum
merchant-default data:

```text
shop.id / existing shopifyShopId alias
shop.myshopifyDomain
shop.ianaTimezone
shop.shopAddress.countryCodeV2
shopLocales.locale
shopLocales.primary
shopLocales.published
```

Select exactly the locale whose `primary == true` as the shop fallback language.

Do not use:

```text
Session.locale
shop currency
country -> language mapping
market currency -> language mapping
```

as `defaultLanguageTag`.

#### Attempt 3 GraphQL shape correction

`shopLocales` is a Shopify Admin GraphQL **QueryRoot** field in API `2026-07`;
it is not a field on the `Shop` object. Keep this as one authenticated Admin
GraphQL request, but query `shop` and `shopLocales` as sibling top-level
selections:

```graphql
query ResolveModaInteractShop {
  shop {
    shopifyShopId: id
    myshopifyDomain
    ianaTimezone
    shopAddress {
      countryCodeV2
    }
  }
  shopLocales {
    locale
    primary
    published
  }
}
```

The response typing and lookup must therefore read locales from:

```text
result.data.shopLocales
```

not from:

```text
result.data.shop.shopLocales
```

Do not split this into a second Shopify request. Do not change the already
approved merchant-default semantics while making this correction.

### 3. Canonical validation

Use the accepted shared helpers to canonicalise/validate:

```text
primary ShopLocale -> defaultLanguageTag
shop.ianaTimezone -> defaultTimeZone
shop.shopAddress.countryCodeV2 -> defaultCountryCode
```

If Shopify returns missing/invalid optional data, preserve null rather than
inventing a value.

### 4. Idempotent ShopSettings initialisation

After resolving/upserting the `Shop`, ensure a `ShopSettings` row exists.

Creation must be safe under repeated/concurrent authenticated app requests.

On first creation, initialise:

```text
defaultLanguageTag
defaultTimeZone
defaultCountryCode
```

and retain existing database defaults such as:

```text
onboardingCompleted = false
recoveryDelayMinutes = existing schema default
```

On later `resolveShopifyShop()` calls, existing merchant settings MUST NOT be
silently overwritten.

The desired lifecycle is:

```text
Shop resolved/created
    -> ShopSettings exists
    -> first-time defaults are seeded from Shopify
    -> later merchant edits remain authoritative
```

### 5. Repository dependency adoption

Adopt:

```text
@modainteract/moda-interact-shared@0.6.1
```

and the committed database submodule revision containing accepted
DATABASE-001 fields.

If the DATABASE-001 revision has not yet been committed/pushed and therefore
cannot be adopted through the submodule, do not copy the schema into
`moda-interact`; stop and report that publication dependency to the architect.

## Work Items

- [x] Verify the active Shopify app config file and add `read_locales,read_markets` read scopes.
- [x] Adopt the published shared internationalization helpers without local validator duplication.
- [x] Verify the accepted DATABASE-001 submodule revision is already adopted.
- [x] Extend `resolveShopifyShop()` merchant configuration query.
- [x] Canonicalise Shopify merchant defaults using shared helpers.
- [x] Create missing `ShopSettings` idempotently.
- [x] Preserve existing `ShopSettings` values on subsequent resolutions.
- [x] Add focused tests for first creation and repeated resolution.
- [x] Add a regression proving `Session.locale` is not used as merchant default language.
- [x] Add a regression proving shop currency does not become recovery/customer currency.
- [x] Correct `shopLocales` to a QueryRoot sibling of `shop` and update response typing/lookup.
- [x] Add a regression that structurally proves `shopLocales` is not nested inside `shop`.

## Interfaces / Contracts

Shopify provider inputs:

```text
Shop.ianaTimezone
Shop.shopAddress.countryCodeV2
ShopLocale.locale where primary == true
```

Moda persisted outputs:

```text
ShopSettings.defaultLanguageTag
ShopSettings.defaultTimeZone
ShopSettings.defaultCountryCode
```

The relationship is merchant fallback only. It is not customer identity.

## Dependencies

- ARCH-005-SHARED-002 — Complete, published as `0.6.1`.
- ARCH-005-DATABASE-001 — Complete; consuming submodule revision must be published by the developer before adoption.

## Enables

- Provides merchant fallback state used by later runtime/system validation.
- Contributes to ARCH-005-SYSTEM-TEST-001 readiness, but does not directly
  unblock buyer event emission.

## Acceptance Criteria

- [x] active Shopify app config includes `read_locales` and `read_markets` as required read scopes.
- [x] no write-locales/write-markets scope is added.
- [x] `ShopSettings` is created for a resolved shop when missing.
- [x] primary `ShopLocale` seeds `defaultLanguageTag`.
- [x] Shopify IANA timezone seeds `defaultTimeZone`.
- [x] Shopify shop-address country seeds `defaultCountryCode`.
- [x] invalid/missing optional provider values remain null.
- [x] existing merchant settings are not overwritten on repeat resolution.
- [x] `Session.locale` cannot seed `defaultLanguageTag`.
- [x] shop currency cannot seed a checkout/recovery currency.
- [x] no per-webhook Shopify API lookup is introduced.
- [x] existing Shop identity/domain checks remain intact.
- [x] `shopLocales` is queried as a top-level QueryRoot field, sibling to `shop`.
- [x] locale selection reads `result.data.shopLocales`, not a nested `Shop.shopLocales` value.
- [x] focused query-shape coverage would fail if `shopLocales` were moved back under `shop`.
- [x] focused/full tests, build, Prisma validation, focused lint and diff checks pass; repository-wide typecheck/lint baseline failures are documented below.

## Validation

At minimum validate:

```text
new shop + no settings
    -> Shop created/resolved
    -> ShopSettings created with canonical locale/timezone/country

existing ShopSettings with merchant-edited values
    -> resolveShopifyShop() again
    -> merchant values unchanged

no primary locale / invalid optional source
    -> corresponding default remains null

Admin GraphQL request
    -> QueryRoot contains sibling `shop` and `shopLocales` selections
    -> `shop` selection does NOT contain `shopLocales`
```

Run repository-standard implementation validation including focused tests,
full tests, typecheck, lint/build where configured, Prisma generation against
the adopted database submodule and `git diff --check`.

## Implementation Notes

Do not query all Markets or persist market rows in this task. `read_markets` is
part of the pre-production permission boundary for the broader ARCH-005 Shopify
Markets objective; actual buyer language/country/currency remains field-specific
and is handled independently.

## Completion Report

### Status

In Progress

### Attempt 1 Findings

The first execution correctly identified that the previous task mixed two
capabilities:

```text
merchant ShopSettings initialisation
buyer-specific event context propagation
```

It also identified that the repository's database submodule predates
DATABASE-001 and that the strict shared Shopify event schema cannot accept new
buyer context without shared-contract coordination.

The architect has therefore narrowed this canonical task to merchant-default
initialisation and created separate cross-repository tasks for buyer event
context.

### Attempt 2 Files Changed

- `app/services/shop/shop.service.ts`
- `shopify.app.moda-interact.toml`
- `tests/unit/services/shop.service.test.ts`

### Attempt 2 Work Completed

- Extended the authenticated shop query with primary locale, IANA timezone and
  shop-address country fields.
- Canonicalized optional provider values using the published shared helpers,
  preserving null for missing or invalid values.
- Added idempotent `ShopSettings` creation with `update: {}` so merchant edits
  remain authoritative on repeat shop resolution.
- Added read-only `read_locales` and `read_markets` scopes without write scopes.
- Added focused regressions for initial creation, repeat preservation, invalid
  values, session-locale independence and currency independence.

### Attempt 2 Validation Results

- Focused ShopService tests: 3 passed.
- Full test suite: 107 passed, 1 skipped.
- Focused ESLint for changed implementation and test: passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- Repository-wide `npm run typecheck` remains blocked by existing baseline errors
  in unrelated JSX/module-resolution files; no changed ShopService error was
  reported.
- Repository-wide `npm run lint` retains existing unrelated errors in onboarding,
  billing, privacy and webhook telemetry files; the task-local test lint error
  was fixed and the changed files lint cleanly.

### Attempt 2 Deviations

The repository already consumed published shared `0.6.2`, which includes the
required `0.6.1` internationalization helpers, so no downgrade was made. The
DATABASE-001 submodule revision was already adopted at `61337e1`; no pointer
change was necessary.

### Attempt 2 Unresolved Issues

Repository-wide typecheck and lint baseline failures remain outside this task's
changed files.

## Attempt 3 Completion Report

### Status

Ready for Review

### Files Changed

- `app/services/shop/shop.service.ts`
- `tests/unit/services/shop.service.test.ts`

The Attempt 2 scope/configuration changes remain preserved.

### Work Completed

- Moved `shopLocales` from the `Shop` selection to the top-level Admin GraphQL
  QueryRoot selection beside `shop`.
- Updated the response type and primary-locale lookup to use
  `result.data.shopLocales`.
- Added structural focused coverage proving the query closes the `shop` object
  before selecting top-level `shopLocales`.

### Validation Results

- Shopify Admin GraphQL `2026-07` validation: passed; required scopes reported
  as `read_locales, read_markets_home`.
- Focused ShopService tests: 3 passed.
- Full test suite: 107 passed, 1 skipped.
- Focused ESLint for changed implementation and test: passed, with the existing
  TypeScript-version support warning.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: remains blocked by existing unrelated JSX implicit-any
  and module-resolution baseline errors; no changed ShopService error was
  reported.

### Deviations

None.

### Assumptions

The existing Attempt 2 scope/configuration and merchant-default implementation
are retained unchanged; Attempt 3 is limited to the architect-requested
GraphQL query-shape correction.

### Unresolved Issues

Repository-wide typecheck baseline failures remain outside this task's changed
files.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested — Attempt 1 scope correction

### Review Notes

The agent's blocker was valid, but it applied only to the buyer-event portion of
the original task. Merchant defaults do not require a queue-contract change.

The task is returned to `ready` with Attempt 1 preserved. On the next claim the
executor should increment the attempt and implement only the bounded merchant
initialisation capability described above.

Do not start SHOPIFY-003 from this task. Return this task to `review` and STOP.
No commit or push.

### Attempt 2 Review

**Review Status:** Changes Requested — GraphQL query-shape correction

The merchant-default lifecycle, canonical normalization, scope additions and
`ShopSettings.upsert({ update: {} })` preservation behaviour are acceptable.

However, the implementation queried:

```graphql
shop {
  ...
  shopLocales { ... }
}
```

Shopify Admin GraphQL API `2026-07` exposes `shopLocales` on QueryRoot, not on
`Shop`. The current focused tests mirror the invalid nested mock response and
therefore do not catch the provider-runtime failure.

Attempt 3 is intentionally narrow:

1. move `shopLocales` to a sibling top-level selection beside `shop`;
2. update `ShopifyShopResponse` so `shopLocales` is under `data`;
3. resolve the primary locale from `result.data?.shopLocales`;
4. add structural regression coverage for the real query shape;
5. leave scopes, normalization, `ShopSettings` persistence, buyer-event logic
   and unrelated code unchanged.

Return this same task to `review` after validation and STOP. No commit or push.

### Attempt 3 Review

**Review Status:** Accepted — Complete

The Attempt 3 correction is accepted. The authenticated Shopify Admin GraphQL
request now selects `shop` and `shopLocales` as sibling QueryRoot fields, and
primary-locale selection reads `result.data.shopLocales`. This matches Shopify
Admin GraphQL API `2026-07`.

The previously accepted merchant-default lifecycle remains intact:

- `ShopSettings` is created idempotently when missing;
- `upsert({ update: {} })` preserves later merchant edits;
- primary shop locale, IANA timezone and shop-address country are independently
  canonicalised and persisted as merchant fallback values;
- missing or invalid optional provider values remain null;
- no Session-locale, country-to-language, currency-to-language or shop-currency
  inference is introduced;
- `read_locales` and `read_markets` remain configured without write scopes;
- no Shopify Admin API lookup was added to webhook hot paths.

The focused structural regression would fail if `shopLocales` were nested under
`shop` again. Reported validation passed for Shopify API `2026-07` schema
validation, focused/full tests, focused lint, build, Prisma validation and
`git diff --check`. Repository-wide typecheck/lint baseline failures remain
unrelated to this task.

`ARCH-005-SHOPIFY-001` is Complete. `ARCH-005-SHOPIFY-002` remains Ready and is
the next Shopify implementation task. `ARCH-005-SYSTEM-TEST-001` remains
Pending until its remaining implementation dependencies are complete.

