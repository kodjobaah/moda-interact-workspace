---
id: ARCH-005-SYSTEM-TEST-001
architecture_id: ARCH-005
title: Verify multi-market context and proactive template selection
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SHOPIFY-001
  - ARCH-005-SHOPIFY-003
  - ARCH-005-BACKGROUND-001
  - ARCH-005-BACKGROUND-002
  - ARCH-005-BACKGROUND-003
  - ARCH-005-SHOPIFY-002
  - ARCH-005-SHOPIFY-004
  - ARCH-005-MESSAGING-003
enables:
  - ARCH-005-SYSTEM-TEST-002
created: 2026-09-05
updated: 2026-09-06
---

# Verify multi-market context and proactive template selection

## Architecture

This is terminal ARCH-005 integrated verification for merchant defaults,
buyer-specific Shopify context, Background materialisation, locale-aware
WhatsApp template selection, proactive provider-template send and merchant presentation.

It must validate international dimensions as independent values. In particular,
a currency, country, market or telephone prefix must never be treated as proof
of customer language.

The test may exercise the existing bounded matured-recovery Shopify lookup, but
must not require or introduce an additional internationalisation-only provider
lookup.

## Objective

Prove that international commerce context reaches proactive WhatsApp template
selection and merchant presentation without coupling country, language,
currency and time zone.

## Context

Representative deterministic combinations include:

```text
en-GB / GB / GBP / Europe/London
fr-FR / FR / EUR / Europe/Paris
pt-BR / BR / BRL / America/Sao_Paulo
```

These are representative tests, not a supported-language allowlist.

At least one scenario must deliberately violate a naive geographic/currency
assumption, for example:

```text
fr-CA / CA / USD
en-GB / FR / EUR
```

## Scope

- Shopify merchant-default initialisation evidence.
- Buyer webhook context canonicalisation and null preservation.
- Background pending-candidate/context materialisation.
- Reuse of the existing matured-recovery Shopify lookup without a second
  i18n-specific lookup.
- Approved/enabled tenant-owned WhatsApp template selection.
- Actual proactive provider-template send uses the selected provider name/language code.
- Deterministic exact/base/merchant/unavailable template outcomes.
- Unknown market capability reaches provider check rather than being treated as locally unavailable.
- Canonical/provider language-code separation.
- Merchant UI formatting independence.
- PII-safe evidence.

## Out of Scope

- Live mutation of Meta template approval merely to create a test scenario.
- A production-wide Shopify Markets catalogue.
- New provider integrations.
- Language inference from country, currency, market or telephone prefix.
- System validation belonging to MESSAGING-002; SYSTEM-TEST-002 owns active
  multilingual conversation behaviour.

## Requirements

### Independent context

Prove:

```text
country does not determine language
language does not determine currency
currency does not determine language
market does not determine language
phone prefix does not determine conversation language
```

A cross-combination such as `fr-CA / CA / USD` must survive end-to-end without
being rewritten to a currency/country-derived language.

### Shopify capture

Verify known provider locale/country/currency context is canonicalised
independently and unknown fields remain null rather than invented.

Verify merchant defaults and buyer-specific context remain separate concepts.

### Background propagation

Verify optional event context survives the delayed pending-candidate lifecycle,
is enriched from the existing bounded matured-recovery lookup where required,
and arrives in recovery/conversation state without an **additional**
internationalisation-specific Shopify lookup.

### Template selection

For configured approved variants, verify:

```text
exact locale
base-language fallback
merchant fallback
unavailable outcome
```

Only approved/enabled tenant-owned variants may be selected.

### Provider code separation

Evidence must show canonical language tag and provider template language code
are separate fields/concepts.

### Money

Same numeric amount with different currency/locale must format appropriately
without changing the underlying amount/currency.

### Merchant UI

Verify merchant UI locale formatting can differ from customer conversation
language.

### No live provider requirement

Where Meta template approval/country capability cannot be safely manipulated in
a test account, provider responses may be represented by deterministic
integration fixtures/mocks.

Do not fabricate a live Meta approval.

## Work Items

- [ ] Build representative merchant/shop international fixtures.
- [ ] Add at least one cross-combination fixture such as `fr-CA / CA / USD`.
- [ ] Exercise merchant ShopSettings initialisation/default behaviour.
- [ ] Exercise buyer webhook canonical context emission.
- [ ] Exercise delayed Background materialisation and existing lookup reuse.
- [ ] Verify exact/base/merchant/unavailable template selection outcomes.
- [ ] Verify selected template name/provider language code are used by proactive provider send.
- [ ] Verify unknown market capability can reach provider send and real provider rejection is bounded.
- [ ] Verify unapproved/disabled variants cannot be selected.
- [ ] Verify canonical/provider language-code separation.
- [ ] Verify merchant UI locale can differ from customer language.
- [ ] Record PII-safe integrated evidence.

## Interfaces / Contracts

Inputs under test include:

```text
ShopSettings merchant defaults
ShopifyRecoveryEventV2.internationalContext?
current abandoned-checkout action-path data
WhatsAppTemplateVariant catalogue
```

Expected durable/output boundaries include:

```text
CheckoutRecovery commerce currency
Conversation international context
selected provider template variant / bounded unavailable outcome
provider template-send result / bounded provider rejection
merchant UI formatted presentation
```

## Dependencies

- ARCH-005-SHOPIFY-001.
- ARCH-005-SHOPIFY-003.
- ARCH-005-BACKGROUND-001.
- ARCH-005-BACKGROUND-002.
- ARCH-005-BACKGROUND-003.
- ARCH-005-SHOPIFY-002.
- ARCH-005-MESSAGING-003.

All dependencies must be Complete and architect-accepted before this task may
become Ready.

## Enables

- ARCH-005-SYSTEM-TEST-002.

## Acceptance Criteria

- [ ] representative multi-market scenarios pass.
- [ ] cross-combination independence scenario passes.
- [ ] currency/country/market/phone do not determine language.
- [ ] buyer locale/country/currency remain independently sourced.
- [ ] optional event context survives delayed Background materialisation.
- [ ] no additional i18n-specific Shopify lookup is introduced.
- [ ] template exact/base/merchant/unavailable cases pass.
- [ ] proactive provider send consumes the selected provider template.
- [ ] unknown market capability is not fabricated as unavailable.
- [ ] unapproved or disabled template cannot be selected.
- [ ] provider language code remains distinct from canonical language tag.
- [ ] currency remains commerce-authoritative.
- [ ] merchant UI locale remains independent.
- [ ] evidence is PII-safe.
- [ ] no hard-coded country allowlist is required for the test.
- [ ] system-test validation/build/diff checks pass.

## Validation

Run the repository-standard system-test validation for the implemented
scenarios, plus `git diff --check`.

Evidence must identify which scenarios use deterministic provider fixtures and
must not claim live Meta approval where none was exercised.

## Implementation Notes

System tests are terminal verification work. Do not make this task Ready merely
because one implementation branch completes; every YAML dependency must first
be Complete.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
