---
id: ARCH-025-ADMIN-004
architecture_id: ARCH-025
title: Extract Shopify pricing step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-003
enables:
  - ARCH-025-ADMIN-005
created: 2026-10-02
updated: 2026-10-02
---

# Extract Shopify pricing step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract the Shopify pricing step presentation for recovery meter, currency and recurring amount without changing payload/economics semantics.

## Context

Step 2 is a coherent pricing-input screen. Included recovery credits remain on the Plan step exactly as today; this task moves only the existing recovery usage-event handle, currency, recurring amount and fixed billing-period presentation.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/shopify-pricing-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Usage-event/tier editing; included recovery-credit placement; economics policy; BillingPlan persistence/action changes.

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


### R1 — exact field ownership

Move current step-2 JSX only: recovery usage-event handle, currency, recurring amount and `EVERY_30_DAYS` billing-period copy. Keep included recovery credits on Plan step.

### R2 — FREE/paid semantics

FREE keeps the recovery handle input disabled/not required while retaining the draft value; submitted payload still nulls it for FREE. Currency still normalizes to uppercase on input/payload and remains max length 3. Recurring remains a string draft value consumed by canonical money/economics helpers.

## Work Items

- [x] Extract step-2 presentation.
- [x] Preserve exact controller/payload semantics.
- [x] Run accepted security/controller/policy suites.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-003`

## Enables

- `ARCH-025-ADMIN-005`

## Acceptance Criteria

- [x] Shopify pricing fields behave exactly as before.
- [x] No economics or server-side pricing validation is duplicated in the child.
- [x] Accepted ADMIN-001 security test file is unmodified and passes.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] All seven frozen pure/domain test SHA-256 values match their task-specified values.
- [x] Diffs for all seven frozen pure/domain tests and `tests/security/admin-merchant-pricing-plan.test.mjs` are empty.
- [x] `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes (13 tests).
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes (14 tests).

- [x] `npm run test:unit` completes without task-introduced regression; the two exact inherited builder translation failures are recorded below.
- [ ] Broad security/observability coverage completes without task-introduced regression. The Attempt 1 `npm test` run produced 235 total / 223 passed / 9 exact baseline failures / 3 skipped production-runtime telemetry tests because `.next/BUILD_ID` was absent. Attempt 2 must execute those three skipped tests after a successful production build.
- [x] Required targeted ESLint command passes.
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
- `src/components/admin/merchant/merchant-pricing-plan-builder/shopify-pricing-step.tsx`

### Work Completed

- Extracted the Shopify pricing step's recovery usage-event handle, currency, recurring amount and `EVERY_30_DAYS` presentation into `ShopifyPricingStep`.
- Kept draft state and updates in the accepted controller. FREE still disables and makes the recovery handle optional while retaining its draft value; currency uppercasing and maximum length, recurring string input and existing payload/economics consumers are unchanged.
- Included recovery credits remain on the Plan step. No validation, economics, payload, server action or controller code was changed.

### Validation Results

- Prisma generation passed.
- All seven frozen test hashes matched their task-specified SHA-256 values; diffs for those files and `tests/security/admin-merchant-pricing-plan.test.mjs` were empty.
- Accepted ADMIN-001 security scan: 13 passed, 0 failed. Focused draft-controller tests: 14 passed, 0 failed.
- `npm run test:unit`: 247 tests, 245 passed, 2 failed. The failures were `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order`, matching the existing builder translation baseline; the ADMIN-004-specific draft suite passed.
- `npm test`: 235 tests, 223 passed, 9 failed. The failures were the exact identifiers documented by `ARCH025-ADMIN-TEST-001`: `no Moda-owned span/metric creation exists in application code`, `accepts strict non-negative lifetime Free defaults`, `every RecoveryCreditPurchaseStatus has an ICU label and filter support`, `purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups`, `Admin validates and consumes the published Shared ICU runtime`, `Admin canonical catalogue keys are independent and intentionally aligned`, `consumes the published shared release without a local declaration shim`, `identity, revocation, mutation, session, and route contracts are wired`, and `Tenant Directory KPIs are derived from durable business state`. No task-owned assertion regressed.
- Required targeted ESLint passed. Production build and TypeScript passed; existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- `git diff --check` passed.

### Deviations

The fresh implementation worktree initially had no `node_modules`; installed from its existing `package-lock.json` with `npm ci` before running Prisma generation and repository validation. No lockfile change was made.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

The extraction is limited to the authorized presentation boundary and consumes the existing ADMIN-001 controller contract.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The ADMIN-004 implementation is accepted in substance. No Shopify-pricing child,
builder shell, controller, reducer, payload, economics, server-action or test source
correction is requested.

Architect inspection of implementation
`6bf1de4384da51091b0c1729172d6219738b8e5a` found exactly the two
task-authorised presentation files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/shopify-pricing-step.tsx
```

The child consumes only the accepted controller draft values
`planKind`, `recoveryUsageEventHandle`, `currency`, `recurring` and their existing
setter actions. The shell retains the form/navigation boundary and included recovery
credits remain on the Plan step.

The exact step-2 behavior is preserved:

- FREE disables the recovery usage-event handle and makes it not required while the
  controller retains the draft value;
- paid plans require the recovery handle;
- currency still uppercases on input and remains `maxLength={3}`;
- payload normalization to uppercase remains in the accepted draft/payload builder;
- FREE payload nulling of the recovery handle remains in the accepted draft/payload
  builder;
- recurring amount remains a string draft consumed by existing canonical
  money/economics logic;
- fixed `EVERY_30_DAYS` presentation is unchanged;
- no economics or server-side pricing validation enters the child.

All seven frozen pricing-policy SHA-256 values independently reproduce exactly from
the uploaded snapshot. GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-004
  6bf1de4384da51091b0c1729172d6219738b8e5a

workspace task/ARCH-025-ADMIN-004
  0bb0c5d45b7902bbd19953f7502ca0426194f312
```

The focused and baseline-aware evidence is otherwise satisfactory: accepted pricing
security is 13/13, draft/controller is 14/14, unit suite is 245/247 with only the two
documented builder-translation failures, and the broad run's nine failures are the
exact `ARCH025-ADMIN-TEST-001` identifiers.

Acceptance is withheld only because that broad run also skipped three tests, and the
ARCH-025 builder rule explicitly does not authorize skipped tests.

#### A1-R1 — execute the three skipped production-runtime observability tests

The reported broad result:

```text
npm test
  total:   235
  passed:  223
  failed:  9
```

accounts for only 232 tests. Source inspection identifies the remaining three as
conditional tests in:

```text
tests/observability/admin-telemetry-bootstrap.test.mjs
```

They skip only when `.next/BUILD_ID` is absent, with the explicit test-runner reason:

```text
run `npm run build` first (.next/BUILD_ID missing)
```

The three test names are:

```text
production start preloads the shared runtime and exports safe telemetry
approved framework/OpenTelemetry telemetry passes through unchanged
exporter/backend failure does not break valid admin requests
```

Attempt 2 is evidence-only. With no source/dependency/environment drift, run:

```bash
npm run build
node --test tests/observability/admin-telemetry-bootstrap.test.mjs
```

The production build must succeed and all three formerly skipped production-runtime
tests must actually execute. If the file is green, combine that result with the
already-complete Attempt 1 broad run: the nine existing failures remain covered by
`ARCH025-ADMIN-TEST-001`, and complete no-skip coverage is established without
repeating unrelated suites.

If one of the formerly skipped tests fails, investigate it as a possible regression;
the existing baseline does not waive these three tests.

Do not modify implementation/test source merely to create another commit. Record the
Attempt 2 launcher/worktree/remote-clean evidence and return to review. If the
launcher incorporates relevant source, dependency or build-environment drift, rerun
the validation materially affected by that drift.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/shopify-pricing-step.tsx`
- accepted ADMIN-001 draft/controller and payload boundary
- accepted ADMIN-001 security test
- seven frozen pricing-policy tests
- `tests/observability/admin-telemetry-bootstrap.test.mjs` skip contract
- `ARCH025-ADMIN-BUILDER-TEST-001`
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-005 downstream contract

### Validation Reviewed

- GitHub implementation
  `6bf1de4384da51091b0c1729172d6219738b8e5a`: exactly two authorised files.
- Seven frozen pricing-policy SHA-256 values independently reproduced: all exact.
- Submitted accepted security suite: 13/13 passed.
- Submitted draft/controller suite: 14/14 passed.
- Submitted unit suite: 245 passed / 2 exact
  `ARCH025-ADMIN-BUILDER-TEST-001` failures.
- Submitted `npm test`: nine exact `ARCH025-ADMIN-TEST-001` failures, but three
  conditional production-runtime telemetry tests skipped because the build artifact
  did not yet exist; A1-R1 required.
- Submitted Prisma generation, targeted lint, TypeScript/production build and
  `git diff --check`: passed as recorded.
- Parent and implementation task refs are pushed and remote-aligned as submitted.

### Architecture Conformance

Conformant in implementation. ADMIN-004 moves only Shopify-pricing presentation and
preserves the accepted controller/payload/economics/server boundaries. Acceptance is
pending only no-skip execution evidence for the three production-runtime observability
tests.

### Follow-up

Return this same task to Ready, Attempt 1 retained and claim clear. Reclaim through
`/moda-task ARCH-025-ADMIN-004`, which must create Attempt 2 exactly once.

Attempt 2 is evidence-only unless A1-R1 exposes a real regression. Do not begin
ADMIN-005 until ADMIN-004 is architect-accepted Complete.
