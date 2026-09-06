---
id: ARCH-005-SHOPIFY-001
architecture_id: ARCH-005
title: Initialise Shopify merchant international defaults
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-005-SHARED-002
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-05T21:27:16Z
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

- [ ] Verify the active Shopify app config file and add `read_locales,read_markets` read scopes.
- [ ] Adopt shared `0.6.1` without local validator duplication.
- [ ] Update the database submodule pointer to the accepted DATABASE-001 revision when available.
- [ ] Extend `resolveShopifyShop()` merchant configuration query.
- [ ] Canonicalise Shopify merchant defaults using shared helpers.
- [ ] Create missing `ShopSettings` idempotently.
- [ ] Preserve existing `ShopSettings` values on subsequent resolutions.
- [ ] Add focused tests for first creation and repeated resolution.
- [ ] Add a regression proving `Session.locale` is not used as merchant default language.
- [ ] Add a regression proving shop currency does not become recovery/customer currency.

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

- [ ] active Shopify app config includes `read_locales` and `read_markets` as required read scopes.
- [ ] no write-locales/write-markets scope is added.
- [ ] `ShopSettings` is created for a resolved shop when missing.
- [ ] primary `ShopLocale` seeds `defaultLanguageTag`.
- [ ] Shopify IANA timezone seeds `defaultTimeZone`.
- [ ] Shopify shop-address country seeds `defaultCountryCode`.
- [ ] invalid/missing optional provider values remain null.
- [ ] existing merchant settings are not overwritten on repeat resolution.
- [ ] `Session.locale` cannot seed `defaultLanguageTag`.
- [ ] shop currency cannot seed a checkout/recovery currency.
- [ ] no per-webhook Shopify API lookup is introduced.
- [ ] existing Shop identity/domain checks remain intact.
- [ ] focused/full tests, typecheck, lint, build and diff checks pass subject to baseline.

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

Attempt 1 returned blocked before implementation. No Shopify runtime source was
changed.

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
