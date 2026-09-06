---
id: ARCH-005
title: Global internationalisation and WhatsApp market support
status: in_progress
coordinator: moda_architect
created: 2026-09-05
updated: 2026-09-06
---

# ARCH-005: Global internationalisation and WhatsApp market support

## Status

In Progress.

Immediate executable task:

```text
ARCH-005-MESSAGING-003
```

All accepted runtime internationalisation implementation has completed. The remaining implementation work is a bounded Messaging cleanup that removes the unused selector left by the superseded MESSAGING-001 attempt before terminal system validation begins.

The Shopify buyer-context producer/consumer rollout is complete:

```text
SHARED-003 implementation — Complete
        |
        v
SHARED-004 publication — Complete
        |
        v
BACKGROUND-001 consumer adoption/materialisation — Complete
        |
        v
SHOPIFY-003 producer emission — Complete
```

Architect review of the first Messaging-owned template task then exposed a
separate runtime-ownership issue: proactive template selection/send and active
conversation/CommerceAgent processing execute in Background, not the stateless
Messaging ingress service. Those capabilities are now rehomed to
`BACKGROUND-002`, `BACKGROUND-003` and `BACKGROUND-004`. `SHOPIFY-001` and
`SHOPIFY-002` remain independently Ready.

Architect review has accepted `BACKGROUND-002`, `BACKGROUND-003` and `BACKGROUND-004`. The proactive approved-template selection/send path and active-conversation language/CommerceAgent path are Complete. A final bounded Messaging cleanup (`MESSAGING-003`) removes the unused selector residue from the superseded Messaging attempt before terminal system validation.

## Goal

Make Moda Interact internationally correct by design so the platform can serve
merchants and customers across WhatsApp-supported markets without coupling:

```text
country
language
locale
currency
time zone
telephone country
```

or requiring new application code for every additional language/market.

The target architecture must support arbitrary standards-based international
context and a data-driven WhatsApp template catalogue.

## Core principles

### 1. Country is not language

Never derive a customer's language permanently from:

```text
phone number
country
currency
merchant locale
```

Examples that must remain valid:

```text
country = CH
languageTag = fr
currencyCode = CHF

country = GB
languageTag = pl
currencyCode = GBP

country = DE
languageTag = en
currencyCode = EUR
```

### 2. Standards are canonical

Use:

```text
language / locale  -> BCP-47 language tag
country            -> ISO 3166-1 alpha-2
currency           -> ISO 4217
phone              -> E.164
time zone          -> IANA time-zone identifier
timestamps         -> UTC instants
```

Examples:

```text
en-GB
fr-FR
pt-BR
ar
GB
FR
BR
GBP
EUR
BRL
Europe/London
America/Sao_Paulo
```

Provider-specific codes are mapped at provider boundaries and are not the
canonical Moda representation.

### 3. International context has provenance

A resolved language must retain how it was chosen.

Canonical source vocabulary:

```text
customer-explicit
detected
shopify
merchant-default
platform-default
```

The architecture must be able to distinguish:

```text
languageTag = fr-FR
languageSource = detected
```

from:

```text
languageTag = fr-FR
languageSource = shopify
```

### 4. Money belongs to commerce data

Currency comes from the checkout/order/commerce context.

Do not infer currency from language.

Do not construct money strings manually.

Rendering uses locale-aware formatting at the presentation boundary.

### 5. Time is stored as UTC

Persist/schedule instants as UTC.

A time zone is contextual metadata used for display and future local-time
policy decisions.

Do not persist presentation strings such as:

```text
5 September at 3pm
```

as authoritative time values.

### 6. Phone country is not customer locale

E.164 remains the canonical phone format.

Telephone calling-code interpretation may be used only for telephone/provider
routing where required.

It must not overwrite:

```text
languageTag
countryCode
currencyCode
timeZone
```

derived from stronger commerce/customer context.

## Logical international context

The canonical logical context is:

```text
InternationalContext
  languageTag: string | null
  languageSource:
      customer-explicit
      detected
      shopify
      merchant-default
      platform-default
      null

  countryCode: string | null
  currencyCode: string | null
  timeZone: string | null
```

Not every source can populate every field.

Unknown values remain null and are resolved through explicit fallback rules.

Do not invent international context.

## Merchant defaults

Each merchant needs independently configurable fallback defaults:

```text
defaultLanguageTag
defaultTimeZone
defaultCountryCode   (optional)
```

For Shopify merchants these values are initialised, when available, from
independent authoritative store configuration:

```text
primary ShopLocale             -> defaultLanguageTag
Shop.ianaTimezone              -> defaultTimeZone
Shop.shopAddress.countryCodeV2 -> defaultCountryCode
```

The initial Shopify values seed a missing `ShopSettings` row only. Ordinary
authenticated shop resolution must not silently overwrite later merchant edits.

ARCH-005 does not persist a merchant default currency in `ShopSettings`.
Checkout/order presentment currency remains commerce-object data and is never
used to infer merchant or customer language.

Merchant defaults are fallback inputs, not customer identity.

## Customer/conversation language resolution

The resolved customer conversation language follows this priority:

```text
1. explicit customer preference
2. confident language detected from customer conversation
3. Shopify/customer/checkout language context
4. merchant default language
5. platform fallback
```

A detected language may change during an active conversation when the customer
clearly changes language.

Short/ambiguous messages must not cause uncontrolled language flapping.

The resolver must expose both:

```text
languageTag
languageSource
```

## Proactive WhatsApp templates

Proactive WhatsApp messages must use provider-approved template variants.

Moda MUST NOT:

```text
translate a template ad hoc with the LLM
and submit that text as if it were an approved provider template
```

The logical template catalogue is:

```text
purpose
tenant / WhatsApp account
canonical languageTag
providerLanguageCode
providerTemplateName
provider status
enabled
```

Example purpose:

```text
abandoned_cart_initial
```

Possible variants:

```text
en-GB
en-US
fr
de
es
pt-BR
it
ar
...
```

Architecture must not impose a fixed language list.

Adding an approved language variant should primarily be a data/configuration
operation.

## Template fallback

Template selection must be deterministic.

Recommended policy:

```text
resolved customer language
        |
        v
exact approved variant?
        |
       no
        v
approved base-language variant?
        |
       no
        v
merchant configured fallback language?
        |
       no
        v
platform fallback if explicitly enabled?
        |
       no
        v
do not send + bounded operational reason
```

Every selected provider template must be:

```text
approved
enabled
owned by the correct tenant/provider account
```

The persisted catalogue must guarantee that each selector step resolves to at
most one selectable variant for the tenant/provider account, purpose and
canonical language being queried.

Do not silently send an unapproved locale.

## Active-conversation AI language

Once customer messaging is inside an active conversation, CommerceAgent should
respond in the accepted conversation language unless the latest substantive
customer message itself clearly establishes a different language **and no stronger
explicit customer preference is active**.

Do not add a second language-detection model call. The existing CommerceAgent
LLM/tool run owns the natural-language turn and returns one schema-validated final
result containing both the reply and bounded language metadata.

The current production provider is Groq `openai/gpt-oss-20b`. Groq currently
supports local tool calling but documents Structured Outputs as incompatible with
tool use. Therefore the production agent MUST NOT combine `Output.object(...)`
with `searchProducts`. Instead, the same tool loop terminates through an internal,
side-effect-free final-response tool whose validated input is:

```text
replyText
detectedLanguageTag | null
detectedLanguageConfidence | null
```

Conceptually:

```text
inbound message persisted / inboundVersion advanced
      |
      v
CommerceAgent existing Groq LLM + tool loop
      |
      +--> searchProducts when factual product data is needed
      |
      +--> finalResponse tool (schema-validated, no external side effect)
             +--> replyText
             +--> detectedLanguageTag | null
             +--> detectedLanguageConfidence | null
      |
      v
application stability + confidence + explicit-preference policy
      |
      v
version-guarded Conversation language/source update when accepted
      |
      v
send replyText
```

This preserves one AI invocation, provider-compatible tool grounding and one
validated final result without a second AI request solely for language
classification/finalisation.

Language adaptation must not alter factual commerce data. Product names, URLs,
prices, order state and merchant policies remain grounded in authoritative source
data.

## Language detection

The application boundary remains provider-agnostic, but detection metadata is
produced as part of the existing CommerceAgent run rather than by a standalone
production detector service.

The bounded model result is:

```text
detectedLanguageTag
detectedLanguageConfidence
```

No model reasoning/explanation is persisted. Application code owns BCP-47
validation, confidence thresholding, stability/anti-flapping and durable state
mutation.

Text-only detection must not invent regional specificity. If an existing durable
locale is more specific and the detected base language is unchanged, preserve the
durable locale:

```text
current en-GB + detected en -> keep en-GB
current fr-CA + detected fr -> keep fr-CA
```

A confident different-base-language switch may update the conversation, for
example `en-GB -> fr`, **unless** the current durable language source is
`customer-explicit`. Explicit customer preference remains stronger than ordinary
message-language detection until replaced by another trusted explicit preference.
Country, currency, phone country, Shopify Market and shipping geography are never
language-detection inputs.

A stale CommerceAgent result must not mutate language after a newer inbound
message has advanced the conversation version.

## Shopify context

Shopify is a source of several **independent** international signals. It is not
a global source of truth from which one dimension may be inferred from another.

### Merchant/store defaults

At the existing authenticated shop-resolution boundary, Moda may obtain the
merchant fallback values required by ARCH-005:

```text
primary ShopLocale             -> defaultLanguageTag
Shop.ianaTimezone              -> defaultTimeZone
Shop.shopAddress.countryCodeV2 -> defaultCountryCode
```

The Shopify app requires the read-only scopes:

```text
read_locales
read_markets
```

`read_locales` supports authoritative primary-store-locale resolution.
`read_markets` establishes the Shopify Markets read permission boundary while
Moda is still pre-production. ARCH-005 does not require persisting a local copy
of every Shopify Market merely because that scope exists.

Do not use `Session.locale` as the merchant default language: it describes the
authenticated Admin user's locale, not necessarily the shop/storefront primary
locale.

### Buyer webhook snapshot

Where the actual checkout/order webhook payload contains buyer-specific values,
the Shopify producer may preserve them independently in canonical context:

```text
customer_locale                -> languageTag / source=shopify
presentment_currency           -> currencyCode
billing_address.country_code   -> countryCode
shipping_address.country_code  -> fulfilment only; never canonical buyer country
```

A missing dimension remains null. Never manufacture one dimension from another.
`countryCode` is buyer/localisation context, not fulfilment geography. A shipping
destination may represent a gift recipient and therefore MUST NOT populate
canonical buyer `countryCode` or buyer `timeZone`. Prefer verified explicit
buyer/market context when genuinely available, otherwise purchaser/billing
context, then independent event/merchant fallbacks.

These are hard invariants:

```text
NEVER derive languageTag from currencyCode.
NEVER derive languageTag solely from countryCode or market.
NEVER derive currencyCode from languageTag or countryCode.
NEVER derive countryCode from telephone country.
```

Cross-combinations are valid and must survive unchanged, for example:

```text
languageTag = fr-CA
countryCode = CA
currencyCode = USD
```

### Current abandoned-checkout action-path data

The Background recovery flow already performs a bounded Shopify Admin lookup
when a pending abandoned-checkout candidate matures. ARCH-005 reuses that
existing action-path lookup to obtain current authoritative checkout information
where the configured Shopify API exposes it, including:

```text
presentment money/currency
verified buyer/purchaser country (billing fallback; never shipping destination)
buyer/purchaser time zone when directly supplied (never shipping destination)
customer locale when directly supplied
```

This enrichment must not create a second provider lookup and must not move a
Shopify API call into the common webhook/irrelevant-event hot path.

Webhook `customer_locale`, when present, is stronger evidence of the buyer's
checkout language than a generic customer-profile locale. Current checkout
presentment currency is stronger commerce evidence than shop/base currency.

### Shopify Markets

Moda must be deployable to merchants using Shopify Markets without hard-coded
country/language/currency coupling. Markets are therefore an explicit provider
capability/context boundary, but ARCH-005 does not require:

```text
a local replica of all Market objects
a marketId on every recovery
market currency -> language inference
market country -> language inference
```

Additional Market-specific persistence should be introduced only when a concrete
Moda capability requires it and the authoritative mapping is available without
violating the Shopify ingress scalability boundary.

## WhatsApp market support

Do not hard-code a giant country switch in business logic.

Support is determined through a provider/tenant capability boundary.

Conceptually:

```text
destination / commerce country
        |
        v
provider/tenant capability
        |
        +-- messaging permitted
        |
        +-- messaging unavailable/restricted
        |
        +-- unknown/provider check required
```

Provider availability and template availability are separate concerns.

The architecture must allow capability/configuration changes without adding a
new branch for each country.

## Merchant UI internationalisation

Merchant UI locale is independent from customer conversation language.

The merchant application should gain:

```text
translation catalogue infrastructure
merchant UI locale resolution
Intl-based money/date/number formatting
```

Architecture must support arbitrary BCP-47 locales.

Initial translation catalogues may be introduced incrementally; the framework
must not constrain future language additions.

Merchant UI strings and customer WhatsApp strings are separate catalogues.

## Formatting

Use standards-aware formatting facilities.

Examples:

```text
Intl.NumberFormat
Intl.DateTimeFormat
Intl.PluralRules
```

or an equivalent repository-approved internationalisation library.

Never hard-code:

```text
"$" + amount
amount + " EUR"
MM/DD/YYYY
DD/MM/YYYY
```

as universal formats.

Formatting must not change stored canonical values.

## RTL

The internationalisation framework must not assume left-to-right text.

Merchant/customer rendering components touched by ARCH-005 should avoid
directional assumptions and preserve the ability to render:

```text
dir=auto
```

or locale-derived direction where appropriate.

A complete visual redesign for RTL is not required in this architecture, but
new internationalisation primitives must not block it.

## Database model

ARCH-005 requires persistence for two concerns.

### International context

Persist merchant defaults and conversation/customer-facing resolved context
using the existing most appropriate entities.

Logical fields:

```text
merchant:
  defaultLanguageTag
  defaultTimeZone
  defaultCountryCode

conversation/context:
  languageTag
  languageSource
  countryCode
  currencyCode
  timeZone
```

Exact table placement is a database implementation decision after inspection of
the current ERD/schema.

Avoid duplicating the same authoritative field across several tables unless a
snapshot is intentionally required.

### WhatsApp template variants

Extend existing template storage if it exists; otherwise add the minimal
provider-template catalogue required for locale-aware selection.

Two different uniqueness invariants apply and MUST NOT be conflated.

Provider-record identity:

```text
tenant/provider account
purpose
provider template identity
provider language code
```

This identifies the provider template variant itself. Canonical `languageTag`
is deliberately not part of provider identity because canonical BCP-47 mapping
and provider language codes are separate concepts.

Selectable-template identity:

```text
tenant/provider account
purpose
canonical languageTag
WHERE enabled = true
  AND provider status = APPROVED
```

For one tenant/provider account/purpose/canonical language, at most one stored
variant may be simultaneously selectable. This is a database integrity
invariant required by deterministic Messaging selection.

Multiple stored variants for the same canonical language are allowed when they
are not simultaneously selectable. For example, an existing approved/enabled
template may coexist with a pending or disabled replacement.

Do NOT enforce unconditional uniqueness on only:

```text
tenant/provider account/purpose/canonical languageTag
```

because that would prevent retaining a pending replacement beside the active
variant. Do not resolve ambiguity in Messaging with arbitrary ordering such as
`createdAt DESC`; invalid selectable configuration should be prevented at the
database boundary.

Store canonical language mapping separately from provider codes when needed.

## Context propagation

International context follows the existing recovery/messaging path, but merchant
defaults and buyer-specific context have separate acquisition paths:

```text
authenticated Shopify shop resolution
        |
        v
ShopSettings merchant fallbacks

Shopify checkout/order webhook snapshot
        |
        v
optional canonical shared event context
        |
        v
Background pending candidate
        |
        +---- existing matured-recovery abandoned-checkout lookup
        |
        v
field-by-field resolved recovery/conversation context
        |
        v
Messaging template / CommerceAgent context
```

The shared event extension is additive and optional so legacy V2 events remain
valid. Because the existing consumer schema is strict, rollout is consumer-first:
Background must adopt the published optional field before Shopify begins emitting
it.

Do not make every downstream service re-query Shopify for information already
captured upstream. Conversely, do not duplicate the existing bounded Background
abandoned-checkout lookup merely to fill international metadata.

## Security / privacy

Internationalisation must not increase PII exposure.

Do not add customer language/country/phone to high-cardinality telemetry labels.

Operational metrics use bounded attributes such as:

```text
template purpose
selection outcome
language source
```

A raw `languageTag` may only be used as a metric dimension if the implementing
agent demonstrates bounded cardinality and the metric is operationally
necessary. Prefer grouped/bounded outcomes.

## Observability

Required bounded outcomes include:

```text
international-context resolution source
template selected
template fallback used
template unavailable
market unavailable
language detected / unchanged / changed
```

Do not log:

```text
raw customer message text
phone number
email
full address
```

merely for localisation diagnostics.

## Rolling compatibility

ARCH-005 is deployed across several repositories.

Shared contracts must be additive and backward compatible where possible.

Database changes must support rolling deployment.

Consumers must tolerate:

```text
null international context
legacy conversations without language metadata
legacy template records without canonical language mapping
```

until migration/backfill is complete.

## Non-goals

ARCH-005 does not:

- promise that every Meta/WhatsApp market is commercially available to every
  merchant account;
- bypass Meta/provider template approval;
- auto-translate proactive templates outside provider approval;
- translate the internal Admin/operations application in this phase;
- translate product data that Shopify/merchant sources do not provide;
- infer customer language solely from telephone number;
- implement local quiet-hour policy;
- rewrite existing timestamps into local strings in storage;
- introduce country-specific business-logic branches.

## Representative verification locales

System tests should use representative international combinations such as:

```text
en-GB / GB / GBP / Europe/London
fr-FR / FR / EUR / Europe/Paris
pt-BR / BR / BRL / America/Sao_Paulo
ar / suitable market/currency / RTL-capable rendering boundary
```

These are test representatives, not an allowlist.

The architecture must accept additional valid standards-based locales without
new business-logic branches.

## Runtime ownership correction — WhatsApp selection and conversation language

Architect review of `ARCH-005-MESSAGING-001` confirmed that
`moda-interact-messaging` is the stateless Meta/WhatsApp **inbound ingress**
boundary. It does not own Prisma, the proactive recovery workflow, outbound
WhatsApp sending or CommerceAgent execution. Those runtime paths live in
`moda-interact-background`.

Therefore the earlier Messaging-owned implementation tasks are superseded and
rehomed to Background:

```text
MESSAGING-001  -> BACKGROUND-002  deterministic approved-template selection
                                  using the real DATABASE-002 catalogue

                -> BACKGROUND-003  proactive provider-template send integration
                                  in the existing recovery workflow

MESSAGING-002  -> BACKGROUND-004  active-conversation language resolution and
                                  CommerceAgent language context
```

The pure selector produced during the superseded Messaging task is **not** an accepted runtime capability in `moda-interact-messaging` and must not remain there merely to satisfy unit tests. `ARCH-005-MESSAGING-003` removes that residue after the accepted Background replacement is complete.

### Market capability semantics

Pre-send market capability has three states:

```text
supported
  -> selected template may proceed to provider send

unsupported
  -> bounded market-unavailable; do not send

unknown / provider-check-required
  -> do NOT fabricate support and do NOT fabricate unavailability
  -> preserve the selected approved template
  -> allow the provider send boundary to make the authoritative decision
  -> map an actual provider rejection into a bounded operational outcome
```

`unknown` therefore must not be represented as `market-unavailable`. This is
important for global deployment because lack of a locally maintained country
allowlist is expected; Moda must not block otherwise valid markets merely
because it cannot pre-compute Meta capability.

### Proactive versus active-conversation ownership

The initial abandoned-cart recovery is proactive provider-template work. The
current Background implementation still calls `WhatsAppService.sendWhatsAppText`
from the recovery workflow, so approved-template selection is not complete until
the selected provider template is actually used by that outbound path.

Free-form responses after the customer is in an active conversation remain a
separate capability. Language resolution and CommerceAgent execution occur in
Background's WhatsApp worker and therefore also belong to Background rather than
the inbound Messaging service.

Architect review of BACKGROUND-004 Attempt 1 further clarified that active-message
language detection must not create a second AI/provider invocation. The configured
CommerceAgent already sees the message and performs the natural-language turn, so
its validated final-result tool supplies bounded detected-language metadata for
the application-owned resolver to accept or reject. The current Groq provider
must not be sent Structured Outputs together with tools.

## Task graph

```text
ARCH-005-SHARED-001
        |
        +---------------------> DATABASE-001
        |                           |
        v                           v
ARCH-005-SHARED-002           DATABASE-002
        |                           |
        +---------------------> SHOPIFY-001
        |
        +---------------------> SHOPIFY-002
        |
        v
ARCH-005-SHARED-003
        |
        v
ARCH-005-SHARED-004
        |
        v
ARCH-005-BACKGROUND-001 <----- DATABASE-001
        |
        +---------------------> SHOPIFY-003
        |
        +---------------------> BACKGROUND-002 <----- DATABASE-002
        |                              |
        |                              v
        |                        BACKGROUND-003
        |                              |
        |                              v
        |                        MESSAGING-003
        |
        +---------------------> BACKGROUND-004

SHOPIFY-001 + SHOPIFY-002 + SHOPIFY-003 + BACKGROUND-001 +
BACKGROUND-002 + BACKGROUND-003 + MESSAGING-003
        |
        v
SYSTEM-TEST-001
        |
        v
SYSTEM-TEST-002  <----- BACKGROUND-004
```

More precisely:

```text
DATABASE-001 depends on SHARED-001
DATABASE-002 depends on DATABASE-001
SHOPIFY-001 depends on SHARED-002 + DATABASE-001
SHOPIFY-002 depends on SHARED-002 + DATABASE-001
SHARED-003 depends on SHARED-002
SHARED-004 depends on SHARED-003
BACKGROUND-001 depends on SHARED-004 + DATABASE-001
SHOPIFY-003 depends on SHARED-004 + BACKGROUND-001
BACKGROUND-002 depends on BACKGROUND-001 + DATABASE-002
BACKGROUND-003 depends on BACKGROUND-002
BACKGROUND-004 depends on BACKGROUND-001
MESSAGING-003 depends on BACKGROUND-002 + BACKGROUND-003
SYSTEM-TEST-001 depends on SHOPIFY-001 + SHOPIFY-002 + SHOPIFY-003 + BACKGROUND-001 + BACKGROUND-002 + BACKGROUND-003 + MESSAGING-003
SYSTEM-TEST-002 depends on SYSTEM-TEST-001 + BACKGROUND-004
```

The `BACKGROUND-001 -> SHOPIFY-003` edge remains a rollout dependency, not a
domain ownership inversion: Background first tolerated the optional event field
because the legacy V2 consumer was strict. Shopify remains the producer owner.

`BACKGROUND-002` and `BACKGROUND-004` may execute independently.
`BACKGROUND-003` follows `BACKGROUND-002` because provider send must consume an
architect-accepted deterministic selection result.

For repository/submodule dependencies, architectural completion also requires the
consumer to adopt the developer-published revision containing the accepted
capability. A dependency task marked `complete` is not sufficient if the
consumer still compiles against an older submodule/schema. Agents must update and
verify the dependency; they must not compensate with raw SQL, duplicate schema or
stale-client casts.

## Tasks

```text
ARCH-005-SHARED-001
  Define canonical international-context contracts

ARCH-005-SHARED-002
  Publish internationalisation shared contract release

ARCH-005-DATABASE-001
  Persist merchant and conversation international context

ARCH-005-DATABASE-002
  Persist locale-aware WhatsApp template variants

ARCH-005-SHARED-003
  Extend Shopify recovery events with canonical international context

ARCH-005-SHARED-004
  Publish Shopify international-context event contract

ARCH-005-SHOPIFY-001
  Initialise Shopify merchant international defaults

ARCH-005-SHOPIFY-002
  Introduce merchant UI locale and standards-aware formatting

ARCH-005-BACKGROUND-001
  Adopt and materialise Shopify international context

ARCH-005-SHOPIFY-003
  Emit canonical buyer international context on Shopify recovery events

ARCH-005-MESSAGING-001
  Superseded — runtime template selection belongs to Background

ARCH-005-MESSAGING-002
  Superseded — conversation language / CommerceAgent belongs to Background

ARCH-005-MESSAGING-003
  Remove superseded Messaging template-selector residue

ARCH-005-BACKGROUND-002
  Select approved WhatsApp templates by locale and market capability

ARCH-005-BACKGROUND-003
  Send selected approved WhatsApp template on proactive recovery path

ARCH-005-BACKGROUND-004
  Resolve active-conversation language through CommerceAgent structured output

ARCH-005-SYSTEM-TEST-001
  Verify multi-market context and proactive template selection/send

ARCH-005-SYSTEM-TEST-002
  Verify multilingual conversation language behaviour
```

## Current execution state

```text
ARCH-005-SHARED-001      Complete
ARCH-005-SHARED-002      Complete
ARCH-005-DATABASE-001    Complete
ARCH-005-DATABASE-002    Complete
ARCH-005-SHARED-003      Complete
ARCH-005-SHARED-004      Complete
ARCH-005-BACKGROUND-001  Complete
ARCH-005-SHOPIFY-001     Complete
ARCH-005-SHOPIFY-002     Complete
ARCH-005-SHOPIFY-003     Complete
ARCH-005-MESSAGING-001   Superseded
ARCH-005-MESSAGING-002   Superseded
ARCH-005-MESSAGING-003   Ready
ARCH-005-BACKGROUND-002  Complete
ARCH-005-BACKGROUND-003  Complete
ARCH-005-BACKGROUND-004  Complete
ARCH-005-SYSTEM-TEST-001 Pending
ARCH-005-SYSTEM-TEST-002 Pending
```

Immediate implementation work is:

```text
MESSAGING-003
```

After `MESSAGING-003` is architect-accepted, `SYSTEM-TEST-001` may become Ready because all of its implementation dependencies will then be Complete.

For the proactive WhatsApp path:

```text
DATABASE-002 — Complete
BACKGROUND-001 — Complete
        |
        v
BACKGROUND-002 — Complete
        |
        v
BACKGROUND-003 — Complete
```

System validation remains terminal and must not become Ready until every listed
implementation dependency is Complete and architect-accepted.

## Architecture acceptance

ARCH-005 is Complete only when:

- country/language/currency/time zone remain independent;
- canonical standards-based validation exists;
- merchant defaults and conversation context persist;
- Shopify merchant defaults are initialised from authoritative independent store
  sources without overwriting later merchant configuration;
- `read_locales` and `read_markets` establish the required pre-production
  read-only Shopify international/Markets permission boundary;
- checkout/order presentment currency remains authoritative for buyer commerce
  values and never determines language;
- buyer checkout `customer_locale`, purchaser/buyer country and presentment currency can be
  preserved independently, including valid cross-combinations such as
  `fr-CA / CA / USD`;
- shipping/delivery geography never overwrites canonical buyer country or buyer
  timezone;
- Shopify Markets support does not couple market/country/currency to language;
- Shopify-derived context is captured without inventing unavailable fields;
- Background reuses the existing bounded matured-recovery checkout lookup and
  does not add provider calls to the irrelevant-event hot path;
- the optional Shopify event-context contract is rolled out consumer-first;
- proactive WhatsApp template selection uses only approved variants;
- locale fallback is deterministic and auditable;
- missing template variants fail safely rather than ad-hoc translating;
- active conversations can resolve/update customer language;
- telephone country cannot overwrite customer language;
- merchant UI uses locale-aware formatting primitives;
- representative multi-market system tests pass;
- adding a new supported language/template variant is primarily data/config,
  not a new country switch in application logic.
