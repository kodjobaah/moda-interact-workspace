---
id: ARCH-024-COMMERCE-002
architecture_id: ARCH-024
title: Resolve effective available and active Commerce model
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
enables:
  - ARCH-024-COMMERCE-003
  - ARCH-024-COMMERCE-005
created: 2026-09-30
updated: 2026-10-01
---

# Resolve effective available and active Commerce model

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Consume the accepted ARCH-024 database schema and published Shared model contracts, then make `moda-interact-commerce` the authoritative resolver for:

1. which enabled Model Catalogue entries are available to Platform and to a selected Shop;
2. which current subscribed `MerchantPricingPlan` applies to the Shop for model selection;
3. which single model is effectively active for that Shop in the current Commerce environment using `SHOP -> PRICING_PLAN -> PLATFORM`; and
4. whether a requested Platform/Shop model selection is valid for that selection scope.

The task must preserve the existing Agent Configuration selection model:

```text
Platform Agent Configuration
    modelId -> one Platform-available model

Merchant Pricing Plan
    commerceModelId = NULL
        -> no Price Plan override

    commerceModelId != NULL
        -> product-tier selection from Platform availability only

Shop Agent Configuration
    modelId = NULL
        -> no explicit Shop override; resolve Price Plan then Platform

    modelId != NULL
        -> explicit Shop selection
           from Platform availability
           OR that exact Shop's availability
```

A broken explicit Shop selection MUST resolve `UNAVAILABLE`; it MUST NOT inspect Price Plan/Platform fallback. A broken explicit Price Plan selection MUST also resolve `UNAVAILABLE`; it MUST NOT silently downgrade to Platform.

## Context

The integrated baseline currently treats `CommerceModelCatalogueEntry` as a global catalogue.

Current reads effectively do:

```text
list every enabled catalogue row
```

and current `ModelConfigurationService.setModel(...)` checks only:

```text
model exists
model.enabled = true
```

It does not validate Model Availability.

Current `resolveEffectiveConfiguration(...)` also validates only the selected model's `enabled` flag. In addition, the old implementation first requires a valid Platform model and only then considers a Shop override. There is no current Price Plan model tier between Shop and Platform.

ARCH-024 changes the model boundary:

```text
CommerceModelAvailability(scope=PLATFORM)
        1
        |
        *
CommerceModelCatalogueEntry

CommerceModelAvailability(scope=SHOP, shopId=S)
        1
        |
        *
CommerceModelCatalogueEntry
```

For selected Shop `S`:

```text
EffectiveAvailableModels(S)
    = enabled entries in enabled PLATFORM availability
      UNION
      enabled entries in enabled SHOP availability for S
```

There is no merchant-side model selector. Commerce Studio remains the only model-selection UI, and ARCH-024-COMMERCE-003 will simplify that UI after this service/domain task is accepted.

This task deliberately separates **availability** from **selection**:

```text
Availability
    what may be selected

Agent Configuration
    explicit Platform/Shop selection

MerchantPricingPlan.commerceModelId
    optional product-tier selection

Effective active model
    explicit valid Shop selection when present
    otherwise current Price Plan selection when configured
    otherwise valid Platform selection
```

The accepted Shared package owns the canonical runtime-safe schemas under:

```text
@modainteract/moda-interact-shared/commerce/model
```

Do not recreate local `OPENAI | GROQ` unions or duplicate Shared model validators.

ARCH-023 is frozen. This task MUST NOT alter Platform/Shop Instruction or prompt semantics. Only the model side of effective Agent Configuration is changed here.

## Scope

Primary implementation targets:

```text
moda-interact-commerce/database/                                  # consume accepted ARCH-024 DATABASE-001 gitlink only
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json

moda-interact-commerce/src/commerce/agent-configuration/model-availability.ts          # NEW
moda-interact-commerce/src/commerce/agent-configuration/pricing-plan-model.ts           # NEW
moda-interact-commerce/src/commerce/agent-configuration/model-service.ts
moda-interact-commerce/src/commerce/agent-configuration/effective-configuration.ts

moda-interact-commerce/src/studio/agent-configuration/model-contracts.ts
moda-interact-commerce/src/studio/agent-configuration/effective-contracts.ts
moda-interact-commerce/src/studio/agent-configuration/model-server-actions.ts

moda-interact-commerce/tests/agent-configuration-model-availability.test.ts             # NEW
moda-interact-commerce/tests/agent-configuration-effective.test.ts
moda-interact-commerce/tests/agent-configuration-reduced.test.ts
moda-interact-commerce/tests/agent-configuration-model-postgres.test.ts

moda-interact-commerce/scripts/run-arch024-model-resolution-disposable.mjs              # NEW
```

Additional files may be changed only when required to consume the accepted Database/Shared dependencies or to keep current Commerce compilation/tests valid. Every additional file must be listed and justified in the Completion Report.

### Dependency consumption

This task MUST:

1. update the nested `database/` gitlink to the architect-accepted, merged ARCH-024-DATABASE-001 database commit through the normal repository-task workflow;
2. update `@modainteract/moda-interact-shared` to the **exact version published by ARCH-024-SHARED-002**;
3. update the Commerce lockfile using the normal package manager;
4. run Prisma generation from the accepted nested database schema.

Do not edit the nested database schema in this task.

Do not use a local Shared checkout, npm link, file dependency or workspace borrowing in place of the published SHARED-002 package.

## Out of Scope

- Commerce Studio React model-selection cleanup; ARCH-024-COMMERCE-003 owns it.
- Admin Model Catalogue or Availability authoring.
- OpenRouter credential lookup/decryption.
- `OpenRouterModelClient` construction or model invocation.
- Test Conversation Feature composition.
- Test Conversation UI.
- Tool execution.
- Background production model execution.
- Gateway/environment configuration.
- Merchant-facing model selection; merchants do not select models.
- Changing Platform/Shop Instruction or prompt resolution semantics from frozen ARCH-023.
- Adding a second active-model table, active flag or selection record.
- Silently clearing an invalid explicit Agent Configuration selection.
- Deduplicating two different catalogue entries merely because they share `provider + providerModelId` across different Availabilities.

## Requirements

### R1 — Consume only the canonical Shared model contracts

Replace Commerce-local model identity/environment unions with imports from:

```text
@modainteract/moda-interact-shared/commerce/model
```

Use at minimum these published exports where applicable:

```text
COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
CommerceEnvironment
CommerceEnvironmentSchema
CommerceModelAvailability
CommerceModelAvailabilitySchema
CommerceModelCatalogueEntry
CommerceModelCatalogueEntrySchema
CommerceModelProvider
CommerceProviderModelId
ResolvedCommerceModel
ResolvedCommerceModelSchema
CommerceModelSelectionSource
CommerceModelSelectionSourceSchema
CommercePricingPlanModelAssignment
CommercePricingPlanModelAssignmentSchema
```

The Commerce repository MUST NOT retain or introduce:

```ts
type ModelProvider = 'OPENAI' | 'GROQ';
```

or another closed provider allowlist.

The existing Commerce environment parsing may remain local, but it must validate through `CommerceEnvironmentSchema` rather than maintaining a second environment enum/list.

### R2 — Add the authoritative local available-model read shape exactly

In `src/studio/agent-configuration/model-contracts.ts`, define/export:

```ts
export type AvailableCommerceModel = {
  availability: CommerceModelAvailability;
  model: CommerceModelCatalogueEntry;
};
```

Do not flatten Availability metadata into the model and do not add credentials.

Do not deduplicate `AvailableCommerceModel` rows by provider/model identity. Distinct catalogue entry IDs are distinct selectable configurations even when they point to the same underlying OpenRouter model.

### R3 — Add `model-availability.ts` with exactly three domain operations

Create:

```text
src/commerce/agent-configuration/model-availability.ts
```

It MUST export exactly these domain functions:

```ts
export async function listPlatformAvailableModels(input: {
  db: PrismaClient | Prisma.TransactionClient;
}): Promise<AvailableCommerceModel[]>;

export async function listEffectiveAvailableModels(input: {
  db: PrismaClient | Prisma.TransactionClient;
  shopId: string;
}): Promise<AvailableCommerceModel[]>;

export async function assertModelSelectable(input: {
  db: PrismaClient | Prisma.TransactionClient;
  modelId: string;
  selectionScope: 'PLATFORM' | 'SHOP';
  shopId: string | null;
}): Promise<AvailableCommerceModel>;
```

Do not place Admin mutation logic or Agent Configuration writes in this module.

### R4 — Platform available-model query semantics are exact

`listPlatformAvailableModels(...)` must consider only:

```text
CommerceModelAvailability.scope   = PLATFORM
CommerceModelAvailability.shopId  = NULL
CommerceModelAvailability.enabled = true
CommerceModelCatalogueEntry.enabled = true
```

The query must include the Availability row and Catalogue Entry rows in one bounded Prisma read/query plan.

Each returned Availability and Catalogue Entry must be validated using the published Shared schemas before being returned.

A structurally invalid row must not become selectable. Fail the operation with the existing bounded Commerce `UNAVAILABLE`/database-unavailable error boundary rather than returning unvalidated data.

Return ordering is exact:

```text
1. displayName ascending
2. provider ascending
3. providerModelId ascending
4. model.id ascending
```

Do not perform locale-dependent sorting in JavaScript when Prisma/database ordering can satisfy this contract.

### R5 — Effective Shop availability is the exact union of Platform + exact Shop scope

For Shop `S`, `listEffectiveAvailableModels(...)` must return only enabled entries from enabled Availabilities matching:

```text
scope = PLATFORM AND shopId IS NULL

OR

scope = SHOP AND shopId = S
```

Before returning the list, verify that `commerce.Shop.id = S` exists. A missing Shop is `NOT_FOUND`; do not treat it as a Shop with Platform-only availability.

Return ordering is exact:

```text
1. Platform-availability entries
2. Shop-availability entries

within each group:
    displayName ascending
    provider ascending
    providerModelId ascending
    model.id ascending
```

Do not deduplicate a Shop-specific entry against a Platform entry with the same `provider + providerModelId`.

Disabled Availability rows and disabled Catalogue Entry rows are omitted.

### R6 — `assertModelSelectable(...)` is the single write-time availability gate

All Platform/Shop Agent Configuration model-selection writes in this repository must call `assertModelSelectable(...)` before updating `CommerceAgentConfiguration.modelId`.

Load the target Catalogue Entry with its Availability and validate both through Shared schemas.

For `selectionScope = 'PLATFORM'`, selection is valid only when all are true:

```text
model exists
model.enabled = true
availability exists
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = null
```

For `selectionScope = 'SHOP'` and exact Shop `S`, selection is valid only when all are true:

```text
Shop S exists
model exists
model.enabled = true
availability exists
availability.enabled = true
and either:
    availability.scope = PLATFORM
    availability.shopId = null
or:
    availability.scope = SHOP
    availability.shopId = S
```

A model belonging to another Shop is invalid even if the caller knows its ID.

Failure mapping is exact:

```text
missing Shop                     -> NOT_FOUND
missing model                    -> NOT_FOUND
invalid Shared model/config row  -> INVALID_INPUT
model disabled                   -> INVALID_INPUT
availability disabled            -> INVALID_INPUT
wrong availability scope/shop    -> INVALID_INPUT
```

Do not query or require an OpenRouter credential here. Availability/selection is valid independently of current provider credential status.

### R6A — Resolve the current Price Plan model assignment from verified local subscription state

Create:

```text
src/commerce/agent-configuration/pricing-plan-model.ts
```

Export exactly:

```ts
export type CurrentPricingPlanModelAssignment = {
  merchantPricingPlanId: string;
  shopifyPlanHandle: string;
  modelId: string | null;
};

export async function resolveCurrentPricingPlanModelAssignment(input: {
  db: PrismaClient | Prisma.TransactionClient;
  shopId: string;
}): Promise<CurrentPricingPlanModelAssignment | null>;
```

Resolution is exact:

1. load the Shop's unique `Subscription`;
2. only `Subscription.status IN (ACTIVE, TRIALING)` is eligible;
3. require current `Subscription.planId` and current `Subscription.plan`;
4. read current `BillingPlan.shopifyPlanHandle`;
5. ignore `pendingPlanId`, `pendingPlan` and `pendingShopifyPlanHandle`;
6. find `MerchantPricingPlan` by the exact same unique `shopifyPlanHandle`;
7. when no eligible Subscription/current plan or no matching `MerchantPricingPlan` exists, return `null`;
8. when the matching Price Plan exists, validate `{ merchantPricingPlanId, shopifyPlanHandle, modelId }` with the published `CommercePricingPlanModelAssignmentSchema` and return it.

Do **not** require `MerchantPricingPlan.isActive = true`. Catalogue activation controls whether the plan may be newly sold; an existing subscriber retains the current plan's configured model benefit until billing changes the current plan.

Do not infer a Price Plan from catalogue position, recurring amount, pending selection or Feature set. Do not read a merchant-supplied plan handle.

### R6B — A Price Plan model is selectable only from Platform Availability

When `CurrentPricingPlanModelAssignment.modelId != null`, load that exact Catalogue Entry with its Availability. It is valid only when all are true:

```text
model exists
model validates through Shared schema
model.enabled = true
availability exists
availability validates through Shared schema
availability.enabled = true
availability.scope = PLATFORM
availability.shopId = null
```

A Price Plan is multi-tenant product configuration and MUST NOT select a Shop-availability entry.

If the explicit `commerceModelId` is missing, malformed, disabled, assigned to disabled Availability or no longer Platform-available, effective resolution is `UNAVAILABLE`. Do not clear the Price Plan association and do not fall back to Platform.

If `modelId = null`, there is no Price Plan override and effective resolution may continue to Platform.

### R7 — Effective model resolution uses exact `SHOP -> PRICING_PLAN -> PLATFORM` precedence

Update only the **model** branch of `resolveEffectiveConfiguration(...)`.

Prompt/Instruction resolution is outside this task and must preserve the current/frozen behaviour until the owning ARCH-023 integration changes it.

The exact model algorithm for selected Shop `S` and environment `E` is:

```text
load Shop Agent Configuration for (E, S)

IF Shop configuration exists AND shop.modelId IS NOT NULL:
    resolve that exact Shop-selected model
    IF valid for Shop S:
        winner = SHOP
    ELSE:
        return UNAVAILABLE
        DO NOT inspect Price Plan or Platform

ELSE:
    resolveCurrentPricingPlanModelAssignment(S)

    IF matching current Price Plan exists AND plan.modelId IS NOT NULL:
        validate that exact Price Plan-selected model as PLATFORM-available
        IF valid:
            winner = PRICING_PLAN
        ELSE:
            return UNAVAILABLE
            DO NOT inspect Platform

    ELSE:
        load Platform Agent Configuration for E
        resolve Platform modelId
        IF valid Platform selection:
            winner = PLATFORM
        ELSE:
            return UNAVAILABLE
```

A valid explicit Shop model remains authoritative even if Price Plan/Platform configuration is missing or broken. A valid Price Plan model remains authoritative even if Platform configuration is missing or broken. Platform is used only when there is neither an explicit Shop override nor an explicit current Price Plan model assignment.

Changing the current subscription plan or Price Plan model association affects the next effective-resolution transaction; it MUST NOT change a model already captured for an in-progress Test Conversation/turn.

This differs intentionally from the old ARCH-021 implementation, which had only Shop/Platform selection and first required a valid Platform model baseline before considering the Shop override.

### R8 — Effective resolution validates current Availability every time

The effective resolver must load the selected Catalogue Entry **with its current Availability** inside the same existing `REPEATABLE READ` transaction used for Agent Configuration resolution.

A selected model is effective only when:

```text
Catalogue Entry validates against Shared schema
Catalogue Entry enabled = true
Availability validates against Shared schema
Availability enabled = true
selection is allowed for its selection source:
    SHOP      -> R6 Shop rules
    PRICING_PLAN -> R6B Platform-only Price Plan rule
    PLATFORM  -> R6 Platform rules
```

This ensures Admin changes take effect without rewriting Agent Configuration:

```text
Admin disables selected model
    -> explicit selection remains durable
    -> next resolution = UNAVAILABLE

Admin disables/moves selected Availability
    -> explicit selection remains durable
    -> next resolution = UNAVAILABLE

Admin moves Shop-selected model to another Shop
    -> explicit selection remains durable
    -> next resolution = UNAVAILABLE

Admin disables/reassigns Price Plan-selected model away from Platform Availability
    -> Price Plan `commerceModelId` remains durable
    -> next resolution = UNAVAILABLE
```

Do not clear `CommerceAgentConfiguration.modelId` or `MerchantPricingPlan.commerceModelId` automatically.

### R9 — Effective-model contract preserves selection, Price Plan and Availability provenance

Update `src/studio/agent-configuration/effective-contracts.ts` so `EffectiveModel` is exactly:

```ts
export type EffectiveModelUnavailableReason =
  | 'MODEL_NOT_SELECTED'
  | 'SELECTED_MODEL_NOT_FOUND'
  | 'SELECTED_MODEL_INVALID'
  | 'SELECTED_MODEL_DISABLED'
  | 'SELECTED_AVAILABILITY_INVALID'
  | 'SELECTED_AVAILABILITY_DISABLED'
  | 'SELECTED_MODEL_NOT_AVAILABLE_FOR_SCOPE';

export type EffectiveModel = {
  source: 'SHOP' | 'PRICING_PLAN' | 'PLATFORM' | 'UNAVAILABLE';
  selectionSource: CommerceModelSelectionSource;
  environment: CommerceEnvironment;
  selectionEditVersion: number | null;
  shopId: string | null;
  merchantPricingPlanId: string | null;
  shopifyPlanHandle: string | null;
  reason: EffectiveModelUnavailableReason | null;
  availability: CommerceModelAvailability | null;
  model: ResolvedCommerceModel | null;
};
```

Semantics are exact:

```text
source
    effective result provenance; AVAILABLE -> SHOP | PRICING_PLAN | PLATFORM
    unavailable -> UNAVAILABLE

selectionSource
    authoritative selection tier for this resolution attempt
    if an explicit Shop selection fails -> SHOP
    if an explicit current Price Plan selection fails -> PRICING_PLAN
    if Platform fallback/missing Platform selection fails -> PLATFORM
    `source = UNAVAILABLE` does not erase the tier that failed

selectionEditVersion
    SHOP/PLATFORM -> CommerceAgentConfiguration.modelEditVersion
    PRICING_PLAN  -> null (MerchantPricingPlan uses the billing catalogue transaction/revision fence)

shopId
    selected Shop ID for SHOP or PRICING_PLAN; null for PLATFORM

merchantPricingPlanId / shopifyPlanHandle
    non-null only when selectionSource = PRICING_PLAN

availability
    Availability containing the selected Catalogue Entry

model.sourceScope / model.sourceShopId
    Availability provenance of the selected Catalogue Entry
```

For a Shop override that explicitly selects a Platform-available entry:

```text
EffectiveModel.source          = SHOP
EffectiveModel.selectionSource = SHOP
EffectiveModel.shopId          = selected Shop
merchantPricingPlanId          = null
ResolvedCommerceModel.sourceScope  = PLATFORM
ResolvedCommerceModel.sourceShopId = null
```

For a Price Plan winner:

```text
EffectiveModel.source          = PRICING_PLAN
EffectiveModel.selectionSource = PRICING_PLAN
EffectiveModel.shopId          = selected Shop
merchantPricingPlanId          = current MerchantPricingPlan.id
shopifyPlanHandle              = current BillingPlan/MerchantPricingPlan handle
selectionEditVersion           = null
ResolvedCommerceModel.sourceScope  = PLATFORM
ResolvedCommerceModel.sourceShopId = null
```

This distinction is mandatory.

### R10 — Map selected model rows into `ResolvedCommerceModel` exactly

For a valid selected Catalogue Entry + Availability, produce:

```ts
{
  environment,
  sourceScope: availability.scope,
  sourceShopId: availability.scope === 'SHOP' ? availability.shopId : null,
  catalogueEntryId: model.id,
  provider: model.provider,
  providerModelId: model.providerModelId,
  configurationSchemaVersion: model.configurationSchemaVersion,
  configuration: model.configuration,
}
```

Validate the final object with `ResolvedCommerceModelSchema` before returning it.

Do not include:

```text
OpenRouter credential
ciphertext
nonce
authTag
keyId
```

### R11 — Preserve one repeatable-read effective model transaction boundary

`resolveEffectiveConfiguration(...)` must continue to execute model and prompt/instruction reads inside one Prisma `REPEATABLE READ` transaction.

Do not split effective model and prompt reads across transactions.

The task may refactor internal helper functions but must preserve one coherent snapshot for the returned `EffectiveAgentConfiguration`.

### R12 — Harden `ModelConfigurationService.setModel(...)` with Availability validation

Before any `CommerceAgentConfiguration.modelId` write:

```text
setPlatformModel
setShopModel
```

call `assertModelSelectable(...)` within the same Prisma transaction as the Agent Configuration write and immutable audit receipt.

Use:

```text
selectionScope = PLATFORM, shopId = null
```

for Platform selection and:

```text
selectionScope = SHOP, shopId = request.shopId
```

for Shop selection.

The selection validation and `modelId` write must therefore observe one transaction snapshot.

Continue using the existing CAS field:

```text
CommerceAgentConfiguration.modelEditVersion
```

Do not change existing operation-ID reconciliation/audit semantics.

`clearShopModel(...)` remains the only operation that deliberately sets Shop `modelId = NULL`.

### R13 — Add read methods for later Commerce Studio selection UI

Extend the existing model service/port with exactly:

```ts
listPlatformAvailableModels(
  principal: StudioAdminPrincipal,
): Promise<AvailableCommerceModel[]>;

listEffectiveAvailableModels(
  principal: StudioAdminPrincipal,
  shopId: string,
): Promise<AvailableCommerceModel[]>;
```

Both use the existing read authorization path and delegate to `model-availability.ts`.

Add server actions with exactly these exported names:

```ts
export async function listPlatformAvailableModels();

export async function listEffectiveAvailableModels(
  shopId: string,
);
```

These are the read APIs ARCH-024-COMMERCE-003 must consume.

Do not add a merchant/public API.

### R14 — Keep current Catalogue-management API only as a temporary compile bridge

ARCH-024-COMMERCE-003 owns removal of Commerce Studio Catalogue administration. Until that task, the current Catalogue-management service/actions/components must continue to compile against the ARCH-024 schema.

Make only these bounded compatibility changes:

1. local `ModelProvider` types become the Shared dynamic provider string type;
2. `CatalogueRow` / `toCatalogueEntry(...)` include and validate:

```text
availabilityId
provider
providerModelId
displayName
description
configurationSchemaVersion
configuration
enabled
editVersion
```

3. legacy `createCatalogueEntry(...)`, while it still exists, may create **only** inside the deterministic bootstrap Platform Availability:

```text
arch024-platform-model-availability
```

and must create with:

```text
configurationSchemaVersion = COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
configuration = {}
```

4. legacy creation validates the dynamic provider with the Shared provider schema;
5. legacy update/enable operations preserve `availabilityId`, provider/model identity and configuration unchanged.

Do NOT add Shop Availability authoring, Availability reassignment or arbitrary configuration editing to Commerce Studio as compatibility work. Those are Admin-owned.

Do NOT broaden the current legacy Model Catalogue UI in this task. ARCH-024-COMMERCE-003 removes it.

### R15 — No credential/runtime-provider dependency enters model resolution

This task MUST NOT read:

```text
CommerceOpenRouterCredential
COMMERCE_PREVIEW_API_KEY
OPENROUTER_API_KEY
```

and MUST NOT instantiate:

```text
OpenRouterModelClient
ChatOpenRouter
```

A model can be correctly selected/effective even when its runtime credential is currently absent. Credential/runtime availability is owned by later ARCH-024 Commerce/Background tasks.

### R16 — Focused PostgreSQL proof is mandatory

Extend/create the PostgreSQL model test so it proves actual Prisma/schema behaviour for all of these cases:

1. Platform available list contains only enabled entries in enabled Platform Availability.
2. Shop effective list returns Platform entries followed by exact-Shop entries.
3. Another Shop's private entries are absent.
4. Disabled Availability entries are absent.
5. Disabled Catalogue Entries are absent.
6. Two different Catalogue Entries with the same `provider + providerModelId` in Platform and Shop Availability are both returned; no deduplication occurs.
7. Platform selection accepts a Platform entry.
8. Platform selection rejects a Shop entry.
9. Shop selection accepts a Platform entry.
10. Shop selection accepts an entry from that exact Shop Availability.
11. Shop selection rejects an entry from another Shop Availability.
12. Shop selection rejects disabled model/availability.
13. Explicit valid Shop selection resolves even when Price Plan/Platform selection is missing or broken.
14. Shop `modelId = null` plus ACTIVE/TRIALING current subscription and Price Plan `commerceModelId` resolves the valid Price Plan model.
15. Price Plan model must be in enabled Platform Availability; a Shop-availability model is rejected.
16. Broken explicit Price Plan model resolves `UNAVAILABLE` and never falls back to Platform.
17. `pendingPlanId`/pending handle does not affect the winner until it becomes current.
18. Changing current `Subscription.planId` from lower to higher plan changes the next resolution to the higher plan's configured model.
19. A matching inactive `MerchantPricingPlan` still supplies its model to an existing current subscriber.
20. No matching MerchantPricingPlan or matching plan with `commerceModelId = NULL` falls through to the valid Platform model.
21. Broken explicit Shop selection resolves `UNAVAILABLE` and never falls back to Price Plan/Platform.
22. Reassigning/disabling the selected entry/Availability leaves the durable Agent/Price Plan pointer but makes the next effective resolution `UNAVAILABLE`.
23. Platform selection becomes `UNAVAILABLE` when its selected model is no longer Platform-available.
24. No credential row is required for any availability/selection/resolution scenario.

Do not run these cases against a developer/shared database.

### R17 — Add a deterministic disposable PostgreSQL runner

Create:

```text
scripts/run-arch024-model-resolution-disposable.mjs
```

It must follow the repository's existing disposable-Docker safety pattern and:

1. use `postgres:16.4-alpine`;
2. create a unique run ID and Docker ownership label;
3. create a dedicated Docker network and PostgreSQL container;
4. bind PostgreSQL only to `127.0.0.1` on an ephemeral host port;
5. use a tmpfs PostgreSQL data directory;
6. wait for `pg_isready`;
7. construct a loopback disposable `COMMERCE_TEST_DATABASE_URL`;
8. run Prisma `db push` using `database/prisma/schema.prisma`;
9. run exactly the focused ARCH-024 PostgreSQL test file;
10. remove the owned container/network in `finally`;
11. verify no resource bearing the run ownership label remains;
12. redact database URLs/passwords from output on failure.

Add package script:

```json
"test:arch024-model-resolution:postgres": "node scripts/run-arch024-model-resolution-disposable.mjs"
```

Do not reuse an existing non-disposable database target.

## Work Items

- [x] Consume the architect-accepted ARCH-024 database gitlink without editing nested schema.
- [x] Consume the exact SHARED-002 published package version and synchronized lockfile.
- [x] Replace local closed provider/environment contract duplication with canonical Shared model contracts.
- [x] Add `AvailableCommerceModel`.
- [x] Add `model-availability.ts` with the exact three domain functions from R3.
- [x] Add `pricing-plan-model.ts` with the exact current-subscription/Price Plan assignment resolver from R6A.
- [x] Implement deterministic Platform/effective Shop availability queries.
- [x] Add the single write-time `assertModelSelectable(...)` gate.
- [x] Harden Platform/Shop model selection mutations with the availability gate inside their write transaction.
- [x] Change effective model resolution to exact `SHOP -> PRICING_PLAN -> PLATFORM` semantics, using only current ACTIVE/TRIALING subscription state and ignoring pending plan state.
- [x] Validate selected model and Availability on every effective resolution.
- [x] Add the R9 effective-model provenance/error contract including `PRICING_PLAN`, plan ID and plan handle provenance.
- [x] Preserve the existing repeatable-read effective Agent Configuration transaction.
- [x] Add Platform/effective Shop available-model service methods and Server Actions for COMMERCE-003.
- [x] Apply only the R14 legacy Catalogue compatibility changes needed until COMMERCE-003 removes that UI.
- [x] Add/update focused unit tests.
- [x] Add/update focused PostgreSQL tests.
- [x] Add the disposable PostgreSQL runner and package script.
- [x] Run all required Validation and record exact results.

## Interfaces / Contracts

### Consumed Shared package

```text
@modainteract/moda-interact-shared/commerce/model
```

The exact package version is the version recorded as successfully published by `ARCH-024-SHARED-002`.

### Commerce-local available model

```ts
type AvailableCommerceModel = {
  availability: CommerceModelAvailability;
  model: CommerceModelCatalogueEntry;
};
```

### Effective model

```ts
type EffectiveModelUnavailableReason =
  | 'MODEL_NOT_SELECTED'
  | 'SELECTED_MODEL_NOT_FOUND'
  | 'SELECTED_MODEL_INVALID'
  | 'SELECTED_MODEL_DISABLED'
  | 'SELECTED_AVAILABILITY_INVALID'
  | 'SELECTED_AVAILABILITY_DISABLED'
  | 'SELECTED_MODEL_NOT_AVAILABLE_FOR_SCOPE';

type EffectiveModel = {
  source: 'SHOP' | 'PRICING_PLAN' | 'PLATFORM' | 'UNAVAILABLE';
  selectionSource: CommerceModelSelectionSource;
  environment: CommerceEnvironment;
  selectionEditVersion: number | null;
  shopId: string | null;
  merchantPricingPlanId: string | null;
  shopifyPlanHandle: string | null;
  reason: EffectiveModelUnavailableReason | null;
  availability: CommerceModelAvailability | null;
  model: ResolvedCommerceModel | null;
};
```

### Available-model server actions

```ts
listPlatformAvailableModels()
listEffectiveAvailableModels(shopId)
```

No public merchant route is produced.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`

COMMERCE-001 is intentionally **not** a dependency. It owns subtractive human Preview/Test-Conversations UI cleanup, while this task owns database-backed model resolution and can execute independently once Database + Shared are published.

## Enables

- `ARCH-024-COMMERCE-003`
- `ARCH-024-COMMERCE-005`

## Acceptance Criteria

- [x] Commerce consumes the accepted ARCH-024 database schema through its nested database gitlink.
- [x] Commerce consumes the exact published SHARED-002 package version rather than a local Shared checkout.
- [x] No Commerce-local `OPENAI | GROQ` provider union remains in the model-selection/resolution boundary.
- [x] Platform available-model reads return only valid enabled Platform entries from enabled Platform Availability.
- [x] Effective Shop available-model reads equal Platform entries plus exact-Shop entries and exclude every other Shop.
- [x] Effective available-model reads never deduplicate two distinct catalogue IDs.
- [x] Platform selection cannot select a Shop-only catalogue entry.
- [x] Shop selection may select a Platform entry or exact-Shop entry and cannot select another Shop's entry.
- [x] Disabled/invalid model or Availability cannot be newly selected.
- [x] A Shop with a valid explicit override uses that model even if Price Plan/Platform configuration is missing or broken.
- [x] A Shop with `modelId = NULL` and an explicit current Price Plan model uses the valid Price Plan model before Platform.
- [x] A current Price Plan model may reference only enabled Platform Availability; a broken explicit plan model returns `UNAVAILABLE` and does not fall back to Platform.
- [x] With no explicit Shop override and no explicit usable Price Plan model, the Shop inherits the valid Platform model.
- [x] Pending subscription plans do not affect model selection until current.
- [x] A broken explicit Shop override returns `UNAVAILABLE` and does not inspect Price Plan/Platform fallback.
- [x] Availability/model changes can invalidate an existing selection without clearing or rewriting the durable `modelId`.
- [x] Effective resolution preserves `SHOP | PRICING_PLAN | PLATFORM` selection provenance separately from catalogue Availability provenance and includes Price Plan ID/handle only for plan selection.
- [x] Effective Agent Configuration still uses one repeatable-read snapshot.
- [x] Prompt/Instruction resolution semantics are unchanged by this task.
- [x] Model resolution does not query credentials or invoke OpenRouter/LangChain.
- [x] The temporary legacy Catalogue compatibility path does not add Shop Availability/configuration authoring to Commerce Studio.
- [x] Focused unit tests pass.
- [x] Focused disposable PostgreSQL proof passes and cleans up all owned Docker resources.
- [x] Changed-file diagnostics, lint/typecheck and `git diff --check` pass.

## Validation

Before Node commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Inspect `package.json` before running validation. Use the repository's actual scripts.

Required minimum validation:

```bash
npm run prisma:generate

npx vitest run \
  tests/agent-configuration-model-availability.test.ts \
  tests/agent-configuration-effective.test.ts \
  tests/agent-configuration-reduced.test.ts \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-server-actions.test.ts

npm run test:arch024-model-resolution:postgres

npx eslint \
  src/commerce/agent-configuration/model-availability.ts \
  src/commerce/agent-configuration/pricing-plan-model.ts \
  src/commerce/agent-configuration/model-service.ts \
  src/commerce/agent-configuration/effective-configuration.ts \
  src/studio/agent-configuration/model-contracts.ts \
  src/studio/agent-configuration/effective-contracts.ts \
  src/studio/agent-configuration/model-server-actions.ts \
  tests/agent-configuration-model-availability.test.ts \
  tests/agent-configuration-effective.test.ts \
  tests/agent-configuration-reduced.test.ts \
  tests/agent-configuration-model-postgres.test.ts \
  scripts/run-arch024-model-resolution-disposable.mjs

npm run typecheck

git diff --check
```

If this task changes a file not listed in the targeted ESLint command, include that changed TypeScript/JavaScript file in targeted ESLint as well.

A full production build is not required unless the changed dependency/package/export state causes typecheck to pass while build integration remains uncertain or the implementing agent observes a build-specific problem. If run, record the exact result.

The PostgreSQL proof is required and may not be replaced by mocked Prisma tests.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect`, and STOP.

Do not begin ARCH-024-COMMERCE-003 or any other enabled/follow-on task.

## Implementation Notes

- Treat `source`/`selectionSource` as **effective selection provenance** (`SHOP | PRICING_PLAN | PLATFORM`) and `ResolvedCommerceModel.sourceScope/sourceShopId` as **Catalogue Availability provenance**.
- Do not make lower-precedence configuration a prerequisite for a valid higher-precedence winner. Shop override is highest; Price Plan is considered only when Shop `modelId` is null/absent; Platform is considered only when neither higher tier has an explicit model.
- Resolve current Price Plan through trusted `Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle`; never use `pendingPlanId` or browser/provider callback input directly.
- The bootstrap Platform Availability ID from DATABASE-001 is:

```text
arch024-platform-model-availability
```

and may be used only for the temporary R14 legacy create compatibility path. Normal availability reads must query by scope, not hard-code the bootstrap ID.
- C003 will remove the legacy Commerce Studio Model Catalogue authoring surface. Do not expand that surface here.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `database/` nested gitlink advanced to accepted schema commit `cfeeb12`; nested schema was not edited.
- `package.json`, `package-lock.json`: consume Shared `1.1.0` and register the focused disposable PostgreSQL script.
- `src/commerce/agent-configuration/model-availability.ts` (new): Shared-validated Availability queries, database ordering, and the single selection gate.
- `src/commerce/agent-configuration/pricing-plan-model.ts` (new): trusted current ACTIVE/TRIALING subscription-to-Price-Plan resolution.
- `src/commerce/agent-configuration/effective-configuration.ts`: Shop, Price Plan, Platform precedence and model/Availability provenance in the existing repeatable-read transaction; prompt resolution is unchanged.
- `src/commerce/agent-configuration/model-service.ts`: transactional selection gate, available-model reads, Shared-schema catalogue compatibility, nullable selection reads, and bounded database-failure logging.
- `src/studio/agent-configuration/model-contracts.ts`, `effective-contracts.ts`, `model-server-actions.ts`: canonical model contracts, effective provenance, and authorized read actions.
- `tests/agent-configuration-model-availability.test.ts` (new), `agent-configuration-effective.test.ts`, `agent-configuration-reduced.test.ts`, `agent-configuration-model.test.ts`: focused behavior and regression coverage.
- `tests/agent-configuration-model-postgres.test.ts`: real Prisma proof for Availability, exact scopes, precedence, pending/current plans, durable invalid pointers, and credential independence.
- `scripts/run-arch024-model-resolution-disposable.mjs` (new): isolated, labeled, loopback-only PostgreSQL provisioning and verified cleanup.
- Attempt 2 A1-R1 changes: `src/commerce/agent-configuration/model-service.ts`, `tests/agent-configuration-model.test.ts`, and `tests/agent-configuration-model-postgres.test.ts`.

### Work Completed

- Implementation committed and pushed on `task/ARCH-024-COMMERCE-002` at `1f9a462`.
- Implemented Platform and exact-Shop Availability reads with strict Shared-schema projection and database-side ordering; distinct catalogue IDs remain distinct even when provider identities match.
- Enforced Platform/Shop selectability within the same mutation transaction as configuration writes and audit receipts.
- Resolved current subscription benefits from `Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan`, ignoring pending plans and allowing inactive plans for existing eligible subscribers.
- Implemented fail-closed effective model precedence `SHOP -> PRICING_PLAN -> PLATFORM` while preserving one `RepeatableRead` transaction and frozen prompt behavior.
- Added effective selection and Availability provenance, authorized Platform/Shop model-read service methods, and their Server Actions.
- Added the temporary deterministic Platform Availability catalogue-create bridge using canonical Shared provider/configuration contracts.
- Added a task-owned PostgreSQL runner using `postgres:16.4-alpine`, unique ownership labels, a dedicated network, ephemeral loopback publishing, tmpfs storage, redaction, and cleanup verification.
- A1-R1 correction: legacy `createCatalogueEntry(...)` now reads only the migration-owned `arch024-platform-model-availability`, validates the complete row with the published Shared schema and requires `PLATFORM` scope with null `shopId`. Missing or invalid bootstrap availability fails through the bounded retryable `DATABASE_UNAVAILABLE` result and cannot be recreated by production Commerce code. Added a unit regression asserting the row remains absent and no Catalogue/audit write occurs; the real-PostgreSQL fixture now seeds the migration-owned Availability explicitly after schema setup, as test-only fixture state.
- Attempt 2 implementation commit `f7cf6deb0e108bc5d70a055db6283441503d7dc7` (`fix(commerce): preserve migration-owned availability`) was pushed to `origin/task/ARCH-024-COMMERCE-002`.
- Attempt 2 launcher evidence: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-COMMERCE-002`, branch `task/ARCH-024-COMMERCE-002`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-COMMERCE-002`, branch `task/ARCH-024-COMMERCE-002`. Both canonical task worktrees were reused; the shared workspace and implementation source checkouts were not switched or mutated for task work, and no other task worktree was reused.
- Attempt 2 start synchronization: parent remote task branch fast-forward `not-needed`, parent `origin/main` incorporation `yes`; implementation remote task branch fast-forward `not-needed`, implementation `origin/main` incorporation `already-current`.
- Attempt 2 launcher claim: Attempt 2, executor `copilot`, claimed at `2026-10-01T18:33:40Z`; durable parent claim commit `3334f66aa1684b612b1ce0b3291e3bc9ff44d783` was pushed. Dependency gate passed for `ARCH-024-DATABASE-001` and `ARCH-024-SHARED-002`, both `complete`.
- Attempt 2 recursive submodules: `git submodule sync --recursive` and `git submodule update --init --recursive` passed; recursive status `ready`; accepted `database/` commit `cfeeb12456b4e05067a96857a8c47837d7e33bbd` initialized.
- Attempt 2 parent Completion Report commit `c155b6c7493312fbdada66231418f8f191ea1a3b` was pushed to `origin/task/ARCH-024-COMMERCE-002`. After publication, both parent and implementation worktrees were verified on `task/ARCH-024-COMMERCE-002`, up to date with their respective origin task branches, with clean working trees.

### Validation Results

- `npm run prisma:generate`: PASS; Prisma Client v6.19.3 generated from the accepted schema.
- Required focused Vitest set (Availability, effective resolution, reduced mode, model UI, Server Actions): PASS, 5 files / 36 tests.
- `npx vitest run tests/agent-configuration-model.test.ts`: PASS, 1 file / 5 tests.
- `npm run test:arch024-model-resolution:postgres`: PASS; Prisma `db push` passed, all 7 PostgreSQL tests passed, and runner verified zero owned containers/networks remained.
- Targeted ESLint over all changed JS/TS files, including the additional model-service test: PASS.
- `npm run typecheck`: PASS.
- VS Code diagnostics for changed model service and Availability test: no errors.
- `git diff --check`: PASS.
- Attempt 2: `npx vitest run tests/agent-configuration-model.test.ts`: PASS, 6 tests, including missing-bootstrap non-recreation and bounded failure.
- Attempt 2 focused ARCH-024 Vitest set plus `tests/agent-configuration-model.test.ts`: PASS, 6 files / 42 tests.
- Attempt 2 `npm run test:arch024-model-resolution:postgres`: PASS, all 7 PostgreSQL tests; disposable runner verified no task-owned containers or networks remained.
- Attempt 2 targeted ESLint and `npm run typecheck`: PASS. `npx prisma generate --schema database/prisma/schema.prisma`: PASS. `git diff --check`: PASS.
- A1-R1 review: production legacy create path contains no Availability create/upsert/repair; only the PostgreSQL fixture seeds the deterministic row. No OpenRouter or live provider call was made.

### Deviations

- The required base image does not ship pgvector, while the accepted schema contains an existing PostgreSQL `vector` column. The disposable runner builds pinned pgvector `v0.8.0` inside its task-owned `postgres:16.4-alpine` container and enables the extension before `db push`; no schema or required base-image change was made.

### Assumptions

- Existing Commerce Agent Configuration and prompt semantics remain authoritative outside the requested model-resolution branch; no prompt behavior or credential/runtime behavior was changed.

### Unresolved Issues

None.

### Architectural Concerns

None identified. Implementation is ready for `moda_architect` review; no follow-on task was started.

## Architect Review

### Review Status

Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — Accepted — 2026-10-01

Attempt 2 closes both corrections from the prior Architect Review and is accepted.

**A1-R1 is closed.** `ModelConfigurationService.createCatalogueEntry(...)` now performs a read-only `findUnique(...)` of the deterministic `arch024-platform-model-availability` row, projects it through the published `CommerceModelAvailabilitySchema`, requires `scope = PLATFORM` with `shopId = null`, and fails boundedly as retryable `DATABASE_UNAVAILABLE` when the bootstrap row is missing or structurally invalid. Direct inspection of production `src/` finds no `CommerceModelAvailability` create/upsert/update/delete operation. The missing-row unit regression proves the operation does not recreate the Availability and leaves Catalogue/audit state untouched. The disposable PostgreSQL test fixture seeds the migration-owned row explicitly as test-only state before legacy Catalogue creation; that seeding is not reachable from production Commerce code.

**A1-R2 is closed.** The Completion Report now records the launcher-resolved canonical workspace root, dedicated parent and Commerce implementation worktrees, matching `task/ARCH-024-COMMERCE-002` branches, start-of-attempt synchronization, dependency gates, recursive submodule materialisation, accepted `database/` gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, Attempt 2 implementation commit `f7cf6deb0e108bc5d70a055db6283441503d7dc7`, a pushed parent report commit, and final clean/remote-aligned evidence for both worktrees.

The resubmission identifies implementation head `f7cf6deb` and final parent task-branch head `886dd95c`. The uploaded review archive contains no usable Git metadata, so those remote heads cannot be independently queried here. The durable Completion Report itself records the implementation commit, pushed parent report evidence and final clean/local-equals-remote state; the later submitted parent head is treated as additional handoff evidence, not as a reason to manufacture another report-only commit.

The correction remains bounded to the prior A1-R1 contract. The rest of Attempt 1's already-conformant effective Availability, Price Plan and fail-closed `SHOP -> PRICING_PLAN -> PLATFORM` resolution remains unchanged in architectural ownership and behavior.

#### Attempt 1 review — Changes Requested — 2026-10-01

Attempt 1 is substantially architecture-conformant across the new model-resolution boundary, but two corrections are required before acceptance.

**A1-R1 — Preserve the migration-owned Platform Availability boundary.**

`ModelConfigurationService.createCatalogueEntry(...)` currently calls `commerceModelAvailability.upsert(...)` for `arch024-platform-model-availability`. The accepted ARCH-024 architecture establishes that deterministic Platform Availability in the database migration and makes it non-recreatable; Availability authoring is not owned by Commerce. The legacy Catalogue compatibility bridge may create a Catalogue Entry *inside* that row, but must not create/recreate the Availability itself.

Correct the production path so it only reads the deterministic Platform Availability (for example, `findUnique`) and fails closed with the existing bounded database-unavailable error if the row is absent or structurally not the expected `PLATFORM` / `shopId = null` row. Do not create, upsert or repair the Availability from Commerce application code.

Because the required disposable PostgreSQL runner uses Prisma `db push`, which creates schema but does not execute the migration's deterministic data insert, seed `arch024-platform-model-availability` explicitly as **test fixture state only** after `db push` (or in the focused PostgreSQL fixture) before exercising legacy Catalogue creation. This fixture seeding must not be reachable from production Commerce service code.

Add a focused regression proving that a missing bootstrap Platform Availability is not recreated by `createCatalogueEntry(...)`; the operation must fail boundedly and leave the Availability absent.

**A1-R2 — Record deterministic task-launch evidence in the Completion Report.**

The submitted Completion Report records the implementation commit and validation but does not preserve the launcher-resolved physical-isolation/synchronization packet required for repository-task review. Attempt 2 must record the canonical workspace root, dedicated parent task worktree, dedicated Commerce implementation worktree, matching `task/ARCH-024-COMMERCE-002` branches, start-of-attempt synchronization evidence, recursive submodule materialisation evidence, accepted `database/` gitlink identity (`cfeeb12` or the exact accepted equivalent present at preparation), and final clean/local-equals-remote evidence for both worktrees.

The implementation commit `1f9a462` and parent report commit `5184a5c1` are accepted as the submitted Attempt 1 heads; do not create source churn outside A1-R1 merely to manufacture another implementation change.

### Reviewed Files

- `src/commerce/agent-configuration/model-availability.ts`
- `src/commerce/agent-configuration/pricing-plan-model.ts`
- `src/commerce/agent-configuration/effective-configuration.ts`
- `src/commerce/agent-configuration/model-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/effective-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model-availability.test.ts`
- `tests/agent-configuration-effective.test.ts`
- `tests/agent-configuration-reduced.test.ts`
- `tests/agent-configuration-model.test.ts`
- `tests/agent-configuration-model-postgres.test.ts`
- `scripts/run-arch024-model-resolution-disposable.mjs`
- `package.json`
- `package-lock.json`
- accepted nested `database/prisma/schema.prisma` and ARCH-024 migration
- this task's Completion Report
- parent `ARCH-024` architecture and Commerce task index

### Validation Reviewed

- Independently inspected `src/commerce/agent-configuration/model-service.ts`: the legacy Catalogue create bridge now reads only the deterministic bootstrap Availability and contains no Availability mutation/repair path.
- Independently inspected `tests/agent-configuration-model.test.ts`: the missing-bootstrap regression expects retryable `DATABASE_UNAVAILABLE`, confirms the Availability remains absent, and confirms no Catalogue or audit row is written.
- Independently inspected `tests/agent-configuration-model-postgres.test.ts`: the deterministic Platform Availability is seeded explicitly in test fixture setup before legacy Catalogue creation.
- Re-checked production `src/` for `commerceModelAvailability.create/upsert/update/delete` operations: none are present.
- Re-checked Commerce dependency consumption: `@modainteract/moda-interact-shared` is exactly `1.1.0`, and the lockfile carries the accepted SHARED-002 integrity.
- Reviewed submitted Attempt 2 evidence for the six-file focused Vitest set (**42 tests**), disposable PostgreSQL proof (**7 tests**) with owned-resource cleanup, targeted ESLint, typecheck, Prisma generation and `git diff --check`; all are recorded PASS.
- The uploaded archive contains no installed `node_modules` and no usable Git metadata, so the dependency-backed Vitest/PostgreSQL/Prisma/ESLint/typecheck commands and remote branch heads were not independently re-executed/queried in this review environment.

### Architecture Conformance

Conforms. Attempt 2 restores the migration-owned Platform Availability boundary without weakening the already-conformant ARCH-024 model-resolution design. Commerce reads but does not author/recreate the bootstrap Availability; legacy Catalogue creation remains bounded to that deterministic Platform row; Platform/Shop write selection continues through the canonical availability gate; current Price Plan resolution remains trusted and pending-plan independent; explicit invalid Shop/Price-Plan selections remain fail-closed; effective resolution retains one repeatable-read snapshot; and no credential/OpenRouter runtime dependency enters this task.

### Follow-up

`ARCH-024-COMMERCE-002` is **Complete / Accepted at Attempt 2**.

Dependency reconciliation promotes exactly:

```text
ARCH-024-COMMERCE-005 -> Ready
```

`ARCH-024-COMMERCE-003` remains Pending because its ownership-migration dependency `ARCH-024-ADMIN-002` is not Complete in this isolated parent snapshot. No follow-on implementation is started implicitly by this review.

This isolated COMMERCE-002 parent snapshot has not incorporated the separately accepted ADMIN-001 reconciliation from its sibling parent task branch. This acceptance patch does not replay another task's Completion Report or Architect Review. During later parent-branch integration, preserve ADMIN-001 as Complete and ADMIN-002 as Ready rather than regressing that accepted state.
