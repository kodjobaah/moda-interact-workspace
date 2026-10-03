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
status: review
priority: 25
executor: copilot
claimed_at: 2026-10-03T13:31:55Z
attempt: 1
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

- [x] Add `storeLocale`, `defaultLanguageTag`, `defaultTimeZone`, and `defaultCountryCode` to shared `commerce.Shop`.
- [x] Add the migration/backfill from the retained Shopify ShopSettings fields for language/time-zone/country.
- [x] Leave pre-existing `storeLocale` null rather than deriving provider-native identity from normalized language tags.
- [x] Add the bounded nullable country-code database check.
- [x] Preserve all existing ShopSettings international-context fields unchanged.
- [x] Add schema/migration validators proving no locale enum/allowlist was introduced.
- [x] Regenerate the Prisma ERD through the repository's normal workflow.
- [x] Rehearse fresh and upgrade PostgreSQL paths.

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

- [x] `commerce.Shop` has all four provider-neutral international-context fields with the specified nullability/bounds.
- [x] Existing ShopSettings language/time-zone/country values are backfilled to Shop on upgrade.
- [x] Existing rows with no ShopSettings/context remain nullable rather than receiving invented defaults.
- [x] Pre-existing rows do not receive manufactured `storeLocale` values.
- [x] The three existing ShopSettings fields remain present and unchanged.
- [x] No Woo/WordPress locale enum or Moda locale allowlist is introduced in Prisma or migration SQL.
- [x] `defaultCountryCode`, when present, is constrained to two uppercase ASCII letters using an explicit PostgreSQL `C` collation.
- [x] Fresh migration rehearsal succeeds.
- [x] Upgrade rehearsal from the pre-DATABASE-002 schema succeeds and preserves existing development data.
- [x] Prisma validation/client generation and migration validators pass.

## Validation

Required validation categories:

- [x] Prisma format/validate;
- [x] Prisma client generation;
- [x] architecture-specific schema validator;
- [x] architecture-specific migration validator;
- [x] disposable PostgreSQL fresh migration rehearsal;
- [x] disposable PostgreSQL upgrade rehearsal with representative ShopSettings values and nulls;
- [x] SQL/catalog assertion for the shared Shop columns and country-code check, including the explicit `C` collation;
- [x] static audit proving no locale enum/allowlist was added;
- [x] generated ERD validation;
- [x] Repository-declared database tests/tooling: focused ARCH-026 validators and Node syntax checks passed; no task-specific typecheck/lint script is declared.
- [x] `git diff --check`;
- [x] clean task-worktree/branch evidence.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect`, and STOP. Do not begin consumer tasks.

## Implementation Notes

Treat locale support and translation coverage as separate concepts. Persist provider-native locale identity without claiming that every locale already has Moda-authored translations.

Do not use `defaultLanguageTag.replace(...)` or similar migration logic to invent `storeLocale` for historical rows.

## Completion Report

### Status

Ready for Architect Review

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-DATABASE-002` on `task/ARCH-026-DATABASE-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-DATABASE-002` on `task/ARCH-026-DATABASE-002`.
- Git confirmed both task worktrees are dedicated physical paths; the implementation repository root is the implementation worktree itself.
- Shared/default checkout used for implementation: no. Another task worktree reused: no.

### Start-of-Attempt Synchronization and Preparation

- Deterministic `start-agent-task.py ARCH-026-DATABASE-002 --prepare --executor copilot --json`: succeeded; `prepared_execution: true`, Attempt 1 claimed, dependency gate passed.
- Launcher claim commit: `bee29f0899cb5c3cfbc514b6d1ef7571c358347f`.
- The session’s preserved prepare summary confirms worktrees were ready but does not retain exact startup fast-forward/origin-main synchronization outcomes; no stronger synchronization claim is made here.
- Recursive implementation-repository submodule state: zero entries (`git submodule status --recursive`).
- Parent workspace recursive status reports 14 service gitlinks uninitialized (`-<sha>` entries); these are workspace children and do not indicate implementation-repository submodules. The startup preparation summary reported the implementation submodule ready.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261003140000_arch026_shared_international_context/migration.sql`
- `moda-interact-database/scripts/validate-arch026-shared-international-context-schema.mjs`
- `moda-interact-database/scripts/validate-arch026-shared-international-context-migration.mjs`
- `moda-interact-database/scripts/test-arch026-shared-international-context-postgres.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/docs/generated/prisma-erd.puml`

### Work Completed

- Added nullable, bounded `storeLocale`, `defaultLanguageTag`, `defaultTimeZone`, and `defaultCountryCode` fields to shared `commerce.Shop`.
- Added an additive migration that backfills the three legacy Shopify context values, preserves nulls and legacy fields, and leaves historical `storeLocale` unset.
- Added a nullable uppercase-ASCII alpha-2 country-code check explicitly evaluated with PostgreSQL `C` collation, plus schema/migration validators that guard against closed locale catalogues.
- Regenerated the Prisma ERD and added explicit fresh/upgrade PostgreSQL rehearsal commands, including column catalog, default-null, backfill, legacy preservation, and country constraint assertions.

### Validation Results

- `npm run format` — passed.
- `npm run validate` — passed.
- `npm run prisma:generate` — passed (Prisma Client 6.19.3).
- `npm run erd:puml` — passed; generated ERD validator passed.
- `npm run test:arch026-shared-international-context-schema` — passed.
- `npm run test:arch026-shared-international-context-migration` — passed.
- `npm run test:arch026-shared-international-context-migration:fresh` — passed in invocation-owned `pgvector/pg17`, `--network none` container; catalog assertions and country-code behavior passed.
- `npm run test:arch026-shared-international-context-migration:upgrade` — passed in invocation-owned `pgvector/pg17`, `--network none` container; full, partial, and absent settings fixtures preserved expected values and nulls, with `storeLocale` remaining null.
- After Architect review correction, both fresh and upgrade PostgreSQL rehearsals passed again; catalog assertion confirms the check expression uses `COLLATE "C"`, and invalid lowercase, short, and non-ASCII country codes are rejected.
- `npm run test:arch026-woocommerce-installation-schema` — passed.
- `node --check` for all three new JavaScript files — passed.
- `git diff --check` — passed.

### Deviations

Architect review requested an explicit collation-independent ASCII range and complete execution evidence. The country-code check now applies `COLLATE "C"`, its static validator checks that expression, the PostgreSQL rehearsal checks the installed constraint definition, and both database modes were rerun successfully. `npm ci` reported three high-severity audit findings in installed dependencies; dependency remediation was outside this task and no dependency manifests were changed.

### Architect Review Response

- Review outcome: Changes Requested.
- Required correction: make the uppercase ASCII country-code rule independent of database collation. Addressed with `("defaultCountryCode" COLLATE "C") ~ '^[A-Z]{2}$'`; the migration validator requires this exact collation and the PostgreSQL rehearsal checks the installed constraint definition and rejection cases.
- Required reporting correction: complete task checklists and record worktree, preparation, and recursive-submodule evidence. Completed above; the ARCH-026 database index now reports `Review`.
- Post-correction validation: migration validator, fresh PostgreSQL rehearsal, upgrade PostgreSQL rehearsal, and implementation `git diff --check` passed.

### Assumptions

- DATABASE-001 is complete before this task executes.
- Existing Shopify ShopSettings values were already normalized by current application code where populated.

### Unresolved Issues

No implementation issues. The dependency audit findings noted under Deviations remain unassessed and are not introduced by this task.

### Architectural Concerns

None identified; implementation follows the additive provider-neutral storage contract and defers consumer migration to dependent tasks.

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
