---
id: ARCH-026-SHOPIFY-002
architecture_id: ARCH-026
title: Adopt the shared merchant international context in the Shopify application
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-001
enables:
  - ARCH-026-BACKGROUND-002
  - ARCH-026-ADMIN-002
created: 2026-10-02
updated: 2026-10-02
---

# Adopt the shared merchant international context in the Shopify application

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Make provider-neutral `commerce.Shop` international-context fields authoritative for Shopify application business reads while continuing to mirror the retained Shopify ShopSettings fields during the development transition.

The shared fields are:

```text
Shop.storeLocale
Shop.defaultLanguageTag
Shop.defaultTimeZone
Shop.defaultCountryCode
```

This task must preserve current Shopify behavior while removing the architectural requirement that downstream cross-platform code read international context from `shopify.ShopSettings`.

## Context

The Shopify Shop provisioning service already receives:

```text
primary shop locale
IANA timezone
country code
```

and currently writes normalized defaults into `ShopSettings`. DATABASE-002 adds shared Shop fields and backfills existing language/time-zone/country values while retaining the old columns.

`storeLocale` is new and represents provider-native locale identity. For Shopify, persist the primary locale returned by Shopify after bounded trim/validation; do not force it through the current fixed Admin locale catalogue.

The normalized `defaultLanguageTag` remains the value used by Moda business/translation helpers. Translation coverage does not constrain which provider locale may be persisted.

## Scope

Modify only `moda-interact` production/tests needed to migrate Shopify-owned international-context writes and application reads.

Current inspected areas include Shop provisioning, Merchant Knowledge, merchant support/billing notifications, recovery query presentation and merchant i18n helpers.

### Authoritative writes

When Shopify provisioning establishes merchant international context, write both:

```text
commerce.Shop.storeLocale
a shared normalized language/time-zone/country context
```

and the existing ShopSettings language/time-zone/country compatibility fields in the same bounded provisioning operation where practical.

Do not clear a previously-known shared value merely because a provider response omits an optional field during a later/reinstall lookup unless current product semantics explicitly require clearing it.

### Authoritative reads

After this task, Shopify application business code that needs merchant/store international context must read the shared Shop fields rather than querying ShopSettings solely for those values.

Keep ShopSettings reads that are genuinely required for Shopify-specific recovery/discount settings.

### Locale policy

Do not introduce or reuse a fixed Moda allowlist to validate the provider-native store locale.

`storeLocale` preserves the bounded Shopify locale identifier. `defaultLanguageTag` continues through the existing canonical language-tag normalizer when possible.

Do not change the Shopify Admin user's UI-locale catalogue in this task; that is a separate UI concern.

## Out of Scope

- Removing the legacy ShopSettings fields.
- Woo/WordPress locale mapping.
- Background migration; owned by BACKGROUND-002.
- Admin migration; owned by ADMIN-002.
- Translation catalogue expansion.
- Billing/recovery semantics unrelated to the context source.
- Merchant Knowledge language-policy redesign.

## Requirements

### R1 — Shared context is authoritative for application business reads

Production `moda-interact/app` code must not require ShopSettings solely to obtain merchant language/time-zone/country after this task.

### R2 — Provider locale remains open-ended

Do not reject a Shopify store locale because it is absent from a Moda UI translation list.

### R3 — Legacy mirrors remain coherent

Current ShopSettings language/time-zone/country columns remain populated as compatibility mirrors when Shopify establishes those values.

### R4 — Missing provider data does not manufacture locale

Do not invent a provider-native `storeLocale` from a fallback language tag when Shopify does not supply one.

### R5 — Existing normalization behavior is preserved

Use the existing language-tag, time-zone and country canonicalization rules for the shared normalized fields rather than inventing new semantics.

## Work Items

- [ ] Update the nested database gitlink to accepted DATABASE-002 and regenerate Prisma.
- [ ] Write Shopify primary provider locale to `Shop.storeLocale` without a fixed allowlist.
- [ ] Write normalized language/time-zone/country to shared Shop fields during provisioning.
- [ ] Continue mirroring retained ShopSettings international-context fields.
- [ ] Migrate application reads that use ShopSettings solely for international context to shared Shop fields.
- [ ] Preserve Shopify-specific settings reads unrelated to international context.
- [ ] Update focused tests for non-English/region locales, nulls and unsupported-by-Moda-translation provider locales.
- [ ] Add a static audit of remaining production ShopSettings international-context reads/writes and document compatibility mirrors.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

Authoritative shared fields:

```text
commerce.Shop.storeLocale
commerce.Shop.defaultLanguageTag
commerce.Shop.defaultTimeZone
commerce.Shop.defaultCountryCode
```

Retained mirrors:

```text
shopify.ShopSettings.defaultLanguageTag
shopify.ShopSettings.defaultTimeZone
shopify.ShopSettings.defaultCountryCode
```

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-001`

SHOPIFY-001 serializes the two ARCH-026 migrations in `moda-interact`; DATABASE-002 provides the accepted shared schema.

## Enables

- `ARCH-026-BACKGROUND-002`
- `ARCH-026-ADMIN-002`

## Acceptance Criteria

- [ ] Shopify provisioning persists provider-native primary locale to `Shop.storeLocale` without a fixed allowlist.
- [ ] Shared Shop normalized language/time-zone/country fields are populated using existing canonicalization rules.
- [ ] Legacy ShopSettings fields remain present and are mirrored for compatibility.
- [ ] Production application business reads no longer require ShopSettings solely for international context.
- [ ] A syntactically bounded Shopify provider locale lacking Moda translation coverage is preserved rather than rejected.
- [ ] Null/missing provider values do not create invented locale/time-zone/country values.
- [ ] Existing Merchant Knowledge/recovery/billing behavior is unchanged except for the source of international context.

## Validation

- [ ] Prisma generation from accepted DATABASE-002;
- [ ] typecheck;
- [ ] targeted lint;
- [ ] focused Shop provisioning tests including regional/non-English/provider-locale cases;
- [ ] Merchant Knowledge/recovery/billing notification tests affected by context-source migration;
- [ ] static audit of ShopSettings international-context references;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Do not expand this source migration into a general i18n refactor. Reuse current canonicalizers and preserve existing behavior.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- DATABASE-002 is complete and the shared fields are available.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
