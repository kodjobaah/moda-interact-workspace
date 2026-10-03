---
id: ARCH-026-DATABASE-002
architecture_id: ARCH-026
title: Establish provider-neutral merchant international context
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-001
enables:
  - ARCH-026-SHOPIFY-002
  - ARCH-026-API-003
created: 2026-10-02
updated: 2026-10-03
---

# Establish provider-neutral merchant international context

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Move the durable merchant/store international context required by both Shopify and WooCommerce onto shared `commerce.Shop`, without removing the existing Shopify compatibility fields.

The provider-neutral durable shape is:

```text
commerce.Shop
    storeLocale?          provider-native store locale, preserved verbatim after bounded validation
    defaultLanguageTag?   canonical Moda/BCP-47 language tag when one can be established
    defaultTimeZone?      IANA time-zone identifier
    defaultCountryCode?   ISO-3166 alpha-2 country code
```

The existing fields remain temporarily present in:

```text
shopify.ShopSettings.defaultLanguageTag
shopify.ShopSettings.defaultTimeZone
shopify.ShopSettings.defaultCountryCode
```

This task adds/backfills shared state only. It MUST NOT remove the legacy fields, create a Woo-specific settings duplicate, introduce a locale allowlist, or change application/runtime internationalization behavior.

## Context

ARCH-026 treats internationalization as a first-class cross-platform requirement.

The current durable defaults are stored in the Shopify-specific `shopify.ShopSettings` model even though language, time zone and country describe the merchant/store rather than Shopify itself. Current Shopify installation code derives these values from Shopify store metadata, and Background/Admin/application consumers read them from `ShopSettings`.

WooCommerce/WordPress has its own locale system and must not depend on a Shopify-specific settings row. WordPress/Woo locale identifiers are not a closed Moda enum. ARCH-026 therefore must preserve provider-native locale identity while separately allowing a normalized language tag for Moda business/i18n use.

This task is pre-production and additive. It does not delete the legacy Shopify fields because the repository consumers are migrated in bounded follow-on tasks.

## Scope

Modify only `moda-interact-database` files required for the schema, migration, validation and generated ERD changes.

Expected primary files:

```text
prisma/schema.prisma
prisma/migrations/<timestamp>_arch026_shared_international_context/migration.sql
scripts/validate-arch026-shared-international-context-schema.mjs
scripts/validate-arch026-shared-international-context-migration.mjs
package.json
docs/generated/prisma-erd.puml
```

### Required `Shop` additions

Add exactly these logical fields to `commerce.Shop`:

```prisma
storeLocale        String? @db.VarChar(128)
defaultLanguageTag String? @db.VarChar(64)
defaultTimeZone    String? @db.VarChar(255)
defaultCountryCode String? @db.VarChar(2)
```

Formatting may differ after Prisma formatting, but field names, nullability and bounded storage semantics are architectural requirements.

`storeLocale` is the provider-native store locale string. It is deliberately not an enum and MUST NOT be constrained to Shopify's current locale catalogue or a Moda-maintained Woo locale allowlist.

`defaultLanguageTag` is a separate normalized language tag used by Moda services where a BCP-47-compatible tag is available. A valid provider-native locale may exist even when `defaultLanguageTag` is temporarily `NULL`; unsupported translation coverage must not cause the provider locale itself to be rejected or rewritten.

### Upgrade backfill

For every existing Shop with a `shopify.ShopSettings` row, backfill:

```text
Shop.defaultLanguageTag <- ShopSettings.defaultLanguageTag
Shop.defaultTimeZone    <- ShopSettings.defaultTimeZone
Shop.defaultCountryCode <- ShopSettings.defaultCountryCode
```

Do not populate `Shop.storeLocale` from `defaultLanguageTag` during migration. The provider-native Shopify locale was not historically persisted separately, so manufacturing it from a normalized language tag would blur two distinct concepts. Leave `storeLocale = NULL` for pre-existing rows until a provider-owned writer establishes it.

Preserve existing `NULL` values exactly.

### Legacy fields retained

Do not remove, rename or repurpose:

```text
shopify.ShopSettings.defaultLanguageTag
shopify.ShopSettings.defaultTimeZone
shopify.ShopSettings.defaultCountryCode
```

They remain compatibility mirrors until later cleanup is explicitly approved.

### Database constraints

Do not create a database enum or closed locale catalogue.

Add a deterministic database check for `defaultCountryCode` only when non-null:

```text
length = 2
uppercase ASCII A-Z
```

Do not add database-level IANA time-zone or language-tag catalogues. Those evolve independently of the schema and belong to bounded application validation/canonicalization.

Do not enforce a foreign key/reference to any translation catalogue.

## Out of Scope

- Removing legacy international-context fields from `ShopSettings`.
- Migrating Shopify application readers/writers; owned by `ARCH-026-SHOPIFY-002`.
- Migrating Background readers; owned by `ARCH-026-BACKGROUND-002`.
- Migrating Admin readers; owned by `ARCH-026-ADMIN-002`.
- WordPress locale -> BCP-47 conversion logic.
- Woo plugin store-context synchronization.
- Woo Admin current-user locale handling.
- Translation catalogue generation/publication.
- Changing Merchant Knowledge translation policy.
- Billing/recovery/business-state changes.
- A fixed list of WooCommerce/WordPress locales.

## Requirements

### R1 — International context is shared tenant state

Provider-neutral store locale/language/time-zone/country values live on `commerce.Shop`, not in a new Woo-specific settings table.

### R2 — Provider-native locale is open-ended

`storeLocale` is a bounded string, not an enum/allowlist. The database must be able to preserve any syntactically valid provider-native locale accepted by the platform integration.

### R3 — Locale and language tag are distinct

Do not treat `storeLocale` and `defaultLanguageTag` as aliases. A provider locale may be preserved even when a canonical Moda language tag is not available.

### R4 — Legacy Shopify state is retained

No existing ShopSettings international-context column is removed in this task.

### R5 — Existing development data is backfilled

Existing normalized Shopify language/time-zone/country values are copied to the new shared Shop fields without inventing `storeLocale`.

### R6 — No translation coverage constraint

The schema must not reject a provider locale because Moda lacks translated strings for it.

## Work Items

- [ ] Add `storeLocale`, `defaultLanguageTag`, `defaultTimeZone`, and `defaultCountryCode` to shared `commerce.Shop`.
- [ ] Add the migration/backfill from the retained Shopify ShopSettings fields for language/time-zone/country.
- [ ] Leave pre-existing `storeLocale` null rather than deriving provider-native identity from normalized language tags.
- [ ] Add the bounded nullable country-code database check.
- [ ] Preserve all existing ShopSettings international-context fields unchanged.
- [ ] Add schema/migration validators proving no locale enum/allowlist was introduced.
- [ ] Regenerate the Prisma ERD through the repository's normal workflow.
- [ ] Rehearse fresh and upgrade PostgreSQL paths.

## Interfaces / Contracts

### Shared database owner

`ARCH-026-DATABASE-002`

### Provider-neutral fields

```text
commerce.Shop.storeLocale
commerce.Shop.defaultLanguageTag
commerce.Shop.defaultTimeZone
commerce.Shop.defaultCountryCode
```

### Retained compatibility fields

```text
shopify.ShopSettings.defaultLanguageTag
shopify.ShopSettings.defaultTimeZone
shopify.ShopSettings.defaultCountryCode
```

No HTTP/queue/shared-package contract is created by this task.

## Dependencies

- `ARCH-026-DATABASE-001`

DATABASE-001 must be architect-accepted Complete before DATABASE-002 becomes Ready so two independent Shop-schema migrations are not implemented concurrently.

## Enables

- `ARCH-026-SHOPIFY-002`
- `ARCH-026-API-003`

## Acceptance Criteria

- [ ] `commerce.Shop` has all four provider-neutral international-context fields with the specified nullability/bounds.
- [ ] Existing ShopSettings language/time-zone/country values are backfilled to Shop on upgrade.
- [ ] Existing rows with no ShopSettings/context remain nullable rather than receiving invented defaults.
- [ ] Pre-existing rows do not receive manufactured `storeLocale` values.
- [ ] The three existing ShopSettings fields remain present and unchanged.
- [ ] No Woo/WordPress locale enum or Moda locale allowlist is introduced in Prisma or migration SQL.
- [ ] `defaultCountryCode`, when present, is constrained to two uppercase ASCII letters.
- [ ] Fresh migration rehearsal succeeds.
- [ ] Upgrade rehearsal from the pre-DATABASE-002 schema succeeds and preserves existing development data.
- [ ] Prisma validation/client generation and migration validators pass.

## Validation

Required validation categories:

- [ ] Prisma format/validate;
- [ ] Prisma client generation;
- [ ] architecture-specific schema validator;
- [ ] architecture-specific migration validator;
- [ ] disposable PostgreSQL fresh migration rehearsal;
- [ ] disposable PostgreSQL upgrade rehearsal with representative ShopSettings values and nulls;
- [ ] SQL/catalog assertion for the shared Shop columns and country-code check;
- [ ] static audit proving no locale enum/allowlist was added;
- [ ] generated ERD validation;
- [ ] repository-declared tests/typecheck/lint required for changed database tooling;
- [ ] `git diff --check`;
- [ ] clean task-worktree/branch evidence.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect`, and STOP. Do not begin consumer tasks.

## Implementation Notes

Treat locale support and translation coverage as separate concepts. Persist provider-native locale identity without claiming that every locale already has Moda-authored translations.

Do not use `defaultLanguageTag.replace(...)` or similar migration logic to invent `storeLocale` for historical rows.

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

- DATABASE-001 is complete before this task executes.
- Existing Shopify ShopSettings values were already normalized by current application code where populated.

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
