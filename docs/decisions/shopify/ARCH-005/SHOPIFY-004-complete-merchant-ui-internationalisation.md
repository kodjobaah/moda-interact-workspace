---
id: ARCH-005-SHOPIFY-004
architecture_id: ARCH-005
title: Complete authenticated Shopify merchant UI internationalisation coverage
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SHOPIFY-002
  - ARCH-006-SHOPIFY-003
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-08
updated: 2026-09-08
---

# ARCH-005-SHOPIFY-004: Complete authenticated Shopify merchant UI internationalisation coverage

## Architecture

Canonical architecture:

```text
docs/architecture/ARCH-005-global-internationalisation-whatsapp-markets.md
```

This is a bounded follow-on to architect-accepted `ARCH-005-SHOPIFY-002`. It does **not** replace or redesign the Shared ICU runtime, locale resolution model, or existing 20 locale catalogues.

## Why this task exists

`ARCH-005-SHOPIFY-002` internationalised the dashboard, usage, pending-recovery, recovery-detail, onboarding and shared touched primitives. Later ARCH-006/ARCH-007 work and older Shopify-template surfaces still leave authenticated `/app/**` merchant chrome with residual hard-coded English.

The current inspected residuals are limited and concrete:

```text
app/routes/app.jsx
  Home
  Messages
  Moda Interact logo

app/routes/app.additional.jsx
  Shopify template/example page headings and instructional copy

app/routes/app.merchant-support.jsx
  support headings, empty state, pagination, compose labels/buttons/errors,
  sender labels, translation-state labels and translation-toggle labels

app/routes/app.usage.jsx
  loader-created "Guest" presentation fallback

app/routes/app._index.jsx
  loader-created "Guest" presentation fallback

app/components/dashboard/UsageEvents.jsx
  customer display fallback must localise Guest rather than receive English from loader

app/routes/app.billing.tsx
  ACTIVE/TRIALING subscription status is still rendered as raw provider/domain enum text
```

## Dependency gate — satisfied

All YAML dependencies are now architect-accepted Complete. This task is Ready and may be claimed as Attempt 1.

The final dependency, `ARCH-007-SHOPIFY-002`, was architect-accepted Complete on 2026-09-08. The task may now proceed, while still respecting the overlap warning because its implementation owns the final natural-language cleanup of:

```text
app/routes/app.merchant-support.jsx
app/i18n/locales/*.json
```

Do not start this task in parallel with ARCH-007-SHOPIFY-002. Do not resolve the overlap by merging speculative copies of either implementation.

## Objective

Remove residual hard-coded English from the **authenticated embedded Shopify merchant UI** while preserving the existing Shared ICU runtime, merchant locale precedence, customer-language independence, tenant boundaries and billing/support behaviour.

## Exact scope

Only modify the following implementation/test surfaces unless a directly required import/test fixture forces a tiny adjacent change:

```text
moda-interact/app/routes/app.jsx
moda-interact/app/routes/app.additional.jsx
moda-interact/app/routes/app.merchant-support.jsx
moda-interact/app/routes/app.usage.jsx
moda-interact/app/routes/app._index.jsx
moda-interact/app/components/dashboard/UsageEvents.jsx
moda-interact/app/routes/app.billing.tsx
moda-interact/app/i18n/locales/*.json
moda-interact/tests/unit/merchant-i18n.test.ts
moda-interact/tests/unit/merchant-support-route.test.ts
moda-interact/tests/unit/billing-ui.test.ts
moda-interact/tests/unit/shopify-ui-i18n-coverage.test.ts   # create
```

The exact new catalogue keys and English source meanings are architect-owned in:

```text
docs/decisions/shopify/ARCH-005/SHOPIFY-004-i18n-key-manifest.md
```

Read that manifest before editing locale files.

## Explicitly out of scope

Do **not** modify:

```text
app/routes/_index/route.jsx
app/routes/auth.login/**
app/routes/privacy.tsx
app/components/onboarding/PlanSelector.jsx
```

Reasons:

- `/` and `/auth/login` are pre-authentication surfaces and need a separate decision for the locale source when no authenticated Shopify session exists.
- `privacy.tsx` is legal-policy copy; translating legal text requires separately approved copy rather than opportunistic machine translation.
- `PlanSelector.jsx` is currently not imported/rendered and contains obsolete static pricing copy. Do not revive or refactor dead pricing UI as part of i18n completion.

Also do not edit health/readiness/webhook/resource-only routes or internal exception strings that are never rendered as merchant UI.

## Deterministic implementation recipe

### 1. Preserve the existing i18n runtime

Continue using:

```text
createMerchantI18n(...)
merchantUiContext(...)
@modainteract/moda-interact-shared/internationalization
```

Do not create another translator, message formatter, locale registry or fallback engine.

Do not change `SUPPORTED_ADMIN_LOCALES`.

Do not add a new language in this task.

### 2. `app/routes/app.jsx` — localise embedded app shell

The loader already authenticates the Shopify merchant and resolves the internal shop.

Add only what is required to obtain the existing merchant UI context:

1. import `db` from `../db.server`;
2. import `createMerchantI18n` and `merchantUiContext` from `../utils/merchant-i18n`;
3. after `resolveShopifyShop`, read `shopSettings` with `shopId`;
4. return `merchantUi: merchantUiContext(settings, session)` with the existing `apiKey` and `unreadMessages`;
5. in the component create `const i18n = createMerchantI18n(merchantUi)`;
6. replace only these visible literals:

```text
Moda Interact logo -> common.logoAlt
Home               -> navigation.home
Messages           -> navigation.messages
```

For the unread suffix keep the count separate from the translated label and format it through the runtime:

```jsx
{i18n.t("navigation.messages")}
{unreadMessages > 0 ? ` (${i18n.formatNumber(unreadMessages)})` : ""}
```

Do not change routes/hrefs.

Pass the already-created `merchantUi` to the nested template/example page using React Router Outlet context:

```jsx
<Outlet context={{ merchantUi }} />
```

Do not refactor existing child loaders to use this context.

### 3. `app/routes/app.additional.jsx` — localise the authenticated example page

Do not add another authentication/Shopify/database loader.

Use the parent Outlet context:

```jsx
const { merchantUi } = useOutletContext();
const i18n = createMerchantI18n(merchantUi);
```

Replace the current long template prose with the exact simpler semantic structure below so the translator does not need rich-text interpolation around links/code:

```text
page heading             -> additional.title
first section heading    -> additional.multiplePages
paragraph                -> additional.description
App Bridge link label    -> additional.appBridgeDocs
second paragraph         -> additional.navigationInstructions
aside heading            -> additional.resources
best-practices link label-> additional.appNavBestPractices
```

Preserve both existing Shopify documentation URLs exactly.

Preserve these technical tokens exactly inside translated text where present:

```text
App Bridge
app/routes
app/routes/app.jsx
```

### 4. `app/routes/app.merchant-support.jsx` — finish the partial i18n migration

This route already loads `merchantUi` and creates `i18n`. Do not change tenant resolution, unread-message behaviour, CTA routing, grapheme counting or message translation semantics.

Replace every merchant-visible hard-coded English string listed in the key manifest with `i18n.t(...)`.

Mandatory mappings include:

```text
page heading                        -> navigation.messages
Support thread                      -> support.thread
No messages yet.                    -> support.empty
Support thread pages                -> support.paginationLabel
Previous                            -> support.previous
Next                                -> support.next
Page {page} of {totalPages}         -> support.page
Contact Moda Support                -> support.contactHeading
Message                             -> support.messageLabel
client 1..500 grapheme validation   -> support.messageLengthError { max: 500 }
Sending...                          -> support.sending
Send                                -> support.send
You                                 -> support.you
System                              -> support.system
Moda Support                        -> support.modaSupport
translation unavailable text        -> support.translationUnavailable
translation processing text         -> support.translationProcessing
View translation                    -> support.viewTranslation
View original                       -> support.viewOriginal
```

Do not translate `message.originalBody` or `message.displayBody` again. Keep customer/merchant free text `dir="auto"`.

#### Stable action errors

The action must stop returning arbitrary English/service exception text to the component.

Use bounded stable error codes:

```text
UNSUPPORTED_ACTION
SEND_FAILED
```

Required response behaviour:

```js
unsupported intent -> { errorCode: "UNSUPPORTED_ACTION" }, status 400
compose exception  -> { errorCode: "SEND_FAILED" }, status 400
```

The component maps those codes only at presentation time:

```text
UNSUPPORTED_ACTION -> support.unsupportedAction
SEND_FAILED        -> support.sendFailed
```

Do not return `error.message` to the merchant UI.

Do not change `composeMerchantMessage` or service validation ownership in this task.

### 5. Remove loader-owned English `Guest`

In both:

```text
app/routes/app.usage.jsx
app/routes/app._index.jsx
```

change only the display fallback used while constructing `customerName`:

```text
"Guest" -> null
```

Names and email values remain unchanged.

In `UsageEvents.jsx`, render the customer column exactly by meaning:

```text
no linked recovery            -> usage.unlinked
linked recovery + no customer -> chart.guest
linked recovery + customer    -> customerName
```

Do not add another Guest key; reuse existing `chart.guest`.

### 6. Localise safe billing projection status

`app.billing.tsx` already localises the page. Do not change ARCH-007 billing behaviour.

For the safe statuses only:

```text
ACTIVE   -> billing.statusActive
TRIALING -> billing.statusTrialing
```

Do not render a raw enum value in the `<strong>` status label.

Do not change fail-closed `UNMAPPED`/unsafe presentation, current-vs-pending plan semantics, hosted plan navigation or entitlement logic.

### 7. Update all 20 existing locale JSON files

Add every key from 

# ARCH-005-SHOPIFY-004 — Canonical i18n key manifest

This file is an architect-owned implementation input for `ARCH-005-SHOPIFY-004`.

The task must add **exactly these new keys** to every existing Shopify locale JSON catalogue. `en.json` must use the exact English source strings below. Non-English catalogues must provide natural translations while preserving ICU placeholders and invariant technical/brand tokens.

| Key | Exact English source / semantic value |
|---|---|
| `common.logoAlt` | `Moda Interact logo` |
| `navigation.home` | `Home` |
| `navigation.messages` | `Messages` |
| `additional.title` | `Additional page` |
| `additional.multiplePages` | `Multiple pages` |
| `additional.description` | `This example page demonstrates how to add multiple pages to the embedded app.` |
| `additional.appBridgeDocs` | `App Bridge documentation` |
| `additional.navigationInstructions` | `Add routes under app/routes and add navigation links in app/routes/app.jsx.` |
| `additional.resources` | `Resources` |
| `additional.appNavBestPractices` | `App navigation best practices` |
| `support.thread` | `Support thread` |
| `support.empty` | `No messages yet.` |
| `support.paginationLabel` | `Support thread pages` |
| `support.previous` | `Previous` |
| `support.next` | `Next` |
| `support.page` | `Page {page} of {totalPages}` |
| `support.contactHeading` | `Contact Moda Support` |
| `support.messageLabel` | `Message` |
| `support.messageLengthError` | `Message must contain between 1 and {max} graphemes.` |
| `support.sending` | `Sending...` |
| `support.send` | `Send` |
| `support.you` | `You` |
| `support.system` | `System` |
| `support.modaSupport` | `Moda Support` |
| `support.translationUnavailable` | `Translation unavailable. Please try again later.` |
| `support.translationProcessing` | `Translation is processing.` |
| `support.viewTranslation` | `View translation` |
| `support.viewOriginal` | `View original` |
| `support.sendFailed` | `Unable to send message. Please try again.` |
| `support.unsupportedAction` | `That support action is not available.` |
| `billing.statusActive` | `Active` |
| `billing.statusTrialing` | `Trial` |

### Exact locale translation requirements

For every new key in the canonical manifest, write the value in the language represented by that locale file.

Use this exact locale mapping:

```text
en.json       -> English
cs.json       -> Czech
da.json       -> Danish
de.json       -> German
es.json       -> Spanish
fi.json       -> Finnish
fr.json       -> French
it.json       -> Italian
ja.json       -> Japanese
ko.json       -> Korean
nb.json       -> Norwegian Bokmål
nl.json       -> Dutch
pl.json       -> Polish
pt-BR.json    -> Brazilian Portuguese
pt-PT.json    -> European Portuguese
sv.json       -> Swedish
th.json       -> Thai
tr.json       -> Turkish
zh-Hans.json  -> Simplified Chinese
zh-Hant.json  -> Traditional Chinese
```

`en.json` is the canonical English source catalogue and MUST use the exact English values from the manifest.

For every other locale file:

1. Translate the **meaning of every manifest value** into the target language above.
2. Do NOT copy the English sentence into a non-English catalogue merely as a fallback.
3. Use natural merchant-facing UI language appropriate for the target locale rather than a word-for-word transliteration.
4. Do NOT leave a value in English unless the only English content is an explicitly invariant brand or technical token.
5. Translate surrounding words even when a sentence contains an invariant token.

For example:

```text
English:
App Bridge documentation

fr.json:
Documentation App Bridge

de.json:
App-Bridge-Dokumentation

ja.json:
App Bridge ドキュメント
```

`App Bridge` remains unchanged because it is an invariant technical name, but the surrounding UI wording is translated.

The following must NEVER be translated or modified:

```text
Moda Interact
Moda Support
App Bridge
app/routes
app/routes/app.jsx
{page}
{totalPages}
{max}
```

The ICU placeholder identifiers must remain byte-for-byte identical. For example, the French translation of:

```text
Page {page} of {totalPages}
```

must still contain both:

```text
{page}
{totalPages}
```

Do not change them to French words, different variable names, positional placeholders or another interpolation syntax.

Treat regional variants as distinct translations:

```text
pt-BR.json -> Brazilian Portuguese wording
pt-PT.json -> European Portuguese wording

zh-Hans.json -> Simplified Chinese
zh-Hant.json -> Traditional Chinese
```

Do NOT generate one Portuguese translation and copy it into both Portuguese catalogues without considering regional wording.

Do NOT generate one Chinese translation and copy it into both Chinese catalogues. Use the appropriate writing system for each locale.

When implementing this task, process all manifest keys for one locale catalogue and then continue to the next locale. Do not stop after updating `en.json` or a representative subset.

Completion requires all 20 locale files to contain every manifest key.

## Placeholder invariants

These placeholders must be preserved exactly in every locale:

```text
support.page               -> {page}, {totalPages}
support.messageLengthError -> {max}
```

Do not rename, translate or remove placeholder identifiers.

## Invariant tokens

These tokens may remain unchanged inside translated values:

```text
Moda Interact
Moda Support
App Bridge
app/routes
app/routes/app.jsx
```

## Existing keys

Do not rename or remove existing catalogue keys. This manifest defines additions only.
 to **every** existing locale file:

```text
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

Rules:

- `en.json` values must exactly match the architect English source strings in the manifest.
- Every non-English file must contain a natural translation of every new UI string.
- Do not intentionally use the English sentence as a fallback in a declared supported non-English catalogue.
- Preserve ICU placeholders exactly, including `{page}`, `{totalPages}` and `{max}`.
- Preserve brand/technical tokens exactly where they occur: `Moda Interact`, `Moda Support`, `App Bridge`, `app/routes`, `app/routes/app.jsx`.
- Do not change existing catalogue keys/values unless a test proves a directly related defect.
- Do not embed JavaScript functions in locale files.

### 8. Tests — exact required coverage

#### `merchant-i18n.test.ts`

Keep the existing completeness/ICU test. Because `CATALOGUE_KEYS` comes from `en.json`, it must automatically prove every supported locale contains every new key.

Add representative assertions that new copy is actually translated, at minimum:

```text
fr navigation.home != en navigation.home
ja support.send != en support.send
zh-Hans additional.resources != en additional.resources
de billing.statusActive != en billing.statusActive
```

Brand tokens may legitimately remain unchanged; do not use them for the non-English-difference assertion.

#### `merchant-support-route.test.ts`

Update the compose failure expectation from raw exception text to:

```json
{ "errorCode": "SEND_FAILED" }
```

Add an unsupported-intent regression expecting:

```json
{ "errorCode": "UNSUPPORTED_ACTION" }
```

Keep all existing tenant/provenance/read/CTA regressions.

#### `billing-ui.test.ts`

Add a focused source/component regression proving safe billing status presentation uses:

```text
billing.statusActive
billing.statusTrialing
```

and does not directly render `subscription.status` as merchant copy.

Do not duplicate ARCH-007-SHOPIFY-002 billing-behaviour tests.

#### create `tests/unit/shopify-ui-i18n-coverage.test.ts`

This is a bounded regression guard for this task only. Read the scoped source files and prove:

1. `app.jsx` uses `common.logoAlt`, `navigation.home`, `navigation.messages`;
2. `app.additional.jsx` uses every `additional.*` key from the manifest and does not retain the old English headings;
3. `app.merchant-support.jsx` uses every required `support.*` key and no longer contains the exact old visible literals listed in the manifest;
4. `app.usage.jsx` and `app._index.jsx` do not contain `|| "Guest"`;
5. `UsageEvents.jsx` uses `chart.guest` for a linked recovery without customer display data;
6. `app.billing.tsx` uses both billing status keys.

Do **not** write a generic repository-wide English-text regex scanner. It would create false positives for code, logs, provider enums, tests and legal copy. Assert only the exact scoped literals/keys defined by this task.

## Work Items

- [ ] Verify all three explicit dependencies are architect-accepted Complete before claiming.
- [ ] Localise authenticated app shell navigation and logo alt text.
- [ ] Localise `app.additional` through parent Outlet merchant context.
- [ ] Complete merchant-support UI localisation and stable error-code presentation.
- [ ] Remove loader-owned English Guest fallback and localise the presentation fallback.
- [ ] Localise safe billing status labels without changing billing semantics.
- [ ] Add all manifest keys to all 20 locale JSON files with valid ICU strings.
- [ ] Add/update the exact focused tests required above.
- [ ] Run required validation and complete the task report.
- [ ] Return only this task to `review` and STOP.

## Acceptance Criteria

- [ ] No scoped authenticated `/app/**` surface listed by this task retains the identified hard-coded English merchant UI copy.
- [ ] Existing Shared ICU runtime and merchant locale precedence are reused unchanged.
- [ ] All 20 supported locale JSON catalogues contain the exact same complete key set and validate as ICU MessageFormat.
- [ ] Merchant-support service/action failures are presented through bounded error codes and translated UI keys, not raw English exception text.
- [ ] Customer/merchant message bodies remain `dir="auto"` and are not retranslated by this task.
- [ ] No locale/country/currency/customer-language coupling is introduced.
- [ ] `Guest` is presentation-owned and localised; loaders no longer bake English `Guest` into DTO data.
- [ ] ACTIVE/TRIALING labels are translated without changing ARCH-007 billing state semantics.
- [ ] No pre-auth, legal-policy, dead pricing component, database, Shared, Admin, Background, Messaging or Gateway implementation is modified.
- [ ] Focused tests, full declared repository tests/build/Prisma validation and diff checks pass subject only to documented pre-existing baseline diagnostics.

## Validation

Before running commands, inspect `moda-interact/package.json` and use only scripts that exist.

Required:

```text
npx vitest run tests/unit/merchant-i18n.test.ts tests/unit/merchant-support-route.test.ts tests/unit/billing-ui.test.ts tests/unit/shopify-ui-i18n-coverage.test.ts
npm test
npm run build
npm run prisma:validate
npm run lint
npm run typecheck
git diff --check
```

Existing documented repository baseline lint/typecheck diagnostics may remain only when unchanged and outside this task slice. Any new diagnostic in a changed task file is a regression and must be corrected.

## Luna deterministic-execution guardrails

- The file list, key manifest and edit recipe above are the implementation contract. Do not broaden the task into a general UI refactor.
- Do not start while `ARCH-007-SHOPIFY-002` is not Complete.
- Do not edit `/`, `/auth/login`, `privacy.tsx` or `PlanSelector.jsx`.
- Do not invent a new locale, runtime, translator, fallback engine, route or database field.
- Do not change Shopify billing entitlement/policy while localising status labels.
- Do not change merchant-support message bodies, translation pipeline, CTA destinations or tenant resolution.
- Do not create a repository-wide hard-coded-English lint rule.
- Do not modify another repository.
- Do not start `ARCH-005-SYSTEM-TEST-001` after this task; return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-005-SHOPIFY-004` branch and the mirrored parent-workspace `task/ARCH-005-SHOPIFY-004` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status

Pending

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending

### Follow-up

After `ARCH-007-SHOPIFY-002` is architect-accepted Complete, moda_architect may move this task from `pending` to `ready` if the other dependencies remain Complete.
