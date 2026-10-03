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
status: review
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

- [x] Verify the Admin nested database gitlink contains the accepted shared onboarding field and regenerate Prisma. The existing pin is the newer accepted DATABASE-002 main commit and is preserved.
- [x] Change tenant query/read-model mapping to source onboarding completion from `Shop.onboardingCompleted`.
- [x] Preserve existing Admin DTO/UI semantics while removing the need for ShopSettings solely for onboarding status.
- [x] Update Admin-owned Shopify test-data tooling/docs to set shared + legacy onboarding completion consistently.
- [x] Add focused tests for Shopify Shop with settings and Woo Shop without settings.

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

- [x] Admin tenant read model uses `Shop.onboardingCompleted`.
- [x] A Woo Shop with no `ShopSettings` row reports the shared onboarding value correctly.
- [x] Existing Shopify Admin tenant presentation remains behaviorally unchanged.
- [x] Admin Shopify fixture tooling writes both shared and legacy flags when explicitly setting onboarding completion.
- [x] No Woo-specific onboarding duplicate or `ACCOUNT_PENDING_ACTIVATION` state is introduced.
- [x] Legacy field remains in schema.

## Validation

- [x] Prisma generation from the accepted nested database pin (DATABASE-002 main, including the DATABASE-001 field);
- [x] typecheck;
- [x] targeted lint;
- [x] focused Admin data/read-model tests for Shopify and Woo Shop shapes;
- [x] Admin UI information-architecture test (4/4; no UI component source change was required);
- [x] test-data script validation (`py_compile` and `--help`; no database dry-run is provided by the script);
- [x] production build;
- [x] `git diff --check`;
- [x] clean task-worktree evidence.

## Stop Condition

After the defined work and validation complete, set the task to `review`, finish the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Keep this task a data-source migration. Do not redesign tenant administration or add Woo-specific Admin screens merely because the shared field now supports Woo Shops.

## Completion Report

### Status

Review

### Files Changed

- `src/lib/admin/data.ts`
- `src/lib/admin/tenant-onboarding.ts`
- `tests/unit/tenant-onboarding.test.ts`
- `scripts/shopify_dashboard_test_data.py`
- `scripts/README-shopify-dashboard-test-data.md`

### Work Completed

- Changed `getTenantDetail` to select `commerce.Shop.onboardingCompleted` directly and map the existing DTO property through a small shared-field projection. The nested settings select remains for recovery controls but no longer includes or supplies the onboarding flag.
- Added focused tests proving the shared value wins for a Shopify-shaped Shop even if a legacy settings value differs, Woo-shaped Shops work without settings, and the actual tenant-detail query selects/maps the shared field without a nested fallback.
- Updated the Admin-owned Shopify dashboard test-data script to synchronize `commerce.Shop.onboardingCompleted` with the fixture's `ShopSettings.onboardingCompleted`. Newly-created Shopify test settings use `true` for both; existing setting values are preserved and mirrored to Shop. The script resolves Shop platform and only queries/creates Shopify settings for `SHOPIFY`, so a Woo fixture does not acquire a `ShopSettings` row.
- Updated the test-data README to document the shared/legacy synchronization and the Shopify-only settings guard.
- Preserved the existing tenant DTO property and UI behavior; no Woo-specific lifecycle or state was added.
- The nested `database/` gitlink was already at accepted DATABASE-002 main commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3` (`heads/main`), which includes the required shared onboarding field. Preserved this newer compatible pin rather than moving backwards to an older DATABASE-001 commit; no schema or gitlink change was needed.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-ADMIN-001` / `task/ARCH-026-ADMIN-001`
  - implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-ADMIN-001` / `task/ARCH-026-ADMIN-001`
  - shared workspace checkout switched/mutated: no; shared implementation checkout switched/mutated: no; another task worktree reused: no.
- Start-of-attempt synchronization: parent and implementation remote task branches fast-forwarded `not-needed`; `origin/main` incorporated `already-current` in both worktrees.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; recorded database pin `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.

### Validation Results

- `npm ci`: passed; installed 661 locked packages. npm reported 1 critical, 10 high, and 2 moderate audit findings and install-script approval notices.
- `npm run prisma:generate`: passed against nested database commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3` using Prisma 6.19.3.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed.
- `npx eslint src/lib/admin/data.ts src/lib/admin/tenant-onboarding.ts`: passed. The repository ESLint configuration ignores `tests/`.
- `node --experimental-strip-types --test tests/unit/tenant-onboarding.test.ts`: passed, 3/3.
- `node --test tests/security/admin-tenant-information-architecture.test.mjs`: passed, 4/4.
- Python script validation after the Shopify-only guard: `/Users/kwadwoadomafriyie/project/moda-interact-workspace/.venv/bin/python -m py_compile scripts/shopify_dashboard_test_data.py` passed; invoking the script with `--help` passed. The script does not provide a database-free dry-run.
- `npm run test:unit`: 265 passed / 2 failed / 0 skipped across 267 tests. The unrelated failures are in `merchant-pricing-translation-workbook.test.ts` and `merchant-pricing-translations.test.ts`.
- `npm test`: executed; six unrelated existing security checks fail in billing-pack status, two Shared internationalization catalogue/package expectations, merchant-support package expectations, security-boundary, and tenant-business-KPI tests. No failing case concerns onboarding.
- `npm run build`: passed (Prisma generation, optimized Next.js build and TypeScript). Existing optional BullMQ dependency/critical-dependency warnings were emitted.
- Final source audit found no Admin tenant onboarding reads from `settings?.onboardingCompleted`; the remaining ShopSettings onboarding references are fixture creation/preservation and documentation.
- `git diff --check`: passed.

### Deviations

- The nested database pointer already referenced the newer accepted DATABASE-002 main commit, so it was retained rather than reset to DATABASE-001.
- Broad unit/security suites have unrelated failures documented above; focused onboarding tests, Prisma validation, typecheck, lint, UI architecture test, script validation and production build pass.

### Assumptions

- SHOPIFY-001 and BACKGROUND-001 maintain the shared field before this task becomes Ready.

### Unresolved Issues

The repository-wide unit and security suites have the unrelated failures listed above; no task-specific validation remains outstanding.

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
