---
id: ARCH-005-SHARED-005
architecture_id: ARCH-005
title: Implement reusable ICU MessageFormat internationalisation runtime
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 27
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-005-SHARED-004
enables:
  - ARCH-005-SHARED-006
created: 2026-09-06
updated: 2026-09-06
---

# Implement reusable ICU MessageFormat internationalisation runtime

## Objective

Extend the existing published Shared internationalisation boundary so Shopify,
Admin and future Moda applications can use the same ICU MessageFormat runtime
without copying locale/plural/formatting logic into each repository.

## Existing boundary

The package already publishes:

```text
@modainteract/moda-interact-shared/internationalization
```

and already owns canonical BCP-47/country/currency/time-zone primitives.

Build on that boundary. Do not create a competing package or a second unrelated
internationalisation API unless technically required and explicitly documented.

## Required implementation

Use ICU MessageFormat via the repository-appropriate FormatJS runtime
(`intl-messageformat` or the direct equivalent required to provide ICU
MessageFormat semantics).

The Shared package must provide reusable, framework-neutral capabilities for:

```text
- canonical locale handling using existing BCP-47 primitives;
- ICU message compilation/formatting from string messages + values;
- CLDR plural/select/selectordinal semantics supplied by ICU/Intl;
- number formatting;
- percentage formatting;
- date/time formatting with an explicit time zone when supplied;
- currency formatting that REQUIRES an explicit ISO currency code;
- locale text-direction resolution;
- strict catalogue/key validation helpers suitable for app-owned catalogues;
- bounded compilation caching so messages are not reparsed on every render.
```

The exact exported function/type names are repository-local design choices, but
the public API must be usable from both React Router/Vite (`moda-interact`) and
Next.js (`moda-interact-admin`) without React-specific dependencies.

## Catalogue contract

The Shared package owns the runtime, not product copy.

Do **not** add Shopify/Admin UI translations to `moda-interact-shared`.

Consumers provide data-only ICU catalogues, for example:

```json
{
  "usage.actions": "{quantity, plural, one {# action} other {# actions}}",
  "pending.page": "Page {page} of {totalPages}"
}
```

The shared runtime must accept application-provided catalogue data and must not
require executable translation functions.

## Strictness and fallback

Support a strict mode appropriate for declared/supported locales:

```text
missing required key -> detectable validation/runtime failure
malformed ICU message -> detectable validation/build/test failure
```

A consumer may implement unsupported-locale fallback at its application
boundary, but the Shared runtime must not silently manufacture missing
translations for a declared complete catalogue.

## International-context invariants

Preserve ARCH-005 independence:

```text
NEVER derive language from country/currency/phone.
NEVER derive currency from locale/language/country.
NEVER derive country from language/phone.
```

Formatting helpers receive their dimensions independently.

For money:

```text
(locale, numeric value, explicit currencyCode)
```

For operational date/time:

```text
(locale, instant, explicit timeZone)
```

## Direction

Expose a standards-aware direction helper using canonical locale semantics and
`Intl.Locale(...).getTextInfo()` where available, with compatibility for older
implementations that exposed the former `textInfo` accessor, followed by a safe
deterministic locale/script fallback.
Do not maintain Shopify-language direction data in Shared; direction is a
property of locale/language semantics, not a Shopify-specific registry.

## Tests

Add focused tests proving at minimum:

- English ICU interpolation;
- English plural selection;
- Czech `one/few/other` plural behaviour;
- one `select` or `selectordinal` case;
- regional locale formatting such as `fr-CA` without changing message language;
- explicit currency formatting and rejection of missing/invalid currency;
- explicit time-zone formatting without mutating the input instant;
- RTL direction for an RTL locale and LTR for an LTR locale;
- malformed ICU message is rejected/detectable;
- strict catalogue validation detects a missing required key;
- runtime works from the published `./internationalization` entrypoint shape;
- no React/Next/Vite dependency is introduced.

## Out of scope

- Shopify translation catalogue content.
- Admin translation catalogue content.
- Database schema changes.
- Merchant/customer free-text translation.
- ARCH-006 message translation pipeline.
- Consumer repository changes.
- Package publication; SHARED-006 owns publication.

## Acceptance criteria

- [x] ICU MessageFormat runtime is implemented in Shared.
- [x] existing internationalisation primitives remain compatible or migration is explicitly bounded/documented.
- [x] public runtime is framework-neutral and Node/browser safe.
- [x] app-provided JSON/string catalogues are supported.
- [x] strict catalogue/key validation is available.
- [x] plural/select semantics come from ICU/Intl rather than a Moda custom plural engine.
- [x] currency requires an explicit currency code.
- [x] date/time accepts an explicit time zone.
- [x] direction resolution is standards-aware.
- [x] compilation is cached/bounded appropriately.
- [x] no Shopify/Admin product strings are stored in Shared.
- [x] tests/typecheck/build/diff checks pass as applicable.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/src/internationalization.ts`
- `moda-interact-shared/src/internationalization.test.ts`
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `moda-interact-shared/scripts/validate-internationalization-entrypoint.mjs`

### Work Completed

- Preserved the existing ICU runtime and corrected explicit formatter dimension
  authority: currency code and currency style cannot be overridden, percent
  style cannot be overridden, and a runtime-level time zone remains authoritative
  over per-call options.
- Added current `Intl.Locale(...).getTextInfo()` direction resolution, legacy
  `textInfo` compatibility, and deterministic Arabic/Hebrew/Persian/Urdu and
  RTL-script fallback behavior.
- Added an automated build-and-import validation through
  `@modainteract/moda-interact-shared/internationalization` and its exports map.
- Added regressions for formatter-option override attempts and the direction
  fallback path.

### Validation Results

- `npm test`: passed, 83 tests; 1 unchanged Redis-dependent test skipped because
  `TEST_REDIS_URL` is unset.
- `npm run typecheck`: passed.
- `npm run build`: passed, including declaration generation.
- `npm run validate:internationalization-entrypoint`: passed; rebuilt the
  package and imported/used the ICU runtime through the public subpath.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Implementation is ready for developer commit/push. The repository agent did not
commit or push.

### Implementation Report

- Added `intl-messageformat` to the Shared runtime dependencies.
- Extended the existing `internationalization` entrypoint with
  `createInternationalizationRuntime`, strict `validateIcuCatalogue`,
  `resolveLocaleDirection`, ICU message formatting, number/percent/date-time/
  currency helpers, and a bounded LRU compilation cache.
- Preserved the existing BCP-47, country, currency, time-zone, and context
  schemas without adding consumer catalogue content or framework dependencies.
- Added coverage for interpolation, plural/select/selectordinal, Czech CLDR
  plural categories, regional `fr-CA` formatting, explicit currency/time zone,
  RTL/LTR direction, malformed messages, required keys, and fallback lookup.
- Validation: `npm test` passed with 82 tests and 1 Redis-dependent skip;
  `npm run typecheck` passed; `npm run build` passed.
- No lint script is declared by the Shared package. No consumer repositories
  were changed and no package publication was performed.

## Architect Review — Attempt 1

### Review Status

Changes Requested.

### Review Notes

Attempt 1 establishes the correct overall Shared ICU boundary and most of the
required implementation is sound. Preserve the ICU runtime, app-owned string
catalogue contract, bounded message cache, CLDR plural/select semantics and the
independent locale/country/currency/time-zone primitives.

Direct source review identified three blocking runtime-contract defects and one
missing acceptance validation:

```text
1. formatMoney() allows Intl.NumberFormatOptions to override the explicit
   currencyCode and even the required currency style because consumer options are
   spread after { style: "currency", currency: ... }.

2. formatPercent() likewise allows consumer options to replace style="percent".

3. resolveLocaleDirection() checks only the former Intl.Locale.textInfo accessor
   and otherwise returns ltr. Current standards expose getTextInfo(); in a runtime
   with getTextInfo() but no legacy accessor, Arabic/Hebrew/etc. would be
   incorrectly classified as LTR. The task also requires a deterministic fallback
   when neither API shape is available.

4. The required public-entrypoint proof is absent. The focused tests import the
   source module directly rather than proving the built package's
   ./internationalization export shape can be imported and used.
```

The existing date/time helper also permits per-call `options.timeZone` to override
a runtime-level explicit time zone. Preserve flexibility only when no runtime time
zone was supplied; when the runtime was created with an explicit time zone, that
explicit dimension must remain authoritative.

This remains the same canonical task. Preserve `attempt: 1`; the next claim is
Attempt 2.

## Attempt 2 — bounded runtime-invariant correction

Do not redesign the ICU architecture or add consumer catalogue content. Make only
the following corrections.

### A. Make explicit formatter dimensions authoritative

`formatMoney(value, currencyCode, options)` must always format as currency using
the normalized explicit `currencyCode` argument. `options` may customize ordinary
number-format presentation but must not change `style` or `currency` away from the
explicit arguments.

Required regressions:

```text
formatMoney(10, "USD", { currency: "EUR" }) -> still USD
formatMoney(10, "USD", { style: "decimal" }) -> still currency formatting
invalid explicit currencyCode -> rejected
```

`formatPercent(value, options)` must always retain `style: "percent"`; ordinary
percent formatting options remain permitted.

For date/time, if the runtime was created with `timeZone`, that explicit time zone
must not be silently replaced by `options.timeZone`. If no runtime time zone was
supplied, an explicit per-call time zone may remain supported if documented and
tested.

### B. Use the current standards-aware text-direction API with compatibility

Direction resolution order must be:

```text
1. Intl.Locale(...).getTextInfo().direction when available
2. legacy Intl.Locale(...).textInfo.direction when present
3. deterministic locale/script fallback when neither is available
```

The fallback must correctly classify at minimum common RTL language/script cases
such as Arabic (`ar`/Arab), Hebrew (`he`/Hebr), Persian (`fa`) and Urdu (`ur`). Do
not use country to infer direction and do not introduce a Shopify-specific
language registry into Shared.

Add tests that exercise the fallback path rather than only the host runtime's
native Intl implementation.

### C. Prove the public package subpath

Add an automated validation that builds the package and imports:

```text
@modainteract/moda-interact-shared/internationalization
```

through the package `exports` map (or an equivalent clean package-entrypoint
fixture) and successfully constructs/uses the ICU runtime. A source-relative
`./internationalization.js` import alone does not satisfy this acceptance item.

Do not publish from this task; SHARED-006 still owns publication.

### D. Preserve accepted Attempt 1 behaviour

Do not regress:

```text
ICU MessageFormat via intl-messageformat
app-owned data-only string catalogues
strict missing-key / malformed-message detection
CLDR Czech plural semantics
locale/country/currency/time-zone independence
explicit ISO currency validation
bounded compilation cache
framework-neutral Node/browser API
no Shopify/Admin product copy in Shared
```

### Attempt 2 validation and stop point

Run and record at minimum:

```text
npm test
npm run typecheck
npm run build
package-subpath import validation
git diff --check
```

The Redis-dependent integration test may remain skipped only when
`TEST_REDIS_URL` is unset and the skip is unchanged/unrelated.

Return this same task to `status: review` and STOP. No commit, push or package
publication.


## Architect Review — Attempt 2

### Review Status

Accepted.

### Review Notes

Attempt 2 satisfies the bounded runtime-invariant correction and the original
SHARED-005 contract. Source review confirmed:

```text
- formatMoney() preserves explicit normalized currencyCode and currency style;
- formatPercent() preserves percent style;
- runtime-level timeZone remains authoritative over per-call options;
- direction resolution uses getTextInfo(), then legacy textInfo, then a
  deterministic locale/script fallback;
- ICU MessageFormat remains framework-neutral and app catalogues remain
  data-only strings;
- strict missing-key/malformed-message validation remains available;
- bounded compiled-message caching remains in place;
- the built package exposes ./internationalization and includes an automated
  self-reference import validation through the package exports map;
- no Shopify/Admin product copy or consumer repository changes were introduced.
```

The submitted completion report records 83 passing tests with one unchanged
Redis-dependent skip when `TEST_REDIS_URL` is unset, plus passing typecheck,
build, package-entrypoint validation and diff check. The review environment did
not contain installed package dependencies, so those commands were not
independently rerun; acceptance is based on direct source/task inspection plus
the recorded validation evidence.

### Dependency Result

```text
ARCH-005-SHARED-005   Complete
ARCH-005-SHARED-006   Ready
ARCH-005-SHOPIFY-002  remains Blocked until SHARED-006 is published + accepted
ARCH-005-ADMIN-001    remains Pending until SHARED-006 is published + accepted
```

No publication is authorised from SHARED-005. Continue with the canonical
publication task `ARCH-005-SHARED-006`.
