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
status: complete
priority: 33
executor: null
claimed_at: null
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

- [x] Consume accepted ARCH-024 Database gitlink and exact SHARED-002 package version.
- [x] Extend Merchant Pricing builder payload with nullable `commerceModelId` and exact validation.
- [x] Add `pricing-plan-model.ts` with deterministic Platform-only model option/query/validation contracts.
- [x] Add the Commerce model selector to the existing Merchant Pricing Plan builder.
- [x] Preserve/render invalid existing associations explicitly rather than silently clearing them.
- [x] Integrate create/update model validation into the existing transactional mutation.
- [x] Keep materialised BillingPlan synchronization model-neutral.
- [x] Preserve association through plan activation/deactivation.
- [x] Extend existing `PLAN_CATALOG_CHANGED` audit before/after values when the association changes.
- [x] Add focused unit/security/UI regression coverage from R14.
- [x] Run required validation and record exact results/warnings in the Completion Report.

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

- [x] Each Merchant Pricing Plan can persist zero/one `commerceModelId` through the existing Admin builder.
- [x] Null is presented as `Use Platform default` and stored as SQL NULL.
- [x] New/changed non-null assignments accept only enabled Catalogue Entries in enabled Platform Availability.
- [x] Shop-availability models cannot be assigned to a Price Plan.
- [x] Merchants have no model-selection control.
- [x] Existing invalid associations remain visible and repairable; they are not silently cleared.
- [x] Unrelated edits can preserve an unchanged invalid association, while any changed association must become null or currently selectable.
- [x] Materialised `BillingPlan` synchronization remains model-neutral and no BillingPlan model pointer/FK exists.
- [x] `MerchantPricingPlan.isActive` toggles do not rewrite the model association.
- [x] Audit remains `PLAN_CATALOG_CHANGED` and model changes record bounded before/after IDs only.
- [x] Shared schemas validate Availability/Catalogue/assignment shapes.
- [x] No OpenRouter credential or live provider request is involved.
- [x] Focused unit/security/UI regression coverage from R14 passes.

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

Ready for Review

### Files Changed

- `package.json` and `package-lock.json`: upgrade `@modainteract/moda-interact-shared` from `1.0.1` to the SHARED-002 release `1.1.0`.
- `src/lib/admin/merchant/pricing-builder-payload.ts`: require and normalize nullable `commerceModelId` with the specified 128-character/path validation.
- `src/lib/admin/merchant/pricing-plan-model.ts`: shared-schema validated Platform model option listing and write-time selectability helper.
- `src/lib/admin/merchant/pricing-plan.ts`: include/validate persisted model assignments in plan reads and catalogue projection.
- `src/app/actions/merchant-pricing-plan.ts`: validate changed assignments inside the existing transaction; persist exact IDs; validate canonical assignment shape; extend the existing audit event. BillingPlan synchronization and toggle remain model-neutral.
- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`, `src/components/admin/billing-drawers.tsx`, and `src/app/(protected)/billing/page.tsx`: add the Platform-only selector, deterministic unavailable sentinel/repair alert, requested plan-runtime help text, and pass options through the existing drawer.
- `tests/unit/merchant-pricing-builder-payload.test.ts`: cover nullable, blank, trimmed, maximum-length, invalid-type and overlength input.
- `tests/unit/merchant-pricing-plan-model.test.ts`: cover enabled Platform-only filtering, deterministic order, projection, selectability, and invalid Shared-schema data.
- `tests/security/admin-merchant-pricing-plan.test.mjs`: source-level regression assertions for transactional validation ordering, Platform-admin authorization, association/audit/toggle invariants, repair UI contract, model-neutral BillingPlan synchronization, and static schema absence.

The launcher-provided database submodule was already at accepted ARCH-024-DATABASE-001 commit `cfeeb12456b4e05067a96857a8c47837d7e33bbd`; it was regenerated/validated and no database schema, migration, or gitlink change was needed.

### Work Completed

- Consumed Shared `1.1.0`, whose `@modainteract/moda-interact-shared/commerce/model` export provides the canonical Availability, Catalogue Entry and Pricing Plan Assignment schemas; no local duplicate contracts were added. Regenerated Prisma Client from the accepted database schema.
- Added required `commerceModelId` to every builder payload. Null and blank strings normalize to null; nonblank values are trimmed and bounded to 128 characters; invalid values fail at `$.commerceModelId`.
- Added the single reusable selector/helper. Listing filters to enabled Catalogue Entries with enabled `PLATFORM` Availability and null `shopId`, validates each returned Availability and Catalogue Entry, orders by display name/provider/provider model ID/id, and projects only the four UI-safe fields. Write validation loads the exact selected model and fails closed with a bounded message. No credentials or provider calls are read.
- Integrated the selector in the existing Platform Admin Merchant Pricing Plan builder. It presents `Use Platform default`, formatted selectable options, and a deterministic `Current model unavailable — <id>` sentinel plus `role="alert"` repair guidance without clearing the stored ID. The help text describes current-plan timing and does not expose a merchant-facing control.
- Added the nullable association to existing read/build state and validates persisted assignments with `CommercePricingPlanModelAssignmentSchema`.
- Changed non-null assignments are revalidated inside the existing plan transaction. Unchanged now-invalid IDs bypass current-selectability validation and remain persisted; changed IDs must be null or selectable. Create/update save the exact ID. Existing toggle only updates `isActive`; materialized BillingPlan sync still writes only its existing billing fields.
- Extended the existing `PLAN_CATALOG_CHANGED` event with only the old/new `commerceModelId` when the association changes; no duplicate audit event or model configuration/credential data is written.
- Launcher preparation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-ADMIN-004`, branch `task/ARCH-024-ADMIN-004`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-ADMIN-004`, branch `task/ARCH-024-ADMIN-004`. Both dedicated worktrees were newly created. Shared workspace/admin checkouts were not switched or mutated for implementation; no other task worktree was reused.
- Launcher synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` incorporation `already-current`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` incorporation `already-current`.
- Launcher recursive submodule setup passed (`git submodule sync --recursive` and `git submodule update --init --recursive`); `database` is initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Claim: Attempt 1 by `copilot` at `2026-10-01T17:16:59Z`; launcher claim commit `16a3889f5e6177445b898fddced7cb2a874f8a38` was committed and pushed.
- Implementation commit `2bdfb89` (`task(ARCH-024-ADMIN-004): assign models to pricing plans`) is pushed to `origin/task/ARCH-024-ADMIN-004`. No database gitlink was staged.

### Validation Results

- PASS: `npm run prisma:generate` — Prisma Client v6.19.3 generated from `database/prisma/schema.prisma`.
- PASS: `npm run prisma:validate` — accepted schema is valid.
- PASS: `node --experimental-strip-types --test tests/unit/merchant-pricing-builder-payload.test.ts tests/unit/merchant-pricing-plan-model.test.ts` — 14 tests passed. Node emitted the existing `MODULE_TYPELESS_PACKAGE_JSON` warning for typed ESM test files.
- PASS: `node --test tests/security/admin-merchant-pricing-plan.test.mjs` — 13 tests passed. The mutation-path assertions inspect the server-action source; this task does not add a database-backed server-action integration test.
- PASS: task-required targeted `npx prettier --check` over all changed/new implementation and test files — all matched files use Prettier style.
- BLOCKED BY PRE-EXISTING DIAGNOSTIC: task-required targeted ESLint command over changed TypeScript/TSX files reports one `react-hooks/purity` error in `src/components/admin/billing-drawers.tsx:182`: `Date.now()` is called during render. This line is unchanged by the task; the only edits to that file pass a `commerceModelOptions` prop through the existing drawer. No unrelated drawer behavior was changed.
- PASS: targeted ESLint over the other changed TypeScript/TSX files, excluding only `billing-drawers.tsx`, completed with no diagnostics.
- PASS: `npm run build` — production build completed. Existing warnings include BullMQ dynamic dependency resolution and unresolved optional `@valkey/valkey-glide` imports; compilation, TypeScript, static generation and route generation completed successfully.
- PASS: static BillingPlan absence check — `BillingPlan` in `database/prisma/schema.prisma` has neither `commerceModelId` nor `modelId`; the materialized BillingPlan update block contains neither field.
- PASS: no-live-provider check — added tests contain no provider request; the `openrouter` text in the helper test is only a model-provider fixture value.
- PASS: `git diff --check` — clean.

### Deviations

No scope deviation. The database gitlink already pointed to the accepted Database commit supplied by the task branch/launcher, so it required no update. `src/lib/admin/merchant/pricing-plan-builder.ts` did not need a change; the existing drawer/builder component is the active create/edit flow and receives model options through the billing page.

### Assumptions

The ARCH-024-SHARED-002 published package version is `1.1.0`, as resolved from the task's accepted Shared dependency state. Existing now-invalid associations are retained in the edit payload unless an Admin explicitly changes them.

### Unresolved Issues

The task's server-action mutation scenarios are protected by source-level security assertions rather than executed against a database; payload parsing, option filtering/validation, and schema rejection are exercised by unit tests. The targeted ESLint command remains red on the unchanged `Date.now()` purity diagnostic in `billing-drawers.tsx:182`; it is unrelated to the model selector. Build warnings described above also remain non-blocking.

### Architectural Concerns

None. The model pointer exists only on `MerchantPricingPlan`; no BillingPlan model field/FK, physical plan relation, billing/subscription mutation, merchant selector, OpenRouter call, or follow-on runtime behavior was introduced.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted at Attempt 1. The implementation conforms to the ARCH-024 Merchant Pricing Plan product-tier model-assignment boundary. `commerceModelId` remains nullable durable state owned only by `MerchantPricingPlan`; the implementation does not add or copy a model pointer onto `BillingPlan`, does not create a physical MerchantPricingPlan/BillingPlan relationship, and does not expose merchant model selection.

The existing Admin builder now carries an explicit nullable `commerceModelId`. The reusable model-option helper queries enabled Catalogue Entries only through enabled global Platform Availability, validates both persisted Availability and Catalogue shapes through the published Shared `1.1.0` contracts, orders options deterministically, projects only the four UI-safe fields and fails closed for missing/disabled/non-Platform selections. No OpenRouter credential or provider execution is involved.

Create and changed update assignments are validated inside the existing catalogue-fenced `prisma.$transaction`; an unchanged now-invalid stored assignment remains preserved so unrelated plan edits can proceed and the builder renders the deterministic unavailable sentinel plus repair alert. Materialised BillingPlan synchronization remains limited to its existing billing-owned fields, plan activation/deactivation does not rewrite `commerceModelId`, and the existing `PLAN_CATALOG_CHANGED` row receives bounded before/after model IDs only when the association changes.

The submitted action-mutation coverage is source-level rather than database-backed. That is a non-blocking coverage limitation for this task: the task's prescribed Admin security suite uses this existing source-assertion style, the payload/model helpers are exercised as executable unit tests, and Architect Review independently inspected the transaction ordering and mutation branches against R6/R9-R13. No additional implementation or publication work is required.

### Reviewed Files

- `moda-interact-admin/package.json`
- `moda-interact-admin/package-lock.json`
- `moda-interact-admin/database/prisma/schema.prisma` (accepted DATABASE-001 contract / BillingPlan absence verification)
- `moda-interact-admin/src/lib/admin/merchant/pricing-builder-payload.ts`
- `moda-interact-admin/src/lib/admin/merchant/pricing-plan-model.ts`
- `moda-interact-admin/src/lib/admin/merchant/pricing-plan.ts`
- `moda-interact-admin/src/app/actions/merchant-pricing-plan.ts`
- `moda-interact-admin/src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `moda-interact-admin/src/components/admin/billing-drawers.tsx`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/tests/unit/merchant-pricing-builder-payload.test.ts`
- `moda-interact-admin/tests/unit/merchant-pricing-plan-model.test.ts`
- `moda-interact-admin/tests/security/admin-merchant-pricing-plan.test.mjs`
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`
- `docs/decisions/admin/ARCH-024/ADMIN-004-assign-commerce-model-to-merchant-pricing-plans.md`

### Validation Reviewed

Submitted evidence records:

- `npm run prisma:generate` passed against the accepted ARCH-024 database submodule;
- `npm run prisma:validate` passed;
- focused payload/model unit suite: 14 tests passed;
- `node --test tests/security/admin-merchant-pricing-plan.test.mjs`: 13 tests passed;
- targeted Prettier passed over all task-owned changed/new files;
- targeted ESLint passed for the changed TypeScript/TSX files other than the unchanged `Date.now()` `react-hooks/purity` diagnostic in `billing-drawers.tsx`;
- production build passed with the reported non-blocking BullMQ/optional Valkey warnings;
- static BillingPlan model-pointer absence check passed;
- `git diff --check` passed;
- implementation commit `2bdfb89` and parent Completion Report commit `002a1304` were reported pushed with both dedicated task worktrees clean and remote-aligned.

Architect-side review of the uploaded snapshot additionally reran the 13 Admin security regressions successfully, verified the exact `@modainteract/moda-interact-shared@1.1.0` package/lock resolution and SHARED-002 integrity, confirmed the reported `Date.now()` lint line is unchanged from the supplied pre-task baseline, and inspected the BillingPlan schema/update block for prohibited model fields. The uploaded snapshot does not contain installed `node_modules`, so Prisma generation, the TypeScript unit suite, ESLint and the production build were not rerun in the review environment.

### Architecture Conformance

Conforms. ADMIN-004 implements only the Platform-owned Merchant Pricing Plan -> Commerce model product-tier association and preserves the accepted `SHOP -> PRICING_PLAN -> PLATFORM` runtime boundary. It does not implement Availability/Catalogue/Credential administration, effective-model resolution, Background behaviour, Gateway deployment or merchant-facing model controls.

### Follow-up

No correction required. ADMIN-004 directly enables no other implementation task, so acceptance does not promote a dependant. The ARCH-024 Ready frontier remains `ARCH-024-ADMIN-001`, `ARCH-024-COMMERCE-002` and `ARCH-024-BACKGROUND-001`.
