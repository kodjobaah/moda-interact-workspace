---
id: ARCH-017-ADMIN-001
architecture_id: ARCH-017
title: Manage dynamic features, durable MerchantPricingPlans and platform billing controls
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-18T21:25:31Z
attempt: 2
depends_on:
- ARCH-017-DATABASE-001
enables: []
created: 2026-09-18
updated: 2026-09-18
---

# ARCH-017-ADMIN-001

## Objective

Make Admin the authoritative management surface for:

- dynamic Feature catalogue definitions;
- MerchantPricingPlan supported features;
- dedicated normal recovery usage-meter handle;
- MerchantPricingPlan durability/delete restrictions;
- transactional downstream BillingPlan projection for durable plan edits;
- PlatformBillingPolicy outbound defaults;
- ShopBillingPolicyOverride terminal-message override;
- deterministic legacy UNMAPPED repair using catalogue state rather than hand-authored BillingPlan features/limits.

This is one Admin task because all work is within the existing billing administration domain and depends only on ARCH-017-DATABASE-001.

ARCH-011 is out of scope.

## Dependency gate

Do not start until ARCH-017-DATABASE-001 is accepted and the accepted database submodule commit is materialised in this task worktree.

Regenerate Prisma client before TypeScript/build validation.

## Read before editing

Read these exact current files and their focused tests:

```text
src/app/actions/merchant-pricing-plan.ts
src/lib/admin/merchant/pricing-plan.ts
src/lib/admin/merchant/pricing-plan-builder.ts
src/lib/admin/merchant/pricing-builder-payload.ts
src/lib/admin/merchant/pricing-builder-presentation.ts
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/lib/admin/unmapped-subscriptions.ts
src/app/actions/billing-unmapped-subscriptions.ts
src/lib/admin/data.ts
existing /billing page/view/drawer wiring
existing platform billing policy action/component files
existing shop billing policy override action/component files
tests/unit/*merchant-pricing*
tests/security/admin-merchant-pricing-plan.test.mjs
tests/security/admin-billing-controls.test.mjs
database/prisma/schema.prisma
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
```

Search for all imports/usages of:

```text
BillingPlanFeatureIdentifier
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
shopifyUsageEventHandle
```

Do not leave stale Admin form controls that write deleted BillingPlan fields.

## Authorized implementation surface

```text
src/app/actions/merchant-pricing-plan.ts
src/lib/admin/merchant/pricing-plan.ts
src/lib/admin/merchant/pricing-plan-builder.ts
src/lib/admin/merchant/pricing-builder-payload.ts
src/lib/admin/merchant/pricing-builder-presentation.ts
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/app/actions/billing-unmapped-subscriptions.ts
src/lib/admin/unmapped-subscriptions.ts
existing billing page/view/navigation files
existing platform/tenant billing policy Admin files
new small Feature-catalogue action/lib/component files under existing billing admin conventions
focused unit/security tests
```

Do not edit the database submodule in this task.

## Part A — Feature catalogue Admin

### 1. Add Feature catalogue section

Add a Feature catalogue to the existing billing administration surface. Prefer the current `/billing` host rather than creating a disconnected application.

Required operations for SUPER_ADMIN:

- list features;
- create feature;
- edit display name/description;
- activate/deactivate non-system-required features.

Do not implement hard delete in ARCH-017.

### 2. Create Feature validation

Server-side validation MUST use:

```ts
const FEATURE_KEY_PATTERN = /^[a-z][a-z0-9_]{0,127}$/;
```

Create requires:

```text
key            required, pattern above, globally unique
displayName    trimmed 1..255
description    optional, trimmed <= 2000
activationMode ALWAYS_ENABLED | MERCHANT_OPT_IN
```

New Admin-created Feature always has:

```text
systemRequired = false
active = true
```

Never accept `systemRequired=true` from browser input.

### 3. Feature immutability rules

For an existing Feature:

- `key` is immutable;
- `systemRequired` is immutable;
- `activationMode` is immutable in this task;
- displayName/description may change;
- non-system-required active may toggle;
- systemRequired Feature may not be deactivated.

Deactivating a non-system Feature MUST NOT delete or rewrite MerchantPricingPlanFeature, BillingPlanFeature or ShopFeaturePreference rows. `Feature.active` is the global availability gate. Reactivation restores eligibility wherever the existing mappings/preferences still permit it.

Server enforces all rules even if UI controls are disabled.

The seeded `checkout_recovery` row must display as required/system and cannot be deactivated.

## Part B — MerchantPricingPlan builder

### 4. Extend builder data/payload

Add these fields to the Admin builder payload/view model:

```ts
shopifyRecoveryUsageEventHandle: string | null;
supportedFeatureKeys: string[];
materializedAt: string | Date | null; // use the repository's normal server/client serialization form
```

Do not reuse `usageEvents[].eventHandle` for the normal recovery meter.

UI copy must clearly distinguish:

```text
Recovery usage-event handle
  -> normal paid recovery meter copied to BillingPlan.shopifyUsageEventHandle

Usage events / top-up offers
  -> existing ARCH-014 0..5 credit purchase offers
```

### 5. Meter validation

Server and client presentation validation:

```text
FREE:
  shopifyRecoveryUsageEventHandle MUST be null/blank

PAID_METERED:
  shopifyRecoveryUsageEventHandle MUST be a non-empty trimmed string
  before create/save/activation succeeds
```

Do not infer the field from top-up usage events.

### 6. Supported-feature selection

Load all active Feature rows for the builder **plus any inactive Feature already mapped to the MerchantPricingPlan being edited**.

Display system-required `checkout_recovery` as checked/read-only. Display an inactive already-mapped feature as checked/read-only with an `Inactive globally` indicator; preserve that mapping on unrelated plan saves. Admin must reactivate the Feature before changing that plan mapping.

For every save, server builds the desired feature set from database state, not trusted browser state:

```ts
const systemRequiredKeys = activeFeatures
  .filter((feature) => feature.systemRequired)
  .map((feature) => feature.key);

const requestedKeys = ...validated browser list...;
const preservedInactiveMappedKeys = existingPlanMappedFeatures
  .filter((feature) => !feature.active)
  .map((feature) => feature.key);
const desiredKeys = new Set([
  ...systemRequiredKeys,
  ...preservedInactiveMappedKeys,
  ...requestedKeys,
]);
```

Reject any requested key that:

- does not exist;
- is inactive;
- is duplicated after normalization.

Do not allow browser omission of checkout_recovery to remove it.

### 7. Create transaction

On MerchantPricingPlan create, in the existing transaction:

- create MerchantPricingPlan with `materializedAt=null`;
- create exact `MerchantPricingPlanFeature` mappings for desired Feature IDs;
- preserve existing translations/highlights/top-up usage-event behavior;
- preserve global `shopifyPlanHandle @unique` duplicate precheck and database unique constraint;
- do not create BillingPlan during normal Admin plan creation.

That last rule is important: BillingPlan remains lazily materialised by Shopify lifecycle.

## Part C — durable MerchantPricingPlan lifecycle

### 8. Durable status display

`materializedAt != null` means durable.

In list/detail UI display a clear status:

```text
Operational status: Not yet materialised
```

or

```text
Operational status: Durable since <materializedAt>
```

Do not call an inactive durable plan "deleted" or imply its handle is reusable.

### 9. Delete rule

Current delete action allows inactive paid plan deletion. Change it.

Inside the delete transaction select `materializedAt`.

Required order:

```text
if plan missing -> existing not-found behavior
if materializedAt != null -> reject:
  "This pricing plan has been materialised for operational billing and cannot be deleted. Deactivate it instead."
if FREE -> preserve existing FREE delete prohibition
if active -> preserve deactivate-first rule
otherwise -> deletion allowed
```

UI must hide or disable Delete for durable plans, but server enforcement is mandatory.

### 10. Handle uniqueness

Preserve existing database `@unique` and current Admin duplicate precheck across all MerchantPricingPlan rows, active and inactive.

Add/retain a friendly server error exactly conveying:

```text
A MerchantPricing plan with this Shopify handle already exists. Handles cannot be reused, including when the existing plan is inactive.
```

Do not filter duplicate lookup by `isActive`.

### 11. Durable field immutability

`shopifyPlanHandle` remains immutable for all plans as today.

When `materializedAt != null`, additionally reject any attempt to change `planKind` with:

```text
The plan kind cannot be changed after this pricing plan has been materialised.
```

Other existing plan-kind invariants remain.

## Part D — transactional downstream projection for durable edits

### 12. When projection is required

On create with `materializedAt=null`: no BillingPlan write.

On edit with `materializedAt=null`: no BillingPlan write.

On edit with `materializedAt!=null`: reconcile BillingPlan in the SAME transaction as MerchantPricingPlan + MerchantPricingPlanFeature changes.

### 13. Locate runtime plan

For a durable edit:

```ts
const billingPlan = await transaction.billingPlan.findUnique({
  where: { shopifyPlanHandle: existing.shopifyPlanHandle },
  include: { features: true },
});
```

If absent, abort the entire Admin save with an invariant error. Do not silently clear materializedAt and do not create a replacement BillingPlan in the edit path.

### 14. Synchronize exact operational fields

After successful MerchantPricingPlan write, update BillingPlan:

```ts
await transaction.billingPlan.update({
  where: { id: billingPlan.id },
  data: {
    name: savedMerchantPricingPlan.displayName,
    shopifyUsageEventHandle:
      savedMerchantPricingPlan.planKind === "FREE"
        ? null
        : savedMerchantPricingPlan.shopifyRecoveryUsageEventHandle!.trim(),
    includedRecoveryConversationAllowance:
      savedMerchantPricingPlan.planKind === "FREE"
        ? null
        : savedMerchantPricingPlan.includedRecoveryCredits,
    features: {
      deleteMany: {
        featureId: { notIn: desiredFeatureIds },
      },
      upsert: desiredFeatureIds.map((featureId) => ({
        where: {
          planId_featureId: {
            planId: billingPlan.id,
            featureId,
          },
        },
        create: { featureId, enabled: true },
        update: { enabled: true },
      })),
    },
  },
});
```

If Prisma nested `upsert` syntax generated by the accepted schema differs, implement the same desired-state algorithm using explicit `deleteMany` + `upsert/createMany` inside the transaction. Do not weaken the invariant.

Do NOT update:

```text
BillingPlan.active
BillingPlan.recoveryCreditPackEnabled
BillingPlan.recoveryCreditsPerPack
BillingPlan.shopifyRecoveryCreditPackEventHandle
```

Do not set `BillingPlan.active = MerchantPricingPlan.isActive`.

### 15. Removing a feature

Removing a supported Feature from a durable MerchantPricingPlan removes the corresponding BillingPlanFeature mapping in the same transaction.

Do NOT delete any `ShopFeaturePreference`. Preferences become dormant naturally.

### 16. Adding a feature

Adding a supported Feature creates/enables the BillingPlanFeature mapping in the same transaction.

Existing enabled ShopFeaturePreference becomes effective automatically where Background/Shopify evaluates it.

### 17. Toggle active/inactive

Existing `intent=toggle` changes only `MerchantPricingPlan.isActive` and existing economics override state/audit.

It MUST NOT mutate `BillingPlan.active` or delete BillingPlanFeature rows.

This permits retiring a plan from new selection without breaking existing subscribers.

## Part E — PlatformBillingPolicy / ShopBillingPolicyOverride Admin

### 18. Platform policy controls

Update existing platform billing controls to read/write:

```text
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
absoluteOutboundHardLimit
```

Server validation:

```text
defaultOutboundSoftLimit >= 1
defaultOutboundHardLimit >= 2
defaultOutboundSoftLimit <= defaultOutboundHardLimit
defaultOutboundHardLimit <= absoluteOutboundHardLimit
terminalMessageReservedSlots >= 1
terminalMessageReservedSlots < defaultOutboundHardLimit
```

Use existing SUPER_ADMIN authorization, audit and transaction patterns. Never accept platformAdminId from form data.

### 19. Shop override control

Extend current ShopBillingPolicyOverride Admin editing/view with optional:

```text
terminalMessageReservedSlots
```

Effective display uses:

```text
override value if active and non-null
otherwise PlatformBillingPolicy.terminalMessageReservedSlots
```

Validate the final effective terminal reserve is >=1 and < final effective hard limit.

Remove Admin reads/presentation that derive default outbound values from `subscription.plan.defaultOutbound*` or plan terminal slots.

## Part F — legacy UNMAPPED resolution

### 20. Remove hand-authored BillingPlan inputs

Current UNMAPPED repair allows/derives:

```text
BillingPlanFeatureIdentifier[]
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
primary shopifyUsageEventHandle chosen from top-up events
```

Remove those inputs/fallbacks.

For a known MerchantPricingPlan, repair must use catalogue data deterministically:

```text
name = MerchantPricingPlan.displayName
kind = MerchantPricingPlan.planKind
shopifyUsageEventHandle = MerchantPricingPlan.shopifyRecoveryUsageEventHandle
included allowance = paid ? includedRecoveryCredits : null
features = MerchantPricingPlanFeature featureIds
legacy credit-pack fields = false/null when a new BillingPlan must be created
```

The same transaction that first creates the BillingPlan sets `MerchantPricingPlan.materializedAt` if null.

Existing active BillingPlan is reused; inactive BillingPlan is not auto-reactivated.

No outbound limit inputs remain because those are Platform/Shop policy.

Provider contract verification remains mandatory exactly where current UNMAPPED repair already performs it.

## Required tests

### Feature catalogue security/behavior

- unauthenticated denied;
- non-SUPER_ADMIN mutation denied per existing policy;
- create valid feature succeeds;
- invalid key rejected;
- duplicate key rejected cleanly;
- key immutable;
- activationMode immutable;
- systemRequired cannot be set from browser;
- checkout_recovery cannot be deactivated;
- non-system feature can deactivate/reactivate.

### MerchantPricingPlan

- create automatically includes checkout_recovery even if browser omits it;
- optional selected features persisted;
- inactive/nonexistent newly requested feature rejected;
- globally deactivating an optional Feature preserves existing MPP/BillingPlan/preference relationships;
- unrelated plan save preserves already-mapped inactive features;
- FREE rejects recovery meter handle;
- PAID requires dedicated recovery meter handle;
- top-up usage event is not substituted for recovery meter;
- existing global Shopify-handle uniqueness includes inactive rows;
- non-durable inactive paid plan can still be deleted under existing rules;
- durable plan cannot be deleted even when inactive;
- durable plan cannot change planKind;
- deactivating durable MPP does not modify BillingPlan.active;
- reactivating does not create a second BillingPlan.

### Durable downstream synchronization

Given durable MPP + matching BillingPlan:

- add optional feature -> BillingPlanFeature created/enabled;
- remove optional feature -> BillingPlanFeature removed;
- checkout_recovery cannot be removed;
- ShopFeaturePreference is untouched on feature removal;
- displayName change updates BillingPlan.name;
- paid included credit change updates BillingPlan included allowance;
- recovery usage meter change updates BillingPlan.shopifyUsageEventHandle;
- failed/missing BillingPlan rolls back MPP edit;
- catalogue `isActive` toggle does not alter BillingPlan.active.

### Policy Admin

- platform soft/hard/terminal fields shown and validated;
- shop terminal override shown and validated against effective hard limit;
- no BillingPlan default limit field is queried/written.

### UNMAPPED repair

- no enum feature/plan-limit manual inputs;
- repair uses MPP feature mappings;
- repair uses dedicated recovery meter field;
- first repair-created BillingPlan sets materializedAt;
- unknown/inactive catalogue plan remains blocked per current repair security policy.

## Validation

Inspect current `package.json` and run declared scripts. Expected current commands:

```text
npm run prisma:generate
npm run test:unit
npm test
npm run lint
npm run format:check
npm run build
git diff --check
```

Also run focused MerchantPricingPlan, billing-control and UNMAPPED security tests independently and record results before aggregate suite.

## Stop conditions

STOP and return to moda_architect if:

- accepted DATABASE-001 does not expose the required Feature/MPPFeature/policy fields;
- implementation would add a MerchantPricingPlan/BillingPlan FK;
- Admin would need to guess the normal recovery meter from top-up offers;
- catalogue deactivate would have to disable existing BillingPlan runtime;
- a durable edit cannot be made atomic with its BillingPlan projection using the current database;
- ARCH-011 proration enters scope.

## Non-goals

- Shopify callback materialisation path;
- Background effective feature enforcement;
- merchant feature preference UI;
- new Shared contracts;
- proration.

## Acceptance criteria

- Admin can manage dynamic feature definitions without enum changes;
- every MPP always includes checkout_recovery;
- paid MPP has an explicit normal recovery usage-meter handle distinct from top-up offers;
- durable state is visible and permanent;
- durable plan deletion and planKind mutation are blocked;
- inactive handles remain globally reserved;
- durable supported-feature edits synchronize BillingPlanFeature atomically;
- catalogue deactivation does not disable existing BillingPlan runtime;
- platform/shop operational limits no longer live on BillingPlan forms/data;
- legacy UNMAPPED repair follows the same deterministic catalogue projection;
- tests/build validation pass or only architect-approved unrelated baseline failures remain.

## Completion protocol

Set task to `review`. Completion Report must include exact implementation/parent commits, validation output, physical worktree evidence and accepted DATABASE-001 revision.

## Completion Report

### Implementation

- Added SUPER_ADMIN Feature catalogue create/edit/activation controls with server-side key, description, activation-mode, system-required, immutability, and checkout-recovery safeguards.
- Extended MerchantPricingPlan administration with the dedicated recovery meter handle, dynamic supported-feature mappings, materialization status, paid/free validation, inactive-feature preservation, and durable plan-kind/delete restrictions.
- Added same-transaction durable BillingPlan projection for operational name, recovery meter, allowance, and feature mappings without mutating BillingPlan lifecycle or credit-pack fields.
- Updated platform and shop billing controls for PlatformBillingPolicy and terminal-message overrides.
- Reworked legacy UNMAPPED repair to use MerchantPricingPlan catalogue state and the dedicated recovery meter rather than hand-authored enum/limit/top-up inputs.

### Commits and Dependency

- implementation commit: `07817815134385202ab22519dc2bbcb99b6f3c69` (`feat(admin): manage durable billing catalogue and policies`);
- implementation branch: `task/ARCH-017-ADMIN-001`, pushed to `origin/task/ARCH-017-ADMIN-001`;
- accepted DATABASE-001 submodule revision materialized in the implementation worktree: `9921b273642599e5cf255565d73ebad507f71ee4`;
- no database submodule files were edited by this task.

### Validation

- `npm run prisma:generate`: passed;
- `npm run prisma:validate`: passed;
- `npm run test:unit -- --test-name-pattern='merchant-pricing|billing|feature'`: task-focused assertions passed; two unrelated existing translation assertions failed in `merchant-pricing-translation-workbook.test.ts` and `merchant-pricing-translations.test.ts`;
- `npm test`: completed with existing baseline failures in shared-version/i18n/security fixture expectations and source-contract checks outside the ARCH-017 implementation; no task implementation runtime failure was identified;
- `npm run lint`: existing baseline errors in promotion reactivation components and warnings in unrelated files; no ARCH-017 changed-file lint error reported;
- `npm run build`: passed TypeScript and production build; only existing BullMQ optional dependency/critical-dependency warnings;
- `git diff --check`: passed for the implementation commit.

### Physical Worktree Evidence

- canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-017-ADMIN-001`;
- parent branch: `task/ARCH-017-ADMIN-001`;
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-017-ADMIN-001`;
- implementation branch: `task/ARCH-017-ADMIN-001`;
- shared workspace checkout switched/mutated for task work: no;
- another task worktree reused: no;
- recursive submodule sync/update: passed;
- recorded database submodule commit: `9921b273642599e5cf255565d73ebad507f71ee4`;
- launcher claim commit: `67c03781199ff3482611c832afa898419eb2f2c6`;
- executor and claim timestamp cleared for review; no main branch modified.

Task status is `review`; return control to `moda_architect`.


## Architect Review — Attempt 1 — Changes Requested

### Decision

**Changes Requested — return to Ready**

Architect review covered implementation commit `07817815134385202ab22519dc2bbcb99b6f3c69`, parent Completion Report commit `062bb01c`, and the returned ARCH-017 database dependency state. The review is functionality-led: focused and aggregate test results are supporting evidence, but the decision below is based on production-path behaviour against the task contract.

Most of the implementation is functionally aligned with ARCH-017. In particular:

- Feature catalogue mutation is data-driven and server-authorized;
- Feature deactivation does not rewrite MerchantPricingPlanFeature, BillingPlanFeature or ShopFeaturePreference rows;
- normal MerchantPricingPlan creation leaves `materializedAt=null` and does not eagerly create BillingPlan;
- durable edits project name, normal recovery meter, included allowance and exact BillingPlanFeature state inside the same transaction without mutating `BillingPlan.active`;
- platform/shop billing policy writes use PlatformBillingPolicy / ShopBillingPolicyOverride rather than BillingPlan-owned limits;
- UNMAPPED repair uses MerchantPricingPlan catalogue state, the dedicated recovery usage-meter handle and MerchantPricingPlanFeature mappings, preserves provider verification, and does not auto-reactivate an inactive BillingPlan.

Attempt 2 is required for the functional gaps below.

### 1. MerchantPricingPlan builder does not expose the authoritative Feature catalogue

The billing page loads the full Feature catalogue with `getFeatureCatalogue()`, but those rows are only rendered by `FeatureCatalogue`. They are not passed to `MerchantPricingPlanDrawer` / `MerchantPricingPlanBuilder`.

The builder currently constructs its selectable feature list only from:

```text
plan.features
+
cataloguePlans[*].features
```

This means a newly created active optional Feature that is not yet mapped to any MerchantPricingPlan is absent from the builder and cannot be selected for its first plan through Admin.

There is a second symptom in the same code path: initial `supportedFeatureKeys` filters current mappings by `feature.active`. Therefore an inactive optional Feature already mapped to the edited plan is rendered disabled but unchecked, even though ARCH-017 requires it to remain visibly checked/read-only with `Inactive globally` while the server preserves the mapping.

Required correction:

- pass the authoritative Feature catalogue into the plan drawer/builder;
- show every active Feature;
- additionally show any inactive Feature already mapped to the plan being edited;
- initialize current mapped keys without dropping inactive mappings;
- keep system-required features checked/read-only;
- keep inactive mapped optional features checked/read-only with the existing `Inactive globally` indicator;
- do not weaken the existing server-side desired-set reconstruction or inactive/new-key rejection.

A new active Feature must be selectable for its first MerchantPricingPlan without first being mapped to another plan.

### 2. Paid-plan activation bypasses the dedicated recovery-meter requirement

`intent=toggle` can reactivate an inactive `PAID_METERED` MerchantPricingPlan without validating `shopifyRecoveryUsageEventHandle`.

This is a real reachable state because the accepted DATABASE-001 migration intentionally did not infer/backfill the new normal recovery meter for existing development MerchantPricingPlan rows.

The task contract requires:

```text
PAID_METERED:
  shopifyRecoveryUsageEventHandle MUST be non-empty
  before create/save/activation succeeds
```

Required correction:

- when `intent=toggle` is activating an inactive `PAID_METERED` plan, reject activation if `shopifyRecoveryUsageEventHandle` is null/blank;
- keep deactivation unaffected;
- do not infer the handle from MerchantPricingUsageEvent/top-up offers;
- retain existing economics activation checks.

A focused regression should cover an inactive paid plan with no dedicated recovery meter remaining inactive after an activation attempt.

### 3. Durable status/delete behaviour is not represented correctly in the Admin UI

Server-side delete protection is correct, but the required durable lifecycle is not visible in the plan catalogue and the Delete control only considers `plan.isActive`.

Current consequences:

- there is no displayed `Operational status: Not yet materialised` / `Operational status: Durable since ...` state;
- an inactive durable paid plan exposes an enabled Delete button even though the server must always reject that deletion.

Required correction:

- display the operational durability state for each MerchantPricingPlan;
- disable or hide Delete whenever `materializedAt != null`, regardless of `isActive`;
- retain the existing deactivate-first rule for non-durable paid plans;
- use durable-specific UI copy so an inactive durable plan is not presented as deletable or as having a reusable handle.

Server enforcement must remain unchanged.

### 4. Shop terminal-message policy display does not show the effective value

`TenantBillingControls` correctly computes effective soft/hard limits, but terminal reserve currently renders:

```text
active override value
OR
"inherit"
```

The ARCH-017 contract requires the effective display to be:

```text
active non-null shop override
OR
PlatformBillingPolicy.terminalMessageReservedSlots
```

Required correction:

- compute and display the effective terminal reserve using the active override when present, otherwise the platform value already returned in `controls.platform`;
- expired overrides must fall back to the platform value;
- replace remaining shop-control wording that says numeric values inherit "plan defaults" with "platform defaults" so Admin no longer presents BillingPlan as the owner of these limits.

For this narrow wording correction, Attempt 2 is authorized to update the existing English billing-control locale entry in `src/i18n/locales/en.json` in addition to the already-authorized billing-control component files.

### Validation scope for Attempt 2

Keep validation functionality-focused. At minimum:

```text
npm run prisma:generate
npm run prisma:validate
npm run build
focused MerchantPricingPlan / billing-control tests covering the corrections
git diff --check
```

Also rerun any existing focused security tests directly affected by changed files. Do not expand Attempt 2 into unrelated translation/lint/security baseline cleanup. Existing unrelated baseline failures remain non-blocking unless the Attempt 2 changes worsen them.

### State transition

```yaml
ARCH-017-ADMIN-001:
  status: ready
  attempt: 1
  executor: null
  claimed_at: null
```

There is **no Attempt 2 yet**. Attempt 2 begins only when the normal task launcher claims the Ready task.
