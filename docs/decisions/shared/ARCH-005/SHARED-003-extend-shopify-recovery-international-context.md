---
id: ARCH-005-SHARED-003
architecture_id: ARCH-005
title: Extend Shopify recovery events with canonical international context
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 25
executor: copilot
claimed_at: 2026-09-05T21:35:00Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-002
enables:
  - ARCH-005-SHARED-004
created: 2026-09-05
updated: 2026-09-05T22:21:00Z
---

# Extend Shopify recovery events with canonical international context

## Architecture

ARCH-005 already defines canonical `InternationalContext` in
`@modainteract/moda-interact-shared`. Shopify recovery events are strict V2
schemas and currently have no legal place to carry buyer-specific canonical
international context.

This task extends the shared queue contract only. It does not map Shopify
provider fields and does not modify any producer or consumer repository.

The extension must remain input-compatible with legacy V2 events that do not
contain international context. Because an older strict consumer would reject a
new field, ARCH-005 rollout remains consumer-first after publication.

## Objective

Add an optional canonical `InternationalContext` field to the existing Shopify
V2 recovery event envelope so buyer-specific language/country/currency/time-zone
context can cross the Shopify -> BullMQ -> Background boundary without provider
field names leaking into cross-service contracts.

## Context

Current contract owner:

```text
moda-interact-shared
```

Package:

```text
@modainteract/moda-interact-shared
```

Producer:

```text
moda-interact
```

Consumer:

```text
moda-interact-background
```

Current runtime validation:

```text
ShopifyRecoveryEventV2Schema
```

The existing V2 base event is strict. `InternationalContextSchema` already
provides canonical BCP-47 / ISO country / ISO currency / IANA timezone
validation and keeps all dimensions independent.

## Scope

Primary files to inspect/change:

```text
moda-interact-shared/src/shopify/v2/recovery-event.schema.ts
moda-interact-shared/src/shopify/v2/recovery-event.test.ts
```

Use the existing:

```text
InternationalContextSchema
InternationalContext
```

from the shared internationalisation module.

## Out of Scope

- Shopify webhook field mapping.
- Shopify OAuth scopes.
- Background persistence or fallback logic.
- Database changes.
- Meta/WhatsApp template selection.
- A local Shopify Markets model.
- Inferring language from country, currency, market, phone or timezone.
- Package publication; that is SHARED-004.

## Requirements

Add one optional canonical field to the V2 recovery envelope:

```text
internationalContext?: InternationalContext
```

When present, the object uses the existing strict canonical schema and therefore
contains the existing independently nullable fields:

```text
languageTag
languageSource
countryCode
currencyCode
timeZone
```

Do not add provider-specific names such as:

```text
customer_locale
presentment_currency
shipping_address
market_id
```

to the shared event contract.

Do not make `internationalContext` required. Existing queued/legacy V2 events
without it must continue to parse.

Do not add fallback policy to the shared schema. This task validates and carries
context; producer/consumer tasks decide source precedence.

## Work Items

- [x] Import/reuse `InternationalContextSchema` from the shared internationalisation module.
- [x] Add optional `internationalContext` to the strict V2 recovery event base.
- [x] Preserve all existing V2 event types and ordering/idempotency fields.
- [x] Add focused tests for legacy events without the field.
- [x] Add focused tests for valid context with intentionally cross-combined values.
- [x] Add invalid language/country/currency/timezone rejection tests.
- [x] Prove provider-specific extra fields are still rejected.
- [x] Prove no field is inferred from another field.

## Interfaces / Contracts

Contract:

```text
ShopifyRecoveryEventV2
```

New additive field:

```text
internationalContext?: InternationalContext
```

Compatibility rule:

```text
old event -> new parser: MUST pass
new event -> old strict parser: may fail
```

Therefore publication and runtime rollout MUST be:

```text
SHARED-003 accepted
    -> SHARED-004 published
    -> BACKGROUND-001 adopts new package/parser
    -> SHOPIFY-003 begins emitting the new field
```

Do not change that ordering inside this task.

## Dependencies

- ARCH-005-SHARED-002 — Complete.

## Enables

- ARCH-005-SHARED-004.

## Acceptance Criteria

- [x] Legacy V2 recovery events without `internationalContext` still parse.
- [x] V2 events with valid canonical `internationalContext` parse.
- [x] BCP-47 language validation remains standards based.
- [x] ISO country and currency validation remain independent.
- [x] IANA timezone validation remains independent.
- [x] Country cannot imply language.
- [x] Currency cannot imply language.
- [x] Provider-specific fields remain outside the contract.
- [x] Existing queue event identity, ordering and idempotency fields are unchanged.
- [x] Existing shared tests plus focused contract tests pass.
- [x] typecheck/build/diff checks pass.

## Validation

Run focused shared Shopify contract tests, then the repository's normal shared
validation for an implementation task:

```text
npm test
npm run typecheck
npm run build
git diff --check
```

Do not publish a package version from this task.

## Implementation Notes

The preferred shape is an optional field on the common V2 recovery event
envelope rather than duplicating the canonical object independently into each
payload. If actual source inspection shows that this conflicts with an existing
shared invariant, stop and report the exact conflict to the architect instead
of inventing a parallel contract.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/src/shopify/v2/recovery-event.schema.ts`
- `moda-interact-shared/src/shopify/v2/recovery-event.test.ts`

### Work Completed

- Added optional `internationalContext` to the common strict Shopify V2
  recovery-event envelope.
- Reused `InternationalContextSchema` so language, country, currency, and time
  zone remain canonical, independently nullable, and standards validated.
- Preserved all existing event identity, ordering, and idempotency fields.
- Kept provider-specific Shopify field names outside the shared contract.
- Did not add fallback policy, producer mapping, consumer logic, database
  changes, or package publication.

### Validation Results

- Focused `src/shopify/v2/recovery-event.test.ts`: 19 passed.
- `npm test`: 77 passed, 1 skipped because `TEST_REDIS_URL` is not configured.
- `npm run typecheck`: passed.
- `npm run build`: passed, including declaration generation.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

- The optional envelope field is the single cross-service carrier for buyer
  context; provider mapping remains owned by the later producer task.
- Legacy V2 events remain valid because the field is optional.

### Unresolved Issues

Package publication is intentionally deferred to `ARCH-005-SHARED-004`.

## Architect Review

### Review Status

Accepted

### Review Notes

The architect reviewed the supplied `moda-interact-shared` implementation, not
only the Completion Report.

The implementation is correctly bounded to the shared recovery-event contract:

- `internationalContext` is optional on the common strict V2 recovery envelope;
- the existing canonical `InternationalContextSchema` is reused rather than
  duplicating provider-specific fields;
- legacy V2 events without the field still parse under the new parser;
- language, country, currency and time zone remain independently validated;
- provider-specific fields remain rejected by the strict canonical object;
- existing identity, ordering and idempotency fields are unchanged.

The focused cross-combination test deliberately accepts a context such as:

```text
languageTag  = fr-FR
countryCode  = GB
currencyCode = CHF
```

which proves the shared contract does not infer language from country or
currency.

### Pre-production schema-version decision

The V2 schema version is intentionally retained. Moda Interact is still in
development: there are no production consumers and no queued/persisted V2
events whose historical wire meaning must be preserved. The V2 contract is
therefore not yet frozen as a production compatibility boundary. Introducing a
V3 solely for this pre-production additive correction would create unnecessary
versioning machinery.

This decision is specific to the present pre-production state. Once a strict
wire contract has production consumers or durable queued events, future changes
must be reviewed against the normal schema-version/backwards-compatibility
policy instead of assuming the version may be redefined.

### Dependency Result

`ARCH-005-SHARED-003` is **Complete**.

Its only direct enabled task is now eligible:

```text
ARCH-005-SHARED-004   Ready
```

`BACKGROUND-001` remains Pending until SHARED-004 is published and architect
accepted. `SHOPIFY-003` remains Pending until the consumer-side Background
adoption is Complete. This preserves the consumer-first rollout despite the
pre-production environment.

No commit, push or package publication belongs to this implementation task.
