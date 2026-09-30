---
id: ARCH-023-SHOPIFY-001
architecture_id: ARCH-023
title: Materialise Merchant Knowledge plan-feature configuration
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: copilot
claimed_at: 2026-09-30T12:32:00Z
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables:
  - ARCH-023-SHOPIFY-003
  - ARCH-023-SHOPIFY-004
created: 2026-09-29
updated: 2026-09-30
---

# Materialise Merchant Knowledge plan-feature configuration

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing ARCH-017 lazy `MerchantPricingPlan -> BillingPlan` materialisation path so generic `MerchantPricingPlanFeature.configuration` is copied unchanged into the corresponding `BillingPlanFeature.configuration`.

For the `merchant_knowledge` mapping, validate the published C2 configuration and its selected `allowedSourceTypes` against the current active Purpose/Data Format catalogue before a new operational BillingPlan is created.

Do not create a second BillingPlan materialisation path.

## Context

ARCH-017 already defines one operational resolver conceptually named:

```text
resolveOrMaterializeBillingPlan(planHandle)
```

which:

- reuses an existing operational BillingPlan;
- otherwise loads the active MerchantPricingPlan with Feature mappings;
- validates catalogue materialisation invariants;
- creates one BillingPlan;
- projects every MerchantPricingPlan Feature mapping into BillingPlanFeature;
- sets `MerchantPricingPlan.materializedAt`;
- is concurrency-safe by unique `shopifyPlanHandle`.

ARCH-023 adds generic JsonB configuration to both mapping tables.

Admin owns later durable MerchantPricingPlan edits and synchronises an already-materialised BillingPlan in that same Admin transaction. This task changes only **first materialisation**.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

app/services/billing/billing.service.ts
app/services/billing/merchant-pricing-plan-validation.ts   # optional bounded helper

tests/unit/services/billing.service.test.ts
tests/integration/billing-plan-materialisation.integration.test.ts  # if current harness has/needs one
```

If current main has moved the accepted ARCH-017 resolver into another existing billing helper, modify that existing helper instead of creating a duplicate resolver.

## Out of Scope

- Admin plan editing.
- new BillingPlan creation path outside the existing resolver.
- plan-name-specific Merchant Knowledge logic.
- subscription-category activation.
- merchant knowledge source CRUD.
- Store Category UI.
- R2.
- Background processing.
- Commerce lookup.
- ShopFeaturePreference mutation.
- retroactive automatic repair of already-existing BillingPlan configuration.

## Requirements

### R1 — adopt exact accepted dependencies

Before implementation:

1. advance the repository `database` gitlink to the accepted/merged `ARCH-023-DATABASE-001` revision;
2. do not edit files inside the database submodule;
3. pin `@modainteract/moda-interact-shared` to exactly `1.0.1`, the Architect-Accepted revision published by `ARCH-023-SHARED-002`; do not substitute a range, `latest`, workspace link or later release without architect reconciliation;
4. regenerate Prisma Client using the existing repository script.

If either accepted dependency is unavailable, STOP.

### R2 — preserve the single ARCH-017 materialisation resolver

Use the existing ARCH-017 resolver. The canonical method name remains:

```ts
resolveOrMaterializeBillingPlan(planHandle: string)
```

If the accepted implementation has factored it into a helper, keep one logical resolver and one transaction path.

Do not implement a new ARCH-023-specific `materializeMerchantKnowledgePlan`.

### R3 — load generic feature configuration during new materialisation

When the resolver loads the source `MerchantPricingPlan`, include every mapping with:

```text
MerchantPricingPlanFeature.featureId
MerchantPricingPlanFeature.configuration
MerchantPricingPlanFeature.feature:
  key
  active
  activationMode
  systemRequired
```

Do not load only Feature ids.

### R4 — validate the Merchant Knowledge mapping before creating a new BillingPlan

When no operational BillingPlan exists and the source MerchantPricingPlan contains Feature:

```text
feature.key = merchant_knowledge
```

require exactly one mapping.

Parse that mapping's `configuration` with:

```text
MerchantKnowledgeFeatureConfigurationSchema
```

Then load the active global compatibility catalogue:

```text
MerchantKnowledgePurpose.active = true
MerchantKnowledgeDataFormat.active = true
MerchantKnowledgePurposeDataFormat exists
```

Require every configured:

```text
(purposeKey, dataFormatKey)
```

in `allowedSourceTypes` to resolve to one active compatibility row.

If C2 parse fails or any pair is missing/inactive:

```text
return INVALID_CATALOGUE_PLAN
reason = INVALID_MERCHANT_KNOWLEDGE_CONFIGURATION
```

Do not create BillingPlan/BillingPlanFeature rows.
Do not silently remove the invalid source type.
Do not substitute default limits/source types.

This is pre-validation of source catalogue data; the actual feature-copy loop remains generic.

### R5 — generic copy loop

When creating the new BillingPlan, create every `BillingPlanFeature` from the source mapping exactly as:

```text
planId        = newly created BillingPlan.id
featureId     = source.featureId
enabled       = true
configuration = source.configuration
```

Do not branch on Feature key while copying.

The JSON value must be semantically identical to the source Prisma Json value. Do not add/remove/reorder contract fields in application code.

### R6 — preserve existing BillingPlan reuse semantics

If an operational BillingPlan already exists for the handle:

- preserve its current `BillingPlanFeature` rows/configuration;
- do not overwrite it from current MerchantPricingPlan merely because ARCH-023 exists;
- preserve the accepted ARCH-017 inactive-plan behavior;
- preserve the accepted `materializedAt` repair behavior.

Later Admin durable-plan save owns catalogue -> existing BillingPlan synchronisation.

### R7 — preserve activation/sync semantics

Existing callers:

```text
prepareFreeActivation
preparePaidActivation
syncSubscription
```

continue to use the one resolver.

Do not change:

```text
pending plan timing
end-of-cycle plan-change semantics
BillingPeriod semantics
recovery-credit semantics
onboarding milestone semantics
```

except where tests need to prove newly materialised feature configuration is present.

### R8 — configuration does not create merchant preference

The materialisation transaction must not:

```text
insert/update/delete ShopFeaturePreference
```

`merchant_knowledge` uses `ALWAYS_ENABLED`, but preference state remains a separate existing concept for other features.

### R9 — exact tests

Add/extend tests proving:

```text
new BillingPlan copies arbitrary non-MK feature configuration unchanged
new BillingPlan copies valid merchant_knowledge C2 configuration unchanged
merchant_knowledge configuration malformed -> INVALID_CATALOGUE_PLAN
merchant_knowledge allowedSourceType with inactive/missing global pair -> INVALID_CATALOGUE_PLAN
no BillingPlan/BillingPlanFeature rows committed on invalid C2/catalogue state
copy loop does not branch on Free/Starter/Growth
existing BillingPlan configuration is not overwritten by resolver reuse
concurrent materialisation still produces one BillingPlan
no ShopFeaturePreference write
```

Existing ARCH-017 billing-materialisation tests must remain green.

## Work Items

- [x] Adopt accepted database and Shared revisions.
- [x] Extend existing materialisation read to include mapping configuration.
- [x] Add bounded Merchant Knowledge pre-validation.
- [x] Copy every Feature mapping/configuration generically.
- [x] Preserve existing BillingPlan reuse/concurrency behavior.
- [x] Add focused materialisation regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-001
@modainteract/moda-interact-shared/merchant-knowledge
```

Writes existing operational tables only through the accepted materialiser:

```text
BillingPlan
BillingPlanFeature
MerchantPricingPlan.materializedAt
```

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

## Enables

- `ARCH-023-SHOPIFY-003`
- `ARCH-023-SHOPIFY-004`

## Acceptance Criteria

- [x] One existing BillingPlan materialiser remains authoritative.
- [x] New operational plan Feature configuration is copied unchanged.
- [x] Merchant Knowledge config/pairs fail closed before materialisation.
- [x] No plan-name-specific rules are introduced.
- [x] Existing operational plan is not rewritten by resolver reuse.
- [x] No merchant preference state is touched.

## Validation

- [x] focused billing materialisation tests
- [x] existing billing service/callback regression tests
- [x] `npm run prisma:validate`
- [x] `npm run typecheck`
- [ ] `npm run lint` (run; 17 errors are in unrelated files, changed-file lint passes)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin another ARCH-023 Shopify task.

## Completion Report

### Status
Review
### Files Changed
Implementation commit `787b62a5c27c6d732503c02476eb094ae5258ffa` changes:

- `app/services/billing/billing.service.ts`
- `tests/unit/services/billing.service.test.ts`

The database gitlink and exact Shared `1.0.1` dependency were already present in the prepared baseline and were not changed.
### Work Completed
Implemented attempt 2 against the prepared canonical app baseline, which includes the accepted ARCH-017 `resolveOrMaterializeBillingPlan` resolver. The launcher confirmed the accepted database revision `2eb17ee910491e8f9df82736fc0a843844415947`, exact Shared `1.0.1`, synchronized implementation branch, and initialized recursive submodule.

The existing resolver now loads feature configuration and validates a single `merchant_knowledge` mapping with `MerchantKnowledgeFeatureConfigurationSchema` and the active Purpose/Data Format compatibility catalogue before creating the operational BillingPlan. Invalid or duplicate Merchant Knowledge mappings return `INVALID_CATALOGUE_PLAN` with reason `INVALID_MERCHANT_KNOWLEDGE_CONFIGURATION` before plan creation. The existing generic feature projection copies each mapping's configuration unchanged; reuse of an existing operational plan remains unchanged.

Added regressions for generic and Merchant Knowledge configuration projection, malformed configuration, missing active compatibility, duplicate mappings, existing-plan reuse, and absence of ShopFeaturePreference writes. The copy loop remains generic and no plan-name-specific rules or new materialisation path were added.

Launcher claim evidence: attempt 2, executor `copilot`, claimed at `2026-09-30T12:32:00Z`, claim commit `27532f57e275d451cdba7c514721031bc4292487` pushed. Implementation commit `787b62a5c27c6d732503c02476eb094ae5258ffa` is pushed to `origin/task/ARCH-023-SHOPIFY-001`; implementation worktree is clean.
### Validation Results
Passed: focused billing materialisation and billing callback regression tests (247 tests); `npm run prisma:validate`; `npm run typecheck`; changed-file lint; `npm run build` (which runs `npm run prisma:generate`); changed-file diagnostics; and `git diff --check`.

Full `npm run lint` was run but reports 17 errors in unrelated files. No changed-file lint or diagnostic errors were reported.
### Deviations
No scope deviations. No source changes were needed in the database submodule or dependency manifests because the prepared baseline already had the accepted database and exact Shared revisions.
### Assumptions
The launcher-prepared canonical app baseline is authoritative for the accepted ARCH-017 integration; it contains the single resolver required by R2.
### Unresolved Issues
Repository-wide lint remains red for 17 unrelated errors; the changed files pass focused lint and diagnostics.
### Architectural Concerns
None identified in the implemented scope. The pre-existing Attempt 1 `Architect Review` and Developer Override were left unchanged.

## Architect Review

### Review Status
Blocked

### Review Notes

Attempt 1 is correctly blocked before implementation. The supplied prepared Shopify
baseline at `3ec4c6fb4e519ddcb640e03a614d442f525a630c` does not contain the
ARCH-017 `resolveOrMaterializeBillingPlan(...)` resolver, a BillingPlan creation path,
or the BillingPlanFeature projection path that this task is explicitly required to
extend. Implementing or copying that missing resolver inside ARCH-023-SHOPIFY-001 would
violate R2 and would broaden this task into ownership of the earlier ARCH-017 capability.

The blocker is therefore an integration/coordination prerequisite, not a defect in an
ARCH-023 implementation. No application source change was required or authorised in this
attempt.

The durable ARCH-017 coordination state must also be reconciled before its branch is used
as a prerequisite. The current workspace's ARCH-017 parent architecture and later
SHOPIFY-002/SHOPIFY-003 records describe ARCH-017-SHOPIFY-001 as Complete, while the
individual authoritative ARCH-017-SHOPIFY-001 task file still says `status: ready`,
`attempt: 0` and contains no Completion Report or Architect Review. Do not treat
`1333957364903afc87bec9a9938b19d3f5b3b0d3` as merge-authorised solely because the
implementation exists on `task/ARCH-017-SHOPIFY-001`; first recover/reconcile the durable
acceptance record for that task.

### Reviewed Files

- `docs/decisions/shopify/ARCH-023/SHOPIFY-001-materialise-merchant-knowledge-feature-configuration.md`
- `docs/decisions/shopify/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`
- `docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md`
- `docs/decisions/shopify/ARCH-017/SHOPIFY-001-lazy-billing-plan-materialisation-and-feature-preferences.md`
- `docs/decisions/shopify/ARCH-017/SHOPIFY-002-callback-onboarding-milestone-decoupling.md`
- `docs/decisions/shopify/ARCH-017/SHOPIFY-003-current-billing-period-plan-projection.md`
- `moda-interact/app/services/billing/` and current billing-related tests for the required resolver/materialisation path
- `moda-interact/package.json` and `moda-interact/package-lock.json`

### Validation Reviewed

- The repository agent reported `git diff --check` passing with no implementation files changed.
- Source inspection of the supplied app baseline found no `resolveOrMaterializeBillingPlan` implementation and no current BillingPlan/BillingPlanFeature materialisation path to extend.
- The current app manifest/lockfile still declare `@modainteract/moda-interact-shared` `0.13.1`; exact `1.0.1` adoption remains required by this task after the prerequisite baseline is available.
- Implementation tests were not required for this blocked attempt because implementation correctly stopped before application/dependency edits.

### Architecture Conformance

The stop is architecture-conformant. ARCH-023-SHOPIFY-001 must extend the one existing
ARCH-017 materialiser and must not recreate it. The task remains Blocked until the
canonical Shopify base used by `/moda-task` contains an architect-accepted ARCH-017
resolver/lifecycle baseline. SHOPIFY-002 remains independently executable because its
declared dependencies are satisfied and it does not depend on SHOPIFY-001.

### Follow-up

1. Reconcile the authoritative ARCH-017-SHOPIFY-001 task record with the actual branch/review history. If commit `1333957364903afc87bec9a9938b19d3f5b3b0d3` was not architect-accepted, submit that task for its required review rather than merging it implicitly.
2. Through the normal developer final-integration workflow, integrate the accepted ARCH-017 Shopify lifecycle chain into `moda-interact` so the base used for new task preparation contains `resolveOrMaterializeBillingPlan(...)` and the later accepted ARCH-017 Shopify corrections. Do not copy/cherry-pick the resolver as an ARCH-023 implementation shortcut.
3. After that integration is visible on the canonical base, return to `moda_architect` for blocker clearance. The architect should verify the resolver is present in the base and then change this same task `blocked -> ready`; Attempt 1 remains preserved until the next claim increments it to Attempt 2.
4. On the reclaimed ARCH-023 attempt, adopt exact Shared `1.0.1`, regenerate Prisma Client, and implement only this task's configuration-copy/pre-validation delta.
5. Keep ARCH-023-SHOPIFY-003 and ARCH-023-SHOPIFY-004 gated on SHOPIFY-001 completion. Do not start either while this blocker remains.

## Developer Override

### Decision
Reopened on 2026-09-30 by explicit developer request: `/moda_developer_update ARCH-023-SHOPIFY-001 reopen`.

### Previous Attempt
Attempt 1 is the prior attempt. There is no previously accepted attempt; Attempt 1 ended Blocked. The existing Architect Review remains unchanged and records the missing accepted ARCH-017 resolver/base integration prerequisite.

### Reason
The developer explicitly requested reopening; no further reason was supplied. This override changes workflow state only and does not claim that the Architect Review blocker has been cleared. No implementation work was performed and no new attempt was claimed.

### Downstream Dependency Reconciliation
`ARCH-023-SHOPIFY-003` and `ARCH-023-SHOPIFY-004` remain `pending` because they depend on SHOPIFY-001, which is not Complete. Both were already pending, so no downstream status regression was needed. `ARCH-023-SHOPIFY-002` remains Complete and independent of SHOPIFY-001; its task record was inspected and left untouched. `ARCH-023-SHOPIFY-005` remains pending behind SHOPIFY-004 and was left untouched.
