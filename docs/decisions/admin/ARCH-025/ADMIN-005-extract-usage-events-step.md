---
id: ARCH-025-ADMIN-005
architecture_id: ARCH-025
title: Extract Usage events step
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-ADMIN-004
enables:
  - ARCH-025-ADMIN-006
created: 2026-10-02
updated: 2026-10-03
---

# Extract Usage events step

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract usage-event/tier presentation and local editing dispatch behind a focused child component while retaining canonical BuilderEvent helpers and navigation/economics ownership.

## Context

Step 3 contains the largest repeated form markup outside economics. The existing pure helpers already own add/move/update/tier transformations and serialization; the child should present/edit through those accepted controller actions rather than copy their logic.

## Scope

Authorised implementation surface:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/usage-events-step.tsx
```

Directly adjacent type-only files under `src/components/admin/merchant/merchant-pricing-plan-builder/` are permitted only when required to keep this bounded extraction coherent.

## Out of Scope

Rewriting BuilderEvent helpers, economics evaluation, Shopify pricing step, changing five-event limit or zero-cost policy.

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


### R1 — complete usage-event presentation

Move step-3 markup for event count/add, labels/handles/credits/max uses, FIXED/GRADUATED/VOLUME modes, currency-aware prices, tiers, ordering and removal.

### R2 — canonical local operations

Continue using accepted controller actions backed by existing `createEmptyBuilderEvent`, `moveBuilderEvent`, `updateBuilderEvent`, `addBuilderTier`, `updateBuilderTier`, `serializeBuilderEvent`, `formatBuilderEventPrice` and zero-cost helpers. Preserve the maximum of five events and ADMIN-001 deterministic client-key generation semantics.

Preserve current editing quirks rather than normalizing data during extraction: switching pricing mode is a shallow event update and does not clear the inactive FIXED/tier fields; non-FIXED events allow at most six tiers; the last tier's `upTo` input remains disabled and displayed as Unlimited; a tier cannot be removed when only one remains; event/tier removal and reordering preserve all surviving client keys and field values exactly.

### R3 — gate stays outside presentation

The wizard controller remains owner of the step-3 forward gate (`events.some(hasUnboundedZeroCostFixedEvent)`). The child may display `ZERO_COST_USAGE_EVENT_MESSAGE` but must not redefine navigation or economics policy.

## Work Items

- [x] Extract complete Usage events markup.
- [x] Route edits through accepted controller actions/canonical helpers.
- [x] Keep navigation/economics decisions outside the child.
- [x] Run accepted security/controller/policy suites.

## Interfaces / Contracts

Repository-internal UI extraction only. Public contract remains `MerchantPricingPlanBuilder` at its existing module path and the existing `mutateMerchantPricingPlanAction` form submission contract. Canonical domain/policy modules are consumed rather than redefined.

## Dependencies

- `ARCH-025-ADMIN-004`

## Enables

- `ARCH-025-ADMIN-006`

## Acceptance Criteria

- [x] All usage-event modes/labels/tier controls and five-event limit remain unchanged.
- [x] Zero-cost forward blocking and payload serialization remain identical.
- [x] Accepted ADMIN-001 security test file is unmodified and passes.

## Validation

- [x] `npm run prisma:generate` succeeds.
- [x] All seven frozen domain-test SHA-256 values match their expected values.
- [x] The seven frozen domain tests and `tests/security/admin-merchant-pricing-plan.test.mjs` have no diff.
- [x] `node --test tests/security/admin-merchant-pricing-plan.test.mjs` passes.
- [x] `node --experimental-strip-types --test tests/unit/merchant-pricing-plan-builder-draft.test.ts` passes.

- [x] `npm run test:unit` completes with only the two exact `ARCH025-ADMIN-BUILDER-TEST-001` failures.
- [x] `npm test` completes with no failure outside the documented `ARCH025-ADMIN-TEST-001` identifiers.
- [x] The task-specified targeted lint command reports no errors; test files are ignored by repository ESLint config, and direct ESLint on both changed production TSX files passes cleanly.
- [x] `npm run build` succeeds, including TypeScript compilation. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- [x] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Admin task.

## Implementation Notes

None

## Completion Report

### Status

Review; Usage events presentation extraction and task validation are complete.

### Files Changed

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/usage-events-step.tsx`

### Work Completed

- Moved the complete step-3 Usage events presentation into `UsageEventsStep`, preserving the existing copy, labels, controls, pricing modes, tier limits/order, and event ordering/removal affordances.
- Wired the child to the accepted draft controller's existing event/tier actions and zero-cost presentation selector. Kept navigation gating, economics, serialization, form action/fields, and final-review summary in their existing owners.
- Left `tests/security/admin-merchant-pricing-plan.test.mjs`, all seven frozen domain tests, the draft/controller, and canonical policy/helpers unchanged.

### Validation Results

- Focused ADMIN-001 security suite: 13 passed, 0 failed.
- Focused draft/controller suite: 14 passed, 0 failed.
- `npm run prisma:generate`: passed.
- All seven frozen domain-test SHA-256 values matched; frozen-test and accepted security-test diffs are empty.
- `npm run test:unit`: 250 tests, 248 passed, 2 failed. The only failures are `rejects stale metadata, locale/header changes, and highlight identity changes` and `returns all bounded validation issues in canonical order`, both documented in `ARCH025-ADMIN-BUILDER-TEST-001`.
- `npm test`: six failures observed, all within the exact inherited `ARCH025-ADMIN-TEST-001` identifier set; no new identifier or failure reason was observed. Several failures from the documented nine-failure set passed in this run.
- Task-specified targeted lint completed with no errors; the two test paths were reported ignored by the repository ESLint configuration. Direct ESLint on the builder and new child passed cleanly.
- `npm run build`: passed, including TypeScript. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- `git diff --check`: passed.

### Deviations

The two required full suites retain only documented inherited baseline failures. Full unit/security validation was rerun serially after Prisma generation/build to avoid test-run contention; serial unit results matched `ARCH025-ADMIN-BUILDER-TEST-001`, and serial security failures were a subset of `ARCH025-ADMIN-TEST-001`.

### Assumptions

The existing controller action signatures and selectors are the accepted ADMIN-001 contract; no controller-interface changes were needed.

### Unresolved Issues

No task-owned issues remain. The inherited unit and security failures remain tracked by their baseline IDs.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

The Usage-events extraction is accepted as a move-only presentation refactor.

Architect inspection of Admin implementation
`bbc560a6b2b2d49f4a0836326104e37135d767ac` found exactly the two
task-authorised files changed:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/merchant/merchant-pricing-plan-builder/usage-events-step.tsx
```

The new child consumes only the accepted ADMIN-001 controller boundary: `events`,
`currency`, existing event/tier actions, and the existing zero-cost presentation
selector/message. No controller, reducer, payload, economics, server-action, policy
helper or test source changed.

GitHub comparison against the implementation parent confirms that the extracted JSX
preserves the pre-ADMIN-005 step-3 behavior exactly, including the intentionally
existing editing quirks:

- maximum five events;
- deterministic event identity remains owned by the accepted controller;
- FIXED / GRADUATED / VOLUME mode switching remains a shallow event update and does
  not clear inactive fields;
- non-FIXED events retain the six-tier maximum;
- the final tier remains disabled and displayed as Unlimited;
- a tier cannot be removed when only one remains;
- tier removal continues to use the pre-existing `updateEvent(...tiers.filter(...))`
  path rather than introducing a new normalization behavior;
- event removal/reordering continues through the accepted controller actions and
  preserves surviving client keys/field values;
- the existing currency-aware field labels and zero-cost warning copy are unchanged.

The required policy owners remain outside the child. In the accepted controller:

- `serializedUsageEvents = draft.events.map(serializeBuilderEvent)` still owns payload
  serialization;
- `economicsConfigurationKey` still incorporates serialized usage events and drives
  economics-override invalidation;
- portfolio economics evaluation still consumes `draft.events`;
- `canNavigateTo()` still owns the step-3 forward gate through
  `draft.events.some(hasUnboundedZeroCostFixedEvent)`;
- hidden form payload construction remains controller-owned.

The builder shell still owns navigation and retains the final-review Usage-events
summary using the existing controller formatting selector.

Independent checks against the uploaded snapshot reproduce all seven frozen
pricing-policy SHA-256 values exactly. The accepted ADMIN-001 pricing security suite
passes 13/13 and the draft/controller suite passes 14/14.

The broader validation is baseline-conformant:

```text
npm run test:unit
  250 total
  248 passed
  2 failed
```

The two failures are the exact `ARCH025-ADMIN-BUILDER-TEST-001` translation failures.

The full security/observability run was executed serially after Prisma generation and
the successful production build. It reports six failures, all a strict subset of the
existing `ARCH025-ADMIN-TEST-001` identifiers; no new identifier or failure reason is
present. Disappeared baseline failures are improvements and must not be recreated.

GitHub independently confirms the pushed task heads:

```text
Admin implementation task/ARCH-025-ADMIN-005
  bbc560a6b2b2d49f4a0836326104e37135d767ac

workspace task/ARCH-025-ADMIN-005
  b936ae428725c50a9058e86d7767342670b4c051
```

The task returned to review with stale `executor` / `claimed_at` metadata despite the
handoff being complete and both task worktrees clean. This architect reconciliation
clears those lifecycle fields directly; no additional attempt is required.

### Reviewed Files

- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/usage-events-step.tsx`
- accepted ADMIN-001 draft/controller modules
- accepted ADMIN-001 pricing security test
- seven frozen pricing-policy test assets
- `ARCH025-ADMIN-BUILDER-TEST-001`
- `ARCH025-ADMIN-TEST-001`
- this task Completion Report
- ARCH-025 parent architecture and ADMIN-006 downstream contract

### Validation Reviewed

- GitHub implementation commit
  `bbc560a6b2b2d49f4a0836326104e37135d767ac`: exactly two authorised files.
- Seven frozen pricing-policy SHA-256 values independently reproduced: all exact.
- Independently rerun accepted pricing security suite: 13/13 passed.
- Independently rerun draft/controller suite: 14/14 passed.
- Submitted unit suite: 248/250 with only the two exact inherited builder-translation
  failures.
- Submitted full security/observability suite: six failures, all within the exact
  inherited `ARCH025-ADMIN-TEST-001` set; no new/worsened task failure.
- Submitted Prisma generation, targeted source lint, production build and
  `git diff --check`: passed as recorded.
- Parent and implementation task refs are pushed and remote-aligned.

### Architecture Conformance

Conformant. ADMIN-005 moves only Usage-events presentation/edit wiring while preserving
the accepted controller's navigation, serialization, economics, identity and policy
ownership. Public builder/form/server semantics remain unchanged.

### Follow-up

`ARCH-025-ADMIN-005` is Complete / Accepted at Attempt 1. Its sole dependant,
`ARCH-025-ADMIN-006`, has all declared dependencies satisfied and is promoted to
Ready, Attempt 0, claim clear. Do not start ADMIN-007 or later builder-chain tasks
implicitly.
