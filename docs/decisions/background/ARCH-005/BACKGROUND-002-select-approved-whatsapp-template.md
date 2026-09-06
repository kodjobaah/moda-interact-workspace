---
id: ARCH-005-BACKGROUND-002
architecture_id: ARCH-005
title: Select approved WhatsApp templates by locale and market capability
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 50
executor: copilot
claimed_at: 2026-09-06T00:32:03Z
attempt: 1
depends_on:
  - ARCH-005-BACKGROUND-001
  - ARCH-005-DATABASE-002
enables:
  - ARCH-005-BACKGROUND-003
created: 2026-09-06
updated: 2026-09-06
---

# Select approved WhatsApp templates by locale and market capability

## Architecture

This capability belongs in Background because Background owns Prisma-backed
recovery state and the outbound recovery workflow. `moda-interact-messaging` is
inbound ingress only.

The superseded `ARCH-005-MESSAGING-001` implementation may be inspected as an
algorithmic reference, but do not create a cross-service call to Messaging and
do not copy its `unknown -> market-unavailable` behaviour.

## Objective

Implement a deterministic Background-owned selection boundary that reads the
DATABASE-002 catalogue and resolves the provider-approved template variant for a
proactive recovery without inferring language from country, currency or phone.

## Context

Accepted upstream state already provides durable Conversation international
context through `ARCH-005-BACKGROUND-001`. DATABASE-002 guarantees at most one
`APPROVED + enabled` row for a tenant/provider-account/purpose/canonical language.

Current outbound provider work remains in Background:

```text
src/services/checkout-recovery.service.ts
src/services/whatsapp.service.ts
```

This task selects only. `BACKGROUND-003` integrates the selected variant into the
actual provider send path.

## Scope

- Add a Background-owned template selector/service under `src/services/` or an
  equally clear Background domain boundary.
- Query/select DATABASE-002 `WhatsAppTemplateVariant` rows using typed Prisma.
- Resolve exact, base-language, merchant fallback and explicitly enabled platform
  fallback deterministically.
- Preserve canonical BCP-47 `languageTag` separately from provider language code.
- Enforce tenant/shop, provider-account, purpose, `APPROVED` and `enabled` filters.
- Add an injected/configurable market-capability boundary.
- Return bounded, typed selection outcomes suitable for `BACKGROUND-003`.

## Out of Scope

- Sending a Meta message.
- Modifying `moda-interact-messaging`.
- New database schema/migrations.
- Country/language allowlists.
- AI translation of provider templates.
- Active-conversation language detection.

## Requirements

### Selector input

Use canonical/durable input equivalent to:

```text
shopId
providerAccountId
purpose
resolved customer languageTag
countryCode when known
merchant fallback language
optional explicitly enabled platform fallback
```

The provider account must come from the actual configured outbound-send boundary;
do not infer it from a customer phone number or arbitrary template row.

### Fallback order

```text
1. exact canonical languageTag
2. approved base-language variant
3. merchant configured fallback
4. platform fallback only when explicitly enabled
5. bounded template-unavailable
```

Every selected row must be approved, enabled and owned by the requested
shop/provider account/purpose.

### Market capability semantics

Model at least:

```text
supported
unsupported
unknown / provider-check-required
```

Required behaviour:

```text
supported
  -> return selected template

unsupported
  -> bounded market-unavailable / unsupported-market

unknown
  -> retain selected template
  -> mark provider-check-required
  -> DO NOT return market-unavailable solely because local capability is unknown
```

The provider-send task owns the final provider decision when capability is
unknown.

### Output

Return a bounded result carrying, when selected:

```text
canonicalLanguageTag
providerLanguageCode
providerTemplateName
providerTemplateId when present
selectionSource
marketCapability = supported | provider-check-required
```

Do not collapse provider name and provider id into one field; Meta send requires
provider-facing values to remain explicit.

## Work Items

- [x] Inspect current Background Prisma/database dependency and outbound recovery path.
- [x] Implement typed DATABASE-002 variant lookup/selection.
- [x] Implement deterministic exact/base/merchant/platform fallback.
- [x] Implement bounded market-capability result with unknown preserved as provider-check-required.
- [x] Keep canonical/provider language identifiers separate.
- [x] Add focused selector/service tests.
- [x] Add cross-combination tests proving country/currency do not select language.

## Interfaces / Contracts

DATABASE-002 model:

```text
WhatsAppTemplateVariant
```

Accepted international context is already materialised by BACKGROUND-001.

Do not introduce a new cross-service contract.

## Dependencies

- ARCH-005-BACKGROUND-001.
- ARCH-005-DATABASE-002.

Both are Complete and developer-published/consumed by the Background repository.

## Enables

- ARCH-005-BACKGROUND-003.

## Acceptance Criteria

- [x] selector is implemented in `moda-interact-background`, not Messaging.
- [x] real typed Prisma catalogue rows are the source of selection.
- [x] only approved/enabled tenant/provider-owned variants can be selected.
- [x] exact locale selection is deterministic.
- [x] approved base-language fallback is deterministic.
- [x] merchant fallback occurs only after customer locale candidates.
- [x] platform fallback is opt-in.
- [x] canonical and provider language codes remain separate.
- [x] unsupported market returns bounded unavailable.
- [x] unknown market returns selected + provider-check-required rather than unavailable.
- [x] telephone country/currency/country do not choose language.
- [x] no hard-coded global country/language switch exists.
- [x] focused/full tests, build/typecheck and `git diff --check` pass subject to documented baseline.

## Validation

Run focused selector/service tests, repository-standard tests, typecheck/build and
`git diff --check`.

Tests must include:

```text
exact locale
base fallback
merchant fallback
platform fallback disabled/enabled
unapproved/disabled/wrong-tenant rows
unsupported market
unknown market -> provider-check-required with selected template
fr-CA / CA / USD-style independence
```

## Implementation Notes

Do not modify the architect-owned `Architect Review` section. Once complete,
return this task to `review` and STOP. Do not begin BACKGROUND-003. Do not commit
or push.

## Completion Report

### Status

Complete; returned to review.

### Implementation

- Added `src/services/whatsapp-template-selector.service.ts` with typed Prisma
  catalogue selection, exact/base/merchant/platform fallback, explicit market
  capability resolution, and bounded outcomes.
- Added focused selector coverage in
  `tests/unit/services/whatsapp-template-selector.service.test.ts`.

### Validation

- `npx vitest run tests/unit/services/whatsapp-template-selector.service.test.ts`
  passes: 8 tests.
- `npm run build` passes, including Prisma client generation and TypeScript
  compilation.
- `npm run prisma:validate` passes.
- `git diff --check` passes.
- `npm test` reports 141 passed and 4 skipped, with three pre-existing failures
  in `recovery-routing.service.test.ts` and
  `pending-recovery-candidate.service.test.ts`; the new selector suite passes.

### Notes

- No schema or migration changes were needed.
- No Messaging repository changes were made.
- BACKGROUND-003 remains out of scope.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

The architect inspected the supplied Background workspace and actual selector
source/tests rather than relying only on the Completion Report. The implementation
conforms to the rehomed ARCH-005 runtime ownership and DATABASE-002 invariants.

Accepted findings:

1. selection is implemented in `moda-interact-background`, where the proactive
   recovery workflow and typed Prisma client already live;
2. `WhatsAppTemplateVariant` is queried through typed Prisma and scoped by
   `shopId`, `providerAccountId`, `purpose`, `status = APPROVED`, and
   `enabled = true`;
3. the accepted DATABASE-002 partial unique index guarantees at most one raw
   selectable row for an exact stored canonical language key, while the service
   additionally returns bounded `ambiguous-approved-variant` if canonical-equivalent
   catalogue rows are ever observed;
4. fallback order is deterministic: exact customer locale, base language, merchant
   default, then explicitly enabled platform fallback;
5. customer, merchant and platform language tags are canonicalised as BCP-47 before
   comparison;
6. canonical `languageTag` remains separate from provider `providerLanguageCode`,
   `providerTemplateName`, and optional `providerTemplateId`;
7. currency is not part of the selector input and therefore cannot choose language;
   country is passed only to the explicit market-capability resolver and does not
   participate in locale fallback;
8. known unsupported capability returns bounded `market-unavailable`;
9. unknown capability preserves the selected approved variant and returns
   `provider-check-required`, allowing BACKGROUND-003 to defer the authoritative
   decision to the provider send boundary;
10. the focused tests cover exact/base/merchant/platform fallback, catalogue query
    scoping, unsupported market, unknown market and a country/currency/language
    cross-combination.

The reported unrelated repository baseline failures are outside the files and
capability implemented by this task and do not block ARCH-005 acceptance.

### Architectural Dependency Result

`ARCH-005-BACKGROUND-002` is **Complete**.

Its only downstream implementation dependency is now satisfied, therefore:

```text
ARCH-005-BACKGROUND-003   Ready
```

`ARCH-005-BACKGROUND-004` remains independently Ready. System-test tasks remain
Pending terminal validation because the proactive provider-template send and the
remaining Shopify implementation tasks are not yet Complete.

The repository agent correctly made no commit or push; developer publication
remains outside agent ownership.
