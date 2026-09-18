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
status: complete
priority: 67
executor: null
claimed_at: null
attempt: 1
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

## Completion Report

### Status

Ready for architect review.

### Launcher evidence

- Claim commit: `5021fd11e245087d55ac58c2db4825e5adacef74`
- Attempt: `1`
- Dependency gate: passed (`ARCH-014-ADMIN-008` and `ARCH-014-ADMIN-009` complete)
- Parent and implementation worktrees were created at the canonical paths.
- Recursive database submodule sync/update passed; recorded commit was `47232f6876469f209c7efde4cefbb8a47d864e6a`.

### Files changed

- `src/lib/admin/promotion-translation-workbook.ts`
- `src/lib/admin/background-runtime-control-validation.ts`
- `tests/unit/promotion-translation-workbook.test.ts`
- `tests/unit/background-runtime-control-validation.test.ts`

### Implementation

- Rejected oversized workbook bytes before lazy-loading ExcelJS, workbook construction, or XLSX parsing.
- Added the exact 2 MiB boundary regression assertion using a non-XLSX buffer.
- Formatted all runtime range errors through display metadata so millisecond-backed fields report seconds and UI values.
- Added exact quiet-window and maximum-settle-window error assertions.
- No workbook schema, runtime bounds, persistence, authorization, concurrency, worker, or merchant-rendering behavior was changed.

### Validation Results

- `node --test tests/unit/promotion-translation-workbook.test.ts tests/unit/background-runtime-control-validation.test.ts`: passed, 11/11.
- `npm test`: 173 passed, 4 unrelated baseline failures in existing observability/internationalization contracts (`shared-runtime-ownership`, shared ICU version, catalogue alignment, and merchant translation coverage).
- `npm run build`: passed; emitted existing BullMQ optional-dependency and critical-dependency warnings.
- `npm run lint --if-present`: passed.
- `git diff --check`: passed.
- Dependencies were installed with `npm ci` from the existing lockfile because the fresh implementation worktree had no `node_modules`; no dependency files changed.

### Completion Protocol

- Returned only ADMIN-010 to `review`.
- Dependent system-test work was not started.
## Architect Review

### Review Status

Accepted

### Attempt Reviewed

Attempt 1 — implementation `6995200`, Completion Report `28740ba`.

### Functional assessment

ADMIN-010 satisfies both narrow corrective contracts. `parsePromotionTranslationWorkbook(...)` now rejects `bytes.byteLength > PROMOTION_TRANSLATION_WORKBOOK_MAX_BYTES` before lazy-loading ExcelJS, constructing a workbook, or calling `workbook.xlsx.load(...)`, so direct lower-level callers cannot force an oversized XLSX parse. The returned primary issue remains exactly `INVALID_XLSX` / `The workbook exceeds the 2 MiB limit.`

Runtime range errors now derive minimum, maximum and unit from the same display metadata used by the Admin controls. Millisecond-backed settle fields therefore report `0.25–10 seconds` and `1–30 seconds` rather than persisted millisecond bounds labelled as seconds. Integer/ordinary-second fields retain equivalent existing behavior, and cross-field rules are unchanged.

The implementation commit changes only the two authorized production files plus their focused unit tests. No workbook schema/sheets, `exceljs@4.4.0`, DATABASE-004 bounds, authorization, persistence/audit/CAS behavior, Background workers, promotion lifecycle/localization rules or Shopify merchant rendering were changed. The reported repository-wide baseline failures are unrelated and do not block this functionality-first review.

No further ADMIN-010 implementation attempt is required.

### Dependency result

`ARCH-014-ADMIN-010` is Complete. `ARCH-014-SYSTEM-TEST-002` has all four prerequisites Complete in this branch and is promoted to Ready; it remains developer-gated and must not auto-start. `ARCH-014-SYSTEM-TEST-003` remains Pending because corrective Background tasks `ARCH-014-BACKGROUND-006` and `ARCH-014-BACKGROUND-007` are not yet Complete.
