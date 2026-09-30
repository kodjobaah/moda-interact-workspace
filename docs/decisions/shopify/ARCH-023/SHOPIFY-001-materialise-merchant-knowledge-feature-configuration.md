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
status: blocked
priority: 50
executor: copilot
claimed_at: 2026-09-30T09:59:14Z
attempt: 1
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

- [ ] Adopt accepted database and Shared revisions.
- [ ] Extend existing materialisation read to include mapping configuration.
- [ ] Add bounded Merchant Knowledge pre-validation.
- [ ] Copy every Feature mapping/configuration generically.
- [ ] Preserve existing BillingPlan reuse/concurrency behavior.
- [ ] Add focused materialisation regressions.

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

- [ ] One existing BillingPlan materialiser remains authoritative.
- [ ] New operational plan Feature configuration is copied unchanged.
- [ ] Merchant Knowledge config/pairs fail closed before materialisation.
- [ ] No plan-name-specific rules are introduced.
- [ ] Existing operational plan is not rewritten by resolver reuse.
- [ ] No merchant preference state is touched.

## Validation

- [ ] focused billing materialisation tests
- [ ] existing billing service/callback regression tests
- [ ] `npm run prisma:validate`
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin another ARCH-023 Shopify task.

## Completion Report

### Status
Blocked
### Files Changed
Task report only; no implementation files changed.
### Work Completed
Confirmed the accepted database submodule revision is present at `2eb17ee910491e8f9df82736fc0a843844415947` and the exact Shared `1.0.1` package is published with the expected registry integrity. Inspected the prepared app branch at `3ec4c6fb4e519ddcb640e03a614d442f525a630c`: it does not contain `resolveOrMaterializeBillingPlan`, any BillingPlan creation path, or a BillingPlanFeature copy path. The resolver implementation exists only in commit `1333957364903afc87bec9a9938b19d3f5b3b0d3` on `task/ARCH-017-SHOPIFY-001`, which is not merged into `main`.
### Validation Results
No implementation validation run because the required existing resolver is absent from the authorized branch. Shopify app-pricing documentation search confirmed existing Billing API subscriptions are retained until migrated; no Shopify billing behavior change is needed for this task.
### Deviations
Implementation stopped before dependency or source edits because adding or importing a resolver from another task branch would exceed this task's boundary and conflict with R2 and the out-of-scope prohibition on a new BillingPlan creation path.
### Assumptions
None.
### Unresolved Issues
The app manifest and lockfile still pin `@modainteract/moda-interact-shared` to `0.13.1`, although `1.0.1` is available; dependency adoption must occur after the resolver prerequisite is made available.
### Architectural Concerns
`ARCH-023-SHOPIFY-001` cannot extend the ARCH-017 resolver while the accepted resolver commit is absent from `main`. The ARCH-017 task branch must be merged/accepted into the base before this task is reclaimed, or `moda_architect` must explicitly revise the dependency/scope sequencing. No `Architect Review` content was changed.

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
