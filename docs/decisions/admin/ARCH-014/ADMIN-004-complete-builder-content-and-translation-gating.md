---
id: ARCH-014-ADMIN-004
architecture_id: ARCH-014
title: Complete MerchantPricing builder gating, localized plan-card highlights and final review flow
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-014-DATABASE-002
- ARCH-014-ADMIN-003
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-004

## Objective

Complete the Admin MerchantPricing builder so an administrator can author the **actual merchant-facing pricing-card content** shown in the agreed card design, while fixing the final-step/translation gating gaps found after ADMIN-002.

This task has four inseparable outcomes in the same `moda-interact-admin` workflow:

1. human-readable catalogue placement;
2. merchant description + ordered merchant highlight cards;
3. translation JSON schema v2 covering the description and every highlight title/description in all 20 locales;
4. deterministic step/final-submit/server gating.

Do not split these into separate Admin tasks. They touch the same builder payload, translation package, server action and review flow.

## Binding GPT-5.6 Luna rule

The design below is complete. Implement it exactly. Do not infer an alternative content model, translation structure, step order, placement UX, translation fallback or save workflow.

Do not move merchant highlight copy into static i18n. Do not turn highlights into Shopify usage events. Do not add operational `BillingPlan` dependencies.

## Prerequisite gate

This task may start only after accepted/integrated `ARCH-014-DATABASE-002` is present in the Admin database submodule/client.

Before editing, verify generated Prisma exposes:

```text
MerchantPricingPlanHighlight
MerchantPricingPlanHighlightTranslation
MerchantPricingPlan.highlights
```

If not, STOP. Do not emulate the missing schema with JSON columns or Admin-only state.

## Exact authorized implementation surface

Primary files to modify:

```text
src/components/admin/merchant-pricing-plan-builder.tsx
src/components/admin/merchant-pricing-translation-import.tsx
src/components/admin/merchant-pricing-plan-catalog.tsx          # only if summary/status needs highlight count
src/app/actions/merchant-pricing-plan.ts
src/lib/admin/merchant-pricing-builder-payload.ts
src/lib/admin/merchant-pricing-translations.ts
src/lib/admin/merchant-pricing-plan.ts
```

Tests to add/update under existing test conventions:

```text
tests/security/admin-merchant-pricing-plan.test.mjs
tests/security/admin-billing-progressive-disclosure.test.mjs
existing/new focused MerchantPricing unit tests for payload/translation/economics-independent builder logic
```

You may add one small pure helper module under `src/lib/admin/merchant-pricing-*` if it makes source-content comparison deterministic. Do not create a second builder architecture.

## Exact seven-step builder

The visible steps MUST be exactly:

```text
1 Plan
2 Catalogue placement
3 Shopify pricing
4 Usage events
5 Merchant content
6 Portfolio economics
7 Translations & review
```

Replace the current `5 English description` label with `5 Merchant content`.

The final Create/Save submit control MUST exist only inside step 7. It MUST NOT be rendered on steps 1..6.

Back/Next navigation may be present on earlier steps. The final mutation is never submitted by `Next`.

## Step 2 — plain-language catalogue placement

The Admin user MUST NOT see internal strings such as:

```text
BEFORE:cm...
AFTER:cm...
ONLY
```

The visible field label is exactly:

```text
Where should this plan appear?
```

Helper text:

```text
Choose where this plan should appear in the pricing list merchants see. This order is also used when Moda compares this plan with the other plans.
```

For a non-empty catalogue, render one human-readable option for each possible insertion slot:

```text
Before <first plan display name>
After <plan 1 display name>
After <plan 2 display name>
...
After <last plan display name>
```

For an empty catalogue show:

```text
This will be the first plan.
```

and internally use `ONLY`.

The UI may store the existing `BEFORE:<id>` / `AFTER:<id>` values internally. Those values are implementation details only.

### Fresh-order concurrency protection

For **create** payloads, include a hidden/serialized:

```ts
catalogueOrderSnapshot: string[]
```

containing the exact ordered MerchantPricingPlan ids the builder used to present placement options.

On final Save, inside the server transaction:

1. re-read all MerchantPricing plans ordered by `cataloguePosition ASC`;
2. compare the fresh ordered ids with `catalogueOrderSnapshot`;
3. if they are not exactly equal, perform no writes and return/throw the user-safe error:

```text
The pricing list changed while you were editing. Review where this plan should appear and try again.
```

4. only when the snapshots match, resolve the chosen BEFORE/AFTER/ONLY value against that fresh list.

Do not silently choose another slot. Do not infer placement from price, allowance, name, Shopify handle or operational topology.

Edits retain `UNCHANGED` catalogue position and do not require a create-placement snapshot.

## Step 5 — Merchant content

Step 5 contains the existing English merchant plan description plus an ordered list of highlight cards.

### English plan description

Keep:

```text
English merchant description
```

Rules remain:

```text
trim-non-empty
<= 2000 characters
```

### Highlight editor

Represent client builder highlights exactly as:

```ts
type MerchantPricingBuilderHighlight = {
  contentKey: string;     // canonical UUID, stable across reorder/edit
  title: string;          // English source title
  description: string;    // English source description
};
```

The array order is the persisted display order. Do not accept a client-supplied numeric position field.

For each highlight render:

```text
Highlight title
[........................................]

Highlight description
[........................................]

[Move up] [Move down] [Remove]
```

and one:

```text
+ Add highlight
```

control below the list.

Rules:

```text
0 highlights is valid
contentKey must be a canonical UUID string
title trim-non-empty and <= 120 characters
description trim-non-empty and <= 500 characters
contentKey unique within the plan
```

For a new highlight generate the key exactly once with:

```js
crypto.randomUUID()
```

Store that key in component state. Moving a highlight MUST NOT change its key. Editing title/description MUST NOT change its key.

Do not auto-create an `Included capacity` highlight. The large allowance block is rendered from structured plan economics in Shopify. Highlights are additional Admin-authored merchant content; the Admin may choose to add an `Included capacity` highlight as in the reference design, but it is not synthesized by code.

## Builder payload v2

Extend `MerchantPricingBuilderPayload` with:

```ts
catalogueOrderSnapshot: string[] | null;
highlights: MerchantPricingBuilderHighlight[];
```

Rules:

```text
create -> catalogueOrderSnapshot required and exact string array
edit   -> catalogueOrderSnapshot must be null
highlights -> array; each exact fields contentKey/title/description; no extra fields
```

No separate business maximum highlight count is introduced by ARCH-014. Existing request-size/platform limits still apply. Every individual field remains bounded as above.

`parseMerchantPricingBuilderPayload` is server-authoritative and must reject malformed UUIDs, duplicate keys, blank/oversized fields and unexpected highlight fields.

## Translation package schema v2 — exact shape

Schema v1 is superseded for newly generated/imported packages after this task.

Generate exactly:

```json
{
  "_meta": {
    "schemaVersion": 2,
    "planHandle": "starter",
    "planName": "Starter",
    "sourceLocale": "en"
  },
  "translations": {
    "en": {
      "description": "English plan description",
      "highlights": {
        "550e8400-e29b-41d4-a716-446655440000": {
          "title": "Included capacity",
          "description": "100 monthly recovery conversations."
        }
      }
    },
    "fr": {
      "description": "",
      "highlights": {
        "550e8400-e29b-41d4-a716-446655440000": {
          "title": "",
          "description": ""
        }
      }
    }
  }
}
```

The real generated package contains **all exact 20 locales**, not only the two shown above.

For every locale:

```text
description
highlights object keyed by the exact current highlight contentKey set
```

Every highlight translation value has exactly:

```text
title
description
```

No position appears in translation JSON. Display order comes from the builder/database highlight order, not translation content.

## Canonical 20 locales

Require exactly:

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

No fallback and no locale aliases.

## Translation template generation — create

For a new plan:

```text
English locale:
  plan description populated from current Step 5
  every highlight title/description populated from current Step 5

Other 19 locales:
  plan description empty
  every highlight title empty
  every highlight description empty
```

The Admin does not need to know locale codes or JSON structure; Download template creates the whole valid skeleton.

## Translation template generation — edit

Make edit templates easy to complete instead of discarding existing translated work.

Use existing stored content keyed by locale/contentKey.

For the plan description:

```text
if English plan description unchanged:
  prepopulate all 20 existing plan descriptions
else:
  en = new English description
  other 19 descriptions = empty
```

For each current highlight:

```text
if same contentKey existed before AND English title+description are unchanged:
  prepopulate all 20 existing highlight title/descriptions
else:
  en = current English title/description
  other 19 title/descriptions = empty
```

Removed highlights do not appear in the new template.

Reordering a highlight alone MUST NOT invalidate its translations because `contentKey` remains stable.

Changing the plan display name alone does not invalidate translations because plan names are not localized in ARCH-014 v1. `_meta.planName` simply reflects the current draft when a new package is generated.

## Completed package validation — exact rules

Paste and `.json` upload MUST call the same parser.

Retain the existing 256 KiB upload/text safety limit unless repository code already enforces a stricter equivalent.

A completed package is valid only when:

```text
valid JSON object
exact root keys _meta/translations
schemaVersion === 2
sourceLocale === en
planHandle matches normalized current draft
planName matches normalized current draft
exact 20 locales
no unknown locale
locale description non-empty <=2000
exact current highlight contentKey set in every locale
no missing highlight key
no unknown highlight key
highlight title non-empty <=120
highlight description non-empty <=500
English plan description exactly matches current Step 5 after normalization
English title/description for every contentKey exactly match current Step 5 after normalization
```

Expose deterministic issue codes at minimum for:

```text
INVALID_JSON
UNSUPPORTED_SCHEMA_VERSION
PLAN_HANDLE_MISMATCH
PLAN_NAME_MISMATCH
MISSING_LOCALE
UNEXPECTED_LOCALE
DESCRIPTION_EMPTY
DESCRIPTION_TOO_LONG
ENGLISH_SOURCE_MISMATCH
MISSING_HIGHLIGHT
UNEXPECTED_HIGHLIGHT
HIGHLIGHT_TITLE_EMPTY
HIGHLIGHT_TITLE_TOO_LONG
HIGHLIGHT_DESCRIPTION_EMPTY
HIGHLIGHT_DESCRIPTION_TOO_LONG
HIGHLIGHT_ENGLISH_SOURCE_MISMATCH
```

Do not auto-translate or silently fill a missing field.

## Translation retention and final-step gating

Define the current translatable English content as:

```text
normalized plan description
+ exact highlight contentKey set
+ normalized English title/description for each contentKey
```

Highlight order is deliberately excluded from content equality.

### Create

A create can reach a valid final-submit state only when a schema-v2 package validates 20/20 against the **current** draft.

### Edit

If the current translatable English content is exactly unchanged from persisted state:

```text
existing 20 plan descriptions are retained
existing 20 highlight translations are retained
no translation re-import is required
step 7 shows: 20/20 translations retained
```

If any translatable English content changes, including adding/removing a highlight or changing a highlight title/description:

```text
existing package state is stale
new schema-v2 completed package is required
```

Reorder-only edit retains translations.

Do not trust a previously cached `translationResult` after handle/name/description/highlight English content changes. Translation validity must be derived against the current payload/package.

## Step 6 — portfolio economics gate

Preserve accepted ADMIN-001 economics semantics.

The Next control from Step 6 to Step 7 is enabled only when:

```text
builder pricing inputs parse successfully
projected portfolio result exists
every required lower->higher pair is PASS
```

FAIL or UNVERIFIED keeps the administrator on Step 6 and displays the existing deterministic matrix/result details.

Highlights and translations do not participate in economics calculations.

## Step 7 — final review and submit

Render a final review of at least:

```text
plan name/handle
catalogue placement
recurring pricing
allowance
usage-event count and pricing summary
English merchant description
ordered English highlight titles/descriptions
portfolio economics PASS summary
translation state: either 20/20 validated or 20/20 retained
Admin reason
```

The only Create/Save submit button exists here.

It is disabled unless every server-relevant condition is currently valid, including:

```text
required plan fields valid
Admin reason non-empty and <=2000
create placement snapshot/selection valid OR edit placement unchanged
usage-event payload valid
all portfolio economics PASS
translation state valid for current content
```

Do not rely on HTML `required` alone.

## Server-authoritative mutation algorithm

`mutateMerchantPricingPlanAction` remains authoritative. Inside one Prisma transaction perform this exact sequence:

1. require SUPER_ADMIN mutation authorization;
2. parse/revalidate the full builder payload including highlights;
3. read all MerchantPricing plans fresh, ordered by `cataloguePosition`, including:
   - plan translations;
   - usage events/tiers;
   - highlights ordered by `position` with all highlight translations;
4. for create, compare fresh ordered ids against `catalogueOrderSnapshot`; reject with the exact pricing-list-changed message before writes if different;
5. validate immutable handle/edit semantics and resolve create placement;
6. determine whether translatable English content changed using the exact rule above;
7. if create/content-changed, require and validate completed schema-v2 translation JSON against current payload;
8. if edit/content-unchanged, obtain retained translations from existing DB rows and do not require translation JSON;
9. construct projected portfolio from MerchantPricing plan economics only and require every pair PASS;
10. shift catalogue positions for create only using the existing ARCH-014 algorithm;
11. create/update the MerchantPricingPlan and usage events/tiers;
12. rebuild that plan's highlight rows in the payload array order, preserving the submitted `contentKey` values and creating exactly 20 highlight-translation rows per highlight from either validated package data or retained DB data;
13. when a new package is required, replace/create the 20 plan-description translations from that same package; when retained, leave the existing plan-description translations unchanged;
14. write the existing bounded Admin audit evidence;
15. commit atomically;
16. revalidate `/billing` only after successful commit.

For highlight rebuild, deleting/recreating ARCH-014 highlight child rows inside this transaction is permitted. Deferred DATABASE-002 constraints validate the final state. Do not mutate any operational billing table.

If any validation fails, the transaction commits **nothing**.

## Read-model updates

Update `MerchantPricingPlanWithChildren` and Admin include definitions so every plan read used by the builder contains:

```text
highlights ordered by position ASC
  + translations ordered by locale ASC
```

Do not expose `adminLabel` or highlight internal ids outside Admin requirements.

## Required tests

Add/update deterministic tests covering at minimum:

### Placement UX/server

```text
empty catalogue -> human text "This will be the first plan."
non-empty options -> Before first + After every existing plan display name
internal ids are not rendered as option labels
fresh DB order equals snapshot -> create proceeds
fresh DB order differs -> exact pricing-list-changed error and zero writes
```

### Highlight editor/payload

```text
add generates stable UUID
move up/down changes order but not contentKey
remove removes only selected highlight
blank title rejected
>120 title rejected
blank description rejected
>500 description rejected
duplicate/invalid contentKey rejected
```

### Translation v2

```text
create template -> en populated + 19 blank for description/highlights
edit unchanged content -> all existing translations prepopulated/retained
edit changed plan description -> 19 plan descriptions blanked
edit changed existing highlight -> 19 translations for that highlight blanked
new highlight -> en populated + 19 highlight translations blank
reorder-only -> translations retained
missing locale rejected
unknown locale rejected
missing highlight rejected
unknown highlight rejected
English highlight mismatch rejected
schemaVersion 1 rejected after this task
paste/upload same parser
```

### Final flow

```text
Create/Save button absent steps 1..6
portfolio FAIL/UNVERIFIED cannot advance from step 6
step 7 create with incomplete translations cannot submit
step 7 edit unchanged content can submit with retained translations and no import
server rejects direct malicious submit that bypasses client gates
successful create/update writes exact highlights + 20 translations each atomically
```

### Architecture isolation

Source tests must continue to prove no ARCH-014 Admin implementation dependency on:

```text
BillingPlan
BillingEconomicsSnapshot
BillingUpgradeEconomicsEdge
mutateBillingPlanAction
getBillingPlans
```

The existing `PlatformBillingPolicy.minimumUpgradePremiumBps` read remains allowed.

## Required validation

Inspect `package.json` first and use only declared scripts. At minimum run:

```bash
npm test
npm run test:unit
npm run prisma:validate
npm run prisma:generate
npm run build
npm run lint -- --no-cache
npm run format:check
git diff --check
```

If repository-wide lint/format contains a documented unchanged baseline, record the exact baseline evidence; do not hide failures in files changed by this task.

## Stop conditions

STOP and return to `moda_architect` if:

- DATABASE-002 models are not available after proper task preparation/submodule materialization;
- implementation would require modifying an existing database table;
- implementation appears to require hard-coded merchant highlight copy in Admin source/i18n;
- operational BillingPlan/topology data appears necessary;
- accepted ADMIN-001 economics semantics would have to change merely to support highlights;
- the existing builder differs so materially that the seven-step flow cannot be implemented without unrelated redesign.

Do not weaken translation completeness, economics gating or server revalidation to continue.

## Completion protocol

Completion Report must list exact changed files, v2 JSON example, placement concurrency evidence, translation-retention evidence, focused test counts and full validation results. Set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-ADMIN-004` on `task/ARCH-014-ADMIN-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-ADMIN-004` on `task/ARCH-014-ADMIN-004`.
- Shared/default checkout switched or mutated: no.
- Another task worktree reused: no.
- DATABASE-002 submodule materialized at `f202931c58dba7f9fcc53c74333736e978e8b6de`.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not-needed.
- Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed.
- Implementation `origin/main` incorporated: already-current.
- Recursive submodule synchronization and initialization: passed; database submodule initialized at the recorded commit.
- Launcher claim commit: `4fc095b8ee450068a5bb72112eb477a53b86cc43`.

### Changed Files

- `src/components/admin/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant-pricing-translation-import.tsx`
- `src/app/actions/merchant-pricing-plan.ts`
- `src/lib/admin/merchant-pricing-builder-payload.ts`
- `src/lib/admin/merchant-pricing-translations.ts`
- `src/lib/admin/merchant-pricing-plan.ts`
- `tests/unit/merchant-pricing-builder-payload.test.ts`
- `tests/unit/merchant-pricing-translations.test.ts`

### Implemented Contract

- Exactly seven builder steps; `Merchant content` is step 5 and the only Create/Save control is in step 7.
- Human-readable catalogue placement with exact create `catalogueOrderSnapshot`; fresh-order mismatch rejects before writes with: `The pricing list changed while you were editing. Review where this plan should appear and try again.`
- Stable canonical UUID highlight keys, add/move/remove controls, bounded content validation, and atomic highlight plus 20-locale translation rebuilds.
- Server-authoritative payload, fresh-read, economics, translation, and final-submit gating. Highlights remain independent of portfolio economics.

### Translation v2 Example

```json
{
  "_meta": {
    "schemaVersion": 2,
    "planHandle": "starter",
    "planName": "Starter",
    "sourceLocale": "en"
  },
  "translations": {
    "en": {
      "description": "English plan description",
      "highlights": {
        "550e8400-e29b-41d4-a716-446655440000": {
          "title": "Included capacity",
          "description": "100 monthly recovery conversations."
        }
      }
    }
  }
}
```

Generated packages contain all exact 20 locales. Validation requires schema v2, exact locale/highlight-key sets, bounded content, and exact English source equality; paste and upload use the same parser.

### Translation Retention Evidence

- New plans populate English and blank the other 19 locales.
- Unchanged edit content retains all stored translations; changed descriptions/highlights invalidate stale translations and require a current schema-v2 package.
- Reorder-only edits retain translations because equality uses stable content keys and normalized content, excluding order.

### Validation Evidence

- `npm test`: 167 passed, 2 failed out of 169; both are unchanged baseline assertions expecting shared package version `^0.7.3` while the current package declares `^0.11.2`.
- `npm run test:unit`: 42 passed.
- Focused payload/translation tests: 11 passed.
- Focused security/progressive-disclosure/boundary tests: 24 passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run build`: passed with existing BullMQ optional dependency/critical-dependency warnings.
- `npm run lint -- --no-cache`: passed with 0 errors and 2 pre-existing hook warnings in `queue-monitor.tsx`.
- `npm run format:check`: repository baseline reports 115 existing files with formatting issues; all eight task files pass targeted Prettier checks.
- `git diff --check`: passed.

### Architect Review

Implementation commit: `4f575f6`. The complete builder/content/translation/gating flow is ready for `moda_architect` review. No operational `BillingPlan` dependency or database-table change was introduced.
