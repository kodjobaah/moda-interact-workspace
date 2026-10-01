---
id: ARCH-024-ADMIN-004
architecture_id: ARCH-024
title: Assign Commerce models to Merchant Pricing Plans
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 33
executor: copilot
claimed_at: 2026-10-01T17:16:59Z
attempt: 1
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
enables: []
created: 2026-10-01
updated: 2026-10-01
---

# Assign Commerce models to Merchant Pricing Plans

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing Admin Merchant Pricing Plan builder so a Platform `SUPER_ADMIN` can assign **zero or one enabled Platform-available Commerce model** to each `MerchantPricingPlan`.

The durable product-tier contract is exactly:

```text
MerchantPricingPlan.commerceModelId = NULL
    -> this plan has no model override
    -> runtime may inherit Platform when there is no explicit Shop override

MerchantPricingPlan.commerceModelId = <catalogue entry id>
    -> this plan explicitly grants that Platform-available model tier
```

This is Platform product configuration. Merchants do not choose the model.

The model association is stored only on `MerchantPricingPlan`. It MUST NOT be copied to `BillingPlan`, and this task MUST NOT add a physical `MerchantPricingPlan <-> BillingPlan` relationship. Accepted ARCH-017 runtime identity remains the shared unique `shopifyPlanHandle`.

## Context

`ARCH-024-DATABASE-001` adds:

```prisma
model MerchantPricingPlan {
  // existing fields...

  commerceModelId String? @db.Text
  commerceModel   CommerceModelCatalogueEntry? @relation(
    "MerchantPricingPlanCommerceModel",
    fields: [commerceModelId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )

  @@index([commerceModelId])
}
```

and the inverse relation on `CommerceModelCatalogueEntry`.

The existing Admin Merchant Pricing Plan workflow already owns:

```text
src/lib/admin/merchant/pricing-builder-payload.ts
src/lib/admin/merchant/pricing-plan.ts
src/lib/admin/merchant/pricing-plan-builder.ts
src/app/actions/merchant-pricing-plan.ts
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
src/components/admin/billing-drawers.tsx
src/app/(protected)/billing/page.tsx
```

and already performs one transactional plan mutation with catalogue-revision fencing, materialised `BillingPlan` synchronization for billing-owned fields and `BillingAuditEvent(action = PLAN_CATALOG_CHANGED)` audit.

ARCH-024 must extend that existing workflow. Do not build a second Price Plan editor.

`ARCH-024-SHARED-002` publishes the canonical model contracts including:

```ts
CommerceModelAvailabilitySchema
CommerceModelCatalogueEntrySchema
CommercePricingPlanModelAssignmentSchema
```

A Price Plan may select only a model from the global enabled Platform Availability. Shop-specific models are not product-tier defaults.

## Scope

Primary implementation targets:

```text
moda-interact-admin/database/                                     # accepted ARCH-024-DATABASE-001 gitlink
moda-interact-admin/src/lib/admin/merchant/pricing-builder-payload.ts
moda-interact-admin/src/lib/admin/merchant/pricing-plan.ts
moda-interact-admin/src/lib/admin/merchant/pricing-plan-builder.ts
moda-interact-admin/src/lib/admin/merchant/pricing-plan-model.ts    # NEW
moda-interact-admin/src/app/actions/merchant-pricing-plan.ts
moda-interact-admin/src/components/admin/merchant/merchant-pricing-plan-builder.tsx
moda-interact-admin/src/components/admin/billing-drawers.tsx
moda-interact-admin/src/app/(protected)/billing/page.tsx

moda-interact-admin/tests/unit/merchant-pricing-builder-payload.test.ts
moda-interact-admin/tests/unit/merchant-pricing-plan-model.test.ts   # NEW
moda-interact-admin/tests/security/admin-merchant-pricing-plan.test.mjs
```

Update `package.json` / lockfile only when mechanically required to consume the exact SHARED-002 version.

Additional files may change only when mechanically required by the existing Merchant Pricing Plan builder flow. Name and justify each additional file in the Completion Report.

Do not edit the database schema/migration in this task.

## Out of Scope

- Model Availability administration; `ARCH-024-ADMIN-001` owns it.
- Model Catalogue lifecycle/configuration; `ARCH-024-ADMIN-002` owns it.
- OpenRouter credential administration; `ARCH-024-ADMIN-003` owns it.
- Platform/Shop `CommerceAgentConfiguration` selection; Commerce Studio owns that surface.
- Merchant-facing model selection.
- Automatically selecting a model from plan price, position, feature count or plan name.
- Copying `commerceModelId` into `BillingPlan`.
- Adding a `BillingPlan -> CommerceModelCatalogueEntry` relation.
- Adding a physical `BillingPlan <-> MerchantPricingPlan` relation.
- Mutating `Subscription`, current plan or pending plan state.
- Calling OpenRouter.
- Changing effective-model runtime precedence; the parent ARCH-024 architecture owns `SHOP -> PRICING_PLAN -> PLATFORM`, while Commerce and Background implement that policy in their own runtime boundaries.
- Clearing a Price Plan association merely because an Admin later disables/reassigns the model/Availability.
- Preventing an existing subscriber from receiving the current plan association solely because `MerchantPricingPlan.isActive = false`.

## Requirements

### R1 — consume accepted Database and Shared contracts before implementation

This task MUST:

1. update the nested `database/` gitlink to the architect-accepted ARCH-024-DATABASE-001 merged commit;
2. update `@modainteract/moda-interact-shared` to the exact version published by ARCH-024-SHARED-002;
3. regenerate Prisma from the accepted nested schema;
4. use the published Shared model/assignment schemas rather than defining structurally similar local copies.

At minimum import:

```ts
import {
  CommerceModelAvailabilitySchema,
  CommerceModelCatalogueEntrySchema,
  CommercePricingPlanModelAssignmentSchema,
} from "@modainteract/moda-interact-shared/commerce/model";
```

Use the actual published export path from SHARED-002 if packaging differs; do not duplicate the schemas locally.

### R2 — extend the Merchant Pricing Plan builder payload exactly

In:

```text
src/lib/admin/merchant/pricing-builder-payload.ts
```

extend the public payload shape with exactly:

```ts
export type MerchantPricingBuilderPayload = {
  // existing fields unchanged
  commerceModelId: string | null;
};
```

Add `commerceModelId` to `TOP_LEVEL_KEYS`.

Parsing rules are exact:

```text
null
    -> valid; means "Use Platform default"

blank string
    -> normalize to null

nonblank string
    -> trim
    -> maximum 128 characters
    -> retain exact ID after trim

all other values
    -> MerchantPricingPayloadError at $.commerceModelId
```

Do not infer a model ID from provider/model name or UI label.

All builder create/edit payloads MUST include the field. Existing tests/fixtures must be updated explicitly rather than making the field disappear from validation.

### R3 — create one reusable Platform-model selection helper

Create:

```text
src/lib/admin/merchant/pricing-plan-model.ts
```

Export exactly these public shapes:

```ts
import type { Prisma, PrismaClient } from "@prisma/client";

export type MerchantPricingPlanModelOption = {
  id: string;
  displayName: string;
  provider: string;
  providerModelId: string;
};

export async function listMerchantPricingPlanModelOptions(input?: {
  db?: PrismaClient | Prisma.TransactionClient;
}): Promise<MerchantPricingPlanModelOption[]>;

export async function assertMerchantPricingPlanModelSelectable(input: {
  db: PrismaClient | Prisma.TransactionClient;
  modelId: string;
}): Promise<MerchantPricingPlanModelOption>;
```

If repository conventions require the default `prisma` singleton rather than an optional `db`, adapt only the `list...` injection shape while preserving one reusable read implementation. Record any such mechanical deviation.

### R4 — selectable Price Plan models are exactly enabled Platform-available entries

`listMerchantPricingPlanModelOptions(...)` must query only Catalogue Entries satisfying all of:

```text
CommerceModelCatalogueEntry.enabled = true
CommerceModelAvailability.enabled = true
CommerceModelAvailability.scope = PLATFORM
CommerceModelAvailability.shopId = NULL
```

For every returned row:

1. validate the Availability through `CommerceModelAvailabilitySchema`;
2. validate the Catalogue Entry through `CommerceModelCatalogueEntrySchema`;
3. project only `id`, `displayName`, `provider`, `providerModelId` to browser/UI code.

Ordering is exact:

```text
1. displayName ascending
2. provider ascending
3. providerModelId ascending
4. id ascending
```

Do not return model configuration JSON, credentials, Shop availability rows or disabled rows in the selector options.

### R5 — write-time selection validation is exact and fail-closed

`assertMerchantPricingPlanModelSelectable(...)` must load the exact target Catalogue Entry with its Availability and require:

```text
model exists
model Shared-schema valid
model.enabled = true
availability exists
availability Shared-schema valid
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = NULL
```

Failure mapping should follow the existing Admin action error boundary:

```text
missing model                     -> bounded validation error
invalid persisted model/config    -> bounded validation error
model disabled                    -> bounded validation error
availability disabled             -> bounded validation error
SHOP-scoped availability          -> bounded validation error
```

Never silently substitute another model.

The helper MUST NOT read an OpenRouter credential and MUST NOT call OpenRouter.

### R6 — preserve an existing now-invalid association for repair visibility

Admin lifecycle changes can make an already-stored `MerchantPricingPlan.commerceModelId` no longer selectable after it was validly written.

The edit surface MUST NOT silently clear it.

When loading a Price Plan for edit:

```text
commerceModelId = NULL
    -> selector shows "Use Platform default"

commerceModelId points to a currently selectable model
    -> normal selected option

commerceModelId points to a now-missing/disabled/non-Platform model
    -> retain the stored ID
    -> render an explicit unavailable selected sentinel
    -> show role="alert" repair guidance
```

The unavailable sentinel label must be deterministic:

```text
Current model unavailable — <commerceModelId>
```

Do not expose configuration JSON through this sentinel.

An unrelated edit to an existing Price Plan with an unchanged now-invalid model association MAY proceed. This prevents an Availability/Catalogue lifecycle change from locking the entire billing plan editor.

However, when `commerceModelId` is **changed**, the new value must be either:

```text
NULL
or
currently selectable under R5
```

### R7 — integrate model selection into the existing Merchant Pricing Plan builder

Add one field to the existing builder rather than creating another page/drawer.

UI contract:

```text
Label: Commerce model

null option:
  Use Platform default

model option:
  <displayName> (<provider>/<providerModelId>)
```

Help text must state, in equivalent wording:

```text
When a Shop has no explicit model override, a current subscription to this plan uses this model. "Use Platform default" leaves the plan without its own model override.
```

Do not expose Shop-scoped models.

Do not present separate merchant/customer controls.

Do not suggest that changing the model changes a pending plan immediately; runtime uses the Shop's **current** billing plan on the next CommerceAgent turn.

### R8 — include the association in existing plan read/build state

Update the existing Merchant Pricing Plan read/include/projection flow so builder state contains:

```ts
commerceModelId: string | null;
```

The plan catalogue/read surface may show a bounded model label/status for Platform Admins, but model configuration JSON is not required.

The canonical persisted assignment must also validate as:

```ts
CommercePricingPlanModelAssignmentSchema.parse({
  merchantPricingPlanId: plan.id,
  shopifyPlanHandle: plan.shopifyPlanHandle,
  modelId: plan.commerceModelId,
});
```

This is validation of the assignment shape only. Current selectability is governed separately by R5/R6.

### R9 — create and update mutations validate changed model association inside the existing transaction

Use the existing `mutateMerchantPricingPlanAction(...)` transaction. Do not add a second transaction or independent model-assignment Server Action.

For create:

```text
payload.commerceModelId = NULL
    -> create MerchantPricingPlan with commerceModelId = NULL

payload.commerceModelId != NULL
    -> assertMerchantPricingPlanModelSelectable(transaction, modelId)
    -> create MerchantPricingPlan with that exact commerceModelId
```

For update:

```text
payload.commerceModelId === existing.commerceModelId
    -> preserve exact value
    -> do not require currently-selectable state solely for an unrelated edit

payload.commerceModelId !== existing.commerceModelId
    -> if NULL: clear association
    -> else: assert currently selectable inside SAME transaction
    -> persist exact new ID
```

The model-validation read and MerchantPricingPlan write therefore share the existing plan mutation transaction.

Do not use a browser-supplied model label/provider as authority.

### R10 — materialised BillingPlan synchronization MUST NOT copy model association

The existing edit path synchronizes selected billing-owned fields into the matching operational `BillingPlan` when `existing.materializedAt` is set.

That block MUST remain model-neutral.

Specifically, do **not** add any of:

```text
BillingPlan.commerceModelId
BillingPlan.modelId
BillingPlan.model
```

and do not write model association data into BillingPlan JSON/metadata.

The only runtime bridge is accepted ARCH-017 identity:

```text
current Subscription.plan
    -> BillingPlan.shopifyPlanHandle
    -> MerchantPricingPlan.shopifyPlanHandle
```

### R11 — plan activation/deactivation does not rewrite the model association

Existing `toggle` behaviour may change `MerchantPricingPlan.isActive`.

It MUST NOT:

```text
clear commerceModelId
replace commerceModelId
copy commerceModelId to BillingPlan
```

An inactive Price Plan may still be the current plan of an existing subscriber and therefore its configured model remains meaningful until billing changes that subscriber's current plan.

### R12 — use the existing billing audit stream

Do not add a new audit enum/action solely for model assignment.

Continue using:

```text
BillingAuditEvent.action = PLAN_CATALOG_CHANGED
relatedEntityType = MerchantPricingPlan
relatedEntityId = <plan id>
```

When `commerceModelId` changes, the corresponding audit event MUST additionally record bounded before/after values using the existing columns:

```json
beforeValue: { "commerceModelId": "<old-or-null>" }
afterValue:  { "commerceModelId": "<new-or-null>" }
```

If the existing mutation already creates one `PLAN_CATALOG_CHANGED` audit row for the same save, extend that row rather than writing a duplicate event solely for the model field.

Do not include model configuration JSON or provider credentials in audit values.

### R13 — authorization remains Platform Admin control-plane authorization

All reads/mutations continue through the existing Admin authorization boundary.

Mutation remains `SUPER_ADMIN`-only under the existing Merchant Pricing Plan mutation contract.

Do not expose the selector or mutation to merchants.

Do not trust browser-selected `commerceModelId` until R5/R9 server validation succeeds.

### R14 — focused tests are mandatory

Add/extend deterministic tests proving at least:

1. payload `commerceModelId = null` parses;
2. blank string normalizes to null;
3. valid nonblank ID is trimmed/preserved;
4. non-string/non-null and overlength values fail at `$.commerceModelId`;
5. options contain only enabled models in enabled Platform Availability;
6. disabled model is omitted;
7. disabled Platform Availability is omitted;
8. Shop-availability model is omitted;
9. option order is deterministic;
10. selectable validator accepts an enabled Platform-available model;
11. validator rejects missing/disabled/Shop-scoped targets;
12. create with null stores null;
13. create with valid model stores exact ID;
14. update from model A -> model B validates and stores B;
15. update model -> null clears association;
16. unrelated edit with unchanged now-invalid stored model is allowed and preserves the ID;
17. changing from an invalid current ID to another invalid/nonselectable ID is rejected;
18. UI renders `Use Platform default` for null;
19. UI renders `<displayName> (<provider>/<providerModelId>)` for valid options;
20. UI renders `Current model unavailable — <id>` plus alert for an invalid persisted association;
21. materialised BillingPlan update never receives a model field;
22. toggle active/inactive preserves `commerceModelId`;
23. model association change is audited with bounded before/after values;
24. no test makes a live OpenRouter request.

### R15 — static absence checks are mandatory

Validation MUST prove the Admin/Billing operational schema/source did not gain a duplicated model pointer on `BillingPlan`.

At minimum inspect/grep task-owned source and accepted Prisma schema for prohibited additions equivalent to:

```text
BillingPlan.commerceModelId
BillingPlan.modelId
```

Do not flag ordinary unrelated uses of a generic `modelId` identifier outside BillingPlan.

## Work Items

- [ ] Consume accepted ARCH-024 Database gitlink and exact SHARED-002 package version.
- [ ] Extend Merchant Pricing builder payload with nullable `commerceModelId` and exact validation.
- [ ] Add `pricing-plan-model.ts` with deterministic Platform-only model option/query/validation contracts.
- [ ] Add the Commerce model selector to the existing Merchant Pricing Plan builder.
- [ ] Preserve/render invalid existing associations explicitly rather than silently clearing them.
- [ ] Integrate create/update model validation into the existing transactional mutation.
- [ ] Keep materialised BillingPlan synchronization model-neutral.
- [ ] Preserve association through plan activation/deactivation.
- [ ] Extend existing `PLAN_CATALOG_CHANGED` audit before/after values when the association changes.
- [ ] Add focused unit/security/UI regression coverage from R14.
- [ ] Run required validation and record exact results/warnings in the Completion Report.

## Interfaces / Contracts

### Shared contract owner

Task/publication:

```text
ARCH-024-SHARED-001
ARCH-024-SHARED-002
```

Package:

```text
@modainteract/moda-interact-shared
```

Consumed contracts:

```text
CommerceModelAvailabilitySchema
CommerceModelCatalogueEntrySchema
CommercePricingPlanModelAssignmentSchema
```

### Durable state owner

`ARCH-024-DATABASE-001`

This task mutates only:

```text
billing.MerchantPricingPlan.commerceModelId
```

for the new model association.

It does not add/update a BillingPlan model field.

### Runtime consumer contract

`ARCH-024-COMMERCE-002` and `ARCH-024-BACKGROUND-001` resolve current product-tier model inheritance through:

```text
Subscription.planId / plan
    -> BillingPlan.shopifyPlanHandle
    -> MerchantPricingPlan.shopifyPlanHandle
    -> MerchantPricingPlan.commerceModelId
```

This Admin task must not invent an alternative relationship.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`

These are the only implementation dependencies. This task reads/writes the accepted database model and published Shared contracts directly; it does not consume `ARCH-024-ADMIN-002` source or UI implementation. Catalogue rows required by focused tests are seeded directly through the accepted database schema.

All dependencies must be architect-accepted Complete before this task becomes Ready.

## Enables

None directly.

The terminal ARCH-024 system-test task must include ADMIN-004 among its implementation dependencies when materialised.

## Acceptance Criteria

- [ ] Each Merchant Pricing Plan can persist zero/one `commerceModelId` through the existing Admin builder.
- [ ] Null is presented as `Use Platform default` and stored as SQL NULL.
- [ ] New/changed non-null assignments accept only enabled Catalogue Entries in enabled Platform Availability.
- [ ] Shop-availability models cannot be assigned to a Price Plan.
- [ ] Merchants have no model-selection control.
- [ ] Existing invalid associations remain visible and repairable; they are not silently cleared.
- [ ] Unrelated edits can preserve an unchanged invalid association, while any changed association must become null or currently selectable.
- [ ] Materialised `BillingPlan` synchronization remains model-neutral and no BillingPlan model pointer/FK exists.
- [ ] `MerchantPricingPlan.isActive` toggles do not rewrite the model association.
- [ ] Audit remains `PLAN_CATALOG_CHANGED` and model changes record bounded before/after IDs only.
- [ ] Shared schemas validate Availability/Catalogue/assignment shapes.
- [ ] No OpenRouter credential or live provider request is involved.
- [ ] Focused unit/security/UI regression coverage from R14 passes.

## Validation

Before Node-related commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

From the dedicated `moda-interact-admin` task worktree, inspect `package.json` first, then run:

```bash
npm run prisma:generate
npm run prisma:validate
```

Focused unit tests:

```bash
node --experimental-strip-types --test \
  tests/unit/merchant-pricing-builder-payload.test.ts \
  tests/unit/merchant-pricing-plan-model.test.ts
```

Focused Admin security/UI regression:

```bash
node --test tests/security/admin-merchant-pricing-plan.test.mjs
```

Targeted Prettier over every changed/new file, including at minimum:

```bash
npx prettier --check \
  src/lib/admin/merchant/pricing-builder-payload.ts \
  src/lib/admin/merchant/pricing-plan.ts \
  src/lib/admin/merchant/pricing-plan-builder.ts \
  src/lib/admin/merchant/pricing-plan-model.ts \
  'src/app/actions/merchant-pricing-plan.ts' \
  'src/components/admin/merchant/merchant-pricing-plan-builder.tsx' \
  'src/components/admin/billing-drawers.tsx' \
  'src/app/(protected)/billing/page.tsx' \
  tests/unit/merchant-pricing-builder-payload.test.ts \
  tests/unit/merchant-pricing-plan-model.test.ts \
  tests/security/admin-merchant-pricing-plan.test.mjs
```

Targeted ESLint over changed TypeScript/TSX files, including at minimum:

```bash
npx eslint \
  src/lib/admin/merchant/pricing-builder-payload.ts \
  src/lib/admin/merchant/pricing-plan.ts \
  src/lib/admin/merchant/pricing-plan-builder.ts \
  src/lib/admin/merchant/pricing-plan-model.ts \
  'src/app/actions/merchant-pricing-plan.ts' \
  'src/components/admin/merchant/merchant-pricing-plan-builder.tsx' \
  'src/components/admin/billing-drawers.tsx' \
  'src/app/(protected)/billing/page.tsx'
```

Production build:

```bash
npm run build
```

Static schema/source inspection proving no duplicated BillingPlan model association.

Whitespace:

```bash
git diff --check
```

If validation encounters a documented baseline condition, apply the architect's development-baseline policy rather than broadening this task into unrelated repair.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set the task to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin Commerce/Background/system-test follow-on work.

## Implementation Notes

- Extend the existing Merchant Pricing Plan builder/mutation. Do not create a parallel model-assignment page or mutation route.
- Treat `MerchantPricingPlan.commerceModelId` as product-tier configuration, not tenant-specific state.
- A higher-priced plan is not automatically a "better" model. Admin explicitly chooses the model per plan; pricing tier semantics are product policy, not inferred by code.
- Runtime precedence remains `SHOP -> current PRICING_PLAN -> PLATFORM` and is owned by the Commerce/Background resolver tasks.
- A pending upgrade does not grant the pending plan model early.
- An inactive pricing catalogue row may still describe the current plan of an existing subscriber; do not use `isActive` as runtime entitlement state.
- The database FK prevents deleting a model referenced by a Price Plan. Availability/catalogue disable/reassignment may make the association runtime-invalid; leave the durable pointer visible for repair.
- Never copy model configuration JSON, Tool configuration, OpenRouter credentials or customer data into billing audit metadata.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
