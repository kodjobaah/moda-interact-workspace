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
status: ready
priority: 42
executor: null
claimed_at: null
attempt: 0
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

- [ ] Update fixed product-policy descriptor.
- [ ] Add bounded old-state -> target-state reconciliation in existing plan mutation.
- [ ] Preserve generic plan configuration/materialisation behavior.
- [ ] Add focused migration/idempotency/audit tests.

## Dependencies

- `ARCH-023-ADMIN-001`

## Acceptance Criteria

- [ ] Merchant Knowledge fixed Feature is `MERCHANT_OPT_IN`.
- [ ] Previously accepted `ALWAYS_ENABLED` state transitions safely/idempotently.
- [ ] No per-shop preference is auto-created.
- [ ] Existing plan C2 configuration is unchanged.

## Validation

- [ ] focused ADMIN-004 tests
- [ ] existing ADMIN-001 regressions
- [ ] `npm run typecheck`
- [ ] changed-file lint/diagnostics
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

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
