---
id: ARCH-005-SHOPIFY-003
architecture_id: ARCH-005
title: Emit canonical buyer international context on Shopify recovery events
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 50
executor: copilot
claimed_at: 2026-09-06T00:09:19Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-004
  - ARCH-005-BACKGROUND-001
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-06
---

# Emit canonical buyer international context on Shopify recovery events

## Architecture

This is the producer half of the ARCH-005 Shopify -> Background international
context contract.

It deliberately executes **after** BACKGROUND-001 because the existing V2
recovery event parser is strict. Background must first adopt the published
optional `internationalContext` field before Shopify begins emitting it.

Shopify ingress remains a high-volume hot path. This task may only use fields
already present in authenticated webhook payloads; it must not call Shopify APIs
from webhook handling merely to fill optional international metadata.

## Objective

Map buyer-specific international signals that Shopify actually includes in the
current checkout/order webhook payloads into canonical `InternationalContext`
and attach that context to recovery events without inferring one dimension from
another.

## Context

Current Shopify webhook documentation/payload shape includes independent
signals such as:

```text
customer_locale
presentment_currency
billing_address.country_code
shipping_address.country_code  # fulfilment only; not canonical buyer country
```

The current Moda normalizers intentionally discard these fields.

`currency` is not an acceptable substitute for buyer presentment currency when
`presentment_currency` is available.

## Scope

Primary files to inspect/change:

```text
moda-interact/app/services/webhooks/checkout-normalization.ts
moda-interact/app/services/webhooks/order-normalization.ts
moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts
moda-interact/tests/unit/webhooks/shopify-normalization.test.js
moda-interact/tests/unit/webhooks/shopify-webhook-ingress.service.test.js
moda-interact/package.json
moda-interact/package-lock.json
```

Also inspect checkout-update normalisation because Shopify can supply updated
buyer context there. Do not add context to cart events unless the actual cart
payload contains an architect-approved authoritative source.

## Out of Scope

- ShopSettings initialisation; SHOPIFY-001 owns it.
- Shared schema changes/publication; SHARED-003/004 own them.
- Background fallback/persistence; BACKGROUND-001 owns it.
- Shopify Markets API lookups on webhook receipt.
- Market ID invention.
- Language inference from currency/country/phone/market.
- Currency inference from language/country.
- Timezone inference from language.

## Requirements

### Shared package

Adopt the exact package version published by SHARED-004.

Do not locally cast around the schema and do not duplicate
`InternationalContext` validation.

### Language

When `customer_locale` is a non-empty valid value:

```text
languageTag = canonicalised customer_locale
languageSource = shopify
```

If missing/invalid:

```text
languageTag = null
languageSource = null
```

Do not replace missing `customer_locale` with country, currency or
`Session.locale`.

### Currency

Use:

```text
presentment_currency
```

as the buyer/commerce currency snapshot when present and valid.

Do NOT use webhook `currency` as a substitute for presentment currency merely
because it is populated.

### Country

Canonical `countryCode` represents buyer/localisation context, not delivery
destination. At the webhook boundary use purchaser/billing country when present:

```text
billing_address.country_code -> internationalContext.countryCode
```

Do **not** map `shipping_address.country_code` into canonical buyer `countryCode`;
it is fulfilment geography and may belong to a gift recipient or other delivery
destination. If billing/buyer country is unavailable, leave this dimension null
for Background's independent fallback chain rather than substituting shipping.

Do not use:

```text
customer.default_address.country_code
shop country
phone calling country
currency country
shipping destination country
```

as buyer checkout country at this boundary.

### Time zone

Leave webhook `timeZone` null unless the inspected payload contains a direct,
authoritative timezone field with understood semantics. Do not derive timezone
from country/language.

### Event publication

Attach canonical context through the published shared event contract.

The context dimensions remain independent. A valid event such as:

```text
languageTag = fr-CA
countryCode = CA
currencyCode = USD
```

must remain valid without correction.

If all buyer-specific fields are absent, either omit `internationalContext` or
emit the canonical all-null object consistently with the published contract;
choose one behaviour and test it.

### Hot path

No Admin API/Markets API network lookup may be added to checkout/order webhook
processing for ARCH-005 context.

Preserve existing:

```text
webhook authentication
idempotency
event identity
ordering key
queue publication
acknowledgement behaviour
```

## Work Items

- [x] Adopt SHARED-004 package release.
- [x] Extend checkout create/update normalization for `customer_locale`, presentment currency and checkout address country when present.
- [x] Extend order normalization for equivalent independent buyer signals.
- [x] Canonicalise with shared helpers only.
- [x] Attach context through the canonical V2 event contract.
- [x] Keep cart events unchanged unless real source data justifies context.
- [x] Add cross-combination tests proving language/country/currency independence.
- [x] Add null/missing/invalid provider-field tests.
- [x] Prove no new Shopify API lookup occurs in ingress.

## Interfaces / Contracts

Provider -> canonical mapping:

```text
customer_locale                    -> internationalContext.languageTag
                                    -> languageSource = shopify
presentment_currency               -> internationalContext.currencyCode
billing_address.country_code       -> internationalContext.countryCode
shipping_address.country_code      -> no canonical mapping; fulfilment only
no authoritative webhook timezone  -> internationalContext.timeZone = null
```

No mapping between canonical dimensions is permitted.

## Dependencies

- ARCH-005-SHARED-004 — published event contract.
- ARCH-005-BACKGROUND-001 — consumer-first adoption complete.

## Enables

- ARCH-005-SYSTEM-TEST-001.

## Acceptance Criteria

- [x] checkout/order `customer_locale` is canonicalised independently.
- [x] valid locale is marked `languageSource = shopify`.
- [x] `presentment_currency` is used for buyer currency snapshot.
- [x] webhook `currency` is not used to infer presentment currency when the latter is unavailable.
- [x] billing/purchaser country may populate canonical buyer country; shipping destination never does.
- [x] neither country nor currency affects language selection.
- [x] missing international fields remain null/omitted by documented policy.
- [x] no per-webhook Shopify API call is added.
- [x] legacy event identity/idempotency/ordering semantics remain intact.
- [x] strict shared runtime validation accepts emitted events.
- [x] focused/full tests, typecheck, lint, build and diff checks pass subject to baseline.

## Validation

Include fixtures such as:

```text
customer_locale=fr-CA, country=CA, presentment_currency=USD
customer_locale=en-GB, billing_country=GB, shipping_country=FR, presentment_currency=GBP
customer_locale=null, billing_country=DE, shipping_country=FR, presentment_currency=EUR
```

The second case must additionally prove a gift/different-delivery-country does
not rewrite canonical buyer country from GB to FR. The second and third cases
must prove that neither country nor currency causes a language rewrite.

Run focused normalization/ingress tests and repository-standard implementation
validation.

## Implementation Notes

Do not start from market configuration and work backwards to customer language.
The actual checkout/order payload is the stronger buyer-context source when it
contains the field.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `app/services/webhooks/international-context-normalization.ts`
- `app/services/webhooks/shopify-webhook-ingress.service.ts`
- `tests/unit/webhooks/shopify-normalization.test.js`
- `tests/unit/webhooks/shopify-webhook-ingress.service.test.js`
- `package.json`
- `package-lock.json`

### Work Completed

Adopted `@modainteract/moda-interact-shared@0.6.2` and mapped Shopify checkout
create/update and order webhook fields into the optional V2 event-level
`internationalContext`. Locale, billing country and presentment currency are
canonicalised independently through shared helpers; shipping country and
webhook `currency` are ignored for buyer context. Context is omitted when no
authoritative buyer fields are available, and cart events remain unchanged.

### Validation Results

- Focused normalization and ingress tests: 33 passed.
- Full app tests: 104 passed, 1 skipped.
- Targeted ESLint: passed.
- Build: passed.
- `git diff --check`: passed.
- Full lint: baseline failures in unrelated onboarding, billing, privacy and
  telemetry/queue test files.
- Typecheck: baseline failures in unrelated JSX routes/components and database
  globals; no producer-specific failure was reported.
- No Shopify API lookup was added; the ingress source guard and existing event
  publication tests remain passing.

### Deviations

None.

### Assumptions

Shopify `billing_address.country_code` is the authoritative purchaser country
available at this webhook boundary, while `timeZone` has no direct authoritative
provider field and remains null.

### Unresolved Issues

Repository-wide lint and typecheck remain blocked by pre-existing unrelated
diagnostics documented above.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

The architect reviewed the supplied workspace and actual producer runtime source,
not only the Completion Report. The implementation conforms to the ARCH-005
producer contract.

Accepted findings:

1. `@modainteract/moda-interact-shared` is pinned consistently to `0.6.2`;
2. checkout create, checkout update and order create events attach the optional
   canonical `internationalContext` through the published shared V2 contract;
3. the emitted event is runtime-validated by the corresponding strict shared
   event schema before queue publication;
4. `customer_locale` is canonicalised independently and is the only source used
   here for `languageTag`;
5. `presentment_currency` is canonicalised independently and webhook `currency`
   is deliberately not substituted when presentment currency is unavailable;
6. `billing_address.country_code` may provide buyer country while
   `shipping_address.country_code` is deliberately excluded from canonical buyer
   context;
7. webhook timezone remains null because this boundary has no direct authoritative
   buyer-timezone field in the inspected payload contract;
8. cart events remain unchanged and do not receive international context;
9. no Shopify Admin or Markets API lookup was added to the webhook hot path;
10. focused ingress tests cover independent language/country/currency combinations,
    the GB-billing/FR-shipping gift case, invalid/missing provider fields, and cart
    non-emission;
11. existing event identity, ordering and queue-publication structure is preserved.

The reported repository-wide lint/typecheck diagnostics are pre-existing baseline
issues outside the files changed for SHOPIFY-003. Focused tests, the full test suite,
targeted ESLint, build and `git diff --check` passed for this implementation.

### Architectural Dependency Result

`ARCH-005-SHOPIFY-003` is **Complete**.

This completes the producer half of the optional Shopify international-context
contract. Background was accepted first, so producer emission is now compatible
with the consumer path.

This task alone does **not** make ARCH-005 system testing Ready.
`ARCH-005-SHOPIFY-001`, `ARCH-005-SHOPIFY-002`, and remaining Messaging tasks
still have to be architect-accepted according to their own dependency graph.

The remaining immediately executable Shopify tasks are therefore:

```text
ARCH-005-SHOPIFY-001
ARCH-005-SHOPIFY-002
```

The repository agent correctly made no commit or push. The developer owns
publication of this accepted implementation.
