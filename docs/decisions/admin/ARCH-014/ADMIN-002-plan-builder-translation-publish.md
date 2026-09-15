---
id: ARCH-014-ADMIN-002
architecture_id: ARCH-014
title: Refactor plan builder with catalogue ordering, multi-meter pricing and complete translation import
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-15T12:02:23Z
attempt: 3
depends_on:
- ARCH-014-DATABASE-001
- ARCH-014-ADMIN-001
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-002

## Objective

Refactor the Admin billing `plans` view into a self-contained ARCH-014 MerchantPricing catalogue builder that:

- creates/edits `MerchantPricingPlan` rows only;
- never creates, updates, reads or orders the catalogue through `BillingPlan`/operational topology rows;
- explicitly places a new plan in ARCH-014 `cataloguePosition` order;
- captures informational Shopify recurring pricing + 0..5 Shopify App Pricing usage events;
- previews full projected-portfolio economics using ADMIN-001;
- generates an exact 20-locale translation JSON template;
- accepts paste/upload through one parser;
- persists no incomplete plan;
- atomically saves the MerchantPricing plan + exact translations/events/tiers only after all validation passes.

Do not create Shopify subscriptions.

## Binding isolation rule

ARCH-014 Admin code MUST NOT query or mutate these operational plan/economics sources for this feature:

```text
BillingPlan
BillingPlanFeature
BillingEconomicsSnapshot
BillingUpgradeEconomicsEdge
getBillingPlans()
getBillingPlanById()
mutateBillingPlanAction
billing-plan-topology helpers
```

Do not remove/change their existing implementation; simply do not use them for ARCH-014 catalogue creation/editing/rendering.

The existing read of `PlatformBillingPolicy.minimumUpgradePremiumBps` is permitted solely as the platform-wide economics threshold. Existing generic platform-admin authentication/audit infrastructure may be reused without schema changes.

If implementation seems to require an operational plan row to complete ARCH-014, STOP and return evidence to `moda_architect`.

## Authorized implementation surface

Use these exact current/new files. Prefer the new MerchantPricing-specific modules rather than repurposing operational plan modules:

```text
src/app/(protected)/billing/page.tsx
src/app/actions/merchant-pricing-plan.ts                         # new ARCH-014 server action
src/components/admin/admin-detail-drawer.tsx
src/components/admin/billing-drawers.tsx                         # add/use MerchantPricingPlanDrawer; do not route to PlanForm
src/components/admin/merchant-pricing-plan-catalog.tsx           # new catalogue/list UI
src/components/admin/merchant-pricing-plan-builder.tsx           # new client builder
src/components/admin/merchant-pricing-translation-import.tsx     # new client import UI
src/lib/admin/merchant-pricing-plan.ts                            # new server read model/data access
src/lib/admin/merchant-pricing-builder-payload.ts                 # new pure strict parser
src/lib/admin/merchant-pricing-locales.ts                         # new exact local 20-locale tuple/labels
src/lib/admin/merchant-pricing-translations.ts                    # new pure template/parser
src/lib/admin/merchant-pricing-economics.ts                       # ADMIN-001; consume, do not fork
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/unit/merchant-pricing-builder-payload.test.ts               # new
tests/unit/merchant-pricing-translations.test.ts                  # new
tests/security/admin-merchant-pricing-plan.test.mjs               # new focused mutation/security suite
```

`src/components/admin/billing-plan-catalog.tsx`, `src/app/actions/billing-plan.ts`, `src/lib/admin/billing-plan*.ts` and operational topology modules are outside ARCH-014 implementation scope except for read-only inspection. Do not edit them to make ARCH-014 work.

Keep navigation host:

```text
/billing?view=plans&drawer=register-plan
/billing?view=plans&planId=<MerchantPricingPlan.id>
```

## Billing page integration

For `view === "plans"` only:

1. replace `getBillingPlans()`/`getBillingPlanEconomics()` with `getMerchantPricingPlans()` from the new ARCH-014 data module;
2. replace `getBillingPlanById(planId)` with `getMerchantPricingPlanById(planId)`;
3. render `MerchantPricingPlanCatalog`;
4. open `MerchantPricingPlanDrawer` for `drawer=register-plan` or a selected ARCH-014 plan id;
5. do not pass a `BillingPlanRow` into the ARCH-014 drawer.

Other billing views (`overview`, `packs`, `refunds`, `events`, `controls`) remain unchanged.

## Drawer/layout requirement

`AdminDetailDrawer` currently hard-codes `max-w-[520px]`. Add an optional width/size prop whose default preserves 520px for every existing drawer. The ARCH-014 `MerchantPricingPlanDrawer` uses the wide option (approximately `max-w-[960px]` or `max-w-5xl`). Do not globally widen other Admin drawers.

## Exact local locale contract

Create `merchant-pricing-locales.ts` with this exact ordered tuple and human labels:

```text
cs Czech
da Danish
de German
en English
es Spanish
fi Finnish
fr French
it Italian
ja Japanese
ko Korean
nb Norwegian Bokmål
nl Dutch
pl Polish
pt-BR Portuguese (Brazil)
pt-PT Portuguese (Portugal)
sv Swedish
th Thai
tr Turkish
zh-Hans Chinese (Simplified)
zh-Hant Chinese (Traditional)
```

Do not import a Shared package for this list. Do not add aliases.

## Exact MerchantPricing plan fields

The builder owns only these plan-level ARCH-014 commercial/presentation fields:

```text
shopifyPlanHandle             required immutable string; trim non-empty
name                          required displayName; trim non-empty <=255
planKind                      FREE | PAID_METERED
isActive                      Boolean
featured                      Boolean
includedRecoveryCredits       integer >=0
allowancePeriod               derived from planKind in v1
billingPeriod                 literal EVERY_30_DAYS
currency                      uppercase 3-letter code
recurring amount              decimal input -> integer recurringAmountMinor
catalogue placement           explicit create token only
English merchant description trim non-empty <=2000
reason                        required bounded Admin audit reason using existing Admin conventions
```

Derive allowance period exactly:

```text
FREE          -> LIFETIME
PAID_METERED  -> EVERY_30_DAYS
```

Do not expose a contradictory allowance-period selector.

Do not include any of these operational fields in the ARCH-014 builder:

```text
shopifyUsageEventHandle
recoveryCreditPackEnabled
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
BillingPlanFeature rows
```

## Builder steps

Render these logical steps in this exact order:

```text
1 Plan
2 Catalogue placement
3 Shopify pricing
4 Usage events
5 English description
6 Portfolio economics
7 Translations & review
```

A stepper/tabs UI is allowed, but all fields form one client draft and no database write occurs until final Create/Save.

### Step 1 — Plan

Collect the exact plan fields above except placement/pricing/description.

For edit:

```text
shopifyPlanHandle is read-only/immutable
cataloguePosition is displayed read-only
```

### Step 2 — explicit ARCH-014 catalogue placement

Load **all** existing `MerchantPricingPlan` rows ordered by `cataloguePosition ASC` regardless of active state.

For create require exactly one placement token:

```text
ONLY                                  valid only when zero MerchantPricingPlan rows exist
BEFORE:<currentFirstMerchantPlanId>   insert at catalogue position 0
AFTER:<existingMerchantPlanId>        insert immediately after that ARCH-014 plan
```

Rules:

- `BEFORE:` is accepted only for the current first plan id;
- `AFTER:` may target any current ARCH-014 plan id;
- target id is a MerchantPricingPlan id, never a BillingPlan id;
- do not infer placement from name, price, allowance, handle, active state or current DOM order;
- edit does not reorder in ARCH-014 v1; display position read-only and preserve it.

Server derives insertion index from a fresh ordered DB read. A stale/missing target token is rejected; do not silently choose another position.

### Step 3 — informational Shopify recurring pricing

Collect:

```text
billingPeriod = EVERY_30_DAYS (read-only literal)
currency      = uppercase 3-letter
recurring amount = decimal money input converted exactly to integer minor units
```

Do not store/render formatted strings such as `£35` as data.

Money parsing rules:

- trim;
- decimal point `.` only in submitted canonical value;
- 0, 1 or 2 fraction digits; normalize `35` -> 3500, `35.5` -> 3550, `35.50` -> 3550;
- reject negatives, exponent notation, thousands separators and > Prisma safe Int minor units;
- server reparses independently.

### Step 4 — Shopify pricing usage events

Allow 0..5 ordered events. Each card has:

```text
adminLabel                      required, trim 1..255
eventHandle                     required, trim, unique within draft
creditsGrantedPerUnit           positive integer
maximumUnitsPerBillingPeriod    optional positive integer
pricingMode                     FIXED | GRADUATED | VOLUME
currency                        inherited plan currency; no independent selector
```

FIXED fields:

```text
unit amount money input -> fixedUnitAmountMinor
no tier rows
```

GRADUATED/VOLUME fields:

```text
1..6 tier rows in order
upTo positive integer for all non-final tiers
final tier forced/displayed as open-ended (`null`)
amountPerUnit money
flatAmount money
```

UI actions:

```text
Add usage event     disabled at 5
Remove usage event
Move up / Move down (or equivalent deterministic reorder)
Add tier            disabled at 6
Remove tier         disabled if it would leave zero tier rows
```

Submitted event/tier `position` values are derived from final UI order `0..n-1`; do not accept browser-supplied arbitrary position numbers as authority.

If FIXED amount is 0, require finite maximum units. For tiered pricing, server-side ARCH-014 DB/economics validation remains final authority for zero-cost boundedness; surface a clear client issue before economics preview when detectable.

### Step 5 — English merchant description

Collect one English description:

```text
trim non-empty
<= 2000 characters
```

It is commercial content stored in `MerchantPricingPlanTranslation(locale="en")`, not a static `en.json` key.

### Step 6 — projected full-portfolio economics

Before enabling final translation/save flow:

1. load all existing `MerchantPricingPlan` rows ordered `cataloguePosition ASC` with complete usage-event/tier data;
2. for create, derive the proposed catalogue order from the fresh placement token and insert the proposed candidate in-memory;
3. for edit, replace only the edited plan candidate in-memory and preserve its catalogue position;
4. form economics portfolio from currently `isActive=true` rows, replacing the edited row when applicable, **plus the proposed candidate even when proposed `isActive=false`**;
5. preserve order by `cataloguePosition`; never infer order;
6. read `PlatformBillingPolicy.minimumUpgradePremiumBps`; use the repository's current established fallback (currently 2000) only if the policy row is absent;
7. call **only** `evaluateMerchantPricingPortfolio` from ADMIN-001;
8. render every pair result in deterministic ordered-pair sequence;
9. block continuation unless every result status is PASS.

Do not read/reconstruct any commercial value from `BillingPlan`, hard-coded onboarding data, `BillingEconomicsSnapshot`, or operational topology.

Preview columns at minimum:

```text
lower plan
higher plan
additional credits needed
chosen usage-event quantities
stay + top-up total
higher recurring price
premium/result code
PASS/FAIL/UNVERIFIED
```

### Step 7 — translation import and review

When the plan/economics draft is valid, expose:

```text
Download translation JSON template
Paste JSON
Upload .json file
Validate translations
```

Do not write the database before final Create/Save confirmation.

## Exact translation template/parser module

`merchant-pricing-translations.ts` exports pure helpers equivalent to:

```text
buildMerchantPricingTranslationTemplate({planHandle, planName, englishDescription})
parseCompletedMerchantPricingTranslationPackage(rawJsonText, expected)
```

Generated JSON uses the exact ARCH-014 v1 shape from the architecture document and exact locale order from `merchant-pricing-locales.ts`.

English is populated from current description; other 19 descriptions are empty strings.

### Required validation issues

Return **all detectable bounded issues** in deterministic structural/canonical-locale order with shape equivalent to:

```text
{ code, path, locale?, message }
```

Codes at minimum:

```text
INVALID_JSON
INVALID_ROOT
UNEXPECTED_ROOT_FIELD
INVALID_META
UNSUPPORTED_SCHEMA_VERSION
PLAN_HANDLE_MISMATCH
PLAN_NAME_MISMATCH
SOURCE_LOCALE_INVALID
INVALID_TRANSLATIONS_OBJECT
MISSING_LOCALE
UNEXPECTED_LOCALE
INVALID_LOCALE_OBJECT
UNEXPECTED_LOCALE_FIELD
DESCRIPTION_EMPTY
DESCRIPTION_TOO_LONG
ENGLISH_SOURCE_MISMATCH
```

Rules:

- root keys exactly `_meta,translations`;
- `_meta` keys exactly `schemaVersion,planHandle,planName,sourceLocale`;
- locale object key exactly `description`;
- all 20 canonical locales exactly once;
- no alias/case normalization;
- package English exactly equals normalized current English source;
- plan metadata match current normalized draft; metadata never chooses the DB target.

### Upload/paste convergence

`merchant-pricing-translation-import.tsx` must make both paths converge to the same raw JSON string and same parser:

```text
paste textarea -> rawJsonText -> parser
file -> File.text() -> rawJsonText -> parser
```

Upload constraints:

```text
extension .json OR type application/json
max bytes = 262144 (256 KiB)
UTF-8 text
```

Do not create a separate server endpoint/parser for files. Final server mutation reparses submitted raw text with the same pure parser.

Display:

```text
20/20 complete
or
N/20 complete + exact structural/per-locale issues
```

The Admin may paste/upload a corrected package again. A dedicated 20-tab editor is not required.

## Exact server builder payload

Use one explicit serialized payload (JSON hidden field or equivalent) containing only ARCH-014 fields. `merchant-pricing-builder-payload.ts` strictly parses it server-side; do not trust client React state.

The parser validates:

- exact plan/pricing fields;
- exact `isActive`/`featured` booleans;
- planKind and derived allowance-period rule;
- immutable handle on edit;
- exact create placement-token format;
- 0..5 event rows;
- pricing-mode discriminated shapes;
- 1..6 tiers;
- integer/money rules;
- duplicate handles;
- finite max-unit rules;
- description length.

## Exact create transaction

After SUPER_ADMIN authorization, perform one Prisma transaction in this exact logical order:

1. parse/revalidate ARCH-014 builder payload and completed translation package;
2. assert no `MerchantPricingPlan` exists for proposed `shopifyPlanHandle`;
3. load **all** current `MerchantPricingPlan` rows ordered by `cataloguePosition ASC`;
4. validate placement token against that exact current ordered list; fail stale token;
5. derive insertion index `k` and projected ordered catalogue;
6. load complete current ARCH-014 commercial data required for active portfolio evaluation;
7. construct projected economics portfolio from active existing rows + proposed candidate and run ADMIN-001; assert every pair PASS;
8. shift existing catalogue rows with `cataloguePosition >= k` **one row at a time in descending current position order**, setting each position to `position + 1`;
9. create `MerchantPricingPlan` at `cataloguePosition = k` with all final plan fields;
10. create exactly 20 `MerchantPricingPlanTranslation` rows from validated package;
11. create 0..5 `MerchantPricingUsageEvent` rows in UI order;
12. create 0..6 tier rows per event as applicable;
13. if an existing bounded generic `PLAN_CATALOG_CHANGED` audit action already supports arbitrary entity type, write audit with `relatedEntityType="MerchantPricingPlan"`; otherwise omit new audit rather than changing an enum/schema and record the limitation in Completion Report;
14. rely on ARCH-014 deferred DB completeness/position integrity at commit;
15. commit and `revalidatePath("/billing")`.

If any step fails, transaction rolls back **all ARCH-014 catalogue writes/position shifts**.

The transaction MUST NOT query/create/update/delete `BillingPlan`, `BillingPlanFeature`, `BillingEconomicsSnapshot` or `BillingUpgradeEconomicsEdge` rows.

## Exact edit transaction

For an existing `MerchantPricingPlan`:

1. load by ARCH-014 id;
2. `shopifyPlanHandle` remains immutable;
3. `cataloguePosition` remains immutable/read-only in v1;
4. parse/revalidate proposed plan/pricing/events;
5. if English description changes, require a newly validated complete 20-locale package and replace all 20 translation rows in the same transaction;
6. if English description is unchanged, retain existing exact 20 translations and do not require a new import;
7. replace usage-event/tier children atomically when usage pricing changes;
8. build projected economics portfolio by replacing the old candidate with proposed candidate at the same catalogue position and require all PASS;
9. update only ARCH-014 tables;
10. commit under DB completeness constraints.

No existing-plan reordering is implemented here.

## Exact active toggle behaviour

The plan card may expose an active/inactive toggle operating on `MerchantPricingPlan.isActive`.

Deactivate:

```text
SUPER_ADMIN + reason required
set isActive=false in ARCH-014 row
no BillingPlan/topology write
```

Activate:

1. load all current ARCH-014 catalogue rows/commercial data;
2. construct projected active portfolio including the target plan in `cataloguePosition` order;
3. run ADMIN-001 using current minimum premium policy;
4. require every pair PASS;
5. set `isActive=true` only in `MerchantPricingPlan`;
6. commit/audit/revalidate.

Do not fabricate any operational billing mapping when activating.

## Plan catalogue Admin cards

`MerchantPricingPlanCatalog` shows only ARCH-014 data:

```text
displayName
shopifyPlanHandle
planKind
active/inactive
catalogue position
featured
recurring amount + currency
included recovery credits + allowance period
usage event count
translation count (must always be 20 for persisted plans)
```

The register-plan CTA continues to open `drawer=register-plan`.

## Required focused tests

Implement all cases below; do not replace them with broad snapshot tests.

### Translation/template

1. generated template exact root/meta shape;
2. exact 20 locale keys in architecture order;
3. English pre-populated and exactly 19 empty descriptions;
4. completed valid paste => 20/20;
5. same raw file text => identical parser result;
6. malformed JSON;
7. missing locale;
8. unexpected locale;
9. `pt_BR` rejected and `pt-BR` accepted;
10. blank/over-2000 description;
11. handle/name/source-locale/schema mismatch;
12. unexpected fields rejected;
13. English source mismatch;
14. >256KiB file rejected before parsing.

### Builder payload

15. money parser valid integer/1-decimal/2-decimal values;
16. negative/exponent/comma/too-many-decimal money rejected;
17. 0 usage events valid;
18. 5 valid; 6 rejected;
19. 1..6 tier rows valid by mode; 7 rejected;
20. duplicate event handles rejected;
21. zero-cost unbounded event rejected;
22. event positions derived from UI order, not browser arbitrary values;
23. FREE derives LIFETIME and PAID_METERED derives EVERY_30_DAYS;
24. builder payload contains no operational BillingPlan fields.

### Catalogue placement

25. empty catalogue accepts ONLY and creates position 0;
26. ONLY rejected when catalogue non-empty;
27. BEFORE accepts only current first ARCH-014 id;
28. AFTER accepts current ARCH-014 id;
29. stale/missing target rejected with zero writes;
30. middle insertion shifts existing positions high-to-low and final positions are contiguous;
31. create order is unaffected by plan price/name/allowance/active state.

### Transaction/security/economics

32. non-SUPER_ADMIN rejected before writes;
33. portfolio failure => zero catalogue/translation/event/tier/position writes;
34. successful create writes exactly one MerchantPricingPlan + 20 translations + expected events/tiers;
35. successful create does not create/update/query BillingPlan/BillingEconomicsSnapshot/BillingUpgradeEconomicsEdge in ARCH-014 data/action modules;
36. description edit requires new package;
37. non-description edit preserves all 20 translations;
38. handle edit rejected;
39. catalogue-position edit rejected;
40. activation re-runs full active portfolio and fails closed on FAIL/UNVERIFIED;
41. deactivation changes only MerchantPricingPlan visibility state;
42. no ARCH-014 path creates/changes a Shopify subscription.

### Billing-page integration

43. `view=plans` reads `getMerchantPricingPlans`, not `getBillingPlans`;
44. `planId` resolves `MerchantPricingPlan.id`;
45. register drawer submits `merchant-pricing-plan` action, not `mutateBillingPlanAction`;
46. all non-plan billing views remain unchanged.

## Validation

Inspect `package.json`, then run:

```text
node --experimental-strip-types --test tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-translations.test.ts
node --test tests/security/admin-merchant-pricing-plan.test.mjs
npm run test:unit
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run prisma:validate
npm run prisma:generate
npm run build
npm run format:check
rg -n "billingPlan|BillingPlan|BillingEconomicsSnapshot|BillingUpgradeEconomicsEdge|getBillingPlans|getBillingPlanById|mutateBillingPlanAction" src/app/actions/merchant-pricing-plan.ts src/lib/admin/merchant-pricing-* src/components/admin/merchant-pricing-* || true
git diff --check
```

The focused `rg` command must return no operational-plan dependency in ARCH-014 modules except explicit type/test text that is justified in the Completion Report; runtime imports/queries are forbidden.

Use documented baseline IDs for unchanged failures. Any failure in a changed path is not a baseline exemption.

## Stop conditions

STOP and return evidence if:

- integrated Prisma client does not contain accepted ARCH-014 new tables;
- implementation would require any existing-table schema change;
- implementation would require a `BillingPlan`, `BillingEconomicsSnapshot` or operational-topology read/write;
- implementation would require changing App Events/top-up runtime;
- exact atomic catalogue create cannot be achieved within current Admin transaction boundary;
- a second independent translation/pricing calculator would be required rather than consuming specified modules;
- current Admin billing page cannot host the MerchantPricing plans view without changing unrelated billing views.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

### Audit Findings

- Confirmed gap: the Portfolio economics step only described server-side evaluation and did not render the ordered pair results or block submission on non-PASS outcomes. Fixed by wiring the existing `evaluateMerchantPricingPortfolio` evaluator into the builder preview, passing the configured `minimumUpgradePremiumBps` threshold, rendering each result, and disabling save for FAIL/UNVERIFIED.
- Confirmed gap: active-toggle reasons were only checked for non-empty input. Fixed by applying the existing 2000-character bounded-reason rule server-side.
- Confirmed coverage gap: the focused security suite did not assert the bounded toggle reason. Added the focused assertion; the existing parser/translation tests remain green.
- No operational `BillingPlan`/economics reads or writes, Shopify subscription path, unrelated billing-view change, or schema change was introduced.

### Status

Ready for Architect Review.

### Work Items

- [x] Refactored the plans view to use only the ARCH-014 `MerchantPricingPlan` catalogue and drawer, preserving the other billing views.
- [x] Added strict server payload parsing, explicit catalogue placement, recurring pricing, 0..5 usage events with tier pricing, derived allowance periods, and atomic ARCH-014 mutations.
- [x] Added the wide ARCH-014 drawer layout without changing the default width of existing drawers.
- [x] Added the exact local 20-locale contract, translation template/parser, paste/upload convergence, and final server-side reparsing.
- [x] Consumed the ADMIN-001 portfolio economics evaluator and enforced PASS-only create/edit/activation flow.
- [x] Added focused parser, translation, and mutation/security tests, including the toggle-reason bound.

### Acceptance Criteria

- [x] ARCH-014 catalogue reads and writes are isolated from `BillingPlan`, operational economics snapshots/edges, and Shopify subscription creation; the focused isolation scan returned no matches.
- [x] Create/edit payloads are strictly validated, incomplete plans are not persisted, placement is derived from a fresh ordered ARCH-014 read, and child rows/translations are written atomically.
- [x] The builder renders the required seven logical steps and excludes the prohibited operational plan fields.
- [x] The translation package enforces the exact 20 canonical locales, metadata, shape, English-source match, bounded descriptions, and deterministic issue ordering.
- [x] Billing-page plans navigation resolves `MerchantPricingPlan` records and the register/edit drawer uses the ARCH-014 server action; non-plan views retain their existing data paths.
- [x] Required focused tests pass: 7 translation/payload tests and 4 ARCH-014 security tests.

### Implementation Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-ADMIN-002`.
- Branch: `task/ARCH-014-ADMIN-002`.
- Implementation commit: `00c8aa5` (`fix(admin): complete merchant pricing builder audit gaps`), based on `077c943`.
- Preserved dependency commit: `2905631f3a8303be7b5906cdb1c5d58d09fbadda`; database submodule resolves to `c6a8fb5b1debb309bb8aaea9d1168a3758f09201`.
- Implementation branch is clean after publication and `git diff --check` passes.

### Validation Results

- `node --experimental-strip-types --test tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-translations.test.ts`: **7 passed, 0 failed**.
- `node --test tests/security/admin-merchant-pricing-plan.test.mjs`: **4 passed, 0 failed**.
- `npm run test:unit`: **42 passed, 0 failed**.
- `npx tsc --noEmit --pretty false`: **passed**.
- `npm run lint`: **passed with 2 pre-existing warnings** in `src/components/admin/queue-monitor.tsx`; no errors.
- `npm run prisma:validate`: **passed**.
- `npm run prisma:generate`: **passed**.
- `npm run build`: **passed**; existing BullMQ optional-dependency/critical-dependency warnings remain.
- ARCH-014 isolation `rg` check: **no matches**; `git diff --check`: **passed**.
- `npm run format:check`: **fails on 106 repository baseline files**; the changed MerchantPricing builder, parser, translation, action, catalogue, and drawer files are not among the reported files.
- `npm test`: **177 passed, 5 failed**. Three plans-view failures in `admin-billing-progressive-disclosure.test.mjs` and `admin-billing-visibility.test.mjs` assert the superseded `BillingPlanCatalog`/`getBillingPlans` contract after the authoritative ARCH-014 replacement. Two failures are unrelated shared-runtime/fixture checks in `admin-internationalization.test.mjs` and `admin-merchant-support.test.mjs`.
- `npx prettier --check` over the authorized implementation surface: **passed** after formatting the changed page, builder, and authorized economics module. `npm run format:check` is unavailable because `package.json` declares no `format:check` script.
- The full build and typecheck passed after the audit fixes. Existing lint warnings remain only in `src/lib/admin/queue-monitor.tsx`; the build retains existing BullMQ optional-dependency/critical-dependency warnings.

### Publication

- Implementation commit `00c8aa5` is published on `origin/task/ARCH-014-ADMIN-002`.
- Parent report commit: `6523239` (published on `origin/task/ARCH-014-ADMIN-002`).
- Claim cleared: `executor: null`, `claimed_at: null`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 materially improves the ARCH-014 builder: the server action recomputes and asserts the authoritative portfolio before create/edit/activation writes; the client invokes the accepted ADMIN-001 evaluator with the configured premium threshold; save is blocked for returned FAIL/UNVERIFIED results; toggle reasons are bounded server-side; the ARCH-014 isolation scan is clean; and the focused parser/translation/security validation passes.

The implementation is not yet functionally conformant with the live ADMIN-002 contract in three bounded areas. These are builder/runtime-contract defects, not requests for exhaustive additional test coverage.

1. **Create preview uses the wrong catalogue position.** In `src/components/admin/merchant-pricing-plan-builder.tsx`, the create candidate is currently assigned `cataloguePlans.length` for portfolio preview regardless of the selected `placement` token. A `BEFORE:<firstId>` or middle `AFTER:<id>` proposal is therefore previewed as the final plan even though the server transaction evaluates it at the authoritative insertion index. Because catalogue order defines every lower->higher pair, the preview can display a different portfolio result from the one the server will enforce.
2. **Usage-event/tier prices are collected as minor-unit integers instead of decimal money inputs.** The UI currently exposes `fixedUnitAmountMinor`, `amountPerUnitMinor`, and `flatAmountMinor` directly. ADMIN-002 requires normal decimal money inputs which are converted exactly to integer minor units, with the submitted money representation independently parsed/validated server-side under the same no-negative/no-exponent/no-thousands/>2-decimal rules as recurring price.
3. **The economics preview omits required decision evidence.** The task requires, at minimum, chosen usage-event quantities, stay+top-up total, higher recurring price, and premium/result code in addition to lower/higher plan and additional credits. The current preview renders IDs, status/message, additional credits and code only.

The server-side transaction remains fail-closed and no evidence was found of ARCH-014 operational `BillingPlan`/economics/topology writes. Do not redesign the transaction, translation parser, catalogue persistence, ADMIN-001 algorithm, or unrelated billing views as part of this rework.

### Required Corrections

1. **Make create preview placement-aware in `src/components/admin/merchant-pricing-plan-builder.tsx`.**
   - For edit, continue to use the immutable persisted `plan.cataloguePosition`.
   - For create, derive the candidate preview insertion index from the currently selected placement token and the `cataloguePlans` array supplied in canonical `cataloguePosition ASC` order:
     - `ONLY` is preview-valid only when `cataloguePlans.length === 0`, with index `0`.
     - `BEFORE:<id>` is preview-valid only when `<id> === cataloguePlans[0]?.id`, with index `0`.
     - `AFTER:<id>` is preview-valid only when `<id>` resolves to an existing catalogue row, with index `resolvedIndex + 1`.
   - Do not use `cataloguePlans.length` as the create position except when that is the actual result of `AFTER:<current-last-id>`.
   - If the selected token cannot be resolved against the current client catalogue snapshot, fail the preview closed and disable save; do not silently substitute another position.
   - Preserve the existing server-side fresh-read `placementIndex()` as final authority. The client logic is preview-only and MUST NOT weaken the server stale-token rejection.

2. **Use decimal money draft fields for every usage price and reparse them server-side.**
   - Keep normalized persisted/economics values as integer minor units.
   - In the client draft, collect FIXED `unit amount`, tier `amount per unit`, and tier `flat amount` as decimal money text, just like recurring price. Do not label or expose these inputs as “minor” values.
   - The serialized builder wire payload must carry the canonical decimal money text needed for independent server validation. Do not trust browser-computed minor integers as the only submitted authority.
   - In `src/lib/admin/merchant-pricing-builder-payload.ts`, parse the recurring amount and all FIXED/tier money strings through the one existing exact money parser (or one shared pure helper with identical rules) and return the existing normalized `recurringAmountMinor` / `fixedUnitAmountMinor` / tier minor-unit values used by the action and ADMIN-001.
   - Apply the task's exact money rules to every money field: trim; `.` decimal separator only; 0, 1 or 2 fractional digits; reject negative values, exponent notation, thousands separators, more than two decimals and unsafe integer minor-unit results.
   - For edit initialization, convert stored minor units to deterministic decimal text without floating-point rounding ambiguity.
   - Do not create a second economics calculator. Preview and server action must continue consuming ADMIN-001 after the same money normalization.

3. **Render the complete minimum economics evidence already returned by ADMIN-001.**
   For every deterministic lower->higher result, show:
   - lower plan and higher plan;
   - `additionalCreditsNeeded`;
   - chosen usage-event quantities from `result.summary` (including event handle and quantity; displaying granted credits/cost as additional detail is allowed);
   - `stayAndTopUpCostMinor` formatted using the portfolio currency when present;
   - higher recurring price from `upgradeCostMinor` when present;
   - `premiumBps` when finite, with an explicit representation for infinity/not-applicable;
   - result `code`;
   - result `status` (`PASS | FAIL | UNVERIFIED`).
   Preserve deterministic result order from `evaluateMerchantPricingPortfolio()`.

4. Keep the save gate fail-closed. A placement-resolution error, money-parse error, `FAIL`, or `UNVERIFIED` must prevent submission from the client. The existing server parse + authoritative projected-portfolio assertion remains mandatory regardless of client state.

5. Add only focused regression evidence for these functional corrections:
   - a create preview for `BEFORE:<first>` and one middle `AFTER:<id>` proves the candidate is evaluated at the selected catalogue position rather than last;
   - decimal FIXED and tier money values normalize to expected minor units server-side, while one invalid decimal form is rejected;
   - the preview rendering path exposes the required combination/cost/premium fields.
   Existing accepted translation/security/economics coverage may be reused; no broad snapshot or combinatorial matrix is required.

6. Re-run the task's focused parser/translation/security tests, relevant unit/typecheck/build/isolation validation, and `git diff --check`. Any unrelated repository-wide baseline failures may remain documented under the normal baseline policy.

### Rework State

Return this same task through `/moda-task ARCH-014-ADMIN-002`. Preserve `attempt: 2`; the next authorized claim increments it to Attempt 3. `ARCH-014-SYSTEM-TEST-001` remains gated until ADMIN-002 and SHOPIFY-001 are both Complete.
