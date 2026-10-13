---
id: ARCH-038-ADMIN-002
architecture_id: ARCH-038
title: Manage Price Plan LIVE CommerceAgent overrides
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 21
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-14
---
# Manage Price Plan LIVE CommerceAgent overrides

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Add administrator-only optional LIVE CommerceAgent budget overrides to the existing Merchant Pricing Plan builder.

## Context

ARCH-024 assigns Commerce models on MerchantPricingPlan, not BillingPlan. Plan identity for subscription benefits matches by shopifyPlanHandle.

## Scope

- Integrate the reusable schema-driven Admin editor from ADMIN-001 in the existing Merchant Pricing Plan builder, in a separate **CommerceAgent Policy** section; show per-field **Override / Inherit** controls, labels, units and descriptions.
- Display the inherited LIVE Platform value and source when each `budget` JSON key is absent, without persisting the computed value as an override; show a read-only **effective plan budget** and independent field sources.
- Implement audited version-checked plan policy changes and explicit clear-to-inherit actions, a required audit reason, single-flight Save, inline validation, conflict/reload recovery, and a scoped paginated **Policy History** (actor, time, reason, before/after).
- Preserve current price-plan publication, translations, economics and model association workflow.
## Out of Scope

- Do not create another plan editor, duplicate BillingPlan fields or modify live shop policy.
- Do not expose override mutation to merchant-facing apps.

## Requirements

- Use MerchantPricingPlan.id for persisted override association; selection remains current-subscription handle match in Background.
- Saving one key in a sparse versioned JSONB `budget` must not implicitly copy Platform values or erase the other key. Reject explicit JSON null, unsupported keys and unknown schema versions. Use allowlisted ADMIN-001 editor descriptors rather than interpreting unrecognised JSON as editable fields.
- An inactive plan may remain the current subscribed plan; do not silently remove its existing benefits.

## Work Items

- [x] Reuse ADMIN-001 field descriptors/editor in the existing Merchant Pricing Plan UI and actions; render per-field inheritance and read-only effective-value/source summary.
- [x] Add scope/plan-filtered paginated Policy History and actionable conflict/reload presentation.
- [x] Add audit/CAS and inheritance validation.
- [x] Add focused plan-authoring regressions including mixed inheritance, cleared key deletion, other-key preservation, unsupported schema, duplicate submission, scoped audit history and conflicting edit.

## Interfaces / Contracts

Consumes `CommerceModelPolicy` (`context=LIVE`, `scope=PRICE_PLAN`, sparse `budget`) from DATABASE-001 and the reusable Admin policy editor and versioned field descriptors from ADMIN-001; no separate relation to BillingPlan.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Admin may override one field and inherit the other.
- [x] Plan publishing/model/translation behaviour remains unchanged.
- [x] Unauthorised changes and cross-plan writes are rejected.
- [x] Each override is an independent control with correct source labels and effective values; Inherit omits its JSON key.
- [x] Audit-history entries are scoped to this plan/environment and expose before/after, actor and reason; saving is disabled while in flight and conflicts offer reload.

## Validation

- [x] Focused plan UI/action tests
- [x] Relevant typecheck/lint/build scripts
- [x] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Developer Self-Review Passed — Attempt 2 is submitted for Architect review. All Work Items, Acceptance Criteria, and required validation are satisfied. `completion_mode: developer` remains in force; explicit developer completion is pending Architect acceptance.

### Files Changed

- `src/app/(protected)/billing/page.tsx`
- `src/app/actions/commerce-model-plan-policy.ts`
- `src/app/actions/merchant-pricing-plan.ts`
- `src/components/admin/billing-drawers.tsx`
- `src/components/admin/commerce-model-policy/live-plan-policy.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/commerce-agent-policy-step.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/merchant-pricing-plan-draft.ts`
- `src/components/admin/merchant/merchant-pricing-plan-builder/translations-review-step.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-builder/use-merchant-pricing-plan-draft.ts`
- `src/lib/admin/commerce-model-plan-create-policy.ts`
- `src/lib/admin/commerce-model-plan-policy-fields.ts`
- `src/lib/admin/commerce-model-plan-policy.ts`
- `tests/unit/commerce-model-plan-create-policy.test.ts`
- `tests/unit/commerce-model-plan-policy-action.test.mjs`
- `tests/unit/commerce-model-plan-policy-component.test.mjs`
- `tests/unit/commerce-model-plan-policy-drawer.test.mjs`
- `tests/unit/commerce-model-plan-policy-fields.test.ts`
- `tests/unit/commerce-model-plan-policy-wizard.test.mjs`
- `tests/unit/commerce-model-plan-policy.test.ts`

### Work Completed

- Added a plan-specific LIVE sparse-budget read/mutation service, effective Platform inheritance projection, version-checked set/clear operations, and scoped paginated audit history.
- Added the billing-page CommerceAgent Policy controls, optional field inheritance editor, validation/action path, and SUPER_ADMIN write gating.
- Added a CommerceAgent Policy step to the Merchant Pricing Plan wizard, preserving the existing plan workflow and carrying new-plan sparse overrides into the serializable plan-creation transaction with an audit event.
- Added service/parser, server-action, component, drawer, and wizard regressions for authorization, field validation, mixed inheritance, one-key/all-key clear, CAS conflicts, audit rollback, double submission, reload recovery, history presentation, and new-plan policy drafts.

### Validation Results

- Focused plan/create policy suite: **PASS**, 38 tests across seven files using Node's test runner. Node emitted existing `MODULE_TYPELESS_PACKAGE_JSON` warnings for `.ts` tests.
- `./node_modules/.bin/tsc --noEmit`: **PASS**.
- ESLint on all changed production files: **PASS**, zero errors.
- `npm run build`: **PASS**. Existing BullMQ optional `@valkey/valkey-glide` and dynamic dependency warnings were emitted; Prisma generation, Next.js compilation, TypeScript/build stages, and route generation completed.
- `git diff --check origin/main...HEAD`: **PASS** for the implementation branch; parent task record `git diff --check`: **PASS** before this review update.
- The implementation task branch is pushed at `3fb479f3be874ace5edbe451acdc8eb5d117bd78`, matching `origin/task/ARCH-038-ADMIN-002`.

### Deviations

The implementation branch upstream initially pointed to `origin/main`; it was corrected to `origin/task/ARCH-038-ADMIN-002` before Attempt 2 publication. No unresolved deviations remain.

### Assumptions

None

## Developer Self-Review - Changes Requested

### Review Result

Changes Requested — Attempt 1. Keep attempt 1 unchanged and transition to `ready` with `executor: null` and `claimed_at: null`. The implementation exists and is published, but the required focused plan-authoring interaction coverage is incomplete. Do not create Attempt 2 here.

### Required Corrections

1. Add tests that invoke `saveLivePlanBudgetAction` and verify unauthorized mutation denial, form-field validation errors, scoped create/update/clear, stale/CAS conflict response, and transaction rollback when audit insertion fails.
2. Add component/page tests for independent Override/Inherit controls and effective/source display, in-flight/double-submit disabling, inline errors, conflict reload, and empty plus paginated Policy History states. Include a regression that existing plan publishing, model association and translations remain unchanged.
3. Add a service/action regression that clearing one override removes only that key and preserves the other sparse override; verify mixed inheritance and reject explicit null, unsupported keys and schema versions.
4. Correct the implementation branch upstream to `origin/task/ARCH-038-ADMIN-002`, then rerun the focused action/component suite, `tsc --noEmit`, changed-file ESLint, `npm run build`, and `git diff --check`. Update the task checkboxes/report only from the resulting evidence.

### Evidence Reviewed

- Implementation commit `7570b5ec9d7f94a1b29210ec9baa80f6da148a5c` changes the eight files listed in the Completion Report. The implementation worktree was clean, and `HEAD` matched `origin/task/ARCH-038-ADMIN-002`; its configured upstream incorrectly points to `origin/main`.
- Parent claim commit `486a3f4e177769b7e44b1d094b40b3caffd1b4d0` is pushed on `origin/task/ARCH-038-ADMIN-002`; the parent worktree was clean before this review update.
- Focused service/parser tests passed 9/9; TypeScript, production-file ESLint, production build, and implementation `git diff --check` passed. The task's UI/action interaction coverage was not present in the test tree.
- Canonical parent and implementation worktrees were used. The implementation worktree's recursive `database` submodule is initialized at `12c3bee13cabeb3c8b9cb0ac602d836700702413`. No shared checkout or `main` branch was used for implementation changes.

### Unresolved Issues

- Required action and rendered-component regression tests are missing for authorization, form errors, saving/clear behavior, conflict recovery, double submission, and history states.
- The specified one-key clear behavior preserving the other sparse override and the unchanged Price Plan publication/model/translation workflow are not covered by a focused regression.
- The implementation branch's configured upstream is `origin/main`; point it to `origin/task/ARCH-038-ADMIN-002` before the next publication operation.

### Architectural Concerns

None

## Developer Self-Review - Passed/Accepted

### Review Result

Passed — Attempt 2. The plan-policy action, editor, wizard integration, sparse inheritance behavior, audit/CAS handling, and focused regression coverage satisfy the task scope. The task transitions to `review`; explicit developer completion remains pending and is not recorded here. Attempt 1's Changes Requested record remains historical.

### Attempt 2 Reconciliation

- Implementation commit `3fb479f3be874ace5edbe451acdc8eb5d117bd78` contains the plan-builder integration and action/component/drawer/wizard tests; the implementation worktree is clean and matches `origin/task/ARCH-038-ADMIN-002`.
- Parent claim commit `71a671f3a9fb4f7508058e96595a2884a5d9311f` is published. This review update will be committed and pushed on the same parent task branch.
- The implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-ADMIN-002`; the parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-ADMIN-002`. Both are on `task/ARCH-038-ADMIN-002`; recursive `database` submodule initialization passed at `12c3bee13cabeb3c8b9cb0ac602d836700702413`.
- The implementation branch upstream is `origin/task/ARCH-038-ADMIN-002`; its published task branch is synchronized.

### Evidence Reviewed

- Focused suite: **38 passed, 0 failed** across plan creation/service/parser/action/component/drawer/wizard tests.
- TypeScript, changed-production-file ESLint, production build, and implementation `git diff --check origin/main...HEAD` passed. Existing BullMQ build warnings and Node module-type warnings are recorded in the Completion Report.
- Action coverage verifies ADMIN/SUPPORT rejection, form errors, successful scoped mutation/audit, one-key sparse preservation, clearing all keys, create, stale/CAS conflict, audit rollback, unsupported schema, and missing-plan rejection. Component/wizard coverage verifies independent Override/Inherit controls, effective/source display, double-submit prevention, errors, conflict reload, history empty/pagination states, and new/existing plan wizard placement.

### Remaining Issues

None identified for the task scope. Architect acceptance and explicit developer completion remain pending.

### Follow-up

Await Architect review. Do not mark the task complete until the developer explicitly records completion after acceptance.

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

Pending implementation

### Follow-up

None
