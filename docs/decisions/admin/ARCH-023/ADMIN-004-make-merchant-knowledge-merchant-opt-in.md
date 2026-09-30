---
id: ARCH-023-ADMIN-004
architecture_id: ARCH-023
title: Make Merchant Knowledge merchant opt-in
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 42
executor: copilot
claimed_at: 2026-09-30T21:29:45Z
attempt: 1
depends_on:
  - ARCH-023-ADMIN-001
enables:
  - ARCH-023-SHOPIFY-004
  - ARCH-023-BACKGROUND-006
  - ARCH-023-COMMERCE-004
created: 2026-09-30
updated: 2026-09-30
---

# Make Merchant Knowledge merchant opt-in

## Objective

Reconcile the ARCH-023 fixed Merchant Knowledge Feature product policy from the previously accepted `ALWAYS_ENABLED` state to the final `MERCHANT_OPT_IN` state without changing plan configuration, source data or billing materialisation mechanics.

Target Feature identity/state:

```text
key            = merchant_knowledge
activationMode = MERCHANT_OPT_IN
systemRequired = false
active         = true
```

Missing `ShopFeaturePreference` is intentionally OFF. This task must not create per-shop preference rows.

## Context

ADMIN-001 was accepted before the merchant-opt-in product decision and deliberately created/validated `merchant_knowledge` as `ALWAYS_ENABLED`. Do not rewrite ADMIN-001 history. This bounded follow-up changes the product-policy descriptor and provides a safe transition for an existing row in the exact old ARCH-023 state.

## Scope

Primary authorized implementation surface:

```text
src/lib/admin/merchant-knowledge-plan-policy.ts
src/lib/admin/merchant/pricing-plan.ts
src/app/actions/merchant-pricing-plan.ts
src/app/actions/feature-catalogue.ts

existing ADMIN-001 focused tests
new/focused merchant-opt-in reconciliation tests
```

No database schema/migration changes.

## Requirements

### R1 — exact descriptor

Change the fixed descriptor to exactly:

```ts
{
  key: "merchant_knowledge",
  displayName: "Merchant Knowledge",
  description: "Allow the CommerceAgent to use merchant-managed knowledge sources.",
  activationMode: "MERCHANT_OPT_IN",
  systemRequired: false,
  active: true,
}
```

### R2 — bounded existing-row transition

The existing plan-authoring `ensureMerchantKnowledgeFeature(...)` path must be idempotent and accept exactly two pre-states:

```text
A. already target:
   MERCHANT_OPT_IN / systemRequired=false / active=true
   -> no mode mutation

B. exact previously accepted ARCH-023 state:
   ALWAYS_ENABLED / systemRequired=false / active=true
   -> update activationMode only to MERCHANT_OPT_IN
   -> write one normal PLAN_CATALOG_CHANGED audit event
```

Any other activationMode/systemRequired/active conflict fails closed with the existing bounded configuration-conflict behavior.

Do not change Feature key, plan mappings or C2 configuration during this transition.

### R3 — supported operational reconciliation path

The transition must occur through the existing authenticated Merchant Pricing Plan create/update transaction when that workflow is used after this task. Do not add a read-path/startup side effect and do not special-case the database schema.

Gateway/deployment validation will require the Feature to be in the target state before final ARCH-023 rollout; an operator may submit an unchanged supported plan update to execute the idempotent reconciliation if the old state is still present.

### R4 — generic feature catalogue ownership

Keep `merchant_knowledge` active and protected from generic deactivation. The ordinary Feature catalogue must not offer a conflicting way to change this fixed product-policy activation mode.

Do not set `systemRequired=true`.

### R5 — no preference seeding

Do not create or update `ShopFeaturePreference` rows. Existing generic semantics are authoritative:

```text
missing preference -> disabled
false              -> disabled
true               -> enabled
```

### R6 — tests

Prove:

```text
absent feature -> created MERCHANT_OPT_IN
old exact ALWAYS_ENABLED feature -> activationMode-only transition + audit
already MERCHANT_OPT_IN -> idempotent
wrong systemRequired/active/conflicting state -> fail closed
plan C2 configuration/mappings unchanged by transition
no ShopFeaturePreference rows created
merchant_knowledge cannot be deactivated through generic catalogue toggle
```

## Work Items

- [x] Update fixed product-policy descriptor.
- [x] Add bounded old-state -> target-state reconciliation in existing plan mutation.
- [x] Preserve generic plan configuration/materialisation behavior.
- [x] Add focused migration/idempotency/audit tests.

## Dependencies

- `ARCH-023-ADMIN-001`

## Acceptance Criteria

- [x] Merchant Knowledge fixed Feature is `MERCHANT_OPT_IN`.
- [x] Previously accepted `ALWAYS_ENABLED` state transitions safely/idempotently.
- [x] No per-shop preference is auto-created.
- [x] Existing plan C2 configuration is unchanged.

## Validation

- [x] focused ADMIN-004 tests (11 passed)
- [x] existing ADMIN-001 security regressions (12 passed)
- [x] TypeScript validation through `npm run build`; this repository does not declare an `npm run typecheck` script.
- [x] changed-file lint/diagnostics
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Review ready — ADMIN-004 implementation and validation are complete. The implementation task branch is committed and pushed; the parent task report is committed and pushed separately. Architect Review remains pending.

### Files Changed
- Implementation commit `dc6641249225857404192aff72ced80647c1d2d8` on `task/ARCH-023-ADMIN-004`:
  - `src/lib/admin/merchant-knowledge-plan-policy.ts`
  - `src/app/actions/feature-catalogue.ts`
  - focused Merchant Knowledge plan-policy and feature-catalogue tests.
- Parent task report: this file only.

### Work Completed
Updated the fixed `merchant_knowledge` descriptor to `MERCHANT_OPT_IN`, keeping `active=true` and `systemRequired=false`. The existing authenticated Merchant Pricing Plan save path now accepts the target state without a mode mutation, and transitions only the exact legacy `ALWAYS_ENABLED`/active/non-system-required state by changing `activationMode` only and writing one normal `PLAN_CATALOG_CHANGED` audit. Other incompatible states fail closed, including a compare-and-set race. The generic feature catalogue cannot create a duplicate fixed Feature or deactivate it. The transition preserves plan mappings and C2 configuration and never creates or mutates `ShopFeaturePreference` rows.

### Validation Results
Passed: 11 focused ADMIN-004 unit tests; 12 existing Admin security regressions; changed-file ESLint and diagnostics; `npm run build` (including TypeScript validation); and `git diff --check`. The repository does not declare an `npm run typecheck` script, so that exact command is unavailable; the production build completed its TypeScript validation successfully.

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-ADMIN-004`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-ADMIN-004`; both task branches are `task/ARCH-023-ADMIN-004`. The parent claim commit was `357d10223fa5461aa5021bcd2c1f8371dbf3d6ee`; parent and implementation branches were already current with `origin/main` at preparation. Recursive submodule synchronization and initialization passed, with `database` at `2eb17ee910491e8f9df82736fc0a843844415947`. No shared implementation checkout was switched or mutated. Implementation commit `dc6641249225857404192aff72ced80647c1d2d8` is pushed to `origin/task/ARCH-023-ADMIN-004`.

### Deviations
No schema/migration changes or per-shop preference seeding were required. The repository lacks the requested standalone typecheck script; TypeScript validation was provided by the successful production build.

### Assumptions
The existing authenticated plan create/update flow is the supported operational path for reconciling a previously accepted legacy Feature row, as specified by R3.

### Unresolved Issues
None.

### Architectural Concerns
None. The task is handed off for architect review; no Architect Review fields have been edited.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
