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
status: complete
priority: 40
executor: null
claimed_at: null
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
- `npm test`: executed; residual failures are confined to the existing `ARCH025-ADMIN-TEST-001` categories in billing-pack status, Shared internationalization catalogue/package expectations, merchant-support package expectations, security-boundary, and tenant-business-KPI tests. No failing case concerns onboarding, and no new failure category was introduced by ADMIN-001.
- `npm run build`: passed (Prisma generation, optimized Next.js build and TypeScript). Existing optional BullMQ dependency/critical-dependency warnings were emitted.
- Final source audit found no Admin tenant onboarding reads from `settings?.onboardingCompleted`; the remaining ShopSettings onboarding references are fixture creation/preservation and documentation.
- `git diff --check`: passed.

### Deviations

- The nested database pointer already referenced the newer accepted DATABASE-002 main commit, so it was retained rather than reset to DATABASE-001.
- Broad unit/security suites have unrelated failures documented above; focused onboarding tests, Prisma validation, typecheck, lint, UI architecture test, script validation and production build pass.

### Assumptions

- SHOPIFY-001 and BACKGROUND-001 maintain the shared field before this task becomes Ready.

### Unresolved Issues

No task-specific validation remains outstanding. The two unit failures are the established Merchant Pricing translation baseline and the residual security failures are within `ARCH025-ADMIN-TEST-001`; baseline failures that have disappeared are improvements and must not be recreated.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

ARCH-026-ADMIN-001 is accepted Complete.

Implementation `2fdbf1813a039ff8ee9e58423cc38517de5e95b9` is a bounded Admin
read-model/test-fixture migration. GitHub confirms the commit changes exactly:

```text
src/lib/admin/data.ts
src/lib/admin/tenant-onboarding.ts
tests/unit/tenant-onboarding.test.ts
scripts/shopify_dashboard_test_data.py
scripts/README-shopify-dashboard-test-data.md
```

No package/lockfile, schema, database gitlink, UI component, billing-control module or
unrelated Admin source changed.

The production tenant-detail boundary is correct:

- `getTenantDetail()` selects top-level `commerce.Shop.onboardingCompleted`;
- the existing DTO property remains `onboardingCompleted`;
- mapping delegates only to the shared Shop value;
- the nested `settings` select no longer includes onboarding state;
- Shopify settings remain selected only for existing recovery-control fields.

A Woo Shop does not require `ShopSettings` to be represented by this read model.
`row.settings` is optional throughout the recovery-control projection, and
`getTenantBillingControls(shopId)` is itself Shop-scoped and does not require a Shopify
settings row. The Woo-without-settings behavior is therefore a real runtime property,
not only a helper-test artifact.

The fixture-tool migration is also bounded correctly. `resolve_shop()` reads the Shop
platform. `ensure_dashboard_access()` enters the Shopify settings path only when:

```text
shop.platform == SHOPIFY
```

For explicit Shopify fixtures:

- an absent test-owned `ShopSettings` row is created with
  `onboardingCompleted = true`;
- shared `Shop.onboardingCompleted` is set to the same value;
- an existing ShopSettings milestone is preserved and mirrored to shared Shop state;
- the script does not create a Shopify settings row for a Woo Shop.

This preserves the script's pre-existing safety rule not to overwrite an existing
merchant ShopSettings row while keeping the development fixture internally coherent.
No Woo-specific onboarding lifecycle/state was introduced.

The nested database pin is correct and intentionally unchanged. GitHub independently
confirms both implementation parent
`9cf71c8e71961c2ced7e3cceee590a2e5b41b9fc` and submitted implementation
`2fdbf181...` point at:

```text
database/
  16dba1a7c88f432f2f7d2cf718ae8297977cdcc3
```

That accepted DATABASE-002 commit contains the DATABASE-001 shared onboarding field, so
resetting the gitlink backwards was neither required nor desirable.

The task-owned focused checks are green. The architect independently reran from the
uploaded exact snapshot:

```text
tests/unit/tenant-onboarding.test.ts
  3 / 3 passed

tests/security/admin-tenant-information-architecture.test.mjs
  4 / 4 passed

python -m py_compile scripts/shopify_dashboard_test_data.py
  passed

python scripts/shopify_dashboard_test_data.py --help
  passed
```

Submitted Prisma generation/validation, TypeScript, targeted lint, production build and
`git diff --check` also pass.

The broad-suite residuals do not block this task:

```text
npm run test:unit
  265 passed / 2 failed
```

The two failures are the exact established Merchant Pricing translation baseline:

```text
rejects stale metadata, locale/header changes, and highlight identity changes
returns all bounded validation issues in canonical order
```

For `npm test`, the submitted residual categories are a strict subset of the durable
`ARCH025-ADMIN-TEST-001` set. The architect independently reran the source-only
`admin-billing-pack-status.test.mjs` from this snapshot and reproduced both exact
baseline identifiers:

```text
every RecoveryCreditPurchaseStatus has an ICU label and filter support
purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups
```

The remaining reported categories are the already documented Shared i18n,
merchant-support package, security-boundary and tenant-business-KPI baseline areas.
The ADMIN-001 commit does not touch those owning modules/tests; its `data.ts` edit is
confined to `getTenantDetail`, while the tenant-business-KPI baseline assertion targets
the unchanged Tenant Directory KPI source. No onboarding-owned assertion fails.

The Completion Report's brittle “six checks” wording is corrected by this architect
reconciliation to reference the durable baseline categories rather than an imprecise
count. Baseline failures that have disappeared are improvements and are not recreated.

The disclosed npm audit findings are inherited from the unchanged lockfile/dependency
tree; ADMIN-001 changes no dependency metadata, so dependency remediation is outside this
bounded data-source migration.

The Completion Report records the required launcher/worktree preparation packet:
dedicated parent and Admin task worktrees, negative shared/other-worktree assertions,
start-of-attempt synchronization, recursive submodule preparation and the database pin.
GitHub independently confirms the final pushed heads:

```text
moda-interact-admin task/ARCH-026-ADMIN-001
  2fdbf1813a039ff8ee9e58423cc38517de5e95b9

moda-interact-workspace task/ARCH-026-ADMIN-001
  e8d5fc5dfad26941810aa21f765684440fee9bbf
```

The user-submitted publication evidence states both worktrees are clean and local task
branches match those remote refs; the remote refs independently match the supplied
commits. The stale review-time claim fields are cleared directly by this acceptance
reconciliation; no additional attempt is required.

### Reviewed Files

- `src/lib/admin/data.ts`
- `src/lib/admin/tenant-onboarding.ts`
- `tests/unit/tenant-onboarding.test.ts`
- `scripts/shopify_dashboard_test_data.py`
- `scripts/README-shopify-dashboard-test-data.md`
- `src/lib/admin/billing-controls.ts` for the Woo-without-ShopSettings dependency check
- durable Admin baseline entries in `docs/development-baseline.md`
- accepted DATABASE-001 / DATABASE-002 ancestry and Admin database gitlink
- this task Completion Report and launcher evidence
- ADMIN-002 downstream dependency contract

### Validation Reviewed

- GitHub implementation commit
  `2fdbf1813a039ff8ee9e58423cc38517de5e95b9`: exactly five authorised files.
- GitHub parent report commit
  `e8d5fc5dfad26941810aa21f765684440fee9bbf`.
- Independent focused onboarding tests: 3/3 passed.
- Independent tenant information-architecture tests: 4/4 passed.
- Independent Python syntax + CLI smoke: passed.
- Submitted Prisma generate/validate, TypeScript, targeted lint, build and diff check:
  passed.
- Submitted unit suite: 265/267 with exactly the two established translation failures.
- Submitted security residuals: confined to established
  `ARCH025-ADMIN-TEST-001` categories; source-only billing-pack baseline reproduced
  independently.
- Database gitlink unchanged from pre-task parent at accepted
  `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.

### Architecture Conformance

Conformant and accepted. Admin tenant onboarding presentation now consumes the
provider-neutral shared Shop milestone while preserving existing Shopify recovery-control
settings and the legacy schema compatibility field. Woo tenant representation no longer
depends on a fabricated Shopify settings row.

This accepted shared-onboarding read boundary is frozen for ADMIN-002; the later
international-context migration must not reopen onboarding authority.

### Follow-up

`ARCH-026-ADMIN-001` is Complete / Accepted at Attempt 1.

`ARCH-026-ADMIN-002` now has all declared dependencies satisfied
(DATABASE-002, SHOPIFY-002 and ADMIN-001) and is promoted to Ready, Attempt 0, claim
clear.

Do not start ADMIN-002 implicitly; claim it through `/moda-task ARCH-026-ADMIN-002`.
