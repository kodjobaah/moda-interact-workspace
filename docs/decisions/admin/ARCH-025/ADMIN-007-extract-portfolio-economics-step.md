---
id: ARCH-025-ADMIN-007
architecture_id: ARCH-025
title: Extract Portfolio economics step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-006
enables:
  - ARCH-025-ADMIN-008
created: 2026-10-02
updated: 2026-10-03
---

# Extract Portfolio economics step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract portfolio economics result/override presentation behind a focused child component while preserving canonical evaluation, override eligibility and exact invalidation semantics in the controller/domain modules.

## Context

Step 5 is a large presentation surface over canonical economics results. The child should render already-derived results and dispatch override-local edits; it must not become another economics engine.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/portfolio-economics-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Changing economics formulas/status codes/override policy, usage-event editing, final review or server approval/audit.

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


### R1 — render derived economics only

Move current step-5 pass/fail summary, failed comparison guidance/technical details, passed comparison list, the secondary `economicsPreview` list, OVERRIDEABLE controls/reason and HARD_FAIL message into `portfolio-economics-step.tsx`.

The current secondary `economicsPreview` list intentionally/incidentally renders one bordered `<li>` per result whose body contains only the existing placeholder comment. Treat that as observable current markup for this move-only task: do not delete, populate or otherwise "clean up" those rows as part of extraction. A later product/UI task may decide whether they should exist.

### R2 — policy ownership stays canonical

`evaluateBuilderEconomics`, `presentMerchantPricingEconomicsResult`, `assessMerchantPricingEconomicsOverride`, `findUnboundedZeroCostEventLabel` and controller selectors remain the policy/derivation owners. The child receives derived results/state and local override actions only.

### R3 — exact override invalidation

Do not alter the ADMIN-001 economics configuration key or which edits clear `economicsOverrideEnabled`. Override reason remains bounded to 2000 characters and required only when an available override is enabled.

## Work Items

- [x] Extract economics presentation/override controls.
- [x] Keep calculations/policy/invalidation outside the child.
- [x] Run accepted security/controller/policy suites.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-006`

## Enables

- `ARCH-025-ADMIN-008`

## Acceptance Criteria

- [x] Economics PASS/override/hard-fail rendering and guidance are unchanged.
- [x] Override eligibility/reason/invalidation semantics remain identical.
- [x] Accepted ADMIN-001 security test file is unmodified and passes.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/merchant-pricing-builder-payload.test.ts':'a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243','tests/unit/merchant-pricing-plan-model.test.ts':'e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086','tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts':'610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f','tests/unit/merchant-pricing-economics.test.ts':'eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8','tests/unit/merchant-pricing-economics-override.test.ts':'434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7','tests/unit/merchant-pricing-translations.test.ts':'90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92','tests/unit/merchant-pricing-translation-workbook.test.ts':'385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}" prints all expected frozen SHA-256 values.
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

Ready for Architect Review

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/portfolio-economics-step.tsx`

### Work Completed

- Extracted the complete Step 5 PASS/fail summary, failed and passed comparison details, economics preview rows, OVERRIDEABLE controls/reason, and HARD_FAIL guidance into `PortfolioEconomicsStep`.
- Kept the step presentational: it receives the existing controller's derived economics state, results, presentation, override assessment, formatting helper, override draft values, and two existing local edit actions. No economics calculation, eligibility policy, or invalidation behavior moved into the child.
- Preserved the seven-step shell, existing final-review economics summary, hidden form fields, and the empty placeholder body in each secondary economics-preview row.

### Validation Results

- Focused economics, override, and draft-controller suites: 44/44 passed.
- Accepted `admin-merchant-pricing-plan.test.mjs`: 13/13 passed; unchanged during this task.
- Targeted ESLint with `--no-ignore` for both changed components and the required draft/security tests: passed.
- `npm run prisma:generate`: passed.
- All seven frozen pure/domain test SHA-256 values matched; frozen test diffs were empty.
- `npm run test:unit`: 254 passed, 2 failed. Both exact failures are documented by `ARCH025-ADMIN-BUILDER-TEST-001`: stale translation workbook metadata/highlight identity and canonical bounded-translation issue assertions.
- `npm test`: 226 passed, 9 failed, 0 skipped. All nine failure identifiers match the documented `ARCH025-ADMIN-TEST-001` baseline; the accepted ADMIN-001 pricing security suite passes independently.
- `npm run build`: passed. Existing BullMQ critical-dependency and optional Valkey resolution warnings remain.
- `git diff --check`: passed.

### Deviations

- None in implementation scope. Full unit/security commands retain only their documented inherited baseline failures; no tests were changed or skipped.

### Assumptions

- The existing accepted controller's derived selector/action contract is authoritative; no controller or domain-policy changes were required.

### Unresolved Issues

- None within ADMIN-007 scope.

### Architectural Concerns

- None. Economics derivation, override eligibility, invalidation, payload serialization, and final review remain owned by the accepted controller/domain and parent shell.

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-007`, branch `task/ARCH-025-ADMIN-007`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-007`, branch `task/ARCH-025-ADMIN-007`.
- Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.

### Start-of-Attempt Synchronization

- Parent remote task branch fast-forwarded: not-needed. Parent `origin/main` incorporated: already-current.
- Implementation remote task branch fast-forwarded: not-needed. Implementation `origin/main` incorporated: already-current.

### Recursive Implementation Submodules

- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Verified initialized submodule: `database` at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

The Portfolio-economics extraction is accepted as a move-only presentation refactor.

Architect inspection of Admin implementation
`ab65e92d204c1423acb3ef7e3a588cb80047c13f` found exactly the two
task-authorised files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/portfolio-economics-step.tsx
```

The child consumes only accepted ADMIN-001 draft/actions/selectors: currency, override
draft values, the two existing override-edit actions, already-derived economics state,
preview/pass/fail/override assessment data and the existing formatting selector. It
does not run economics evaluation, override policy, invalidation-key construction,
payload serialization, submission policy or navigation policy.

GitHub comparison against the implementation parent confirms the Step-5 markup is
moved without product/UI cleanup. In particular:

- PASS/fail heading, summary and guidance remain unchanged;
- the `UNBOUNDED_ZERO_COST_USAGE_EVENT` bespoke guidance remains unchanged;
- failed comparison technical details and currency formatting remain unchanged;
- passed comparison disclosure/list and plan-name fallback remain unchanged;
- the secondary `economicsPreview` list still renders one bordered `<li>` per result
  with the intentionally empty existing placeholder body;
- OVERRIDEABLE copy, checkbox, bounded 2000-character reason field and missing-reason
  guidance remain unchanged;
- HARD_FAIL presentation remains unchanged.

All economics derivation/policy remains canonical in the accepted controller/domain:

- `evaluateBuilderEconomics(...)` still owns economics calculation;
- `presentMerchantPricingEconomicsResult(...)` still owns result presentation
  derivation;
- `assessMerchantPricingEconomicsOverride(...)` still owns override eligibility;
- `findUnboundedZeroCostEventLabel(...)` still owns the zero-cost event label;
- `buildEconomicsConfigurationKey(...)` still owns exact override invalidation inputs;
- the effect still clears enabled override state only when that key changes;
- `isEconomicsOverrideReady(...)` still owns enabled/reason readiness;
- `canNavigateTo()` still owns the Step-5 forward gate through
  `economicsSatisfied`;
- form hidden override fields and final-review economics state remain in the controller
  and builder shell.

Independent validation against the uploaded snapshot confirms:

```text
focused economics + override + draft/controller
  44 / 44 passed

accepted pricing security
  13 / 13 passed

frozen pricing-policy hashes
  7 / 7 exact
```

The submitted broader results are baseline-conformant:

```text
npm run test:unit
  256 total
  254 passed
  2 failed
```

Both failures are the exact unchanged
`ARCH025-ADMIN-BUILDER-TEST-001` translation failures.

```text
npm test
  235 total
  226 passed
  9 failed
  0 skipped
```

All nine failures are the exact unchanged `ARCH025-ADMIN-TEST-001` identifiers. No
task-owned regression is present.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-007
  ab65e92d204c1423acb3ef7e3a588cb80047c13f

workspace task/ARCH-025-ADMIN-007
  9a7e0279a3b434fa5ff3143cd108f389ab2119f2
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect reconciliation
clears those lifecycle fields directly; no additional attempt is required.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/portfolio-economics-step.tsx`
- accepted ADMIN-001 draft/controller modules
- canonical economics / override / presentation modules
- accepted ADMIN-001 pricing security test
- seven frozen pricing-policy test assets
- `ARCH025-ADMIN-BUILDER-TEST-001`
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-008 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `ab65e92d204c1423acb3ef7e3a588cb80047c13f`: exactly two authorised files.
- Independently rerun focused economics/override/draft-controller suite: 44/44 passed.
- Independently rerun accepted pricing security suite: 13/13 passed.
- Seven frozen pricing-policy SHA-256 values independently reproduced: all exact.
- Submitted unit suite: 254/256 with only the two exact inherited builder-translation
  failures.
- Submitted broad security/observability suite: 226/235 with exactly the nine inherited
  `ARCH025-ADMIN-TEST-001` failures and zero skips.
- Submitted Prisma generation, targeted lint, production build and `git diff --check`:
  passed as recorded.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-007 moves only Step-5 economics/override presentation while
preserving canonical calculation, presentation derivation, override eligibility,
override invalidation, navigation gating, hidden form fields, payload and final-review
ownership.

### Follow-up

`ARCH-025-ADMIN-007` is Complete / Accepted at Attempt 1. Its sole dependant,
`ARCH-025-ADMIN-008`, has all declared dependencies satisfied and is promoted to
Ready, Attempt 0, claim clear. ADMIN-008 is the final builder-chain extraction task.
