---
id: ARCH-023-ADMIN-001
architecture_id: ARCH-023
title: Author Merchant Knowledge plan entitlement
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Author Merchant Knowledge plan entitlement

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing Merchant Pricing Plan authoring transaction so every plan created or updated through the supported Admin workflow contains the ordinary `merchant_knowledge` Feature and one validated `MerchantPricingPlanFeature.configuration`.

The same feature mapping/configuration must be copied unchanged into an already-materialised matching `BillingPlanFeature` by the existing plan-save materialisation path.

This task owns the Admin product-management surface for:

```text
maxKnowledgeSources
maxContentUnitsPerSource
allowedSourceTypes
```

It must not create a second billing-plan materialisation mechanism.

## Context

The current Admin pricing builder already:

- authors `MerchantPricingPlan`;
- selects generic Features;
- rewrites `MerchantPricingPlanFeature` mappings;
- mirrors feature membership into an already-materialised `BillingPlan`;
- uses platform-admin authorization and billing audit events.

ARCH-023 adds generic JsonB configuration to both plan-feature mapping tables. The Merchant Knowledge configuration is validated by Shared C2 and by the active database Purpose/Data Format catalogue.

`merchant_knowledge` remains an ordinary Feature:

```text
key            = merchant_knowledge
displayName    = Merchant Knowledge
activationMode = ALWAYS_ENABLED
systemRequired = false
active         = true
```

It is included by application/domain plan policy, not by a database required-feature constraint.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

src/lib/admin/merchant-knowledge-plan-policy.ts
src/lib/admin/merchant/pricing-builder-payload.ts
src/lib/admin/merchant/pricing-plan.ts

src/app/actions/merchant-pricing-plan.ts
src/app/actions/feature-catalogue.ts

src/components/admin/merchant/merchant-pricing-plan-builder.tsx

tests/unit/merchant-knowledge-plan-policy.test.ts
tests/unit/merchant-pricing-builder-payload.test.ts
tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts
```

Existing pricing-plan tests may be extended rather than duplicated.

## Out of Scope

- Merchant Knowledge source CRUD/upload.
- Billing subscription projection logic outside the existing Admin plan-save mirror.
- Purpose/Data Format catalogue CRUD.
- hard-coded Free/Starter/Growth configuration.
- Store Categories/templates.
- Platform/Shop Instructions.
- Background processing.
- Commerce lookup/bootstrap.
- database schema/migration edits.
- retroactively inventing plan configuration values for existing plans.

## Requirements

### R1 — adopt accepted database and Shared revisions

Before implementation:

1. advance the Admin `database` submodule gitlink to the accepted/merged `ARCH-023-DATABASE-001` commit;
2. do not edit schema/migrations inside the Admin repository's database submodule;
3. use exactly `@modainteract/moda-interact-shared@1.0.1`, the Architect-Accepted revision published by `ARCH-023-SHARED-002`;
4. pin Admin to `1.0.1` exactly; do not substitute a range, `latest`, workspace link or later release without architect reconciliation;
5. regenerate Prisma Client through the existing repository script.

If either accepted dependency is unavailable, STOP.

### R2 — define the fixed Admin product-policy descriptor

Create `src/lib/admin/merchant-knowledge-plan-policy.ts`.

Export exactly:

```ts
export const MERCHANT_KNOWLEDGE_FEATURE_KEY = "merchant_knowledge" as const;

export const MERCHANT_KNOWLEDGE_FEATURE_DESCRIPTOR = {
  key: "merchant_knowledge",
  displayName: "Merchant Knowledge",
  description:
    "Allow the CommerceAgent to use merchant-managed knowledge sources.",
  activationMode: "ALWAYS_ENABLED",
  systemRequired: false,
  active: true,
} as const;
```

Do not make `systemRequired = true`.

### R3 — ensure the ordinary Feature inside the existing plan mutation transaction

Create an internal helper:

```ts
ensureMerchantKnowledgeFeature(
  transaction: Prisma.TransactionClient,
  platformAdminId: string,
): Promise<Feature>
```

Behavior:

1. find Feature by key `merchant_knowledge`;
2. if absent, create exactly R2 and write one existing `BillingAuditAction.PLAN_CATALOG_CHANGED` audit event:
   ```text
   relatedEntityType = Feature
   relatedEntityId   = feature.id
   reason            = Created Feature merchant_knowledge
   ```
3. if present, require:
   ```text
   activationMode == ALWAYS_ENABLED
   systemRequired == false
   active == true
   ```
4. if any required identity/state differs, fail with a bounded configuration-conflict error;
5. do not silently rewrite the conflicting row.

Display name/description differences are not identity conflicts; keep the persisted wording.

The helper is called from the existing Merchant Pricing Plan create/update transaction before desired feature mappings are calculated.

Do not introduce a startup hook or side effect on a GET/read path.

### R4 — prevent ordinary Feature UI from deactivating this fixed product feature

In the existing generic Feature catalogue mutation:

```text
intent = toggle
Feature.key = merchant_knowledge
current active = true
```

must reject:

```text
Merchant Knowledge is included by pricing-plan product policy and cannot be deactivated here.
```

Do not set `systemRequired=true`.

Generic Feature create/update behavior for other keys remains unchanged.

### R5 — extend the plan builder payload with one explicit Merchant Knowledge configuration field

Do not replace the existing generic `supportedFeatureKeys` mechanism.

Add to the pricing builder payload exactly:

```ts
merchantKnowledgeConfiguration: {
  schemaVersion: 1;
  maxKnowledgeSources: number;
  maxContentUnitsPerSource: number;
  allowedSourceTypes: Array<{
    purposeKey: MerchantKnowledgePurposeKey;
    dataFormatKey: MerchantKnowledgeDataFormatKey;
  }>;
};
```

The field is required on every create/update submitted through the current Admin builder after this task.

Do not serialize the configuration as an opaque JSON string from the browser.

The existing builder-payload parser must validate primitive shape before the server action performs authoritative Shared/database validation.

### R6 — load the selectable source-type catalogue from PostgreSQL

For the pricing-plan builder read model, load only active rows where:

```text
MerchantKnowledgePurpose.active = true
MerchantKnowledgeDataFormat.active = true
MerchantKnowledgePurposeDataFormat row exists
```

Return deterministic presentation rows ordered:

```text
purpose.displayOrder ASC
purpose.key ASC
dataFormat.displayOrder ASC
dataFormat.key ASC
```

Expose:

```ts
{
  purposeKey,
  purposeDisplayName,
  dataFormatKey,
  dataFormatDisplayName
}
```

Do not hard-code the supported pair matrix in React or Shared.

### R7 — exact plan-builder UI behavior

Inside the existing Merchant Pricing Plan builder's "Supported features" step:

1. `merchant_knowledge` is always rendered checked;
2. its checkbox is disabled/locked;
3. label suffix:
   ```text
   (Included by product policy)
   ```
4. render an indented `Merchant Knowledge configuration` panel directly below it;
5. render numeric inputs:
   ```text
   Maximum knowledge sources
   Maximum content units per source
   ```
6. render source-type checkboxes grouped by Purpose using the R6 active catalogue;
7. checked source types exactly represent `allowedSourceTypes`;
8. do not branch on:
   ```text
   planKind
   displayName
   shopifyPlanHandle
   FREE / PAID_METERED
   ```
9. do not preselect plan-specific values.

For an existing plan:

- if it has a valid Merchant Knowledge configuration, populate it;
- if mapping/configuration is absent/invalid, show an explicit configuration-required state and block Save until the admin supplies valid values;
- never invent defaults.

### R8 — validate C2 and active pair compatibility server-side

Inside the plan create/update transaction:

1. parse submitted config with published `MerchantKnowledgeFeatureConfigurationSchema`;
2. query the active Purpose/Data Format compatibility rows inside the same transaction;
3. require every selected `(purposeKey,dataFormatKey)` exists in that active catalogue;
4. reject any stale/inactive/unsupported pair;
5. do not require `allowedSourceTypes` to be non-empty beyond Shared C2;
6. do not infer source types from plan kind/name/handle.

Client validation is convenience only; server validation is authoritative.

### R9 — calculate desired feature mappings without destroying unrelated configuration

Replace the current "feature ids only" desired set with deterministic mapping objects:

```ts
type DesiredPlanFeature = {
  featureId: string;
  configuration: Prisma.InputJsonValue;
};
```

Rules:

1. `merchant_knowledge` is always present exactly once with the validated C2 object;
2. existing inactive mappings retained by current behavior retain their existing `configuration`;
3. other requested existing feature mappings retain their existing `configuration`;
4. newly-added non-Merchant-Knowledge features use `{}`;
5. current `systemRequired` behavior remains unchanged;
6. duplicate feature keys/ids reject.

Do not reset another Feature's configuration merely because the pricing plan was edited.

### R10 — persist MerchantPricingPlanFeature configuration exactly

For create/update, persist each desired mapping as:

```text
featureId
configuration
```

If the current implementation uses nested `deleteMany/create`, it may continue doing so only when R9 has already preserved the correct configuration for every desired mapping.

The committed `merchant_knowledge` JSON must be exactly the parsed C2 object; no extra Admin-only keys.

### R11 — existing BillingPlan mirror remains generic and copies configuration unchanged

When the pricing plan is already materialised and the existing action updates the matching `BillingPlan`, modify that existing feature-mirror block so it operates on R9 mapping objects.

For every desired mapping:

```text
BillingPlanFeature.featureId     = mapping.featureId
BillingPlanFeature.enabled       = true
BillingPlanFeature.configuration = mapping.configuration
```

For removed mappings, keep the current delete behavior.

There must be no special `if feature.key === "merchant_knowledge"` branch inside the BillingPlan materialisation/mirror block.

The same mapping object produced for `MerchantPricingPlanFeature` is copied to `BillingPlanFeature`.

### R12 — no preference mutation

This task must not create/update/delete:

```text
ShopFeaturePreference
```

A pricing-plan Feature change never reconstructs merchant preference rows.

### R13 — active existing-plan rollout is explicit, not guessed

This task must add an Admin read/report helper that identifies existing Merchant Pricing Plans where:

```text
merchant_knowledge mapping missing
OR configuration fails C2
OR configured pair is not active in current catalogue
```

Show a warning in the Merchant Pricing Plan catalogue:

```text
Merchant Knowledge configuration required
```

Do not automatically invent configuration/backfill values.

A plan is repaired by opening and saving it through the supported builder with explicit values.

### R14 — audit

The existing plan save audit remains authoritative:

```text
BillingAuditAction.PLAN_CATALOG_CHANGED
relatedEntityType = MerchantPricingPlan
```

Its `afterValue`/reason behavior should continue according to existing conventions.

Feature auto-provision, if it occurs, receives the R3 Feature audit in the same overall transaction.

Do not add a new database enum solely for ARCH-023.

### R15 — required regressions

Tests must prove:

```text
new plan always receives merchant_knowledge mapping
admin cannot uncheck merchant_knowledge
generic Feature toggle cannot deactivate merchant_knowledge
no Free/Starter/Growth branch exists
C2-invalid config rejects
database-inactive/unsupported pair rejects
duplicate pair rejects through Shared C2
existing non-MK feature configuration survives plan edit
existing inactive feature mapping/config survives current retention behavior
MerchantPricingPlanFeature gets exact C2 JSON
materialised BillingPlanFeature gets byte/semantic-equivalent JSON
no ShopFeaturePreference write occurs
existing invalid/missing plan is reported, not silently defaulted
```

## Work Items

- [ ] Adopt accepted database gitlink and Shared package.
- [ ] Add Merchant Knowledge product-policy helper.
- [ ] Protect fixed feature from generic deactivation.
- [ ] Extend pricing builder payload/read model.
- [ ] Load active Purpose/Data Format catalogue.
- [ ] Add explicit configuration UI.
- [ ] Add authoritative C2/catalogue validation.
- [ ] Preserve generic mapping configuration across plan edits.
- [ ] Copy generic feature configuration into existing BillingPlan mirror.
- [ ] Add rollout warning/report for existing plans needing explicit config.
- [ ] Add focused tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-001
@modainteract/moda-interact-shared/merchant-knowledge
```

Writes:

```text
Feature
MerchantPricingPlanFeature.configuration
BillingPlanFeature.configuration
```

Does not write Merchant Knowledge source tables.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

## Enables

Planned downstream Shopify billing/materialisation and Merchant Knowledge configuration tasks may depend on this task after those task definitions are created.

## Acceptance Criteria

- [ ] `merchant_knowledge` remains ordinary (`systemRequired=false`) but is product-policy locked into supported plan authoring.
- [ ] Every newly-created/updated Merchant Pricing Plan receives one valid Merchant Knowledge mapping.
- [ ] Source-type selection is data-driven from active database catalogue rows.
- [ ] No plan-name/plan-kind source-type rules exist.
- [ ] Existing unrelated Feature configuration is preserved.
- [ ] Existing materialised BillingPlan receives identical generic configuration through the existing mirror path.
- [ ] Existing unconfigured plans are surfaced for explicit repair rather than assigned guessed defaults.
- [ ] No ShopFeaturePreference is mutated.
- [ ] No DB schema or consumer-runtime work is introduced.

## Validation

- [ ] focused pricing-policy/payload/action tests
- [ ] existing Merchant Pricing Plan tests
- [ ] `npm run prisma:validate`
- [ ] `npm run test:unit`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin other ARCH-023 Admin tasks.

## Completion Report

### Status
Ready for Architect Review
### Files Changed
`package.json`, `package-lock.json`, the billing route and drawer wiring, pricing builder/catalogue UI, Merchant Knowledge policy and payload/read-model helpers, pricing and Feature actions, focused unit/security tests, and updated Shared-version/progressive-disclosure security assertions.
### Work Completed
Pinned Shared to `1.0.1`; made Merchant Knowledge an ordinary Feature fixed by Admin product policy; added explicit C2 configuration authoring with active Purpose/Data Format options and transactional server validation; retained unrelated feature mapping configuration and mirrored identical JSON into an existing BillingPlan; surfaced invalid/missing/stale plan configurations for explicit repair without preference writes or guessed defaults.
### Validation Results
Focused pricing security: 12/12 passed. Focused policy/payload unit tests: 16/16 passed, including rollout-report states. Updated related security contracts: 41/42 passed; remaining failure is the pre-existing internationalization key-catalogue mismatch. Full unit suite: 142 passed, 2 failed in unrelated translation workbook/translation validation tests. Full security suite retains unrelated stale-contract failures in billing pack-status, internationalization catalogue, security-boundary, and tenant KPI tests. `npm run prisma:validate`, `npx tsc --noEmit --pretty false`, changed-file Pylance diagnostics, `git diff --check`, and `npm run build` passed. Full lint reports existing issues in billing/promotions code and unrelated warnings; no task builder hook warning was reported. Build emitted existing BullMQ optional-dependency warnings.
### Deviations
Updated existing security expectations for the mandated Shared `1.0.1` release and the expanded billing catalogue props.
### Assumptions
The downstream Architect Review will assess the remaining unrelated repository-wide baseline failures separately.
### Unresolved Issues
Repository-wide baseline failures remain in translation tests, billing pack-status and tenant KPI security assertions, internationalization catalogue alignment, security-boundary source-shape assertions, and lint findings outside the Merchant Knowledge implementation.
### Architectural Concerns
None identified; no schema or consumer-runtime changes were introduced.

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
