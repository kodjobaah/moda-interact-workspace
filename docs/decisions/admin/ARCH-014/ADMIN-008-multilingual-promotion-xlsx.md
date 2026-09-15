---
id: ARCH-014-ADMIN-008
architecture_id: ARCH-014
title: Author multilingual promotion campaigns with the shared pre-populated XLSX workflow
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 58
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-014-DATABASE-003
- ARCH-014-ADMIN-006
enables:
- ARCH-014-SYSTEM-TEST-002
created: 2026-09-15
updated: 2026-09-16T00:20:00Z
---

# ARCH-014-ADMIN-008

## Objective

Make Promotion Campaign merchant-facing content complete in all 20 supported locales using the **same pre-populated XLSX workflow and the same spreadsheet package established by ADMIN-006**.

The Admin user supplies English source content; Moda generates the spreadsheet structure, all 20 language labels/locale codes and any still-valid stored translations. The human fills only genuinely missing cells.

## Binding GPT-5.6 Luna rule

Do not design a second spreadsheet subsystem. `ARCH-014-ADMIN-006` is the mandatory spreadsheet foundation.

Before editing verify:

```text
exceljs is installed at exact version 4.4.0
src/lib/admin/translation-workbook-common.ts exists
ADMIN-006 is complete
DATABASE-003 PromotionCampaignTranslation exists
```

If any prerequisite is absent, STOP. Do not install `xlsx`, SheetJS, another Excel library, CSV fallback or drag/drop dependency.

## Spreadsheet package standard

Use exactly the existing `exceljs@4.4.0` from ADMIN-006. Do not modify its version and do not add another spreadsheet package.

Reuse `translation-workbook-common.ts` for:

```text
lazy ExcelJS loading
XLSX MIME/type handling
2 MiB maximum file size
canonical 20 locale + language-label metadata
shared safe-cell checks where exported
```

Promotion-specific workbook semantics belong in a new feature helper; generic mechanics remain shared.

## Merchant-facing content model

`PromotionCampaign.name` is now explicitly **internal Admin-only**.

The campaign form MUST present:

```text
Internal campaign name
[ ... ]
Only administrators see this name.

English merchant title
[ ... ]

English merchant description
[ ... ]
```

Limits:

```text
internal name: 1..255
merchant title: 1..255
merchant description: 1..10000
```

Do not use the legacy scalar `PromotionCampaign.merchantDescription` as the new merchant-facing source. Do not remove/change that database column.

## Draft lifecycle and persistence

### Create draft

On create, within the existing promotion transaction:

1. validate campaign operational fields exactly as today;
2. create `PromotionCampaign` as `DRAFT` using internal `name`, scope/quantity/target/dates; omit the legacy scalar merchantDescription from new writes so it remains null for new campaigns;
3. create exactly one `PromotionCampaignTranslation` row for locale `en` using English merchant title/description;
4. create the existing CREATED lifecycle event;
5. commit atomically.

A new draft is intentionally `1 / 20 languages complete` until a complete workbook is imported.

### Edit draft English source

For a DRAFT campaign:

- if English title and description are byte-for-byte unchanged after existing trim normalization, preserve all existing translation rows;
- if either English title or English description changes, update the `en` row and delete **all 19 non-English translation rows in the same transaction**. Do not attempt field-level translation retention for campaigns. The next workbook download therefore contains current English plus blank non-English cells.

This deliberately simple rule prevents stale promotion copy.

ACTIVE campaign terms/translations remain immutable under the existing rule. Do not allow translation edits after activation; materially changed merchant copy requires a new campaign.

## Promotion workbook contract

Create:

```text
src/lib/admin/promotion-translation-workbook.ts
src/components/admin/promotion-translation-workbook.tsx
```

Normal Admin UI MUST NOT expose JSON.

Use exactly three worksheets in this order:

```text
Instructions
Translations
_meta
```

`_meta` is `veryHidden` on generation.

### Visible Translations sheet

Exact headers:

```text
A1 Language
B1 Locale
C1 Merchant title
D1 Merchant description
```

Rows 2-21 are the exact 20 language/locale entries supplied by `translation-workbook-common.ts`. The user never enters language names or locale codes.

Pre-populate:

```text
English row -> current English title + description
non-English row with stored valid translation -> existing title + description
missing non-English row -> blank C/D cells
```

Use the same usability conventions as ADMIN-006: freeze header/A:B, widths, wrap text, pale-yellow blank required cells, autofilter.

### Instructions sheet

Must tell the user:

```text
This spreadsheet is already populated with all 20 supported languages.
Fill only blank Merchant title / Merchant description cells.
Do not change Language, Locale, worksheet names or the English source row.
Save as .xlsx and upload it back to Moda Interact.
```

Also show internal campaign name for context and explicitly state it is not translated/merchant-facing.

### _meta sheet

Exact key/value rows:

```text
workbookKind                      moda-interact-promotion-translations
workbookSchemaVersion             1
campaignId                        <campaign id>
campaignInternalName              <PromotionCampaign.name>
sourceLocale                      en
sourceMerchantTitle               <current English title>
sourceMerchantDescription         <current English description>
localeOrder                       <JSON exact 20 locale order>
```

Do not use merchant title as an identity key.

## Workbook upload/import

Campaign must already exist as DRAFT before translations can be uploaded. On the creation panel, after successful draft creation the existing navigation/edit state should lead the Admin to the draft where the translation section is available.

UI:

```text
Translations
1 / 20 languages complete

[ Download pre-populated translation spreadsheet ]

Upload completed translation spreadsheet
┌─────────────────────────────────────────────┐
│ Drop your completed .xlsx spreadsheet here │
│                     or                      │
│          [ Choose spreadsheet ]             │
│ .xlsx only · maximum size 2 MiB            │
└─────────────────────────────────────────────┘
```

Drag/drop and picker MUST call one processing function. No third-party drop package.

Workbook parser validates in this exact order:

1. XLSX load succeeds;
2. exact sheet names;
3. exact workbook kind/schema version;
4. campaign id/internal name matches current draft;
5. English source title/description matches current draft;
6. exact locale order;
7. exact headers;
8. exact Language/Locale row labels/order;
9. title/description cells are blank or plain strings only; never evaluate formulas;
10. convert to canonical promotion translation package;
11. validate exact 20/20 completeness before persistence.

Use workbook issue codes consistent with ADMIN-006 where semantically identical (`INVALID_XLSX`, `MISSING_WORKSHEET`, `HEADER_MISMATCH`, `LOCALE_ROW_MISMATCH`, `LANGUAGE_LABEL_MISMATCH`, `UNSUPPORTED_CELL_VALUE`) plus:

```text
CAMPAIGN_ID_MISMATCH
CAMPAIGN_NAME_MISMATCH
ENGLISH_SOURCE_MISMATCH
```

## Canonical internal package

JSON is internal only. Define one parser/validator in:

```text
src/lib/admin/promotion-translations.ts
```

Canonical shape:

```json
{
  "_meta": {
    "schemaVersion": 1,
    "campaignId": "...",
    "campaignInternalName": "...",
    "sourceLocale": "en",
    "sourceMerchantTitle": "...",
    "sourceMerchantDescription": "..."
  },
  "translations": {
    "cs": { "merchantTitle": "...", "merchantDescription": "..." },
    "en": { "merchantTitle": "...", "merchantDescription": "..." }
  }
}
```

Validator MUST require exactly the canonical 20 locale keys and non-empty title/description for all locales before import can persist.

Do not expose this JSON editor to humans.

## Import persistence action

Add a dedicated SUPER_ADMIN server action for a DRAFT campaign translation import. The client submits canonical JSON produced by the workbook adapter, not XLSX bytes.

Inside one transaction:

1. re-read campaign + current English row;
2. require status `DRAFT`;
3. parse canonical package server-side again;
4. require campaign/source metadata match fresh DB values;
5. require exact 20/20;
6. delete existing translation rows for that campaign;
7. create exactly 20 validated rows;
8. increment `PromotionCampaign.version` using optimistic `updateMany` against the version read at transaction start;
9. if version update count != 1, rollback with `Promotion campaign changed; reload and retry.`;
10. commit and revalidate `/promotions`.

Do not activate automatically after import.

## Activation gate

Both UI and server are authoritative:

- DRAFT card shows translation state: `1 / 20`, `20 / 20`, etc.;
- Activate button is visually disabled/absent until 20/20;
- server `intent === "activate"` re-reads translations inside the activation transaction and requires exact 20 locales with non-empty title/description;
- malicious/direct activation with fewer than 20 MUST fail and status remains DRAFT.

Exact primary message:

```text
Complete all 20 merchant translations before activating this campaign.
```

## Human-readable validation feedback

Do not display raw cell/JSON paths as primary UI. Group missing translations by language, for example:

```text
Missing translations

Japanese (ja)
• Merchant description

Thai (th)
• Merchant title
• Merchant description
```

Technical workbook/parser codes may be available under collapsed `Show technical details`.

## Promotion list/form presentation

Update campaign list/history Admin UI to continue showing `PromotionCampaign.name` as the internal name. Do not replace Admin history/report headings with merchant translations; this distinction is intentional.

Label the old field clearly so there is no ambiguity between internal campaign name and merchant title.

## Mandatory tests

Prove at minimum:

1. ExcelJS exact version remains `4.4.0`; no second spreadsheet package added.
2. Promotion workbook imports shared common XLSX/locale helper rather than redefining locale labels.
3. New draft writes internal name + one English translation row.
4. Existing unchanged English edit preserves translation rows.
5. English title change deletes non-English rows and preserves new English.
6. English description change does the same.
7. Workbook contains exact 20 pre-populated language/locale rows.
8. Existing valid translations are pre-populated.
9. Missing translations are blank only.
10. English source is populated and protected by validation.
11. Changed-source stale workbook is rejected.
12. Wrong campaign workbook is rejected.
13. Formula/non-string cell is rejected and never evaluated.
14. Upload/picker use one parser path.
15. Incomplete workbook does not persist partial 20-locale package.
16. Complete workbook persists exactly 20 rows atomically.
17. Direct activation at 1/20 is rejected.
18. Activation at 20/20 succeeds under existing lifecycle semantics.
19. ACTIVE translations remain immutable.
20. Legacy scalar `PromotionCampaign.merchantDescription` is not used as localized source and schema is unchanged.
21. Existing scope/target/quantity/date/lifecycle tests still pass.

## Required validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm test
npx tsc --noEmit
npm run build
npm run format:check
git diff --check
```

Also:

```bash
rg -n 'exceljs|xlsx|sheetjs|react-dropzone' package.json package-lock.json src
rg -n 'PromotionCampaignTranslation|merchantTitle|merchantDescription' src tests
```

Expected: only `exceljs@4.4.0` is the spreadsheet library; no new spreadsheet/drop dependency.

## Stop conditions

STOP if DATABASE-003 is absent, ADMIN-006 shared spreadsheet helper is absent, implementing this requires another XLSX library, or activation integrity would require changing the database schema. Do not infer an alternative architecture.

## Completion Report

Status: Ready for Review

### Implementation

- Implementation commit: `50e9d5e` (`feat(admin): add multilingual promotion translations`), pushed to `origin/task/ARCH-014-ADMIN-008`.
- Audit-fix commit: `76d3131` (`fix(admin): close promotion translation audit gaps`), pushed to `origin/task/ARCH-014-ADMIN-008`.
- Added the canonical promotion translation package/validator, promotion-specific XLSX adapter, client upload/download workflow, atomic draft/import persistence, exact 20-locale activation gate, translation completeness state, and focused workbook tests.
- Legacy `PromotionCampaign.merchantDescription` remains unchanged and is not read as localized source. No database, Shopify, or dependency files changed.

### Validation

- Focused promotion validation/workbook tests: `10/10` passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run test:unit`: `118/118` passed after widening discovery to all TypeScript unit tests.
- `node --test tests/security/admin-promotions.test.mjs`: `13/13` passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency warnings remain.
- Touched-file Prettier check and `git diff --check`: passed.
- `npm test`: existing unrelated baseline failures remain in shared-package version assertions (`^0.11.2` installed, tests expect `^0.7.3`); no ADMIN-008 failure was reported.
- Repository-wide `npm run format:check`: existing baseline reports 99 files; all ADMIN-008 files pass the focused check.

### Contract evidence

- Generated workbook sheets are exactly `Instructions`, `Translations`, `_meta`; `_meta` is `veryHidden`.
- Workbook uses shared `translation-workbook-common.ts`, exact `exceljs@4.4.0`, exact 20 locale labels/order, English source protection, blank missing cells, 2 MiB limit, and no drop dependency.
- XLSX parsing validates metadata/rows/plain strings, rejects formulas as `UNSUPPORTED_CELL_VALUE`, converts to canonical JSON, and server-reparses before atomic 20-row replacement with version CAS.
- New drafts persist only internal campaign terms plus one English translation row; changed English source deletes non-English rows; unchanged source preserves translations; active translations remain immutable.
- Activation re-reads translations and rejects incomplete campaigns with `Complete all 20 merchant translations before activating this campaign.`
- Admin history/report headings continue to use the internal campaign name; merchant-facing title/description are translation-backed.

### Audit findings resolved

- Workbook parsing now rejects non-exact worksheet sets/order before metadata or translation processing, and requires exactly eight ordered `_meta` key/value rows.
- Import replacement now deletes and creates the complete validated 20-row set before the optimistic campaign-version CAS, so any CAS failure rolls the replacement back atomically.
- The configured unit command now discovers all TypeScript unit tests instead of only the unrelated economics guardrail file.
- The promotion security assertion for `expiresAt` is whitespace-tolerant after formatting, with no behavior change to the lifecycle form.

### Isolation

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-ADMIN-008`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-ADMIN-008`.
- Implementation and report changes remain on dedicated task branches; neither branch was merged to `main`.
- Task lifecycle is returned to `review` with executor and claim cleared for architect handoff.
