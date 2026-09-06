# ARCH-005 Amendment — Shared ICU MessageFormat Runtime

Date: 2026-09-06

## Decision

ARCH-005 merchant/admin UI internationalisation will use one reusable ICU
MessageFormat runtime owned by `moda-interact-shared`.

Application-specific UI message catalogues remain owned by each application.
The shared package owns the internationalisation engine and standards-aware
formatting primitives; it does **not** own Shopify/Admin product copy.

```text
@modainteract/moda-interact-shared/internationalization
    |
    +-- BCP-47 canonicalisation / validation
    +-- ICU MessageFormat compilation + formatting
    +-- locale-aware number/date/time/percentage helpers
    +-- explicit-currency money formatting
    +-- text-direction resolution
    +-- catalogue/key validation primitives
    +-- Node/browser-safe caching
            |
            +------------------------------+
            |                              |
            v                              v
moda-interact                       moda-interact-admin
merchant UI                         platform-admin UI
app-owned catalogues                app-owned catalogues
app/i18n/locales/*.json             src/i18n/locales/*.json
```

## Why

The existing SHOPIFY-002 implementation started recreating ICU features locally:
custom plural selection, executable message functions, direction resolution,
number/date formatting and a large in-source translation object. That is not the
long-term platform boundary.

The platform must not maintain different plural/formatting engines in Shopify,
Admin and future Moda applications.

## Catalogue ownership

Shared runtime:

```text
NO merchant UI strings
NO admin UI strings
NO country-specific copy
NO checkout/customer content
```

Shopify application:

```text
one independent ICU message catalogue file per supported Shopify Admin language
```

Admin application:

```text
its own ICU catalogue files; initial foundation may ship English only
```

Merchant/customer free text, WhatsApp conversation content and ARCH-006 merchant
message translations are not ICU UI catalogue strings.

## International-context invariant

The existing ARCH-005 separation remains mandatory:

```text
languageTag != countryCode != currencyCode != timeZone
```

The runtime must never infer currency from locale, country from language, or
language from currency/country/phone.

Currency formatting always receives an explicit currency code from commerce
state. Date/time formatting receives the selected locale and explicit merchant
or customer time zone according to the owning feature.


## Formatter authority rule

Shared formatting helpers must preserve explicit business dimensions as
authoritative inputs. Consumer presentation options may refine display but must
not replace the explicit currency code, required percentage/currency style, or a
runtime-level explicit time zone.

Text direction should use the current `Intl.Locale.getTextInfo()` API where
available, support the former `textInfo` accessor for compatibility, and retain a
deterministic locale/script fallback for runtimes exposing neither shape.

## Dependency graph

```text
ARCH-005-SHARED-004 (Complete, published 0.6.2)
        |
        v
ARCH-005-SHARED-005
Implement reusable ICU runtime
        |
        v
ARCH-005-SHARED-006
Publish shared ICU runtime
        |
        +--------------------------+
        |                          |
        v                          v
ARCH-005-SHOPIFY-002          ARCH-005-ADMIN-001
Blocked until publication     Adopt shared ICU runtime
        |                          |
        v                          v
ARCH-005-SYSTEM-TEST-001      ARCH-006-ADMIN-001
                              Merchant support inbox
```

## State rule for SHOPIFY-002

`ARCH-005-SHOPIFY-002` is blocked while SHARED-006 is incomplete.

The architect must not mark it Ready merely because SHARED-005 implementation is
accepted. The dependency is the **published** SHARED-006 release.

After SHARED-006 is architect-accepted and the exact package revision is verified,
the architect only needs to change SHOPIFY-002 from `blocked` to `ready` and clear
no additional dependency. Its next claim is Attempt 5.

## Shopify Attempt 5 migration rule

Attempt 5 must consume the published shared runtime and remove the superseded
local implementation. It is not permitted to keep the local custom engine as a
fallback or compatibility layer.

Required removal includes the current bespoke implementation rooted at:

```text
moda-interact/app/utils/merchant-i18n.js
```

including its local:

```text
englishCatalogue
languageOverrides
sourceCatalogues
custom plural helper
custom direction registry/runtime
custom message interpolation engine
```

Application-owned JSON catalogues and thin application-specific locale selection
wiring remain appropriate.

## Admin rule

Admin must adopt the same published runtime before ARCH-006-ADMIN-001 begins.
This prevents the Merchant Messages UI from introducing a second translation or
pluralisation system.

Admin UI localisation is separate from ARCH-006 merchant-message translation:

```text
Admin chrome/UI labels        -> ICU catalogue
MerchantMessage.originalBody  -> durable original content
MerchantMessageTranslation    -> translation pipeline
```
