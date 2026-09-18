---
id: ARCH-014-SYSTEM-TEST-002
architecture_id: ARCH-014
title: Validate multilingual promotion authoring through exact merchant-locale presentation
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-003
- ARCH-014-ADMIN-008
- ARCH-014-SHOPIFY-003
- ARCH-014-ADMIN-010
enables: []
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-014-SYSTEM-TEST-002

## Terminal/manual gate

Do not auto-start. Developer invokes this only after DATABASE-003, ADMIN-008 and SHOPIFY-003 are architect-accepted and integrated. Do not modify production code from this task.

## Objective

Prove one promotion campaign flows from an internal Admin draft + pre-populated XLSX through exact 20-locale persistence/activation to merchant offer/history presentation without exposing internal campaign names or falling back across supported locales.

## Required scenario A — draft and workbook

Create a DRAFT campaign with:

```text
internal name: Autumn acquisition test
English merchant title: Get 20 recovery conversations free
English merchant description: Try Moda recovery with 20 promotional credits.
```

Prove database initially contains exactly one `en` translation and campaign remains DRAFT.

Download workbook and prove:

- exact sheets `Instructions`, `Translations`, `_meta`;
- exactly 20 language/locale rows already populated;
- English title/description pre-populated;
- 19 non-English rows blank;
- internal name shown only as context/instructions/meta, never as a field to translate;
- workbook implementation uses `exceljs@4.4.0`, same common Admin helper as MerchantPricing, and no second spreadsheet package.

## Scenario B — partial/stale failures

Prove each fails closed without partial translation persistence or activation:

```text
missing locale
blank title
blank description
renamed locale
formula cell
wrong campaign workbook
stale English source workbook
renamed/missing sheet
oversized workbook (> 2 MiB), rejected at the byte-size boundary before ExcelJS parsing
```

After changing the English source in a draft, prove all non-English persisted translations are invalidated/deleted and a fresh download pre-populates only the new English source plus blanks.

## Scenario C — complete import and activation

Populate exact translations for all 20 locales and upload.

Prove exactly 20 `PromotionCampaignTranslation` rows persist atomically, then activation succeeds.

Prove direct activation before 20/20 fails and status remains DRAFT.

## Scenario D — exact merchant locales

For the same ACTIVE campaign prove at least:

```text
en
fr
ja
pt-BR
pt-PT
zh-Hans
zh-Hant
```

render the exact corresponding merchant title and description.

Assert `pt-BR != pt-PT` fixture copy and `zh-Hans != zh-Hant` fixture copy so accidental fallback is detectable.

Prove internal Admin campaign name is absent from merchant offer HTML/data.

## Scenario E — promotion history

Select/use the campaign through existing fixture mechanisms, then prove history renders the requested localized campaign title and preserves grant/remaining/status accounting.

Simulate a missing exact history translation in an isolated fixture and prove generic localized unavailable-title text is shown instead of internal campaign name/English fallback.

## Scenario F — operational isolation

Prove multilingual work did not change:

```text
scope targeting
BillingPlan target identity
shop target identity
quantity
starts/expires lifecycle
selection serializable concurrency
credit grant/reservation/commit accounting
```

DATABASE-003 migration must create only the translation table/constraints and must not alter the PromotionCampaign table physically.

## Evidence

Completion report table:

| Scenario | PASS/FAIL | DB evidence | Admin/XLSX evidence | Merchant evidence | Isolation evidence |
|---|---|---|---|---|---|

Record exact integrated repository commits.

## Validation

Use existing system-test scripts plus repository-declared type/lint/test checks and `git diff --check`. Do not expose provider secrets.

## Stop conditions

STOP if prerequisites are not integrated, if a production defect is discovered, or if tests would require weakening exact-locale/20-of-20 rules. Return defect to `moda_architect`.
