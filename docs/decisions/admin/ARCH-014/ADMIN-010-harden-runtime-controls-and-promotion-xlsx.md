---
id: ARCH-014-ADMIN-010
architecture_id: ARCH-014
title: Harden promotion XLSX parsing and runtime-control validation messages
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 67
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-ADMIN-008
- ARCH-014-ADMIN-009
enables:
- ARCH-014-SYSTEM-TEST-002
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-ADMIN-010

## Objective

Apply two narrow Admin hardening corrections discovered in the current snapshot:

1. reject an oversized promotion XLSX **before** loading/parsing it with ExcelJS;
2. make runtime-control range errors use the same human-facing units shown in the UI rather than stored milliseconds.

Do not redesign either feature.

## Binding scope

Touch only:

```text
src/lib/admin/promotion-translation-workbook.ts
src/lib/admin/background-runtime-control-validation.ts
tests/unit/promotion-translation-workbook.test.ts
tests/unit/background-runtime-control-validation.test.ts
```

Additional directly related test files may be updated only if an existing assertion needs the corrected message/order.

Do not modify database schema, promotion lifecycle rules, workbook sheets/layout, `exceljs@4.4.0`, runtime-control fields/bounds, authorization, optimistic concurrency, Background workers or Shopify merchant rendering.

## Part A — size before parse

Current defect:

```text
parsePromotionTranslationWorkbook(...)
    loads XLSX with ExcelJS
    then checks bytes.byteLength > 2 MiB
```

Move the byte-size check to the very beginning of the parser, **before**:

```text
loadTranslationWorkbookExcelJS()
new ExcelJS.Workbook()
workbook.xlsx.load(...)
```

Required order:

```text
1. inspect bytes.byteLength
2. if > PROMOTION_TRANSLATION_WORKBOOK_MAX_BYTES:
     return invalid with code INVALID_XLSX
     message: The workbook exceeds the 2 MiB limit.
3. only then lazy-load ExcelJS and parse XLSX
```

Keep the existing 2 MiB constant from the ADMIN-006 shared workbook standard. Do not introduce another file-size limit or spreadsheet dependency.

The lower-level parser must be safe even when called directly without the React upload component.

### Required regression test

Pass an oversized `ArrayBuffer` containing non-XLSX bytes directly to `parsePromotionTranslationWorkbook(...)`.

Assert the primary issue is exactly:

```text
INVALID_XLSX
The workbook exceeds the 2 MiB limit.
```

and **not** the unreadable-XLSX message. This proves the size boundary executes before ExcelJS parsing.

Do not allocate an excessively large fixture: exactly `PROMOTION_TRANSLATION_WORKBOOK_MAX_BYTES + 1` bytes is sufficient.

## Part B — human display units in validation errors

`conversationQuietWindowMs` and `conversationMaxSettleWindowMs` are persisted in milliseconds but displayed/edited as seconds.

The current generic range failure constructs its message from stored min/max values while appending `seconds`, which can produce misleading text such as:

```text
250 ... 10000 seconds
```

For every runtime field, the server validation error must report the same display values/unit as the Admin table.

For normal integer/seconds fields, behaviour remains naturally equivalent.

For millisecond-backed fields the required messages are:

```text
Wait after customer message must be between 0.25 and 10 seconds.
Maximum message settle time must be between 1 and 30 seconds.
```

Use the existing field metadata / `runtimeFieldDisplayValue(...)` and `displayUnit ?? unit`; do not hard-code these two messages in a special-case branch.

A suitable generic construction is:

```text
<label> must be between <display min> and <display max> <display unit>.
```

`runtimeFieldDisplayRange(...)` must continue to render the compact UI range with an en dash. Do not change the table presentation merely to build the error message.

## Required tests

Add exact assertions for:

```text
conversationQuietWindowMs below 250ms-equivalent input
    -> Wait after customer message must be between 0.25 and 10 seconds.

conversationMaxSettleWindowMs above 30s
    -> Maximum message settle time must be between 1 and 30 seconds.
```

Retain tests for integer bounds and cross-field rules.

## Required validation

Run from `moda-interact-admin`:

```bash
node --test tests/unit/promotion-translation-workbook.test.ts tests/unit/background-runtime-control-validation.test.ts
npm test
npm run build
npm run lint --if-present
git diff --check
```

If the repository's `npm test` runner is not Node's native runner for `.ts`, use the repository-declared command that currently executes these files and record the exact command. Do not skip the two focused tests.

## Stop conditions

STOP and return to architect if either correction would require:

- changing workbook schema/sheet names;
- changing `exceljs@4.4.0`;
- changing DATABASE-004 bounds;
- changing runtime-control persistence/audit/CAS semantics;
- changing promotion activation/localization rules.
