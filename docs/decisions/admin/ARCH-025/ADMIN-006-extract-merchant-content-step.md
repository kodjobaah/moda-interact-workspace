---
id: ARCH-025-ADMIN-006
architecture_id: ARCH-025
title: Extract Merchant content step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-005
enables:
  - ARCH-025-ADMIN-007
created: 2026-10-02
updated: 2026-10-03
---

# Extract Merchant content step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract English merchant description/highlight editing behind a focused child component without changing content validation or translation-retention semantics.

## Context

Step 4 owns description/highlight presentation and local ordering but canonical validity and translation retention are pure helper concerns. This extraction must not reset translation state or change which content edits invalidate retained translations.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/merchant-content-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Translation workbook/review extraction; translation validation; economics; server action.

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


### R1 — content presentation

Move step-4 English description, highlight title/description edit/order/remove/add controls and invalid-content guidance into `merchant-content-step.tsx`. Preserve `crypto.randomUUID()` creation for new highlight `contentKey` values at the accepted ADMIN-001 hook/UI action boundary; the pure reducer receives the generated key and does not call `crypto.randomUUID()` itself.

### R2 — canonical validation/retention

Continue using `updateBuilderHighlight`, `moveBuilderHighlight`, `merchantPricingBuilderMerchantContentValid` and `merchantPricingBuilderTranslationsRetained`. The child does not decide navigation or translation retention. Editing content must not eagerly clear uploaded translation workbook state beyond the existing retained/validated submit semantics.

## Work Items

- [x] Extract complete Merchant content markup.
- [x] Keep validity/navigation/translation-retention derivation in controller/canonical helpers.
- [x] Run accepted security/controller/policy suites.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-005`

## Enables

- `ARCH-025-ADMIN-007`

## Acceptance Criteria

- [x] Description/highlight behaviour/order/content keys are unchanged.
- [x] Step-4 navigation gate and translation retention remain identical.
- [x] Accepted ADMIN-001 security test file is unmodified and passes.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] All seven frozen policy-test SHA-256 values match; the frozen-test and accepted security-test diffs are empty.
- [x] `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes (13/13), and its source diff is empty.
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes (14/14).

- [x] `npm run test:unit` introduces no task regression. Result: 254 passed, 2 failed; the exact two translation failures match `ARCH025-ADMIN-BUILDER-TEST-001`.
- [x] `npm test` introduces no task regression. Result: 226 passed, 9 failed; all nine identifiers match `ARCH025-ADMIN-TEST-001`.
- [x] Targeted ESLint passes for the changed builder and new child component.
- [x] `npm run build` succeeds, including TypeScript. Existing BullMQ dynamic-dependency and optional Valkey resolution warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/merchant-content-step.tsx`

### Work Completed

- Extracted the English merchant description, highlight editing/order/removal controls, add control, and invalid-content guidance into `MerchantContentStep`.
- Typed child props from the accepted draft controller's state, action, and selector surfaces; highlight identity creation remains owned by the controller's `crypto.randomUUID()` boundary.
- Kept canonical content validity, step-4 navigation gating, translation retention, and workbook state in existing controller/helper owners. No policy, persistence, payload, or server-action logic moved or changed.
- Preserved the builder shell export/prop contract, form action/hidden fields, and step labels.

Physical worktree isolation and launcher evidence:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-006`, `task/ARCH-025-ADMIN-006`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-006`, `task/ARCH-025-ADMIN-006`.
- Shared workspace and implementation source checkouts were not switched or edited; no other task worktree was reused.
- Parent remote task branch fast-forward: not-needed; parent `origin/main`: already-current.
- Implementation remote task branch fast-forward: not-needed; implementation `origin/main`: already-current.
- Recursive submodule sync/update: passed; `database` initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

- Focused draft/controller suite: 14 passed, 0 failed.
- Accepted ADMIN-001 pricing security suite: 13 passed, 0 failed.
- `npm run prisma:generate`: passed.
- Frozen domain-test hashes: all seven matched; frozen test and accepted security test diffs are empty.
- Targeted ESLint: passed for the changed builder and new child.
- `npm run test:unit`: 256 total, 254 passed, 2 failed; both exact failures are documented in `ARCH025-ADMIN-BUILDER-TEST-001`.
- `npm test`: 235 total, 226 passed, 9 failed; all exact identifiers are documented in `ARCH025-ADMIN-TEST-001`.
- `npm run build`: passed, including TypeScript; existing BullMQ and optional Valkey warnings remain.
- `git diff --check`: passed.

### Deviations

None. Existing baseline test failures were documented by baseline ID; no test assertions or expected behavior were changed.

### Assumptions

The accepted ADMIN-001 controller actions and selectors are the authoritative interface; no controller change was required.

### Unresolved Issues

No task-owned issues remain. The two unit and nine security-suite failures remain tracked by their existing baseline IDs.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

The Merchant-content extraction is accepted as a move-only presentation refactor.

Architect inspection of Admin implementation
`17b96fab514068fc7c1b336cc53656bb8fe4b311` found exactly the two
task-authorised files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/merchant-content-step.tsx
```

The child consumes only the accepted ADMIN-001 controller boundary:
`description`, `highlights`, existing description/highlight actions and the already
derived `merchantContentValid` selector. It does not receive translation workbook
state, translation-retention state, navigation operations, payload data, economics
state or server-action concerns.

GitHub comparison against the implementation parent confirms that the step-4 markup
and behavior are preserved exactly:

- English description remains `rows={6}`, `maxLength={2000}`;
- highlight title remains `maxLength={120}`;
- highlight description remains `rows={3}`, `maxLength={500}`;
- highlight order uses the existing move action and surviving `contentKey` values;
- first/last move buttons retain the same disabled behavior;
- remove/add controls preserve the existing copy and placement;
- invalid-content guidance is unchanged.

Highlight identity generation remains at the accepted controller/UI action boundary:

```text
controller.actions.addHighlight
  -> contentKey: crypto.randomUUID()
  -> reducer receives the generated highlight
```

The pure reducer still does not call `crypto.randomUUID()`.

Canonical content/translation ownership also remains unchanged:

- `merchantPricingBuilderMerchantContentValid(...)` still derives the step-4 validity
  selector in the controller;
- `canNavigateTo()` still owns the step-4 forward gate through that selector;
- `merchantPricingBuilderTranslationsRetained(...)` still compares the current English
  description/highlights with the persisted plan;
- `retainedTemplate`, `currentTemplate` and `validTranslationJson(...)` remain
  controller/helper-owned;
- description/highlight actions dispatch only their existing draft transitions and do
  not eagerly clear `translationJson`, `translationResult` or workbook component
  state;
- `MerchantPricingTranslationWorkbook` remains mounted under the builder's existing
  step-6 visibility behavior.

The economics invalidation boundary is likewise unchanged: the controller's
`economicsConfigurationKey` still contains only handle, credits, currency, recurring,
effective placement, minimum upgrade premium and serialized usage events. Description
and highlights remain excluded exactly as before.

Independent validation against the uploaded snapshot confirms:

```text
accepted pricing security
  13 / 13 passed

draft/controller
  14 / 14 passed

frozen pricing-policy hashes
  7 / 7 exact
```

The submitted broad results are baseline-conformant:

```text
npm run test:unit
  256 total
  254 passed
  2 failed
```

The two failures are the exact unchanged
`ARCH025-ADMIN-BUILDER-TEST-001` translation failures.

```text
npm test
  235 total
  226 passed
  9 failed
```

All nine failures are the exact unchanged `ARCH025-ADMIN-TEST-001` identifiers. No
task-owned regression is present.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-006
  17b96fab514068fc7c1b336cc53656bb8fe4b311

workspace task/ARCH-025-ADMIN-006
  3d7c15feb7c7d8977a7ae2bc4dca8a840b751200
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect reconciliation
clears those lifecycle fields directly; no additional attempt is required.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/merchant-content-step.tsx`
- accepted ADMIN-001 draft/controller modules
- accepted ADMIN-001 pricing security test
- seven frozen pricing-policy test assets
- `ARCH025-ADMIN-BUILDER-TEST-001`
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-007 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `17b96fab514068fc7c1b336cc53656bb8fe4b311`: exactly two authorised files.
- Seven frozen pricing-policy SHA-256 values independently reproduced: all exact.
- Independently rerun accepted pricing security suite: 13/13 passed.
- Independently rerun draft/controller suite: 14/14 passed.
- Submitted unit suite: 254/256 with only the two exact inherited builder-translation
  failures.
- Submitted broad security/observability suite: 226/235 with exactly the nine inherited
  `ARCH025-ADMIN-TEST-001` failures.
- Submitted Prisma generation, targeted source lint, production build and
  `git diff --check`: passed as recorded.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-006 moves only Merchant-content presentation/edit wiring while
preserving controller/helper ownership of content validity, navigation, generated
highlight identity, translation retention, translation JSON precedence, economics
invalidation and form/server semantics.

### Follow-up

`ARCH-025-ADMIN-006` is Complete / Accepted at Attempt 1. Its sole dependant,
`ARCH-025-ADMIN-007`, has all declared dependencies satisfied and is promoted to
Ready, Attempt 0, claim clear. Do not start ADMIN-008 implicitly.
