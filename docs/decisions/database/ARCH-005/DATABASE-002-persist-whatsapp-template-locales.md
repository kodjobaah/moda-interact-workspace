---
id: ARCH-005-DATABASE-002
architecture_id: ARCH-005
title: Persist locale-aware WhatsApp template variants
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 30
executor: copilot
claimed_at: 2026-09-05T20:20:00Z
attempt: 2
depends_on:
  - ARCH-005-DATABASE-001
enables:
  - ARCH-005-MESSAGING-001
created: 2026-09-05
updated: 2026-09-05T20:45:00Z
---

# Persist locale-aware WhatsApp template variants

## Objective

Provide a data-driven catalogue of provider-approved WhatsApp template
variants so adding a language does not require a new application switch.

## Schema inspection

Inspect existing WhatsApp/template/provider-account models first.

Extend existing storage where appropriate.

Create a new model only when there is no suitable canonical place.

## Logical template variant

Persist equivalents of:

```text
tenant / provider account identity
purpose
canonical languageTag
providerLanguageCode
providerTemplateName / provider template identity
providerStatus
enabled
```

Required purpose example:

```text
abandoned_cart_initial
```

Do not assume provider language code equals BCP-47.

## Status

Persist only a bounded provider/template status vocabulary consistent with
current Meta integration.

Selection logic belongs to Messaging, not database triggers.

## Uniqueness

Two separate invariants are required. They solve different problems.

### A. Provider-record identity

Prevent duplicate representation of the same provider template variant using:

```text
shopId
providerAccountId
purpose
providerTemplateName
providerLanguageCode
```

Canonical `languageTag` MUST NOT replace `providerLanguageCode` in this
provider-identity constraint. The provider code and canonical BCP-47 mapping are
separate concepts.

### B. Selectable-template identity

For one:

```text
shopId
providerAccountId
purpose
languageTag
```

there MUST be at most one row satisfying both:

```text
enabled = true
status = APPROVED
```

This is required so `ARCH-005-MESSAGING-001` cannot receive two equally valid
answers for the same exact-locale selector lookup.

Implement this as a PostgreSQL partial unique index (or an exactly equivalent
database constraint). Prisma does not need to pretend that a normal
unconditional `@@unique` represents this predicate.

The intended SQL shape is equivalent to:

```sql
CREATE UNIQUE INDEX "WhatsAppTemplateVariant_selectable_key"
ON "whatsapp"."WhatsAppTemplateVariant" (
    "shopId",
    "providerAccountId",
    "purpose",
    "languageTag"
)
WHERE "enabled" = true
  AND "status" = 'APPROVED';
```

Multiple rows for the same canonical `languageTag` MAY exist when they are not
simultaneously selectable. This permits an approved/enabled current template to
coexist with a pending, rejected, paused, disabled or otherwise non-selectable
replacement/history row.

Do NOT use this unconditional constraint as the selectable invariant:

```text
UNIQUE(shopId, providerAccountId, purpose, languageTag)
```

because it would prevent safe staged replacement of provider templates.

Do NOT solve duplicate selectable rows in Messaging by ordering by creation
time, update time, provider template name or ID. The database must reject the
ambiguous selectable state.

## No fixed language list

There must be no schema enum enumerating every supported human language.

Language tags are standards-based values.

## Rolling compatibility

Existing template rows remain valid.

If legacy records cannot be mapped authoritatively to a canonical language,
leave the canonical mapping null/unavailable for selection until configured;
do not guess.

## Acceptance criteria

- [x] actual existing template/provider schema was inspected.
- [x] locale variant catalogue is data-driven.
- [x] canonical language and provider language code are separate concepts.
- [x] approval/status and enabled state can be represented.
- [x] tenant/provider ownership is enforceable.
- [x] no fixed language enum exists.
- [x] legacy rows remain safe.
- [x] provider-record uniqueness uses provider template identity plus
  `providerLanguageCode`, not canonical `languageTag`.
- [x] the database rejects a second row that would be simultaneously
  `APPROVED` and `enabled` for the same
  `shopId/providerAccountId/purpose/languageTag`.
- [x] the database still permits a non-selectable replacement/history row for
  the same canonical language.
- [x] migration/schema generation/diff checks pass; this repository does not
  provide a database test or typecheck script.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260905195000_add_whatsapp_template_variants/migration.sql`
- `moda-interact-database/prisma/migrations/20260905202000_correct_whatsapp_template_variant_uniqueness/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`

### Work Completed

- Added a tenant-owned `whatsapp.WhatsAppTemplateVariant` catalogue linked to
  `commerce.Shop`.
- Persisted provider account identity, purpose, canonical BCP-47 language tag,
  provider language code, provider template name/identity, bounded provider
  status, enabled state, and timestamps as separate fields.
- Added the bounded Meta-compatible status vocabulary without enumerating human
  languages.
- Added provider-record uniqueness for tenant, provider account, purpose,
  provider template name, and provider language code, plus a selector-oriented
  index.
- Added a follow-up migration with a partial unique index enforcing one
  approved/enabled variant per exact tenant/account/purpose/canonical locale.
- Kept selection logic and provider capability decisions outside the database.

### Validation Results

- `npm run validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client `6.19.3`.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: passed; migration applied successfully after local failed-attempt recovery.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run status`: passed; database schema is up to date.
- Direct PostgreSQL catalog verification confirmed the status enum, template
  table, primary key, unique identity index, and selector index.
- `npm run erd`: passed; regenerated the PlantUML ERD and PNG.
- Generated ERD verification confirmed the template model, status enum, and
  provider/canonical locale fields.
- `git diff --check`: passed.
- Direct PostgreSQL behavior verification passed:
  - a second approved/enabled exact-locale variant was rejected;
  - a pending staged replacement for the same locale was allowed;
  - a duplicate provider template identity and provider language code was
    rejected.

### Deviations

The first local deployment attempt exposed PostgreSQL's 63-byte identifier
limit because two long generated index names truncated to the same relation
name. The migration was corrected with explicit short index names, the failed
local migration was marked rolled back, and deployment then succeeded.

### Assumptions

- `shopId` is the existing tenant boundary and `providerAccountId` is the
  provider-scoped account identity; a separate provider-account model is not
  currently present in this repository.
- Canonical `languageTag` is required for new variants; legacy records remain
  unaffected because this is a new additive table.
- The status enum reflects the bounded Meta template lifecycle states needed by
  selection and administration; no provider-specific language list is stored.

### Unresolved Issues

This repository does not provide database test or typecheck scripts. Messaging
selection and market capability logic remain owned by the downstream Messaging
task.

## Architect Review

### Review Status

Accepted

### Attempt 2 review

`ARCH-005-DATABASE-002` is accepted and Complete.

The corrected implementation satisfies both architecture-required invariants:

```text
provider-record identity
  shopId + providerAccountId + purpose
  + providerTemplateName + providerLanguageCode

selectable-template identity
  at most one APPROVED + enabled row for
  shopId + providerAccountId + purpose + canonical languageTag
```

The selectable invariant is enforced by the follow-up PostgreSQL partial unique
index rather than by an unconditional Prisma `@@unique`, so a pending or
disabled replacement may coexist with the currently selectable template. The
already-applied Attempt 1 migration was not rewritten.

Architect review of the submitted implementation also confirms:

- the corrected provider-identity constraint uses `providerLanguageCode`;
- the partial predicate is exactly `enabled = true AND status = 'APPROVED'`;
- direct database validation covered duplicate selectable rejection, staged
  replacement allowance, and duplicate provider-identity rejection;
- ERD/schema artifacts were regenerated;
- no unrelated repository implementation was introduced.

### Dependency impact

Acceptance of this task satisfies the `ARCH-005-DATABASE-002` dependency of
`ARCH-005-MESSAGING-001`, but **does not make MESSAGING-001 Ready yet**.

`ARCH-005-MESSAGING-001` still depends on:

```text
ARCH-005-SHARED-002       Complete
ARCH-005-DATABASE-001     Complete
ARCH-005-DATABASE-002     Complete
ARCH-005-BACKGROUND-001   Pending
```

Therefore `ARCH-005-MESSAGING-001` remains `pending` until
`ARCH-005-BACKGROUND-001` is architect-accepted as `complete`.

The downstream Messaging selector may rely on the database invariant that an
exact tenant/account/purpose/canonical-language lookup cannot contain more than
one simultaneously `APPROVED` and enabled variant.

### Attempt 1 review history

Changes Requested

### Attempt 1 finding

The overall catalogue model is accepted in principle, but the submitted
uniqueness does not yet guarantee deterministic template selection.

The current Prisma constraint is:

```prisma
@@unique([shopId, providerAccountId, purpose, languageTag, providerTemplateName])
```

This allows two rows such as:

```text
same shop/account/purpose/languageTag
recovery_v1  APPROVED  enabled=true
recovery_v2  APPROVED  enabled=true
```

Both rows satisfy the exact-locale lookup that `ARCH-005-MESSAGING-001` must
perform. The downstream selector would therefore have two valid answers.

There is also a separate provider-identity mismatch: ARCH-005 defines provider
record identity using provider template identity plus provider language code,
not canonical languageTag.

### Exact required correction

Keep this correction in `ARCH-005-DATABASE-002`. Do NOT create another task.

1. In `moda-interact-database/prisma/schema.prisma`, replace the current
   provider identity `@@unique` so it represents:

   ```text
   shopId + providerAccountId + purpose + providerTemplateName + providerLanguageCode
   ```

2. Keep the existing selector-oriented non-unique index unless inspection
   proves a concrete reason to adjust it.

3. Add a PostgreSQL partial unique index that enforces at most one selectable
   row for:

   ```text
   shopId + providerAccountId + purpose + languageTag
   WHERE enabled = true AND status = APPROVED
   ```

4. The first task migration was already applied during Attempt 1 validation.
   Do NOT ambiguously rewrite that applied migration and assume the local
   database will follow it. Create a small follow-up migration inside this same
   task that:

   ```text
   drops/replaces the incorrect Attempt 1 identity index;
   creates the corrected provider-identity unique index;
   creates the partial selectable-variant unique index.
   ```

5. Do not delete, merge, disable or otherwise guess how to repair existing data
   if the new uniqueness check encounters conflicting rows. If validation finds
   conflicting data, stop and report the exact conflict to `moda_architect`.

6. Regenerate the ERD artifacts after the schema/index correction.

### Required behavioural verification

Validation MUST prove all three cases, not merely that Prisma accepts the
schema:

```text
CASE 1 — reject ambiguous selectable state
row A: same selector key, APPROVED, enabled=true
row B: same selector key, APPROVED, enabled=true
expected: second row rejected by database uniqueness

CASE 2 — allow staged replacement
row A: same selector key, APPROVED, enabled=true
row B: same selector key, PENDING (or enabled=false)
expected: both rows allowed

CASE 3 — reject duplicate provider identity
same shop/account/purpose/providerTemplateName/providerLanguageCode
expected: duplicate provider record rejected
```

Use direct PostgreSQL/catalog verification where Prisma cannot represent or
inspect the partial-index predicate accurately.

### Validation to rerun

Run the repository/task validation contract, including at minimum:

```text
npm run validate
npm run prisma:generate
DATABASE_URL=<local-development-database> npm run migrate:deploy
DATABASE_URL=<local-development-database> npm run status
<direct catalog/behaviour verification for the two uniqueness invariants>
npm run erd
git diff --check
```

Use the already configured local development database URL/environment. Do not
print credentials or secret values.

Before returning to review, inspect the actual diff and confirm it contains:

```text
provider identity based on providerLanguageCode
partial unique selectable index with APPROVED + enabled predicate
follow-up migration rather than an unexplained rewrite of applied migration
regenerated ERD artifacts
```

Record the correction and validation in the Completion Report. Do not edit this
architect-owned review section.

Then set this same task to `review`, return control to `moda_architect`, and
STOP. Do not begin `ARCH-005-MESSAGING-001`. Do not commit or push.
