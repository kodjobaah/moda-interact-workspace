# ARCH-005-SHOPIFY-004 — Canonical i18n key manifest

This is the architect-owned implementation input for `ARCH-005-SHOPIFY-004`.
It defines **new** authenticated Shopify app-shell/support UI message keys only.
The retired additional/example route, already-internationalised navigation and Guest
fallback, and removed raw subscription-status presentation are not part of this task.

The English source strings below are exact. Add each listed key to every one of the
20 existing locale catalogues, preserving the complete pre-existing catalogue.

| Key | Exact English source / semantic value |
|---|---|
| `common.logoAlt` | `Moda Interact logo` |
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

### Locale catalogues

```text
cs.json       Czech
da.json      Danish
de.json      German
en.json      English, canonical source
es.json      Spanish
fi.json      Finnish
fr.json      French
it.json      Italian
ja.json      Japanese
ko.json      Korean
nb.json      Norwegian Bokmål
nl.json      Dutch
pl.json      Polish
pt-BR.json   Brazilian Portuguese
pt-PT.json   European Portuguese
sv.json      Swedish
th.json      Thai
tr.json      Turkish
zh-Hans.json Simplified Chinese
zh-Hant.json Traditional Chinese
```

- Translate the meaning of each key naturally in each target language. Do not use
  English filler values in non-English catalogues; invariant brand names are an
  exception, but the surrounding UI wording must still be translated.
- Preserve `Moda Interact` and `Moda Support` where they appear as brand names.
- Preserve ICU placeholder identifiers exactly: `support.page` uses `{page}`
  and `{totalPages}`; `support.messageLengthError` uses `{max}`.
- Retain distinctions between `pt-BR`/`pt-PT` and `zh-Hans`/`zh-Hant`.
- Do not add keys beyond this manifest, a new locale, a new translator or a fallback engine.
- Never rename or remove any pre-existing catalogue key. `en.json` must contain
  precisely the English values defined above for these new keys.
- `support.modaSupport` is intentionally invariant as a brand label. Tests
  comparing translated strings must choose semantically translatable keys.
