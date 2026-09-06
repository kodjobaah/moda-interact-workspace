---
id: ARCH-005-DATABASE-001
architecture_id: ARCH-005
title: Persist merchant and conversation international context
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T19:31:35Z
attempt: 2
depends_on:
  - ARCH-005-SHARED-001
enables:
  - ARCH-005-DATABASE-002
  - ARCH-005-SHOPIFY-001
  - ARCH-005-BACKGROUND-001
  - ARCH-005-MESSAGING-001
  - ARCH-005-SHOPIFY-002
created: 2026-09-05
updated: 2026-09-05T19:38:00Z
---

# Persist merchant and conversation international context

## Objective

Add the minimum database persistence required for merchant defaults and
customer/conversation international context without duplicating authoritative
commerce data unnecessarily.

## Required schema inspection

Before editing, inspect the actual current schema/ERD for:

```text
Shop / tenant settings
Conversation
CheckoutRecovery
customer/contact entities
existing locale/currency/timezone fields
```

Use the existing most appropriate entities.

Do not create duplicate fields merely because the logical architecture lists a
context shape.

## Logical merchant defaults

Persist equivalents of:

```text
defaultLanguageTag
defaultTimeZone
defaultCountryCode
```

Fields may be nullable during rolling deployment.

## Logical conversation context

Persist equivalents of:

```text
languageTag
languageSource
countryCode
currencyCode
timeZone
```

on Conversation or the existing canonical conversation-context entity.

If commerce currency already exists authoritatively on CheckoutRecovery/order,
do not duplicate it unless the conversation requires an intentional snapshot.
Document the decision.

## Language source

Persist a bounded representation compatible with:

```text
customer-explicit
detected
shopify
merchant-default
platform-default
```

Prefer a schema enum only if compatible with current migration/deployment
practice; otherwise use a constrained representation consistent with the
repository.

## Template work separation

Do not add WhatsApp locale template catalogue fields in this task except where
an existing model must be prepared for DATABASE-002.

## Migration

Migration must be rolling-deployment safe.

Existing merchants/conversations remain valid with null international fields.

No destructive backfill is required unless an authoritative current source
exists.

Do not infer language from phone/country during migration.

## Acceptance criteria

- [x] actual schema was inspected and report records chosen field placement.
- [x] merchant default language/timezone/country can persist independently.
- [x] conversation language/source can persist.
- [x] country/currency/timezone can persist where logically required.
- [x] no country->language backfill exists.
- [x] no phone->language backfill exists.
- [x] existing rows remain valid.
- [x] migration is reversible/consistent with repository policy.
- [x] Prisma/schema generation succeeds.
- [ ] database tests/typecheck/diff checks pass; this repository does not
  provide database test or typecheck scripts, while `git diff --check` passes.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260905191500_add_international_context/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/prisma-erd.png`

### Work Completed

- Added nullable `defaultLanguageTag`, `defaultTimeZone`, and
  `defaultCountryCode` to `shopify.ShopSettings`.
- Added nullable language, provenance, country, currency, and time-zone fields
  to `whatsapp.Conversation`.
- Added a bounded `whatsapp.LanguageSource` enum matching the shared contract.
- Preserved `commerce.CheckoutRecovery.currency` as the authoritative commerce
  currency; no duplicate recovery currency snapshot was added.
- Added an additive rolling-deployment migration with no country/phone language
  inference or backfill.

### Validation Results

- `npm run validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client `6.19.3`.
- `git diff --check`: passed.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; migration `20260905191500_add_international_context` applied successfully.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run status`: passed; database schema is up to date.
- Direct PostgreSQL catalog verification confirmed `whatsapp.LanguageSource` and
  all merchant/conversation international-context columns exist.
- `npm run erd`: passed; regenerated the PlantUML ERD and PNG from the current
  Prisma schema.
- Generated ERD verification confirmed `LanguageSource` and all eight
  international-context fields are present.
- `git diff --check`: passed after normalizing generated ERD whitespace.

### Deviations

The migration was written as equivalent additive SQL after the initial
`prisma migrate dev` attempt encountered an unavailable local database. It was
then applied successfully with `prisma migrate deploy` against the supplied
local URL.

### Assumptions

- Nullable fields preserve rolling deployment compatibility and existing rows.
- Conversation currency is an intentional conversational context snapshot when
  present; checkout/order currency remains authoritative for commerce data.

### Unresolved Issues

This repository does not provide database test or typecheck scripts. The
available schema, generation, migration, status, catalog, and diff checks pass.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The architect reviewed the supplied `moda-interact-database` workspace
directly.

The Prisma schema and migration themselves conform to the ARCH-005 persistence
requirements:

```text
shopify.ShopSettings
  defaultLanguageTag?
  defaultTimeZone?
  defaultCountryCode?

whatsapp.Conversation
  languageTag?
  languageSource?
  countryCode?
  currencyCode?
  timeZone?

whatsapp.LanguageSource
  CUSTOMER_EXPLICIT
  DETECTED
  SHOPIFY
  MERCHANT_DEFAULT
  PLATFORM_DEFAULT
```

The migration is additive and nullable, contains no language inference or
backfill, and preserves rolling compatibility.

The task report also records successful deployment to the supplied local
development database and catalog verification.

One repository-convention defect prevents acceptance.

### Required Correction — regenerate the ERD

The database repository identifies ERD generation as part of database schema
ownership, and the `moda_database` agent requires schema-changing work to
generate/update the ERD where applicable.

The submitted generated ERD is stale.

The architect inspected:

```text
moda-interact-database/docs/generated/prisma-erd.puml
```

and confirmed it does **not** currently contain the new internationalisation
fields or enum, including:

```text
defaultLanguageTag
defaultTimeZone
defaultCountryCode
languageTag
languageSource
countryCode
currencyCode
timeZone
LanguageSource
```

The README describes the generated ERD as representing the current Prisma
schema, so leaving it unchanged would make repository documentation disagree
with the source-of-truth schema.

### Required Work

From `moda-interact-database`, run the repository-standard ERD generation:

```bash
npm run erd
```

This should update the generated artifacts, normally:

```text
docs/generated/prisma-erd.puml
docs/generated/erd.png
```

Then verify the generated PlantUML contains the new ShopSettings fields,
Conversation fields and `LanguageSource` enum.

Do not alter the accepted schema design merely to satisfy the diagram.

### Validation to rerun

After regenerating the ERD:

```text
npm run validate
npm run prisma:generate
npm run erd
git diff --check
```

The already-successful localhost migration does not need to be recreated.
Rechecking `npm run status` is acceptable but not required unless the schema or
migration is changed.

### Source Review

The architect found no correction required in:

```text
prisma/schema.prisma
prisma/migrations/20260905191500_add_international_context/migration.sql
```

Specifically:

- merchant defaults remain independently nullable;
- conversation language provenance is persisted;
- conversation country/currency/time zone are nullable snapshots;
- `CheckoutRecovery.currency` remains the authoritative commerce currency;
- no country-to-language inference exists;
- no phone-to-language inference exists;
- existing rows remain valid;
- no DATABASE-002 template catalogue work leaked into this task.

### Follow-up

Keep this correction in the same canonical task.

Do **not** create an amendment task file.

After regenerating and validating the ERD artifacts, return
`ARCH-005-DATABASE-001` to architect review.

Until architect acceptance, dependent implementation tasks remain gated.

### Architect Re-review — Attempt 2

#### Review Status

Accepted

#### Source Review

The architect reviewed the supplied `moda-interact-database` workspace
directly.

The previously accepted Prisma schema and migration are unchanged from Attempt
1.

The required ERD regeneration correction is now present.

The generated PlantUML contains:

```text
shopify.ShopSettings
  defaultLanguageTag
  defaultTimeZone
  defaultCountryCode

whatsapp.Conversation
  languageTag
  languageSource
  countryCode
  currencyCode
  timeZone

whatsapp.LanguageSource
  CUSTOMER_EXPLICIT
  DETECTED
  SHOPIFY
  MERCHANT_DEFAULT
  PLATFORM_DEFAULT
```

The generated PNG is also present and readable at:

```text
moda-interact-database/docs/generated/erd.png
```

The task report's `Files Changed` section refers to
`docs/generated/prisma-erd.png`; the actual repository-standard PNG filename is
`docs/generated/erd.png`. This is a documentation filename discrepancy only and
does not affect acceptance.

#### Schema / Migration Conformance

Accepted.

The final persistence shape remains:

```text
ShopSettings
  defaultLanguageTag?
  defaultTimeZone?
  defaultCountryCode?

Conversation
  languageTag?
  languageSource?
  countryCode?
  currencyCode?
  timeZone?
```

All fields are independently nullable for rolling deployment.

The migration remains additive and contains no:

```text
country -> language inference
phone -> language inference
destructive backfill
template catalogue work
```

`CheckoutRecovery.currency` remains authoritative for commerce values;
`Conversation.currencyCode` is only a conversational context snapshot when
present.

#### Validation Reviewed

Attempt 2 reports:

```text
npm run erd                 passed
generated artifact checks   passed
git diff --check            passed
```

Attempt 1 had already established:

```text
npm run validate             passed
npm run prisma:generate      passed
migrate:deploy               passed against supplied localhost DATABASE_URL
migration status             up to date
direct PostgreSQL catalogue  verified enum + all new columns
```

The architect independently confirmed the regenerated PlantUML contains all
eight new international-context fields plus the `LanguageSource` enum, and the
generated PNG is a valid image artifact.

No commit or push was performed.

#### Result

`ARCH-005-DATABASE-001` is **Complete**.

The following tasks are now unblocked because all of their declared
dependencies are Complete:

```text
ARCH-005-DATABASE-002   Ready
ARCH-005-SHOPIFY-001    Ready
ARCH-005-SHOPIFY-002    Ready
```

These three tasks may proceed independently.

`ARCH-005-BACKGROUND-001` remains Pending because it also depends on
`ARCH-005-SHOPIFY-001`.

`ARCH-005-MESSAGING-001` remains Pending because it still depends on
DATABASE-002 and BACKGROUND-001.

