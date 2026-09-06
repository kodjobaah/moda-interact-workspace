# ARCH-005 Internationalisation and Global WhatsApp Markets — Overview

> Companion overview for the canonical architecture decision:
> [`ARCH-005-global-internationalisation-whatsapp-markets.md`](ARCH-005-global-internationalisation-whatsapp-markets.md)
>
> The canonical `ARCH-005` architecture and task files remain authoritative for
> implementation state. This document explains the product and system design in
> a more readable form.

## Purpose

Moda Interact is intended to serve Shopify merchants and customers across
WhatsApp-supported markets without treating **country**, **language**,
**currency**, **time zone**, and **telephone country** as the same thing.

The architecture therefore starts from one rule:

```text
Country != Language != Currency != Time zone != Telephone country
```

Examples that must remain valid include:

```text
Switzerland + French + CHF
United Kingdom + Polish + GBP
Germany + English + EUR
Brazil + Portuguese + BRL
```

A customer's phone number must never become a permanent proxy for the language
in which Moda communicates with them.

## Product outcomes

ARCH-005 is designed so that Moda can:

- understand international Shopify commerce context;
- preserve the checkout/order currency supplied by Shopify;
- choose the appropriate language for a customer conversation;
- select an approved WhatsApp template variant for proactive messaging;
- continue an active AI conversation in the customer's language;
- format merchant-facing money, dates, numbers and times correctly;
- support right-to-left languages without embedding left-to-right assumptions;
- add new languages and markets mainly through configuration/data rather than
  country-specific application branches.

The architecture supports standards-based international context rather than a
hard-coded list of "supported Moda countries".

## Canonical standards

Moda uses established identifiers throughout the platform:

| Concern | Canonical standard | Examples |
| --- | --- | --- |
| Language / locale | BCP-47 | `en-GB`, `fr-FR`, `pt-BR`, `ar` |
| Country | ISO 3166-1 alpha-2 | `GB`, `FR`, `BR` |
| Currency | ISO 4217 | `GBP`, `EUR`, `BRL` |
| Phone | E.164 | `+447...`, `+5511...` |
| Time zone | IANA | `Europe/London`, `America/Sao_Paulo` |
| Stored timestamps | UTC instant | `2026-09-05T14:00:00Z` |

Provider-specific values are mapped at provider boundaries. For example, a
Meta/WhatsApp provider language code is not automatically the canonical Moda
BCP-47 language tag.

## International context

The logical context carried through the system is deliberately independent:

```text
InternationalContext
  languageTag
  languageSource
  countryCode
  currencyCode
  timeZone
```

Values may be unknown. Unknown values stay `null`; they are not invented.

Language also carries provenance:

```text
customer-explicit
detected
shopify
merchant-default
platform-default
```

This makes it possible to distinguish a language chosen by the customer from a
fallback language inherited from the merchant.

## Customer language resolution

The intended precedence is:

```text
explicit customer preference
        |
        v
confident language detected from conversation
        |
        v
Shopify/customer/checkout language context
        |
        v
merchant default language
        |
        v
platform fallback
```

A customer may change language during a conversation. Short or ambiguous
messages must not cause the conversation language to flap unpredictably.

The detected/resolved language belongs to the customer conversation, not to the
merchant account as a whole.

## Merchant language is separate

The Shopify merchant UI has its own locale.

```text
Merchant UI locale  !=  Customer conversation language
```

A French-speaking merchant can operate a store whose customers converse in
English, German, Arabic, Spanish and Portuguese. Changing the merchant UI
language must not change customer WhatsApp conversations.

## Shopify integration

Shopify is an international-commerce context source, not the sole source of
truth for language.

Where the current Shopify APIs/webhooks actually provide them, Moda can capture:

```text
locale/language context
country/market context
checkout/order currency
merchant/store locale and timezone defaults
```

The integration must only map real provider fields whose meaning is understood.
Missing optional fields remain unknown rather than triggering speculative
lookups or inferred values.

The checkout or order remains authoritative for its own currency.

## Proactive WhatsApp messages

Proactive WhatsApp communication uses provider-approved template variants.

Conceptually:

```text
abandoned_cart_initial
  +-- en-GB
  +-- en-US
  +-- fr
  +-- de
  +-- es
  +-- pt-BR
  +-- ar
  +-- ...
```

Each variant maps canonical Moda language context to the provider's approved
template identity and provider language code.

Selection is deterministic:

```text
resolved customer language
        |
        v
exact approved variant?
        |
       no
        v
approved configured base-language fallback?
        |
       no
        v
merchant configured fallback?
        |
       no
        v
platform fallback explicitly allowed?
        |
       no
        v
do not send + bounded operational reason
```

Moda must never translate a proactive template with an LLM on the fly and then
submit the result as though Meta had approved that template.

## Active AI conversations

Active customer conversations are a different problem from proactive template
approval.

Once the WhatsApp conversation is active:

```text
inbound customer message
        |
        v
language resolution/detection
        |
        v
Conversation.languageTag + languageSource
        |
        v
CommerceAgent
        |
        v
reply in resolved customer language
```

The model may express authoritative commerce information in another language,
but it must not invent or transform the underlying facts. Prices, currencies,
URLs, order status and merchant policies continue to come from structured
sources.

## Money, dates and time zones

Canonical values remain canonical; localisation happens at presentation
boundaries.

For example, money is rendered using the explicit commerce currency:

```text
en-GB + GBP -> £49.99
de-DE + EUR -> 49,99 €
fr-FR + EUR -> 49,99 €
pt-BR + BRL -> R$ 49,99
```

The application uses `Intl.NumberFormat`, `Intl.DateTimeFormat`,
`Intl.PluralRules`, or equivalent approved primitives rather than manually
concatenating symbols or assuming one date format.

Timestamps stay UTC in storage. Merchant/customer time zones are presentation
and future policy inputs.

## WhatsApp market capability

Provider/tenant capability is kept separate from language and template
availability.

```text
commerce/destination context
        |
        v
provider / tenant capability
        |
        +-- permitted
        +-- unavailable/restricted
        +-- unknown/provider check required
```

The architecture does not embed a giant `switch(country)` throughout business
logic. Provider availability can change independently of Moda releases.

## Data and service ownership

ARCH-005 spans several repositories:

| Repository / agent | Internationalisation responsibility |
| --- | --- |
| `moda-interact-shared` / `moda_shared` | Canonical language/country/currency/time-zone contracts |
| `moda-interact-database` / `moda_database` | Merchant defaults, conversation context and template variants |
| `moda-interact` / `moda_app` | Shopify context capture and merchant UI localisation |
| `moda-interact-background` / `moda_background` | Propagate international context; select/send approved proactive WhatsApp templates; resolve active-conversation language; execute/localise CommerceAgent turns |
| `moda-interact-messaging` / `moda_messaging` | Stateless Meta/WhatsApp inbound webhook ingress, validation/normalisation and publication of inbound events |
| `moda-interact-system-test` / `moda_system_test` | Multi-market and multilingual integrated verification |

## Representative verification

Representative test combinations include:

```text
en-GB / GB / GBP / Europe/London
fr-FR / FR / EUR / Europe/Paris
pt-BR / BR / BRL / America/Sao_Paulo
ar / representative market / RTL-capable presentation
```

These are test cases, not an allowlist. The system must be able to accept new
valid standards-based locales without adding country-specific business logic.

## Relationship to ARCH-006

ARCH-006, the internal merchant support inbox, reuses ARCH-005 language
primitives. It does not create another language model.

For example:

```text
Shop.defaultLanguageTag
        |
        +--> merchant UI localisation
        |
        +--> ARCH-006 support-message display language
```

ARCH-006 translations preserve the original message and create separate target
language translations using the same canonical BCP-47 rules.

## Implementation documentation

Canonical architecture:

- [`ARCH-005-global-internationalisation-whatsapp-markets.md`](ARCH-005-global-internationalisation-whatsapp-markets.md)

Task ownership is under:

```text
docs/decisions/shared/ARCH-005/
docs/decisions/database/ARCH-005/
docs/decisions/shopify/ARCH-005/
docs/decisions/background/ARCH-005/
docs/decisions/messaging/ARCH-005/
docs/decisions/system-test/ARCH-005/
```
