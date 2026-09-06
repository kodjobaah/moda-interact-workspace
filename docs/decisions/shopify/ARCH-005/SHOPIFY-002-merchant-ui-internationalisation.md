---
id: ARCH-005-SHOPIFY-002
architecture_id: ARCH-005
title: Introduce merchant UI locale and standards-aware formatting
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 6
depends_on:
  - ARCH-005-SHARED-006
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-06T10:50:00Z
---

# Introduce merchant UI locale and standards-aware formatting

## Dependency satisfied

`ARCH-005-SHARED-006` is Complete and architect-accepted. The required published revision is:

```text
@modainteract/moda-interact-shared@0.6.3
```

This task is now **Ready**. The next claim is Attempt 6.

Attempt 6 must continue consuming that published Shared revision through:

```text
@modainteract/moda-interact-shared/internationalization
```

and must remove the superseded bespoke Shopify i18n implementation as specified below.

## Architect correction — Attempt 6: use the supplied JSON catalogues exactly

Attempt 5 is not accepted because it retained Shopify-owned translations inside a
single JavaScript data module instead of the mandatory one-file-per-locale layout.
The agent documented this as a deviation, but this requirement is not optional.

The architect overlay for Attempt 6 **already supplies the final locale files** at:

```text
moda-interact/app/i18n/locales/
  cs.json
  da.json
  de.json
  en.json
  es.json
  fi.json
  fr.json
  it.json
  ja.json
  ko.json
  nb.json
  nl.json
  pl.json
  pt-BR.json
  pt-PT.json
  sv.json
  th.json
  tr.json
  zh-Hans.json
  zh-Hant.json
```

These files contain the canonical 98 Shopify merchant UI message keys as data-only
ICU MessageFormat strings. They are architect-supplied implementation inputs.

### Mandatory implementation instructions

1. **Do not regenerate the locale files.** Use the architect-supplied JSON files.
   Do not collapse them back into one JavaScript object, do not replace them with
   `languageOverrides`, and do not manufacture missing keys from English.
2. The overlay also supplies a replacement `app/i18n/catalogues.js` whose only job
   is to import/register the 20 JSON files and expose the existing catalogue
   registry exports. Keep it data-loader/registry only. Do not reintroduce message
   strings into this file.
3. Remove the Attempt 5 embedded `englishCatalogue`, `translations`, English merge,
   or any equivalent hard-coded catalogue data from the Shopify codebase.
4. Keep `app/utils/merchant-i18n.js` as a thin Shopify adapter over
   `@modainteract/moda-interact-shared/internationalization`. It may resolve the
   authenticated Shopify locale, merchant fallback locale and merchant timezone,
   but it must not own ICU parsing, plural rules, formatter implementations, or
   translation message data.
5. Validate the **raw JSON objects** with Shared `validateIcuCatalogue` against the
   canonical key set derived from `en.json`. Supported-locale missing keys are a
   hard failure; there is no per-key English fallback for these 20 locales.
6. Update focused tests so they assert the supplied file-backed translations rather
   than old English-merge behaviour. At minimum prove:

```text
fr dashboard.performance != English
all 20 locale files have exactly the 98 canonical keys
all 20 locale files pass Shared ICU catalogue validation
pt-BR and pt-PT remain separate catalogues
zh-Hans and zh-Hant remain separate catalogues
fr-CA -> fr catalogue while locale remains fr-CA for formatting
unsupported future locale may fall back at catalogue selection boundary
```

7. Do not modify the supplied translation text simply to make tests easier. If an
   architect-supplied ICU string fails parsing, make only the smallest syntax fix
   required and record the exact key/file in the Completion Report.
8. Preserve every already-correct Attempt 5 behaviour: Shared runtime `0.6.3`,
   authenticated-locale precedence, explicit commerce currency, mixed-currency
   separation, merchant timezone formatting, Shared direction semantics, and
   customer free text `dir="auto"`.
9. Return this **same** task to `status: review` and STOP. No commit or push.

### Attempt 6 acceptance gate

Architect review will reject the task if any of the following remain:

```text
translation message literals embedded in app/i18n/catalogues.js
englishCatalogue / languageOverrides / translations aggregate objects
per-key English merge for a declared supported locale
supported locale represented without its own JSON file
custom Shopify ICU/plural/formatting engine duplicated from Shared
```

Required validation before handoff:

```text
focused merchant-i18n tests
full npm test
npm run build
npm run prisma:validate
npm run lint
npm run typecheck
git diff --check
```

Existing unrelated baseline lint/typecheck diagnostics may remain only if unchanged
and clearly reported.

## Objective

Complete merchant UI internationalisation by migrating the existing Attempt 4
behaviour onto the canonical Shared ICU MessageFormat runtime, while preserving
country/language/currency/time-zone independence.

## Attempt 5 — mandatory Shared-runtime migration

### 1. Consume the published Shared runtime

Use the SHARED-006 architect-accepted published revision:

```text
@modainteract/moda-interact-shared@0.6.3
```

through the public subpath:

```text
@modainteract/moda-interact-shared/internationalization
```

Update `moda-interact` package metadata/lockfile to that exact compatible
revision according to repository conventions.

Do not copy Shared runtime source into the Shopify repository.

Do not introduce a second ICU wrapper or custom plural engine in Shopify.

### 2. Remove the superseded local implementation

The current bespoke implementation rooted at:

```text
moda-interact/app/utils/merchant-i18n.js
```

must be removed or reduced to a genuinely thin app-specific adapter that only
selects Shopify-owned catalogue/locale/time-zone inputs and delegates message/
formatting behaviour to Shared.

It must no longer contain or own:

```text
englishCatalogue
languageOverrides
sourceCatalogues
custom plural category selection
custom message interpolation functions
custom number/date/time/currency formatter engine
custom direction runtime duplicated from Shared
```

A compatibility wrapper that retains those implementations behind the old API
is **not** acceptable.

Update every existing import from `app/utils/merchant-i18n` accordingly.

### 3. Store Shopify UI translations in independent files

Shopify owns its UI copy as data-only ICU catalogues under:

```text
moda-interact/app/i18n/locales/
```

Use one independent catalogue file per supported Shopify Admin language, for
example:

```text
en.json
fr.json
de.json
es.json
cs.json
...
pt-BR.json
pt-PT.json
zh-Hans.json
zh-Hant.json
```

The canonical current set remains:

```text
zh-Hans  Chinese (Simplified)
zh-Hant  Chinese (Traditional)
cs       Czech
da       Danish
nl       Dutch
en       English
fi       Finnish
fr       French
de       German
it       Italian
ja       Japanese
ko       Korean
nb       Norwegian (Bokmål)
pl       Polish
pt-BR    Portuguese (Brazil)
pt-PT    Portuguese (Portugal)
es       Spanish
sv       Swedish
th       Thai
tr       Turkish
```

Catalogue entries are ICU MessageFormat strings, not executable JavaScript
translation functions.

Example:

```json
{
  "usage.actions": "{quantity, plural, one {# action} other {# actions}}",
  "pending.page": "Page {page} of {totalPages}"
}
```

### 4. Catalogue completeness must be real

Maintain a canonical Shopify message-key set and validate the **raw app-owned
catalogue files** before any unsupported-locale fallback occurs.

For every declared supported Shopify language:

```text
missing catalogue -> test/build failure
missing canonical key -> test/build failure
malformed ICU message -> test/build failure
```

Do not manufacture completeness by merging English into a supported-language
catalogue before validation.

English/platform fallback is allowed only for genuinely unsupported/future
locale resolution, not missing keys in a declared complete supported catalogue.

### 5. Merchant locale resolution

Preserve the accepted precedence:

```text
authenticated Shopify/app locale
  -> merchant default language
  -> platform fallback
```

Regional locale remains exact for formatting even when UI copy uses a compatible
base-language catalogue:

```text
fr-CA -> fr UI catalogue + fr-CA formatting
es-MX -> es UI catalogue + es-MX formatting
```

Do not model languages as countries.

### 6. Formatting and context independence

Use the Shared runtime for standards-aware formatting.

Currency comes from the commerce object and must be explicit.

Do not infer:

```text
currency from locale/country/language
language from country/currency/phone
country from language/phone
```

Use merchant time zone only where merchant operational UI requires it. Stored
UTC instants remain unchanged.

Mixed currencies remain separate; missing currency remains unavailable rather
than becoming GBP or another default.

### 7. Direction and free text

Use the Shared direction helper for application chrome.

Customer-authored/free text remains:

```tsx
dir="auto"
```

Do not force merchant UI direction onto customer message content.

### 8. Surfaces

Preserve the Attempt 4 localisation coverage across:

```text
merchant dashboard
usage views
pending recoveries
recovery chart/details
onboarding
breadcrumbs/shared touched primitives
```

No hard-coded residual English UI labels should remain on those touched
merchant-facing surfaces when a catalogue key should own them.

## Customer independence

Regression tests must continue to prove changing merchant UI locale does not
change:

```text
Conversation.languageTag
WhatsApp template language
checkout currency
```

## Attempt 5 acceptance criteria

- [ ] SHARED-006 is Complete and the exact published Shared version is consumed.
- [ ] Shopify no longer owns a bespoke ICU/plural/formatting engine.
- [ ] the superseded `englishCatalogue` / `languageOverrides` implementation is removed.
- [ ] all supported Shopify Admin catalogues are independent data-only files.
- [ ] all catalogue messages parse as valid ICU MessageFormat.
- [ ] raw supported catalogues must contain every canonical required key.
- [ ] supported-language missing keys cannot silently inherit English.
- [ ] locale resolution preserves authenticated Shopify locale precedence.
- [ ] regional BCP-47 formatting remains independent from catalogue language.
- [ ] currency remains explicit and mixed-currency aggregation remains safe.
- [ ] time-zone formatting preserves stored UTC instants.
- [ ] application direction uses Shared semantics and customer free text remains `dir="auto"`.
- [ ] merchant UI language cannot mutate customer conversation/template language or checkout currency.
- [ ] focused tests plus full tests/build/Prisma/lint/typecheck/diff checks pass subject only to documented pre-existing baseline diagnostics.

## Out of scope

- modifying `moda-interact-shared` from this task;
- Admin application changes;
- database schema changes;
- customer/merchant free-text translation;
- changing ARCH-005 buyer/WhatsApp language-selection semantics.

## Completion Report

### Status

In Progress

### Attempt 2 Implementation

- Added authenticated Shopify session locale precedence over merchant default and platform fallback, while keeping timezone sourced from `ShopSettings`.
- Added the complete 19-locale Shopify Admin registry, canonical catalogue key set, deterministic exact/base/fallback catalogue resolution, and plural-aware messages.
- Removed invented GBP fallbacks and mixed-currency customer aggregation; dashboard totals now remain explicit per currency and missing currency is localized as unavailable.
- Localized touched dashboard, usage, pending-recovery, chart, onboarding, and breadcrumb copy; removed fixed table-left alignment and forceful customer-message direction.
- Added focused regressions for locale precedence, catalogue completeness, regional locale formatting, pluralization, currency isolation, customer-context independence, and RTL direction behavior.

### Validation

- Focused Attempt 2 tests: 13 passed.
- Full `npm test`: 116 passed, 1 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run lint`: existing baseline errors remain in PlanSelector, billing routes, privacy, and telemetry tests; no new errors remain in Attempt 2 files.
- `npm run typecheck`: existing JavaScript/React implicit-any, alias-resolution, and Redis typing baseline diagnostics remain; the authenticated session locale property diagnostic was removed.

### Attempt 3 Revalidation

- Re-entered through the deterministic resolver as `moda_app`; explicit dependencies remained complete.
- Focused ARCH-005 suite: 13 passed.
- Full `npm test`: 116 passed, 1 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `npm run lint`: unchanged baseline of 9 unrelated errors and 2 warnings; no changed-file lint regressions.
- `npm run typecheck`: unchanged repository baseline diagnostics; no `Session.locale` diagnostic.
- `git diff --check`: passed.
- No implementation changes were required during Attempt 3; no commit or push was performed.

### Attempt 4 Implementation

- Replaced the merged-English catalogue construction with exported source catalogues and source-key completeness regression coverage for all 20 Shopify Admin locales.
- Added canonical locale direction metadata with `Intl.Locale` direction fallback for valid future or non-Shopify locales.
- Added category-aware plural forms using raw numeric quantities, including Czech one/few/other coverage and locale-aware formatting for large values.
- Removed remaining hard-coded RecoveryChart close copy and usage chart aria copy; mapped bounded sender and message-status values through catalogue keys while preserving customer message bodies with `dir="auto"`.

### Attempt 4 Files Changed

- `moda-interact/app/utils/merchant-i18n.js`
- `moda-interact/app/components/dashboard/RecoveryChart.jsx`
- `moda-interact/app/components/dashboard/UsageOverview.jsx`
- `moda-interact/app/components/dashboard/UsageEvents.jsx`
- `moda-interact/app/components/dashboard/PendingRecoveries.jsx`
- `moda-interact/tests/unit/merchant-i18n.test.ts`
- `docs/decisions/shopify/ARCH-005/SHOPIFY-002-merchant-ui-internationalisation.md`

### Attempt 4 Validation

- Focused ARCH-005 suite: 14 passed.
- Full `npm test`: 117 passed, 1 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `npm run lint`: unchanged baseline of 9 unrelated errors and 2 warnings; no changed-surface lint regressions.
- `npm run typecheck`: unchanged repository baseline diagnostics; no new `Session.locale` diagnostic.
- `git diff --check`: passed.
- No commit or push was performed.

### Attempt 5 Shared-runtime migration

- Consumed the exact published `@modainteract/moda-interact-shared@0.6.3` revision through `@modainteract/moda-interact-shared/internationalization`.
- Reduced `app/utils/merchant-i18n.js` to a Shopify adapter for locale precedence, catalogue selection, merchant timezone, compatibility formatting defaults, and explicit commerce currency validation; ICU parsing, plural selection, formatting, direction, and raw catalogue validation now delegate to Shared.
- Converted the Shopify message values from executable interpolation functions to ICU MessageFormat strings and preserved the 20-locale catalogue/key contract in `app/i18n/catalogues.js`.
- Preserved authenticated-locale precedence, regional formatting, mixed-currency isolation, UTC instant handling, Shared direction semantics, and `dir="auto"` for customer-authored message content.

### Attempt 5 Validation

- Focused merchant i18n suite: 10 passed.
- Full `npm test`: 117 passed, 1 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run lint`: unchanged repository baseline of 9 unrelated errors and 2 warnings.
- `npm run typecheck`: unchanged repository baseline implicit-any and related diagnostics; no migration-specific failure was introduced.
- No commit or push was performed.

### Attempt 5 Review Note

The runtime migration is complete and ready for architectural review. The remaining packaging deviation is that catalogue data is currently kept in one data-only module rather than split into one raw JSON file per locale under `app/i18n/locales/`; the ICU values are complete and validated through Shared, but this file-layout requirement should be resolved in review before final acceptance.

### Review decision

Changes requested. Attempt 1 establishes a useful merchant-i18n foundation, but
ARCH-005-SHOPIFY-002 is not yet architect-acceptable. Keep this as the same
canonical task. Do not reopen already-correct ARCH-005 Shopify work.

### 1. Resolve the authenticated merchant UI locale before the shop default

The current routes call `merchantUiContext(settings)`, so the UI locale is always
`ShopSettings.defaultLanguageTag` (or platform fallback) even though both loaders
already have the authenticated Shopify `session`.

Use this independent precedence for **merchant UI language only**:

```text
valid authenticated Shopify/app user locale (for example session.locale)
    -> ShopSettings.defaultLanguageTag
    -> platform fallback en-GB
```

Timezone remains independent:

```text
ShopSettings.defaultTimeZone
    -> platform fallback UTC
```

Do not persist the authenticated staff user's locale into `ShopSettings`. Do not
use country, checkout currency, customer language or WhatsApp language to choose
the merchant UI locale.

Add focused tests proving authenticated-locale precedence and fallback.

### 2. Do not invent or combine commerce currencies

The touched merchant UI path still contains false GBP fallbacks:

```text
app/routes/app._index.jsx
  recovery.currency ?? "GBP"

app/components/dashboard/RecoveryChart.jsx
  customer.recoveries[0]?.currency ?? "GBP"
```

Remove invented currency defaults. Currency must come from the relevant commerce
record. A missing currency remains missing/unknown; it must not become GBP merely
because the old UI used GBP.

Also do not sum monetary values across different currencies into one customer
`totalPrice` and then label the result using the first recovery's currency. For a
customer with mixed currencies, either display separate totals per currency or
avoid presenting a single combined monetary total.

`Stats` must likewise not present a monetary total as a plain locale-formatted
number when no reliable currency exists. Use explicit per-currency values or a
localized unavailable/neutral presentation that does not invent a currency.

Add regressions for:

```text
GBP + EUR recoveries for one customer -> never combined as one currency amount
missing recovery currency             -> never formatted as GBP
explicit USD with fr-FR UI locale      -> remains USD
```

### 3. Finish catalogue/plural handling for the surfaces changed by this task

Attempt 2 must implement the full current Shopify Admin merchant-language set
listed in the Translation framework section above, not only representative
English/French/German catalogues. This is an initial product requirement, not an
example-only test fixture.

Required catalogue behaviour:

```text
Shopify/app exact locale
    -> exact Moda catalogue when present
    -> compatible base-language catalogue
    -> merchant default catalogue
    -> platform fallback en
```

Keep the exact resolved BCP-47 locale for `Intl` formatting even when UI copy is
served from a base-language catalogue. Never choose a catalogue from country or
currency.

Add tests proving:

```text
every required Shopify Admin language has a catalogue
every required catalogue has the canonical key set
fr-CA uses French copy while retaining fr-CA formatting
es-MX uses Spanish copy while retaining es-MX formatting
pt-BR and pt-PT remain independently selectable
zh-Hans and zh-Hant remain independently selectable
unknown/future valid locale falls through deterministically
```

RTL behaviour must be registry/locale driven rather than country driven. If a
future Shopify-supported RTL language is added, it should require catalogue/
metadata addition, not React branching.

Attempt 1 still leaves user-visible English literals inside the surfaces it
claims to internationalise, including `UsageOverview`, `UsageEvents`,
`RecoveryChart`, `PendingRecoveries` and the usage page heading. Status labels,
metric labels, pagination text and unavailable text are examples.

Move the user-visible text for the surfaces changed by this task behind the
catalogue abstraction, except for deliberate domain/provider identifiers.

Implement plural-aware messages where quantity changes grammar. Use
`Intl.PluralRules` or an equivalent bounded catalogue mechanism. At minimum cover
representative singular/plural cases such as:

```text
1 action / 2 actions
1 recovery / 2 recoveries
1 message / 2 messages
```

Add focused tests for English and one non-English catalogue.

### 4. Remove LTR assumptions and keep customer text direction independent

The touched internationalised UI still contains fixed LTR assumptions such as:

```text
align="left"
textAlign: "left"
```

and customer message content is currently rendered with:

```text
dir={i18n.direction}
```

Do not force customer/user-generated message direction from the merchant UI
locale. Use `dir="auto"` for independently authored free text where appropriate.
For merchant-interface chrome, use the resolved merchant direction and logical
start/end alignment (or remove fixed left/right alignment).

Add a regression proving an RTL merchant UI does not force unrelated customer
message text into the merchant UI direction.

### 5. Strengthen the customer-independence regression

The current test only adds ad-hoc `customerLanguageTag` and `checkoutCurrency`
properties to a settings object and proves `merchantUiContext` does not mutate
them. That does not substantively prove the task invariant.

Use representative canonical fixtures/fields for the independent contexts and
prove that changing only merchant UI locale leaves them unchanged, including:

```text
Conversation.languageTag
WhatsApp/provider template language identity
checkout/recovery currency
```

The Shopify task must not implement downstream Messaging behaviour; this is a
boundary/independence regression only.

### Validation required before returning to review

Run and record:

```text
focused ARCH-005 merchant-i18n tests, including full Shopify-language catalogue completeness
full npm test
npm run build
npm run prisma:validate
npm run lint
npm run typecheck
git diff --check
```

Existing baseline lint/typecheck failures may remain only if they are unchanged
and clearly identified. New/changed SHOPIFY-002 files must not add new failures.

### Scope guard

Do not change:

```text
ARCH-005-SHOPIFY-001 accepted Shopify locale/market default initialisation
ARCH-005-SHOPIFY-003 accepted buyer international-context producer behaviour
customer conversation-language resolution
WhatsApp template selection
background/messaging repositories
```

Return this same task to `status: review`, complete the Completion Report for
Attempt 2, leave Architect Review unchanged, and STOP. No commit or push.


## Architect Review

### Review Status

Accepted — Attempt 6

### Review Notes

Attempt 6 is accepted. Architect source review confirmed the mandatory Shared-ICU
migration and file-backed catalogue boundary are now implemented as required.

Verified architecture/conformance:

```text
@modainteract/moda-interact-shared@0.6.3 is pinned
20 independent app/i18n/locales/*.json catalogues exist
each supplied catalogue contains exactly the canonical 98 keys
ICU placeholder variables are preserved across all 20 catalogues
app/i18n/catalogues.js is registry/import metadata only
no englishCatalogue / languageOverrides / embedded translations aggregate remains
no per-key English merge exists for declared supported locales
merchant-i18n.js is a thin adapter over the Shared internationalization runtime
authenticated Shopify locale precedence is preserved
regional BCP-47 formatting locale is preserved independently from catalogue locale
merchant timezone remains independent
commerce currency remains explicit and mixed currencies remain separated
customer-authored message content remains dir=auto
```

Focused tests also exercise raw catalogue completeness and Shared ICU validation for
all supported locales, regional catalogue fallback, Czech plural categories, explicit
currency handling, merchant timezone conversion and customer-context independence.

The repository archive does not contain installed dependencies, so architect review
did not rerun the npm suite locally. The submitted execution evidence records 11
focused tests, 118 full tests with one skip, build, Prisma validation and diff check
as passing; source review found no contradiction with that report.

### Architecture Conformance

Accepted. `country`, `language`, `currency` and `timeZone` remain independent, and
Shopify no longer owns a duplicate ICU/plural/formatting implementation.

### Follow-up

`ARCH-005-SHOPIFY-002` is Complete. Its declared downstream system-test dependency
may be moved to Ready once the authoritative system-test task/index is reconciled
against its full dependency set. Translation copy should receive normal product/
native-speaker localisation QA over time; that is not an architectural blocker.

## Attempt 6 Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/package.json`
- `moda-interact/package-lock.json`
- `moda-interact/app/i18n/catalogues.js`
- `moda-interact/app/i18n/locales/{cs,da,de,en,es,fi,fr,it,ja,ko,nb,nl,pl,pt-BR,pt-PT,sv,th,tr,zh-Hans,zh-Hant}.json`
- `moda-interact/app/utils/merchant-i18n.js`
- `moda-interact/tests/unit/merchant-i18n.test.ts`
- Localized merchant dashboard, usage, pending recovery, chart, onboarding, breadcrumb, route, and shop-service files from the accepted Shopify implementation remain in scope and unchanged by the Attempt 6 catalogue correction.

### Work Completed

- Consumed the exact published `@modainteract/moda-interact-shared@0.6.3` runtime through `@modainteract/moda-interact-shared/internationalization`.
- Adopted all 20 architect-supplied JSON catalogues as independent data-only ICU files; `app/i18n/catalogues.js` now only imports and registers them.
- Removed the Attempt 5 embedded catalogue aggregate and all per-key English merge behavior.
- Validated raw supported catalogues with Shared `validateIcuCatalogue` against the canonical 98-key set before runtime locale fallback.
- Kept the thin Shopify adapter responsible only for authenticated-locale precedence, compatible catalogue selection, merchant timezone, compatibility display defaults, and explicit currency validation.
- Preserved regional BCP-47 formatting, merchant timezone handling, Shared direction semantics, mixed-currency isolation, and customer free text `dir="auto"`.
- Strengthened focused regressions for all 20 raw catalogues, ICU validity, representative French/Japanese/Simplified Chinese/Traditional Chinese translations, locale fallback, plural behavior, currency isolation, timezone conversion, and context independence.

### Validation Results

- `npx vitest run tests/unit/merchant-i18n.test.ts`: passed, 11 tests.
- `npm test`: passed, 118 tests; 1 skipped.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run lint`: unchanged repository baseline, 9 errors and 2 warnings in unrelated billing, privacy, onboarding, and telemetry test files.
- `npm run typecheck`: unchanged repository baseline diagnostics remain; no diagnostics were reported for `app/utils/merchant-i18n.js`, `app/i18n/catalogues.js`, or `tests/unit/merchant-i18n.test.ts` after the final correction.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Implementation is ready for developer commit/push. The repository agent did not commit or push.

Review handoff complete.
