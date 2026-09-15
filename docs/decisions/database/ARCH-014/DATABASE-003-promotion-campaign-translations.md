---
id: ARCH-014-DATABASE-003
architecture_id: ARCH-014
title: Add additive 20-locale promotion campaign merchant translations
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 42
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-002
enables:
- ARCH-014-ADMIN-008
- ARCH-014-SHOPIFY-003
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-DATABASE-003

## Objective

Add localized merchant-facing title/description persistence for `PromotionCampaign` without changing the existing campaign table or operational promotion semantics.

`PromotionCampaign.name` remains the **internal Admin campaign name**. Merchant-facing text moves to a new additive child table.

## Binding GPT-5.6 Luna rule

Implement exactly one new Prisma model/table and its new-table constraints/indexes. Do not alter, rename, drop, backfill, add a column/index/constraint/trigger to, or otherwise modify an existing table/enum. Do not change campaign targeting, grant, selection, reservation or lifecycle semantics.

## Exact Prisma model

Add the inverse Prisma relation field to `PromotionCampaign` (virtual relation metadata only; it creates no parent-table column):

```prisma
translations PromotionCampaignTranslation[]
```

Add exactly:

```prisma
model PromotionCampaignTranslation {
  id                  String            @id @default(cuid())
  promotionCampaignId String
  promotionCampaign   PromotionCampaign @relation(fields: [promotionCampaignId], references: [id], onDelete: Cascade)

  locale              String @db.VarChar(16)
  merchantTitle       String @db.VarChar(255)
  merchantDescription String @db.Text

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([promotionCampaignId, locale])
  @@index([promotionCampaignId])
  @@schema("billing")
}
```

Do not add a locale enum.

## Exact supported locale set

Database validation MUST accept exactly:

```text
cs
da
de
en
es
fi
fr
it
ja
ko
nb
nl
pl
pt-BR
pt-PT
sv
th
tr
zh-Hans
zh-Hant
```

Add new-table CHECK constraints requiring:

```text
locale is one of the exact 20 values
length(trim(merchantTitle)) between 1 and 255
length(trim(merchantDescription)) between 1 and 10000
```

Draft campaigns are allowed to have fewer than 20 rows. Therefore do **not** add a database trigger requiring 20 rows at all times. The Admin activation action owns the 20/20 publication gate.

## Migration

Create exactly one new migration folder:

```text
prisma/migrations/20260915210000_arch014_promotion_campaign_translations/
```

Its SQL may create only:

```text
billing.PromotionCampaignTranslation
new indexes/unique/check/FK constraints on that new table
```

The SQL MUST NOT contain `ALTER TABLE` targeting any pre-existing table. The FK constraint belongs to the new table and may reference `billing.PromotionCampaign(id)` with `ON DELETE CASCADE`.

Do not modify the baseline migration.

## Legacy scalar column

The existing nullable:

```text
PromotionCampaign.merchantDescription
```

MUST remain physically unchanged. Do not drop/rename/backfill it. DATABASE-003 does not define runtime fallback behavior; ADMIN-008/SHOPIFY-003 stop treating it as the merchant-facing localization source.

## Validation script

Add/update a focused database validator (use existing repository conventions) proving:

- model/table exists exactly once;
- unique `(promotionCampaignId, locale)` exists;
- exact locale CHECK exists;
- title and description checks exist;
- FK cascades from campaign to translation;
- migration does not alter any pre-existing table;
- `PromotionCampaign`, promotion lifecycle tables and operational BillingPlan definitions are otherwise byte/semantic unchanged by this task.

## Mandatory tests/commands

Run the repository's declared Prisma/schema/migration validators and generated ERD workflow where applicable, plus:

```bash
git diff --check
rg -n 'PromotionCampaignTranslation' prisma docs scripts
rg -n 'ALTER TABLE "billing"\."PromotionCampaign"|DROP COLUMN|RENAME COLUMN' prisma/migrations/20260915210000_arch014_promotion_campaign_translations/migration.sql
```

The final scan MUST return no forbidden parent-table alteration.

## Stop conditions

STOP if implementation appears to require changing an existing campaign column, campaign status enum, `BillingPlan`, grant/selection tables, or adding a trigger to `PromotionCampaign`. Return that requirement to `moda_architect` rather than broadening the migration.
