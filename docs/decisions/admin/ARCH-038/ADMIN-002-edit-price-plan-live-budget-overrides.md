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
status: in_progress
priority: 21
executor: developer
claimed_at: 2026-10-13T23:09:52Z
attempt: 2
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
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

- [ ] Reuse ADMIN-001 field descriptors/editor in the existing Merchant Pricing Plan UI and actions; render per-field inheritance and read-only effective-value/source summary.
- [ ] Add scope/plan-filtered paginated Policy History and actionable conflict/reload presentation.
- [ ] Add audit/CAS and inheritance validation.
- [ ] Add focused plan-authoring regressions including mixed inheritance, cleared key deletion, other-key preservation, unsupported schema, duplicate submission, scoped audit history and conflicting edit.

## Interfaces / Contracts

Consumes `CommerceModelPolicy` (`context=LIVE`, `scope=PRICE_PLAN`, sparse `budget`) from DATABASE-001 and the reusable Admin policy editor and versioned field descriptors from ADMIN-001; no separate relation to BillingPlan.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Admin may override one field and inherit the other.
- [ ] Plan publishing/model/translation behaviour remains unchanged.
- [ ] Unauthorised changes and cross-plan writes are rejected.
- [ ] Each override is an independent control with correct source labels and effective values; Inherit omits its JSON key.
- [ ] Audit-history entries are scoped to this plan/environment and expose before/after, actor and reason; saving is disabled while in flight and conflicts offer reload.

## Validation

- [ ] Focused plan UI/action tests
- [x] Relevant typecheck/lint/build scripts
- [x] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-13T23:09:52Z. Attempt 1 review history is preserved below.

### Files Changed

- `src/app/(protected)/billing/page.tsx`
- `src/app/actions/commerce-model-plan-policy.ts`
- `src/components/admin/billing-drawers.tsx`
- `src/components/admin/commerce-model-policy/live-plan-policy.tsx`
- `src/lib/admin/commerce-model-plan-policy-fields.ts`
- `src/lib/admin/commerce-model-plan-policy.ts`
- `tests/unit/commerce-model-plan-policy-fields.test.ts`
- `tests/unit/commerce-model-plan-policy.test.ts`

### Work Completed

- Added a plan-specific LIVE sparse-budget read/mutation service, effective Platform inheritance projection, version-checked set/clear operations, and scoped paginated audit history.
- Added the billing-page CommerceAgent Policy controls, optional field inheritance editor, validation/action path, and SUPER_ADMIN write gating.
- Added focused service/parser tests for sparse validation, create/update/clear, CAS conflicts, audit coupling, and history scoping.

### Validation Results

- Focused service/parser tests: **PASS**, 9 tests across two files using `node --experimental-strip-types --test tests/unit/commerce-model-plan-policy.test.ts tests/unit/commerce-model-plan-policy-fields.test.ts`. Node emitted existing `MODULE_TYPELESS_PACKAGE_JSON` warnings for the `.ts` tests.
- `./node_modules/.bin/tsc --noEmit`: **PASS**.
- ESLint on all six changed production files: **PASS**, zero errors.
- `npm run build`: **PASS**. Existing BullMQ optional `@valkey/valkey-glide` and dynamic dependency warnings were emitted.
- `git diff --check origin/main...HEAD`: **PASS** for the implementation branch; parent task record `git diff --check`: **PASS** before this review update.
- Required action/component-level plan-authoring regression coverage: **NOT COMPLETE**. The two new tests do not invoke `saveLivePlanBudgetAction` or render `LivePlanPolicyControls`.

### Deviations

The implementation branch's configured upstream points to `origin/main` even though `origin/task/ARCH-038-ADMIN-002` exists at the same implementation commit. Correct the task branch upstream before the next publication operation.

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
