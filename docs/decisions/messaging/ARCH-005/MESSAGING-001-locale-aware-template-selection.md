---
id: ARCH-005-MESSAGING-001
architecture_id: ARCH-005
title: Select approved WhatsApp templates by locale and market capability
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
status: superseded
priority: 50
executor: copilot
claimed_at: 2026-09-06T00:15:00Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-002
  - ARCH-005-DATABASE-001
  - ARCH-005-DATABASE-002
  - ARCH-005-BACKGROUND-001
enables:
  - ARCH-005-MESSAGING-002
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-05
updated: 2026-09-06
---

# Select approved WhatsApp templates by locale and market capability

## Objective

Make proactive WhatsApp template selection deterministic, provider-approved,
tenant-safe and locale-aware without hard-coded country/language switches.

## Template selector input

Resolve from canonical state:

```text
tenant/provider account
template purpose
resolved/initial customer languageTag
country/market context when known
merchant fallback language
```

## Template selector output

Return a bounded result equivalent to:

```text
selected
  canonicalLanguageTag
  providerLanguageCode
  providerTemplateIdentity
  selectionSource / fallback level

or

unavailable
  bounded reason
```

Do not return arbitrary provider error prose as business state.

## Approval requirement

A selected variant must be:

```text
approved
enabled
owned by the correct tenant/provider account
```

No LLM-generated translation may substitute for provider approval.

## Fallback

Implement/document deterministic fallback:

```text
exact languageTag
base language where explicitly mapped/approved
merchant configured fallback
platform fallback only when explicitly enabled
otherwise unavailable
```

A fallback may only choose an approved configured provider variant.

Do not derive fallback from destination telephone country.

## Provider language codes

Provider language codes are read from template configuration.

Do not construct them by assuming they equal BCP-47.

## Market capability

Introduce a `MarketCapabilityResolver` or equivalent boundary.

Do not implement:

```ts
switch(countryCode) { ... every country ... }
```

Provider/tenant capability changes must be configuration/provider-boundary
concerns.

If no reliable pre-send market restriction data exists, preserve an
`unknown/provider-check-required` state rather than fabricating support.

Map provider send failures into bounded operational outcomes without teaching
core business logic a country list.

## Formatting

Template variables that contain money/date values must be prepared from
canonical data with locale-aware formatting where the provider template
requires display text.

Do not alter stored canonical values.

## Observability

Emit bounded outcomes such as:

```text
template-selected
template-fallback
template-unavailable
market-unavailable
provider-rejected
```

Do not attach customer phone, email, address or raw template text as metric
dimensions.

## Acceptance criteria

- [x] only approved/enabled tenant-owned templates can be selected.
- [x] exact locale selection works.
- [x] configured fallback is deterministic.
- [x] missing locale does not trigger ad-hoc AI translation.
- [x] canonical language and provider language code remain separate.
- [x] no hard-coded all-country switch exists.
- [x] market capability boundary exists.
- [x] telephone country cannot choose conversation language.
- [x] selection outcome is auditable and bounded.
- [x] representative locale tests pass.
- [x] focused/full tests/build/typecheck/diff checks pass subject to baseline.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `app/lib/templates/whatsapp-template-selector.ts`
- `tests/whatsapp-template-selector.test.mjs`
- `tests/startup-contract.test.mjs`
- `package.json`
- `package-lock.json`

### Work Completed

Adopted `@modainteract/moda-interact-shared@0.6.2` and added a pure selector
boundary for the DATABASE-002 WhatsApp template catalogue. Selection filters
tenant/provider ownership plus `APPROVED` and enabled state, then applies exact
locale, explicitly mapped base locale, merchant fallback, and opt-in platform
fallback in deterministic order. Provider language codes and template identity
remain separate from canonical BCP-47 language tags.

Added an injected `MarketCapabilityResolver` boundary. Unsupported markets and
unknown/provider-check-required capability return bounded outcomes; country is
passed only as capability context and never selects language from telephone
country. No AI translation or hard-coded country switch was added.

### Validation Results

- Focused selector tests: 8 passed.
- Full Messaging tests: 21 passed, 1 skipped (existing Redis trace test).
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed before final report metadata update.

### Deviations

None.

### Assumptions

The caller supplies tenant-scoped DATABASE-002 variant rows and an approved
provider-boundary market capability resolver; this repository has no existing
database client or outbound provider-send workflow.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Superseded — ownership correction.

### Findings

The pure selector implementation is locally coherent, but it is not accepted as
the ARCH-005 runtime capability because it was implemented in the wrong service.

Inspection confirmed:

- `moda-interact-messaging` is the Meta/WhatsApp inbound webhook and queue-ingress boundary;
- it has no Prisma client and no proactive recovery workflow;
- it does not own outbound provider sending;
- its own README states worker-side outbound behaviour lives in `moda-interact-background`;
- `moda-interact-background/src/services/checkout-recovery.service.ts` owns the proactive recovery send path;
- `moda-interact-background/src/services/whatsapp.service.ts` owns Meta send operations;
- Background also owns CommerceAgent execution.

Leaving this helper in Messaging would therefore create an unused implementation
that passes unit tests without changing the runtime path.

A second semantic correction is required: an unknown pre-send market capability
must mean `provider-check-required`, not `market-unavailable`. Unknown capability
must preserve an otherwise valid selected template so the provider send boundary
can make the authoritative decision.

The capability is rehomed to `ARCH-005-BACKGROUND-002`; actual proactive template
sending is completed by `ARCH-005-BACKGROUND-003`. Do not commit this task's
Messaging runtime implementation as the accepted ARCH-005 solution.
