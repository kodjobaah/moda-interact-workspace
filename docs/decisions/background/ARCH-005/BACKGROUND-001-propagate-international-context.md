---
id: ARCH-005-BACKGROUND-001
architecture_id: ARCH-005
title: Adopt and materialise Shopify international context
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 40
executor: copilot
claimed_at: 2026-09-05T23:57:28Z
attempt: 4
depends_on:
  - ARCH-005-SHARED-004
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-SHOPIFY-003
  - ARCH-005-BACKGROUND-002
  - ARCH-005-BACKGROUND-004
created: 2026-09-05
updated: 2026-09-06
---

# Adopt and materialise Shopify international context

## Architecture

Background is the consumer-first rollout boundary for the new optional Shopify
V2 `internationalContext` field.

The existing recovery architecture already performs a bounded Shopify Admin
GraphQL abandoned-checkout lookup when a pending recovery candidate matures.
ARCH-005 must reuse that existing action-path lookup rather than adding another
provider call merely for international metadata.

The resulting context is assembled from independent sources:

```text
buyer webhook snapshot (when present)
current abandoned-checkout data
merchant ShopSettings fallback
```

No field may be inferred from another field.

## Objective

Adopt the published shared event contract, preserve buyer international context
through pending recovery processing, enrich it from the existing authoritative
abandoned-checkout lookup, and persist stable conversation international state
without adding Shopify work to the common irrelevant-event hot path.

## Context

Relevant current files include:

```text
src/events/shopify-contract-adapter.ts
src/domain/pending-recovery-candidate.ts
src/services/pending-recovery-candidate.service.ts
src/domain/abandoned-checkout.ts
src/services/abandoned-checkout-lookup.service.ts
src/services/checkout-recovery.service.ts
src/services/conversation.service.ts
```

DATABASE-001 provides:

```text
ShopSettings.defaultLanguageTag
ShopSettings.defaultTimeZone
ShopSettings.defaultCountryCode
Conversation.languageTag
Conversation.languageSource
Conversation.countryCode
Conversation.currencyCode
Conversation.timeZone
```

The developer has already committed and pushed the accepted DATABASE-001 and
DATABASE-002 database work. For this task, dependency satisfaction therefore
requires the Background repository's `database` submodule to be updated to a
developer-published revision that actually contains these fields before
implementation continues. A `complete` task status without consuming the
published revision is not operational dependency satisfaction.

The existing abandoned-checkout lookup is already part of the recovery action
path. Do not create an additional market/locale lookup per webhook or per
irrelevant event.

## Scope

- Adopt the exact shared package release from SHARED-004.
- Adopt the latest developer-published database submodule revision that contains
  the accepted DATABASE-001 and DATABASE-002 work; DATABASE-001 fields are a hard
  runtime prerequisite for this task.
- Parse optional event `internationalContext` while preserving legacy V2 events.
- Carry relevant event context through the pending candidate lifecycle.
- Enrich current abandoned-checkout normalization with authoritative commerce
  country/currency/timezone and customer locale fields that the current Admin
  GraphQL object genuinely exposes.
- Persist resolved initial context when a recovery conversation is created.
- Preserve stronger existing customer language state on later updates.

## Out of Scope

- Shopify producer mapping; SHOPIFY-003 owns it.
- ShopSettings creation; SHOPIFY-001 owns it.
- New Shopify API calls on webhook receipt.
- Persisting a Shopify Market catalogue or market ID merely for ARCH-005.
- Active-conversation language detection; later ownership review rehomed this to BACKGROUND-004.
- Proactive WhatsApp template selection/send; later ownership review rehomed these to BACKGROUND-002/003.
- Country/currency/phone based language inference.

## Requirements

### 0. Hard database-submodule precondition

Before changing or validating the Background international-context implementation:

1. Fetch the configured `database` submodule remote.
2. Update the submodule pointer to the latest **developer-published** revision that
   contains the accepted ARCH-005-DATABASE-001 and DATABASE-002 work.
3. Verify `database/prisma/schema.prisma` contains at least:

```text
ShopSettings.defaultLanguageTag
ShopSettings.defaultCountryCode
ShopSettings.defaultTimeZone
Conversation.languageTag
Conversation.languageSource
Conversation.countryCode
Conversation.currencyCode
Conversation.timeZone
```

4. Run the repository's normal Prisma validation/generation against that schema.
5. Implement and test using the generated typed Prisma client.

Do **not** run `update-database-submodule.sh` as a whole because that helper also
commits and pushes; repository agents are prohibited from commit/push. Use the
necessary fetch/submodule-update commands directly and leave the gitlink change
uncommitted for the developer.

If the fields are still absent after fetching the configured remote, STOP and
return the task to architect review with the exact submodule remote, fetched
revision/branch evidence, and missing fields. Do not create a compatibility
layer around a stale schema.

The following are specifically prohibited as substitutes for updating the
dependency:

```text
raw SQL reads for DATABASE-001 fields
conditional Prisma spreads to hide unsupported fields
casts around a stale generated Prisma client
local duplicate migrations/schema definitions
```

### 1. Consumer-first shared contract adoption

Upgrade to the exact SHARED-004 package release before Shopify emits the field.

`parseRuntimeShopifyEvent()` must continue accepting legacy V2 events that omit
`internationalContext` and must accept valid new V2 events that contain it.

### 2. Pending candidate preservation

For checkout candidate events, preserve the optional canonical event context
through the existing Redis/BullMQ pending-candidate lifecycle so a checkout
locale observed at ingress is not lost before delayed materialisation.

Keep the candidate extension bounded and PII-free.

If checkout update events carry newer non-null Shopify context, merge them
field-by-field using explicit precedence rather than replacing known values with
null.

### 3. Reuse the existing abandoned-checkout lookup

Do not introduce a second lookup merely for ARCH-005.

Extend the existing bounded GraphQL query/normalizer only where the current API
supports authoritative values needed by the recovery flow.

For current checkout commerce currency, use presentment money from the existing
MoneyBag source, conceptually:

```text
totalPriceSet.presentmentMoney.amount
totalPriceSet.presentmentMoney.currencyCode
```

Do not use shop/base money as the customer commerce currency when presentment
money exists.

For buyer country, do **not** use shipping destination as canonical buyer
country. A shipping address may belong to a gift recipient or other delivery
destination. Prefer a directly exposed buyer/market country from the existing
lookup only if its semantics are verified; otherwise use purchaser/billing
country:

```text
verified explicit buyer/market country, when already available from the same lookup
then billingAddress.countryCodeV2
```

`shippingAddress.countryCodeV2` is fulfilment/delivery geography and MUST NOT be
written into canonical `InternationalContext.countryCode`. If no trustworthy
buyer/purchaser country exists, preserve the event snapshot or merchant fallback
according to the field precedence below.

For buyer time zone, do not use a shipping-address timezone. Prefer a directly
exposed buyer timezone when its semantics are verified; otherwise a directly
supplied billing-address timezone may be used as a purchaser fallback:

```text
verified explicit buyer timezone, when already available from the same lookup
then billingAddress.timeZone
```

If neither is available, preserve event context or use the merchant default. Do
not derive timezone from country, currency or language.

For language fallback from the current Shopify object, `customer.locale` may be
used when a customer exists. It is weaker than an actual checkout
`customer_locale` snapshot carried in the event.

### 3A. Attempt 3 — GraphQL document/API-version integrity

Attempt 2 corrected the buyer semantics, but review of the actual source found
that removing `shippingAddress` accidentally truncated the existing
`AbandonedCheckouts` GraphQL document inside the line-item selection. The
current string has unmatched braces and cannot execute against Shopify. Mocked
fetch tests did not detect this because they return a response without parsing
the submitted GraphQL document.

The repository is configured for Shopify Admin GraphQL API `2026-07`. Repair the
existing list query using fields that are valid for that API version. The
selection should be equivalent in capability to:

```graphql
query AbandonedCheckouts($query: String!, $first: Int!) {
  abandonedCheckouts(first: $first, query: $query, sortKey: CREATED_AT) {
    nodes {
      id
      abandonedCheckoutUrl
      createdAt
      completedAt
      totalPriceSet {
        presentmentMoney {
          amount
          currencyCode
        }
      }
      customer {
        id
        email
        phone
        firstName
        lastName
        locale
      }
      billingAddress {
        countryCodeV2
        timeZone
      }
      lineItems {
        nodes {
          id
          product { id }
          variant { id }
          sku
          title
          variantTitle
          quantity
          originalUnitPriceSet {
            presentmentMoney {
              amount
              currencyCode
            }
          }
        }
      }
    }
  }
}
```

Do not restore the removed `shippingAddress` selection merely to make the query
look like Attempt 1. Shipping geography is intentionally not part of canonical
buyer context.

For API `2026-07`, do not rely on legacy/non-current selections such as:

```text
AbandonedCheckout.currencyCode
AbandonedCheckout.totalPrice
AbandonedCheckoutLineItem.originalUnitPrice
```

Use `totalPriceSet.presentmentMoney` for checkout amount/currency and
`originalUnitPriceSet.presentmentMoney` for line-item unit price so the durable
recovery amount, line-item prices and `CheckoutRecovery.currency` remain in the
same buyer presentment currency. Use the line-item `sku` field directly.

Update the normalizer and unit fixtures to reflect the actual query shape rather
than retaining mock-only legacy fields that Shopify will not return.

Add regression coverage that inspects the actual outbound list-query body. It
must prove the document is complete (including closing selections), contains the
required `totalPriceSet`, `billingAddress`, customer locale and complete line-item
selection, excludes `shippingAddress`, and does not use the legacy fields listed
above. A normalized full-query snapshot or an equivalent complete structural
assertion is preferred over checking one or two substrings.

### 3B. Attempt 4 — Shopify count pre-check argument integrity

Attempt 3 repaired the abandoned-checkout **list** query, but architect review of
the actual service against Shopify Admin GraphQL API `2026-07` found that the
count pre-check still uses a non-existent `maximum` argument:

```graphql
abandonedCheckoutsCount(query: $query, maximum: $maximum)
```

For API `2026-07`, `abandonedCheckoutsCount` accepts `limit`, `query`, and
`savedSearchId`; it does not accept `maximum`. Because the count pre-check runs
before the list query, this defect prevents the repaired lookup from executing
against Shopify at all.

Repair only this bounded count pre-check. Preserve the existing architectural
bound of `ABANDONED_CHECKOUT_MAX_CANDIDATES = 20`, but request **one more than
the bound** so the service can still distinguish `<= 20` from `> 20` without
performing an unbounded count:

```graphql
query AbandonedCheckoutsCount($query: String!, $limit: Int!) {
  abandonedCheckoutsCount(query: $query, limit: $limit) {
    count
  }
}
```

with:

```text
limit = ABANDONED_CHECKOUT_MAX_CANDIDATES + 1
```

For the current bound this means `21`. Do **not** set `limit` to `20`, because
then the returned count can never be greater than the bound and the existing
`bounded-limit-exceeded` branch becomes unreachable.

Keep the existing behaviour:

```text
count == 0       -> not-found
count <= 20      -> perform the bounded list lookup
count >= 21      -> bounded-limit-exceeded; do not issue the list query
```

Add a regression that inspects the actual outbound count GraphQL request body
and proves all of the following:

- the operation uses `limit`, not `maximum`;
- the variables include the existing created-at `query`;
- the `limit` variable is exactly `ABANDONED_CHECKOUT_MAX_CANDIDATES + 1`;
- a returned count of `21` causes `bounded-limit-exceeded`;
- the list request is not issued for that over-bound case.

Do not reopen the already-correct Attempt 3 list query, buyer-country/timezone
semantics, typed Prisma/database adoption, event adapter, candidate merge logic,
or package pin unless the narrow count-query correction directly requires it.

### 4. Field-by-field precedence

Resolve each dimension independently.

Language for a newly created recovery conversation:

```text
1. existing explicit/detected conversation language, if any
2. checkout event internationalContext.languageTag
3. current abandoned-checkout customer.locale
4. ShopSettings.defaultLanguageTag
5. leave null for later platform fallback if none is configured here
```

When language comes from Shopify checkout/customer data:

```text
languageSource = shopify
```

When it comes from ShopSettings:

```text
languageSource = merchant-default
```

Country:

```text
1. verified explicit current buyer/market country, if already exposed by the same lookup
2. current billingAddress.countryCodeV2
3. event internationalContext.countryCode
4. ShopSettings.defaultCountryCode
```

Never use `shippingAddress.countryCodeV2` for canonical buyer country.

Currency:

```text
1. current abandoned-checkout presentment currency
2. event internationalContext.currencyCode
3. existing authoritative CheckoutRecovery currency when updating
4. null if genuinely unavailable
```

Do not fall back from currency to shop language/country and do not derive
currency from them.

Time zone:

```text
1. verified explicit current buyer timezone, if already exposed by the same lookup
2. current billing-address timezone when directly supplied/valid
3. event internationalContext.timeZone
4. ShopSettings.defaultTimeZone
```

Never use shipping-address timezone as canonical buyer timezone.

These are independent precedence chains. A value selected for one dimension
must not influence another.

### 5. Conversation persistence

When the recovery conversation is first created, initialise the DATABASE-001
conversation fields from the resolved context:

```text
languageTag
languageSource
countryCode
currencyCode
timeZone
```

Do not overwrite an existing stronger explicit/detected conversation language
with later weaker Shopify/merchant context.

Keep the recovery's existing commerce currency snapshot authoritative and
consistent with conversation currency where available.

### 6. Hot-path/scalability invariant

The common Shopify event path remains:

```text
dequeue -> minimal correlation/filtering -> no action -> acknowledge
```

Internationalisation must not make irrelevant events perform the abandoned
checkout lookup, market lookup, large DB reads, or provider API calls.

The extra Shopify fields are fetched only in the existing matured-recovery
action path where the bounded abandoned-checkout lookup already occurs.

## Work Items

- [x] Adopt SHARED-004 package release.
- [x] Fetch/update the database submodule to developer-published revision `61337e1` containing DATABASE-001/DATABASE-002 and regenerate Prisma.
- [x] Extend shared-event adapter types for optional canonical context.
- [x] Preserve canonical context through pending recovery candidates.
- [x] Merge checkout-update context without null-erasing known values.
- [x] Correct abandoned-checkout buyer country/timezone enrichment so shipping destination is not treated as buyer context.
- [x] Use presentment money as commerce currency/amount source.
- [x] Re-verify independent field resolution using the corrected buyer-country/timezone semantics.
- [x] Persist conversation context through the typed Prisma client generated from the adopted DATABASE-001 schema.
- [x] Preserve stronger existing conversation language by leaving existing conversation updates empty.
- [x] Add broader cross-combination tests, including a buyer/billing country different from shipping destination.
- [x] Prove irrelevant-event hot path has no new Shopify call by retaining the existing early recovery filter/update flow.
- [x] Remove the Attempt 1 raw-SQL/stale-Prisma compatibility workaround once the database submodule is updated.

- [x] Repair the truncated `AbandonedCheckouts` list GraphQL document and restore all required closing selections.
- [x] Align checkout/line-item query fields, normalizer and fixtures with Admin GraphQL API `2026-07` (`totalPriceSet.presentmentMoney`, direct line-item `sku`, `originalUnitPriceSet.presentmentMoney`).
- [x] Add a regression that inspects the complete outbound list GraphQL query so syntactic truncation/schema-shape drift cannot be hidden by mocked fetch responses.
- [x] Add an adapter regression proving a valid V2 event with `internationalContext` is preserved by `mapCheckoutCreatedContractInput` / `mapCheckoutUpdatedContractInput`.
- [x] Add pending-candidate merge regressions proving incoming nulls do not erase known context and newer non-null fields replace only their own dimensions.
- [x] Synchronize `package-lock.json` root dependency metadata with the exact `0.6.2` package pin used by `package.json`.
- [x] Replace the invalid `abandonedCheckoutsCount(... maximum: ...)` argument with the API `2026-07` `limit` argument.
- [x] Preserve the over-bound sentinel by sending `ABANDONED_CHECKOUT_MAX_CANDIDATES + 1` as the count `limit`.
- [x] Add count-request regression coverage proving `limit`/no-`maximum`, sentinel value `21`, and no list request when the count is over the bound.

## Interfaces / Contracts

Input contract:

```text
ShopifyRecoveryEventV2.internationalContext?: InternationalContext
```

Durable output:

```text
Conversation.languageTag
Conversation.languageSource
Conversation.countryCode
Conversation.currencyCode
Conversation.timeZone
CheckoutRecovery.currency
```

Merchant fallback input:

```text
ShopSettings.defaultLanguageTag
ShopSettings.defaultCountryCode
ShopSettings.defaultTimeZone
```

## Dependencies

- ARCH-005-SHARED-004 — published canonical event extension.
- ARCH-005-DATABASE-001 — Complete; consuming submodule revision must be available.

## Enables

- ARCH-005-SHOPIFY-003 — safe producer rollout after consumer acceptance.
- ARCH-005-BACKGROUND-002 — stable context exists for proactive template selection.
- ARCH-005-BACKGROUND-004 — stable context exists for active-conversation language resolution.

## Acceptance Criteria

- [x] legacy V2 events without context still process safely.
- [x] valid new V2 events with context parse safely.
- [x] checkout event locale survives pending candidate delay.
- [x] checkout updates do not erase known context with nulls.
- [x] current abandoned-checkout presentment currency is authoritative.
- [x] shipping destination is never persisted as canonical buyer `countryCode`; billing/verified buyer country is independent from language.
- [x] Shopify/customer locale does not derive currency/country.
- [x] merchant fallback is used only when stronger field-specific context is absent.
- [x] explicit/detected conversation language is not overwritten by weaker context.
- [x] conversation context/source is persisted on creation through the generated typed Prisma client from the adopted DATABASE-001 schema.
- [x] no new per-webhook/irrelevant-event Shopify lookup exists.
- [x] queue/pending candidate additions are bounded and PII-safe.
- [x] focused/full tests, typecheck, lint/build and diff checks pass subject to baseline.

- [x] the actual outbound abandoned-checkout list GraphQL document is complete and valid for the repository's configured `2026-07` field model.
- [x] checkout and line-item monetary normalization uses presentment-money fields that the query actually selects.
- [x] the list query does not request/use shipping geography for canonical buyer context.
- [x] a V2 event carrying canonical `internationalContext` is explicitly tested through the Background contract adapter.
- [x] pending-candidate tests explicitly prove null-preserving and newer-non-null field-by-field context merge behaviour.
- [x] `package.json` and lockfile root metadata agree on the exact shared `0.6.2` dependency.
- [x] the `abandonedCheckoutsCount` pre-check uses only API `2026-07` arguments and is executable against Shopify.
- [x] the count pre-check remains bounded while still detecting more than 20 candidates by requesting a sentinel limit of 21.

## Validation

Required behavioural cases include:

```text
fr-CA / CA / USD
    remains fr-CA / CA / USD

en-GB / FR / EUR
    remains en-GB / FR / EUR

no event language + current customer.locale=de + current presentment EUR
    -> language=de/source=shopify, currency=EUR

no Shopify language + merchant default=pt-BR + country=GB + currency=GBP
    -> language=pt-BR/source=merchant-default, country=GB, currency=GBP

gift / different delivery destination:
    billing buyer country=GB
    shipping destination country=FR
    language=en-GB
    presentment currency=GBP
    -> canonical countryCode=GB, NOT FR
```

Before behavioural validation, prove the adopted database submodule/schema and
generated client contain the DATABASE-001 fields. Tests that only pass because
new fields are hidden behind raw SQL or conditional unsupported Prisma writes do
not satisfy this task.

Also prove an irrelevant checkout/cart event does not call the abandoned
checkout provider lookup merely to obtain international context.

Run focused adapter/candidate/materialisation/conversation tests and the normal
repository validation suite for an implementation task.

Attempt 4 must additionally inspect the **count** request body. It must prove:

```text
abandonedCheckoutsCount uses limit, not maximum
limit variable = ABANDONED_CHECKOUT_MAX_CANDIDATES + 1 = 21
count=21 -> bounded-limit-exceeded
count=21 -> list query is not sent
```

This is required because mocked provider responses do not validate GraphQL
argument names.

Attempt 3 must additionally validate the actual GraphQL request document, not
only normalized results returned by a mocked provider. At minimum:

```text
count pre-check succeeds
list request is issued
captured request body contains the complete expected 2026-07 selection
query braces/selections are complete
shippingAddress is absent
legacy top-level currencyCode/totalPrice and originalUnitPrice are absent
normalizer consumes presentment-money fields present in that request shape
```

Add candidate lifecycle cases equivalent to:

```text
existing: language=en-GB, country=GB, currency=GBP
incoming update: all null
-> existing values remain unchanged

existing: language=en-GB, country=GB, currency=GBP
incoming update: language=fr-FR/source=shopify, country=null, currency=EUR
-> language=fr-FR/source=shopify, country=GB, currency=EUR
```

Run the previously passing focused ARCH-005 suites again after the repair. The
known unrelated baseline routing-mock/Groq integration failures may remain
documented only if they are unchanged and no files involved in those failures
were modified by Attempt 3.

## Implementation Notes

If source inspection shows that any named Shopify GraphQL field is unavailable
in the repository's configured API version, do not invent an equivalent or
silently infer it. Use the closest authoritative current field only when its
semantics are verified; otherwise preserve null and report the limitation.

Attempt 2 must not compensate for a stale database dependency. The developer owns
commits/pushes; the agent owns consuming the already-published dependency and
leaving any updated submodule gitlink uncommitted.

## Completion Report

### Status

Ready for Review.

Implemented the consumer-first international-context path in
`moda-interact-background`:

- pinned `@modainteract/moda-interact-shared` to `0.6.2` and preserved legacy
  V2 event parsing;
- propagated bounded optional context through adapter, BullMQ candidate
  scheduling, refresh, and merge paths;
- enriched the existing abandoned-checkout GraphQL lookup with presentment
  money, customer locale, and billing purchaser country/timezone; shipping
  destination is not selected or persisted as canonical buyer context;
- resolved language, country, currency, and timezone independently and
  initialized new recovery conversations without overwriting existing state;
- retained independent field precedence and presentment currency precedence;
- updated the database submodule to developer-published revision `61337e1`,
  regenerated Prisma, and removed the Attempt 1 raw-SQL/stale-client workaround.
- repaired the complete Shopify Admin GraphQL `2026-07` list selection;
- normalized line-item SKU and price from the selected direct `sku` and
  `originalUnitPriceSet.presentmentMoney` fields;
- added outbound-query integrity coverage, V2 adapter context coverage, and
  null-preserving/newer-non-null candidate merge coverage;
- synchronized the lockfile root dependency metadata with the exact `0.6.2`
  package pin.
- corrected the count pre-check to use Shopify API `2026-07` `limit` with the
  bounded sentinel value `21` and added request-body/over-bound coverage.

Validation:

- focused ARCH-005 suites including adapter, candidate, lookup, materialisation,
  checkout refresh and runtime observability: 80/80;
- lookup/adapter/candidate Attempt 3 suites: 50/50;
- `npm run test:integration`: 1 passed, 4 skipped;
- `npm run test:unit`: 134 passed, 1 unchanged baseline failure in
  `recovery-routing.service.test.ts` because its Prisma mock lacks
  `customerPhone.findMany`;
- `npm test`: 135 passed, 4 skipped, 1 unchanged baseline routing-mock failure;
- `npm run prisma:validate`: passed against submodule revision `61337e1`;
- `npm run prisma:generate`: passed;
- `npm run build`: passed;
- `git diff --check`: passed.

Attempt 4 focused lookup validation: 10/10, including count query argument,
sentinel limit and no-list-on-over-bound assertions.

The complete test run did not reproduce the earlier external Groq failure; only
the unchanged routing mock baseline remains.

Changed files:

- `src/events/checkout-events.ts`
- `src/events/shopify-contract-adapter.ts`
- `src/domain/pending-recovery-candidate.ts`
- `src/services/pending-recovery-candidate.service.ts`
- `src/domain/abandoned-checkout.ts`
- `src/services/abandoned-checkout-lookup.service.ts`
- `src/services/checkout-recovery.service.ts`
- `src/services/conversation.service.ts`
- `package.json`, `package-lock.json`
- `tests/unit/events/shopify-contract-adapter.test.ts`
- `tests/unit/services/pending-recovery-candidate.service.test.ts`
- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/services/abandoned-checkout-lookup.service.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- database submodule gitlink, now at `61337e1`

The database gitlink change is intentionally uncommitted for developer
publication. No commit or push was performed.

## Architect Review

### Review Status

Accepted — Attempt 4

### Review Notes

The architect reviewed the supplied Attempt 4 workspace and the actual runtime
source, not only the Completion Report. The previously reopened issues are now
resolved.

Accepted findings:

1. `@modainteract/moda-interact-shared` is pinned consistently to `0.6.2`;
2. the Background database submodule contains the accepted DATABASE-001 schema
   and typed Prisma persistence is used for conversation international fields;
3. candidate propagation preserves non-null international context without null
   erasure;
4. language, buyer country, presentment currency and timezone resolve
   independently;
5. shipping/delivery geography is not used as canonical buyer country or buyer
   timezone;
6. the existing bounded abandoned-checkout action-path lookup is reused rather
   than adding provider work to the Shopify-event hot path;
7. the Shopify Admin GraphQL `2026-07` abandoned-checkout list query is
   structurally complete and uses `totalPriceSet.presentmentMoney` and
   `originalUnitPriceSet.presentmentMoney`;
8. `Customer.locale` and billing `countryCodeV2` / `timeZone` are normalized
   independently;
9. the count pre-check uses `abandonedCheckoutsCount(... limit: $limit)` with
   `ABANDONED_CHECKOUT_MAX_CANDIDATES + 1` (21), allowing the implementation to
   detect more than 20 candidates without unbounded enumeration;
10. the Attempt 4 regression inspects the serialized count request and proves a
    count of 21 returns `bounded-limit-exceeded` and skips the list query.

The Attempt 4 implementation delta from Attempt 3 is narrowly limited to the
count-query correction and its focused regression. The reported unrelated
`recovery-routing.service.test.ts` mock failure remains a pre-existing baseline
issue and is not caused by ARCH-005 files changed in Attempt 4.

### Architectural Dependency Result

`ARCH-005-BACKGROUND-001` is **Complete**.

Its completion satisfies the remaining dependency gates for both:

```text
ARCH-005-SHOPIFY-003
ARCH-005-MESSAGING-001
```

Therefore both tasks may become **Ready**. This is intentional parallelism:
`SHOPIFY-003` owns producer emission of buyer-specific webhook context, while
`MESSAGING-001` consumes the durable conversation context already materialised
by Background. Neither depends on the other.

`ARCH-005-MESSAGING-002` remains Pending because it depends on MESSAGING-001.
System-test tasks remain Pending terminal validation work until their complete
implementation dependency sets are architect-accepted.

The repository agent correctly made no commit or push. The developer owns
publication of this accepted Background implementation.

### Post-Acceptance Ownership Coordination

A later architect review established that proactive template selection/send and
active-conversation/CommerceAgent processing execute in `moda-interact-background`,
not in the inbound Messaging repository. The historical Attempt 4 acceptance
remains valid; only its downstream ownership references are superseded.

Current downstream ownership from this accepted capability is:

```text
ARCH-005-SHOPIFY-003      producer emission
ARCH-005-BACKGROUND-002   proactive approved-template selection
ARCH-005-BACKGROUND-004   active-conversation language / CommerceAgent
```

System tests remain terminal and depend on the later Background capabilities rather
than directly on this task alone.

