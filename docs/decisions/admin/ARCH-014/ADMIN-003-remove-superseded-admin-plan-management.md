---
id: ARCH-014-ADMIN-003
architecture_id: ARCH-014
title: Remove superseded legacy Admin BillingPlan catalogue and mutation surface
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-ADMIN-002
enables:
- ARCH-014-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-15
---

# ARCH-014-ADMIN-003

## Objective

After `ARCH-014-ADMIN-002` has replaced the Admin `view=plans` implementation with the self-contained `MerchantPricingPlan` catalogue, remove the legacy **Admin BillingPlan plan-catalogue/editor/mutation/read-model code that has become unreachable solely because of ARCH-014**.

This is a post-refactor dead-code removal task. It MUST NOT delete or change operational billing database schema/state, subscription runtime behaviour, billing controls that remain live, recovery-credit purchase handling, billing ledger handling, or Shopify subscription management.

## Binding deletion boundary

This task removes only the superseded Admin plan-management surface. It does **not** mean that the durable `BillingPlan` model or other pre-ARCH-014 operational billing objects are obsolete.

### Existing database/runtime objects that MUST remain unchanged

Do not edit or delete any Prisma model, enum, migration, database script, generated ERD or durable row related to:

```text
BillingPlan
BillingPlanFeature
BillingEconomicsSnapshot
BillingUpgradeEconomicsEdge
PlatformBillingPolicy
BillingAuditEvent
```

Do not create a database migration in this task.

### Existing Admin operational economics/control code that MUST remain

Preserve these files and their live behaviour unless a build-only import path adjustment caused by deletion is strictly required:

```text
src/app/actions/billing-economics.ts
src/lib/admin/billing-economics.ts
src/lib/admin/billing-economics-validation.ts
src/lib/admin/billing-plan-guardrail.ts
src/lib/admin/upgrade-economics-guardrail.ts
src/components/admin/billing-controls.tsx
tests/security/admin-billing-economics.test.mjs
tests/unit/billing-economics-validation.test.ts
tests/unit/upgrade-economics-guardrail.test.ts
```

These still back the existing operational `controls` view. Do not migrate them to ARCH-014 and do not delete them merely because ARCH-014 has a new portfolio calculator.

If one of the preserved files becomes demonstrably unreachable for reasons outside the exact legacy plan-management deletion below, STOP and return that evidence to `moda_architect`; do not widen this task.

## Required preflight reference gate

Run this task only after accepted `ARCH-014-ADMIN-002` is present in the implementation worktree.

Before deleting anything, prove that the new plans view is already MerchantPricing-owned:

```text
src/app/(protected)/billing/page.tsx
```

must satisfy all of these:

```text
imports/uses getMerchantPricingPlans (or exact ADMIN-002 accepted equivalent)
imports/uses MerchantPricingPlanCatalog
opens MerchantPricingPlanDrawer for register/select plan
DOES NOT import/use getBillingPlans
DOES NOT import/use getBillingPlanById
DOES NOT import/use getBillingPlanEconomics for view=plans
DOES NOT import/use BillingPlanCatalog
DOES NOT import/use BillingPlanDrawer
```

If any legacy plans-view dependency above is still live, STOP. Do not delete files and do not compensate by reimplementing ADMIN-002 in this cleanup task.

Then search all current Admin source/tests for the candidate legacy modules/symbols listed below. Expected references are limited to the candidate legacy cluster itself, `billing-drawers.tsx` legacy drawer imports/export, and tests that this task explicitly deletes/updates. Any other runtime-source consumer is unexpected: STOP and return the exact path/symbol to `moda_architect` before deletion.

Use repository-root commands equivalent to:

```bash
rg -n 'billing-plan-catalog|BillingPlanCatalog|PlanForm|BillingPlanDrawer|mutateBillingPlanAction|getBillingPlans\(|getBillingPlanById\(|getBillingPlanEconomics\(|billing-plan-mutation|billing-plan-audit|billing-plan-validation' src tests
```

## Files that MUST be deleted after the preflight gate passes

Delete these exact legacy files:

```text
src/app/actions/billing-plan.ts
src/components/admin/billing-plan-catalog.tsx
src/components/admin/billing-plan-economics-presentation.ts
src/lib/admin/billing-plan.ts
src/lib/admin/billing-plan-audit.ts
src/lib/admin/billing-plan-mutation.ts
src/lib/admin/billing-plan-validation.ts
tests/security/admin-billing-plan.test.mjs
tests/unit/billing-plan-economics-presentation.test.mjs
```

Do not replace these files with stubs, re-exports, compatibility aliases or wrappers. Their removal is intentional.

## `billing-drawers.tsx` exact cleanup

Edit:

```text
src/components/admin/billing-drawers.tsx
```

Remove only the obsolete BillingPlan drawer surface:

```text
import type { BillingPlanRow } from "@/lib/admin/billing-plan";
import { PlanForm } from "./billing-plan-catalog";
export function BillingPlanDrawer(...)
```

Preserve without semantic changes:

```text
DetailList
RecoveryCreditPurchaseDrawer
BillingEventDrawer
```

Preserve their existing close-link/filter behaviour and receipt/provider diagnostics.

## Progressive-disclosure test migration

Edit, do not delete:

```text
tests/security/admin-billing-progressive-disclosure.test.mjs
```

Update only assertions invalidated by ARCH-014 plan-view replacement.

The test must now assert that:

1. `view === "plans"` loads the accepted ADMIN-002 MerchantPricing list reader, not `getBillingPlans()`;
2. selected plan detail uses the MerchantPricing reader/id, not `getBillingPlanById()`;
3. the plans view renders `MerchantPricingPlanCatalog`;
4. register/selected plan uses `MerchantPricingPlanDrawer`;
5. the page contains no `BillingPlanCatalog` or `BillingPlanDrawer` reference;
6. overview/packs/events/controls progressive disclosure assertions remain intact;
7. the existing controls-view security assertion remains, but it must no longer read the deleted `tests/security/admin-billing-plan.test.mjs`; use the accepted ARCH-014 Admin security test (`tests/security/admin-merchant-pricing-plan.test.mjs`) for the plan mutation/authentication assertion and continue to assert the controls mutation path independently.

Do not weaken unrelated progressive-disclosure/security assertions merely to make the suite pass.

## Admin i18n dead-key cleanup

The old plan catalogue/economics presentation contains translation keys that may become dead after deletion. Remove only keys that are now genuinely unreferenced.

Candidate legacy key set is the union of string keys formerly used by the deleted UI files, including:

```text
billing.capacityGap
billing.confirmUsageChange
billing.createPlan
billing.displayName
billing.editPlanAction
billing.feature.*
billing.features
billing.guardrailBlocked
billing.guardrailCode
billing.guardrailCurrencyMismatch
billing.guardrailInvalidTopUpConfiguration
billing.guardrailInvalidUpgradeEdge
billing.guardrailInvalidUsagePricing
billing.guardrailMissingPlanEvidence
billing.guardrailMissingTopUpEvidence
billing.guardrailPass
billing.hardLimit
billing.includedRecoveryAllowance
billing.kind
billing.noTopUpPath
billing.noUpgradeEdge
billing.noUpgradeEdgeTitle
billing.planHandle
billing.premium
billing.recoveryCreditPackEnabled
billing.recoveryCreditPackEventHandle
billing.recoveryCreditPackHelp
billing.recoveryCreditPackRateHelp
billing.recoveryCreditsPerPack
billing.registerPlanAction
billing.requiredPackUnits
billing.requiredPremium
billing.savePlan
billing.softLimit
billing.stayAndTopUps
billing.terminalSlots
billing.topUpPath
billing.upgradeCost
billing.upgradeEconomics
billing.usageHandle
billing.verifiedShopifyEvidence
```

Some generic keys from the old components (`billing.active`, `billing.inactive`, `billing.activate`, `billing.deactivate`, `billing.reason`, `billing.reasonPlaceholder`, `billing.tab.plans`, `billing.plansDescription`, `billing.pass`, `billing.fail`, `billing.unverified`) may still be used by ARCH-014 or other Admin views. **Do not remove any key based only on this candidate list.**

For each candidate key:

1. search remaining `src` and `tests`, excluding `src/i18n/locales/en.json` and `src/i18n/required-keys.ts`;
2. if at least one live reference remains, retain the key;
3. if zero live references remain, remove it from both:
   - `src/i18n/locales/en.json`
   - `src/i18n/required-keys.ts`
4. keep JSON valid and keep required-key validation passing.

Do not rename a live key as part of cleanup. New ARCH-014 copy/keys belong to ADMIN-002.

## No cleanup of historical architecture evidence

Do not delete or rewrite completed ARCH-010/ARCH-011 architecture/task/Completion Report history merely because source code is now superseded. Historical documents remain evidence of the implementation sequence.

Do not remove existing migrations or baseline schema artifacts.

## Required tests

At minimum prove:

1. all exact legacy files in the required deletion list are absent;
2. `BillingPlanDrawer`, `BillingPlanCatalog`, `PlanForm`, `mutateBillingPlanAction`, `getBillingPlans`, `getBillingPlanById` and `getBillingPlanEconomics` are absent from the active `/billing?view=plans` implementation;
3. MerchantPricing plan list/register/edit flow from ADMIN-002 remains present;
4. recovery-pack and billing-event drawers still exist and their existing focused tests pass;
5. controls view still imports/uses the preserved billing-economics action path;
6. `admin-billing-economics.test.mjs`, `billing-economics-validation.test.ts` and `upgrade-economics-guardrail.test.ts` still pass;
7. `admin-billing-progressive-disclosure.test.mjs` passes with MerchantPricing assertions;
8. dead Admin translation keys removed by this task are absent from both catalogue and required-key list;
9. retained translation keys still satisfy required-key/catalogue validation;
10. no Prisma schema/migration/database file is changed by this task.

## Validation

Inspect `package.json` and run the repository-declared commands required by the accepted ADMIN-002 baseline. At minimum run:

```bash
rg -n 'billing-plan-catalog|BillingPlanCatalog|PlanForm|BillingPlanDrawer|mutateBillingPlanAction|getBillingPlans\(|getBillingPlanById\(|getBillingPlanEconomics\(|billing-plan-mutation|billing-plan-audit|billing-plan-validation' src tests || true

rg -n 'MerchantPricingPlanCatalog|MerchantPricingPlanDrawer|getMerchantPricingPlans' 'src/app/(protected)/billing/page.tsx' src/components/admin src/lib/admin

node --test tests/security/admin-billing-progressive-disclosure.test.mjs
node --test tests/security/admin-billing-economics.test.mjs
npm test
npm run typecheck
npm run lint
npm run build
git diff --check
```

If the repository uses different exact script names, inspect `package.json` and use those declared scripts; do not invent scripts.

Also prove the task did not touch database/schema files:

```bash
git diff --name-only <attempt-base>...HEAD | rg '(^|/)(prisma|migrations|database)/'
```

Expected result for the database/schema check: **no matches**. Use the launcher's recorded attempt base/parent rather than inventing a commit hash.

## Acceptance criteria

The task is Complete only when all are true:

- accepted ADMIN-002 MerchantPricing plans flow remains functional;
- all nine required legacy files are deleted, not stubbed;
- obsolete `BillingPlanDrawer` code/imports are removed from `billing-drawers.tsx`;
- no unexpected runtime consumer of the deleted legacy plan-management surface exists;
- operational economics/controls files explicitly listed above remain present and passing;
- no existing database table/model/migration is modified or deleted;
- progressive-disclosure/security tests describe the new MerchantPricing plan flow;
- dead Admin i18n keys are removed using the zero-live-reference rule;
- full required validation introduces no task-caused regression.

## Stop conditions

STOP and return evidence to `moda_architect` without widening the task if:

- ADMIN-002 has not fully removed a runtime `/billing?view=plans` dependency on the legacy BillingPlan catalogue/editor;
- any required-delete candidate has a live runtime consumer outside the explicitly obsolete cluster;
- cleanup would require modifying Prisma schema/migrations or deleting durable BillingPlan/economics data;
- cleanup would require deleting/changing the existing operational billing economics controls;
- a Shopify merchant-app cleanup gap is discovered (that belongs to `ARCH-014-SHOPIFY-001`, not this Admin task).

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
