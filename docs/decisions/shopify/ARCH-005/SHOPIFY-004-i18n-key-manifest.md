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
