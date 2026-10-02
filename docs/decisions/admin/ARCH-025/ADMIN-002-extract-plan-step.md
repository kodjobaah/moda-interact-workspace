---
id: ARCH-025-ADMIN-002
architecture_id: ARCH-025
title: Extract Plan step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-025-ADMIN-001
enables:
  - ARCH-025-ADMIN-003
created: 2026-10-02
updated: 2026-10-02
---

# Extract Plan step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the complete Plan step presentation behind a bounded child component while preserving identity/status, Commerce-model repair, supported-feature and Merchant Knowledge behaviour through the accepted draft/controller.

## Context

Step 0 currently appears in two separated JSX blocks: identity/model/kind/credits/status fields and the supported-features/Merchant Knowledge section. They are one user-facing Plan step and should move together so product-policy state does not remain split across the shell.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/plan-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Catalogue, Shopify pricing, usage events, content, economics or translation/review extraction; controller redesign; server policy changes.

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


### R1 — complete Plan step boundary

Move both existing step-0 JSX regions into `plan-step.tsx`: Shopify plan handle/display name; Commerce-model selector/repair alert/guidance; plan kind; included recovery credits; Active/Featured; supported feature controls; Merchant Knowledge limits/source-type controls and validation alert.

### R2 — bounded props/actions

The step receives only the values/catalogues/derived controls/actions it needs. It must not build the final payload, evaluate portfolio economics or own wizard navigation.

### R3 — exact product/model semantics

Preserve read-only handle-on-edit, existing FREE option disablement, current-unavailable model option/alert/guidance text semantics, product-policy-included feature controls and active Merchant Knowledge source option filtering. Do not change which fields participate in economics override invalidation.

## Work Items

- [x] Extract the complete Plan step into `plan-step.tsx`.
- [x] Wire it only through the accepted controller/bounded props.
- [x] Keep the top-level shell responsible for form/navigation.
- [x] Run extraction-safe security assertions and frozen policy tests.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-001`

## Enables

- `ARCH-025-ADMIN-003`

## Acceptance Criteria

- [x] Both current Plan-step JSX regions are owned by the child component.
- [x] Commerce-model and Merchant Knowledge repair/product-policy semantics are unchanged; focused security assertions pass.
- [x] No hidden payload or server validation moves into the child; the child receives only bounded draft, action, selector, and catalogue props.
- [x] Accepted ADMIN-001 security test file is unmodified and passes (13/13).

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] The required `node -e` frozen-file hash check prints all seven expected SHA-256 values.
- [x] The required frozen pure/domain test diff is empty.
- [x] `git diff -- tests/security/admin-merchant-pricing-plan.test.mjs` is empty for this task and `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes (13/13).
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes (14/14).

- [x] `npm run test:unit` completes with 242 passed / 2 failed; both exact failures match `ARCH025-ADMIN-BUILDER-TEST-001`, with no task-introduced regression.
- [x] `npm test` completes with 226 passed / 9 failed / 0 skipped; all nine exact failures match `ARCH025-ADMIN-BUILDER-TEST-001`, with no task-introduced regression.
- [x] The required scoped `npm run lint -- ...` completes with zero errors; ESLint reports the two test files ignored by repository configuration.
- [x] `npm run build` succeeds (Next reports existing BullMQ optional dependency/dynamic-require warnings).
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Attempt 2 completed. Architect correction A1-R1 is implemented and validated; returned to Architect Review.

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/plan-step.tsx`

### Work Completed

Moved both Plan-step JSX regions into `PlanStep`. The shell continues to own the form, hidden payload fields, step selection and navigation. The child receives only the required draft fields, action callbacks, selector values and model/source-type catalogues; payload construction, server validation, economics and navigation remain outside it. Existing Commerce-model repair guidance, FREE-option behavior, product-policy feature controls, active Merchant Knowledge source options and validation are preserved.

Implemented Architect correction A1-R1: removed the full persisted `plan` prop and `MerchantPricingPlanWithChildren` import from `plan-step.tsx`; added the accepted `draft.isEditing` value to the bounded draft Pick; changed handle read-only behavior to `draft.isEditing`; and passed `controller.draft.isEditing` from the shell. No controller, test, action, payload or policy source changed. Focused validation: `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passed 13/13, `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passed 14/14, targeted ESLint on both changed components completed without warnings or errors, and editor diagnostics reported no errors.

### Validation Results

Attempt 2 focused `node --test tests/security/admin-merchant-pricing-plan.test.mjs`: 13/13 passed; the test file was not modified. Focused `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts`: 14/14 passed. All seven frozen SHA-256 values matched; frozen unit-test and accepted ADMIN-001 security-test diffs were empty. `npm run prisma:generate` succeeded. The required scoped ESLint command completed with zero errors; it warned that the specified unit and security test files are ignored by repository configuration. Targeted ESLint on the two changed component files completed without warnings or errors. `npm run build` succeeded; Next emitted existing BullMQ dynamic-require and optional `@valkey/valkey-glide` resolution warnings. `git diff --check` passed.

`npm run test:unit`: 242 passed / 2 failed. Both failures exactly match the inherited `ARCH025-ADMIN-BUILDER-TEST-001` identifiers: stale translation-workbook metadata/header/highlight identity and canonical translation issue ordering. `npm test`: 226 passed / 9 failed / 0 skipped. All nine failures exactly match the documented baseline identifiers (shared runtime ownership, lifetime-Free defaults, billing-pack status/i18n, shared release declaration, security boundary, and tenant KPI assertions). No task-introduced regression was observed; the Architect correction affects only the boolean source for handle read-only presentation.

### Deviations

Attempt 1's recorded deviations remain historical. Attempt 2 required no dependency installation or manifest/lockfile changes; the existing task branch tracking was aligned with its task remote.

### Assumptions

None

### Unresolved Issues

No task-owned unresolved issues. The broader inherited Admin suite failures remain tracked under `ARCH025-ADMIN-BUILDER-TEST-001`; the workspace doctor also reported `DEP-ZOD-001` in Admin, outside this presentation-only task's ownership and scope.

### Architectural Concerns

None. The accepted ADMIN-001 controller/action/selector contract was consumed without extension or redesign.

### Prepared Execution and VCS Evidence

```text
Claim: attempt 1; executor copilot; claimed at 2026-10-02T21:41:13Z
Parent claim commit: cadaf4e9edfcd70b09eae4c338a470c41c60cdbb (committed and pushed)
Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-002
Parent branch: task/ARCH-025-ADMIN-002
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-002
Implementation branch: task/ARCH-025-ADMIN-002
Parent remote task fast-forwarded: not-needed
Parent origin/main incorporated: already-current
Implementation remote task fast-forwarded: not-needed
Implementation origin/main incorporated: already-current
Recursive submodule sync: passed
Recursive submodule update/init: passed
Recorded database submodule commit: cfeeb12456b4e05067a96857a8c47837d7e33bbd
Shared workspace checkout switched/mutated for task work: no
Shared implementation checkout switched/mutated for task work: no
Another task worktree reused: no
Implementation commit: 4a98b7a27198932861bbdaed462d85d7cc174f57 (pushed; local task branch tracks matching origin task branch)
```

Attempt 1 implementation was clean at `4a98b7a27198932861bbdaed462d85d7cc174f57`. After the A1-R1 correction, Attempt 2 implementation HEAD is `77a5e68f323667c863caa54d6aa9edb87dc624c4`, pushed to and matching `origin/task/ARCH-025-ADMIN-002`; the implementation worktree is clean.

Attempt 2 prepared execution:

```text
Claim: attempt 2; executor copilot; claimed at 2026-10-02T22:05:25Z
Parent claim commit: 6f6c9290155d5f158750ea80b8aa26ff92ac6c91 (committed and pushed)
Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-ADMIN-002
Parent branch: task/ARCH-025-ADMIN-002
Parent task-branch fast-forward: not-needed
Parent origin/main incorporated: already-current
Parent prepared HEAD: 30c379d3f0851f76cedffd0368472f71ab1308b6
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-ADMIN-002
Implementation branch: task/ARCH-025-ADMIN-002
Implementation task-branch fast-forward: not-needed
Implementation origin/main incorporated: already-current
Implementation prepared HEAD: 4a98b7a27198932861bbdaed462d85d7cc174f57
Recursive submodule sync: passed
Recursive submodule update/init: passed
Recorded database submodule commit: cfeeb12456b4e05067a96857a8c47837d7e33bbd
Shared workspace checkout switched/mutated for task work: no
Shared implementation checkout switched/mutated for task work: no
Another task worktree reused: no
Implementation correction commit: 77a5e68f323667c863caa54d6aa9edb87dc624c4 (pushed to task/ARCH-025-ADMIN-002)
```

Final implementation branch is clean and matches its task remote at `77a5e68`. The parent report finalization is committed and pushed; its final commit and local-equals-remote state are verified after publication.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The submitted Plan-step extraction is conformant in substance and preserves the
move-only product behaviour. Architect inspection of Admin implementation
`4a98b7a27198932861bbdaed462d85d7cc174f57` found exactly the two task-authorised
source files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/plan-step.tsx
```

The synchronized implementation parent `dfb790ffe613f7afeb8630e740010bdd12d5e014`
is one commit ahead of accepted ADMIN-001 `0cd5c010926acfbfaf808fb5d727df9269b30fdb`
with no file delta, so the accepted controller boundary is present unchanged.

Both former step-0 JSX regions now live in `PlanStep`; the shell still owns the
`mutateMerchantPricingPlanAction` form, hidden payload fields, seven-step navigation,
and all non-Plan steps. Commerce-model repair text/option semantics, FREE option
disablement, supported-feature/product-policy controls, active Merchant Knowledge
source options and configuration validation remain unchanged.

One bounded R2/Acceptance-Criterion-3 violation remains.

#### A1-R1 — remove the full persisted `plan` object from the child boundary

**Source correction required; no controller/server/test redesign is authorised.**

`PlanStepProps` currently accepts:

```ts
plan?: MerchantPricingPlanWithChildren;
```

and the child uses that entire persisted plan object only for:

```ts
readOnly={Boolean(plan)}
```

This is broader than the task contract:

```text
R2 — the step receives only the values/catalogues/derived controls/actions it needs
Acceptance — only bounded draft, action, selector and catalogue props
ADMIN-001 — accepted controller is the consume-only boundary for ADMIN-002..008
```

The accepted controller already exposes `draft.isEditing`, so passing the complete
`MerchantPricingPlanWithChildren` object is unnecessary and creates a presentation
escape hatch around the controller boundary.

Attempt 2 must make only this bounded correction:

1. add `isEditing` to the `PlanStep` `draft` Pick;
2. remove the `plan` prop and the `MerchantPricingPlanWithChildren` import from
   `plan-step.tsx`;
3. change handle read-only logic to `readOnly={draft.isEditing}`;
4. pass `isEditing` from the existing `controller.draft` object in the shell;
5. do not change `merchant-pricing-plan-draft.ts`,
   `use-merchant-pricing-plan-draft.ts`, server actions, payload construction,
   validation policy or the accepted ADMIN-001 security test.

No new test framework or test-source change is required. Because source changes are
required, rerun the complete ADMIN-002 validation contract, using
`ARCH025-ADMIN-BUILDER-TEST-001` only for the exact inherited broad-suite failures.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/plan-step.tsx`
- accepted ADMIN-001 controller/draft modules
- `tests/security/admin-merchant-pricing-plan.test.mjs`
- `tests/unit/merchant-pricing-plan-builder-draft.test.ts`
- seven frozen pricing-policy test assets
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-003 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `4a98b7a27198932861bbdaed462d85d7cc174f57`: exactly two authorised files.
- GitHub parent comparison: accepted ADMIN-001
  `0cd5c010926acfbfaf808fb5d727df9269b30fdb` ->
  synchronized ADMIN-002 base `dfb790ffe613f7afeb8630e740010bdd12d5e014`
  contains no file delta.
- All seven frozen SHA-256 values independently reproduced against the uploaded
  snapshot.
- `node --test tests/security/admin-merchant-pricing-plan.test.mjs` independently
  rerun: 13/13 passed.
- `node --experimental-strip-types --test
  tests/unit/merchant-pricing-plan-builder-draft.test.ts` independently rerun:
  14/14 passed.
- Submitted `npm run test:unit`: 242 passed / 2 inherited failures covered by
  `ARCH025-ADMIN-BUILDER-TEST-001`.
- Submitted `npm test`: 226 passed / 9 inherited failures / 0 skipped, all covered by
  `ARCH025-ADMIN-BUILDER-TEST-001`.
- Submitted Prisma generation, scoped lint, production build and `git diff --check`:
  passed as recorded.
- GitHub confirms parent task branch head
  `69efd67c411d5c5103581b8c27edd393aa604e40` and Admin implementation task branch
  head `4a98b7a27198932861bbdaed462d85d7cc174f57`.

### Architecture Conformance

Changes required only for the child-prop boundary. Runtime/product semantics and the
move-only extraction are otherwise conformant. The current full `plan` prop violates
the accepted consume-only controller boundary even though it is presently used only as
a boolean.

### Follow-up

Return this same task to Ready, Attempt 1 retained and claim clear. Reclaim through
`/moda-task ARCH-025-ADMIN-002`, which must create Attempt 2 exactly once. Apply only
A1-R1, rerun the defined validation, update the Completion Report and return to review.

Do not begin ADMIN-003 until ADMIN-002 is architect-accepted Complete.
