---
id: ARCH-025-ADMIN-003
architecture_id: ARCH-025
title: Extract Catalogue placement step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-002
enables:
  - ARCH-025-ADMIN-004
created: 2026-10-02
updated: 2026-10-02
---

# Extract Catalogue placement step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract Catalogue placement presentation behind a bounded child component while preserving create/edit/FREE placement rules owned by the accepted controller and canonical payload helpers.

## Context

Step 1 is presentation-heavy but its values depend on subtle create/edit semantics. The controller established in ADMIN-001 remains the single transition owner; this task moves only presentation and callbacks.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/catalogue-placement-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Changing placement policy, catalogue ordering/CAS, server action, economics calculations or other steps.

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
- ADMIN-001 owns the accepted controller/action/selector contract. ADMIN-002..008 are consume-only presentation extractions and MUST NOT redesign or extend `merchant-pricing-plan-draft.ts` / `use-merchant-pricing-plan-draft.ts`. If an accepted controller value/action/selector required by this step is missing, stop and return the interface gap to `moda_architect` rather than widening this task.
- Preserve these existing pure/domain test assets byte-for-byte throughout ADMIN-001..008:
  - `tests/unit/merchant-pricing-builder-payload.test.ts` — SHA-256 `a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243`
  - `tests/unit/merchant-pricing-plan-model.test.ts` — SHA-256 `e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086`
  - `tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts` — SHA-256 `610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f`
  - `tests/unit/merchant-pricing-economics.test.ts` — SHA-256 `eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8`
  - `tests/unit/merchant-pricing-economics-override.test.ts` — SHA-256 `434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7`
  - `tests/unit/merchant-pricing-translations.test.ts` — SHA-256 `90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92`
  - `tests/unit/merchant-pricing-translation-workbook.test.ts` — SHA-256 `385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8`


### R1 — presentation-only extraction

Move the full step-1 select, FREE-first explanatory copy and edit current-position display into `catalogue-placement-step.tsx`.

### R2 — preserve placement semantics

Existing plan edits remain disabled/`UNCHANGED`; create FREE remains forced before the first catalogue plan; empty catalogue remains `ONLY`; paid create options remain `AFTER:<id>`. Plan-kind transition logic stays in the accepted controller and canonical `resolveMerchantPricingCreatePlacement(...)` helper.

## Work Items

- [x] Extract step-1 presentation.
- [x] Keep placement transition/derivation in the controller/canonical helper.
- [x] Run accepted security/controller/policy suites.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-002`

## Enables

- `ARCH-025-ADMIN-004`

## Acceptance Criteria

- [x] Catalogue placement behaviour/text/options are unchanged.
- [x] No catalogue CAS/server persistence logic enters the child component.
- [x] Accepted ADMIN-001 security test file is unmodified and passes.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/merchant-pricing-builder-payload.test.ts':'a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243','tests/unit/merchant-pricing-plan-model.test.ts':'e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086','tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts':'610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f','tests/unit/merchant-pricing-economics.test.ts':'eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8','tests/unit/merchant-pricing-economics-override.test.ts':'434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7','tests/unit/merchant-pricing-translations.test.ts':'90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92','tests/unit/merchant-pricing-translation-workbook.test.ts':'385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen SHA-256 values.
- [x] `git diff -- tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-plan-model.test.ts tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts tests/unit/merchant-pricing-economics.test.ts tests/unit/merchant-pricing-economics-override.test.ts tests/unit/merchant-pricing-translations.test.ts tests/unit/merchant-pricing-translation-workbook.test.ts` is empty.
- [x] `git diff -- tests/security/admin-merchant-pricing-plan.test.mjs` is empty for this task and `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes.
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes.

- [x] `npm run test:unit` passes without task-introduced regression.
- [x] `npm test` passes without task-introduced regression.
- [x] `npm run lint -- src/components/admin/merchant/merchant-pricing-plan-builder.tsx src/components/admin/merchant/merchant-pricing-plan-builder tests/unit/merchant-pricing-plan-builder-draft.test.ts tests/security/admin-merchant-pricing-plan.test.mjs` passes.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/catalogue-placement-step.tsx`

### Work Completed

- Extracted the Catalogue placement select, explanatory FREE-first copy and edit current-position display into `CataloguePlacementStep`.
- Kept plan-kind transition and placement derivation in the accepted draft controller and canonical `resolveMerchantPricingCreatePlacement(...)` helper; the child only receives bounded display values and `setPlacement`.
- Preserved create/edit, FREE, empty-catalogue and paid placement options/disabled states. No server/CAS/persistence logic or controller changes were made.
- Implementation commit `c31959a` was pushed to `origin/task/ARCH-025-ADMIN-003`.

### Validation Results

- Prisma generation passed.
- Focused draft/controller test: 14 passed, 0 failed. Accepted `admin-merchant-pricing-plan.test.mjs`: 13 passed, 0 failed.
- Frozen payload/model/Merchant Knowledge/economics/translation test SHA-256 values all matched; frozen pure/domain test diff and accepted security test diff were empty.
- Full unit suite: 245 passed, 2 failed. The exact failures (`rejects stale metadata, locale/header changes, and highlight identity changes`; `returns all bounded validation issues in canonical order`) match `ARCH025-ADMIN-BUILDER-TEST-001`; no task-specific regression appeared.
- Full `npm test`: the exact six existing baseline failures were observed in billing-pack presentation, Shared ICU/catalogue alignment, shared-release consumption, security-boundary wiring and tenant KPIs. The accepted ADMIN-001 security test passed.
- Task lint command passed with zero errors; ESLint reports the two test files as ignored by configuration. Direct ESLint on both changed JSX files passed without warnings/errors.
- Production build and TypeScript passed. Existing BullMQ dynamic dependency and optional `@valkey/valkey-glide` warnings remain.
- `git diff --check` passed.
- Launcher claimed Attempt 1 at `2026-10-02T23:02:10Z` with executor `copilot`; durable claim commit `6d74b6566516393bf16aa52ec486c6427bb334aa` was pushed. Dependency gate passed for `ARCH-025-ADMIN-002` (`complete`).
- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-003`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-003`; both task branches are `task/ARCH-025-ADMIN-003`.
- Parent and implementation task-branch fast-forward were `not-needed`; `origin/main` incorporation was `already-current`. Recursive submodule sync/update passed with database at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`. No shared/default checkout or other task worktree was used or mutated.

### Deviations

- Broad unit and security suites retain the exact failures documented by `ARCH025-ADMIN-BUILDER-TEST-001`; no unrelated baseline changes were made.

### Assumptions

- Existing catalogue rows are presentation inputs only; the controller remains authoritative for effective placement and transitions.

### Unresolved Issues

- None.

### Architectural Concerns

- None within the bounded ADMIN-003 scope.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

The Catalogue-placement extraction is accepted as a move-only presentation refactor.

Architect inspection of Admin implementation
`c31959af6c019f7ba8553ccad6bf09d341b460c7` found exactly the two
task-authorised files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/catalogue-placement-step.tsx
```

The child receives only bounded presentation inputs: catalogue `id`/`displayName`
pairs, edit state, current catalogue position, the accepted controller's `planKind`
and `effectivePlacement`, plus the accepted `setPlacement` action. It contains no
catalogue CAS, persistence, payload construction, server validation or placement
transition logic.

The accepted controller/canonical helper continue to own create/edit placement
semantics. The final-review `placementLabel` selector remains controller-owned and in
use elsewhere; ADMIN-003 does not duplicate or replace that policy surface.

The extracted JSX preserves the exact existing behavior and copy:

- edit mode is disabled and presents `UNCHANGED`;
- an empty create catalogue presents `ONLY`;
- FREE create is forced before the first catalogue plan;
- paid create presents `AFTER:<id>` options;
- the FREE-first explanation and edit current-position display are unchanged.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-003
  c31959af6c019f7ba8553ccad6bf09d341b460c7

workspace task/ARCH-025-ADMIN-003
  9edcec5bbf8155bbd5ff5ff36feabd1a1a7eb0ca
```

The implementation base contains independent accepted/mainline QueueMonitor work, but
the ADMIN-003 commit itself is limited to the two Catalogue-placement files and does
not alter the accepted ADMIN-001/002 controller, security test, server action, payload
or policy modules.

The broad suite result is baseline-conformant. `ARCH025-ADMIN-BUILDER-TEST-001`
documents nine historical failures and explicitly requires later tasks not to recreate
failures that upstream work fixes. ADMIN-003 reports only six remaining broad failures;
all reported categories are a subset of the documented baseline and no new/worsened
identifier is present. The disappearance of the other baseline failures is an
improvement, not drift.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/catalogue-placement-step.tsx`
- accepted ADMIN-001 draft/controller modules
- accepted ADMIN-001 security test
- seven frozen pricing-policy test assets
- this task Completion Report
- `ARCH025-ADMIN-BUILDER-TEST-001`
- ARCH-025 parent architecture and ADMIN-004 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `c31959af6c019f7ba8553ccad6bf09d341b460c7`: exactly two authorised files.
- Seven frozen pricing-policy SHA-256 values independently reproduced from the uploaded
  snapshot: all exact.
- Submitted draft/controller tests: 14/14 passed.
- Submitted accepted pricing-plan security tests: 13/13 passed.
- Submitted full unit suite: 245 passed / 2 exact documented translation-baseline
  failures.
- Submitted `npm test`: six remaining failures, all within the existing
  `ARCH025-ADMIN-BUILDER-TEST-001` failure set; no new task regression identified.
- Submitted Prisma generation, targeted source lint, TypeScript/production build and
  `git diff --check`: passed as recorded.
- Parent and implementation task worktrees are recorded clean and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-003 moves only Catalogue-placement presentation while keeping
placement derivation/transitions in the accepted controller and canonical helper.
Public builder/form/server/CAS semantics remain unchanged.

### Follow-up

`ARCH-025-ADMIN-003` is Complete / Accepted at Attempt 1. Its sole dependant,
`ARCH-025-ADMIN-004`, has all declared dependencies satisfied and is promoted to
Ready, Attempt 0, claim clear. Do not start ADMIN-005 or later builder-chain tasks
implicitly.
