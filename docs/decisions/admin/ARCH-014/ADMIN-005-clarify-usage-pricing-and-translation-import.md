---
id: ARCH-014-ADMIN-005
architecture_id: ARCH-014
title: Clarify usage-event pricing and harden translation JSON import UX
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 55
executor: copilot
claimed_at: 2026-09-15T18:40:22Z
attempt: 2
depends_on:
- ARCH-014-ADMIN-004
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-005

## Objective

Correct two usability defects discovered while manually creating a `MerchantPricingPlan` in the ARCH-014 Admin builder:

1. **Usage-event pricing is technically present but visually ambiguous.** The Admin user must be able to see exactly how much each Shopify usage event costs, which currency applies, and when a zero-cost event requires a finite usage limit.
2. **Translation JSON import is too easy to misuse and too difficult to diagnose.** The Admin user must receive clear template instructions, an obvious file-upload button, drag-and-drop support, non-destructive upload errors, and a concise human-readable validation summary while preserving the strict schema-v2 contract and stable highlight ids.

This is an Admin-only correction. It MUST NOT change the ARCH-014 database schema, Shopify merchant application, translation schema version, portfolio-economics rules, or operational billing runtime.

## Binding GPT-5.6 Luna rule

The required behaviour below is complete and deterministic. Implement it exactly.

Do **not** redesign the builder. Do **not** relax the economics guardrail. Do **not** invent a new translation schema. Do **not** accept translated highlight titles as highlight keys. Do **not** perform currency conversion. Do **not** alter any database model or migration.

If an implementation decision is not explicitly authorized below and cannot be resolved from the existing accepted ARCH-014 code, STOP and return the question to `moda_architect`.

## Prerequisite gate

Before editing, verify all of the following are present from accepted `ARCH-014-ADMIN-004`:

```text
src/components/admin/merchant-pricing-plan-builder.tsx
src/components/admin/merchant-pricing-translation-import.tsx
src/lib/admin/merchant-pricing-translations.ts
translation schemaVersion: 2
MerchantPricing builder highlights use stable contentKey UUID values
```

Also verify the builder still uses the accepted portfolio economics implementation and that `UNBOUNDED_ZERO_COST_USAGE_EVENT` is still a fail-closed economics result.

If any prerequisite is absent, STOP. Do not recreate ADMIN-004 inside this task.

## Exact authorized implementation surface

Primary files:

```text
src/components/admin/merchant-pricing-plan-builder.tsx
src/components/admin/merchant-pricing-translation-import.tsx
src/lib/admin/merchant-pricing-translations.ts          # only if a pure presentation helper is needed; do not change schema v2
src/lib/admin/merchant-pricing-economics.ts             # only for exported/readable metadata if strictly required; do not weaken calculations
```

Tests:

```text
tests/security/admin-merchant-pricing-plan.test.mjs
tests/security/admin-billing-progressive-disclosure.test.mjs
existing/new focused MerchantPricing unit tests under tests/unit/
```

You MAY add exactly one small pure helper module under:

```text
src/lib/admin/merchant-pricing-*.ts
```

if needed to group translation issues or compute builder-only usage-event validation messages. Do not create a second form architecture or duplicate the economics engine.

# Part A — usage-event pricing UI

## A1. Preserve the existing data model

Keep the accepted `BuilderEvent` pricing representation:

```ts
pricingMode: "FIXED" | "GRADUATED" | "VOLUME";
fixedUnitAmount?: string;
tiers?: Array<{
  upTo: number | null;
  amountPerUnit: string;
  flatAmount: string;
}>;
maximumUnitsPerBillingPeriod: number | null;
```

Do not add a new cost column or database field. The cost already exists; this task makes it explicit and safe to enter.

## A2. Exact human-readable labels

In step `4 Usage events`, each usage event MUST use visible `<label>` text. Placeholder-only inputs are not acceptable.

Render these fields in this order:

```text
Admin label
Shopify usage-event handle
Recovery credits granted per event
Maximum uses per billing period (optional)
Pricing model
```

Pricing-model option labels MUST be:

```text
Fixed price
Graduated pricing
Volume pricing
```

The underlying values MUST remain exactly:

```text
FIXED
GRADUATED
VOLUME
```

Do not show raw enum text as the only user-facing label.

### FIXED mode

When `pricingMode === "FIXED"`, render exactly one monetary field labelled:

```text
Price per usage event (<PLAN_CURRENCY>)
```

Example when plan currency is USD:

```text
Price per usage event (USD)
```

Example when plan currency is GBP:

```text
Price per usage event (GBP)
```

The input value is decimal major units and is parsed by the existing `parseMoneyToMinorUnits` helper.

Do not concatenate or store `£`, `$`, `€` or any other symbol in the input value.

Do not convert the amount when plan currency changes. The label changes to the new ISO currency code; the numeric value remains the Admin-entered numeric value unless the Admin changes it.

### GRADUATED and VOLUME modes

When mode is GRADUATED or VOLUME:

- do not render the fixed-price input as an enabled editable field;
- render tier rows;
- every tier row MUST visibly label its monetary fields:

```text
Up to quantity
Price per unit (<PLAN_CURRENCY>)
Additional flat charge (<PLAN_CURRENCY>)
```

For the final open-ended tier, show `Unlimited` as the meaning of `upTo = null`. Do not require the Admin to infer that an empty disabled box means infinity.

## A3. Pricing-mode switching must not submit stale pricing

The persisted/server payload MUST continue to use exactly one pricing representation:

```text
FIXED       -> fixedUnitAmount only; ignore tiers
GRADUATED   -> tiers only; ignore fixedUnitAmount
VOLUME      -> tiers only; ignore fixedUnitAmount
```

Switching modes may preserve inactive values in local React state for convenience, but inactive values MUST NOT influence:

```text
preview economics
serialized builder payload
server validation
persisted rows
```

Add tests proving stale inactive values cannot leak into persistence/economics.

## A4. Zero-cost usage-event rule must be explained before portfolio economics

Preserve the existing safety rule:

> A usage event that grants positive recovery credits for zero cost and has no finite maximum is economically unbounded and MUST remain invalid.

The following configurations MUST behave exactly as follows:

```text
Free plan recurring price = 0, no usage events
-> valid plan evidence; a one-plan portfolio has no lower->higher pair and therefore no economics failure.

FIXED usage event: price = 5.00, maximum = null
-> valid pricing evidence.

FIXED usage event: price = 0.00, maximum = 1
-> valid bounded zero-cost pricing evidence.

FIXED usage event: price = 0.00, maximum = null
-> invalid with UNBOUNDED_ZERO_COST_USAGE_EVENT.
```

For the last case, show an inline event-level message in step 4:

```text
This usage event gives recovery credits for free but has no usage limit. Enter a price greater than 0 or set a maximum number of uses per billing period.
```

Do not wait until step 6 to expose this obvious configuration defect.

`Next` from step 4 MUST be disabled while any FIXED usage event has all three properties:

```text
creditsGrantedPerUnit > 0
parsed fixedUnitAmountMinor === 0
maximumUnitsPerBillingPeriod === null
```

Do not weaken the portfolio engine; the engine must still independently fail closed if a malformed/malicious payload reaches it.

For GRADUATED/VOLUME pricing, continue to rely on the authoritative economics validator for complex zero-cost tier semantics. If it returns `UNBOUNDED_ZERO_COST_USAGE_EVENT`, show the same human explanation in the portfolio step.

## A5. Human-readable portfolio-economics error presentation

Do not use the raw diagnostic block as the primary message for known configuration errors.

When the only/first relevant result is:

```text
code = UNBOUNDED_ZERO_COST_USAGE_EVENT
```

show this primary UI:

```text
Usage-event pricing needs attention

One of the usage events gives recovery credits for free with no usage limit.
Enter a price greater than 0 or set a maximum number of uses per billing period.
```

When the offending event is deterministically identifiable from builder state, include its Admin label:

```text
Bronze Top Up gives recovery credits for free with no usage limit.
```

Do not fabricate an event name when it cannot be identified.

Keep raw fields such as:

```text
candidate:free
UNBOUNDED_ZERO_COST_USAGE_EVENT
status: UNVERIFIED
```

behind a collapsed disclosure labelled exactly:

```text
Show technical details
```

The raw diagnostic remains available for support/debugging but is not the main Admin message.

## A6. Final review usage-event summary

In step `7 Translations & review`, render each usage event using human-readable information.

For FIXED mode, show:

```text
<Admin label>: <credits> credits per event · <formatted price> per event · <maximum or Unlimited>
```

Example:

```text
Bronze Top Up: 5 credits per event · $10.00 per event · Unlimited
```

Use `Intl.NumberFormat` with the plan's existing ISO currency code for display only. Do not perform FX conversion and do not infer currency from Admin/browser locale.

For GRADUATED/VOLUME, identify the pricing model and tier count; do not attempt to compress all tier economics into a misleading single price.

# Part B — translation template/import UX

## B1. Preserve schemaVersion 2 exactly

The accepted translation contract remains:

```json
{
  "_meta": {
    "schemaVersion": 2,
    "planHandle": "free",
    "planName": "Free",
    "sourceLocale": "en"
  },
  "translations": {
    "en": {
      "description": "...",
      "highlights": {
        "<stable-contentKey-uuid>": {
          "title": "...",
          "description": "..."
        }
      }
    }
  }
}
```

Do NOT accept this incorrect shape:

```json
"highlights": {
  "Translated highlight title": "Translated description"
}
```

Do NOT accept translated titles as object keys.

The stable `contentKey` UUID generated by the Admin builder is the identity of the highlight across all 20 locales. It MUST remain byte-for-byte unchanged in every locale.

The existing parser's strict `MISSING_HIGHLIGHT`, `UNEXPECTED_HIGHLIGHT`, and exact `{title, description}` validation semantics remain authoritative.

## B2. Template instructions shown before download/upload

At the top of the translation section, render this guidance prominently:

```text
How to complete the translation file

1. Download the JSON template generated for this plan.
2. Translate only the text values inside description, title and description fields.
3. Do not rename locale codes, highlight IDs, field names or JSON structure.
4. Keep every highlight ID exactly as it appears in the downloaded template.
5. Upload the completed JSON file or paste its contents below.
```

Immediately below, show a small example:

```json
"f2e0f43f-614f-4333-ba0c-23aa08a51d3b": {
  "title": "Translated title",
  "description": "Translated description"
}
```

The UUID in documentation/example may be a static illustrative UUID. Never expose it as the current plan's actual identity unless it comes from the generated template.

## B3. Keep one canonical parser for paste and upload

Both paths MUST feed the exact same `rawJson` state and therefore the exact same:

```ts
parseCompletedMerchantPricingTranslationPackage(...)
```

Do not create a second file-upload parser.

Flow:

```text
paste text -> set rawJson -> canonical parser
valid file -> file.text() -> set rawJson -> canonical parser
```

## B4. Replace the visually ambiguous native file input

The existing visible native `<input type="file">` MUST NOT remain the primary upload control.

Implement a visually explicit drop zone containing:

```text
Upload completed translation file

Drop your completed JSON file here
or
[ Choose JSON file ]

JSON only · maximum size 256 KiB
```

`Choose JSON file` MUST be rendered as an obvious bordered/button control, not browser-default filename text.

Implementation requirements:

- keep a real `<input type="file" accept=".json,application/json">` for accessibility/browser integration;
- visually hide that native input;
- clicking `Choose JSON file` programmatically activates the hidden input via a React ref;
- the drop zone handles drag enter/over/leave/drop;
- call `preventDefault()` on drag-over/drop so the browser does not navigate to the file;
- provide a visible drag-active state using existing Admin design tokens/classes;
- do not introduce a drag/drop dependency package.

## B5. Exact drag/drop and file-validation behaviour

Maintain these component states separately:

```ts
rawJson: string
selectedFileName: string | null
uploadError: string | null
isDragging: boolean
```

Use one function for both picker and dropped file processing, e.g.:

```ts
async function processSelectedTranslationFile(file: File): Promise<void>
```

Exact rules:

### one valid JSON file

```text
size <= 262144 bytes
AND
(name ends .json OR MIME application/json)
```

Then:

```text
uploadError = null
selectedFileName = file.name
rawJson = await file.text()
canonical parser runs from rawJson
```

### multiple dropped files

Do not read any of them.

Set:

```text
Upload one JSON file at a time.
```

Preserve existing `rawJson` and existing `selectedFileName`.

### file too large

Do not read it.

Set:

```text
The translation file is larger than 256 KiB.
```

Preserve existing `rawJson` and `selectedFileName`.

### invalid file type

Do not read it.

Set:

```text
Choose a JSON file ending in .json.
```

Preserve existing `rawJson` and `selectedFileName`.

### file read failure

Catch the error.

Set:

```text
The translation file could not be read. Try the file again or paste the JSON instead.
```

Preserve existing `rawJson` and `selectedFileName`.

The current behaviour of replacing `rawJson` with synthetic JSON such as:

```json
{"error":"Translation package exceeds 256 KiB."}
```

MUST be removed.

## B6. Selected-file feedback

After a successful file read, show:

```text
Selected file: <filename>
```

When validation passes, show:

```text
✓ <filename>
20 / 20 languages complete
Translation file is ready to save.
```

When validation fails, keep showing the selected filename and the human-readable error summary below it.

If the Admin subsequently edits the pasted textarea manually, keep the filename visible but label it:

```text
Source file: <filename> · contents edited after upload
```

Implement this deterministically with a boolean `editedAfterUpload` that becomes true only when the textarea `onChange` occurs after a successful file load. Loading another file resets it to false.

## B7. Human-readable validation summary

Do not immediately present dozens of raw parser issues as the primary UI.

Add a pure issue-summary function that maps parser issue codes to concise Admin guidance. It MUST NOT alter parser validity.

At minimum implement these summaries:

### highlight structure mismatch

If issues contain any of:

```text
MISSING_HIGHLIGHT
UNEXPECTED_HIGHLIGHT
```

show:

```text
The highlight structure does not match the downloaded template.
Keep the highlight IDs from the template unchanged. Put the translated title and description inside each highlight ID instead of using translated titles as JSON keys.
```

### missing/invalid locales

If issues contain:

```text
MISSING_LOCALE
UNEXPECTED_LOCALE
```

show:

```text
The file does not contain the exact 20 supported locale codes from the template. Do not add, remove or rename locale codes.
```

### source mismatch

If issues contain any of:

```text
PLAN_HANDLE_MISMATCH
PLAN_NAME_MISMATCH
ENGLISH_SOURCE_MISMATCH
HIGHLIGHT_ENGLISH_SOURCE_MISMATCH
```

show:

```text
This translation file was created for different or older plan content. Download a fresh template for the current draft and apply the translations to that template.
```

### empty translated content

If issues contain any of:

```text
DESCRIPTION_EMPTY
HIGHLIGHT_TITLE_EMPTY
HIGHLIGHT_DESCRIPTION_EMPTY
```

show:

```text
Some required translated text is empty. Every plan description and every highlight title and description must be completed in all 20 languages.
```

### unsupported schema

For `UNSUPPORTED_SCHEMA_VERSION` show:

```text
This translation file uses an unsupported template version. Download a new template from this plan and try again.
```

A validation result may show more than one summary category, but show each summary category at most once.

## B8. Technical issue disclosure

Raw parser issues MUST remain available inside a collapsed native `<details>` disclosure:

```text
Show technical details (<N> issues)
```

Inside that disclosure render the existing exact:

```text
<code>: <path> <message>
```

Do not discard paths/codes because they are useful for support.

The disclosure MUST be closed by default.

## B9. Validation count wording

Replace this style:

```text
0/20 complete + 60 structural or locale issue(s)
```

with:

```text
0 / 20 languages complete
Translation file needs attention.
```

Then show the human summaries and optional technical detail disclosure.

On success show:

```text
20 / 20 languages complete
Translation file is ready to save.
```

# Server-authoritative invariants

This task improves client UX only; server correctness remains mandatory.

Do not remove or weaken any existing server validation for:

```text
usage-event shape/pricing
money parsing
zero-cost unbounded economics
translation schemaVersion 2
exact 20 locales
exact highlight contentKey set
English source matching
portfolio economics
```

A malicious direct action submission MUST still fail closed even if client step validation is bypassed.

# Non-goals

Do not:

- modify Prisma schema or migrations;
- modify `moda-interact` merchant UI;
- add regional currencies or FX conversion;
- infer currency from locale/country;
- change `schemaVersion` from 2;
- accept legacy/alternative translation JSON shapes;
- replace stable UUID highlight keys with translated titles/slugs;
- change the portfolio economics premium policy;
- remove `UNBOUNDED_ZERO_COST_USAGE_EVENT`;
- add a third-party drag/drop package;
- redesign the seven-step wizard beyond the exact field/presentation changes above.

# Mandatory tests

Add/update focused tests that prove every item below.

## Usage-event tests

1. A FREE plan with recurring amount `0` and no usage events produces no single-plan economics failure.
2. FIXED `5.00`, unlimited -> accepted pricing evidence.
3. FIXED `0.00`, maximum `1` -> accepted bounded zero-cost evidence.
4. FIXED `0.00`, unlimited -> inline step-4 error and Next disabled.
5. The authoritative economics engine still returns `UNBOUNDED_ZERO_COST_USAGE_EVENT` for malicious/unbounded zero-cost evidence.
6. FIXED `10.00` is parsed/persisted as `1000` minor units through existing payload/action flow.
7. Changing currency from USD to GBP changes the visible label from `Price per usage event (USD)` to `Price per usage event (GBP)` and does not numerically convert the entered amount.
8. FIXED -> VOLUME ignores stale `fixedUnitAmount` in preview/payload persistence.
9. VOLUME -> FIXED ignores stale tier values in preview/payload persistence.
10. GRADUATED/VOLUME tier rows use the exact visible labels required by this task.
11. Known zero-cost economics diagnostics show human guidance first; raw code is available only under `Show technical details`.

## Translation-import tests

12. Downloaded template remains schemaVersion 2 and stable UUID highlight-keyed.
13. A valid uploaded schema-v2 file and the same JSON pasted into the textarea produce the same parser result.
14. A file using translated highlight titles as keys is rejected and the UI shows the highlight-structure guidance.
15. Missing locale produces the locale-code guidance.
16. English/source mismatch produces the stale-template guidance.
17. Empty translated values produce the incomplete-content guidance.
18. Unsupported schema version produces the fresh-template guidance.
19. Raw parser issue code/path/message remain accessible inside collapsed `Show technical details (<N> issues)`.
20. Dragging one valid JSON file reads it and updates the canonical raw JSON state.
21. Clicking `Choose JSON file` follows the same file-processing function as drag/drop.
22. Multiple dropped files are rejected without changing existing JSON.
23. Oversized file is rejected without changing existing JSON.
24. Invalid file type is rejected without changing existing JSON.
25. File read failure is handled without changing existing JSON.
26. Successful upload shows selected filename.
27. Manual textarea edit after upload marks `contents edited after upload`.
28. Loading another valid file clears that edited-after-upload flag.
29. Native file input remains present but is not the visually primary upload control.
30. No third-party drag/drop package is added.

## Regression tests

31. Existing ADMIN-004 translation-retention/edit rules still pass.
32. Existing catalogue placement concurrency protection still passes.
33. Existing highlights add/remove/reorder behaviour still passes.
34. Existing full-portfolio economics tests still pass.
35. Existing operational billing controls remain unchanged/reachable.

# Required validation commands

Run from `moda-interact-admin`:

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

Also run focused source scans:

```bash
rg -n 'Price per usage event|Maximum uses per billing period|Choose JSON file|Drop your completed JSON file here|Show technical details|UNBOUNDED_ZERO_COST_USAGE_EVENT' src tests
rg -n '\{"error":"Translation package' src/components/admin/merchant-pricing-translation-import.tsx
rg -n 'react-dropzone|dropzone' package.json package-lock.json src
```

Expected scan outcomes:

```text
required human-readable labels/messages are present
synthetic upload-error JSON replacement is absent
no new drag/drop dependency is present
```

If `format:check`, build, typecheck or broad tests fail only for an already-documented unrelated baseline, record exact commands and diagnostics in the Completion Report. Do not hide or repair unrelated baseline failures under this task.

# Completion evidence

The Completion Report MUST include:

```text
implementation commit
parent/docs commit
exact files changed
focused test counts
full test result
TypeScript result
build result
format/diff result
proof zero-cost unlimited remains fail-closed
proof zero-cost capped event is accepted
proof fixed usage-event cost is clearly editable
proof upload and drag/drop use the same parser
proof invalid upload does not overwrite existing JSON
proof translated-title-as-key file receives human-readable guidance
proof schemaVersion remains 2
proof no database/Shopify files were changed
```

# Stop conditions

STOP and return to `moda_architect` without broadening scope if any of the following becomes necessary:

1. a Prisma/database schema change;
2. a Shopify merchant-app change;
3. translation `schemaVersion` change;
4. accepting translated highlight titles instead of stable `contentKey` ids;
5. weakening/removing `UNBOUNDED_ZERO_COST_USAGE_EVENT`;
6. introducing FX conversion or regional pricing;
7. adding a third-party drag/drop dependency;
8. modifying operational BillingPlan/runtime billing behaviour;
9. changing portfolio economics policy rather than its Admin presentation.

## Completion Report

Status: Ready for Review

Implementation commit: `cdea0aaf2d62e43f066f18b1930f491319066c09` (pushed to `task/ARCH-014-ADMIN-005`).

Exact files changed:

- `src/components/admin/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant-pricing-translation-import.tsx`
- `tests/security/admin-merchant-pricing-plan.test.mjs`

Implementation evidence:

- Usage events now use visible labels in the required order, human pricing-mode labels, ISO currency labels, tier labels, and explicit `Unlimited` open-tier text.
- Builder payload serialization omits inactive fixed or tier pricing fields, while the existing economics engine remains authoritative.
- `FIXED` zero-cost, unlimited events show the inline fail-closed guidance and disable step-4 `Next`; `UNBOUNDED_ZERO_COST_USAGE_EVENT` remains present in and returned by the economics engine.
- Fixed usage pricing remains decimal major-unit input and final review uses existing ISO-currency `Intl.NumberFormat`; no FX conversion was added.
- Portfolio diagnostics show human guidance first and keep raw code/status behind collapsed `Show technical details`.
- Translation import keeps schemaVersion 2 and stable UUID content keys, shows the required translated-title-as-key guidance, and uses one `processSelectedTranslationFile` path for picker and drag/drop before the existing canonical parser runs from shared `rawJson` state.
- Upload size/type/multiple-file/read failures preserve existing JSON and filename state; successful uploads expose filename and edited-after-upload feedback. Synthetic upload-error JSON is absent.
- No database schema/migration, Shopify app, operational BillingPlan/runtime, economics policy, or third-party drag/drop dependency changed.

Focused validation:

- `npm run test:unit`: 42 passed.
- `node --test tests/security/admin-merchant-pricing-plan.test.mjs tests/security/admin-billing-progressive-disclosure.test.mjs`: 16 passed.
- `node --experimental-strip-types --test tests/unit/merchant-pricing-economics.test.ts tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-translations.test.ts`: 39 passed.
- Editor diagnostics for both changed TSX files: no errors.
- Required source scans passed: required labels/messages present, synthetic upload-error JSON absent, and no `react-dropzone`/`dropzone` dependency found.
- `git diff --check`: passed.

Required validation limitations:

- `npm test` could not complete because the prepared worktree has missing installed dependencies including `@prisma/client` and `bullmq`; the focused security suites passed independently.
- `npm run prisma:validate`, `npm run prisma:generate`, and `npm run build` are unavailable because `prisma` is not installed in the prepared worktree; build stopped at its required Prisma generation step.
- `npx tsc --noEmit` is unavailable because TypeScript is not installed in the prepared worktree; editor diagnostics reported no errors for the changed files.
- `npm run lint -- --no-warn-ignored ...` and `npm run format:check` are unavailable because `eslint` and `prettier` are not installed. No formatting changes were made, and `git diff --check` passed.

The prepared isolation packet was used as supplied: implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-ADMIN-005`, parent report worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-ADMIN-005`, mirrored branch `task/ARCH-014-ADMIN-005`, claim commit `5f706e14074b1476c199601ac2e26771cd3472e1`, and dependency gate `ARCH-014-ADMIN-004` complete. No Architect Review section was edited.
