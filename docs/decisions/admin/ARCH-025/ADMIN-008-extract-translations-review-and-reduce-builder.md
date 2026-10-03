---
id: ARCH-025-ADMIN-008
architecture_id: ARCH-025
title: Extract Translations/review and reduce builder shell
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-007
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Extract Translations/review and reduce builder shell

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the mounted translation-workbook/final-review/admin-reason/submit presentation and finish `MerchantPricingPlanBuilder` as a thin form/navigation/controller shell without changing submission behaviour.

## Context

The final step combines an always-mounted workbook, final summary, admin reason and submit control. Moving it last ensures every preceding screen already consumes the stable controller. This task must preserve workbook mount lifetime and hidden form payload ownership while reducing the public builder to orchestration.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/translations-review-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Changing `MerchantPricingTranslationWorkbook`, submit button implementation, translation schema/workbook parser, server action, economics policy or form payload contract.

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


### R1 — workbook remains mounted

Move the workbook wrapper and final step presentation into `translations-review-step.tsx`, but render that child for the wizard lifetime so the `MerchantPricingTranslationWorkbook` subtree stays mounted and is hidden outside step 6 exactly as today. Do not replace it with `{step === 6 ? <Workbook/> : null}` or otherwise discard selected-file/workbook issue/uploaded-bytes state during navigation.

Preserve the current conditional DOM for the rest of the final step: final review, admin-reason textarea and `MerchantPricingPlanSubmitButton` are rendered only while `step === 6`; keeping the child mounted must not make those controls present on earlier steps.

### R2 — final review fidelity

Preserve the current review summary, including human-readable fixed usage-event formatting (`formatBuilderEventPrice(...) ... per event ... Unlimited`), catalogue placement label, recurring/allowance counts, description/highlights, economics PASS/OVERRIDE/NOT PASS state and override failure codes/reason. Preserve the exact translation-state display precedence: when `translationsRetained` is true it displays `20/20 retained` even if a currently uploaded workbook result is also valid; otherwise a valid workbook displays `20/20 validated`; otherwise `Not validated`.

### R3 — form shell ownership

The top-level `merchant-pricing-plan-builder.tsx` remains owner of `<form action={mutateMerchantPricingPlanAction}>`, hidden fields, seven-step nav, Back/Next buttons and controller wiring. The child owns final-step admin reason/submit presentation but receives `canSubmit` and dispatches reason edits rather than rebuilding submission policy.

### R4 — definition of done

After extraction the public builder should read as a thin wizard shell/controller composition. It must not contain substantial step-specific JSX or independently duplicate state derivation from child modules.

## Work Items

- [x] Extract the always-mounted translations/review child without changing mount lifetime.
- [x] Move final review/admin reason/submit presentation.
- [x] Reduce the top-level builder to form, hidden fields, nav, controller wiring and step composition.
- [x] Run all accepted controller/security/policy tests plus full Admin suites/build/lint; the full suites retain only the documented baseline failures recorded below.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-007`

## Enables

None

## Acceptance Criteria

- [x] Workbook local upload/error state survives Back/Next navigation: the workbook remains mounted in the always-rendered child and is hidden outside step 6.
- [x] Final review and submit gating are unchanged; review, reason and submit DOM remain conditional on step 6 and submit uses the controller's `canSubmit` selector.
- [x] Top-level builder is a thin shell with no substantial step-specific workflow implementation.
- [x] Accepted ADMIN-001 security test file is unmodified and passes 13/13; full Admin suites introduce no task regression and retain only the exact documented `ARCH025-ADMIN-BUILDER-TEST-001` / `ARCH025-ADMIN-TEST-001` baseline failures.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/merchant-pricing-builder-payload.test.ts':'a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243','tests/unit/merchant-pricing-plan-model.test.ts':'e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086','tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts':'610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f','tests/unit/merchant-pricing-economics.test.ts':'eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8','tests/unit/merchant-pricing-economics-override.test.ts':'434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7','tests/unit/merchant-pricing-translations.test.ts':'90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92','tests/unit/merchant-pricing-translation-workbook.test.ts':'385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen SHA-256 values.
- [x] `git diff -- tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-plan-model.test.ts tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts tests/unit/merchant-pricing-economics.test.ts tests/unit/merchant-pricing-economics-override.test.ts tests/unit/merchant-pricing-translations.test.ts tests/unit/merchant-pricing-translation-workbook.test.ts` is empty.
- [x] `git diff -- tests/security/admin-merchant-pricing-plan.test.mjs` is empty for this task and `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes.
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes.

- [x] `npm run test:unit` completes with only the two documented translation baseline failures; no task-introduced regression.
- [x] `npm test` completes with only the nine documented Admin baseline failures; no task-introduced regression.
- [x] `npm run lint -- src/components/admin/merchant/merchant-pricing-plan-builder.tsx src/components/admin/merchant/merchant-pricing-plan-builder tests/unit/merchant-pricing-plan-builder-draft.test.ts tests/security/admin-merchant-pricing-plan.test.mjs` passes.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Ready for architect review

### Files Changed

`src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
`src/components/admin/merchant/merchant-pricing-plan-builder/translations-review-step.tsx`

### Work Completed

Extracted the always-mounted translations/review presentation into `TranslationsReviewStep`. The child keeps the workbook subtree mounted for the wizard lifetime, hides it outside step 6, and gates final review, admin reason, and submit presentation to step 6. The parent retains the form action, hidden payload fields, step navigation, Back/Next controls, controller wiring, and existing public props.

Prepared and claimed as ADMIN-008 Attempt 1 in the launcher-provided implementation and parent task worktrees. The ADMIN-007 dependency gate passed and recursive submodules were ready. No controller, domain policy, payload, action, or test files were changed.

### Validation Results

`npm run prisma:generate`: passed.

Frozen test SHA-256 checks: all seven required hashes matched. The seven frozen pure/domain test files and `tests/security/admin-merchant-pricing-plan.test.mjs` have empty diffs.

`node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts`: 14 passed.

`node --test tests/security/admin-merchant-pricing-plan.test.mjs`: 13 passed.

Targeted ESLint for the builder, builder step directory, draft test, and ADMIN-001 security test: passed.

`npm run test:unit`: 256 total, 254 passed, 2 failed. The only failures are the documented translation baseline cases: `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order` (`ARCH025-ADMIN-BUILDER-TEST-001`).

`npm test`: 235 total, 226 passed, 9 failed, 0 skipped. The nine failures match the documented `ARCH025-ADMIN-TEST-001` baseline: `no Moda-owned span/metric creation exists in application code`; `accepts strict non-negative lifetime Free defaults`; `every RecoveryCreditPurchaseStatus has an ICU label and filter support`; `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups`; `Admin validates and consumes the published Shared ICU runtime`; `Admin canonical catalogue keys are independent and intentionally aligned`; `consumes the published shared release without a local declaration shim`; `identity, revocation, mutation, session, and route contracts are wired`; `Tenant Directory KPIs are derived from durable business state`.

`npm run build`: passed, including TypeScript and production compilation. Existing BullMQ warnings remain for its dynamic dependency and unresolved optional `@valkey/valkey-glide` module.

`git diff --check`: passed.

### Deviations

Full Admin suites are not fully green due to the documented pre-existing failures above; no new failure identifiers were observed.

### Assumptions

The workbook mount-lifetime guarantee is preserved structurally by always rendering `TranslationsReviewStep` and keeping the workbook wrapper mounted while toggling its `hidden` class. No browser/component test framework was introduced.

### Unresolved Issues

The two translation unit failures and nine broader Admin suite failures remain known baseline issues and are outside this presentation-only task's scope.

### Architectural Concerns

None identified. The builder retains its existing public contract and controller/action ownership; the extracted component consumes the accepted controller draft/actions/selectors.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

ADMIN-008 is accepted Complete and closes the ADMIN-001..008 Merchant Pricing builder
refactor tranche.

Architect inspection of Admin implementation
`e528cf1a61e6a89e586c117bfd56c8155828705c` found exactly the two
task-authorised files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/translations-review-step.tsx
```

GitHub comparison against parent
`f487fb5b8dd61240aab656b75133f91878a40c0a` confirms the final-step JSX was moved
without product-behaviour changes. The extracted child preserves the required mount
and conditional-DOM split:

- `TranslationsReviewStep` is rendered unconditionally for the wizard lifetime;
- `MerchantPricingTranslationWorkbook` remains mounted beneath a wrapper whose class
  toggles between `""` and `"hidden"`;
- final review, Admin reason and submit button remain rendered only when
  `step === 6`;
- workbook props remain `planHandle`, `retainedTemplate ?? currentTemplate`,
  `highlights`, `translationsRetained` and the existing `onWorkbookChange` action.

The final-review contract is preserved exactly:

- name/handle and catalogue placement remain unchanged;
- recurring price and allowance remain unchanged;
- fixed usage events still use
  `formatBuilderEventPrice(event, currency)`, append `per event`, and show the bounded
  maximum or `Unlimited`;
- graduated/volume events retain the pricing-mode/tier-count summary;
- English description/highlights remain unchanged;
- economics review remains `PASS`, `OVERRIDE REQUESTED` or `NOT PASS`;
- override failure codes and trimmed override reason remain visible only when the
  override is ready;
- translation-state display still gives `translationsRetained` precedence:
  `20/20 retained`, else a valid current workbook is `20/20 validated`, else
  `Not validated`.

Form/submission ownership remains outside the child. The top-level
`MerchantPricingPlanBuilder` still owns:

```text
<form action={mutateMerchantPricingPlanAction}>
intent
payload
translationJson
economicsOverrideRequested
economicsOverrideReason
seven-step navigation
Back / Next navigation
controller creation and child composition
```

`TranslationsReviewStep` receives the accepted controller's `canSubmit` selector and
dispatches only the existing `setReason` / `onWorkbookChange` actions; it does not
rebuild submission, translation, economics or payload policy.

The resulting public builder is a thin orchestration shell. It contains no substantial
step-specific workflow implementation; each of the seven screens is composed through
its bounded child while the shell retains only form/navigation/controller wiring.

Independent validation against the uploaded snapshot confirms:

```text
accepted ADMIN-001 pricing security
  13 / 13 passed

draft/controller
  14 / 14 passed

frozen pricing-policy hashes
  7 / 7 exact
```

The accepted security suite's `final review uses the exact human-readable fixed
usage-event summary` assertion passes against the extracted module set, independently
confirming final-review formatting survived the move.

The submitted full-suite results are baseline-conformant:

```text
npm run test:unit
  256 total
  254 passed
  2 failed
```

The only failures are the exact unchanged
`ARCH025-ADMIN-BUILDER-TEST-001` translation failures.

```text
npm test
  235 total
  226 passed
  9 failed
  0 skipped
```

All nine failures are the exact unchanged `ARCH025-ADMIN-TEST-001` identifiers. No
ADMIN-008 regression is present.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-008
  e528cf1a61e6a89e586c117bfd56c8155828705c

workspace task/ARCH-025-ADMIN-008
  3e7498347f9f31fc510c30454c999d5dc39eb253
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect reconciliation
clears those lifecycle fields directly; no additional attempt is required.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/translations-review-step.tsx`
- accepted ADMIN-001 draft/controller modules
- `MerchantPricingTranslationWorkbook`
- `MerchantPricingPlanSubmitButton`
- accepted ADMIN-001 pricing security test
- seven frozen pricing-policy test assets
- `ARCH025-ADMIN-BUILDER-TEST-001`
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and Admin task index

### Validation Reviewed

- GitHub implementation commit
  `e528cf1a61e6a89e586c117bfd56c8155828705c`: exactly two authorised files.
- Seven frozen pricing-policy SHA-256 values independently reproduced: all exact.
- Independently rerun accepted pricing security suite: 13/13 passed.
- Independently rerun draft/controller suite: 14/14 passed.
- Submitted unit suite: 254/256 with only the two exact inherited builder-translation
  failures.
- Submitted broad security/observability suite: 226/235 with exactly the nine inherited
  `ARCH025-ADMIN-TEST-001` failures and zero skips.
- Submitted Prisma generation, targeted lint, production build and `git diff --check`:
  passed as recorded.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-008 preserves workbook mount lifetime, final-step conditional DOM,
review-summary fidelity, translation-state precedence, submit gating and hidden form
ownership while completing the public builder's reduction to a thin wizard shell.

The ADMIN-001..008 builder tranche is now fully architect-accepted. The accepted
ADMIN-001 controller/security boundary and all seven frozen pricing-policy assets
remain the durable behavioural baseline for later unrelated work.

### Follow-up

`ARCH-025-ADMIN-008` is Complete / Accepted at Attempt 1. It has no declared
dependants. The ADMIN-001..008 builder chain is closed; do not start adjacent ARCH-025
work implicitly. Continue only from another independently Ready frontier when
explicitly launched.
