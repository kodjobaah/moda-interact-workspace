---
id: ARCH-025-ADMIN-001
architecture_id: ARCH-025
title: Extract typed pricing-plan draft/controller
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: copilot
claimed_at: 2026-10-02T19:02:37Z
attempt: 1
depends_on: []
enables:
  - ARCH-025-ADMIN-002
created: 2026-10-02
updated: 2026-10-02
---

# Extract typed pricing-plan draft/controller

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the MerchantPricingPlanBuilder local draft, transition rules and derived controller state into a typed pure reducer/controller plus thin React hook, while making the existing source-based security assertions extraction-safe before any substantial JSX moves.

## Context

The 1,553-line builder currently stores many independent `useState` values and embeds plan-kind, placement, navigation, economics-override invalidation, payload composition and translation fallback transitions in the component. Later step extractions need one stable controller contract. Existing `admin-merchant-pricing-plan.test.mjs` assertions read only the monolithic source file today, so the test loader must be widened to the bounded builder module set without changing its assertions before JSX moves.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/merchant-pricing-plan-draft.ts
src/components/admin/merchant/merchant-pricing-plan-builder/use-merchant-pricing-plan-draft.ts
tests/unit/merchant-pricing-plan-builder-draft.test.ts
tests/security/admin-merchant-pricing-plan.test.mjs
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Moving substantial step JSX; server action changes; domain-helper rewrites; child step components.

## Requirements

### Common ARCH-025 Admin invariants

- This is a **move-only structural refactor**. Do not change pricing-plan product behaviour, payload semantics, economics policy, Merchant Knowledge rules, Commerce-model assignment meaning, translation requirements, server authorization, catalogue CAS semantics, audit semantics or durable persistence.
- Preserve `MerchantPricingPlanBuilder` at `src/components/admin/merchant/merchant-pricing-plan-builder.tsx` with the same exported name and prop contract (`plan`, `cataloguePlans`, `featureCatalogue`, `merchantKnowledgeSourceTypes`, `commerceModelOptions`, `minimumUpgradePremiumBps`). Existing callers do not migrate during this tranche.
- Preserve the form action `mutateMerchantPricingPlanAction` and hidden fields `intent`, `payload`, `translationJson`, `economicsOverrideRequested`, `economicsOverrideReason`. Do not change the server action in this tranche.
- Preserve the exact ordered seven-step labels: `Plan`, `Catalogue placement`, `Shopify pricing`, `Usage events`, `Merchant content`, `Portfolio economics`, `Translations & review`.
- Preserve navigation semantics: backward navigation is allowed; forward navigation may advance at most one step; step 3 blocks only for an unbounded zero-cost fixed usage event, step 4 blocks only for invalid merchant content, and step 5 blocks until economics passes or a valid allowed override is ready. Final submit remains stricter than navigation.
- Preserve create/edit placement semantics: create-time plan-kind changes recompute placement; edit-time plan-kind changes do not. For FREE submission, the payload recovery usage-event handle is `null` while the local draft retains the previous handle.
- Preserve economics override invalidation exactly: changing handle, credits, currency, recurring amount, effective placement, `minimumUpgradePremiumBps` or serialized usage events clears enabled override state. Commerce model, Merchant Knowledge fields, merchant description/highlights, admin reason and translation state do not currently participate in that invalidation key.
- Preserve Merchant Knowledge product policy: it remains included in submitted `supportedFeatureKeys` regardless of generic feature toggles; its configuration is separately validated with the Shared schema and only active purpose/data-format source options are offered.
- Preserve Commerce-model repair behaviour: `Use Platform default` maps to `null`; a saved currently-unavailable model remains present as `Current model unavailable — <id>` with the existing alert until the admin deliberately repairs it.
- Preserve translation semantics exactly: retained translations depend on the current English description/highlights rules; `validTranslationJson()` returns the raw `translationJson` when `translationResult?.valid`, otherwise an edit `retainedTemplate` when present, otherwise the existing non-empty raw `translationJson` unchanged, and only when that raw value is empty builds the fresh current template. `canSubmit` independently still requires retained translations or a valid translation result. `MerchantPricingTranslationWorkbook` remains mounted across normal step navigation (hidden outside step 6), so uploaded workbook/file/error state is not discarded by Back/Next navigation.
- The typed reducer/controller manages local UI transitions only. Do not move or duplicate canonical payload validation, economics policy, translation validation or feature policy from existing modules under `src/lib/admin/merchant/`.
- Do not add a Redux/global store, form framework, generic UI plugin system or new React test framework solely for this extraction.
- Keep tests honest: no skipped tests, weakened assertions or changed expected behaviour merely because JSX/state moved. `npm run test:unit`, `npm test` and production build must introduce no task regression.
- Preserve these existing pure/domain test assets byte-for-byte throughout ADMIN-001..008:
  - `tests/unit/merchant-pricing-builder-payload.test.ts` — SHA-256 `a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243`
  - `tests/unit/merchant-pricing-plan-model.test.ts` — SHA-256 `e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086`
  - `tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts` — SHA-256 `610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f`
  - `tests/unit/merchant-pricing-economics.test.ts` — SHA-256 `eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8`
  - `tests/unit/merchant-pricing-economics-override.test.ts` — SHA-256 `434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7`
  - `tests/unit/merchant-pricing-translations.test.ts` — SHA-256 `90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92`
  - `tests/unit/merchant-pricing-translation-workbook.test.ts` — SHA-256 `385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8`


### R1 — typed draft/controller and complete downstream contract

Create one typed draft initialized from the current props/plan and one pure reducer/action surface for local transitions. A thin hook wraps it for React. Keep non-draft external inputs (`cataloguePlans`, feature/source/model catalogues, minimum premium) explicit rather than copying entire server objects into mutable state.

ADMIN-001 is the contract-establishing task for ADMIN-002..008. Before returning for review, the hook/controller MUST expose every current value, action and derived selector needed by all seven later steps so those tasks can be presentation-only consumers. This includes: step navigation; plan identity/status/model/kind/credits; supported-feature and Merchant Knowledge edits; placement; recovery handle/currency/recurring pricing; usage-event add/remove/move/update and tier add/remove/update; description/highlight add/remove/move/update; economics override enabled/reason; workbook `onChange`; admin reason; payload/hidden-field values; `canNavigateTo`; `canSubmit`; Commerce-model repair state; Merchant Knowledge configuration/validity; effective placement/placement label; merchant-content validity; economics derived/presented state; translation retention/template state; and final translation JSON serialization.

The pure `merchant-pricing-plan-draft.ts` module MUST remain React-free, Next/browser-runtime-free and directly loadable by the repository's plain Node `--experimental-strip-types` unit-test command. Do not depend on the `@/` tsconfig path alias from that pure module because the plain Node test runner does not resolve it; use Node-resolvable package imports and relative `.ts` imports for repository-local pure helpers. React effects/refs belong in `use-merchant-pricing-plan-draft.ts`.

### R2 — preserve exact transition rules and impurity boundaries

Focused controller tests must cover at least: a new plan defaults to `FREE` when no FREE plan exists and to `PAID_METERED` when a FREE plan already exists; the FREE option is disabled for a non-FREE edit while remaining available for the existing FREE plan; create-only placement recomputation on plan-kind change; edit placement staying `UNCHANGED`; FREE payload nulling the recovery usage handle without erasing the draft value; exact forward-navigation gates; exact final can-submit dependencies (required fields, valid Merchant Knowledge configuration, bounded non-empty admin reason, satisfied economics and retained-or-valid translations); economics override invalidation field set and non-field set; Merchant Knowledge always included in submitted feature keys; unavailable current Commerce-model retention; and the exact translation JSON precedence documented above.

Preserve the current Merchant Knowledge initialization quirk: an existing configuration is retained only when exactly one `merchant_knowledge` mapping exists, the Shared schema parses it, and every configured purpose/data-format pair is still present in the active source-type options; otherwise limits/source selections initialize blank/empty and require repair.

The reducer itself must remain pure. Preserve identity generation outside it: new usage events use a per-component-mount monotonic counter starting at `0` and only allocate `new-usage-event-<n>` when an event can actually be added (the five-event cap does not consume a key); new highlight `contentKey` values are created with `crypto.randomUUID()` at the hook/UI action boundary and passed into the reducer.

Preserve economics override invalidation as the current hook-level effect keyed by the exact `economicsConfigurationKey`; do not silently turn field-update reducer actions into synchronous override clearing. The key remains exactly handle.trim(), credits, uppercase-trimmed currency, recurring string, effective placement, `minimumUpgradePremiumBps` and `events.map(serializeBuilderEvent)`.

### R3 — canonical policy reuse

The controller may call existing pure helpers but must not reimplement `merchantPricingBuilderRequiredFieldsValid`, `merchantPricingBuilderMerchantContentValid`, `evaluateBuilderEconomics`, economics override assessment, translation retention/validation, feature controls or Merchant Knowledge schema validation.

### R4 — extraction-safe security assertions

In `admin-merchant-pricing-plan.test.mjs`, replace only source-location plumbing needed for builder extraction with one deterministic bounded builder-module loader: the public `merchant-pricing-plan-builder.tsx` shell plus sorted `.ts`/`.tsx` files directly under `src/components/admin/merchant/merchant-pricing-plan-builder/`. Preserve all 13 existing test names and product/security assertion intent; do not broaden the search to unrelated Admin source.

Use that bounded builder-module source not only for the tests that currently assign a `builder` string, but also for the existing ARCH-014 `nonActionModules` forbidden-operational-dependency scan. Otherwise later extracted step modules could introduce `BillingEconomicsSnapshot`, `BillingUpgradeEconomicsEdge`, `getBillingPlans`, `getBillingPlanById` or `mutateBillingPlanAction` without the existing security assertion seeing them. No assertion is deleted merely because later tasks move JSX. After ADMIN-001 is accepted, ADMIN-002..008 must not modify this security file.

## Work Items

- [x] Introduce typed draft/reducer/selectors and thin hook with the complete ADMIN-002..008 consume-only action/selector contract.
- [x] Rewire the existing builder to the controller without substantial JSX extraction.
- [x] Add focused pure controller tests for all listed state transitions, identity-generation inputs, hidden-field serialization and complete downstream action/selector surface.
- [x] Make the existing security test loader extraction-safe without weakening assertions.
- [x] Prove all frozen pure-policy tests remain byte-identical.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

None

## Enables

- `ARCH-025-ADMIN-002`

## Acceptance Criteria

- [x] Draft/controller exposes the complete consume-only state/action/selector interface required by ADMIN-002..008; later step tasks need no controller extension.
- [x] Builder renders/submits through the same public component/form contract.
- [x] Draft/controller tests prove the exact current state-transition semantics.
- [x] No server/domain validation moved into the reducer/controller.
- [x] All 13 existing security tests/assertions remain present and pass through the bounded module-set loader.
- [x] Frozen pure-policy assets remain unchanged.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/merchant-pricing-builder-payload.test.ts':'a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243','tests/unit/merchant-pricing-plan-model.test.ts':'e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086','tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts':'610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f','tests/unit/merchant-pricing-economics.test.ts':'eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8','tests/unit/merchant-pricing-economics-override.test.ts':'434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7','tests/unit/merchant-pricing-translations.test.ts':'90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92','tests/unit/merchant-pricing-translation-workbook.test.ts':'385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen SHA-256 values.
- [x] `git diff -- tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-plan-model.test.ts tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts tests/unit/merchant-pricing-economics.test.ts tests/unit/merchant-pricing-economics-override.test.ts tests/unit/merchant-pricing-translations.test.ts tests/unit/merchant-pricing-translation-workbook.test.ts` is empty.
- [x] For ADMIN-001 only: `tests/security/admin-merchant-pricing-plan.test.mjs` may change solely as authorised by R4; run `node --test tests/security/admin-merchant-pricing-plan.test.mjs` and prove all 13 tests/assertions remain.
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes.
- [x] `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes and still reports 13 tests.
- [x] `npm run test:unit` completed with 242/244 passing; the two failures are in unchanged frozen translation tests and are detailed below. No changed controller/security file is implicated.
- [x] `npm test` completed; the task-specific 13-test security suite passes. Six failures are in unrelated untouched admin tests and are detailed below.
- [x] `npm run lint -- src/components/admin/merchant/merchant-pricing-plan-builder.tsx src/components/admin/merchant/merchant-pricing-plan-builder tests/unit/merchant-pricing-plan-builder-draft.test.ts tests/security/admin-merchant-pricing-plan.test.mjs` exits successfully with no lint errors; ESLint reports the two test files as ignored by repository configuration.
- [x] `npm run build` succeeds; non-blocking BullMQ optional-dependency/dynamic-import warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/merchant-pricing-plan-draft.ts`
- `src/components/admin/merchant/merchant-pricing-plan-builder/use-merchant-pricing-plan-draft.ts`
- `tests/unit/merchant-pricing-plan-builder-draft.test.ts`
- `tests/security/admin-merchant-pricing-plan.test.mjs`

### Work Completed

- Extracted the local pricing-plan draft and transition rules into a React-free typed reducer module and a thin React hook. Exported the hook's controller return type for downstream ADMIN-002..008 consumers.
- Rewired the existing builder without moving step JSX or changing its public component/prop contract, form action, hidden fields, or ordered step labels. Canonical domain/policy helpers remain the validation and economics authorities.
- Preserved create/edit placement behavior, FREE payload semantics, hook-effect economics override invalidation, Merchant Knowledge policy and repair behavior, Commerce-model fallback, translation serialization precedence, and external event/highlight identity generation.
- Updated the security test to load the public builder shell and sorted direct `.ts`/`.tsx` modules, including for the ARCH-014 forbidden-operational-dependency scan. All 13 existing test names/assertions remain and pass.
- Added 14 focused pure controller tests covering initialization, navigation/submission gates, placement, FREE payload, Merchant Knowledge, unavailable models, identities/list actions, economics key fields/non-fields, translation precedence, and hidden-field serialization.
- Prepared execution facts honored: task `ARCH-025-ADMIN-001`, attempt 1, executor `copilot`; claim commit `ba629b61612a512a78db9feb060190869209c09d` was already pushed. Reused the supplied parent and implementation worktrees and `task/ARCH-025-ADMIN-001` branch without rerunning the launcher, reclaiming, or recreating/switching worktrees.
- Implementation commit `0cd5c010926acfbfaf808fb5d727df9269b30fdb` pushed to implementation `task/ARCH-025-ADMIN-001`.

### Validation Results

- `npm run prisma:generate` — passed.
- Frozen policy verification — all seven specified SHA-256 values match; the specified frozen-test Git diff is empty.
- `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` — passed, 14/14.
- `node --test tests/security/admin-merchant-pricing-plan.test.mjs` — passed, 13/13.
- `npm run test:unit` — 242/244 passed. The two failures are `tests/unit/merchant-pricing-translation-workbook.test.ts` / “rejects stale metadata, locale/header changes, and highlight identity changes” and `tests/unit/merchant-pricing-translations.test.ts` / “returns all bounded validation issues in canonical order”. Both test assets match the required frozen hashes; their implementation modules are unchanged by this task.
- `npm test` — the task-specific security suite passes. Six failures occur only in untouched suites: `admin-billing-pack-status.test.mjs` (purchase-status presenter), `admin-internationalization.test.mjs` (published ICU runtime and canonical keys), `admin-merchant-support.test.mjs` (published shared release), `admin-security-boundary.test.mjs` (identity/revocation/mutation/session/route wiring), and `admin-tenant-business-kpis.test.mjs` (durable KPIs). These files and owning implementation surfaces are outside this task's changes. `docs/development-baseline.md` does not record a matching Admin failure baseline ID.
- Scoped lint — exit 0 with no lint errors; the two supplied test files are reported as ignored by repository ESLint configuration.
- `npm run build` — passed, including TypeScript and static page generation. Next emitted non-blocking BullMQ optional `@valkey/valkey-glide` and dynamic-dependency warnings.
- `git diff --check` — passed.

### Deviations

- Full repository test commands are not entirely green because of the unchanged-suite failures listed above. The task-owned focused suites pass; no changed file is implicated by those failures.

### Assumptions

None

### Unresolved Issues

- The unrelated unit/security suite failures remain for their owning work; the Admin failures do not currently have a documented baseline identifier.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
