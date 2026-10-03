---
id: ARCH-026-ADMIN-001
architecture_id: ARCH-026
title: Read the shared Shop onboarding milestone in tenant administration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-10-03T19:43:25Z
attempt: 1
depends_on:
  - ARCH-026-SHOPIFY-001
  - ARCH-026-BACKGROUND-001
enables:
  - ARCH-026-ADMIN-002
created: 2026-10-02
updated: 2026-10-03
---

# Read the shared Shop onboarding milestone in tenant administration

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Migrate the Admin tenant read model and repository-owned development/test-data tooling from `shopify.ShopSettings.onboardingCompleted` to provider-neutral `commerce.Shop.onboardingCompleted`, so Admin can represent Shopify and future WooCommerce merchants without requiring a Shopify settings row.

The legacy Shopify field remains in the schema and is not removed by this task.

## Context

Current Admin production tenant presentation exposes `onboardingCompleted` from the nested Shopify settings relation. That is not valid for a Woo-backed Shop because Woo must not create `shopify.ShopSettings` merely to satisfy an Admin read model.

DATABASE-001 introduces/backfills the shared field. SHOPIFY-001 and BACKGROUND-001 then ensure the current production onboarding completion writers maintain that shared field (while still mirroring the legacy field). Only after both are complete should Admin make the shared field its cross-platform presentation source.

Inspected Admin references include:

```text
src/lib/admin/data.ts
src/lib/admin/types.ts
src/components/admin/tenant-administration.tsx
scripts/shopify_dashboard_test_data.py
scripts/README-shopify-dashboard-test-data.md
```

## Scope

Modify only `moda-interact-admin` read-model/test/script code needed to use the shared Shop milestone.

### Tenant read model

Load:

```text
commerce.Shop.onboardingCompleted
```

as the source for the existing tenant-facing `onboardingCompleted` property.

Do not require `Shop.settings` to exist merely to determine onboarding status.

Preserve the existing Admin DTO/UI property name unless a repository-local type cleanup is unavoidable; this task changes ownership/source, not presentation semantics.

### Admin development/test-data tooling

Any Admin-owned script that deliberately creates/changes onboarding fixtures must update the shared Shop field as well as the retained legacy Shopify field where it is creating a Shopify fixture.

For explicit Shopify test fixtures, dual-setting is acceptable during this transition. Do not create Shopify settings for Woo fixtures.

## Out of Scope

- Removing the legacy `ShopSettings.onboardingCompleted` column.
- Shopify app/background production lifecycle changes; prerequisites own them.
- Woo merchant application UI.
- Billing/subscription redesign.
- Cross-tenant Admin redesign.
- System-test fixture migration outside the Admin repository.

## Requirements

### R1 — Admin source is provider-neutral

Tenant administration reads onboarding completion from `Shop.onboardingCompleted`.

### R2 — Woo does not require Shopify settings

A Woo-backed Shop without `ShopSettings` can still be represented correctly by the Admin tenant read model.

### R3 — Legacy schema remains untouched

Do not remove/rename the Shopify compatibility field.

### R4 — Admin fixture tooling remains coherent

Shopify fixtures that intentionally set onboarding completion update both shared and legacy values while the legacy field remains.

## Work Items

- [ ] Update Admin nested database gitlink to the accepted DATABASE-001 main commit and regenerate Prisma.
- [ ] Change tenant query/read-model mapping to source onboarding completion from `Shop.onboardingCompleted`.
- [ ] Preserve existing Admin DTO/UI semantics while removing the need for ShopSettings solely for onboarding status.
- [ ] Update Admin-owned Shopify test-data tooling/docs to set shared + legacy onboarding completion consistently.
- [ ] Add focused tests for Shopify Shop with settings and Woo Shop without settings.

## Interfaces / Contracts

### Database owner

`ARCH-026-DATABASE-001`

### Source

```text
commerce.Shop.onboardingCompleted
```

### Compatibility field retained

```text
shopify.ShopSettings.onboardingCompleted
```

## Dependencies

- `ARCH-026-SHOPIFY-001`
- `ARCH-026-BACKGROUND-001`

Both must be architect-accepted Complete so the shared field is maintained by the existing production completion writers before Admin relies on it as its cross-platform source.

## Enables

- `ARCH-026-ADMIN-002`

ADMIN-002 serializes the later provider-neutral international-context read migration in the Admin repository.

## Acceptance Criteria

- [ ] Admin tenant read model uses `Shop.onboardingCompleted`.
- [ ] A Woo Shop with no `ShopSettings` row reports the shared onboarding value correctly.
- [ ] Existing Shopify Admin tenant presentation remains behaviorally unchanged.
- [ ] Admin Shopify fixture tooling writes both shared and legacy flags when explicitly setting onboarding completion.
- [ ] No Woo-specific onboarding duplicate or `ACCOUNT_PENDING_ACTIVATION` state is introduced.
- [ ] Legacy field remains in schema.

## Validation

- [ ] Prisma generation from accepted DATABASE-001 gitlink;
- [ ] typecheck;
- [ ] targeted lint;
- [ ] focused Admin data/read-model tests for Shopify and Woo Shop shapes;
- [ ] Admin UI component tests where affected;
- [ ] test-data script validation/dry-run as supported by the repository;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

## Stop Condition

After the defined work and validation complete, set the task to `review`, finish the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Keep this task a data-source migration. Do not redesign tenant administration or add Woo-specific Admin screens merely because the shared field now supports Woo Shops.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- SHOPIFY-001 and BACKGROUND-001 maintain the shared field before this task becomes Ready.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
